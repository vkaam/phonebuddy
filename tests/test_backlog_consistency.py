"""Seed policy failures using native records, live evidence fixtures and real Git."""

from copy import deepcopy
import hashlib
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
DIGEST = hashlib.sha256(b"approved intent").hexdigest()


def record(number=80, status="To Do", deps=(), archived=False, created="2026-11-02", issue=ISSUE):
    tid = f"TASK-{number}"
    path = f"backlog/{'archive/' if archived else ''}tasks/task-{number} - Fixture.md"
    dependency = "\n".join(f"  - {x}" for x in deps)
    text = f"""---
id: {tid}
title: Fixture
status: {status}
created_date: '{created}T00:00:00Z'
assignee: []
labels: []
references:
  - {issue}
dependencies:{'' if deps else ' []'}
{dependency}
---
## Description
Issue: {issue}
Approved revision: 2026-11-02T00:00:00Z; SHA-256 {DIGEST}.
Approval evidence: direct owner instruction with pinned requirements.
Branch: agent/task-{number}
Scope: scripts/feature-{number}.py; {path}
Verify: from repository root run python3 -B scripts/quality.py; hosted Quality required.
## Acceptance Criteria
<!-- AC:BEGIN -->
- [{'x' if status == 'Done' else ' '}] #1 Observable outcome {number} verified, including failure cases.
<!-- AC:END -->
"""
    return guard.parse_task(text, path)


def live(claims=(), pulls=(), state="open", body="approved intent"):
    return {"issues": {ISSUE: {"state": state, "body": body}}, "claims": list(claims),
            "pulls": list(pulls), "default_branch": "main", "default_sha": "a" * 40}


def pull(number=1, branch="agent/task-80", merged=False, source_repo=REPO):
    return {"number": number, "state": "closed" if merged else "open",
            "head": {"ref": branch, "sha": "b" * 40, "repo": {"full_name": source_repo}},
            "base": {"ref": "main"}, "merged_at": "2026-11-02" if merged else None,
            "merge_commit_sha": "c" * 40, "on_default_branch": merged}


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


