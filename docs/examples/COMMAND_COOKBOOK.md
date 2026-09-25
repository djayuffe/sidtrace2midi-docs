# Command Cookbook

## Validate package

```bash
./validate_distribution.sh
```

## Smoke test

```bash
./run_example.sh /tmp/simple_pulse.mid
```

## Convert one SID, long demo-safe settings

```bash
python3 sid2midi.py tune.sid --song 1 --auto --seconds 600 --auto-min-seconds 540 --auto-confirm-windows 3 --ppq 9600 --bpm 125 --drumvoice 3 --report -o tune.mid
```

## Convert one SID, full capture, no trim

```bash
python3 sid2midi.py tune.sid --song 1 --seconds 600 --ppq 9600 --report -o tune_full.mid
```

## Export register JSON

```bash
python3 sid2midi.py tune.sid --song 1 --seconds 30 --export-register-json tune_registers.json --report -o tune.mid
```

## Classic Top-100

```bash
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi
```

## Demo Top-100

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

## Cracktro Top-100

```bash
./convert_top100_cracktros_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_cracktros_midi
```

## List selected demo candidates

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --list
```

## Rerun one rank

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --out ~/Downloads/c64_top100_demos_midi --start-at 63 --stop-after 1 --debug
```

## Analyze manifest

```bash
python3 tools/analyze_top100_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --emit-rerun
```

## Forensic salvage for one rank

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --out ~/Downloads/c64_top100_demos_midi --start-at 63 --stop-after 1 --salvage-retry --no-delete-weak-midi --debug
```

