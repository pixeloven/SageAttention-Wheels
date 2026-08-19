#!/usr/bin/env python3
"""Append an explicit CUDA/Torch local version to upstream wheel metadata."""

from __future__ import annotations

import argparse
import pathlib
import re


VERSION_PATTERN = re.compile(
    r"(?P<prefix>\bversion\s*=\s*)(?P<quote>['\"])(?P<version>[^'\"]+)(?P=quote)"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--local-version", required=True)
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:\.[a-z0-9]+)*", args.local_version):
        raise SystemExit("local version must contain lowercase PEP 440 segments")

    setup_path = args.source / "setup.py"
    original = setup_path.read_text(encoding="utf-8")
    matches = list(VERSION_PATTERN.finditer(original))
    if len(matches) != 1:
        raise SystemExit(f"expected one setup.py version, found {len(matches)}")

    match = matches[0]
    base_version = match.group("version").split("+", 1)[0]
    packaged_version = f"{base_version}+{args.local_version}"
    replacement = f"{match.group('prefix')}{match.group('quote')}{packaged_version}{match.group('quote')}"
    updated = original[: match.start()] + replacement + original[match.end() :]
    setup_path.write_text(updated, encoding="utf-8")
    print(f"Packaging upstream {base_version} as {packaged_version}")


if __name__ == "__main__":
    main()
