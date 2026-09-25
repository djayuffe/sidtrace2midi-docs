# SID register trace model

SIDTrace2MIDI is not an audio-to-MIDI tool and not a waveform transcription
system.  It extracts musical intent by executing the original C64 player code and
observing SID register writes.

## Why register tracing works

C64 music players usually update SID registers once per frame or via a CIA timer.
Those writes encode the musical state:

```text
frequency low/high       -> pitch
control register gate    -> note on/off and waveform
pulse width              -> PWM movement
ADSR                     -> articulation metadata
filter cutoff/resonance  -> MIDI CC automation
volume / $D418 writes    -> master volume / digi activity
```

## Pipeline

```text
SID file
  -> header parser
  -> load/init/play addresses
  -> C64 memory map and 6510 banking
  -> CPU6502 executes init/play/IRQ
  -> C64.write() captures SID/CIA/VIC writes
  -> SidFrame per logical frame
  -> loop detector / length policy
  -> MIDI event writer
```

## What is captured

Per frame, the canonical `SidFrame` stores:

```text
sid      primary SID register image
trig     gate-trigger flags for voices 1..3
trigcyc  C64-cycle timestamps for trigger writes
sidB     optional second SID register image
trigB    second SID gate triggers
trigcycB second SID trigger cycles
sidC     optional third SID register image
trigC    third SID gate triggers
trigcycC third SID trigger cycles
digi     $D418 / digi write activity counter
```

## What is not captured

SIDTrace2MIDI intentionally does not emulate the full analog SID output stage.
It does not reconstruct every filter nonlinearity, distortion, chip variance or
sample waveform.  The goal is editable MIDI, not bit-identical audio rendering.
