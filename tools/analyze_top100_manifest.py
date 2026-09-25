#!/usr/bin/env python3
"""Summarize SID2MIDI Top-100 manifests and print targeted rerun commands.

This is an offline helper for long HVSC batch runs.  It never modifies files.
It groups failures by reason, flags weak/0-note rows, and emits exact commands
for rerunning only failed ranks with stronger options when useful.
"""
from __future__ import annotations
import argparse, json, shlex
from collections import Counter
from pathlib import Path


def load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"manifest is not a list: {path}")
    return [r for r in data if isinstance(r, dict)]


def q(s: str) -> str:
    return shlex.quote(str(s))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Analyze SID2MIDI Top-100 manifest quality and rerun targets")
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--min-notes", type=int, default=100)
    ap.add_argument("--show", type=int, default=30, help="maximum rows to print per section")
    ap.add_argument("--emit-rerun", action="store_true", help="print shell commands to rerun failed/weak ranks one by one")
    ap.add_argument("--converter-script", default="./convert_top100_demos_hvsc.py", help="batch converter script used in emitted commands")
    ap.add_argument("--hvsc", default="/Users/ulfbertilsson/Downloads/C64Music")
    ap.add_argument("--out", default="~/Downloads/c64_top100_demos_midi")
    args = ap.parse_args(argv)

    rows = load_rows(args.manifest.expanduser())
    ok = [r for r in rows if r.get("status") == "ok"]
    failed = [r for r in rows if r.get("status") != "ok"]
    weak = [r for r in ok if isinstance(r.get("notes"), int) and r.get("notes", 0) < args.min_notes]
    zeroish = [r for r in rows if r.get("notes") in (0, None) or (isinstance(r.get("notes"), int) and r.get("notes", 0) < args.min_notes)]

    print(f"manifest: {args.manifest}")
    print(f"rows={len(rows)} ok={len(ok)} failed={len(failed)} weak_ok={len(weak)} zero_or_unknown_or_weak={len(zeroish)}")
    if rows:
        durations = Counter(str(r.get("duration_policy", "")) for r in rows)
        reasons = Counter(str(r.get("reason", "")) or "ok" for r in rows)
        profiles = Counter(str(r.get("profile", "")) for r in rows)
        print("reasons:")
        for k, v in reasons.most_common(): print(f"  {k}: {v}")
        print("profiles:")
        for k, v in profiles.most_common(): print(f"  {k}: {v}")
        print("duration_policy:")
        for k, v in durations.most_common(): print(f"  {k}: {v}")

    if failed:
        print("\nfailed rows:")
        for r in failed[:args.show]:
            print(f"  {r.get('rank'):>3} {r.get('title')} status={r.get('status')} reason={r.get('reason')} notes={r.get('notes')} song={r.get('actual_song')} probes={r.get('probe_attempts')} full={r.get('full_render_count')}")
    if weak:
        print("\nweak ok rows:")
        for r in weak[:args.show]:
            print(f"  {r.get('rank'):>3} {r.get('title')} notes={r.get('notes')} midi={r.get('midi')}")

    if args.emit_rerun:
        print("\n# Rerun failed/weak rows one rank at a time")
        targets = failed + weak
        for r in targets[:args.show]:
            rank = int(r.get("rank") or 0)
            if not rank: continue
            print(
                f"{q(args.converter_script)} --hvsc {q(args.hvsc)} --out {q(args.out)} "
                f"--start-at {rank} --stop-after 1 --keep-going --debug --skip-existing "
                f"--seconds 600 --auto --auto-min-seconds 540 --auto-confirm-windows 3 "
                f"--subtune-probe-seconds 45 --subtune-probe-timeout 60 --subtune-zero-streak-limit 4 "
                f"--subtune-bad-streak-limit 6 --subtune-scan-time-budget 240 --max-full-subtune-renders 4"
            )
    return 0 if not failed and not weak else 1

if __name__ == "__main__":
    raise SystemExit(main())
