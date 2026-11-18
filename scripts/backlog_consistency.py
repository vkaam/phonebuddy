"""Read-only task-link guard for the issue -> task -> PR workflow.

Python 3.9+, standard library only. It never writes to GitHub, tasks or issues.

Modes (see docs/issue-backlog-governance.md):
  --pr                     validate the current branch against its single task
  --task TASK-n --branch B check a claim or resume; requires claim_verified true
  (default)                audit every task; --offline skips GitHub evidence
"""

import argparse
from datetime import datetime, timezone
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"TASK-[1-9][0-9]*\Z")
PATH = re.compile(r"backlog/(?:archive/)?tasks/task-([1-9][0-9]*) - .+\.md\Z", re.I)
APPROVED = "approved"
EXEMPT_AUTHORS = {"dependabot[bot]"}
DEPENDENCY_FILES = ("package.json", "package-lock.json", ".github/workflows/*.yml", "**/package.json",
                    "**/package-lock.json")


class EvidenceError(ValueError):
    """Evidence is missing, malformed or unavailable; never a passing result."""


def git(root, *args, optional=False):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=30,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    if result.returncode:
        if optional:
            return None
        raise EvidenceError("Git evidence unavailable; fetch the default branch and check the checkout.")
    return result.stdout.decode("utf-8")


def scalar(value):
    """Accept the flat string/list subset emitted by the native task CLI.

    Reject unsupported YAML rather than interpreting aliases, tags or objects.
    The reader never rewrites native records. More complex syntax needs a reader
    update, not a second task schema or a silent best-effort parse.
    """
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"'):
        result = json.loads(value)
        if not isinstance(result, str):
            raise EvidenceError("Expected a string scalar.")
        return result
    if value.startswith("'"):
        if not value.endswith("'"):
            raise EvidenceError("Unterminated quoted scalar.")
        return value[1:-1].replace("''", "'")
    if value[0] in "!&*{|>" or " #" in value:
        raise EvidenceError("Unsupported native frontmatter syntax.")
    return value


