# Performance Tuning

SIDTrace2MIDI is pure Python and executes real 6502 player code. Some SIDs are cheap; some loader/demo-runtime SIDs can be expensive.

## Fast production defaults

The Top-100 wrappers are tuned for production:

```text
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
--subtune-probe-seconds 45
--subtune-probe-timeout 60
--subtune-zero-streak-limit 4
--subtune-bad-streak-limit 6
--subtune-scan-time-budget 240
--max-full-subtune-renders 4
```

## Do not enable salvage globally

`--salvage-retry` is useful for investigation but expensive. It can produce zero-note placeholders on loader-only SIDs. Keep it opt-in.

## When a file times out

Try a targeted rerun:

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /path/to/C64Music \
  --out /tmp/sid-debug \
  --start-at 61 \
  --stop-after 1 \
  --timeout 600 \
  --debug
```

## When a file has many subtunes

Use probes first. Only use `--exhaustive-subtune-scan` for one SID at a time.

## MIDI size and PPQ

PPQ 9600 gives high timing precision but creates more events. For rough preview work, PPQ can be lowered, but production output should keep PPQ 9600.
