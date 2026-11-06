"""E Jack-in: the world layer. Data shadows, lattice floor, conduits, ICE towers on Sites, the Solace
ICE cage, our HOME deck, infection (Bloom A necrosis). Everything is drawn over the real plate."""
import math
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from lib import *

K = 0.643  # iso ground squash (matches the shipped hex/diamond ratio)
BASE_OFF = 57.5  # raw px from the Site icon anchor (xy) down to the node on the street


def site_base(s):
    return T(s['xy'], BASE_OFF)


# ------------------------------------------------------------------ ambient: data shadows + lattice floor
def rooftop_points(base, n=210, seed=11, cell=44):
    """bright lit-roof pixels of the plate -> where ghost data volumes grow."""
    mx = base.max(2)
    sat = mx - base.min(2)
    score = (mx > .38) * (sat > .16) * mx
    pts = []
    for y in range(0, H - cell, cell):
        for x in range(0, W - cell, cell):
            blk = score[y:y + cell, x:x + cell]
            i = np.argmax(blk)
            if blk.flat[i] > .3:
                pts.append((x + i % cell, y + i // cell, float(blk.flat[i])))
    rng = np.random.RandomState(seed)
    rng.shuffle(pts)
    return pts[:n]


def datashadows(cv, base, near=None, seed=11, boost=1.0):
    pts = rooftop_points(base, seed=seed)
    rng = np.random.RandomState(seed + 1)
    ly = Lyr()
    fl = Lyr()
    for x, y, sc in pts:
        if y < 70 or y > H - 40:
            continue
        a = rng.uniform(7, 14)
        h = rng.uniform(14, 62)
        c = (x, y)
        b = a * K
        L0, F0, R0 = (c[0] - a, c[1]), (c[0], c[1] + b), (c[0] + a, c[1])
        L1, F1, R1, K1 = (L0[0], L0[1] - h), (F0[0], F0[1] - h), (R0[0], R0[1] - h), (c[0], c[1] - b - h)
        ly.line([L0, L1], 1, 190)
        ly.line([F0, F1], 1, 190)
        ly.line([R0, R1], 1, 190)
        ly.line([L1, K1, R1, F1, L1], 1, 220)
        fl.poly([L1, K1, R1, F1], 255)
        if rng.rand() < .3:   # a few carry a data spike
            ly.line([(c[0], c[1] - b - h), (c[0], c[1] - b - h - rng.uniform(16, 44))], 1, 160, dash=(2, 3))
    cv.add(LATT_D, ly.m, .34 * boost)
    cv.add(LATT_D, blur(ly.m, 3), .35 * boost)
    cv.add(LATT, fl.m, .035 * boost)


def lattice_floor(cv, focus=(900, 560), rad=900, step=57, alpha=.16):
    """Gibson's lattice: an iso ground grid under everything, faint, brightest around the corridor."""
    ly = Lyr()
    L = 3400
    for i in range(-40, 60):
        o = i * step
        ly.line([(-200, o - 200 * 0 + 0), (-200 + L, o + L * K)], 1, 255)
        ly.line([(-200, o + 900), (-200 + L, o + 900 - L * K)], 1, 255)
    m = ly.m
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - focus[0]) / rad) ** 2 + ((yy - focus[1]) / (rad * .6)) ** 2)
    f = np.clip(1.15 - d, 0, 1) ** 1.3
    cv.add(LATT_D, m * f, alpha)


# ------------------------------------------------------------------ conduits (the real streets of the net)
def rails(cv, links, active=None, alpha=.55):
    """thin cyan conduits on the real street polylines + hollow diamond junction nodes."""
    ly = Lyr()
    nd = Lyr()
    seen = set()
    for l in links:
        if not l['polyline']:
            continue
        pts = [tuple(T(p)) for p in l['polyline']]
        # drop the vertical stub ends
        ly.line(pts, 2, 255)
        for p in (pts[0], pts[-1]):
            k = (round(p[0] / 4), round(p[1] / 4))
            if k not in seen:
                seen.add(k)
                nd.poly(iso_diamond(p, 7), 255, outline=255, ow=1)
    cv.over(INK, blur(ly.m, 2.5) * 0.0 + ly.m, .55)
    cv.neon(ly.m, LATT_D, core=alpha * .8, g1=(3, .5), g2=(10, .35))
    cv.neon(nd.m, LATT, core=.55, g1=(3, .4), g2=None)


