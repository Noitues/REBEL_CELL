"""Live Nav concept: pins, bubbles, HUD, cards, Bloom, traffic."""
import math
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from lib import *

IND = hexc('2B2278')        # healthy pin body (deep indigo)
SLATE = hexc('59577A')
RAISED = hexc('E8E4F5')


def spr(w, h, fn, ss=4, out_scale=1.0):
    d = D(w, h, ss)
    fn(d)
    return d.out(out_scale)


def scrawl(d, p0, p1, col, w, seed=0, a=1.0, under=True):
    """grease-pencil stroke: wobbly, thick, near opaque, dark under-shadow (D28)."""
    rng = np.random.RandomState(seed)
    pts = []
    for t in np.linspace(0, 1, 7):
        x = p0[0] + (p1[0] - p0[0]) * t + rng.uniform(-w * .18, w * .18)
        y = p0[1] + (p1[1] - p0[1]) * t + rng.uniform(-w * .18, w * .18)
        pts.append((x, y))
    if under:
        d.line([(x + 1.2, y + 1.6) for x, y in pts], w + 2.6, INK, a=.85)
    d.line(pts, w, col, a=a)


def site_pin(cv, xy, tier=1, kind='stack', state='healthy', ring=None, ring_w=2.4, focus=False, scale=1.0,
             badge=None, dim=1.0, pulse=0.0, clock=None):
    """Map POI pin. Tip sits on the street node. state: healthy|DOWN|TAKEN."""
    r = {1: 12.5, 2: 14.5, 3: 17}[tier] * scale
    w = int(2 * r + 44)
    h = int(r * 3.2 + 40)
    cx, tipy = w / 2, h - 18

    def fn(d):
        # ground footprint (iso flattened)
        if ring is not None:
            d.ell(cx, tipy, r * 1.55, r * .78, out=INK, ow=ring_w + 2.4, a=.8)
            d.ell(cx, tipy, r * 1.55, r * .78, out=ring, ow=ring_w)
        if focus:
            d.ell(cx, tipy, r * 1.95, r * .98, out=INK, ow=7.5)
            d.ell(cx, tipy, r * 1.95, r * .98, out=LIME, ow=4.2)
        if clock is not None:      # decay clock: ring that fills toward TAKEN
            d.ell(cx, tipy, r * 1.5, r * .75, out=INK, ow=5, a=.7)
            n = int(clock * 36)
            for i in range(n):
                a0 = 2 * math.pi * i / 36 - math.pi / 2
                a1 = 2 * math.pi * (i + 1.02) / 36 - math.pi / 2
                pts = [(cx + math.cos(t) * r * 1.5, tipy + math.sin(t) * r * .75) for t in (a0, a1)]
                d.line(pts, 3.4, TIER['SITES_LOST'] if clock < .95 else TIER['BREACHED'], round_=False)
        # tier pips on the street
        for i in range(tier):
            d.ell(cx - (tier - 1) * 4 + i * 8, tipy + 7, 2.2, fill=PAPER, out=INK, ow=.8)
        if state == 'healthy':
            body, ico = IND, RAISED
        elif state == 'DOWN':
            body, ico = SLATE, hexc('C9C6D8')
        else:
            body, ico = PLUM, hexc('7A3A6E')
        cyh = g_pin_body(d, cx, tipy, r, PAPER, INK, 2.2)
        # inner coloured disc = category badge
        d.ell(cx, cyh, r * .78, fill=body)
        if state == 'TAKEN':
            d.ell(cx, cyh, r * .78, out=VEIN, ow=1.6, a=.9)
        g_site(d, kind, cx, cyh, r * .5, ico)
        if state == 'DOWN':
            scrawl(d, (cx - r * 1.05, cyh + r * .9), (cx + r * 1.05, cyh - r * .9), GREASE_Y, r * .34, seed=3)
        elif state == 'TAKEN':
            scrawl(d, (cx - r * .95, cyh - r * .95), (cx + r * .95, cyh + r * .95), GREASE_R, r * .36, seed=5)
            scrawl(d, (cx + r * .95, cyh - r * .95), (cx - r * .95, cyh + r * .95), GREASE_R, r * .36, seed=6)
        if badge is not None:
            bx, by = cx + r * .95, cyh - r * .85
            d.ell(bx, by, r * .42, fill=badge, out=INK, ow=1.4)
    a = spr(w, h, fn, 4)
    if dim < 1:
        a = a.copy()
        a[..., 3] *= dim
    cv.sprite(a, xy[0] - w / 2, xy[1] - (h - 18), shadow=.35, sh_off=(2, 4), sh_blur=3)


