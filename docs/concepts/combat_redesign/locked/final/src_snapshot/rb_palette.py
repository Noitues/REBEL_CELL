"""rb_palette: print the colour picks of rb_tokens against their neighbours (dE76, L*), and suggest a nearest passing colour for a failing pick.
python rb_palette.py"""
import sys
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T


def L(c):
    return float(T.lstar(T.lum(np.array(c, np.float64))))


def report(name, c, neigh):
    ds = {n: T.de76(c, T.TOKENS[n]) for n in neigh}
    worst = min(ds, key=ds.get)
    print('%-14s #%02X%02X%02X  L* %5.1f  min dE %5.1f vs %s   %s' % (name, *c, L(c), ds[worst], worst, ' '.join('%s %.0f' % (k, v) for k, v in ds.items())))


print('-- tokens (all pairs)')
ks = list(T.TOKENS)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        d = T.de76(T.TOKENS[ks[i]], T.TOKENS[ks[j]])
        if d < 20:
            print('  %-12s %-12s %5.1f' % (ks[i], ks[j], d))
print('-- slice inks')
for k, c in T.SLICE_INK.items():
    report(k, c, T.SLICE_NEIGHBOURS)
print('-- skin inks')
for s, d in T.SKIN_INKS.items():
    for k, c in d.items():
        report(s + '.' + k, c, T.SKIN_NEIGHBOURS)
print('-- boss gold vs all')
report('BOSS_GOLD', T.BOSS_GOLD, [k for k in T.TOKENS if k != 'BOSS_GOLD'])
for nm, hx_ in (('TOWER', '2F5BFF'), ('WAVE', 'FF8A1F'), ('SPIN3', 'FFD21F')):
    report('card ' + nm, T.hx(hx_), T.CARD_NEIGHBOURS)
