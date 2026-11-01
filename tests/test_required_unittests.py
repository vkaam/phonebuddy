"""Exercise real unittest discovery and incomplete-run handling."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / "scripts/run_required_unittests.py"


class RequiredUnittestRunnerTests(unittest.TestCase):
    def test_real_discovery_outcomes(self):
        cases = {
            "pass": ("    def test_case(self): self.assertTrue(True)\n", 0),
            "skip": ("    @unittest.skip('not run')\n    def test_case(self): pass\n", 1),
            "expected_failure": ("    @unittest.expectedFailure\n    def test_case(self): self.fail()\n", 1),
            "failure": ("    def test_case(self): self.fail()\n", 1),
            "error": ("    def test_case(self): raise RuntimeError('broken')\n", 1),
            "empty": (None, 1),
        }
        for name, (body, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                if body is not None:
                    Path(directory, "test_fixture.py").write_text(
                        "import unittest\nclass Fixture(unittest.TestCase):\n" + body,
                        encoding="utf-8",
                    )
                result = subprocess.run(
                    [sys.executable, "-B", str(RUNNER), "--start-directory", directory],
                    capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected:
                    self.assertIn("Required Python tests incomplete", result.stderr)


if __name__ == "__main__":
    unittest.main()
