# Register-to-MIDI Decisions

SIDTrace2MIDI converts SID register behavior into MIDI events. This document explains the practical decisions behind that mapping.

## Frequency to note

A SID voice has a 16-bit frequency register. The converter estimates musical pitch from this register and emits MIDI notes and pitch bend. Exact SID pitch can move continuously, while MIDI note grids are discrete. The converter therefore uses note events for stable pitch regions and pitch bend / CC movement for expressive movement.

## Gate to note boundaries

The SID gate bit is the strongest signal for note starts and stops. A rising gate edge creates a note-on. A falling gate edge creates a note-off. Same-tick retriggers are ordered as note-off before note-on to avoid stuck notes.

## Pulse width to CC

Pulse width is not a note; it is a timbral movement. It is exported as MIDI CC so a DAW instrument can map it to PWM, wavetable position, filter movement or automation.

## Waveform/control to CC or metadata

SID waveform/control bits can change rapidly. The converter preserves these changes as MIDI control information rather than trying to force every change into a new note.

## ADSR to velocity and metadata

The SID envelope generator is analog/digital hybrid behavior and not reconstructed sample-by-sample. ADSR registers are used as hints for velocity, articulation and metadata.

## Filter to CC

Filter cutoff/resonance/mode changes are represented as CC lanes. This is suitable for DAW editing and automation but is not a reSID-style audio filter render.

## Digi writes

Writes to `$D418` are counted and can be exported as debug information. Full sample reconstruction is outside the current project scope.

## Why not audio?

The goal is editable MIDI, not SID audio rendering. If you need audio, use a SID emulator or a SID plugin. If you need arrangement data, note timing, pitch and automation for DAW editing, use SIDTrace2MIDI.
