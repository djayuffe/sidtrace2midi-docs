import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502

class Mem:
    def __init__(self):
        self.m = bytearray(65536)
        self.reads=[]; self.writes=[]
    def read(self,a):
        self.reads.append(a & 0xffff); return self.m[a & 0xffff]
    def write(self,a,v):
        self.writes.append((a & 0xffff, v & 0xff)); self.m[a & 0xffff]=v & 0xff

class CPU6502PerfectLastIssueClosureTests(unittest.TestCase):
    def test_trace_has_no_legacy_before_len_counter_logic(self):
        src = Path(__file__).resolve().parents[1].joinpath('cpu6502.py').read_text()
        self.assertNotIn('before_len', src)
        self.assertNotIn('trace_dropped +=', src)
        self.assertIn('trace_seen - self.trace_total', src)

    def test_trace_limit_zero_is_counter_only_not_unbounded(self):
        mem = Mem(); mem.m[0x2000:0x2008] = bytes([0xEA] * 8)
        cpu = CPU6502(mem.read, mem.write, trace=True, trace_limit=0)
        cpu.pc = 0x2000
        for _ in range(8):
            self.assertTrue(cpu.step())
        st = cpu.status()
        self.assertEqual(st['trace_seen'], 8)
        self.assertEqual(st['trace_total'], 0)
        self.assertEqual(st['trace_len'], 0)
        self.assertEqual(st['trace_dropped'], 8)
        self.assertEqual(cpu.trace_snapshot(), [])

    def test_trace_limit_none_is_unbounded_and_drop_free(self):
        mem = Mem(); mem.m[0x2100:0x2108] = bytes([0xEA] * 8)
        cpu = CPU6502(mem.read, mem.write, trace=True, trace_limit=None)
        cpu.pc = 0x2100
        for _ in range(8):
            self.assertTrue(cpu.step())
        st = cpu.status()
        self.assertEqual(st['trace_seen'], 8)
        self.assertEqual(st['trace_total'], 8)
        self.assertEqual(st['trace_len'], 8)
        self.assertEqual(st['trace_dropped'], 0)

    def test_official_opcodes_are_exact_and_do_not_inflate_illegal_counter(self):
        self.assertEqual(len(CPU6502.OFFICIAL_OPS), 151)
        for op in (0x00,0x20,0x4C,0x60,0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0):
            self.assertIn(op, CPU6502.OFFICIAL_OPS)
        mem = Mem(); mem.m[0x3000:0x3004] = bytes([0xEA, 0x4C, 0x03, 0x30])
        cpu = CPU6502(mem.read, mem.write); cpu.pc = 0x3000
        cpu.step(); cpu.step()
        self.assertEqual(cpu.illegal_opcode_count, 0)

    def test_disassemble_at_is_non_mutating_debug_helper(self):
        mem = Mem(); mem.m[0x4000:0x4004] = bytes([0x20, 0x34, 0x12, 0xEA])
        cpu = CPU6502(mem.read, mem.write); cpu.pc = 0x4000
        before = cpu.status().copy()
        line = cpu.disassemble_at()
        after = cpu.status().copy()
        self.assertIn('$4000:', line)
        self.assertIn('20 34 12', line)
        self.assertIn('JSR $1234', line)
        self.assertEqual(before['pc'], after['pc'])
        self.assertEqual(before['cycles'], after['cycles'])

    def test_6510_port_mirror_policies_are_explicit(self):
        mem = Mem()
        cpu = CPU6502(mem.read, mem.write, intercept_6510_port=True,
                      mirror_6510_port_writes=True, mirror_6510_port_reads=True)
        cpu.write(0x0000, 0x00)
        cpu.write(0x0001, 0x00)
        self.assertEqual(cpu.read(0x0001), 0x3F)
        self.assertIn((0x0001, 0x00), mem.writes)
        self.assertIn(0x0001, mem.reads)
        mem2 = Mem()
        cpu2 = CPU6502(mem2.read, mem2.write, intercept_6510_port=True,
                       mirror_6510_port_writes=False, mirror_6510_port_reads=False)
        cpu2.write(0x0001, 0x12)
        _ = cpu2.read(0x0001)
        self.assertEqual(mem2.writes, [])
        self.assertEqual(mem2.reads, [])

if __name__ == '__main__':
    unittest.main()
