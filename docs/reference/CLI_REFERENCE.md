# CLI Reference

This document explains the command-line interface in practical groups. The goal is not to repeat `--help`; it explains when each option should be used.

## `sid2midi.py`

Basic conversion:

```bash
python3 sid2midi.py tune.sid --song 1 --auto --seconds 600 --ppq 9600 -o tune.mid
```

### Input and output

| Option | Meaning | Normal value |
|---|---|---|
| `sid` | Input PSID/RSID file. | required |
| `-o`, `--out` | Output MIDI path. | auto-derived when omitted |
| `--song` | Subtune number. If omitted, uses PSID default/start song. | `1` for deterministic batch |
| `--report` | Print SID metadata, ROM status, timing and output summary. | recommended |

### Length and loop detection

| Option | Meaning | Normal value |
|---|---|---|
| `--seconds` | Maximum capture length. | `600` in Top-100 wrappers; `300` direct default |
| `--auto` | Enable loop detection and trim when a sufficiently confirmed loop is found. | on in wrappers |
| `--auto-min-seconds` | Ignore loop candidates shorter than this. | `540` in long Top-100 wrappers |
| `--auto-confirm-windows` | Require repeated matching windows before accepting a loop. | `3` in long Top-100 wrappers |

For demo/cracktro material, use a high `--auto-min-seconds` so repeating intros do not cut the output too early.

### MIDI timing and DAW grid

| Option | Meaning | Normal value |
|---|---|---|
| `--ppq` | MIDI pulses per quarter note. Higher preserves SID write timing. | `9600` |
| `--bpm` | Grid label for DAW editing. Does not change C64-cycle capture. | `125` |
| `--auto-bpm` | Derive grid BPM from frame speed/rows. | off |
| `--frames-per-row` | Tracker-style grid helper for `--auto-bpm`. | `6` |
| `--rows-per-beat` | Tracker-style rows per beat for `--auto-bpm`. | `4` |

### Musical output controls

| Option | Meaning |
|---|---|
| `--drumvoice N` | Treat C64 voice N as drum/noise helper track. |
| `--no-bend` | Disable pitch bend export. Useful for simplified DAW editing. |
| `--no-cc` | Disable SID register CC export. Useful for note-only preview. |

### Init/play safety budgets

| Option | Meaning | Default |
|---|---|---|
| `--max-ins-init` | Init routine instruction budget. | `8000000` |
| `--max-ins-call` | Per-frame play/IRQ call budget. | `250000` |
| `--max-stuck-frames` | Abort after repeated budget-exceeded frames. | `8` |
| `--strict-init` | Treat init budget exhaustion as fatal. | off |
| `--salvage-init` | Continue after init budget. For forensic/manual runs only. | off in batch |

### ROM and IRQ accuracy controls

| Option | Meaning |
|---|---|
| `--require-roms` | Fail if BASIC/KERNAL/CHARGEN ROMs are missing or invalid. |
| `--respect-irq-disable` | Do not force-clear CPU I flag for KERNAL IRQ playback. Stricter, but can be silent for drivers that leave SEI set. |
| `--cia-advance-mode pre_irq_latch` | Default instruction-level CIA order: latch IRQ source before handler. |
| `--cia-advance-mode post_call` | Experimental stricter debug mode: advance CIA after handler. |

### Debug export

| Option | Meaning |
|---|---|
| `--export-register-json PATH` | Export raw SidFrame/fcyc capture for debugging. |

## Top-100 batch wrappers

The wrappers set the safe defaults for long capture, high PPQ, retry guards and manifest generation.

```bash
./convert_top100_exact.sh /path/to/C64Music ~/Downloads/c64_top100_midi
./convert_top100_demos_exact.sh /path/to/C64Music ~/Downloads/c64_top100_demos_midi
./convert_top100_cracktros_exact.sh /path/to/C64Music ~/Downloads/c64_top100_cracktros_midi
```

## `convert_top25_hvsc.py` / Top-100 engine

Important operational options:

| Option | Meaning |
|---|---|
| `--hvsc PATH` | HVSC root. |
| `--out PATH` | Output directory. |
| `--top N` | Attempt first N ranked entries. |
| `--limit N` | Hard cap. If explicitly set, wins over `--top`. |
| `--start-at N` | Start from rank N. Useful for reruns. |
| `--stop-after N` | Stop after N ranks. Useful for a single rank. |
| `--list` | Show selected candidates without converting. |
| `--dry-run` | Resolve and report without rendering. |
| `--skip-existing` | Keep existing strong MIDI files. Weak files are replaced by default. |
| `--keep-going` | Continue after failures. Default wrapper behavior. |
| `--debug` | Write per-rank debug logs. |

### Weak MIDI policy

| Option | Meaning |
|---|---|
| `--min-notes N` | Minimum note count for OK status. |
| `--allow-weak-midi` | Allow low-note output as OK/debug. Not recommended for production batch. |
| `--no-delete-weak-midi` | Keep weak artifacts on disk for forensic debugging. |

### Subtune scanning controls

| Option | Meaning |
|---|---|
| `--song-scan-limit N` | Max subtunes to consider. |
| `--always-scan-subtunes` | Scan even when preferred song worked. |
| `--no-scan-subtunes-on-failure` | Disable alternate subtune scan. |
| `--subtune-probe-seconds` | Short probe capture length for alternate subtunes. |
| `--subtune-probe-timeout` | Timeout for probes. |
| `--subtune-probe-min-notes` | Probe must meet this before expensive full render. |
| `--subtune-zero-streak-limit` | Stop after consecutive 0-note probes. |
| `--subtune-bad-streak-limit` | Stop after failed/weak/timeouts streak. |
| `--subtune-scan-time-budget` | Wall-clock budget for alternate scan per SID. |
| `--max-full-subtune-renders` | Cap expensive full renders during scan. |
| `--exhaustive-subtune-scan` | Old slow forensic behavior. Use only for one SID. |

### Retry policy

Default batch retry stack is:

1. default
2. large-init
3. large-init-large-call

`salvage-init` is opt-in through `--salvage-retry`, because it can create 0-note placeholders for loader/demo SIDs.

