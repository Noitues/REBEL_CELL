"""H "Jack-in over the Night City": the hybrid layers.
One beam body (A's cased, traffic-coloured, chevron route ribbon on the real street polylines), E's daemon
silhouettes as heads only, F's intent tiles / grease tally / stencil discs / wheatpaste poster / vinyl cards / HUD,
D's HOME ring + damage chip. Everything is drawn over E's world (ICE towers on Sites only, no city-wide wireframe)."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from lib import *
from glyphs import *
from daemon import head_shape, lane, extend_back
import scene as SC
import ui

K = 0.643
HERE = os.path.dirname(os.path.abspath(__file__))
TIERS = ['UNTOUCHED', 'HOLDS', 'SITES_LOST', 'DAMAGED', 'BREACHED']
BONE = hexc('F6F0DE')
DEAD = hexc('8A90A8')


def fnt(name, size):
    return ImageFont.truetype(os.path.join(HERE, name), int(size))


# ------------------------------------------------------------------ path helper (fast arclength access)
class PX:
    def __init__(self, pts):
        self.p = np.asarray(pts, float)
        self.c = cum_len(self.p)
        self.L = float(self.c[-1])

    def at(self, s):
        s = max(0.0, min(s, self.L))
        i = min(int(np.searchsorted(self.c, s, side='right') - 1), len(self.p) - 2)
        seg = self.c[i + 1] - self.c[i]
        u = 0 if seg < 1e-9 else (s - self.c[i]) / seg
        p = self.p[i] + (self.p[i + 1] - self.p[i]) * u
        d = self.p[i + 1] - self.p[i]
        ang = math.atan2(d[1], d[0])
        return p, ang

    def frame(self, s):
        p, a = self.at(s)
        u = np.array([math.cos(a), math.sin(a)])
        return p, u, np.array([-u[1], u[0]])

    def sub(self, s0, s1, step=4.0):
        s0 = max(0, s0); s1 = min(self.L, s1)
        if s1 <= s0:
            return np.array([self.at(s0)[0]])
        ss = list(np.arange(s0, s1, step)) + [s1]
        return np.array([self.at(s)[0] for s in ss])


def seg_lyr(L, pts, w, v=255):
    L.line([tuple(p) for p in pts], w, v)


# ------------------------------------------------------------------ THE beam body: cased, chevroned route ribbon
def ribbon(cv, path, typ, s0, s1, cols=None, k=1.0, w=8.0, edge=None, dead=False, chev=True, glow=1.0):
    """A's route ribbon on the real street, one per beam. Pattern is the second type cue:
    D dashed links, N braided double strand, E solid wide band; chevrons run in the travel direction.
    cols: None -> type colour, else [(s_end, rgb), ...] covering s0..s1 (the forecast's traffic colouring).
    edge: thin rail colour (the type hue) under a tier-coloured fill."""
    P = path if isinstance(path, PX) else PX(path)
    s1 = min(s1, P.L)
    if s1 - s0 < 6:
        return
    tc = TYPE_COL[typ]
    if dead:
        tc = DEAD
    segs = [(s0, s1, tc)] if cols is None else []
    if cols is not None:
        a = s0
        for se, c in cols:
            se = min(se, s1)
            if se > a:
                segs.append((a, se, c))
                a = se
    pts = P.sub(s0, s1, 4)
    bb = pbox(pts, 30)
    if cols is not None and not dead:
        # FORECAST: traffic colour = a tier-coloured rail either side of the beam (type hue stays on the beam itself)
        for (a_, b_, col_) in segs:
            tl = Lyr(bb)
            seg_lyr(tl, P.sub(a_, b_, 4), w + 19, 255)
            cv.over(np.asarray(col_, np.float32), tl.m, (.5 if col_[0] < 0 or tuple(np.round(col_, 2)) == tuple(np.round(TIER['UNTOUCHED'], 2)) else .97) * k, tl.off)
            cv.add(np.asarray(col_, np.float32), blur(tl.m, 7), .3 * k, tl.off)
        segs = [(s0, s1, tc)]
    cas = Lyr(bb)
    seg_lyr(cas, pts, w + 7.5 if typ != 'N' else w + 11, 255)
    cv.over(INK, cas.m, .92 * k, cas.off)
    for (a, b, col) in segs:
        col = np.asarray(col, np.float32)
        fm = Lyr(bb)
        ch = Lyr(bb)
        if typ == 'D':
            on, off = 15.0, 8.0
            t = a - ((a - s0) % (on + off)) if False else a
            while t < b:
                t2 = min(t + on, b)
                if t2 - t > 2:
                    seg_lyr(fm, P.sub(t, t2, 2.5), w, 255)
                if chev and t2 - t > 8:
                    p, u, n = P.frame((t + t2) / 2)
                    ch.line([tuple(p - u * 3 + n * 3.6), tuple(p + u * 2.6), tuple(p - u * 3 - n * 3.6)], 2.0, 255)
                t += on + off
        elif typ == 'N':
            lam = 24.0
            amp = 5.0
            ss_ = np.arange(a, b, 2.0)
            A_ = []
            B_ = []
            for s in ss_:
                p, u, n = P.frame(s)
                sn = math.sin(2 * math.pi * s / lam)
                A_.append(p + n * amp * sn)
                B_.append(p - n * amp * sn)
            if len(A_) > 2:
                seg_lyr(fm, A_, 3.6, 255)
                seg_lyr(fm, B_, 3.6, 255)
                for i in range(0, len(A_), 6):
                    fm.line([tuple(A_[i]), tuple(B_[i])], 1.5, 200)
        else:
            seg_lyr(fm, P.sub(a, b, 3), w + 1.5, 255)
            if chev:
                s = a + 14
                while s < b - 8:
                    p, u, n = P.frame(s)
                    ch.line([tuple(p - u * 5 + n * 5.4), tuple(p + u * 3.6), tuple(p - u * 5 - n * 5.4)], 3.0, 255)
                    s += 28
        fmm = fm.m
        cv.over(col * .92 + WHITE * .08, fmm, .97 * k, fm.off)
        cv.add(col * .55 + WHITE * .45, np.clip(fmm * fmm, 0, 1), .22 * k, fm.off)
        if typ != 'N' and chev:
            cv.over(INK, ch.m, .78 * k, ch.off)
        cv.add(col, blur(fmm, 4), .45 * k * glow, fm.off)
        cv.add(col, blur(fmm, 11), .26 * k * glow, fm.off)
    if typ == 'N' and chev:
        ch = Lyr(bb)
        s = s0 + 16
        while s < s1 - 8:
            p, u, n = P.frame(s)
            ch.line([tuple(p - u * 3.4 + n * 4.8), tuple(p + u * 3), tuple(p - u * 3.4 - n * 4.8)], 1.8, 255)
            s += 48
        cv.add(WHITE, ch.m, .75 * k, ch.off)


def stop_bar(cv, path, s, col, k=1.0, half=17):
    """Into-the-Breach flat end: a bar across the street where a beam stops."""
    P = path if isinstance(path, PX) else PX(path)
    p, u, n = P.frame(s)
    a, b = p + n * half, p - n * half
    ly = Lyr(pbox([a, b], 12))
    ly.line([tuple(a), tuple(b)], 9, 255)
    ly2 = Lyr(pbox([a, b], 12))
    ly2.line([tuple(a), tuple(b)], 5, 255)
    cv.over(INK, ly.m, .92 * k, ly.off)
    cv.neonL(ly2, col, core=1.0 * k, g1=(3, .7 * k), g2=(9, .4 * k), white=.35)


def dead_trail(cv, path, s0, s1, k=.7):
    """what a stopped beam would have done: grey dotted."""
    P = path if isinstance(path, PX) else PX(path)
    pts = P.sub(s0, min(s1, P.L), 2)
    if len(pts) < 2:
        return
    ly = Lyr(pbox(pts, 8))
    s = 0.0
    L = P.L
    t = s0
    while t < min(s1, L):
        p, _ = P.at(t)
        ly.ell(tuple(p), 2.1, v=255)
        t += 13
    cv.add(DEAD, ly.m, .8 * k, ly.off)


# ------------------------------------------------------------------ daemon HEADS only (E's silhouettes)
def head_shape2(typ, p, u, n, sc=1.0):
    """E's silhouettes; the E enforcer gets a stronger horned-ram outline (U of bull horns round a lens)."""
    if typ != 'E':
        return head_shape(typ, p, u, n, sc)

    def P_(x, y):
        return p + u * x * sc + n * y * sc
    body = [P_(-14, -13), P_(8, -13), P_(12, -8), P_(12, 8), P_(8, 13), P_(-14, 13)]
    hr = [P_(3, 12), P_(13, 25), P_(30, 30), P_(44, 20), P_(49, 5), P_(41, 13), P_(29, 21), P_(17, 17), P_(9, 10)]
    hl = [P_(x, -y) for x, y in ((3, 12), (13, 25), (30, 30), (44, 20), (49, 5), (41, 13), (29, 21), (17, 17), (9, 10))]
    return {'fill': [body, hr, hl], 'rim': [body + [body[0]], hr + [hr[0]], hl + [hl[0]]], 'eye': (P_(0, 0), 5.0 * sc)}


def head(cv, path, s, typ, sc=1.7, mode='full', k=1.0, tail=120, col=None):
    """E's daemon silhouette, head only: D arrow in blue, N square cursor in magenta, E horned ram in signal yellow."""
    P = path if isinstance(path, PX) else PX(path)
    p, u, n = P.frame(s)
    col = TYPE_COL[typ] if col is None else col
    hs = head_shape2(typ, p, u, n, sc)
    allp = [x for poly in hs['rim'] for x in poly]
    bb = pbox([tuple(x) for x in allp] + [tuple(P.at(max(0, s - tail))[0])], 40)
    fill, rim, spine = Lyr(bb), Lyr(bb), Lyr(bb)
    for poly in hs['fill']:
        fill.poly([tuple(x) for x in poly], 255)
    rw = 2.8 * sc ** .75
    for ln in hs['rim']:
        rim.line([tuple(x) for x in ln], rw if mode != 'ghost' else rw * .6, 255)
    if mode == 'ghost':
        cv.neon(rim.m, col, core=.85 * k, g1=(3, .4 * k), g2=None, off=rim.off)
        return
    if 'eye' in hs:
        spine.ell(tuple(hs['eye'][0]), hs['eye'][1], v=255)
    if 'cursor' in hs:
        c, u2, n2, r = hs['cursor']
        q = [c + u2 * r * .45 + n2 * r * .45, c + u2 * r * .45 - n2 * r * .45, c - u2 * r * .45 - n2 * r * .45, c - u2 * r * .45 + n2 * r * .45]
        spine.poly([tuple(x) for x in q], 255)
        for a in hs['ant']:
            rim.line([tuple(x) for x in a], 2.0 * sc ** .7, 255)
    if typ == 'E':
        acc = Lyr(bb)
        acc.ell(tuple(hs['eye'][0]), hs['eye'][1] * 1.9, v=255, outline=True, ow=1.6)
        cv.add(col, acc.m, .9 * k, acc.off)
    cv.add(col, blur(fill.m, 10), .35 * k, fill.off)
    cv.over(INK, fill.m, .94 * k, fill.off)
    cv.neon(rim.m, col, core=1.0 * k, g1=(3.5, .9 * k), g2=(13, .65 * k), off=rim.off)
    cv.add(WHITE, spine.m, .95 * k, spine.off)
    cv.add(col, blur(spine.m, 4), .5 * k, spine.off)


# ------------------------------------------------------------------ F intent tile (hex plate + tier glyph + number)
def hexpts(c, r, rot=30):
    return [(c[0] + r * math.cos(math.radians(60 * i + rot)), c[1] + r * math.sin(math.radians(60 * i + rot))) for i in range(6)]


def hex_tile(cv, c, tier, num=None, r=23, k=1.0, numcol=None, side='r'):
    col = TIER[tier]
    bx = (c[0] - r - 8, c[1] - r - 8, c[0] + r + 8, c[1] + r + 8)
    o = Lyr(bx); f = Lyr(bx); e = Lyr(bx); g = Lyr(bx)
    o.poly(hexpts(c, r + 4.5), 255)
    f.poly(hexpts(c, r), 255)
    e.line(hexpts(c, r) + [hexpts(c, r)[0]], max(2.6, r * .13), 255)
    g_tier(g, tier, c, r * .56)
    cv.overL(o, INK, .96 * k)
    cv.overL(f, hexc('0B0F2A'), .96 * k)
    cv.addL(f, col, .10 * k)
    cv.neonL(e, col, core=1.0 * k, g1=(3, .7 * k), g2=(9, .4 * k))
    cv.neonL(g, col, core=1.0 * k, g1=(2, .5 * k), g2=None, white=.3 * k)
    if num is not None:
        x = c[0] + r + 12 if side == 'r' else c[0] - r - 12
        ui.ntext(cv, (x, c[1] + 1), str(num), int(r * 1.25), numcol if numcol is not None else col, anchor='lm' if side == 'r' else 'rm', stroke=3, k=k)


def leader(cv, a, b, k=.8, col=None):
    ly = Lyr(pbox([a, b], 6), ss=2)
    ly.line([tuple(a), tuple(b)], 1.4, 255)
    cv.neonL(ly, WHITE * .75 + LATT * .25 if col is None else col, core=.7 * k, g1=None, g2=None)


def fan(anchors, min_d=64.0, iters=60, bias=(0, -1), y_floor=60):
    """DECLUTTER RULE for site clusters: tiles leave their towers on hairline leaders and fan out so that no two
    tiles are closer than min_d (ordered by x, pushed up/out, never across each other). anchors: list of (x, y)."""
    pos = [np.array(a, float) for a in anchors]
    for _ in range(iters):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                d = pos[j] - pos[i]
                dist = np.hypot(*d)
                if dist < min_d:
                    if dist < 1e-3:
                        d = np.array([1.0, -.2]); dist = 1.0
                    push = (min_d - dist) / 2 + .5
                    u = d / dist
                    pos[i] -= u * push
                    pos[j] += u * push
                    moved = True
        if not moved:
            break
    return [tuple(np.maximum(p, [40, y_floor])) for p in pos]


# ------------------------------------------------------------------ grease pencil (waxy) helpers + F tally
def waxy(m, seed, rough=.55, sc=2.6):
    nz = SC.noise(seed, sc, shape=m.shape)
    mm = blur(m, 1.0) + (nz - .5) * rough
    return np.clip((mm - .45) * 6, 0, 1)


def waxy_glyph(cv, c, fn, r, col, seed=1, k=1.0, backing=True):
    bx = (c[0] - r * 1.6, c[1] - r * 1.6, c[0] + r * 1.6, c[1] + r * 1.6)
    g = Lyr(bx)
    fn(g, c, r)
    m = waxy(g.m, seed)
    if backing:
        cv.over(INK, blur(g.m, 3.2) * 1.5, .85 * k, g.off)
    cv.over(col, m, .96 * k, g.off)
    cv.add(col, blur(m, 5), .18 * k, g.off)


def tally(cv, c, counts, r=15, gap=36, group_gap=16, k=1.0, seed=3):
    """F's grease-pencil tally: one glyph per simulated outcome, grouped in tier order (the odds as a row of marks)."""
    seq = []
    for t in TIERS:
        seq += [t] * counts.get(t, 0)
    n = len(seq)
    ng = len([t for t in TIERS if counts.get(t, 0)])
    wtot = (n - 1) * gap + (ng - 1) * group_gap
    x = c[0] - wtot / 2
    prev = None
    for i, t in enumerate(seq):
        if prev is not None and t != prev:
            x += group_gap
        waxy_glyph(cv, (x, c[1]), lambda l, c_, r_, t=t: g_tier(l, t, c_, r_), r, TIER[t], seed + i, k)
        x += gap
        prev = t


# ------------------------------------------------------------------ vinyl cards (F: colour-coded by beam type)
def vcard_sprite(verb, typ, w=104, h=140, ss=3):
    col = TYPE_COL[typ]
    outer, inner, gl, tg, hl = (Lyr((0, 0, w, h), ss=ss, pad=0) for _ in range(5))
    outer.rr(1, 1, w - 1, h - 1, 13, 255)
    inner.rr(7, 7, w - 7, h - 7, 8, 255)
    ui.VERB_FN[verb](gl, (w / 2, h * .58), 29)
    g_type(tg, typ, (22, 23), 9.5)
    hl.poly([(w * .1, h * .98), (w * .55, h * .02), (w * .72, h * .02), (w * .27, h * .98)], 255)
    o, i_, g_, t_, h_ = (x.m[:h, :w] for x in (outer, inner, gl, tg, hl))
    img = np.zeros((h, w, 3), np.float32)
    img[:] = hexc('FBF8EC')
    face = col * .94
    img = img * (1 - i_[..., None]) + face * i_[..., None]
    img = img * (1 - g_[..., None]) + INK * g_[..., None]
    img = img * (1 - t_[..., None]) + INK * t_[..., None]
    img = img + WHITE * (h_ * i_ * .12)[..., None]
    return img, o


def vcard(cv, c, verb, typ, angle=0.0, lime=False, k=1.0, sc=1.0):
    img, a = vcard_sprite(verb, typ)
    h, w = a.shape
    im = Image.fromarray((np.clip(np.dstack([img, a]), 0, 1) * 255).astype(np.uint8), 'RGBA')
    if sc != 1.0:
        im = im.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox, oy = int(c[0] - arr.shape[1] / 2), int(c[1] - arr.shape[0] / 2)
    cv.over(INK, blur(arr[..., 3], 7), .6 * k, (ox + 4, oy + 9))
    if lime:
        big = Image.fromarray((arr[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        ring = np.clip(np.asarray(big, np.float32) / 255 - arr[..., 3], 0, 1)
        cv.add(LIME, blur(arr[..., 3], 6), .9, (ox, oy))
        cv.add(LIME, ring, 1.0, (ox, oy))
    cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))


def hand(cv, cards, y=975, k=1.0, lift=None, skip=None, spread=108, sc=.9):
    n = len(cards)
    x0 = W / 2 - (n - 1) / 2 * spread
    for i, (verb, typ) in enumerate(cards):
        if skip is not None and i == skip:
            continue
        t = i - (n - 1) / 2
        yy = y + abs(t) ** 1.6 * 8 - (34 if lift == i else 0)
        vcard(cv, (x0 + i * spread, yy), verb, typ, -t * 3.4, lime=(lift == i), k=k, sc=sc)


# ------------------------------------------------------------------ HUD (F's layout in the game's CRT-chip language)
def g_bio(ly, c, r):
    for kk in range(3):
        a = -math.pi / 2 + kk * 2 * math.pi / 3
        ly.ell((c[0] + math.cos(a) * r * .5, c[1] + math.sin(a) * r * .5), r * .52, v=255)
    for kk in range(3):
        a = -math.pi / 2 + kk * 2 * math.pi / 3
        ly.ell((c[0] + math.cos(a) * r * .66, c[1] + math.sin(a) * r * .66), r * .3, v=0)
        ly.ell((c[0] + math.cos(a) * r * .98, c[1] + math.sin(a) * r * .98), r * .36, v=0)
    ly.ell(c, r * .3, v=0)
    ly.ell(c, r * .16, v=255)


def hud(cv, home=44, home_max=50, heat=80, healthy=8, infected=0, home_col=None, heat_tint=None, flash=0.0, lost=False):
    hc = (WHITE * .88 + LATT * .12) if home_col is None else home_col
    ui.crt_chip(cv, 22, 14, 248, 70, k=1.0)
    gl = Lyr((30, 20, 70, 64)); g_house(gl, (48, 42), 16)
    cv.neonL(gl, hc, core=1, g1=(2, .5), g2=None, white=.3)
    ui.ntext(cv, (76, 42), str(home), 36, hc, anchor='lm', stroke=2)
    ui.ntext(cv, (150, 46), '/%d' % home_max, 20, LATT_D * .9 + WHITE * .1, anchor='lm', stroke=0, glow=False, white=0)
    ui.crt_chip(cv, 260, 14, 420, 70)
    fg = Lyr((268, 20, 308, 64)); g_flame(fg, (286, 42), 16)
    hcol = ui.HEAT if heat_tint is None else heat_tint
    cv.neonL(fg, hcol, core=1, g1=(3, .6), g2=None, white=.2)
    ui.ntext(cv, (314, 42), str(heat), 36, hcol, anchor='lm', stroke=2)
    # INFECTED (plum biohazard) vs healthy (card) with a balance beam tipping to the heavier side
    x0, x1 = 1590, 1898
    ui.crt_chip(cv, x0, 14, x1, 70, col=(VEIN * .75 if (lost or infected > healthy) else LATT_D))
    bio = Lyr((x0 + 6, 18, x0 + 62, 66))
    bio.ell((x0 + 32, 42), 21, v=255)
    cv.overL(bio, PLUM_MID * 1.2, .95)
    bg = Lyr((x0 + 6, 18, x0 + 62, 66)); g_bio(bg, (x0 + 32, 42), 15)
    cv.neonL(bg, VEIN, core=1.0, g1=(2, .6), g2=None, white=.2)
    ring = Lyr((x0 + 6, 18, x0 + 62, 66)); ring.ell((x0 + 32, 42), 21, v=255, outline=True, ow=2.2)
    cv.neonL(ring, VEIN * .9, core=.9, g1=(2, .5), g2=None)
    ui.ntext(cv, (x0 + 66, 42), str(infected), 36, VEIN * .8 + HOT * .2 if infected else PLUM_MID * 2.4, anchor='lm', stroke=2)
    mid = (x0 + x1) / 2 + 4
    tilt = float(np.clip((infected - healthy) / max(infected + healthy, 1), -1, 1)) * 11
    bl = Lyr((mid - 36, 16, mid + 36, 68))
    bl.line([(mid - 30, 38 + tilt), (mid + 30, 38 - tilt)], 3.0, 255)
    bl.line([(mid, 38), (mid, 58)], 2.6, 255)
    bl.line([(mid - 10, 58), (mid + 10, 58)], 3.0, 255)
    bl.ell((mid, 38), 3.6, v=255)
    cv.neonL(bl, WHITE * .85, core=.95, g1=(2, .4), g2=None)
    cd = Lyr((x1 - 100, 18, x1 - 6, 66))
    cd.rr(x1 - 86, 28, x1 - 66, 56, 3, 255, outline=True, ow=2.2)
    cd.rr(x1 - 80, 34, x1 - 72, 50, 1, 255)
    cv.neonL(cd, TIER['HOLDS'], core=.95, g1=(2, .4), g2=None)
    ui.ntext(cv, (x1 - 58, 42), str(healthy), 36, TIER['HOLDS'], anchor='lm', stroke=2)
    if flash:
        cv.add(TIER['DAMAGED'], np.full((56, 226), flash * .3, np.float32), 1, (22, 14))


# ------------------------------------------------------------------ F stencil discs (RESPONSE)
def _g_deploy(l, c, r):
    ui.g_deploy(l, c, r * 1.05)


def stencil_disc(cv, c, kind, outs, selected=False, word='', r=62, k=1.0, seed=5):
    fn = {'DEPLOY': ui.g_deploy, 'HOLD': ui.g_hold, 'MOVE': ui.g_move, 'SACRIFICE': ui.g_sac}[kind]
    bx = (c[0] - r - 30, c[1] - r - 30, c[0] + r + 30, c[1] + r + 30)
    d = Lyr(bx); ring = Lyr(bx); g = Lyr(bx)
    d.ell(c, r)
    ring.ell(c, r, v=255, outline=True, ow=5)
    fn(g, c, r * .52)
    # stencil bridges: two ink gaps through the glyph
    for yy in (-.15, .35):
        g.line([(c[0] - r * .7, c[1] + r * yy), (c[0] + r * .7, c[1] + r * yy)], 2.6, 0)
    cv.overL(d, hexc('0A0D26'), .93 * k)
    if selected:
        hl = Lyr((c[0] - r - 22, c[1] - r - 22, c[0] + r + 22, c[1] + r + 22))
        hl.ell(c, r + 11, v=255, outline=True, ow=5)
        cv.neonL(hl, LIME, core=1.0, g1=(4, .9), g2=(12, .6))
    rm = waxy(ring.m, seed, .35)
    cv.over(INK, blur(ring.m, 3), .8 * k, ring.off)
    cv.over(BONE, rm, .95 * k, ring.off)
    gm = waxy(g.m, seed + 1, .3)
    cv.over(BONE if not selected else WHITE, gm, .98 * k, g.off)
    cv.add(BONE, blur(gm, 6), .2 * k, g.off)
    # three outcome tier glyphs above
    for i, t in enumerate(outs):
        p = (c[0] + (i - 1) * 40, c[1] - r - 36)
        tg = Lyr((p[0] - 22, p[1] - 22, p[0] + 22, p[1] + 22))
        g_tier(tg, t, p, 14)
        cv.over(INK, blur(tg.m, 3.2) * 1.5, .85 * k, tg.off)
        cv.neonL(tg, TIER[t], core=1.0 * k, g1=(2, .5 * k), g2=None, white=.25)
    if word:
        wl = Lyr((c[0] - 110, c[1] + r + 6, c[0] + 110, c[1] + r + 50))
        f = fnt('PermanentMarker-Regular.ttf', 27 * 2)
        im = Image.new('L', (wl.w * 2, wl.h * 2), 0)
        ImageDraw.Draw(im).text(((c[0] - wl.off[0]) * 2, (c[1] + r + 28 - wl.off[1]) * 2), word, font=f, fill=255, anchor='mm')
        m = np.asarray(im.reduce(2), np.float32) / 255
        cv.over(INK, blur(m, 2.4) * 2.2, .85 * k, wl.off)
        cv.over(BONE, m, .98 * k, wl.off)


# ------------------------------------------------------------------ F wheatpaste verdict poster
def halftone(m, rect, step, ang, grad, ss=2):
    x0, y0, x1, y1 = rect
    ca, sa = math.cos(ang), math.sin(ang)
    ly = Image.new('L', (m.shape[1] * ss, m.shape[0] * ss), 0)
    dr = ImageDraw.Draw(ly)
    for i in range(-80, 140):
        for j in range(-80, 140):
            px = x0 + (i * ca - j * sa) * step
            py = y0 + (i * sa + j * ca) * step
            if not (x0 <= px <= x1 and y0 <= py <= y1):
                continue
            kk = grad(px, py)
            if kk > .05:
                r = step * .5 * kk * ss
                dr.ellipse((px * ss - r, py * ss - r, px * ss + r, py * ss + r), fill=255)
    return np.asarray(ly.reduce(ss), np.float32) / 255


def poster(cv, c, tier, word, w=330, h=300, ang=-4.5, seed=5):
    """wheatpaste verdict poster: paper with torn edges and wrinkles, tier-colour block, halftone, tier glyph, ONE word."""
    col = TIER[tier]
    pw, ph = int(w + 60), int(h + 60)
    bx = (c[0] - pw / 2, c[1] - ph / 2, c[0] + pw / 2, c[1] + ph / 2)
    base = Lyr(bx, pad=0, ss=2)
    x0, y0 = base.off
    cx, cy = c
    base.rr(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 5, 255)
    blk = Lyr(bx, pad=0, ss=2)
    blk.rr(cx - w / 2 + 14, cy - h / 2 + 14, cx + w / 2 - 14, cy + h / 2 - 14, 3, 255)
    shape = base.m
    H_, W_ = shape.shape
    nz = SC.noise(seed, 3, shape=shape.shape)
    sil = np.clip((blur(shape, 1.2) + (nz - .5) * .45 - .5) * 8, 0, 1)
    gy0 = cy - h / 2 + 14
    gy1 = cy + h / 2 - 14
    ht = halftone(shape, (cx - w / 2 + 14 - x0, gy0 - y0, cx + w / 2 - 14 - x0, gy1 - y0), 11, .6,
                  lambda x, y: max(0.0, min(1.0, 1 - (y - (gy0 - y0)) / (gy1 - gy0))) * .95)
    img = np.zeros((H_, W_, 3), np.float32) + hexc('F0E4C8')
    wr = (SC.noise(seed + 2, 9, shape=shape.shape) - .5) * .12 + (SC.noise(seed + 3, 2.5, shape=shape.shape) - .5) * .05
    img = img * (1 + wr[..., None])
    bm = blk.m
    img = img * (1 - bm[..., None]) + (col * (1 + wr[..., None] * .6)) * bm[..., None]
    img = img * (1 - (ht * bm)[..., None] * .62) + (col * .42)[None, None, :] * (ht * bm)[..., None] * .62
    # glyph + word
    gl = Lyr(bx, pad=0, ss=2)
    g_tier(gl, tier, (cx, cy - 26), 78)
    gmk = gl.m
    img = img * (1 - gmk[..., None]) + hexc('FCF6E8') * gmk[..., None]
    gedge = np.clip(blur(gmk, 2.2) * 2.2, 0, 1) * (1 - gmk)
    img = img * (1 - gedge[..., None] * .85) + INK * gedge[..., None] * .85
    f = fnt('Anton-Regular.ttf', int(62 * 2))
    wim = Image.new('L', (W_ * 2, H_ * 2), 0)
    ImageDraw.Draw(wim).text(((cx - x0) * 2, (cy + h / 2 - 62 - y0) * 2), word, font=f, fill=255, anchor='mm', stroke_width=0)
    wm = np.asarray(wim.reduce(2), np.float32) / 255
    wedge = np.clip(blur(wm, 3) * 2.6, 0, 1) * (1 - wm)
    img = img * (1 - wedge[..., None]) + INK * wedge[..., None]
    img = img * (1 - wm[..., None]) + hexc('FCF6E8') * wm[..., None]
    # rotate everything together
    rgba = np.dstack([np.clip(img, 0, 1), sil])
    im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').rotate(ang, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox = int(c[0] - arr.shape[1] / 2); oy = int(c[1] - arr.shape[0] / 2)
    cv.over(INK, blur(arr[..., 3], 9), .75, (ox + 7, oy + 11))
    cv.over(arr[..., :3], arr[..., 3], 1.0, (ox, oy))
    cv.add(col, blur(arr[..., 3], 18), .16, (ox, oy))


# ------------------------------------------------------------------ HOME damage chip + HOME ticks leaving (D)
def home_chip(cv, home, dmg, k=1.0, tier='DAMAGED', hit=False):
    c = (home[0] + 112, home[1] - 74)
    ly = Lyr(pbox([home, c], 30))
    ly.line([(home[0] + 54, home[1] - 28), (c[0] - 22, c[1] + 10)], 1.6, 255)
    cv.neonL(ly, TIER[tier] * .8, core=.7 * k, g1=None, g2=None)
    hex_tile(cv, c, tier, '-%d' % dmg, r=30, k=k)
    return c


def spark_ticks(cv, home, n=6, hp=44, hp_max=50, R=74, k=1.0, seed=2):
    """the ticks the HOME hit knocks off the ring fly out as hot sparks."""
    rng = np.random.RandomState(seed)
    ly = Lyr((home[0] - 260, home[1] - 190, home[0] + 260, home[1] + 190))
    for i in range(hp - n, hp):
        ang = math.radians(-90 + i * 360 / hp_max)
        p0 = np.array([home[0] + (R - 2) * math.cos(ang), home[1] + (R - 2) * K * math.sin(ang)])
        d = np.array([math.cos(ang), math.sin(ang) * .7])
        dist = rng.uniform(40, 120)
        p1 = p0 + d * dist + np.array([0, -rng.uniform(10, 40)])
        ly.line([tuple(p0 + d * 12), tuple(p1)], 2.4, 255, dash=(3, 3))
        ly.line([tuple(p1), tuple(p1 + d * 9)], 4.2, 255)
    cv.neonL(ly, TIER['DAMAGED'], core=1.0 * k, g1=(3, .9 * k), g2=(9, .5 * k), white=.5)


# ------------------------------------------------------------------ hex shield flash (06)
def hex_flash(cv, c, r, col, k=1.0, seed=1):
    ly = Lyr((c[0] - r * 1.3, c[1] - r * 1.1, c[0] + r * 1.3, c[1] + r * 1.1), pad=10)
    fl = Lyr((c[0] - r * 1.3, c[1] - r * 1.1, c[0] + r * 1.3, c[1] + r * 1.1), pad=10)
    cs = r * .27
    for q in range(-5, 6):
        for p in range(-5, 6):
            x = c[0] + q * 1.5 * cs
            y = c[1] + (p * 1.732 + q * .866) * cs * .78
            d = math.hypot(x - c[0], (y - c[1]) / .78)
            if d > r:
                continue
            a = int(255 * (1 - d / r) ** 1.1)
            hp = [(x + cs * .92 * math.cos(math.radians(60 * i)), y + cs * .92 * .78 * math.sin(math.radians(60 * i))) for i in range(6)]
            ly.line(hp + [hp[0]], 1.8, a)
            fl.poly(hp, int(a * .35))
    cv.add(col, fl.m, .55 * k, fl.off)
    cv.neonL(ly, col * .5 + WHITE * .5, core=1.0 * k, g1=(2.5, .8 * k), g2=(9, .5 * k), white=.4)
    rr = Lyr((c[0] - r * 1.3, c[1] - r * 1.1, c[0] + r * 1.3, c[1] + r * 1.1), pad=10)
    rr.line(ring_pts(c, r, 80), 3.4, 255)
    cv.neonL(rr, WHITE * .7 + col * .3, core=1.0 * k, g1=(3, .8 * k), g2=(10, .5 * k))


# ------------------------------------------------------------------ HQ step: ghosted repair
def ghost_repair(cv, B, tier=1, k=1.0):
    SC.tower(cv, B, tier, 'healthy', tint=TIER['UNTOUCHED'], alpha=.5 * k, seed=4)
