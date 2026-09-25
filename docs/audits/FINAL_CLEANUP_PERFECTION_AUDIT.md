# Final cleanup/perfection audit

Implemented final low-level cleanup items for the combined CPU6502 + SID2MIDI path.

## Closed

- Trace counter semantics clarified and tested: retained rows vs lifetime seen instructions are no longer conflated.
- OFFICIAL_OPS remains locked to 151 official NMOS 6502 opcodes.
- Optional 6510 host read side-effect failures are counted and cannot corrupt CPU port state.
- Legacy frame helpers now reject malformed data loudly instead of silently returning zeroed register arrays.
- CIA timing order is an explicit API/CLI choice via `--cia-advance-mode`.
- Raw register stream export added through `--export-register-json`.

## Still intentionally out of scope

- Visual6502 transistor-level BCD invalid-input quirks.
- RDY/SYNC and per-PHI2 bus timing.
- VIC badline/sprite DMA interference.
- Full analog SID filter/digi reconstruction.
