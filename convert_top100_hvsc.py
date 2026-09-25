#!/usr/bin/env python3
"""Classic/game Top-100 HVSC SID -> MIDI batch wrapper."""
from __future__ import annotations
import argparse, os, re, sys
from pathlib import Path
import convert_top25_hvsc as core
from convert_top25_hvsc import TopTune

DEFAULT_HVSC = Path('/Users/ulfbertilsson/Downloads/C64Music')
DEFAULT_OUT = Path('~/Downloads/c64_top100_midi')

EXTRA_SEEDS = (
    ('Arkanoid','Martin Galway',('Arkanoid.sid',)), ('Auf Wiedersehen Pet','Rob Hubbard',('Auf_Wiedersehen_Pet.sid',)),
    ('Bionic Commando','Tim Follin',('Bionic_Commando.sid',)), ('Comic Bakery','Martin Galway',('Comic_Bakery.sid',)),
    ('Dominator','Matt Gray',('Dominator.sid',)), ('Enforcer','Jeroen Tel',('Enforcer.sid',)),
    ('Flimbo’s Quest','Reyn Ouwehand',('Flimbos_Quest.sid','Flimbo_s_Quest.sid')), ('Ghosts n Goblins','Mark Cooksey',('Ghosts_n_Goblins.sid',)),
    ('Green Beret','Martin Galway',('Green_Beret.sid',)), ('Hawkeye','Jeroen Tel',('Hawkeye.sid',)),
    ('Human Race','Rob Hubbard',('Human_Race.sid',)), ('IK+','Rob Hubbard',('IK+.sid','International_Karate_Plus.sid')),
    ('Knucklebusters','Rob Hubbard',('Knucklebusters.sid',)), ('Lightforce','Rob Hubbard',('Lightforce.sid',)),
    ('Parallax','Martin Galway',('Parallax.sid',)), ('Sanxion','Rob Hubbard',('Sanxion.sid',)),
    ('Skate or Die','Rob Hubbard',('Skate_or_Die.sid',)), ('Spellbound','Rob Hubbard',('Spellbound.sid',)),
    ('Turrican','Chris Huelsbeck',('Turrican.sid',)), ('Turrican II','Chris Huelsbeck',('Turrican_II.sid',)),
    ('W.A.R.','Rob Hubbard',('WAR.sid','W_A_R.sid')), ('Zoids','Rob Hubbard',('Zoids.sid',)),
)

def _norm(s): return re.sub(r'[^a-z0-9]+','',s.lower())

def title_from_sid(path: Path) -> str:
    return re.sub(r'\s+',' ',path.stem.replace('_',' ')).strip().title()

def composer_from_path(path: Path) -> str:
    parts = path.parts
    if 'MUSICIANS' in parts:
        i=parts.index('MUSICIANS')
        if i+2 < len(parts): return parts[i+2].replace('_',' ')
    if 'GAMES' in parts: return 'HVSC game auto-fill'
    return 'HVSC auto-fill'

def build_top100(root: Path, target: int=100) -> tuple[TopTune,...]:
    tunes=list(core.TOP25); seen={_norm(t.title) for t in tunes}; seen_paths=set()
    by_base, by_norm = core.build_index(root) if root.exists() else ({},{})
    for s in EXTRA_SEEDS:
        if len(tunes)>=target: break
        if _norm(s[0]) in seen: continue
        t=TopTune(len(tunes)+1,s[0],s[1],125,1,tuple(s[2]))
        if root.exists():
            p=core.find_tune(root,t,by_base,by_norm)
            if p is None: continue
            rp=str(p.resolve())
            if rp in seen_paths: continue
            t=TopTune(len(tunes)+1,t.title,t.composer,t.bpm,t.song,(str(p.relative_to(root)).replace(os.sep,'/'),p.name))
            seen_paths.add(rp)
        tunes.append(t); seen.add(_norm(t.title))
    if root.exists() and len(tunes)<target:
        candidates=sorted((p for p in core._iter_sid_files(root) if core.is_reasonable_sid_candidate(p)), key=lambda p: core.candidate_score(p,root), reverse=True)
        for p in candidates:
            rp=str(p.resolve()); title=title_from_sid(p); key=_norm(title)
            if key in seen or rp in seen_paths: continue
            try: rel=str(p.relative_to(root)).replace(os.sep,'/')
            except Exception: rel=p.name
            tunes.append(TopTune(len(tunes)+1,title,composer_from_path(p),125,1,(rel,p.name)))
            seen.add(key); seen_paths.add(rp)
            if len(tunes)>=target: break
    # Re-rank 1..N after merge
    return tuple(TopTune(i+1,t.title,t.composer,t.bpm,t.song,t.candidates) for i,t in enumerate(tunes[:target]))

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    pre=argparse.ArgumentParser(add_help=False); pre.add_argument('--hvsc',type=Path,default=DEFAULT_HVSC); pre.add_argument('--top',type=int,default=100); pre.add_argument('--out',type=Path,default=DEFAULT_OUT)
    known,_=pre.parse_known_args(argv); root=known.hvsc.expanduser().resolve(); target=max(1,min(known.top,500))
    old_top, old_out = core.TOP25, core.DEFAULT_OUT
    core.TOP25 = build_top100(root,target); core.DEFAULT_OUT = DEFAULT_OUT
    try:
        args=[]; i=0
        while i<len(argv):
            if argv[i]=='--top': i+=2; continue
            if argv[i].startswith('--top='): i+=1; continue
            args.append(argv[i]); i+=1
        defaults=[('--limit',str(target)),('--stop-after',str(target)),('--out',str(DEFAULT_OUT)),('--min-notes','100'),('--subtune-good-notes','500'),('--song-scan-limit','32'),('--seconds','600'),('--ppq','9600'),('--manifest-prefix','top100')]
        for k,v in defaults:
            if k not in args and not any(a.startswith(k+'=') for a in args): args += [k,v]
        if '--auto' not in args: args.append('--auto')
        if '--auto-min-seconds' not in args and not any(a.startswith('--auto-min-seconds=') for a in args): args += ['--auto-min-seconds','540']
        if '--auto-confirm-windows' not in args and not any(a.startswith('--auto-confirm-windows=') for a in args): args += ['--auto-confirm-windows','3']
        if '--max-full-subtune-renders' not in args and not any(a.startswith('--max-full-subtune-renders=') for a in args): args += ['--max-full-subtune-renders','4']
        rc=core.main(args)
        manifest=known.out.expanduser().resolve()/'top100_manifest.json'
        if manifest.exists(): print(f'Top-100 manifest={manifest}')
        return rc
    finally:
        core.TOP25, core.DEFAULT_OUT = old_top, old_out
if __name__=='__main__': raise SystemExit(main())
