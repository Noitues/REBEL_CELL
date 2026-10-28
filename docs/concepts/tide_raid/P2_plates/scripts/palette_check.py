"""DAMAGED candidates vs the other marks under normal / deutan / tritan (dE76). Designer ruling: a yellower DAMAGED."""
import sys
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts')
import numpy as np
import colcheck as cc
def hx(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])
others = {'N': 'FF40D6', 'BREACHED': 'FF3347', 'SITESLOST': 'F29A1A', 'E': 'FFEE3A', 'HOLDS': '19C9B4', 'lime': 'C6FF2E'}
cands = ['FF6A1A', 'FF8A12', 'FF9A00', 'FFA21C', 'FF8F00', 'FFB000']
sl = ['F29A1A', 'D9820F', 'C47A0A', 'B8730E', 'D08A12']
print('DAMAGED candidates: min dE vs N / BREACHED / E (T, D, N)')
for c in cands:
    row = []
    for k in ('N', 'BREACHED', 'E', 'SITESLOST'):
        a, b = hx(c), hx(others[k])
        row.append('%s %4.0f/%4.0f/%4.0f' % (k[:4], cc.de(a, b, cc.TRIT), cc.de(a, b, cc.DEUT), cc.de(a, b)))
    print(c, ' | '.join(row))
print('SITES LOST alternatives vs a DAMAGED of FF9A00')
for s in sl:
    a, b = hx(s), hx('FF9A00')
    print(s, 'T %4.0f D %4.0f N %4.0f' % (cc.de(a, b, cc.TRIT), cc.de(a, b, cc.DEUT), cc.de(a, b)))
