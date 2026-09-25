# Detailed Data Flow

This file describes the full execution path from a SID file to a finished MIDI file.

## 1. SID file input

`sidtrace2midi.py` loads a PSID/RSID file and reads the header fields:

- format/version
- load address
- init address
- play address
- number of subtunes
- preferred subtune
- clock/chip flags
- 2SID/3SID base offsets when present

The loader decides whether the file is a PSID abstraction or an RSID-style C64 runtime case.

## 2. C64 memory setup

The runtime builds a 64 KiB C64 RAM image. The project also ships ROM files under `roms/` so RSID/KERNAL paths can be represented more honestly.

Important memory areas:

- `$0000/$0001`: 6510 data direction and port latch
- `$A000-$BFFF`: BASIC ROM or RAM under ROM
- `$D000-$DFFF`: I/O or character ROM depending on banking
- `$E000-$FFFF`: KERNAL ROM or RAM under ROM
- `$D400-$D41F`: primary SID register window

## 3. CPU execution

`CPU6502` executes the SID init/play routine through callback-based `read()` and `write()` functions. This lets the C64 host intercept writes to SID, CIA and VIC registers.

Execution modes:

- direct PSID init/play calls
- IRQ-driven RSID-style calls
- salvage/debug modes for difficult files
- strict ROM mode when `--require-roms` is used

## 4. Register capture

When player code writes to SID registers, the host records:

- frequency low/high
- pulse width low/high
- control/waveform/gate
- ADSR
- filter cutoff/resonance/mode
- volume and `$D418` digi-like writes

Each capture step becomes a canonical `SidFrame`.

## 5. Timing capture

The converter tracks C64-cycle timestamps in `fcyc`. The invariant is:

```text
len(fcyc) == len(frames) + 1
```

That means every frame has a start cycle and the whole capture has one final end cycle.

## 6. Loop detection

When `--auto` is enabled, SIDTrace2MIDI searches for repeated frame signatures. Modern loop detection uses a richer signature covering primary SID, 2SID, 3SID, filter state and digi indicators.

Top-100 defaults are intentionally conservative:

```text
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
```

This avoids cutting demo tunes at short intro repetitions.

## 7. MIDI rendering

The renderer maps register movement to MIDI tracks:

- voice pitch -> MIDI note / pitch bend
- gate edges -> note on/off
- pulse width -> CC
- waveform/control -> CC/metadata
- filter movement -> CC
- noise/drum voice -> percussion mapping when selected

Same-tick event order is deterministic:

```text
meta -> program -> CC/bend -> note-off -> note-on
```

This prevents stuck or inverted retrigger notes.

## 8. Output files

A normal conversion produces:

- `.mid` MIDI file
- optional `.json` register export when `--export-register-json` is used
- report text on stdout when `--report` is enabled

Batch conversion also produces JSON/CSV manifests and debug logs.
