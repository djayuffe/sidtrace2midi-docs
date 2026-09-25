# Top-100 retry and batch final closure audit

## Problems observed

A real Top-100 demos run failed on `Compotune.sid` with:

```text
RuntimeError: SID init exceeded instruction budget (8000000)
```

The wrapper also stopped at the first failed row, and `--skip-existing` wrote `notes=0` to the manifest, which made later validation treat already-converted files as weak.

The shell transcript also showed zsh `permission denied` lines because blank lines were inserted after a trailing backslash.  That is shell syntax: a backslash only continues the immediately next physical line.  The README/QUICKSTART now emphasize one-line wrapper use.

## Fixes

- `convert_top25_hvsc.py` now retries failed conversions with profiles:
  - `default`
  - `large-init`
  - `large-init-large-call`
  - `salvage-init`
- Batch wrappers now pass `--keep-going`, so one hard tune does not abort the entire Top-100.
- `--skip-existing` now counts note-on events from the existing MIDI file instead of writing `notes=0`.
- Duplicate manifest append bug removed.
- Added regression tests for retry/salvage, skip-existing MIDI note counting, and wrapper keep-going policy.

## Remaining honest boundary

`salvage-init` is an extraction policy, not forensic emulation. It is intentionally used for HVSC batch conversion when a SID init routine appears to have completed useful setup but never returns cleanly. For strict emulator audits, use `--strict-init` and disable salvage.
