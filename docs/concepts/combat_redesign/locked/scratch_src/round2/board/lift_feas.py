"""C6 feasibility on board p2 (Trigger lifted out of slot 2): for each lifted-card print offset and lift zoom, the centre-y window where the
straight-up lift covers 0 px of every sibling's protected set (cost hex, title band, rules line, x3 plate), the buttons, the HUD (with
`clear` px under it) and r455, with the cards right of it opened by OPEN_PX.
python lift_feas.py <clear_px> <open_px> <btn_dx> <print_dx ...>"""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ.setdefault('CORP', 'neutral')
import numpy as np
import lw_render as LW
import f1_hand as FH
import card_render as CR
import rb_capture as RBC
import rb_checks as RC
import rb_lift as RL
import hud2, cv_lib
R = LW.R
J = R.A.J
clear, RL.OPEN_PX, bdx = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
pdx = [int(v) for v in sys.argv[4:]] or [-9, 9]
Lh = cv_lib.L2()
cv_lib.NOW['words'] = True
hud2.draw_hud(Lh, J['f2'], 'p2', None)
hud = np.asarray(Lh.done().split()[3]) >= 32
hud_d = hud.copy()
for d in range(1, clear + 1):
    hud_d[d:] |= hud[:-d]
M = RC.load_masks('p2')
btn = M.get('send', np.zeros((1080, 1920), bool)) | M.get('undo', np.zeros((1080, 1920), bool))
btn_s = np.zeros_like(btn)
btn_s[:, bdx:] = btn[:, :-bdx]
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
hand = list(J['f1']['hand'])
hov = hand.index('Trigger')
n = len(hand)
sl, _ = RL.layout(n, hov)
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
        prot['%s %s' % (nm, k)] = RC.poly_mask([poly])
print('rest hand min rho %.1f (HAND_MIN_R %.0f)' % (rho[rest].min(), FH.HAND_MIN_R))
out = {}
for p in pdx:
    CR.HOVER_PRINT_OFF[1] = p
    FH._mem.clear()
    lim = FH.card_hi(hand[hov], False, 'hover')
    for z in [float(v) for v in os.environ.get('ZOOMS', '1.0').split(',')]:
        clear_cy = []
        block = {}
        for cy in range(880, 600, -1):
            lm = RBC._placed_alpha(lim, sl[hov]['cx'], cy, 0.0, z * FH.CARD_SCALE)
            bad = [k for k, pm in prot.items() if (lm & pm).any()]
            if (lm & hud_d).any():
                bad.append('hud')
            if ((lm | rest) & btn_s).any():
                bad.append('buttons')
            if (lm & (rho < FH.HAND_MIN_R)).any():
                bad.append('r455')
            if not bad:
                clear_cy.append(cy)
            else:
                for b in bad:
                    block.setdefault(b, []).append(cy)
        rng = [min(clear_cy), max(clear_cy)] if clear_cy else None
        out['print %+d zoom %.2f' % (p, z)] = dict(clear_cy=rng, blockers={k: [min(v), max(v)] for k, v in block.items()})
        print('print %+d zoom %.2f clear cy %s  blockers %s' % (p, z, rng, {k: [min(v), max(v)] for k, v in block.items()}), flush=True)
json.dump(out, open('D:/rc_scratch/combat_redesign/locked/round2/board/work/lift_feas_c%d_o%d_b%d.json' % (clear, RL.OPEN_PX, bdx), 'w'), indent=1)
