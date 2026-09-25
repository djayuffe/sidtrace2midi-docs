import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sid2midi


def make_basic_sys_psid(path: Path, target=49152):
    # Tokenized BASIC at $0801: 10 SYS <target>
    line = bytearray()
    line += b'\x00\x00'          # next ptr patched below
    line += (10).to_bytes(2, 'little')
    line += bytes([0x9E]) + str(target).encode('ascii') + b'\x00'
    next_ptr = 0x0801 + len(line) + 2
    line[0:2] = next_ptr.to_bytes(2, 'little')
    body = bytes(line) + b'\x00\x00'
    off = 0x7C
    h = bytearray(off)
    h[0:4] = b'RSID'
    def be16(pos, val): h[pos:pos+2] = int(val).to_bytes(2, 'big')
    def be32(pos, val): h[pos:pos+4] = int(val).to_bytes(4, 'big')
    be16(4, 4); be16(6, off); be16(8, 0x0801); be16(10, 0); be16(12, 0)
    be16(14, 1); be16(16, 1); be32(18, 0)
    h[0x16:0x36] = b'Basic SYS'.ljust(32, b'\0')
    h[0x36:0x56] = b'Test'.ljust(32, b'\0')
    h[0x56:0x76] = b'2026'.ljust(32, b'\0')
    be16(0x76, 0x0002)  # BASIC flag
    path.write_bytes(bytes(h) + body)
    return path


class Sid2MidiFinalFeatureClosureTests(unittest.TestCase):
    def test_cli_help_exposes_integrated_feature_flags(self):
        exe = Path(__file__).resolve().parents[1] / 'sid2midi.py'
        cp = subprocess.run([sys.executable, str(exe), '--help'], text=True, capture_output=True, check=True)
        for flag in ('--ppq', '--auto-bpm', '--auto-min-seconds', '--auto-confirm-windows', '--max-ins-init', '--salvage-init'):
            self.assertIn(flag, cp.stdout)

    def test_vlq_boundaries_and_large_meta_lengths(self):
        self.assertEqual(sid2midi.vlq(0), b'\x00')
        self.assertEqual(sid2midi.vlq(127), b'\x7f')
        self.assertEqual(sid2midi.vlq(128), b'\x81\x00')
        self.assertEqual(sid2midi.vlq(16383), b'\xff\x7f')
        tr = sid2midi.Trk('long-meta')
        tr.meta(0, 0x01, 'A' * 200)
        blob = tr.render()
        self.assertIn(b'\xff\x01\x81\x48' + b'A' * 200, blob)

    def test_basic_sys_scanner_extracts_rsid_basic_entry(self):
        with tempfile.TemporaryDirectory() as td:
            p = make_basic_sys_psid(Path(td) / 'basic_sys.sid', target=49152)
            sid = sid2midi.SidFile(str(p))
            self.assertTrue(sid.rsid)
            self.assertTrue(sid.basic_player)
            self.assertEqual(sid.basic_sys, 49152)

    def test_timer_period_helper_prefers_timer_a_then_timer_b_then_frame(self):
        class DummySid:
            frame = 19656
            def vsync(self, song): return False
        c = sid2midi.C64(psid_mode=False)
        sid = DummySid()
        self.assertEqual(c.current_timer_period(sid, 0, True), sid.frame)
        c.tb_latch = 1234; c.icr_mask = 2
        self.assertEqual(c.current_timer_period(sid, 0, True), 1235)
        c.ta_latch = 4567; c.icr_mask = 3
        self.assertEqual(c.current_timer_period(sid, 0, True), 4568)

    def test_auto_bpm_grid_formula(self):
        self.assertAlmostEqual(sid2midi.grid_bpm_from_c64(50, 6, 4), 125.0)
        self.assertAlmostEqual(sid2midi.grid_bpm_from_c64(60, 6, 4), 150.0)


if __name__ == '__main__':
    unittest.main()
