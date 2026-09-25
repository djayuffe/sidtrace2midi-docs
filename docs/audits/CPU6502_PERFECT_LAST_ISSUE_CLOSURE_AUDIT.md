# CPU6502 Perfect Last-Issue Closure Audit

This closure pass verifies and finalizes the last CPU6502 audit items raised after the complete SID2MIDI release.

## Fixed / verified

### 1. Trace dropped counter

The legacy pattern:

```python
before_len = len(self.opcode_trace)
self.opcode_trace.append(item)
if before_len == self.trace_limit:
    self.trace_dropped += 1
```

is not present.  The trace accounting is now derived from the source of truth:

```python
trace_dropped = trace_total - len(opcode_trace)
```

This is correct for `deque(maxlen=N)` because the deque itself owns eviction.

Additional closure:

- `trace_limit=N` keeps newest N rows.
- `trace_limit=None` is unbounded and drop-free.
- `trace_limit=0` is explicit counter-only tracing: no rows are stored, and every traced instruction counts as dropped from the retained buffer.
- `clear_trace()` resets buffer and counters.

### 2. Official opcode set

`CPU6502.OFFICIAL_OPS` is verified to exactly contain the 151 official NMOS 6502 opcodes.  The final regression checks that BRK, JSR, JMP, RTS and all branch opcodes are included and do not inflate `illegal_opcode_count`.

### 3. Dead BCD helpers

Unused `_bcd_to_int()` and `_int_to_bcd()` helpers remain removed.  Decimal mode is documented as practical NMOS/SID extraction behavior, not transistor-level invalid-BCD analog behavior.

### 4. 6510 port mirroring policy

The 6510 `$0000/$0001` intercept path now has explicit host side-effect knobs:

- `mirror_6510_port_writes=True` by default.
- `mirror_6510_port_reads=False` by default.

The tests verify both logging/side-effect mode and CPU-owned isolated mode.

### 5. Debug helper

Added `disassemble_at(addr=None)` as a safe, non-mutating diagnostic helper.  It includes raw opcode bytes even for undocumented or unknown opcodes, so trace analysis remains useful without claiming a full symbolic disassembler.

## Validation

New regression file:

```text
tests/test_cpu6502_perfect_last_issue_closure.py
```

It checks:

- absence of the old trace-counter bug pattern;
- exact trace accounting for `trace_limit=0`, bounded traces and unbounded traces;
- official opcode set correctness for high-risk official opcodes;
- non-mutating disassembly helper behavior;
- explicit 6510 port mirror policy.

## Remaining accuracy boundary

The CPU is complete for the SID2MIDI goal: instruction-level NMOS 6502/6510 SID-register extraction.  It intentionally does not claim Visual6502/per-PHI2 transistor accuracy, RDY/SYNC pin timing, VIC badline/DMA interference, or invalid-BCD silicon analog edge cases.
