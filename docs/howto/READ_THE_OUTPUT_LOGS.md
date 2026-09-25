# How to read conversion logs

The batch converters print one block per SID.

Example:

```text
CONVERT 61: Sci Music 1 -> 61_Sci_Music_1.mid timeout=300.0s
  DEBUG profile=default song=1 rc=124 elapsed=300.2s notes=None
  DEBUG retry-profile large-init song=1
  DEBUG profile=large-init song=1 rc=0 elapsed=165.8s notes=3263
  DEBUG rc=0 elapsed=165.8s notes=3263 profile=large-init song=1 status=ok
```

## Important fields

| Field | Meaning |
|---|---|
| `profile` | Which retry mode was used. |
| `song` | Subtune number. |
| `rc` | Process return code. `0` means the child process completed. |
| `notes` | Counted MIDI note events after conversion. |
| `status` | Batch-level result: `ok`, `failed`, `weak`, etc. |
| `debug_log` | Per-SID captured stdout/stderr. |

## Good result

A good Top-100 result has `status=ok`, nonzero notes, and a MIDI duration close to the configured `--seconds` unless a confirmed loop was found.

## Weak result

A weak result has too few notes. By default weak MIDI artifacts are deleted so later `--skip-existing` cannot preserve false 0-note files.

## Slow subtune scan

If a SID has many subtunes that all produce 0 notes, the fast probe and bad-streak guards stop the scan early. Use `--exhaustive-subtune-scan` only for a single forensic/manual SID investigation.
