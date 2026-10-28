"""P3 look-dev additions (punch #3, the V gap): hero facades with real material, volumetric light shafts from the brightest sources, richer wet reflections.
All evaluated per pixel in wall (u, v) BU coordinates / screen space so they are native-sharp at 4K.
hero_pack(geo, P) -> dict(emis, mul, ink, rim, src)   (cached)
shafts(...) -> linear RGB additive     wet2(...) -> linear RGB additive"""
import numpy as np
from scipy import ndimage as ndi
import p1lib as L
import p1_comp as C
import p2_signs as S2

W, H = C.W, C.H
S = C.S
SOD = np.array([1.0, 0.48, 0.14], np.float32)
ICE = np.array([0.78, 0.92, 1.0], np.float32)
JADE = np.array([0.12, 0.85, 0.62], np.float32)
_cache = {}


def _h(a, b, seed=0):
    return np.mod(np.sin(a * 127.1 + b * 311.7 + seed * 74.7) * 43758.5453, 1.0)


def pick_heroes(geo, P, n=8, sep=170.0):
    """hero buildings = the biggest planar tall facades in the dense downtown (not under the Solace cage, not on the water), well separated."""
    walls = S2.find_walls(geo, P, min_w=4.5, min_h=14.0)
    walls = [w for w in walls if not (w['cx'] > 1300 and w['cy'] < 700) and w['cy'] > 120 and w['cx'] < 1750]
    walls.sort(key=lambda w: -(w['area'] * min(w['v1'] - w['v0'], 46)))
    out = []
    for w in walls:
        if all(np.hypot(w['cx'] - c['cx'], w['cy'] - c['cy']) > sep for c in out):
            out.append(w)
        if len(out) >= n:
            break
    return out


def facade_pack(heroes, P, seed=5):
    """per-hero facade material. Returns emissive (linear RGB), multiplicative darkening, ink outline, rim light, and shaft sources."""
    emis = np.zeros((H, W, 3), np.float32)
    mul = np.zeros((H, W), np.float32)
    ink = np.zeros((H, W), np.float32)
    rim = np.zeros((H, W, 3), np.float32)
    src = []
    for i, w in enumerate(heroes):
        sl = w['sl']
        m = w['mask'][sl]
        mf = ndi.gaussian_filter(m.astype(np.float32), 0.5 * S)
        uax = 0 if w['kind'] == 'Z' else 2
        u = P[sl][..., uax]; v = P[sl][..., 1]
        wu = w['u1'] - w['u0']; wv = w['v1'] - w['v0']
        fl = 2.3
        fv = (v - w['v0']) / fl
        ff = np.mod(fv, 1.0)
        slab = (ff < 0.09).astype(np.float32)                                # spandrel line between floors
        cu = np.floor((u - w["u0"]) / 1.25); cf = np.floor(fv)
        mull = (np.mod((u - w["u0"]) / 1.25, 1.0) < 0.07).astype(np.float32)   # mullions
        pane = (1 - slab) * (1 - mull)
        hh = _h(cu, cf, i + seed)
        cool = _h(cu, cf, i + 31) > 0.62
        lit = (hh > 0.80).astype(np.float32) * pane
        wcol = np.where(cool[..., None], ICE[None, None], SOD[None, None]) * (0.6 + 0.5 * _h(cu, cf, 9)[..., None])
        e = wcol * lit[..., None] * 0.30
        # glass: sky gradient + diagonal specular streaks + city-glow reflection low on the facade
        t = np.clip((v - w['v0']) / max(wv, 1.0), 0, 1)
        sky = np.array([0.020, 0.075, 0.150], np.float32) * (0.35 + 0.9 * t)[..., None]
        streak = np.exp(-((np.mod((u - w['u0']) * 0.42 + (v - w['v0']) * 0.30 + i * 1.7, 11.0) - 2.0) / 0.85) ** 2) * 0.10
        glow_low = (np.exp(-(t / 0.22) ** 2) * 0.05)[..., None] * SOD[None, None]
        e = e + (sky * pane[..., None] + (streak * pane)[..., None] * ICE[None, None] + glow_low * pane[..., None])
        # continuous light strip on every 7th floor (a real facade feature, reads as architecture at 320 px)
        strip = ((np.mod(cf, 7) == 3) & (ff > 0.40) & (ff < 0.62)).astype(np.float32)
        e = e + ICE[None, None] * (strip * 0.55)[..., None]
        # lit atrium: warm slot with mullions, lower third, off-centre
        uc = w['u0'] + wu * (0.30 + 0.4 * _h(i, 3.0))
        atr = ((np.abs(u - uc) < min(wu * 0.17, 3.2)) & (t < 0.34)).astype(np.float32)
        atr_i = atr * (0.55 + 0.45 * (np.mod((v - w['v0']) / 1.1, 1.0) > 0.12)) * (1 - 0.7 * mull)
        e = e + SOD[None, None] * (atr_i * 0.95)[..., None]
        # rooftop sign band
        top = ((v > w['v1'] - 0.055 * wv - 1.2) & (v < w['v1'] - 0.012 * wv)).astype(np.float32)
        seg = (np.mod((u - w['u0']) / 1.6, 1.0) < 0.72).astype(np.float32)
        sc = [ICE, SOD, JADE][i % 3]
        e = e + sc[None, None] * (top * seg * 2.4)[..., None]
        emis[sl] += e * mf[..., None]
        mul[sl] = np.maximum(mul[sl], mf * (0.18 + 0.38 * slab))
        # sharp ink line outside the facade mask + a corner rim light on its inside edge
        er = ndi.binary_erosion(m, iterations=max(1, S))
        edge_in = (m & ~er)
        di = ndi.binary_dilation(m, iterations=2 * S + 1) & ~m
        ink[sl] = np.maximum(ink[sl], di.astype(np.float32))
        rim[sl] += edge_in[..., None] * (ICE * 0.38 * (0.5 + 0.5 * _h(i, 1.0)))[None, None]
        ys, xs = np.nonzero(m)
        if len(ys) > 0:
            ytop = ys.min()
            xt = xs[ys < ytop + 3 * S].mean()
            src.append(dict(x=(xt + sl[1].start) / S, y=(ytop + sl[0].start) / S, col=sc, h=w['v1'] - w['v0'], idx=i))
    return dict(emis=emis, mul=mul, ink=ink, rim=rim, src=src)


