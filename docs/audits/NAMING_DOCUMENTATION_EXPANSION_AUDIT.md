# Naming + documentation expansion audit

## Purpose

This pass rebrands the public documentation around the clearer name
**SIDTrace2MIDI**, while preserving script compatibility with `sid2midi.py`.
It also adds more module, workflow, DAW and operational documentation.

## Added

```text
sidtrace2midi.py

docs/branding/PROJECT_NAME.md
docs/reference/NAMING_AND_COMPATIBILITY.md
docs/reference/RELEASE_NAMING.md
docs/deepdives/SID_REGISTER_TRACE_MODEL.md
docs/deepdives/CPU_TO_MIDI_MAPPING_FLOW.md
docs/tutorials/DAW_IMPORT_GUIDE.md
docs/tutorials/BATCH_RERUN_PLAYBOOK.md
docs/operations/HVSC_SETUP.md
docs/operations/DOCUMENTATION_STYLE_GUIDE.md
```

## Compatibility

Existing commands using `sid2midi.py` and Top-100 wrappers remain supported.
The new `sidtrace2midi.py` wrapper is a friendly alias.

## Validation

The release was revalidated after SHA regeneration and zip creation.
