import json, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Top100SubtuneGuardFinalClosureTests(unittest.TestCase):
    def test_failed_probes_stop_on_bad_streak_and_manifest_reason(self):
        import convert_top25_hvsc as core
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / 'hvsc'; hvsc.mkdir()
            sid = hvsc / 'Many.sid'
            data = bytearray(b'PSID' + b'\0' * 0x7c)
            data[0x0E:0x10] = (20).to_bytes(2, 'big')
            sid.write_bytes(data)
            out = td / 'out'
            old_top, old_run = core.TOP25, core.run_command
            calls = []
            def fake_run(cmd, timeout):
                calls.append((list(map(str, cmd)), timeout))
                # Main selected subtune: rc failure. Alternate probes: rc failure, no note count.
                return 1, 'RuntimeError: SID init exceeded instruction budget\n', 0.01
            core.TOP25 = (core.TopTune(1, 'Many', 'test', 125, 1, ('Many.sid',)),)
            core.run_command = fake_run
            try:
                rc = core.main([
                    '--hvsc', str(hvsc), '--out', str(out), '--limit', '1', '--keep-going', '--debug',
                    '--min-notes', '100', '--song-scan-limit', '20', '--subtune-bad-streak-limit', '3',
                    '--subtune-zero-streak-limit', '99', '--manifest-prefix', 'badstreak',
                ])
            finally:
                core.TOP25, core.run_command = old_top, old_run
            self.assertEqual(rc, 0)
            # 4 selected-song attempts + 3 bad probes, then stop.
            self.assertLessEqual(len(calls), 7)
            rows = json.loads((out / 'badstreak_manifest.json').read_text())
            self.assertEqual(rows[0]['status'], 'failed')
            self.assertEqual(rows[0]['reason'], 'subtune-bad-streak-3')
            self.assertEqual(rows[0]['probe_attempts'], 3)

    def test_probe_time_budget_stops_scan(self):
        import convert_top25_hvsc as core
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / 'hvsc'; hvsc.mkdir()
            sid = hvsc / 'Budget.sid'
            data = bytearray(b'PSID' + b'\0' * 0x7c)
            data[0x0E:0x10] = (10).to_bytes(2, 'big')
            sid.write_bytes(data)
            out = td / 'out'
            old_top, old_run = core.TOP25, core.run_command
            def fake_run(cmd, timeout):
                return 1, 'TIMEOUT after probe\n', 2.0
            core.TOP25 = (core.TopTune(1, 'Budget', 'test', 125, 1, ('Budget.sid',)),)
            core.run_command = fake_run
            try:
                core.main([
                    '--hvsc', str(hvsc), '--out', str(out), '--limit', '1', '--keep-going',
                    '--song-scan-limit', '10', '--subtune-bad-streak-limit', '99',
                    '--subtune-scan-time-budget', '3', '--manifest-prefix', 'budget',
                ])
            finally:
                core.TOP25, core.run_command = old_top, old_run
            rows = json.loads((out / 'budget_manifest.json').read_text())
            self.assertEqual(rows[0]['status'], 'failed')
            self.assertTrue(rows[0]['reason'].startswith('subtune-probe-budget-'))
            self.assertLessEqual(rows[0]['probe_attempts'], 2)

    def test_wrappers_and_manifest_include_guard_fields(self):
        core = (ROOT / 'convert_top25_hvsc.py').read_text()
        self.assertIn('--subtune-bad-streak-limit', core)
        self.assertIn('--subtune-scan-time-budget', core)
        self.assertIn('subtune_attempts', core)
        self.assertIn('probe_attempts', core)
        self.assertIn('reason', core)
        for name in ('convert_top100_exact.sh', 'convert_top100_demos_exact.sh', 'convert_top100_cracktros_exact.sh'):
            text = (ROOT / name).read_text()
            self.assertIn('--subtune-bad-streak-limit 6', text)
            self.assertIn('--subtune-scan-time-budget 240', text)

if __name__ == '__main__':
    unittest.main()