# ------------------------------------------------------------------ ICE towers on Sites
def _box_edges(B, a, h, k=K):
    b = a * k
    L0, F0, R0, K0 = (B[0] - a, B[1]), (B[0], B[1] + b), (B[0] + a, B[1]), (B[0], B[1] - b)
    L1, F1, R1, K1 = (L0[0], L0[1] - h), (F0[0], F0[1] - h), (R0[0], R0[1] - h), (K0[0], K0[1] - h)
    return L0, F0, R0, K0, L1, F1, R1, K1


def tower(cv, B, tier=1, state='healthy', tint=None, alpha=.84, seed=0, glitch=0.0):
    """Translucent ICE data volume rising from the Site. state: healthy | DOWN | TAKEN.
    T1 box, T2 obelisk (exploit), T3 stepped spire with a halo ring."""
    rng = np.random.RandomState(seed + 7)
    a = {1: 25, 2: 23, 3: 25}.get(tier, 25)
    h = {1: 66, 2: 84, 3: 78}.get(tier, 66)
    col = LATT if tint is None else tint
    colD = LATT_D if tint is None else tint * .75
    dead = state in ('TAKEN', 'INFECTED')
    down = state == 'DOWN'
    if dead:
        col = VEIN * .8 + HOT * .2
        colD = PLUM_MID * 1.9
    if down:
        col = LATT * .55 + np.array([.2, .1, .15], np.float32)
        colD = LATT_D * .45
    cut = 1.0
    if down:
        cut = .55  # the upper half has dropped off the grid
    hh = h * cut
    L0, F0, R0, K0, L1, F1, R1, K1 = _box_edges(B, a, hh)
    bx = (B[0] - 75, B[1] - h - 190, B[0] + 75, B[1] + 30)
    faceL, faceR, top, edge, lat, hid = Lyr(bx), Lyr(bx), Lyr(bx), Lyr(bx), Lyr(bx), Lyr(bx)
    OF = faceL.off
    faceL.poly([L0, F0, F1, L1], 255)
    faceR.poly([F0, R0, R1, F1], 255)
    top.poly([K1, R1, F1, L1], 255)
    edge.line([L0, L1], 2, 255)
    edge.line([F0, F1], 2, 255)
    edge.line([R0, R1], 2, 255)
    edge.line([L1, K1, R1, F1, L1], 2, 255)
    edge.line([L0, F0, R0], 2, 255)
    hid.line([K0, K1], 1, 255, dash=(3, 3))
    hid.line([L0, K0, R0], 1, 255, dash=(3, 3))
    # lattice rungs on both visible faces (bands) + diagonals
    n = max(3, int(hh / 11))
    for i in range(1, n):
        t = i / n
        lat.line([(L0[0], L0[1] - hh * t), (F0[0], F0[1] - hh * t)], 1, 200)
        lat.line([(F0[0], F0[1] - hh * t), (R0[0], R0[1] - hh * t)], 1, 200)
    lat.line([L0, F1], 1, 150)
    lat.line([F0, L1], 1, 150)
    lat.line([F0, R1], 1, 150)
    lat.line([R0, F1], 1, 150)
    apex = None
    if tier == 2 and not down:
        apex = (B[0], K1[1] - a * 1.15)
        edge.line([L1, apex], 2, 255)
        edge.line([R1, apex], 2, 255)
        edge.line([F1, apex], 2, 255)
        hid.line([K1, apex], 1, 255, dash=(3, 3))
        faceL.poly([L1, F1, apex], 255)
        faceR.poly([F1, R1, apex], 255)
    if tier == 3 and not down:
        # upper step + spire
        a2 = a * .6
        U = (B[0], B[1] - hh)
        l0, f0, r0, k0, l1, f1, r1, k1 = _box_edges(U, a2, h * .5)
        faceL.poly([l0, f0, f1, l1], 255)
        faceR.poly([f0, r0, r1, f1], 255)
        top.poly([k1, r1, f1, l1], 255)
        edge.line([l0, l1], 2, 255)
        edge.line([f0, f1], 2, 255)
        edge.line([r0, r1], 2, 255)
        edge.line([l1, k1, r1, f1, l1], 2, 255)
        edge.line([(B[0], k1[1] + a2 * K), (B[0], k1[1] - 22)], 2, 255)
        apex = (B[0], k1[1] - 22)
        for i in range(1, 5):
            t = i / 5
            lat.line([(l0[0], l0[1] - h * .5 * t), (f0[0], f0[1] - h * .5 * t)], 1, 200)
            lat.line([(f0[0], f0[1] - h * .5 * t), (r0[0], r0[1] - h * .5 * t)], 1, 200)
        # halo ring orbiting the crown
        ring = ring_pts((B[0], k1[1] - 6), a * 1.25, 60)
        edge.line(ring, 2, 255)
    if down:
        # dropped fragment: offset slices + static (the upper volume tore away)
        for i in range(5):
            y = B[1] - hh - 8 - i * 9
            ox = rng.uniform(-9, 9)
            hid.line([(L0[0] + ox, y), (F0[0] + ox, y + a * K), (R0[0] + ox, y)], 1, 255, dash=(4, 3))
    if dead:
        # necrotic stump: plum glass, dark windows, veins climbing the faces
        for i in range(7):
            x0 = rng.uniform(B[0] - a, B[0] + a)
            y0 = B[1] + rng.uniform(-6, 6)
            lat.line([(x0, y0), (x0 + rng.uniform(-9, 9), y0 - rng.uniform(10, hh * .8))], 1, 255)
    # draw: dark glass then light
    bodyM = np.maximum(np.maximum(faceL.m, faceR.m), top.m)
    cv.over(INK, bodyM, .62 * alpha, OF)
    cv.add(colD, faceL.m, .10 * alpha, OF)
    cv.add(col, faceR.m, .20 * alpha, OF)
    cv.add(col, top.m, .36 * alpha, OF)
    cv.neon(lat.m * (1 if not dead else .8), colD, core=.5 * alpha, g1=None, g2=None, off=OF)
    cv.neon(hid.m, colD, core=.35 * alpha, g1=None, g2=None, off=OF)
    cv.neon(edge.m, col, core=1.0 * alpha, g1=(3, .7 * alpha), g2=(11, .5 * alpha), white=.35 * alpha, off=OF)
    # data stream rising from the crown (volume of data, not a flat marker)
    crown = (B[0], B[1] - hh - (a * 1.15 if tier == 2 and not down else 0) - (h * .5 + 22 if tier == 3 and not down else 0))
    if not dead:
        st = Lyr(bx)
        for i in range(10):
            yy = crown[1] - 6 - i * 7 - rng.uniform(0, 4)
            st.line([(crown[0] + rng.uniform(-3, 3), yy), (crown[0] + rng.uniform(-3, 3), yy - rng.uniform(2, 5))], 1, int(255 * (1 - i / 11)))
        cv.neon(st.m, col, core=.8 * alpha * (.5 if down else 1), g1=(2, .5), g2=None, off=OF)
    return crown


