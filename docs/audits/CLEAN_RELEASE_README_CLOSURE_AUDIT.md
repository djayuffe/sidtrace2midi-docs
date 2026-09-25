# Clean Release / README Closure Audit

This closure pass focused on release quality rather than core behavior.

## Changes

- Rewrote `README.md` into a complete user-facing guide.
- Rewrote `QUICKSTART.md` with current release command examples.
- Rewrote `REQUIREMENTS.md` with runtime and ROM requirements.
- Added portable `tools/verify_sha256.py` for macOS/Linux/Windows SHA verification.
- Updated `validate_release.sh` to use the portable verifier instead of GNU-only `sha256sum`.
- Updated `validate_distribution.sh` to re-run portable SHA verification and cache cleanliness checks.
- Regenerated `SHA256SUMS.txt` after cleanup.
- Removed cache/build artifacts before packaging.

## Why

The previous release was technically valid, but the README had grown by appending closure notes. The new README is structured as a real project front page: purpose, requirements, quick start, CLI, MIDI mapping, CPU API, 6510 banking, accuracy boundaries, validation, layout and troubleshooting.

## Validation target

The final distribution must pass:

```bash
./validate_distribution.sh
python3 tools/verify_sha256.py
unzip -t <release>.zip
```
