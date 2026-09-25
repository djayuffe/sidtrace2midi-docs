# Module group: tools

The `tools/` directory contains helper utilities for validation, triage and release checks.

## `tools/cpu_opcode_coverage_report.py`

Reports CPU opcode implementation coverage:

- handler coverage;
- official opcode coverage;
- JAM opcode list;
- unstable opcode list;
- page-cross penalty list;
- diagnostic feature summary.

## `tools/verify_sha256.py`

Portable SHA256 manifest verifier.

Usage:

```bash
python3 tools/verify_sha256.py
```

## `tools/analyze_top100_manifest.py`

Reads a Top-100 manifest and summarizes failed/weak rows. It can emit targeted rerun commands.

Usage:

```bash
python3 tools/analyze_top100_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --emit-rerun
```

## `tools/run_test_files.py`

Runs regression test files in isolated subprocesses. This makes failures easier to attribute and avoids cross-test global state leaks.
