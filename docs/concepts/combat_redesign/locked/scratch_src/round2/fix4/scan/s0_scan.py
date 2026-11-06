"""s0_scan.py (round 2 gate fix r2.2, S2-1 h02): where can the hovered slot-0 card (Brace) go on the PUBLISHED round-2 fan?
The board fan is not moved (corp/src as published, final/src_snapshot).  The hover set's numbers: the cards right of the lifted card open 36 px,
UNDO / SEND IT 16 px right.  For each variant of the hovered card (angle: upright or its rest angle; print / drop offset; dx) it scans centre y
and lists, per cy, what blocks it, with the same tests as hv_comp.hand_layout / hv_checks e:
  siblings' protected sets (rb_lift.protected: cost hex, title band, rules line, xN plate) 0 px under the lifted card's alpha (card, print, drop)
  lifted card outside r459 (HAND_MIN_R + LIFT_CLEAR), 3 px off the landing marks (h02's board arcs mask), 0 px within 2 px of SEND IT / UNDO,
  lowest hand px <= 1067, rest cards outside r455.
python s0_scan.py  -> ../work/s0_scan.json and one line per variant"""
import sys, os, json, math
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
from scipy import ndimage as ndi
import lw_render as LW
import f1_hand as FH
import rb_capture as RBC
import rb_checks as RC
import rb_lift as RL
import card_render as CR
import a2_stick as AS
import f1_render as F1

OUT = 'D:/rc_scratch/combat_redesign/locked/round2/fix4/work/'
H, W = 1080, 1920
Y0, Y1, X0, X1 = 560, 1080, 850, 1800
J = LW.R.A.J
OPEN, BDX = 36, 16
LIFT_CLEAR, ARC_GAP = 4.0, 3          # hz_core.LIFT_CLEAR, LIFT_ARC_GAP


def crop(m):
    return m[Y0:Y1, X0:X1]


z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/h02_brace.npz')
ARCS = np.unpackbits(z['Z__arcs'])[:H * W].reshape(H, W).astype(bool)
ARCS3 = crop(ndi.binary_dilation(ARCS, iterations=ARC_GAP))
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - 536, yy - 540)
r455 = crop(rho < FH.HAND_MIN_R)
r459 = crop(rho < FH.HAND_MIN_R + LIFT_CLEAR)
RL.BTN_DX = BDX
F1.BTN_DX[0] = BDX
im, (bx0, by0) = FH.ui_img('send', False)
btn = np.zeros((H, W), bool)
a = np.asarray(im.split()[3]) >= 128
btn[by0:by0 + a.shape[0], bx0:bx0 + a.shape[1]] = a[:H - by0, :W - bx0]
lay, info = AS.stack_layer(True, {})
a = np.asarray(lay.split()[3]) >= 128
box = np.zeros_like(a)
box[850:900, 1655 + BDX:1896 + BDX] = True
btn |= a & box
BTN = crop(ndi.binary_dilation(btn, iterations=2))
hand = list(J['f1']['hand'])
n = len(hand)
rest_ims = {nm: FH.card_hi(nm, False) for nm in hand}
print('hand', hand, 'slots', [(round(s['cx'], 1), round(s['cy'], 1), round(s['ang'], 2)) for s in FH.slots(n)], flush=True)


def lift_img(name, print_off, drop_off):
    CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = print_off
    CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = drop_off
    FH._mem.clear()
    return FH.card_hi(name, False, 'hover')


def placed(sl, i):
    s = sl[i]
    ci = rest_ims[hand[i]]
    return dict(name=hand[i], role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ci.width, h2=ci.height)


slot = 0
sl = FH.slots(n)
rest_cx, rest_cy, rest_ang = sl[slot]['cx'], sl[slot]['cy'], sl[slot]['ang']
for k in range(slot + 1, n):
    sl[k]['cx'] += OPEN
rest = np.zeros((Y1 - Y0, X1 - X0), bool)
prot = {}
for i in range(n):
    if i == slot:
        continue
    c = placed(sl, i)
    rest |= crop(RBC._placed_alpha(rest_ims[hand[i]], c['cx'], c['cy'], c['ang'], c['scale']))
    for kk, poly in RL.protected(c).items():
        prot['%s %s' % (hand[i], kk)] = crop(RC.poly_mask([poly]))
rest_bad = dict(r455=int((rest & r455).sum()), buttons=int((rest & BTN).sum()))
print('rest cards (open %d, buttons +%d):' % (OPEN, BDX), rest_bad, flush=True)
PRINTS = {'right (published)': ((0, 9), (0, 9)), 'under': ((0, 0), (0, 0)), 'down': ((9, 0), (9, 0))}
res = []
for pname, (po, do) in PRINTS.items():
    li = lift_img(hand[slot], po, do)
    for ang_name, ang in (('upright', 0.0), ('rest angle', rest_ang)):
        for dx in (0, 2, 4, -2, -4):
            ok, block, rows = [], {}, []
            for cy in np.arange(rest_cy - 40, rest_cy + 16, 1.0):
                lm = crop(RBC._placed_alpha(li, rest_cx + dx, cy, ang, RL.LIFT_ZOOM * FH.CARD_SCALE))
                bad = {}
                for kk, pm in prot.items():
                    v = int((lm & pm).sum())
                    if v:
                        bad[kk] = v
                for kk, m in (('buttons', BTN), ('r459', r459), ('arcs3', ARCS3)):
                    v = int((lm & m).sum())
                    if v:
                        bad[kk] = v
                low = int(np.nonzero((lm | rest).any(1))[0].max()) + Y0
                if low > 1067:
                    bad['bottom'] = low
                if not bad:
                    ok.append(float(cy))
                for b in bad:
                    block.setdefault(b, []).append(float(cy))
                rows.append(dict(cy=float(cy), bad=bad))
            rec = dict(print=pname, angle=ang_name, dx=dx, window=[min(ok), max(ok)] if ok else None,
                       blockers={kk: [min(v), max(v)] for kk, v in block.items()}, rest_cy=round(rest_cy, 2), rows=rows)
            res.append(rec)
            print('%-18s %-10s dx %+d window %s blockers %s' % (pname, ang_name, dx, rec['window'], rec['blockers']), flush=True)
os.makedirs(OUT, exist_ok=True)
json.dump(dict(rest=dict(cx=rest_cx, cy=rest_cy, ang=rest_ang), rest_bad=rest_bad, variants=res), open(OUT + 's0_scan.json', 'w'), indent=1)
print('written', flush=True)
