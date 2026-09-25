# Output Files Reference

## Single conversion output

```text
tune.mid
```

The MIDI file contains six tracks by default: metadata plus SID voice-derived tracks. Exact content depends on the tune, drum voice selection and detected register activity.

## Optional register JSON

```bash
python3 sidtrace2midi.py tune.sid --export-register-json tune.trace.json -o tune.mid
```

The JSON export is useful when debugging conversion logic. It preserves the cycle timeline and canonical `SidFrame` values before MIDI rendering.

## Top-100 batch outputs

Classic/game batch:

```text
c64_top100_midi/*.mid
c64_top100_midi/top100_manifest.json
c64_top100_midi/top100_manifest.csv
c64_top100_midi/debug/*.log
```

Demo batch:

```text
c64_top100_demos_midi/*.mid
c64_top100_demos_midi/top100_demos_manifest.json
c64_top100_demos_midi/top100_demos_manifest.csv
c64_top100_demos_midi/debug/*.log
```

Cracktro batch:

```text
c64_top100_cracktros_midi/*.mid
c64_top100_cracktros_midi/top100_cracktros_manifest.json
c64_top100_cracktros_midi/top100_cracktros_manifest.csv
c64_top100_cracktros_midi/debug/*.log
```

## Manifest fields

Important manifest fields include:

- `rank`
- `title`
- `sid`
- `out`
- `status`
- `reason`
- `notes`
- `profile`
- `song`
- `actual_song`
- `subtune_attempts`
- `probe_attempts`

`status=ok` means a usable MIDI file was produced. `status=failed` means no production-quality MIDI was accepted. Weak/0-note MIDI files are deleted by default unless forensic options are used.
