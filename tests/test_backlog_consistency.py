"""Task-link guard rules, exercised with native records, API-shaped fixtures and real Git."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


SPEC = importlib.util.spec_from_file_location(
    "backlog_consistency", Path(__file__).resolve().parents[1] / "scripts/backlog_consistency.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)
REPO = "example/project"
ISSUE = f"https://github.com/{REPO}/issues/1"


def record(number=80, status="To Do", deps=(), archived=False, assignee=(), checked=None,
           scope=None, branch=None, issue=ISSUE):
    tid = f"TASK-{number}"
    path = f"backlog/{'archive/' if archived else ''}tasks/task-{number} - Fixture.md"
    dependency = "\n".join(f"  - {x}" for x in deps)
    owners = "\n".join(f"  - {x}" for x in assignee)
    checked = status == "Done" if checked is None else checked
    scope = f"scripts/feature-{number}.py; docs/feature/**" if scope is None else scope
    branch = f"agent/task-{number}" if branch is None else branch
    text = f"""---
id: {tid}
title: Fixture
status: {status}
assignee:{'' if assignee else ' []'}
{owners}
references:
  - {issue}
dependencies:{'' if deps else ' []'}
{dependency}
---
## Description
Issue: {issue}
Branch: {branch}
Scope: {scope}
Verify: python3 -B scripts/quality.py
## Acceptance Criteria
<!-- AC:BEGIN -->
- [{'x' if checked else ' '}] #1 Observable outcome {number}.
<!-- AC:END -->
"""
    return guard.parse_task(text, path)


def tasks(*records):
    return {t["id"]: t for t in records}


def live(pulls=(), state="open", labels=("approved",)):
    return {"issues": {ISSUE: {"state": state, "labels": [{"name": n} for n in labels]}},
            "pulls": list(pulls)}


def pull(number=1, branch="agent/task-80", merged=False, title="Change"):
    return {"number": number, "state": "closed" if merged else "open", "title": title,
            "head": {"ref": branch}, "merged_at": "2026-11-02T00:00:00Z" if merged else None}


class NativeReaderTests(unittest.TestCase):
    def test_native_folded_paths_quoted_lists_and_commas(self):
        text = """---
id: TASK-1
title: 'Owner''s task, with punctuation'
status: To Do
references: ['one, two', "three"]
modified_files:
  - >-
    backlog/tasks/task-1 -
    Fixture.md
