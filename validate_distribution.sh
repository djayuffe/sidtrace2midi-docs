#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
# validate_release.sh performs the full CPU/test/smoke pass.  This distribution
# script stays lightweight and package-focused so it is safe to run repeatedly.
python3 tools/verify_sha256.py
python3 - <<'PY'
import subprocess, sys
help_text = subprocess.check_output([sys.executable, 'sid2midi.py', '--help'], text=True, timeout=15)
alias_help = subprocess.check_output([sys.executable, 'sidtrace2midi.py', '--help'], text=True, timeout=15)
if '--auto-min-seconds' not in alias_help:
    raise SystemExit('sidtrace2midi.py launcher help missing expected flags')
required = [
    '--ppq', '--auto-min-seconds', '--auto-confirm-windows', '--auto-bpm',
    '--frames-per-row', '--rows-per-beat', '--max-ins-init', '--max-ins-call',
    '--max-stuck-frames', '--strict-init', '--salvage-init', '--respect-irq-disable', '--require-roms', '--cia-advance-mode', '--export-register-json'
]
missing = [x for x in required if x not in help_text]
if missing:
    raise SystemExit('missing CLI flags: ' + ', '.join(missing))
print('CLI feature flags OK')
PY
python3 - <<'PY'
from pathlib import Path
required = [
    'convert_top100_exact.sh', 'convert_top100_demos_exact.sh', 'convert_top100_cracktros_exact.sh',
    'convert_top100_hvsc.py', 'convert_top100_demos_hvsc.py', 'convert_top100_cracktros_hvsc.py',
    'validate_top100_manifest.py', 'validate_top100_demos_manifest.py', 'validate_top100_cracktros_manifest.py',
    'tests/test_top100_retry_and_release_cleanup.py',
    'tests/test_top100_long_default_closure.py',
    'tests/test_top100_fast_subtune_probe_closure.py',
    'tests/test_top100_subtune_guard_final_closure.py',
    'tests/test_top100_salvage_optin_and_manifest_analyzer.py',
    'tools/analyze_top100_manifest.py',
    'sidtrace2midi.py',
]
missing=[p for p in required if not Path(p).exists()]
if missing:
    raise SystemExit('missing distribution files: ' + ', '.join(missing))
for script in ('convert_top100_exact.sh','convert_top100_demos_exact.sh','convert_top100_cracktros_exact.sh'):
    txt = Path(script).read_text(encoding='utf-8')
    for flag in ('--keep-going','--skip-existing','--auto-min-seconds'):
        if flag not in txt:
            raise SystemExit(f'{script} missing {flag}')
    for required_arg in ('--seconds 600', '--timeout 300', '--auto-min-seconds 540', '--subtune-probe-seconds 45', '--subtune-probe-timeout 60', '--subtune-bad-streak-limit 6', '--subtune-scan-time-budget 240', '--max-full-subtune-renders 4'):
        if required_arg not in txt:
            raise SystemExit(f'{script} missing long default {required_arg}')
print('Top-100 batch scripts OK')
PY
python3 tools/cpu_opcode_coverage_report.py >/tmp/sid2midi_distribution_coverage.txt
grep -q 'handlers: 256/256' /tmp/sid2midi_distribution_coverage.txt
grep -q 'official opcodes covered: 151/151' /tmp/sid2midi_distribution_coverage.txt
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
find . \( -name '__pycache__' -o -name '*.pyc' \) | tee /tmp/sid2midi_distribution_cache_files.txt
if [ -s /tmp/sid2midi_distribution_cache_files.txt ]; then
  echo 'unexpected cache files in release tree' >&2
  exit 1
fi
echo 'SID2MIDI distribution validation OK'
