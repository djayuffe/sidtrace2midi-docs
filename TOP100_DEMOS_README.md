# Top-100 demos HVSC -> MIDI

This package adds a demo-scene oriented batch converter beside the game/classic
Top-100 converter.

Run:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Outputs:

```text
~/Downloads/c64_top100_demos_midi/*.mid
~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json
~/Downloads/c64_top100_demos_midi/top100_demos_manifest.csv
~/Downloads/c64_top100_demos_midi/debug/*.log
```

List selected demo candidates before converting:

```bash
python3 convert_top100_demos_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --list
```

Validate after conversion:

```bash
python3 validate_top100_demos_manifest.py --min-notes 100
```

The demo converter reuses the same hardened PSID/RSID runtime, high-resolution
PPQ=9600 timing, subtune probing, retry profiles, timeout, debug logging and
manifest handling as the Top-100 classic converter.  It resolves demo seeds
strictly and auto-fills from local HVSC demo/composer folders when exact seed
paths differ across HVSC versions.

## Batch reliability notes

The Top-100 wrappers are intended to be run as one physical shell command line, for example:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Do not place blank lines after a trailing `\`; zsh will then try to execute the following path as a command and may print `permission denied`.

The batch engine keeps going after individual failures and automatically retries difficult init routines using larger init/play budgets and a final `salvage-init` extraction profile. Existing MIDI files are now note-counted when `--skip-existing` is active, so manifest validation does not mark skipped files as `notes=0`.
