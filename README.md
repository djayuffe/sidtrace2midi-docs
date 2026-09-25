# SIDTrace2MIDI — Ultra Documentation Release


> **New public name:** SIDTrace2MIDI.  The historical script `sid2midi.py` remains fully supported, and the new `sidtrace2midi.py` launcher is provided as a clearer entrypoint.  This tool is **SID → MIDI**, not `midi2sid`: it runs SID player code, traces SID chip register writes, then exports MIDI.

A self-contained **Commodore 64 SID → MIDI extraction toolkit** with a hardened NMOS 6502/6510 CPU core, PSID/RSID loader, C64 memory/banking model, SID/CIA/VIC register capture, high-resolution MIDI export, and Top-100 HVSC batch tooling for classic/game tunes, demos and cracktros.

For a concise capability overview, see [docs/FEATURES.md](docs/FEATURES.md).

This project is built for **SID player execution and MIDI conversion**. It is not a transistor-level C64 emulator. The design goal is to execute enough of the real SID init/play code to capture musically meaningful SID register writes and convert them into editable DAW MIDI: notes, pitch bend, pulse-width movement, filter movement, waveform changes, ADSR metadata, noise/drum extraction and timing.


---

## Expanded documentation map

This release now includes a dedicated documentation tree for module-by-module and step-by-step learning. Start here:

```text
docs/README_INDEX.md
```

Module documents:

```text
docs/modules/cpu6502.md          CPU6502 core, tracing, diagnostics, 6510 port
docs/modules/sid2midi.md          SID parser, C64 runtime, SidFrame, MIDI writer
docs/modules/top100_batch.md      classic/demo/cracktro batch system
docs/modules/validators.md        release, SHA and manifest validators
docs/modules/tools.md             helper tools and manifest analysis
docs/modules/tests.md             regression test groups
docs/modules/roms.md              BASIC/KERNAL/CHARGEN ROM handling
```

Step documents:

```text
docs/steps/00_end_to_end_pipeline.md
docs/steps/01_validation_and_release_checks.md
docs/steps/02_single_sid_conversion.md
docs/steps/03_top100_batch_conversion.md
docs/steps/04_manifest_triage_and_reruns.md
docs/steps/05_debugging_register_export.md
docs/steps/06_accuracy_boundaries.md
```

Use these files when you want a slower, clearer explanation of every module and each conversion stage instead of only the quick command examples.

### Branding and naming docs

```text
docs/branding/PROJECT_NAME.md
docs/reference/NAMING_AND_COMPATIBILITY.md
docs/reference/RELEASE_NAMING.md
```

### Extra deep-dives and operations docs

```text
docs/deepdives/SID_REGISTER_TRACE_MODEL.md
docs/deepdives/CPU_TO_MIDI_MAPPING_FLOW.md
docs/tutorials/DAW_IMPORT_GUIDE.md
docs/tutorials/BATCH_RERUN_PLAYBOOK.md
docs/operations/HVSC_SETUP.md
docs/operations/DOCUMENTATION_STYLE_GUIDE.md
```

### Ultra documentation additions

This release adds an expanded documentation layer for release building, log reading, file-tree lookup and onboarding:

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

Use `docs/README_INDEX.md` as the table of contents when learning the project from scratch.

### Final documentation completion additions

This release also adds final operator/reference documentation for completing real HVSC runs and publishing releases:

```text
docs/release/FINAL_RELEASE_SUMMARY.md
docs/architecture/DATA_FLOW_DETAILED.md
docs/reference/OUTPUT_FILES.md
docs/reference/ERROR_REASON_MATRIX.md
docs/howto/CONTINUE_FAILED_TOP100_RUN.md
docs/deepdives/REGISTER_TO_MIDI_DECISIONS.md
docs/operations/PERFORMANCE_TUNING.md
docs/operations/FINAL_QA_MATRIX.md
```

