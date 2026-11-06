import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
for k in T.SLICE_TEX:
    for nm, c in (('ink', T.SLICE_INK[k]), ('tex', T.SLICE_TEX[k])):
        lab = T.lab(np.array(c, float))
        print(k, nm, '#%02X%02X%02X' % c, 'L* %.1f C %.0f h %.0f' % (lab[0], np.hypot(lab[1], lab[2]), np.degrees(np.arctan2(lab[2], lab[1])) % 360))
for h in sys.argv[1:]:
    c = T.hx(h); lab = T.lab(np.array(c, float))
    print('cand', h, 'L* %.1f C %.0f h %.0f' % (lab[0], np.hypot(lab[1], lab[2]), np.degrees(np.arctan2(lab[2], lab[1])) % 360), 'dE old ink', round(T.de76(c, T.SLICE_INK['TURRET']), 1), 'vs BOSS', round(T.de76(c, T.BOSS_GOLD), 1))
