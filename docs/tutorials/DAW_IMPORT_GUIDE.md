# DAW import guide

SIDTrace2MIDI produces high-resolution multi-track MIDI designed for DAW editing.

## Recommended conversion

```bash
python3 sidtrace2midi.py tune.sid \
  --song 1 \
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

## Import into Logic, Ableton, Reaper or Cubase

1. Import the `.mid` file.
2. Keep tempo at the grid BPM shown in the report unless you intentionally want
   to remap the song.
3. Assign one synth/instrument per SID voice track.
4. Map CC lanes for pulse width/filter automation.
5. Use the noise/drum track as a guide for drum replacement or layering.

## Recommended track interpretation

```text
Voice 1      melody/bass/arpeggio depending on tune
Voice 2      counterline/chords/arpeggio
Voice 3      lead/noise/drums/digi helper depending on tune
Automation   filter, pulse width, waveform, volume
```

## Why PPQ 9600

C64 music often has fast arps, vibrato and gate tricks.  PPQ 9600 keeps timing
fine enough for editing without forcing a DAW-specific format.

## Common cleanup after import

- Quantize only if you want DAW-grid music; do not blindly quantize if you want
  C64 groove.
- Keep pitch bend lanes; many SID melodies rely on slides/vibrato.
- Keep CC automation; it contains pulse width and filter motion.
- Replace noise bursts with drums only after listening to the original role of
  voice 3.
