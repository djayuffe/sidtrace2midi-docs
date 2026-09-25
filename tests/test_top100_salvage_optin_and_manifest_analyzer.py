import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Top100SalvageOptInAndAnalyzerTests(unittest.TestCase):
    def test_batch_help_exposes_guard_options(self):
        p = subprocess.run([sys.executable, str(ROOT/'convert_top25_hvsc.py'), '--help'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn('--salvage-retry', p.stdout)
        self.assertIn('--max-full-subtune-renders', p.stdout)
        self.assertIn('--subtune-scan-time-budget', p.stdout)

    def test_default_wrappers_do_not_enable_salvage_retry(self):
        for name in ['convert_top100_exact.sh','convert_top100_demos_exact.sh','convert_top100_cracktros_exact.sh']:
            text = (ROOT/name).read_text()
            self.assertIn('--max-full-subtune-renders 4', text)
            self.assertNotIn('--salvage-retry', text)

    def test_manifest_analyzer_reports_failed_and_emits_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            mf = Path(td)/'top100_demos_manifest.json'
            rows = [
                {'rank': 1, 'title': 'Good', 'status': 'ok', 'reason': '', 'notes': 1000, 'profile': 'default'},
                {'rank': 63, 'title': 'Party Songs', 'status': 'failed', 'reason': 'subtune-bad-streak-6', 'notes': 0, 'actual_song': 1, 'probe_attempts': 6, 'full_render_count': 0, 'profile': 'large-init-large-call'},
            ]
            mf.write_text(json.dumps(rows), encoding='utf-8')
            p = subprocess.run([sys.executable, str(ROOT/'tools/analyze_top100_manifest.py'), str(mf), '--emit-rerun', '--show', '5'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(p.returncode, 1, p.stdout)
            self.assertIn('failed rows:', p.stdout)
            self.assertIn('Party Songs', p.stdout)
            self.assertIn('--start-at 63 --stop-after 1', p.stdout)

if __name__ == '__main__':
    unittest.main()
