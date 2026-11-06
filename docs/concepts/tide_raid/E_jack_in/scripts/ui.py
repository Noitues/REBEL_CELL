"""E Jack-in: HUD chips, vinyl cards, installed countermeasure programs, grease-pencil marks, stamps, sealed-route
fog + letter locks, hunter eye + reticle, odds chart, response keycaps, hit FX."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *
K = 0.643
from glyphs import *
import scene as SC

CYAN_UI = hexc('5BE3FF')
HEAT = hexc('F2B77C')
FOG = hexc('9C8CFF')


# ------------------------------------------------------------------ text
def ntext(cv, c, s, size, col, anchor='mm', mono=False, stroke=2.2, white=.35, k=1.0, glow=True):
    n = max(len(s), 1)
    bx = (c[0] - n * size * .8 - 10, c[1] - size * 1.2, c[0] + n * size * .8 + 10, c[1] + size * 1.2)
    a = Lyr(bx, pad=8)
    b = Lyr(bx, pad=8)
    if stroke:
        a.text(c, s, size, 255, anchor, mono, stroke=stroke)
    b.text(c, s, size, 255, anchor, mono)
    cv.overL(a, INK, .88 * k)
    cv.addL(b, col, k)
    if glow:
        cv.add(col, blur(b.m, 3), .45 * k, b.off)
    if white:
        cv.add(WHITE, b.m, white * k, b.off)


def glyph_disc(cv, c, r, col, fn, fill=INK, ring_w=2.4, gscale=.56, k=1.0, glyph_col=None, fill_a=.88, white=.3, g=True):
    bx = (c[0] - r - 6, c[1] - r - 6, c[0] + r + 6, c[1] + r + 6)
    d = Lyr(bx)
    d.ell(c, r)
    ring = Lyr(bx)
    ring.ell(c, r, v=255, outline=True, ow=ring_w)
    gl = Lyr(bx)
    fn(gl, c, r * gscale)
    cv.overL(d, fill, fill_a * k)
    cv.neonL(ring, col, core=k, g1=(3, .7 * k), g2=(9, .45 * k) if g else None)
    gc = col if glyph_col is None else glyph_col
    cv.neonL(gl, gc, core=k, g1=(2, .5 * k), g2=None, white=white * k)


def tier_chip(cv, c, tier, r=14, k=1.0, num=None):
    glyph_disc(cv, c, r, TIER[tier], lambda l, c_, r_: g_tier(l, tier, c_, r_), gscale=.62, k=k, ring_w=max(2, r * .16))
    if num is not None:
        ntext(cv, (c[0], c[1] + r + 12), str(num), 15, TIER[tier], k=k)


# ------------------------------------------------------------------ HUD
def crt_chip(cv, x0, y0, x1, y1, col=LATT_D, k=1.0, r=8):
    bx = (x0, y0, x1, y1)
    f = Lyr(bx, pad=10)
    f.rr(x0, y0, x1, y1, r, 255)
    e = Lyr(bx, pad=10)
    e.rr(x0, y0, x1, y1, r, 255, outline=True, ow=1.8)
    sc = Lyr(bx, pad=10)
    for y in range(int(y0) + 3, int(y1), 4):
        sc.line([(x0 + 4, y), (x1 - 4, y)], 1, 255)
    cv.overL(f, INK, .82 * k)
    cv.addL(sc, col, .06 * k)
    cv.neonL(e, col, core=.9 * k, g1=(3, .5 * k), g2=None)


def hud(cv, home=44, home_max=50, heat=80, healthy=8, infected=0, home_col=None, heat_tint=None, flash=0.0, lost=False):
    hc = (WHITE * .85 + LATT * .15) if home_col is None else home_col
    # HOME integrity chip
    crt_chip(cv, 22, 14, 236, 66, k=1.0)
    gl = Lyr((30, 20, 70, 60)); g_house(gl, (47, 40), 15)
    cv.neonL(gl, hc, core=1, g1=(2, .5), g2=None, white=.3)
    ntext(cv, (74, 40), str(home), 34, hc, anchor='lm', stroke=2)
    bar = Lyr((150, 30, 226, 56)); bar.rr(152, 54, 224, 59, 2, 255, outline=True, ow=1.2)
    cv.neonL(bar, LATT_D, core=.6, g1=None, g2=None)
    fl = Lyr((150, 30, 226, 56)); fl.rr(153, 55, 153 + 70 * home / home_max, 58, 1.5, 255)
    cv.neonL(fl, hc, core=1, g1=(2, .5), g2=None)
    # HEAT chip
    crt_chip(cv, 248, 14, 396, 66)
    fg = Lyr((256, 20, 296, 60)); g_flame(fg, (274, 40), 15)
    hcol = HEAT if heat_tint is None else heat_tint
    cv.neonL(fg, hcol, core=1, g1=(3, .6), g2=None, white=.2)
    ntext(cv, (302, 40), str(heat), 34, hcol, anchor='lm', stroke=2)
    # deck strip: infected (plum) vs healthy (teal), a balance in the middle
    n = healthy + infected
    cw, ch, gp = 20, 29, 5
    maxn = 14
    shown_i = min(infected, maxn)
    shown_h = min(healthy, maxn)
    wtot = (shown_i + shown_h) * (cw + gp) + 150
    x1 = 1898
    x0 = x1 - wtot
    crt_chip(cv, x0, 14, x1, 66, col=(VEIN * .7 if (lost or infected > healthy) else LATT_D))
    mid = x0 + 74 + shown_i * (cw + gp)
    ntext(cv, (x0 + 28, 40), str(infected), 32, VEIN if infected else PLUM_MID * 2.3, stroke=2)
    ntext(cv, (x1 - 28, 40), str(healthy), 32, TIER['HOLDS'], stroke=2)
    cx = x0 + 58
    pl = Lyr((x0, 14, x1, 66)); tl = Lyr((x0, 14, x1, 66)); tf = Lyr((x0, 14, x1, 66)); vv = Lyr((x0, 14, x1, 66))
    for i in range(shown_i):
        c = (cx + i * (cw + gp) + cw / 2, 40)
        pl.rr(c[0] - cw / 2, c[1] - ch / 2, c[0] + cw / 2, c[1] + ch / 2, 3, 255)
        vv.line([(c[0] - 5, c[1] - 7), (c[0] + 1, c[1] - 1), (c[0] - 3, c[1] + 4), (c[0] + 5, c[1] + 9)], 1.4, 255)
    cx = mid + 16
    for i in range(shown_h):
        c = (cx + i * (cw + gp) + cw / 2, 40)
        tl.rr(c[0] - cw / 2, c[1] - ch / 2, c[0] + cw / 2, c[1] + ch / 2, 3, 255, outline=True, ow=1.6)
        tf.rr(c[0] - 4, c[1] - 8, c[0] + 4, c[1] + 8, 1, 255)
    cv.overL(pl, PLUM_MID * 1.1, .9)
    cv.neonL(pl, VEIN * .9, core=.45, g1=(2, .4), g2=None)
    cv.neonL(vv, HOT, core=.8, g1=(1.5, .4), g2=None)
    cv.neonL(tl, TIER['HOLDS'], core=.9, g1=(2, .4), g2=None)
    cv.neonL(tf, TIER['HOLDS'], core=.5, g1=None, g2=None)
    # balance beam (tilts to the heavier pile)
    tilt = np.clip((infected - healthy) / max(n, 1), -1, 1) * 10
    bl = Lyr((mid - 18, 20, mid + 14, 62))
    bl.line([(mid - 12, 40 + tilt), (mid + 8, 40 - tilt)], 2.2, 255)
    bl.line([(mid - 2, 40), (mid - 2, 54)], 2, 255)
    bl.line([(mid - 8, 54), (mid + 4, 54)], 2.4, 255)
    cv.neonL(bl, WHITE * .8, core=.9, g1=(2, .4), g2=None)
    if flash:
        cv.add(TIER['DAMAGED'], np.full((52, 214), flash * .3, np.float32), 1, (22, 14))


# ------------------------------------------------------------------ vinyl sticker cards
def _lab(typ):
    return TYPE_COL[typ]


VERB_FN = {'GUARD': g_wall, 'SHIFT': g_detour, 'JAM': g_zig}


def card_sprite(verb, typ, w=98, h=134, ss=3, back=False):
    """vinyl sticker card (module 13 vocabulary): die-cut paper border, navy body, type band, verb glyph."""
    L = Lyr((0, 0, w, h), ss=ss, pad=0)
    L.pad = 0
    outer, inner, band, gl, tg, hl = (Lyr((0, 0, w, h), ss=ss, pad=0) for _ in range(6))
    outer.rr(1, 1, w - 1, h - 1, 13, 255)
    inner.rr(6, 6, w - 6, h - 6, 9, 255)
    band.rr(6, 6, w - 6, 40, 9, 255)
    band.rr(6, 24, w - 6, 40, 0, 255)
    VERB_FN[verb](gl, (w / 2, h * .62), 27)
    g_type(tg, typ, (w / 2, 23), 11)
    hl.poly([(w * .1, h * .98), (w * .55, h * .02), (w * .75, h * .02), (w * .3, h * .98)], 255)
    o, i_, b_, g_, t_, h_ = (x.m[:h, :w] for x in (outer, inner, band, gl, tg, hl))
    col = _lab(typ)
    img = np.zeros((h, w, 3), np.float32)
    img[:] = PAPER
    navy = hexc('0B1236')
    img = img * (1 - i_[..., None]) + navy * i_[..., None]
    img = img * (1 - b_[..., None]) + col * b_[..., None]
    img = img * (1 - t_[..., None]) + INK * t_[..., None]
    gcol = col * .35 + WHITE * .65
    img = img * (1 - g_[..., None]) + gcol * g_[..., None]
    img = img + WHITE * (h_ * i_ * .07)[..., None]
    return img, o


def card(cv, c, verb, typ, angle=0.0, lime=False, k=1.0, sc=1.0, shadow=True):
    img, a = card_sprite(verb, typ)
    h, w = a.shape
    rgba = np.dstack([img, a])
    im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    if sc != 1.0:
        im = im.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox, oy = int(c[0] - arr.shape[1] / 2), int(c[1] - arr.shape[0] / 2)
    if shadow:
        sh = blur(arr[..., 3], 7)
        cv.over(INK, sh, .6 * k, (ox + 4, oy + 8))
    if lime:
        lm = blur(arr[..., 3], 5)
        cv.add(LIME, np.clip(lm - arr[..., 3] * .0, 0, 1), .9, (ox, oy))
        big = Image.fromarray((arr[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
        ring = np.clip(np.asarray(big, np.float32) / 255 - arr[..., 3], 0, 1)
        cv.add(LIME, ring, 1.0, (ox, oy))
    cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))


def hand(cv, cards, y=972, dim=1.0, lift=None, lime_idx=None, spread=118, skip=None):
    n = len(cards)
    x0 = W / 2 - (n - 1) / 2 * spread
    for i, (verb, typ) in enumerate(cards):
        if skip is not None and i == skip:
            continue
        t = (i - (n - 1) / 2)
        ang = -t * 3.2
        yy = y + abs(t) ** 1.6 * 7 - (30 if lime_idx == i else 0)
        card(cv, (x0 + i * spread, yy), verb, typ, ang, lime=(lime_idx == i), k=dim)


# ------------------------------------------------------------------ installed programs on Sites
def _hexcell(c, r, rot=0):
    return [(c[0] + r * math.cos(math.radians(60 * i + rot)), c[1] + r * math.sin(math.radians(60 * i + rot))) for i in range(6)]


def firewall(cv, B, typ, mode='up', impact=None, t=0.0, k=1.0, seed=2):
    """GUARD program: a standing wall of hex-brick cells across the street, edged in the type colour."""
    col = TYPE_COL[typ]
    C = (B[0] + 34, B[1] + 12)
    hl, ht = 34, 50
    ax = np.array([1.0, K])
    P0 = np.array(C) - ax * hl
    P1 = np.array(C) + ax * hl

    def uv(u, v):  # u in [0,1] along the wall, v px up
        return tuple(P0 + (P1 - P0) * u - np.array([0, v]))

    bx = (P0[0] - 80, P0[1] - ht - 70, P1[0] + 80, P1[1] + 70)
    fill, cells, frame = Lyr(bx), Lyr(bx), Lyr(bx)
    shard = Lyr(bx)
    fill.poly([uv(0, 0), uv(1, 0), uv(1, ht), uv(0, ht)], 255)
    rng = np.random.RandomState(seed)
    r = 8.0
    rows = int(ht / (r * 1.5)) + 1
    ncol = int(2 * hl / (r * 1.74)) + 1
    for j in range(rows):
        for i in range(ncol):
            u = (i + (.5 if j % 2 else 0)) * (r * 1.74) / (2 * hl)
            v = j * r * 1.5 + 6
            if u > 1 or v > ht:
                continue
            cen = uv(u, v)
            sq = _hexcell(cen, r * .92, 30)
            sq = [(p[0], cen[1] + (p[1] - cen[1])) for p in sq]
            if mode == 'shatter' and impact is not None:
                d = math.hypot(cen[0] - impact[0], cen[1] - impact[1])
                if d < 62 * (.3 + t):
                    dirv = np.array([cen[0] - impact[0], cen[1] - impact[1] - 6])
                    dirv = dirv / (np.hypot(*dirv) + 1e-6)
                    off = dirv * (20 + 90 * t) * (1.1 - d / 90) + np.array([0, 14 * t * t * 4])
                    rot = rng.uniform(-60, 60) * t
                    cc = (cen[0] + off[0], cen[1] + off[1])
                    shard.line(_hexcell(cc, r * .8, 30 + rot) + [_hexcell(cc, r * .8, 30 + rot)[0]], 1.8, 255)
                    continue
            cells.line(sq + [sq[0]], 1.5, 255)
    frame.line([uv(0, 0), uv(1, 0), uv(1, ht), uv(0, ht), uv(0, 0)], 2.4, 255)
    ink = 0.6 * k if mode != 'ghost' else 0.2
    cv.overL(fill, INK, ink)
    cv.addL(fill, col, .07 * k)
    cv.neonL(cells, col, core=.8 * k, g1=(2.5, .6 * k), g2=(9, .4 * k))
    cv.neonL(shard, col * .5 + WHITE * .5, core=1.0, g1=(2.5, .8), g2=(9, .5))
    cv.neonL(frame, col * .6 + WHITE * .4, core=1.0 * k, g1=(3, .6 * k), g2=None, white=.3)
    # type shape on top: which beam this wall answers
    ic = Lyr(bx)
    g_type(ic, typ, uv(.5, ht + 14), 8.5)
    cv.overL(ic, INK, .0)
    cv.neonL(ic, col, core=1.0 * k, g1=(2.5, .6 * k), g2=None, white=.4)


def decoy(cv, B, typ, tier=1, k=1.0):
    """SHIFT program: a hologram copy of the Site beside it + a curved hand-off arrow (the beam re-targets)."""
    col = TYPE_COL[typ]
    Bd = (B[0] - 62, B[1] + 20)
    SC.tower(cv, Bd, tier, 'healthy', tint=col * .55 + LATT * .45, alpha=.42 * k, seed=9)
    ar = Lyr((B[0] - 80, B[1] - 130, B[0] + 20, B[1] - 20))
    pts = [(B[0] - 4, B[1] - 80 - 20 * math.sin(math.pi * t) * 1.2 + 0) for t in np.linspace(0, 1, 2)]
    a0 = (B[0] + 2, B[1] - 78)
    a1 = (Bd[0] + 2, Bd[1] - 62)
    mid = ((a0[0] + a1[0]) / 2 - 8, min(a0[1], a1[1]) - 34)
    curve = [((1 - t) ** 2 * a0[0] + 2 * t * (1 - t) * mid[0] + t * t * a1[0],
              (1 - t) ** 2 * a0[1] + 2 * t * (1 - t) * mid[1] + t * t * a1[1]) for t in np.linspace(0, 1, 22)]
    ar.line(curve, 2.6, 255, dash=(6, 4))
    d = np.array(curve[-1]) - np.array(curve[-3])
    d = d / np.hypot(*d)
    n = np.array([-d[1], d[0]])
    tip = np.array(curve[-1]) + d * 4
    ar.poly([tuple(tip), tuple(tip - d * 12 + n * 7), tuple(tip - d * 12 - n * 7)], 255)
    cv.neonL(ar, col, core=1.0 * k, g1=(2.5, .6 * k), g2=None, white=.3)
    ic = Lyr((Bd[0] - 20, Bd[1] - 150, Bd[0] + 20, Bd[1] - 60))
    g_type(ic, typ, (Bd[0], Bd[1] - 96), 8)
    cv.neonL(ic, col, core=.9 * k, g1=(2, .5), g2=None)


def tracer(cv, B, typ, k=1.0, phase=0.0):
    """JAM / ghost program: a tracer reticle locked on the street, static crackle across the lane."""
    col = TYPE_COL[typ]
    C = (B[0] + 6, B[1] + 8)
    bx = (C[0] - 70, C[1] - 60, C[0] + 70, C[1] + 60)
    ly = Lyr(bx)
    ly.line(SC.ring_pts(C, 40, 60), 2.2, 255, dash=(7, 5))
    for ang in (45, 135, 225, 315):
        a = math.radians(ang + phase)
        p = (C[0] + 46 * math.cos(a), C[1] + 46 * K * math.sin(a))
        q = (C[0] + 58 * math.cos(a), C[1] + 58 * K * math.sin(a))
        ly.line([p, q], 3, 255)
    ly.line([(C[0] - 22, C[1]), (C[0] + 22, C[1])], 1.6, 255)
    ly.line([(C[0], C[1] - 14), (C[0], C[1] + 14)], 1.6, 255)
    zz = Lyr(bx)
    rng = np.random.RandomState(4)
    pts = [(C[0] - 52 + i * 8, C[1] - 28 + (8 if i % 2 else -8) * rng.uniform(.4, 1)) for i in range(14)]
    zz.line(pts, 2.2, 255)
    cv.neonL(ly, col, core=1.0 * k, g1=(3, .6 * k), g2=(9, .35 * k))
    cv.neonL(zz, col, core=.8 * k, g1=(2, .4 * k), g2=None, white=.3)


# ------------------------------------------------------------------ grease-pencil marks (D28 vocabulary)
def scribble(ly, a, b, w, seed, passes=2, wob=2.4, v=255):
    rng = np.random.RandomState(seed)
    a = np.array(a, float); b = np.array(b, float)
    n = np.array([-(b - a)[1], (b - a)[0]]); n = n / (np.hypot(*n) + 1e-6)
    for p in range(passes):
        pts = []
        for t in np.linspace(0, 1, 9):
            pts.append(a + (b - a) * t + n * rng.uniform(-wob, wob) + n * (p - (passes - 1) / 2) * 2.2)
        ly.line([tuple(x) for x in pts], w * (1 - .12 * p), v)


def grease_down(cv, c, size=30, seed=1, k=1.0):
    """DOWN: a white china-marker double slash through the Site (the shared D28 helper idea)."""
    bx = (c[0] - size - 20, c[1] - size - 20, c[0] + size + 20, c[1] + size + 20)
    ly = Lyr(bx)
    scribble(ly, (c[0] - size * .8, c[1] + size), (c[0] + size * .8, c[1] - size), 6.5, seed)
    scribble(ly, (c[0] - size * .8 + 16, c[1] + size + 4), (c[0] + size * .8 + 16, c[1] - size + 4), 5.2, seed + 9)
    cv.overL(ly, INK, .65 * k)
    cv.addL(ly, GREASE_W, 1.0 * k)


def grease_taken(cv, c, size=30, seed=2, k=1.0):
    """TAKEN: a heavy red double X (over a plum stump)."""
    bx = (c[0] - size - 20, c[1] - size - 20, c[0] + size + 20, c[1] + size + 20)
    ly = Lyr(bx)
    for o in (0, 1):
        s_ = size * (1 - .15 * o)
        scribble(ly, (c[0] - s_, c[1] - s_ + o * 4), (c[0] + s_, c[1] + s_), 7.5, seed + o, 2)
        scribble(ly, (c[0] + s_, c[1] - s_ + o * 4), (c[0] - s_, c[1] + s_), 7.5, seed + 3 + o, 2)
    cv.overL(ly, INK, .7 * k)
    cv.addL(ly, GREASE_R, 1.0 * k)
    cv.add(GREASE_R, blur(ly.m, 5), .4 * k, ly.off)


def decay_ring(cv, B, k=1.0, frac=1.0):
    """a DOWN Site's clock: plum veins creeping inward over the pad, ring half-eaten."""
    bx = (B[0] - 60, B[1] - 40, B[0] + 60, B[1] + 40)
    ly = Lyr(bx)
    ly.line(SC.ring_pts(B, 44, 60, a0=0, a1=360 * frac), 2.6, 255, dash=(4, 4))
    rng = np.random.RandomState(int(B[0]))
    vn = Lyr(bx)
    for i in range(7):
        a = rng.uniform(0, 6.28)
        p0 = (B[0] + 44 * math.cos(a), B[1] + 44 * K * math.sin(a))
        p1 = (B[0] + 24 * math.cos(a + .4), B[1] + 24 * K * math.sin(a + .4))
        p2 = (B[0] + 12 * math.cos(a - .3), B[1] + 12 * K * math.sin(a - .3))
        vn.line([p0, p1, p2], 1.8, 255)
    cv.neonL(ly, VEIN, core=.9 * k, g1=(2, .5 * k), g2=None)
    cv.neonL(vn, VEIN * .8, core=.8 * k, g1=(2, .4 * k), g2=None)