def site_pad(cv, B, col=None, alpha=1.0, r=34):
    col = LATT if col is None else col
    ly = Lyr()
    ly.poly(iso_diamond(B, r), 255, outline=255, ow=1)
    ly.line(iso_diamond(B, r * .62) + [iso_diamond(B, r * .62)[0]], 1, 255)
    cv.over(INK, (lambda m: m)(Lyr().m + 0), 0)
    cv.neon(ly.m, col, core=.5 * alpha, g1=(3, .4), g2=None)


# ------------------------------------------------------------------ Solace HQ ICE cage
def solace_cage(cv, hq_base, alpha=1.0, phase=0.0, hot=False):
    """the corp HQ (the Solace helix) caged in a tall ICE lattice: rings + rails + a scanning band."""
    col = LATT if not hot else HOT
    c = np.array([hq_base[0] + 140, hq_base[1] - 170])   # helix foot on screen
    ly = Lyr()
    rails_ = Lyr()
    Hh = 330
    for i in range(0, 9):
        t = i / 8
        r = 112 - 20 * math.sin(t * math.pi) * 0 - 12 * t
        ly.line(ring_pts((c[0], c[1] - t * Hh), r, 72), 2, 255)
    for ang in range(0, 360, 45):
        p0 = (c[0] + 112 * math.cos(math.radians(ang)), c[1] + 112 * K * math.sin(math.radians(ang)))
        p1 = (c[0] + 100 * math.cos(math.radians(ang)), c[1] - Hh + 100 * K * math.sin(math.radians(ang)))
        if math.sin(math.radians(ang)) >= -0.2:   # front rails only; back rails faint
            rails_.line([p0, p1], 2, 255)
    back = Lyr()
    for ang in range(180, 360, 45):
        p0 = (c[0] + 112 * math.cos(math.radians(ang)), c[1] + 112 * K * math.sin(math.radians(ang)))
        p1 = (c[0] + 100 * math.cos(math.radians(ang)), c[1] - Hh + 100 * K * math.sin(math.radians(ang)))
        back.line([p0, p1], 1, 255, dash=(3, 3))
    # scanning band
    sy = c[1] - ((phase % 1.0) * Hh)
    sc = Lyr()
    sc.line(ring_pts((c[0], sy), 118, 80), 4, 255)
    cv.over(INK, ring_fill((c, 112, Hh)), .25 * alpha)
    cv.neon(ly.m, col, core=.55 * alpha, g1=(3, .5 * alpha), g2=(12, .35 * alpha))
    cv.neon(rails_.m, col, core=.55 * alpha, g1=(3, .4 * alpha), g2=None)
    cv.neon(back.m, LATT_D, core=.4 * alpha, g1=None, g2=None)
    cv.neon(sc.m, WHITE * .6 + LATT * .4, core=.8 * alpha, g1=(5, .9), g2=(18, .6))
    return c


