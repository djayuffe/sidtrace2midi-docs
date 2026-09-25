# Batch rerun playbook

Use this when a Top-100 batch produced failed, weak or suspicious rows.

## 1. Analyze the manifest

```bash
python3 tools/analyze_top100_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --emit-rerun
```

The analyzer prints weak/failed rows and suggested rerun commands.

## 2. Re-render one rank

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /Users/ulfbertilsson/Downloads/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 \
  --stop-after 1 \
  --debug
```

## 3. Enable forensic salvage only for one difficult file

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

## 4. Do not enable exhaustive scan globally

`--exhaustive-subtune-scan` is intentionally not default.  Use it only when a
single SID is important enough to spend time on every subtune and retry profile.

## 5. Clean stale weak files

If older releases created 0-note MIDI files, delete them before rerun:

```bash
rm -f ~/Downloads/c64_top100_demos_midi/63_Party_Songs.mid
```

Newer releases delete weak outputs by default unless `--no-delete-weak-midi` is
specified.
