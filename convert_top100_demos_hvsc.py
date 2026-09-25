#!/usr/bin/env python3
"""Demo-scene Top-100 HVSC SID -> MIDI batch wrapper."""
from __future__ import annotations
import argparse, os, re, sys
from pathlib import Path
import convert_top25_hvsc as core
from convert_top25_hvsc import TopTune

DEFAULT_HVSC=Path('/Users/ulfbertilsson/Downloads/C64Music')
DEFAULT_OUT=Path('~/Downloads/c64_top100_demos_midi')
DEMO_SEEDS=(
    ('Uncensored','Booze Design',('DEMOS/U/Uncensored.sid','Uncensored.sid')),
    ('Edge of Disgrace','Booze Design',('DEMOS/E/Edge_of_Disgrace.sid','Edge_of_Disgrace.sid')),
    ('Desert Dream','Demoscene',('DEMOS/D/Desert_Dream.sid','Desert_Dream.sid')),
    ('Deus Ex Machina','Crest',('DEMOS/D/Deus_Ex_Machina.sid','Deus_Ex_Machina.sid')),
    ('Krestage 3','Crest',('DEMOS/K/Krestage_3.sid','Krestage_3.sid')),
    ('Coma Light 13','Oxyron',('DEMOS/C/Coma_Light_13.sid','Coma_Light_13.sid')),
    ('Dutch Breeze','Blackmail',('DEMOS/D/Dutch_Breeze.sid','Dutch_Breeze.sid')),
    ('Wonderland','Censor Design',('DEMOS/W/Wonderland.sid','Wonderland.sid')),
    ('Access Denied','Booze Design',('DEMOS/A/Access_Denied.sid','Access_Denied.sid')),
    ('Royal Arte','Booze Design',('DEMOS/R/Royal_Arte.sid','Royal_Arte.sid')),
    ('Mathematica','Reflex',('DEMOS/M/Mathematica.sid','Mathematica.sid')),
    ('Triage','Offence',('DEMOS/T/Triage.sid','Triage.sid')),
    ('We Are New','Booze Design',('DEMOS/W/We_Are_New.sid','We_Are_New.sid')),
    ('Cycle','Booze Design',('DEMOS/C/Cycle.sid','Cycle.sid')),
    ('Soiled Legacy','Resource',('DEMOS/S/Soiled_Legacy.sid','Soiled_Legacy.sid')),
    ('Eldorado','Resource',('DEMOS/E/Eldorado.sid','Eldorado.sid')),
)
GENERIC={'demo_tune.sid','demo.sid','music.sid','tune.sid','intro.sid','main.sid','loader.sid','part.sid'}
GOOD=('demo','compo','party','trackmo','megademo','music','tune','remix','acid','funk','jazz','space','dream','light','edge','coma','uncensored')
BAD=('basic','sfx','sound_effect','speech','test','charset','picture','sample_only','collection','unknown','empty','readme','joke','beeper')

def _norm(s): return re.sub(r'[^a-z0-9]+','',s.lower())
def _rel(p,root):
    try: return '/' + str(p.relative_to(root)).replace(os.sep,'/')
    except Exception: return '/' + str(p).replace(os.sep,'/')
def is_reasonable_demo_sid(p:Path,root:Path)->bool:
    low=_rel(p,root).lower(); stem=_norm(p.stem)
    return len(stem)>=3 and not any(h in low for h in BAD)
def demo_score(p:Path,root:Path):
    low=_rel(p,root).lower(); score=0
    if '/demos/' in low: score+=700
    if '/musicians/' in low: score+=400
    for h in GOOD:
        if h in low: score+=30
    for h in BAD:
        if h in low: score-=500
    if p.name.lower() in GENERIC: score-=150
    return (score, -len(low), low)
def title_from_sid(p): return re.sub(r'\s+',' ',p.stem.replace('_',' ')).strip().title()
def composer_from_path(p):
    parts=p.parts
    if 'MUSICIANS' in parts:
        i=parts.index('MUSICIANS')
        if i+2<len(parts): return parts[i+2].replace('_',' ')
    return 'HVSC demo auto-fill'