These files explain the full pipeline, output artifacts, error reasons, manifest repair, performance tuning, register-to-MIDI mapping decisions and final QA checklist.




---


## Preferred command name

Use the new clear launcher when writing new documentation or commands:

```bash
python3 sidtrace2midi.py tune.sid --auto --seconds 600 --ppq 9600 -o tune.mid
```

The old command remains supported for compatibility:

```bash
python3 sid2midi.py tune.sid --auto --seconds 600 --ppq 9600 -o tune.mid
```

Both call the same conversion engine.

## What is included

```text
Core conversion:
  cpu6502.py                       NMOS 6502/6510 CPU core
  sid2midi.py                      PSID/RSID SID-register extractor and MIDI writer
  roms/basic.bin                   C64 BASIC ROM for RSID/KERNAL path
  roms/kernal.bin                  C64 KERNAL ROM for RSID/KERNAL path
  roms/chargen.bin                 C64 character ROM for proper C64 memory map

Validation:
  validate_release.sh              full syntax/test/smoke/SHA validation
  validate_distribution.sh         package/CLI/Top-100 distribution validation
  validate_nmos_cpu_release.sh     CPU-focused validation
  tools/verify_sha256.py           portable SHA256 verifier
  tools/cpu_opcode_coverage_report.py

Examples:
  examples/simple_pulse.sid        tiny smoke-test SID
  run_example.sh                   converts the smoke-test SID

Top-100 batch tooling:
  convert_top100_exact.sh          classic/game Top-100 wrapper
  convert_top100_hvsc.py           classic/game Top-100 resolver/converter
  validate_top100_manifest.py
  TOP100_AUTO_README.md

  convert_top100_demos_exact.sh    demo-scene Top-100 wrapper
  convert_top100_demos_hvsc.py
  validate_top100_demos_manifest.py
  TOP100_DEMOS_README.md

  convert_top100_cracktros_exact.sh
  convert_top100_cracktros_hvsc.py
  validate_top100_cracktros_manifest.py
  TOP100_CRACKTROS_README.md
```

---

## Release status

This release closes the current CPU + SID2MIDI + Top-100 + logic-order + README/distribution audit chain.

Validated capabilities:

```text
CPU:
  - 256/256 opcode handlers present
  - 151/151 official NMOS 6502 opcodes covered
  - common NMOS undocumented opcodes implemented for SID players/decrunchers
  - configurable decimal policy: nmos / binary / adjusted / strict
  - safe KIL/JAM handling with strict_jam option
  - IRQ + NMI support
  - BRK/JAM/unstable opcode diagnostics
  - bounded deque trace buffer with exact `trace_seen` / `trace_total` / `trace_dropped` accounting and `clear_trace()`
  - 6510 $0000/$0001 processor-port latch, optional CPU-level interception and configurable host side-effect mirroring

SID2MIDI:
  - PSID and RSID loading
  - PSID v2/v3/v4 metadata handling
  - 2SID and 3SID base support
  - BASIC SYS scan for simple RSID/BASIC loaders
  - C64 RAM/ROM/I/O memory map with CPU-side 6510 banking
  - ROM presence reporting and optional --require-roms hard failure
  - CIA Timer A/B period detection and improved timer advancement
  - dynamic IRQ/KERNAL vector handling
  - optional --respect-irq-disable strict IRQ behavior
  - named SidFrame access model instead of fragile magic-only tuple indexing
  - multi-SID aware loop signature
  - robust MIDI VLQ/meta-event writer
  - high-resolution MIDI timing, default PPQ 9600

Batch:
  - Top-100 classic/game, demo and cracktro wrappers
  - strict resolver policy, no broad generic-name collapse
  - retry profiles for stubborn init/play paths
  - keep-going batch behavior
  - manifest JSON/CSV output
  - per-song debug logs
  - skip-existing with note-count recovery
```

---

## Requirements

```text
Python 3.10+ recommended
No third-party Python packages required
macOS or Linux shell for bundled .sh wrappers
HVSC tree required only for Top-100 batch conversion
```

