import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pr_safety import allowed_document, assess, collect  # noqa: E402


def evidence():
    return {
        "policy_sha": "b" * 40, "latest_base_sha": "b" * 40, "default_branch": "main",
        "pr": {
            "head": {"sha": "a" * 40, "repo": {"full_name": "vkaam/phonebuddy"}},
            "base": {"sha": "b" * 40, "ref": "main", "repo": {"full_name": "vkaam/phonebuddy"}},
            "merge_commit_sha": "c" * 40, "state": "open", "draft": False,
            "mergeable": True, "mergeable_state": "clean", "labels": [],
            "changed_files": 1, "additions": 2, "deletions": 1, "user": {"login": "author"},
        },
        "files": [{"filename": "docs/usage/calling.md", "status": "modified", "mode": "100644",
                   "patch": "@@ -1 +1,2 @@\n-old\n+new\n+line", "additions": 2, "deletions": 1, "changes": 3}],
        "quality": {"conclusion": "success", "head_sha": "a" * 40, "merge_sha": "c" * 40,
                    "workflow_path": ".github/workflows/ci.yml", "event": "pull_request"},
        "reviews": [{"state": "APPROVED", "commit_id": "a" * 40, "author_association": "COLLABORATOR",
                     "user": {"login": "reviewer", "type": "User"}}],
    }


class SafetyTests(unittest.TestCase):
    def test_documentation_with_current_evidence_is_only_a_candidate(self):
        report = assess(evidence())
        self.assertTrue(report["auto_merge_candidate"])
        self.assertFalse(report["merge_authorized"])

    def test_unknown_sensitive_and_disguised_paths_require_review(self):
        for path in ["apps/web/main.ts", "infra/main.bicep", "package-lock.json", "AGENTS.md",
                     ".github/workflows/ci.yml", "scripts/pr_safety.py", "tests/test_pr_safety.py",
                     "docs/software-plan.md", "docs/quality-and-delivery.md", "docs/adr/identity.md",
                     "docs/runbooks/release.md", "backlog/config.yml", ".groma/index.md",
                     "docs/usage/../security.md", "docs/usage//guide.md", "docs/usage/.hidden.md",
                     "docs/usage/agents.md", "docs/usage/skill.md", "docs/usage/security.md",
                     "docs/usage/Guide.MD", "docs/usage/x.md.py", "docs/usage/x.md\nREADME.md"]:
            with self.subTest(path=path):
                item = evidence()
                item["files"][0]["filename"] = path
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_readme_and_nested_usage_documents_are_allowed(self):
        for path in ["README.md", "docs/usage/calling.md", "docs/usage/calls/hold.md"]:
            self.assertTrue(allowed_document(path))

    def test_metadata_vetoes(self):
        for key, value in [("draft", True), ("state", "closed"), ("mergeable", None),
                           ("mergeable", False), ("mergeable_state", "behind"),
                           ("mergeable_state", "blocked"), ("changed_files", 2),
                           ("labels", [{"name": "No-Auto-Merge"}])]:
            with self.subTest(key=key, value=value):
                item = evidence()
                item["pr"][key] = value
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_forks_other_branches_and_stale_policy(self):
        for field in ["fork", "branch", "policy", "latest_base"]:
            with self.subTest(field=field):
                item = evidence()
                if field == "fork":
                    item["pr"]["head"]["repo"]["full_name"] = "outsider/phonebuddy"
                elif field == "branch":
                    item["pr"]["base"]["ref"] = "release"
                else:
                    item["policy_sha" if field == "policy" else "latest_base_sha"] = "d" * 40
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_unavailable_binary_symlink_executable_rename_and_deleted_diffs(self):
        for key, value in [("mode", "120000"), ("mode", "100755"), ("mode", None),
                           ("status", "removed"), ("status", "renamed"), ("patch", None),
                           ("previous_filename", "infra/main.bicep"), ("changes", -1),
                           ("additions", "2")]:
            with self.subTest(key=key, value=value):
                item = evidence()
                item["files"][0][key] = value
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_size_bounds_and_inconsistent_evidence(self):
        item = evidence()
        item["files"][0].update(additions=200, deletions=1, changes=201)
        item["pr"].update(additions=200, deletions=1)
        self.assertFalse(assess(item)["auto_merge_candidate"])
        item = evidence()
        item["files"] *= 11
        item["pr"]["changed_files"] = 11
        self.assertFalse(assess(item)["auto_merge_candidate"])
        item = evidence()
        item["files"] = []
        self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_stale_missing_failed_and_wrong_workflow_checks(self):
        for key, value in [("conclusion", "failure"), ("conclusion", "skipped"),
                           ("head_sha", "d" * 40), ("merge_sha", "d" * 40),
                           ("workflow_path", ".github/workflows/fake.yml"), ("event", "push")]:
            with self.subTest(key=key, value=value):
                item = evidence()
                item["quality"][key] = value
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_review_must_be_current_independent_and_human(self):
        for change in [{"state": "CHANGES_REQUESTED"}, {"state": "DISMISSED"},
                       {"commit_id": "d" * 40}, {"author_association": "NONE"},
                       {"user": {"login": "author", "type": "User"}},
                       {"user": {"login": "review-bot", "type": "Bot"}}]:
            with self.subTest(change=change):
                item = evidence()
                item["reviews"][0].update(change)
                self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_comment_does_not_erase_changes_requested(self):
        item = evidence()
        veto = copy.deepcopy(item["reviews"][0])
        veto.update(state="CHANGES_REQUESTED", user={"login": "other", "type": "User"})
        comment = dict(veto, state="COMMENTED")
        item["reviews"].extend([veto, comment])
        self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_missing_fields_fail_closed(self):
        for malformed in [{}, None, [], {"pr": None}, {"pr": {"head": None}}]:
            self.assertFalse(assess(malformed)["auto_merge_candidate"])
        for key in evidence():
            item = evidence()
            del item[key]
            self.assertFalse(assess(item)["auto_merge_candidate"])

    def test_exact_line_limit_is_eligible(self):
        item = evidence()
        item["files"][0].update(additions=199, deletions=1, changes=200)
        item["pr"].update(additions=199, deletions=1)
        self.assertTrue(assess(item)["auto_merge_candidate"])

    def test_cli_writes_machine_readable_decision_without_authorizing_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "input.json", Path(directory) / "report.json"
            source.write_text(json.dumps(evidence()))
            subprocess.run([sys.executable, "scripts/pr_safety.py", "--input", str(source),
                            "--output", str(output)], check=True, capture_output=True)
            report = json.loads(output.read_text())
            self.assertEqual(report["decision"], "low-risk-candidate")
            self.assertFalse(report["merge_authorized"])


