"""P2 pressure on the map BEFORE the hit (punch #6): plum creep from the Solace cage, a dread shadow ahead of each head, burn marks (06).
All evaluated per pixel from the depth recon so the front follows the real ground and climbs the facades."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import p1lib as L
import p1_comp as C

W, H = C.W, C.H
S = C.S
PLUM = np.array([0.060, 0.012, 0.075], np.float32)       # linear
PLUM_MID = np.array([0.05, 0.008, 0.055], np.float32)
VEIN = np.array([1.0, 0.05, 0.40], np.float32)
HOT = np.array([1.0, 0.55, 0.85], np.float32)
CAGE_PX = (1650.0, 470.0)
_P = None


def worldP():
    global _P
    if _P is None:
        _P = np.load(L.WORK + C.REC)['P']
    return _P


def creep(img, geo, R_bu, k=1.0, seed=7, emis_out=False):
    """plum creep: front at ground distance R_bu (BU) from the cage base, domain-warped; facades climb with the front; veins + a hairline at the front.
    returns img', hairline emission (linear, for bloom)."""
    P = worldP()
    g = L.screen_to_ground(np.array([CAGE_PX]))[0]
    d = np.hypot(P[..., 0] - g[0], P[..., 2] - g[2])
    nz = C.fbm(seed)
    warp = (nz - 0.5) * 2.0 * 16.0 + (C.noise2(seed + 5, 22) - 0.5) * 8.0
    dd = d + warp
    inside = np.clip((R_bu - dd) / 1.4, 0, 1)
    hag = geo['hag']; idm = geo['idm']
    # facades: the plum climbs to a height proportional to how deep inside the front the base is
    climb = np.clip((R_bu - dd) * 0.9, 0, 60)
    bld = (idm == 2) | (hag > 2.0)
    m = np.where(bld, np.clip((climb - hag) / 2.0, 0, 1) * (inside > 0), inside)
    m = C.blur(m, 0.8) * k
    veins = 1 - np.abs(C.noise2(seed + 9, 14) + 0.5 * (C.noise2(seed + 11, 6) - 0.5) - 0.5) * 7.0
    veins = np.clip(veins, 0, 1) ** 2.5
    body = img * (1 - 0.70 * m[..., None]) + PLUM_MID[None, None] * (0.6 * m[..., None]) + PLUM[None, None] * (0.4 * m[..., None])
    body = body + VEIN[None, None] * (0.04 * veins * m)[..., None]
    front = np.clip(1 - np.abs(R_bu - dd) / 0.9, 0, 1) * (bld == False) * k
    front_b = np.clip(1 - np.abs(climb - hag) / 0.8, 0, 1) * bld * (inside > 0) * k
    hair = np.maximum(front, front_b * 0.8)
    em = HOT[None, None] * (0.12 * hair)[..., None] + VEIN[None, None] * (0.12 * np.clip(C.blur(hair, 3) * 3, 0, 1))[..., None]
    return body + em, em


def dread(heads_route, route_px, ahead=300.0, k=0.45):
    """dark corridor ahead of every head along its route: heads_route = list of (rid, s_px); route_px[rid] = polyline (list of px). Returns (H,W) darkening 0..k."""
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for rid, s0 in heads_route:
        p = np.asarray(route_px[rid], float)
        cs = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
        for s in np.arange(s0, min(s0 + ahead, cs[-1]), 6.0):
            t = (s - s0) / ahead
            w = (1 - t) ** 1.1
            q = (np.interp(s, cs, p[:, 0]) * S, np.interp(s, cs, p[:, 1]) * S)
            r = (34 + 14 * (1 - t)) * S
            d.ellipse([q[0] - r, q[1] - r * 0.8, q[0] + r, q[1] + r * 0.8], fill=int(255 * w))
    a = np.asarray(im, np.float32) / 255
    a = C.blur(a, 16)
    return np.clip(a * 1.5, 0, 1) * k


def burn_marks(img, sites_px, seed=3, k=1.0):
    """scorch on the map (06): ink-black blooms with ember rims and soot streaks up-screen, centred on the lost / hit places."""
    rng = np.random.RandomState(seed)
    yy, xx = (np.mgrid[0:H, 0:W].astype(np.float32) / S)
    soot = np.zeros((H, W), np.float32); ember = np.zeros((H, W), np.float32); glow = np.zeros((H, W), np.float32)
    n = C.noise2(seed + 1, 18)
    for (x, y, r) in sites_px:
        dd = np.hypot((xx - x) / 1.0, (yy - y) / 0.62)
        edge = r * (0.85 + 0.35 * n)
        s = np.clip((edge - dd) / 6.0, 0, 1)
        soot = np.maximum(soot, s)
        ring = np.clip(1 - np.abs(dd - edge * 0.96) / 6.0, 0, 1) * (n > 0.36)
        crack = np.clip(1 - np.abs(((n * 9.0) % 1.0) - 0.5) * 9.0, 0, 1) * np.clip((edge * 0.9 - dd) / 8.0, 0, 1)
        ember = np.maximum(ember, np.maximum(ring, crack * 0.8))
        smold = np.exp(-(dd / (edge * 0.75)) ** 2) * 0.35
        glow = np.maximum(glow, smold)
        # soot streak up
        for j in range(5):
            a = rng.uniform(-0.5, 0.5)
            L_ = rng.uniform(r * 1.2, r * 2.6)
            for t in np.linspace(0, 1, 28):
                cx = x + a * t * L_ * 0.5 + rng.randn() * 0.5
                cy = y - r * 0.3 - t * L_
                soot = np.maximum(soot, np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (5 + 6 * (1 - t)) ** 2))) * (1 - t) * 0.8)
    soot = C.blur(soot, 1.2)
    img = img * (1 - 0.88 * soot[..., None] * k) + np.array([0.004, 0.003, 0.008], np.float32) * soot[..., None] * 0.88 * k
    emb_c = np.array([1.0, 0.28, 0.05], np.float32)
    img = img + emb_c[None, None] * (ember * 1.6 * k)[..., None] + emb_c[None, None] * (C.blur(ember, 5) * 2.2 * k)[..., None] + emb_c[None, None] * (glow * 0.6 * k)[..., None]
    return img
