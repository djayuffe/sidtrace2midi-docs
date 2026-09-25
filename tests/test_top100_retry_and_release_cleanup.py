from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SID = ROOT / 'examples' / 'simple_pulse.sid'

class Top100RetryAndCleanupTests(unittest.TestCase):
    def run_py(self, *args, timeout=30):
        return subprocess.run([sys.executable, *map(str,args)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)

    def make_hvsc(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name) / 'C64Music'
        p = root / 'MUSICIANS/H/Hubbard_Rob/Commando.sid'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(SID.read_bytes())
        return td, root

    def test_batch_retries_with_salvage_init_after_init_budget_failure(self):
        td, hvsc = self.make_hvsc(); self.addCleanup(td.cleanup)
        fake = Path(td.name) / 'fake_sid2midi.py'
        fake.write_text(textwrap.dedent('''
            import sys
            out = sys.argv[sys.argv.index('-o') + 1]
            if '--salvage-init' not in sys.argv:
                print('RuntimeError: SID init exceeded instruction budget (8000000)')
                raise SystemExit(1)
            open(out, 'wb').write(b'MThd\\x00\\x00\\x00\\x06\\x00\\x01\\x00\\x01\\x01\\xe0MTrk\\x00\\x00\\x00\\x0c\\x00\\x90<d`\\x80<\\x00\\x00\\xff/\\x00')
            print(f"{out} : 6 tracks, 123 notes, 41 CC, PPQ 9600, 100.0s @ grid 125 BPM")
        '''), encoding='utf-8')
        out = Path(td.name) / 'out'
        p = self.run_py('convert_top25_hvsc.py','--hvsc',hvsc,'--out',out,'--sid2midi',fake,'--limit','1','--manifest-prefix','retry_test','--keep-going','--debug','--min-notes','100','--salvage-retry')
        self.assertEqual(p.returncode, 0, p.stdout)
        rows = json.loads((out/'retry_test_manifest.json').read_text())
        self.assertEqual(rows[0]['status'], 'ok')
        self.assertEqual(rows[0]['profile'], 'salvage-init')
        self.assertIn('--salvage-init', rows[0]['command'])

    def test_skip_existing_counts_notes_instead_of_zero(self):
        td, hvsc = self.make_hvsc(); self.addCleanup(td.cleanup)
        out = Path(td.name) / 'out'; out.mkdir()
        existing = out / '01_Commando.mid'
        # Minimal MIDI with one note-on.  count_midi_note_on should return 1.
        existing.write_bytes(b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0MTrk\x00\x00\x00\x0c\x00\x90<d`\x80<\x00\x00\xff/\x00')
        p = self.run_py('convert_top25_hvsc.py','--hvsc',hvsc,'--out',out,'--limit','1','--manifest-prefix','skip_test','--skip-existing','--keep-going','--min-notes','1')
        self.assertEqual(p.returncode, 0, p.stdout)
        rows = json.loads((out/'skip_test_manifest.json').read_text())
        self.assertEqual(rows[0]['status'], 'ok')
        self.assertEqual(rows[0]['notes'], 1)

    def test_exact_wrappers_keep_going(self):
        for name in ('convert_top100_exact.sh','convert_top100_demos_exact.sh','convert_top100_cracktros_exact.sh'):
            txt = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn('--keep-going', txt)

if __name__ == '__main__':
    unittest.main()
