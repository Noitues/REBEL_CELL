"""hv_core: the hover plates on the REBUILT board, ROUND 2 (2026-11-04; R1_REREVIEW build order steps 3-4, the hover stage).
A copy of locked/rebuild/hover/src/hv_core.py (round 1) moved onto the round-2 board.  The one generator (corp/src) is imported READ-ONLY
through hz_core; every change below is an in-process patch or a primitive in this file.  Nothing under corp/src is written.

Round 2 (art-pass calls C1, C2, C6, C8 of locked/REVIEW_RESPONSE.md "Round 2"):
  C1  THE pencil is corp/src rb_pencil.wax_stroke, the board's one drawer (it is round 1's hv_core stroke, moved there): 7 px PLAN wax, a 3 px ink
      edge each side, wax grain (8 % value noise, darkens only) with drag streaks and a ragged edge, round caps, no glow.  wax_stroke here only
      collects its masks and coverage for the hover checks.  Long marks keep the full width (A.5).
  C2  THE FOCUS drawer is corp/src rb_focus.draw (FOCUS #D4FF00, four separate corners, 2 px legal / 3.5 px aimed, ink + 3.2 px); ring-tag FOCUS
      uses rb_focus.rect (12 px legs; round 1 used 10)
  C8  THE HUD grid is corp/src hud_rows (the board HUD reserves the option rows at all times): this file no longer adds its own ring room or
      patches bill_box / hero_pair / the YOU strip.  h04's option rows are drawn into the reserved slots through hud_rows.OPT['draw']
  C6  THE lift is corp/src rb_lift.layout (hv_comp)
Kept from round 1: the L5 arrowed outline in wax (16 px channel, two 3 px edges, 10 px chevrons at a 24 px pitch, filled head), real pencil
rings round the hero digits (no brackets), the YOU underline, one RAM treatment (3.9).
Env CORP=neutral|solace|meridian selects the skin (lw_render, at import)."""
import sys, os, math, json, copy, hashlib
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
os.chdir(SRC)
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy import ndimage as ndi
import hz_core as Z
Z.HERE = HERE
from hz_core import R, A, FH, HL, C, W, H, L2, ppx, NOW, CB, RA, AU, hud2, MASKS, LOGD, HS, M2m, P2m, H2m
import rb_tokens as T
import rb2_patch as RB2
import rb3_patch as RB3
import rb_checks as RC
import rb_capture as RBC
import obj2
import rb_pencil as PENM
import rb_focus as FOC
import hud_rows as HR
import rb_lift as RL

# ------------------------------------------------------------------------------------------------ C6: the lift constants the hover needs
# The board stage set rb_lift.BTN_DX 12 and OPEN_PX 30 for its one lift (p2, slot 2).  A slot-1 lift (h01 Spin 3, h05-h09) clears Trigger's cost
# hex only when the cards right of it open 36 px, and then Twist keeps 2 px off UNDO only with the column 16 px right (the call allows 12-16).
# So the hover set runs rb_lift with BTN_DX 16 and OPEN_PX 36 (in-process; corp/src rb_lift.py is NOT edited: the board must take the same two
# numbers, NOTES "corp/src change").  lift_scan_hover.py measured both.
# 2026-11-04 round 2 gate-1 fix (S3 "the button column moves on hover", S2-1 h02): corp/src rb_lift now holds the one geometry for the board
# and the hover set (BTN_DX 16, OPEN_PX 36, LIFT_CY per slot, the fan offsets FAN_OFF (8, 3, 3, 0), the print and drop under the card).  The hover
# reads it; it sets nothing of its own.
HOVER_BTN_DX = RL.BTN_DX
HOVER_OPEN_PX = RL.OPEN_PX
import f1_render as _F1
assert _F1.BTN_DX[0] == RL.BTN_DX, 'rb_lift.install must have set the column'

# ------------------------------------------------------------------------------------------------ the hover hit bursts (gate-1 fix, C3)
# hz_core.pink_burst drew a white (L* 100) core: unclassed pure white above the HOT reference on h03 / h05 / h09.  The core is HIT_PAPER, the
# board's gun hit star value (L* 86, A.1), so the burst sits under the HOT marks like every other X / P mark on the board.
HIT_CORE = tuple(T.HIT_PAPER)


def pink_burst(L, x, y, r=22, seed=1):
    HL.starburst(L, x, y, r, Z.PINK, HIT_CORE, 11, 2.6, seed)


