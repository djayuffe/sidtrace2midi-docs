import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502

class Mem:
    def __init__(self):
        self.m = bytearray(65536)
        self.writes=[]
    def read(self,a): return self.m[a & 0xFFFF]
    def write(self,a,v):
        self.m[a & 0xFFFF] = v & 0xFF
        self.writes.append((a & 0xFFFF, v & 0xFF))
    def cpu(self, **kw): return CPU6502(self.read, self.write, **kw)

class CPU6502FinalPerfectTests(unittest.TestCase):
    def test_decimal_flags_modes_are_live_not_dead_code(self):
        # 99 + 01 produces adjusted BCD result 00 with carry, but binary low byte
        # is 9A.  This proves decimal_flags changes observable flags.
        m=Mem(); c=m.cpu(decimal_flags='adjusted'); c.D=1; c.a=0x99; c.C=0; c._adc(0x01)
        self.assertEqual(c.a, 0x00)
        self.assertEqual(c.Z, 1)             # adjusted-result policy
        m=Mem(); c=m.cpu(decimal_flags='nmos'); c.D=1; c.a=0x99; c.C=0; c._adc(0x01)
        self.assertEqual(c.a, 0x00)
        self.assertEqual(c.Z, 0)             # binary-intermediate policy

    def test_decimal_flags_strict_rejects_invalid_bcd_input(self):
        m=Mem(); c=m.cpu(decimal_flags='strict'); c.D=1; c.a=0x1A; c.C=1
        with self.assertRaises(ValueError): c._adc(0x00)
        m=Mem(); c=m.cpu(decimal_flags='strict'); c.D=1; c.a=0x10; c.C=1
        with self.assertRaises(ValueError): c._sbc(0x0A)
        with self.assertRaises(ValueError): m.cpu(decimal_flags='bogus')

    def test_trace_uses_bounded_deque_and_snapshot(self):
        m=Mem(); c=m.cpu(trace=True, trace_limit=2)
        m.m[0x2000:0x2004] = bytes([0xEA,0xEA,0xEA,0xEA])
        c.pc=0x2000
        for _ in range(4): c.step()
        self.assertEqual(len(c.opcode_trace), 2)
        self.assertEqual(c.trace_dropped, 2)
        self.assertEqual([x[0] for x in c.trace_snapshot()], [0x2002,0x2003])

    def test_brk_diagnostic_counter_and_step_dump(self):
        m=Mem(); c=m.cpu()
        m.m[0xFFFE]=0x00; m.m[0xFFFF]=0x40
        m.m[0x3000]=0x00
        c.pc=0x3000
        d=c.step_dump()
        self.assertTrue(d['ok'])
        self.assertEqual(c.brk_count, 1)
        self.assertEqual(c.pc, 0x4000)
        self.assertEqual(d['before']['pc'], 0x3000)
        self.assertEqual(d['after']['last_opcode'], 0x00)
        self.assertIn('brk_count', c.status())

    def test_cpu_can_intercept_6510_port_callbacks_automatically(self):
        m=Mem(); c=CPU6502(m.read, m.write, intercept_6510_port=True)
        c.write(0x0000, 0x00)
        c.write(0x0001, 0x00)
        self.assertEqual(c.read(0x0001), 0x3F)
        self.assertEqual(m.m[0x0001], 0x00)  # host mirror still receives write
        c.write(0x0000, 0x07)
        c.write(0x0001, 0x00)
        self.assertEqual(c.read(0x0001) & 0x07, 0x00)

if __name__ == '__main__':
    unittest.main()