The release is intentionally dependency-light. Everything required for CPU tests, the smoke SID conversion, SHA verification and normal conversion is inside the package.

---

## Install / unpack

```bash
unzip sidtrace2midi_documentation_ultra_release.zip
cd sidtrace2midi
```

Make scripts executable if your unzip tool did not preserve mode bits:

```bash
chmod +x *.sh *.py
```

---

## Validate the release

Run the complete distribution check:

```bash
./validate_distribution.sh
```

Run the full CPU/SID2MIDI validation:

```bash
./validate_release.sh
```

Expected high-level result:

```text
Ran 78 tests
OK
CPU6502 opcode coverage
handlers: 256/256
official opcodes covered: 151/151
simple_pulse.sid: 6 tracks, 1 notes, 41 CC, PPQ 9600
SHA256SUMS OK
SID2MIDI release validation OK
SID2MIDI distribution validation OK
```

Verify only file integrity:

```bash
python3 tools/verify_sha256.py
```

---

## Quick smoke conversion

```bash
./run_example.sh /tmp/simple_pulse_sid2midi.mid
```

This converts the bundled tiny SID and proves that CPU, SID loader, ROM path, MIDI writer and output file creation work.

---

## Convert one SID

Recommended full-song mode:

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --auto \
  --seconds 600 \
  --auto-min-seconds 540 \
  --auto-confirm-windows 3 \
  --ppq 9600 \
  --bpm 125 \
  --drumvoice 3 \
  --report \
  -o tune.mid
```

Fixed-duration mode:

```bash
python3 sid2midi.py /path/to/tune.sid \
  --song 1 \
  --seconds 180 \
  --ppq 9600 \
  --bpm 125 \
  --drumvoice 3 \
  --report \
  -o tune_180s.mid
```

Strict ROM mode for RSID/KERNAL-sensitive files:

```bash
python3 sid2midi.py /path/to/tune.sid \
  --auto \
  --seconds 600 \
  --require-roms \
  --report \
  -o tune.mid
```

Stubborn init/play path:

```bash
python3 sid2midi.py /path/to/tune.sid \
  --seconds 600 \
  --max-ins-init 16000000 \
  --max-ins-call 1000000 \
  --salvage-init \
  --report \
  -o tune.mid
```

---

## Important shell usage note

Do not put blank lines after a trailing `\` in zsh/bash. This is wrong:

```bash
./convert_top100_demos_exact.sh \

  /Users/ulfbertilsson/Downloads/C64Music \

  ~/Downloads/c64_top100_demos_midi
```

The shell will try to execute the path as a command and can print `permission denied`.

Use one line:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Or use backslashes with no blank lines:

```bash
./convert_top100_demos_exact.sh \
  /Users/ulfbertilsson/Downloads/C64Music \
  ~/Downloads/c64_top100_demos_midi
```

---

## Main `sid2midi.py` options

```text
Input/output:
  sidfile                         input .sid file
  -o, --out FILE                  output .mid path
  --song N                        subtune number, 1-based
  --report                        print conversion and ROM/timing summary
  --require-roms                  fail if required C64 ROMs are missing

Length and timing:
  --seconds S                     maximum render duration
  --auto                          detect loop/full-song length and trim
  --auto-min-seconds S            ignore false loops below this duration
  --auto-confirm-windows N        require repeated confirmation windows
  --bpm B                         DAW grid BPM label
  --auto-bpm                      derive BPM label from frame/row settings
  --frames-per-row N              tracker-style auto-BPM helper
  --rows-per-beat N               tracker-style auto-BPM helper
  --ppq N                         MIDI pulses per quarter note; default 9600

MIDI mapping:
  --drumvoice 1|2|3               route selected voice/noise to channel 10 drums
  --no-bend                       disable pitch bend output
  --no-cc                         disable CC automation output

