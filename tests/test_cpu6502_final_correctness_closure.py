import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cpu6502 import CPU6502

OFFICIAL_6502_OPS = frozenset((
    0x00,0x01,0x05,0x06,0x08,0x09,0x0A,0x0D,0x0E,0x10,0x11,0x15,0x16,0x18,0x19,0x1D,0x1E,
    0x20,0x21,0x24,0x25,0x26,0x28,0x29,0x2A,0x2C,0x2D,0x2E,0x30,0x31,0x35,0x36,0x38,0x39,0x3D,0x3E,
    0x40,0x41,0x45,0x46,0x48,0x49,0x4A,0x4C,0x4D,0x4E,0x50,0x51,0x55,0x56,0x58,0x59,0x5D,0x5E,
    0x60,0x61,0x65,0x66,0x68,0x69,0x6A,0x6C,0x6D,0x6E,0x70,0x71,0x75,0x76,0x78,0x79,0x7D,0x7E,
    0x81,0x84,0x85,0x86,0x88,0x8A,0x8C,0x8D,0x8E,0x90,0x91,0x94,0x95,0x96,0x98,0x99,0x9A,0x9D,
    0xA0,0xA1,0xA2,0xA4,0xA5,0xA6,0xA8,0xA9,0xAA,0xAC,0xAD,0xAE,0xB0,0xB1,0xB4,0xB5,0xB6,0xB8,0xB9,0xBA,0xBC,0xBD,0xBE,
    0xC0,0xC1,0xC4,0xC5,0xC6,0xC8,0xC9,0xCA,0xCC,0xCD,0xCE,0xD0,0xD1,0xD5,0xD6,0xD8,0xD9,0xDD,0xDE,
    0xE0,0xE1,0xE4,0xE5,0xE6,0xE8,0xE9,0xEA,0xEC,0xED,0xEE,0xF0,0xF1,0xF5,0xF6,0xF8,0xF9,0xFD,0xFE,
))

class Mem:
    def __init__(self):
        self.m = bytearray(65536)
        self.reads = []
        self.writes = []
    def read(self, a):
        self.reads.append(a & 0xFFFF)
        return self.m[a & 0xFFFF]
    def write(self, a, v):
        self.writes.append((a & 0xFFFF, v & 0xFF))
        self.m[a & 0xFFFF] = v & 0xFF

class CPU6502FinalCorrectnessClosureTests(unittest.TestCase):
    def test_official_opcode_set_is_complete_and_exact(self):
        self.assertEqual(len(OFFICIAL_6502_OPS), 151)
        self.assertEqual(CPU6502.OFFICIAL_OPS, OFFICIAL_6502_OPS)

    def test_official_opcode_diagnostics_do_not_mark_official_nop_jmp_jsr_branch_illegal(self):
        mem = Mem()
        # NOP; JMP $2004; JSR $2008 is not executed; branch is official too.
        mem.m[0x2000:0x2008] = bytes([0xEA, 0x4C, 0x04, 0x20, 0x10, 0x00, 0x20, 0x08])
        cpu = CPU6502(mem.read, mem.write)
        cpu.pc = 0x2000
        cpu.step()  # NOP
        cpu.step()  # JMP
        cpu.step()  # BPL +0
        self.assertEqual(cpu.illegal_opcode_count, 0)

    def test_trace_dropped_counter_is_exact_and_clearable(self):
        mem = Mem()
        mem.m[0x3000:0x3008] = bytes([0xEA] * 8)
        cpu = CPU6502(mem.read, mem.write, trace=True, trace_limit=3)
        cpu.pc = 0x3000
        for _ in range(8):
            cpu.step()
        self.assertEqual(cpu.status()['trace_seen'], 8)
        self.assertEqual(cpu.status()['trace_total'], 3)
        self.assertEqual(cpu.status()['trace_len'], 3)
        self.assertEqual(cpu.status()['trace_dropped'], 5)
        self.assertEqual([x[0] for x in cpu.trace_snapshot()], [0x3005, 0x3006, 0x3007])
        cpu.clear_trace()
        self.assertEqual(cpu.status()['trace_total'], 0)
        self.assertEqual(cpu.status()['trace_len'], 0)
        self.assertEqual(cpu.status()['trace_dropped'], 0)

    def test_direct_step_updates_stop_reason_for_brk_jam_and_step(self):
        mem = Mem()
        mem.m[0xFFFE] = 0x00
        mem.m[0xFFFF] = 0x40
        mem.m[0x4000] = 0xEA
        cpu = CPU6502(mem.read, mem.write)
        cpu.pc = 0x4000
        self.assertTrue(cpu.step())
        self.assertEqual(cpu.last_stop_reason, 'step')
        self.assertEqual(cpu.last_instruction_count, 1)
        mem.m[0x4001] = 0x00
        self.assertTrue(cpu.step())
        self.assertEqual(cpu.last_stop_reason, 'brk')
        mem.m[0x5000] = 0x02
        cpu.pc = 0x5000
        self.assertFalse(cpu.step())
        self.assertEqual(cpu.last_stop_reason, 'jam')

    def test_6510_port_intercept_read_side_effects_are_configurable(self):
        mem = Mem()
        cpu = CPU6502(mem.read, mem.write, intercept_6510_port=True, mirror_6510_port_reads=True)
        cpu.write(0x0000, 0x00)
        cpu.write(0x0001, 0x00)
        self.assertEqual(cpu.read(0x0001), 0x3F)
        self.assertIn(0x0001, mem.reads)
        self.assertIn((0x0001, 0x00), mem.writes)
        mem2 = Mem()
        cpu2 = CPU6502(mem2.read, mem2.write, intercept_6510_port=True, mirror_6510_port_writes=False)
        cpu2.write(0x0001, 0x12)
        self.assertNotIn((0x0001, 0x12), mem2.writes)
        self.assertEqual(cpu2.read(0x0001) & 0x3F, cpu2.effective_6510_port())

    def test_dead_bcd_converter_helpers_removed_from_public_core(self):
        self.assertFalse(hasattr(CPU6502, '_bcd_to_int'))
        self.assertFalse(hasattr(CPU6502, '_int_to_bcd'))

if __name__ == '__main__':
    unittest.main()
