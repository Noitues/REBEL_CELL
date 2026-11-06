"""P2 mark kit (STYLE_CONTRACT sec. 5): tier ring, stop block, ranked ICE towers, mint cage, HOME ring + tick gauge, head sprites,
ground occlusion ('grounded'), hatch / pulse preview channel. Imports lib only; hy / scene call into it.

World units: 1 BU = 4.866 px horizontally (0.2055 BU per px); the ground squash is K = 0.643, so a world circle is an iso ellipse
(rx = r * BU, ry = rx * K)."""
import math, os
import numpy as np
from PIL import Image
from lib import *

BU = 1.0 / 0.2055
KK = 0.643
MINT = hexc('55E0A0')
WARM = hexc('F6F1E4')
OCHRE = hexc('C98410')
INK2 = hexc('0A0A18')
P2BASE = 'D:/rc_scratch/tide_concepts/p2_base/'
TIER_R_BU = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES_LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}
BAND = 2.8 * BU          # 13.6 px
UNDER = 1.3 * BU         # 6.3 px each side
RIM = 0.45 * BU          # 2.2 px

_OCC = [None]


def occ():
    """occluder mask (class 2, height above ground > 1.5 BU), 0..1, softened 0.8 px."""
    if _OCC[0] is None:
        a = np.asarray(Image.open(P2BASE + 'layers/occluder_mask.png').convert('L'), np.float32) / 255
        _OCC[0] = blur(a, .8)
    return _OCC[0]


def grounded(cv, fn, box, ghost=.55):
    """run fn() (draws on cv), then scale what it added by the occlusion: ground marks are hidden where the city occludes them,
    leaving `ghost` of the mark (x-ray) so a Site is never lost. ghost=1 disables."""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, W), min(y1, H)
    if x1 <= x0 or y1 <= y0:
        return
    before = cv.img[y0:y1, x0:x1].copy()
    fn()
    after = cv.img[y0:y1, x0:x1]
    f = 1 - occ()[y0:y1, x0:x1] * (1 - ghost)
    cv.img[y0:y1, x0:x1] = before + (after - before) * f[..., None]


