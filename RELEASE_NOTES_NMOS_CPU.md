# Release notes — NMOS CPU 100% closure

This release finalizes the CPU6502 core for SID2MIDI extraction.

## Added

- `tests/test_cpu6502_final_100_closure.py`
- `tools/cpu_opcode_coverage_report.py`
- `docs/audits/CPU_OPCODE_COVERAGE_REPORT.txt`
- `docs/audits/NMOS_6502_CPU_100_PERCENT_CLOSURE_AUDIT.md`

## Closed

- Verified call sentinel return contract.
- Verified JSR/RTS, BRK, RTI, zero-page wrap, branch cycle penalties and KERNAL IRQ exit.
- Added more decimal ADC/SBC reference cases.
- Verified all 256 opcodes are bounded for one-step execution.
- Confirmed official opcode coverage: 151/151.
- Confirmed handler coverage: 256/256.
- Confirmed KIL/JAM stops safely instead of continuing as NOP.

## Policy

The CPU is complete for PSID/RSID SID-register extraction. It remains intentionally non-transistor-level: unstable illegal opcodes that are not useful to SID extraction are bounded/recoverable so large HVSC batches do not hang.

## Final-final closure pass

- Added `FINAL_CLOSURE_REPORT.md`.
- Added `REQUIREMENTS.md`.
- Added `validate_release.sh` as a top-level full validator.
- Added `run_example.sh` for quick smoke conversion.
- Reworked validation syntax check to avoid generating `__pycache__` in release validation.
- Regenerated `SHA256SUMS.txt` after final cleanup.

## Audit-driven CPU improvement pass

- Fixed KERNAL IRQ exit double-status-pop bug.
- Added NMI support.
- Added `reset()` / `reset_jam()` lifecycle helpers.
- Added strict forensic modes: `strict_jam` and `strict_unstable`.
- Added opcode diagnostics and optional opcode tracing.
- Added ANE/XAA `$8B` and LXA `$AB` practical approximations with configurable magic constants.
- Added optional 6510 processor-port helper storage.
- Reworked BCD ADC/SBC code for clearer NMOS decimal behavior.
- Added `tests/test_cpu6502_audit_improvements.py`.

## Further improvement pass — 6510 port and diagnostics closure

- Integrated CPU-side 6510 `$0000/$0001` port latch into `sid2midi.py` C64 banking logic.
- Added `CPU6502.effective_6510_port()` with input-bit pull-up behavior.
- Added bounded trace support via `trace_limit` and `trace_dropped`.
- Added `CPU6502.status()` and `__repr__()` diagnostics.
- Added exhaustive valid-BCD ADC/SBC arithmetic tests over 00-99 operands and carry states.
- Added `tests/test_cpu6502_further_improvements.py`.
- Updated opcode coverage report and validation scripts.

## Final Perfect Audit Closure

- `decimal_flags` is now live: `nmos`, `binary`, `adjusted`, `strict`.
- `strict` decimal mode rejects invalid BCD input.
- Added `collections.deque` trace buffer with `trace_dropped` accounting.
- Added `trace_snapshot()` and `step_dump()`.
- Added `brk_count` diagnostics.
- Added optional automatic 6510 `$0000/$0001` trapping via `intercept_6510_port=True`.
- Replaced hot transfer/inc/dec `setattr()` lambdas with direct assignments.
- Added `tests/test_cpu6502_final_perfect.py`.
- Updated validation and opcode coverage report.

## SID2MIDI uploaded feature integration pass

Integrated feature logic from the uploaded `sid2midi(1).py` while preserving the final-perfect NMOS CPU core.

Highlights:

- PSID v4 3SID support.
- Correct 2SID/3SID base calculation.
- PSID-mode RAM-under-ROM behavior while keeping SID/CIA/VIC I/O visible.
- BASIC SYS stub scanner for simple BASIC/RSID wrappers.
- CIA Timer B support.
- Dynamic IRQ vector/exit path based on current 6510 port banking.
- Safer init/play instruction budgets and stuck-frame aborts.
- Conservative `--auto` loop detection with `--auto-min-seconds` and `--auto-confirm-windows`.
- Rational C64-cycle to MIDI-tick scaling.
- Configurable high-resolution `--ppq`, default 9600.
- `--auto-bpm` DAW-grid helper.
- CPU/C64 6510 port integration preserved through `intercept_6510_port=True`.
- Added `tests/test_sid2midi_feature_integration.py`.


## Final SID2MIDI feature closure pass