class CollectorTests(unittest.TestCase):
    def collect_fixture(self, scenario="valid"):
        item = evidence()
        pr_reads = 0

        def response(route):
            nonlocal pr_reads
            if route == "/repos/vkaam/phonebuddy":
                return {"default_branch": "main"}
            if route.endswith("/pulls/1"):
                pr_reads += 1
                result = copy.deepcopy(item["pr"])
                if scenario == "force-push" and pr_reads > 1:
                    result["head"]["sha"] = "d" * 40
                return result
            if "/pulls/1/files?" in route:
                return copy.deepcopy(item["files"])
            if "/pulls/1/reviews?" in route:
                return copy.deepcopy(item["reviews"])
            if "/git/trees/" in route:
                return {"truncated": scenario == "truncated-tree", "tree": [
                    {"path": "docs/usage/calling.md", "mode": "100644"}]}
            if "/check-runs?" in route:
                return {"check_runs": [{
                    "name": "Quality", "status": "completed", "conclusion": "success",
                    "app": {"slug": "fake-app" if scenario == "fake-app" else "github-actions"},
                    "details_url": "https://github.com/vkaam/phonebuddy/actions/runs/123/job/456",
                }]}
            if "/actions/runs/123" in route:
                return {"path": ".github/workflows/ci.yml", "event": "pull_request",
                        "head_sha": ("d" if scenario == "stale-ci" else "a") * 40}
            if route.endswith("/branches/main"):
                return {"commit": {"sha": "b" * 40}}
            raise AssertionError("Unexpected endpoint: " + route)

        with patch("pr_safety.api", side_effect=response), patch(
                "pr_safety.subprocess.check_output", return_value="b" * 40 + "\n"):
            return collect("vkaam/phonebuddy", 1)

    def test_collector_binds_ci_tree_and_reviews_to_live_pr(self):
        self.assertTrue(assess(self.collect_fixture())["auto_merge_candidate"])

    def test_collector_rejects_force_push_truncated_tree_and_spoofed_or_stale_ci(self):
        for scenario in ["force-push", "truncated-tree", "fake-app", "stale-ci"]:
            with self.subTest(scenario=scenario):
                self.assertFalse(assess(self.collect_fixture(scenario))["auto_merge_candidate"])


if __name__ == "__main__":
    unittest.main()