def origin_pin(cv, xy, pulse=0.0):
    """Corp HQ = the origin dot of the route (Maps hollow circle), with the Solace helix."""
    r = 28
    w = h = 150
    if pulse >= 0:   # light column: the origin 'pin beam'
        col = TIER['UNTOUCHED'] * .5 + VEIN * .5
        yy, xx = np.mgrid[0:int(xy[1] - 24), int(xy[0] - 60):int(xy[0] + 60)].astype(np.float32)
        k = np.clip(1 - np.abs(xx - xy[0]) / 38, 0, 1) ** 2 * np.clip(yy / max(1, xy[1] - 24), 0, 1) ** 1.6
        k = k * .0 + k
        cv.add(col, k * .55, (int(xy[0] - 60), 0))
    if pulse > 0:
        for k in range(3):
            rr = r * (1.0 + pulse * (0.9 + k * .55))
            al = max(0, 1 - pulse * (0.7 + k * .3)) * .55
            cv_ring(cv, xy, rr, 3, TIER['UNTOUCHED'], al, flat=.6)

    def fn(d):
        c = w / 2
        d.ell(c, c, r + 5, fill=INK, a=.9)
        d.ell(c, c, r + 2, fill=PAPER)
        d.ell(c, c, r - 4, fill=hexc('3A1E5A'))
        g_helix(d, c, c, r * .62, hexc('E6FF9A') * 0 + hexc('FFB8EC'))
    a = spr(w, h, fn, 4)
    cv.sprite(a, xy[0] - w / 2, xy[1] - h / 2 - 26, shadow=.4, sh_off=(2, 5), sh_blur=4)
    # stand on the street: tiny tether
    cv_ring(cv, (xy[0], xy[1]), 20, 3, INK, .9, flat=.5)


def cv_ring(cv, xy, r, w, col, alpha, flat=0.5):
    """flattened (iso ground) ring"""
    x0, y0 = int(xy[0] - r - w - 4), int(xy[1] - r * flat - w - 4)
    ww, hh = int(2 * r + 2 * w + 8), int(2 * r * flat + 2 * w + 8)
    Y, X = np.mgrid[0:hh, 0:ww].astype(np.float32)
    dx = (X + x0 + .5 - xy[0])
    dy = (Y + y0 + .5 - xy[1]) / flat
    d = np.sqrt(dx * dx + dy * dy)
    m = cov(w / 2 - np.abs(d - r))
    cv.over(col, m * alpha, (x0, y0))


def home_pin(cv, xy, pips=None, pulse=0.0, pulse_col=None, shake=0, hit=False):
    """Destination pin (big teardrop + house) + 12-pip odds bar."""
    r = 34
    w, h = 260, 240
    cx, tipy = w / 2, h - 22
    for k in range(3):
        if pulse > 0:
            rr = 34 + pulse * (60 + k * 40)
            al = max(0, 1 - pulse * (.85 + k * .1)) * .9
            cv_ring(cv, xy, rr, 5 - k, pulse_col if pulse_col is not None else TIER['HOLDS'], al, flat=.55)
    cv_ring(cv, xy, 34, 4.4, INK, .9, flat=.55)
    cv_ring(cv, xy, 34, 2.4, PAPER, 1, flat=.55)

    def fn(d):
        cyh = g_pin_body(d, cx, tipy, r, PAPER, INK, 2.6)
        d.ell(cx, cyh, r * .84, fill=hexc('0E8F8A') if not hit else TIER['DAMAGED'])
        g_house(d, cx, cyh + 1, r * .52, PAPER)
        if pips:
            n = len(pips)
            pw, gap = 11, 2
            tot = n * pw + (n - 1) * gap + 12
            bx0 = cx - tot / 2
            by = cyh - r - 36
            d.rr(bx0, by, bx0 + tot, by + 26, 7, PAPER, INK, 2.2)
            for i, c in enumerate(pips):
                d.rr(bx0 + 6 + i * (pw + gap), by + 5, bx0 + 6 + i * (pw + gap) + pw, by + 21, 2, c, INK, .8)
    a = spr(w, h, fn, 4)
    cv.sprite(a, xy[0] - w / 2 + shake, xy[1] - (h - 20), shadow=.4, sh_off=(3, 6), sh_blur=4)