Z.pink_burst = pink_burst

# ------------------------------------------------------------------------------------------------ the REFUND tab clears the lifted card
# rb2_patch hangs the REFUND tab (REFUND_TAB_W wide) centred under the refunded RAM coin; hud_rows sized it so "its right edge clears the lifted
# card's left edge" for the board's one case (p2: coin 3, tab x 1172-1268, Trigger lifted from slot 2 at x 1271).  h03 refunds coin 4 (x 1252):
# centred, the tab ran to x 1300 and the lifted Trigger covered 899 px of it ("REFUN").  The same rule, generalised: when the lifted card rises
# into the tab's rows, the tab slides left until its right edge is REFUND_TAB_CLEAR px off the card, with its hanging line still inside it
# (REFUND_TAB_HANG_IN px from either end).  On p2 this moves nothing.  TAB is set per plate (hv_plates.make) before the board is drawn.
REFUND_TAB_CLEAR = 4
REFUND_TAB_HANG_IN = 8
TAB = {'lift_left': None, 'lift_top': None, 'shift': 0.0}


def _install_refund_tab():
    from cv_lib import NOW as _NOW
    rr = hud2.ram_row
    fv = dict(zip(rr.__code__.co_freevars, (c.cell_contents for c in (rr.__closure__ or ()))))
    if '_orr' not in fv:
        raise RuntimeError('rb2_patch resources_row not found under hud2.ram_row (its wrapped original _orr is the RAM row draw)')
    _orr = fv['_orr']

    def resources_row(L, f, y):
        """rb2_patch resources_row (the REFUND tab under the refunded coin, hanging line, plate, word / coin) with the lift clearance above"""
        yb = _orr(L, f, y)
        bx = obj2.R.get('ram_refund')
        TAB['shift'] = 0.0
        if not f.get('refunds') or bx is None:
            return yb
        cx = (bx[0] + bx[2]) / 2
        t0 = yb + RB2.REFUND_TAB_GAP
        x0, x1 = cx - RB2.REFUND_TAB_W / 2, cx + RB2.REFUND_TAB_W / 2
        lx, lt = TAB.get('lift_left'), TAB.get('lift_top')
        if lx is not None and lt is not None and lt < t0 + RB2.REFUND_TAB_H + REFUND_TAB_CLEAR and x1 > lx - REFUND_TAB_CLEAR:
            dx = x1 - (lx - REFUND_TAB_CLEAR)
            if x0 - dx + REFUND_TAB_HANG_IN <= cx <= x1 - dx - REFUND_TAB_HANG_IN:
                x0, x1 = x0 - dx, x1 - dx
                TAB['shift'] = round(-dx, 2)
        box = (x0, t0, x1, t0 + RB2.REFUND_TAB_H)
        L.line([(cx, yb - 2), (cx, t0 + 2)], hud2.CYAN, 2.0)
        hud2.P(L, box, 'plate')
        if _NOW['words']:
            hud2.txt(L, (x0 + x1) / 2, t0 + RB2.REFUND_TAB_H / 2, 'REFUND', hud2.LBL_PX, hud2.CYAN, 'mono', 'mm', hud2.LBL_TRK)
        else:
            hud2.coin(L, (x0 + x1) / 2, t0 + RB2.REFUND_TAB_H / 2, 18, True)
        obj2.R['refund_tab'] = box
        return t0 + RB2.REFUND_TAB_H
    obj2.resources_row = resources_row
    hud2.ram_row = resources_row


_install_refund_tab()

PLAN = tuple(T.TOKENS['PLAN'])
FOCUS = tuple(T.TOKENS['FOCUS'])      # VISUAL_PLAN E FOCUS (cell_acid) #D4FF00
INKC = (12, 10, 22)                   # L1 ink #0C0A16
HL.LIME = FOCUS
HL.INKC = INKC
CORP = Z.CORP

# ================================================================================================ L6 pencil and L5 in wax (C1: rb_pencil)
PEN_W, PEN_INK = PENM.PEN_W, PENM.PEN_INK          # 7 px wax, 3 px ink edge each side (VISUAL_PLAN A.5 / B L6)
L5_EDGE, L5_INK = 3.0, 2.25           # B L5: two 3 px edges; L1 keyline 4.5 px (2.25 each side)
L5_CHEV_W = 3.4                       # chevron stroke, L5 (10 px chevrons at a 24 px pitch)
PEN = {'cap': True}                   # capture of the wax / ink masks per class, for the checks
PEN_MASKS = {}
PEN_COV = {}              # the same classes as coverage (0-1, the 2x drawing box-filtered to 1x): the width checks integrate it


