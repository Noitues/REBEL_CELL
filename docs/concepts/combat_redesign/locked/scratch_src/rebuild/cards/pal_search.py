"""pal_search: candidate TOWER / WAVE plate hues and a Spin 3 band hue with CIE76 dE >= 15 from every meaning token and slice ink.
python pal_search.py  -> prints the best candidates per hue bin"""
import sys, re, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from de_lib import *

SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
sys.path.insert(0, SRC)
import xf_slices as XS
FILL_K = float(re.search(r'^FILL_K\s*=\s*([0-9.]+)', open(SRC + 'lw_tower.py').read(), re.M).group(1))

FORB = {k: hx(v) for k, v in TOKENS.items()}
for t, p in XS.PAL['A'].items():
    FORB['slice_' + t] = hx(p['fill'])
    FORB['slice_' + t + '_onboard'] = hx(p['fill']) * FILL_K
EXTRA = {'card_PINK': hx('FF3DA8'), 'CYAN_COIN': hx('1A8FB8'), 'CELL_LIME': hx('D4FF00'), 'card_CREAM': hx('F4EEE0')}
ALL = dict(FORB); ALL.update(EXTRA)
INK, WHITE = hx('15121A'), hx('FBFAF4')

g = np.linspace(0, 1, 52)
R, G, B = np.meshgrid(g, g, g, indexing='ij')
C = np.stack([R.ravel(), G.ravel(), B.ravel()], -1)
LAB = lab(C)
names = list(ALL)
F = np.stack([lab(ALL[k]) for k in names])
D = np.linalg.norm(LAB[:, None, :] - F[None], axis=-1)
mind = D.min(1)
lin_ = lin(C); Yc = lin_ @ np.array([0.2126, 0.7152, 0.0722])
rw = (np.maximum(Yc, Y(WHITE)) + 0.05) / (np.minimum(Yc, Y(WHITE)) + 0.05)
ri = (np.maximum(Yc, Y(INK)) + 0.05) / (np.minimum(Yc, Y(INK)) + 0.05)
chroma = np.hypot(LAB[:, 1], LAB[:, 2])
hue = (np.degrees(np.arctan2(LAB[:, 2], LAB[:, 1])) + 360) % 360

for role, txt, rr in (('dark plate, white text', 'WHITE', rw), ('light plate, ink text', 'INK', ri)):
    print('==', role)
    ok = (mind >= 18) & (rr >= 4.8) & (chroma >= 30)
    for h0 in range(0, 360, 30):
        sel = ok & (hue >= h0) & (hue < h0 + 30)
        if not sel.any():
            continue
        idx = np.where(sel)[0]
        # prefer high chroma, then margin
        sc = chroma[idx] + 1.5 * np.minimum(mind[idx], 30)
        best = idx[np.argsort(-sc)[:3]]
        for i in best:
            j = D[i].argmin()
            print('  hue %3d-%3d  %s  L*%5.1f C%5.1f  min dE %5.1f (%s)  text %4.1f' % (h0, h0 + 30, hexs(C[i]), LAB[i, 0], chroma[i], mind[i], names[j], rr[i]))
print('== band (no text), chroma >= 45')
ok = (mind >= 18) & (chroma >= 45)
for h0 in range(0, 360, 30):
    sel = ok & (hue >= h0) & (hue < h0 + 30)
    if not sel.any():
        continue
    idx = np.where(sel)[0]
    sc = LAB[idx, 0] + chroma[idx] * 0.5
    best = idx[np.argsort(-sc)[:3]]
    for i in best:
        j = D[i].argmin()
        print('  hue %3d-%3d  %s  L*%5.1f C%5.1f  min dE %5.1f (%s)' % (h0, h0 + 30, hexs(C[i]), LAB[i, 0], chroma[i], mind[i], names[j]))
