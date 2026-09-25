#!/usr/bin/env python3
"""Emit a compact opcode coverage report for the bundled CPU6502 core."""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502

class Mem:
    def __init__(self): self.m = bytearray(65536)
    def read(self, a): return self.m[a & 0xFFFF]
    def write(self, a, v): self.m[a & 0xFFFF] = v & 0xFF

def main() -> int:
    mem = Mem(); cpu = CPU6502(mem.read, mem.write)
    jam = CPU6502.JAM_OPS
    official = CPU6502.OFFICIAL_OPS
    unstable = CPU6502.UNSTABLE_OPS
    print("CPU6502 opcode coverage")
    print(f"handlers: {sum(1 for h in cpu.ops if h is not None)}/256")
    print(f"official opcodes covered: {len(official)}/151")
    print("jam opcodes:", " ".join(f"{x:02X}" for x in sorted(jam)))
    print("strict/unstable opcodes:", " ".join(f"{x:02X}" for x in sorted(unstable)))
    print(f"page-cross penalty opcodes: {len(CPU6502.PAGE_CROSS)}")
    print("diagnostics: last_opcode/last_pc/opcode_count/illegal_opcode_count/unstable_opcode_count/jam_count/brk_count/status()/trace_limit/deque/trace_seen/trace_total/clear_trace")
    print("policy: official + common NMOS illegal opcodes implemented; KIL/JAM safely stops by default; strict_jam/strict_unstable can raise; decimal_flags nmos/binary/adjusted/strict")
    print("6510 port: CPU-side $0000/$0001 latch + effective pull-up helper; optional intercept_6510_port wrapper with configurable host read/write side-effect mirroring; sid2midi C64 host consults it for banking")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