def _pen_add(cls, m, x0, y0, cov=None):
    full = PEN_MASKS.setdefault(cls, np.zeros((H, W), bool))
    h, w = m.shape
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xb > xa and yb > ya:
        full[ya:yb, xa:xb] |= m[ya - y0:yb - y0, xa - x0:xb - x0]
        if cov is not None:
            fc = PEN_COV.setdefault(cls, np.zeros((H, W), np.float32))
            np.maximum(fc[ya:yb, xa:xb], cov[ya - y0:yb - y0, xa - x0:xb - x0], out=fc[ya:yb, xa:xb])


def _seed(*a):
    return int(hashlib.md5(repr(a).encode()).hexdigest()[:8], 16)


def wax_stroke(L, pts, w=PEN_W, ink=PEN_INK, col=PLAN, seed=1, cap=True, closed=False, cls='L6', streak=True):
    """C1: the one grease pencil, corp/src rb_pencil.wax_stroke (same signature).  rb_pencil records every stroke in its own MASKS / COV; for the
    call they are swapped for fresh dicts and, when PEN['cap'], merged into this file's PEN_MASKS / PEN_COV (the hover checks' classes)"""
    if len(pts) < 2:
        return
    sm, sc = PENM.MASKS, PENM.COV
    tm, tc = {}, {}
    PENM.MASKS, PENM.COV = tm, tc
    try:
        PENM.wax_stroke(L, list(pts), w, ink, col, seed, cap, closed, cls, streak)
    finally:
        PENM.MASKS, PENM.COV = sm, sc
    if PEN['cap']:
        for k, m in tm.items():
            full = PEN_MASKS.setdefault(k, np.zeros((H, W), bool))
            full |= m
        for k, c in tc.items():
            fc = PEN_COV.setdefault(k, np.zeros((H, W), np.float32))
            np.maximum(fc, c, out=fc)