Safety and compatibility:
  --max-ins-init N                SID init instruction budget
  --max-ins-call N                per-frame play/IRQ instruction budget
  --max-stuck-frames N            abort after repeated over-budget frames
  --strict-init                   make init timeout fatal
  --salvage-init                  continue extraction after init timeout when useful
  --respect-irq-disable           strict I-flag behavior for KERNAL IRQ path
```

View exact current help:

```bash
python3 sid2midi.py --help
```

---

## MIDI mapping

Typical channels:

```text
Channel 1       primary SID voice 1
Channel 2       primary SID voice 2
Channel 3       primary SID voice 3
Channel 10      drums/noise if --drumvoice is selected
Extra channels  2SID/3SID voices when present
```

Important CC lanes:

```text
CC20  waveform
CC21  sync
CC22  ring modulation
CC23  test bit
CC70  pulse width / PWM
CC73  attack
CC75  decay
CC79  sustain
CC72  release
CC74  filter cutoff
CC71  resonance
CC24  filter mode
CC25  filter routing
CC7   master volume
CC26  $D418 digi activity
```

Pitch bend is used for SID frequency remainder, slides, vibrato and detune. Keep pitch bend lanes when importing into a DAW.

Recommended DAW import:

```text
Quantize: off
Humanize: off
Pitch bend import: on
CC import: on
Pitch bend range: usually +/-2 semitones
```

---

## Top-100 HVSC batch conversion

You need a local HVSC checkout, for example:

```text
/Users/ulfbertilsson/Downloads/C64Music
```

### Classic/game Top-100

```bash
./convert_top100_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_midi
```

Validate:

```bash
python3 validate_top100_manifest.py ~/Downloads/c64_top100_midi/top100_manifest.json --min-notes 100
```

### Demo-scene Top-100

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi
```

Validate:

```bash
python3 validate_top100_demos_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --min-notes 100
```

### Cracktro / intro Top-100

```bash
./convert_top100_cracktros_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_cracktros_midi
```

Validate:

```bash
python3 validate_top100_cracktros_manifest.py ~/Downloads/c64_top100_cracktros_midi/top100_cracktros_manifest.json --min-notes 80
```

### Batch defaults

The exact wrappers use safe defaults:

```text
--auto
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
--ppq 9600
--timeout 300
--skip-existing
--keep-going
--scan-policy preferred-first
```

Batch retry profiles are used for stubborn tunes. If a tune times out during init, the converter can retry with larger init/call budgets and salvage-init policy rather than failing the whole batch.

Outputs:

```text
*.mid                         converted MIDI files
*_manifest.json               machine-readable manifest
*_manifest.csv                spreadsheet-friendly manifest
debug/*.log                   per-tune debug logs
```

---

## Resolver policy

The Top-100 scripts intentionally avoid dangerous broad fuzzy matching.

```text
- exact seeded paths preferred
- local HVSC auto-fill used when seeds differ across HVSC versions
- generic names such as Intro.sid, Loader.sid, Music.sid and Demo_Tune.sid are not broadly matched
- duplicate resolved SID sources are rejected
- suspicious one-letter junk and helper/test/sfx/basic/picture files are avoided
```

This prevents the old failure mode where many ranks collapse into the same generic file.

---



### Final CPU6502 correctness closure

The final CPU pass closes the last audit-risk items around diagnostics and classification:

- trace accounting is derived from `trace_seen - trace_total`, so `deque(maxlen=...)` eviction cannot create off-by-one dropped counts;
- `trace_limit=0` means counter-only tracing, `trace_limit=None` means unbounded tracing, and `clear_trace()` resets all trace counters;
- `OFFICIAL_OPS` is regression-tested as the exact 151-opcode NMOS 6502 set, so official JMP/JSR/RTS/BRK/branch opcodes do not inflate illegal-opcode counts;
- `disassemble_at()` gives a safe, non-mutating one-line debug view for the current PC or a supplied address;
- 6510 `$0000/$0001` mirroring is explicit via `mirror_6510_port_writes` and `mirror_6510_port_reads`.

