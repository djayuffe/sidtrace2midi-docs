# Loop Detection Deep Dive

Loop detection is enabled with `--auto`.

## Goal

Find a repeated musical state and trim output without cutting intros too early.

## Important controls

| Option | Meaning |
|---|---|
| `--seconds` | Capture ceiling. |
| `--auto-min-seconds` | Ignore loop candidates shorter than this. |
| `--auto-confirm-windows` | Require multiple matching windows. |

## Recommended demo/cracktro defaults

```text
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
```

These settings strongly prefer long output and reject early intro loops.

## Signature content

The loop signature includes:

- primary SID pitch/control/gate state
- 2SID and 3SID state when present
- filter/global SID state
- digi/write-count state

## Why early cuts still happen sometimes

If a tune intentionally repeats a long block or has little state variation, a loop can be real but still musically undesirable. In that case rerun without `--auto` or raise `--auto-min-seconds` close to `--seconds`.

## Force full capture

```bash
python3 sid2midi.py tune.sid --seconds 600 --ppq 9600 -o tune_full.mid
```

No `--auto` means no loop trimming.

