# Top-100 automatic HVSC conversion

Use the wrapper to avoid zsh line-continuation mistakes:

```bash
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi
```

The Top-100 converter reuses the hardened PSID/RSID runtime from `sid2midi.py` and the same batch engine as Top-25:

- tries all selected tunes by default, no safe skip
- first 25 are the validated Top-25 list
- ranks 26..100 are seeded from well-known C64/HVSC titles
- if a seeded title is not found in the user's HVSC checkout, the script auto-fills from local HVSC files using composer/game/path scoring
- short subtune probe first, then full render of the best valid subtune
- high-resolution MIDI timing with `--ppq 9600`
- absolute C64 PHI2-cycle timing; BPM is a DAW grid label
- per-song timeout, retry profiles, debug logs, resume via `--skip-existing`
- manifests are written as both `top25_*` compatibility files and `top100_manifest.json/csv`

Important defaults:

```text
--top 100
--min-notes 100
--subtune-good-notes 500
--song-scan-limit 32
--ppq 9600
--scan-policy preferred-first
```

Useful commands:

```bash
# Show the dynamic Top-100 list chosen for your HVSC tree
python3 convert_top100_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --list

# Regenerate everything from scratch
rm -f ~/Downloads/c64_top100_midi/*.mid
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi

# Convert only ranks 26..100
python3 convert_top100_hvsc.py --hvsc /Users/ulfbertilsson/Downloads/C64Music --out ~/Downloads/c64_top100_midi --start-at 26 --top 100 --skip-existing --debug

# Force best-note-count subtune selection instead of preferred-first
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi --always-scan-subtunes
```

## Closure7 recommended validation

After a Top-100 run, validate the manifest:

```bash
python3 validate_top100_manifest.py ~/Downloads/c64_top100_midi/top100_manifest.json --min-notes 100
```

Closure7 also removes broad substring fuzzy matching, so missing seeds will not resolve to unrelated one-letter files like `y.sid` or `I.sid`. Missing seeds are replaced by real auto-fill candidates from the local HVSC tree.

## Batch reliability notes

The Top-100 wrappers are intended to be run as one physical shell command line, for example:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Do not place blank lines after a trailing `\`; zsh will then try to execute the following path as a command and may print `permission denied`.

The batch engine keeps going after individual failures and automatically retries difficult init routines using larger init/play budgets and a final `salvage-init` extraction profile. Existing MIDI files are now note-counted when `--skip-existing` is active, so manifest validation does not mark skipped files as `notes=0`.
