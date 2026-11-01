"""Exercise runner outcomes and source identity using real subprocesses."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "check", Path(__file__).resolve().parents[1] / "scripts/check.py")
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_success_failure_and_log_digest(self):
        for code, status in [(0, "pass"), (7, "fail")]:
            result = check.run_check(
                f"exit-{code}", [sys.executable, "-c", f"print('result'); exit({code})"],
                self.root, self.root, 5)
            self.assertEqual(result["status"], status)
            self.assertEqual(result["exit_code"], code)
            data = (self.root / result["log"]).read_bytes()
            self.assertIn(b"result", data)
            self.assertEqual(result["log_sha256"], hashlib.sha256(data).hexdigest())

    def test_timeout_and_missing_executable(self):
        result = check.run_check("timeout", [sys.executable, "-c",
                                 "import time; time.sleep(30)"], self.root, self.root, .05)
        self.assertEqual(result["status"], "timeout")
        self.assertIsNone(result["exit_code"])
        result = check.run_check("missing", [str(self.root / "absent")],
                                 self.root, self.root, 1)
        self.assertEqual(result["status"], "error")

    def test_bundle_pass_failure_and_changed_source(self):
        command = [sys.executable, "-c", "pass"]
        for code, changed, expected in [(0, False, "pass"), (3, False, "fail"),
                                         (0, True, "fail")]:
            with self.subTest(code=code, changed=changed):
                with patch.object(check, "snapshot", side_effect=[{"head": "a"},
                                  {"head": "b" if changed else "a"}]):
                    report = check.write_bundle(self.root, self.root,
                                                [("check", command + [])] if code == 0 else
                                                [("check", [sys.executable, "-c", "exit(3)"])], 5)
                self.assertEqual(report["status"], expected)
                self.assertEqual(report["source_unchanged"], not changed)
                saved = json.loads((self.root / "report.json").read_text())
                self.assertEqual(saved, report)
                self.assertFalse(saved["hosted_ci"])
                self.assertEqual(saved["independent_review"], "not run")
                self.assertIn("hosted CI", saved["outstanding_checks"])

    def test_main_registers_web_checks_as_required(self):
        with patch.object(check, "write_bundle", return_value={"status": "pass"}) as bundle:
            self.assertEqual(check.main(["--output-parent", str(self.root)]), 0)
        checks = dict(bundle.call_args.args[2])
        self.assertEqual(checks["node-version"], ["node", "--version"])
        self.assertEqual(checks["npm-version"], ["npm", "--version"])
        self.assertEqual(checks["web-install"],
                         ["npm", "--prefix", "apps/web", "ci", "--no-audit", "--no-fund"])
        self.assertEqual(checks["web-test"][-1], "test")
        self.assertEqual(checks["web-build"][-2:], ["run", "build"])
        self.assertEqual(checks["web-dependencies"][-2:], ["--all", "--json"])
        self.assertEqual(checks["web-audit"], ["npm", "--prefix", "apps/web", "audit"])
        self.assertEqual(checks["web-lint"], ["npm", "--prefix", "apps/web", "run", "lint"])
        self.assertEqual(checks["web-browser"],
                         ["npm", "--prefix", "apps/web", "run", "test:browser"])

    def test_missing_required_check_fails_bundle(self):
        with patch.object(check, "snapshot", return_value={"head": "a"}):
            report = check.write_bundle(self.root, self.root,
                                        [("web-install", [str(self.root / "missing")])], 1)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["checks"][0]["status"], "error")

    def test_snapshot_error_still_writes_failed_report(self):
        with patch.object(check, "snapshot", side_effect=ValueError("unavailable")):
            report = check.write_bundle(self.root, self.root, [], 1)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["errors"], ["unavailable"])

    def test_snapshot_tracks_untracked_modified_deleted_and_ignored_files(self):
        def git(*args):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

        git("init")
        (self.root / "tracked.md").write_text("original\n")
        (self.root / ".gitignore").write_text("ignored\n")
        git("add", ".")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
        initial = check.snapshot(self.root)
        (self.root / "ignored").write_text("not captured")
        self.assertEqual(initial, check.snapshot(self.root))
        (self.root / "new.md").write_text("untracked\n")
        untracked = check.snapshot(self.root)
        self.assertNotEqual(initial["manifest_sha256"], untracked["manifest_sha256"])
        (self.root / "tracked.md").write_text("modified\n")
        modified = check.snapshot(self.root)
        self.assertNotEqual(untracked["manifest_sha256"], modified["manifest_sha256"])
        (self.root / "tracked.md").unlink()
        deleted = check.snapshot(self.root)
        self.assertIn({"path": "tracked.md", "kind": "deleted"}, deleted["manifest"])

    def test_cli_rejects_checkout_output_and_invalid_timeout(self):
        for args in [["--output-parent", str(check.ROOT)], ["--timeout", "0"]]:
            with self.subTest(args=args), self.assertRaises(SystemExit) as raised:
                check.main(args)
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
