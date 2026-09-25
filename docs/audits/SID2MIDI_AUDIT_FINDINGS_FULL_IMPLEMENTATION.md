# SID2MIDI audit findings full implementation

This release implements the requested `sid2midi.py` audit closure pass.

## Implemented

- ROM loader now records explicit ROM status for `basic.bin`, `kernal.bin` and `chargen.bin`.
- `--report` prints ROM status lines for every run, not only partial RSID warnings.
- `--require-roms` fails early when required C64 ROM images are missing/invalid.
- 6510 `$0000/$0001` port is initialized before SID payload placement in `load_sid()`.
- Added a stable `SidFrame` namedtuple and `make_frame()` constructor.
- Frame helpers now prefer named fields (`sidA`, `trigA`, `trigcycA`, etc.) and retain tuple compatibility.
- `_frame_trigcyc()` added for named/tuple-safe trigger-cycle access.
- Loop detection signature now includes 2SID/3SID pitch/control/trigger state, not only primary SID gates.
- CIA Timer A/B handling now has `advance_cia()`, reload helpers, start/stop/one-shot handling and Timer-B count-Timer-A-underflow support.
- `current_timer_period()` now prefers active/masked Timer A/B and falls back to frame timing only when no usable timer exists.
- IRQ masking behavior is configurable.
- New CLI flag: `--respect-irq-disable`.
- Default behavior remains compatibility-oriented by force-clearing KERNAL IRQ I-flag if necessary; strict users can opt out.
- `main(argv=None)` added for direct unit testing of CLI paths.
- Added regression tests covering ROM reporting, frame model, CIA timers, 6510 port initialization, and IRQ masking mode.

## Honest boundaries retained

- CIA is still instruction-level, not PHI2 bus-cycle exact.
- VIC raster timing remains a register/IRQ stub, not a raster-exact badline/sprite DMA model.
- SID envelope remains frame-stepped for velocity extraction.
- Digi is detected/reported as `$D418` activity, not reconstructed as PCM audio.

These boundaries are deliberate for a SID-register-to-MIDI extractor. The project is not a full raster/audio C64 emulator.
