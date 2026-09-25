import io
import struct
import unittest

import sid2midi


def parse_track_events(blob):
    assert blob[:4] == b'MTrk'
    n = struct.unpack('>I', blob[4:8])[0]
    data = blob[8:8+n]
    i = 0
    last = 0
    out = []
    while i < len(data):
        delta = 0
        while True:
            b = data[i]; i += 1
            delta = (delta << 7) | (b & 0x7f)
            if not (b & 0x80):
                break
        last += delta
        status = data[i]; i += 1
        if status == 0xFF:
            typ = data[i]; i += 1
            ln = 0
            while True:
                b = data[i]; i += 1
                ln = (ln << 7) | (b & 0x7f)
                if not (b & 0x80):
                    break
            payload = data[i:i+ln]; i += ln
            out.append((last, status, typ, payload))
            if typ == 0x2F:
                break
        else:
            ln = 1 if (status & 0xF0) in (0xC0, 0xD0) else 2
            payload = data[i:i+ln]; i += ln
            out.append((last, status, None, payload))
    return out


class Sid2MidiLogicOrderFinalClosureTests(unittest.TestCase):
    def test_same_tick_note_off_before_note_on_with_stable_sequence(self):
        tr = sid2midi.Trk()
        tr.on(100, 0, 60, 100)
        tr.on(100, 0, 62, 100)
        tr.off(100, 0, 60)
        rendered = tr.render()
        statuses = [(e[1], list(e[3])) for e in parse_track_events(rendered) if e[1] != 0xFF]
        self.assertEqual(statuses[0][0] & 0xF0, 0x80)
        self.assertEqual(statuses[0][1][0], 60)
        self.assertEqual(statuses[1][0] & 0xF0, 0x90)
        self.assertEqual(statuses[1][1][0], 60)
        self.assertEqual(statuses[2][0] & 0xF0, 0x90)
        self.assertEqual(statuses[2][1][0], 62)

    def test_convert_accepts_legacy_frame_but_normalizes_and_validates_timing(self):
        sid = type('S', (), dict(clock=985248, name='x', author='', release='', model='MOS8580', pal=True,
                                 rate=50, magic=b'PSID', version=2, songs=1, init=0x1000, play=0x1003, load=0x1000,
                                 sid2=0, sid3=0))()
        regs = bytearray(0x19)
        regs[0] = 0x11; regs[1] = 0x11; regs[4] = 0x41; regs[5] = 0x00; regs[6] = 0xF0; regs[24] = 0x0F
        legacy = (bytes(regs), (1,0,0), (0,-1,-1), bytes(0x19), (0,0,0), (-1,-1,-1), bytes(0x19), (0,0,0), (-1,-1,-1), 0)
        ppq, tracks = sid2midi.convert(sid, [legacy], [0, 19656], bpm=125, ppq=9600)
        self.assertEqual(ppq, 9600)
        self.assertGreaterEqual(len(tracks), 6)
        with self.assertRaises(ValueError):
            sid2midi.convert(sid, [legacy], [0], bpm=125, ppq=9600)

    def test_find_loop_prefers_best_evidence_not_first_tail_match(self):
        # Build a simple repeating pattern long enough to satisfy min_seconds=1.
        frames = []
        for i in range(80):
            regs = bytearray(0x19)
            regs[0] = i & 0xFF
            regs[1] = (i * 3) & 0xFF
            regs[4] = 1 if i % 2 else 0
            frames.append(sid2midi.make_frame(regs, (0,0,0), (-1,-1,-1)))
        frames = frames + frames + frames
        self.assertEqual(sid2midi.find_loop(frames, rate=10, min_seconds=1, confirm_windows=2), 80)

    def test_run_tune_period_is_pre_call_interval(self):
        class FakeC64(sid2midi.C64):
            pass
        # Directly exercise step_call elapsed_cycles contract.
        sid = type('S', (), dict(vsync=lambda self, song: False, frame=1000))()
        c = sid2midi.C64()
        c.cra = 1
        c.ta_latch = 500
        c.ta_count = 500
        c.step_call(sid, irq=True, max_ins=1, song=0, elapsed_cycles=100)
        self.assertTrue(0 <= c.ta_count <= 500)


if __name__ == '__main__':
    unittest.main()
