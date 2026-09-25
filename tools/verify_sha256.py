#!/usr/bin/env python3
"""Portable SHA256SUMS verifier for macOS/Linux/Windows.

Reads SHA256SUMS.txt in the project root and verifies every listed file.
This avoids relying on GNU sha256sum, which is not available by default on macOS.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMS = ROOT / "SHA256SUMS.txt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SUMS.exists():
        print("missing SHA256SUMS.txt", file=sys.stderr)
        return 2
    failed: list[str] = []
    checked = 0
    for raw in SUMS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            failed.append(f"malformed line: {raw!r}")
            continue
        want, name = parts
        name = name.lstrip("*").strip()
        path = ROOT / name
        if not path.exists():
            failed.append(f"missing: {name}")
            continue
        got = sha256(path)
        checked += 1
        if got.lower() != want.lower():
            failed.append(f"mismatch: {name}\n  want {want}\n  got  {got}")
    if failed:
        print("SHA256 verification FAILED", file=sys.stderr)
        for item in failed:
            print(item, file=sys.stderr)
        return 1
    print(f"SHA256SUMS OK ({checked} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