def bubble(cv, xy, typ=None, label=None, pips=None, glyph=None, tail='down', dim=1.0, sealed=False, size=1.0):
    """ETA-style bubble: type glyph + order number or letter + tiny tier pips."""
    pw = 15 * (len(pips) if pips else 0) * 0
    npips = len(pips) if pips else 0
    wcore = 44 + (npips * 7 + 6 if npips else 0)
    w, h = int((wcore + 20) * size), int(60 * size)

    def fn(d):
        s = size
        x0, y0, x1, y1 = 8 * s, 6 * s, (8 + wcore) * s, 34 * s
        d.rr(x0 + 1.5, y0 + 2.5, x1 + 1.5, y1 + 2.5, 8 * s, INK, a=.35)
        d.rr(x0, y0, x1, y1, 8 * s, PAPER, INK, 2.2)
        if sealed:   # dashed border = sealed route
            for i in range(0, 18):
                pass
        tx = (x0 + x1) / 2
        d.poly([(tx - 5 * s, y1 - 1), (tx + 5 * s, y1 - 1), (tx, y1 + 8 * s)], PAPER, None)
        d.line([(tx - 5 * s, y1), (tx, y1 + 8 * s), (tx + 5 * s, y1)], 2.2, INK, round_=False)
        d.rr(tx - 5.5 * s, y1 - 2.2, tx + 5.5 * s, y1 + 1.4, 0, PAPER)
        cxg = x0 + 14 * s
        if glyph == 'fork':
            g_fork(d, cxg, 20 * s, 7 * s, hexc('3A2A8A'))
        elif typ:
            g_type(d, typ, cxg, 20 * s, 7.5 * s, TYPE_COL[typ] if typ != 'E' else hexc('F4F7FF'), INK, 1.6)
        if label:
            d.text(x0 + 30 * s, 20.5 * s, label, sfont(17 * s), INK)
        if npips:
            for i, c in enumerate(pips):
                d.rr(x0 + 40 * s + i * 7 * s, 14 * s, x0 + 45 * s + i * 7 * s, 26 * s, 1, c, INK, .8)
    a = spr(w, h, fn, 4)
    if dim < 1:
        a[..., 3] *= dim
    cv.sprite(a, xy[0] - w / 2, xy[1] - 42 * size, shadow=.0)


def barrier(cv, xy, typ, verb='GUARD', flash=0.0, tilt=0.0, dim=1.0, scale=1.35):
    """Defense = road-block barrier planted on the ribbon; the flag shape says which beam type it stops."""
    w, h = 170, 170
    cx, by = w / 2, h - 14
    col = TYPE_COL[typ]
    if typ == 'E':
        col = hexc('E9EEFF')

    def fn(d):
        # base shadow
        d.ell(cx, by, 24, 8, fill=INK, a=.35)
        if verb == 'GUARD':
            # A-frame barricade with striped plank
            d.line([(cx - 20, by), (cx - 14, by - 24)], 4.5, INK)
            d.line([(cx + 20, by), (cx + 14, by - 24)], 4.5, INK)
            d.rr(cx - 26, by - 38, cx + 26, by - 20, 3, PAPER, INK, 2.4)
            for i in range(-3, 4):
                if i % 2 == 0:
                    d.poly([(cx + i * 8 - 1, by - 38), (cx + i * 8 + 7, by - 38), (cx + i * 8 + 3, by - 20), (cx + i * 8 - 5, by - 20)], col)
            d.rr(cx - 26, by - 38, cx + 26, by - 20, 3, None, INK, 2.4)
            # type flag
            d.line([(cx, by - 38), (cx, by - 66)], 2.6, INK)
            d.ell(cx, by - 70, 12, fill=PAPER, out=INK, ow=2.2)
            g_type(d, typ, cx, by - 70, 7.5, col, INK, 1.5)
        elif verb == 'SHIFT':
            d.ell(cx, by - 40, 22, fill=hexc('FFFFFF'), out=INK, ow=2.6)
            g_detour(d, cx, by - 38, 11, hexc('3A2A8A'))
            d.line([(cx, by - 18), (cx, by)], 4.4, INK)
            d.ell(cx + 17, by - 58, 8, fill=PAPER, out=INK, ow=1.8)
            g_type(d, typ, cx + 17, by - 58, 5, col, INK, 1.1)
        else:
            d.poly([(cx - 22, by), (cx, by - 40), (cx + 22, by)], hexc('FFFFFF'), INK, 2.6)
            g_jam(d, cx, by - 14, 8, hexc('3A2A8A'))
        if flash > 0:   # hex shield flash (module 16 vocabulary)
            R = 38 + flash * 44
            pts = [(cx + R * math.cos(math.radians(60 * i + 30)), by - 34 + R * .9 * math.sin(math.radians(60 * i + 30))) for i in range(6)]
            d.poly(pts, None, hexc('B8FFF2'), 5, a=1 - flash * .6)
            d.poly(pts, None, PAPER, 2, a=1 - flash * .6)
    a = spr(w, h, fn, int(4 * scale + .99), out_scale=scale)
    a[..., 3] *= dim
    cv.sprite(a, xy[0] - w * scale / 2, xy[1] - (h - 14) * scale, shadow=.3 * dim)
    if flash > 0:
        cv.add(TIER['UNTOUCHED'], blur(disc_mask(xy[0], xy[1] - 46 * scale, 80 * (.6 + flash * .6)), 16) * .9)


