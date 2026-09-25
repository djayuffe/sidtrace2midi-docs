# SID2MIDI Distribution Final Closure Audit

This pass verifies that the feature-final release is usable as a clean distribution artifact after unzip.

## Verified

- `./validate_release.sh` runs from a fresh extracted directory.
- `./run_example.sh /tmp/sid2midi_dist_example.mid` writes a valid MIDI file.
- `python3 sid2midi.py --help` exposes the integrated SID2MIDI feature flags:
  - `--ppq`
  - `--auto-min-seconds`
  - `--auto-confirm-windows`
  - `--auto-bpm`
  - `--frames-per-row`
  - `--rows-per-beat`
  - `--max-ins-init`
  - `--max-ins-call`
  - `--max-stuck-frames`
  - `--strict-init`
  - `--salvage-init`
- CPU coverage report still returns 256/256 handlers and 151/151 official opcodes.
- SHA256 manifest is checked inside `validate_release.sh`.
- Release validation runs with `PYTHONDONTWRITEBYTECODE=1` to avoid generating `__pycache__` in the tree.

## Boundary

The release remains an instruction-level NMOS 6502/6510 + C64/SID-register extraction toolkit. It is intentionally not a Visual6502/RDY/VIC-DMA transistor-level emulator.
