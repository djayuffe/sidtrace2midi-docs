import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PerfectContinuationClosureTests(unittest.TestCase):
    def run_py(self, *args):
        return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    def test_convert_top25_top_argument_overrides_default_limit_when_direct(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / "hvsc"; hvsc.mkdir()
            out = td / "out"
            p = self.run_py(ROOT / "convert_top25_hvsc.py", "--hvsc", hvsc, "--out", out,
                            "--top", "3", "--list", "--manifest-prefix", "direct_top")
            self.assertEqual(p.returncode, 0, p.stdout)
            manifest = json.loads((out / "direct_top_manifest.json").read_text())
            self.assertEqual(len(manifest), 3)
            self.assertEqual([r["rank"] for r in manifest], [1, 2, 3])

    def test_convert_top25_explicit_limit_still_caps_top(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            hvsc = td / "hvsc"; hvsc.mkdir()
            out = td / "out"
            p = self.run_py(ROOT / "convert_top25_hvsc.py", "--hvsc", hvsc, "--out", out,
                            "--top", "10", "--limit", "4", "--list", "--manifest-prefix", "limit_top")
            self.assertEqual(p.returncode, 0, p.stdout)
            manifest = json.loads((out / "limit_top_manifest.json").read_text())
            self.assertEqual(len(manifest), 4)

    def test_validate_top100_manifest_reports_schema_errors(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps([{"rank": 1, "title": "Bad", "status": "ok", "notes": 10}]), encoding="utf-8")
            p = self.run_py(ROOT / "validate_top100_manifest.py", path, "--expect-rows", "0")
            self.assertNotEqual(p.returncode, 0, p.stdout)
            self.assertIn("SCHEMA_BAD", p.stdout)

    def test_no_delete_weak_midi_flag_is_exposed(self):
        p = self.run_py(ROOT / "convert_top25_hvsc.py", "--help")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("--no-delete-weak-midi", p.stdout)

if __name__ == "__main__":
    unittest.main()
