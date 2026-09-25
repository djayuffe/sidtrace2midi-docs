import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502
import sid2midi

class Mem:
    def __init__(self):
        self.m = bytearray(65536); self.reads=[]; self.writes=[]
    def read(self,a):
        self.reads.append(a & 0xffff); return self.m[a & 0xffff]
    def write(self,a,v):
        self.writes.append((a & 0xffff, v & 0xff)); self.m[a & 0xffff]=v & 0xff

class FinalCleanupPerfectionTests(unittest.TestCase):
    def test_trace_counters_have_clear_current_vs_lifetime_semantics(self):
        mem = Mem(); mem.m[0x1000:0x1008] = bytes([0xEA] * 8)
        cpu = CPU6502(mem.read, mem.write, trace=True, trace_limit=3)
        cpu.pc = 0x1000
        for _ in range(8):
            self.assertTrue(cpu.step())
        st = cpu.status()
        self.assertEqual(st['trace_seen'], 8)
        self.assertEqual(st['trace_total'], 3)
        self.assertEqual(st['trace_len'], 3)
        self.assertEqual(st['trace_dropped'], 5)
        self.assertEqual([row[0] for row in cpu.trace_snapshot()], [0x1005, 0x1006, 0x1007])

    def test_official_opcode_set_is_complete_for_diagnostics(self):
        self.assertEqual(len(CPU6502.OFFICIAL_OPS), 151)
        for op in (0x00,0x20,0x40,0x4C,0x60,0x6C,0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0):
            self.assertIn(op, CPU6502.OFFICIAL_OPS)

    def test_6510_mirror_read_error_is_counted_but_does_not_override_port(self):
        def bad_read(addr):
            raise RuntimeError('logger failed')
        mem = Mem()
        cpu = CPU6502(bad_read, mem.write, intercept_6510_port=True, mirror_6510_port_reads=True)
        self.assertEqual(cpu.read(0x0001) & 0x3f, cpu.effective_6510_port())
        self.assertEqual(cpu.status()['port_mirror_read_errors'], 1)

    def test_frame_helpers_reject_malformed_legacy_frames(self):
        with self.assertRaises(ValueError):
            sid2midi._frame_regs((bytes(0x19),), 1)
        with self.assertRaises(TypeError):
            sid2midi._frame_trig(object(), 0)

    def test_raw_register_json_export_helper(self):
        frame = sid2midi.make_frame(bytes(range(25)), (1,0,0), (123,-1,-1), digi=9)
        js = sid2midi.frame_to_jsonable(frame)
        self.assertEqual(js['sidA'][0:3], [0,1,2])
        self.assertEqual(js['trigA'], [1,0,0])
        self.assertEqual(js['trigcycA'][0], 123)
        self.assertEqual(js['digi'], 9)

    def test_cia_advance_modes_are_explicit(self):
        c = sid2midi.C64(cia_advance_mode='post_call')
        self.assertEqual(c.cia_advance_mode, 'post_call')
        with self.assertRaises(ValueError):
            sid2midi.C64(cia_advance_mode='bad')

if __name__ == '__main__':
    unittest.main()
