"""Advisory assessment. Only trusted default-branch code may collect live evidence."""

import argparse
import datetime
import html
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

MAX_FILES = 10
MAX_LINES = 200
SHA = re.compile(r"[0-9a-f]{40}")


def allowed_document(path):
    if path == "README.md":
        return True
    parts = PurePosixPath(path).parts
    return (
        path.startswith("docs/usage/")
        and path.endswith(".md")
        and len(parts) >= 3
        and all(re.fullmatch(r"[a-z0-9][a-z0-9-]*", p) for p in parts[2:-1])
        and re.fullmatch(r"[a-z0-9][a-z0-9-]*\.md", parts[-1]) is not None
        and parts[-1] not in {"agents.md", "skill.md", "security.md"}
        and str(PurePosixPath(path)) == path
    )


def assess(evidence):
    """Missing/ambiguous evidence always requires human review."""
    if not isinstance(evidence, dict):
        evidence = {}
    reasons = []
    try:
        pr, files = evidence["pr"], evidence["files"]
        head, base = pr["head"]["sha"], pr["base"]["sha"]
        if not all(isinstance(s, str) and SHA.fullmatch(s) for s in
                   (head, base, evidence["policy_sha"], pr["merge_commit_sha"])):
            reasons.append("Missing or invalid commit identity.")
        if pr["state"] != "open" or pr["draft"] is not False:
            reasons.append("PR must be open and ready for review.")
        if pr["head"]["repo"]["full_name"] != pr["base"]["repo"]["full_name"]:
            reasons.append("Fork contributions require review.")
        if pr["base"]["ref"] != evidence["default_branch"]:
            reasons.append("Only the default branch is eligible.")
        if base != evidence["policy_sha"] or base != evidence["latest_base_sha"]:
            reasons.append("Policy/base changed; refresh evidence and rerun CI.")
        if pr["mergeable"] is not True or pr["mergeable_state"] != "clean":
            reasons.append("Mergeability is unknown, blocked, conflicting, or out of date.")
        labels = {label["name"].lower() for label in pr["labels"]}
        if labels & {"do-not-merge", "no-auto-merge", "needs-review", "security"}:
            reasons.append("A review/merge veto label is set.")
        if not files or len(files) != pr["changed_files"] or len(files) > MAX_FILES:
            reasons.append("Changed-file evidence is empty, incomplete, or exceeds 10 files.")
        total = 0
        if len({f["filename"] for f in files}) != len(files):
            reasons.append("Duplicate file evidence.")
        for file in files:
            path = file["filename"]
            if not allowed_document(path):
                reasons.append(f"Outside the documentation allowlist: {path}")
            if file["status"] not in {"added", "modified"} or file.get("previous_filename"):
                reasons.append(f"Deletion/rename/type change requires review: {path}")
            if file["mode"] != "100644" or not file.get("patch"):
                reasons.append(f"Non-regular, binary, or unavailable patch: {path}")
            counts = [file["additions"], file["deletions"], file["changes"]]
            if any(type(n) is not int or n < 0 for n in counts) or sum(counts[:2]) != counts[2]:
                reasons.append(f"Invalid change counts: {path}")
            total += file["changes"]
        if total > MAX_LINES or total != pr["additions"] + pr["deletions"]:
            reasons.append("Diff exceeds 200 changed lines or totals are inconsistent.")
        quality = evidence["quality"]
        if not (
            quality["conclusion"] == "success"
            and quality["head_sha"] == head
            and quality["merge_sha"] == pr["merge_commit_sha"]
            and quality["workflow_path"] == ".github/workflows/ci.yml"
            and quality["event"] == "pull_request"
        ):
            reasons.append("No successful CI Quality check for the current PR and merge commit.")
        # COMMENTED reviews do not revoke a previous approval or change request.
        latest = {}
        for review in evidence["reviews"]:
            if review["state"] in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
                latest[review["user"]["login"]] = review
        if any(r["state"] == "CHANGES_REQUESTED" for r in latest.values()):
            reasons.append("An active review requests changes.")
        if not any(
            r["state"] == "APPROVED" and r["commit_id"] == head
            and r["user"]["type"] == "User"
            and r["user"]["login"] != pr["user"]["login"]
            and r["author_association"] in {"OWNER", "MEMBER", "COLLABORATOR"}
            for r in latest.values()
        ):
            reasons.append("A current independent human approval is required.")
    except (KeyError, TypeError, ValueError, AttributeError):
        reasons.append("Required evidence is missing or malformed.")
    pr_metadata = evidence.get("pr")
    pr_metadata = pr_metadata if isinstance(pr_metadata, dict) else {}
    head_metadata, base_metadata = pr_metadata.get("head"), pr_metadata.get("base")
    return {
        "schema_version": 1,
        "decision": "manual-review" if reasons else "low-risk-candidate",
        "auto_merge_candidate": not reasons,
        "merge_authorized": False,
        "head_sha": head_metadata.get("sha") if isinstance(head_metadata, dict) else None,
        "base_sha": base_metadata.get("sha") if isinstance(base_metadata, dict) else None,
        "policy_sha": evidence.get("policy_sha"),
        "reasons": reasons or ["Small documentation diff, current CI, and independent approval."],
        "remaining_controls": [
            "GitHub must enforce required checks, current approvals, and resolved conversations.",
            "Recheck live head/base identities and policy immediately before any merge action.",
            "This report does not enable, authorize, or perform a merge.",
        ],
    }


