"""P2 city grade (punch #2): break the single violet band. Warm sodium districts against cool teal, street lamp pools, wet-street gloss,
water as a cool mirror, recoloured window / roof lights (the pink confetti that fought the N beam is moved to warm / teal), one hero light.
grade_city(P_lin, geo) -> dict(img=linear graded city, emis=linear emissive layer used for reflections, wet=wet-street mask)"""
import numpy as np
from scipy import ndimage as ndi
import p1lib as L
import p1_comp as C

W, H = C.W, C.H
S = C.S
LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)
# hero light (screen px of the 1x plate): a tall lit tower south of the route, away from HOME and the HQ
HERO = (1428.0, 640.0)
PAR = dict(sat=1.5, dim=0.95, contrast=1.1, off_route=0.14, warm_sod=(1.0, 0.56, 0.2), cool_cyan=(0.25, 0.85, 1.0))


def _hsv(a):
    mx = a.max(-1); mn = a.min(-1); d = mx - mn
    m = d > 1e-6
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-6)
    hr = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4))
    h = np.where(m, hr * 60, 0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def warmth_field(shape=(H, W), seed=11):
    """0 = cool teal district, 1 = warm sodium district. Large smooth blobs plus a south / left bias (the lived-in downtown is warm)."""
    f = C.fbm(seed, shape)
    f = (f - .5) * 2.4
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bias = 0.55 * (yy / H - .5) - 0.25 * (xx / W - .5)
    return np.clip(0.5 + f * 0.55 + bias, 0, 1).astype(np.float32)


def street_mask(geo, beauty_srgb):
    idm = geo['idm']; hag = geo['hag']
    h, s, v = _hsv(beauty_srgb)
    green = (np.abs(h - 120) < 50) & (s > .22)
    green = ndi.binary_dilation(ndi.binary_opening(green, iterations=S), iterations=2 * S)
    park = C.blur(green.astype(np.float32), 6) > .25
    st = (idm == 4) & (np.abs(hag) < 1.2) & ~park
    return st, park


def lamp_field(st):
    """sodium lamp pools on street pixels: jittered world-space lattice (every ~9 BU)."""
    z = np.load(L.WORK + C.REC)
    P = z['P']
    X = P[..., 0]; Z = P[..., 2]
    cell = 9.0
    ix = np.floor(X / cell); iz = np.floor(Z / cell)
    rh = lambda a, b: np.mod(np.sin(a * 127.1 + b * 311.7) * 43758.5453, 1.0)
    out = np.zeros((H, W), np.float32)
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            cx = ix + dx; cz = iz + dz
            px = (cx + 0.2 + 0.6 * rh(cx, cz)) * cell
            pz = (cz + 0.2 + 0.6 * rh(cz, cx + 7)) * cell
            on = (rh(cx + 3, cz + 5) > 0.72)
            d2 = ((X - px) ** 2 + (Z - pz) ** 2)
            out = np.maximum(out, np.exp(-d2 / (2 * 1.15 ** 2)) * on)
    return (out * st).astype(np.float32)


def grade_city(P, geo, route_dist=None, corridor=None, par=None, lightk=None):
    par = dict(PAR, **(par or {}))
    C.sys_path_fix()
    a = C.srgb(P)
    lum = (a * LUMW).sum(-1, keepdims=True)
    a = lum + (a - lum) * par['sat']
    a = np.clip(a, 0, 1) ** par['contrast'] * par['dim']
    wm = warmth_field()
    idm = geo['idm']
    st, park = street_mask(geo, np.clip(a, 0, 1))
    lum = (a * LUMW).sum(-1)
    loc = lum - C.blur(lum, 5)
    lite = np.clip((loc - 0.03) * 7, 0, 1) * (idm != 7)
    hh, ss, vv = _hsv(np.clip(a, 0, 1))
    pink = ((hh > 270) & (hh < 340) & (ss > .12)).astype(np.float32)
    warm_t = np.array([1.22, 0.94, 0.74], np.float32); cool_t = np.array([0.72, 1.04, 1.14], np.float32)
    tint = cool_t * (1 - wm[..., None]) + warm_t * wm[..., None]
    body = a * tint
    lift_c = np.array([0.004, 0.022, 0.040], np.float32); lift_w = np.array([0.040, 0.018, 0.012], np.float32)
    body = body + (lift_c * (1 - wm[..., None]) + lift_w * wm[..., None]) * (1 - lum[..., None]) * 1.2
    ws = np.array(par['warm_sod'], np.float32); cc = np.array(par['cool_cyan'], np.float32)
    lcol = ws * wm[..., None] + cc * (1 - wm[..., None])
    mixk = np.clip(lite * (0.72 + 0.28 * pink), 0, 1)[..., None]
    if lightk is not None:
        mixk = mixk * lightk[..., None]
    lights = lcol * (0.5 + 1.1 * vv[..., None])
    a2 = body * (1 - mixk) + lights * mixk * 0.9 + body * mixk * 0.15
    g = C.lin(np.clip(a2, 0, 1))
    # water: deep teal mirror with a cool sky gradient
    wmask = C.blur((idm == 7).astype(np.float32), 2.5)
    yy, xx = (np.mgrid[0:H, 0:W].astype(np.float32) / S)
    sky = np.array([0.006, 0.05, 0.085], np.float32) * (1.2 - yy[..., None] / 600)
    streak = (C.noise2(5, 24) > .6) * np.exp(-((yy - 200) / 300) ** 2) * 0.012
    wat = sky + np.array([0.0, 0.5, 0.65], np.float32) * streak[..., None] * 0.4
    g = g * (1 - wmask[..., None]) + wat * wmask[..., None]
    # street: sodium lamp pools + wet gloss
    lamp = lamp_field(st) * (1.0 if lightk is None else lightk)
    lamp_s = C.blur(lamp, 1.2)
    pool = C.blur(lamp, 9)
    sod = np.array([1.0, 0.36, 0.08], np.float32)
    g = g + (sod * (lamp_s[..., None] * 0.7 + pool[..., None] * 0.5)) * (0.1 + 0.9 * wm[..., None] ** 1.5)
    gloss = np.clip(C.blur(st.astype(np.float32), 1.5), 0, 1)
    g = g + gloss[..., None] * (np.array([0.012, 0.018, 0.030], np.float32) * (1 - wm[..., None]) + np.array([0.030, 0.014, 0.006], np.float32) * wm[..., None])
    # hero light
    d = np.hypot(xx - HERO[0], (yy - HERO[1]) * 1.4)
    herok = np.exp(-(d / 120) ** 2)
    bld = (idm == 2).astype(np.float32)
    g = g * (1 + 0.9 * herok[..., None] * bld[..., None]) + np.array([.9, .35, .1], np.float32)[None, None] * (0.12 * herok * bld)[..., None]
    emis = g * mixk + sod * (lamp_s[..., None] * 1.2)
    if route_dist is not None:
        f = 1 - par['off_route'] * C.smoothstep(90, 420, route_dist)
        g = g * (f[..., None] * (1 - mixk) + mixk)
    if corridor is not None:
        g = g * (1 - 0.22 * corridor[..., None])
    return dict(img=g.astype(np.float32), emis=emis.astype(np.float32), wet=st, wm=wm, park=park, lite=lite)


def wet_reflect(emis, st, k=1.0, decay=0.93, sx=0.8):
    """wet street: downward smear of the emissive layer onto street pixels (a vertical mirror streak), broken by a ripple noise."""
    E = emis.astype(np.float32)
    R = np.zeros_like(E)
    dec = decay ** (1.0 / S)
    for y in range(1, H):
        R[y] = np.maximum(E[y] * 0.6, R[y - 1] * dec)
    R = np.stack([ndi.gaussian_filter(R[..., i], (1.2 * S, sx * S)) for i in range(3)], -1)
    rn = np.random.RandomState(4).rand(1080, 1920).astype(np.float32)
    if S > 1:
        rn = ndi.zoom(rn, S, order=1)
    rip = 0.55 + 0.9 * ndi.gaussian_filter(rn, (0.6 * S, 5 * S))
    rip = np.clip((rip - .45) * 2.2, 0.15, 1.5)
    m = C.blur(st.astype(np.float32), 0.8)
    return R * (m * rip * k)[..., None]
