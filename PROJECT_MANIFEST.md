# Project Manifest — Complete README Final Release

## Root files

```text
README.md                         complete user/developer manual
QUICKSTART.md                     minimal command cheat sheet
PROJECT_MANIFEST.md               this file
RELEASE_NOTES_NMOS_CPU.md         release notes and closure history
FINAL_CLOSURE_REPORT.md           CPU closure report
REQUIREMENTS.md                   runtime requirements
SHA256SUMS.txt                    package file integrity manifest
cpu6502.py                        hardened NMOS 6502/6510 CPU core
sid2midi.py                       PSID/RSID to MIDI converter
run_example.sh                    smoke SID conversion helper
validate_release.sh               full release validation
validate_distribution.sh          distribution validation
validate_nmos_cpu_release.sh      CPU-focused validation
```

## Top-100 batch files

```text
convert_top25_hvsc.py
convert_top100_hvsc.py
convert_top100_exact.sh
convert_top100_demos_hvsc.py
convert_top100_demos_hvsc.sh
convert_top100_demos_exact.sh
convert_top100_cracktros_hvsc.py
convert_top100_cracktros_hvsc.sh
convert_top100_cracktros_exact.sh
validate_top100_manifest.py
validate_top100_demos_manifest.py
validate_top100_cracktros_manifest.py
TOP100_AUTO_README.md
TOP100_DEMOS_README.md
TOP100_CRACKTROS_README.md
```

## Directories

```text
examples/                         bundled simple SID smoke file
roms/                             BASIC/CHARGEN/KERNAL ROMs
tests/                            CPU, SID2MIDI and batch regression tests
tools/                            SHA and opcode coverage helpers
docs/audits/                      audit trail for every closure pass, including CPU6502_FINAL_CORRECTNESS_CLOSURE_AUDIT.md
docs/release/                     reserved release notes area
```

## Validation expectation

The complete final release should pass:

```bash
./validate_distribution.sh
./validate_release.sh
python3 tools/verify_sha256.py
```

Expected core status:

```text
78 tests OK
opcode handlers 256/256
official opcodes 151/151
SHA256SUMS OK
zip integrity OK
```
- `tests/test_cpu6502_perfect_last_issue_closure.py` — final CPU trace/OFFICIAL_OPS/6510 mirror closure tests.
- `docs/audits/CPU6502_PERFECT_LAST_ISSUE_CLOSURE_AUDIT.md` — final CPU audit closure notes.

## Logic Order / Frame / Timing Final Closure

- MIDI event order is now explicit and stable: meta, program, CC/bend, note-off, note-on.
- SidFrame is the canonical internal frame model; legacy tuple frames are normalized at API boundaries.
- `convert()` validates frame/timing alignment before MIDI rendering.
- Multi-SID frame access no longer depends on raw magic tuple indices.
- Loop detection now prefers the best-evidenced loop candidate instead of the first early tail match.
- `run_tune()` uses a pre-call elapsed-period contract so timer writes affect the next frame cleanly.
- Added `docs/audits/SID2MIDI_LOGIC_ORDER_FRAME_TIMING_FINAL_AUDIT.md` and regression tests.


## Final packaged files after logic-order closure