def disc_mask(cx, cy, r):
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    return np.clip(1 - np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / r, 0, 1)


def bits_burst(cv, xy, col, n=46, seed=1, spread=60, size=11):
    """binary-bits / shard burst (module 16)."""
    rng = np.random.RandomState(seed)
    f = sfont(size, 3, 700, 75)
    items = []
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        rad = spread * (rng.rand() ** .6)
        items.append((xy[0] + math.cos(ang) * rad * 1.15, xy[1] + math.sin(ang) * rad * .8 - rng.rand() * 12, rng.choice(['0', '1']), rng.uniform(.5, 1), rng.randint(0, 3)))
    w, h = int(spread * 3), int(spread * 2.6)
    ox, oy = int(xy[0] - w / 2), int(xy[1] - h / 2)
    d = D(w, h, 3)
    for x, y, ch, a, k in items:
        if k == 2:   # shard
            p = [(x - ox, y - oy), (x - ox + rng.uniform(4, 9), y - oy - rng.uniform(1, 4)), (x - ox + rng.uniform(1, 6), y - oy + rng.uniform(4, 9))]
            d.poly(p, col, INK, .9, a=a)
        else:
            d.text(x - ox, y - oy, ch, f, col, a=a, stroke=1.2)
    cv.sprite(d.out(), ox, oy)


