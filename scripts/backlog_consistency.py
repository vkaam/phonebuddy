"""Read-only issue/task/claim validation. Python 3.9+, no package dependencies."""

import argparse
import base64
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"TASK-[1-9][0-9]*\Z")
PATH = re.compile(r"backlog/(?:archive/)?tasks/task-([1-9][0-9]*) - .+\.md\Z", re.I)
ADOPTION = "2026-11-01"


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
    # Existing descriptions use both labeled paragraphs and Markdown headings.
    body = task["body"]
    match = re.search(r"^" + re.escape(name) + r":\s*(.+)$", body, re.M | re.I)
    if match:
        return match[1].strip().rstrip(".")
    match = re.search(r"^## " + re.escape(name) + r"\s*\n(.*?)(?=\n## |\Z)", body, re.S | re.I)
    if match:
        return match[1].strip()
    if name == "Branch":
        match = re.search(r"\bBranch: ([A-Za-z0-9/_-]+)", body)
        return match[1] if match else ""
    return ""


def focus_for_branch(tasks, branch):
    """Include the PR's task and its native dependencies, never unrelated work."""
    owners = [tid for tid, task in tasks.items() if not task["archived"] and field(task, "Branch") == branch]
    focus = set(owners)

    def add_dependencies(tid):
        for dependency in tasks[tid]["meta"]["dependencies"]:
            if dependency in tasks and dependency not in focus:
                focus.add(dependency)
                add_dependencies(dependency)

    for owner in owners:
        add_dependencies(owner)
    return focus


def historical(task, base):
    old = base.get(task["id"])
    return bool(old and str(old["meta"].get("created_date", "9999"))[:10] < ADOPTION)


def primary_issue(task, repository):
    explicit = field(task, "Issue") or field(task, "Primary issue")
    pattern = rf"https://github\.com/{re.escape(repository)}/issues/[1-9][0-9]*"
    if not re.fullmatch(pattern, explicit) or explicit not in task["meta"]["references"]:
        raise EvidenceError("canonical primary Issue URL must also be in native references")
    return explicit


def spec(task, repository):
    issue = primary_issue(task, repository)
    body = task["body"].split("## Acceptance Criteria", 1)[0]
    digest = re.search(r"SHA-256(?: of UTF-8 issue body)?\s+([0-9a-f]{64})", body, re.I)
    revision = re.search(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", body)
    approval = field(task, "Approval evidence") or field(task, "Approval")
    branch = field(task, "Branch")
    scope = field(task, "Scope")
    # Earlier CLI-managed specifications put external/context notes after the
    # repository allowlist on the same line. Those notes grant no file scope.
    scope = scope.split(". External scope:", 1)[0].split(". Archived TASK-", 1)[0]
    verify = field(task, "Verify") or field(task, "Verification")
    if not digest or not revision or not approval:
        raise EvidenceError("approved timestamp, SHA-256 and explicit approval evidence are required")
    if not branch or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9/_-]*", branch) or branch in {"main", "master"}:
        raise EvidenceError("a unique feature Branch is required")
    if not scope or not verify or not task["ac"]:
        raise EvidenceError("explicit Scope, Verify commands and native acceptance are required")
    paths = []
    for path in scope.split(";"):
        path = path.strip().rstrip(".")
        if path in {"this task's own CLI-managed record", "this task's CLI-managed record",
                    "this task record through Backlog CLI", "this task record only"}:
            path = task["path"]
        if (not path or path.startswith(("/", "~")) or "\\" in path
                or ".." in PurePosixPath(path).parts or any(c in path for c in "`$\n")
                or path.split("/")[0] in {"*", "**", ".git"}):
            raise EvidenceError("Scope must enumerate repository-relative paths or bounded directory globs")
        paths.append(path)
    if task["path"] not in paths:
        raise EvidenceError("Scope must explicitly include this native task record")
    return {"issue": issue, "digest": digest[1].lower(), "revision": revision[0],
            "branch": branch, "scope": paths, "verify": verify}


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