def wax_fill(L, poly, col=PLAN, seed=1, ink=L5_INK, cls='L5'):
    """a filled wax shape (the L5 arrowhead) with the grain (rb_pencil's wax layer) and an ink keyline"""
    k = L.k
    pad = ink + 4
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, y0 = int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad))
    x1, y1 = int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))
    ww, hh = (x1 - x0) * k, (y1 - y0) * k
    P = [((x - x0) * k, (y - y0) * k) for x, y in poly]
    mw = Image.new('L', (ww, hh), 0)
    ImageDraw.Draw(mw).polygon(P, fill=255)
    mi = Image.new('L', (ww, hh), 0)
    di = ImageDraw.Draw(mi)
    di.polygon(P, fill=255)
    di.line(P + [P[0]], fill=255, width=max(1, int(round(2 * ink * k))), joint='curve')
    wm = np.asarray(mw).astype(np.float32) / 255.0
    lay = PENM._wax_layer((hh, ww), wm, np.asarray(mi).astype(np.float32) / 255.0, col, seed, k, None)
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    PENM._flag(L, mi, x0, y0, k)
    if PEN['cap']:
        cw = np.asarray(mw.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        ci = np.asarray(mi.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        _pen_add(cls + '_wax', cw >= 0.5, x0, y0, cw)
        _pen_add(cls + '_all', ci >= 0.5, x0, y0, ci)


def pencil(L, pts, w=PEN_W, col=PLAN, ink=PEN_INK, seed=1, grain=True, cap=True):
    """hv_lib.pencil, every caller: L6 is always 7 px wax + 3 px ink (A.5); the caller's thinner widths are retired"""
    wax_stroke(L, pts, PEN_W, PEN_INK, col, seed, cap=cap)


def pencil_poly(L, poly, w=PEN_W, col=PLAN, ink=PEN_INK, seed=2):
    wax_stroke(L, list(poly), PEN_W, PEN_INK, col, seed, cap=False, closed=True)


def channel(L, pts, col=PLAN, w=16.0, head=22.0, ink=True, fill=(10, 8, 20, 200), chev=True, tail_dot=False, seed=1, edge=L5_EDGE, chev_col=None):
    """2026-11-04 round 2 gate-1 fix: the one L5 drawer, corp/src rb_pencil.channel (the board's p2b hover path draws with it too).  Its
    chevrons are drawn before the edges' wax, so the edges stay continuous (the gate read the cut edges as dashes at 1x, DR-1 risk).
    rb_pencil records the strokes in its own MASKS / COV; they are swapped for fresh dicts and merged into PEN_MASKS / PEN_COV, as wax_stroke"""
    if len(pts) < 2:
        return
    sm, sc = PENM.MASKS, PENM.COV
    tm, tc = {}, {}
    PENM.MASKS, PENM.COV = tm, tc
    try:
        PENM.channel(L, list(pts), col=col, w=w, head=head, fill=fill, chev=chev, tail_dot=tail_dot, seed=seed, edge=edge, chev_col=chev_col)
    finally:
        PENM.MASKS, PENM.COV = sm, sc
    if PEN['cap']:
        for k, m in tm.items():
            full = PEN_MASKS.setdefault(k, np.zeros((H, W), bool))
            full |= m
        for k, c in tc.items():
            fc = PEN_COV.setdefault(k, np.zeros((H, W), np.float32))
            np.maximum(fc, c, out=fc)


def _channel_round2(L, pts, col=PLAN, w=16.0, head=22.0, ink=True, fill=(10, 8, 20, 200), chev=True, tail_dot=False, seed=1, edge=L5_EDGE, chev_col=None):
    """round 2 (history, not called): the hover's own L5, edges before chevrons"""
    P0 = HL.resample(HL.smooth(pts, 2), 3.0)
    if len(P0) < 4:
        P0 = HL.resample(pts, 3.0)
    tip = P0[-1]
    t = HL.tangent_at_end(P0, 5)
    cut = head * 0.78
    body = list(P0)
    acc, i = 0.0, len(body) - 1
    while i > 0 and acc < cut:
        acc += math.hypot(body[i][0] - body[i - 1][0], body[i][1] - body[i - 1][1])
        i -= 1
    body = body[:i + 1]
    ns = HL.normals(body)
    hw = w / 2
    left = [(p[0] + n[0] * hw, p[1] + n[1] * hw) for p, n in zip(body, ns)]
    right = [(p[0] - n[0] * hw, p[1] - n[1] * hw) for p, n in zip(body, ns)]
    L.poly(left + right[::-1], fill=fill)
    for j, e in enumerate((left, right)):
        wax_stroke(L, e, edge, L5_INK, col, seed + 31 * j, cap=True, cls='L5', streak=False)
    wax_stroke(L, [left[0], right[0]], edge, L5_INK, col, seed + 77, cap=True, cls='L5', streak=False)
    if chev:
        acc = 12.0
        for j in range(1, len(body)):
            acc += math.hypot(body[j][0] - body[j - 1][0], body[j][1] - body[j - 1][1])
            if acc >= 24.0:
                acc = 0.0
                p, n = body[j], ns[j]
                tx, ty = n[1], -n[0]
                a = (p[0] - tx * 5 + n[0] * 4.2, p[1] - ty * 5 + n[1] * 4.2)
                b = (p[0] + tx * 4, p[1] + ty * 4)
                c = (p[0] - tx * 5 - n[0] * 4.2, p[1] - ty * 5 - n[1] * 4.2)
                wax_stroke(L, [a, b, c], L5_CHEV_W, 1.5, chev_col or col, seed + j, cap=True, cls='L5c', streak=False)   # chevrons: own class
    nx, ny = -t[1], t[0]
    base = (tip[0] - t[0] * head, tip[1] - t[1] * head)
    hw2 = w * 0.95
    hp = [(base[0] + nx * hw2, base[1] + ny * hw2), tip, (base[0] - nx * hw2, base[1] - ny * hw2)]
    wax_fill(L, hp, col, seed + 5, cls='L5h')                  # the filled head: own class (not an edge width)
    inner = [(base[0] + nx * hw2 * 0.46 + t[0] * 4, base[1] + ny * hw2 * 0.46 + t[1] * 4), (tip[0] - t[0] * 7, tip[1] - t[1] * 7),
             (base[0] - nx * hw2 * 0.46 + t[0] * 4, base[1] - ny * hw2 * 0.46 + t[1] * 4)]
    L.poly(inner, fill=(10, 8, 20, 230))
    if tail_dot:
        p = P0[0]
        L.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=INKC)
        L.ellipse([p[0] - 3.6, p[1] - 3.6, p[0] + 3.6, p[1] + 3.6], fill=col)


def done_box(L):
    """the hover marks layer to 1x with a BOX filter (2 x 2 supersampling): LANCZOS rings at the wax / ink edge and lifts the wax above its
    pigment; BOX keeps every wax pixel at or under PLAN, so the grain only darkens"""
    return L.im.resize((W, H), Image.BOX)


HL.pencil = pencil
HL.pencil_poly = pencil_poly
HL.channel = channel


def pc(L, pts, w=13, head=19, **kw):
    """PLAN L5 arrowed outline: the one motion mark of every hover"""
    channel(L, pts, col=PLAN, w=w, head=head, chev=True, fill=kw.pop('fill', (10, 8, 20, 200)), **kw)


Z.pc = pc

# ================================================================================================ FOCUS (C2: rb_focus, the one drawer)
FOCUS_LEG = FOC.LEG
FOCUS_W, FOCUS_W_AIM = FOC.W_LEGAL, FOC.W_AIM
FOCUS_INK = FOC.INK_EXTRA
FOCUS_MASK = {}
TAG_FOCUS_PAD = 5.0                   # px round the ring tag box (hz_core.focus_tag)


def _ink_then(L, polys, col, w, ink_extra=FOCUS_INK):
    """every FOCUS corner (hz_core.safe_corners, hv_lib.band_corners / rect_corners): rb_focus.draw, the board's drawer.  The caller's colour
    is retired (FOCUS token); w >= 3.5 is the aimed weight.  The FOCUS mask of the plate is recorded by hv_comp.focus_layer (accepted corners
    only; round 1 also added the trial corners that safe_corners tested and dropped)"""
    FOC.draw(L, polys, aimed=w >= FOC.W_AIM - 1e-6, tag='hover')


HL._ink_then = _ink_then


def focus_tag(L, d, f, thick=False):
    """FOCUS on a ring tag: rb_focus.rect, 12 px legs (hz_core used hv_lib.rect_corners with 10 px legs)"""
    FOC.rect(L, Z.tag_box(d, f), aimed=thick, pad=TAG_FOCUS_PAD, tag='ring tag %d' % d)


Z.focus_tag = focus_tag

# ================================================================================================ HUD (C8: hud_rows, the one row grid)
HERO_ROOM_T, HERO_ROOM_B, HERO_DX, HERO_GAP = HR.HERO_ROOM_T, HR.HERO_ROOM_B, HR.HERO_DX, HR.HERO_GAP
OPT_PITCH, OPT_BAND = HR.OPT_PITCH, HR.OPT_BAND
OPT = HR.OPT          # h04: hud_rows draws OPT['draw'](L, f, yy, OPT['rows']) into its reserved NEXT slots
HUD_ROOM = {'on': True}
YOU_SHIFT = {'dy': 0}


def hero_digits_xy():
    return hud2.R.get('_hero_xy')


def cold(c):
    g = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    return tuple(int(round((g + (q - g) * RB2.COLD_CHROMA) * RB2.NEXT_V)) for q in c[:3])


def twist_glyph(L, x, y, d, col, r=9.0):
    """the option's turn direction: a vector ring arrow (clockwise for +1), TEXT_MID, ink keyline"""
    a0, a1 = (-150, 120) if d > 0 else (120, -150)
    pts = [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 16)]
    L.line(pts, INKC, 5.6)
    L.line(pts, col, 2.4)
    ta = math.radians(a1)
    tx, ty = x + r * math.cos(ta), y + r * math.sin(ta)
    dd = math.radians(a1 + (90 if d > 0 else -90))
    hx, hy = math.cos(dd), math.sin(dd)
    nx_, ny_ = -hy, hx
    tri = [(tx + hx * 6, ty + hy * 6), (tx + nx_ * 5 - hx * 2, ty + ny_ * 5 - hy * 2), (tx - nx_ * 5 - hx * 2, ty - ny_ * 5 - hy * 2)]
    L.poly(tri, fill=col + (255,), outline=INKC, w=1.6)


