#!/usr/bin/env python3
"""
sid2midi.py — GENERIC, CYCLE-STAMPED SID -> MIDI converter (any .sid)
=====================================================================

Runs an instruction-level 6502/C64 SID-register capture core (CIA Timer-A rate, optional
IRQ, 2nd/3rd-SID, $D418 digi watch), runs the tune and converts the register stream
to a richly-annotated Standard MIDI File.  Pure stdlib, no dependencies.

ACCURACY
  rate : v-sync (50/60 Hz) OR the CIA Timer-A period the init programs, re-read
         every call so multi-speed / tempo changes track; RSID -> IRQ vector.
  time : every SID write is cycle-stamped; note-ONs land on the exact gate-
         trigger cycle; MIDI ticks derive from absolute cycles.
  freq : exact 16-bit frequency -> semitone + PITCH BEND remainder (vibrato).
  bit  : every register bit -> automation.

METADATA (1:1 with the SID header)
  track name, copyright, author/model/clock/format/songs/addresses/timing as
  MIDI text & marker events; per-voice instrument names.

MAXED CC PER VOICE  cutoff74 res71 pwm70 atk73 dec75 sus79 rel72  waveform20
  sync21 ring22 test23  + pitch-bend + program-change when the waveform changes.
A dedicated FILTER/MASTER track carries cutoff74 res71 mode24 route25 vol7 digi26.

Usage:
  python3 sid2midi.py tune.sid [-o out.mid] [--song N] [--seconds S] [--auto]
        [--bpm B] [--drumvoice 1-3] [--no-bend] [--no-cc] [--report]
"""
import sys, os, struct, math, argparse, json
from fractions import Fraction
from collections import namedtuple
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cpu6502 import CPU6502

PAL_CLOCK, NTSC_CLOCK = 985248.0, 1022727.0
PAL_FRAME, NTSC_FRAME = 19656, 17095
ACC = 16777216.0
SIDMODEL = {0:"unknown",1:"MOS6581",2:"MOS8580",3:"6581+8580"}

_BASEDIR = Path(__file__).resolve().parent
_ROM_CANDIDATE_DIRS = (_BASEDIR / "roms", _BASEDIR)
ROM_STATUS = {}

def _rom(name, size):
    """Load a C64 ROM from ./roms first, then beside this script.

    The fallback keeps one-file development checkouts working, while release
    packages can keep the ROMs in the explicit tools/roms layout.  A missing
    ROM returns None; the emulator then falls back to RAM-under-ROM, which is
    useful for pure PSID but is reported as non-ROM-capable for RSID/BASIC.
    """
    tried = []
    for d in _ROM_CANDIDATE_DIRS:
        p = d / name
        tried.append(str(p))
        try:
            blob = p.read_bytes()
        except OSError:
            continue
        if len(blob) >= size:
            ROM_STATUS[name] = {"present": True, "path": str(p), "size": len(blob), "required": size}
            return blob[:size]
        ROM_STATUS[name] = {"present": False, "path": str(p), "size": len(blob), "required": size, "error": "too short"}
    ROM_STATUS[name] = {"present": False, "path": None, "required": size, "tried": tried, "error": "missing"}
    return None

KERNAL=_rom("kernal.bin",8192); BASIC=_rom("basic.bin",8192); CHARGEN=_rom("chargen.bin",4096)

# --------------------------------------------------------------- SID file -----
class SidFile:
    def __init__(self, path):
        with open(path, "rb") as fh:
            d = fh.read()
        self.magic = d[:4]
        if self.magic not in (b"PSID", b"RSID"): raise ValueError("not PSID/RSID")
        (self.version, self.data_off, self.load, self.init, self.play,
         self.songs, self.start, self.speed) = struct.unpack(">HHHHHHHI", d[4:0x16])
        self.name    = d[0x16:0x36].split(b"\0")[0].decode("latin1")
        self.author  = d[0x36:0x56].split(b"\0")[0].decode("latin1")
        self.release = d[0x56:0x76].split(b"\0")[0].decode("latin1")
        self.flags   = struct.unpack(">H", d[0x76:0x78])[0] if self.version >= 2 else 0
        self.sid2off = d[0x7A] if self.version >= 3 and len(d) > 0x7A else 0
        self.sid3off = d[0x7B] if self.version >= 4 and len(d) > 0x7B else 0
        data = d[self.data_off:]
        if self.load == 0:
            self.load = data[0] | data[1] << 8; data = data[2:]
        self.data  = data
        self.rsid  = self.magic == b"RSID"
        self.basic_player = bool((self.flags >> 1) & 1)
        self.basic_sys = self._scan_basic_sys() if (self.init == 0 or self.basic_player) else None
        self.pal   = ((self.flags >> 2) & 3) != 2
        self.clock = PAL_CLOCK if self.pal else NTSC_CLOCK
        self.frame = PAL_FRAME if self.pal else NTSC_FRAME
        self.rate  = 50 if self.pal else 60
        self.model = SIDMODEL[(self.flags >> 4) & 3]
        # PSID v3/v4 stores the extra-SID base as address/16, e.g. 0x42 -> $D420.
        # Do not OR with $D420: that corrupts bases such as $D500 into $D520.
        self.sid2  = (0xD000 + (self.sid2off << 4)) if self.sid2off else 0
        self.sid3  = (0xD000 + (self.sid3off << 4)) if self.sid3off else 0

    def _scan_basic_sys(self):
        """Return the first SYS target from a tokenized BASIC loader, if present.

        Several RSID files are marked BASIC and use a tiny BASIC program such as
        `10 SYS 49152`.  A full BASIC interpreter is outside MIDI extraction
        scope, but detecting the canonical SYS stub gives those wrappers the
        same entry point that the C64 BASIC RUN command would reach.
        """
        if not self.data or not (0x0400 <= self.load < 0xA000):
            return None
        base = self.load
        off = 0
        data = self.data
        for _ in range(512):
            if off + 5 > len(data):
                return None
            nextp = data[off] | (data[off+1] << 8)
            if nextp == 0:
                return None
            line_start = off + 4
            line_end = line_start
            while line_end < len(data) and data[line_end] != 0:
                line_end += 1
            line = data[line_start:line_end]
            i = 0
            while i < len(line):
                if line[i] == 0x9E:  # BASIC SYS token
                    txt = bytes(ch for ch in line[i+1:] if ch in b"0123456789")
                    if txt:
                        try:
                            val = int(txt[:5])
                        except ValueError:
                            return None
                        if 0 <= val <= 0xFFFF:
                            return val
                i += 1
            if nextp <= base:
                return None
            off = nextp - base
        return None

    def vsync(self, song):
        return (self.speed >> min(song, 31)) & 1 == 0

# --------------------------------------------------------------- frame model ---
SidFrame = namedtuple("SidFrame", "sidA trigA trigcycA sidB trigB trigcycB sidC trigC trigcycC digi")

def make_frame(sidA, trigA, trigcycA, sidB=None, trigB=None, trigcycB=None, sidC=None, trigC=None, trigcycC=None, digi=0):
    """Create a stable, tuple-compatible frame object.

    Older code indexed frames as a 10-tuple.  SidFrame preserves that behavior
    while giving new code named fields, removing magic-index maintenance traps.
    """
    zregs = bytes(0x19)
    ztrig = (0, 0, 0)
    zcyc = (-1, -1, -1)
    return SidFrame(bytes(sidA[:0x19]), tuple(trigA), tuple(trigcycA),
                    bytes((sidB or zregs)[:0x19]), tuple(trigB or ztrig), tuple(trigcycB or zcyc),
                    bytes((sidC or zregs)[:0x19]), tuple(trigC or ztrig), tuple(trigcycC or zcyc), int(digi))