Decimal ADC/SBC remains intentionally documented as practical NMOS/SID extraction behavior.  Strict mode rejects invalid BCD inputs, but the package does not claim transistor-level invalid-BCD analog flag quirks.



## Complete README / Distribution Final Closure

This pass is a documentation and packaging closure on top of the logic-order-perfect codebase.  It does not remove the previous CPU/SID2MIDI/Top-100 fixes; it makes the release easier to unpack, validate, run and audit.

What this closure adds:

```text
- README.md expanded into a final operator/developer manual
- release name and validation expectations updated to the current package
- Quickstart aligned with the current package and common macOS/zsh usage
- manifest and release notes aligned with the actual file tree
- final audit document for the README/distribution cleanup
- SHA256SUMS regenerated after all documentation changes
- validation re-run from the cleaned package tree
```

The package is intended to be used directly from a normal Downloads directory.  No build step is required.

### Recommended final validation command

```bash
./validate_distribution.sh
```

This is the highest-level check and runs the practical release contract: syntax, tests, smoke SID conversion, opcode coverage, CLI flag checks, Top-100 wrapper checks, SHA verification and cache cleanup.

### What “complete” means here

For this project, complete means:

```text
- correct release packaging
- deterministic validation
- reproducible SHA file integrity
- tested CPU opcode coverage and diagnostics
- tested SID2MIDI conversion path
- tested frame/timing/event ordering behavior
- integrated classic/demo/cracktro Top-100 batch tooling
- documented accuracy boundary
```

It does not mean transistor-level emulation.  The package remains an instruction-level SID register extractor designed for high-quality MIDI generation.

## CPU6502 API quick reference

```python
from cpu6502 import CPU6502

cpu = CPU6502(read, write, intercept_6510_port=True)
cpu.reset()
cycles = cpu.call(0x1000, a=0, x=0, y=0, max_ins=4_000_000)
irq_cycles = cpu.irq()
nmi_cycles = cpu.nmi()
print(cpu.status())
```

Useful constructor options:

```python
CPU6502(
    read,
    write,
    strict_jam=False,
    strict_unstable=False,
    trace=False,
    trace_limit=4096,
    ane_magic=0xEE,
    lxa_magic=0xEE,
    decimal_flags="nmos",       # nmos / binary / adjusted / strict
    intercept_6510_port=False,
    mirror_6510_port_writes=True,
    mirror_6510_port_reads=False,
)
```

Diagnostics:

```python
cpu.status()
cpu.step_dump()
cpu.trace_snapshot()
cpu.reset_jam()
```

---

## 6510 banking model

The CPU core tracks the C64 6510 processor port:

```text
$0000 = data direction
$0001 = data latch
```

Effective port value:

```text
effective = (port_data & port_dir) | (~port_dir & 0x3F)
```

`sid2midi.py` uses this effective port for BASIC/KERNAL/CHARGEN/I/O banking. This prevents split-brain between CPU state and the C64 host memory mapper.

---

## Accuracy boundary

In scope:

```text
- SID init/play execution
- C64 register capture for musical extraction
- instruction-level NMOS 6502/6510 behavior with exact official opcode classification
- common undocumented opcodes
- 6510 banking
- CIA Timer A/B period extraction and practical timer advancement
- KERNAL IRQ exit behavior sufficient for RSID-style players
- high-resolution MIDI event timing
```

Out of scope:

```text
- transistor-level Visual6502 accuracy
- per-PHI2 bus trace
- VIC badline/sprite DMA cycle stealing
- analog SID filter/audio emulation
- exact unstable-opcode silicon variation
- real digi sample waveform reconstruction
```

For this project, bounded extraction is preferred over hardware-accurate hangs. JAM/KIL can be made strict for debugging, but safe stop is the default for batch conversion.

---

## Troubleshooting