def parse_task(text, path):
    match = PATH.fullmatch(path)
    if not match or not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise EvidenceError(f"{path}: invalid native task path or frontmatter.")
    header, body = text[4:].split("\n---\n", 1)
    meta, current = {}, None
    lines, position = header.splitlines(), 0
    while position < len(lines):
        line = lines[position]
        position += 1
        if not line.strip() or line.startswith("#"):
            continue
        item = re.fullmatch(r"  - (.*)", line)
        if item and current and isinstance(meta[current], list):
            value = item[1]
            if value in {">-", ">", "|-", "|"}:
                folded = []
                while position < len(lines) and lines[position].startswith("    "):
                    folded.append(lines[position][4:])
                    position += 1
                if not folded:
                    raise EvidenceError(f"{path}: empty block scalar.")
                value = (" " if value.startswith(">") else "\n").join(folded)
            meta[current].append(scalar(value))
            continue
        field = re.fullmatch(r"([a-z_]+):(?: (.*))?", line)
        if not field or field[1] in meta:
            raise EvidenceError(f"{path}: unsupported or duplicate metadata field.")
        current, value = field[1], field[2] or ""
        if value in {">-", ">", "|-", "|"}:
            folded = []
            while position < len(lines) and lines[position].startswith("  "):
                folded.append(lines[position][2:])
                position += 1
            if not folded:
                raise EvidenceError(f"{path}: empty block scalar.")
            meta[current] = (" " if value.startswith(">") else "\n").join(folded)
        elif value.startswith("["):
            # Native inline lists use strings; commas inside quotes are preserved.
            if not value.endswith("]"):
                raise EvidenceError(f"{path}: unterminated inline list.")
            parts = re.findall(r"'(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"|[^,]+", value[1:-1])
            meta[current] = [scalar(p) for p in parts]
        else:
            meta[current] = [] if not value else scalar(value)
    tid = meta.get("id")
    if not isinstance(tid, str) or not ID.fullmatch(tid) or tid != f"TASK-{match[1]}":
        raise EvidenceError(f"{path}: task ID does not match its filename.")
    for key in ("references", "dependencies", "assignee", "labels"):
        meta.setdefault(key, [])
        if not isinstance(meta[key], list) or not all(isinstance(v, str) for v in meta[key]):
            raise EvidenceError(f"{path}: {key} must be a native string list.")
    if meta.get("status") not in {"To Do", "In Progress", "Done"}:
        raise EvidenceError(f"{path}: unknown task status.")
    ac = re.search(r"<!-- AC:BEGIN -->(.*?)<!-- AC:END -->", body, re.S)
    criteria = re.findall(r"^- \[([ xX])\] (.+)$", ac[1] if ac else "", re.M)
    return {"id": tid, "path": path, "meta": meta, "body": body,
            "archived": "/archive/" in path or meta.get("archived") == "true",
            "ac": [(state.lower() == "x", text) for state, text in criteria]}


def load_tasks(root, ref=None):
    if ref:
        paths = git(root, "ls-tree", "-r", "--name-only", ref, "--", "backlog").splitlines()
    else:
        paths = [p.relative_to(root).as_posix() for folder in ("backlog/tasks", "backlog/archive/tasks")
                 for p in (root / folder).glob("*.md")]
    tasks = {}
    for path in sorted(paths):
        if not PATH.fullmatch(path):
            if re.match(r"backlog/(?:archive/)?tasks/task-", path, re.I):
                raise EvidenceError(f"{path}: invalid native task filename.")
            continue
        if not ref and (root / path).is_symlink():
            raise EvidenceError(f"{path}: symlink task records are not supported.")
        text = git(root, "show", f"{ref}:{path}") if ref else (root / path).read_text(encoding="utf-8")
        task = parse_task(text, path)
        if task["id"] in tasks:
            raise EvidenceError(f"{task['id']}: ambiguous duplicate native ID.")
        tasks[task["id"]] = task
    return tasks


def field(task, name):
    """Return a `Name: value` line or a `## Name` section from the description."""
    body = task["body"]
    match = re.search(r"^" + re.escape(name) + r":[ \t]*(\S.*)$", body, re.M | re.I)
    if match:
        return match[1].strip().rstrip(".")
    match = re.search(r"^## " + re.escape(name) + r"\s*\n(.*?)(?=\n## |\Z)", body, re.S | re.I)
    return match[1].strip() if match else ""


def issue_url(task, repository):
    pattern = rf"https://github\.com/{re.escape(repository)}/issues/[1-9][0-9]*"
    explicit = field(task, "Issue") or field(task, "Primary issue")
    if re.fullmatch(pattern, explicit):
        return explicit
    for reference in task["meta"]["references"]:
        if re.fullmatch(pattern, reference):
            return reference
    raise EvidenceError("task needs an `Issue:` line or reference to an issue in this repository")


def scope_patterns(task):
    """Scope entries are repository-relative paths or globs separated by `;`.

    Prose entries (words without a slash or extension) are notes and grant nothing.
    Backlog records are always in scope, so tasks never list their own record.
    """
    patterns = []
    for entry in field(task, "Scope").split(";"):
        entry = entry.strip().rstrip(".")
        if not entry or entry.startswith("backlog/"):
            continue
        if " " in entry and "/" not in entry:
            continue
        if (entry.startswith(("/", "~")) or "\\" in entry or ".." in PurePosixPath(entry).parts
                or entry.split("/")[0] == ".git" or any(c in entry.split("/")[0] for c in "*?[")):
            raise EvidenceError(f"Scope entry is not a bounded repository path: {entry}")
        patterns.append(entry)
    return patterns


def spec(task, repository):
    """The fields that make a task executable."""
    issue = issue_url(task, repository)
    branch = field(task, "Branch")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9/._-]*", branch) or branch in {"main", "master"}:
        raise EvidenceError("task needs a `Branch:` line naming its feature branch")
    scope = scope_patterns(task)
    if not scope:
        raise EvidenceError("task needs a `Scope:` line listing the paths it may change")
    if not task["ac"]:
        raise EvidenceError("task needs at least one acceptance criterion")
    return {"issue": issue, "branch": branch, "scope": scope}