def ensure_sid_frame(frame):
    """Return a normalized SidFrame or raise TypeError for malformed input.

    Internal conversion/rendering now standardizes on SidFrame.  Legacy tuples
    are accepted only at API boundaries and converted once, eliminating mixed
    magic-index/named-field behavior in the hot path.
    """
    if isinstance(frame, SidFrame):
        return frame
    if not isinstance(frame, (tuple, list)):
        raise TypeError("frame must be SidFrame or legacy tuple/list")
    if len(frame) >= 10:
        return make_frame(frame[0], frame[1], frame[2], frame[3], frame[4], frame[5], frame[6], frame[7], frame[8], frame[9])
    if len(frame) >= 7 and isinstance(frame[6], int):
        return make_frame(frame[0], frame[1], frame[2], frame[3] if len(frame)>3 else None, frame[4] if len(frame)>4 else None, frame[5] if len(frame)>5 else None, digi=frame[6])
    if len(frame) >= 3:
        return make_frame(frame[0], frame[1], frame[2])
    raise TypeError("legacy frame has too few fields")

def normalize_frames(frames):
    return [ensure_sid_frame(f) for f in frames]

def frame_to_jsonable(frame):
    """Return one SidFrame as JSON-friendly register/trigger data.

    This is intentionally a raw register-stream export, not a synthesized audio
    model. It is useful for debugging loop detection, 2SID/3SID mapping, gate
    triggers, digi writes and CIA-timed captures.
    """
    f = ensure_sid_frame(frame)
    return {
        "sidA": list(f.sidA), "trigA": list(f.trigA), "trigcycA": list(f.trigcycA),
        "sidB": list(f.sidB), "trigB": list(f.trigB), "trigcycB": list(f.trigcycB),
        "sidC": list(f.sidC), "trigC": list(f.trigC), "trigcycC": list(f.trigcycC),
        "digi": int(f.digi),
    }

def validate_frame_timing(frames, fcyc):
    if len(fcyc) != len(frames) + 1:
        raise ValueError("fcyc length must be len(frames)+1, got %d vs %d" % (len(fcyc), len(frames)))
    last = None
    for i, c in enumerate(fcyc):
        if not isinstance(c, int):
            raise TypeError("fcyc[%d] must be int C64 cycles" % i)
        if last is not None and c < last:
            raise ValueError("fcyc must be monotonic at index %d" % i)
        last = c

def rom_report_lines():
    lines = []
    for name in ("basic.bin", "kernal.bin", "chargen.bin"):
        st = ROM_STATUS.get(name, {"present": False})
        if st.get("present"):
            lines.append(f"ROM {name}: OK {st.get('path')} ({st.get('size')} bytes)")
        else:
            tried = ", ".join(st.get("tried", []) or [])
            lines.append(f"ROM {name}: MISSING/INVALID; tried: {tried}")
    return lines

