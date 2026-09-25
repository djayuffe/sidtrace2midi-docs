# QA Checklist

Use this checklist after code or documentation changes.

## Package-level checks

- [ ] `./validate_release.sh` passes.
- [ ] `./validate_distribution.sh` passes.
- [ ] `./run_full_tests.sh` passes.
- [ ] `python3 tools/verify_sha256.py` passes after SHA regeneration.
- [ ] No `__pycache__` directories in zip.
- [ ] No `*.pyc` files in zip.
- [ ] `unzip -t` reports no errors.

## CPU checks

- [ ] Opcode coverage reports `handlers: 256/256`.
- [ ] Official opcode coverage reports `151/151`.
- [ ] Trace counters behave correctly for limited, unlimited and zero trace limits.
- [ ] 6510 port mirror/write/read policy tests pass.

## SID2MIDI checks

- [ ] `examples/simple_pulse.sid` converts.
- [ ] ROM status reports OK.
- [ ] CLI help contains new flags.
- [ ] `--export-register-json` works.
- [ ] `--cia-advance-mode` accepts both choices.

## Batch checks

- [ ] Classic wrapper exists and is executable.
- [ ] Demo wrapper exists and is executable.
- [ ] Cracktro wrapper exists and is executable.
- [ ] Weak MIDI policy is documented.
- [ ] Salvage retry is opt-in.
- [ ] Manifest analyzer is documented.

## Documentation checks

- [ ] README links to `docs/README_INDEX.md`.
- [ ] Docs index lists new reference/tutorial/operations docs.
- [ ] Project manifest includes new files.
- [ ] Release notes include the documentation expansion.
- [ ] Accuracy boundary is stated honestly.

