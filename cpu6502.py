"""MOS 6502 / 6510 CPU core for C64 SID-register extraction.

This module is intentionally **instruction-level**, not transistor/per-PHI2
Visual6502 emulation.  It is tuned for PSID/RSID playback calls inside
``sid2midi.py``: callback memory access, C64/6510 processor-port support, all
official opcodes, common NMOS undocumented opcodes, IRQ/NMI helpers, bounded
trace diagnostics, strict JAM/unstable policies, and selectable decimal-mode
flag policies.

Important accuracy boundary:
    * Official opcode semantics are complete for SID-player extraction.
    * Decimal ADC/SBC supports practical NMOS/binary/adjusted/strict policies,
      but invalid-BCD analog edge cases are not guaranteed transistor-exact.
    * Cycle counts are instruction-level with branch/page-cross penalties; RDY,
      SYNC, VIC badlines/DMA and RMW dummy bus writes are outside scope.

6510 port model:
    ``intercept_6510_port=True`` lets the CPU own $0000/$0001 reads/writes.
    Writes are mirrored to the host callback by default, and reads can optionally
    call the host for logging/side-effects while returning the CPU port value.

Trace model:
    ``trace_limit=None`` keeps an unbounded diagnostic trace.
    ``trace_limit=N`` keeps the newest N entries. ``trace_seen`` is the
    lifetime number of traced instructions; ``trace_total`` is the number of
    rows currently retained. ``trace_dropped`` is exactly
    ``trace_seen - trace_total``. ``trace_limit=0`` records only counters and
    stores no trace rows.
"""

from collections import deque

