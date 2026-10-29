"""Dependency-free repository checks. Run from any directory with Python 3.9+."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check_repository():
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    )
    errors = []
    paths = sorted(set(result.stdout.decode().strip("\0").split("\0")))
    for name in paths:
        path = ROOT / name
        if name.startswith(("backlog/", ".groma/", "groma/")):
            continue  # Generated files are maintained through their owning CLI.
        if path.suffix not in {".md", ".py", ".yml", ".yaml"} or not path.exists():
            continue
        if path.is_symlink():
            errors.append(f"{name}: source/documentation symlinks require review")
            continue
        try:
            content = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{name}: expected UTF-8")
            continue
        if content and not content.endswith("\n"):
            errors.append(f"{name}: missing final newline")
        for number, line in enumerate(content.splitlines(), 1):
            if line.rstrip(" \t") != line:
                errors.append(f"{name}:{number}: trailing whitespace")
            if re.match(r"^(<{7}|={7}|>{7})( |$)", line):
                errors.append(f"{name}:{number}: unresolved merge marker")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^\s)]+)\)", content):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                linked = (path.parent / unquote(url.path)).resolve()
                if not linked.is_relative_to(ROOT) or not linked.exists():
                    errors.append(f"{name}: broken/escaping local link: {target}")
        if name.startswith(".github/workflows/"):
            for action in re.findall(r"uses:\s*([^\s#]+)", content):
                if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action):
                    errors.append(f"{name}: action must use an immutable commit: {action}")
    return errors


if __name__ == "__main__":
    failures = check_repository()
    print("\n".join(failures) if failures else "Repository checks passed.")
    raise SystemExit(bool(failures))
