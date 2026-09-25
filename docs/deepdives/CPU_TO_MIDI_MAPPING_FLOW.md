# CPU-to-MIDI mapping flow

This document explains how a low-level C64 execution trace becomes MIDI.

## 1. CPU execution

`CPU6502` runs the SID player's init and play routines.  The CPU uses callback
memory access, so every write goes through the C64 host object.

```text
CPU opcode -> addressing mode -> C64.read/write -> side-effect capture
```

## 2. C64 host side effects

The C64 host reacts to writes in important ranges:

```text
$0000/$0001   6510 processor port and banking
$D000-$D3FF   VIC/SID/I/O area depending on banking
$D400-$D41F   primary SID registers
2SID/3SID     additional SID register banks
$DC00-$DC0F   CIA 1 timer and interrupt registers
$DD00-$DD0F   CIA 2 / banking-related state
```

## 3. Frame creation

After each logical play step, the current SID register images and trigger flags
are frozen into a `SidFrame`.  The matching `fcyc` array stores C64-cycle
boundaries for each frame interval.

Invariant:

```text
len(fcyc) == len(frames) + 1
```

## 4. Note extraction

For each SID voice, the converter reads frequency, gate and waveform from the
frame stream.  Gate edges and pitch changes become MIDI note and bend events.

## 5. Automation extraction

Pulse width, filter cutoff, resonance, volume and waveform changes are exported
as MIDI controller events so DAWs can edit the SID movement instead of receiving
only flat notes.

## 6. Event rendering

The MIDI writer orders same-tick events deterministically:

```text
meta -> program -> CC / bend -> note-off -> note-on
```

That prevents stuck notes and preserves retrigger articulation.
