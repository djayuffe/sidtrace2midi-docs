# Release naming guide

## Preferred name

**SIDTrace2MIDI**

## Recommended archive names

```text
sidtrace2midi_<topic>_release.zip
sidtrace2midi_vYYYYMMDD_release.zip
sidtrace2midi_top100_<topic>_release.zip
```

## Avoid

```text
midi2sid
sid2midi_superhuman_cpu_nmos
```

`sid2midi_superhuman_cpu_nmos` was useful as an internal working directory name,
but it is too long and CPU-centric for a release.  The public release should be
named after what the user gets: SID register tracing to MIDI.

## Directory naming

The distributable root directory in this release is:

```text
sidtrace2midi/
```

The historical internal modules remain inside that directory.
