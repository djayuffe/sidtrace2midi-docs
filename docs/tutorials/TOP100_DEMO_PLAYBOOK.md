# Top-100 Demo Batch Playbook

This is the practical workflow for `~/Downloads/C64Music` and demo output.

## 1. Run the demo batch

```bash
./convert_top100_demos_exact.sh \
  /Users/ulfbertilsson/Downloads/C64Music \
  ~/Downloads/c64_top100_demos_midi
```

## 2. Watch for these lines

Good:

```text
status=ok notes=6031
... 600.0s @ grid 125 BPM
```

Weak/failed:

```text
status=failed reason=subtune-bad-streak-6
status=failed reason=weak-notes
```

Weak is not kept by default. This prevents later `skip-existing` from preserving 0-note files.

## 3. Validate manifest

```bash
python3 validate_top100_demos_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --min-notes 100
```

## 4. Analyze failures

```bash
python3 tools/analyze_top100_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --emit-rerun
```

## 5. Rerun one rank

Example for rank 63:

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /Users/ulfbertilsson/Downloads/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 \
  --stop-after 1 \
  --debug
```

## 6. Forensic salvage for one rank only

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /Users/ulfbertilsson/Downloads/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 \
  --stop-after 1 \
  --salvage-retry \
  --no-delete-weak-midi \
  --debug
```

Do not use salvage for full production batches unless you intentionally want weak debug artifacts.

