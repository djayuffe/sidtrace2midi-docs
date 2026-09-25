import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding='utf-8')


class Top100LongDefaultClosureTests(unittest.TestCase):
    def test_top100_shell_wrappers_use_long_defaults(self):
        for name in ["convert_top100_exact.sh", "convert_top100_demos_exact.sh", "convert_top100_cracktros_exact.sh"]:
            s = text(name)
            self.assertIn("--seconds 600", s)
            self.assertIn("--auto-min-seconds 540", s)
            self.assertIn("--timeout 300", s)
            self.assertIn("--keep-going", s)

    def test_python_wrappers_default_to_long_policy(self):
        self.assertIn("('--seconds','600')", text("convert_top100_hvsc.py"))
        self.assertIn("['--auto-min-seconds','540']", text("convert_top100_hvsc.py"))
        self.assertIn("('--seconds','600')", text("convert_top100_demos_hvsc.py"))
        self.assertIn("['--auto-min-seconds','540']", text("convert_top100_demos_hvsc.py"))
        self.assertIn('args.extend(["--seconds", "600"])', text("convert_top100_cracktros_hvsc.py"))
        self.assertIn('args.extend(["--auto-min-seconds", "540"])', text("convert_top100_cracktros_hvsc.py"))

    def test_batch_engine_defaults_and_weak_midi_policy_present(self):
        s = text("convert_top25_hvsc.py")
        self.assertIn('default=600.0', s)
        self.assertIn('default=300.0', s)
        self.assertIn('--allow-weak-midi', s)
        self.assertIn('outmid.unlink()', s)

    def test_sid2midi_direct_default_is_300_seconds(self):
        help_text = subprocess.check_output([sys.executable, str(ROOT / "sid2midi.py"), "--help"], text=True)
        self.assertIn("--seconds SECONDS", help_text)
        self.assertIn('default=300.0', text("sid2midi.py"))


if __name__ == '__main__':
    unittest.main()
