# Top-100 full-length / weak salvage final audit

Implemented after real demo batch logs showed salvage-init producing 0-note or 2-note MIDI files and some auto-loop results ending around 179.6 seconds despite ten-minute render targets.

## Fixes

- Top-100 classic/demo/cracktro exact wrappers now default to `--seconds 600 --auto-min-seconds 540 --auto-confirm-windows 3 --timeout 300`.
- Weak existing MIDI files below `--min-notes` are deleted and re-rendered instead of accepted by `--skip-existing`.
- Weak salvage-init outputs below `--min-notes` are marked failed and deleted unless `--allow-weak-midi` is explicitly set.
- The shared batch engine reads PSID/RSID song count from the header and scans alternate subtunes when the selected song fails or renders weak.
- Manifest rows record `actual_song`, profile, notes, status and the exact command used.

## Boundary

This does not make loader-only or non-musical demo parts magically musical. Those rows now fail honestly instead of becoming 0-note MIDI successes.
