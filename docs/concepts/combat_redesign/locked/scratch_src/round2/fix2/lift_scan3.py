"""lift_scan3.py (round 2 gate-1 fix, S2-1 / C6): every slot's lift over the fan geometry (shift / shrink), all print options, slots 0-3.
Knobs: fan shift D (slot 0 moves D px right, slot 3 stays: STEP' = STEP - D / 3), the lifted card's print / drop direction, OPEN_PX and BTN_DX.
For every combination: the clear centre-y window of a straight-up upright lift (0 px of every sibling's protected set, no hand px within 2 px
of the buttons, rest cards outside r455, the lifted card outside r459 and 3 px off h02's landing marks, 4 px under the p1 HUD, lowest hand
px <= 1067).  Also the slot-1 / slot-2 windows at the same fan (protected sets, buttons, HUD; arcs from h01 / h03).
python lift_scan2.py  -> work/lift_scan3.json"""
import sys, os, json
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
Y0, Y1, X0, X1 = 560, 1080, 850, 1800          # the scan window (everything the hand can reach)
R = LW.R
J = R.A.J


def npzmask(name, key):
    z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.npz' % name)
    return np.unpackbits(z[key])[:H * W].reshape(H, W).astype(bool)


ARCS = {0: npzmask('h02_brace', 'Z__arcs'), 1: npzmask('h05_strike', 'Z__arcs'), 2: npzmask('h03_trigger', 'Z__arcs'),
        3: npzmask('h04_twist', 'Z__arcs')}
ARCS3 = {k: ndi.binary_dilation(v, iterations=3)[Y0:Y1, X0:X1] for k, v in ARCS.items()}
Lh = cv_lib.L2()
cv_lib.NOW['words'] = True
hud2.draw_hud(Lh, J['f1'], 'p1', None)
hud = np.asarray(Lh.done().split()[3]) >= 32
hud_d = hud.copy()
for d in range(1, 5):
    hud_d[d:] |= hud[:-d]
hud_d = hud_d[Y0:Y1, X0:X1]
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - 536, yy - 540)
r455 = (rho < FH.HAND_MIN_R)[Y0:Y1, X0:X1]
r459 = (rho < FH.HAND_MIN_R + 4.0)[Y0:Y1, X0:X1]
hand = list(J['f1']['hand'])
n = len(hand)


def buttons(bdx):
    RL.BTN_DX = bdx
    F1.BTN_DX[0] = bdx
    im, (x0, y0) = FH.ui_img('send', False)
    btn = np.zeros((H, W), bool)
    a = np.asarray(im.split()[3]) >= 128
    btn[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a[:H - y0, :W - x0]
    lay, info = AS.stack_layer(True, {})
    a = np.asarray(lay.split()[3]) >= 128
    box = np.zeros_like(a)
    box[850:900, 1655 + bdx:1896 + bdx] = True
    btn |= a & box
    return ndi.binary_dilation(btn, iterations=2)[Y0:Y1, X0:X1]


BTN = {b: buttons(b) for b in (12, 16)}
rest_ims = {nm: FH.card_hi(nm, False) for nm in hand}


def crop(m):
    return m[Y0:Y1, X0:X1]


def vshift(m, dy):
    o = np.zeros_like(m)
    if dy > 0:
        o[dy:] = m[:-dy]
    elif dy < 0:
        o[:dy] = m[-dy:]
    else:
        o[:] = m
    return o


def fan(D, mode='shrink'):
    """shrink: slot 0 moves D right, slot 3 stays (STEP - D / 3); shift: every slot moves D right"""
    sl = FH.slots(n)
    step = FH.STEP - D / 3.0 if mode == 'shrink' else FH.STEP
    for i, s in enumerate(sl):
        s['cx'] = FH.LEFT_CX + D + i * step
    return sl


PRINTS = {'right': ((0, 9), (0, 9)), 'down': ((6, 0), (9, 0)), 'none': ((0, 0), (0, 0))}
LIM = {}
for pname, (po, do) in PRINTS.items():
    CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = po
    CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = do
    FH._mem.clear()
    LIM[pname] = {nm: FH.card_hi(nm, False, 'hover') for nm in hand}
FH._mem.clear()
res = []
CYREF = 900
for D, MODE in [(d, m) for m in ("shift", "shrink") for d in (0, 4, 6, 8, 9, 10, 12)]:
    for op in (24, 27, 30, 33, 36):
        for slot in (0, 1, 2, 3):
            sl = fan(D, MODE)
            for k in range(slot + 1, n):
                sl[k]['cx'] += op
            rest = np.zeros((Y1 - Y0, X1 - X0), bool)
            prot = {}
            for i, nm in enumerate(hand):
                if i == slot:
                    continue
                s = sl[i]
                ci = rest_ims[nm]
                c = dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ci.width, h2=ci.height)
                rest |= crop(RBC._placed_alpha(ci, c['cx'], c['cy'], c['ang'], c['scale']))
                for kk, poly in RL.protected(c).items():
                    prot['%s %s' % (nm, kk)] = crop(RC.poly_mask([poly]))
            for pname in PRINTS:
                if False:
                    continue
                lm0 = crop(RBC._placed_alpha(LIM[pname][hand[slot]], sl[slot]['cx'], CYREF, 0.0, RL.LIFT_ZOOM * FH.CARD_SCALE))
                for bdx in (16,):
                    rest_bad = dict(r455=int((rest & r455).sum()), buttons=int((rest & BTN[bdx]).sum()))
                    ok, block = [], {}
                    cys = range(940, 880, -1) if slot == 0 else range(760, 680, -1)
                    for cy in cys:
                        lm = vshift(lm0, cy - CYREF)
                        bad = [kk for kk, pm in prot.items() if (lm & pm).any()]
                        for kk, m in (('hud', hud_d), ('buttons', BTN[bdx]), ('r459', r459), ('arcs3', ARCS3[slot])):
                            if (lm & m).any():
                                bad.append(kk)
                        if rest_bad['r455'] or rest_bad['buttons']:
                            bad.append('rest')
                        low = int(np.nonzero((lm | rest).any(1))[0].max()) + Y0
                        if low > 1067:
                            bad.append('bottom')
                        if not bad:
                            ok.append(cy)
                        for b in bad:
                            block.setdefault(b, []).append(cy)
                    rec = dict(D=D, open=op, slot=slot, print=pname, btn_dx=bdx, ok=[min(ok), max(ok)] if ok else None, n_ok=len(ok),
                               rest=rest_bad, blockers={kk: [min(v), max(v)] for kk, v in block.items()})
                    res.append(rec)
                    print(('OK  ' if ok else 'no  ') + MODE + ' D %2d open %2d slot %d print %-5s btn %d window %s rest %s blockers %s' % (
                        D, op, slot, pname, bdx, rec['ok'], rest_bad, rec['blockers'] if not ok else ''), flush=True)
json.dump(res, open(OUT + 'lift_scan3.json', 'w'), indent=1)
print('written', flush=True)
