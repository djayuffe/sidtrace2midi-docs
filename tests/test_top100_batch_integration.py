from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SID = ROOT / 'examples' / 'simple_pulse.sid'

class Top100BatchIntegrationTests(unittest.TestCase):
    def make_hvsc(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name) / 'C64Music'
        for rel in [
            'MUSICIANS/H/Hubbard_Rob/Commando.sid',
            'DEMOS/U/Uncensored.sid',
            'DEMOS/E/Edge_of_Disgrace.sid',
            'DEMOS/T/Triad_Intro.sid',
            'MUSICIANS/K/Kleeder/Demo_Tune.sid',
        ]:
            p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(SID.read_bytes())
        return td, root

    def run_py(self, *args):
        return subprocess.run([sys.executable, *map(str,args)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    def test_classic_top100_dry_run_manifest(self):
        td, hvsc = self.make_hvsc(); self.addCleanup(td.cleanup)
        out = Path(td.name) / 'out_classic'
        p = self.run_py('convert_top100_hvsc.py','--hvsc',hvsc,'--out',out,'--top','1','--dry-run','--keep-going')
        self.assertEqual(p.returncode,0,p.stdout)
        rows=json.loads((out/'top100_manifest.json').read_text())
        self.assertEqual(rows[0]['title'],'Commando')
        self.assertIn('--ppq 9600', rows[0]['command'])

    def test_demos_top100_dry_run_avoids_generic_demo_tune_collapse(self):
        td, hvsc = self.make_hvsc(); self.addCleanup(td.cleanup)
        out = Path(td.name) / 'out_demo'
        p = self.run_py('convert_top100_demos_hvsc.py','--hvsc',hvsc,'--out',out,'--top','2','--dry-run','--keep-going')
        self.assertEqual(p.returncode,0,p.stdout)
        rows=json.loads((out/'top100_demos_manifest.json').read_text())
        sids=[Path(r['sid']).name for r in rows if r.get('sid')]
        self.assertIn('Uncensored.sid',sids)
        self.assertIn('Edge_of_Disgrace.sid',sids)
        self.assertNotIn('Demo_Tune.sid',sids)

    def test_cracktros_top100_dry_run_and_validator_default(self):
        td, hvsc = self.make_hvsc(); self.addCleanup(td.cleanup)
        out = Path(td.name) / 'out_crack'
        p = self.run_py('convert_top100_cracktros_hvsc.py','--hvsc',hvsc,'--out',out,'--top','1','--dry-run','--keep-going')
        self.assertEqual(p.returncode,0,p.stdout)
        self.assertTrue((out/'top100_cracktros_manifest.json').exists())
        rows=json.loads((out/'top100_cracktros_manifest.json').read_text())
        self.assertEqual(Path(rows[0]['sid']).name, 'Triad_Intro.sid')

    def test_all_top100_scripts_compile(self):
        files = ['convert_top25_hvsc.py','convert_top100_hvsc.py','convert_top100_demos_hvsc.py','convert_top100_cracktros_hvsc.py','validate_top100_manifest.py','validate_top100_demos_manifest.py','validate_top100_cracktros_manifest.py']
        p = subprocess.run([sys.executable,'-m','py_compile',*files], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(p.returncode,0,p.stdout)

if __name__ == '__main__':
    unittest.main()
