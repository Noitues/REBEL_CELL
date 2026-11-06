"""pick.py <old hex> <Lmin> <Lmax> <floor> [tex]: nearest colour to old in the L* band whose min dE76 to every token, light neutral, slice ink, skin ink and card plate is >= floor"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
old_h, Lmin, Lmax, FLOOR = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
skip = sys.argv[5].split(',') if len(sys.argv) > 5 else []
ref = dict(T.TOKENS)
ref.update({'PAPER': T.hx('F2EEE4'), 'ENAMEL': T.hx('D9E1EA'), 'TEXT_HI': T.hx('F2F6FF'), 'TEXT_MID': T.hx('AFC0D6')})
for k, v in T.SLICE_INK.items(): ref['slice ' + k] = v
for s, d in T.SKIN_INKS.items():
    for k, v in d.items(): ref[s + ' ' + k] = v
ref.update({'card TOWER': T.hx('006E66'), 'card WAVE': T.hx('B4AAFF'), 'card SPIN3BAND': T.hx('FF00F0')})
for s in skip:
    ref.pop(s, None)
names = list(ref)
RL = T.lab(np.array([ref[k] for k in names], float))
g = np.arange(0, 256, 2)
R, G, B = np.meshgrid(g, g, g, indexing='ij')
C = np.stack([R, G, B], -1).reshape(-1, 3).astype(float)
L = T.lstar(T.lum(C))
C = C[(L >= Lmin) & (L <= Lmax)]
LAB = T.lab(C)
D = np.linalg.norm(LAB[:, None, :] - RL[None], axis=-1)
mn = D.min(1)
old = T.lab(np.array(T.hx(old_h), float))
d0 = np.linalg.norm(LAB - old, axis=1)
idx = np.where(mn >= FLOOR)[0]
idx = idx[np.argsort(d0[idx])][:12]
for i in idx:
    lab = LAB[i]
    print('#%02X%02X%02X  L* %.1f a %.0f b %.0f  dE_old %.1f  min dE %.1f vs %s' % (*C[i].astype(int), lab[0], lab[1], lab[2], d0[i], mn[i], names[int(D[i].argmin())]))
