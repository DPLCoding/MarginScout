from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PUBLIC_FILES.txt"
FORBIDDEN_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
    "marginscout.db",
}
SKIP_DIRECTORIES = {".git", ".pytest_cache", "__pycache__"}
TEXT_SUFFIXES = {
    "",
    ".gitignore",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yml",
    ".yaml",
}
PLACEHOLDER = re.compile(r"<[A-Z][A-Z0-9_]+>")
SECRET_PATTERNS = {
    "private key": re.compile("-----BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style secret": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "assigned client secret": re.compile(
        r"(?i)(?:client[_ -]?secret|api[_ -]?key|refresh[_ -]?token)\s*[=:]\s*['\"]?[A-Za-z0-9_./+-]{16,}"
    ),
}


def expected_files() -> set[str]:
    return {
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def actual_files() -> set[str]:
    found: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRECTORIES for part in path.parts):
            continue
        found.add(path.relative_to(ROOT).as_posix())
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the curated public MarginScout package")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on unresolved personalization placeholders",
    )
    arguments = parser.parse_args()
    failures: list[str] = []

    expected = expected_files()
    actual = actual_files()
    for path in sorted(actual - expected):
        failures.append(f"unexpected file: {path}")
    for path in sorted(expected - actual):
        failures.append(f"missing manifest file: {path}")

    for relative in sorted(actual):
        path = ROOT / relative
        if path.name.casefold() in {name.casefold() for name in FORBIDDEN_NAMES}:
            failures.append(f"forbidden filename: {relative}")
        if path.suffix.casefold() not in TEXT_SUFFIXES and path.name != ".gitignore":
            failures.append(f"unexpected non-text file: {relative}")
            continue
        if relative == "tools/audit_release.py":
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"possible {label}: {relative}")
        if arguments.strict and PLACEHOLDER.search(text):
            failures.append(f"unresolved publication placeholder: {relative}")

    if failures:
        print("Public release audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Public release audit passed ({len(actual)} allowlisted files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
