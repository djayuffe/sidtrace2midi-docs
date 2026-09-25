# Quickstart — SIDTrace2MIDI Documentation Ultra Release

```bash
unzip sidtrace2midi_documentation_ultra_release.zip
cd sidtrace2midi
./validate_distribution.sh
./validate_release.sh
```

Smoke test:

```bash
./run_example.sh /tmp/simple_pulse_sid2midi.mid
```

Convert one SID:

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --auto \
  --seconds 600 \
  --auto-min-seconds 540 \
  --auto-confirm-windows 3 \
  --ppq 9600 \
  --bpm 125 \
  --drumvoice 3 \
  --report \
  -o tune.mid
```

Classic/game Top-100:

```bash
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi
```

Demo Top-100:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Cracktro Top-100:

```bash
./convert_top100_cracktros_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_cracktros_midi
```

Do not insert blank lines after a trailing `\` in shell commands. Use one physical command line when possible.

## Logic Order / Frame / Timing Final Closure

- MIDI event order is now explicit and stable: meta, program, CC/bend, note-off, note-on.
- SidFrame is the canonical internal frame model; legacy tuple frames are normalized at API boundaries.
- `convert()` validates frame/timing alignment before MIDI rendering.
- Multi-SID frame access no longer depends on raw magic tuple indices.
- Loop detection now prefers the best-evidenced loop candidate instead of the first early tail match.
- `run_tune()` uses a pre-call elapsed-period contract so timer writes affect the next frame cleanly.
- Added `docs/audits/SID2MIDI_LOGIC_ORDER_FRAME_TIMING_FINAL_AUDIT.md` and regression tests.


## README final release note

This package is the cleaned README/distribution final release on top of the logic-order-perfect codebase. Run `./validate_distribution.sh` after unpacking to verify tests, CLI, Top-100 scripts, SHA integrity and cache cleanup.

## Fast fallback for multi-subtune demo SIDs

The Top-100 scripts use fast subtune probes by default. To force the old exhaustive behavior for one difficult SID/batch, append:

```bash
--exhaustive-subtune-scan
```

For normal Top-100 runs, keep the default. It avoids spending minutes on every 0-note loader subtune.

## Final subtune guard perfection

This release adds one more protection for pathological demo SIDs where alternate
subtune probes fail or time out without even producing a `0 notes` report.  The
batch engine now has two independent guards:

```text
--subtune-zero-streak-limit 4
--subtune-bad-streak-limit 6
--subtune-scan-time-budget 240
```

`zero-streak` stops obvious repeated 0-note loader subtunes. `bad-streak` also
stops repeated probe failures, timeouts, unknown note counts and under-threshold
weak probes. `subtune-scan-time-budget` caps wall-clock probing time per SID so a
single broken demo file cannot stall the whole Top-100 run.

The manifest now includes `reason`, `subtune_attempts` and `probe_attempts`, so a
failed row explains whether it stopped because of weak notes, converter failure,
zero-streak, bad-streak or probe budget. Failed weak outputs are deleted by
default and no longer become future `skip-existing` false successes.


## Preferred command

```bash
python3 sidtrace2midi.py examples/simple_pulse.sid --auto --seconds 10 --ppq 9600 -o /tmp/simple.mid --report
```

`sid2midi.py` remains available for compatibility.
