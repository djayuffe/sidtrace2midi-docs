#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
./validate_nmos_cpu_release.sh
python3 tools/verify_sha256.py
python3 - <<'PY'
from pathlib import Path
required = [
    'cpu6502.py', 'sid2midi.py', 'sidtrace2midi.py', 'README.md', 'QUICKSTART.md',
    'PROJECT_MANIFEST.md', 'RELEASE_NOTES_NMOS_CPU.md', 'FINAL_CLOSURE_REPORT.md',
    'REQUIREMENTS.md', 'SHA256SUMS.txt', 'examples/simple_pulse.sid',
    'roms/basic.bin', 'roms/chargen.bin', 'roms/kernal.bin',
    'tests/test_cpu6502_nmos_upgrade.py', 'tests/test_cpu6502_final_100_closure.py',
    'tests/test_cpu6502_audit_improvements.py', 'tests/test_cpu6502_further_improvements.py',
    'tests/test_cpu6502_final_perfect.py', 'tests/test_sid2midi_feature_integration.py',
    'tests/test_sid2midi_final_feature_closure.py', 'tests/test_top100_retry_and_release_cleanup.py',
    'tests/test_sid2midi_audit_findings_closure.py',
    'tests/test_cpu6502_final_correctness_closure.py',
    'tests/test_cpu6502_perfect_last_issue_closure.py',
    'tests/test_sid2midi_logic_order_final_closure.py',
    'tests/test_top100_long_default_closure.py',
    'tests/test_top100_weak_salvage_and_full_length_closure.py',
    'tests/test_top100_fast_subtune_probe_closure.py',
    'tests/test_top100_subtune_guard_final_closure.py',
    'tests/test_top100_salvage_optin_and_manifest_analyzer.py',
    'tests/test_final_cleanup_perfection.py',
    'tests/test_perfect_continuation_closure.py',
    'tests/test_sidtrace2midi_naming_launcher.py',
    'tools/cpu_opcode_coverage_report.py', 'tools/analyze_top100_manifest.py', 'run_full_tests.sh', 'tools/verify_sha256.py', 'tools/run_test_files.py',
    'convert_top25_hvsc.py', 'convert_top100_hvsc.py', 'convert_top100_exact.sh',
    'convert_top100_demos_hvsc.py', 'convert_top100_demos_exact.sh', 'convert_top100_demos_hvsc.sh',
    'convert_top100_cracktros_hvsc.py', 'convert_top100_cracktros_exact.sh', 'convert_top100_cracktros_hvsc.sh',
    'validate_top100_manifest.py', 'validate_top100_demos_manifest.py', 'validate_top100_cracktros_manifest.py',
    'TOP100_AUTO_README.md', 'TOP100_DEMOS_README.md', 'TOP100_CRACKTROS_README.md',
    'docs/audits/PERFECT_CONTINUATION_CLEANUP_AUDIT.md',

    'docs/branding/PROJECT_NAME.md',
    'docs/reference/NAMING_AND_COMPATIBILITY.md', 'docs/reference/RELEASE_NAMING.md',
    'docs/deepdives/SID_REGISTER_TRACE_MODEL.md', 'docs/deepdives/CPU_TO_MIDI_MAPPING_FLOW.md',
    'docs/tutorials/DAW_IMPORT_GUIDE.md', 'docs/tutorials/BATCH_RERUN_PLAYBOOK.md',
    'docs/operations/HVSC_SETUP.md', 'docs/operations/DOCUMENTATION_STYLE_GUIDE.md',
    'docs/audits/NAMING_DOCUMENTATION_EXPANSION_AUDIT.md',

    'LOGO_ASCII.txt',
    'docs/branding/ASCII_ART_LOGO.md',
    'docs/architecture/COMPLETE_SYSTEM_MAP.md',
    'docs/howto/MAKE_A_RELEASE.md', 'docs/howto/READ_THE_OUTPUT_LOGS.md',
    'docs/reference/FILE_TREE.md', 'docs/reference/GLOSSARY.md',
    'docs/deepdives/WHY_TRACE_NOT_EMULATE_AUDIO.md',
    'docs/operations/DOCUMENTATION_MAINTENANCE.md',
    'docs/tutorials/FIRST_30_MINUTES.md',
    'docs/audits/ASCII_LOGO_DOCUMENTATION_FINAL_AUDIT.md',

]
missing = [p for p in required if not Path(p).exists()]
if missing:
    raise SystemExit('missing required files: ' + ', '.join(missing))
print('Release file layout OK')
PY
# Keep release tree clean after validation.
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
echo "SID2MIDI release validation OK"