def hero_pack(geo, P):
    if 'hero' not in _cache:
        hs = pick_heroes(geo, P)
        _cache['hero'] = facade_pack(hs, P)
    return _cache['hero']


def shafts(img_lin, emis_extra, home_px, hero_src, k=1.0, seed=3, length=64.0):
    """volumetric light shafts from the brightest sources: (1) every very bright point (sodium lamp, lit window, sign) smears UPWARD through the rain haze with a dust modulation,
    (2) HOME beacon column, (3) rooftop searchlight cones from hero buildings. Additive, linear."""
    E = np.maximum(img_lin + emis_extra, 0)
    lum = (E * C.LUMW).sum(-1)
    thr = np.percentile(lum[::4, ::4], 99.9)
    bright = np.clip((lum - thr) / max(thr, 1e-3), 0, 1.5)
    src = E * np.clip(bright[..., None], 0, 1)
    src = C.blur(src, 0.8)
    R = np.zeros_like(src)
    dec = (0.12) ** (1.0 / (length * S))
    for y in range(H - 2, -1, -1):
        R[y] = np.maximum(src[y] * 0.24, R[y + 1] * dec)
    rng = np.random.RandomState(seed)
    dn = ndi.gaussian_filter1d(rng.rand(W).astype(np.float32), 1.6 * S)
    dn = (dn - dn.min()) / (dn.max() - dn.min())
    mod = (0.55 + 0.9 * dn)[None, :, None]
    R = C.blur(R, 1.0) * mod
    out = R * 0.9 * k * 0.55
    yy, xx = (np.mgrid[0:H, 0:W].astype(np.float32) / S)
    if home_px is not None:
        hx, hy = home_px[0], home_px[1] - 20
        t = np.clip((hy - yy) / 420.0, 0, 1)
        wd = 18 + 40 * t
        col = np.exp(-((xx - hx) / wd) ** 2) * (1 - t) ** 1.4 * (yy < hy)
        col = col * (0.6 + 0.6 * (C.noise2(seed + 20, 26) * .7 + .3))
        out = out + np.array([1.0, 0.86, 0.66], np.float32)[None, None] * (col * 0.20 * k)[..., None]
    for j, s_ in enumerate(hero_src[:4]):
        for sgn in (-1, 1):
            ang = sgn * (0.30 + 0.10 * (j % 2))
            ln = 330.0
            ux, uy = np.sin(ang), -np.cos(ang)
            dx = xx - s_['x']; dy = yy - (s_['y'] - 4)
            along = dx * ux + dy * uy
            perp = np.abs(dx * uy - dy * ux)
            ok = (along > 0) & (along < ln)
            wdt = 3.0 + along * 0.16
            c = np.exp(-(perp / wdt) ** 2) * np.clip(1 - along / ln, 0, 1) ** 1.2 * ok
            out = out + s_['col'][None, None] * (c * 0.10 * k * (0.7 + 0.5 * C.noise2(seed + 40 + j, 30)))[..., None]
    return out.astype(np.float32)


def wet2(emis_all, wet, sky_k=1.0, k=1.0, seed=4):
    """richer wet streets: long smears of EVERY light, puddles (noise > thr) that mirror ~2x brighter with a cool sky tint, and a fresnel sheen toward the top of the frame."""
    E = emis_all.astype(np.float32)
    R = np.zeros_like(E)
    dec = 0.955 ** (1.0 / S)
    for y in range(1, H):
        R[y] = np.maximum(E[y] * 0.55, R[y - 1] * dec)
    R = np.stack([ndi.gaussian_filter(R[..., i], (1.3 * S, 0.9 * S)) for i in range(3)], -1)
    rn = np.random.RandomState(seed).rand(1080, 1920).astype(np.float32)
    if S > 1:
        rn = ndi.zoom(rn, S, order=1)
    rip = 0.5 + 0.9 * ndi.gaussian_filter(rn, (0.6 * S, 5 * S))
    rip = np.clip((rip - .42) * 2.2, 0.15, 1.6)
    pud = C.noise2(seed + 9, 22)
    pmask = C.smoothstep(0.58, 0.68, pud)
    m = C.blur(wet.astype(np.float32), 0.8)
    gain = m * (rip * (1 + 1.1 * pmask) * k)
    out = R * gain[..., None]
    yy = (np.mgrid[0:H, 0:W][0].astype(np.float32) / S) / 1080.0
    sheen = m * (pmask * 0.030 + (1 - yy) * 0.012) * sky_k
    out = out + sheen[..., None] * np.array([0.35, 0.8, 1.0], np.float32)[None, None]
    return out.astype(np.float32)
