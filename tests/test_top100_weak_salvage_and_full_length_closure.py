import json, os, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Top100WeakSalvageAndFullLengthClosureTests(unittest.TestCase):
    def test_wrappers_prefer_near_full_600s_auto_loop_policy(self):
        for name in ("convert_top100_exact.sh", "convert_top100_demos_exact.sh", "convert_top100_cracktros_exact.sh"):
            text = (ROOT / name).read_text()
            self.assertIn("--seconds 600", text)
            self.assertIn("--auto-min-seconds 540", text)
            self.assertIn("--auto-confirm-windows 3", text)
            self.assertIn("--timeout 300", text)

    def test_batch_engine_deletes_weak_existing_midi_before_skip_existing(self):
        import convert_top25_hvsc as core
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / "hvsc"; hvsc.mkdir()
            sid = hvsc / "Weak.sid"; sid.write_bytes(b"PSID" + b"\0" * 0x7c)
            out = td / "out"; out.mkdir()
            # malformed tiny file gives None notes, so create a valid-ish MIDI with zero note-ons
            (out / "01_Weak.mid").write_bytes(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00`MTrk\x00\x00\x00\x04\x00\xff/\x00")
            old = core.TOP25
            core.TOP25 = (core.TopTune(1, "Weak", "test", 125, 1, ("Weak.sid",)),)
            try:
                # dry-run after weak-existing deletion avoids calling sid2midi.
                rc = core.main(["--hvsc", str(hvsc), "--out", str(out), "--limit", "1", "--skip-existing", "--dry-run", "--min-notes", "1", "--manifest-prefix", "weakskip"])
            finally:
                core.TOP25 = old
            self.assertEqual(rc, 0)
            rows = json.loads((out / "weakskip_manifest.json").read_text())
            self.assertEqual(rows[0]["status"], "ok")
            self.assertNotIn("/skip-existing", rows[0]["duration_policy"])

    def test_sid_song_count_reads_psid_header(self):
        import convert_top25_hvsc as core
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "multi.sid"
            data = bytearray(b"PSID" + b"\0" * 0x7c)
            data[0x0E:0x10] = (7).to_bytes(2, "big")
            p.write_bytes(data)
            self.assertEqual(core.sid_song_count(p), 7)

if __name__ == "__main__":
    unittest.main()
