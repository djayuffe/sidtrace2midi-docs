# NMOS 6502 audit-driven improvement pass

This pass applies the requested CPU audit improvements while keeping the core aligned with the SID2MIDI goal: robust PSID/RSID SID-register extraction using callback-based C64 memory I/O.

## Fixed / improved

- Fixed KERNAL IRQ exit stack restore: the status byte is popped once, then PC low/high are restored. This closes a brittle double-`_setp()` bug in the final closure.
- Added `nmi()` support through vector `$FFFA/$FFFB` with proper PC/P stack push and RTI/sentinel/JAM termination.
- Added `reset()` and `reset_jam()` lifecycle helpers.
- Added strict forensic modes:
  - `strict_jam=True` raises on KIL/JAM instead of silent safe-stop.
  - `strict_unstable=True` raises on unstable NMOS opcodes.
- Added opcode diagnostics:
  - `last_opcode`
  - `last_pc`
  - `opcode_count`
  - `illegal_opcode_count`
  - `unstable_opcode_count`
  - `jam_count`
  - optional `opcode_trace`
- Added practical unstable opcode approximations:
  - `ANE` / `XAA` `$8B`
  - `LXA` `$AB`
  - configurable `ane_magic` and `lxa_magic` defaults.
- Added optional 6510 processor-port helper storage for `$0000/$0001` tests/tools:
  - `write_6510_port(addr, value)`
  - `read_6510_port(addr)`
- Reworked decimal `ADC`/`SBC` into clearer NMOS-oriented implementations with binary intermediate flags and BCD-adjusted results.
- Updated opcode coverage report to use `CPU6502` class constants and report strict/unstable opcodes.
- Added regression tests for all changes.

## Honest boundary

This is still intentionally an instruction-level SID-extraction CPU, not a Visual6502-level bus/transistor model. It does not perform per-cycle bus tracing, VIC DMA/RDY stealing, or hardware-locking endless JAM. For SID2MIDI batch extraction, default JAM behavior is safe-stop; strict mode is available for forensic runs.