# ---------------------------------------------------------------- C64 env -----
class C64:
    def __init__(self, sid2base=0, sid3base=0, psid_mode=False, force_irq_if_masked=True, cia_advance_mode="pre_irq_latch"):
        self.psid_mode = bool(psid_mode)
        self.force_irq_if_masked = bool(force_irq_if_masked)
        self.cia_advance_mode = str(cia_advance_mode)
        if self.cia_advance_mode not in ("pre_irq_latch", "post_call"):
            raise ValueError("cia_advance_mode must be pre_irq_latch or post_call")
        self.irq_masked_count = 0
        self.ram = bytearray(65536); self.sid = bytearray(0x20); self.sidB = bytearray(0x20); self.sidC = bytearray(0x20)
        self.ram[0x00]=0x2F; self.ram[0x01]=0x37
        self.kernal = KERNAL; self.basic = BASIC; self.chargen = CHARGEN
        self._rnd = 0x1234; self._ras = 0
        self.sid2base = sid2base
        self.sid3base = sid3base
        self.ctrl  = {0xD404:0, 0xD40B:1, 0xD412:2}
        self.ctrlB = {sid2base+4:0, sid2base+0xB:1, sid2base+0x12:2} if sid2base else {}
        self.ctrlC = {sid3base+4:0, sid3base+0xB:1, sid3base+0x12:2} if sid3base else {}
        self.gate=[0,0,0]; self.trig=[0,0,0]; self.trigcyc=[-1,-1,-1]
        self.gateB=[0,0,0]; self.trigB=[0,0,0]; self.trigcycB=[-1,-1,-1]
        self.gateC=[0,0,0]; self.trigC=[0,0,0]; self.trigcycC=[-1,-1,-1]
        self.digi = 0
        self.ta_latch=0; self.ta_count=0; self.tb_latch=0; self.tb_count=0; self.icr_mask=0; self.icr_data=0   # CIA1 timers A/B
        self.cra=0; self.crb=0                                               # CIA control registers
        self.vic_irq=0; self.vic_mask=0; self.vic_raster_cmp=0               # VIC raster IRQ
        self.last_call_reason="reset"
        self.last_call_cycles=0
        self.last_call_ins=0
        self.cpu = CPU6502(self.read, self.write, intercept_6510_port=True)
        self.cpu.write_6510_port(0x0000, 0x2F)
        self.cpu.write_6510_port(0x0001, 0x37)

    def mem_port(self):
        """Effective 6510 processor-port value used for C64 banking.

        The CPU owns the $0000/$0001 latch.  The RAM mirror is still maintained
        for diagnostics and for code that peeks below the CPU wrapper, but bank
        selection always consults CPU6502.effective_6510_port() to avoid CPU/C64
        split-brain.
        """
        if hasattr(self, "cpu") and hasattr(self.cpu, "effective_6510_port"):
            return self.cpu.effective_6510_port() | 0xE0
        ddr = self.ram[0] | 0xE0
        data = self.ram[1] | 0xE0
        return ((data & ddr) | (~ddr & 0xFF)) & 0xFF
    def _io_read(self, a):
        if self.sid2base and self.sid2base <= a < self.sid2base + 0x20:
            return self.sidB[a - self.sid2base]
        if self.sid3base and self.sid3base <= a < self.sid3base + 0x20:
            return self.sidC[a - self.sid3base]
        if 0xD400 <= a <= 0xD7FF:
            r=(a-0xD400)&0x1F
            if r==0x1B: self._rnd=(self._rnd*1103515245+12345)&0xFFFFFFFF; return (self._rnd>>16)&0xFF
            if r==0x1C: return 0
            return self.sid[r]
        if a==0xD012: self._ras=(self._ras+1)&0xFF; return self._ras
        if a==0xD011: return 0x1B
        if a==0xD019: return self.vic_irq | (0x80 if (self.vic_irq & self.vic_mask) else 0)
        if a==0xD01A: return self.vic_mask
        if 0xDC00 <= a <= 0xDCFF:                       # CIA #1
            r=a&0x0F
            if r==0x04: return self.ta_count & 0xFF
            if r==0x05: return (self.ta_count>>8) & 0xFF
            if r==0x06: return self.tb_count & 0xFF
            if r==0x07: return (self.tb_count>>8) & 0xFF
            if r==0x0D:                                 # ICR: read clears, bit7=IRQ
                v=self.icr_data | (0x80 if (self.icr_data & self.icr_mask) else 0)
                self.icr_data=0; return v
            return 0xFF
        return 0xFF                                     # CIA #2 / other I/O
    def read(self, a):
        a &= 0xFFFF
        if a == 0x0000 or a == 0x0001:
            return self.cpu.read_6510_port(a) if hasattr(self, "cpu") else self.ram[a]
        # PSID is a player-call abstraction, not a full C64 boot environment.
        # The SID payload must be visible as RAM even when it lives under BASIC
        # or KERNAL ROM (e.g. many Hubbard/Galway players at $Axxx/$Fxxx).
        # Keep I/O visible for SID/CIA/VIC register capture, but do not overlay
        # BASIC/KERNAL/CHARGEN ROM over the player code.
        if self.psid_mode:
            if 0xD000 <= a <= 0xDFFF:
                return self._io_read(a)
            return self.ram[a]
        if a < 0xA000: return self.ram[a]               # banked memory map ($01)
        p=self.mem_port()
        if a >= 0xE000:                                 # KERNAL
            return self.kernal[a-0xE000] if (p&2 and self.kernal) else self.ram[a]
        if a >= 0xD000:                                 # I/O / CHARGEN / RAM
            if (p&4) and (p&3): return self._io_read(a)
            if p&3: return self.chargen[a-0xD000] if self.chargen else self.ram[a]
            return self.ram[a]
        if 0xA000 <= a <= 0xBFFF and (p&3)==3 and self.basic:
            return self.basic[a-0xA000]
        return self.ram[a]
    def write(self, a, v):
        a &= 0xFFFF
        v&=0xFF
        if a == 0x0000 or a == 0x0001:
            if hasattr(self, "cpu"):
                self.cpu.write_6510_port(a, v)
            self.ram[a] = v
            return
        p = self.mem_port()
        io = (0xD000 <= a <= 0xDFFF) and (self.psid_mode or ((p&4) and (p&3)))
        if io:
            if self.sid2base and self.sid2base <= a < self.sid2base+0x20:
                r=a-self.sid2base; self.sidB[r]=v
                if a in self.ctrlB:
                    vi=self.ctrlB[a]; ng=v&1
                    if ng and not self.gateB[vi]:
                        self.trigB[vi]=1
                        if self.trigcycB[vi]<0: self.trigcycB[vi]=self.cpu.cycles
                    self.gateB[vi]=ng
            elif self.sid3base and self.sid3base <= a < self.sid3base+0x20:
                r=a-self.sid3base; self.sidC[r]=v
                if a in self.ctrlC:
                    vi=self.ctrlC[a]; ng=v&1
                    if ng and not self.gateC[vi]:
                        self.trigC[vi]=1
                        if self.trigcycC[vi]<0: self.trigcycC[vi]=self.cpu.cycles
                    self.gateC[vi]=ng
            elif 0xD400 <= a <= 0xD41F:
                r=(a-0xD400)&0x1F; self.sid[r]=v
                if r==0x18: self.digi+=1
                if a in self.ctrl:
                    vi=self.ctrl[a]; ng=v&1
                    if ng and not self.gate[vi]:
                        self.trig[vi]=1
                        if self.trigcyc[vi]<0: self.trigcyc[vi]=self.cpu.cycles
                    self.gate[vi]=ng
            elif 0xDC00 <= a <= 0xDCFF:                 # CIA #1 timer A + IRQ control
                r=a&0x0F
                if   r==0x04:
                    self.ta_latch=(self.ta_latch&0xFF00)|v
                    if not (self.cra & 1): self.ta_count=self.ta_latch
                elif r==0x05:
                    self.ta_latch=(self.ta_latch&0x00FF)|(v<<8)
                    if not (self.cra & 1): self.ta_count=self.ta_latch
                elif r==0x06:
                    self.tb_latch=(self.tb_latch&0xFF00)|v
                    if not (self.crb & 1): self.tb_count=self.tb_latch
                elif r==0x07:
                    self.tb_latch=(self.tb_latch&0x00FF)|(v<<8)
                    if not (self.crb & 1): self.tb_count=self.tb_latch
                elif r==0x0D: self.icr_mask=(self.icr_mask|(v&0x1F)) if v&0x80 else (self.icr_mask&~(v&0x1F))
                elif r==0x0E:
                    old = self.cra; self.cra=v
                    if v&0x10 or ((v&1) and not (old&1) and self.ta_count<=0): self._cia_reload_timer("A")
                elif r==0x0F:
                    old = self.crb; self.crb=v
                    if v&0x10 or ((v&1) and not (old&1) and self.tb_count<=0): self._cia_reload_timer("B")
            elif a==0xD011:
                self.vic_raster_cmp = (self.vic_raster_cmp & 0xFF) | ((v & 0x80) << 1)
            elif a==0xD012:
                self.vic_raster_cmp = (self.vic_raster_cmp & 0x100) | v
            elif a==0xD019: self.vic_irq &= (~v)&0x0F   # VIC IRQ ack
            elif a==0xD01A: self.vic_mask = v&0x0F      # VIC IRQ enable
        self.ram[a]=v
    def _cia_timer_enabled(self, timer):
        if timer == "A":
            return bool(self.cra & 0x01)
        return bool(self.crb & 0x01)

    def _cia_reload_timer(self, timer):
        if timer == "A":
            self.ta_count = self.ta_latch or 0x10000
        else:
            self.tb_count = self.tb_latch or 0x10000

    def _cia_timer_period_value(self, timer):
        latch = self.ta_latch if timer == "A" else self.tb_latch
        count = self.ta_count if timer == "A" else self.tb_count
        val = count or latch
        return int(val) if val else 0

    def advance_cia(self, cycles):
        """Advance CIA timers by an instruction-call span.

        This remains instruction-level, not PHI2 bus-cycle exact, but it models
        start/stop, reload, one-shot and Timer-B count-underflow mode well enough
        for SID player period selection and IRQ flag behavior.
        """
        cycles = max(0, int(cycles))
        under_a = False
        if self.cra & 0x01:
            if self.ta_count <= 0:
                self._cia_reload_timer("A")
            self.ta_count -= cycles
            if self.ta_count <= 0:
                under_a = True
                self.icr_data |= 1
                if self.cra & 0x08:  # one-shot
                    self.cra &= ~0x01
                    self.ta_count = 0
                else:
                    latch = self.ta_latch or 0x10000
                    self.ta_count = ((self.ta_count % latch) or latch)
        # Timer B can count PHI2 cycles (CRB bit5 clear) or Timer-A underflows (bit5 set).
        if self.crb & 0x01:
            if self.tb_count <= 0:
                self._cia_reload_timer("B")
            dec = 1 if ((self.crb & 0x20) and under_a) else (cycles if not (self.crb & 0x20) else 0)
            if dec:
                self.tb_count -= dec
                if self.tb_count <= 0:
                    self.icr_data |= 2
                    if self.crb & 0x08:
                        self.crb &= ~0x01
                        self.tb_count = 0
                    else:
                        latch = self.tb_latch or 0x10000
                        self.tb_count = ((self.tb_count % latch) or latch)

    def load_sid(self, sid):
        # Establish the C64 power-on banking port before placing the payload.
        # Some BASIC/RSID stubs peek $0001 very early; avoid any transient
        # split-brain between RAM mirror and CPU-owned 6510 latch.
        self.ram[0x00]=0x2F; self.ram[0x01]=0x37
        if hasattr(self, "cpu"):
            self.cpu.write_6510_port(0x0000, 0x2F)
            self.cpu.write_6510_port(0x0001, 0x37)
        if sid.load + len(sid.data) > 0x10000:
            raise ValueError("SID payload overflows C64 memory: load $%04X len %d" % (sid.load, len(sid.data)))
        self.ram[sid.load:sid.load+len(sid.data)]=sid.data
        self.kernal=KERNAL; self.basic=BASIC; self.chargen=CHARGEN
    def init(self, sid, song, max_ins=1_000_000):
        entry = sid.init or sid.basic_sys
        if not entry:
            # PSID is a host-call abstraction.  A few old/odd PSIDs expose no
            # init entry but do expose a play entry; treating init as a no-op is
            # more useful than failing before any capture can happen.  RSID and
            # BASIC files still require a real entry/SYS because they depend on
            # C64 execution semantics.
            if (not sid.rsid) and sid.play:
                self.last_call_reason="no_init_psid"
                self.last_call_cycles=0
                self.last_call_ins=0
                return
            raise RuntimeError("SID has init=$0000 and no simple BASIC SYS entry was found")
        self.cpu.call(entry, a=song, max_ins=max_ins)
        self.last_call_reason=self.cpu.last_stop_reason
        self.last_call_cycles=self.cpu.cycles
        self.last_call_ins=self.cpu.last_instruction_count
    def irq_target(self):
        """Return the IRQ vector/exit convention for the *current* C64 bank state.

        RSID players are allowed to change the processor-port memory map at
        $0001 while they run.  Freezing this decision after init is subtly
        wrong: with KERNAL visible, the normal C64 IRQ path vectors through
        CINV ($0314) and exits through $EA31; with KERNAL hidden, a direct
        hardware vector at $FFFE/$FFFF is the only sensible path.
        """
        kernal_visible = bool((self.mem_port() & 0x02) and self.kernal)
        return (0x0314, True) if kernal_visible else (0xFFFE, False)

    def prepare_cia_irq_for_elapsed(self, cycles):
        """Latch CIA IRQ state for the elapsed interval before entering IRQ.

        This keeps the important C64 ordering explicit: by the time an IRQ
        handler starts, the CIA interrupt flag is visible.  The model remains
        instruction-level; dynamic timer writes inside the handler affect the
        next logical interval chosen by run_tune().
        """
        self.advance_cia(cycles)
        if not (self.icr_data & 0x03):
            self.icr_data |= 1

    def current_timer_period(self, sid, song, irq):
        """Return the next play/IRQ period in C64 PHI2 cycles.

        Exposed as a method so Timer-A/Timer-B/vsync period selection is
        testable outside run_tune().  Timer A is the normal SID player source;
        Timer B is used by some RSID/PSID drivers.  If no CIA source is
        armed/programmed, fall back to the video frame period.
        """
        if not irq and sid.vsync(song):
            return sid.frame
        ta = self._cia_timer_period_value("A")
        tb = self._cia_timer_period_value("B")
        # Prefer timers that are actually interrupt-masked or actively running.
        ta_enabled = bool((self.icr_mask & 1) or (self.cra & 1))
        tb_enabled = bool((self.icr_mask & 2) or (self.crb & 1))
        if ta_enabled and 16 < ta < 0x20000:
            return ta + 1
        if tb_enabled and 16 < tb < 0x20000:
            return tb + 1
        # Some PSID drivers only program latches and expect host playback at CIA rate.
        if ta and 16 < ta < 0x20000 and not sid.vsync(song):
            return ta + 1
        if tb and 16 < tb < 0x20000 and not sid.vsync(song):
            return tb + 1
        return sid.frame

    def step_call(self, sid, irq, max_ins=250_000, song=0, elapsed_cycles=None):
        self.trig=[0,0,0]; self.trigcyc=[-1,-1,-1]
        self.trigB=[0,0,0]; self.trigcycB=[-1,-1,-1]
        self.trigC=[0,0,0]; self.trigcycC=[-1,-1,-1]; self.digi=0
        if irq:
            ivec, kernal = self.irq_target()
            # Advance CIA by the elapsed period since the previous logical play
            # tick.  run_tune passes the pre-call period explicitly so timer
            # reprogramming inside this handler affects the next frame, not the
            # interval that already elapsed.
            elapsed = self.current_timer_period(sid, song, irq) if elapsed_cycles is None else elapsed_cycles
            if self.cia_advance_mode == "pre_irq_latch":
                self.prepare_cia_irq_for_elapsed(elapsed)
            else:
                # Compatibility/testing mode: enter handler first, then elapse
                # the frame after the CPU call below. ICR is still raised so
                # handlers polling $DC0D see an interrupt source.
                if not (self.icr_data & 0x03):
                    self.icr_data |= 1
            self.vic_irq |= 1                                    # & VIC raster (whichever the handler checks)
            if kernal and self.cpu.I:
                self.irq_masked_count += 1
                if self.force_irq_if_masked:
                    self.cpu.I = 0
                else:
                    self.last_call_reason="irq_masked"
                    self.last_call_cycles=0
                    self.last_call_ins=0
                    return make_frame(self.sid, self.trig, self.trigcyc, self.sidB, self.trigB, self.trigcycB, self.sidC, self.trigC, self.trigcycC, self.digi)
            self.cpu.irq(ivec, kernal, max_ins=max_ins)
            if self.cia_advance_mode == "post_call":
                self.advance_cia(elapsed)
        else:
            self.cpu.call(sid.play, max_ins=max_ins)
        self.last_call_reason=self.cpu.last_stop_reason
        self.last_call_cycles=self.cpu.cycles
        self.last_call_ins=self.cpu.last_instruction_count
        return make_frame(self.sid, self.trig, self.trigcyc, self.sidB, self.trigB, self.trigcycB, self.sidC, self.trigC, self.trigcycC, self.digi)

