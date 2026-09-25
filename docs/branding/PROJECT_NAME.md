# Project name: SIDTrace2MIDI

## Recommended public name

**SIDTrace2MIDI**

The name is intentionally directional and technically honest:

```text
SID player code -> C64 runtime -> SID register trace -> MIDI
```

It is better than names like `midi2sid` because this tool does **not** convert
MIDI back into a SID file.  It runs PSID/RSID player code and extracts what the
player writes to the SID chips, then turns that trace into editable MIDI.

## Short description

**SIDTrace2MIDI** is a C64 SID-register tracing and MIDI extraction toolkit.
It executes SID init/play routines using a hardened Python NMOS 6502/6510 core,
captures SID/CIA/VIC-side musical state, and writes high-resolution MIDI for DAW
editing.

## Suggested tagline

```text
Run the SID player. Trace the chip. Export the music.
```

## Naming rules

Use these names consistently:

```text
Project / release name: SIDTrace2MIDI
Main historical script: sid2midi.py
Friendly launcher:      sidtrace2midi.py
CPU module:             cpu6502.py
Batch family:           Top-100 HVSC converters
Output type:            MIDI, plus optional raw register JSON trace
```

Do not call the project `midi2sid`; that implies the opposite direction.

## Why the source file is still called sid2midi.py

The file name `sid2midi.py` is kept for compatibility with existing wrappers,
logs, scripts and user commands.  The new `sidtrace2midi.py` wrapper is the
friendlier public entrypoint and calls the same `main()` function.

## One-line examples

```bash
python3 sidtrace2midi.py tune.sid --auto --seconds 600 --ppq 9600 -o tune.mid
python3 sid2midi.py      tune.sid --auto --seconds 600 --ppq 9600 -o tune.mid
```

Both commands are equivalent.
