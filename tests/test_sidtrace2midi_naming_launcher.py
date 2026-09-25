import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SidTrace2MidiNamingLauncherTests(unittest.TestCase):
    def test_sidtrace2midi_launcher_help_exposes_converter_flags(self):
        out = subprocess.check_output([sys.executable, str(ROOT / 'sidtrace2midi.py'), '--help'], text=True, timeout=20)
        self.assertIn('--auto-min-seconds', out)
        self.assertIn('--export-register-json', out)

    def test_branding_docs_exist_and_describe_direction(self):
        txt = (ROOT / 'docs' / 'branding' / 'PROJECT_NAME.md').read_text(encoding='utf-8')
        self.assertIn('SIDTrace2MIDI', txt)
        self.assertIn('does **not** convert', txt)
        self.assertIn('SID register trace', txt)

if __name__ == '__main__':
    unittest.main()
