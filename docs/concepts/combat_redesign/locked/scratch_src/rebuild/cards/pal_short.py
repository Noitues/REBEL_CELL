"""pal_short: full dE76 rows for a short list of picks.  python pal_short.py HEX [HEX ...]"""
import sys, os, re
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from de_lib import *
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
sys.path.insert(0, SRC)
import xf_slices as XS
FILL_K = float(re.search(r'^FILL_K\s*=\s*([0-9.]+)', open(SRC + 'lw_tower.py').read(), re.M).group(1))
REF = {k: hx(v) for k, v in TOKENS.items()}
for t, p in XS.PAL['A'].items():
    REF['slice_' + t] = hx(p['fill']); REF['slice_' + t + '@FILL_K'] = hx(p['fill']) * FILL_K
REF.update({'card_PINK': hx('FF3DA8'), 'CYAN_COIN': hx('1A8FB8'), 'CELL_LIME': hx('D4FF00'), 'card_CREAM': hx('F4EEE0'),
            'band_Nudge': hx('3BB8F2'), 'band_Spin2': hx('44D9A6')})
INK, WHITE = hx('15121A'), hx('FBFAF4')
picks = [hx(a) for a in sys.argv[1:]]
for a, c in zip(sys.argv[1:], picks):
    rows = sorted(((de76(c, v), k) for k, v in REF.items()))
    others = ['%s %.1f' % (b, de76(c, d)) for b, d in zip(sys.argv[1:], picks) if b != a]
    print('#%s L*%.1f  white %.2f ink %.2f | nearest: %s | vs picks: %s' % (a, Lstar(c), ratio(WHITE, c), ratio(INK, c),
          ', '.join('%s %.1f' % (k, d) for d, k in rows[:4]), ', '.join(others)))
