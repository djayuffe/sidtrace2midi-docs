# SID2MIDI NMOS CPU Final Closure Report

This is the final cleaned release pass for the SID2MIDI NMOS CPU/SID-register-extraction package.

## Final status

The package is self-contained and dependency-free for the included CPU tests and SID smoke conversion.

Validated areas:

- Python syntax for CPU, converter, tests and tools
- Official 6502 opcode coverage
- Common NMOS undocumented opcode coverage
- KIL/JAM safe-stop policy
- Decimal ADC/SBC regression coverage
- JSR/RTS, BRK/RTI, IRQ and KERNAL IRQ restore behavior
- Branch cycle penalties
- Page-cross penalties
- Zero-page wrap behavior
- Opcode bounded one-step execution
- SID smoke conversion from `examples/simple_pulse.sid`
- SHA256 manifest integrity
- Zip integrity

## Final validation commands

```bash
./validate_release.sh
sha256sum -c SHA256SUMS.txt
python3 tools/cpu_opcode_coverage_report.py
python3 sid2midi.py examples/simple_pulse.sid --seconds 1 --report -o /tmp/simple_cpu_final.mid
```

## Scope boundary

This package is a SID2MIDI extraction engine. It is intentionally optimized for robust PSID/RSID SID-register extraction through a callback-based NMOS 6502/C64 runtime. It is not a transistor-level 6502 implementation and does not attempt to reproduce analog SID audio. JAM/KIL opcodes safely stop instead of hanging batch conversions.

## Audit-driven improvement addendum

The CPU core was improved based on the external audit notes. The most important functional fix is the KERNAL IRQ exit pop order: the status byte is now restored exactly once before PC low/high. Additional strict/trace modes make remaining hardware-accuracy boundaries explicit without making normal HVSC batch extraction fragile.
