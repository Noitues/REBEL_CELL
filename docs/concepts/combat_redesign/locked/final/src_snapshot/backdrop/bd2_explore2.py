"""bd2_explore2.py <room> : grid over the street / lift knobs, evaluated on all five beats with the per-beat transfers (bd2_beats)"""
import sys, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_lib as L
import bd_grade as BG
import bd2_beats as BB

room = sys.argv[1]
P0 = dict(BG.ROOMS[room])
for cv in (0.6, 0.8):
    Pp = dict(P0, city_value=cv)
    pre = BG.grade_pre(L.bare(room), Pp)
    for sl, ho, to, tl in itertools.product((0.38, 0.48), (0.5, 0.62), (0.45, 0.9), (0.17, 0.25)):
        P = dict(Pp, haze_out=ho, tone_out=to, tone_lo=tl, spill_rgb=L.spill_rgb(room, lum_target=sl, P=Pp))
        bd = np.clip(L.G2().scrim(BG.grade_post(pre, P), 'P'), 0, 255).astype(np.float32)
        r = {b: BB.stats_from(bd, b) for b in BB.BEATS}
        print('cv %.1f spill %.2f haze_out %.2f tone_out %.2f tone_lo %.2f | ' % (cv, sl, ho, to, tl) +
              ' '.join('%s %.1f/%.1f' % (b, m, p) for b, (m, p) in r.items()), flush=True)
