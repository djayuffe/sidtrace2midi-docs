# Documentation style guide

This project uses documentation for both users and low-level auditing.

## Rules

- Be explicit about direction: SID to MIDI, not MIDI to SID.
- Say `cycle-stamped instruction-level register capture`, not `cycle-perfect C64`.
- Keep commands copy/paste safe for zsh and bash.
- Explain defaults and why they exist.
- Distinguish production batch mode from forensic/debug mode.
- Document honest boundaries instead of overclaiming.

## Preferred wording

```text
SIDTrace2MIDI executes SID player code and captures SID register writes.
```

Avoid:

```text
Perfect C64 emulator
Audio transcription
MIDI to SID converter
```

## Audit files

Audit files in `docs/audits/` should describe what changed, what was validated,
and what remains intentionally out of scope.
