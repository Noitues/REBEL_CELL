"""bd2_explore3.py <room> : flatter street + lower shoulder, evaluated on all five beats (per-beat transfers, bd2_beats)"""
import sys, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_lib as L
import bd_grade as BG
import bd2_beats as BB

room = sys.argv[1]
P0 = dict(BG.ROOMS[room], city_value=0.8)
pre = BG.grade_pre(L.bare(room), P0)
for ce, sl, ho, tl in itertools.product((0.31, 0.33), (0.30, 0.34), (0.70, 0.85), (0.25,)):
    P = dict(P0, ceil=ce, haze_out=ho, tone_out=0.9, tone_lo=tl, spill_rgb=L.spill_rgb(room, lum_target=sl, P=P0))
    bd = np.clip(L.G2().scrim(BG.grade_post(pre, P), 'P'), 0, 255).astype(np.float32)
    r = {b: BB.stats_from(bd, b) for b in BB.BEATS}
    print('ceil %.2f spill %.2f haze_out %.2f tone_lo %.2f | ' % (ce, sl, ho, tl) + ' '.join('%s %.1f/%.1f' % (b, m, p) for b, (m, p) in r.items()), flush=True)
