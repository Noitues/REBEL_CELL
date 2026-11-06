"""every slice ink, slice texture, skin ink and card plate vs every meaning token and neutral (dE76); print pairs < 20"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
NEUTRAL = {'PAPER': T.hx('F2EEE4'), 'ENAMEL': T.hx('D9E1EA'), 'GUNMETAL': T.hx('6E7580'), 'INK': T.hx('0C0A16'), 'TEXT_HI': T.hx('F2F6FF'), 'TEXT_MID': T.hx('AFC0D6')}
CARDS = {'TOWER': T.hx('006E66'), 'WAVE': T.hx('B4AAFF'), 'SPIN3BAND': T.hx('FF00F0')}
ref = dict(T.TOKENS); ref.update(NEUTRAL)
items = {}
for k, v in T.SLICE_INK.items(): items['slice ' + k] = v
for s, d in T.SKIN_INKS.items():
    for k, v in d.items(): items[s + ' ' + k] = v
for k, v in CARDS.items(): items['card ' + k] = v
for a, ca in items.items():
    row = sorted(((T.de76(ca, cb), b) for b, cb in ref.items() if b != a))
    bad = [(round(d, 1), b) for d, b in row if d < 20]
    L = float(T.lstar(T.lum(np.array(ca, float))))
    print('%-20s #%02X%02X%02X L* %5.1f  %s' % (a, *ca, L, bad))
