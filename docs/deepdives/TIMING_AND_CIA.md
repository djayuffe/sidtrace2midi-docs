# Timing, CIA and IRQ Deep Dive

SID2MIDI captures register writes at instruction-level timing and maps them into MIDI ticks.

## Frame period sources

The runtime chooses period from:

1. active CIA Timer A/B when usable,
2. PSID speed metadata,
3. PAL/NTSC frame fallback.

## CIA Timer A/B model

The model tracks:

- latches
- counters
- start/stop control bits
- one-shot behavior
- ICR flags
- Timer B counting Timer A underflows when selected

This is enough for many SID players that use CIA-based playback periods. It is not a full CIA 6526 emulator.

## Advance order modes

### `pre_irq_latch`

Default. The runtime advances/latches CIA before entering the IRQ/play handler. This models the IRQ source being present when the handler runs and preserves compatibility with HVSC batch conversion.

```bash
python3 sid2midi.py tune.sid --cia-advance-mode pre_irq_latch -o tune.mid
```

### `post_call`

Experimental. The handler runs before the frame-period advance is applied. This can be useful when debugging tunes that poll/reprogram timers inside the play routine.

```bash
python3 sid2midi.py tune.sid --cia-advance-mode post_call -o tune.mid
```

## C64 cycles to MIDI ticks

C64 cycle timestamps are scaled using rational arithmetic. High PPQ keeps sub-frame changes useful in DAWs.

Recommended:

```text
--ppq 9600
--bpm 125
```

## Why some songs still fail

Some demo SIDs are not standalone music drivers. They may depend on full demo runtime, raster scheduling, sprite/badline effects or external loader state. Those should fail clearly rather than creating fake 0-note MIDI.

