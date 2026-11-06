"""search a TURRET slice ink: L* 60-72, dE76 >= 15 (target 17) from every meaning token, the neutrals (PAPER, ENAMEL, gunmetal), the other slice inks and the card type plates; nearest to the old pick"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
NEUTRAL = {'PAPER': T.hx('F2EEE4'), 'ENAMEL': T.hx('D9E1EA'), 'GUNMETAL': T.hx('6E7580')}
CARDS = {'TOWER': T.hx('006E66'), 'WAVE': T.hx('B4AAFF'), 'SPIN3BAND': T.hx('FF00F0')}
others = {k: v for k, v in T.SLICE_INK.items() if k != 'TURRET'}
ref = dict(T.TOKENS); ref.update(NEUTRAL); ref.update({'slice ' + k: v for k, v in others.items()}); ref.update({'card ' + k: v for k, v in CARDS.items()})
old = np.array(T.lab(np.array(T.SLICE_INK['TURRET'], float)))
best = []
for r in range(0, 256, 3):
    for g in range(0, 256, 3):
        for b in range(0, 256, 3):
            c = (r, g, b)
            L = float(T.lstar(T.lum(np.array(c, float))))
            if not (61 <= L <= 71):
                continue
            ds = {k: T.de76(c, v) for k, v in ref.items()}
            mn = min(ds.values())
            if mn < 17:
                continue
            d0 = float(np.linalg.norm(np.array(T.lab(np.array(c, float))) - old))
            best.append((d0, c, L, mn, min(ds, key=ds.get)))
best.sort()
for d0, c, L, mn, w in best[:25]:
    lab = T.lab(np.array(c, float))
    print('#%02X%02X%02X  L* %.1f  a %.0f b %.0f  dE_old %.1f  min dE %.1f vs %s' % (*c, L, lab[1], lab[2], d0, mn, w))
