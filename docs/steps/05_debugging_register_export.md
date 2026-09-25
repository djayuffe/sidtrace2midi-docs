# Step 05: Debugging with register export

`--export-register-json` writes the captured SID register stream and frame cycle timestamps.

## Command

```bash
python3 sid2midi.py /path/to/tune.sid \
  --seconds 60 \
  --ppq 9600 \
  --report \
  --export-register-json tune_registers.json \
  -o tune.mid
```

## What to inspect

Look for:

- gate bit changes in control registers;
- frequency register movement;
- pulse width changes;
- filter cutoff/resonance changes;
- `$D418` writes for digi activity;
- 2SID/3SID register activity.

## When useful

Use this when:

- MIDI has few or no notes;
- CCs exist but notes do not;
- a subtune may be loader-only;
- a tune needs another subtune;
- you suspect unsupported runtime behavior.
