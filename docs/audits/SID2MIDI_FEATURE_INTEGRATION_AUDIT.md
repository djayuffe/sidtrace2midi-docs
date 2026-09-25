# SID2MIDI Feature Integration Audit

This pass integrates the uploaded `sid2midi(1).py` logic into the final-perfect NMOS CPU release while preserving the audited CPU core.

## Integrated features

- PSID/RSID loader now supports PSID v4 third-SID address byte.
- Fixed extra-SID address calculation: base is `$D000 + offset*16`, not `$D420 | offset*16`.
- Added 3SID capture path: `sidC`, gates/triggers/cycles, MIDI channels 11/12/13-equivalent layout via ch base 10.
- Added PSID mode memory behavior: RAM under BASIC/KERNAL remains visible while I/O remains capturable.
- Added BASIC SYS stub scanner for simple RSID/BASIC loaders.
- Added CIA Timer B latch/count/control handling.
- Added dynamic IRQ target selection from current 6510 memory-port state.
- Added VIC raster compare high-bit handling via `$D011/$D012`.
- Added safer init/play budgets: `--max-ins-init`, `--max-ins-call`, `--max-stuck-frames`, `--strict-init`, `--salvage-init`.
- Added conservative loop detection: `--auto-min-seconds`, `--auto-confirm-windows`.
- Added rational cycle-to-MIDI tick scaling and configurable `--ppq` default 9600.
- Added `--auto-bpm`, `--frames-per-row`, `--rows-per-beat` for DAW grid labeling.
- Added robust MIDI meta-event length encoding via VLQ.
- Added ROM search fallback: `./roms` first, then script directory.

## Preserved/fixed from final-perfect CPU release

- `CPU6502` remains the final-perfect audited core.
- `C64` now instantiates CPU with `intercept_6510_port=True`.
- Direct host reads/writes to `$0000/$0001` update/consult the CPU-side 6510 latch.
- C64 banking uses `cpu.effective_6510_port()` to avoid CPU/C64 split-brain.
- `CPU6502.call/irq/nmi` now expose `last_stop_reason` and `last_instruction_count`, required by the integrated budget logic.

## Regression tests added

`tests/test_sid2midi_feature_integration.py` verifies:

- correct 2SID/3SID base formula;
- PSID mode RAM-under-ROM plus I/O visibility;
- CPU-owned 6510 port banking;
- CPU budget stop diagnostics for `sid2midi.py`;
- rational tick scaling;
- loop detector minimum-duration guard.

## Honest boundary

This integration improves SID2MIDI extraction semantics significantly, especially for PSID/RSID banking, 2SID/3SID and long batch runs. It remains an instruction-level SID-register extractor, not a Visual6502/RDY/VIC-DMA bus-cycle emulator.