class ConsistencyTests(unittest.TestCase):
    def run_guard(self, records, base=None, remote=None, **options):
        return guard.validate({r["id"]: r for r in records}, base or {}, REPO,
                              live() if remote is None else remote, **options)

    def assertFails(self, result, fragment):
        self.assertEqual(result["status"], "fail", result)
        self.assertTrue(any(fragment in e for e in result["errors"]), result)

    def test_valid_claim_and_distinct_slices_of_same_issue(self):
        a, b = record(), record(81)
        result = self.run_guard([a, b], target=a["id"], branch="agent/task-80")
        self.assertEqual(result["status"], "pass", result)
        self.assertTrue(result["claim_verified"])

    def test_pr_focus_ignores_unrelated_closed_issue_but_rejects_own_claim(self):
        other_issue = f"https://github.com/{REPO}/issues/2"
        own, unrelated = record(), record(81, issue=other_issue)
        remote = live()
        remote["issues"][other_issue] = {"state": "closed", "body": "approved intent"}
        focus = guard.focus_for_branch({own["id"]: own, unrelated["id"]: unrelated}, "agent/task-80")
        self.assertEqual(focus, {"TASK-80"})
        scoped = self.run_guard([own, unrelated], remote=remote, branch="agent/task-80",
                                changed=["scripts/feature-80.py"], focus=focus)
        self.assertEqual(scoped["status"], "pass", scoped)
        self.assertFails(self.run_guard([own, unrelated], remote=remote), "TASK-81: issue is closed")

        remote["claims"] = [{"task": "TASK-80", "branch": "agent/task-80", "status": "To Do", "pr": 12}]
        self.assertFails(self.run_guard([own, unrelated], remote=remote, branch="agent/task-80",
                                        changed=["scripts/feature-80.py"], focus=focus), "unclaimed To Do")

    def test_pr_focus_includes_dependencies_and_rejects_unapproved_scope(self):
        dependency, own = record(81), record(deps=("TASK-81",), status="In Progress")
        own["meta"]["assignee"] = ["@codex"]
        tasks = {task["id"]: task for task in (own, dependency)}
        focus = guard.focus_for_branch(tasks, "agent/task-80")
        self.assertEqual(focus, {"TASK-80", "TASK-81"})
        result = self.run_guard([own, dependency], branch="agent/task-80",
                                changed=["outside/scope.py"], focus=focus)
        self.assertFails(result, "active work lacks default-branch completion")
        self.assertFails(result, "changed path outside approved scope")

    def test_missing_required_execution_metadata(self):
        for marker in ["Issue:", "Approved revision:", "Approval evidence:", "Branch:", "Scope:", "Verify:", "<!-- AC:BEGIN -->"]:
            task = record()
            task["body"] = "\n".join(line for line in task["body"].splitlines() if not line.startswith(marker))
            if marker == "<!-- AC:BEGIN -->":
                task["ac"] = []
            self.assertFails(self.run_guard([task]), "TASK-80")

    def test_scope_rejects_escaping_or_unbounded_authority(self):
        for path in ["../outside", "/absolute", "**", "${HOME}/secret", ".git/config"]:
            task = record()
            task["body"] = task["body"].replace("scripts/feature-80.py", path)
            self.assertFails(self.run_guard([task]), "Scope")
        self.assertFails(self.run_guard([record()], branch="agent/task-80", changed=["new/unapproved.py"]), "outside approved scope")
        self.assertFails(self.run_guard([record()], branch="other", changed=["scripts/feature-80.py"]), "exactly one")

    def test_existing_self_record_aliases_do_not_grant_external_notes_file_scope(self):
        for alias in ["this task record through Backlog CLI", "this task's own CLI-managed record"]:
            task = record()
            task["body"] = task["body"].replace(task["path"], alias + ". External scope: owner progress reporting")
            result = self.run_guard([task])
            self.assertEqual(result["status"], "pass", result)
            info = guard.spec(task, REPO)
            self.assertEqual(info["scope"], ["scripts/feature-80.py", task["path"]])

    def test_changed_cancelled_or_missing_issue_evidence_blocks(self):
        for remote, reason in [(live(body="edited intent"), "body changed"),
                               (live(state="closed"), "closed"),
                               ({**live(), "issues": {}}, "unavailable")]:
            self.assertFails(self.run_guard([record()], remote=remote), reason)

    def test_timestamp_only_progress_does_not_redefine_approved_body(self):
        remote = live()
        remote["issues"][ISSUE]["updated_at"] = "2026-11-02T23:59:00Z"
        self.assertEqual(self.run_guard([record()], remote=remote)["status"], "pass")

    def test_competing_claims_fork_claim_and_multiple_prs(self):
        remote = live(claims=[{"task": "TASK-80", "branch": "other", "status": "In Progress"}])
        self.assertFails(self.run_guard([record()], remote=remote), "competing")
        remote = live(claims=[{"task": "TASK-80", "branch": "agent/task-80", "status": "In Progress", "repository": "fork/project"}])
        self.assertFails(self.run_guard([record()], remote=remote, target="TASK-80", branch="agent/task-80"), "another branch or repository")
        self.assertFails(self.run_guard([record()], remote=live(pulls=[pull(), pull(2)])), "multiple PRs")

    def test_task57_style_claim_is_discovered_without_mirroring_main_status(self):
        claims = [{"task": "TASK-80", "branch": "agent/task-80", "status": "In Progress", "pr": 55}]
        self.assertEqual(self.run_guard([record()], remote=live(claims=claims))["status"], "pass")
        claims[0]["status"] = "To Do"
        self.assertFails(self.run_guard([record()], remote=live(claims=claims)), "unclaimed To Do")

    def test_exact_duplicate_decomposition_or_branch_is_rejected(self):
        a, b = record(), record(81)
        b["body"] = b["body"].replace("feature-81", "feature-80").replace("outcome 81", "outcome 80")
        b["ac"] = a["ac"]
        self.assertFails(self.run_guard([a, b]), "duplicate decomposition")
        b = record(81)
        b["body"] = b["body"].replace("Branch: agent/task-81", "Branch: agent/task-80")
        self.assertFails(self.run_guard([a, b]), "feature branch already")

    def test_branch_local_done_closed_issue_or_archival_never_satisfies_dependency(self):
        dep = record(81, status="Done")
        task = record(deps=["TASK-81"])
        for base in [{}, {"TASK-81": record(81, archived=True)}, {"TASK-81": record(81)}]:
            self.assertFails(self.run_guard([task, dep], base=base, target="TASK-80", branch="agent/task-80"), "dependencies lack")
        # A closed issue is not consulted to infer completion.
        self.assertFails(self.run_guard([task, dep], remote=live(state="closed"), target="TASK-80", branch="agent/task-80"), "dependencies lack")

    def test_completed_execution_dependency_requires_merged_default_branch_evidence(self):
        dep = record(81, status="Done")
        task = record(deps=[dep["id"]])
        base = {dep["id"]: dep}
        for pr in [pull(branch="agent/task-81"), {**pull(branch="agent/task-81", merged=True), "on_default_branch": False}]:
            self.assertFails(self.run_guard([task, dep], base, live(pulls=[pr]), target="TASK-80", branch="agent/task-80"), "dependencies lack")
        result = self.run_guard([task, dep], base, live(pulls=[pull(branch="agent/task-81", merged=True)]), target="TASK-80", branch="agent/task-80")
        self.assertTrue(result["claim_verified"], result)
        incomplete = deepcopy(dep)
        incomplete["ac"][0] = (False, incomplete["ac"][0][1])
        self.assertFails(self.run_guard([task, dep], {dep["id"]: incomplete}, live(pulls=[pull(branch="agent/task-81", merged=True)]), target="TASK-80", branch="agent/task-80"), "dependencies lack")
        reopened = deepcopy(dep)
        reopened["meta"]["status"] = "To Do"
        self.assertFails(self.run_guard([task, reopened], base, live(pulls=[pull(branch="agent/task-81", merged=True)]), target="TASK-80", branch="agent/task-80"), "dependencies lack")

    def test_merged_legacy_in_progress_record_is_effectively_complete(self):
        predecessor = record(81, status="In Progress")
        predecessor["meta"]["assignee"] = ["@codex"]
        predecessor["ac"][0] = (True, predecessor["ac"][0][1])
        follower = record(deps=("TASK-81",))
        base = {predecessor["id"]: deepcopy(predecessor)}
        remote = live(pulls=[pull(branch="agent/task-81", merged=True)])
        result = self.run_guard([predecessor, follower], base, remote,
                                target="TASK-80", branch="agent/task-80")
        self.assertTrue(result["claim_verified"], result)
        self.assertTrue(any("TASK-81: merged PR" in w for w in result["warnings"]), result)

        remote["issues"][ISSUE]["state"] = "closed"
        self.assertFails(self.run_guard([predecessor, follower], base, remote), "closed before all linked tasks")
        completed_follower = record(status="Done", deps=("TASK-81",))
        completed_base = {**base, completed_follower["id"]: deepcopy(completed_follower)}
        remote["pulls"].append(pull(number=2, merged=True))
        closed = self.run_guard([predecessor, completed_follower], completed_base, remote)
        self.assertEqual(closed["status"], "pass", closed)

        archived_unfinished = record(82, archived=True)
        with_archive = {**completed_base, archived_unfinished["id"]: deepcopy(archived_unfinished)}
        self.assertFails(self.run_guard([predecessor, completed_follower, archived_unfinished],
                                        with_archive, remote), "closed before all linked tasks")

    def test_unmerged_or_unchecked_legacy_status_does_not_complete(self):
        predecessor = record(81, status="In Progress")
        predecessor["meta"]["assignee"] = ["@codex"]
        follower = record(deps=("TASK-81",))
        base = {predecessor["id"]: deepcopy(predecessor)}
        for pr in [pull(branch="agent/task-81"), pull(branch="agent/task-81", merged=True)]:
            self.assertFails(self.run_guard([predecessor, follower], base,
                                            live(pulls=[pr]), target="TASK-80",
                                            branch="agent/task-80"), "dependencies lack")
        predecessor["ac"][0] = (True, predecessor["ac"][0][1])
        self.assertFails(self.run_guard([predecessor, follower], base,
                                        live(pulls=[pull(branch="agent/task-81", merged=True)]),
                                        target="TASK-80", branch="agent/task-80"), "dependencies lack")
        archived = record(81, status="In Progress", archived=True)
        archived["meta"]["assignee"] = ["@codex"]
        archived["ac"][0] = (True, archived["ac"][0][1])
        self.assertFails(self.run_guard([archived, follower], {archived["id"]: deepcopy(archived)},
                                        live(pulls=[pull(branch="agent/task-81", merged=True)]),
                                        target="TASK-80", branch="agent/task-80"), "dependencies lack")

    def test_imports_are_ineligible_and_new_records_cannot_backdate_exemption(self):
        old = record(created="2026-10-29")
        result = self.run_guard([old], {old["id"]: old}, target=old["id"], branch="agent/task-80")
        self.assertFails(result, "historical")
        self.assertTrue(result["warnings"])
        old["body"] = "imported context only"
        self.assertFails(self.run_guard([old]), "canonical primary")

    def test_unknown_cycles_duplicate_identity_and_deletion_are_not_ignored(self):
        self.assertFails(self.run_guard([record(deps=["TASK-999"])]), "unknown native")
        self.assertFails(self.run_guard([record(deps=["TASK-81"]), record(81, deps=["TASK-80"])]), "cyclic")
        self.assertFails(self.run_guard([], {"TASK-80": record()}), "history was removed")

    def test_migration_replacement_and_stale_downstream_edges(self):
        old, replacement = record(), record(81)
        archive = record(archived=True)
        archive["body"] += "\nReplaced by: TASK-81\n"
        child = record(82, deps=["TASK-80"])
        base = {old["id"]: old}
        self.assertFails(self.run_guard([archive, replacement, child], base), "stale migration dependency")
        self.assertFails(self.run_guard([archive, replacement, child], {archive["id"]: archive}), "stale migration dependency")
        child["meta"]["dependencies"] = ["TASK-81"]
        self.assertEqual(self.run_guard([archive, replacement, child], base)["status"], "pass")
        archive["meta"]["status"] = "Done"
        self.assertFails(self.run_guard([archive, replacement, child], base), "must not turn unfinished")

    def test_existing_unfinished_archive_cannot_be_promoted(self):
        old = record(archived=True, created="2026-10-29")
        promoted = deepcopy(old)
        promoted["meta"]["status"] = "Done"
        promoted["ac"] = [(True, promoted["ac"][0][1])]
        self.assertFails(self.run_guard([promoted], {old["id"]: old}), "must not turn unfinished")

    def test_amended_done_records_require_valid_acceptance_and_spec(self):
        for archived in (False, True):
            old = record(status="Done", archived=archived)
            self.assertEqual(self.run_guard([deepcopy(old)], {old["id"]: old})["status"], "pass")
            unchecked = deepcopy(old)
            unchecked["ac"] = [(False, unchecked["ac"][0][1])]
            self.assertFails(self.run_guard([unchecked], {old["id"]: old}), "unchecked native acceptance")
            invalid = deepcopy(old)
            invalid["body"] = invalid["body"].replace("Approval evidence:", "Removed evidence:")
            self.assertFails(self.run_guard([invalid], {old["id"]: old}), "approval evidence")

    def test_unexplained_archive_is_rejected_and_explicit_intake_stays_unfinished(self):
        old, archive = record(), record(archived=True)
        self.assertFails(self.run_guard([archive], {old["id"]: old}), "migration requires")
        archive["meta"]["labels"] = ["historical-import", "needs-triage"]
        result = self.run_guard([archive], {old["id"]: old})
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(archive["meta"]["status"], "To Do")

    def test_reusing_merged_task_and_offline_claims_fail(self):
        self.assertFails(self.run_guard([record()], remote=live(pulls=[pull(merged=True)]), target="TASK-80", branch="agent/task-80"), "already produced a merged PR")
        result = guard.validate({"TASK-80": record()}, {}, REPO, target="TASK-80", branch="agent/task-80")
        self.assertFails(result, "require live evidence")

    def test_proposed_done_and_stale_unassigned_active_records_fail(self):
        task = record(status="Done")
        task["ac"] = [(False, "Not yet verified")]
        self.assertFails(self.run_guard([task]), "unchecked native acceptance")
        task = record(status="In Progress")
        self.assertFails(self.run_guard([task]), "one explicit assignee")
        task["meta"]["assignee"] = ["@worker"]
        self.assertFails(self.run_guard([task]), "no live branch/PR")
        self.assertEqual(self.run_guard([task], branch="agent/task-80")["status"], "pass")


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

    def test_stale_default_and_truncated_branch_trees_fail_closed(self):
        client = unittest.mock.Mock()
        client.get.side_effect = [{"default_branch": "main"}, {"object": {"sha": "other"}}]
        with self.assertRaisesRegex(guard.EvidenceError, "stale"):
            guard.collect(Path.cwd(), REPO, {}, "base", client)
        client.get.side_effect = None
        client.get.return_value = {"truncated": True, "tree": []}
        with patch.object(guard, "git", return_value=None):
            with self.assertRaisesRegex(guard.EvidenceError, "Truncated"):
                guard.branch_tasks(Path.cwd(), client, "a" * 40, {"TASK-80"})

    def test_default_branch_change_during_collection_fails(self):
        client = unittest.mock.Mock()
        client.get.side_effect = [{"default_branch": "main"}, {"object": {"sha": "base"}},
                                  {"object": {"sha": "new-default"}}]
        client.pages.return_value = []
        with self.assertRaisesRegex(guard.EvidenceError, "changed during collection"):
            guard.collect(Path.cwd(), REPO, {}, "base", client)

    def test_branch_records_supply_actual_claims_and_copied_claims_are_not_owners(self):
        client = unittest.mock.Mock()
        client.get.side_effect = [{"default_branch": "main"}, {"object": {"sha": "base"}},
                                  {"state": "open", "body": "approved intent"},
                                  {"object": {"sha": "base"}}]
        client.pages.side_effect = [[], [{"name": "agent/task-80", "commit": {"sha": "own"}},
                                         {"name": "unrelated", "commit": {"sha": "copy"}}]]
        task = record(status="In Progress")
        with patch.object(guard, "branch_tasks", return_value={"TASK-80": task}):
            result = guard.collect(Path.cwd(), REPO, {"TASK-80": task}, "base", client)
        self.assertEqual([c["branch"] for c in result["claims"]], ["agent/task-80"])

    def test_real_native_duplicates_source_binding_and_cli_output_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)

            git("init")
            task = record()
            path = root / task["path"]
            path.parent.mkdir(parents=True)
            # Only fixture records are written here, never the project's native records.
            text = "---\nid: TASK-80\nstatus: Done\ncreated_date: '2026-10-29T00:00:00Z'\n---\n"
            path.write_text(text)
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "core.hooksPath=/dev/null",
                "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
            before = guard.source(root, guard.load_tasks(root))
            path.write_text(text + "changed context\n")
            self.assertNotEqual(before["manifest_sha256"], guard.source(root, guard.load_tasks(root))["manifest_sha256"])
            snapshot = path.read_bytes()
            with patch("sys.stdout", new_callable=io.StringIO):
                code = guard.main(["--root", str(root), "--base", "HEAD", "--offline", "--output", str(path)])
            self.assertEqual(code, 1)
            self.assertEqual(snapshot, path.read_bytes())
            duplicate = root / "backlog/archive/tasks/task-80 - Duplicate.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text(text)
            with self.assertRaisesRegex(guard.EvidenceError, "duplicate native ID"):
                guard.load_tasks(root)

    def test_pr_mode_reports_main_that_advanced_past_the_test_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)

            git("init")
            (root / "fixture.txt").write_text("base\n", encoding="utf-8")
            git("add", ".")
            commit = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                      "-c", "commit.gpgsign=false", "commit")
            git(*commit, "-m", "base")
            base = git("rev-parse", "HEAD").stdout.decode().strip()
            git("switch", "-c", "main")
            (root / "fixture.txt").write_text("new main\n", encoding="utf-8")
            git("add", ".")
            git(*commit, "-m", "main advanced")
            git("switch", "-c", "agent/feature", base)
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                code = guard.main(["--root", str(root), "--base", "main", "--branch",
                                   "agent/feature", "--ci-pr"])
            self.assertEqual(code, 1)
            self.assertIn("update the branch and rerun CI", output.getvalue())
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                code = guard.main(["--root", str(root), "--base", "HEAD", "--branch",
                                   "agent/feature", "--ci-pr", "--offline"])
            self.assertEqual(code, 1)
            self.assertIn("requires live GitHub evidence", output.getvalue())


if __name__ == "__main__":
    unittest.main()
