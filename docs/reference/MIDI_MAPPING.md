# MIDI Mapping Reference

SID2MIDI exports musical notes plus SID controller telemetry. The MIDI is designed for DAW editing, not as a perfect SID audio render.

## Track layout

The default output has six logical tracks:

1. Metadata / tempo map
2. SID voice 1 notes and CC
3. SID voice 2 notes and CC
4. SID voice 3 notes and CC or drum/noise helper
5. Global SID/filter/controller data
6. Debug / extra controller lane when present

Exact labels can vary by conversion mode, but the goal is consistent: voice material stays separated so it can be edited independently in a DAW.

## Timing

- PPQ default is `9600`.
- C64 cycle timestamps are scaled into MIDI ticks using rational math.
- `--bpm` is a DAW grid label. It does not force C64 playback to a fake tempo.
- `--auto-bpm` can derive a tracker-like grid from frame speed and rows.

## Notes

Notes are inferred from SID frequency registers and gate/control transitions. This is a musical extraction heuristic:

- Gate on + stable pitch becomes note start.
- Gate off or retrigger becomes note end.
- Same-tick retrigger is ordered as Note Off before Note On.
- Pitch bend can represent slides/vibrato when `--no-bend` is not used.

## Controllers

Controller output is intentionally rich. It helps DAW reconstruction and debugging.

Common controller concepts:

| SID concept | MIDI representation |
|---|---|
| Cutoff/filter movement | CC lane |
| Resonance/filter mode | CC lane |
| Pulse width | CC lane and/or pitch expression helper |
| Control register waveform/gate/sync/ring/noise | CC/debug lanes |
| ADSR register changes | CC/debug lanes |
| Digi `$D418` activity | Digi/debug count or raw JSON export |

Disable CC with:

```bash
python3 sid2midi.py tune.sid --no-cc -o notes_only.mid
```

## Drum voice

Use `--drumvoice 3` for many C64 tunes where voice 3 is noise/percussion-heavy:

```bash
python3 sid2midi.py tune.sid --drumvoice 3 -o tune.mid
```

This does not synthesize real drums; it marks and maps SID noise/gate behavior in a DAW-friendly way.

## Raw register JSON

For debugging the exact SID-register stream:

```bash
python3 sid2midi.py tune.sid --song 1 --seconds 30 --export-register-json tune_registers.json -o tune.mid
```

Use this when notes look wrong but register capture may still be correct.

