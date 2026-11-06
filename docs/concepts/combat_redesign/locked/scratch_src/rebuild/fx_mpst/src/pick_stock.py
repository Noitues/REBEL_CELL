"""pick_stock.py: pick the FX-P plate stock (review 3.10: its own stock, pink-tinted paper, not card bone).
Search Lab L* 74-84, a* 14-34, b* -8..10 for the colour with the largest minimum dE76 against every meaning token, the light neutrals,
the slice inks, card bone, HIT_PAPER, K_TYPE, CREAM_HP and the card type plates; floor 15 (rb_tokens.DE_MIN)."""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
import rb_tokens as T
ref = dict(T.TOKENS)
ref.update(T.NEUTRALS)
ref.update({'slice_' + k: v for k, v in T.SLICE_INK.items()})
ref.update({'CARD_BONE': T.hx('F1EAD6'), 'HIT_PAPER': T.HIT_PAPER, 'K_TYPE': T.K_TYPE, 'CREAM_HP': T.CREAM_HP, 'CREAM': T.hx('FFF4D6'),
            'HOT_CORE': T.HOT_CORE, 'COLD_CHEV': T.COLD_CHEV, 'HARM_UP': T.HARM_UP})
try:
    import card_render as CR
    for k in dir(CR):
        pass
except Exception:
    pass
best = []
for L in np.arange(74, 84.1, 1.0):
    for a in np.arange(14, 34.1, 2.0):
        for b in np.arange(-8, 10.1, 2.0):
            rgb = T.lab2rgb(L, a, b)
            lab = T.lab(np.array(rgb, np.float64))
            if abs(lab[0] - L) > 0.8:
                continue
            ds = {k: T.de76(rgb, v) for k, v in ref.items()}
            m = min(ds.values())
            best.append((m, L, a, b, rgb, min(ds, key=ds.get)))
best.sort(reverse=True)
for m, L, a, b, rgb, k in best[:12]:
    print('min dE %.1f  L %.0f a %.0f b %.0f  #%02X%02X%02X  nearest %s' % (m, L, a, b, rgb[0], rgb[1], rgb[2], k))
# the pick: the best candidate at L* 78-80 (quieter than the bone plate, L* 93)
cands = [x for x in best if 77.5 <= x[1] <= 80.5]
m, L, a, b, rgb, k = cands[0]
print('PICK #%02X%02X%02X L* %.1f min dE %.1f nearest %s' % (rgb[0], rgb[1], rgb[2], T.lstar(T.lum(np.array(rgb, np.float64))), m, k))
ds = sorted((T.de76(rgb, v), kk) for kk, v in ref.items())
print('closest five', [(kk, round(d, 1)) for d, kk in ds[:5]])
