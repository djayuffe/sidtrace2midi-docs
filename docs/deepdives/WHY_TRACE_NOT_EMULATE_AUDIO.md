# Why SIDTrace2MIDI traces registers instead of emulating audio

SIDTrace2MIDI does not render audio and then guess notes from waveform analysis. It runs the original player code and captures the data written to SID registers.

## Why this is better for MIDI

Audio-to-MIDI has to infer pitch, envelope and timing after the SID chip has already mixed oscillators, noise, ring modulation and filter movement. Register tracing sees the musical intent earlier:

- frequency registers become pitch / pitch bend;
- gate transitions become note boundaries;
- waveform registers become instrument hints;
- ADSR registers become envelope metadata;
- filter and pulse-width registers become MIDI CC lanes.

## What this cannot do

It cannot perfectly reproduce analog SID chip quirks. It intentionally exports editable DAW MIDI, not a bit-perfect audio render.
