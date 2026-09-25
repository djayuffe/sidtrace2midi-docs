# Module group: Top-100 batch converters

The Top-100 batch layer converts many HVSC SIDs using the same `sid2midi.py` engine. It has three front doors:

- classic/game Top-100;
- demo-scene Top-100;
- cracktro/intro Top-100.

## Classic/game Top-100

Files:

- `convert_top100_exact.sh`
- `convert_top100_hvsc.py`
- `convert_top25_hvsc.py`
- `validate_top100_manifest.py`
- `TOP100_AUTO_README.md`

Typical command:

```bash
./convert_top100_exact.sh /path/to/C64Music ~/Downloads/c64_top100_midi
```

## Demo Top-100

Files:

- `convert_top100_demos_exact.sh`
- `convert_top100_demos_hvsc.py`
- `convert_top100_demos_hvsc.sh`
- `validate_top100_demos_manifest.py`
- `TOP100_DEMOS_README.md`

Typical command:

```bash
./convert_top100_demos_exact.sh /path/to/C64Music ~/Downloads/c64_top100_demos_midi
```

## Cracktro/intro Top-100

Files:

- `convert_top100_cracktros_exact.sh`
- `convert_top100_cracktros_hvsc.py`
- `convert_top100_cracktros_hvsc.sh`
- `validate_top100_cracktros_manifest.py`
- `TOP100_CRACKTROS_README.md`

Typical command:

```bash
./convert_top100_cracktros_exact.sh /path/to/C64Music ~/Downloads/c64_top100_cracktros_midi
```

## Resolver policy

The resolver avoids broad fuzzy matching that can collapse many ranks onto generic filenames such as `Intro.sid`, `Music.sid` or `Loader.sid`.

It prefers:

- exact seed path;
- meaningful title/composer/path score;
- demo/cracktro-specific paths for those lists;
- non-helper, non-test, non-sfx candidates.

It rejects or downranks:

- one-letter junk;
- BASIC/picture/helper/test files;
- generic candidates unless explicitly seeded;
- duplicate resolved SID sources.

## Retry policy

Normal production batch no longer uses expensive salvage automatically. Default stack:

1. default;
2. large-init;
3. large-init-large-call.

`--salvage-retry` is opt-in for forensic/manual work.

## Subtune guard policy

For files with many subtunes, the batch layer probes cheaply before running expensive full conversion. It stops early when many subtunes are bad, zero-note or timed out.

Important options:

- `--subtune-probe-seconds`
- `--subtune-probe-timeout`
- `--subtune-probe-min-notes`
- `--subtune-zero-streak-limit`
- `--subtune-bad-streak-limit`
- `--subtune-scan-time-budget`
- `--max-full-subtune-renders`
- `--exhaustive-subtune-scan`

## Weak MIDI policy

Production default deletes weak/0-note MIDI so later `skip-existing` does not treat it as a valid result.

For forensic debugging:

```bash
--allow-weak-midi --no-delete-weak-midi
```

## Manifest outputs

Each batch writes JSON and CSV manifests with:

- rank;
- title;
- SID path;
- MIDI path;
- status;
- notes;
- profile;
- actual song/subtune;
- reason;
- subtune/probe attempt metadata.
