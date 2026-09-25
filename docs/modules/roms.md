# Module: ROM handling

The package includes C64 ROM images in `roms/` so RSID and KERNAL-sensitive paths can be tested and reported.

## Files

```text
roms/basic.bin
roms/kernal.bin
roms/chargen.bin
```

## Search behavior

`sid2midi.py` searches the package `roms/` directory first and can report status with `--report`.

## Why ROMs matter

Many RSID tunes rely on KERNAL routines or standard C64 vectors. Missing ROMs can change IRQ exit behavior or loader behavior.

## Strict mode

Use:

```bash
--require-roms
```

This turns missing ROMs into hard errors rather than warnings.

## Accuracy note

The ROMs help compatibility, but the package still targets SID-register extraction rather than full C64 machine emulation.
