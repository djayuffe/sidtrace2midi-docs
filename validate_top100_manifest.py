#!/usr/bin/env python3
"""Validate a Top-100 SID->MIDI batch manifest.

Checks the things that matter after a long HVSC conversion run:
  * ok/failed/missing/skipped counts
  * weak MIDI files below a chosen note threshold
  * duplicate SID source paths
  * suspicious one-letter SID matches caused by overly broad fuzzy lookup
  * missing MIDI outputs for ok rows
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate Top-100 SID->MIDI manifest quality")
    ap.add_argument("manifest", nargs="?", default="~/Downloads/c64_top100_midi/top100_manifest.json")
    ap.add_argument("--min-notes", type=int, default=100)
    ap.add_argument("--expect-rows", type=int, default=100, help="Expected manifest row count; use 0 to disable")
    ap.add_argument("--allow-duplicate-sid", action="store_true", help="Do not fail duplicate SID source paths")
    args = ap.parse_args(argv)
    p = Path(args.manifest).expanduser()
    try:
        rows = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"INVALID_JSON: {e}")
        return 1
    if not isinstance(rows, list):
        print("INVALID_SCHEMA: manifest root must be a list")
        return 1
    rows = [r for r in rows if isinstance(r, dict)]
    required = {"rank", "title", "sid", "midi", "status", "notes", "reason"}
    schema_bad = []
    for idx, r in enumerate(rows):
        missing = sorted(required - set(r))
        status = r.get("status")
        if missing or status not in ("ok", "failed", "missing", "skipped"):
            schema_bad.append((idx, missing, status, r.get("title")))
        if status == "ok" and r.get("reason"):
            schema_bad.append((idx, ["ok row has non-empty reason"], status, r.get("title")))
        if status != "ok" and not r.get("reason") and status != "missing":
            schema_bad.append((idx, ["non-ok row missing reason"], status, r.get("title")))
    ok = [r for r in rows if r.get("status") == "ok"]
    bad = [r for r in rows if r.get("status") != "ok"]
    weak = [r for r in ok if (r.get("notes") is None or int(r.get("notes") or 0) < args.min_notes)]
    missing_midi = [r for r in ok if not Path(str(r.get("midi", ""))).expanduser().exists()]
    by_sid = {}
    for r in ok:
        sid = r.get("sid")
        if sid:
            by_sid.setdefault(sid, []).append(r)
    dup = {k:v for k,v in by_sid.items() if len(v) > 1}
    suspicious = [r for r in ok if r.get("sid") and len(Path(str(r["sid"])).stem) < 3]
    print(f"manifest={p}")
    wrong_rows = bool(args.expect_rows and len(rows) != args.expect_rows)
    print(f"rows={len(rows)} ok={len(ok)} non_ok={len(bad)} weak(<{args.min_notes})={len(weak)} duplicate_sid={len(dup)} suspicious_short_sid={len(suspicious)} missing_midi={len(missing_midi)} schema_bad={len(schema_bad)} expected_rows={args.expect_rows}")
    for idx, missing, status, title in schema_bad[:25]:
        print(f"SCHEMA_BAD: index={idx} title={title!r} status={status!r} issue={','.join(missing)}")
    for label, group in (("NON_OK", bad), ("WEAK", weak), ("SUSPICIOUS_SHORT_SID", suspicious), ("MISSING_MIDI", missing_midi)):
        for r in group[:25]:
            print(f"{label}: rank={r.get('rank')} title={r.get('title')} status={r.get('status')} notes={r.get('notes')} sid={r.get('sid')} log={r.get('log')}")
    for sid, group in list(dup.items())[:25]:
        titles = ", ".join(f"{r.get('rank')}:{r.get('title')}" for r in group)
        print(f"DUPLICATE_SID: {sid} <- {titles}")
    if wrong_rows:
        print(f"WRONG_ROW_COUNT: expected {args.expect_rows}, got {len(rows)}")
    duplicate_fail = bool(dup) and not args.allow_duplicate_sid
    return 1 if schema_bad or bad or weak or suspicious or missing_midi or wrong_rows or duplicate_fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