# ------------------------------------------------------------------ verdict stamp on corp paper
def stamp(cv, c, word, tier, angle=-6, size=1.0, glyph=True, ss=3):
    col = TIER[tier]
    ink = col * .78
    f = font(58 * size * ss, False, 800, 75)
    tb = f.getbbox(word)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    gw = int(76 * size * ss) if glyph else 0
    pad = int(30 * size * ss)
    W_ = tw + gw + pad * 2 + int(54 * size * ss)
    H_ = int(th + pad * 1.7)
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pc = tuple(int(x * 255) for x in PAPER) + (255,)
    d.rounded_rectangle((0, 0, W_ - 1, H_ - 1), 14 * ss, fill=pc)
    # string hole
    d.ellipse((12 * ss, H_ / 2 - 9 * ss, 30 * ss, H_ / 2 + 9 * ss), fill=(20, 12, 36, 255))
    inkc = tuple(int(x * 255) for x in ink) + (255,)
    x0 = int(46 * size * ss)
    d.rounded_rectangle((x0 - 6 * ss, 12 * ss, W_ - 14 * ss, H_ - 12 * ss), 8 * ss, outline=inkc, width=int(4 * ss * size))
    d.rounded_rectangle((x0 - 1 * ss, 17 * ss, W_ - 19 * ss, H_ - 17 * ss), 5 * ss, outline=inkc, width=int(2 * ss * size))
    gl = Lyr((0, 0, W_ // ss + 2, H_ // ss + 2), ss=ss, pad=0)
    if glyph:
        g_tier(gl, tier, (x0 / ss + 38 * size, H_ / ss / 2), 30 * size)
        gm = Image.fromarray((np.asarray(gl.im, np.float32)[:H_, :W_]).astype(np.uint8))
        solid = Image.new('RGBA', (W_, H_), inkc)
        im.paste(solid, (0, 0), gm)
    d.text((x0 + gw + 14 * ss * size + tw / 2, H_ / 2 + 2 * ss), word, font=f, fill=inkc, anchor='mm')
    # rubber-stamp wear: erode ink with noise
    arr = np.asarray(im, np.float32) / 255
    rng = np.random.RandomState(5)
    nz = rng.rand(H_ // 3 + 2, W_ // 3 + 2).astype(np.float32)
    nz = np.asarray(Image.fromarray((nz * 255).astype(np.uint8)).resize((W_, H_), Image.BICUBIC), np.float32) / 255
    isink = (np.abs(arr[..., :3] - ink).sum(2) < .25)
    wear = (nz > .86) & isink
    arr[wear, :3] = PAPER
    im2 = Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    im2 = im2.resize((W_ // ss, H_ // ss), Image.LANCZOS).rotate(angle, expand=True, resample=Image.BICUBIC)
    a = np.asarray(im2, np.float32) / 255
    ox, oy = int(c[0] - a.shape[1] / 2), int(c[1] - a.shape[0] / 2)
    cv.over(INK, blur(a[..., 3], 8), .7, (ox + 6, oy + 10))
    cv.over(a[..., :3], a[..., 3], 1.0, (ox, oy))
    cv.add(col, blur(a[..., 3], 14), .22, (ox, oy))
    return a.shape[1], a.shape[0]


# ------------------------------------------------------------------ sealed routes, hunter
def fog_band(cv, path, s0, s1, width=26, seed=1, k=1.0, col=FOG):
    """sealed route = a corridor of static + glyph rain; you see where it may run, never what is in it."""
    pts = sub(path, s0, s1, 6)
    if len(pts) < 2:
        return
    bb = pbox(pts, width)
    band = Lyr(bb, ss=1)
    band.line([tuple(p) for p in pts], width, 255)
    m = band.m
    x0, y0 = band.off
    rng = np.random.RandomState(seed)
    nz = rng.rand(m.shape[0] // 3 + 3, m.shape[1] // 3 + 3).astype(np.float32)
    nz = np.asarray(Image.fromarray((nz * 255).astype(np.uint8)).resize((m.shape[1] + 9, m.shape[0] + 9), Image.BICUBIC), np.float32)[:m.shape[0], :m.shape[1]] / 255
    stat = rng.rand(*m.shape).astype(np.float32)
    fade = m * (.35 + .65 * nz)
    cv.over(col * .18, blur(m, 3), .32 * k, (x0, y0))
    cv.add(col, fade * (stat > .80), .5 * k, (x0, y0))
    cv.add(col, blur(fade, 5), .16 * k, (x0, y0))
    # glyph rain
    g = Lyr(bb, ss=1)
    n = int(len(pts) * .7)
    for i in range(n):
        p = pts[int(rng.randint(0, len(pts)))] + rng.uniform(-width * .4, width * .4, 2)
        ch = rng.choice(list('01FA7C3E9'))
        g.text(tuple(p), ch, 11, int(rng.uniform(120, 255)), mono=True)
    cv.add(WHITE * .8 + col * .2, g.m, .6 * k, g.off)


def lock(cv, c, letter, state='locked', typ=None, r=21, k=1.0, pulse=0.0):
    """letter lock: a hex padlock with the route's letter. Opens to the beam-type silhouette when revealed."""
    col = FOG if state == 'locked' else TYPE_COL[typ]
    bx = (c[0] - r - 20, c[1] - r - 36, c[0] + r + 20, c[1] + r + 20)
    f = Lyr(bx); e = Lyr(bx); sh = Lyr(bx); tx = Lyr(bx)
    hexp = [(c[0] + r * math.cos(math.radians(60 * i + 30)), c[1] + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    f.poly(hexp)
    e.line(hexp + [hexp[0]], 2.8, 255)
    if state == 'locked':
        sh.arc((c[0], c[1] - r * .75), r * .52, 180, 360, 3.2)
        sh.line([(c[0] - r * .52, c[1] - r * .75), (c[0] - r * .52, c[1] - r * .3)], 3.2)
        sh.line([(c[0] + r * .52, c[1] - r * .75), (c[0] + r * .52, c[1] - r * .3)], 3.2)
    else:
        sh.arc((c[0] + r * .4, c[1] - r * .8), r * .52, 180, 360, 3.2)
        sh.line([(c[0] - r * .12, c[1] - r * .8), (c[0] - r * .12, c[1] - r * .38)], 3.2)
    cv.overL(f, INK, .92 * k)
    cv.neonL(e, col, core=1.0 * k, g1=(3, .7 * k), g2=(10, .4 * k))
    cv.neonL(sh, col, core=1.0 * k, g1=(2, .5 * k), g2=None)
    if state == 'locked':
        tx.text((c[0], c[1] + 1), letter, r * 1.15, 255)
        cv.neonL(tx, WHITE * .85 + col * .15, core=1.0 * k, g1=(2, .5 * k), g2=None)
    else:
        g_type(tx, typ, (c[0], c[1]), r * .58)
        cv.neonL(tx, col, core=1.0 * k, g1=(2, .6 * k), g2=None, white=.4)


def hunter_eye(cv, c, r=34, k=1.0, col=None):
    col = HOT if col is None else col
    bx = (c[0] - r * 1.8, c[1] - r * 1.5, c[0] + r * 1.8, c[1] + r * 1.5)
    ly = Lyr(bx); sc = Lyr(bx)
    g_eye(ly, c, r)
    for i in range(16):
        a = math.radians(i * 22.5)
        sc.line([(c[0] + r * 1.18 * math.cos(a), c[1] + r * .8 * math.sin(a)), (c[0] + r * 1.4 * math.cos(a), c[1] + r * .95 * math.sin(a))], 2, 255)
    cv.overL(ly, INK, 0)
    cv.neonL(ly, col, core=1.0 * k, g1=(3, .8 * k), g2=(12, .55 * k), white=.5)
    cv.neonL(sc, col, core=.6 * k, g1=None, g2=None)


def reticle(cv, c, r=30, col=None, k=1.0):
    col = WHITE if col is None else col
    bx = (c[0] - r * 1.6, c[1] - r * 1.6, c[0] + r * 1.6, c[1] + r * 1.6)
    ly = Lyr(bx)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (c[0] + sx * r, c[1] + sy * r * .78)
            ly.line([(p[0], p[1] - sy * 11), p, (p[0] - sx * 14, p[1])], 3, 255)
    ly.line(SC.ring_pts(c, r * .55, 40), 1.8, 255)
    ly.line([(c[0] - r * 1.3, c[1]), (c[0] - r * .7, c[1])], 2, 255)
    ly.line([(c[0] + r * .7, c[1]), (c[0] + r * 1.3, c[1])], 2, 255)
    cv.neonL(ly, col, core=1.0 * k, g1=(3, .8 * k), g2=(10, .5 * k), white=.4)


# ------------------------------------------------------------------ odds chart (wordless: bars + tier glyphs)
def odds_chart(cv, B, probs, k=1.0, hi=None):
    """five iso bars standing on the street beside HOME: height = chance, cap = tier glyph."""
    tiers = ['UNTOUCHED', 'HOLDS', 'SITES_LOST', 'DAMAGED', 'BREACHED']
    ax = np.array([1.0, K])
    for i, t in enumerate(tiers):
        c = np.array(B) + ax * (i * 46)
        h = max(8, probs[i] * 1.9)
        a = 15
        L0, F0, R0, K0, L1, F1, R1, K1 = SC._box_edges(tuple(c), a, h)
        bx = (c[0] - 30, c[1] - h - 70, c[0] + 30, c[1] + 24)
        fL, fR, tp, ed = Lyr(bx), Lyr(bx), Lyr(bx), Lyr(bx)
        fL.poly([L0, F0, F1, L1], 255)
        fR.poly([F0, R0, R1, F1], 255)
        tp.poly([K1, R1, F1, L1], 255)
        ed.line([L0, F0, R0, R1, K1, L1, L0], 1.6, 255)
        ed.line([F0, F1], 1.6, 255)
        ed.line([L1, F1, R1], 1.6, 255)
        col = TIER[t]
        on = 1.0 if (hi is None or hi == i) else .55
        cv.overL(fL, INK, .6 * k)
        cv.overL(fR, INK, .6 * k)
        cv.addL(fL, col * .6, .35 * k * on)
        cv.addL(fR, col, .55 * k * on)
        cv.addL(tp, col, .8 * k * on)
        cv.neonL(ed, col, core=.9 * k * on, g1=(2, .5 * k * on), g2=None)
        tier_chip(cv, (c[0], c[1] - h - 30), t, r=17, k=k * on, num=int(round(probs[i])) if probs[i] >= 1 else None)


# ------------------------------------------------------------------ response keycaps
def g_deploy(ly, c, r):
    ly.rr(c[0] - r * .55, c[1] - r * .95, c[0] + r * .55, c[1] + r * .1, r * .15, 255)
    ly.poly([(c[0] - r * .55, c[1] + r * .38), (c[0] + r * .55, c[1] + r * .38), (c[0], c[1] + r * .98)])


def g_hold(ly, c, r):
    ly.rr(c[0] - r * .7, c[1] - r * .8, c[0] - r * .15, c[1] + r * .8, r * .1, 255)
    ly.rr(c[0] + r * .15, c[1] - r * .8, c[0] + r * .7, c[1] + r * .8, r * .1, 255)


def g_move(ly, c, r):
    ly.line([(c[0] - r * .9, c[1] - r * .45), (c[0] + r * .5, c[1] - r * .45)], r * .26)
    ly.poly([(c[0] + r * .35, c[1] - r * .9), (c[0] + r * 1.0, c[1] - r * .45), (c[0] + r * .35, c[1])])
    ly.line([(c[0] + r * .9, c[1] + r * .45), (c[0] - r * .5, c[1] + r * .45)], r * .26)
    ly.poly([(c[0] - r * .35, c[1]), (c[0] - r * 1.0, c[1] + r * .45), (c[0] - r * .35, c[1] + r * .9)])


def g_sac(ly, c, r):
    ly.poly([(c[0] - r * .7, c[1] + r * .95), (c[0] - r * .7, c[1] - r * .2), (c[0] - r * .15, c[1] - r * .2), (c[0] - r * .15, c[1] + r * .95)])
    g_flame(ly, (c[0] + r * .4, c[1] + r * .1), r * .72)


def resp_key(cv, c, kind, pips, selected=False, r=44, k=1.0):
    fn = {'DEPLOY': g_deploy, 'HOLD': g_hold, 'MOVE': g_move, 'SACRIFICE': g_sac}[kind]
    col = LATT if not selected else WHITE
    if selected:
        # lime focus halo (D25)
        hl = Lyr((c[0] - r - 16, c[1] - r - 16, c[0] + r + 16, c[1] + r + 16))
        hl.ell(c, r + 7, v=255, outline=True, ow=4)
        cv.neonL(hl, LIME, core=1.0, g1=(4, .9), g2=(12, .6))
    glyph_disc(cv, c, r, col if not selected else LATT, fn, gscale=.5, k=k, ring_w=3)
    n = len(pips)
    for i, t in enumerate(pips):
        p = (c[0] + (i - (n - 1) / 2) * 30, c[1] + r + 24)
        tier_chip(cv, p, t, r=11, k=k)


# ------------------------------------------------------------------ FX
def flash(cv, c, r, col=WHITE, k=1.0):
    bx = (c[0] - r, c[1] - r, c[0] + r, c[1] + r)
    ly = Lyr(bx, ss=1, pad=0)
    yy, xx = np.mgrid[0:ly.h, 0:ly.w].astype(np.float32)
    d = np.sqrt((xx + ly.off[0] - c[0]) ** 2 + (yy + ly.off[1] - c[1]) ** 2) / r
    g = np.clip(1 - d, 0, 1) ** 2.2
    cv.add(col, g, k, ly.off)
    cv.add(WHITE, np.clip(1 - d * 2.6, 0, 1) ** 1.5, k * .8, ly.off)


def shock(cv, c, r, col, w=4, k=1.0):
    bx = (c[0] - r * 1.1, c[1] - r * K * 1.2, c[0] + r * 1.1, c[1] + r * K * 1.2)
    ly = Lyr(bx)
    ly.line(SC.ring_pts(c, r, 80), w, 255)
    cv.neonL(ly, col, core=1.0 * k, g1=(4, .8 * k), g2=(12, .5 * k), white=.4)


def bits(cv, c, col, n=40, r=120, seed=3, size=(10, 17), k=1.0, spread=1.0):
    """binary bits flying off a destroyed thing (module 16 vocabulary)."""
    rng = np.random.RandomState(seed)
    bx = (c[0] - r * 1.5, c[1] - r * 1.1, c[0] + r * 1.5, c[1] + r * 1.1)
    ly = Lyr(bx, ss=1)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = r * (.25 + rng.rand() ** .7 * .85) * spread
        p = (c[0] + d * math.cos(a), c[1] + d * math.sin(a) * .75 - rng.uniform(0, 20))
        ly.text(p, str(rng.randint(0, 2)), rng.uniform(*size), int(rng.uniform(110, 255)), mono=True)
    cv.addL(ly, col * .7 + WHITE * .3, .95 * k)
    cv.add(col, blur(ly.m, 3), .5 * k, ly.off)


def hex_shards(cv, c, col, n=14, r=90, seed=4, k=1.0):
    rng = np.random.RandomState(seed)
    bx = (c[0] - r * 1.4, c[1] - r * 1.1, c[0] + r * 1.4, c[1] + r * 1.1)
    ly = Lyr(bx)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = r * (.3 + rng.rand() * .8)
        p = (c[0] + d * math.cos(a), c[1] + d * math.sin(a) * .8)
        ly.line(_hexcell(p, rng.uniform(5, 11), rng.uniform(0, 60)) + [_hexcell(p, 5, 0)[0]], 1.8, 255)
    cv.neonL(ly, col, core=1.0 * k, g1=(2, .6 * k), g2=(7, .4 * k))


def glitch_tear(cv, box, amount=1.0, seed=7, bands=9, split=True, maxdx=48):
    """datamosh tear: bands of the finished frame slide sideways with feathered ends, RGB splits, bright seams."""
    rng = np.random.RandomState(seed)
    x0, y0, x1, y1 = [int(v) for v in box]
    img = cv.img
    for i in range(bands):
        h = int(rng.uniform(4, 16))
        y = int(rng.uniform(y0, y1 - h))
        bx0 = int(rng.uniform(x0, x0 + (x1 - x0) * .4))
        bx1 = int(rng.uniform(x0 + (x1 - x0) * .6, x1))
        dx = int(rng.uniform(-maxdx, maxdx) * amount)
        seg = img[y:y + h, bx0:bx1].copy()
        sh = np.roll(seg, dx, 1)
        if split:
            sh[..., 0] = np.roll(sh[..., 0], int(6 * amount), 1)
            sh[..., 2] = np.roll(sh[..., 2], -int(6 * amount), 1)
        f = np.clip(np.minimum(np.arange(bx1 - bx0), np.arange(bx1 - bx0)[::-1]) / 40.0, 0, 1)[None, :, None]
        img[y:y + h, bx0:bx1] = seg * (1 - f) + sh * f
        if i % 3 == 0:
            img[y:y + 1, bx0:bx1] += np.array([.25, .9, 1.0], np.float32) * .3 * amount * f[0]
            img[y + h - 1:y + h, bx0:bx1] += np.array([1.0, .25, .8], np.float32) * .3 * amount * f[0]


def num_tag(cv, c, s, col, size=34, k=1.0):
    ntext(cv, c, s, size, col, stroke=3, white=.25, k=k)


def focus_dim(cv, c, r, amt=.45, soft=.7):
    """quiet the rest of the city so the event reads (applied to the world before FX are drawn)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - c[0]) / r) ** 2 + ((yy - c[1]) / (r * .8)) ** 2)
    m = np.clip((d - .55) / soft, 0, 1) * amt
    cv.img *= (1 - m)[..., None]
