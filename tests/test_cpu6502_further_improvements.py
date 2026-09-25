import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502
import sid2midi

class Mem:
    def __init__(self): self.m = bytearray(65536)
    def read(self, a): return self.m[a & 0xFFFF]
    def write(self, a, v): self.m[a & 0xFFFF] = v & 0xFF
    def cpu(self, **kw): return CPU6502(self.read, self.write, **kw)

class CPU6502FurtherImprovementTests(unittest.TestCase):
    def test_trace_limit_is_bounded_and_reports_drops(self):
        mem = Mem(); c = mem.cpu(trace=True, trace_limit=3)
        mem.m[0x1000:0x1006] = bytes([0xEA,0xEA,0xEA,0xEA,0xEA,0xEA])
        c.pc = 0x1000
        for _ in range(5): self.assertTrue(c.step())
        self.assertEqual(len(c.opcode_trace), 3)
        self.assertEqual(c.trace_dropped, 2)
        self.assertEqual([x[0] for x in c.opcode_trace], [0x1002,0x1003,0x1004])

    def test_status_and_repr_include_port_and_opcode_diagnostics(self):
        mem = Mem(); c = mem.cpu(); mem.m[0x2000] = 0xEA; c.pc = 0x2000; c.step()
        st = c.status()
        self.assertEqual(st['last_opcode'], 0xEA)
        self.assertEqual(st['last_pc'], 0x2000)
        self.assertIn('port_effective', st)
        self.assertIn('CPU6502', repr(c))

    def test_6510_effective_port_uses_pullups_for_input_bits(self):
        mem = Mem(); c = mem.cpu()
        c.write_6510_port(0x0000, 0x00)  # all input => pulled high
        c.write_6510_port(0x0001, 0x00)
        self.assertEqual(c.effective_6510_port(), 0x3F)
        c.write_6510_port(0x0000, 0x07)
        c.write_6510_port(0x0001, 0x00)
        self.assertEqual(c.effective_6510_port() & 0x07, 0x00)
        self.assertEqual(c.read_6510_port(0x0001) & 0x07, 0x00)

    def test_sid2midi_c64_uses_cpu_6510_port_for_banking(self):
        c64 = sid2midi.C64()
        c64.kernal = bytes([0xAA]) * 0x2000
        c64.basic = bytes([0xBB]) * 0x2000
        c64.chargen = bytes([0xCC]) * 0x1000
        c64.ram[0xE000] = 0x11
        c64.ram[0xA000] = 0x22
        c64.write(0x0000, 0x07)
        c64.write(0x0001, 0x07)
        self.assertEqual(c64.read(0xE000), 0xAA)
        self.assertEqual(c64.read(0xA000), 0xBB)
        c64.write(0x0001, 0x00)
        self.assertEqual(c64.read(0xE000), 0x11)
        self.assertEqual(c64.read(0xA000), 0x22)

    def test_valid_bcd_adc_sbc_digit_arithmetic_exhaustive(self):
        for a_dec in range(100):
            for m_dec in range(100):
                a = ((a_dec // 10) << 4) | (a_dec % 10)
                m = ((m_dec // 10) << 4) | (m_dec % 10)
                for cin in (0,1):
                    mem = Mem(); c = mem.cpu(); c.D=1; c.a=a; c.C=cin; c._adc(m)
                    total = a_dec + m_dec + cin
                    exp = (((total % 100) // 10) << 4) | ((total % 100) % 10)
                    self.assertEqual((c.a, c.C), (exp, 1 if total >= 100 else 0), (a_dec,m_dec,cin))
                    mem = Mem(); c = mem.cpu(); c.D=1; c.a=a; c.C=cin; c._sbc(m)
                    total = a_dec - m_dec - (1-cin)
                    exp_dec = total % 100
                    exp = ((exp_dec // 10) << 4) | (exp_dec % 10)
                    self.assertEqual((c.a, c.C), (exp, 1 if total >= 0 else 0), ('sbc',a_dec,m_dec,cin))

if __name__ == '__main__':
    unittest.main()
