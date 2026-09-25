#!/usr/bin/env python3
"""Validate a Top-100 demos SID->MIDI manifest."""
from __future__ import annotations
import sys
from pathlib import Path
import validate_top100_manifest


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        argv.insert(0, "~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json")
    return validate_top100_manifest.main(argv)

if __name__ == "__main__":
    raise SystemExit(main())
