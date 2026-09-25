# NMOS 6502 Further Improvement Audit

This pass implements the remaining actionable audit recommendations that fit the SID2MIDI project scope.

## Implemented

### 1. 6510 port split-brain closure

The CPU already had `$0000/$0001` helper storage, but the C64 host still used `ram[1]` directly for banking.  That could create a split-brain if player code changed the 6510 processor port during init/play.

Now:

- `CPU6502.effective_6510_port()` returns the effective $0001 banking value with input bits pulled high.
- `C64.read()` returns CPU-side `$0000/$0001` state.
- `C64.write()` forwards writes to `$0000/$0001` into the CPU latch and mirrors RAM.
- C64 BASIC/KERNAL/CHARGEN/I/O banking consults `cpu.effective_6510_port()`.
- `load_sid()` initializes both RAM mirror and CPU-side latch to `$0000=$2F`, `$0001=$37`.

### 2. Trace memory safety

`trace=True` could grow without bound during long HVSC batch runs.  The CPU now accepts:

```python
CPU6502(read, write, trace=True, trace_limit=4096)
```

Behavior:

- trace is bounded by `trace_limit`;
- oldest trace entries are dropped when full;
- `trace_dropped` counts dropped entries;
- `trace_limit=None` allows unlimited trace for explicit forensic runs.

### 3. Status / repr API

Added:

```python
cpu.status()
repr(cpu)
```

`status()` returns registers, flags, cycle count, last opcode/PC, opcode counters, trace size/drop count and 6510 port state.  This makes SID-player failure logs much easier to understand.

### 4. BCD confidence tests

Added exhaustive valid-BCD digit arithmetic tests for ADC/SBC over all 00-99 operands and carry states.  This does not claim transistor-level Visual6502 decimal flags for invalid BCD inputs, but it verifies the most important SID/decruncher-useful valid BCD arithmetic domain.

### 5. Documentation of honest limits

The release documents that it remains instruction-level and SID-extraction oriented, not per-cycle Visual6502/RDY/VIC-DMA exact.  Unstable opcodes remain configurable/bounded by policy.

## Tests added

```text
tests/test_cpu6502_further_improvements.py
```

Covers:

- bounded trace and `trace_dropped`;
- `status()` and `__repr__()`;
- effective 6510 port pull-up behavior;
- sid2midi C64 host banking via CPU-side port;
- exhaustive valid BCD ADC/SBC digit arithmetic.

## Remaining honest boundary

This core is now stronger for SID2MIDI PSID/RSID register extraction.  It is still not a transistor-level emulator: it does not emulate RDY, per-cycle bus phases, VIC badline DMA interference, or silicon-dependent unstable opcode analog variance.
