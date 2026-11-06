"""lift_scan4.py (round 2 gate-1 fix, S2-1 / C6, second pass): the fan with PER-GAP offsets.
fix2's lift_scan3 found every slot 0-3 clear only with the fan's slot 0 moved 6-12 px right and the step shrunk evenly (STEP - D / 3).  That
even shrink closes the Spin 3 / Trigger gap by 3 px, and on the rest fan (p1, every hover plate) Trigger then covers the right end of Spin 3's
x3 plate (seen at 1x on the test render).  This scan keeps slot 3 where it is and moves slot 0 D px right, but splits D over the three gaps
(s01 + s12 + s23 = D), and adds the REST-vs-REST test: on the rest fan (no lift) every card's protected set (cost hex, title band, rules line,
xN plate, and here also the +N loud tab) must be 0 px under the cards drawn above it (higher slot index).
For every split: the rest coverage, and per slot 0-3 the clear centre-y window of the straight-up lift at open 36 / buttons +16 (same tests
as lift_scan3: siblings' protected sets, HUD 4 px, buttons 2 px, r459, 3 px off the slot's landing marks, lowest hand px <= 1067).
python lift_scan4.py -> ../work/lift_scan4.json, prints one line per split"""
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
import hud2, cv_lib
import a2_stick as AS
import f1_render as F1

OUT = 'D:/rc_scratch/combat_redesign/locked/round2/fix3/work/'
H, W = 1080, 1920
Y0, Y1, X0, X1 = 560, 1080, 850, 1800
R = LW.R
J = R.A.J
LEFT0, STEP0 = RL.FAN0['left'], RL.FAN0['step']      # the fan before rb_lift moved it (1035, 168)
OPEN, BDX = 36, 16


def npzmask(name, key):
    z = np.load('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.npz' % name)
    return np.unpackbits(z[key])[:H * W].reshape(H, W).astype(bool)


ARCS = {0: npzmask('h02_brace', 'Z__arcs'), 1: npzmask('h05_strike', 'Z__arcs'), 2: npzmask('h03_trigger', 'Z__arcs'),
        3: npzmask('h03_trigger', 'Z__arcs')}
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


BTN = buttons(BDX)
rest_ims = {nm: FH.card_hi(nm, False) for nm in hand}
CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = (0, 0)
CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = (0, 0)
FH._mem.clear()
lift_ims = {nm: FH.card_hi(nm, False, 'hover') for nm in hand}
FH._mem.clear()


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


def prot_ext(c):
    """rb_lift.protected plus the +N loud tab (card_render: the violet eye plate at CW - 54, 17, +-22 x +-14 design px)"""
    out = RL.protected(c)
    sp = CR.CARDS[c['name']]
    if sp.get('loud'):
        m2 = CR.margin_px(352)
        k = c['scale'] / 2.0
        W2, H2 = c['w2'] * k, c['h2'] * k
        a = math.radians(c['ang'])

        def tr(p):
            x, y = (m2 + 2 * p[0]) * k - W2 / 2, (m2 + 2 * p[1]) * k - H2 / 2
            return (c['cx'] + x * math.cos(a) + y * math.sin(a), c['cy'] - x * math.sin(a) + y * math.cos(a))
        lx = CR.CW - 54
        out['loud'] = [tr(p) for p in [(lx - 24, 1), (lx + 24, 1), (lx + 24, 33), (lx - 24, 33)]]
    return out


def fan(off):
    sl = FH.slots(n)
    for i, s in enumerate(sl):
        s['cx'] = LEFT0 + i * STEP0 + off[i]
    return sl


def placed(sl, i):
    s = sl[i]
    ci = rest_ims[hand[i]]
    return dict(name=hand[i], role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ci.width, h2=ci.height)


def rest_cover(sl, skip=None):
    """per card, px of its protected regions under the cards drawn above it (higher index), skipping the lifted slot"""
    al = {}
    for i in range(n):
        if i == skip:
            continue
        c = placed(sl, i)
        al[i] = crop(RBC._placed_alpha(rest_ims[hand[i]], c['cx'], c['cy'], c['ang'], c['scale']))
    out = {}
    for i in al:
        above = np.zeros_like(al[i])
        for j in al:
            if j > i:
                above |= al[j]
        for kk, poly in prot_ext(placed(sl, i)).items():
            px = int((crop(RC.poly_mask([poly])) & above).sum())
            if px:
                out['%s %s' % (hand[i], kk)] = px
    return out, al


CYREF = 900
splits = []
for D in (0, 6, 8, 9, 10, 12):
    for s12 in (0, 1):
        for s01 in range(0, D - s12 + 1):
            s23 = D - s12 - s01
            if s23 < 0:
                continue
            splits.append((D, s01, s12, s23))
res = []
for D, s01, s12, s23 in splits:
    off = [s01 + s12 + s23, s12 + s23, s23, 0]
    base = fan(off)
    rc, _ = rest_cover(base)
    rec = dict(D=D, gaps_shrink=[s01, s12, s23], off=off, rest_cover=rc, slots={})
    for slot in range(n):
        sl = fan(off)
        for k in range(slot + 1, n):
            sl[k]['cx'] += OPEN
        _, al = rest_cover(sl, skip=slot)
        rest = np.zeros((Y1 - Y0, X1 - X0), bool)
        prot = {}
        for i in al:
            rest |= al[i]
            for kk, poly in prot_ext(placed(sl, i)).items():
                prot['%s %s' % (hand[i], kk)] = crop(RC.poly_mask([poly]))
        rest_bad = dict(r455=int((rest & r455).sum()), buttons=int((rest & BTN).sum()))
        lm0 = crop(RBC._placed_alpha(lift_ims[hand[slot]], sl[slot]['cx'], CYREF, 0.0, RL.LIFT_ZOOM * FH.CARD_SCALE))
        ok, block = [], {}
        cys = range(940, 880, -1) if slot == 0 else range(760, 680, -1)
        for cy in cys:
            lm = vshift(lm0, cy - CYREF)
            bad = [kk for kk, pm in prot.items() if (lm & pm).any()]
            for kk, m in (('hud', hud_d), ('buttons', BTN), ('r459', r459), ('arcs3', ARCS3[slot])):
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
        rec['slots'][slot] = dict(window=[min(ok), max(ok)] if ok else None, rest=rest_bad,
                                  blockers={kk: [min(v), max(v)] for kk, v in block.items()} if not ok else {})
    allok = all(rec['slots'][s]['window'] for s in range(n)) and not rc
    rec['all_ok'] = allok
    res.append(rec)
    print('%s D %2d shrink %s off %s rest %s windows %s' % ('ALL' if allok else '   ', D, rec['gaps_shrink'], off, rc or 0,
                                                             {s: rec['slots'][s]['window'] for s in range(n)}), flush=True)
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(OUT + 'lift_scan4.json', 'w'), indent=1)
print('written', flush=True)
