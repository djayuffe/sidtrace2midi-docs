# Final QA Matrix

Use this matrix before publishing a release.

| Area | Command / Check | Expected |
|---|---|---|
| Syntax | `./validate_release.sh` | Python syntax OK |
| CPU coverage | `python3 tools/cpu_opcode_coverage_report.py` | 256/256 handlers, 151/151 official opcodes |
| Smoke MIDI | `./run_example.sh /tmp/smoke.mid` | MIDI written with report |
| Distribution | `./validate_distribution.sh` | CLI flags and Top-100 scripts OK |
| SHA | `python3 tools/verify_sha256.py` | `SHA256SUMS OK` |
| Zip | `unzip -t <release>.zip` | no errors |
| Docs | `docs/README_INDEX.md` | links to current module/reference/howto docs |
| Branding | root folder and README | `SIDTrace2MIDI`, not `midi2sid` |

## Manual smoke commands

```bash
python3 sidtrace2midi.py examples/simple_pulse.sid --report -o /tmp/simple.mid
python3 sid2midi.py examples/simple_pulse.sid --report -o /tmp/simple_compat.mid
python3 tools/analyze_top100_manifest.py --help
```