def resolve_seed(root,seed,by_base,by_norm):
    title, comp, candidates = seed
    for cand in candidates:
        full=root/cand
        if full.exists() and full.is_file() and is_reasonable_demo_sid(full,root): return full
    if any(Path(c).name.lower() in GENERIC for c in candidates): return None
    hits=[]
    for c in candidates: hits += by_base.get(Path(c).name.lower(),[])
    hits=[h for h in set(hits) if is_reasonable_demo_sid(h,root)]
    if hits: return sorted(hits,key=lambda p:demo_score(p,root),reverse=True)[0]
    hits=[]
    for c in candidates: hits += by_norm.get(_norm(Path(c).stem),[])
    hits=[h for h in set(hits) if is_reasonable_demo_sid(h,root)]
    if hits: return sorted(hits,key=lambda p:demo_score(p,root),reverse=True)[0]
    return None

def build_top100_demos(root:Path,target:int=100):
    tunes=[]; seen=set(); seen_paths=set(); by_base,by_norm=core.build_index(root) if root.exists() else ({},{})
    for seed in DEMO_SEEDS:
        if len(tunes)>=target: break
        if _norm(seed[0]) in seen: continue
        if root.exists():
            p=resolve_seed(root,seed,by_base,by_norm)
            if not p: continue
            rp=str(p.resolve())
            if rp in seen_paths: continue
            rel=str(p.relative_to(root)).replace(os.sep,'/')
            tunes.append(TopTune(len(tunes)+1,seed[0],seed[1],125,1,(rel,p.name))); seen_paths.add(rp)
        else:
            tunes.append(TopTune(len(tunes)+1,seed[0],seed[1],125,1,seed[2]))
        seen.add(_norm(seed[0]))
    if root.exists() and len(tunes)<target:
        candidates=sorted((p for p in core._iter_sid_files(root) if is_reasonable_demo_sid(p,root)), key=lambda p:demo_score(p,root), reverse=True)
        for p in candidates:
            rp=str(p.resolve()); title=title_from_sid(p); key=_norm(title)
            if key in seen or rp in seen_paths: continue
            rel=str(p.relative_to(root)).replace(os.sep,'/')
            tunes.append(TopTune(len(tunes)+1,title,composer_from_path(p),125,1,(rel,p.name)))
            seen.add(key); seen_paths.add(rp)
            if len(tunes)>=target: break
    return tuple(tunes[:target])

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    pre=argparse.ArgumentParser(add_help=False); pre.add_argument('--hvsc',type=Path,default=DEFAULT_HVSC); pre.add_argument('--top',type=int,default=100); pre.add_argument('--out',type=Path,default=DEFAULT_OUT)
    known,_=pre.parse_known_args(argv); root=known.hvsc.expanduser().resolve(); target=max(1,min(known.top,500))
    old_top, old_out=core.TOP25, core.DEFAULT_OUT; core.TOP25=build_top100_demos(root,target); core.DEFAULT_OUT=DEFAULT_OUT
    try:
        args=[]; i=0
        while i<len(argv):
            if argv[i]=='--top': i+=2; continue
            if argv[i].startswith('--top='): i+=1; continue
            args.append(argv[i]); i+=1
        defaults=[('--limit',str(target)),('--stop-after',str(target)),('--out',str(DEFAULT_OUT)),('--min-notes','100'),('--subtune-good-notes','500'),('--song-scan-limit','32'),('--seconds','600'),('--ppq','9600'),('--manifest-prefix','top100_demos')]
        for k,v in defaults:
            if k not in args and not any(a.startswith(k+'=') for a in args): args += [k,v]
        if '--auto' not in args: args.append('--auto')
        if '--auto-min-seconds' not in args and not any(a.startswith('--auto-min-seconds=') for a in args): args += ['--auto-min-seconds','540']
        if '--auto-confirm-windows' not in args and not any(a.startswith('--auto-confirm-windows=') for a in args): args += ['--auto-confirm-windows','3']
        if '--max-full-subtune-renders' not in args and not any(a.startswith('--max-full-subtune-renders=') for a in args): args += ['--max-full-subtune-renders','4']
        rc=core.main(args); manifest=known.out.expanduser().resolve()/'top100_demos_manifest.json'
        if manifest.exists(): print(f'Top-100 demos manifest={manifest}')
        return rc
    finally:
        core.TOP25, core.DEFAULT_OUT=old_top, old_out
if __name__=='__main__': raise SystemExit(main())
