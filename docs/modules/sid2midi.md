# Module: `sid2midi.py`

`sid2midi.py` is the main converter. It loads a SID file, runs the embedded C64 player code using `CPU6502`, captures SID/CIA/VIC register state into frames, and converts those frames to a Standard MIDI File.

## Main flow

```text
SID file
  -> SidFile parser
  -> C64 memory/runtime setup
  -> init routine
  -> repeated play/IRQ calls
  -> SidFrame register capture
  -> loop detection / fixed length decision
  -> MIDI event extraction
  -> SMF writer
```

## `SidFile`

Parses PSID/RSID headers and payload.

Important responsibilities:

- detect PSID vs RSID;
- read load/init/play addresses;
- read song count and selected subtune;
- handle speed flags and PAL/NTSC timing;
- scan simple BASIC `SYS` loaders.

## ROM loading

The converter looks for:

- `roms/basic.bin`
- `roms/kernal.bin`
- `roms/chargen.bin`

ROM status is reported in `--report`. `--require-roms` makes missing ROMs a hard error, useful for RSID/KERNAL-sensitive files.

## `C64` runtime

The `C64` class owns RAM, ROM visibility, I/O behavior, SID register capture and CIA timer state.

Key steps:

1. Initialize RAM and CPU.
2. Initialize CPU-side 6510 `$0000/$0001` port early.
3. Load SID payload into memory.
4. Run init.
5. Run play routine or IRQ handler repeatedly.
6. Record one `SidFrame` per musical frame.

## SidFrame model

`SidFrame` is the canonical internal frame format. It contains primary SID plus optional second/third SID register snapshots, trigger flags, trigger cycle stamps and digi count.

Helpers:

- `make_frame()`
- `ensure_sid_frame()`
- `normalize_frames()`
- `_frame_regs()`
- `_frame_trig()`
- `_frame_trigcyc()`
- `_frame_digi()`

The render path normalizes legacy tuples at API boundaries and then uses named fields, avoiding magic index access in the MIDI conversion path.

## CIA / IRQ handling

SID players often use CIA Timer A/B or raster-like timing. This module implements an instruction-level timer model suitable for SID extraction:

- Timer A/B latches;
- start/stop;
- one-shot behavior;
- Timer B optionally counting Timer A underflows;
- current period selection from active timer or frame fallback;
- optional `--cia-advance-mode` for debugging timing assumptions.

This is not a cycle-exact CIA chip emulator, but it gives stable musical timing for many PSID/RSID players.

## Loop and length policy

With `--auto`, the converter searches for repeated frame signatures and can stop early when a confident loop is found.

Top-100 defaults are conservative:

- long capture target;
- high `--auto-min-seconds`;
- multiple confirmation windows.

This avoids cutting demo tunes at repeated intros.

## MIDI writer

The MIDI writer uses:

- stable event order;
- explicit same-tick priority;
- VLQ encoding;
- high PPQ default, normally 9600;
- CCs for SID register movement;
- note tracks for the three SID voices plus drum/noise extraction.

Same-tick ordering is designed so note-off happens before note-on on retrigger ticks.

## Debug outputs

Useful flags:

- `--report`: print metadata, ROM status and output summary.
- `--export-register-json`: export raw SidFrame/fcyc register stream.
- `--debug`: used by batch wrappers for per-song logs.
