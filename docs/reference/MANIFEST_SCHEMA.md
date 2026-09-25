# Top-100 Manifest Schema

Each Top-100 converter writes JSON and CSV manifests. The manifest is the truth source for batch health: it records what was attempted, what worked, and why rows failed.

## Common files

| Batch | JSON | CSV |
|---|---|---|
| Classic/game Top-100 | `top100_manifest.json` | `top100_manifest.csv` |
| Demo Top-100 | `top100_demos_manifest.json` | `top100_demos_manifest.csv` |
| Cracktro Top-100 | `top100_cracktros_manifest.json` | `top100_cracktros_manifest.csv` |

## Required row concepts

The exact row may contain additional fields, but these concepts are expected:

| Field | Meaning |
|---|---|
| `rank` | Top-list rank used for output naming. |
| `title` | Human-readable tune title. |
| `sid` / `sid_path` | Resolved SID path. |
| `out` / `midi` | MIDI output path. |
| `status` | `ok`, `failed`, `weak`, `skipped`, or equivalent validated status. |
| `notes` | Counted MIDI note events. |
| `cc` | Counted MIDI controller events when available. |
| `profile` | Retry profile that produced the row. |
| `actual_song` | Subtune actually used after scanning. |
| `reason` | Failure/weak reason. OK rows should have an empty reason. |
| `subtune_attempts` | Number of full subtune attempts. |
| `probe_attempts` | Number of quick probes. |

## Status meaning

### `ok`

A strong conversion. It met `--min-notes`, the process returned success, and output should be usable.

### `weak`

A conversion produced MIDI but did not meet note-count expectations. Production mode usually deletes weak output so `--skip-existing` does not preserve it later.

### `failed`

No acceptable MIDI was produced. The row should include a non-empty `reason`.

### `skipped`

Existing strong MIDI was found and reused.

## Common reasons

| Reason | Interpretation | Next action |
|---|---|---|
| `weak-notes` | Render completed but note count was too low. | Try a different subtune or manual flags. |
| `init-budget` | Init exceeded instruction budget. | Try larger init manually or inspect SID. |
| `timeout` | Process exceeded wrapper timeout. | Rerun one rank with higher timeout. |
| `subtune-zero-streak-N` | Alternate scan saw too many zero-note probes. | Likely loader/demo-only SID or unsupported runtime. |
| `subtune-bad-streak-N` | Consecutive failed/weak probes. | Use targeted manual run only if important. |
| `subtune-probe-budget-Xs` | Scan time budget reached. | Raise budget for one SID if needed. |

## Validation

Validate with:

```bash
python3 validate_top100_manifest.py ~/Downloads/c64_top100_midi/top100_manifest.json --min-notes 100
python3 validate_top100_demos_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --min-notes 100
python3 validate_top100_cracktros_manifest.py ~/Downloads/c64_top100_cracktros_midi/top100_cracktros_manifest.json --min-notes 80
```

Analyze and emit targeted rerun commands:

```bash
python3 tools/analyze_top100_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --emit-rerun
```

