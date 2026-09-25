# Continue and Repair a Top-100 Run

A long Top-100 conversion may be interrupted, or a few rows may fail while most rows succeed. Do not delete the whole output folder unless you want a complete rebuild.

## 1. Continue normal run

The wrappers use skip-existing behavior. Re-run the same command:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Existing strong MIDI files are counted and kept.

## 2. Analyze manifest

```bash
python3 tools/analyze_top100_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --emit-rerun
```

This prints a summary and targeted rerun commands for failed/weak rows.

## 3. Remove one bad file

If one row created a bad or old MIDI file, delete only that file:

```bash
rm -f ~/Downloads/c64_top100_demos_midi/63_Party_Songs.mid
```

Then rerun the wrapper.

## 4. Use exhaustive mode only for one SID

Do not enable expensive forensic options for the entire Top-100 unless you intentionally want a very long run.

```bash
python3 convert_top100_demos_hvsc.py \
  --hvsc /Users/ulfbertilsson/Downloads/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 \
  --stop-after 1 \
  --exhaustive-subtune-scan \
  --salvage-retry \
  --debug
```

## 5. Validate after repair

```bash
python3 validate_top100_demos_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --min-notes 100
```