dependencies: []
---
"""
        task = guard.parse_task(text, "backlog/tasks/task-1 - Fixture.md")
        self.assertEqual(task["meta"]["references"], ["one, two", "three"])
        self.assertEqual(task["meta"]["modified_files"], ["backlog/tasks/task-1 - Fixture.md"])
        self.assertEqual(task["meta"]["title"], "Owner's task, with punctuation")

    def test_malformed_duplicate_or_executable_yaml_fails_closed(self):
        original = "---\nid: TASK-1\nstatus: To Do\nreferences: []\n---\n"
        for header in [original.replace("id: TASK-1", "id: TASK-2"),
                       original.replace("references: []", "status: Done"),
                       original.replace("references: []", "references: !!python/object:malicious"),
                       original.replace("references: []", "references: *other"),
                       original.replace("references: []", "references: [unterminated")]:
            with self.subTest(header=header), self.assertRaises((guard.EvidenceError, ValueError)):
                guard.parse_task(header, "backlog/tasks/task-1 - Fixture.md")


class SpecTests(unittest.TestCase):
    def test_required_fields(self):
        info = guard.spec(record(), REPO)
        self.assertEqual(info, {"issue": ISSUE, "branch": "agent/task-80",
                                "scope": ["scripts/feature-80.py", "docs/feature/**"]})
        for broken, message in [(record(branch="main"), "Branch"), (record(scope=""), "Scope"),
                                (record(issue="https://github.com/other/repo/issues/1"), "Issue")]:
            with self.subTest(message=message), self.assertRaisesRegex(guard.EvidenceError, message):
                guard.spec(broken, REPO)

    def test_scope_ignores_backlog_and_prose_and_rejects_escapes(self):
        task = record(scope="backlog/tasks/task-80 - Fixture.md; this task's own record; apps/web/**")
        self.assertEqual(guard.scope_patterns(task), ["apps/web/**"])
        for bad in ("../outside.py", "/etc/passwd", "**", ".git/config"):
            with self.subTest(bad=bad), self.assertRaises(guard.EvidenceError):
                guard.scope_patterns(record(scope=bad))

    def test_approval_is_an_open_issue_with_the_approved_label(self):
        self.assertIsNone(guard.issue_problem(live()["issues"][ISSUE]))
        self.assertIn("not labeled", guard.issue_problem(live(labels=())["issues"][ISSUE]))
        self.assertIn("not open", guard.issue_problem(live(state="closed")["issues"][ISSUE]))
        self.assertIn("could not be read", guard.issue_problem(None))


class PullRequestTests(unittest.TestCase):
    def check(self, current, base=None, evidence=None, changed=("scripts/feature-80.py",),
              branch="agent/task-80", author="agent"):
        return guard.check_pr(current, base if base is not None else current, REPO,
                              evidence or live(), branch, list(changed), author)

    def test_valid_pr_passes(self):
        result = self.check(tasks(record(status="In Progress", assignee=["@agent"])))
        self.assertEqual((result["errors"], result["task"]), ([], "TASK-80"))

    def test_dependabot_and_backlog_only_changes_are_exempt(self):
        self.assertEqual(self.check({}, author="dependabot[bot]", changed=["apps/web/package.json"])["exempt"],
                         "author dependabot[bot]")
        result = self.check({}, changed=["backlog/tasks/task-81 - New.md"], branch="agent/intake")
        self.assertEqual((result["errors"], result["exempt"]), ([], "Backlog records only"))

    def test_branch_needs_exactly_one_task(self):
        self.assertIn("found none", self.check(tasks(record()), branch="agent/other")["errors"][0])
        twins = tasks(record(80), record(81, branch="agent/task-80"))
        self.assertIn("found TASK-80, TASK-81", self.check(twins)["errors"][0])

    def test_unapproved_or_closed_issue_blocks(self):
        self.assertIn("TASK-80: linked issue is not labeled `approved`",
                      self.check(tasks(record()), evidence=live(labels=()))["errors"])
        self.assertIn("TASK-80: linked issue is not open",
                      self.check(tasks(record()), evidence=live(state="closed"))["errors"])

    def test_changed_paths_must_be_in_scope_except_backlog(self):
        changed = ["scripts/feature-80.py", "docs/feature/a.md", "backlog/tasks/task-99 - Follow-up.md",
                   ".github/workflows/ci.yml"]
        self.assertEqual(self.check(tasks(record()), changed=changed)["errors"],
                         ["TASK-80: changed path outside Scope: .github/workflows/ci.yml"])

    def test_dependencies_must_be_done_on_main(self):
        branch_done = tasks(record(80, deps=["TASK-70"]), record(70, status="Done"))
        main = tasks(record(80, deps=["TASK-70"]), record(70, status="In Progress"))
        self.assertIn("TASK-80: dependencies are not complete on main: TASK-70",
                      self.check(branch_done, base=main)["errors"])
        self.assertEqual(self.check(branch_done, base=branch_done)["errors"], [])

    def test_merged_in_progress_dependency_with_checked_acceptance_counts(self):
        main = tasks(record(80, deps=["TASK-70"]), record(70, status="In Progress", checked=True))
        merged = live([pull(5, "agent/task-70", merged=True)])
        self.assertEqual(self.check(main, evidence=merged)["errors"], [])
        unchecked = tasks(record(80, deps=["TASK-70"]), record(70, status="In Progress"))
        self.assertTrue(self.check(unchecked, evidence=merged)["errors"])

    def test_archived_unfinished_dependency_is_not_complete(self):
        main = tasks(record(80, deps=["TASK-70"]), record(70, archived=True))
        self.assertTrue(self.check(main)["errors"])

    def test_proposed_done_needs_checked_acceptance(self):
        base = tasks(record(status="In Progress"))
        done = tasks(record(status="Done"))
        self.assertEqual(self.check(done, base=base)["errors"], [])
        unchecked = tasks(record(status="Done", checked=False))
        self.assertIn("TASK-80: Done requires every acceptance criterion checked",
                      self.check(unchecked, base=base)["errors"])

    def test_task_already_done_on_main_cannot_take_new_work(self):
        done = tasks(record(status="Done"))
        self.assertIn("found none", self.check(done, base=done)["errors"][0])

    def test_competing_open_pr_naming_the_task_blocks(self):
        evidence = live([pull(9, "agent/elsewhere", title="[TASK-80] Duplicate")])
        self.assertIn("TASK-80: another open PR names this task: #9",
                      self.check(tasks(record()), evidence=evidence)["errors"])

    def test_to_do_task_only_warns(self):
        result = self.check(tasks(record()))
        self.assertEqual(result["errors"], [])
        self.assertIn("claim it before review", result["warnings"][0])

    def test_unknown_dependency_and_cycles(self):
        self.assertIn("TASK-80: unknown dependency TASK-9", self.check(tasks(record(deps=["TASK-9"])))["errors"])
        cycle = tasks(record(80, deps=["TASK-81"]), record(81, deps=["TASK-80"]))
        self.assertTrue(any("cyclic" in e for e in guard.structure(cycle)))


class ClaimTests(unittest.TestCase):
    def claim(self, current, evidence=None, branch="agent/task-80"):
        return guard.check_claim(current, current, REPO, evidence or live(), "TASK-80", branch)["errors"]

    def test_unassigned_approved_task_can_be_claimed_and_resumed(self):
        self.assertEqual(self.claim(tasks(record())), [])
        self.assertEqual(self.claim(tasks(record(status="In Progress", assignee=["@me"]))), [])

    def test_claim_rejections(self):
        cases = {
            "already assigned": (tasks(record(assignee=["@other"])), live(), "agent/task-80"),
            "recorded branch": (tasks(record()), live(), "agent/wrong"),
            "missing, archived or Done": (tasks(record(status="Done")), live(), "agent/task-80"),
            "already has a merged PR": (tasks(record()), live([pull(merged=True)]), "agent/task-80"),
            "another open PR": (tasks(record()), live([pull(3, "x", title="TASK-80 fix")]), "agent/task-80"),
            "not labeled": (tasks(record()), live(labels=("bug",)), "agent/task-80"),
        }
        for reason, (current, evidence, branch) in cases.items():
            with self.subTest(reason=reason):
                self.assertTrue(any(reason in e for e in self.claim(current, evidence, branch)))


class AuditTests(unittest.TestCase):
    def test_audit_warns_on_drift_and_errors_on_structure(self):
        current = tasks(record(80, status="In Progress"), record(81, scope=""), record(82, branch="agent/task-80"))
        result = guard.audit(current, current, REPO, live([pull(merged=True)], labels=()))
        self.assertEqual(result["errors"], ["TASK-82: branch agent/task-80 is also recorded by TASK-80"])
        self.assertIn("TASK-80: PR merged but task is still In Progress; finish or split the remaining work",
                      result["warnings"])
        self.assertIn("TASK-81: not executable: task needs a `Scope:` line listing the paths it may change",
                      result["warnings"])
        offline = guard.audit(current, current, REPO, None)
        self.assertFalse(any("issue" in w for w in offline["warnings"]))


class CollectionAndCliTests(unittest.TestCase):
    def test_pagination_reads_all_pages_and_rejects_inconclusive_data(self):
        client = object.__new__(guard.GitHub)
        with patch.object(client, "get", side_effect=[[{}] * 100, [{"id": 101}]]):
            self.assertEqual(len(client.pages("pulls?state=all")), 101)
        with patch.object(client, "get", return_value={"message": "unavailable"}):
            with self.assertRaises(guard.EvidenceError):
                client.pages("pulls")

    def test_http_errors_never_expose_tokens_and_requests_are_get_only(self):
        with patch.dict("os.environ", {"GH_TOKEN": "must-not-leak"}):
            client = guard.GitHub(REPO)
        failure = HTTPError("private-url", 403, "raw must-not-leak", {}, None)
        with patch.object(guard, "urlopen", side_effect=failure) as request:
            with self.assertRaises(guard.EvidenceError) as raised:
                client.get("")
        self.assertNotIn("must-not-leak", str(raised.exception))
        req = request.call_args.args[0]
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(req.full_url, f"https://api.github.com/repos/{REPO}")

    def test_cli_on_a_real_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)

            commit = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                      "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit")
            git("init", "-b", "main")
            task = root / "backlog/tasks/task-80 - Fixture.md"
            task.parent.mkdir(parents=True)
            task.write_text("---\nid: TASK-80\nstatus: To Do\n---\n")
            git("add", ".")
            git(*commit, "-m", "base")
            git("switch", "-c", "agent/intake")
            (root / "backlog/tasks/task-81 - New.md").write_text("---\nid: TASK-81\nstatus: To Do\n---\n")
            self.assertEqual(guard.changed_paths(root, "main"), ["backlog/tasks/task-81 - New.md"])

            def run(*args):
                with patch("sys.stdout", new_callable=io.StringIO) as output:
                    code = guard.main(["--root", str(root), "--base", "main", *args])
                return code, json.loads(output.getvalue())

            code, report = run("--offline")
            self.assertEqual((code, report["mode"], report["status"]), (0, "audit", "pass"))
            with patch.object(guard, "GitHub", side_effect=AssertionError("exempt PRs need no GitHub calls")):
                code, report = run("--pr", "--branch", "agent/intake")
                self.assertEqual((code, report["exempt"]), (0, "Backlog records only"))
                (root / "app.py").write_text("print()\n")
                code, report = run("--pr", "--branch", "agent/intake", "--author", "dependabot[bot]")
                self.assertEqual((code, report["exempt"]), (0, "author dependabot[bot]"))
            code, report = run("--pr", "--offline")
            self.assertEqual(code, 1)
            self.assertIn("audit-only", report["errors"][0])
            snapshot = task.read_bytes()
            code, report = run("--offline", "--output", str(task))
            self.assertEqual((code, task.read_bytes()), (1, snapshot))
            duplicate = root / "backlog/archive/tasks/task-80 - Duplicate.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text("---\nid: TASK-80\nstatus: Done\n---\n")
            with self.assertRaisesRegex(guard.EvidenceError, "duplicate native ID"):
                guard.load_tasks(root)


if __name__ == "__main__":
    unittest.main()
