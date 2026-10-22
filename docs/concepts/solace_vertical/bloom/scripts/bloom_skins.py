"""Solace THE BLOOM v2: the three infection materials as numpy skins (world-space, deterministic hash noise, no RNG).

Every skin takes the clean frame P (float RGB 0..1), a coverage field and a field `d` = units BEHIND the front (positive =
infected), and texture coordinates (u, v) in the same units. Frame builders (street / hq / raid / gauge) supply the fields.
Sizes (zones, cell sizes) are in field units; line widths are in screen pixels (pixel distance from a noise contour, or the
field units-per-pixel estimate `ups`).

  A  Necrosis   plum-black skin, pink veins, hairline hot front edge, dim window light behind the front
  B  Mycelium   pale threads first (front), then thick puffy mats, glowing pink spore caps deeper in
  C  Culture    glossy pink biofilm / agar: translucent gel, bubbles + cells, a meniscus rim at the front
"""
import numpy as np

import solace_lib as L

PINK = L.PINK
PLUM = L.PLUM
SM = L.smoothstep


def pxdist(f):
    """Signed field -> approximate distance in screen pixels to its zero level."""
    gy, gx = np.gradient(f)
    return f / (np.sqrt(gx * gx + gy * gy) + 1e-4)


def line(n, w):
    """Thin line (width ~w px) on the 0.5 contour of a noise field."""
    gy, gx = np.gradient(n)
    dist = np.abs(n - 0.5) / (np.sqrt(gx * gx + gy * gy) + 1e-4)
    return np.clip(1.0 - dist / w, 0, 1)


def ups(u, v):
    """Field units per screen pixel (smoothed), so widths can be set in pixels for any (u, v) mapping."""
    uy, ux = np.gradient(u)
    vy, vx = np.gradient(v)
    g = np.clip(np.sqrt(0.5 * (ux * ux + uy * uy + vx * vx + vy * vy)), 1e-4, None)
    med = float(np.median(g))
    return np.clip(L.boxblur(np.clip(g, med * 0.2, med * 5.0), 6), 1e-4, None)


def cells(u, v, size, seed):
    a, b = u / size, v / size
    i, j = np.floor(a).astype(np.int64), np.floor(b).astype(np.int64)
    r1, r2, r3 = L._hash(i, j, seed), L._hash(i, j, seed + 7), L._hash(i, j, seed + 13)
    cx, cy = i + 0.25 + 0.5 * r1, j + 0.25 + 0.5 * r2
    dx, dy = (a - cx) * size, (b - cy) * size
    return dx, dy, np.hypot(dx, dy), r1, r2, r3


def posterize(s, steps=3):
    return np.floor(np.clip(s, 0, 0.999) * steps + 0.5) / steps if steps else s


# ------------------------------------------------------------------------------------------------ A  Necrosis
def veins(u, v, d, fq, zv, seed=7, w=1.0, keep_lo=0.52):
    out = 0.0
    for k, (su, sv, wgt) in enumerate(((1.0, 1.0, 1.0), (1.9, 1.7, 0.7))):
        n = L.fbm(u * fq * su, v * fq * sv, seed + 31 * k, 4)
        ln = line(n, w * 0.9)
        dens = L.fbm(u * fq * 0.35 + 9, v * fq * 0.35 + 3, seed + 77 + k, 2)
        keep = SM(keep_lo - 0.2, keep_lo + 0.14, dens)
        out = np.maximum(out, ln * keep * wgt)
    return out * (0.45 + 0.55 * SM(0.0, zv, d))


def skin_A(P, cover, d, u, v, c):
    H, W = P.shape[:2]
    Lm = L.luma(P)
    pn = (PINK / 0.4518)[None, None, :]
    plum_n = (PLUM / 0.0830)[None, None, :]
    t = np.clip(Lm / 0.5, 0, 1) ** 0.8
    body = plum_n * (c.get("body0", 0.040) + c.get("body1", 0.030) * t)[..., None]
    bright = SM(0.42, 0.7, Lm)
    win = pn * np.minimum(0.22 * Lm, 0.14)[..., None]
    inf = body * (1 - bright[..., None]) + win * bright[..., None]
    hat = L.hatch(H, W, c.get("hpitch", 9), 2) * SM(0.0, c["zT"], d)
    inf = inf + (hat * 0.35 * 0.06)[..., None] * pn
    vn = veins(u, v, d, c["fq"], c["zM"], c.get("seed", 7), c.get("vw", 1.0), c.get("keep_lo", 0.52)) * c.get("vein", 1.0)
    inf = np.minimum(inf + (vn * c.get("vgain", 0.66))[..., None] * PINK[None, None, :], 1.0)
    out = P * (1 - cover[..., None]) + inf * cover[..., None]
    dp = pxdist(d)
    edge = np.exp(-((dp - 0.3) / c.get("ew", 1.5)) ** 2) * (dp > -4) * (cover > 0.02)
    out = out + (edge * 0.75)[..., None] * PINK[None, None, :]
    return np.clip(out, 0, 1)