# ---------------------------------------------------------- MIDI writer --------
def vlq(n):
    o=bytearray([n&0x7f]); n>>=7
    while n: o.insert(0,(n&0x7f)|0x80); n>>=7
    return bytes(o)
class Trk:
    # Same-tick ordering is explicit and stable:
    # meta -> program -> CC/bend -> note-off -> note-on.
    # This prevents same-tick retriggers from rendering as On-before-Off.
    P_META = 0
    P_PROG = 1
    P_CTRL = 2
    P_OFF  = 3
    P_ON   = 4

    def __init__(self, name=""):
        self.ev=[]
        self._seq=0
        if name:
            self.meta(0,0x03,name.encode())

    def _a(self,t,b,p=1):
        self.ev.append((max(0,int(t)), int(p), self._seq, bytes(b)))
        self._seq += 1

    def meta(self,t,k,d):
        if isinstance(d,str): d=d.encode("latin1")
        self._a(t, bytes([0xFF,k]) + vlq(len(d)) + bytes(d), self.P_META)
    def tempo(self,t,us): self.meta(t,0x51,bytes([(us>>16)&255,(us>>8)&255,us&255]))
    def marker(self,t,s): self.meta(t,0x06,s)
    def cc(self,t,ch,n,v): self._a(t,[0xB0|ch,n&0x7f,max(0,min(127,int(v)))],self.P_CTRL)
    def prog(self,t,ch,p): self._a(t,[0xC0|ch,p&0x7f],self.P_PROG)
    def bend(self,t,ch,val):
        val=max(0,min(16383,val)); self._a(t,[0xE0|ch,val&0x7f,(val>>7)&0x7f],self.P_CTRL)
    def on(self,t,ch,n,v): self._a(t,[0x90|ch,n&0x7f,max(1,min(127,v))],self.P_ON)
    def off(self,t,ch,n): self._a(t,[0x80|ch,n&0x7f,0],self.P_OFF)
    def render(self):
        ev=sorted(self.ev,key=lambda e:(e[0],e[1],e[2])); d=bytearray(); last=0
        for t,_,__,b in ev:
            d+=vlq(t-last)+b; last=t
        d+=vlq(0)+bytes([0xFF,0x2F,0x00]); return b"MTrk"+struct.pack(">I",len(d))+bytes(d)
