# Feature guide

SIDTrace2MIDI is an executable SID-register trace extractor and MIDI exporter.
It runs enough of the C64 player environment to observe musical register writes
and turn them into DAW-editable events.

Choose this release when you need the most complete operator, architecture,
troubleshooting, and release-process documentation.

## Extraction and emulation

- PSID and RSID loading with ROM, banking, CIA, VIC, and IRQ support.
- Hardened NMOS 6502/6510 execution, including documented and common illegal
  instructions plus useful diagnostics.
- MIDI notes, pitch bend, ADSR, pulse width, filter, waveform, routing, digi,
  and timing metadata from SID register activity.

## Operations

- Single-file conversion with loop detection and subtune recovery.
- HVSC Top-100 workflows for classics, demos, and cracktros.
- Manifests, release validation, quality gates, and focused operator guides.

Use `docs/README_INDEX.md` for the full documentation map and
`docs/tutorials/FIRST_30_MINUTES.md` for a guided first run.
