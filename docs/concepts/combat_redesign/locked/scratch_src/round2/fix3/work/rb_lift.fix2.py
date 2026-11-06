"""rb_lift (2026-11-04 round 2, call C6 / review 2.6, h02 and N1; reviewer's option (a)): THE hand lift, shared by the board (p2) and the hover
set.  Rules:
  - the fan keeps its slot positions; the hovered card lifts straight up (its slot's x, upright, at LIFT_ZOOM of the hand scale) and is drawn
    on top of the hand;
  - the fan never closes over its neighbours: the cards LEFT of the hovered card never move; the cards RIGHT of it may only open (move right)
    by OPEN_PX, so the lifted card covers nothing of them;
  - the UNDO / SEND IT column moves BTN_DX right on every plate (option (a): 12-16 px, there is room to the screen edge), so the opened fan
    never touches it;
  - every sibling's protected set is its cost hex, title band, rules line and multiplier plate: 0 px of it is covered by the lifted card
    (rb_checks e).
  LIFT_CY[slot] is the lifted card's centre y per hand slot: as low as the left neighbour's protected set allows (searched below), never
  above the HUD.
python rb_lift.py search [slot ...]      offline search (card alphas and the HUD layer only, no board render): per slot, the lowest centre y
                                         and the smallest opening with 0 px on every protected set, the buttons, r455 and the HUD"""
import sys, os, json, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

LIFT_ZOOM = 1.0                    # the lifted card's scale over the hand scale (round 1: 1.10).  Board p2 lifts Trigger out of slot 2 under the
                                   # p2 HUD with its reserved option rows (C8): at 1.10 no centre y clears Spin3's x3 plate (top y 861) and stays
                                   # under the HUD; under 0.99 the lifted card's rules line drops under the 16 px cap height (check c)
# 2026-11-04 round 2, gate-1 fix (S2-1: h02 x4, the slot-0 Brace lift covered Spin 3's cost hex and title band; S3: the button column sat
# 12 px right on the board and 16 px on the hover plates).  One geometry for the board and the hover set, from the scan
# round2/fix2/lift_scan3.py (logs/lift_scan3.log): every slot 0-3 has a clear window with
#   - the fan's slot 0 FAN_D0 px right and its last slot where it was (STEP - FAN_D0 / 3): the slot-0 lift needs that room to clear the
#     lane-470 landing marks by 3 px (at FAN_D0 0 no centre y clears them);
#   - the lifted card's pink print and hard drop under the card (no lateral offset): to the right they added ~10 px over the right neighbour,
#     which needed a 43 px opening for slot 0, past the buttons;
#   - one opening (36) and one button column (16 px right) on every plate: SEND IT's alpha ends at x 1917 (16) and is clipped by the screen
#     edge at 20, so the column cannot move further.
# Windows (centre y): slot 0 920-924, slot 1 714-758, slot 2 714-721, slot 3 714-760.
LIFT_CY = {0: 922, 1: 718, 2: 718, 3: 718}   # per hand slot (slot 0 rises 12 px: its top corner meets r459 and the landing marks above that)
OPEN_PX = 36                       # the cards right of the lifted card open this far (never close)
BTN_DX = 16                        # UNDO / SEND IT column, px right, on every plate (option (a): 12-16)
FAN_D0 = 9                         # the fan's slot 0 moves this far right; the last slot stays (f1_hand STEP 168 -> 165)
PRINT_OFF = (0, 0)                 # the lifted card's pink print, (down, right) design px: under the card.  Round 1 (6, -9); round 2 board (0, 9)
DROP_OFF = (0, 0)                  # its hard drop, under the card.  Round 1 (11, 7); round 2 board (0, 9).  The lift reads by its height, its
                                   # full value over the 88 % rest of the hand and the soft LIFT_SHADOW
LIFT_SHADOW = dict(off=(6, 12), blur=10)
INFO = {}


def protected(card):
    """the protected regions of a placed card in screen px: cost hex, title band, rules line and (Nudge / Spin) the multiplier plate"""
    import card_render as CR
    import rb_checks as RC
    sp = CR.CARDS[card['name']]
    cost, rules = RC.card_regions(card)
    m2 = CR.margin_px(352)
    k = card['scale'] / 2.0
    W2, H2 = card['w2'] * k, card['h2'] * k
    a = math.radians(card['ang'])

    def tr(p):
        x, y = (m2 + 2 * p[0]) * k - W2 / 2, (m2 + 2 * p[1]) * k - H2 / 2
        return (card['cx'] + x * math.cos(a) + y * math.sin(a), card['cy'] - x * math.sin(a) + y * math.cos(a))
    out = dict(cost=cost, rules=rules, title=[tr(p) for p in [(0, 124), (CR.CW, 124), (CR.CW, 166), (0, 166)]])
    if sp.get('mult'):
        out['mult'] = [tr(p) for p in [(110, 88), (166, 88), (166, 126), (110, 126)]]
    return out


