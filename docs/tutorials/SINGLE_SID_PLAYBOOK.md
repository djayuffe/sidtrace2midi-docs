# Single SID Conversion Playbook

Use this when tuning one specific SID by hand.

## Normal long conversion

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

## Force full length, no loop trim

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --seconds 600 \
  --ppq 9600 \
  --bpm 125 \
  --report \
  -o tune_full.mid
```

## Strict ROM validation

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --require-roms \
  --report \
  -o tune.mid
```

## Debug raw register stream

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --seconds 30 \
  --export-register-json tune_registers.json \
  --report \
  -o tune_debug.mid
```

## Try alternate CIA order

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --cia-advance-mode post_call \
  --seconds 120 \
  --report \
  -o tune_post_call.mid
```

## If init fails

First increase budget:

```bash
python3 sid2midi.py /path/to/tune.sid --song 1 --max-ins-init 32000000 --report -o tune.mid
```

Use salvage only as forensic last resort:

```bash
python3 sid2midi.py /path/to/tune.sid --song 1 --salvage-init --report -o tune_salvage.mid
```

If salvage produces 0 notes, the file likely needs full demo context or a different subtune.

