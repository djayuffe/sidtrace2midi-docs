import tempfile
import unittest
from pathlib import Path

import sid2midi
from cpu6502 import CPU6502


def make_psid(path: Path, *, version=4, load=0x1000, init=0x1000, play=0x1003, songs=1, start=1, flags=0x14, sid2off=0x42, sid3off=0x50, payload=b'\x60\xea\x60'):
    off = 0x7C if version >= 4 else 0x7A
    h = bytearray(off)
    h[0:4] = b'PSID'
    def be16(pos, val): h[pos:pos+2] = int(val).to_bytes(2, 'big')
    def be32(pos, val): h[pos:pos+4] = int(val).to_bytes(4, 'big')
    be16(4, version); be16(6, off); be16(8, load); be16(10, init); be16(12, play)
    be16(14, songs); be16(16, start); be32(18, 0)
    h[0x16:0x36] = b'Test'.ljust(32, b'\0')
    h[0x36:0x56] = b'Author'.ljust(32, b'\0')
    h[0x56:0x76] = b'2026'.ljust(32, b'\0')
    be16(0x76, flags)
    if version >= 3 and off > 0x7A:
        h[0x7A] = sid2off
    if version >= 4 and off > 0x7B:
        h[0x7B] = sid3off
    path.write_bytes(bytes(h) + payload)
    return path


class Sid2MidiFeatureIntegrationTests(unittest.TestCase):
    def test_sidfile_uses_correct_2sid_3sid_base_formula(self):
        with tempfile.TemporaryDirectory() as td:
            p = make_psid(Path(td) / 'multi.sid', sid2off=0x42, sid3off=0x50)
            sid = sid2midi.SidFile(str(p))
            self.assertEqual(sid.sid2, 0xD420)
            self.assertEqual(sid.sid3, 0xD500)

    def test_c64_psid_mode_keeps_ram_under_rom_but_io_visible(self):
        c = sid2midi.C64(0xD420, 0xD500, psid_mode=True)
        c.ram[0xA000] = 0x5A
        c.write(0xD400, 0x34)
        c.write(0xD420, 0x56)
        c.write(0xD500, 0x78)
        self.assertEqual(c.read(0xA000), 0x5A)
        self.assertEqual(c.read(0xD400), 0x34)
        self.assertEqual(c.read(0xD420), 0x56)
        self.assertEqual(c.read(0xD500), 0x78)

    def test_c64_6510_port_uses_cpu_latch_for_banking(self):
        c = sid2midi.C64(psid_mode=False)
        # KERNAL visible by default. Hide KERNAL through a CPU-visible write to $0001.
        c.write(0x0001, 0x35)  # bit1 clear: KERNAL hidden, I/O still visible
        c.ram[0xE000] = 0xA5
        self.assertEqual(c.cpu.read_6510_port(0x0001) & 0x3F, c.mem_port() & 0x3F)
        self.assertEqual(c.read(0xE000), 0xA5)

    def test_cpu_call_records_max_ins_for_sid2midi_budget_logic(self):
        mem = bytearray(65536)
        # $1000: JMP $1000
        mem[0x1000:0x1003] = bytes([0x4C, 0x00, 0x10])
        c = CPU6502(lambda a: mem[a & 0xFFFF], lambda a, v: mem.__setitem__(a & 0xFFFF, v & 0xFF))
        c.call(0x1000, max_ins=3)
        self.assertEqual(c.last_stop_reason, 'max_ins')
        self.assertEqual(c.last_instruction_count, 3)

    def test_tick_scale_is_rational_and_ppq_configurable(self):
        tick, num, den = sid2midi.tick_scale(9600, 125, sid2midi.PAL_CLOCK)
        self.assertGreater(num, 0)
        self.assertGreater(den, 0)
        self.assertEqual(tick(0), 0)
        self.assertGreater(tick(sid2midi.PAL_FRAME), 0)

    def test_loop_detector_respects_min_seconds(self):
        regs = bytearray(0x19); regs[0]=0x34; regs[1]=0x12; regs[4]=0x41; regs[24]=0x0F
        frame = (bytes(regs), (1,0,0), (0,-1,-1), bytes(0x19), (0,0,0), (-1,-1,-1), bytes(0x19), (0,0,0), (-1,-1,-1), 0)
        frames = [frame for _ in range(2000)]
        self.assertEqual(sid2midi.find_loop(frames, 50, min_seconds=6, confirm_windows=1), 300)
        self.assertIsNone(sid2midi.find_loop(frames, 50, min_seconds=90, confirm_windows=1))


if __name__ == '__main__':
    unittest.main()