# ------------------------------------------------------------------------------------------------ B  Mycelium
MAT_DARK = np.array([0.06, 0.03, 0.06], np.float32)
MAT_BONE = np.array([0.80, 0.55, 0.68], np.float32)
THREAD = np.array([0.96, 0.92, 0.90], np.float32)
CAP = np.array([1.0, 0.275, 0.588], np.float32)
CAP_HOT = np.array([1.0, 0.82, 0.92], np.float32)


def threads(u, v, fq, seed, w):
    """A web of long pale hairs: three anisotropic noise fields at 60 degree steps, thin contours (w px)."""
    out = 0.0
    for k in range(3):
        a = np.pi * k / 3 + 0.4
        uu = (u * np.cos(a) + v * np.sin(a))
        vv = (-u * np.sin(a) + v * np.cos(a))
        warp = 0.6 * L.fbm(uu * fq * 0.4, vv * fq * 0.4, seed + 5 * k, 2)
        n = L.fbm(uu * fq * 0.30 + warp, vv * fq * 2.4, seed + 11 * k, 3)
        keep = 0.55 + 0.45 * SM(0.35, 0.65, L.fbm(uu * fq * 0.2, vv * fq * 0.2, seed + 3 * k, 2))
        out = np.maximum(out, line(n, w) * keep)
    return out


def hyphae(shape, d, cover, seed, spacing=26.0, length=90.0, width=1.4, branch=0.05, dmin=-8.0, wander=0.22, flow=0.55):
    """Fungal hyphae as strokes: curvy hairs that follow the screen-space gradient of the front distance `d` (so they crawl
    out of the front), forking now and then. Returns alpha 0..1 (shape H x W). Deterministic (numpy RandomState(seed))."""
    from PIL import Image as _I, ImageDraw as _D
    H, W = shape
    rs = np.random.RandomState(seed)
    gy, gx = np.gradient(L.blur(np.clip(d, -40, 60) / 60.0 + 0.5, 6.0))
    gm = np.sqrt(gx * gx + gy * gy) + 1e-6
    fx, fy = gx / gm, gy / gm
    SSn = 2
    img = _I.new("L", (W * SSn, H * SSn), 0)
    dr = _D.Draw(img)
    ny, nx = int(H / spacing), int(W / spacing)
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = (i + rs.rand()) * spacing
            y = (j + rs.rand()) * spacing
            xi, yi = int(min(W - 1, x)), int(min(H - 1, y))
            if cover[yi, xi] < 0.5 or rs.rand() > 0.85:
                continue
            stack = [(x, y, 1, 1, length * (0.5 + rs.rand()))]
            while stack:
                px, py, sgn, depth, ln = stack.pop()
                ang = np.arctan2(fy[int(min(H - 1, max(0, py))), int(min(W - 1, max(0, px)))], fx[int(min(H - 1, max(0, py))), int(min(W - 1, max(0, px)))])
                wob = rs.randn() * 0.4
                pts = [(px, py)]
                steps = int(ln / 4)
                for k in range(steps):
                    wob += rs.randn() * wander
                    wob *= 0.9
                    xi, yi = int(min(W - 1, max(0, px))), int(min(H - 1, max(0, py)))
                    a = np.arctan2(fy[yi, xi], fx[yi, xi]) if flow > 0 else ang
                    a = a + wob * (1.0 - flow * 0.5) + (0 if sgn > 0 else np.pi)
                    px += np.cos(a) * 4.0
                    py += np.sin(a) * 4.0
                    if not (0 <= px < W and 0 <= py < H):
                        break
                    xi, yi = int(px), int(py)
                    if cover[yi, xi] < 0.3 or d[yi, xi] < dmin:
                        break
                    pts.append((px, py))
                    if depth < 3 and rs.rand() < branch:
                        stack.append((px, py, sgn, depth + 1, ln * 0.5))
                if len(pts) > 2:
                    wd = max(1, int(round(width * SSn * (1.0 if depth == 1 else 0.7))))
                    dr.line([(a * SSn, b * SSn) for a, b in pts], fill=255, width=wd, joint="curve")
            # a strand also goes the other way (back toward the front)
            stack = [(x, y, -1, 1, length * 0.5 * (0.5 + rs.rand()))]
            while stack:
                px, py, sgn, depth, ln = stack.pop()
                wob = rs.randn() * 0.4
                pts = [(px, py)]
                for k in range(int(ln / 4)):
                    wob += rs.randn() * wander
                    wob *= 0.9
                    xi, yi = int(min(W - 1, max(0, px))), int(min(H - 1, max(0, py)))
                    a = np.arctan2(fy[yi, xi], fx[yi, xi]) + np.pi + wob * (1.0 - flow * 0.5)
                    px += np.cos(a) * 4.0
                    py += np.sin(a) * 4.0
                    if not (0 <= px < W and 0 <= py < H):
                        break
                    xi, yi = int(px), int(py)
                    if cover[yi, xi] < 0.3 or d[yi, xi] < dmin:
                        break
                    pts.append((px, py))
                if len(pts) > 2:
                    dr.line([(a * SSn, b * SSn) for a, b in pts], fill=255, width=max(1, int(round(width * SSn))), joint="curve")
    a = np.asarray(img.resize((W, H), _I.LANCZOS), np.float32) / 255.0
    return a


