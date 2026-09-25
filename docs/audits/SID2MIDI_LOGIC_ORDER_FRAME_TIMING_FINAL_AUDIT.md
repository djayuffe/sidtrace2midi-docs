# SID2MIDI Logic Order / Frame / Timing Final Closure Audit

This pass closes the final low-level script audit around ordering, frame handling,
cycle-to-tick timing and side-effect sequencing.

## Implemented fixes

- MIDI event rendering now uses explicit stable event priorities:
  meta -> program -> CC/bend -> note-off -> note-on.
- Same-tick retriggers now render note-off before the new note-on.
- `Trk` stores an insertion sequence so same-priority events remain stable.
- `SidFrame` is now the internal canonical frame format.
- Legacy tuple frames are accepted only at the API boundary and normalized with
  `ensure_sid_frame()` / `normalize_frames()`.
- `convert()` validates `len(fcyc) == len(frames)+1` and monotonic integer cycle
  timestamps before rendering.
- Multi-SID detection and rendering now use `_frame_regs()` / `_frame_trig()` /
  `_frame_trigcyc()` helpers instead of raw `frames[f][3]` style indexing.
- Filter/digi automation uses named frame helpers.
- `find_loop()` normalizes frames and chooses the best-evidenced loop candidate
  rather than blindly returning the first tail match.
- `tick_scale()` keeps cycle conversion rational via `Fraction` to avoid avoidable
  float drift if non-integer cycle-like values are ever supplied.
- `run_tune()` computes the elapsed playback period before the play/IRQ call,
  passes it into `step_call()`, and then advances the absolute capture clock by
  that same period. Timer writes inside the handler therefore affect the next
  frame, not the already elapsed interval.
- Consecutive play/IRQ budget errors now report the number of frames captured so
  far, making partial-capture diagnostics clearer.

## Still intentionally out of scope

This remains SID-register extraction, not a full PHI2/RDY/SYNC/VIC-badline bus
emulator. CIA is still instruction-level, not per-cycle transistor/bus accurate.
Digi handling remains `$D418` write/count/automation oriented, not waveform sample
reconstruction.
