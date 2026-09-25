import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502

class Mem:
    def __init__(self): self.m = bytearray(65536)
    def read(self, a): return self.m[a & 0xFFFF]
    def write(self, a, v): self.m[a & 0xFFFF] = v & 0xFF
    def cpu(self, **kw): return CPU6502(self.read, self.write, **kw)

class CPU6502AuditImprovementTests(unittest.TestCase):
    def test_kernal_irq_exit_pops_status_only_once(self):
        mem = Mem(); c = mem.cpu()
        mem.m[0x0314] = 0x00; mem.m[0x0315] = 0x20
        mem.m[0x2000:0x2004] = bytes([0x4C,0x31,0xEA,0xEA])
        c.pc = 0x4567; c.a=0x12; c.x=0x34; c.y=0x56; c.C=1; c.D=1; c.I=0
        sp0 = c.sp
        c.irq(0x0314, kernal=True)
        self.assertEqual((c.pc, c.sp, c.a, c.x, c.y), (0x4567, sp0, 0x12, 0x34, 0x56))
        self.assertEqual((c.C, c.D), (1, 1))

    def test_nmi_ignores_interrupt_disable_and_rti_restores_context(self):
        mem = Mem(); c = mem.cpu()
        mem.m[0xFFFA] = 0x00; mem.m[0xFFFB] = 0x30
        mem.m[0x3000] = 0x40  # RTI
        c.pc = 0x2222; c.I = 1; c.C = 1; sp0 = c.sp
        cycles = c.nmi()
        self.assertGreaterEqual(cycles, 13)  # interrupt entry + RTI
        self.assertEqual(c.pc, 0x2222)
        self.assertEqual(c.sp, sp0)
        self.assertEqual(c.C, 1)

    def test_strict_jam_raises_and_default_jam_stops(self):
        mem = Mem(); c = mem.cpu(); mem.m[0x1000] = 0x02; c.pc = 0x1000
        self.assertFalse(c.step())
        self.assertTrue(c.jammed)
        c.reset_jam(); self.assertFalse(c.jammed)
        mem2 = Mem(); c2 = mem2.cpu(strict_jam=True); mem2.m[0x1000] = 0x02; c2.pc = 0x1000
        with self.assertRaises(RuntimeError): c2.step()

    def test_unstable_opcode_strict_mode_and_counters(self):
        mem = Mem(); c = mem.cpu(); mem.m[0x1000:0x1003] = bytes([0x8B,0x7F,0x60])
        c.a = 0x55; c.x = 0xF0; c.pc = 0x1000
        self.assertTrue(c.step())
        self.assertEqual(c.unstable_opcode_count, 1)
        self.assertEqual(c.illegal_opcode_count, 1)
        mem2 = Mem(); c2 = mem2.cpu(strict_unstable=True); mem2.m[0x1000:0x1002] = bytes([0x8B,0x7F]); c2.pc = 0x1000
        with self.assertRaises(RuntimeError): c2.step()

    def test_lxa_ane_practical_approximations_are_configurable(self):
        mem = Mem(); c = mem.cpu(ane_magic=0x00, lxa_magic=0x00)
        # ANE #$0F with A=$F0 X=$FF and magic 0 => result 0
        mem.m[0x1000:0x1004] = bytes([0x8B,0x0F,0xAB,0xF3])
        c.a = 0xF0; c.x = 0xFF; c.pc = 0x1000
        self.assertTrue(c.step()); self.assertEqual(c.a, 0x00)
        c.a = 0x0C
        self.assertTrue(c.step()); self.assertEqual((c.a,c.x), (0x00,0x00))
        mem2 = Mem(); c2 = mem2.cpu(lxa_magic=0xEE); mem2.m[0x2000:0x2002] = bytes([0xAB,0xF3]); c2.pc=0x2000; c2.a=0x0C
        self.assertTrue(c2.step()); self.assertEqual((c2.a,c2.x), (0xEE & 0xF3, 0xEE & 0xF3))

    def test_6510_port_helper_storage(self):
        mem = Mem(); c = mem.cpu()
        c.write_6510_port(0x0000, 0xFF); c.write_6510_port(0x0001, 0x35)
        self.assertEqual(c.read_6510_port(0x0000), 0x3F)
        self.assertEqual(c.read_6510_port(0x0001), 0x35)

    def test_trace_records_pre_instruction_state(self):
        mem = Mem(); c = mem.cpu(trace=True); mem.m[0x1000:0x1003] = bytes([0xA9,0x44,0xEA]); c.pc=0x1000
        self.assertTrue(c.step())
        self.assertEqual(c.opcode_trace[0][0:2], (0x1000, 0xA9))
        self.assertEqual(c.last_opcode, 0xA9)
        self.assertEqual(c.last_pc, 0x1000)

if __name__ == '__main__':
    unittest.main()