def hex_ring(cv, xy, r, col, a=1.0, w=3):
    ww = int(r * 2.4)
    d = D(ww, ww, 3)
    pts = [(ww / 2 + r * math.cos(math.radians(60 * i + 30)), ww / 2 + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    d.poly(pts, None, INK, w + 2.5, a=a)
    d.poly(pts, None, col, w, a=a)
    cv.sprite(d.out(), xy[0] - ww / 2, xy[1] - ww / 2)


# ---------------------------------------------------------------- Bloom (necrosis)
def bloom(cv, centers, seed=3, strength=1.0, front=True, hatch=True):
    """Plum-black body, pink Voronoi veins, hot hairline front, windows dying behind the front.
    centers: [(x,y,r)] screen coords (ground footprint). Drawn on the iso ground plane (y squashed)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    field = np.zeros((H, W), np.float32)
    for (cx, cy, r) in centers:
        d2 = ((xx - cx) / r) ** 2 + ((yy - cy) / (r * .62)) ** 2
        field += np.exp(-d2 * 1.3)
    n1 = noise_field(seed, 28)
    n2 = noise_field(seed + 7, 9)
    field = field + (n1 - .5) * .55 + (n2 - .5) * .16
    thr = 0.5
    m = np.clip((field - thr) * 14, 0, 1)
    if m.max() <= 0:
        return
    # voronoi veins inside the body
    rng = np.random.RandomState(seed)
    ys, xs = np.where(m > .6)
    sel = rng.choice(len(xs), size=min(len(xs), 70), replace=False)
    seeds = np.stack([xs[sel], ys[sel]], 1).astype(np.float32)
    tree = cKDTree(seeds)
    ymin, ymax, xmin, xmax = ys.min() - 10, ys.max() + 10, xs.min() - 10, xs.max() + 10
    gy, gx = np.mgrid[ymin:ymax, xmin:xmax].astype(np.float32)
    dd, _ = tree.query(np.stack([gx.ravel(), (gy.ravel() - 0) * 1.45], 1) * 1.0 if False else np.stack([gx.ravel(), gy.ravel()], 1), k=2)
    edge = (dd[:, 1] - dd[:, 0]).reshape(gx.shape)
    vein = np.zeros((H, W), np.float32)
    vein[ymin:ymax, xmin:xmax] = np.clip(1 - edge / 3.2, 0, 1)
    depth = np.clip((field - thr) * 1.8, 0, 1)      # 0 at the front, 1 deep inside
    body_a = m * (0.80 * strength)
    # soft drop to show the city under the plum at the rim
    rim_soft = np.clip((field - thr + 0.18) * 6, 0, 1) * (1 - m)
    cv.over(PLUM_MID, rim_soft * .35 * strength)
    col = PLUM[None, None, :] * (1 - depth[..., None] * .0) + np.zeros((H, W, 3), np.float32)
    # lighter plum near the front, black-plum deep
    col = PLUM_MID[None, None] * (1 - depth[..., None]) * .6 + PLUM[None, None] * (.4 + depth[..., None] * .6)
    cv.over(col, body_a)
    if hatch:  # closed-area hatch (nav 'restricted region'): faint diagonal stripes
        diag = np.mod((xx + yy) / 9.0, 1.0)
        hm = cov((0.22 - np.abs(diag - .5)) * 9) * m * .16
        cv.over(PLUM_MID * 1.6, hm * strength)
    cv.over(VEIN, vein * m * (0.30 + 0.55 * (1 - depth)) * strength)
    # windows dying behind the front: sparse tiny lights fading with depth
    rng2 = np.random.RandomState(seed + 1)
    nwin = 900
    wx = rng2.randint(0, W, nwin)
    wy = rng2.randint(0, H, nwin)
    keep = (m[wy, wx] > .9) & (rng2.rand(nwin) < (1 - depth[wy, wx]) ** 1.5 * .9)
    for x, y in zip(wx[keep], wy[keep]):
        cv.img[max(0, y - 1):y + 2, max(0, x - 1):x + 2] += np.array([1.0, .35, .65]) * (.35 * (1 - depth[y, x]))
    if front:
        fr = np.clip(1 - np.abs(field - thr) * 28, 0, 1) ** 1.2
        cv.add(VEIN, blur(fr, 5) * .9 * strength)
        cv.over(HOT, cov(1.1 - np.abs(field - thr) * 14) * .95 * strength)
        # sparks riding the front
        rr = np.random.RandomState(seed + 4)
        ys2, xs2 = np.where(fr > .9)
        if len(xs2):
            for i in rr.choice(len(xs2), size=min(60, len(xs2)), replace=False):
                x, y = xs2[i], ys2[i]
                cv.img[max(0, y - 1):y + 2, max(0, x - 1):x + 2] += HOT * .7


# ---------------------------------------------------------------- traffic
def glow_dot(cv, p, r, col, a=1.0):
    x0, y0 = int(p[0] - r * 3 - 2), int(p[1] - r * 3 - 2)
    n = int(r * 6 + 5)
    Y, X = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt((X + x0 + .5 - p[0]) ** 2 + (Y + y0 + .5 - p[1]) ** 2)
    m = np.clip(1 - np.maximum(d - r * .7, 0) / (r * 2.4), 0, 1) ** 2
    cv.add(col, m * a, (x0, y0))


def glow_dot(cv, p, r, col, a=1.0):
    x0, y0 = int(p[0] - r * 3 - 2), int(p[1] - r * 3 - 2)
    n = int(r * 6 + 5)
    Y, X = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt((X + x0 + .5 - p[0]) ** 2 + (Y + y0 + .5 - p[1]) ** 2)
    m = np.clip(1 - np.maximum(d - r * .7, 0) / (r * 2.4), 0, 1) ** 2
    cv.add(col, m * a, (x0, y0))


def traffic(cv, link_pts, seed=2, n=80, only_dim=1.0, skip=None):
    rng = np.random.RandomState(seed)
    lens = np.array([poly_len(p) for p in link_pts])
    tot = lens.sum()
    for _ in range(n):
        li = rng.choice(len(link_pts), p=lens / tot)
        pts = link_pts[li]
        s = rng.uniform(0, lens[li])
        p, ang = point_at(pts, s)
        dirn = 1 if rng.rand() < .5 else -1
        if dirn < 0:
            ang += math.pi
        lane = rng.choice([-4.2, 4.2])
        p = p + np.array([-math.sin(ang), math.cos(ang)]) * lane
        col = np.array([1, .93, .7]) if dirn > 0 else np.array([1, .4, .34])
        if rng.rand() < .22:
            col = hexc('7CF0FF')
        for k in range(1, 8):
            q = p - np.array([math.cos(ang), math.sin(ang)]) * k * 3.2
            glow_dot(cv, q, 2.0, col, (1 - k / 8) * .8 * only_dim)
        glow_dot(cv, p, 3.4, col, only_dim * 1.2)


# ---------------------------------------------------------------- HUD (CRT chips, module 14 vocabulary)
def crt_chip(d, x0, y0, x1, y1, cut=9, border=CYAN_UI, a=.94):
    pts = [(x0 + cut, y0), (x1, y0), (x1, y1 - cut), (x1 - cut, y1), (x0, y1), (x0, y0 + cut)]
    d.poly(pts, NAVY, border, 2.2, a=a)
    for yy in range(int(y0) + 4, int(y1) - 2, 4):
        d.line([(x0 + 4, yy), (x1 - 4, yy)], .7, CYAN_UI, a=.07, round_=False)


def hud(cv, home=44, home_max=50, home_delta=None, heat=80, heat_to=None, infected=3, healthy=8, lost_at=9, flash_inf=False,
        shake=0, home_col=None):
    # HOME chip
    w, h = 270, 78
    def fn(d):
        crt_chip(d, 4, 4, w - 4, h - 4)
        g_house(d, 36, 34, 15, hexc('E8FFFB'), NAVY, 1.4)
        d.text(94, 33, str(home), sfont(44), PAPER if home_col is None else home_col, stroke=0)
        d.text(140, 40, '/%d' % home_max, sfont(20), hexc('8FB6D0'))
        if home_delta:
            d.text(212, 33, home_delta, sfont(32), TIER['DAMAGED'])
        for i in range(10):
            on = i < round(10 * home / home_max)
            d.rr(18 + i * 23, 56, 18 + i * 23 + 19, 66, 2, hexc('19C9B4') if on else hexc('1B2B4A'))
    cv.sprite(spr(w, h, fn), 24 + shake, 18, shadow=.35)
    # HEAT chip
    w2 = 330
    def fn2(d):
        crt_chip(d, 4, 4, w2 - 4, h - 4, border=hexc('FF7A3A'))
        g_flame(d, 36, 35, 16, TIER['DAMAGED'], NAVY)
        d.text(98, 33, str(heat), sfont(44), PAPER)
        if heat_to:
            d.text(150, 36, '→', sfont(28), hexc('FFC27A'))
            d.text(192, 33, str(heat_to), sfont(36), hexc('FFC27A'))
        # gradient bar w/ thresholds 25/50/75
        x0, x1 = 18, w2 - 20
        d.rr(x0, 56, x1, 66, 2, hexc('1B2B4A'))
        fill = x0 + (x1 - x0) * heat / 100
        for i in range(int(x0), int(fill)):
            t = (i - x0) / (x1 - x0)
            c = hexc('FFD24A') * (1 - t) + hexc('FF3347') * t
            d.line([(i, 56), (i, 66)], 1.2, c, round_=False)
        for t in (.25, .5, .75):
            d.line([(x0 + (x1 - x0) * t, 52), (x0 + (x1 - x0) * t, 70)], 1.5, PAPER, a=.8, round_=False)
    cv.sprite(spr(w2, h, fn2), 24 + 270 + 16, 18, shadow=.35)
    # deck strip: healthy tiles (cyan) then INFECTED (plum x), lost line
    w3 = 640
    def fn3(d):
        crt_chip(d, 4, 4, w3 - 4, h - 4, border=hexc('B58CFF'))
        g_x(d, 34, 30, 9, GREASE_R)
        d.text(78, 33, str(infected), sfont(44), hexc('FF8AD8') if not flash_inf else PAPER)
        g_shield(d, 138, 32, 11, hexc('19C9B4'))
        d.text(188, 33, str(healthy), sfont(44), PAPER)
        # tile row: healthy cyan tiles from left, infected plum tiles from right
        tx0 = 232
        total = lost_at + 2
        for i in range(healthy):
            d.rr(tx0 + i * 21, 20, tx0 + i * 21 + 17, 52, 3, hexc('2FD6E6'), INK, 1.4)
        for i in range(infected):
            d.rr(tx0 + (healthy + i) * 21 + 4, 20, tx0 + (healthy + i) * 21 + 21, 52, 3, PLUM_MID, VEIN, 1.4)
            d.line([(tx0 + (healthy + i) * 21 + 8, 28), (tx0 + (healthy + i) * 21 + 17, 44)], 2.2, GREASE_R, round_=False)
        # lost line marker: tick over the Nth tile
        lx = tx0 + lost_at * 21 + 2
        d.line([(lx, 12), (lx, 60)], 2.4, TIER['BREACHED'])
        g_skull(d, lx, 11, 6, PAPER)
    cv.sprite(spr(w3, h, fn3), 24 + 270 + 16 + 330 + 16, 18, shadow=.35)


# ---------------------------------------------------------------- vinyl sticker cards (module 13)
CARD_W, CARD_H = 112, 150


def sticker(kind, typ, state='held', rot=0.0, infected=False, cost=0):
    w, h = CARD_W + 24, CARD_H + 24

    def fn(d):
        x0, y0, x1, y1 = 12, 12, 12 + CARD_W, 12 + CARD_H
        if state == 'spent':
            d.rr(x0, y0, x1, y1, 14, None, hexc('FFFFFF'), 2.4, a=.55)
            for i in range(0, CARD_W, 10):
                pass
            return
        d.rr(x0 + 2, y0 + 4, x1 + 2, y1 + 4, 14, INK, a=.35)
        d.rr(x0, y0, x1, y1, 14, PAPER, INK, 2.6)           # die-cut white vinyl rim
        inner = PLUM if infected else NAVY
        d.rr(x0 + 7, y0 + 7, x1 - 7, y1 - 7, 9, inner, INK, 1.4)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 8
        if infected:
            g_x(d, cx, cy, 24, GREASE_R)
        elif kind == 'GUARD':
            g_shield(d, cx, cy, 28, hexc('F1F3FF'))
        elif kind == 'SHIFT':
            g_detour(d, cx, cy + 4, 30, hexc('F1F3FF'))
        elif kind == 'JAM':
            g_jam(d, cx, cy, 30, hexc('F1F3FF'))
        elif kind == 'GHOST':
            g_shield(d, cx, cy, 28, TIER['UNTOUCHED'], INK, 1.6)
            d.ell(cx, cy - 2, 9, fill=INK, a=.8)
        if typ and not infected:
            g_type(d, typ, x0 + 21, y1 - 22, 9, TYPE_COL[typ] if typ != 'E' else E_CHALK, INK, 1.5)
        if not infected:
            g_flame(d, x1 - 32, y1 - 22, 7, hexc('FF8A3A'), INK, 1.0)
            d.text(x1 - 19, y1 - 21, str(cost), sfont(15), PAPER)
        # peel curl
        d.poly([(x1 - 22, y0), (x1, y0), (x1, y0 + 22)], hexc('FFFFFF'), INK, 1.3, a=.9)
    a = spr(w, h, fn, 3)
    if rot:
        im = Image.fromarray((a * 255).astype(np.uint8)).rotate(rot, Image.BICUBIC, expand=False)
        a = np.asarray(im, np.float32) / 255
    return a


def hand(cv, cards, y=1075 - 176, x0=None, spacing=124, lift=None, motion=None):
    """cards: [(kind,typ,state,infected)]; lift: index->px raise"""
    n = len(cards)
    x0 = (W - n * spacing) / 2 + 150 if x0 is None else x0
    for i, (kind, typ, state, inf) in enumerate(cards):
        rot = (i - (n - 1) / 2) * 1.6
        s = sticker(kind, typ, state, rot=rot, infected=inf)
        yy = y + abs(i - (n - 1) / 2) * 4
        if lift and i in lift:
            yy -= lift[i]
        cv.sprite(s, x0 + i * spacing, yy, shadow=.0)


def nav_button(cv, xy, r=44, ready=True, glyph='chev'):
    """Start-navigation button (Maps 'Start'): big round, triple chevron."""
    w = int(2 * r + 30)

    def fn(d):
        c = w / 2
        d.ell(c + 2, c + 5, r, fill=INK, a=.35)
        d.ell(c, c, r, fill=hexc('0E8F8A') if ready else SLATE, out=INK, ow=3)
        d.ell(c, c, r - 6, out=PAPER, ow=2.4)
        if glyph == 'chev':
            for k in (-1, 0, 1):
                g_chev(d, c + k * 13, c, 17, PAPER, 6)
        elif glyph == 'eye':
            d.ell(c, c, r * .55, r * .32, fill=PAPER, out=INK, ow=1.6)
            d.ell(c, c, r * .2, fill=hexc('0E8F8A'))
    cv.sprite(spr(w, w, fn), xy[0] - w / 2, xy[1] - w / 2)


def lens(cv, src, dest, rsrc=62, rdest=150, zoom=None):
    """Junction-view lens (Maps/Waze junction callout): magnifies the impact into a free corner."""
    zoom = rdest / rsrc if zoom is None else zoom
    x0, y0 = int(src[0] - rsrc), int(src[1] - rsrc)
    x1, y1 = int(src[0] + rsrc), int(src[1] + rsrc)
    pad = np.pad(np.clip(cv.img, 0, 1), ((rsrc, rsrc), (rsrc, rsrc), (0, 0)), mode='edge')
    crop = pad[y0 + rsrc:y1 + rsrc, x0 + rsrc:x1 + rsrc]
    im = Image.fromarray((crop * 255).astype(np.uint8)).resize((rdest * 2, rdest * 2), Image.BICUBIC).filter(ImageFilter.UnsharpMask(2.0, 80, 2))
    big = np.asarray(im, np.float32) / 255
    Y, X = np.mgrid[0:rdest * 2, 0:rdest * 2].astype(np.float32)
    dd = np.sqrt((X - rdest + .5) ** 2 + (Y - rdest + .5) ** 2)
    m = cov(rdest - dd)
    ox, oy = int(dest[0] - rdest), int(dest[1] - rdest)
    # leader line from lens edge to the spot
    v = np.array(src) - np.array(dest)
    L = np.hypot(*v)
    u = v / L
    p0 = np.array(dest) + u * (rdest + 4)
    p1 = np.array(src) - u * 4
    seg = np.array([p0, p1])
    box = bbox_of(seg, 8)
    dline, _, _ = sdf(seg, box)
    cv.over(INK, cov(4.5 - dline) * .9, (box[0], box[1]))
    cv.over(PAPER, cov(2.4 - dline), (box[0], box[1]))
    cv.over(INK, cov(rdest + 9 - dd) * .35, (ox + 4, oy + 8))
    cv.over(INK, cov(rdest + 7 - dd), (ox, oy))
    cv.over(PAPER, cov(rdest + 3 - dd), (ox, oy))
    cv.over(big, m, (ox, oy))
    cv.over(INK, cov(1.5 - np.abs(dd - rdest + 1)) * .8, (ox, oy))
    # ring on the spot itself
    cv_ring(cv, src, rsrc * .9, 3, PAPER, .95, flat=1.0)


def lens_scene(cv, src, dest, painter, rdest=160, blur_bg=3.0, zoom=2.0):
    """Junction-view callout drawn natively (crisp): soft magnified city behind, hero marks painted big by `painter(tmp, cx, cy)`."""
    ox, oy = int(dest[0] - rdest), int(dest[1] - rdest)
    rs = int(rdest / zoom)
    pad = np.pad(np.clip(cv.img, 0, 1), ((rs, rs), (rs, rs), (0, 0)), mode='edge')
    x0, y0 = int(src[0]), int(src[1])
    crop = pad[y0:y0 + 2 * rs, x0:x0 + 2 * rs]
    im = Image.fromarray((crop * 255).astype(np.uint8)).resize((rdest * 2, rdest * 2), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur_bg))
    bg = np.asarray(im, np.float32) / 255 * .85
    # tmp canvas same size as screen so primitives work in screen coords; paint around dest
    tmp = Canvas(np.zeros((H, W, 3), np.float32))
    tmp.img[oy:oy + 2 * rdest, ox:ox + 2 * rdest] = bg[:min(2 * rdest, H - oy), :min(2 * rdest, W - ox)] if oy >= 0 and ox >= 0 else bg
    painter(tmp, dest[0], dest[1])
    Y, X = np.mgrid[0:rdest * 2, 0:rdest * 2].astype(np.float32)
    dd = np.sqrt((X - rdest + .5) ** 2 + (Y - rdest + .5) ** 2)
    m = cov(rdest - dd)
    v = np.array(src, float) - np.array(dest, float)
    L = np.hypot(*v)
    u = v / L
    seg = np.array([np.array(dest) + u * (rdest + 4), np.array(src) - u * 6])
    box = bbox_of(seg, 8)
    dline, _, _ = sdf(seg, box)
    cv.over(INK, cov(4.5 - dline) * .9, (box[0], box[1]))
    cv.over(PAPER, cov(2.4 - dline), (box[0], box[1]))
    cv.over(INK, cov(rdest + 9 - dd) * .35, (ox + 4, oy + 8))
    cv.over(INK, cov(rdest + 7 - dd), (ox, oy))
    cv.over(PAPER, cov(rdest + 3 - dd), (ox, oy))
    cv.over(tmp.img[oy:oy + 2 * rdest, ox:ox + 2 * rdest], m, (ox, oy))
    cv_ring(cv, src, 34, 3, PAPER, .95, flat=1.0)
    cv_ring(cv, src, 34, 7, INK, .35, flat=1.0)
