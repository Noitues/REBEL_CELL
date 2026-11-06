"""C6 on the hover set: for each hand slot, the centre-y window where the straight-up lift (rb_lift.layout: the fan keeps its slots, the
cards right of the hovered card open OPEN_PX, upright, zoom rb_lift.LIFT_ZOOM) covers 0 px of every sibling's protected set
(rb_lift.protected: cost hex, title band, rules line, xN plate), the HUD (+ CLEAR px under it), SEND IT / UNDO (+ BTN_GAP px, the column at
rb_lift.BTN_DX), r455 (every card) and r459 (the lifted card), and keeps the lowest hand pixel at y <= 1067.  The landing-arc gap and the
insets are plate-specific and are tested per plate by hv_comp / check e.
python lift_scan_hover.py <hud: p1|p2> <slot> [open_px ...]   -> round2/hover/work/lift_scan_<hud>_s<slot>.json"""
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
import hud2, cv_lib
import a2_stick as AS

OUT = 'D:/rc_scratch/combat_redesign/locked/round2/hover/work/'
CLEAR = 4            # px under the HUD (the board's p2 window used 4: round2/board/work/lift_feas_c4_o30_b12.json)
BTN_GAP = 2          # px between the hand and SEND IT / UNDO (hover check e)
LIFT_CLEAR = 4.0     # r455 + 4 for the lifted card (hover check e)
R = LW.R
J = R.A.J
if os.environ.get('BTN_DX'):                 # in-process only: the column offset to test (rb_lift reads its module global at call time)
    import f1_render as F1
    RL.BTN_DX = int(os.environ['BTN_DX'])
    F1.BTN_DX[0] = RL.BTN_DX
hud_kind, slot = sys.argv[1], int(sys.argv[2])
ops = [int(v) for v in sys.argv[3:]] or [RL.OPEN_PX]
Lh = cv_lib.L2()
cv_lib.NOW['words'] = True
hud2.draw_hud(Lh, J['f1' if hud_kind == 'p1' else 'f2'], hud_kind, None)
hud = np.asarray(Lh.done().split()[3]) >= 32
hud_d = hud.copy()
for d in range(1, CLEAR + 1):
    hud_d[d:] |= hud[:-d]
# the buttons as drawn on the plate (FH.ui_img('send') is already BTN_DX right; the stack layer's UNDO too)
im, (x0, y0) = FH.ui_img('send', False)
btn = np.zeros((1080, 1920), bool)
a = np.asarray(im.split()[3]) >= 128
btn[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a[:1080 - y0, :1920 - x0]
lay, info = AS.stack_layer(True, {})
a = np.asarray(lay.split()[3]) >= 128
box = np.zeros_like(a)
box[850:900, 1655 + RL.BTN_DX:1896 + RL.BTN_DX] = True
btn |= a & box
btn = ndi.binary_dilation(btn, iterations=BTN_GAP)
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
hand = list(J['f1']['hand'])
n = len(hand)
res = {}
for op in ops:
    RL.OPEN_PX = op
    sl, _ = RL.layout(n, slot)
    rest = np.zeros((1080, 1920), bool)
    prot = {}
    for i, nm in enumerate(hand):
        if i == slot:
            continue
        s = sl[i]
        ci = FH.card_hi(nm, False)
        c = dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ci.width, h2=ci.height)
        rest |= RBC._placed_alpha(ci, c['cx'], c['cy'], c['ang'], c['scale'])
        for k, poly in RL.protected(c).items():
            prot['%s %s' % (nm, k)] = RC.poly_mask([poly])
    rest_bad = dict(r455=int((rest & (rho < FH.HAND_MIN_R)).sum()), buttons=int((rest & btn).sum()),
                    low=int(np.nonzero(rest.any(1))[0].max()))
    lim = FH.card_hi(hand[slot], False, 'hover')
    ok_cy, block = [], {}
    for cy in range(912, 600, -1):
        lm = RBC._placed_alpha(lim, sl[slot]['cx'], cy, 0.0, RL.LIFT_ZOOM * FH.CARD_SCALE)
        bad = [k for k, pm in prot.items() if (lm & pm).any()]
        if (lm & hud_d).any():
            bad.append('hud')
        if (lm & btn).any():
            bad.append('buttons')
        if (lm & (rho < FH.HAND_MIN_R + LIFT_CLEAR)).any():
            bad.append('r459')
        if int(np.nonzero((lm | rest).any(1))[0].max()) > 1067:
            bad.append('bottom')
        if not bad:
            ok_cy.append(cy)
        for b in bad:
            block.setdefault(b, []).append(cy)
    runs = []
    for cy in sorted(ok_cy):
        if runs and cy == runs[-1][1] + 1:
            runs[-1][1] = cy
        else:
            runs.append([cy, cy])
    res['open %d' % op] = dict(card=hand[slot], slot_cx=sl[slot]['cx'], clear_windows=runs, rest=rest_bad,
                               blockers={k: [min(v), max(v), len(v)] for k, v in block.items()})
    print('slot', slot, hand[slot], 'hud', hud_kind, 'open', op, 'windows', runs, 'rest', rest_bad,
          'blockers', {k: [min(v), max(v)] for k, v in block.items()}, flush=True)
json.dump(res, open(OUT + 'lift_scan_%s_s%d_b%d.json' % (hud_kind, slot, RL.BTN_DX), 'w'), indent=1)
