#!/usr/bin/env python3
"""Shared hardened HVSC batch engine for SID2MIDI Top-N conversion.

The Top-100 classic, demos and cracktro wrappers build a list of ``TopTune``
records and then delegate conversion to this module.  It intentionally keeps the
resolver strict: exact path/name/stem first, then deterministic local HVSC
fallbacks.  No broad substring matching to one-letter junk files.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_HVSC = Path("/Users/ulfbertilsson/Downloads/C64Music")
DEFAULT_OUT = Path("~/Downloads/c64_top25_midi")

@dataclass(frozen=True)
class TopTune:
    rank: int
    title: str
    composer: str = "HVSC"
    bpm: int = 125
    song: int = 1
    candidates: tuple[str, ...] = ()

TOP25: tuple[TopTune, ...] = (
    TopTune(1, "Commando", "Rob Hubbard", 125, 1, ("MUSICIANS/H/Hubbard_Rob/Commando.sid", "Commando.sid")),
    TopTune(2, "Monty On The Run", "Rob Hubbard", 125, 1, ("MUSICIANS/H/Hubbard_Rob/Monty_on_the_Run.sid", "Monty_on_the_Run.sid")),
    TopTune(3, "International Karate", "Rob Hubbard", 125, 1, ("MUSICIANS/H/Hubbard_Rob/International_Karate.sid", "International_Karate.sid")),
    TopTune(4, "Last Ninja", "Ben Daglish", 125, 1, ("Last_Ninja.sid", "The_Last_Ninja.sid")),
    TopTune(5, "Delta", "Rob Hubbard", 125, 1, ("Delta.sid",)),
    TopTune(6, "R-Type", "Chris Huelsbeck", 125, 1, ("R-Type.sid", "R_Type.sid")),
    TopTune(7, "Cybernoid II", "Jeroen Tel", 125, 1, ("Cybernoid_II.sid",)),
    TopTune(8, "Wizball", "Martin Galway", 125, 1, ("Wizball.sid",)),
    TopTune(9, "Bubble Bobble", "Peter Clarke", 125, 1, ("Bubble_Bobble.sid",)),
    TopTune(10, "Giana Sisters", "Chris Huelsbeck", 125, 1, ("Great_Giana_Sisters.sid", "Giana_Sisters.sid")),
)

BAD_AUTO_HINTS = ("readme", "basic", "test", "sfx", "sound_effect", "speech", "empty", "charset", "picture", "collection")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def safe_name(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_. -]+", "_", s).strip().replace(" ", "_")
    return s[:96] or "sid"


def _iter_sid_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return (p for p in root.rglob("*.sid") if p.is_file())


def build_index(root: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    by_base: dict[str, list[Path]] = {}
    by_norm: dict[str, list[Path]] = {}
    for p in _iter_sid_files(root):
        by_base.setdefault(p.name.lower(), []).append(p)
        by_norm.setdefault(_norm(p.stem), []).append(p)
    return by_base, by_norm


def is_reasonable_sid_candidate(path: Path) -> bool:
    stem = _norm(path.stem)
    low = str(path).lower()
    if len(stem) < 3:
        return False
    if any(h in low for h in BAD_AUTO_HINTS):
        return False
    return True


def candidate_score(path: Path, root: Path, title: str = "", composer: str = "") -> tuple[int, int, str]:
    rel = str(path.relative_to(root)).replace(os.sep, "/") if root in path.parents or path == root else str(path)
    low = rel.lower(); score = 0
    for hint in (title, composer):
        n = _norm(hint)
        if n and n in _norm(path.stem):
            score += 500
        if n and n in _norm(rel):
            score += 250
    if "/musicians/" in "/" + low: score += 80
    if "/games/" in "/" + low: score += 60
    if "/demos/" in "/" + low: score += 50
    score += min(len(path.stem), 60)
    score -= rel.count("/")
    return (score, -len(rel), rel)


def find_tune(root: Path, tune: TopTune, by_base: dict[str, list[Path]] | None = None, by_norm: dict[str, list[Path]] | None = None) -> Path | None:
    by_base = by_base or {}; by_norm = by_norm or {}
    # Exact relative/absolute paths first.
    for cand in tune.candidates:
        p = Path(cand)
        full = p if p.is_absolute() else root / cand
        if full.exists() and full.is_file() and is_reasonable_sid_candidate(full):
            return full
    # Exact basename only, never broad fuzzy/substring.
    hits: list[Path] = []
    for cand in tune.candidates:
        hits.extend(by_base.get(Path(cand).name.lower(), []))
    hits = [h for h in set(hits) if is_reasonable_sid_candidate(h)]
    if hits:
        return sorted(hits, key=lambda p: candidate_score(p, root, tune.title, tune.composer), reverse=True)[0]
    # Exact normalized stem only.
    hits = []
    for cand in tune.candidates or (tune.title + ".sid",):
        hits.extend(by_norm.get(_norm(Path(cand).stem), []))
    hits = [h for h in set(hits) if is_reasonable_sid_candidate(h)]
    if hits:
        return sorted(hits, key=lambda p: candidate_score(p, root, tune.title, tune.composer), reverse=True)[0]
    return None


def parse_notes(report: str) -> int | None:
    # Expected: "... : 6 tracks, 123 notes, 456 CC, PPQ ..."
    m = re.search(r"\b(\d+)\s+notes\b", report)
    return int(m.group(1)) if m else None


def _read_vlq(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        value = (value << 7) | (b & 0x7F)
        if not (b & 0x80):
            break
    return value, pos


def count_midi_note_on(path: Path) -> int | None:
    """Count note-on events in an existing MIDI file without external deps.

    Used for --skip-existing manifest quality.  Returns None on malformed files
    so the row can still be audited instead of crashing the batch.
    """
    try:
        data = path.read_bytes()
        if data[:4] != b"MThd":
            return None
        pos = 8 + int.from_bytes(data[4:8], "big")
        total = 0
        while pos + 8 <= len(data):
            tag = data[pos:pos+4]; pos += 4
            size = int.from_bytes(data[pos:pos+4], "big"); pos += 4
            chunk = data[pos:pos+size]; pos += size
            if tag != b"MTrk":
                continue
            i = 0; running = None
            while i < len(chunk):
                _delta, i = _read_vlq(chunk, i)
                if i >= len(chunk):
                    break
                status = chunk[i]
                if status & 0x80:
                    i += 1
                    if status == 0xFF:
                        if i >= len(chunk): break
                        meta_type = chunk[i]; i += 1
                        ln, i = _read_vlq(chunk, i); i += ln
                        if meta_type == 0x2F:
                            break
                        continue
                    if status in (0xF0, 0xF7):
                        ln, i = _read_vlq(chunk, i); i += ln; continue
                    running = status
                else:
                    if running is None:
                        break
                    status = running
                op = status & 0xF0
                if op in (0xC0, 0xD0):
                    if i < len(chunk): i += 1
                else:
                    if i + 1 >= len(chunk): break
                    d1 = chunk[i]; d2 = chunk[i+1]; i += 2
                    if op == 0x90 and d2 != 0:
                        total += 1
        return total
    except Exception:
        return None




def sid_song_count(path: Path) -> int:
    """Return PSID/RSID song count from the file header, or 1 if unknown."""
    try:
        data = path.read_bytes()[:0x16]
        if len(data) >= 0x16 and data[:4] in (b"PSID", b"RSID"):
            songs = int.from_bytes(data[0x0E:0x10], "big")
            return max(1, min(256, songs or 1))
    except Exception:
        pass
    return 1

def should_accept_notes(notes: int | None, min_notes: int, allow_weak: bool) -> bool:
    """A run with unknown notes is accepted only when the MIDI exists and the converter did not report a count.

    A known count below min_notes is treated as weak/failed by default so a
    salvage-init placeholder with 0-2 notes cannot become a future
    --skip-existing false success.
    """
    return notes is None or allow_weak or notes >= min_notes

def make_command(args, sid: Path, outmid: Path, tune: TopTune, song: int | None = None, profile: str = "default") -> list[str]:
    cmd = [sys.executable, str(Path(args.sid2midi)), str(sid), "--song", str(song or tune.song), "--bpm", str(tune.bpm), "--report", "-o", str(outmid)]
    if args.auto: cmd.append("--auto")
    cmd += ["--seconds", str(float(args.seconds))]
    if args.drumvoice: cmd += ["--drumvoice", str(args.drumvoice)]
    if args.ppq: cmd += ["--ppq", str(args.ppq)]
    if args.auto_min_seconds is not None: cmd += ["--auto-min-seconds", str(args.auto_min_seconds)]
    if args.auto_confirm_windows is not None: cmd += ["--auto-confirm-windows", str(args.auto_confirm_windows)]
    if args.max_ins_init is not None: cmd += ["--max-ins-init", str(args.max_ins_init)]
    if args.max_ins_call is not None: cmd += ["--max-ins-call", str(args.max_ins_call)]
    if args.max_stuck_frames is not None: cmd += ["--max-stuck-frames", str(args.max_stuck_frames)]
    if args.strict_init: cmd.append("--strict-init")
    if args.salvage_init: cmd.append("--salvage-init")
    cmd += list(args.extra_arg or [])
    return cmd




def make_probe_command(args, sid: Path, outmid: Path, tune: TopTune, song: int) -> list[str]:
    """Build a cheap subtune probe command.

    The probe deliberately avoids large-init/salvage retries.  If a subtune cannot
    produce notes with the normal init path in a short window, the expensive full
    retry stack is not run for that subtune unless --exhaustive-subtune-scan is
    requested.  This prevents pathological SIDs with many loader subtunes from
    spending minutes per 0-note subtune.
    """
    ns = argparse.Namespace(**vars(args))
    ns.seconds = max(1.0, float(args.subtune_probe_seconds))
    ns.auto = False
    ns.auto_min_seconds = None
    ns.auto_confirm_windows = None
    ns.max_ins_init = args.max_ins_init
    ns.max_ins_call = args.max_ins_call
    ns.max_stuck_frames = args.max_stuck_frames
    ns.salvage_init = False
    ns.strict_init = args.strict_init
    return make_command(ns, sid, outmid, tune, song=song, profile="probe")

def run_command(cmd: list[str], timeout: float) -> tuple[int, str, float]:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        return p.returncode, p.stdout, time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        return 124, out + f"\nTIMEOUT after {timeout}s\n", time.time() - t0


def write_manifest(outdir: Path, prefix: str, rows: list[dict]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    jp = outdir / f"{prefix}_manifest.json"
    cp = outdir / f"{prefix}_manifest.csv"
    jp.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = ["rank","title","composer","bpm","song","actual_song","profile","sid","midi","status","reason","notes","elapsed_sec","ppq","seconds","auto","duration_policy","subtune_attempts","probe_attempts","full_render_count","command","log"]
    with cp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    # compatibility for older scripts
    if prefix == "top100":
        (outdir / "top25_manifest.json").write_text(jp.read_text(encoding="utf-8"), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shared Top-N HVSC SID2MIDI batch engine")
    ap.add_argument("--hvsc", type=Path, default=DEFAULT_HVSC)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--sid2midi", type=Path, default=Path(__file__).with_name("sid2midi.py"))
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--top", type=int, default=None)
    ap.add_argument("--start-at", type=int, default=1)
    ap.add_argument("--stop-after", type=int, default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-going", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--seconds", type=float, default=600.0)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--auto-min-seconds", type=float, default=None)
    ap.add_argument("--auto-confirm-windows", type=int, default=None)
    ap.add_argument("--ppq", type=int, default=9600)
    ap.add_argument("--drumvoice", type=int, default=3)
    ap.add_argument("--min-notes", type=int, default=100)
    ap.add_argument("--allow-weak-midi", action="store_true", help="Keep rc=0 outputs even when note count is below --min-notes")
    ap.add_argument("--delete-weak-midi", action="store_true", default=True, help="Delete/replace rc=0 outputs that fail --min-notes so skip-existing will not keep 0-note files")
    ap.add_argument("--no-delete-weak-midi", dest="delete_weak_midi", action="store_false", help="Keep weak/0-note MIDI artifacts for forensic debugging; not recommended for batch output")
    ap.add_argument("--subtune-good-notes", type=int, default=500)
    ap.add_argument("--song-scan-limit", type=int, default=16)
    ap.add_argument("--scan-policy", default="preferred-first")
    ap.add_argument("--always-scan-subtunes", action="store_true")
    ap.add_argument("--no-scan-subtunes-on-failure", action="store_true", help="Disable automatic subtune scan when selected song fails or renders weak/0-note output")
    ap.add_argument("--exhaustive-subtune-scan", action="store_true", help="Old slow behavior: run all retry/salvage profiles on every subtune during scan")
    ap.add_argument("--subtune-probe-seconds", type=float, default=45.0, help="Fast probe length used before full rendering alternate subtunes")
    ap.add_argument("--subtune-probe-timeout", type=float, default=60.0, help="Timeout for quick alternate-subtune probes")
    ap.add_argument("--subtune-probe-min-notes", type=int, default=20, help="Minimum probe note count before full rendering that alternate subtune")
    ap.add_argument("--subtune-zero-streak-limit", type=int, default=4, help="Stop alternate-subtune scan after this many consecutive 0-note probes")
    ap.add_argument("--subtune-bad-streak-limit", type=int, default=6, help="Stop alternate-subtune scan after this many consecutive failed/weak probes, including timeouts")
    ap.add_argument("--subtune-scan-time-budget", type=float, default=240.0, help="Maximum wall-clock seconds spent probing alternate subtunes for one SID; 0 disables the budget")
    ap.add_argument("--manifest-prefix", default="top25")
    ap.add_argument("--max-ins-init", type=int, default=None)
    ap.add_argument("--max-ins-call", type=int, default=None)
    ap.add_argument("--max-stuck-frames", type=int, default=None)
    ap.add_argument("--strict-init", action="store_true")
    ap.add_argument("--salvage-init", action="store_true")
    ap.add_argument("--salvage-retry", action="store_true", help="Opt in to the old automatic salvage-init retry profile. Default batch mode avoids salvage placeholders because they commonly produce 0-note MIDI for loader/demo subtunes.")
    ap.add_argument("--max-full-subtune-renders", type=int, default=4, help="Maximum expensive full alternate-subtune renders after quick probes. 0 disables the cap.")
    ap.add_argument("--extra-arg", action="append", default=[])
    args = ap.parse_args(argv)

    root = args.hvsc.expanduser().resolve()
    outdir = args.out.expanduser().resolve()
    debugdir = outdir / "debug"
    outdir.mkdir(parents=True, exist_ok=True); debugdir.mkdir(parents=True, exist_ok=True)

    tunes = list(TOP25)
    # `--top N` means “attempt N ranked entries” when used directly.  If the
    # caller explicitly supplied --limit as well, honor the tighter cap.  Older
    # behavior accidentally kept the default --limit 25 even for `--top 100`.
    limit_explicit = any(a == "--limit" or str(a).startswith("--limit=") for a in (argv or sys.argv[1:]))
    if args.top:
        args.limit = min(args.limit, args.top) if limit_explicit else args.top
    selected = [t for t in tunes if t.rank >= args.start_at]
    if args.stop_after: selected = selected[:args.stop_after]
    selected = selected[:args.limit]

    by_base, by_norm = build_index(root) if root.exists() else ({}, {})
    rows: list[dict] = []
    failed = 0
    for i, tune in enumerate(selected, 1):
        sid = find_tune(root, tune, by_base, by_norm)
        outmid = outdir / f"{tune.rank:02d}_{safe_name(tune.title)}.mid"
        row = {"rank": tune.rank, "title": tune.title, "composer": tune.composer, "bpm": tune.bpm, "song": tune.song, "actual_song": tune.song, "profile": "default", "sid": str(sid) if sid else None, "midi": str(outmid), "status": "missing", "notes": None, "elapsed_sec": 0.0, "ppq": args.ppq, "seconds": args.seconds, "auto": bool(args.auto), "duration_policy": "auto-loop-detect-capped" if args.auto else "fixed-duration", "subtune_attempts": 0, "probe_attempts": 0, "full_render_count": 0, "reason": "", "command": "", "log": str(debugdir / f"{tune.rank:02d}_{safe_name(tune.title)}.log")}
        if args.list:
            print(f"{tune.rank:03d}: {tune.title} -> {sid or 'MISSING'}")
            rows.append(row); continue
        print(f"CONVERT {tune.rank:02d}: {tune.title} -> {outmid.name}  timeout={args.timeout}s")
        if not sid:
            print("  MISSING SID candidate")
            row["status"] = "missing"; rows.append(row); failed += 1
            if not args.keep_going: break
            continue
        if args.skip_existing and outmid.exists() and outmid.stat().st_size > 0:
            existing_notes = count_midi_note_on(outmid)
            if existing_notes is not None and existing_notes < args.min_notes and not args.allow_weak_midi:
                print(f"  weak-existing notes={existing_notes} < min-notes={args.min_notes}; deleting and re-rendering")
                try:
                    outmid.unlink()
                except OSError:
                    pass
            else:
                row["status"] = "ok"
                row["notes"] = existing_notes
                row["duration_policy"] = row["duration_policy"] + "/skip-existing"
                rows.append(row)
                print(f"  skip-existing notes={row['notes']}")
                continue
        if args.dry_run:
            cmd = make_command(args, sid, outmid, tune)
            row["status"] = "ok"; row["command"] = " ".join(map(str, cmd)); rows.append(row); continue
        cmd = make_command(args, sid, outmid, tune)
        row["command"] = " ".join(map(str, cmd))
        if args.debug:
            print(f"  DEBUG sid={sid}")
            print(f"  DEBUG cmd={' '.join(map(str, cmd))}")
        def build_attempts_for_song(song_no: int) -> list[tuple[str, list[str]]]:
            base = make_command(args, sid, outmid, tune, song=song_no)
            attempts: list[tuple[str, list[str]]] = [("default", base)]
            # Large demo/cracktro init routines sometimes finish useful setup then
            # fall into a resident wait/player loop.  Retry with larger budgets and
            # finally salvage-init, but weak note counts are never accepted unless
            # --allow-weak-midi is explicit.
            if not args.strict_init and not args.salvage_init:
                attempts.extend([
                    ("large-init", make_command(argparse.Namespace(**{**vars(args), "max_ins_init": max(args.max_ins_init or 0, 32_000_000), "max_ins_call": args.max_ins_call, "max_stuck_frames": args.max_stuck_frames, "salvage_init": False}), sid, outmid, tune, song=song_no)),
                    ("large-init-large-call", make_command(argparse.Namespace(**{**vars(args), "max_ins_init": max(args.max_ins_init or 0, 32_000_000), "max_ins_call": max(args.max_ins_call or 0, 1_000_000), "max_stuck_frames": max(args.max_stuck_frames or 0, 16), "salvage_init": False}), sid, outmid, tune, song=song_no)),
                ])
                if args.salvage_retry:
                    attempts.append(("salvage-init", make_command(argparse.Namespace(**{**vars(args), "max_ins_init": max(args.max_ins_init or 0, 32_000_000), "max_ins_call": max(args.max_ins_call or 0, 1_000_000), "max_stuck_frames": max(args.max_stuck_frames or 0, 16), "salvage_init": True}), sid, outmid, tune, song=song_no)))
            return attempts

        def run_attempts_for_song(song_no: int):
            attempts = build_attempts_for_song(song_no)
            best_output = ""; best_elapsed = 0.0; best_rc = 1; best_notes = None; best_profile = "default"; best_cmd = attempts[0][1]
            for profile, acmd in attempts:
                if profile != "default" and args.debug:
                    print(f"  DEBUG retry-profile {profile} song={song_no}")
                rc, output, elapsed = run_command(acmd, args.timeout)
                notes = parse_notes(output)
                ok = rc == 0 and outmid.exists() and should_accept_notes(notes, args.min_notes, args.allow_weak_midi)
                if args.debug:
                    print(f"  DEBUG profile={profile} song={song_no} rc={rc} elapsed={elapsed:.1f}s notes={notes}")
                if ok or best_notes is None or (notes is not None and notes > (best_notes or -1)):
                    best_output, best_elapsed, best_rc, best_notes, best_profile, best_cmd = output, elapsed, rc, notes, profile, acmd
                if ok:
                    return best_output, best_elapsed, best_rc, best_notes, best_profile, best_cmd, True, attempts
                if notes is not None and notes < args.min_notes and outmid.exists() and args.delete_weak_midi and not args.allow_weak_midi:
                    try:
                        outmid.unlink()
                    except OSError:
                        pass
            return best_output, best_elapsed, best_rc, best_notes, best_profile, best_cmd, False, attempts

        output, elapsed, rc, notes, best_profile, best_cmd, accepted, attempts = run_attempts_for_song(tune.song)
        subtune_attempts = 1
        probe_attempts = 0
        failure_reason = "" if accepted else ("weak-notes" if notes is not None and notes < args.min_notes else ("timeout" if rc == 124 else "converter-failed"))
        best_song = tune.song
        # If the seeded subtune fails or creates a weak placeholder, scan other
        # subtunes.  This catches demo SIDs where song 1 is a loader/wait loop
        # but another subtune contains the music.
        scan_limit = min(max(1, args.song_scan_limit), sid_song_count(sid))
        if (not accepted or args.always_scan_subtunes) and not args.no_scan_subtunes_on_failure and scan_limit > 1:
            zero_streak = 0
            bad_streak = 0
            full_render_count = 0
            probe_elapsed_total = 0.0
            for song_no in range(1, scan_limit + 1):
                if song_no == tune.song:
                    continue
                if args.subtune_scan_time_budget and probe_elapsed_total >= float(args.subtune_scan_time_budget):
                    failure_reason = f"subtune-probe-budget-{probe_elapsed_total:.1f}s"
                    if args.debug:
                        print(f"  DEBUG subtune-scan stop: probe time budget {probe_elapsed_total:.1f}s >= {float(args.subtune_scan_time_budget):.1f}s")
                    break
                if args.debug:
                    print(f"  DEBUG subtune-scan song={song_no}/{scan_limit}")
                # Fast gate before expensive large-init/salvage profiles.  The
                # previous behavior could spend 50-140 seconds per alternate
                # subtune just to create 0-note salvage artifacts.  Failed probes
                # and timeouts also count against a bad-probe streak so loader
                # SIDs cannot burn the whole batch.
                if not args.exhaustive_subtune_scan:
                    pcmd = make_probe_command(args, sid, outmid, tune, song_no)
                    probe_attempts += 1
                    prc, pout, pelapsed = run_command(pcmd, min(float(args.timeout), float(args.subtune_probe_timeout)))
                    probe_elapsed_total += float(pelapsed)
                    pnotes = parse_notes(pout)
                    if args.debug:
                        print(f"  DEBUG probe song={song_no} rc={prc} elapsed={pelapsed:.1f}s notes={pnotes} bad_streak={bad_streak} zero_streak={zero_streak}")
                    if outmid.exists() and (pnotes is None or pnotes < args.min_notes) and args.delete_weak_midi and not args.allow_weak_midi:
                        try:
                            outmid.unlink()
                        except OSError:
                            pass
                    probe_is_zero = (pnotes == 0)
                    probe_is_weak = (prc != 0 or pnotes is None or pnotes < max(1, args.subtune_probe_min_notes))
                    if probe_is_zero:
                        zero_streak += 1
                    elif pnotes is not None and pnotes > 0:
                        zero_streak = 0
                    if probe_is_weak:
                        bad_streak += 1
                        if zero_streak >= max(1, args.subtune_zero_streak_limit):
                            failure_reason = f"subtune-zero-streak-{zero_streak}"
                            if args.debug:
                                print(f"  DEBUG subtune-scan stop: {zero_streak} consecutive zero-note probes")
                            break
                        if bad_streak >= max(1, args.subtune_bad_streak_limit):
                            failure_reason = f"subtune-bad-streak-{bad_streak}"
                            if args.debug:
                                print(f"  DEBUG subtune-scan stop: {bad_streak} consecutive failed/weak probes")
                            break
                        continue
                    bad_streak = 0
                if args.max_full_subtune_renders and full_render_count >= max(0, args.max_full_subtune_renders):
                    failure_reason = f"subtune-full-render-cap-{full_render_count}"
                    if args.debug:
                        print(f"  DEBUG subtune-scan stop: full render cap {full_render_count}")
                    break
                subtune_attempts += 1
                full_render_count += 1
                so, se, src, sn, sp, scmd, sok, sattempts = run_attempts_for_song(song_no)
                better = sok and (not accepted or (sn or -1) > (notes or -1))
                good_enough = sn is not None and sn >= args.subtune_good_notes
                if better or good_enough:
                    output, elapsed, rc, notes, best_profile, best_cmd, accepted = so, se, src, sn, sp, scmd, sok
                    attempts = sattempts
                    best_song = song_no
                    failure_reason = "" if accepted else failure_reason
                    if good_enough:
                        break
        if notes is not None and notes < args.min_notes and outmid.exists() and args.delete_weak_midi and not args.allow_weak_midi:
            try:
                outmid.unlink()
            except OSError:
                pass
        row["profile"] = best_profile
        row["actual_song"] = best_song
        row["elapsed_sec"] = round(elapsed, 3)
        row["command"] = " ".join(map(str, best_cmd))
        row["subtune_attempts"] = subtune_attempts
        row["probe_attempts"] = probe_attempts
        row["full_render_count"] = locals().get("full_render_count", 0)
        Path(row["log"]).write_text(output, encoding="utf-8", errors="replace")
        row["notes"] = notes
        weak_notes = (notes is not None and notes < args.min_notes)
        row["status"] = "ok" if rc == 0 and outmid.exists() and should_accept_notes(notes, args.min_notes, args.allow_weak_midi) else "failed"
        if row["status"] == "ok":
            row["reason"] = ""
        elif not row.get("reason"):
            row["reason"] = failure_reason or ("weak-notes" if weak_notes else ("timeout" if rc == 124 else "converter-failed"))
        if row["status"] != "ok" and weak_notes and outmid.exists() and args.delete_weak_midi:
            # Do not let a 0-note/weak salvage artifact become a future --skip-existing false success.
            try:
                outmid.unlink()
            except OSError:
                pass
        print(f"  DEBUG rc={rc} elapsed={elapsed:.1f}s notes={notes} profile={best_profile} song={best_song} status={row['status']} debug_log={row['log']}") if args.debug else None
        if output.strip():
            last = output.strip().splitlines()[-1]
            if row["status"] == "ok":
                print(f"  {last}")
            else:
                print(f"  FAILED status={row['status']} reason={row.get('reason','')} notes={notes} midi_kept={outmid.exists()}")
        if row["status"] != "ok":
            failed += 1
            if not args.keep_going:
                rows.append(row); break
        rows.append(row)
    write_manifest(outdir, args.manifest_prefix, rows)
    print(f"Done: manifest={outdir / (args.manifest_prefix + '_manifest.json')} ok={sum(1 for r in rows if r['status']=='ok')} failed={failed}")
    return 0 if failed == 0 or args.keep_going else 1

if __name__ == "__main__":
    raise SystemExit(main())
