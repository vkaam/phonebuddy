"""Run local baseline checks and retain source-bound evidence (Python 3.9+)."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, timeout=15,
    ).stdout


def snapshot(root):
    """Include tracked changes, deletions, and non-ignored untracked files."""
    names = sorted(set(git(root, "ls-files", "--cached", "--others",
                           "--exclude-standard", "-z").split(b"\0")) - {b""})
    manifest = []
    for raw in names:
        name = os.fsdecode(raw)
        path = root / name
        if path.is_symlink():
            entry = {"path": name, "kind": "symlink",
                     "sha256": digest(os.fsencode(os.readlink(path)))}
        elif path.is_file():
            entry = {"path": name, "kind": "file",
                     "mode": path.stat().st_mode & 0o777,
                     "sha256": digest(path.read_bytes())}
        elif not path.exists():
            entry = {"path": name, "kind": "deleted"}
        else:
            raise ValueError(f"Unsupported source entry: {name}")
        manifest.append(entry)
    return {
        "head": git(root, "rev-parse", "HEAD").decode().strip(),
        "status": git(root, "status", "--porcelain=v1", "--untracked-files=all").decode(),
        "manifest_sha256": digest(json.dumps(manifest, sort_keys=True).encode()),
        "manifest": manifest,
    }


def run_check(name, command, root, output, timeout):
    started = time.monotonic()
    log = output / f"{name}.txt"
    with log.open("wb") as stream:
        try:
            result = subprocess.run(command, cwd=root, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
            code = result.returncode
            status = "pass" if code == 0 else "fail"
        except subprocess.TimeoutExpired:
            code, status = None, "timeout"
        except OSError as exc:
            stream.write(str(exc).encode())
            code, status = None, "error"
    return {"name": name, "command": command, "cwd": str(root),
            "status": status, "exit_code": code, "timeout_seconds": timeout,
            "duration_seconds": round(time.monotonic() - started, 3),
            "log": log.name, "log_sha256": digest(log.read_bytes())}


def write_bundle(root, output, checks, timeout):
    report = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(),
        "kind": "local-baseline", "hosted_ci": False,
        "independent_review": "not run", "checks": [], "errors": [],
        "outstanding_checks": ["lint", "browser smoke", "dependency vulnerability scan",
                               "hosted CI", "actionlint", "Gitleaks"],
    }
    try:
        report["source_before"] = snapshot(root)
        for name, command in checks:
            report["checks"].append(run_check(name, command, root, output, timeout))
        report["source_after"] = snapshot(root)
        report["source_unchanged"] = report["source_before"] == report["source_after"]
        if not report["source_unchanged"]:
            report["errors"].append("Source changed during checks; rerun on stable source.")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["errors"].append(str(exc))
    report["status"] = "pass" if (
        not report["errors"] and len(report["checks"]) == len(checks)
        and all(check["status"] == "pass" for check in report["checks"])
    ) else "fail"
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-parent", type=Path, default=Path(tempfile.gettempdir()),
                        help="Existing directory outside the checkout for a unique bundle")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout per check in seconds (1–600; default 120)")
    args = parser.parse_args(argv)
    parent = args.output_parent.resolve()
    if not 1 <= args.timeout <= 600:
        parser.error("--timeout must be between 1 and 600")
    if parent == ROOT or ROOT in parent.parents or not parent.is_dir():
        parser.error("--output-parent must be an existing directory outside the checkout")
    output = Path(tempfile.mkdtemp(prefix="phonebuddy-quality-", dir=parent))
    checks = [
        ("repository", [sys.executable, "-B", "scripts/quality.py"]),
        ("tests", [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("node-version", ["node", "--version"]),
        ("npm-version", ["npm", "--version"]),
        ("web-install", ["npm", "--prefix", "apps/web", "ci", "--no-audit", "--no-fund"]),
        ("web-dependencies", ["npm", "--prefix", "apps/web", "ls", "--all", "--json"]),
        ("web-test", ["npm", "--prefix", "apps/web", "test"]),
        ("web-build", ["npm", "--prefix", "apps/web", "run", "build"]),
    ]
    report = write_bundle(ROOT, output, checks, args.timeout)
    print(f"Local baseline: {report['status']}; evidence: {output / 'report.json'}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
