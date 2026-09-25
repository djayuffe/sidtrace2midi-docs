# CPU6502 API Reference

`cpu6502.py` contains the callback-based NMOS 6502/6510 CPU used by `sid2midi.py`.

## Purpose

The CPU core executes SID player init/play routines so the host C64 model can capture writes to SID, CIA and VIC registers. It is not a full C64 emulator and does not claim PHI2/transistor-level fidelity.

## Construction

```python
from cpu6502 import CPU6502

cpu = CPU6502(read, write, intercept_6510_port=True)
```

`read(addr)` and `write(addr, value)` are host callbacks.

## Important constructor options

| Option | Meaning |
|---|---|
| `strict_jam` | Raise on JAM/KIL instead of stopping safely. |
| `strict_unstable` | Raise on unstable NMOS opcodes. |
| `trace` | Enable opcode trace. |
| `trace_limit` | Number of retained trace rows. `None` is unlimited, `0` is counter-only. |
| `ane_magic`, `lxa_magic` | Configurable unstable opcode magic constants. |
| `decimal_flags` | `nmos`, `binary`, `adjusted`, or `strict`. |
| `intercept_6510_port` | Let CPU own `$0000/$0001` latch behavior. |
| `mirror_6510_port_writes` | Forward port writes to host for RAM mirror/logging. |
| `mirror_6510_port_reads` | Allow host read side-effect hooks for port reads. |

## Main methods

| Method | Meaning |
|---|---|
| `reset(pc=None)` | Reset registers and optionally set PC. |
| `step()` | Execute one instruction. |
| `call(addr, a=0, x=0, y=0, max_ins=...)` | Call an init/play routine with sentinel return. |
| `irq(vec=0xFFFE, max_ins=...)` | Enter IRQ sequence. |
| `nmi(vec=0xFFFA, max_ins=...)` | Enter NMI sequence. |
| `status()` | Return register/counter diagnostics. |
| `step_dump()` | Execute one instruction and return before/after state. |
| `trace_snapshot()` | Return retained trace rows. |
| `clear_trace()` | Clear trace rows and trace counters. |
| `disassemble_at(addr=None)` | Non-mutating one-line opcode preview. |

## Diagnostics

The core tracks:

- `opcode_count`
- `illegal_opcode_count`
- `unstable_opcode_count`
- `jam_count`
- `brk_count`
- `last_opcode`
- `last_pc`
- `last_stop_reason`
- `last_instruction_count`
- `trace_seen`
- `trace_total`
- `trace_dropped`

## 6510 port model

The C64 CPU port lives at `$0000/$0001`.

- `$0000` is data direction.
- `$0001` is data latch.
- Effective port bits use pull-ups:

```text
effective = (port_data & port_dir) | (~port_dir & 0x3F)
```

`sid2midi.py` uses this for BASIC/KERNAL/CHARGEN/I/O banking.

## Accuracy boundary

Implemented:

- 151 official NMOS opcodes
- common undocumented opcodes used by C64 loaders/players
- safe JAM/KIL handling
- IRQ/NMI/BRK/RTI/RTS stack semantics suitable for SID extraction
- decimal-mode framework and strict invalid-BCD checking

Not implemented:

- Visual6502 transistor timing
- RDY/SYNC pin behavior
- VIC badline/DMA bus stealing
- exact invalid-BCD silicon quirks
- tape/serial pin side effects

