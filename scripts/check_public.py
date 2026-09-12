"""Check the explicit publication inventory, local links, and suspicious content.

No network requests. This is a focused guard, not a comprehensive secret detector.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    expected = set((ROOT / "PUBLIC_FILES.txt").read_text().splitlines())
    actual = set()
    errors = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part == "__pycache__" or part == ".git" or part.startswith("demo-output") for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append((str(relative), "symlink not allowed"))
        elif path.is_file():
            actual.add(relative.as_posix())
    for name in sorted(actual - expected):
        errors.append((name, "not in publication inventory"))
    for name in sorted(expected - actual):
        errors.append((name, "missing publication file"))
    patterns = {
        "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "provider token shape": r"\bsk-(?:or-v1-)?[A-Za-z0-9_-]{20,}",
        "bot token shape": r"\b\d{7,12}:[A-Za-z0-9_-]{30,}",
        "personal home path": r"/(?:Users|home)/[A-Za-z0-9_.-]+/",
        "IPv4 address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }
    for name in sorted(actual & expected):
        path = ROOT / name
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append((name, "unreviewed binary file"))
            continue
        for kind, pattern in patterns.items():
            if re.search(pattern, text):
                errors.append((name, kind))
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                target_path = target.split("#", 1)[0]
                resolved = (path.parent / target_path).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    errors.append((name, "broken or escaping local link"))
    env = (ROOT / ".env.example").read_text()
    for line in env.splitlines():
        if line and not line.startswith("#") and line.partition("=")[2].strip():
            errors.append((".env.example", "nonempty example value"))
    for name, kind in errors:
        print(f"FAIL {name}: {kind}")
    if errors:
        return 1
    print(f"PASS: {len(actual)} publication files; local links and focused privacy checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