def issue_problem(issue):
    if not issue:
        return "linked issue could not be read"
    if issue.get("pull_request"):
        return "linked number is a pull request, not an issue"
    if issue.get("state") != "open":
        return "linked issue is not open"
    if APPROVED not in {label.get("name") for label in issue.get("labels", [])}:
        return f"linked issue is not labeled `{APPROVED}`"
    return None


def merged_from(branch, live):
    return [p for p in live["pulls"] if p.get("merged_at") and p["head"]["ref"] == branch]


def completed(tid, base, live):
    """A dependency is complete when main has it Done, or (older records) when
    main still says In Progress but every criterion is checked and its PR merged."""
    task = base.get(tid)
    if not task:
        return False
    if task["meta"]["status"] == "Done":
        return True
    if task["archived"] or task["meta"]["status"] != "In Progress" or not task["ac"]:
        return False
    if not all(checked for checked, _ in task["ac"]) or not live:
        return False
    branch = field(task, "Branch")
    return bool(branch and merged_from(branch, live))


def structure(tasks, only=None):
    """Unknown dependencies and cycles; restricted to `only` and its dependencies."""
    errors, visiting, visited = [], set(), set()

    def walk(tid):
        if tid in visiting:
            errors.append(f"{tid}: cyclic dependencies")
            return
        if tid in visited:
            return
        visiting.add(tid)
        for dep in tasks[tid]["meta"]["dependencies"]:
            if dep not in tasks:
                errors.append(f"{tid}: unknown dependency {dep}")
            else:
                walk(dep)
        visiting.discard(tid)
        visited.add(tid)

    for tid in ([only] if only else tasks):
        walk(tid)
    return errors


def active(tasks):
    return {tid: t for tid, t in tasks.items() if not t["archived"] and t["meta"]["status"] != "Done"}


def competing_prs(tid, branch, live):
    title = re.compile(rf"\b{re.escape(tid)}\b")
    return sorted(p["number"] for p in live["pulls"]
                  if p["state"] == "open" and p["head"]["ref"] != branch and title.search(p.get("title") or ""))


def check_task(task, base, repository, live, branch):
    """Rules shared by PR and claim validation for one task."""
    tid, errors = task["id"], []
    try:
        info = spec(task, repository)
    except EvidenceError as error:
        return [f"{tid}: {error}"], None
    if info["branch"] != branch:
        errors.append(f"{tid}: recorded branch is {info['branch']}, not {branch}")
    problem = issue_problem(live["issues"].get(info["issue"]))
    if problem:
        errors.append(f"{tid}: {problem}")
    waiting = [dep for dep in task["meta"]["dependencies"] if not completed(dep, base, live)]
    if waiting:
        errors.append(f"{tid}: dependencies are not complete on main: {', '.join(waiting)}")
    if base.get(tid, {}).get("meta", {}).get("status") == "Done":
        errors.append(f"{tid}: task is already Done on main; create a follow-up task")
    others = competing_prs(tid, branch, live)
    if others:
        errors.append(f"{tid}: another open PR names this task: {', '.join(f'#{n}' for n in others)}")
    return errors, info


def exemption(changed, author):
    """PRs that need no task: dependency bots and pure Backlog record changes."""
    if author in EXEMPT_AUTHORS and changed and all(
            any(fnmatch.fnmatchcase(path, pattern) for pattern in DEPENDENCY_FILES) for path in changed):
        return f"author {author}"
    if not changed:
        return "no changed paths"
    if all(path.startswith("backlog/") for path in changed):
        return "Backlog records only"
    return None