def domes(u, v, size, seed, rmax=0.30):
    dx, dy, dist, r1, r2, r3 = cells(u, v, size, seed)
    rad = size * (0.17 + (rmax - 0.17) * r3)
    return np.sqrt(np.clip(1.0 - (dist / rad) ** 2, 0, None)), rad


def skin_B(P, cover, d, u, v, c):
    fq, seed = c["fq"], c.get("seed", 7)
    cel = c.get("cel", False)
    pu = ups(u, v)
    Lm = L.luma(P)
    zT, zM, zC = c["zT"], c["zM"], c["zC"]
    sz = c["cap"]
    tw = c.get("tw", 1.4)
    cov_h = (cover > 0.3).astype(np.float32)
    hy = hyphae(P.shape[:2], d / max(pu.mean(), 1e-6) * 0 + pxdist(d), np.maximum(cover, (d > -zT * 1.5).astype(np.float32) * 0.6), seed + 5, spacing=c.get("hsp", 22.0), length=c.get("hlen", 110.0), width=c.get("hw", 1.5), dmin=-zT / max(pu.mean(), 1e-6) * 1.2)
    thr_front = hy
    dens = L.fbm(u * fq * 0.8, v * fq * 0.8, seed + 21, 3)
    matk = SM(zT * 0.9, zM, d + c.get("matw", 1.0) * zT * (dens - 0.5))
    # felt relief: three layers of soft domes, light from the upper left in screen space
    h1, _ = domes(u, v, sz * 1.7, seed + 40)
    h2, _ = domes(u + 4.1, v + 2.3, sz * 1.0, seed + 44)
    h3, _ = domes(u - 1.7, v + 5.9, sz * 0.55, seed + 48, 0.32)
    h = L.blur(np.maximum(np.maximum(h1 * 0.95, h2 * 0.75), h3 * 0.55), 1.2)
    gy, gx = np.gradient(h)
    shade = np.clip(0.50 + (-gx * 0.6 - gy * 0.8) * c.get("lump", 4.0) + 0.45 * (h - 0.4), 0.0, 1.0) ** c.get("gamma", 1.3)
    if cel:
        shade = posterize(shade, 3)
    mat_col = (MAT_DARK[None, None, :] * (1 - shade[..., None]) + MAT_BONE[None, None, :] * shade[..., None]) * c.get("matv", 0.6)
    # felt fibres over the mat: a dense fine hair web (pale), plus a blotchy pink under-glow
    fib = hyphae(P.shape[:2], pxdist(d), cover, seed + 9, spacing=c.get("hsp", 22.0) * 0.8, length=c.get("hlen", 110.0) * 0.8, width=c.get("hw", 1.5) * 0.85, dmin=0.0, wander=0.30)
    fibc = np.array([0.98, 0.80, 0.88], np.float32)
    mat_col = mat_col * (1 - 0.7 * fib[..., None]) + fibc[None, None, :] * fib[..., None] * c.get("fibv", 0.7) * (0.5 + 0.5 * shade[..., None])
    # spore caps: discrete discs with a hot core, a glow, and a stalk-shadow underneath
    dx, dy, dist, r1, r2, r3 = cells(u, v, sz * 1.6, seed + 60)
    rad = sz * 1.6 * (0.10 + 0.07 * r3)
    soft = 1.2 * pu
    pres = (r1 > 1.0 - c.get("capp", 0.5) * SM(zC, zC * 2.5, d)) * (d > zC)
    capm = SM(rad, rad - soft, dist) * pres
    core = SM(rad * 0.55, rad * 0.15, np.hypot(dx + 0.22 * rad, dy + 0.25 * rad)) * pres
    halo = np.exp(-(dist / (rad * 2.6)) ** 2) * pres * 0.8
    shadow = SM(rad * 1.5, rad * 0.9, np.hypot(dx - 0.5 * rad, dy - 0.7 * rad)) * pres * (1 - capm)
    dx2, dy2, dist2, q1, q2, q3 = cells(u + 3.1, v - 1.7, sz * 0.8, seed + 80)
    rad2 = sz * (0.06 + 0.05 * q3)
    pres2 = (q1 > 0.6) * (d > zC * 0.7)
    cap2 = SM(rad2, rad2 - soft, dist2) * pres2
    halo2 = np.exp(-(dist2 / (rad2 * 2.4)) ** 2) * pres2 * 0.5
    mat_col = mat_col * (1 - 0.55 * shadow[..., None])
    mat_col = mat_col + (halo + halo2)[..., None] * CAP[None, None, :] * 0.30
    mat_col = mat_col * (1 - capm[..., None]) + capm[..., None] * CAP[None, None, :] * (0.80 + 0.2 * shade[..., None])
    mat_col = mat_col * (1 - core[..., None]) + core[..., None] * CAP_HOT[None, None, :]
    mat_col = mat_col * (1 - cap2[..., None]) + cap2[..., None] * CAP[None, None, :] * 0.95
    ma = (cover * matk)[..., None]
    out = P * (1 - ma) + mat_col * ma
    tcol = THREAD[None, None, :] * (0.55 + 0.45 * np.clip(Lm * 1.4, 0, 1))[..., None] * c.get("tv", 0.9)
    ta = thr_front * cover * c.get("ta", 0.95)
    out = out * (1 - ta[..., None]) + tcol * ta[..., None]
    return np.clip(out, 0, 1)