class CPU6502:
    # Base cycle counts per opcode; page-cross / branch penalties are added live.
    CYC = bytearray([
        7,6,2,8,3,3,5,5,3,2,2,2,6,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7,
        6,6,2,8,3,3,5,5,4,2,2,2,6,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7,
        6,6,2,8,3,3,5,5,3,2,2,2,6,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7,
        6,6,2,8,3,3,5,5,4,2,2,2,6,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7,
        2,6,2,6,3,3,3,3,2,2,2,2,4,4,4,4,
        2,6,2,6,4,4,4,4,2,5,2,5,5,5,5,5,
        2,6,2,6,3,3,3,3,2,2,2,2,4,4,4,4,
        2,5,2,5,4,4,4,4,2,4,2,4,4,4,4,4,
        2,6,2,8,3,3,5,5,2,2,2,2,4,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7,
        2,6,2,8,3,3,5,5,2,2,2,2,4,4,6,6,
        2,5,2,8,4,4,6,6,2,4,2,7,6,4,7,7
    ])

    # Opcodes that incur +1 cycle on page boundary cross.
    # Includes indexed reads and abs,X RMW illegals/officials for closer timing.
    PAGE_CROSS = frozenset([
        0x1D,0x19,0x11,0x3D,0x39,0x31,0x5D,0x59,0x51,0x7D,0x79,0x71,
        0xDD,0xD9,0xD1,0xFD,0xF9,0xF1,0xBD,0xB9,0xB1,0xBC,0xBE,
        0x1E,0x3E,0x5E,0x7E,0xDE,0xFE
    ])
    # Backward-compatible alias for older tests/tools that used CPU6502.PAGE.
    PAGE = PAGE_CROSS

    JAM_OPS = frozenset((0x02,0x12,0x22,0x32,0x42,0x52,0x62,0x72,0x92,0xB2,0xD2,0xF2))
    UNSTABLE_OPS = frozenset((0x8B,0x93,0x9B,0x9C,0x9E,0x9F,0xAB,0xBB))
    OFFICIAL_OPS = frozenset((
        0x00,0x01,0x05,0x06,0x08,0x09,0x0A,0x0D,0x0E,0x10,0x11,0x15,0x16,0x18,0x19,0x1D,0x1E,
        0x20,0x21,0x24,0x25,0x26,0x28,0x29,0x2A,0x2C,0x2D,0x2E,0x30,0x31,0x35,0x36,0x38,0x39,0x3D,0x3E,
        0x40,0x41,0x45,0x46,0x48,0x49,0x4A,0x4C,0x4D,0x4E,0x50,0x51,0x55,0x56,0x58,0x59,0x5D,0x5E,
        0x60,0x61,0x65,0x66,0x68,0x69,0x6A,0x6C,0x6D,0x6E,0x70,0x71,0x75,0x76,0x78,0x79,0x7D,0x7E,
        0x81,0x84,0x85,0x86,0x88,0x8A,0x8C,0x8D,0x8E,0x90,0x91,0x94,0x95,0x96,0x98,0x99,0x9A,0x9D,
        0xA0,0xA1,0xA2,0xA4,0xA5,0xA6,0xA8,0xA9,0xAA,0xAC,0xAD,0xAE,0xB0,0xB1,0xB4,0xB5,0xB6,0xB8,0xB9,0xBA,0xBC,0xBD,0xBE,
        0xC0,0xC1,0xC4,0xC5,0xC6,0xC8,0xC9,0xCA,0xCC,0xCD,0xCE,0xD0,0xD1,0xD5,0xD6,0xD8,0xD9,0xDD,0xDE,
        0xE0,0xE1,0xE4,0xE5,0xE6,0xE8,0xE9,0xEA,0xEC,0xED,0xEE,0xF0,0xF1,0xF5,0xF6,0xF8,0xF9,0xFD,0xFE
    ))

    def __init__(self, read, write, *, strict_jam=False, strict_unstable=False, trace=False,
                 trace_limit=4096, ane_magic=0xEE, lxa_magic=0xEE, decimal_flags='nmos', intercept_6510_port=False,
                 mirror_6510_port_writes=True, mirror_6510_port_reads=False):
        self._host_read = read
        self._host_write = write
        self.intercept_6510_port = bool(intercept_6510_port)
        self.mirror_6510_port_writes = bool(mirror_6510_port_writes)
        self.mirror_6510_port_reads = bool(mirror_6510_port_reads)
        self.read = self._read_with_6510_port if self.intercept_6510_port else read
        self.write = self._write_with_6510_port if self.intercept_6510_port else write
        self.strict_jam = bool(strict_jam)
        self.strict_unstable = bool(strict_unstable)
        self.trace = bool(trace)
        self.trace_limit = None if trace_limit is None else max(0, int(trace_limit))
        self.trace_dropped = 0
        self.trace_total = 0      # currently retained trace rows
        self.trace_seen = 0       # lifetime traced instruction count
        self.decimal_flags = str(decimal_flags).lower()
        if self.decimal_flags not in ('nmos', 'binary', 'adjusted', 'strict'):
            raise ValueError("decimal_flags must be one of: nmos, binary, adjusted, strict")
        self.ane_magic = ane_magic & 0xFF
        self.lxa_magic = lxa_magic & 0xFF
        self.opcode_count = 0
        self.illegal_opcode_count = 0
        self.unstable_opcode_count = 0
        self.jam_count = 0
        self.brk_count = 0
        self.last_opcode = None
        self.last_pc = None
        self.last_stop_reason = "reset"
        self.last_instruction_count = 0
        self.opcode_trace = deque(maxlen=None if self.trace_limit is None else self.trace_limit)
        self.port_dir = 0x2F  # common C64/6510 power-on-ish defaults
        self.port_data = 0x37
        self.port_mirror_read_errors = 0
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.pc = 0
        self.C = self.Z = self.I = self.D = self.B = self.V = self.N = 0
        self.cycles = 0
        self._cross = 0
        self.jammed = False
        self._build()

    # ---- lifecycle / diagnostics ----
    def reset(self, pc=None):
        """Reset CPU registers. If pc is None, load the reset vector $FFFC/$FFFD."""
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.C = self.Z = self.D = self.B = self.V = self.N = 0
        self.I = 1
        self.cycles = 0
        self._cross = 0
        self.jammed = False
        self.last_opcode = None
        self.last_pc = None
        self.last_stop_reason = "reset"
        self.last_instruction_count = 0
        self.pc = self._r16(0xFFFC) if pc is None else (pc & 0xFFFF)

    def reset_jam(self):
        """Clear JAM/KIL latch for manual stepping after host-side reset/recovery."""
        self.jammed = False

    def status(self):
        """Return a compact diagnostic snapshot useful for SID-player audits."""
        return {
            'pc': self.pc & 0xFFFF, 'a': self.a & 0xFF, 'x': self.x & 0xFF, 'y': self.y & 0xFF,
            'sp': self.sp & 0xFF, 'p': self._getp(0), 'cycles': int(self.cycles),
            'jammed': bool(self.jammed), 'last_pc': self.last_pc, 'last_opcode': self.last_opcode,
            'opcode_count': self.opcode_count, 'illegal_opcode_count': self.illegal_opcode_count,
            'unstable_opcode_count': self.unstable_opcode_count, 'jam_count': self.jam_count,
            'brk_count': self.brk_count, 'last_stop_reason': self.last_stop_reason, 'last_instruction_count': self.last_instruction_count, 'trace_len': len(self.opcode_trace), 'trace_total': self.trace_total,
            'trace_seen': self.trace_seen, 'trace_dropped': self.trace_dropped,
            'port_dir': self.port_dir & 0x3F, 'port_data': self.port_data & 0x3F,
            'port_effective': self.effective_6510_port(),
            'port_mirror_read_errors': self.port_mirror_read_errors,
        }

    def __repr__(self):
        st = self.status()
        op = st['last_opcode']
        op_s = '--' if op is None else f'{op:02X}'
        return (f"CPU6502(pc=${st['pc']:04X}, a=${st['a']:02X}, x=${st['x']:02X}, "
                f"y=${st['y']:02X}, sp=${st['sp']:02X}, p=${st['p']:02X}, "
                f"cycles={st['cycles']}, last_op=${op_s}, jammed={st['jammed']})")

    def effective_6510_port(self):
        """Return the effective 6510 $0001 output pins with input bits pulled high.

        For C64 banking, bits configured as inputs behave as high/pulled-up.
        This prevents CPU/host split-brain when play routines change $0000/$0001.
        """
        return ((self.port_data & self.port_dir) | ((~self.port_dir) & 0x3F)) & 0x3F

    def write_6510_port(self, addr, value):
        """Optional helper for hosts that want CPU-side 6510 $0000/$0001 storage.

        sid2midi's C64 memory mapper normally owns banking, but tests/tools can
        use this helper to model the processor-port latch consistently.
        """
        if (addr & 0xFFFF) == 0x0000:
            self.port_dir = value & 0x3F
        elif (addr & 0xFFFF) == 0x0001:
            self.port_data = value & 0x3F

    def read_6510_port(self, addr):
        if (addr & 0xFFFF) == 0x0000:
            return self.port_dir & 0x3F
        if (addr & 0xFFFF) == 0x0001:
            return self.effective_6510_port()
        return 0xFF


    def _read_with_6510_port(self, addr):
        addr &= 0xFFFF
        if addr == 0x0000 or addr == 0x0001:
            # Return CPU-owned 6510 port state.  Optional host read mirrors only
            # side effects/logging and never overrides the hardware port value.
            if self.mirror_6510_port_reads:
                try:
                    self._host_read(addr)
                except Exception:
                    # Optional mirror reads are for host logging/side effects only.
                    # They must never override the CPU-owned 6510 port value.
                    self.port_mirror_read_errors += 1
            return self.read_6510_port(addr)
        return self._host_read(addr)

    def _write_with_6510_port(self, addr, value):
        addr &= 0xFFFF
        value &= 0xFF
        if addr == 0x0000 or addr == 0x0001:
            self.write_6510_port(addr, value)
            if self.mirror_6510_port_writes:
                self._host_write(addr, value)
            return
        self._host_write(addr, value)

    def trace_snapshot(self):
        """Return a stable list copy of the bounded opcode trace."""
        return list(self.opcode_trace)

    _DISASM = {
        0x00: ("BRK", 1), 0x20: ("JSR", 3), 0x4C: ("JMP", 3), 0x6C: ("JMP", 3),
        0x40: ("RTI", 1), 0x60: ("RTS", 1), 0xEA: ("NOP", 1),
        0x10: ("BPL", 2), 0x30: ("BMI", 2), 0x50: ("BVC", 2), 0x70: ("BVS", 2),
        0x90: ("BCC", 2), 0xB0: ("BCS", 2), 0xD0: ("BNE", 2), 0xF0: ("BEQ", 2),
        0xA9: ("LDA", 2), 0xA2: ("LDX", 2), 0xA0: ("LDY", 2),
        0x8D: ("STA", 3), 0x8E: ("STX", 3), 0x8C: ("STY", 3),
        0x69: ("ADC", 2), 0xE9: ("SBC", 2), 0x29: ("AND", 2), 0x09: ("ORA", 2), 0x49: ("EOR", 2),
        0xC9: ("CMP", 2), 0xE0: ("CPX", 2), 0xC0: ("CPY", 2),
        0xAA: ("TAX", 1), 0xA8: ("TAY", 1), 0x8A: ("TXA", 1), 0x98: ("TYA", 1),
        0x9A: ("TXS", 1), 0xBA: ("TSX", 1), 0x48: ("PHA", 1), 0x68: ("PLA", 1),
        0x08: ("PHP", 1), 0x28: ("PLP", 1), 0x18: ("CLC", 1), 0x38: ("SEC", 1),
        0x58: ("CLI", 1), 0x78: ("SEI", 1), 0xB8: ("CLV", 1), 0xD8: ("CLD", 1), 0xF8: ("SED", 1),
    }

    def disassemble_at(self, addr=None):
        """Return a compact one-line diagnostic disassembly at *addr* or PC.

        This is intentionally a debugger aid, not a full symbolic disassembler.
        It never changes CPU state and always includes raw opcode bytes, so even
        undocumented/unknown opcodes remain inspectable in traces.
        """
        a = self.pc if addr is None else (addr & 0xFFFF)
        op = self.read(a) & 0xFF
        name, ln = self._DISASM.get(op, ("ILL" if op not in self.OFFICIAL_OPS else "OP", 1))
        raw = [self.read((a + i) & 0xFFFF) & 0xFF for i in range(ln)]
        raw_s = " ".join(f"{b:02X}" for b in raw)
        if ln == 1:
            return f"${a:04X}: {raw_s:<8} {name}"
        if ln == 2:
            return f"${a:04X}: {raw_s:<8} {name} #${raw[1]:02X}"
        arg = raw[1] | (raw[2] << 8)
        return f"${a:04X}: {raw_s:<8} {name} ${arg:04X}"

    def clear_trace(self):
        """Clear opcode trace and reset trace accounting counters."""
        self.opcode_trace.clear()
        self.trace_dropped = 0
        self.trace_total = 0      # currently retained trace rows
        self.trace_seen = 0       # lifetime traced instruction count

    def step_dump(self):
        """Single-step and return before/after status for debugging."""
        before = self.status()
        ok = self.step()
        after = self.status()
        return {'ok': ok, 'before': before, 'after': after}

    # ---- flag helpers ----
    def _setp(self, p):
        self.C = p & 1
        self.Z = (p >> 1) & 1
        self.I = (p >> 2) & 1
        self.D = (p >> 3) & 1
        self.B = (p >> 4) & 1
        self.V = (p >> 6) & 1
        self.N = (p >> 7) & 1

    def _getp(self, b=0):
        return (self.C | (self.Z << 1) | (self.I << 2) | (self.D << 3) |
                (b << 4) | 0x20 | (self.V << 6) | (self.N << 7))

    def _nz(self, v):
        v &= 0xFF
        self.Z = 1 if v == 0 else 0
        self.N = (v >> 7) & 1
        return v

    # ---- stack / memory ----
    def _push(self, v):
        self.write(0x100 | self.sp, v & 0xFF)
        self.sp = (self.sp - 1) & 0xFF

    def _pop(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.read(0x100 | self.sp)

    def _r16(self, a):
        return self.read(a) | (self.read((a + 1) & 0xFFFF) << 8)

    # ---- addressing modes ----
    def _imm(self):
        a = self.pc
        self.pc = (self.pc + 1) & 0xFFFF
        return a

    def _zp(self):
        v = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def _zpx(self):
        v = (self.read(self.pc) + self.x) & 0xFF
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def _zpy(self):
        v = (self.read(self.pc) + self.y) & 0xFF
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def _abs(self):
        a = self._r16(self.pc)
        self.pc = (self.pc + 2) & 0xFFFF
        return a

    def _abx(self):
        b = self._r16(self.pc)
        self.pc = (self.pc + 2) & 0xFFFF
        a = (b + self.x) & 0xFFFF
        if (b & 0xFF00) != (a & 0xFF00):
            self._cross = 1
        return a

    def _aby(self):
        b = self._r16(self.pc)
        self.pc = (self.pc + 2) & 0xFFFF
        a = (b + self.y) & 0xFFFF
        if (b & 0xFF00) != (a & 0xFF00):
            self._cross = 1
        return a

    def _izx(self):
        z = (self.read(self.pc) + self.x) & 0xFF
        self.pc = (self.pc + 1) & 0xFFFF
        return self.read(z) | (self.read((z + 1) & 0xFF) << 8)

    def _izy(self):
        z = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        b = self.read(z) | (self.read((z + 1) & 0xFF) << 8)
        a = (b + self.y) & 0xFFFF
        if (b & 0xFF00) != (a & 0xFF00):
            self._cross = 1
        return a

    def _ind(self):  # JMP indirect page-wrap bug
        a = self._r16(self.pc)
        self.pc = (self.pc + 2) & 0xFFFF
        lo = self.read(a)
        hi = self.read((a & 0xFF00) | ((a + 1) & 0xFF))
        return lo | (hi << 8)

    def _rel(self):
        o = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return o - 256 if o & 0x80 else o

    # ---- BCD / ALU ----
    def _decimal_invalid(self, a, m):
        return ((a & 0x0F) > 9 or (a >> 4) > 9 or (m & 0x0F) > 9 or (m >> 4) > 9)

    def _decimal_flags_apply(self, binary, result, overflow):
        """Apply selectable decimal-mode flag policy.

        nmos/binary: Z and V from the binary intermediate, N from the adjusted
        result.  This is the best SID-player/default compromise and matches the
        documented project boundary: instruction-level NMOS, not Visual6502.

        adjusted: Z/N/V from the adjusted result; useful for comparison tests.
        strict: same as nmos, but invalid BCD input raises before execution.
        """
        if self.decimal_flags == 'adjusted':
            self.Z = 1 if (result & 0xFF) == 0 else 0
            self.N = (result >> 7) & 1
            self.V = overflow & 1
        else:  # nmos, binary, strict
            self.Z = 1 if (binary & 0xFF) == 0 else 0
            self.N = (result >> 7) & 1
            self.V = overflow & 1

    def _adc(self, m):
        """ADC with selectable decimal flag policy.

        `decimal_flags='nmos'` is the default used by SID extraction.  `strict`
        rejects invalid BCD digits so test harnesses do not accidentally treat
        undefined NMOS invalid-BCD flag behavior as a guaranteed contract.
        """
        m &= 0xFF
        a = self.a
        c = self.C
        if self.D:
            if self.decimal_flags == 'strict' and self._decimal_invalid(a, m):
                raise ValueError(f"invalid BCD ADC input a=${a:02X} m=${m:02X}")
            binary = a + m + c
            overflow = (~(a ^ m) & (a ^ binary) & 0x80) >> 7
            lo = (a & 0x0F) + (m & 0x0F) + c
            hi = (a >> 4) + (m >> 4)
            if lo > 9:
                lo += 6
            if lo > 0x0F:
                hi += 1
            if hi > 9:
                hi += 6
            result = ((hi << 4) | (lo & 0x0F)) & 0xFF
            self.C = 1 if hi > 0x0F else 0
            self._decimal_flags_apply(binary, result, overflow)
            self.a = result
        else:
            s = a + m + c
            self.C = 1 if s > 0xFF else 0
            self.V = (~(a ^ m) & (a ^ s) & 0x80) >> 7
            self.a = self._nz(s)

    def _sbc(self, m):
        """SBC with selectable decimal flag policy."""
        m &= 0xFF
        a = self.a
        c = self.C
        if self.D:
            if self.decimal_flags == 'strict' and self._decimal_invalid(a, m):
                raise ValueError(f"invalid BCD SBC input a=${a:02X} m=${m:02X}")
            inv = m ^ 0xFF
            binary = a + inv + c
            overflow = ((binary ^ a) & (binary ^ inv) & 0x80) >> 7
            carry = 1 if binary > 0xFF else 0
            dec = binary
            if ((a & 0x0F) + (inv & 0x0F) + c) <= 0x0F:
                dec -= 0x06
            if dec <= 0xFF:
                dec -= 0x60
            result = dec & 0xFF
            self.C = carry
            self._decimal_flags_apply(binary, result, overflow)
            self.a = result
        else:
            self._adc(m ^ 0xFF)

    def _cmp(self, r, m):
        t = (r - m) & 0x1FF
        self.C = 1 if r >= m else 0
        self._nz(t & 0xFF)

    # ---- instruction execution ----
    def step(self):
        if self.jammed:
            return False
        pc0 = self.pc
        op = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        h = self.ops[op]
        if h is None:
            return False
        self.last_pc = pc0
        self.last_opcode = op
        self.opcode_count += 1
        if op not in self.OFFICIAL_OPS:
            self.illegal_opcode_count += 1
        if op in self.UNSTABLE_OPS:
            self.unstable_opcode_count += 1
            if self.strict_unstable:
                raise RuntimeError(f"unstable NMOS opcode ${op:02X} at ${pc0:04X}")
        if self.trace:
            item = (pc0, op, self.a, self.x, self.y, self.sp, self._getp(0))
            self.trace_seen += 1
            if self.trace_limit != 0:
                self.opcode_trace.append(item)
            self.trace_total = len(self.opcode_trace)
            self.trace_dropped = max(0, self.trace_seen - self.trace_total)
        self._cross = 0
        h()
        extra = 1 if (op in self.PAGE_CROSS and self._cross) else 0
        self.cycles += self.CYC[op] + extra
        if self.jammed:
            self.last_stop_reason = "jam"
        elif op == 0x00:
            self.last_stop_reason = "brk"
        else:
            self.last_stop_reason = "step"
        self.last_instruction_count = 1
        return not self.jammed

    def call(self, addr, a=0, x=0, y=0, max_ins=4_000_000):
        self.a = a & 0xFF
        self.x = x & 0xFF
        self.y = y & 0xFF
        self.sp = 0xFD
        self.pc = addr & 0xFFFF
        self.jammed = False
        self.last_stop_reason = "running"
        self.last_instruction_count = 0
        self._push(0x00)  # sentinel return -> $0001
        self._push(0x00)
        self.cycles = 0
        n = 0
        while n < max_ins:
            if self.pc == 0x0001:
                self.last_stop_reason = "sentinel"
                break
            if not self.step():
                self.last_stop_reason = "jam" if self.jammed else "stop"
                break
            n += 1
        else:
            self.last_stop_reason = "max_ins"
        self.last_instruction_count = n
        return self.cycles

    def irq(self, vec=0xFFFE, kernal=True, max_ins=4_000_000):
        if self.I:
            return 0
        self.jammed = False
        self.cycles = 7
        isp = self.sp
        self._push((self.pc >> 8) & 0xFF)
        self._push(self.pc & 0xFF)
        self._push(self._getp(0))
        self.I = 1
        if kernal:
            self._push(self.a)
            self._push(self.x)
            self._push(self.y)
        self.pc = self._r16(vec)
        self.last_stop_reason = "running"
        self.last_instruction_count = 0
        n = 0
        while n < max_ins:
            if self.sp == isp:
                self.last_stop_reason = "irq_stack_restored"
                break
            if self.pc == 0x0001:
                self.last_stop_reason = "sentinel"
                break
            if kernal and self.pc in (0xEA31, 0xEA7E, 0xEA81):
                self.y = self._pop()
                self.x = self._pop()
                self.a = self._pop()
                self._setp(self._pop())
                lo = self._pop()
                hi = self._pop()
                self.pc = (hi << 8) | lo
                self.last_stop_reason = "kernal_irq_exit"
                break
            if not self.step():
                self.last_stop_reason = "jam" if self.jammed else "stop"
                break
            n += 1
        else:
            self.last_stop_reason = "max_ins"
        self.last_instruction_count = n
        return self.cycles

    def nmi(self, vec=0xFFFA, max_ins=4_000_000):
        """Run a non-maskable interrupt through vector $FFFA/$FFFB.

        NMI ignores I, pushes PC/P with B=0, sets I, then executes until RTI,
        sentinel $0001, JAM or max_ins.  This is primarily for completeness and
        rare RSID/decruncher support; most SID players use IRQ/CIA.
        """
        self.jammed = False
        self.cycles = 7
        isp = self.sp
        self._push((self.pc >> 8) & 0xFF)
        self._push(self.pc & 0xFF)
        self._push(self._getp(0))
        self.I = 1
        self.pc = self._r16(vec)
        self.last_stop_reason = "running"
        self.last_instruction_count = 0
        n = 0
        while n < max_ins:
            if self.sp == isp:
                self.last_stop_reason = "nmi_stack_restored"
                break
            if self.pc == 0x0001:
                self.last_stop_reason = "sentinel"
                break
            if not self.step():
                self.last_stop_reason = "jam" if self.jammed else "stop"
                break
            n += 1
        else:
            self.last_stop_reason = "max_ins"
        self.last_instruction_count = n
        return self.cycles

    # ---- build opcode table ----
    def _build(self):
        o = [None] * 256
        rd = self.read
        wr = self.write

        def br(cond):
            d = self._rel()
            if cond:
                old = self.pc
                self.pc = (self.pc + d) & 0xFFFF
                self.cycles += 1 + (1 if (old & 0xFF00) != (self.pc & 0xFF00) else 0)

        Z = self._zp
        ZX = self._zpx
        ZY = self._zpy
        AB = self._abs
        AX = self._abx
        AY = self._aby
        IX = self._izx
        IY = self._izy
        IM = self._imm

        # Core opcodes
        def LDA(m): self.a = self._nz(rd(m()))
        def LDX(m): self.x = self._nz(rd(m()))
        def LDY(m): self.y = self._nz(rd(m()))
        def STA(m): wr(m(), self.a)
        def STX(m): wr(m(), self.x)
        def STY(m): wr(m(), self.y)
        def ORA(m): self.a = self._nz(self.a | rd(m()))
        def AND(m): self.a = self._nz(self.a & rd(m()))
        def EOR(m): self.a = self._nz(self.a ^ rd(m()))
        def ADC(m): self._adc(rd(m()))
        def SBC(m): self._sbc(rd(m()))
        def CMP(m): self._cmp(self.a, rd(m()))
        def CPX(m): self._cmp(self.x, rd(m()))
        def CPY(m): self._cmp(self.y, rd(m()))
        def BIT(m):
            v = rd(m())
            self.Z = 1 if (self.a & v) == 0 else 0
            self.N = (v >> 7) & 1
            self.V = (v >> 6) & 1

        def INC(m):
            a = m()
            wr(a, self._nz(rd(a) + 1))
        def DEC(m):
            a = m()
            wr(a, self._nz(rd(a) - 1))

        def ASL(m):
            a = m()
            v = rd(a)
            self.C = (v >> 7) & 1
            wr(a, self._nz(v << 1))
        def LSR(m):
            a = m()
            v = rd(a)
            self.C = v & 1
            wr(a, self._nz(v >> 1))
        def ROL(m):
            a = m()
            v = rd(a)
            c = self.C
            self.C = (v >> 7) & 1
            wr(a, self._nz((v << 1) | c))
        def ROR(m):
            a = m()
            v = rd(a)
            c = self.C
            self.C = v & 1
            wr(a, self._nz((v >> 1) | (c << 7)))

        def ASLa():
            self.C = (self.a >> 7) & 1
            self.a = self._nz(self.a << 1)
        def LSRa():
            self.C = self.a & 1
            self.a = self._nz(self.a >> 1)
        def ROLa():
            c = self.C
            self.C = (self.a >> 7) & 1
            self.a = self._nz((self.a << 1) | c)
        def RORa():
            c = self.C
            self.C = self.a & 1
            self.a = self._nz((self.a >> 1) | (c << 7))

        # Populate standard opcodes
        for code, fn, am in [
            (0xA9,LDA,IM),(0xA5,LDA,Z),(0xB5,LDA,ZX),(0xAD,LDA,AB),(0xBD,LDA,AX),(0xB9,LDA,AY),(0xA1,LDA,IX),(0xB1,LDA,IY),
            (0xA2,LDX,IM),(0xA6,LDX,Z),(0xB6,LDX,ZY),(0xAE,LDX,AB),(0xBE,LDX,AY),
            (0xA0,LDY,IM),(0xA4,LDY,Z),(0xB4,LDY,ZX),(0xAC,LDY,AB),(0xBC,LDY,AX),
            (0x85,STA,Z),(0x95,STA,ZX),(0x8D,STA,AB),(0x9D,STA,AX),(0x99,STA,AY),(0x81,STA,IX),(0x91,STA,IY),
            (0x86,STX,Z),(0x96,STX,ZY),(0x8E,STX,AB),
            (0x84,STY,Z),(0x94,STY,ZX),(0x8C,STY,AB),
            (0x09,ORA,IM),(0x05,ORA,Z),(0x15,ORA,ZX),(0x0D,ORA,AB),(0x1D,ORA,AX),(0x19,ORA,AY),(0x01,ORA,IX),(0x11,ORA,IY),
            (0x29,AND,IM),(0x25,AND,Z),(0x35,AND,ZX),(0x2D,AND,AB),(0x3D,AND,AX),(0x39,AND,AY),(0x21,AND,IX),(0x31,AND,IY),
            (0x49,EOR,IM),(0x45,EOR,Z),(0x55,EOR,ZX),(0x4D,EOR,AB),(0x5D,EOR,AX),(0x59,EOR,AY),(0x41,EOR,IX),(0x51,EOR,IY),
            (0x69,ADC,IM),(0x65,ADC,Z),(0x75,ADC,ZX),(0x6D,ADC,AB),(0x7D,ADC,AX),(0x79,ADC,AY),(0x61,ADC,IX),(0x71,ADC,IY),
            (0xE9,SBC,IM),(0xE5,SBC,Z),(0xF5,SBC,ZX),(0xED,SBC,AB),(0xFD,SBC,AX),(0xF9,SBC,AY),(0xE1,SBC,IX),(0xF1,SBC,IY),
            (0xC9,CMP,IM),(0xC5,CMP,Z),(0xD5,CMP,ZX),(0xCD,CMP,AB),(0xDD,CMP,AX),(0xD9,CMP,AY),(0xC1,CMP,IX),(0xD1,CMP,IY),
            (0xE0,CPX,IM),(0xE4,CPX,Z),(0xEC,CPX,AB),
            (0xC0,CPY,IM),(0xC4,CPY,Z),(0xCC,CPY,AB),
            (0x24,BIT,Z),(0x2C,BIT,AB),
            (0xE6,INC,Z),(0xF6,INC,ZX),(0xEE,INC,AB),(0xFE,INC,AX),
            (0xC6,DEC,Z),(0xD6,DEC,ZX),(0xCE,DEC,AB),(0xDE,DEC,AX),
            (0x06,ASL,Z),(0x16,ASL,ZX),(0x0E,ASL,AB),(0x1E,ASL,AX),
            (0x46,LSR,Z),(0x56,LSR,ZX),(0x4E,LSR,AB),(0x5E,LSR,AX),
            (0x26,ROL,Z),(0x36,ROL,ZX),(0x2E,ROL,AB),(0x3E,ROL,AX),
            (0x66,ROR,Z),(0x76,ROR,ZX),(0x6E,ROR,AB),(0x7E,ROR,AX),
        ]:
            o[code] = (lambda f=fn, a=am: f(a))

        # Accumulator shifts
        o[0x0A] = ASLa
        o[0x4A] = LSRa
        o[0x2A] = ROLa
        o[0x6A] = RORa

        # Transfers / inc-dec
        def TAX(): self.x = self._nz(self.a)
        def TAY(): self.y = self._nz(self.a)
        def TXA(): self.a = self._nz(self.x)
        def TYA(): self.a = self._nz(self.y)
        def TSX(): self.x = self._nz(self.sp)
        def TXS(): self.sp = self.x & 0xFF
        def INX(): self.x = self._nz(self.x + 1)
        def DEX(): self.x = self._nz(self.x - 1)
        def INY(): self.y = self._nz(self.y + 1)
        def DEY(): self.y = self._nz(self.y - 1)
        o[0xAA]=TAX; o[0xA8]=TAY; o[0x8A]=TXA; o[0x98]=TYA; o[0xBA]=TSX
        o[0x9A]=TXS; o[0xE8]=INX; o[0xCA]=DEX; o[0xC8]=INY; o[0x88]=DEY

        # Stack
        def PLA(): self.a = self._nz(self._pop())
        o[0x48] = lambda: self._push(self.a)
        o[0x68] = PLA
        o[0x08] = lambda: self._push(self._getp(1))
        o[0x28] = lambda: self._setp(self._pop())

        # Flags
        def CLC(): self.C = 0
        def SEC(): self.C = 1
        def CLI(): self.I = 0
        def SEI(): self.I = 1
        def CLV(): self.V = 0
        def CLD(): self.D = 0
        def SED(): self.D = 1
        o[0x18]=CLC; o[0x38]=SEC; o[0x58]=CLI; o[0x78]=SEI
        o[0xB8]=CLV; o[0xD8]=CLD; o[0xF8]=SED; o[0xEA]=lambda: None

        # Branches
        o[0x90] = lambda: br(self.C == 0)
        o[0xB0] = lambda: br(self.C == 1)
        o[0xD0] = lambda: br(self.Z == 0)
        o[0xF0] = lambda: br(self.Z == 1)
        o[0x10] = lambda: br(self.N == 0)
        o[0x30] = lambda: br(self.N == 1)
        o[0x50] = lambda: br(self.V == 0)
        o[0x70] = lambda: br(self.V == 1)

        # Jumps / subroutines
        def JMP(): self.pc = self._abs()
        def JMPI(): self.pc = self._ind()
        def JSR():
            a = self._r16(self.pc)
            ret = (self.pc + 1) & 0xFFFF
            self._push((ret >> 8) & 0xFF)
            self._push(ret & 0xFF)
            self.pc = a
        def RTS():
            lo = self._pop()
            hi = self._pop()
            self.pc = (((hi << 8) | lo) + 1) & 0xFFFF
        def RTI():
            self._setp(self._pop())
            lo = self._pop()
            hi = self._pop()
            self.pc = (hi << 8) | lo
        def BRK():
            self.brk_count += 1
            self.pc = (self.pc + 1) & 0xFFFF
            self._push((self.pc >> 8) & 0xFF)
            self._push(self.pc & 0xFF)
            self._push(self._getp(1))
            self.I = 1
            self.pc = self._r16(0xFFFE)

        o[0x4C] = JMP
        o[0x6C] = JMPI
        o[0x20] = JSR
        o[0x60] = RTS
        o[0x40] = RTI
        o[0x00] = BRK

        # ---- Undocumented opcodes ----
        def NOPm(m): m()
        def LAX(m):
            v = rd(m())
            self.a = self.x = self._nz(v)
        def SAX(m): wr(m(), self.a & self.x)
        def DCP(m):
            a = m()
            v = (rd(a) - 1) & 0xFF
            wr(a, v)
            self._cmp(self.a, v)
        def ISC(m):
            a = m()
            v = (rd(a) + 1) & 0xFF
            wr(a, v)
            self._sbc(v)
        def SLO(m):
            a = m()
            v = rd(a)
            self.C = (v >> 7) & 1
            v = (v << 1) & 0xFF
            wr(a, v)
            self.a = self._nz(self.a | v)
        def RLA(m):
            a = m()
            v = rd(a)
            c = self.C
            self.C = (v >> 7) & 1
            v = ((v << 1) | c) & 0xFF
            wr(a, v)
            self.a = self._nz(self.a & v)
        def SRE(m):
            a = m()
            v = rd(a)
            self.C = v & 1
            v = v >> 1
            wr(a, v)
            self.a = self._nz(self.a ^ v)
        def RRA(m):
            a = m()
            v = rd(a)
            c = self.C
            self.C = v & 1
            v = ((v >> 1) | (c << 7)) & 0xFF
            wr(a, v)
            self._adc(v)
        def ANC(m):
            self.a = self._nz(self.a & rd(m()))
            self.C = (self.a >> 7) & 1
        def ALR(m):
            self.a &= rd(m())
            self.C = self.a & 1
            self.a = self._nz(self.a >> 1)
        def ARR(m):
            self.a &= rd(m())
            self.a = self._nz(((self.C << 7) | (self.a >> 1)) & 0xFF)
            self.C = (self.a >> 6) & 1
            self.V = ((self.a >> 6) ^ (self.a >> 5)) & 1
        def SBX(m):
            v = rd(m())
            t = (self.a & self.x) - v
            self.C = 1 if (self.a & self.x) >= v else 0
            self.x = self._nz(t & 0xFF)
        def ANE(m):
            # Unstable: common practical approximation with configurable magic.
            self.a = self._nz((self.a | self.ane_magic) & self.x & rd(m()))
        def LXA(m):
            # Unstable: common practical approximation, useful for decrunchers.
            v = (self.a | self.lxa_magic) & rd(m())
            self.a = self.x = self._nz(v)

        # Unstable/undocumented store/load family used by some decrunchers.
        # These are close practical NMOS approximations, good enough for
        # SID-player extraction where the key effect is the memory write/read.
        def AHX(m):
            a = m()
            wr(a, self.a & self.x & (((a >> 8) + 1) & 0xFF))
        def SHX(m):
            a = m()
            wr(a, self.x & (((a >> 8) + 1) & 0xFF))
        def SHY(m):
            a = m()
            wr(a, self.y & (((a >> 8) + 1) & 0xFF))
        def TAS(m):
            a = m()
            self.sp = self.a & self.x
            wr(a, self.sp & (((a >> 8) + 1) & 0xFF))
        def LAS(m):
            v = rd(m()) & self.sp
            self.a = self.x = self.sp = self._nz(v)
        def JAM():
            self.jammed = True
            self.jam_count += 1
            if self.strict_jam:
                raise RuntimeError(f"JAM/KIL opcode at ${self.last_pc:04X}")

        # NOPs
        for code in (0x1A,0x3A,0x5A,0x7A,0xDA,0xFA):
            o[code] = lambda: None
        for code in (0x80,0x82,0x89,0xC2,0xE2):
            o[code] = (lambda m=IM: NOPm(m))
        for code, am in [(0x04,Z),(0x44,Z),(0x64,Z),(0x14,ZX),(0x34,ZX),(0x54,ZX),
                         (0x74,ZX),(0xD4,ZX),(0xF4,ZX),(0x0C,AB),(0x1C,AX),(0x3C,AX),
                         (0x5C,AX),(0x7C,AX),(0xDC,AX),(0xFC,AX)]:
            o[code] = (lambda m=am: NOPm(m))

        # Illegal groups
        for fn, group in [
            (LAX, [(0xA7,Z),(0xB7,ZY),(0xAF,AB),(0xBF,AY),(0xA3,IX),(0xB3,IY)]),
            (SAX, [(0x87,Z),(0x97,ZY),(0x8F,AB),(0x83,IX)]),
            (DCP, [(0xC7,Z),(0xD7,ZX),(0xCF,AB),(0xDF,AX),(0xDB,AY),(0xC3,IX),(0xD3,IY)]),
            (ISC, [(0xE7,Z),(0xF7,ZX),(0xEF,AB),(0xFF,AX),(0xFB,AY),(0xE3,IX),(0xF3,IY)]),
            (SLO, [(0x07,Z),(0x17,ZX),(0x0F,AB),(0x1F,AX),(0x1B,AY),(0x03,IX),(0x13,IY)]),
            (RLA, [(0x27,Z),(0x37,ZX),(0x2F,AB),(0x3F,AX),(0x3B,AY),(0x23,IX),(0x33,IY)]),
            (SRE, [(0x47,Z),(0x57,ZX),(0x4F,AB),(0x5F,AX),(0x5B,AY),(0x43,IX),(0x53,IY)]),
            (RRA, [(0x67,Z),(0x77,ZX),(0x6F,AB),(0x7F,AX),(0x7B,AY),(0x63,IX),(0x73,IY)]),
        ]:
            for code, am in group:
                o[code] = (lambda f=fn, m=am: f(m))

        # Special illegals
        o[0x0B] = lambda: ANC(IM)
        o[0x2B] = lambda: ANC(IM)
        o[0x4B] = lambda: ALR(IM)
        o[0x6B] = lambda: ARR(IM)
        o[0xCB] = lambda: SBX(IM)
        o[0x8B] = lambda: ANE(IM)
        o[0xAB] = lambda: LXA(IM)
        o[0xEB] = lambda m=IM: SBC(m)  # USBC
        # AHX/SHA, TAS/SHS, SHY, SHX, LAS
        o[0x93] = lambda: AHX(IY)
        o[0x9F] = lambda: AHX(AY)
        o[0x9B] = lambda: TAS(AY)
        o[0x9C] = lambda: SHY(AX)
        o[0x9E] = lambda: SHX(AY)
        o[0xBB] = lambda: LAS(AY)

        # Real KIL/JAM opcodes: stop execution safely.  This avoids both
        # hardware-inaccurate endless running and batch hangs.
        for code in (0x02,0x12,0x22,0x32,0x42,0x52,0x62,0x72,0x92,0xB2,0xD2,0xF2):
            o[code] = JAM
            self.CYC[code] = 2

        # Remaining unstable/rare opcodes: recoverable 2-cycle NOP policy for
        # SID extraction, so one exotic byte does not destroy batch conversion.
        for code in range(256):
            if o[code] is None:
                o[code] = lambda: None
                self.CYC[code] = 2

        self.ops = o
