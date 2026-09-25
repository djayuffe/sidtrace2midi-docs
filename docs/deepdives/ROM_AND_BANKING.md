# ROM and Banking Deep Dive

C64 SID players often rely on memory banking and sometimes KERNAL routines. This package includes ROM files in `roms/` for repeatable tests and RSID compatibility.

## ROM files

| File | Purpose |
|---|---|
| `roms/basic.bin` | BASIC ROM for BASIC loader/SYS context. |
| `roms/kernal.bin` | KERNAL routines and IRQ/RTI paths. |
| `roms/chargen.bin` | Character ROM banking region. |

## Search order

The runtime checks project-local `roms/` first. This makes the release self-contained.

## Strict mode

Use:

```bash
python3 sid2midi.py tune.sid --require-roms --report -o tune.mid
```

This fails loudly if ROMs are missing or invalid.

## 6510 port

C64 banking is controlled by `$0000/$0001`.

- CPU owns the port latch.
- Host memory map reads `cpu.effective_6510_port()`.
- RAM mirror is kept synchronized for compatibility.

## PSID vs RSID

### PSID

PSID is a player-call abstraction. The converter calls init/play routines and captures SID writes. Banking is still available because many files touch `$0001`, but PSID does not imply full demo runtime.

### RSID

RSID is closer to real C64 execution expectations. ROM presence and IRQ behavior matter more. Use `--require-roms` when validating RSID behavior.