def layout(n, hov, played_n=0):
    """slot dicts for an n-card row (hand + played) with card `hov` lifted: rest cards keep their slots, the cards right of it open OPEN_PX"""
    import f1_hand as FH
    sl = FH.slots(n)
    if hov is None:
        return sl, None
    for k in range(hov + 1, n):
        sl[k]['cx'] += OPEN_PX
    s = sl[hov]
    lift = dict(cx=s['cx'], cy=LIFT_CY.get(hov, LIFT_CY[2]), ang=0.0, scale=LIFT_ZOOM * FH.CARD_SCALE)
    return sl, lift


FAN0 = {}


def install(R, A):
    import f1_hand as FH
    import lw_ui as LU
    from PIL import Image as _I
    FH.LIFT_S = LIFT_ZOOM
    if not FAN0:                   # the fan (rb2_patch: LEFT_CX 1035, STEP 168): slot 0 FAN_D0 right, the last slot (n = 4) unchanged
        FAN0.update(left=FH.LEFT_CX, step=FH.STEP)
        FH.LEFT_CX = FAN0['left'] + FAN_D0
        FH.STEP = FAN0['step'] - FAN_D0 / 3.0
    import card_render as CR
    CR.HOVER_PRINT_OFF[0], CR.HOVER_PRINT_OFF[1] = PRINT_OFF
    CR.HOVER_DROP_OFF[0], CR.HOVER_DROP_OFF[1] = DROP_OFF
    FH._mem.clear()

    def draw_hand(base, J, beat, nw=False, lift=None, dim_others=None):
        """the one hand: rest cards in their fan slots, played slots upright (2.3), the hovered / previewed card straight up (C6)"""
        hand, played, hov = FH.hand_lists(J, beat)
        if lift is not None:
            hov = hand.index(lift)
        n = len(hand) + len(played)
        sl, L = layout(n, hov, len(played))
        for i, nm in enumerate(hand):
            if i == hov:
                continue
            s = sl[i]
            ci = FH.card_hi(nm, nw)
            a_ = np.asarray(ci).astype(np.float32)
            a_[..., :3] *= FH.REST_V * (dim_others or 1.0)
            FH.put(base, _I.fromarray(a_.astype(np.uint8), 'RGBA'), s['cx'], s['cy'], s['ang'], FH.CARD_SCALE)
        for j, nm in enumerate(played):
            s = sl[len(hand) + j]
            FH.put(base, FH.played_slot(nm, nw), s['cx'], s['cy'], 0.0, FH.CARD_SCALE, shadow=False)
        if hov is not None:
            im = FH.card_hi(hand[hov], nw, 'hover')
            FH.put(base, im, L['cx'], L['cy'], 0, L['scale'], shadow=True, **LIFT_SHADOW)
            INFO['lift'] = dict(card=hand[hov], slot=hov, **{k: round(v, 2) for k, v in L.items()}, open_px=OPEN_PX, zoom=LIFT_ZOOM)
        return sl
    FH.draw_hand = draw_hand
    # the UNDO / SEND IT column (and the hint line under it) moves BTN_DX right
    _oui = FH.ui_img

    def ui_img(kind, nw, f=None, seed=0):
        im, (x0, y0) = _oui(kind, nw, f, seed)
        if kind == 'send':
            return im, (x0 + BTN_DX, y0)
        return im, (x0, y0)
    FH.ui_img = ui_img
    import a2_stick as AS
    import f1_render as F1
    F1.BTN_DX[0] = BTN_DX
    _ost = AS.stack_layer

    def stack_layer(words, sel):
        """the stack layer (the paper UNDO that lw_render puts in, and the hint line under SEND IT) moves with the column; f1_render's keep
        boxes move by F1.BTN_DX"""
        lay, info = _ost(words, sel)
        if BTN_DX > 0:
            a = np.asarray(lay).copy()
            x0 = 1600
            a[:, x0 + BTN_DX:] = a[:, x0:-BTN_DX].copy()
            a[:, x0:x0 + BTN_DX] = 0
            lay = _I.fromarray(a, 'RGBA')
        return lay, info
    AS.stack_layer = stack_layer


