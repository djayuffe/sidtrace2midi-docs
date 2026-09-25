# Perfect Continuation Cleanup Audit

This pass continues from the perfect clean final package and closes practical distribution/batch polish issues found during a real zip audit.

## Fixed

- Direct `convert_top25_hvsc.py --top N` now attempts `N` ranked entries when `--limit` is not explicitly supplied.  Previously the default `--limit 25` could silently cap direct `--top 100` usage.
- Explicit `--limit` still wins as a tighter cap when both `--top` and `--limit` are supplied.
- Added `--no-delete-weak-midi` for forensic/debug runs that intentionally want to keep weak/0-note MIDI artifacts.  Default production behavior still deletes weak outputs so `--skip-existing` cannot preserve false successes.
- `validate_top100_manifest.py` now performs basic schema validation: required fields, valid status values, empty reason for OK rows, and reason presence for failed rows.
- `sid2midi.py` wording now says cycle-stamped instruction-level SID capture instead of overclaiming full cycle-accurate C64 emulation.
- Added `tools/run_test_files.py`, an isolated per-file test runner used by `run_full_tests.sh` for clearer attribution and safer long batch regression runs.

## Verified

- Python syntax check passes.
- CPU opcode coverage remains 256/256 handlers and 151/151 official opcodes.
- SID smoke conversion still renders the bundled `simple_pulse.sid`.
- Distribution validation still checks CLI flags and Top-100 wrapper defaults.

## Accuracy boundary

The package remains intentionally instruction-level for SID register extraction.  It does not claim PHI2/RDY/SYNC/VIC-badline/transistor-level exact C64 emulation.
