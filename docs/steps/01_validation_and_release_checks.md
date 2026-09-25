# Step 01: Validation and release checks

Run this after unpacking a release.

## Complete validation

```bash
./validate_distribution.sh
```

This checks release layout, CLI flags, Top-100 scripts and core validation.

## Core validation

```bash
./validate_release.sh
```

This runs syntax checks, regression tests, opcode coverage, smoke conversion and SHA verification.

## Full tests

```bash
./run_full_tests.sh
```

Use this when developing or changing code.

## SHA only

```bash
python3 tools/verify_sha256.py
```

Use this after unpacking to confirm files match `SHA256SUMS.txt`.
