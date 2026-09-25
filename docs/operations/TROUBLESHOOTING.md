# Troubleshooting Guide

## `zsh: permission denied: /Users/.../C64Music`

Cause: a blank line after a trailing backslash. zsh treats the next path as a command.

Wrong:

```bash
./convert_top100_demos_exact.sh \

  /Users/ulfbertilsson/Downloads/C64Music \
```

Right:

```bash
./convert_top100_demos_exact.sh \
  /Users/ulfbertilsson/Downloads/C64Music \
  ~/Downloads/c64_top100_demos_midi
```

Or one line:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

## Output is 0 notes

Likely causes:

- wrong subtune
- loader-only SID
- init budget issue
- full demo runtime dependency
- salvage placeholder

Actions:

```bash
python3 tools/analyze_top100_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --emit-rerun
```

Try one rank with alternate subtunes:

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --out ~/Downloads/c64_top100_demos_midi --start-at 63 --stop-after 1 --debug
```

## Existing bad MIDI keeps being skipped

Delete the bad file or let batch replace weak files. Default production mode deletes weak output. For manual cleanup:

```bash
rm -f ~/Downloads/c64_top100_demos_midi/63_Party_Songs.mid
```

## Conversion times out

For one SID/rank:

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --out ~/Downloads/c64_top100_demos_midi --start-at 61 --stop-after 1 --timeout 600 --debug
```

## Too short output

Disable auto loop trim:

```bash
python3 sid2midi.py tune.sid --seconds 600 --ppq 9600 -o tune_full.mid
```

Or make trim stricter:

```bash
python3 sid2midi.py tune.sid --auto --seconds 600 --auto-min-seconds 590 --auto-confirm-windows 4 -o tune.mid
```

## Missing ROM warning

Check ROMs:

```bash
ls -l roms/basic.bin roms/kernal.bin roms/chargen.bin
python3 sid2midi.py tune.sid --require-roms --report -o tune.mid
```

## MIDI has too many CC events

For note-only preview:

```bash
python3 sid2midi.py tune.sid --no-cc --no-bend -o tune_notes.mid
```

## Need exact debugging

Export registers:

```bash
python3 sid2midi.py tune.sid --seconds 30 --export-register-json tune_registers.json -o tune.mid
```

Then inspect `tune_registers.json` to see whether the SID writes were captured before note heuristics.