def ring_fill(args):
    c, r, Hh = args
    ly = Lyr()
    ly.poly([(c[0] - r, c[1]), (c[0] - r, c[1] - Hh), (c[0] + r, c[1] - Hh), (c[0] + r, c[1])], 255)
    ly.ell((c[0], c[1]), r, r * K)
    ly.ell((c[0], c[1] - Hh), r, r * K)
    return ly.m * .5


# ------------------------------------------------------------------ HOME: our hand-built deck
def home_deck(cv, B, hp=44, hp_max=50, preview=0, hit=0, tint=None, alpha=1.0, flash=0.0, scar=0):
    """our HQ is a rebel cyberdeck: a chunky slab with a key-bed, jacked into the grid, ringed by a 50-tick
    integrity gauge on the street. preview = ticks about to be lost (ghosted orange), hit = ticks just lost."""
    col = WHITE * .85 + LATT * .15 if tint is None else tint
    # gauge ring on the ground
    R = 74
    ticks = Lyr(); lost = Lyr(); prev = Lyr(); dead = Lyr(); scr_ = Lyr()
    for i in range(hp_max):
        ang = -90 + i * 360 / hp_max
        a0 = math.radians(ang)
        p0 = (B[0] + (R - 7) * math.cos(a0), B[1] + (R - 7) * K * math.sin(a0))
        p1 = (B[0] + (R + 5) * math.cos(a0), B[1] + (R + 5) * K * math.sin(a0))
        remain = hp - preview - hit
        if i < remain:
            ticks.line([p0, p1], 3, 255)
        elif i < hp - hit:
            prev.line([p0, p1], 3, 255)
        elif i < hp:
            lost.line([p0, p1], 3, 255)
        elif i < hp + scar:
            scr_.line([p0, p1], 3, 255)
        else:
            dead.line([p0, p1], 1, 200)
    cv.over(INK, ring_fill_ground(B, R + 10), .35 * alpha)
    cv.neon(ticks.m, col, core=.95 * alpha, g1=(3, .6), g2=(10, .35))
    cv.neon(prev.m, TIER['DAMAGED'], core=.95 * alpha, g1=(3, .8), g2=(10, .5))
    cv.neon(lost.m, TIER['DAMAGED'], core=1.0, g1=(4, 1.0), g2=(14, .7), white=.5)
    cv.neon(dead.m, LATT_D, core=.35 * alpha, g1=None, g2=None)
    cv.neon(scr_.m, TIER['DAMAGED'] * .8, core=.55, g1=(2, .3), g2=None)
    # slab (the deck): iso box a=30, h=16, key-bed top, hinged screen up behind
    a = 31
    b = a * K
    h = 15
    L0, F0, R0, K0, L1, F1, R1, K1 = _box_edges(B, a, h)
    body = Lyr(); keys = Lyr(); scr = Lyr(); edge = Lyr()
    body.poly([L1, K1, R1, F1], 255)
    body.poly([L0, F0, F1, L1], 255)
    body.poly([F0, R0, R1, F1], 255)
    for i in range(1, 5):   # keys
        t = i / 5
        keys.line([(L1[0] + (F1[0] - L1[0]) * t, L1[1] + (F1[1] - L1[1]) * t),
                   (K1[0] + (R1[0] - K1[0]) * t, K1[1] + (R1[1] - K1[1]) * t)], 1, 255, dash=(3, 2))
    # screen: tilted panel standing on the back edge
    S0, S1 = (L1[0] + 4, L1[1] - 1), (K1[0], K1[1] - 1)
    sh = 36
    scr.poly([(L1[0] + 2, L1[1] - 2), (K1[0], K1[1] - 2), (K1[0], K1[1] - 2 - sh), (L1[0] + 2, L1[1] - 2 - sh)], 255)
    scr.poly([(K1[0], K1[1] - 2), (R1[0] - 2, R1[1] - 2), (R1[0] - 2, R1[1] - 2 - sh), (K1[0], K1[1] - 2 - sh)], 255)
    edge.line([L0, F0, R0, R1, K1, L1, L0], 2, 255)
    edge.line([F0, F1], 2, 255)
    edge.line([L1, F1, R1], 2, 255)
    edge.line([(L1[0] + 2, L1[1] - 2), (L1[0] + 2, L1[1] - 2 - sh), (K1[0], K1[1] - 2 - sh), (R1[0] - 2, R1[1] - 2 - sh), (R1[0] - 2, R1[1] - 2)], 2, 255)
    cv.over(INK, body.m, .85 * alpha)
    cv.over(INK, scr.m, .55 * alpha)
    cv.add(col, scr.m, .22 * alpha + flash * .6)
    cv.neon(keys.m, col, core=.5 * alpha, g1=None, g2=None)
    cv.neon(edge.m, col, core=1.0 * alpha, g1=(3, .7 * alpha), g2=(10, .45 * alpha), white=.4)
    # jack cable running down into the street
    cab = Lyr()
    cab.line([(B[0] + 20, B[1] + 6), (B[0] + 40, B[1] + 30), (B[0] + 70, B[1] + 34)], 2, 255)
    cv.neon(cab.m, col, core=.6 * alpha, g1=(2, .4), g2=None)
    return (B[0], B[1] - 70)