- Exposed `C64.current_timer_period()` so CIA Timer-A/Timer-B/vsync period selection is directly testable.
- `run_tune()` now uses that helper instead of a nested closure.
- Added regression tests for CLI feature flags, BASIC SYS scanner, MIDI VLQ/meta length encoding, auto-BPM grid calculation, and Timer-A/Timer-B fallback order.
- Added `tests/test_sid2midi_final_feature_closure.py`.
- Added `docs/audits/SID2MIDI_FINAL_FEATURE_CLOSURE_AUDIT.md`.


## Distribution final closure

- Added `validate_distribution.sh` to verify fresh-unzip usability, example conversion, CLI feature flags, opcode coverage, SHA256 integrity, and absence of Python cache files.
- Added `docs/audits/SID2MIDI_DISTRIBUTION_FINAL_CLOSURE_AUDIT.md`.
- Updated README/QUICKSTART wording to match the current feature-final package.

## Clean release / README closure

- Rewrote `README.md` into a complete release guide.
- Rewrote `QUICKSTART.md` and `REQUIREMENTS.md`.
- Added portable `tools/verify_sha256.py` so SHA verification works on macOS without GNU `sha256sum`.
- Updated `validate_release.sh` and `validate_distribution.sh` to use the portable verifier and keep the tree clean.
- Added `docs/audits/CLEAN_RELEASE_README_CLOSURE_AUDIT.md`.
- Regenerated `SHA256SUMS.txt` after cleanup.

## Top-100 batch integration clean release

Integrated uploaded Top-100 batch tooling:

- `convert_top25_hvsc.py` shared batch engine
- `convert_top100_hvsc.py` + `convert_top100_exact.sh`
- `convert_top100_demos_hvsc.py` + `convert_top100_demos_hvsc.sh` + uploaded exact wrapper
- uploaded `convert_top100_cracktros_hvsc.py` + wrappers
- uploaded Top-100 README files
- uploaded Top-100 validators
- `tests/test_top100_batch_integration.py`

The exact wrappers use full-song ten-minute full-length defaults: `--auto --seconds 600 --auto-min-seconds 540 --auto-confirm-windows 3 --ppq 9600`.

## Top-100 retry / batch cleanup closure

- Added automatic retry profiles for failed Top-100 conversions: `large-init`, `large-init-large-call`, and `salvage-init`.
- Top-100 wrappers now pass `--keep-going` by default.
- Fixed `--skip-existing` manifest rows to count MIDI note-on events instead of writing `notes=0`.
- Removed duplicate row append in the batch manifest loop.
- Added `tests/test_top100_retry_and_release_cleanup.py`.
- Added `docs/audits/TOP100_RETRY_AND_BATCH_FINAL_CLOSURE_AUDIT.md`.

## SID2MIDI audit findings full implementation

- Added explicit ROM status tracking and `--require-roms`.
- `--report` now prints BASIC/KERNAL/CHARGEN ROM status.
- Added stable `SidFrame` namedtuple frame model while preserving old tuple indexing.
- Frame helpers now use named fields and include `_frame_trigcyc()`.
- Multi-SID loop detection now includes extra SID pitch/control/trigger data.
- CIA Timer A/B now has instruction-level advance/reload/one-shot handling and Timer-B count-Timer-A-underflow support.
- Added `--respect-irq-disable` for stricter IRQ masking behavior.
- 6510 port defaults are applied before SID payload placement during `load_sid()`.
- Added `tests/test_sid2midi_audit_findings_closure.py`.

---

## Complete final release cleanup

This release pass rewrote and expanded the top-level README into a complete user/developer manual, refreshed QUICKSTART/REQUIREMENTS/PROJECT_MANIFEST, retained all Top-100 classic/demo/cracktro integration, and regenerated SHA256SUMS after cleanup.

Final validation covers:

```text
- CPU regression tests
- SID2MIDI feature/audit tests
- Top-100 batch integration tests
- opcode coverage report
- ROM status reporting
- smoke SID->MIDI conversion
- CLI flag checks
- distribution file layout
- SHA256 integrity
- pycache/pyc cleanup
```


## CPU6502 final correctness closure

- Fixed trace accounting to use exact total-minus-retained semantics.
- Added `trace_total` and `clear_trace()`.
- Added direct `step()` stop-reason updates for step/BRK/JAM.
- Regression-tested `OFFICIAL_OPS` against the full 151-opcode NMOS official set.
- Added configurable 6510-port host read/write side-effect mirroring.
- Removed unused BCD converter helpers and clarified decimal-mode accuracy boundaries.

