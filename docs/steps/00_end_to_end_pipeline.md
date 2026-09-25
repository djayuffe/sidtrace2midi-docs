# Step 00: End-to-end pipeline

This document explains the complete conversion path.

## 1. Input SID

The input is a `.sid` file from HVSC or another C64 source.

## 2. Header parsing

`SidFile` reads:

- PSID/RSID magic;
- version;
- load/init/play addresses;
- song count;
- selected subtune;
- speed flags;
- SID chip/base metadata.

## 3. C64 runtime setup

`C64` creates RAM, loads ROMs, initializes the 6510 port and maps memory.

## 4. Payload load

The SID payload is copied into C64 RAM. If the SID has load address zero, the first two payload bytes supply the load address.

## 5. Init routine

The selected subtune is initialized by calling the SID init address through `CPU6502.call()`.

## 6. Frame loop

For each frame:

1. choose current period from CIA Timer A/B or fallback vsync;
2. run play routine or IRQ path;
3. capture SID registers and trigger flags into `SidFrame`;
4. append frame cycle timestamp to `fcyc`.

## 7. Loop/length decision

If `--auto` is enabled, `find_loop()` searches for a confirmed repeated frame sequence. Otherwise the converter uses the requested duration.

## 8. MIDI conversion

`convert()` turns SidFrames into:

- notes;
- note-offs;
- pitch bend;
- waveform/program changes;
- filter and pulse-width CCs;
- drum/noise events;
- metadata and timing.

## 9. Output

The Standard MIDI File is written to `-o output.mid`.
