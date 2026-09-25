# Step 06: Accuracy boundaries

This project is intentionally an instruction-level SID-register extraction system.

## Good fit

- PSID/RSID music players.
- HVSC tunes with normal init/play routines.
- Multi-SID register capture.
- Batch conversion to editable DAW MIDI.
- Diagnostic register stream export.

## Not a full C64 emulator

Not claimed:

- PHI2 bus exactness;
- VIC badline/sprite DMA cycle stealing;
- RDY/SYNC pin behavior;
- exact analog SID filter model;
- real digi sample reconstruction;
- transistor-level invalid BCD behavior;
- full demo runtime/raster effects.

## Practical meaning

Some files in demo folders are not standalone music players. They may be loader stubs, demo runtime modules, or code that expects a complete demo environment. The batch tools should now mark those as failed instead of producing misleading 0-note success files.
