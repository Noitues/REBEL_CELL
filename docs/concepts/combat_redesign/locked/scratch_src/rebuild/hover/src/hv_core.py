"""hv_core: the hover plates on the REBUILT board (2026-11-03 rebuild, stage 2 and gate 1), fixing AD review IMPL items 2.4, 2.5, 2.6, 3.8, 3.9
and 3.13 (locked/REVIEW_RESPONSE.md).  The one generator (corp/src) is imported READ-ONLY through hz_core; every change below is an in-process
patch or a new primitive in this file.  Nothing under corp/src is written.

  2.5  pencil (L6) = 7 px PLAN wax + 3 px ink edge each side + wax grain (8 % value noise and drag streaks along the stroke), no glow.  Every
       hz / hv_lib pencil call goes through wax_stroke.  The L5 arrowed outline keeps its B-table geometry (16 px channel, two 3 px edges,
       10 px chevrons at a 24 px pitch, 22 px head) in the same wax material.  No pencil brackets "( 9 )": the bill gets room for a real ring
       (HERO_ROOM_*), and the YOU strip is never drawn over: its change is a pencil underline under the strip.
  2.6  the hand is laid out by search (hand_layout): 0 px under SEND IT / UNDO, the lifted card 0 px on every sibling's cost hex and rules line
       (rb_checks.card_regions, the board's check e), outside r459, 3 px off the landing marks, lowest pixel y <= 1067.
  3.9  one RAM treatment: the RAM row shows the plan in its own coin states (filled / spent socket / refund plus), never a pencil or GAIN ring.
  FOCUS  four separate 12 px corners in FOCUS #D4FF00 (2 px legal, 3.5 px aimed), never the a_kit lime, never joined.
Env CORP=neutral|solace|meridian selects the skin (lw_render, at import)."""
import sys, os, math, json, copy, hashlib
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
os.chdir(SRC)
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
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

PLAN = T.TOKENS['PLAN'] if 'PLAN' in T.TOKENS else (255, 226, 0)
FOCUS = (212, 255, 0)                 # VISUAL_PLAN E FOCUS (cell_acid) #D4FF00
INKC = (12, 10, 22)                   # L1 ink #0C0A16
HL.LIME = FOCUS
HL.INKC = INKC
CORP = Z.CORP

# ================================================================================================ L6 pencil and L5 in wax (2.5)
PEN_W, PEN_INK = 7.0, 3.0             # VISUAL_PLAN A.5 / B L6: 7 px wax, 3 px ink edge (each side)
PEN_GRAIN = 0.08                      # wax grain: value noise, 8 percent
PEN_GRAIN_SIGMA = 0.9                 # grain blob size, 1x px
PEN_DRAG = 0.15                       # drag streaks along the stroke (wax drawn on glass): value drop
PEN_DRAG_N = 3                        # streaks per stroke
PEN_DRAG_W = 0.9                      # streak width, 1x px
PEN_EDGE_JIT = 0.45                   # ragged wax edge, 1x px
L5_EDGE, L5_INK = 3.0, 2.25           # B L5: two 3 px edges; L1 keyline 4.5 px (2.25 each side)
L5_CHEV_W = 3.4                       # chevron stroke, L5 (10 px chevrons at a 24 px pitch)
PEN = {'cap': True}                   # capture of the wax / ink masks per class, for the checks
PEN_MASKS = {}


PEN_COV = {}              # the same classes as coverage (0-1, the 2x drawing box-filtered to 1x): the width checks integrate it, so a
                          # stroke's measured width does not jump by a pixel with its sub-pixel position (a 50 % mask does)


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


