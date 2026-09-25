# NMOS 6502 Final Perfect Audit

This final pass closes the last actionable issues from the exhaustive CPU audit while preserving the project boundary: SID register extraction and MIDI conversion, not Visual6502 transistor-level C64 emulation.

## Closed in this pass

- `decimal_flags` is no longer dead code.
  - Supported modes: `nmos`, `binary`, `adjusted`, `strict`.
  - `strict` rejects invalid BCD digits so test suites do not accidentally treat undefined NMOS invalid-BCD flag behavior as deterministic.
  - `adjusted` exposes adjusted-result flag behavior for comparison harnesses.
- Added bounded `deque` trace storage instead of `list.pop(0)`.
- Added `trace_snapshot()` for stable trace export.
- Added `step_dump()` for before/after single-step diagnostics.
- Added `brk_count` diagnostics.
- Added optional `intercept_6510_port=True` wrapper mode so CPU callbacks can automatically trap `$0000/$0001` while still forwarding writes to the host memory mirror.
- Replaced hot transfer/inc/dec flag lambdas using `setattr()` with direct assignment functions.
- Added final regression tests in `tests/test_cpu6502_final_perfect.py`.
- Updated opcode coverage report, release validation, manifest and SHA256 sums.

## Honest remaining boundary

The core is instruction-level and batch-safe. It does not model RDY, SYNC, transistor-level invalid BCD quirks, VIC-DMA/badline interference for unstable store opcodes, or exact per-cycle dummy read/write bus traces. Those are intentionally outside this SID2MIDI extractor scope.

## Validation

- 37 CPU regression tests pass.
- Opcode handlers: 256/256.
- Official opcodes covered: 151/151.
- SID smoke conversion succeeds.
- SHA256 and zip integrity verified.
