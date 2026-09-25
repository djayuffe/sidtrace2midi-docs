# Module group: tests

The `tests/` directory contains focused regression tests created during the closure passes.

## CPU tests

These protect:

- opcode coverage;
- official vs illegal opcode classification;
- trace accounting;
- 6510 port behavior;
- strict JAM/unstable handling;
- IRQ/NMI/BRK stop reasons;
- decimal policy behavior.

Representative files:

- `test_cpu6502_nmos_upgrade.py`
- `test_cpu6502_final_correctness_closure.py`
- `test_cpu6502_perfect_last_issue_closure.py`

## SID2MIDI core tests

These protect:

- PSID/RSID feature integration;
- ROM status/reporting;
- SidFrame normalization;
- frame/fcyc validation;
- MIDI event ordering;
- register JSON export;
- CIA timing helpers.

Representative files:

- `test_sid2midi_feature_integration.py`
- `test_sid2midi_audit_findings_closure.py`
- `test_sid2midi_logic_order_final_closure.py`

## Top-100 batch tests

These protect:

- wrapper defaults;
- retry profiles;
- full-length defaults;
- weak MIDI deletion policy;
- fast subtune probing;
- subtune guard limits;
- salvage opt-in behavior;
- manifest analyzer and schema validation.

Representative files:

- `test_top100_batch_integration.py`
- `test_top100_fast_subtune_probe_closure.py`
- `test_top100_salvage_optin_and_manifest_analyzer.py`
- `test_perfect_continuation_closure.py`

## Full test runner

```bash
./run_full_tests.sh
```

This runs the package’s broader regression set through `tools/run_test_files.py`.