```text
FINAL_CLOSURE_REPORT.md
PROJECT_MANIFEST.md
QUICKSTART.md
README.md
RELEASE_NOTES_NMOS_CPU.md
REQUIREMENTS.md
TOP100_AUTO_README.md
TOP100_CRACKTROS_README.md
TOP100_DEMOS_README.md
convert_top100_cracktros_exact.sh
convert_top100_cracktros_hvsc.py
convert_top100_cracktros_hvsc.sh
convert_top100_demos_exact.sh
convert_top100_demos_hvsc.py
convert_top100_demos_hvsc.sh
convert_top100_exact.sh
convert_top100_hvsc.py
convert_top25_hvsc.py
cpu6502.py
docs/audits/CLEAN_RELEASE_README_CLOSURE_AUDIT.md
docs/audits/COMPLETE_FINAL_RELEASE_README_CLEANUP_AUDIT.md
docs/audits/CPU6502_FINAL_CORRECTNESS_CLOSURE_AUDIT.md
docs/audits/CPU6502_PERFECT_LAST_ISSUE_CLOSURE_AUDIT.md
docs/audits/CPU_OPCODE_COVERAGE_REPORT.txt
docs/audits/FINAL_PERFECT_RELEASE_AUDIT.md
docs/audits/NMOS_6502_AUDIT_DRIVEN_IMPROVEMENT.md
docs/audits/NMOS_6502_CPU_100_PERCENT_CLOSURE_AUDIT.md
docs/audits/NMOS_6502_CPU_FINAL_CLOSURE_AUDIT.md
docs/audits/NMOS_6502_CPU_UPGRADE_AUDIT.md
docs/audits/NMOS_6502_FINAL_PERFECT_AUDIT.md
docs/audits/NMOS_6502_FURTHER_IMPROVEMENT_AUDIT.md
docs/audits/SID2MIDI_AUDIT_FINDINGS_FULL_IMPLEMENTATION.md
docs/audits/SID2MIDI_DISTRIBUTION_FINAL_CLOSURE_AUDIT.md
docs/audits/SID2MIDI_FEATURE_INTEGRATION_AUDIT.md
docs/audits/SID2MIDI_FINAL_FEATURE_CLOSURE_AUDIT.md
docs/audits/SID2MIDI_LOGIC_ORDER_FRAME_TIMING_FINAL_AUDIT.md
docs/audits/TOP100_BATCH_INTEGRATION_CLEAN_RELEASE_AUDIT.md
docs/audits/TOP100_RETRY_AND_BATCH_FINAL_CLOSURE_AUDIT.md
examples/simple_pulse.sid
roms/basic.bin
roms/chargen.bin
roms/kernal.bin
run_example.sh
sid2midi.py
tests/test_cpu6502_audit_improvements.py
tests/test_cpu6502_final_100_closure.py
tests/test_cpu6502_final_correctness_closure.py
tests/test_cpu6502_final_perfect.py
tests/test_cpu6502_further_improvements.py
tests/test_cpu6502_nmos_upgrade.py
tests/test_cpu6502_perfect_last_issue_closure.py
tests/test_sid2midi_audit_findings_closure.py
tests/test_sid2midi_feature_integration.py
tests/test_sid2midi_final_feature_closure.py
tests/test_sid2midi_logic_order_final_closure.py
tests/test_top100_batch_integration.py
tests/test_top100_retry_and_release_cleanup.py
tools/cpu_opcode_coverage_report.py
tools/verify_sha256.py
validate_distribution.sh
validate_nmos_cpu_release.sh
validate_release.sh
validate_top100_cracktros_manifest.py
validate_top100_demos_manifest.py
validate_top100_manifest.py
```


## README / Distribution Final Closure

- `README.md` and `QUICKSTART.md` were expanded/updated for the current package name and validation flow.
- `docs/audits/README_DISTRIBUTION_FINAL_RELEASE_AUDIT.md` records the cleanup pass.
- Expected validation baseline is 78 tests OK plus opcode coverage 256/256 and official opcodes 151/151.

- `tests/test_top100_long_default_closure.py`

- `docs/audits/TOP100_LONG_DEFAULT_SONG_CLOSURE_AUDIT.md`

- `tests/test_top100_weak_salvage_and_full_length_closure.py` — verifies 600s/540s/3-window full-length Top-100 defaults, weak skip-existing cleanup, and PSID subtune count parsing.
- `convert_top25_hvsc.py` — shared batch engine now rejects weak salvage outputs, deletes weak existing MIDI files before `--skip-existing`, and scans alternate subtunes when the selected song fails or renders below `--min-notes`.

## Added in fast subtune probe release

- `tests/test_top100_fast_subtune_probe_closure.py`
- `docs/audits/TOP100_FAST_SUBTUNE_PROBE_FINAL_AUDIT.md`
- `convert_top25_hvsc.py` probe options:
  - `--subtune-probe-seconds`
  - `--subtune-probe-timeout`
  - `--subtune-probe-min-notes`
  - `--subtune-zero-streak-limit`
  - `--exhaustive-subtune-scan`

## Final subtune guard closure

- `tests/test_top100_subtune_guard_final_closure.py`
- `docs/audits/TOP100_SUBTUNE_GUARD_PERFECTION_AUDIT.md`
- Batch manifest fields: `reason`, `subtune_attempts`, `probe_attempts`
- Wrapper defaults: `--subtune-bad-streak-limit 6`, `--subtune-scan-time-budget 240`

## Final batch guard additions

- `tools/analyze_top100_manifest.py` — offline manifest summary and targeted rerun command generator.
- `tests/test_top100_salvage_optin_and_manifest_analyzer.py` — verifies salvage opt-in, wrapper defaults and manifest analyzer output.
- `docs/audits/TOP100_SALVAGE_OPTIN_MANIFEST_ANALYZER_AUDIT.md` — audit note for the final batch policy closure.