# ------------------------------------------------------------------------------------------------ C  Culture spill
GEL = np.array([1.0, 0.25, 0.58], np.float32)
GEL_DEEP = np.array([0.55, 0.07, 0.30], np.float32)
WHITE = np.array([1.0, 0.90, 0.95], np.float32)


def skin_C(P, cover, d, u, v, c):
    fq, seed = c["fq"], c.get("seed", 7)
    cel = c.get("cel", False)
    pu = ups(u, v)
    Lm = L.luma(P)
    zT, zM = c["zT"], c["zM"]
    dp = pxdist(d)
    depth = SM(0.0, zM, d)
    tint = np.array([1.0, 0.62, 0.82], np.float32)[None, None, :]
    seen = P * tint * (c.get("seen", 0.70) - 0.25 * depth)[..., None]
    body = GEL_DEEP[None, None, :] * (0.28 + 0.55 * np.sqrt(np.clip(Lm, 0, 1)))[..., None] * 0.42 + GEL[None, None, :] * (0.06 + 0.12 * depth)[..., None]
    sk = c.get("see", 0.8)
    gel = seen * sk + body * (1 - sk * 0.3)
    h = L.fbm(u * fq * 0.7, v * fq * 0.7, seed + 90, 4)
    gy, gx = np.gradient(L.blur(h, 2.0))
    nx, ny = -gx * c.get("rip", 90.0), -gy * c.get("rip", 90.0)
    spec = np.clip(0.55 + 0.9 * (nx * -0.55 + ny * -0.8), 0, 1) ** c.get("spec_p", 14.0)
    if cel:
        spec = (spec > 0.35).astype(np.float32) * 0.8
    gel = gel + (spec * c.get("spec", 0.55))[..., None] * WHITE[None, None, :]
    cau = line(L.fbm(u * fq * 1.4, v * fq * 1.4, seed + 120, 4), 1.1) * SM(zT, zM, d) * c.get("cau", 0.25)
    gel = gel + cau[..., None] * GEL[None, None, :]
    acc = np.zeros(P.shape, np.float32)
    for (sz, seed_b, p, rr) in ((c["bub"], seed + 200, 0.50, 0.30), (c["bub"] * 0.45, seed + 220, 0.55, 0.28)):
        dx, dy, dist, r1, r2, r3 = cells(u, v, sz, seed_b)
        rad = sz * (0.14 + rr * 0.20 * r3)
        pres = (r1 > 1.0 - p * SM(zT * 0.4, zM, d)) * (d > rad * 0.6)
        ringw = np.maximum(0.07 * rad, 1.4 * pu)
        ring = np.exp(-((dist - rad) / ringw) ** 2) * pres
        inside = SM(rad, rad - 1.2 * pu, dist) * pres
        hi = SM(rad * 0.30, rad * 0.12, np.hypot(dx + 0.38 * rad, dy + 0.42 * rad)) * pres
        cres = np.exp(-((np.hypot(dx - 0.25 * rad, dy - 0.3 * rad) - rad * 0.78) / ringw) ** 2) * pres * (dx * 0.5 + dy * 0.8 > 0)
        acc += inside[..., None] * GEL[None, None, :] * 0.16
        acc += (ring * 0.7)[..., None] * WHITE[None, None, :] + (hi * 0.9)[..., None] * WHITE[None, None, :] + (cres * 0.4)[..., None] * GEL[None, None, :]
    gel = gel + acc
    dx, dy, dist, r1, r2, r3 = cells(u - 2.2, v + 5.1, c["bub"] * 0.32, seed + 300)
    rad = c["bub"] * 0.32 * (0.15 + 0.12 * r3)
    pres = (r1 > 1.0 - 0.5 * SM(zM * 0.6, zM * 1.4, d)) * (d > zT)
    dm = SM(rad, rad - 1.0 * pu, dist) * pres
    nuc = SM(rad * 0.38, rad * 0.22, dist) * pres
    gel = gel * (1 - dm[..., None] * 0.25) + dm[..., None] * GEL[None, None, :] * 0.14
    gel = gel * (1 - nuc[..., None]) + nuc[..., None] * (GEL_DEEP * 0.5)[None, None, :]
    if cel:
        gel = posterize(gel, 5)
    a = cover * c.get("alpha", 0.92)
    out = P * (1 - a[..., None]) + np.clip(gel, 0, 1) * a[..., None]
    rim = np.exp(-(dp / 1.7) ** 2) * (np.abs(dp) < 8) * (cover > 0.01)
    band = SM(0.0, 3.0, dp) * (1 - SM(8.0, 22.0, dp)) * 0.42 * (cover > 0.01)
    out = out + band[..., None] * GEL[None, None, :] * 0.55
    sh = SM(-14.0, -1.0, dp) * (1 - SM(-1.0, 0.5, dp)) * 0.35 * c.get("lead_shadow", 1.0)
    out = out * (1 - sh[..., None])
    out = out * (1 - np.clip(rim * 0.9, 0, 1)[..., None]) + np.clip(rim, 0, 1)[..., None] * 0.95 * WHITE[None, None, :]
    return np.clip(out, 0, 1)


