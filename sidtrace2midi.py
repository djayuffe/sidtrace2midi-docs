#!/usr/bin/env python3
"""Compatibility launcher for SIDTrace2MIDI.

The historical implementation file is still `sid2midi.py` for script and
batch compatibility.  This wrapper gives the project its clearer public name:
SIDTrace2MIDI — a SID register trace to MIDI converter.
"""
from sid2midi import main

if __name__ == "__main__":
    raise SystemExit(main())
