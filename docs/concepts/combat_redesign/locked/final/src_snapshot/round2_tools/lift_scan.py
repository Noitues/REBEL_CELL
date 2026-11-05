"""C6 diagnostic: for one hand slot, zoom and opening, print what blocks the straight-up lift at each centre y (protected sets of each
sibling, the buttons, r455, the p2 HUD with 8 px clearance, the plate bottom).
python lift_scan.py <slot> <zoom> <open_px> [btn_dx] [cy_hi cy_lo step]"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
import lw_render as LW
import f1_hand as FH
import rb_capture as RBC
import rb_checks as RC
import rb_lift as RL
import hud2, cv_lib, hud_rows
R = LW.R
J = R.A.J
hov = int(sys.argv[1])
zoom = float(sys.argv[2])
RL.OPEN_PX = int(sys.argv[3])
bdx = int(sys.argv[4]) if len(sys.argv) > 4 else 14
hi, lo, st = (int(v) for v in sys.argv[5:8]) if len(sys.argv) > 7 else (880, 700, 10)
Lh = cv_lib.L2()
cv_lib.NOW['words'] = True
hud2.draw_hud(Lh, J['f2'], 'p2', None)
hud = np.asarray(Lh.done().split()[3]) >= 32
hud_d = hud.copy()
for d in range(1, 9):
    hud_d[d:] |= hud[:-d]
ys, xs = np.nonzero(hud)
print('HUD x %d-%d y %d-%d rows %s' % (xs.min(), xs.max(), ys.min(), ys.max(), {k: v for k, v in hud_rows.ROWS.items() if not isinstance(v, (list, dict))}))
M = RC.load_masks('p2')
btn = M.get('send', np.zeros((1080, 1920), bool)) | M.get('undo', np.zeros((1080, 1920), bool))
btn_s = np.zeros_like(btn)
btn_s[:, bdx:] = btn[:, :-bdx]
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
hand = list(J['f1']['hand'])
n = len(hand)
sl, Lf = RL.layout(n, hov)
print('slots', [(round(s['cx'], 1), round(s['cy'], 1), round(s['ang'], 1)) for s in sl], 'hand', hand)
rest = np.zeros((1080, 1920), bool)
prot = {}
for i, nm in enumerate(hand):
    if i == hov:
        continue
    s = sl[i]
    im = FH.card_hi(nm, False)
    c = dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=im.width, h2=im.height)
    rest |= RBC._placed_alpha(im, c['cx'], c['cy'], c['ang'], c['scale'])
    for k, poly in RL.protected(c).items():
        pm = RC.poly_mask([poly])
        prot['%s %s' % (nm, k)] = pm
        ys_, xs_ = np.nonzero(pm)
        print('  protected %-16s x %4d-%4d y %4d-%4d' % (nm + ' ' + k, xs_.min(), xs_.max(), ys_.min(), ys_.max()))
lim = FH.card_hi(hand[hov], False, 'hover')
for cy in range(hi, lo - 1, -st):
    lm = RBC._placed_alpha(lim, sl[hov]['cx'], cy, 0.0, zoom * FH.CARD_SCALE)
    allm = lm | rest
    bad = {k: int((lm & pm).sum()) for k, pm in prot.items() if (lm & pm).any()}
    for k, m, src in (('buttons', btn_s, allm), ('r455', rho < FH.HAND_MIN_R + 3, allm), ('hud', hud_d, lm)):
        v = int((src & m).sum())
        if v:
            bad[k] = v
    low = int(np.nonzero(allm.any(1))[0].max())
    ly, lx = np.nonzero(lm)
    print('cy %d lift x %d-%d y %d-%d low %d  %s' % (cy, lx.min(), lx.max(), ly.min(), ly.max(), low, bad or 'CLEAR'), flush=True)
