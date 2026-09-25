# Error and Reason Matrix

This reference explains common batch failure reasons and what to do next.

| Reason / Symptom | Meaning | Action |
|---|---|---|
| `weak-midi` | MIDI was created but note count is below threshold. | Try another subtune, inspect debug log, or rerun with `--no-delete-weak-midi` for analysis. |
| `subtune-zero-streak-*` | Several subtunes probed with zero notes. | Usually loader/demo-runtime SID. Do not waste full batch time unless manually investigating. |
| `subtune-bad-streak-*` | Consecutive subtunes failed, timed out, or produced weak output. | Use `tools/analyze_top100_manifest.py --emit-rerun` for targeted commands. |
| `subtune-probe-budget-*` | Probe budget was exhausted. | Increase budget only for one SID, not whole Top-100. |
| `timeout` / `rc=124` | Conversion subprocess hit timeout. | Use a larger timeout or large-init profile for that single SID. |
| `SID init exceeded instruction budget` | Init routine did not return before safety cap. | Try `--max-ins-init`, `--strict-init`, or manual subtune selection. |
| `0 notes, 41 CC` | Often a silent/wait-loop capture. | Treat as failed unless you are debugging register writes. |
| missing ROM warning | ROM file is not available or not found. | Use bundled `roms/` or run with `--require-roms` to fail loudly. |

## Production default

Production batch deletes weak MIDI artifacts. This keeps `skip-existing` from preserving bad 0-note results.

## Forensic mode

Use forensic mode only for targeted debugging:

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /path/to/C64Music \
  --out /tmp/demo-debug \
  --start-at 63 \
  --stop-after 1 \
  --salvage-retry \
  --no-delete-weak-midi \
  --debug
```
