# Top-100 fast subtune probe final audit

## Trigger

A demo batch run showed `Party_Songs.sid` with 20 subtunes where the selected song and many alternate subtunes all failed normal init and then produced 0-note `salvage-init` placeholders.  The previous full-length/weak-salvage release correctly rejected those weak MIDI files, but it still spent the expensive retry stack on every alternate subtune.

## Root cause

The batch engine used the same heavy retry profile stack for the selected tune and every fallback subtune:

1. default
2. large-init
3. large-init-large-call
4. salvage-init

For multi-subtune loader/demo SIDs, each alternate subtune could cost 50-140 seconds while still producing exactly 0 notes.  That is correct as an exhaustive forensic scan, but wrong as the default Top-100 batch behavior.

## Fix

The batch engine now uses a two-stage subtune fallback:

1. The requested/seeded song still gets the full retry stack.
2. Alternate subtunes first get a cheap fixed-length probe:
   - `--subtune-probe-seconds 45`
   - `--subtune-probe-timeout 60`
   - `--subtune-probe-min-notes 20`
3. Only alternate subtunes that emit enough notes during the probe are promoted to full 600-second rendering.
4. Consecutive zero-note probes stop the alternate scan early:
   - `--subtune-zero-streak-limit 4`
5. The old slow behavior is still available with:
   - `--exhaustive-subtune-scan`

## Result

Pathological 20-subtune loader/demo files no longer burn minutes per 0-note subtune. They are marked failed honestly unless a real alternate subtune emits notes in the probe. Weak salvage files are still deleted by default and do not become future `--skip-existing` false successes.

## Honest boundary

A very unusual subtune that requires huge init budgets before emitting any note may be missed by fast probing. Use `--exhaustive-subtune-scan` for forensic conversion of a single SID where runtime cost is acceptable.
