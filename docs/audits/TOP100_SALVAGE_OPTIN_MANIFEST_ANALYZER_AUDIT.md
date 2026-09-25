# Top-100 salvage opt-in and manifest analyzer audit

## Problem observed

Large demo batch logs showed pathological SIDs where every subtune failed normal
init and then `salvage-init` produced 0-note MIDI.  This wasted minutes per
subtune and risked stale weak MIDI artifacts becoming future `--skip-existing`
false successes.

## Fix

- Automatic batch retry stack now uses:
  - `default`
  - `large-init`
  - `large-init-large-call`
- `salvage-init` retry is opt-in via `--salvage-retry`.
- Alternate subtune scan remains guarded by fast probes, zero/bad streaks and a
  wall-clock probe budget.
- Added `--max-full-subtune-renders` to cap expensive full renders after probes.
- Added `tools/analyze_top100_manifest.py` for post-run triage.

## Result

Normal Top-100 runs finish faster, avoid false 0-note salvage successes, and give
clear manifest reasons plus targeted rerun commands for forensic/manual follow-up.