def api(path):
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def pages(path):
    values = []
    # GitHub's files API caps responses at 3,000 files; count mismatch fails closed.
    for page in range(1, 31):
        batch = api(f"{path}?per_page=100&page={page}")
        values.extend(batch)
        if len(batch) < 100:
            return values
    return values


def collect(repo, number):
    prefix = f"/repos/{repo}"
    metadata = api(prefix)
    policy = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    pr = api(f"{prefix}/pulls/{number}")
    files = pages(f"{prefix}/pulls/{number}/files")
    tree = api(f"{prefix}/git/trees/{pr['head']['sha']}?recursive=1")
    modes = {} if tree.get("truncated") else {f["path"]: f["mode"] for f in tree["tree"]}
    for file in files:
        file["mode"] = modes.get(file["filename"])
    quality = {}
    merge_sha = pr.get("merge_commit_sha")
    if merge_sha and SHA.fullmatch(merge_sha):
        checks = api(
            f"{prefix}/commits/{pr['head']['sha']}/check-runs?check_name=Quality&filter=latest&per_page=100"
        )["check_runs"]
        for check in checks:
            match = re.fullmatch(
                rf"https://github\.com/{re.escape(repo)}/actions/runs/(\d+)/job/\d+",
                check.get("details_url", ""),
            )
            if (check["app"]["slug"] != "github-actions" or not match
                    or check["name"] != "Quality" or check["status"] != "completed"):
                continue
            run = api(f"{prefix}/actions/runs/{match[1]}")
            tested_merge = re.fullmatch(r"CI ([0-9a-f]{40})", run.get("display_title", ""))
            if (run["path"] == ".github/workflows/ci.yml"
                    and run["head_sha"] == pr["head"]["sha"] and tested_merge):
                quality = {"conclusion": check["conclusion"], "head_sha": run["head_sha"],
                           "merge_sha": tested_merge[1], "workflow_path": run["path"], "event": run["event"]}
                break
    latest_base = api(f"{prefix}/branches/{urllib.parse.quote(metadata['default_branch'], safe='')}")
    # A force-push while collecting evidence must not produce a candidate.
    refreshed = api(f"{prefix}/pulls/{number}")
    if (refreshed["head"]["sha"], refreshed["base"]["sha"]) != (pr["head"]["sha"], pr["base"]["sha"]):
        quality = {}
    return {"pr": pr, "files": files, "quality": quality, "policy_sha": policy,
            "latest_base_sha": latest_base["commit"]["sha"],
            "default_branch": metadata["default_branch"],
            "reviews": pages(f"{prefix}/pulls/{number}/reviews")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Assess an offline evidence JSON file")
    parser.add_argument("--collect", type=int, help="Collect read-only evidence for a PR number")
    parser.add_argument("--output", type=Path, default=Path("artifacts/pr-safety.json"))
    args = parser.parse_args()
    if bool(args.input) == bool(args.collect):
        parser.error("Specify exactly one of --input or --collect")
    try:
        evidence = json.loads(args.input.read_text()) if args.input else collect(
            os.environ["GITHUB_REPOSITORY"], args.collect)
        report = assess(evidence)
    except Exception as error:
        # Never print tokens or remote response bodies into logs/artifacts.
        report = assess({})
        report["reasons"].append(f"Evidence collection failed ({type(error).__name__}).")
    report["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write("## PR safety: " + report["decision"] + "\n\n")
            summary.write("Advisory only. No merge is authorized.\n\n<pre>" +
                          html.escape(json.dumps(report, indent=2)) + "</pre>\n")
    print(report["decision"] + ": " + str(len(report["reasons"])) + " assessment reason(s).")


if __name__ == "__main__":
    main()
