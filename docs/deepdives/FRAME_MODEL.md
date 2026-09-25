# SidFrame Model

`SidFrame` is the canonical frame object used between capture and MIDI conversion.

## Why it exists

Older iterations used raw tuples. That became fragile when 2SID, 3SID, trigger cycles and digi counters were added. `SidFrame` gives named fields and avoids magic indexes.

## Conceptual fields

| Field | Meaning |
|---|---|
| primary SID registers | `$D400-$D418` snapshot for chip 1 |
| primary trigger/gate flags | Which voices retriggered in this frame |
| primary trigger cycle | CPU cycle when trigger was observed |
| second SID registers/state | optional chip 2 data |
| third SID registers/state | optional chip 3 data |
| digi metadata | `$D418` activity/counts |

## Normalization

At API boundaries:

```python
frame = ensure_sid_frame(frame)
frames = normalize_frames(frames)
```

After that, render code should use helpers:

```python
_frame_regs(frame, chip)
_frame_trig(frame, chip)
_frame_trigcyc(frame, chip)
_frame_digi(frame)
```

## Failure policy

Malformed legacy frames should fail loudly. Silent zero-register fallback hides bugs and creates fake empty MIDI.

## Debug export

Use:

```bash
python3 sid2midi.py tune.sid --seconds 30 --export-register-json tune_registers.json -o tune.mid
```

The JSON stream lets you inspect captured registers before MIDI heuristics are applied.