SKINS = {"A": skin_A, "B": skin_B, "C": skin_C}


def lift_median(P0, out, cover, tol=0.004, gmax=1.6):
    """Value rule: keep the frame median at the clean frame's (bisected gain on the uncovered dim pixels, or a dimming of
    the covered part when the skin is brighter than the clean frame)."""
    tm = float(np.median(L.luma(P0)))
    unc = (1 - cover)[..., None]
    dim = (1 - SM(0.4, 0.8, L.luma(P0)))[..., None]

    def med(g):
        return float(np.median(L.luma(np.clip(out * (1 + (g - 1) * unc * dim), 0, 1))))
    m0 = med(1.0)
    if m0 < tm - tol:
        lo, hi = 1.0, gmax
        for _ in range(9):
            mid = (lo + hi) / 2
            if med(mid) < tm - tol / 2:
                lo = mid
            else:
                hi = mid
        return np.clip(out * (1 + (hi - 1) * unc * dim), 0, 1), hi
    if m0 > tm + tol:
        lo, hi = 0.25, 1.0
        cv = (cover * (1 - SM(0.22, 0.5, L.luma(out))))[..., None]          # bright skin features (threads, caps, rims) stay

        def med2(g):
            return float(np.median(L.luma(out * (1 - cv * (1 - g)))))
        for _ in range(9):
            mid = (lo + hi) / 2
            if med2(mid) > tm + tol / 2:
                hi = mid
            else:
                lo = mid
        return np.clip(out * (1 - cv * (1 - lo)), 0, 1), lo
    return out, 1.0