def ring_fill_ground(B, r):
    ly = Lyr()
    ly.ell(B, r, r * K)
    return ly.m


# ------------------------------------------------------------------ infection: Bloom A necrosis
def _voronoi_veins(seed, scale=26, shape=(H, W)):
    from scipy.spatial import cKDTree
    rng = np.random.RandomState(seed)
    ny, nx = int(shape[0] / scale) + 2, int(shape[1] / scale) + 2
    pts = np.stack(np.meshgrid(np.arange(nx), np.arange(ny)), -1).reshape(-1, 2).astype(np.float32)
    pts = (pts + rng.rand(len(pts), 2) * .9) * scale
    sh = (shape[0] // 2, shape[1] // 2)
    yy, xx = np.mgrid[0:sh[0], 0:sh[1]].astype(np.float32) * 2
    d, _ = cKDTree(pts).query(np.stack([xx.ravel(), yy.ravel()], 1), k=2)
    v = np.clip(1 - (d[:, 1] - d[:, 0]).reshape(sh) / 2.3, 0, 1)
    return np.asarray(Image.fromarray((v * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BILINEAR), np.float32) / 255


_VEIN_CACHE = {}


def noise(seed, sc, shape=(H, W)):
    rng = np.random.RandomState(seed)
    small = rng.rand(int(shape[0] / sc) + 3, int(shape[1] / sc) + 3).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((int(shape[1] + 3 * sc), int(shape[0] + 3 * sc)), Image.BICUBIC)
    return np.asarray(im, np.float32)[:shape[0], :shape[1]] / 255


def bloom(cv, centers, radii, seed=5, grow=1.0, floor_all=False):
    """Bloom A necrosis: plum-black body, pink Voronoi veins, a hot hairline front, windows dying behind it.
    centers: screen px list; radii: px list (ellipse squashed by the iso ratio)."""
    if not centers:
        return np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = np.full((H, W), 9.0, np.float32)
    for c, r in zip(centers, radii):
        d = np.sqrt(((xx - c[0]) / r) ** 2 + ((yy - c[1]) / (r * K * 1.15)) ** 2)
        f = np.minimum(f, d)
    n = noise(seed, 38) * .55 + noise(seed + 1, 15) * .3 + noise(seed + 2, 6) * .15
    f = f + (n - .5) * .42
    inside = np.clip((1.0 - f) * 14, 0, 1)             # 1 inside the front
    depth = np.clip((1.0 - f) * 2.2, 0, 1)             # 0 at the front -> 1 deep inside
    front = np.clip(1 - np.abs(f - 1.0) * 80, 0, 1)    # hairline
    key = (seed,)
    if key not in _VEIN_CACHE:
        _VEIN_CACHE[key] = _voronoi_veins(seed + 40, scale=19)
    veins = _VEIN_CACHE[key]
    # body: plum-black; windows die behind the front (deeper = darker), a few survive near the front
    img = cv.img
    keep = (np.clip(1 - depth * 2.4, 0, 1) ** 1.6 * .6)[..., None]
    body = PLUM * .42 + img * keep
    a = (inside * .97)[..., None]
    cv.img = img * (1 - a) + (body + np.array([.05, .0, .045], np.float32) * depth[..., None]) * a
    vv = veins * inside * np.clip(1.0 - depth * .55, .25, 1)
    cv.add(VEIN, vv, .55)
    cv.add(VEIN, blur(vv, 5), .22)
    cv.add(HOT, front, .85)
    cv.add(VEIN, blur(front, 2.5), .5)
    cv.add(VEIN, blur(front, 8), .2)
    return inside
