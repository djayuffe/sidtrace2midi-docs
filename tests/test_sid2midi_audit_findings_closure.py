import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import sid2midi


def make_minimal_psid(path: Path, *, magic=b"PSID", load=0x1000, init=0x1000, play=0x1001, flags=0x14, payload=b"\x60\x60"):
    off = 0x7C
    h = bytearray(off)
    h[0:4] = magic
    def be16(pos, val): h[pos:pos+2] = int(val).to_bytes(2, 'big')
    def be32(pos, val): h[pos:pos+4] = int(val).to_bytes(4, 'big')
    be16(4, 4); be16(6, off); be16(8, load); be16(10, init); be16(12, play)
    be16(14, 1); be16(16, 1); be32(18, 0)
    h[0x16:0x36] = b'Audit'.ljust(32, b'\0')
    h[0x36:0x56] = b'Test'.ljust(32, b'\0')
    h[0x56:0x76] = b'2026'.ljust(32, b'\0')
    be16(0x76, flags)
    path.write_bytes(bytes(h) + payload)
    return path


class Sid2MidiAuditFindingsClosureTests(unittest.TestCase):
    def test_sidframe_is_named_and_tuple_compatible(self):
        regs = bytes(range(0x19))
        f = sid2midi.make_frame(regs, (1,0,0), (11,-1,-1), digi=7)
        self.assertEqual(f.sidA[0], 0)
        self.assertEqual(f[0][1], 1)
        self.assertEqual(sid2midi._frame_regs(f, 0), regs)
        self.assertEqual(sid2midi._frame_trig(f, 0), (1,0,0))
        self.assertEqual(sid2midi._frame_trigcyc(f, 0), (11,-1,-1))
        self.assertEqual(sid2midi._frame_digi(f), 7)

    def test_c64_load_sid_sets_cpu_port_before_payload_visible(self):
        with tempfile.TemporaryDirectory() as td:
            sid = sid2midi.SidFile(str(make_minimal_psid(Path(td) / 'x.sid')))
            c = sid2midi.C64(psid_mode=False)
            c.write(0x0001, 0x00)
            c.load_sid(sid)
            self.assertEqual(c.cpu.read_6510_port(0x0000), 0x2F)
            self.assertEqual(c.cpu.read_6510_port(0x0001), c.cpu.effective_6510_port())
            self.assertEqual(c.ram[0x0001], 0x37)

    def test_cia_advance_timer_a_underflow_and_reload(self):
        c = sid2midi.C64(psid_mode=False)
        c.write(0xDC04, 9); c.write(0xDC05, 0)
        c.write(0xDC0D, 0x81)
        c.write(0xDC0E, 0x11)  # load + start continuous
        c.advance_cia(10)
        self.assertTrue(c.icr_data & 1)
        self.assertGreater(c.ta_count, 0)

    def test_cia_timer_b_can_count_timer_a_underflows(self):
        c = sid2midi.C64(psid_mode=False)
        c.write(0xDC04, 4); c.write(0xDC05, 0)
        c.write(0xDC06, 1); c.write(0xDC07, 0)
        c.write(0xDC0D, 0x83)
        c.write(0xDC0E, 0x11)
        c.write(0xDC0F, 0x31)  # load + start + count Timer A underflows
        c.advance_cia(5)
        self.assertTrue(c.icr_data & 1)
        self.assertTrue(c.icr_data & 2)

    def test_respect_irq_disable_does_not_force_clear_i(self):
        c = sid2midi.C64(psid_mode=False, force_irq_if_masked=False)
        c.cpu.I = 1
        # Minimal sid-like object sufficient for current_timer_period fallback.
        class S:
            frame = sid2midi.PAL_FRAME
            def vsync(self, song): return True
        f = c.step_call(S(), irq=True, max_ins=1, song=0)
        self.assertEqual(c.last_call_reason, 'irq_masked')
        self.assertEqual(c.irq_masked_count, 1)
        self.assertEqual(sid2midi._frame_digi(f), 0)

    def test_rom_report_lines_are_explicit(self):
        lines = sid2midi.rom_report_lines()
        self.assertTrue(any('kernal.bin' in line for line in lines))
        self.assertTrue(all(('ROM ' in line and (('OK' in line) or ('MISSING' in line))) for line in lines))

    def test_report_prints_rom_status(self):
        with tempfile.TemporaryDirectory() as td:
            p = make_minimal_psid(Path(td) / 'x.sid')
            out = Path(td) / 'x.mid'
            buf = io.StringIO()
            with redirect_stdout(buf):
                sid2midi.main([str(p), '--seconds', '0.02', '--report', '-o', str(out)])
            self.assertIn('ROM kernal.bin:', buf.getvalue())
            self.assertTrue(out.exists())


if __name__ == '__main__':
    unittest.main()