def branch_tasks(root, client, sha, wanted):
    listing = git(root, "ls-tree", "-r", "--name-only", sha, "--", "backlog/tasks", optional=True)
    if listing is None:
        tree = client.get(f"git/trees/{sha}?recursive=1")
        if tree.get("truncated") or not isinstance(tree.get("tree"), list):
            raise EvidenceError("Truncated branch tree cannot establish exclusive claims.")
        listing = "\n".join(x["path"] for x in tree["tree"] if x.get("type") == "blob")
    found = {}
    for path in listing.splitlines():
        match = PATH.fullmatch(path)
        if not match or path.startswith("backlog/archive/") or f"TASK-{match[1]}" not in wanted:
            continue
        content = git(root, "show", f"{sha}:{path}", optional=True)
        if content is None:
            blob = client.get(f"contents/{quote(path, safe='/')}?ref={sha}")
            if blob.get("encoding") != "base64" or "content" not in blob:
                raise EvidenceError("Branch task content unavailable.")
            content = base64.b64decode(blob["content"]).decode()
        task = parse_task(content, path)
        if task["id"] in found:
            raise EvidenceError(f"{task['id']}: ambiguous branch claim record.")
        found[task["id"]] = task
    return found


def collect(root, repository, tasks, base_sha, client=None):
    client = client or GitHub(repository)
    repo = client.get("")
    default = repo["default_branch"]
    default_sha = client.get(f"git/ref/heads/{quote(default, safe='')}")["object"]["sha"]
    if default_sha != base_sha:
        raise EvidenceError("Default-branch evidence is stale; fetch current main and rerun validation.")
    pulls = client.pages("pulls?state=all")
    for pr in pulls:
        pr["on_default_branch"] = bool(pr.get("merged_at") and pr.get("merge_commit_sha")
                                       and git(root, "merge-base", "--is-ancestor", pr["merge_commit_sha"],
                                               base_sha, optional=True) is not None)
    branches = client.pages("branches")
    issues = {}
    for task in tasks.values():
        try:
            url = primary_issue(task, repository)
        except EvidenceError:
            continue
        if url not in issues:
            issues[url] = client.get("issues/" + url.rsplit("/", 1)[1])
    claims = []
    for branch in branches:
        for tid, task in branch_tasks(root, client, branch["commit"]["sha"], tasks).items():
            if (field(task, "Branch") == branch["name"] and not task["archived"]
                    and task["meta"]["status"] in {"In Progress", "Done"}):
                claims.append({"task": tid, "branch": branch["name"],
                               "sha": branch["commit"]["sha"], "status": task["meta"]["status"]})
    # Open PRs can come from a fork whose branch is absent from the base repo.
    for pr in pulls:
        if pr["state"] != "open":
            continue
        for tid, task in branch_tasks(root, client, pr["head"]["sha"], tasks).items():
            if field(task, "Branch") == pr["head"]["ref"] and not task["archived"]:
                claims.append({"task": tid, "branch": pr["head"]["ref"],
                               "sha": pr["head"]["sha"], "status": task["meta"]["status"],
                               "pr": pr["number"], "repository": pr["head"]["repo"]["full_name"]})
    if client.get(f"git/ref/heads/{quote(default, safe='')}")["object"]["sha"] != default_sha:
        raise EvidenceError("Default branch changed during collection; rerun on fresh evidence.")
    return {"default_branch": default, "default_sha": default_sha, "issues": issues,
            "pulls": pulls, "claims": claims, "collected_at": datetime.now(timezone.utc).isoformat()}