def option_next_rows(L, f, y, rows):
    """2.4 + ART_BIBLE 3.22: an option card splits NEXT into one row per option, in hud_rows' reserved slots (yy + NX_YY + k x OPT_PITCH).  Each
    row: the COLD turn pip and NEXT, the option's three NEXT counts under the SPLIT columns (COLD digits + filled COLD tallies), and at the right
    the option: its ring tag words (+1 W2 / +2 W3, the board's own) and the turn direction.  3.8: the hovered option row takes the neutral
    TEXT_HI 3 px edge, the best option the filled TEXT_HI star; no PLAN yellow in these rows."""
    H_ = hud2
    sx0, sx1 = H_.G['sx0'], H_.G['sx1']
    cols = H_.R.get('_split_cols')
    num_tally = H_._rb2['num_tally']
    op = H_._rb2['op']
    out = []
    for i, r_ in enumerate(rows[:HR.OPT_SLOTS]):
        yg = y + RB2.NX_YY + i * OPT_PITCH
        box = (sx0, yg - OPT_BAND / 2, sx1, yg + OPT_BAND / 2)
        H_.inset(L, box)
        if r_.get('sel'):
            L.rect([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], outline=H_.THI, w=RB3.SEL_EDGE_W, r=6)
        x = sx0 + 16
        L.ellipse([x - RB2.TURN_PIP_R, yg - RB2.TURN_PIP_R, x + RB2.TURN_PIP_R, yg + RB2.TURN_PIP_R], fill=H_.TMID, outline=H_.INK, w=1.0)
        H_.txt(L, x + 10, yg, 'NEXT', H_.LBL_PX, tuple(int(c * RB2.NEXT_V) for c in H_.TMID), 'mono', 'lm', H_.LBL_TRK)
        nx = r_['next']
        vals = {'ABSORBED': nx['absorbed'], 'SOAK': nx['slost'], 'YOU': nx['taken']}
        for nm, c in cols.items():
            if c['op_x'] is not None:
                op(L, c['op_x'], yg, '+', RB2.NEXT_V)
            num_tally(L, c['xg'], yg, c['kind'], vals[nm], px=RB2.NUM_PX_SMALL, val=RB2.NEXT_V, hollow=True)
        xr = sx1 - 14
        twist_glyph(L, xr - 10, yg, r_['d'], H_.TMID)
        xr -= 28
        if NOW['words']:
            tw_ = H_.ttw(L, r_['tag'], H_.LBL_PX, 'mono', H_.LBL_TRK)
            H_.txt(L, xr - tw_, yg, r_['tag'], H_.LBL_PX, H_.THI if r_.get('sel') else H_.TMID, 'mono', 'lm', H_.LBL_TRK)
            xr -= tw_ + 10
        else:
            for q in range(r_['ring']):
                L.ellipse([xr - 7 - q * 11, yg - 4, xr + 1 - q * 11, yg + 4], fill=H_.TMID, outline=H_.INK, w=1.2)
            xr -= 11 * r_['ring'] + 8
        star = None
        if r_.get('best'):
            star = [xr - RB3.BEST_STAR_R, yg, RB3.BEST_STAR_R]
            RB3.best_star(L, star[0], yg)
        out.append(dict(box=box, star=star, **{k: v for k, v in r_.items() if k != 'next'}, next=nx))
    H_.reg('next_row', (sx0, y + RB2.NX_BAND[0], sx1, y + RB2.NX_YY + (len(rows) - 1) * OPT_PITCH + OPT_BAND / 2))
    H_.R['_opt_rows'] = out


