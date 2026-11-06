"""vectorised: TURRET slice ink candidates at L* 61-71 with min dE76 >= FLOOR from tokens, neutrals, other slice inks, card plates"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
FLOOR = float(sys.argv[1]) if len(sys.argv) > 1 else 25
NEUTRAL = {'PAPER': T.hx('F2EEE4'), 'ENAMEL': T.hx('D9E1EA'), 'GUNMETAL': T.hx('6E7580')}
CARDS = {'TOWER': T.hx('006E66'), 'WAVE': T.hx('B4AAFF'), 'SPIN3BAND': T.hx('FF00F0')}
others = {k: v for k, v in T.SLICE_INK.items() if k != 'TURRET'}
ref = dict(T.TOKENS); ref.update(NEUTRAL); ref.update({'slice ' + k: v for k, v in others.items()}); ref.update({'card ' + k: v for k, v in CARDS.items()})
names = list(ref)
RL = T.lab(np.array([ref[k] for k in names], float))
g = np.arange(0, 256, 2)
R, G, B = np.meshgrid(g, g, g, indexing='ij')
C = np.stack([R, G, B], -1).reshape(-1, 3).astype(float)
L = T.lstar(T.lum(C))
C = C[(L >= 61) & (L <= 71)]
LAB = T.lab(C)
D = np.linalg.norm(LAB[:, None, :] - RL[None], axis=-1)
mn = D.min(1)
ok = mn >= FLOOR
old = T.lab(np.array(T.SLICE_INK['TURRET'], float))
d0 = np.linalg.norm(LAB - old, axis=1)
idx = np.where(ok)[0]
idx = idx[np.argsort(d0[idx])]
seen = []
for i in idx:
    lab = LAB[i]
    h = np.degrees(np.arctan2(lab[2], lab[1])) % 360
    if any(abs(h - s) < 6 for s in seen):
        continue
    seen.append(h)
    print('#%02X%02X%02X  L* %.1f  C %.0f h %.0f  dE_old %.1f  min dE %.1f vs %s' % (*C[i].astype(int), lab[0], np.hypot(lab[1], lab[2]), h, d0[i], mn[i], names[int(D[i].argmin())]))
    if len(seen) > 14:
        break