### `RuntimeError: SID init exceeded instruction budget`

Use the batch wrappers first; they include retry profiles. For a single file:

```bash
python3 sid2midi.py tune.sid --seconds 600 --max-ins-init 16000000 --salvage-init --report -o tune.mid
```

### `permission denied` after a multiline command

You probably inserted a blank line after `\`. Use one physical command line or no blank lines between continued lines.

### RSID output seems wrong

Run with `--report` and check ROM status. For strict behavior:

```bash
python3 sid2midi.py tune.sid --require-roms --report -o tune.mid
```

### Auto loop is too short

Increase minimum loop length:

```bash
python3 sid2midi.py tune.sid --auto --seconds 600 --auto-min-seconds 120 -o tune.mid
```

### DAW import sounds too static

Do not strip pitch bend or CC lanes. SID expression is often in bend, PWM and filter CC data rather than only notes.

---

## Project layout

```text
sidtrace2midi/
├── README.md
├── QUICKSTART.md
├── PROJECT_MANIFEST.md
├── RELEASE_NOTES_NMOS_CPU.md
├── FINAL_CLOSURE_REPORT.md
├── REQUIREMENTS.md
├── SHA256SUMS.txt
├── cpu6502.py
├── sid2midi.py
├── run_example.sh
├── validate_release.sh
├── validate_distribution.sh
├── validate_nmos_cpu_release.sh
├── convert_top100_*.py / .sh
├── validate_top100_*.py
├── TOP100_*_README.md
├── examples/
├── roms/
├── tests/
├── tools/
└── docs/audits/
```

---

## Final release notes

This release is the completed cleaned distribution for the current SID2MIDI line: CPU closure, SID2MIDI feature closure, audit-finding closure, Top-100 integration and batch-retry closure. The package is intended to be directly unzipped, validated and used on a local HVSC tree.


## Final CPU correctness closure

The last CPU pass fixes the remaining API/diagnostic edge cases from the final audit:

```text
- `OFFICIAL_OPS` is regression-tested as the exact 151 official NMOS 6502 opcodes.
- bounded trace accounting is now exact: `trace_seen - trace_total == trace_dropped`.
- `clear_trace()` resets trace state for long batch/debug sessions.
- direct manual `step()` updates `last_stop_reason` for normal step, BRK and JAM.
- 6510 `$0000/$0001` interception can mirror host write/read side effects when tests or loggers need it.
- unused BCD converter helpers were removed; decimal behavior is documented as practical instruction-level policy, not transistor-level invalid-BCD truth.
```

## Logic Order / Frame / Timing Final Closure

- MIDI event order is now explicit and stable: meta, program, CC/bend, note-off, note-on.
- SidFrame is the canonical internal frame model; legacy tuple frames are normalized at API boundaries.
- `convert()` validates frame/timing alignment before MIDI rendering.
- Multi-SID frame access no longer depends on raw magic tuple indices.
- Loop detection now prefers the best-evidenced loop candidate instead of the first early tail match.
- `run_tune()` uses a pre-call elapsed-period contract so timer writes affect the next frame cleanly.
- Added `docs/audits/SID2MIDI_LOGIC_ORDER_FRAME_TIMING_FINAL_AUDIT.md` and regression tests.


## README / Distribution Cleanup Final Closure

- README now documents the current release name, validation order, shell gotchas, CPU API, SidFrame model, timing/event ordering closure, Top-100 batch workflow, ROM handling and accuracy boundary in one place.
- QUICKSTART is aligned with the final package name and includes the safest one-line demo/classic/cracktro batch commands.
- PROJECT_MANIFEST and RELEASE_NOTES were refreshed so they match the actual cleaned archive.
- SHA256SUMS was regenerated after documentation cleanup.
- Added `docs/audits/README_DISTRIBUTION_FINAL_RELEASE_AUDIT.md`.


## Long default Top-100 song policy

The Top-100 wrappers now render longer by default because demo/cracktro material often contains short intro loops that can otherwise be accepted too early.

Default batch values:

```text
--seconds 600
--auto-min-seconds 540
--timeout 300
--auto-confirm-windows 3
--ppq 9600
```

This means the converter may capture up to ten minutes, ignores loop candidates shorter than three minutes, and gives each SID more host time before timing out.  You can still override everything from the command line:

```bash
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi --seconds 900 --auto-min-seconds 240 --timeout 480
```

Weak salvage outputs are no longer kept as future `--skip-existing` successes.  If a retry profile produces a 0-note or under-min-note MIDI, the batch marks the row failed and removes that weak MIDI file by default.  Use `--allow-weak-midi` only for forensic debugging when you intentionally want to keep such artifacts.

## Final full-length Top-100 defaults

The Top-100 wrappers are intentionally biased toward long, DAW-ready captures:

```text
--seconds 600
--auto-min-seconds 540
--auto-confirm-windows 3
--timeout 300
```

This means a tune can still loop-detect automatically, but a short or mid-length repeating intro around 90–300 seconds is not accepted as the final song length by default.  The batch now tries to produce a near-ten-minute arrangement unless a very strong late loop is found.

Weak salvage outputs are not kept as success.  If a retry profile produces `0 notes`, `2 notes`, or any known note count below `--min-notes`, the MIDI file is deleted and the row is marked failed unless `--allow-weak-midi` is explicitly set.  If the SID has multiple subtunes, failed/weak song 1 now triggers automatic subtune scanning up to `--song-scan-limit`, so demo files where song 1 is a loader/wait loop can still resolve to a musical subtune.

## Final Top-100 subtune scan behavior

The Top-100 wrappers now use a fast probe before spending the expensive retry stack on alternate subtunes. This fixes pathological demo SIDs where song 1 and many alternate songs all enter loader/wait-loop code and `salvage-init` returns 0-note MIDI.

Default alternate-subtune probe policy:

```text
--subtune-probe-seconds 45
--subtune-probe-timeout 60
--subtune-probe-min-notes 20
--subtune-zero-streak-limit 4
```

The seeded/requested song still gets the full retry stack. Alternate subtunes are promoted to full 600-second rendering only if the cheap probe shows real musical activity. Use `--exhaustive-subtune-scan` when you intentionally want the old slow forensic behavior for every subtune.

For log lines like `notes=0` or repeated `salvage-init` over many subtunes, this release now stops early and marks the tune failed instead of wasting time and keeping fake MIDI.

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

## Final batch perfection: fast failure, no false salvage success

The Top-100 wrappers are tuned for long unattended HVSC runs.  The default
policy is now intentionally conservative:

- render target: `--seconds 600`
- loop acceptance floor: `--auto-min-seconds 540`
- loop confirmation: `--auto-confirm-windows 3`
- alternate-subtune quick probe before expensive retries
- stop alternate scan on repeated weak/zero probes
- cap expensive alternate full renders with `--max-full-subtune-renders 4`
- automatic `salvage-init` retry is **not** enabled by default

`salvage-init` is useful as a forensic/manual tool, but in large demo batches it
can turn loader/wait-loop subtunes into 0-note placeholder MIDI files.  The batch
engine therefore treats salvage as opt-in:

```bash
# normal safe batch, recommended
./convert_top100_demos_exact.sh /Users/ulfbertilsson/Downloads/C64Music ~/Downloads/c64_top100_demos_midi

