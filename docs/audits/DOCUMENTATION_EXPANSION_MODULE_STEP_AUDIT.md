# Documentation Expansion / Module-Step Audit

This pass expands the package documentation without changing conversion behavior.

## Added

- `docs/README_INDEX.md`
- `docs/modules/cpu6502.md`
- `docs/modules/sid2midi.md`
- `docs/modules/top100_batch.md`
- `docs/modules/validators.md`
- `docs/modules/tools.md`
- `docs/modules/tests.md`
- `docs/modules/roms.md`
- `docs/steps/00_end_to_end_pipeline.md`
- `docs/steps/01_validation_and_release_checks.md`
- `docs/steps/02_single_sid_conversion.md`
- `docs/steps/03_top100_batch_conversion.md`
- `docs/steps/04_manifest_triage_and_reruns.md`
- `docs/steps/05_debugging_register_export.md`
- `docs/steps/06_accuracy_boundaries.md`

## Updated

- `README.md` links to the documentation index and explains the new module/step docs.
- `PROJECT_MANIFEST.md` lists the documentation tree.
- `RELEASE_NOTES_NMOS_CPU.md` records this documentation pass.
- `SHA256SUMS.txt` regenerated.

## Behavior

No runtime/conversion code was changed in this pass. The goal was documentation clarity and release cleanliness.