def write_smf(path,ppq,trks):
    with open(path,"wb") as fh:
        fh.write(b"MThd"+struct.pack(">IHHH",6,1,len(trks),ppq)+b"".join(t.render() for t in trks))

# ----------------------------------------------------- helpers / detection ----
def hz_exact(hz): return 69+12*math.log2(hz/440.0) if hz>0 else None
def wave_code(w): return (1 if w&0x10 else 0)|(2 if w&0x20 else 0)|(4 if w&0x40 else 0)|(8 if w&0x80 else 0)
def wave_prog(w):
    if w&0x80 and not w&0x70: return None      # noise
    if w&0x40 and w&0x20: return 81            # pulse+saw
    if w&0x40: return 80                       # pulse  -> square lead
    if w&0x20: return 81                       # saw    -> saw lead
    if w&0x10: return 89                       # tri    -> warm pad
    return 80

class Env:
    """reSID-accurate SID ADSR envelope generator (stepped per frame)."""
    RATE=[9,32,63,95,149,220,267,313,392,977,1954,3126,3907,11719,15625,31250]
    EXP ={0xFF:1,0x5D:2,0x36:4,0x1A:8,0x0E:16,0x06:30,0x00:1}
    def __init__(self):
        self.env=0; self.state=2; self.rc=0; self.ec=0; self.ep=1
        self.hold=True; self.gate=0; self.ad=0; self.sr=0
    def trigger(self): self.state=0; self.hold=False           # gate 0->1: start attack
    def set_gate(self,g):
        if g and not self.gate: self.trigger()
        elif not g and self.gate: self.state=2                 # gate 1->0: release
        self.gate=g
    def _rate(self):
        return self.RATE[self.ad>>4] if self.state==0 else \
               self.RATE[self.ad&15] if self.state==1 else self.RATE[self.sr&15]
    def _step(self):
        if self.state==0:
            self.env=(self.env+1)&0xFF
            if self.env==0xFF: self.state=1
        else:
            self.ec+=1
            if self.ec>=self.ep:
                self.ec=0
                if not self.hold and self.env>0: self.env-=1
        if self.env in self.EXP: self.ep=self.EXP[self.env]
        if self.env==0: self.hold=True
    def advance(self,cycles):
        sus=(self.sr>>4)*0x11
        if (self.state==1 and self.env<=sus) or (self.env==0 and self.state==2):
            return                                              # frozen at sustain / silent
        rp=self._rate(); self.rc+=cycles; g=0
        while self.rc>=rp and g<6000:
            self.rc-=rp; self._step(); rp=self._rate(); g+=1
            sus=(self.sr>>4)*0x11
            if (self.state==1 and self.env<=sus) or (self.env==0 and self.state==2): break

def compute_env(frames, getregs, gettrig, fcyc):
    out=[[],[],[]]; es=[Env(),Env(),Env()]
    for f in range(len(frames)):
        regs=getregs(f); trig=gettrig(f); pf=fcyc[f+1]-fcyc[f]
        for v in range(3):
            o=7*v; e=es[v]; e.ad=regs[o+5]; e.sr=regs[o+6]
            if trig[v]: e.trigger()
            e.set_gate(regs[o+4]&1); e.advance(pf); out[v].append(e.env)
    return out

def _coerce_regs(obj):
    if isinstance(obj, (bytes, bytearray)):
        return bytes(obj[:0x19]).ljust(0x19, b"\0")
    if obj is None:
        return bytes(0x19)
    vals = list(obj)[:0x19]
    return bytes(int(x) & 0xFF for x in vals).ljust(0x19, b"\0")

def _frame_regs(frame, chip=0):
    """Return the 25 captured SID register bytes for chip 0/1/2.

    Prefer named SidFrame attributes and fall back to the historical 10-tuple
    layout only for compatibility.  Type errors are not swallowed here: malformed
    frames should fail tests instead of silently producing wrong MIDI.
    """
    attr = ("sidA", "sidB", "sidC")[chip]
    if hasattr(frame, attr):
        return _coerce_regs(getattr(frame, attr))
    idx = 0 if chip == 0 else 3 if chip == 1 else 6
    if not isinstance(frame, (tuple, list)):
        raise TypeError("frame must be SidFrame or legacy tuple/list")
    if len(frame) <= idx:
        raise ValueError("legacy frame missing SID chip %d register slot" % chip)
    return _coerce_regs(frame[idx])

def _frame_trig(frame, chip=0):
    attr = ("trigA", "trigB", "trigC")[chip]
    if hasattr(frame, attr):
        t = getattr(frame, attr)
    else:
        idx = 1 if chip == 0 else 4 if chip == 1 else 7
        if not isinstance(frame, (tuple, list)):
            raise TypeError("frame must be SidFrame or legacy tuple/list")
        if len(frame) <= idx:
            raise ValueError("legacy frame missing SID chip %d trigger slot" % chip)
        t = frame[idx]
    if isinstance(t, (tuple, list)):
        vals = [1 if bool(x) else 0 for x in list(t)[:3]]
        return tuple(vals + [0] * (3 - len(vals)))
    return (0, 0, 0)

def _frame_trigcyc(frame, chip=0):
    attr = ("trigcycA", "trigcycB", "trigcycC")[chip]
    if hasattr(frame, attr):
        t = getattr(frame, attr)
    else:
        idx = 2 if chip == 0 else 5 if chip == 1 else 8
        if not isinstance(frame, (tuple, list)):
            raise TypeError("frame must be SidFrame or legacy tuple/list")
        if len(frame) <= idx:
            raise ValueError("legacy frame missing SID chip %d trigger-cycle slot" % chip)
        t = frame[idx]
    if isinstance(t, (tuple, list)):
        vals = [int(x) for x in list(t)[:3]]
        return tuple(vals + [-1] * (3 - len(vals)))
    return (-1, -1, -1)

def _frame_digi(frame):
    if hasattr(frame, "digi"):
        return int(frame.digi)
    if isinstance(frame, (tuple, list)) and len(frame) >= 10:
        return int(frame[9])
    if isinstance(frame, (tuple, list)) and len(frame) > 6 and isinstance(frame[6], int):
        return int(frame[6])
    return 0

