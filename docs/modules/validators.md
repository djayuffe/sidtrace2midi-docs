# Module group: validators

Validators make the release reproducible and catch packaging, schema and conversion regressions.

## `validate_release.sh`

Runs the main release checks:

- Python syntax checks;
- selected regression tests;
- CPU opcode coverage report;
- smoke SID conversion;
- SHA verification;
- file layout checks.

## `validate_distribution.sh`

Runs distribution-facing checks:

- validates release;
- checks CLI help includes expected feature flags;
- checks Top-100 batch scripts exist and are executable;
- checks package integrity.

## `validate_nmos_cpu_release.sh`

CPU-focused validation for `cpu6502.py`.

## Top-100 manifest validators

- `validate_top100_manifest.py`
- `validate_top100_demos_manifest.py`
- `validate_top100_cracktros_manifest.py`

These validate status fields, required schema, note-count thresholds and failed-row reasons.

## SHA verifier

`tools/verify_sha256.py` is portable and avoids GNU-only `sha256sum` dependency. It validates `SHA256SUMS.txt` against the current package files.