def check_pr(tasks, base, repository, live, branch, changed, author):
    reason = exemption(changed, author)
    if reason:
        return {"errors": [], "warnings": [], "exempt": reason}
    owners = [t for t in active(tasks).values() if field(t, "Branch") == branch]
    owners += [t for t in tasks.values() if t["meta"]["status"] == "Done" and not t["archived"]
               and field(t, "Branch") == branch and base.get(t["id"], {}).get("meta", {}).get("status") != "Done"]
    if len(owners) != 1:
        found = ", ".join(t["id"] for t in owners) or "none"
        return {"errors": [f"branch {branch}: needs exactly one task with `Branch: {branch}` (found {found})"],
                "warnings": [], "task": None}
    task = owners[0]
    errors, info = check_task(task, base, repository, live, branch)
    errors += structure(tasks, task["id"])
    warnings = []
    if info:
        outside = [p for p in changed if not p.startswith("backlog/")
                   and not any(fnmatch.fnmatchcase(p, pattern) for pattern in info["scope"])]
        errors += [f"{task['id']}: changed path outside Scope: {p}" for p in outside]
    if task["meta"]["status"] == "Done" and not all(checked for checked, _ in task["ac"]):
        errors.append(f"{task['id']}: Done requires every acceptance criterion checked")
    if task["meta"]["status"] == "To Do":
        warnings.append(f"{task['id']}: task is still To Do; claim it before review")
    on_main = base.get(task["id"])
    if info and on_main and field(on_main, "Scope") and field(on_main, "Scope") != field(task, "Scope"):
        warnings.append(f"{task['id']}: Scope differs from main; reviewer must confirm the owner agreed")
    return {"errors": errors, "warnings": warnings, "task": task["id"]}


def check_claim(tasks, base, repository, live, target, branch):
    task = tasks.get(target)
    if not task or task["archived"] or task["meta"]["status"] == "Done":
        return {"errors": [f"{target}: task is missing, archived or Done"], "warnings": []}
    errors, _ = check_task(task, base, repository, live, branch)
    errors += structure(tasks, target)
    if task["meta"]["status"] == "To Do" and task["meta"]["assignee"]:
        errors.append(f"{target}: To Do task is already assigned to {', '.join(task['meta']['assignee'])}")
    if merged_from(branch, live):
        errors.append(f"{target}: branch {branch} already has a merged PR; use a new task and branch")
    claimed = sorted(p["number"] for p in live["pulls"] if p["state"] == "open" and p["head"]["ref"] == branch)
    if claimed and (task["meta"]["status"] == "To Do" or not task["meta"]["assignee"]):
        errors.append(f"{target}: open PR {', '.join(f'#{n}' for n in claimed)} already claims this task; "
                      "resume from that branch's task record")
    return {"errors": errors, "warnings": []}


def audit(tasks, base, repository, live):
    errors, warnings, branches = structure(tasks), [], {}
    for tid, task in sorted(active(tasks).items()):
        try:
            info = spec(task, repository)
        except EvidenceError as error:
            warnings.append(f"{tid}: not executable: {error}")
            continue
        if info["branch"] in branches:
            errors.append(f"{tid}: branch {info['branch']} is also recorded by {branches[info['branch']]}")
        branches[info["branch"]] = tid
        if not live:
            continue
        problem = issue_problem(live["issues"].get(info["issue"]))
        if problem:
            warnings.append(f"{tid}: {problem}")
        if task["meta"]["status"] == "In Progress" and merged_from(info["branch"], live):
            warnings.append(f"{tid}: PR merged but task is still In Progress; finish or split the remaining work")
    return {"errors": errors, "warnings": warnings}


