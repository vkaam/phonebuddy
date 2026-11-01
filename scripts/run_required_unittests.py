"""Run required Python unit tests; incomplete or expected-failure runs fail."""

import argparse
from pathlib import Path
import sys
import unittest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-directory", default="tests")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    suite = unittest.defaultTestLoader.discover(args.start_directory)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or not result.testsRun or result.skipped or result.expectedFailures:
        print(
            f"Required Python tests incomplete: {result.testsRun} run, "
            f"{len(result.skipped)} skipped, {len(result.expectedFailures)} expected failures.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
