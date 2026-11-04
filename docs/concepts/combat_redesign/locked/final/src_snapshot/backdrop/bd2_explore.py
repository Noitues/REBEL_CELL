"""bd2_explore.py <room> <corp> <params.json> : grid of (knee, ceil, tone_lo) -> room region mean / p95 L* on p1 masks, plus the spread of
the room mean / p95 over the other beats' masks (p2, p2b, p3, nowords) for one setting.  Uses the cached grade_pre."""
import sys, json, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_lib as L
import bd_grade as BG
import rb_tokens as TK

room, corp, pf = sys.argv[1], sys.argv[2], sys.argv[3]
P0 = json.load(open(pf))
P0 = P0.get(room, next(iter(P0.values())))
P0.setdefault('spill_rgb', L.spill_rgb(room, lum_target=0.38, P=P0))
pre = BG.grade_pre(L.bare(room), P0)
F, T = L.fg(corp)
regs = {s: L.room_region(s) for s in ('p1', 'p2', 'p2b', 'p3', 'nowords')}


def st(P, sfx='p1'):
    bd = np.clip(L.G2().scrim(BG.grade_post(pre, P), 'P'), 0, 255)
    pl = np.clip(F + T * bd, 0, 255)
    Y = TK.lum(pl.astype(np.float64))
    r = regs[sfx]
    return float(TK.lstar(Y[r].mean())), float(np.percentile(TK.lstar(Y[r]), 95))


for kn, ce, lo in itertools.product((0.20, 0.24), (0.33, 0.35, 0.37), (0.13, 0.17, 0.21)):
    P = dict(P0, knee=kn, ceil=ce, tone_lo=lo)
    m_, p_ = st(P)
    print('knee %.2f ceil %.2f tone_lo %.2f  ->  mean %.2f  p95 %.2f' % (kn, ce, lo, m_, p_), flush=True)
P = dict(P0)
for s in regs:
    print('beat masks', s, 'px', int(regs[s].sum()), 'mean %.2f p95 %.2f' % st(P, s))
