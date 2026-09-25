# Complete system map

This document explains how the project is wired end-to-end.

```mermaid
flowchart LR
  A[HVSC SID / PSID / RSID] --> B[SID header parser]
  B --> C[C64 memory image]
  C --> D[NMOS CPU6502 / 6510 port]
  D --> E[Init/play or IRQ calls]
  E --> F[SID/CIA/VIC register writes]
  F --> G[SidFrame stream]
  G --> H[Loop detector / timing normalizer]
  H --> I[MIDI tracks + CC + pitch bend]
  I --> J[DAW import]
```

## Main modules

| Module | Responsibility |
|---|---|
| `cpu6502.py` | Instruction-level NMOS 6502/6510 execution, opcodes, stack, IRQ/NMI, diagnostics. |
| `sid2midi.py` | SID parser, C64 runtime, register capture, frame conversion, MIDI writer. |
| `sidtrace2midi.py` | Public launcher with the clearer project name. |
| `convert_top100_*.py` | HVSC batch selection, retry policy, manifest generation. |
| `validate_top100_*.py` | Manifest quality gates. |
| `tools/analyze_top100_manifest.py` | Triage and rerun command generation. |

## Execution order

1. Parse SID header and select subtune.
2. Build a C64 memory view with RAM, ROM visibility, I/O, SID and CIA registers.
3. Initialize the 6510 port state before SID payload setup.
4. Run `init` using CPU6502.
5. Repeatedly run `play` or IRQ entrypoint.
6. Capture every SID register write into a canonical `SidFrame`.
7. Convert register history into note, CC, pitch bend and metadata events.
8. Sort events with deterministic ordering and write the MIDI file.
