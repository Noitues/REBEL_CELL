"""C16: pick the Solace rim rope inks in the celadon / teal family of the Solace ink #B8DCCC.  Rules: dE76 >= 25 from GAIN and from the hub
HP ring green (rgb 123,211,123, as the reviewer measured), >= 15 from every meaning token and light neutral (check d), hue angle clearly off
green (LCh h >= 180), and a luma step from the celadon porcelain body so the rope reads.  python pick_teal.py"""
import sys, math, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
import rb_tokens as T

HUB_GREEN = (123, 211, 123)
POR = T.SKIN_INKS['solace']['porcelain']


def lch(c):
    L, a, b = T.lab(np.array(c, float))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def report(nm, c):
    L, C, h = lch(c)
    worst = min([(T.de76(c, v), k) for k, v in T.TOKENS.items()] + [(T.de76(c, v), k) for k, v in T.NEUTRALS.items()])
    print('%-10s #%02X%02X%02X L %.1f C %.1f h %.0f | GAIN %.1f hubHP %.1f porcelain %.1f | worst token/neutral %s %.1f' % (
        nm, *c, L, C, h, T.de76(c, T.TOKENS['GAIN']), T.de76(c, HUB_GREEN), T.de76(c, POR), worst[1], worst[0]))
    return worst[0]


print('porcelain', lch(POR))
cands = []
for L_ in (48, 52, 56, 60, 64, 68, 72, 76):
    for C_ in (22, 26, 30, 34):
        for h_ in (180, 185, 190, 195, 200):
            a, b = C_ * math.cos(math.radians(h_)), C_ * math.sin(math.radians(h_))
            c = T.lab2rgb(L_, a, b)
            if T.de76(c, T.TOKENS['GAIN']) < 25 or T.de76(c, HUB_GREEN) < 25:
                continue
            w = min([T.de76(c, v) for v in T.TOKENS.values()] + [T.de76(c, v) for v in T.NEUTRALS.values()])
            if w < 17:
                continue
            cands.append((L_, C_, h_, c, w))
for L_ in (52, 60, 68, 76):
    row = [x for x in cands if x[0] == L_]
    row.sort(key=lambda x: -x[4])
    for x in row[:3]:
        report('L%d' % L_, x[3])
for nm, c in (('old leaf', T.SKIN_INKS['solace']['leaf']), ('old deep', T.SKIN_INKS['solace']['leaf_deep']),
              ('pick hi', T.hx('6FC2BC')), ('pick deep', T.hx('2E7F7E')), ('pick mid', T.hx('4FA6A2'))):
    report(nm, c)