## Perfect last-issue closure

- Closed final CPU6502 audit items.
- Verified trace accounting uses `trace_seen - trace_total` instead of legacy deque `before_len` logic.
- Made `trace_limit=0` explicit counter-only tracing.
- Verified `OFFICIAL_OPS` is exactly 151 official NMOS 6502 opcodes.
- Added `disassemble_at()` as a non-mutating debug helper.
- Added final regression tests in `tests/test_cpu6502_perfect_last_issue_closure.py`.
- Added audit document `docs/audits/CPU6502_PERFECT_LAST_ISSUE_CLOSURE_AUDIT.md`.


## Logic Order / Frame / Timing Final Closure

- MIDI event order is now explicit and stable: meta, program, CC/bend, note-off, note-on.
- SidFrame is the canonical internal frame model; legacy tuple frames are normalized at API boundaries.
- `convert()` validates frame/timing alignment before MIDI rendering.
- Multi-SID frame access no longer depends on raw magic tuple indices.
- Loop detection now prefers the best-evidenced loop candidate instead of the first early tail match.
- `run_tune()` uses a pre-call elapsed-period contract so timer writes affect the next frame cleanly.
- Added `docs/audits/SID2MIDI_LOGIC_ORDER_FRAME_TIMING_FINAL_AUDIT.md` and regression tests.


## Complete README / Distribution Final Release

- Expanded `README.md` into the final operator/developer manual for this line.
- Updated `QUICKSTART.md`, `PROJECT_MANIFEST.md`, and release naming references.
- Added `docs/audits/README_DISTRIBUTION_FINAL_RELEASE_AUDIT.md`.
- Regenerated `SHA256SUMS.txt` and validated from a clean package tree.
- This release sits on top of the logic-order-perfect codebase: stable MIDI event order, SidFrame normalization, hard frame/fcyc validation, multi-SID loop signatures, Top-100 tooling and final CPU diagnostics remain included.


## Long default Top-100 batch closure

Top-100 classic, demo and cracktro wrappers now default to longer musical captures:

- `--seconds 600`
- `--auto-min-seconds 540`
- `--timeout 300`

This prevents short or mid-length demo/cracktro intro loops around 90–300 seconds from being accepted too early and gives longer DAW-ready arrangements by default.  Weak 0-note salvage artifacts are deleted instead of being kept as future `--skip-existing` false positives unless `--allow-weak-midi` is explicitly used.

## Full-length batch / weak salvage closure

- Top-100 classic/demo/cracktro wrappers now default to `--seconds 600 --auto-min-seconds 540 --auto-confirm-windows 3 --timeout 300`.
- This makes the batch render near-full ten-minute arrangements by default instead of accepting ~180 second loop candidates too early.
- Weak existing MIDI files below `--min-notes` are deleted and re-rendered instead of being accepted by `--skip-existing`.
- A failed or weak selected subtune now triggers automatic subtune scanning up to `--song-scan-limit`, unless `--no-scan-subtunes-on-failure` is used.
- Salvage-init outputs with 0-note/under-min-note results are marked failed and deleted by default; `--allow-weak-midi` is now strictly a forensic/debug option.

## Top-100 fast subtune probe closure

- Added `--subtune-probe-seconds`.
- Added `--subtune-probe-timeout`.
- Added `--subtune-probe-min-notes`.
- Added `--subtune-zero-streak-limit`.
- Added `--exhaustive-subtune-scan` for old slow forensic behavior.
- Alternate subtunes now get cheap probes before full retry/salvage profiles.
- Consecutive zero-note alternate subtunes stop the scan early by default.
- Prevents pathological multi-subtune demo SIDs from burning minutes per 0-note salvage placeholder.

## Final subtune guard perfection

This release adds one more protection for pathological demo SIDs where alternate
subtune probes fail or time out without even producing a `0 notes` report.  The
batch engine now has two independent guards:

```text
--subtune-zero-streak-limit 4
--subtune-bad-streak-limit 6
--subtune-scan-time-budget 240
```

`zero-streak` stops obvious repeated 0-note loader subtunes. `bad-streak` also
stops repeated probe failures, timeouts, unknown note counts and under-threshold
weak probes. `subtune-scan-time-budget` caps wall-clock probing time per SID so a
single broken demo file cannot stall the whole Top-100 run.

The manifest now includes `reason`, `subtune_attempts` and `probe_attempts`, so a
failed row explains whether it stopped because of weak notes, converter failure,
zero-streak, bad-streak or probe budget. Failed weak outputs are deleted by
default and no longer become future `skip-existing` false successes.

