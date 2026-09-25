#!/usr/bin/env python3
"""Auto Top-100 cracktro/intro HVSC SID -> MIDI batch converter.

This is the cracktro/intro sibling of convert_top100_hvsc.py and
convert_top100_demos_hvsc.py.  It uses the same hardened batch engine in
convert_top25_hvsc.py, but builds a cracktro-oriented Top-100 list.

Design goals:
  * target classic cracktro / intro / loader / trainer / demogroup-style tunes
  * strict seed resolution; no broad generic basename collapse
  * duplicate SID source rejection
  * auto-fill from local HVSC when curated paths differ between HVSC versions
  * full-song loop policy by default: --auto --seconds 600 --auto-min-seconds 540
  * high-resolution MIDI timing: PPQ 9600
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import convert_top25_hvsc as core
from convert_top25_hvsc import TopTune

DEFAULT_HVSC = Path("/Users/ulfbertilsson/Downloads/C64Music")
DEFAULT_OUT = Path("~/Downloads/c64_top100_cracktros_midi")

# Cracktro/intro seeds.  The paths are conservative candidates.  If an exact
# path/name is absent in the user's HVSC checkout, we auto-fill with a real local
# cracktro/intro-like SID instead of broad-matching generic names.
CRACKTRO_SEEDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Future Composer Intro", "Demoscene", ("DEMOS/F/Future_Composer_Intro.sid", "Future_Composer_Intro.sid")),
    ("Triad Intro", "Triad", ("DEMOS/T/Triad_Intro.sid", "Triad_Intro.sid")),
    ("Fairlight Intro", "Fairlight", ("DEMOS/F/Fairlight_Intro.sid", "Fairlight_Intro.sid")),
    ("Ikari Intro", "Ikari", ("DEMOS/I/Ikari_Intro.sid", "Ikari_Intro.sid")),
    ("Hotline Intro", "Hotline", ("DEMOS/H/Hotline_Intro.sid", "Hotline_Intro.sid")),
    ("Remember Intro", "Remember", ("DEMOS/R/Remember_Intro.sid", "Remember_Intro.sid")),
    ("Genesis Project Intro", "Genesis Project", ("DEMOS/G/Genesis_Project_Intro.sid", "Genesis_Project_Intro.sid")),
    ("Censor Design Intro", "Censor Design", ("DEMOS/C/Censor_Design_Intro.sid", "Censor_Design_Intro.sid")),
    ("Booze Design Intro", "Booze Design", ("DEMOS/B/Booze_Design_Intro.sid", "Booze_Design_Intro.sid")),
    ("Crest Intro", "Crest", ("DEMOS/C/Crest_Intro.sid", "Crest_Intro.sid")),
    ("Oxyron Intro", "Oxyron", ("DEMOS/O/Oxyron_Intro.sid", "Oxyron_Intro.sid")),
    ("Camelot Intro", "Camelot", ("DEMOS/C/Camelot_Intro.sid", "Camelot_Intro.sid")),
    ("Offence Intro", "Offence", ("DEMOS/O/Offence_Intro.sid", "Offence_Intro.sid")),
    ("Resource Intro", "Resource", ("DEMOS/R/Resource_Intro.sid", "Resource_Intro.sid")),
    ("Bonzai Intro", "Bonzai", ("DEMOS/B/Bonzai_Intro.sid", "Bonzai_Intro.sid")),
    ("Vision Intro", "Vision", ("DEMOS/V/Vision_Intro.sid", "Vision_Intro.sid")),
    ("The Sharks Intro", "The Sharks", ("DEMOS/S/Sharks_Intro.sid", "Sharks_Intro.sid", "The_Sharks_Intro.sid")),
    ("Talent Intro", "Talent", ("DEMOS/T/Talent_Intro.sid", "Talent_Intro.sid")),
    ("Dominators Intro", "Dominators", ("DEMOS/D/Dominators_Intro.sid", "Dominators_Intro.sid")),
    ("Crazy Intro", "Crazy", ("DEMOS/C/Crazy_Intro.sid", "Crazy_Intro.sid")),
    ("Laser Intro", "Laser", ("DEMOS/L/Laser_Intro.sid", "Laser_Intro.sid")),
    ("Noice Intro", "Noice", ("DEMOS/N/Noice_Intro.sid", "Noice_Intro.sid")),
    ("Padua Intro", "Padua", ("DEMOS/P/Padua_Intro.sid", "Padua_Intro.sid")),
    ("Plush Intro", "Plush", ("DEMOS/P/Plush_Intro.sid", "Plush_Intro.sid")),
    ("Atlantis Intro", "Atlantis", ("DEMOS/A/Atlantis_Intro.sid", "Atlantis_Intro.sid")),
    ("F4CG Intro", "F4CG", ("DEMOS/F/F4CG_Intro.sid", "F4CG_Intro.sid")),
    ("Excess Intro", "Excess", ("DEMOS/E/Excess_Intro.sid", "Excess_Intro.sid")),
    ("Onslaught Intro", "Onslaught", ("DEMOS/O/Onslaught_Intro.sid", "Onslaught_Intro.sid")),
    ("Hokuto Force Intro", "Hokuto Force", ("DEMOS/H/Hokuto_Force_Intro.sid", "Hokuto_Force_Intro.sid")),
    ("Delysid Intro", "Delysid", ("DEMOS/D/Delysid_Intro.sid", "Delysid_Intro.sid")),
    ("Cracktro Tune", "HVSC", ("Cracktro_Tune.sid", "Cracktro.sid")),
    ("Intro Tune", "HVSC", ("Intro_Tune.sid", "Intro.sid")),
    ("Loader Intro", "HVSC", ("Loader_Intro.sid", "Loader.sid")),
    ("Trainer Intro", "HVSC", ("Trainer_Intro.sid", "Trainer.sid")),
    ("Onefile Intro", "HVSC", ("Onefile_Intro.sid", "One_File_Intro.sid")),
)

PREFERRED_CRACKTRO_PATH_PARTS = (
    "/DEMOS/", "/MUSICIANS/", "/GAMES/", "/VARIOUS/", "/",
)

GOOD_CRACKTRO_HINTS = (
    "crack", "cracktro", "intro", "intro_", "_intro", "loader", "trainer",
    "onefile", "one_file", "import", "release", "preview", "previewer", "menu",
    "triad", "fairlight", "ikari", "hotline", "remember", "genesis", "censor",
    "booze", "crest", "oxyron", "camelot", "offence", "resource", "bonzai",
    "vision", "dominators", "onslaught", "hokuto", "f4cg", "excess",
)

BAD_CRACKTRO_HINTS = (
    "basic", "sfx", "sound_effect", "speech", "test", "charset", "picture",
    "sample_only", "collection", "unknown", "empty", "readme", "joke", "beeper",
    "seuck", "editor", "utility", "manual", "note", "docs",
)

# These names are too generic for global basename resolution.  They are accepted
# only when a seeded exact path exists, otherwise auto-fill must choose a unique
# real SID with stronger contextual hints.
GENERIC_CRACKTRO_BASENAMES = {
    "intro.sid", "intro_tune.sid", "loader.sid", "loader_intro.sid",
    "trainer.sid", "trainer_intro.sid", "menu.sid", "music.sid", "tune.sid",
    "main.sid", "demo.sid", "cracktro.sid", "cracktro_tune.sid",
}

MIN_AUTO_STEM_LEN = 4

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _rel(path: Path, root: Path) -> str:
    try:
        return "/" + str(path.relative_to(root)).replace(os.sep, "/")
    except Exception:
        return "/" + str(path).replace(os.sep, "/")


def _is_generic_candidate_name(name: str) -> bool:
    return name.lower() in GENERIC_CRACKTRO_BASENAMES


def is_reasonable_cracktro_sid(path: Path, root: Path) -> bool:
    rel = _rel(path, root)
    low = rel.lower()
    stem_norm = _norm(path.stem)
    if len(stem_norm) < MIN_AUTO_STEM_LEN:
        return False
    if any(h in low for h in BAD_CRACKTRO_HINTS):
        return False
    # For auto-fill, require at least one cracktro/intro-ish signal unless the
    # file is in /DEMOS/.  This avoids drifting into random games/composer tunes.
    if "/demos/" not in low and not any(h in low for h in GOOD_CRACKTRO_HINTS):
        return False
    return True


def cracktro_score(path: Path, root: Path) -> tuple[int, int, str]:
    rel = _rel(path, root)
    low = rel.lower()
    score = 0
    for idx, part in enumerate(PREFERRED_CRACKTRO_PATH_PARTS):
        if part.lower() in low:
            score += 700 - idx * 35
    for hint in GOOD_CRACKTRO_HINTS:
        if hint in low:
            score += 45
    for hint in BAD_CRACKTRO_HINTS:
        if hint in low:
            score -= 500
    if _is_generic_candidate_name(path.name):
        score -= 200
    score += min(len(path.stem), 50)
    score -= rel.count("/")
    return (score, -len(rel), rel)


def title_from_sid(path: Path) -> str:
    title = re.sub(r"\s+", " ", path.stem.replace("_", " ")).strip().title()
    # Keep common scene acronyms readable.
    return (title.replace("F4Cg", "F4CG").replace("Ikari", "IKARI")
                 .replace("Flt", "FLT").replace("Triad", "TRIAD"))


def composer_from_path(path: Path) -> str:
    parts = path.parts
    if "MUSICIANS" in parts:
        i = parts.index("MUSICIANS")
        if i + 2 < len(parts):
            raw = parts[i + 2].replace("_", " ")
            bits = raw.split()
            return " ".join(bits[1:] + bits[:1]).strip() if len(bits) >= 2 else raw
    if "DEMOS" in parts:
        return "Cracktro / demoscene"
    return "HVSC cracktro auto-fill"


def seed_to_tune(rank: int, seed: tuple[str, str, tuple[str, ...]], resolved: Path | None, root: Path | None) -> TopTune:
    title, composer, candidates = seed
    if resolved is not None and root is not None:
        try:
            rel = str(resolved.relative_to(root)).replace(os.sep, "/")
        except Exception:
            rel = resolved.name
        return TopTune(rank, title, composer, 125, 1, (rel, resolved.name))
    return TopTune(rank, title, composer, 125, 1, candidates)


def resolve_seed(root: Path, seed: tuple[str, str, tuple[str, ...]], by_base: dict[str, list[Path]], by_norm: dict[str, list[Path]]) -> Path | None:
    _title, _composer, candidates = seed
    # Exact relative paths first.  This is the only path allowed for generic
    # names like Intro.sid / Loader.sid / Cracktro.sid.
    for cand in candidates:
        p = root / cand
        if p.exists() and p.is_file() and is_reasonable_cracktro_sid(p, root):
            return p
    if any(_is_generic_candidate_name(Path(c).name) for c in candidates):
        return None

    hits: list[Path] = []
    for cand in candidates:
        hits.extend(by_base.get(Path(cand).name.lower(), []))
    hits = [h for h in set(hits) if is_reasonable_cracktro_sid(h, root)]
    if hits:
        return sorted(hits, key=lambda p: cracktro_score(p, root), reverse=True)[0]

    hits = []
    for cand in candidates:
        key = _norm(Path(cand).stem)
        if key:
            hits.extend(by_norm.get(key, []))
    hits = [h for h in set(hits) if is_reasonable_cracktro_sid(h, root)]
    if hits:
        return sorted(hits, key=lambda p: cracktro_score(p, root), reverse=True)[0]
    return None


def build_top100_cracktros(root: Path, target: int = 100) -> tuple[TopTune, ...]:
    tunes: list[TopTune] = []
    seen_titles: set[str] = set()
    seen_paths: set[str] = set()
    by_base: dict[str, list[Path]] = {}
    by_norm: dict[str, list[Path]] = {}
    if root.exists():
        by_base, by_norm = core.build_index(root)

    for seed in CRACKTRO_SEEDS:
        if len(tunes) >= target:
            break
        title_key = _norm(seed[0])
        if title_key in seen_titles:
            continue
        if root.exists():
            resolved = resolve_seed(root, seed, by_base, by_norm)
            if resolved is None:
                continue
            rkey = str(resolved.resolve())
            if rkey in seen_paths:
                continue
            tunes.append(seed_to_tune(len(tunes) + 1, seed, resolved, root))
            seen_paths.add(rkey)
        else:
            tunes.append(seed_to_tune(len(tunes) + 1, seed, None, None))
        seen_titles.add(title_key)

    if root.exists() and len(tunes) < target:
        candidates = sorted(
            (p for p in core._iter_sid_files(root) if is_reasonable_cracktro_sid(p, root)),
            key=lambda p: cracktro_score(p, root), reverse=True,
        )
        used_titles = set(seen_titles)
        used_paths = {c for t in tunes for c in t.candidates}
        used_real_paths = set(seen_paths)
        for sid in candidates:
            title = title_from_sid(sid)
            title_key = _norm(title)
            try:
                rel = str(sid.relative_to(root)).replace(os.sep, "/")
            except Exception:
                rel = sid.name
            rkey = str(sid.resolve())
            if title_key in used_titles or rel in used_paths or sid.name in used_paths or rkey in used_real_paths:
                continue
            # Reject generic filenames from auto-fill unless the path carries
            # strong intro/cracktro context.  This prevents 100 rows of Intro.sid.
            if _is_generic_candidate_name(sid.name) and not any(h in _rel(sid, root).lower() for h in GOOD_CRACKTRO_HINTS):
                continue
            tunes.append(TopTune(len(tunes) + 1, title, composer_from_path(sid), 125, 1, (rel, sid.name)))
            used_titles.add(title_key); used_paths.update((rel, sid.name)); used_real_paths.add(rkey)
            if len(tunes) >= target:
                break
    return tuple(tunes[:target])


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--hvsc", type=Path, default=DEFAULT_HVSC)
    pre.add_argument("--top", type=int, default=100, help="Number of cracktro/intro SIDs to attempt, default 100")
    pre.add_argument("--out", type=Path, default=DEFAULT_OUT)
    known, _ = pre.parse_known_args(argv)
    target = max(1, min(known.top, 500))
    root = known.hvsc.expanduser().resolve()
    cracktro_top = build_top100_cracktros(root, target)

    old_top = core.TOP25
    old_default_out = core.DEFAULT_OUT
    core.TOP25 = cracktro_top
    core.DEFAULT_OUT = DEFAULT_OUT
    try:
        args: list[str] = []
        i = 0
        while i < len(argv):
            if argv[i] == "--top":
                i += 2; continue
            if argv[i].startswith("--top="):
                i += 1; continue
            args.append(argv[i]); i += 1
        if "--limit" not in args:
            args.extend(["--limit", str(target)])
        if "--stop-after" not in args:
            args.extend(["--stop-after", str(target)])
        if "--out" not in args and not any(a.startswith("--out=") for a in args):
            args.extend(["--out", str(DEFAULT_OUT)])
        if "--min-notes" not in args and not any(a.startswith("--min-notes=") for a in args):
            args.extend(["--min-notes", "80"])
        if "--subtune-good-notes" not in args and not any(a.startswith("--subtune-good-notes=") for a in args):
            args.extend(["--subtune-good-notes", "400"])
        if "--song-scan-limit" not in args and not any(a.startswith("--song-scan-limit=") for a in args):
            args.extend(["--song-scan-limit", "32"])
        if "--seconds" not in args and not any(a.startswith("--seconds=") for a in args):
            args.extend(["--seconds", "600"])
        if "--auto" not in args:
            args.append("--auto")
        if "--auto-min-seconds" not in args and not any(a.startswith("--auto-min-seconds=") for a in args):
            args.extend(["--auto-min-seconds", "540"])
        if "--auto-confirm-windows" not in args and not any(a.startswith("--auto-confirm-windows=") for a in args):
            args.extend(["--auto-confirm-windows", "3"])
        if "--ppq" not in args and not any(a.startswith("--ppq=") for a in args):
            args.extend(["--ppq", "9600"])
        if "--max-full-subtune-renders" not in args and not any(a.startswith("--max-full-subtune-renders=") for a in args):
            args.extend(["--max-full-subtune-renders", "4"])
        if "--manifest-prefix" not in args and not any(a.startswith("--manifest-prefix=") for a in args):
            args.extend(["--manifest-prefix", "top100_cracktros"])
        rc = core.main(args)
        outdir = known.out.expanduser().resolve()
        manifest = outdir / "top100_cracktros_manifest.json"
        if manifest.exists():
            print(f"Top-100 cracktros manifest={manifest}")
        return rc
    finally:
        core.TOP25 = old_top
        core.DEFAULT_OUT = old_default_out


if __name__ == "__main__":
    raise SystemExit(main())
