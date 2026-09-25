# Top-100 long default song closure audit

## Problem

The previous Top-100 wrappers rendered with `--seconds 300` and `--auto-min-seconds 90`.  Demo/cracktro material can hit a short intro loop near 540 seconds, producing output that is technically valid but too short for DAW use.  In addition, salvage-init could generate a 0-note MIDI file that later became a misleading `--skip-existing` artifact.

## Fix

- Classic Top-100 wrapper default: `--seconds 600`, `--auto-min-seconds 540`, `--auto-confirm-windows 3`, `--timeout 300`.
- Demo Top-100 wrapper default: `--seconds 600`, `--auto-min-seconds 540`, `--auto-confirm-windows 3`, `--timeout 300`.
- Cracktro Top-100 wrapper default: `--seconds 600`, `--auto-min-seconds 540`, `--auto-confirm-windows 3`, `--timeout 300`.
- Shared batch engine default `--seconds` is now `600.0` and `--timeout` is now `300.0`.
- `sid2midi.py` direct CLI default `--seconds` is now `300.0` instead of `180.0`.
- Weak 0-note/under-min-note outputs are deleted by default so future `--skip-existing` does not treat them as successful conversions.
- `--allow-weak-midi` can intentionally keep weak outputs for forensic/debug work.

## Result

Default batch output is longer, less likely to cut at a short intro loop, and safer when a salvage profile produces no musical notes.
