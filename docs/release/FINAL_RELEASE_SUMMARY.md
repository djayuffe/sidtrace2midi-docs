# SIDTrace2MIDI Final Release Summary

SIDTrace2MIDI is a SID / PSID / RSID to MIDI extraction toolkit. It does not synthesize SID audio and it does not try to convert MIDI back to SID. It executes the original C64 SID player code, records what the player writes to the SID registers, and turns that register trace into high-resolution MIDI.

## Release identity

- Public name: **SIDTrace2MIDI**
- Historical compatible entrypoint: `sid2midi.py`
- Preferred entrypoint: `sidtrace2midi.py`
- Default Top-100 capture length: 600 seconds
- Default MIDI resolution: PPQ 9600
- Default Top-100 salvage behavior: opt-in only

## What is complete

- Hardened NMOS 6502/6510 CPU core with 256 opcode handlers.
- C64 memory model with 6510 `$0000/$0001` banking support.
- PSID/RSID loader with ROM reporting and strict ROM option.
- SID register capture for primary SID, 2SID and 3SID layouts.
- Canonical `SidFrame` frame model for rendering and debug export.
- MIDI writer with deterministic same-tick event ordering.
- Top-100 classic, demo and cracktro batch converters.
- Manifest validation, manifest analysis and targeted rerun workflow.
- Fast subtune probing and guards for broken/loader-only/demo-runtime SIDs.
- Extensive module, operation, reference and troubleshooting documentation.

## What is intentionally not claimed

SIDTrace2MIDI is an instruction-level SID-register extraction tool. It is not a transistor-level C64 emulator. It does not claim full PHI2 bus fidelity, RDY/SYNC pin behavior, VIC badline/sprite-DMA exactness, real SID analog filter output, or full digi sample reconstruction.

## Recommended first command

```bash
./validate_distribution.sh
```

Then run a smoke conversion:

```bash
./run_example.sh /tmp/sidtrace2midi_smoke.mid
```

## Recommended real conversion

```bash
python3 sidtrace2midi.py /path/to/tune.sid \
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
