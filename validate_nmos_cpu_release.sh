#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "== SID2MIDI NMOS CPU release validation =="
python3 - <<'PYCODECHECK'
from pathlib import Path
files = [
    'cpu6502.py', 'sid2midi.py', 'convert_top25_hvsc.py', 'convert_top100_hvsc.py',
    'convert_top100_demos_hvsc.py', 'convert_top100_cracktros_hvsc.py',
    'validate_top100_manifest.py', 'validate_top100_demos_manifest.py',
    'validate_top100_cracktros_manifest.py', 'tools/cpu_opcode_coverage_report.py',
    'tools/analyze_top100_manifest.py', 'tools/verify_sha256.py',
]
for fn in files:
    src = Path(fn).read_text(encoding='utf-8')
    compile(src, fn, 'exec')
print('Python syntax check OK')
PYCODECHECK

echo "== Opcode coverage =="
python3 tools/cpu_opcode_coverage_report.py

echo "== SID smoke conversion =="
python3 sid2midi.py examples/simple_pulse.sid \
  --seconds 1 \
  --report \
  -o /tmp/simple_cpu_final100.mid \
  >/tmp/simple_cpu_final100.log
cat /tmp/simple_cpu_final100.log
test -s /tmp/simple_cpu_final100.mid || { echo 'smoke MIDI missing/empty' >&2; exit 1; }
echo "NMOS CPU perfect release validation OK"
