# First 30 minutes with SIDTrace2MIDI

## 1. Validate the package

```bash
./validate_distribution.sh
```

## 2. Run the bundled smoke example

```bash
./run_example.sh /tmp/simple_pulse.mid
```

## 3. Convert one SID

```bash
python3 sidtrace2midi.py /Users/ulfbertilsson/Downloads/C64Music/MUSICIANS/R/Rob_Hubbard/Commando.sid   --song 1   --auto   --seconds 600   --ppq 9600   --report   -o ~/Downloads/Commando.mid
```

## 4. Run a demo batch

```bash
./convert_top100_demos_exact.sh   /Users/ulfbertilsson/Downloads/C64Music   ~/Downloads/c64_top100_demos_midi
```

## 5. Analyze the manifest

```bash
python3 tools/analyze_top100_manifest.py   ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json   --emit-rerun
```
