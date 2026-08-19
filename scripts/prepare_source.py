#!/usr/bin/env python3
"""Validate the requested CUDA architectures against upstream setup.py and
append an explicit CUDA/Torch local version to upstream wheel metadata."""

from __future__ import annotations

import argparse
import ast
import pathlib
import re


VERSION_PATTERN = re.compile(
    r"(?P<prefix>\bversion\s*=\s*)(?P<quote>['\"])(?P<version>[^'\"]+)(?P=quote)"
)

SUPPORTED_ARCHS_PATTERN = re.compile(r"\bSUPPORTED_ARCHS\s*=\s*(\{[^{}]*\})")


def normalize_capabilities(arch_list: str) -> set[str]:
    capabilities: set[str] = set()
    for item in arch_list.replace(",", ";").split(";"):
        it = item.strip()
        if not it:
            continue
        it = it.lower().replace("sm_", "").replace("compute_", "")
        it = it.replace("a", "")
        if it.endswith("+ptx"):
            capabilities.add(f"{it[:-4]}+PTX")
        else:
            if len(it) == 2 and it.isdigit():
                it = f"{it[0]}.{it[1]}"
            capabilities.add(it)
    return capabilities


def check_arch_list(setup_text: str, arch_list: str) -> None:
    match = SUPPORTED_ARCHS_PATTERN.search(setup_text)
    if not match:
        raise SystemExit(
            "could not find SUPPORTED_ARCHS in upstream setup.py; "
            "update scripts/prepare_source.py for this upstream ref"
        )
    supported = ast.literal_eval(match.group(1))
    requested = normalize_capabilities(arch_list)
    if not requested:
        raise SystemExit("CUDA architecture list is empty")
    unsupported = sorted(
        capability
        for capability in requested
        if not any(capability.startswith(arch) for arch in supported)
    )
    if unsupported:
        raise SystemExit(
            f"upstream setup.py only compiles kernels for {sorted(supported)} "
            f"and silently ignores other architectures; remove {unsupported}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--local-version", required=True)
    parser.add_argument("--arch-list")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:\.[a-z0-9]+)*", args.local_version):
        raise SystemExit("local version must contain lowercase PEP 440 segments")

    setup_path = args.source / "setup.py"
    original = setup_path.read_text(encoding="utf-8")

    if args.arch_list is not None:
        check_arch_list(original, args.arch_list)

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
