"""rb_lift (2026-11-03 rebuild): search the lifted-card layout (lift dx, lift centre y, push of the cards after it) so the lifted card covers no
sibling cost hex or rules line, the hand stays off SEND IT / UNDO and outside r455.  Offline: card alphas only, no board render.
python rb_lift.py <beat> [lift card]      prints the best (dx, cy, push) and its numbers"""
import sys, os, json, math, itertools
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import f1_hand as FH
import rb_checks as RC
import rb_capture as RBC

J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
beat = sys.argv[1] if len(sys.argv) > 1 else 'p2'
lift = sys.argv[2] if len(sys.argv) > 2 else None
chk = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/work/chk_%s.json' % beat))
M = RC.load_masks(beat)
btn = M.get('send', np.zeros((1080, 1920), bool)) | M.get('undo', np.zeros((1080, 1920), bool))
hand, played, hov = FH.hand_lists(J, beat)
if lift:
    hov = hand.index(lift)
n = len(hand) + len(played)
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
ims = {nm: FH.card_hi(nm, False) for nm in hand}
lim = FH.card_hi(hand[hov], False, 'hover')


def layout(dx, cy, push):
    sl = FH.slots(n)
    for k in range(hov + 1, n):
        sl[k]['cx'] += push
    cards = []
    for i, nm in enumerate(hand):
        if i == hov:
            continue
        s = sl[i]
        cards.append(dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ims[nm].width, h2=ims[nm].height))
    s = sl[hov]
    L = dict(name=hand[hov], role='lift', cx=s['cx'] + dx, cy=cy, ang=0.0, scale=FH.LIFT_S * FH.CARD_SCALE, w2=lim.width, h2=lim.height)
    return cards, L


best = None
for dx, cy, push in itertools.product(range(-40, 1, 4), range(800, 870, 4), range(16, 41, 4)):
    cards, L = layout(dx, cy, push)
    lm = RBC._placed_alpha(lim, L['cx'], L['cy'], 0.0, L['scale'])
    allm = lm.copy()
    bad = 0
    for c in cards:
        m = RBC._placed_alpha(ims[c['name']], c['cx'], c['cy'], c['ang'], c['scale'])
        allm |= m
        cost, rules = RC.card_regions(c)
        bad += int((lm & RC.poly_mask([cost])).sum()) + int((lm & RC.poly_mask([rules])).sum())
    bad += int((allm & btn).sum()) + int((allm & (rho < FH.HAND_MIN_R + 3)).sum())
    score = (bad, abs(dx) + abs(push - 16) + abs(cy - FH.LIFT_CY))
    if best is None or score < best[0]:
        best = (score, dx, cy, push)
        if bad == 0:
            print('ok', dx, cy, push, score, flush=True)
print('best', best)
