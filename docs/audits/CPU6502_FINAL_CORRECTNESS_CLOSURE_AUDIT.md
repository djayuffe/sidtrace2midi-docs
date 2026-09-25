# CPU6502 final correctness closure audit

This closure implements the final CPU6502 audit findings from the post-release review.

## Fixed

- Reworked bounded trace accounting so `trace_dropped` is derived from total appended trace entries minus retained deque length.
- Added `trace_total` to `status()`.
- Added `clear_trace()` to reset trace buffer and counters.
- Added direct `step()` stop-reason updates for ordinary step, BRK and JAM.
- Added explicit regression proving `OFFICIAL_OPS` is exactly the 151 documented NMOS 6502 official opcodes.
- Added configurable 6510-port side-effect mirroring:
  - `mirror_6510_port_writes=True` by default, preserving host RAM/log mirrors.
  - `mirror_6510_port_reads=False` by default, with optional read-side logging/side-effect calls.
- Removed unused `_bcd_to_int()` and `_int_to_bcd()` helpers.
- Updated CPU docstring to document decimal policies, trace options and 6510 interception.

## Accuracy boundary kept honest

The CPU remains instruction-level. It is complete for SID-register extraction and robust PSID/RSID play calls, but it does not claim transistor-level invalid-BCD, RDY/SYNC, VIC badline/DMA, or RMW dummy-write bus fidelity.

## New regression file

`tests/test_cpu6502_final_correctness_closure.py`