HR.OPT['draw'] = option_next_rows


# ================================================================================================ HUD boxes from the registries (round-2 HUD)
def hud_box(name):
    if name == 'bill':
        return hud2.R['bill_frame']
    if name == 'res':
        return obj2.R['res_plate']
    if name == 'obj':
        return obj2.R['obj_plate']
    if name == 'head':
        return hud2.R.get('header_plate', (1072, 12, 1896, 68))


def lit_bill(Lt):
    Lt.box(*hud_box('bill'), r=8)


def lit_res(Lt):
    b = hud_box('res')
    Lt.box(*b, r=8)
    if obj2.R.get('refund_tab'):
        Lt.box(*obj2.R['refund_tab'], r=6)


Z.lit_bill = lit_bill
Z.lit_res = lit_res

# ================================================================================================ pencil ring (no brackets) and YOU underline
RING = {'turns': 1.07, 'drift': 0.03, 'n': 3.0}
RING_N = (3.0, 3.5, 4.0, 5.0, 6.0)     # ring shape exponents tried, roundest first (2 = ellipse; 3-5 = a hand ring that hugs a tall digit)
RING_GAP = 1.0                    # px between the hero digit fill and the ring's inner ink edge
RING_HALF = PEN_W / 2 + PEN_INK   # 6.5: centre line to the ring's outer ink edge
FIT_LOG = []
YOU_MASK = {}


