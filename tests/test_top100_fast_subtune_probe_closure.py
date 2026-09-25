import json, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Top100FastSubtuneProbeClosureTests(unittest.TestCase):
    def test_core_exposes_fast_probe_controls(self):
        import convert_top25_hvsc as core
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / "hvsc"; hvsc.mkdir()
            sid = hvsc / "Multi.sid"
            data = bytearray(b"PSID" + b"\0" * 0x7c)
            data[0x0E:0x10] = (6).to_bytes(2, "big")
            sid.write_bytes(data)
            out = td / "out"
            old_top, old_run = core.TOP25, core.run_command
            calls = []
            def fake_run(cmd, timeout):
                calls.append((list(map(str, cmd)), timeout))
                # selected song default fails; all alternate probes produce 0 notes.
                return 0, "/tmp/out.mid : 6 tracks, 0 notes, 41 CC, PPQ 9600, 45.0s @ grid 125 BPM\n", 0.01
            core.TOP25 = (core.TopTune(1, "Multi", "test", 125, 1, ("Multi.sid",)),)
            core.run_command = fake_run
            try:
                rc = core.main([
                    "--hvsc", str(hvsc), "--out", str(out), "--limit", "1",
                    "--keep-going", "--debug", "--min-notes", "100",
                    "--song-scan-limit", "6", "--subtune-zero-streak-limit", "2",
                    "--subtune-probe-seconds", "12", "--subtune-probe-timeout", "13",
                    "--manifest-prefix", "probezero",
                ])
            finally:
                core.TOP25, core.run_command = old_top, old_run
            self.assertEqual(rc, 0)
            # 4 selected-song retry attempts + only 2 alternate probes, then stop.
            # Old behavior would run 4 attempts for every alternate subtune.
            self.assertLessEqual(len(calls), 6)
            probe_calls = [c for c in calls if "--seconds" in c[0] and "12.0" in c[0]]
            self.assertEqual(len(probe_calls), 2)
            self.assertTrue(all(c[1] == 13.0 for c in probe_calls))
            rows = json.loads((out / "probezero_manifest.json").read_text())
            self.assertEqual(rows[0]["status"], "failed")

    def test_exhaustive_subtune_scan_keeps_old_behavior_available(self):
        text = (ROOT / "convert_top25_hvsc.py").read_text()
        self.assertIn("--exhaustive-subtune-scan", text)
        self.assertIn("--subtune-probe-seconds", text)
        self.assertIn("--subtune-zero-streak-limit", text)
        self.assertIn("make_probe_command", text)

    def test_wrappers_expose_fast_subtune_probe_defaults(self):
        for name in ("convert_top100_exact.sh", "convert_top100_demos_exact.sh", "convert_top100_cracktros_exact.sh"):
            text = (ROOT / name).read_text()
            self.assertIn("--subtune-probe-seconds 45", text)
            self.assertIn("--subtune-probe-timeout 60", text)
            self.assertIn("--subtune-probe-min-notes 20", text)
            self.assertIn("--subtune-zero-streak-limit 4", text)

if __name__ == "__main__":
    unittest.main()
