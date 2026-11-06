"""lift_scan_s0.py (round 2 gate-1 fix, S2-1 / C6 / N1): the slot-0 (Brace) lift on h02, scanned over the knobs the lift has:
  print / drop offset of the lifted card (card_render.HOVER_PRINT_OFF / HOVER_DROP_OFF, design px (down, right)),
  OPEN_PX (cards right of the lift open), BTN_DX (UNDO / SEND IT column), and the lift's centre y.
Constraints (hover check e, rb_checks e): 0 px of every sibling's protected set (cost hex, title band, rules line, xN plate) under the lifted
card; no hand px within 2 px of SEND IT / UNDO; rest cards outside r455; lifted card outside r459 and 3 px off the landing marks (h02's
Z__arcs mask from the round-2 hover chk); lifted card 4 px under the HUD; lowest hand px <= y 1067.
Also reports SEND IT's alpha right edge per BTN_DX.
python lift_scan_s0.py  -> work/lift_scan_s0.json"""
import sys, os, json, itertools
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
import hud2, cv_lib
import a2_stick as AS
import f1_render as F1

OUT = 'D:/rc_scratch/combat_redesign/locked/round2/fix2/work/'
H, W = 1080, 1920
R = LW.R
J = R.A.J
z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/h02_brace.npz')
arcs = np.unpackbits(z['Z__arcs'])[:H * W].reshape(H, W).astype(bool)
arcs3 = ndi.binary_dilation(arcs, iterations=3)
Lh = cv_lib.L2()
cv_lib.NOW['words'] = True
hud2.draw_hud(Lh, J['f1'], 'p1', None)
hud = np.asarray(Lh.done().split()[3]) >= 32
hud_d = hud.copy()
for d in range(1, 5):
    hud_d[d:] |= hud[:-d]
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - 536, yy - 540)
hand = list(J['f1']['hand'])
n = len(hand)
slot = 0


def buttons(bdx):
    RL.BTN_DX = bdx
    F1.BTN_DX[0] = bdx
    im, (x0, y0) = FH.ui_img('send', False)
    btn = np.zeros((H, W), bool)
    a = np.asarray(im.split()[3]) >= 128
    btn[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a[:H - y0, :W - x0]
    send_right = int(np.nonzero(btn.any(0))[0].max())
    lay, info = AS.stack_layer(True, {})
    a = np.asarray(lay.split()[3]) >= 128
    box = np.zeros_like(a)
    box[850:900, 1655 + bdx:1896 + bdx] = True
    undo = a & box
    undo_right = int(np.nonzero(undo.any(0))[0].max()) if undo.any() else None
    btn |= undo
    return ndi.binary_dilation(btn, iterations=2), send_right, undo_right


BTN = {b: buttons(b) for b in (12, 16, 20, 24)}
rest_ims = {nm: FH.card_hi(nm, False) for nm in hand}
res = dict(send_right={b: v[1] for b, v in BTN.items()}, undo_right={b: v[2] for b, v in BTN.items()}, runs=[])
print('SEND IT alpha right edge per BTN_DX', res['send_right'], 'UNDO', res['undo_right'], flush=True)
PRINTS = {'right(0,9)': ((0, 9), (0, 9)), 'none(0,0)': ((0, 0), (0, 0)), 'down(6,0)/(9,0)': ((6, 0), (9, 0)),
          'left(6,-9)/(11,-7)': ((6, -9), (11, -7)), 'left(0,-9)': ((0, -9), (0, -9)), 'downleft(4,-5)/(8,-4)': ((4, -5), (8, -4))}
for pname, (po, do) in PRINTS.items():
    CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = po
    CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = do
    FH._mem.clear()
    lim = FH.card_hi(hand[slot], False, 'hover')
    for ang_kind in ('upright', 'fan'):
        for op in (30, 34, 36, 38, 40, 42, 44):
            RL.OPEN_PX = op
            sl, _ = RL.layout(n, slot)
            ang = 0.0 if ang_kind == 'upright' else sl[slot]['ang']
            rest = np.zeros((H, W), bool)
            prot = {}
            for i, nm in enumerate(hand):
                if i == slot:
                    continue
                s = sl[i]
                ci = rest_ims[nm]
                c = dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ci.width, h2=ci.height)
                rest |= RBC._placed_alpha(ci, c['cx'], c['cy'], c['ang'], c['scale'])
                for k, poly in RL.protected(c).items():
                    prot['%s %s' % (nm, k)] = RC.poly_mask([poly])
            for bdx in (12, 16, 20, 24):
                btn = BTN[bdx][0]
                rest_btn = int((rest & btn).sum())
                ok, block = [], {}
                for cy in range(930, 880, -1):
                    lm = RBC._placed_alpha(lim, sl[slot]['cx'], cy, ang, RL.LIFT_ZOOM * FH.CARD_SCALE)
                    bad = {k: int((lm & pm).sum()) for k, pm in prot.items() if (lm & pm).any()}
                    for k, m in (('hud', hud_d), ('buttons', btn), ('r459', rho < FH.HAND_MIN_R + 4.0), ('arcs3', arcs3)):
                        v = int((lm & m).sum())
                        if v:
                            bad[k] = v
                    if rest_btn:
                        bad['rest_buttons'] = rest_btn
                    low = int(np.nonzero((lm | rest).any(1))[0].max())
                    if low > 1067:
                        bad['bottom'] = low
                    if not bad:
                        ok.append(cy)
                    for b in bad:
                        block.setdefault(b, []).append(cy)
                rec = dict(print=pname, ang=ang_kind, open=op, btn_dx=bdx, ok=sorted(ok), rest_buttons=rest_btn,
                           blockers={k: [min(v), max(v)] for k, v in block.items()})
                res['runs'].append(rec)
                if ok:
                    print('OK', pname, ang_kind, 'open', op, 'btn', bdx, 'cy', min(ok), '-', max(ok), flush=True)
            print('done', pname, ang_kind, 'open', op, 'last blockers', rec['blockers'], flush=True)
json.dump(res, open(OUT + 'lift_scan_s0.json', 'w'), indent=1)
print('written', flush=True)