def _se(t, n):
    c, s_ = math.cos(t), math.sin(t)
    return math.copysign(abs(c) ** (2.0 / n), c), math.copysign(abs(s_) ** (2.0 / n), s_)


def ring_pts(cx, cy, rx, ry, seed, turns=None, drift=None, n=None):
    """a closed pencil ring with a short overshoot: superellipse |x/rx|^n + |y/ry|^n = 1 (n = 2 is an ellipse), drifting outward by drift"""
    turns = RING['turns'] if turns is None else turns
    drift = RING['drift'] if drift is None else drift
    n = RING['n'] if n is None else n
    rnd = np.random.default_rng(seed)
    t0 = -2.0 + rnd.random() * 0.6
    m = 144
    pts = []
    for i in range(int(m * turns) + 1):
        f = i / (m * turns)
        t = t0 + 2 * math.pi * turns * f
        k = 1.0 + drift * (f - 0.5) + 0.010 * math.sin(3.1 * t + seed)
        ex, ey = _se(t, n)
        pts.append((cx + rx * k * ex, cy + ry * k * ey))
    return pts


def ring_axes(gx0, gy0, gx1, gy1, n, extra_x):
    """the centre-line half axes of the smallest ring of shape n whose inner ink edge clears the glyph box by RING_GAP, given extra_x px of
    horizontal slack"""
    a = (gx1 - gx0) / 2.0 + RING_GAP + 0.5
    b = (gy1 - gy0) / 2.0 + RING_GAP + 0.5
    ia = a + extra_x
    q = 1.0 - (a / ia) ** n
    ib = b / (q ** (1.0 / n)) if q > 0 else b * 4
    ib *= 1.0 + RING['drift'] / 2 + 0.012
    ia *= 1.0 + RING['drift'] / 2 + 0.012
    return ia + RING_HALF, ib + RING_HALF


def _forbid_hud():
    forb = np.zeros((H, W), bool)
    if 'hud_labels' in MASKS:
        forb |= MASKS['hud_labels']
    if 'hud_hero' in MASKS:
        forb |= MASKS['hud_hero']          # the digit with its black keyline: the ring's ink never merges with the digit's keyline
    if 'you' in YOU_MASK:
        forb |= YOU_MASK['you']
    return ndi.binary_dilation(forb, iterations=1)


def fit_ring(L, box, seed, tag='', col=PLAN):
    """2.5: a real pencil ring (7 px wax + 3 px ink, closed with a short overshoot) round a number the plan changes.  It may touch no HUD word, no
    hero digit fill and no part of the YOU strip, and stays inside the bill frame.  No bracket or open fallback: a ring that does not fit is
    logged ok=False and fails the plate."""
    gx0, gy0, gx1, gy1 = box
    cx, cy = (gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0
    forb = _forbid_hud()
    bx = hud_box('bill')
    inside = np.zeros((H, W), bool)
    inside[int(bx[1]) + 3:int(bx[3]) - 3, int(bx[0]) + 3:int(bx[2]) - 3] = True
    forb |= ~inside
    cands = []
    for ni, n in enumerate(RING_N):
        for ex in (9, 7, 11, 5, 6, 13, 15, 4, 17):
            rx, ry = ring_axes(gx0, gy0, gx1, gy1, n, ex)
            for dy in (0, 1, -1, 2, -2, 3, 4, -3, 5):
                for dx in (0, 1, -1, 2, -2, 3, -3):
                    cands.append((ni * 3.0 + abs(ex - 9) * 0.25 + abs(dy) * 0.7 + abs(dx) * 0.7, n, ex, rx, ry, dx, dy))
    cands.sort()
    tested = 0
    for cost, n, ex, rx_, ry_, dx, dy in cands:
        pts = ring_pts(cx + dx, cy + dy, rx_, ry_, seed, n=n)
        if Z._quick_hit(pts, RING_HALF, forb):            # coarse pre-filter; the drawn ring below is the test
            continue
        tested += 1
        T_ = L2()
        PEN['cap'] = False
        wax_stroke(T_, pts, seed=seed, cap=True)
        PEN['cap'] = True
        m = np.asarray(done_box(T_).split()[3]) >= 40
        if not (m & forb).any():
            wax_stroke(L, pts, seed=seed, cap=True)
            ys, xs = np.nonzero(m)
            FIT_LOG.append(dict(tag=tag, form='ring', n=n, extra_x=ex, rx=round(rx_, 1), ry=round(ry_, 1), dx=dx, dy=dy, ok=True, real_tests=tested,
                                glyph=[round(float(v), 1) for v in box], ring_box=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]))
            return True
        if tested > 240:
            break
    FIT_LOG.append(dict(tag=tag, form='ring', ok=False, glyph=[round(float(v), 1) for v in box], real_tests=tested))
    return False