# ------------------------------------------------------------------------------------------------ offline search
def _search(slots_wanted):
    os.environ.setdefault('CORP', 'neutral')
    import lw_render as LW
    import f1_hand as FH
    import rb_capture as RBC
    import rb_checks as RC
    import hud2
    import cv_lib
    R = LW.R
    J = R.A.J
    # the p2 HUD layer (the tallest decide HUD: bill with its reserved rows, WIN, RAM and the REFUND tab)
    Lh = cv_lib.L2()
    cv_lib.NOW['words'] = True
    hud2.draw_hud(Lh, J['f2'], 'p2', None)
    hud = np.asarray(Lh.done().split()[3]) >= 32
    import hud_rows
    print('HUD bottom', hud_rows.ROWS.get('hud_bottom'), 'hud mask y max', int(np.nonzero(hud.any(1))[0].max()), flush=True)
    hud_d = np.zeros_like(hud)
    hud_d[8:] = hud[:-8]                         # 8 px clearance under the HUD
    hud_d |= hud
    for d in range(1, 9):
        hud_d[d:] |= hud[:-d]
    M = RC.load_masks('p2')
    btn = M.get('send', np.zeros((1080, 1920), bool)) | M.get('undo', np.zeros((1080, 1920), bool))
    yy, xx = np.mgrid[0:1080, 0:1920]
    rho = np.hypot(xx - 536, yy - 540)
    hand = list(J['f1']['hand'])
    n = len(hand)
    ims = {nm: FH.card_hi(nm, False) for nm in hand}
    lims = {nm: FH.card_hi(nm, False, 'hover') for nm in hand}
    global OPEN_PX
    res = {}
    r455 = rho < FH.HAND_MIN_R + 3
    CY0 = 780

    def vshift(m, dy):
        o = np.zeros_like(m)
        if dy > 0:
            o[dy:] = m[:-dy]
        elif dy < 0:
            o[:dy] = m[-dy:]
        else:
            o[:] = m
        return o
    zooms = [LIFT_ZOOM] + [z for z in (1.05, 1.10) if z != LIFT_ZOOM]
    for hov in slots_wanted:
        best = None
        diag = {}
        for zoom in zooms:
            lm0 = RBC._placed_alpha(lims[hand[hov]], FH.slots(n)[hov]['cx'], CY0, 0.0, zoom * FH.CARD_SCALE)
            for op in range(0, 41, 2):
                OPEN_PX = op
                sl, Lf = layout(n, hov)
                rest = np.zeros((1080, 1920), bool)
                prot = {}
                for i, nm in enumerate(hand):
                    if i == hov:
                        continue
                    s = sl[i]
                    c = dict(name=nm, role='rest', cx=s['cx'], cy=s['cy'], ang=s['ang'], scale=FH.CARD_SCALE, w2=ims[nm].width, h2=ims[nm].height)
                    rest |= RBC._placed_alpha(ims[nm], c['cx'], c['cy'], c['ang'], c['scale'])
                    for k, poly in protected(c).items():
                        prot['%s %s' % (nm, k)] = RC.poly_mask([poly])
                for bdx in (12, 14, 16):
                    btn_s = np.zeros_like(btn)
                    btn_s[:, bdx:] = btn[:, :-bdx]
                    found = None
                    for cy in range(870, 640, -2):
                        lm = vshift(lm0, cy - CY0)
                        allm = lm | rest
                        bad = {}
                        for k, pm in prot.items():
                            v = int((lm & pm).sum())
                            if v:
                                bad[k] = v
                        for k, m, src in (('buttons', btn_s, allm), ('r455', r455, allm), ('hud', hud_d, lm)):
                            v = int((src & m).sum())
                            if v:
                                bad[k] = v
                        low = int(np.nonzero(allm.any(1))[0].max())
                        if low > 1067:
                            bad['bottom'] = low
                        if not bad:
                            found = (cy, low, int(np.nonzero(lm.any(1))[0].min()))
                            break
                        diag[(zoom, op, bdx)] = (cy, bad)
                    if found:
                        cand = (op, bdx, -found[0], dict(slot=hov, card=hand[hov], zoom=zoom, cy=found[0], open_px=op, btn_dx=bdx,
                                                       lift_top=found[2], lowest=found[1]))
                        if best is None or cand[:3] < best[:3]:
                            best = cand
                        break
                if best is not None and best[0] == op:
                    break
            res['slot%d_zoom%.2f' % (hov, zoom)] = best[3] if best else dict(slot=hov, zoom=zoom, feasible=False,
                                                                          last_blockers={str(k): v[1] for k, v in list(diag.items())[-3:]})
            print('slot', hov, hand[hov], 'zoom', zoom, '->', res['slot%d_zoom%.2f' % (hov, zoom)], flush=True)
            best = None
    return res


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'search':
        want = [int(v) for v in sys.argv[2:]] or [0, 1, 2, 3]
        out = _search(want)
        json.dump(out, open('D:/rc_scratch/combat_redesign/locked/round2/board/work/lift_search.json', 'w'), indent=1)
