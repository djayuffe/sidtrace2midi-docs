# Documentation maintenance guide

## Rules

1. Do not call the project `midi2sid`; the correct public name is `SIDTrace2MIDI`.
2. Mention that `sid2midi.py` remains as the historical compatibility script.
3. Avoid claiming cycle-perfect or transistor-level C64 emulation.
4. Use “cycle-stamped instruction-level SID register capture” when describing timing.
5. Keep command examples copy/paste safe for zsh: no blank lines after a trailing backslash.

## When adding a feature

Update these files:

- `README.md`
- `QUICKSTART.md` if the user-facing command changes
- `PROJECT_MANIFEST.md`
- `RELEASE_NOTES_NMOS_CPU.md`
- relevant file in `docs/modules/`, `docs/reference` or `docs/deepdives`
- one audit file in `docs/audits/`
- `SHA256SUMS.txt`

## Good documentation style

Use short sections, concrete commands and clear boundaries. This project is technical, but the documentation should let a user run a batch conversion without reading the source.