def validate(tasks, base, repository, live=None, target=None, branch=None, changed=(), focus=None):
    errors, warnings, specs, blocked = [], [], {}, {}

    def fail(tid, reason):
        if focus is None or tid in focus or tid == "scope":
            errors.append(f"{tid}: {reason}")

    for tid in base.keys() - tasks.keys():
        fail(tid, "native identity/history was removed; retain an explicit archival/migration record")
    for tid, task in tasks.items():
        old = base.get(tid)
        unchanged_done = (old is not None and old == task
                          and task["meta"]["status"] == "Done")
        amended_done = (old is not None and old != task
                        and task["meta"]["status"] == "Done"
                        and old["meta"]["status"] == "Done")
        if historical(task, base) and not amended_done:
            if not task["archived"] and task["meta"]["status"] != "Done":
                warnings.append(f"{tid}: historical import is ineligible; fresh atomic triage is required")
            continue
        if unchanged_done or (task["archived"] and not amended_done):
            continue
        try:
            specs[tid] = spec(task, repository)
            if task["meta"]["status"] == "Done" and not all(x[0] for x in task["ac"]):
                fail(tid, "proposed completion has unchecked native acceptance")
            if task["meta"]["status"] == "In Progress" and len(task["meta"]["assignee"]) != 1:
                fail(tid, "active execution requires one explicit assignee")
        except EvidenceError as error:
            fail(tid, str(error))
    visiting, visited = set(), set()

    def walk(tid):
        if tid in visiting:
            fail(tid, "cyclic native dependencies")
            return
        if tid in visited:
            return
        visiting.add(tid)
        for dep in tasks[tid]["meta"]["dependencies"]:
            if dep not in tasks:
                fail(tid, f"unknown native dependency {dep}")
            else:
                walk(dep)
        visiting.remove(tid)
        visited.add(tid)

    for tid in tasks:
        walk(tid)

    completion_cache, completing = {}, set()

    def completed(tid):
        if tid in completion_cache:
            return completion_cache[tid]
        if tid in completing:
            return False
        old = base.get(tid)
        current = tasks.get(tid)
        legacy_merged = (old and current and old["meta"]["status"] == "In Progress"
                         and current["meta"]["status"] == "In Progress")
        if (not old or not current or ((old["archived"] or current["archived"])
                                    and old["meta"]["status"] != "Done")
                or not (old["meta"]["status"] == current["meta"]["status"] == "Done"
                                            or legacy_merged) or not old["ac"]
                or current["ac"] != old["ac"] or current["meta"]["dependencies"] != old["meta"]["dependencies"]
                or not all(x[0] for x in current["ac"])
                or any(field(current, key) != field(old, key) for key in
                       ("Issue", "Primary issue", "Branch", "Scope", "Verify", "Verification"))
                or not all(x[0] for x in old["ac"])):
            return False
        completing.add(tid)
        dependencies_done = all(completed(dep) for dep in current["meta"]["dependencies"])
        completing.remove(tid)
        if not dependencies_done:
            return False
        if historical(old, base):
            return True  # Grandfather verified historic completion on the default branch only.
        if not live:
            return False  # Offline structure is never live dependency authorization.
        pr_branch = field(old, "Branch")
        done = any(p.get("merged_at") and p.get("on_default_branch")
                   and p["base"]["ref"] == live["default_branch"]
                   and p["head"]["ref"] == pr_branch
                   and p["head"]["repo"] and p["head"]["repo"]["full_name"] == repository
                   for p in live["pulls"])
        completion_cache[tid] = done
        return done

    for tid, task in tasks.items():
        blocked[tid] = [dep for dep in task["meta"]["dependencies"] if not completed(dep)]
        if task["meta"]["status"] == "In Progress" and completed(tid):
            warnings.append(f"{tid}: merged PR and checked acceptance establish completion; native status is stale")
        # Superseded IDs must not survive on any active downstream record.
        old = base.get(tid)
        replacements = re.findall(r"^Replaced by: (TASK-[1-9][0-9]*)\s*$", task["body"], re.M) if task["archived"] else []
        if old and task["archived"] and old["meta"]["status"] != "Done" and task["meta"]["status"] != old["meta"]["status"]:
            fail(tid, "archival must not turn unfinished work into completion")
        if old and not old["archived"] and task["archived"] and old["meta"]["status"] != "Done":
            intake = ("historical-import" in task["meta"]["labels"]
                      and "needs-triage" in task["meta"]["labels"]
                      and any(re.fullmatch(rf"https://github\.com/{re.escape(repository)}/issues/[1-9][0-9]*", u)
                              for u in task["meta"]["references"]))
            if not replacements and not intake:
                fail(tid, "migration requires 'Replaced by: TASK-n' or explicit historical-import/needs-triage issue intake")
        for replacement in replacements:
            if replacement not in tasks or tasks[replacement]["archived"]:
                fail(tid, f"replacement {replacement} is missing or archived")
            else:
                urls = set(task["meta"]["references"]) & set(tasks[replacement]["meta"]["references"])
                if not any(re.fullmatch(rf"https://github\.com/{re.escape(repository)}/issues/[1-9][0-9]*", u) for u in urls):
                    fail(tid, f"replacement {replacement} lacks the same canonical issue mapping")
            for child in tasks.values():
                if not child["archived"] and tid in child["meta"]["dependencies"]:
                    fail(child["id"], f"stale migration dependency {tid}; remap to {replacement}")

    signatures, branches = {}, {}
    for tid, info in specs.items():
        signature = (info["issue"], info["digest"], tuple(sorted(p for p in info["scope"] if not p.startswith("backlog/"))),
                     tuple(text for _, text in tasks[tid]["ac"]))
        if signature in signatures:
            fail(tid, f"duplicate decomposition of {signatures[signature]}")
            fail(signatures[signature], f"duplicate decomposition of {tid}")
        signatures[signature] = tid
        if info["branch"] in branches:
            fail(tid, f"feature branch already assigned to {branches[info['branch']]}")
            fail(branches[info["branch"]], f"feature branch already assigned to {tid}")
        branches[info["branch"]] = tid
        if live:
            issue = live["issues"].get(info["issue"])
            if not issue or "body" not in issue:
                fail(tid, "live approval/revision evidence is unavailable")
            elif issue.get("state") == "closed" and not all(
                    completed(peer["id"]) for peer in tasks.values()
                    if primary_issue(peer, repository) == info["issue"]):
                fail(tid, "issue is closed before all linked tasks have merged completion")
            elif issue.get("state") not in {"open", "closed"}:
                fail(tid, "issue state is unavailable")
            elif hashlib.sha256((issue["body"] or "").encode()).hexdigest() != info["digest"]:
                fail(tid, "issue body changed; authorized triage must reassess the approved revision")
            prs = [p for p in live["pulls"] if p["head"]["ref"] == info["branch"]
                   and p["head"]["repo"] and p["head"]["repo"]["full_name"] == repository]
            if len(prs) > 1:
                fail(tid, "multiple PRs reuse this task branch; split/reconcile through triage")
            claims = [c for c in live["claims"] if c["task"] == tid]
            owners = {(c.get("repository", repository), c["branch"]) for c in claims}
            if (len(owners) > 1 or any(owner[0] != repository for owner in owners)
                    or any(c["branch"] != info["branch"] for c in claims)):
                fail(tid, "competing branch/PR claims; reconcile ownership before execution")
            if any(c["status"] == "To Do" and c.get("pr") for c in claims):
                fail(tid, "open implementation PR has an unclaimed To Do record")
            if (tasks[tid]["meta"]["status"] == "In Progress" and not completed(tid)
                    and not claims and info["branch"] != branch):
                fail(tid, "active claim has no live branch/PR; reconcile deleted or stale work")
            if tasks[tid]["meta"]["status"] == "In Progress" and blocked[tid]:
                fail(tid, "active work lacks default-branch completion: " + ", ".join(blocked[tid]))

    if target:
        task = tasks.get(target)
        if not task or task["archived"] or historical(task, base) or task["meta"]["status"] == "Done":
            fail(target, "task is absent, archived, historical or already Done; it cannot be claimed")
        elif target not in specs:
            fail(target, "task has no valid approved execution specification")
        else:
            info = specs[target]
            if task["meta"]["status"] == "To Do" and task["meta"]["assignee"]:
                fail(target, "pending task is already assigned; do not take over another worker")
            if branch != info["branch"]:
                fail(target, f"claim must use the recorded branch {info['branch']}")
            if blocked[target]:
                fail(target, "dependencies lack verified default-branch completion: " + ", ".join(blocked[target]))
            if not live:
                fail(target, "claims require live evidence; offline checks cannot authorize work")
            else:
                for c in live["claims"]:
                    if c["task"] == target and (c["branch"] != branch or c.get("repository", repository) != repository):
                        fail(target, "task already claimed by another branch or repository")
                if any(p.get("merged_at") and p["head"]["ref"] == branch for p in live["pulls"]):
                    fail(target, "task branch already produced a merged PR; reconcile before reuse")

    # PR source changes need an approved task on the current branch. Main audits
    # still validate all records; branch-local Done may propose its own completion.
    if changed and branch not in {"main", "master", None}:
        candidates = [tid for tid, info in specs.items() if info["branch"] == branch]
        if len(candidates) != 1:
            fail("scope", "changed branch requires exactly one approved execution task")
        else:
            tid = candidates[0]
            for path in changed:
                if not any(fnmatch.fnmatchcase(path, pattern) for pattern in specs[tid]["scope"]):
                    fail(tid, f"changed path outside approved scope: {path}")
    return {"status": "fail" if errors else "pass", "errors": sorted(set(errors)),
            "warnings": sorted(set(warnings)), "blocked_dependencies": blocked,
            "task_count": len(tasks), "executable_tasks": sorted(specs),
            "claim_task": target, "claim_verified": bool(target and live and not errors)}