def stripes(box, period=11.0, width=5.0, ang=45, phase=0.0):
    """soft diagonal stripe mask over a frame box (x0,y0,x1,y1) -> (mask, off)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    a = math.radians(ang)
    u = (xx * math.cos(a) + yy * math.sin(a) + phase) % period
    d = np.abs(u - period / 2)
    return np.clip((width / 2 - d) / 1.0 + .5, 0, 1).astype(np.float32), (x0, y0)


def ell_ring(lyr, c, r_out, r_in, v=255):
    lyr.ell(c, r_out, r_out * KK, v=v)
    lyr.ell(c, r_in, r_in * KK, v=0)


def ring_marks(c, rc, n, fn):
    """call fn(point, tangent_unit, k) at n angles around the iso ellipse of radius rc."""
    for i in range(n):
        a = 2 * math.pi * i / n
        p = np.array([c[0] + rc * math.cos(a), c[1] + rc * KK * math.sin(a)])
        t = np.array([-math.sin(a), math.cos(a) * KK])
        t = t / np.hypot(*t)
        fn(p, t, i)


# ------------------------------------------------------------------ tier ring (ground)
def tier_ring(cv, B, tier, k=1.0, preview=False, pulse=1.0, ghost=.55, r_bu=None, dashed=True):
    """STYLE_CONTRACT tier ring: band 13.6 px, ink under-stroke 6.3 px, white inner rim 2.2 px, faint radial fill, tier pattern.
    SITES_LOST = ink-black band + white outer rim + bold ochre hatch. preview=True adds the second 'uncommitted' channel:
    a white 3 px hatch over the band, a soft pulse halo (`pulse` 0..1) and the dashed outer outline."""
    col = TIER[tier]
    R = (r_bu or TIER_R_BU[tier]) * BU
    Ri = R - BAND
    pad = R + UNDER + 40
    bx = (B[0] - pad, B[1] - pad * KK - 20, B[0] + pad, B[1] + pad * KK + 20)

    def draw():
        band, under, rim, pat, fl = (Lyr(bx, ss=2) for _ in range(5))
        ell_ring(band, B, R, Ri)
        ell_ring(under, B, R + UNDER, Ri - UNDER)
        ell_ring(rim, B, Ri + RIM, Ri)
        fl.ell(B, Ri, Ri * KK, 255)
        patn = pat
        mid = (R + Ri) / 2
        if tier == 'UNTOUCHED':          # dot row
            ring_marks(B, mid, max(10, int(2 * math.pi * mid / 15)), lambda p, t, i: patn.ell(p, 2.9, 2.9 * 1.0, v=255))
        elif tier == 'HOLDS':            # vertical bars
            ring_marks(B, mid, max(8, int(2 * math.pi * mid / 17)), lambda p, t, i: patn.line([(p[0], p[1] - 5.2), (p[0], p[1] + 5.2)], 3.4, 255))
        elif tier == 'DAMAGED':          # chevrons along the ring
            def chev(p, t, i):
                n_ = np.array([-t[1], t[0]])
                patn.line([tuple(p - t * 4.5 + n_ * 4.2), tuple(p + t * 3.2), tuple(p - t * 4.5 - n_ * 4.2)], 3.0, 255)
            ring_marks(B, mid, max(8, int(2 * math.pi * mid / 20)), chev)
        under_m = under.m
        band_m = band.m
        rim_m = rim.m
        cv.over(INK, under_m, .92 * k, under.off)
        if tier == 'SITES_LOST':
            cv.over(INK2, band_m, .98 * k, band.off)
            st, so = stripes((band.off[0], band.off[1], band.off[0] + band.w, band.off[1] + band.h), 11.0, 5.6, 45)
            cv.over(col, st * band_m, .98 * k, band.off)
            cv.add(col, blur(st * band_m, 5), .22 * k, band.off)
            orim = Lyr(bx, ss=2)
            ell_ring(orim, B, R, R - RIM)
            cv.over(WARM, orim.m, .96 * k, orim.off)
        else:
            cv.over(col, band_m, .98 * k, band.off)
            cv.add(col, blur(band_m, 6), .34 * k, band.off)
            cv.add(col, blur(band_m, 16), .16 * k, band.off)
            if tier == 'BREACHED':
                st, so = stripes((band.off[0], band.off[1], band.off[0] + band.w, band.off[1] + band.h), 9.0, 2.2, 45)
                st2, so = stripes((band.off[0], band.off[1], band.off[0] + band.w, band.off[1] + band.h), 9.0, 2.2, -45)
                cv.over(INK, np.maximum(st, st2) * band_m, .9 * k, band.off)
                r2 = Lyr(bx, ss=2)
                ell_ring(r2, B, R + UNDER + 9, R + UNDER + 5)
                cv.over(INK, blur(r2.m, 2) * 2.0, .8 * k, r2.off)
                cv.over(col, r2.m, .98 * k, r2.off)
            else:
                cv.over(INK, pat.m, .88 * k, pat.off)
            cv.over(WARM, rim_m, .9 * k, rim.off)
        cv.add(col, fl.m, .10 * k, fl.off)
        if preview:
            st, so = stripes((band.off[0], band.off[1], band.off[0] + band.w, band.off[1] + band.h), 7.0, 2.6, -45)
            cv.over(WHITE, st * band_m, .55 * k, band.off)
            halo = Lyr(bx, ss=2)
            ell_ring(halo, B, R + UNDER + 5, Ri - UNDER - 5)
            cv.add(WHITE * .8 + col * .2, blur(halo.m, 9), .34 * pulse * k, halo.off)
            if dashed:
                dl = Lyr(bx, ss=2)
                dl.line(ring_pts(B, R + UNDER + 8, 96, k=KK), 2.6, 255, dash=(7, 5))
                cv.over(INK, blur(dl.m, 2) * 1.6, .6 * k, dl.off)
                cv.add(WHITE, dl.m, .95 * k, dl.off)

    grounded(cv, draw, bx, ghost)


# ------------------------------------------------------------------ stop block (across the street)
def _w2s(c, w):
    return np.array([c[0] + w[0] * BU, c[1] + w[1] * BU * KK])


def block_poly(p, u, along=10.0, across=13.5, cham=1.4, grow=0.0):
    """world rectangle (BU) centred at screen p whose along-axis follows screen tangent u. chamfered. returns screen pts."""
    t = np.array([u[0], u[1] / KK])
    t = t / np.hypot(*t)
    n = np.array([-t[1], t[0]])
    a, b = along / 2 + grow, across / 2 + grow
    c_ = cham
    loc = [(-a + c_, -b), (a - c_, -b), (a, -b + c_), (a, b - c_), (a - c_, b), (-a + c_, b), (-a, b - c_), (-a, -b + c_)]
    return [tuple(_w2s(p, t * x + n * y)) for x, y in loc]


def stop_block(cv, P, s, tier, k=1.0, preview=False, pulse=1.0, ghost=.55):
    """STYLE_CONTRACT stop block 13.5 x 10 BU. P = hy.PX path, s = arclength."""
    col = TIER[tier]
    p, u, n = P.frame(s)
    poly = block_poly(p, u)
    poly_o = block_poly(p, u, grow=1.2)
    poly_r = block_poly(p, u, grow=-0.0)
    poly_i = block_poly(p, u, grow=-.35, cham=1.1)
    bx = pbox(poly_o, 30)

    def draw():
        o, f, i_, pat = (Lyr(bx, ss=2) for _ in range(4))
        o.poly(poly_o, 255)
        f.poly(poly_r, 255)
        i_.poly(poly_i, 255)
        t = np.array([u[0], u[1] / KK]); t = t / np.hypot(*t); nn = np.array([-t[1], t[0]])
        cv.over(INK, blur(o.m, 2.5) * 1.2, .5 * k, o.off)
        cv.over(INK, o.m, .94 * k, o.off)
        if tier == 'SITES_LOST':
            cv.over(INK2, f.m, .98 * k, f.off)
            st, so = stripes((f.off[0], f.off[1], f.off[0] + f.w, f.off[1] + f.h), 11.0, 5.6, 45)
            cv.over(col, st * i_.m, .98 * k, f.off)
            cv.over(WARM, np.clip(f.m - i_.m, 0, 1), .96 * k, f.off)
        else:
            cv.over(col, f.m, .98 * k, f.off)
            if tier == 'UNTOUCHED':
                for j in (-1, 0, 1):
                    q = _w2s(p, t * (j * 2.6))
                    pat.ell(q, 3.0, 3.0, v=255)
            elif tier == 'HOLDS':
                for j in (-1, 0, 1):
                    c0 = _w2s(p, nn * (j * 3.5))
                    a0 = _w2s(p, nn * (j * 3.5) + t * 3.4); b0 = _w2s(p, nn * (j * 3.5) - t * 3.4)
                    pat.line([tuple(a0), tuple(b0)], 3.6, 255)
            elif tier == 'DAMAGED':
                for j in (-1, 1):
                    c0 = _w2s(p, nn * 0 + t * (j * 2.4))
                    pts = [_w2s(p, t * (j * 2.4 - 1.1) + nn * 2.8), _w2s(p, t * (j * 2.4 + 1.1)), _w2s(p, t * (j * 2.4 - 1.1) - nn * 2.8)]
                    pat.line([tuple(q) for q in pts], 3.2, 255)
            elif tier == 'BREACHED':
                st, so = stripes((f.off[0], f.off[1], f.off[0] + f.w, f.off[1] + f.h), 9.0, 2.2, 45)
                st2, so = stripes((f.off[0], f.off[1], f.off[0] + f.w, f.off[1] + f.h), 9.0, 2.2, -45)
                cv.over(INK, np.maximum(st, st2) * f.m, .9 * k, f.off)
            cv.over(INK, pat.m, .9 * k, pat.off)
            cv.over(WARM, np.clip(f.m - i_.m, 0, 1), .92 * k, f.off)
        cv.add(col, blur(f.m, 6), .36 * k, f.off)
        cv.add(col, blur(f.m, 15), .16 * k, f.off)
        if preview:
            st, so = stripes((f.off[0], f.off[1], f.off[0] + f.w, f.off[1] + f.h), 7.0, 2.6, -45)
            cv.over(WHITE, st * f.m, .5 * k, f.off)
            cv.add(WHITE * .8 + col * .2, blur(f.m, 10), .34 * pulse * k, f.off)
            pg = block_poly(p, u, grow=3.2)
            dl = Lyr(bx, ss=2)
            dl.line(pg + [pg[0]], 2.6, 255, dash=(7, 5))
            cv.over(INK, blur(dl.m, 2) * 1.6, .6 * k, dl.off)
            cv.add(WHITE, dl.m, .95 * k, dl.off)

    grounded(cv, draw, bx, ghost)


# ------------------------------------------------------------------ head sprites (H6 family, 16 pre-rendered headings)
_HS = {}


def head_sprite(typ, ang_deg, scale=1.0):
    q = int(round((ang_deg % 360) / 22.5)) % 16
    key = (typ, q, round(scale, 2))
    if key not in _HS:
        im = Image.open(P2BASE + 'heads/%s_%03d.png' % (typ, int(q * 22.5))).convert('RGBA')
        if abs(scale - 1.0) > 1e-3:
            im = im.resize((max(8, int(im.width * scale)), max(8, int(im.height * scale))), Image.LANCZOS)
        _HS[key] = np.asarray(im, np.float32) / 255
    return _HS[key]


def head_at(cv, p, ang_deg, typ, k=1.0, scale=1.0, tint=None, halo=False):
    """paste a head sprite (STYLE_CONTRACT sec. 3) centred at p. tint = recolour toward a hue (hunter ghost = white)."""
    a = head_sprite(typ, ang_deg, scale)
    h, w = a.shape[:2]
    off = (int(round(p[0] - w / 2)), int(round(p[1] - h / 2)))
    al = a[..., 3] * k
    rgb = a[..., :3]
    if tint is not None:
        lum = rgb.mean(-1, keepdims=True)
        rgb = np.asarray(tint, np.float32)[None, None, :] * (.55 + .7 * lum)
    if halo:                                  # peak-impact halo: 3 px ink around the silhouette
        big = Image.fromarray((a[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
        cv.over(INK, np.asarray(big, np.float32) / 255, .95 * k, off)
    cv.over(np.clip(rgb, 0, 1), al, 1.0, off)


# ------------------------------------------------------------------ HOME: white ring + 50-tick gauge + warm pool
def home_ring(cv, B, hp=44, hp_max=50, preview=0, hit=0, k=1.0, worst=0, glow=1.0):
    """STYLE_CONTRACT HOME: brightest object. ring r22 BU w2.2 BU, ticks r19 BU (3.2 x 1.0 BU radial, major every 10th 4.2),
    lit warm white, preview = amber outline, lost = amber filled, dead 2A3150. Warm pool 18 BU under it."""
    R = 22 * BU
    Rt = 19 * BU
    pad = R + 60
    bx = (B[0] - pad, B[1] - pad * KK - 30, B[0] + pad, B[1] + pad * KK + 30)
    yy, xx = np.mgrid[max(int(bx[1]), 0):min(int(bx[3]), H), max(int(bx[0]), 0):min(int(bx[2]), W)].astype(np.float32)
    d = np.sqrt(((xx - B[0]) / (18 * BU)) ** 2 + ((yy - B[1]) / (18 * BU * KK)) ** 2)
    pool = np.clip(1 - d, 0, 1) ** 1.6
    cv.add(WARM, pool, .26 * k * glow, (max(int(bx[0]), 0), max(int(bx[1]), 0)))
    ring, ring_u, lit, prev, lost, dead, major_l, worstl = (Lyr(bx, ss=2) for _ in range(8))
    wd = 2.2 * BU
    ell_ring(ring, B, R, R - wd)
    ell_ring(ring_u, B, R + UNDER * .7, R - wd - UNDER * .7)
    remain = hp - preview - hit - worst
    for i in range(hp_max):
        ang = math.radians(-90 + 360 * i / hp_max)
        mj = (i % 10 == 0)
        ln = (4.2 if mj else 3.2) * BU
        p0 = (B[0] + (Rt - ln / 2) * math.cos(ang), B[1] + (Rt - ln / 2) * KK * math.sin(ang))
        p1 = (B[0] + (Rt + ln / 2) * math.cos(ang), B[1] + (Rt + ln / 2) * KK * math.sin(ang))
        wt = 1.0 * BU * (1.25 if mj else 1.0)
        if i < remain:
            lit.line([p0, p1], wt, 255)
        elif i < hp - hit - worst:
            prev.line([p0, p1], wt, 255)
        elif i < hp - hit:
            worstl.line([p0, p1], wt, 255)
        elif i < hp:
            lost.line([p0, p1], wt, 255)
        else:
            dead.line([p0, p1], wt * .8, 255)
    cv.over(INK, ring_u.m, .88 * k, ring_u.off)
    cv.over(WARM * .3 + WHITE * .7, ring.m, 1.0 * k, ring.off)
    cv.add(WHITE, ring.m, .8 * k, ring.off)
    cv.add(WARM, blur(ring.m, 7), .5 * k * glow, ring.off)
    cv.add(WARM, blur(ring.m, 22), .22 * k * glow, ring.off)
    cv.over(INK, blur(lit.m, 2) * 1.5, .6 * k, lit.off)
    cv.over(WARM, lit.m, .98 * k, lit.off)
    cv.add(WARM, blur(lit.m, 4), .35 * k, lit.off)
    cv.over(hexc('2A3150'), dead.m, .9 * k, dead.off)
    pc = TIER['DAMAGED']
    if prev.m.max() > 0:                       # preview = amber OUTLINE (the tick body is knocked out)
        pm = prev.m
        er = np.asarray(Image.fromarray((pm * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)), np.float32) / 255
        cv.over(INK, pm, .85 * k, prev.off)
        cv.add(pc, np.clip(pm - er, 0, 1), 1.0 * k, prev.off)
        cv.add(pc, blur(pm, 4), .45 * k, prev.off)
    if worstl.m.max() > 0:
        wc = TIER['BREACHED']
        cv.over(INK, worstl.m, .85 * k, worstl.off)
        cv.over(wc, worstl.m, .95 * k, worstl.off)
        cv.add(wc, blur(worstl.m, 4), .5 * k, worstl.off)
    if lost.m.max() > 0:
        cv.over(pc, lost.m, 1.0 * k, lost.off)
        cv.add(pc, blur(lost.m, 5), .8 * k, lost.off)


# ------------------------------------------------------------------ ICE towers, ranked
TOW_PX = {1: 100.0, 2: 130.0, 3: 164.0}
TOW_A = {1: 31.0, 2: 29.0, 3: 33.0}


def _box(B, a, h):
    b = a * KK
    L0, F0, R0, K0 = (B[0] - a, B[1]), (B[0], B[1] + b), (B[0] + a, B[1]), (B[0], B[1] - b)
    return L0, F0, R0, K0, (L0[0], L0[1] - h), (F0[0], F0[1] - h), (R0[0], R0[1] - h), (K0[0], K0[1] - h)


def tower(cv, B, tier=1, state='healthy', tint=None, alpha=.84, seed=0, glitch=0.0, hs=1.0, bright=True):
    """STYLE_CONTRACT ranked towers: bright (wire + scan lines + spine) only for Sites a beam stops at; the rest quiet glass 35 %,
    no wire, no spine. Heights 27 / 35 / 44 BU = 100 / 130 / 164 px. alpha is the focus ladder level."""
    rng = np.random.RandomState(seed + 7)
    a = TOW_A.get(tier, 31.0)
    h = TOW_PX.get(tier, 100.0) * hs
    col = TOW if tint is None else tint
    colD = TOW_D if tint is None else tint * .75
    dead = state in ('TAKEN', 'INFECTED')
    down = state == 'DOWN'
    if dead:
        col = VEIN * .8 + HOT * .2
        colD = PLUM_MID * 1.9
    if down:
        col = TOW * .55 + np.array([.2, .1, .15], np.float32)
        colD = TOW_D * .45
    hh = h * (.55 if down else 1.0)
    q = 1.0 if bright else .35                  # quiet glass level
    L0, F0, R0, K0, L1, F1, R1, K1 = _box(B, a, hh)
    bx = (B[0] - 80, B[1] - h - 120, B[0] + 80, B[1] + 40)
    faceL, faceR, top, edge, lat, hid, spine, scan = (Lyr(bx) for _ in range(8))
    OF = faceL.off
    faceL.poly([L0, F0, F1, L1], 255)
    faceR.poly([F0, R0, R1, F1], 255)
    top.poly([K1, R1, F1, L1], 255)
    edge.line([L0, L1], 2, 255)
    edge.line([F0, F1], 2, 255)
    edge.line([R0, R1], 2, 255)
    edge.line([L1, K1, R1, F1, L1], 2, 255)
    edge.line([L0, F0, R0], 2, 255)
    apex = None
    if tier == 2 and not down:
        apex = (B[0], K1[1] - a * 1.0)
        edge.line([L1, apex], 2, 255); edge.line([R1, apex], 2, 255); edge.line([F1, apex], 2, 255)
        faceL.poly([L1, F1, apex], 255); faceR.poly([F1, R1, apex], 255)
    if tier == 3 and not down:
        a2 = a * .6
        U = (B[0], B[1] - hh)
        l0, f0, r0, k0, l1, f1, r1, k1 = _box(U, a2, h * .42)
        faceL.poly([l0, f0, f1, l1], 255); faceR.poly([f0, r0, r1, f1], 255); top.poly([k1, r1, f1, l1], 255)
        edge.line([l0, l1], 2, 255); edge.line([f0, f1], 2, 255); edge.line([r0, r1], 2, 255); edge.line([l1, k1, r1, f1, l1], 2, 255)
        edge.line([(B[0], k1[1] + a2 * KK), (B[0], k1[1] - 26)], 2, 255)
        apex = (B[0], k1[1] - 26)
    n_scan = max(4, int(hh / 9))
    for i in range(1, n_scan):
        t = i / n_scan
        scan.line([(L0[0], L0[1] - hh * t), (F0[0], F0[1] - hh * t)], 1, 190)
        scan.line([(F0[0], F0[1] - hh * t), (R0[0], R0[1] - hh * t)], 1, 190)
    lat.line([L0, F1], 1, 130); lat.line([F0, L1], 1, 130); lat.line([F0, R1], 1, 130); lat.line([R0, F1], 1, 130)
    spine.line([(F0[0], F0[1]), (F1[0], F1[1] - 4)], 3.2, 255)
    if down:
        for i in range(5):
            y = B[1] - hh - 8 - i * 9
            ox = rng.uniform(-9, 9)
            hid.line([(L0[0] + ox, y), (F0[0] + ox, y + a * KK), (R0[0] + ox, y)], 1, 255, dash=(4, 3))
    body = np.maximum(np.maximum(faceL.m, faceR.m), top.m)
    cv.over(INK, body, .55 * alpha * (1 if bright else .55), OF)
    cv.add(colD, faceL.m, .10 * alpha * q, OF)
    cv.add(col, faceR.m, .20 * alpha * q, OF)
    cv.add(col, top.m, .34 * alpha * q, OF)
    if bright:
        cv.neon(scan.m, colD, core=.30 * alpha, g1=None, g2=None, off=OF)
        cv.neon(lat.m, colD, core=.35 * alpha, g1=None, g2=None, off=OF)
        cv.neon(edge.m, col, core=.95 * alpha, g1=(3, .3 * alpha), g2=(11, .10 * alpha), white=.07 * alpha, off=OF)
        cv.neon(spine.m, col * .6 + WHITE * .4, core=.8 * alpha, g1=(4, .5 * alpha), g2=(14, .25 * alpha), white=.3 * alpha, off=OF)
        cv.neon(hid.m, colD, core=.35 * alpha, g1=None, g2=None, off=OF)
    else:
        cv.neon(edge.m, col, core=.30 * alpha, g1=None, g2=None, off=OF)       # quiet: faint edge only, no wire, no spine
        cv.neon(hid.m, colD, core=.25 * alpha, g1=None, g2=None, off=OF)
    crown = (B[0], B[1] - hh - (a * 1.0 if tier == 2 and not down else 0) - (h * .42 + 26 if tier == 3 and not down else 0))
    if bright and not dead:
        st = Lyr(bx)
        for i in range(8):
            yy = crown[1] - 6 - i * 7 - rng.uniform(0, 4)
            st.line([(crown[0] + rng.uniform(-3, 3), yy), (crown[0] + rng.uniform(-3, 3), yy - rng.uniform(2, 5))], 1, int(255 * (1 - i / 9)))
        cv.neon(st.m, col, core=.8 * alpha * (.5 if down else 1), g1=(2, .5), g2=None, off=OF)
    return crown


# ------------------------------------------------------------------ Solace cage (mint, 60 %)
def solace_cage(cv, hq_base, alpha=1.0, phase=0.0, hot=False):
    col = MINT * .60
    c = np.array([hq_base[0] + 140, hq_base[1] - 170])
    ly, rails_, back, sc = Lyr(), Lyr(), Lyr(), Lyr()
    Hh = 330
    for i in range(0, 9):
        t = i / 8
        ly.line(ring_pts((c[0], c[1] - t * Hh), 112 - 12 * t, 72), 2, 255)
    for ang in range(0, 360, 45):
        p0 = (c[0] + 112 * math.cos(math.radians(ang)), c[1] + 112 * KK * math.sin(math.radians(ang)))
        p1 = (c[0] + 100 * math.cos(math.radians(ang)), c[1] - Hh + 100 * KK * math.sin(math.radians(ang)))
        if math.sin(math.radians(ang)) >= -0.2:
            rails_.line([p0, p1], 2, 255)
        else:
            back.line([p0, p1], 1, 255, dash=(3, 3))
    sy = c[1] - ((phase % 1.0) * Hh)
    sc.line(ring_pts((c[0], sy), 118, 80), 3, 255)
    cv.neon(ly.m, col, core=.55 * alpha, g1=(3, .4 * alpha), g2=(12, .22 * alpha))
    cv.neon(rails_.m, col, core=.55 * alpha, g1=(3, .3 * alpha), g2=None)
    cv.neon(back.m, col * .6, core=.4 * alpha, g1=None, g2=None)
    cv.neon(sc.m, col * .8 + WHITE * .2, core=.7 * alpha, g1=(5, .6), g2=(18, .35))
    return c


# ------------------------------------------------------------------ pressure: dread shadow + plum creep + draining ring
def dread_shadow(cv, P, s_head, k=1.0, reach=220.0, amt=.45):
    """the city darkens 45 % in a tapering corridor `reach` px ahead of a head along its route."""
    pts = P.sub(s_head + 20, min(P.L, s_head + 20 + reach), 6)
    if len(pts) < 3:
        return
    bb = pbox(pts, 90)
    ly = Lyr(bb, ss=1)
    n = len(pts)
    for i in range(n - 1):
        wgt = 70 * (1 - i / n) + 18
        ly.line([tuple(pts[i]), tuple(pts[i + 1])], wgt, int(255 * (1 - .8 * i / n)))
    m = blur(ly.m, 24)
    mm = np.clip(m * 1.3, 0, 1) * amt * k
    sl = tuple(slice(int(max(o, 0)), int(min(o + s_, lim))) for o, s_, lim in ((ly.off[1], ly.h, H), (ly.off[0], ly.w, W)))
    cv.img[sl] *= (1 - mm[:sl[0].stop - sl[0].start, :sl[1].stop - sl[1].start, None])


def drain_ring(cv, B, frac=.66, k=1.0):
    """DOWN decay ring on the ground: arc fraction = turns left."""
    R = 12.0 * BU
    bx = (B[0] - R - 30, B[1] - R * KK - 30, B[0] + R + 30, B[1] + R * KK + 30)
    ar = Lyr(bx, ss=2)
    pts = ring_pts(B, R, 64, k=KK, a0=-90, a1=-90 + 360 * frac)
    ar.line(pts, 6.0, 255)
    cv.over(INK, blur(ar.m, 2) * 1.8, .85 * k, ar.off)
    cv.over(WARM, ar.m, .9 * k, ar.off)
    ghost = Lyr(bx, ss=2)
    ghost.line(ring_pts(B, R, 64, k=KK, a0=-90 + 360 * frac, a1=270), 2.0, 255, dash=(3, 6))
    cv.add(WARM * .6, ghost.m, .6 * k, ghost.off)


def plum_creep(cv, hq_base, R=150.0, k=.4, seed=4):
    """faint plum creep from the HQ cage base (front radius R px, domain-warped, veins at the edge). k = strength (30-45 %)."""
    c = np.array([hq_base[0] + 140, hq_base[1] - 170 + 8])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rng = np.random.RandomState(seed)
    g = rng.rand(H // 40 + 3, W // 40 + 3).astype(np.float32)
    from scipy import ndimage as ndi
    nz = ndi.zoom(g, 40, order=3)[:H, :W]
    nz2 = ndi.zoom(rng.rand(H // 14 + 3, W // 14 + 3).astype(np.float32), 14, order=3)[:H, :W]
    d = np.sqrt(((xx - c[0]) / 1.0) ** 2 + ((yy - c[1]) / KK) ** 2) + (nz - .5) * 120 + (nz2 - .5) * 36
    m = np.clip((R - d) / 22.0, 0, 1)
    edge = np.clip(1 - np.abs(d - R) / 4.5, 0, 1) * (nz2 > .42)
    box = (int(c[0] - R * 1.5), int(c[1] - R * 1.2), int(c[0] + R * 1.5), int(c[1] + R * 1.2))
    x0, y0, x1, y1 = max(box[0], 0), max(box[1], 0), min(box[2], W), min(box[3], H)
    m_ = m[y0:y1, x0:x1]; e_ = edge[y0:y1, x0:x1]
    cv.img[y0:y1, x0:x1] = cv.img[y0:y1, x0:x1] * (1 - m_[..., None] * .55 * k) + hexc('1E0A22') * m_[..., None] * .55 * k + hexc('4A1440') * (m_ * (nz2[y0:y1, x0:x1]))[..., None] * .5 * k
    cv.img[y0:y1, x0:x1] += VEIN[None, None, :] * (e_ * .9 * k)[..., None] + HOT[None, None, :] * (e_ * (nz2[y0:y1, x0:x1] > .6) * .45 * k)[..., None]