# only when manually investigating one stubborn SID/rank
python3 convert_top100_demos_hvsc.py \
  --hvsc /Users/ulfbertilsson/Downloads/C64Music \
  --out ~/Downloads/c64_top100_demos_midi \
  --start-at 63 --stop-after 1 \
  --salvage-retry \
  --debug
```

After a long run, inspect the manifest and get targeted rerun commands:

```bash
python3 tools/analyze_top100_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --emit-rerun
```

The analyzer groups `reason`, `profile`, weak rows, failed rows, probe counts and
full-render counts.  It does not modify files.

## Final batch performance closure: salvage is opt-in

The final Top-100 batch defaults are designed to avoid wasting many minutes on
loader subtunes that repeatedly produce `notes=0` through `salvage-init`.

Default automatic retries are now:

1. `default`
2. `large-init`
3. `large-init-large-call`

`salvage-init` is available only when explicitly requested with
`--salvage-retry` or when manually passing `--salvage-init`.  This keeps normal
Top-100 classic/demo/cracktro runs fast and prevents 0-note placeholder MIDIs
from becoming future `--skip-existing` false successes.

The subtune scanner also has a hard cap for expensive full alternate renders:

```text
--max-full-subtune-renders 4
```

For post-run triage, use:

```bash
python3 tools/analyze_top100_manifest.py \
  ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json \
  --emit-rerun