def _wax_layer(shape_k, wax_m, ink_m, col, seed, k, streaks):
    """RGBA (2x) of a wax stroke: ink where ink_m, wax colour x grain where wax_m.  wax_m / ink_m: float 0..1 at 2x."""
    rng = np.random.default_rng(seed)
    hh, ww = shape_k
    n = ndi.gaussian_filter(rng.standard_normal((hh, ww)), PEN_GRAIN_SIGMA * k)
    n = n / (n.std() + 1e-6)
    v = 1.0 - PEN_GRAIN * np.clip(0.5 + 0.5 * n, 0.0, 1.6)            # darkens only: no wax pixel is brighter than PLAN
    if streaks is not None:
        v = v * (1.0 - PEN_DRAG * streaks)
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = np.array(INKC, np.float32)
    out[..., 3] = ink_m * 255.0
    wc = np.array(col, np.float32)[None, None, :] * v[..., None]
    a = wax_m[..., None]
    out[..., :3] = out[..., :3] * (1 - a) + wc * a
    out[..., 3] = np.maximum(out[..., 3], wax_m * 255.0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def _stamp(im, P, r, butt):
    """the stroke of radius r along P (2x px) as a union of discs, no PIL wide line: PIL's wide polyline leaves scanline gaps between its many
    short segments (rows where the 13 px ink line shrank to the wax width, so the wax touched the glass with no ink edge), and a line + disc
    union came out up to 1 px (2x) wider than either.  A disc with bbox r - 0.5 is exactly as wide as a line of width 2r.  The discs are spaced
    at most r/3 apart (scallop < 0.05 px).  butt: the two ends are cut square at the end points (an uncapped open stroke)."""
    d = ImageDraw.Draw(im)
    q = r - 0.5
    step = max(0.5, q / 3.0)
    Q = [P[0]]
    for i in range(1, len(P)):
        (xa, ya), (xb, yb) = P[i - 1], P[i]
        n = max(1, int(math.ceil(math.hypot(xb - xa, yb - ya) / step)))
        Q += [(xa + (xb - xa) * j / n, ya + (yb - ya) * j / n) for j in range(1, n + 1)]
    for x, y in Q:
        d.ellipse([x - q, y - q, x + q, y + q], fill=255)
    if butt and len(P) > 1:
        for (ex, ey), (px_, py_) in ((P[0], P[1]), (P[-1], P[-2])):
            tx, ty = ex - px_, ey - py_
            tl = math.hypot(tx, ty) or 1.0
            tx, ty = tx / tl, ty / tl                    # outward tangent at this end
            nx, ny = -ty, tx
            R = r + 4
            d.polygon([(ex + nx * R, ey + ny * R), (ex + nx * R + tx * R, ey + ny * R + ty * R), (ex - nx * R + tx * R, ey - ny * R + ty * R),
                       (ex - nx * R, ey - ny * R)], fill=0)


def wax_stroke(L, pts, w=PEN_W, ink=PEN_INK, col=PLAN, seed=1, cap=True, closed=False, cls='L6', streak=True):
    """N family grease pencil (L6): a w px wax stroke with an ink edge of `ink` px each side, wax grain and drag streaks, round caps, no glow"""
    if len(pts) < 2:
        return
    pts = HL.resample(HL.smooth(list(pts), 1), 1.5)
    if closed:
        pts = pts + [pts[0]]
    k = L.k
    pad = w / 2 + ink + 4
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad))
    x1, y1 = int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))
    ww, hh = (x1 - x0) * k, (y1 - y0) * k
    P = [((x - x0) * k, (y - y0) * k) for x, y in pts]
    mi = Image.new('L', (ww, hh), 0)
    mw = Image.new('L', (ww, hh), 0)
    butt = not cap and not closed
    _stamp(mi, P, (w / 2 + ink) * k, butt)           # round caps come with the discs; an uncapped stroke is cut square
    _stamp(mw, P, (w / 2) * k, butt)
    rng = np.random.default_rng(seed + 7)
    wm = np.asarray(mw).astype(np.float32) / 255.0
    # ragged wax edge: the wax boundary moves by up to PEN_EDGE_JIT px with a smooth noise field
    if PEN_EDGE_JIT > 0:
        jn = ndi.gaussian_filter(rng.standard_normal(wm.shape), 1.6 * k)
        jn = jn / (jn.std() + 1e-6)
        sm = ndi.gaussian_filter(wm, 0.5 * k)
        wm = np.clip((sm - 0.5 + 0.18 * PEN_EDGE_JIT * jn) * 4.0 + 0.5, 0, 1) * (wm > 0)
    im_ = np.asarray(mi).astype(np.float32) / 255.0
    streaks = None
    if streak and w >= 3.0:
        S = Image.new('L', (ww, hh), 0)
        ds = ImageDraw.Draw(S)
        nrm = HL.normals(pts)
        for j in range(PEN_DRAG_N):
            off = (rng.random() - 0.5) * (w - 2.0)
            # one streak follows the stroke for a random stretch (never evenly broken: no dash or dot run)
            n_ = len(pts)
            a_ = int(rng.random() * n_ * 0.35)
            b_ = n_ - int(rng.random() * n_ * 0.35)
            q = [((pts[i][0] + nrm[i][0] * off - x0) * k, (pts[i][1] + nrm[i][1] * off - y0) * k) for i in range(a_, max(a_ + 2, b_))]
            if len(q) > 1:
                ds.line(q, fill=255, width=max(1, int(round(PEN_DRAG_W * k))), joint='curve')
        streaks = ndi.gaussian_filter(np.asarray(S).astype(np.float32) / 255.0, 0.35 * k)
    lay = _wax_layer((hh, ww), wm, im_, col, seed, k, streaks)
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    if PEN['cap']:
        c1 = np.asarray(Image.fromarray((wm * 255).astype(np.uint8)).resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        ci1 = np.asarray(mi.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        _pen_add(cls + '_wax', c1 >= 0.5, x0, y0, c1)
        _pen_add(cls + '_all', ci1 >= 0.5, x0, y0, ci1)


def wax_fill(L, poly, col=PLAN, seed=1, ink=L5_INK, cls='L5'):
    """a filled wax shape (the L5 arrowhead) with the grain and an ink keyline"""
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
    lay = _wax_layer((hh, ww), wm, np.asarray(mi).astype(np.float32) / 255.0, col, seed, k, None)
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    if PEN['cap']:
        cw = np.asarray(mw.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        ci = np.asarray(mi.resize((x1 - x0, y1 - y0), Image.BOX)).astype(np.float32) / 255.0
        _pen_add(cls + '_wax', cw >= 0.5, x0, y0, cw)
        _pen_add(cls + '_all', ci >= 0.5, x0, y0, ci)


def pencil(L, pts, w=PEN_W, col=PLAN, ink=PEN_INK, seed=1, grain=True, cap=True):
    """hv_lib.pencil, every caller: L6 is always 7 px wax + 3 px ink (2.5); the caller's thinner widths are retired"""
    wax_stroke(L, pts, PEN_W, PEN_INK, col, seed, cap=cap)


def pencil_poly(L, poly, w=PEN_W, col=PLAN, ink=PEN_INK, seed=2):
    wax_stroke(L, list(poly), PEN_W, PEN_INK, col, seed, cap=False, closed=True)


def channel(L, pts, col=PLAN, w=16.0, head=22.0, ink=True, fill=(10, 8, 20, 200), chev=True, tail_dot=False, seed=1, edge=L5_EDGE, chev_col=None):
    """L5 arrowed outline in the pencil material: a w px channel (dark floor), two L5_EDGE px wax edges with an L1 ink keyline, 10 px chevrons
    at a 24 px pitch pointing the way of travel, a filled wax arrowhead"""
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
    pigment (PLAN G 226 read up to 239); BOX keeps every wax pixel at or under PLAN, so the grain only darkens"""
    return L.im.resize((W, H), Image.BOX)


HL.pencil = pencil
HL.pencil_poly = pencil_poly
HL.channel = channel


def pc(L, pts, w=13, head=19, **kw):
    """PLAN L5 arrowed outline: the one motion mark of every hover"""
    channel(L, pts, col=PLAN, w=w, head=head, chev=True, fill=kw.pop('fill', (10, 8, 20, 200)), **kw)


Z.pc = pc

# ================================================================================================ FOCUS (four separate corners, FOCUS #D4FF00)
FOCUS_LEG = 12.0
FOCUS_W, FOCUS_W_AIM = 2.0, 3.5
FOCUS_INK = 3.2
FOCUS_MASK = {}


def _focus_layer_add(T_):
    a = np.asarray(done_box(T_).split()[3]) >= 128
    FOCUS_MASK['m'] = FOCUS_MASK.get('m', np.zeros((H, W), bool)) | a


def _ink_then(L, polys, col, w, ink_extra=FOCUS_INK):
    """FOCUS corners: ink keyline then the FOCUS stroke; each corner is its own polyline (never joined)"""
    T_ = L2()
    for p in polys:
        T_.line(p, INKC, w + ink_extra)
    for p in polys:
        T_.line(p, col, w)
    L.im.alpha_composite(T_.im)
    _focus_layer_add(T_)


HL._ink_then = _ink_then

# ================================================================================================ HUD room for a real pencil ring (2.5)
HERO_ROOM_T = 19       # px added between the LANDS / THROUGH labels and the hero digits (the ring's top run)
HERO_ROOM_B = 26       # px added between the hero row and the RAW row (the ring's bottom run; the YOU underline)
HERO_DX = 16           # the hero pair moves right, clear of the YOU strip
HERO_GAP = 32          # digit -> arrow -> digit gap (was 14): the ring passes between a digit and the arrow
HUD_ROOM = {'on': True}
OPT = {'rows': None}   # h04: one NEXT row per option (2.4 / ART_BIBLE 3.22)
OPT_PITCH = 30         # px per option NEXT row
OPT_BAND = 26          # its inset band height
YOU_SHIFT = {'dy': 0}
_obill_box = hud2.bill_box
_ohero = Z.hud2.hero_pair


def hero_digits_xy():
    return hud2.R.get('_hero_xy')


def hero_pair(L, x, y, lands, through):
    """hud2.hero_pair with ring room: the labels keep their row, the digits move down HERO_ROOM_T, the gaps widen to HERO_GAP"""
    H_ = hud2
    if not NOW['words']:
        return hero_nw(L, x, y, lands, through)
    tcol = H_.HARM if through else H_.GAINC
    wl = L.tw(str(lands), 58, 'anton')
    wt = L.tw(str(through), 58, 'anton')
    H_.rowtag(L, x, y - 40 - HERO_ROOM_T, 'LANDS', centre=x + wl / 2)
    L.text((x, y), str(lands), 58, 'anton', fill=H_.WHITE, anchor='lm', stroke=4)
    ax = x + wl + HERO_GAP
    H_.arrow(L, ax, y, H_.THI, 40, 14)
    xt = ax + 40 + HERO_GAP
    H_.rowtag(L, xt, y - 40 - HERO_ROOM_T, 'THROUGH', centre=xt + wt / 2)
    L.text((xt, y), str(through), 58, 'anton', fill=tcol, anchor='lm', stroke=4)
    H_.reg('hero_pair', (x - 6, y - 52 - HERO_ROOM_T, xt + wt + 8, y + 38))
    H_.reg('row_tags_hero', H_.R['hero_pair'])
    H_.R['_hero_xy'] = dict(y=y, lands=(x, wl), through=(xt, wt), arrow=(ax, 40))


def hero_nw(L, x, y, lands, through):
    """hud2.hero_nw (nowords proxies) with the same gaps"""
    H_ = hud2
    sw, sh, sp = 13, 30, 17
    e1 = x
    for i in range(lands):
        xi = x + i * sp + (i // 5) * 12
        L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=H_.WHITE + (255,), outline=H_.INK, w=2, r=3)
        e1 = xi + sw
    ax = e1 + HERO_GAP
    H_.arrow(L, ax, y, H_.THI, 38, 14)
    xt = ax + 38 + HERO_GAP
    e2 = xt
    for i in range(through):
        xi = xt + i * sp + (i // 5) * 12
        L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=H_.HARM + (255,), outline=H_.INK, w=2, r=3)
        e2 = xi + sw
    H_.reg('hero_nowords_proxy', (x - 6, y - 24, e2 + 6, y + 24))
    H_.R['_hero_xy'] = dict(y=y, lands=(x, e1 - x), through=(xt, max(0, e2 - xt)), arrow=(ax, 38), nw=True)


def bill_box(L, f, y, pencil=False, plan_tag=None, twist_pay=None, extra=None):
    """hud2.bill_box with the ring room (HERO_ROOM_T / _B / DX) and, on h04, one NEXT row per option (OPT['rows'])"""
    if not HUD_ROOM['on']:
        return _obill_box(L, f, y, pencil, plan_tag, twist_pay, extra)
    H_ = hud2
    eq = f['pv']['eq']
    rows = OPT['rows']
    room = HERO_ROOM_T + HERO_ROOM_B
    H_.G['bill_h'] = RB2.BILL_H + room + (OPT_PITCH * (len(rows) - 1) if rows else 0)
    H_.el_bill_frame(L, y)
    x = H_.G['ox'] + 56
    e = H_.hp_tally(L, f, x, y + 46 + HERO_ROOM_T)
    H_.hero_pair(L, e + 34 + HERO_DX, y + 54 + HERO_ROOM_T, eq['lands'], eq['through'])
    if plan_tag:
        H_.el_best_tag(L, y, plan_tag)
    yy = y + room
    H_.el_eq_row(L, f, yy, eq)
    H_.el_split_row(L, f, yy, eq)
    if rows:
        option_next_rows(L, f, yy, rows)
    else:
        H_.el_next_row(L, f, yy, twist_pay)
    H_.reg('_bill_room', (H_.G['px0'], y, H_.G['px1'], y + H_.G['bill_h']))
    return y + H_.G['bill_h']


hud2.bill_box = bill_box
hud2.hero_pair = hero_pair
Z._cap('hud_hero', hud2, 'hero_pair')
_oui_img = FH.ui_img


def ui_img(kind, nw, f=None, seed=0):
    """the YOU strip moves down with the hero row (HERO_ROOM_T)"""
    im, (x0, y0) = _oui_img(kind, nw, f, seed)
    if kind == 'you' and HUD_ROOM['on']:
        return im, (x0, y0 + HERO_ROOM_T)
    return im, (x0, y0)


FH.ui_img = ui_img


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
    """2.4 + ART_BIBLE 3.22: an option card splits NEXT into one row per option.  Each row: the COLD turn pip and NEXT, the option's three NEXT
    counts under the SPLIT columns (COLD digits + filled COLD tallies), and at the right the option: its ring tag words (+1 W2 / +2 W3, the board's
    own) and the turn direction.  3.8: the hovered option row takes the neutral TEXT_HI 3 px edge, the best option the filled TEXT_HI star;
    no PLAN yellow in these rows."""
    H_ = hud2
    sx0, sx1 = H_.G['sx0'], H_.G['sx1']
    cols = H_.R.get('_split_cols')
    num_tally = H_._rb2['num_tally']
    op = H_._rb2['op']
    out = []
    for i, r_ in enumerate(rows):
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
        # the option, right aligned: [star] ring tag  direction
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


# ================================================================================================ HUD boxes from the registries (rebuilt HUD)
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
    if 'refund_tab' in obj2.R:
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
    horizontal slack: inner half width a + extra_x, inner half height from the corner condition (a/ia)^n + (b/ib)^n <= 1 (with the drift)"""
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
    hero digit fill and no part of the YOU strip, and stays inside the bill frame.  Candidates: shape n (RING_N, roundest first), horizontal
    slack, small moves; each is pre-tested on its centre line, then drawn and tested.  No bracket or open fallback: a ring that does not fit is
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
    """a pencil ring round each hero number the plan changes (LANDS / THROUGH); GDD 9.2: the bill shows the plan values.  The ring is fitted to
    the drawn digit fill (the hero mask), or to the nowords proxy run"""
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
