"""probe: hand slot geometry, card sizes, protected sets, HUD registry boxes on the round-2 board (p1 HUD), R.AS identity"""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
import lw_render as LW
import f1_hand as FH
import rb_lift as RL
import hud_rows as HR
import hud2, obj2, cv_lib
import a2_stick as AS
R = LW.R
J = R.A.J
print('R is', R.__name__, 'R.AS is a2_stick:', R.AS is AS)
print('slots(4)', [{k: round(v, 1) for k, v in s.items()} for s in FH.slots(4)])
print('CARD_SCALE', FH.CARD_SCALE, 'LIFT_S', FH.LIFT_S, 'REST_V', FH.REST_V, 'HAND_MIN_R', FH.HAND_MIN_R)
print('RL', RL.LIFT_ZOOM, RL.LIFT_CY, RL.OPEN_PX, RL.BTN_DX, RL.PRINT_OFF, RL.DROP_OFF)
for nm in J['f1']['hand']:
    im = FH.card_hi(nm, False)
    hv = FH.card_hi(nm, False, 'hover')
    print(nm, 'normal', im.size, 'hover', hv.size)
for beat, fk in (('p1', 'f1'), ('p2', 'f2')):
    L = cv_lib.L2()
    cv_lib.NOW['words'] = True
    hud2.draw_hud(L, J[fk], beat, None)
    a = np.asarray(L.done().split()[3]) >= 32
    ys = np.nonzero(a.any(1))[0]
    print(beat, 'HUD rows', dict(HR.ROWS), 'alpha y', int(ys.min()), int(ys.max()))
    print(beat, 'regs', {k: hud2.R.get(k) for k in ('bill_frame', '_column', '_bill_room')}, {k: obj2.R.get(k) for k in ('obj_plate', 'res_plate', 'refund_tab')})
    xs = np.nonzero(a.any(0))[0]
    print(beat, 'alpha x', int(xs.min()), int(xs.max()))
im, (x0, y0) = FH.ui_img('send', False)
print('send img', im.size, (x0, y0))
lay, info = AS.stack_layer(True, {})
aa = np.asarray(lay.split()[3]) >= 128
ys, xs = np.nonzero(aa[840:910, 1600:1920])
print('undo alpha box', int(xs.min()) + 1600, int(ys.min()) + 840, int(xs.max()) + 1600, int(ys.max()) + 840)
ys, xs = np.nonzero(aa[1020:1070, 1600:1920])
if len(xs):
    print('hint alpha box', int(xs.min()) + 1600, int(ys.min()) + 1020, int(xs.max()) + 1600, int(ys.max()) + 1020)