def find_loop(frames, rate, min_seconds=90.0, confirm_windows=2):
    """Return a conservative loop period in frames, or None.

    The detector normalizes frames to SidFrame, includes primary/2SID/3SID
    state in the signature, and chooses the best-evidenced period rather than
    blindly accepting the earliest tail match.
    """
    frames = normalize_frames(frames)
    N=len(frames)
    if N < rate*10:
        return None
    try:
        min_p = max(rate*6, int(float(min_seconds) * rate))
    except Exception:
        min_p = rate*60

    def sig(frame):
        r = _frame_regs(frame, 0)
        rb = _frame_regs(frame, 1)
        rc = _frame_regs(frame, 2)
        return (
            r[0], r[1], r[7], r[8], r[14], r[15],
            r[4] & 1, r[11] & 1, r[18] & 1,
            r[4] & 0xFE, r[11] & 0xFE, r[18] & 0xFE,
            _frame_trig(frame, 0),
            rb[0], rb[1], rb[7], rb[8], rb[14], rb[15], rb[4], rb[11], rb[18], _frame_trig(frame, 1),
            rc[0], rc[1], rc[7], rc[8], rc[14], rc[15], rc[4], rc[11], rc[18], _frame_trig(frame, 2),
            r[21], r[22], r[23], r[24] & 0x0F,
            _frame_digi(frame) > 4,
        )

    H=[hash(sig(f)) for f in frames]
    win = min(512, max(rate * 4, N // 8))
    if min_p >= N - win:
        return None

    def same_tail(period: int, multiplier: int = 1) -> bool:
        base = N - 1 - period * multiplier
        if base - (win - 1) < 0:
            return False
        return all(H[N - 1 - j] == H[base - j] for j in range(win))

    max_confirmed_p = (N - win) // 2 if confirm_windows > 1 and N >= (2 * min_p + win) else (N - win)
    best = None
    for P in range(min_p, N - win):
        if P > max_confirmed_p:
            continue
        if not same_tail(P, 1):
            continue
        copies = 1
        k = 2
        while (N - 1 - (k * P) - (win - 1)) >= 0 and same_tail(P, k):
            copies += 1
            k += 1
        if confirm_windows > 1 and copies < min(confirm_windows, 2):
            continue
        # Prefer strongest evidence first; tie-break to shorter, musically useful loop.
        score = (copies, -P)
        if best is None or score > best[0]:
            best = (score, P)
    return best[1] if best else None

# ------------------------------------------------------------ conversion ------
def tick_scale(ppq, bpm, clock):
    """Return an integer-rational C64-cycle -> MIDI-tick converter.

    MIDI time must be a delta-tick stream, but SID writes are timestamped in
    absolute C64 PHI2 cycles.  This converter intentionally keeps BPM as only
    a DAW grid label: with the matching MIDI tempo event, tick(cycle) maps back
    to real seconds as closely as Standard MIDI permits.  The rational form
    avoids float drift and keeps event order deterministic across Python builds.
    """
    bpm_f = Fraction(str(bpm)).limit_denominator(1_000_000)
    clock_i = int(round(clock))
    scale = Fraction(int(ppq)) * bpm_f / (60 * clock_i)
    num, den = scale.numerator, scale.denominator
    def tick(cycles):
        # Keep cycle->tick conversion rational as long as possible.  SID frame
        # boundaries are integer PHI2 cycles, but trigger offsets may come from
        # CPU cycle counters; Fraction avoids float drift if callers pass one.
        c = Fraction(cycles).limit_denominator(1_000_000)
        return int((c * num * 2 + den) // (2 * den))
    return tick, num, den


def grid_bpm_from_c64(rate, frames_per_row=6, rows_per_beat=4):
    return float(rate) * 60.0 / max(1.0, float(frames_per_row) * float(rows_per_beat))


def convert(sid, frames, fcyc, bpm, drum_voice=None, bend=True, do_cc=True, loopP=None, ppq=9600):
    frames = normalize_frames(frames)
    validate_frame_timing(frames, fcyc)
    PPQ=int(ppq); tick, scale_num, scale_den = tick_scale(PPQ, bpm, sid.clock)
    pf=lambda f: fcyc[f+1]-fcyc[f]                  # this frame's duration in cycles
    # ---- metadata track ----
    meta=Trk(sid.name or "SID tune")
    tempo_us=max(1, int(round(60_000_000/float(bpm))))
    meta.tempo(0,tempo_us); meta.meta(0,0x58,bytes([4,2,24,8]))
    if sid.release: meta.meta(0,0x02, sid.release)                 # copyright
    for line in ("name: %s"%sid.name, "author: %s"%sid.author, "released: %s"%sid.release,
                 "chip: %s  %s %dHz"%(sid.model,"PAL" if sid.pal else "NTSC",sid.rate),
                 "format: %s v%d  songs %d"%(sid.magic.decode(),sid.version,sid.songs),
                 "init $%04X  play $%04X  load $%04X"%(sid.init,sid.play,sid.load),
                 "timing: absolute C64 PHI2 cycles -> MIDI ticks, ppq=%d, bpm-grid=%g"%(PPQ,bpm),
                 "cycle_to_tick: round(cycles * %d / %d)"%(scale_num,scale_den),
                 "converted by sid2midi.py (cycle-stamped instruction-level)"):
        meta.meta(0,0x01,line)
    meta.marker(0,"song start")
    if loopP: meta.marker(tick(fcyc[loopP]),"loop")
    # ---- voice + drum + filter/master tracks ----
    def make_voices(n, ch0, label):
        ts=[Trk("%s V%d"%(label,i+1)) for i in range(n)]
        for i,tr in enumerate(ts):
            tr.prog(0,ch0+i,[38,81,80,38,81,80][i]); tr.cc(0,ch0+i,7,100)
            tr.meta(0,0x04,"SID %s voice %d"%(label,i+1))
        return ts
    vtr=make_voices(3,0,"A"); dtr=Trk("Drums"); dtr.cc(0,9,7,110)
    flt=Trk("Filter/Master"); flt.cc(0,3,7,110)
    sid2 = bool(sid.sid2) and bool(frames) and any(any(_frame_regs(f, 1)) for f in frames)
    sid3 = bool(getattr(sid, "sid3", 0)) and bool(frames) and any(any(_frame_regs(f, 2)) for f in frames)
    vtrB=make_voices(3,4,"B") if sid2 else []
    vtrC=make_voices(3,10,"C") if sid3 else []

    def render_sid(tracks, getregs, gettrig, gettcyc, ch0, is_main, envs):
        cur=[None]*3; basev=[0]*3; lastcc=[{} for _ in range(3)]
        lastbend=[8192]*3; lastprog=[None]*3; N=len(frames)
        def velocity(v,f,sr,master):                    # from emulated envelope
            peak=max(envs[v][f:min(f+4,N)] or [envs[v][f]])
            load=0.55*peak + 0.45*((sr>>4)*0x11)
            return max(8, min(127, int(18 + (load/255.0)*((master+1)/16.0)*108)))
        for f in range(len(frames)):
            regs=getregs(f); trig=gettrig(f); tcyc=gettcyc(f); cyc0=fcyc[f]; mvol=regs[24]&15
            for v in range(3):
                tr=tracks[v]; ch=ch0+v; o=7*v
                freq=regs[o]|regs[o+1]<<8; ctrl=regs[o+4]; gate=ctrl&1
                wave=ctrl&0xF0; test=ctrl&8; sync=ctrl&2; ring=ctrl&4
                pw=regs[o+2]|(regs[o+3]&0x0F)<<8; ad=regs[o+5]; sr=regs[o+6]
                noise=(wave&0x80) and not (wave&0x70)
                # perceived pitch: hard sync -> fundamental is the SYNC SOURCE voice
                # (osc resets at the master's rate); ring -> carrier (the melodic intent).
                src=(v+2)%3; sfreq=regs[7*src]|regs[7*src+1]<<8
                pfreq = sfreq if (sync and sfreq) else freq
                hz=pfreq*sid.clock/ACC
                tt=tick(cyc0+(tcyc[v] if tcyc[v]>=0 else 0))
                if do_cc:
                    for num,val in ((71,(regs[23]>>4)*8),(70,pw>>5),(73,(ad>>4)*8),(75,(ad&15)*8),
                                    (79,(sr>>4)*8),(72,(sr&15)*8),(20,wave_code(wave)*8),
                                    (21,127 if sync else 0),(22,127 if ring else 0),(23,127 if test else 0)):
                        if lastcc[v].get(num)!=val: tr.cc(tick(cyc0),ch,num,val); lastcc[v][num]=val
                    pg=13 if ring else wave_prog(wave)    # ring-mod -> tubular bells (metallic)
                    if pg is not None and pg!=lastprog[v]: tr.prog(tick(cyc0),ch,pg); lastprog[v]=pg
                if is_main and (v==drum_voice or (drum_voice is None and noise)):
                    if trig[v]:
                        dn=(42 if hz>1800 else 39 if hz>400 else 38) if noise else (36 if hz<400 else 38)
                        dtr.on(tt,9,dn,108); dtr.off(tt+max(1,tick(pf(f))//2),9,dn)
                    continue
                ex=hz_exact(hz) if (gate and not test and wave and not noise) else None
                note=int(round(ex)) if ex is not None else None
                def setbend(tk,b):
                    b=max(0,min(16383,b))
                    if b!=lastbend[v]: tr.bend(tk,ch,b); lastbend[v]=b
                if note is not None and (trig[v] or note!=cur[v]):
                    if cur[v] is not None: tr.off(tt,ch,cur[v])
                    tr.on(tt,ch,note,velocity(v,f,sr,mvol)); cur[v]=note; basev[v]=note
                    if bend: setbend(tt,8192+int(round((ex-note)*8192/2.0)))
                elif note is None and cur[v] is not None:
                    tr.off(tt,ch,cur[v]); cur[v]=None
                elif note is not None and bend:
                    setbend(tick(cyc0),8192+int(round((ex-basev[v])*8192/2.0)))
        end=tick(fcyc[len(frames)])
        for v in range(3):
            if cur[v] is not None: tracks[v].off(end,ch0+v,cur[v])

    # main SID + (optional) 2nd SID — envelopes drive note velocity
    envA=compute_env(frames, lambda f:_frame_regs(frames[f],0), lambda f:_frame_trig(frames[f],0), fcyc)
    render_sid(vtr, lambda f:_frame_regs(frames[f],0), lambda f:_frame_trig(frames[f],0), lambda f:_frame_trigcyc(frames[f],0), 0, True, envA)
    if sid2:
        envB=compute_env(frames, lambda f:_frame_regs(frames[f],1), lambda f:_frame_trig(frames[f],1), fcyc)
        render_sid(vtrB, lambda f:_frame_regs(frames[f],1), lambda f:_frame_trig(frames[f],1), lambda f:_frame_trigcyc(frames[f],1), 4, False, envB)
    if sid3:
        envC=compute_env(frames, lambda f:_frame_regs(frames[f],2), lambda f:_frame_trig(frames[f],2), fcyc)
        render_sid(vtrC, lambda f:_frame_regs(frames[f],2), lambda f:_frame_trig(frames[f],2), lambda f:_frame_trigcyc(frames[f],2), 10, False, envC)
    # global filter + master + digi automation on its own track
    if do_cc:
        last={}
        for f in range(len(frames)):
            regs=_frame_regs(frames[f],0); t=tick(fcyc[f])
            cut=((regs[22]<<3)|(regs[21]&7))>>3
            for num,val in ((74,cut),(71,(regs[23]>>4)*8),(24,((regs[24]>>4)&7)*16),
                            (25,(regs[23]&7)*16),(7,(regs[24]&15)*8),(26,_frame_digi(frames[f])&127)):
                if last.get(num)!=val: flt.cc(t,3,num,val); last[num]=val
    return PPQ, [meta]+vtr+vtrB+vtrC+[dtr,flt]

# --------------------------------------------------------------- driver --------
def run_tune(sid, song, seconds, auto, max_ins_init=1_000_000, max_ins_call=250_000, max_stuck_frames=8, strict_init=False, salvage_init=False, auto_min_seconds=90.0, auto_confirm_windows=2, respect_irq_disable=False, cia_advance_mode="pre_irq_latch"):
    c=C64(sid.sid2, getattr(sid, "sid3", 0), psid_mode=not sid.rsid, force_irq_if_masked=not respect_irq_disable, cia_advance_mode=cia_advance_mode); c.load_sid(sid); c.init(sid, song, max_ins=max_ins_init)
    init_warning = None
    if c.last_call_reason == "max_ins":
        init_warning = "SID init exceeded instruction budget (%d)" % max_ins_init
        # Real PSID files are not a full C64 boot contract. A surprising number
        # of HVSC PSIDs have init routines that fall into a resident wait/player
        # loop after doing useful setup instead of cleanly RTSing.  Treating that
        # as fatal loses otherwise valid register capture (Arkanoid-class files).
        # RSID remains strict because it promises C64/KERNAL semantics.
        if (sid.rsid and not salvage_init) or strict_init:
            raise RuntimeError(init_warning)
    irq = sid.rsid or sid.play==0
    def cur_period():
        return c.current_timer_period(sid, song, irq)
    # drive by absolute cycles so multi-speed / play-programmed timers stay exact
    total=int(seconds*sid.clock); acc=0; frames=[]; fcyc=[]; stuck=0
    while acc < total and len(frames) < 400000:
        period = int(cur_period())
        if period <= 0:
            raise RuntimeError("invalid non-positive playback period: %r" % (period,))
        fcyc.append(acc)
        frame = c.step_call(sid, irq, max_ins=max_ins_call, song=song, elapsed_cycles=period)
        frames.append(ensure_sid_frame(frame))
        if c.last_call_reason == "max_ins":
            stuck += 1
            if stuck >= max_stuck_frames:
                raise RuntimeError("play/IRQ exceeded instruction budget for %d consecutive frames (max_ins_call=%d, captured_frames=%d)" % (stuck, max_ins_call, len(frames)))
        else:
            stuck = 0
        acc += period                              # timer writes inside frame affect next loop
    fcyc.append(acc)                               # sentinel end-cycle
    validate_frame_timing(frames, fcyc)
    loopP=find_loop(frames, sid.rate, auto_min_seconds, auto_confirm_windows) if auto else None
    if loopP: frames=frames[:loopP]; fcyc=fcyc[:loopP+1]
    return frames, fcyc, irq, loopP

# ---------------------------------------------------------------- main ---------
def main(argv=None):
    ap=argparse.ArgumentParser(description="Generic cycle-stamped SID -> MIDI")
    ap.add_argument("sid"); ap.add_argument("-o","--out",default=None)
    ap.add_argument("--song",type=int,default=None); ap.add_argument("--seconds",type=float,default=300.0)
    ap.add_argument("--auto",action="store_true",help="auto length via loop detection")
    ap.add_argument("--auto-min-seconds",type=float,default=90.0,help="Ignore loop candidates shorter than this many seconds; prevents short false demo/cracktro loops")
    ap.add_argument("--auto-confirm-windows",type=int,default=2,help="Require this many matching tail windows when enough captured material exists")
    ap.add_argument("--bpm",type=float,default=125.0, help="DAW grid BPM; real timing still derives from C64 cycles")
    ap.add_argument("--auto-bpm",action="store_true", help="Set grid BPM from C64 frame rate, --frames-per-row and --rows-per-beat")
    ap.add_argument("--frames-per-row",type=float,default=6.0, help="C64 tracker speed used only for --auto-bpm grid labelling")
    ap.add_argument("--rows-per-beat",type=float,default=4.0, help="Rows per beat used only for --auto-bpm grid labelling")
    ap.add_argument("--ppq",type=int,default=9600, help="MIDI pulses per quarter note; high default preserves SID write timing")
    ap.add_argument("--drumvoice",type=int,default=None)
    ap.add_argument("--no-bend",action="store_true"); ap.add_argument("--no-cc",action="store_true")
    ap.add_argument("--report",action="store_true")
    ap.add_argument("--max-ins-init", type=int, default=8_000_000, help="Init subroutine instruction budget (large PSID decrunch/init routines need headroom)")
    ap.add_argument("--max-ins-call", type=int, default=250_000, help="Per play/IRQ call instruction budget")
    ap.add_argument("--max-stuck-frames", type=int, default=8, help="Abort after N consecutive budget-exceeded frames")
    ap.add_argument("--strict-init", action="store_true", help="Treat PSID init budget exhaustion as fatal instead of continuing with captured setup state")
    ap.add_argument("--salvage-init", action="store_true", help="MIDI extraction salvage mode: continue after init budget even for RSID; forensic runs should leave this off")
    ap.add_argument("--respect-irq-disable", action="store_true", help="Do not force-clear I flag for KERNAL IRQ playback; stricter but may produce silence for drivers that leave SEI set")
    ap.add_argument("--require-roms", action="store_true", help="Fail if BASIC/KERNAL/CHARGEN ROMs are missing or invalid")
    ap.add_argument("--cia-advance-mode", choices=("pre_irq_latch", "post_call"), default="pre_irq_latch", help="Instruction-level CIA timing order; default latches IRQ source before handler, post_call is stricter experimental debug mode")
    ap.add_argument("--export-register-json", default=None, help="Write raw captured SidFrame register stream/fcyc metadata as JSON for debugging")
    a=ap.parse_args(argv)
    sid=SidFile(a.sid)
    missing_roms = [name for name, st in ROM_STATUS.items() if not st.get("present")]
    if a.require_roms and missing_roms:
        raise SystemExit("required C64 ROMs missing/invalid: " + ", ".join(sorted(missing_roms)))
    if a.auto_bpm:
        a.bpm = grid_bpm_from_c64(sid.rate, a.frames_per_row, a.rows_per_beat)
    selected = a.song if a.song is not None else sid.start
    if selected < 1 or selected > max(1, sid.songs):
        raise SystemExit("song must be in 1..%d" % max(1, sid.songs))
    song=selected-1
    out=a.out or os.path.splitext(a.sid)[0]+".mid"
    frames,fcyc,irq,loopP=run_tune(sid,song,a.seconds,a.auto,
                                   max_ins_init=a.max_ins_init,
                                   max_ins_call=a.max_ins_call,
                                   max_stuck_frames=a.max_stuck_frames,
                                   strict_init=a.strict_init,
                                   salvage_init=a.salvage_init,
                                   auto_min_seconds=a.auto_min_seconds,
                                   auto_confirm_windows=max(1,a.auto_confirm_windows),
                                   respect_irq_disable=a.respect_irq_disable,
                                   cia_advance_mode=a.cia_advance_mode)
    digi=sum(1 for f in frames if _frame_digi(f)>4)
    dur=fcyc[len(frames)]/sid.clock
    period=(fcyc[len(frames)]//max(1,len(frames))) if fcyc else sid.frame   # mean call period (cycles)
    if a.report:
        print("%s v%d  '%s' / %s / %s"%(sid.magic.decode(),sid.version,sid.name,sid.author,sid.release))
        print("chip %s  %s %dHz  songs %d  load $%04X init $%04X play $%04X%s"%(
            sid.model,"PAL" if sid.pal else "NTSC",sid.rate,sid.songs,sid.load,sid.init,sid.play,
            (("  2ndSID $%04X"%sid.sid2) if sid.sid2 else "") + (("  3rdSID $%04X"%sid.sid3) if getattr(sid,"sid3",0) else "")))
        if sid.basic_player or sid.basic_sys:
            print("basic %s" % ("SYS $%04X" % sid.basic_sys if sid.basic_sys else "flag set, no simple SYS stub detected"))
        for line in rom_report_lines():
            print(line)
        if sid.rsid and (KERNAL is None or BASIC is None or CHARGEN is None):
            print("warning: one or more C64 ROMs missing; RSID/BASIC/KERNAL behavior is approximate; use --require-roms for strict failure")
        print("timing %s period~%d (%.2f calls/frame)  %d frames (%.1fs)%s%s"%(
            "IRQ" if irq else ("v-sync" if sid.vsync(song) else "CIA"),period,sid.frame/max(1,period),
            len(frames),dur,
            "  loop@%.1fs"%(fcyc[loopP]/sid.clock) if loopP else "",
            "  DIGI($D418)" if digi>len(frames)//4 else ""))
    if a.export_register_json:
        payload = {
            "sid": {"path": a.sid, "name": sid.name, "author": sid.author, "songs": sid.songs,
                    "selected_song": selected, "clock": sid.clock, "rate": sid.rate,
                    "sid2": sid.sid2, "sid3": getattr(sid, "sid3", 0)},
            "timing": {"frames": len(frames), "seconds": dur, "loop_frames": loopP,
                       "fcyc": list(fcyc)},
            "frames": [frame_to_jsonable(f) for f in frames],
        }
        with open(a.export_register_json, "w", encoding="utf-8") as jf:
            json.dump(payload, jf, separators=(",", ":"))
    dv=(a.drumvoice-1) if a.drumvoice else None
    ppq,trks=convert(sid,frames,fcyc,a.bpm,drum_voice=dv,bend=not a.no_bend,do_cc=not a.no_cc,loopP=loopP,ppq=a.ppq)
    write_smf(out,ppq,trks)
    notes=sum(1 for t in trks for *_,b in t.ev if b[0]&0xF0==0x90 and b[2]>0)
    cc=sum(1 for t in trks for *_,b in t.ev if b[0]&0xF0==0xB0)
    print("%s : %d tracks, %d notes, %d CC, PPQ %d, %.1fs @ grid %g BPM"%(
        out,len(trks),notes,cc,ppq,dur,a.bpm))

if __name__=="__main__": main()