- `tests/test_final_cleanup_perfection.py` — verifies final trace semantics, official-opcode diagnostics, 6510 mirror-read errors, strict frame helper failures, register JSON export helpers and CIA timing-mode API.


### Perfect continuation cleanup

- `tools/run_test_files.py` — isolated per-file regression runner.
- `tests/test_perfect_continuation_closure.py` — regression coverage for direct `--top`, explicit `--limit`, manifest schema validation and weak-MIDI preservation flag exposure.
- `docs/audits/PERFECT_CONTINUATION_CLEANUP_AUDIT.md` — final continuation audit note.


## Expanded documentation tree

```text
docs/README_INDEX.md
docs/modules/cpu6502.md
docs/modules/sid2midi.md
docs/modules/top100_batch.md
docs/modules/validators.md
docs/modules/tools.md
docs/modules/tests.md
docs/modules/roms.md
docs/steps/00_end_to_end_pipeline.md
docs/steps/01_validation_and_release_checks.md
docs/steps/02_single_sid_conversion.md
docs/steps/03_top100_batch_conversion.md
docs/steps/04_manifest_triage_and_reruns.md
docs/steps/05_debugging_register_export.md
docs/steps/06_accuracy_boundaries.md
docs/audits/DOCUMENTATION_EXPANSION_MODULE_STEP_AUDIT.md
```

## Documentation plus additions

- `docs/deepdives/ARCHITECTURE.md`
- `docs/deepdives/FRAME_MODEL.md`
- `docs/deepdives/LOOP_DETECTION.md`
- `docs/deepdives/ROM_AND_BANKING.md`
- `docs/deepdives/TIMING_AND_CIA.md`
- `docs/examples/COMMAND_COOKBOOK.md`
- `docs/operations/QA_CHECKLIST.md`
- `docs/operations/RELEASE_PROCESS.md`
- `docs/operations/TROUBLESHOOTING.md`
- `docs/reference/CLI_REFERENCE.md`
- `docs/reference/CPU6502_API.md`
- `docs/reference/MANIFEST_SCHEMA.md`
- `docs/reference/MIDI_MAPPING.md`
- `docs/tutorials/SINGLE_SID_PLAYBOOK.md`
- `docs/tutorials/TOP100_DEMO_PLAYBOOK.md`


## SIDTrace2MIDI documentation ultra release additions

```text
sidtrace2midi.py                                   friendly public launcher
docs/branding/PROJECT_NAME.md                      project name rationale
docs/reference/NAMING_AND_COMPATIBILITY.md         compatibility notes
docs/reference/RELEASE_NAMING.md                   archive/directory naming guide
docs/deepdives/SID_REGISTER_TRACE_MODEL.md         register-trace model
docs/deepdives/CPU_TO_MIDI_MAPPING_FLOW.md         CPU/C64/SidFrame/MIDI flow
docs/tutorials/DAW_IMPORT_GUIDE.md                 DAW import workflow
docs/tutorials/BATCH_RERUN_PLAYBOOK.md             manifest triage and reruns
docs/operations/HVSC_SETUP.md                      local HVSC setup guide
docs/operations/DOCUMENTATION_STYLE_GUIDE.md       documentation rules
docs/audits/NAMING_DOCUMENTATION_EXPANSION_AUDIT.md
```

## ASCII logo and expanded documentation files

```text
LOGO_ASCII.txt
docs/branding/ASCII_ART_LOGO.md
docs/architecture/COMPLETE_SYSTEM_MAP.md
docs/howto/MAKE_A_RELEASE.md
docs/howto/READ_THE_OUTPUT_LOGS.md
docs/reference/FILE_TREE.md
docs/reference/GLOSSARY.md
docs/deepdives/WHY_TRACE_NOT_EMULATE_AUDIO.md
docs/operations/DOCUMENTATION_MAINTENANCE.md
docs/tutorials/FIRST_30_MINUTES.md
docs/audits/ASCII_LOGO_DOCUMENTATION_FINAL_AUDIT.md
```


## Final documentation completion files

```text
docs/release/FINAL_RELEASE_SUMMARY.md
docs/architecture/DATA_FLOW_DETAILED.md
docs/reference/OUTPUT_FILES.md
docs/reference/ERROR_REASON_MATRIX.md
docs/howto/CONTINUE_FAILED_TOP100_RUN.md
docs/deepdives/REGISTER_TO_MIDI_DECISIONS.md
docs/operations/PERFORMANCE_TUNING.md
docs/operations/FINAL_QA_MATRIX.md
docs/audits/FINAL_DOCUMENTATION_COMPLETION_AUDIT.md
```
