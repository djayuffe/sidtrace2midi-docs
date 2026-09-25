# Step 02: Single SID conversion

## Recommended command

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --auto \
  --seconds 600 \
  --auto-min-seconds 540 \
  --auto-confirm-windows 3 \
  --ppq 9600 \
  --bpm 125 \
  --drumvoice 3 \
  --report \
  -o tune.mid
```

## Fixed length

```bash
python3 sid2midi.py /path/to/tune.sid --seconds 180 --ppq 9600 --report -o tune_180s.mid
```

## Strict RSID/ROM mode

```bash
python3 sid2midi.py /path/to/tune.sid --require-roms --report -o tune.mid
```

## Debug register stream

```bash
python3 sid2midi.py /path/to/tune.sid --export-register-json tune_registers.json -o tune.mid
```

Use this when a MIDI file sounds wrong and you need to inspect raw captured SID registers.