class GitHub:
    """GET-only client; no mutations, hooks, PR code execution or token logging."""

    def __init__(self, repository):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise EvidenceError("Invalid repository identity.")
        self.repository = repository
        self.token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            result = subprocess.run(["gh", "auth", "token", "--hostname", "github.com"],
                                    capture_output=True, timeout=15)
            if result.returncode:
                raise EvidenceError("A read-only GitHub connection is required.")
            self.token = result.stdout.decode().strip()
        if not self.token:
            raise EvidenceError("A read-only GitHub connection is required.")

    def get(self, endpoint, missing=False):
        url = f"https://api.github.com/repos/{self.repository}" + (f"/{endpoint}" if endpoint else "")
        request = Request(url, headers={"Authorization": f"Bearer {self.token}",
                          "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except HTTPError as error:
            if missing and error.code == 404:
                return None
            operation = endpoint.split("/", 1)[0] or "repository"
            raise EvidenceError(f"GitHub {operation} evidence unavailable (HTTP {error.code}).") from None
        except (URLError, TimeoutError, OSError, ValueError):
            operation = endpoint.split("/", 1)[0] or "repository"
            raise EvidenceError(f"GitHub {operation} evidence unavailable or malformed.") from None

    def pages(self, endpoint):
        values = []
        for page in range(1, 101):
            rows = self.get(f"{endpoint}{'&' if '?' in endpoint else '?'}per_page=100&page={page}")
            if not isinstance(rows, list):
                raise EvidenceError("Incomplete GitHub pagination evidence.")
            values.extend(rows)
            if len(rows) < 100:
                return values
        raise EvidenceError("GitHub evidence exceeds pagination limit; no passing fallback.")


def collect(client, tasks, repository, wanted):
    """Fetch PRs and the linked issues of `wanted` task IDs."""
    pulls = client.pages("pulls?state=all")
    issues = {}
    for tid in wanted:
        try:
            url = issue_url(tasks[tid], repository)
        except EvidenceError:
            continue
        if url not in issues:
            issues[url] = client.get("issues/" + url.rsplit("/", 1)[1], missing=True)
    return {"pulls": pulls, "issues": issues}


def changed_paths(root, base_sha):
    merge_base = git(root, "merge-base", base_sha, "HEAD").strip()
    changed = git(root, "diff", "--no-renames", "--name-only", "-z", merge_base, "--").split("\0")
    changed += git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    return sorted({p for p in changed if p and not p.startswith("artifacts/")})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default="origin/main", help="fresh default-branch ref")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "vkaam/phonebuddy"))
    parser.add_argument("--task", help="claim/resume check for this task")
    parser.add_argument("--branch", help="task branch (default: GITHUB_HEAD_REF or the current branch)")
    parser.add_argument("--pr", "--ci-pr", dest="pr", action="store_true", help="validate this branch's PR")
    parser.add_argument("--author", default=os.environ.get("PR_AUTHOR", ""), help="PR author login")
    parser.add_argument("--offline", action="store_true", help="audit structure without GitHub evidence")
    parser.add_argument("--output", type=Path, help="also write the JSON report here")
    args = parser.parse_args(argv)
    mode = "pr" if args.pr else "claim" if args.task else "audit"
    report = {"schema_version": 2, "mode": mode, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "status": "fail", "claim_verified": False, "errors": [], "warnings": []}
    output_ok = False
    try:
        root = args.root.resolve()
        if args.output:
            target = args.output.resolve()
            if root in target.parents and not target.relative_to(root).as_posix().startswith("artifacts/"):
                raise EvidenceError("--output must be outside the checkout or under artifacts/")
            output_ok = True
        if args.pr and args.task:
            raise EvidenceError("--pr and --task are separate modes")
        if args.offline and mode != "audit":
            raise EvidenceError("PR and claim checks need live GitHub evidence; --offline is audit-only")
        tasks = load_tasks(root)
        base_sha = git(root, "rev-parse", args.base + "^{commit}").strip()
        base = load_tasks(root, base_sha)
        branch = args.branch or os.environ.get("GITHUB_HEAD_REF") or git(root, "branch", "--show-current").strip()
        report.update({"base_sha": base_sha, "branch": branch, "repository": args.repository})
        if mode == "pr":
            changed = changed_paths(root, base_sha)
            report["changed_paths"] = changed
            owners = [tid for tid, t in tasks.items() if field(t, "Branch") == branch]
            live = None if exemption(changed, args.author) else collect(
                GitHub(args.repository), tasks, args.repository, owners)
            result = check_pr(tasks, base, args.repository, live, branch, changed, args.author)
        elif mode == "claim":
            live = collect(GitHub(args.repository), tasks, args.repository, [args.task] if args.task in tasks else [])
            result = check_claim(tasks, base, args.repository, live, args.task, branch)
            report["task"] = args.task
        else:
            live = None if args.offline else collect(GitHub(args.repository), tasks, args.repository, active(tasks))
            result = audit(tasks, base, args.repository, live)
        report.update(result)
        report["status"] = "fail" if report["errors"] else "pass"
        report["claim_verified"] = mode == "claim" and not report["errors"]
    except (EvidenceError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        # Never echo raw API responses, issue text or tokens.
        report["status"] = "fail"
        report["claim_verified"] = False
        report["errors"].append(str(error) if isinstance(error, EvidenceError) else "Evidence could not be read or parsed.")
    output = json.dumps(report, indent=2) + "\n"
    if output_ok:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