def bill_marks(L, f_live, f_plan, words):
    """a pencil ring round each hero number the plan changes (LANDS / THROUGH); GDD 9.2: the bill shows the plan values"""
    lv, pl = f_live['pv']['eq'], f_plan['pv']['eq']
    xy = hud2.R.get('_hero_xy')
    out = []
    if xy is None:
        return out
    cy = xy['y']
    hm = MASKS['hud_hero'] if 'hud_hero' in MASKS else None
    for key, seed in (('through', 3), ('lands', 4)):
        if pl[key] == lv[key]:
            continue
        x0, wd = xy[key]
        box = None
        if hm is not None:
            sub = hm[int(cy - 44):int(cy + 44), int(x0 - 4):int(x0 + wd + 4)]
            ys_, xs_ = np.nonzero(sub)
            if ys_.size:
                box = (x0 - 4 + xs_.min(), cy - 44 + ys_.min(), x0 - 4 + xs_.max() + 1, cy - 44 + ys_.max() + 1)
        if box is None:
            box = (x0, cy - 15, x0 + wd, cy + 15) if xy.get('nw') else (x0, cy - 27, x0 + wd, cy + 27)
        if fit_ring(L, box, seed, tag=key + (' nw' if not words else '')):
            out.append(key)
    return out


def you_pip_x(i):
    """YOU strip segment x (rb2_patch you_strip: xs = 1068 + 72, 13.6 x 22 at a 16.4 px pitch, 8 px group gap)"""
    g, k = divmod(i, 5)
    return 1068 + 72 + g * (5 * RB2.YOU_SEG_P + RB2.YOU_GROUP_GAP) + k * RB2.YOU_SEG_P


YOU_UL_GAP = 2.0      # px between the YOU strip's paper and the underline's ink edge


def you_mark(L, f_live, f_plan):
    """the YOU strip's HP after the turn changes: a pencil underline (7 px wax + ink) under exactly the segments that change, never over the strip"""
    a, b = sorted((f_live['pv']['hp_after'], f_plan['pv']['hp_after']))
    if a == b:
        return False
    x0, x1 = you_pip_x(a) + 1.0, you_pip_x(b - 1) + RB2.YOU_SEG_W - 1.0
    ym = YOU_MASK.get('you')
    if ym is not None:
        cols = ym[:, int(x0):int(x1) + 1]
        rows = np.nonzero(cols.any(1))[0]
        ybot = rows.max() if rows.size else 150 + HERO_ROOM_T
    else:
        ybot = 150 + HERO_ROOM_T
    yc = ybot + 1 + YOU_UL_GAP + PEN_INK + PEN_W / 2
    forb = _forbid_hud()
    for dy in (0, 1, 2, 3, -1):
        pts = [(x0, yc + dy), ((x0 + x1) / 2, yc + dy + 0.6), (x1, yc + dy + 0.2)]
        T_ = L2()
        PEN['cap'] = False
        wax_stroke(T_, pts, seed=31, cap=True)
        PEN['cap'] = True
        m = np.asarray(done_box(T_).split()[3]) >= 40
        if not (m & forb).any():
            wax_stroke(L, pts, seed=31, cap=True)
            FIT_LOG.append(dict(tag='you', form='underline', segments=[a, b], y=round(yc + dy, 1), ok=True))
            return [a, b]
    FIT_LOG.append(dict(tag='you', form='underline', segments=[a, b], ok=False))
    return [a, b]


# 3.9: one RAM treatment.  The RAM row draws the plan in the coin's own states; no pencil or GAIN ring on a coin, no pencil box on a TRACE pip.
def ram_mark(L, before, after):
    return None


def ram_plus(L, n_at):
    return None


def trace_mark(L, before, after):
    return None


Z.fit_oval = lambda *a, **k: False
Z.bill_marks = bill_marks
Z.you_mark = you_mark
Z.ram_mark = ram_mark
Z.ram_plus = ram_plus
Z.trace_mark = trace_mark
Z.you_pip_x = you_pip_x