```

This prints grouped failure reasons and exact rerun commands for weak/failed
ranks.

## Final cleanup/perfection closure

This release closes the remaining low-level audit items in the combined `cpu6502.py` + `sid2midi.py` path:

- CPU trace counters now have explicit semantics: `trace_seen` is lifetime traced instructions, `trace_total`/`trace_len` are retained rows, and `trace_dropped = trace_seen - trace_total`.
- `OFFICIAL_OPS` is locked to the full 151 official NMOS 6502 opcodes, so diagnostics no longer misclassify BRK/JSR/JMP/RTS/RTI/branches as illegal.
- 6510 port mirror-read failures are counted via `port_mirror_read_errors` without overriding the CPU-owned `$0000/$0001` port state.
- Malformed legacy frame tuples now fail loudly at helper boundaries instead of silently producing zero-register MIDI. Internal rendering still normalizes to `SidFrame`.
- `--cia-advance-mode` makes the instruction-level CIA ordering explicit: default `pre_irq_latch` models an already-latched IRQ source before the handler; `post_call` exists for stricter debugging experiments.
- `--export-register-json` writes the raw captured `SidFrame` register stream plus `fcyc` timing metadata for loop/debug/regression analysis.

The converter remains intentionally instruction-level SID-register extraction, not a transistor-level VIC/CIA/SID emulator.



## Perfect continuation cleanup

This release adds a final batch/distribution polish pass:

- Direct `convert_top25_hvsc.py --top N` now means “attempt N ranked entries” unless `--limit` is explicitly supplied.
- `--no-delete-weak-midi` is available for forensic/debug output preservation. Production batch defaults still delete weak/0-note MIDI files so future `--skip-existing` runs do not keep false successes.
- `validate_top100_manifest.py` now validates manifest schema in addition to weak notes, missing MIDI, duplicate SID sources and suspicious short generic matches.
- `run_full_tests.sh` delegates to `tools/run_test_files.py` for isolated per-file regression execution.
- Documentation now describes the engine as cycle-stamped instruction-level SID-register capture, not full transistor-level C64 emulation.

## ASCII logo

```text
  _____ _____ _____ _______                  ___ __  __ _____ _____ _____  _____ 
 / ____|_   _|  __ \__   __|                |__ \  \/  |_   _|  __ \_   _|/ ____|
| (___   | | | |  | | | |_ __ __ _  ___ ___   ) | \  / | | | | |  | || | | (___  
 \___ \  | | | |  | | | | '__/ _` |/ __/ _ \ / /| |\/| | | | | |  | || |  \___ \ 
 ____) |_| |_| |__| | | | | | (_| | (_|  __// /_| |  | |_| |_| |__| || |_ ____) |
|_____/|_____|_____/  |_|_|  \__,_|\___\___|____|_|  |_|_____|_____/_____|_____/ 

          SID / PSID / RSID  ->  C64 player execution  ->  SID register trace  ->  MIDI
```

The logo is also available as `LOGO_ASCII.txt` and documented in `docs/branding/ASCII_ART_LOGO.md`.