def source(root, tasks):
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").strip("\0").split("\0")
    tracked = set(git(root, "ls-files", "--cached", "-z").strip("\0").split("\0"))
    manifest = []
    for name in sorted(set(n for n in names if n)):
        if name.startswith("artifacts/") and name not in tracked:
            continue  # Runtime evidence is not source. Tracked artifact changes still count.
        path = root / name
        if path.is_symlink():
            entry = {"path": name, "symlink": os.readlink(path)}
        elif path.is_file():
            entry = {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "mode": path.stat().st_mode & 0o777}
        elif not path.exists():
            entry = {"path": name, "deleted": True}
        else:
            raise EvidenceError("Unsupported source entry in source manifest.")
        manifest.append(entry)
    return {"head": git(root, "rev-parse", "HEAD").strip(),
            "status": git(root, "status", "--porcelain=v1", "--untracked-files=all"),
            "manifest": manifest,
            "manifest_sha256": hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default="origin/main", help="Fresh default-branch ref, never the task branch")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "vkaam/phonebuddy"))
    parser.add_argument("--task", help="Validate this native task immediately before claim/resume")
    parser.add_argument("--branch", help="Task branch (defaults to GITHUB_HEAD_REF or current branch)")
    parser.add_argument("--ci-pr", action="store_true", help="Block only on this PR's task and dependencies")
    parser.add_argument("--offline", action="store_true", help="Structural checks only; cannot verify a claim")
    parser.add_argument("--output", type=Path, help="Write JSON evidence in addition to stdout")
    args = parser.parse_args(argv)
    report = {"schema_version": 1, "mode": "offline" if args.offline else "live",
              "recorded_at": datetime.now(timezone.utc).isoformat(), "status": "fail",
              "claim_verified": False, "errors": []}
    output_safe = False
    try:
        root = args.root.resolve()
        if args.output:
            output_path = args.output.resolve()
            if output_path == root or root in output_path.parents:
                relative = output_path.relative_to(root).as_posix()
                tracked_output = git(root, "ls-files", "--error-unmatch", "--", relative, optional=True)
                if not relative.startswith("artifacts/") or tracked_output is not None:
                    raise EvidenceError("JSON output must be outside the checkout or an untracked artifacts/ file.")
            output_safe = True
        tasks = load_tasks(root)
        base_sha = git(root, "rev-parse", args.base + "^{commit}").strip()
        base = load_tasks(root, base_sha)
        before = source(root, tasks)
        branch = args.branch or os.environ.get("GITHUB_HEAD_REF") or git(root, "branch", "--show-current").strip()
        if args.ci_pr and args.task:
            raise EvidenceError("--ci-pr and --task serve different validation modes.")
        if args.ci_pr and args.offline:
            raise EvidenceError("PR Quality requires live GitHub evidence; --offline cannot validate a claim.")
        if args.ci_pr and git(root, "merge-base", "--is-ancestor", base_sha, "HEAD", optional=True) is None:
            raise EvidenceError("Test merge is behind current main; update the branch and rerun CI.")
        focus = focus_for_branch(tasks, branch) if args.ci_pr else None
        # --no-renames includes both old and new paths in scope validation.
        changed = git(root, "diff", "--no-renames", "--name-only", "-z", base_sha, "--").split("\0")
        changed = [p for p in changed if p]
        changed += [p for p in git(root, "ls-files", "--others", "--exclude-standard", "-z").strip("\0").split("\0")
                    if not p.startswith("artifacts/")]
        changed = sorted(set(p for p in changed if p))
        for path in list(changed):
            candidate = root / path
            if candidate.is_symlink():
                destination = candidate.resolve()
                if root not in destination.parents:
                    raise EvidenceError(f"{path}: changed symlink escapes the approved checkout.")
                changed.append(destination.relative_to(root).as_posix())
        selected = {tid: t for tid, t in tasks.items() if (focus is None or tid in focus)
                    and not t["archived"] and not historical(t, base)
                    and (t["meta"]["status"] != "Done" or tid not in base or base[tid]["meta"]["status"] != "Done")}
        live = None if args.offline else collect(root, args.repository, selected, base_sha)
        report.update(validate(tasks, base, args.repository, live, args.task, branch, changed, focus))
        report.update({"source": before, "base_sha": base_sha, "branch": branch,
                       "repository": args.repository, "changed_paths": changed})
        if live:
            report["remote"] = {k: live[k] for k in ("default_branch", "default_sha", "collected_at", "claims")}
        if source(root, load_tasks(root)) != before:
            raise EvidenceError("Source changed during validation; rerun on stable source.")
    except (EvidenceError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        # No raw API responses, subprocess commands, issue text or tokens in logs.
        report["status"] = "fail"
        report["claim_verified"] = False
        report["errors"].append(str(error) if isinstance(error, EvidenceError) else "Evidence could not be read or parsed.")
    output = json.dumps(report, indent=2) + "\n"
    if args.output and output_safe:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