## Subtune/salvage batch perfection closure

- Added `--salvage-retry` as an explicit opt-in.  Automatic Top-100 wrappers no
  longer run salvage-init by default because long demo logs showed it mostly
  created expensive 0-note placeholders for loader subtunes.
- Added `--max-full-subtune-renders` to cap expensive alternate-subtune renders
  after the quick probe phase.
- Added `tools/analyze_top100_manifest.py` to summarize long batch manifests and
  emit precise rerun commands for failed or weak rows.
- Updated README, wrappers, manifest and validation coverage for the new batch
  policy.

## Final continuation: opt-in salvage and manifest triage

- Automatic Top-100 retries no longer use `salvage-init` unless `--salvage-retry`
  is explicitly passed.
- Added `--max-full-subtune-renders` to bound expensive alternate-subtune full
  renders after quick probes.
- Added `tools/analyze_top100_manifest.py` for manifest grouping and targeted
  rerun commands.
- Added `run_full_tests.sh`; `validate_release.sh` remains fast and distribution
  focused, while full regression discovery is available separately.


## Final cleanup/perfection release

- Clarified CPU trace accounting into `trace_seen`, retained `trace_total`, and `trace_dropped`.
- Added `port_mirror_read_errors` diagnostics for optional 6510 host read side-effect mirroring.
- Added strict malformed-frame rejection in SID frame helpers.
- Added `--cia-advance-mode` and `--export-register-json` to `sid2midi.py`.
- Added `tests/test_final_cleanup_perfection.py`.


## Perfect continuation cleanup

- Fixed direct `--top N` semantics in the shared Top-N batch engine.
- Added `--no-delete-weak-midi` forensic/debug override.
- Strengthened Top-100 manifest validation with schema checks.
- Added isolated per-file regression runner: `tools/run_test_files.py`.
- Cleaned wording around cycle-stamped instruction-level accuracy.


## Documentation expansion release

- Added dedicated module documentation under `docs/modules/`.
- Added step-by-step conversion documentation under `docs/steps/`.
- Added `docs/README_INDEX.md` as the documentation entry point.
- Updated README and manifest to reference every documentation module.
- No runtime behavior changed in this documentation-focused release.

## Documentation Plus Release

This release expands documentation without changing the conversion core:

- Added reference docs for CLI, manifest schema, MIDI mapping and CPU6502 API.
- Added deep dives for architecture, timing/CIA, SidFrame, loop detection and ROM/banking.
- Added practical tutorials for single SID conversion and Top-100 demo workflow.
- Added operations docs for troubleshooting, release process and QA checklist.
- Added command cookbook with copy/paste examples.
- Updated the documentation index and main README so users can find each module and workflow step quickly.



## SIDTrace2MIDI naming and documentation ultra pass

- Introduced the public project name **SIDTrace2MIDI**.
- Added `sidtrace2midi.py` as a compatibility launcher around `sid2midi.py`.
- Added dedicated branding, naming and release-naming documentation.
- Added deeper register-trace, CPU-to-MIDI-flow, DAW import, batch rerun, HVSC setup and documentation style guides.
- Updated README, QUICKSTART, docs index and manifest to describe the new name while preserving old command compatibility.

## SIDTrace2MIDI ASCII-logo documentation release

- Added root `LOGO_ASCII.txt` with a terminal-safe SIDTrace2MIDI banner.
- Added `docs/branding/ASCII_ART_LOGO.md` with logo usage and naming guidance.
- Added `docs/architecture/COMPLETE_SYSTEM_MAP.md` with a Mermaid pipeline diagram.
- Added release/how-to/onboarding docs: `MAKE_A_RELEASE.md`, `READ_THE_OUTPUT_LOGS.md`, `FIRST_30_MINUTES.md`.
- Added lookup docs: `FILE_TREE.md`, `GLOSSARY.md`, `WHY_TRACE_NOT_EMULATE_AUDIO.md`, and `DOCUMENTATION_MAINTENANCE.md`.
- Updated README, documentation index and manifest to reference the new material.


## SIDTrace2MIDI final documentation completion

- Added final release summary, detailed data flow, output file reference, error reason matrix, failed-run continuation guide, register-to-MIDI decision deep-dive, performance tuning guide and final QA matrix.
- Updated README, documentation index and project manifest to point to these operator-facing documents.
- No core conversion behavior was changed in this documentation completion pass.
