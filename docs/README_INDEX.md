# Documentation Index

This index is the starting point for the expanded SIDTrace2MIDI documentation set.

## Start here

- [Main README](../README.md) — overview, install, validation and common commands.
- [Quickstart](../QUICKSTART.md) — shortest path from unzip to MIDI.
- [Command cookbook](examples/COMMAND_COOKBOOK.md) — copy/paste commands for common tasks.

## Module documentation

- [CPU6502 module](modules/cpu6502.md)
- [sid2midi.py module](modules/sid2midi.md)
- [Top-100 batch module](modules/top100_batch.md)
- [Validators module](modules/validators.md)
- [Tools module](modules/tools.md)
- [Tests module](modules/tests.md)
- [ROMs module](modules/roms.md)

## Step-by-step pipeline docs

- [00 End-to-end pipeline](steps/00_end_to_end_pipeline.md)
- [01 Validation and release checks](steps/01_validation_and_release_checks.md)
- [02 Single SID conversion](steps/02_single_sid_conversion.md)
- [03 Top-100 batch conversion](steps/03_top100_batch_conversion.md)
- [04 Manifest triage and reruns](steps/04_manifest_triage_and_reruns.md)
- [05 Debugging register export](steps/05_debugging_register_export.md)
- [06 Accuracy boundaries](steps/06_accuracy_boundaries.md)

## Reference

- [CLI reference](reference/CLI_REFERENCE.md)
- [Manifest schema](reference/MANIFEST_SCHEMA.md)
- [MIDI mapping](reference/MIDI_MAPPING.md)
- [CPU6502 API](reference/CPU6502_API.md)

## Deep dives

- [Architecture](deepdives/ARCHITECTURE.md)
- [Timing and CIA](deepdives/TIMING_AND_CIA.md)
- [SidFrame model](deepdives/FRAME_MODEL.md)
- [Loop detection](deepdives/LOOP_DETECTION.md)
- [ROM and banking](deepdives/ROM_AND_BANKING.md)

## Tutorials and operations

- [Single SID playbook](tutorials/SINGLE_SID_PLAYBOOK.md)
- [Top-100 demo playbook](tutorials/TOP100_DEMO_PLAYBOOK.md)
- [Troubleshooting](operations/TROUBLESHOOTING.md)
- [Release process](operations/RELEASE_PROCESS.md)
- [QA checklist](operations/QA_CHECKLIST.md)

## Audit trail

The `docs/audits/` directory contains closure notes for each implementation and release pass.


## Naming / branding

```text
docs/branding/PROJECT_NAME.md
docs/reference/NAMING_AND_COMPATIBILITY.md
docs/reference/RELEASE_NAMING.md
```

## Additional deep-dives and playbooks

```text
docs/deepdives/SID_REGISTER_TRACE_MODEL.md
docs/deepdives/CPU_TO_MIDI_MAPPING_FLOW.md
docs/tutorials/DAW_IMPORT_GUIDE.md
docs/tutorials/BATCH_RERUN_PLAYBOOK.md
docs/operations/HVSC_SETUP.md
docs/operations/DOCUMENTATION_STYLE_GUIDE.md
```

## ASCII logo, architecture, how-to and onboarding additions

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
```

Read `docs/tutorials/FIRST_30_MINUTES.md` for a fast practical onboarding path. Read `docs/architecture/COMPLETE_SYSTEM_MAP.md` for the full system map.


## Final completion documents

```text
docs/release/FINAL_RELEASE_SUMMARY.md          release identity, scope and recommended commands
docs/architecture/DATA_FLOW_DETAILED.md        detailed SID -> runtime -> frame -> MIDI flow
docs/reference/OUTPUT_FILES.md                 every generated file and manifest output
docs/reference/ERROR_REASON_MATRIX.md          failure reasons and next actions
docs/howto/CONTINUE_FAILED_TOP100_RUN.md       continue, repair and rerun failed Top-100 rows
docs/deepdives/REGISTER_TO_MIDI_DECISIONS.md   why each SID register becomes notes/CC/metadata
docs/operations/PERFORMANCE_TUNING.md          speed, timeout and subtune-scan tuning
docs/operations/FINAL_QA_MATRIX.md             final release checklist
```
