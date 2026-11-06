import sys, json, numpy as np
from lab import *
from lab import _xx, _yy
HUD_BOTTOM = {'p1': 445, 'p2': 615, 'p2b': 445, 'p3': 680, 'nowords': 445}
HAND_TOP = {'p1': 760, 'p2': 650, 'p2b': 760, 'p3': 760, 'nowords': 760}
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
for p in sys.argv[1:]:
    beat = 'nowords' if 'nowords' in p else p.split('_')[0]
    im = load(p); y = Y(im); L = Ls(y)
    base = (_xx >= 1100) & (_yy >= 420) & (R > 505)
    ui = np.zeros_like(base)
    ui[0:HUD_BOTTOM[beat] + 4, 1066:1904] = True
    ui[HAND_TOP[beat]:1080, 916:1664] = True
    ui[846:1014, 1656:1904] = True
    ui[1022:1062, 1650:1904] = True
    if beat == 'p2b': ui[455:615, 1085:1395] = True
    m = base & ~ui
    s = stats(y, m)
    rb = d['rb_checks'][p]['b_value_order']
    room = [r for r in rb['sorted'] if r['family'] == 'room']
    ck = room[0] if room else None
    box = y[450:800, 1200:1800]; box_clean = y[450:760, 1200:1800]
    print('%-22s my region mean %.1f p95 %.1f (px %d) | checker room mean %s p95 %s | reviewer box mean %.1f p95 %.1f | box y<760 mean %.1f' % (p, s['mean'], s['p95'], s['n'], ck and ck['mean'], ck and ck['p95'], float(Ls(box.mean())), float(Ls(np.percentile(box, 95))), float(Ls(box_clean.mean()))))
