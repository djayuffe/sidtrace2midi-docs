# Glossary

| Term | Meaning |
|---|---|
| SID | Commodore 64 sound chip family, MOS 6581 / 8580. |
| PSID | SID file format for player-call style music extraction. |
| RSID | SID file format requiring more realistic C64 environment assumptions. |
| HVSC | High Voltage SID Collection. |
| Subtune | One song inside a multi-song SID file. |
| Init routine | SID player entrypoint that selects/prepares a subtune. |
| Play routine | Routine normally called every frame or timer tick. |
| 6510 port | C64 CPU I/O port at `$0000/$0001`, controls banking. |
| CIA | Complex Interface Adapter, used for timers and interrupts. |
| SidFrame | Canonical captured frame containing SID register snapshots and trigger data. |
| PPQ | MIDI pulses per quarter note. This project defaults to high-resolution `9600`. |
| Weak MIDI | Output with too few notes to be considered a successful musical conversion. |
| Salvage init | Last-resort mode that tries to continue after init problems; opt-in for batch. |
