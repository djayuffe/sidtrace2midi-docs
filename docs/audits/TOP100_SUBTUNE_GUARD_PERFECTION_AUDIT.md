# Top-100 Subtune Guard Perfection Audit

This pass closes the remaining pathological batch behavior found after the
fast-probe release: some demo SIDs can fail or time out during every alternate
subtune probe without producing an explicit `0 notes` report.  The previous
zero-streak guard handled repeated `notes=0`, but a series of `rc!=0` /
`notes=None` probes could still walk many subtunes.

## Implemented

- Added `--subtune-bad-streak-limit`.
  - Counts consecutive failed, timed-out, unknown-note or under-probe-min-note
    alternate-subtune probes.
  - Default wrapper value: `6`.
- Added `--subtune-scan-time-budget`.
  - Caps wall-clock time spent probing alternate subtunes for one SID.
  - Default wrapper value: `240` seconds.
  - `0` disables the budget for forensic/manual runs.
- Manifest now records:
  - `reason`
  - `subtune_attempts`
  - `probe_attempts`
- Failure printing no longer repeats a stale converter success line after the
  weak MIDI file has been deleted.  It prints a direct failure summary instead.
- Added regression tests for failed-probe bad streak, probe time budget, wrapper
  defaults and manifest fields.

## Why this matters

Large demo collections often contain loader or multi-part SIDs where song 1 and
many alternate song numbers enter resident wait loops.  For normal Top-100 batch
runs, those should be marked failed quickly and audibly, not converted into
0-note MIDI or spend many minutes per seed.

The full slow behavior remains available with `--exhaustive-subtune-scan` and by
raising/disabling the budgets.
