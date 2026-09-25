# Step 03: Top-100 batch conversion

## Classic/game Top-100

```bash
./convert_top100_exact.sh /path/to/C64Music ~/Downloads/c64_top100_midi
```

## Demo Top-100

```bash
./convert_top100_demos_exact.sh /path/to/C64Music ~/Downloads/c64_top100_demos_midi
```

## Cracktro Top-100

```bash
./convert_top100_cracktros_exact.sh /path/to/C64Music ~/Downloads/c64_top100_cracktros_midi
```

## Important defaults

```text
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
--ppq 9600
--timeout 300
--keep-going
```

## Why salvage is opt-in

Automatic salvage often produces 0-note placeholders for loader-only or unsupported demo runtime files. Production batch therefore does not use salvage by default.

For one difficult file/rank:

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /path/to/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 \
  --stop-after 1 \
  --salvage-retry \
  --debug
```
