# Naming and compatibility reference

This release introduces the public project name **SIDTrace2MIDI** while keeping
all existing script names compatible.

## Direction of conversion

The conversion direction is:

```text
.SID / PSID / RSID -> emulated C64 player execution -> SID register frames -> .mid
```

That is why the old `sid2midi.py` file name is still technically correct.  A
name like `midi2sid` is wrong for this project because it describes MIDI-to-SID
creation, which is not what this package does.

## Compatible entrypoints

| Entrypoint | Status | Purpose |
|---|---:|---|
| `python3 sidtrace2midi.py` | preferred | New public-friendly launcher. |
| `python3 sid2midi.py` | supported | Historical direct script. |
| `./convert_top100_exact.sh` | supported | Classic/game Top-100 batch. |
| `./convert_top100_demos_exact.sh` | supported | Demo Top-100 batch. |
| `./convert_top100_cracktros_exact.sh` | supported | Cracktro/intro Top-100 batch. |

## Compatibility promise

The rebrand does not remove or rename the old script.  Existing automation that
calls `sid2midi.py` or the Top-100 wrappers should continue to work.

## Recommended release archive naming

Use this pattern for future releases:

```text
sidtrace2midi_<feature>_release.zip
```

For this release:

```text
sidtrace2midi_documentation_ultra_release.zip
```
