# Top-100 Cracktros / Intros

`convert_top100_cracktros_hvsc.py` builds a cracktro/intro-oriented Top-100 batch from a local HVSC tree and converts the selected SIDs to MIDI using the same hardened PSID/RSID engine as the classic and demo Top-100 scripts.

Run:

```bash
./convert_top100_cracktros_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_cracktros_midi
```

Defaults:

```text
--auto --seconds 600 --auto-min-seconds 540 --ppq 9600
```

That means full-song/loop detection is enabled, false short loops below 540 seconds are ignored, and every conversion is capped at ten minutes.

Outputs:

```text
~/Downloads/c64_top100_cracktros_midi/*.mid
~/Downloads/c64_top100_cracktros_midi/top100_cracktros_manifest.json
~/Downloads/c64_top100_cracktros_midi/top100_cracktros_manifest.csv
~/Downloads/c64_top100_cracktros_midi/debug/*.log
```

Validate:

```bash
python3 validate_top100_cracktros_manifest.py ~/Downloads/c64_top100_cracktros_midi/top100_cracktros_manifest.json --min-notes 80
```

Resolver policy:

- prioritizes `DEMOS/`, intro/cracktro/trainer/loader/menu names, and common demogroup/cracking-group names;
- rejects helper/test/sfx/basic/picture/one-letter junk;
- does not use broad matching for generic names like `Intro.sid`, `Loader.sid`, `Music.sid`, or `Cracktro.sid` unless the exact seeded path exists;
- rejects duplicate resolved SID sources so the Top-100 does not collapse to the same generic file repeatedly.

## Batch reliability notes

The Top-100 wrappers are intended to be run as one physical shell command line, for example:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Do not place blank lines after a trailing `\`; zsh will then try to execute the following path as a command and may print `permission denied`.

The batch engine keeps going after individual failures and automatically retries difficult init routines using larger init/play budgets and a final `salvage-init` extraction profile. Existing MIDI files are now note-counted when `--skip-existing` is active, so manifest validation does not mark skipped files as `notes=0`.
