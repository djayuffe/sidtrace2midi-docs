#!/usr/bin/env python3
"""Run each unittest file in an isolated subprocess with a per-file timeout.

This is more useful than one monolithic unittest-discover run for this project:
several tests intentionally spawn converter subprocesses and print batch logs, so
isolating files makes failures and stalls immediately attributable.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run SID2MIDI regression tests one file at a time")
    ap.add_argument("--timeout", type=float, default=180.0, help="seconds allowed per test file")
    ap.add_argument("patterns", nargs="*", default=["tests/test_*.py"])
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    files: list[Path] = []
    for pat in args.patterns:
        files.extend(sorted(root.glob(pat)))
    seen = set()
    files = [f for f in files if f.is_file() and not (str(f) in seen or seen.add(str(f)))]
    if not files:
        print("no test files matched", file=sys.stderr)
        return 1
    failed = 0
    for f in files:
        rel = f.relative_to(root)
        print(f"== {rel} ==", flush=True)
        try:
            p = subprocess.run([sys.executable, "-m", "unittest", str(rel), "-q"], cwd=root, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {rel} exceeded {args.timeout:.1f}s", file=sys.stderr)
            failed += 1
            continue
        if p.returncode != 0:
            print(f"FAILED: {rel} rc={p.returncode}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"Full test file pass FAILED ({failed}/{len(files)} files failed)", file=sys.stderr)
        return 1
    print(f"Full test file pass OK ({len(files)} files)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
