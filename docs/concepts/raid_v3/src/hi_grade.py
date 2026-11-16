"""hi_grade: the tide P3 city grade (make_albedo4k.py = p2_grade.grade_city + p2_signs + wet_reflect + haze + tone), ported to
the raid v3 high-resolution capture (city_hi/capture: the same camera direction, centred on the raid window, 3840x2160).

    python hi_grade.py            -> city_hi/city_albedo_hi.png (3840x2160 sRGB), city_hi/hi_frame.json, city_hi/recon_hi.npz

Read-only on tide_concepts.  Everything the P3 grade does in SCREEN space (the warm / cool district field, the water streak noise,
the hero light, the wet-street ripple noise, the haze noise and depth normalisation, the choice of sign walls) is evaluated in the
P3 frame's coordinates (1920x1080 px of city_default), so the hi plate carries the same districts, signs and hero light as
city_albedo4k.png.  Blur radii and morphology are given in those 1x px and scaled by K = hi px per 1x px (the P3 4k grade used
K = 2).  World-space parts (lamp lattice, sign pictograms) are unchanged.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

TC = 'D:/rc_scratch/tide_concepts/p3_work/'
HI = 'D:/rc_scratch/raid_v3/city_hi/'
CAP = HI + 'capture/'
P3S = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts'
RIGHT = np.array([0.707107, 0.0, -0.707107])
UP = np.array([-0.454519, 0.766044, -0.454519])
BACK = np.array([0.541675, 0.642788, 0.541675])
FWD = -BACK
LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)
W1, H1 = 1920, 1080                       # the P3 1x frame (city_default)
DETAIL = '--no-detail' not in sys.argv     # set 6 city detail on by default


def log(*a):
    print(*a, flush=True)


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4).astype(np.float32)


def srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055).astype(np.float32)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ frames
OLDC = json.load(open(TC + 'depth30/capture.json'))['camera']
NEWC = json.load(open(CAP + 'capture.json'))['camera']
O_OLD, SZ_OLD = np.array(OLDC['position'], float), float(OLDC['size'])
O_NEW, SZ_NEW = np.array(NEWC['position'], float), float(NEWC['size'])
NW, NH = json.load(open(CAP + 'capture.json'))['resolution']
K = (NW / SZ_NEW) / (W1 / SZ_OLD)          # hi px per P3 1x px


def old_px(p):
    """world -> P3 1x frame px (keep-width ortho, size = frame width in BU)"""
    d = np.asarray(p, float) - O_OLD
    return d @ RIGHT / SZ_OLD * W1 + W1 / 2, H1 / 2 - d @ UP / SZ_OLD * W1


CX0, CY0 = old_px(O_NEW)                   # the hi frame's centre on the P3 1x frame
_jj, _ii = np.mgrid[0:NH, 0:NW].astype(np.float32)
OX = (CX0 + (_ii + 0.5 - NW / 2) / K).astype(np.float32)    # every hi pixel's P3 1x coordinate
OY = (CY0 + (_jj + 0.5 - NH / 2) / K).astype(np.float32)
del _ii, _jj


def at_old(field, order=1):
    """sample a P3 1x-frame field (H1, W1) at every hi pixel"""
    return ndi.map_coordinates(field, [OY - 0.5, OX - 0.5], order=order, mode='nearest').astype(np.float32)


def blur(a, s):
    """gaussian blur; sigma in P3 1x px"""
    s = tuple(v * K for v in s) if isinstance(s, (tuple, list)) else s * K
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s, mode='nearest') for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s, mode='nearest')


def noise2_1x(seed, sc):
    """p1_comp.noise2 on the 1x frame (the same random grid at every scale)"""
    rng = np.random.RandomState(seed)
    g = rng.rand(H1 // sc + 3, W1 // sc + 3).astype(np.float32)
    return ndi.zoom(g, sc, order=3)[:H1, :W1]


def fbm_1x(seed):
    n = noise2_1x(seed, 128) * .5 + noise2_1x(seed + 1, 48) * .3 + noise2_1x(seed + 2, 16) * .2
    return (n - n.min()) / (n.max() - n.min())


def _hsv(a):
    mx = a.max(-1); mn = a.min(-1); d = mx - mn
    m = d > 1e-6
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-6)
    hr = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4))
    h = np.where(m, hr * 60, 0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


# ------------------------------------------------------------------ recon + geo (recon.py, p2_geo.py)
def recon():
    rg = np.asarray(Image.open(CAP + 'depth20_rg.png'))[..., :2].astype(np.int64)
    dep = (rg[..., 0] * 256 + rg[..., 1]) / 20.0
    idm = np.asarray(Image.open(CAP + 'id.png'))[..., 0]
    u = (np.arange(NW) + 0.5) / NW - 0.5
    v = 0.5 - (np.arange(NH) + 0.5) / NH
    w_bu, h_bu = SZ_NEW, SZ_NEW * NH / NW
    P = (O_NEW[None, None, :] + RIGHT[None, None, :] * (u[None, :, None] * w_bu) + UP[None, None, :] * (v[:, None, None] * h_bu)
         + FWD[None, None, :] * dep[..., None]).astype(np.float32)
    g = idm == 4
    log('recon: depth %.1f..%.1f  ground y mean %.3f std %.3f' % (dep.min(), dep.max(), P[..., 1][g].mean(), P[..., 1][g].std()))
    return P, idm.astype(np.uint8), dep.astype(np.float32)


def geo_of(P, idm, ground):
    hag = P[..., 1] - ground(P[..., 0], P[..., 2]).astype(np.float32)
    Ps = np.stack([ndi.gaussian_filter(P[..., i], 0.8 * K) for i in range(3)], -1)
    dx = np.gradient(Ps, axis=1); dy = np.gradient(Ps, axis=0)
    n = np.cross(dx, dy)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    s = np.sign((n * BACK).sum(-1, keepdims=True)); s[s == 0] = 1
    return dict(hag=hag.astype(np.float32), n=(n * s).astype(np.float32), idm=idm)


# ------------------------------------------------------------------ grade (p2_grade.grade_city, PAR defaults, no route / corridor)
HERO = (1428.0, 640.0)
PAR = dict(sat=1.5, dim=0.95, contrast=1.1)


def warmth():
    f = (fbm_1x(11) - .5) * 2.4
    yy, xx = np.mgrid[0:H1, 0:W1].astype(np.float32)
    bias = 0.55 * (yy / H1 - .5) - 0.25 * (xx / W1 - .5)
    return at_old(np.clip(0.5 + f * 0.55 + bias, 0, 1).astype(np.float32))


def street_mask(geo, a):
    idm = geo['idm']; hag = geo['hag']
    h, s, v = _hsv(a)
    it = max(1, int(round(K)))
    green = (np.abs(h - 120) < 50) & (s > .22)
    green = ndi.binary_dilation(ndi.binary_opening(green, iterations=it), iterations=2 * it)
    park = blur(green.astype(np.float32), 6) > .25
    return (idm == 4) & (np.abs(hag) < 1.2) & ~park, park


def lamp_field(P, st):
    X = P[..., 0]; Z = P[..., 2]
    cell = 9.0
    ix = np.floor(X / cell); iz = np.floor(Z / cell)
    rh = lambda a, b: np.mod(np.sin(a * 127.1 + b * 311.7) * 43758.5453, 1.0)
    out = np.zeros(X.shape, np.float32)
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            cx = ix + dx; cz = iz + dz
            px = (cx + 0.2 + 0.6 * rh(cx, cz)) * cell
            pz = (cz + 0.2 + 0.6 * rh(cz, cx + 7)) * cell
            on = (rh(cx + 3, cz + 5) > 0.72)
            d2 = ((X - px) ** 2 + (Z - pz) ** 2)
            out = np.maximum(out, np.exp(-d2 / (2 * 1.15 ** 2)) * on)
    return (out * st).astype(np.float32)


def grade_city(Plin, geo, P):
    a = srgb(Plin)
    lum = (a * LUMW).sum(-1, keepdims=True)
    a = lum + (a - lum) * PAR['sat']
    a = np.clip(a, 0, 1) ** PAR['contrast'] * PAR['dim']
    wm = warmth()
    idm = geo['idm']
    st, park = street_mask(geo, np.clip(a, 0, 1))
    lum = (a * LUMW).sum(-1)
    loc = lum - blur(lum, 5)
    lite = np.clip((loc - 0.03) * 7, 0, 1) * (idm != 7)
    hh, ss, vv = _hsv(np.clip(a, 0, 1))
    pink = ((hh > 270) & (hh < 340) & (ss > .12)).astype(np.float32)
    warm_t = np.array([1.22, 0.94, 0.74], np.float32); cool_t = np.array([0.72, 1.04, 1.14], np.float32)
    body = a * (cool_t * (1 - wm[..., None]) + warm_t * wm[..., None])
    lift_c = np.array([0.004, 0.022, 0.040], np.float32); lift_w = np.array([0.040, 0.018, 0.012], np.float32)
    body = body + (lift_c * (1 - wm[..., None]) + lift_w * wm[..., None]) * (1 - lum[..., None]) * 1.2
    ws = np.array((1.0, 0.56, 0.2), np.float32); cc = np.array((0.25, 0.85, 1.0), np.float32)
    lcol = ws * wm[..., None] + cc * (1 - wm[..., None])
    mixk = np.clip(lite * (0.72 + 0.28 * pink), 0, 1)[..., None]
    lights = lcol * (0.5 + 1.1 * vv[..., None])
    a2 = body * (1 - mixk) + lights * mixk * 0.9 + body * mixk * 0.15
    g = lin(np.clip(a2, 0, 1))
    wmask = blur((idm == 7).astype(np.float32), 2.5)
    yy, xx = OY, OX
    sky = np.array([0.006, 0.05, 0.085], np.float32) * (1.2 - yy[..., None] / 600)
    streak = (at_old(noise2_1x(5, 24)) > .6) * np.exp(-((yy - 200) / 300) ** 2) * 0.012
    wat = sky + np.array([0.0, 0.5, 0.65], np.float32) * streak[..., None] * 0.4
    g = g * (1 - wmask[..., None]) + wat * wmask[..., None]
    lamp = lamp_field(P, st)
    lamp_s = blur(lamp, 1.2)
    pool = blur(lamp, 9)
    sod = np.array([1.0, 0.36, 0.08], np.float32)
    g = g + (sod * (lamp_s[..., None] * 0.7 + pool[..., None] * 0.5)) * (0.1 + 0.9 * wm[..., None] ** 1.5)
    gloss = np.clip(blur(st.astype(np.float32), 1.5), 0, 1)
    g = g + gloss[..., None] * (np.array([0.012, 0.018, 0.030], np.float32) * (1 - wm[..., None]) + np.array([0.030, 0.014, 0.006], np.float32) * wm[..., None])
    d = np.hypot(xx - HERO[0], (yy - HERO[1]) * 1.4)
    herok = np.exp(-(d / 120) ** 2)
    bld = (idm == 2).astype(np.float32)
    g = g * (1 + 0.9 * herok[..., None] * bld[..., None]) + np.array([.9, .35, .1], np.float32)[None, None] * (0.12 * herok * bld)[..., None]
    emis = g * mixk + sod * (lamp_s[..., None] * 1.2)
    return dict(img=g.astype(np.float32), emis=emis.astype(np.float32), wet=st)


def wet_reflect(emis, st, k=1.0, decay=0.93, sx=0.8):
    E = emis.astype(np.float32)
    R = np.zeros_like(E)
    dec = decay ** (1.0 / K)
    for y in range(1, E.shape[0]):
        R[y] = np.maximum(E[y] * 0.6, R[y - 1] * dec)
    R = np.stack([ndi.gaussian_filter(R[..., i], (1.2 * K, sx * K)) for i in range(3)], -1)
    rn = np.random.RandomState(4).rand(1080, 1920).astype(np.float32)
    rip = at_old(0.55 + 0.9 * ndi.gaussian_filter(rn, (0.6, 5)))
    rip = np.clip((rip - .45) * 2.2, 0.15, 1.5)
    m = blur(st.astype(np.float32), 0.8)
    return R * (m * rip * k)[..., None]


# ------------------------------------------------------------------ signs (p2_signs): walls chosen on the P3 4k frame, drawn here in world (u, v)
SOD = np.array([1.0, 0.42, 0.10], np.float32)
ICE = np.array([0.80, 0.93, 1.0], np.float32)
JADE = np.array([0.12, 0.85, 0.62], np.float32)
ROSE = np.array([1.0, 0.30, 0.22], np.float32)
COLS = [SOD, ICE, SOD, JADE, ICE, ROSE]


def p3_walls(n_signs=15):
    """p2_signs.find_walls + the choice, run on the P3 4k geometry (geo30 / recon30, read-only), so the same walls carry signs"""
    S = 2
    geo = np.load(TC + 'geo30.npz')
    n = geo['n'].astype(np.float32); idm = geo['idm']; hag = geo['hag']
    P = np.load(TC + 'recon30.npz')['P']
    out = []
    for kind, comp, uax in (('Z', 2, 0), ('X', 0, 2)):
        m = (n[..., comp] > 0.85) & (idm == 2) & (hag > 4)
        m = ndi.binary_opening(m, iterations=S)
        lab, nl = ndi.label(m)
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            mm = lab[sl] == i
            area = int(mm.sum())
            if area < 700 * S * S:
                continue
            c = P[sl][..., comp][mm]
            if c.std() > 0.5:
                continue
            u = P[sl][..., uax][mm]; v = P[sl][..., 1][mm]
            if u.max() - u.min() < 4.5 or v.max() - v.min() < 12.0:
                continue
            cy, cx = ndi.center_of_mass(mm)
            out.append(dict(kind=kind, comp=comp, uax=uax, plane=float(np.median(c)), u0=float(u.min()), u1=float(u.max()),
                            v0=float(v.min()), v1=float(v.max()), area=area / (S * S), cx=float(cx + sl[1].start) / S, cy=float(cy + sl[0].start) / S))
    out = [w for w in out if not (w['cx'] > 1300 and w['cy'] < 700) and w['cy'] > 60]
    out.sort(key=lambda w: -(w['area'] * min(w['v1'] - w['v0'], 40)))
    chosen = []
    for w in out:
        if all(np.hypot(w['cx'] - c['cx'], w['cy'] - c['cy']) > 150 for c in chosen):
            chosen.append(w)
        if len(chosen) >= n_signs:
            break
    return chosen


def _sign_pattern(u, v, typ, seed):
    on = np.zeros_like(u)
    if typ == 0:
        for k in range(4):
            y0 = 0.1 + k * 0.22
            on = np.maximum(on, ((v > y0) & (v < y0 + 0.11) & (u > 0.18) & (u < 0.9 - 0.12 * ((k * 7 + seed) % 4))).astype(np.float32))
        on = np.maximum(on, ((np.hypot((u - 0.08) * 1.0, (v - 0.5) * 0.45) < 0.07)).astype(np.float32))
    elif typ == 1:
        r = np.hypot((u - 0.5) * 1.0, (v - 0.5) * 0.5)
        on = ((r > 0.30) & (r < 0.40)).astype(np.float32)
        on = np.maximum(on, ((np.abs(u - 0.5) < 0.04) & (np.abs(v - 0.5) < 0.40)).astype(np.float32))
        on = np.maximum(on, ((np.abs(v - 0.5) < 0.07) & (np.abs(u - 0.5) < 0.25)).astype(np.float32))
    elif typ == 2:
        for k in range(3):
            c = 0.2 + k * 0.28
            vv = np.abs(u - 0.5) * 0.6
            on = np.maximum(on, ((np.abs(v - (c + vv)) < 0.06) & (np.abs(u - 0.5) < 0.42)).astype(np.float32))
    else:
        on = ((u > 0.30) & (u < 0.70) & ((v * 7) % 1.0 < 0.72)).astype(np.float32)
    return on


def signs(geo, P, chosen, seed=3):
    emis = np.zeros(P.shape, np.float32)
    body = np.zeros(P.shape[:2], np.float32)
    HX, HY = 1300.0, 760.0
    hero_i = int(np.argmin([np.hypot(w['cx'] - HX, w['cy'] - HY) for w in chosen])) if chosen else -1
    n = geo['n']; idm = geo['idm']; hag = geo['hag']
    used = 0
    for i, w in enumerate(chosen):
        x0, y0 = w['cx'], w['cy']
        if not (OX.min() - 200 < x0 < OX.max() + 200 and OY.min() - 200 < y0 < OY.max() + 200):
            continue
        uu = P[..., w['uax']]; vv = P[..., 1]
        wall = ((n[..., w['comp']] > 0.85) & (idm == 2) & (hag > 4) & (np.abs(P[..., w['comp']] - w['plane']) < 0.6)
                & (uu > w['u0'] - 0.3) & (uu < w['u1'] + 0.3) & (vv > w['v0'] - 0.3) & (vv < w['v1'] + 0.3))
        if not wall.any():
            continue
        used += 1
        col = COLS[(i * 5 + seed) % len(COLS)]
        typ = (i + seed) % 4
        wu = w['u1'] - w['u0']; wv = w['v1'] - w['v0']
        sw = min(wu * 0.85, 13.0) if typ != 3 else min(wu * 0.35, 3.2)
        sh = min(wv * 0.36, 14.0) if typ != 3 else min(wv * 0.62, 30.0)
        uc = (w['u0'] + w['u1']) / 2; vc = w['v0'] + wv * (0.62 if typ != 3 else 0.5)
        m = wall & (np.abs(uu - uc) < sw / 2) & (np.abs(vv - vc) < sh / 2)
        if i == hero_i:
            fac = 0.22 + 0.16 * (((uu * 1.7) % 1.0 < 0.5) & ((vv * 0.6) % 1.0 < 0.55))
            emis += (SOD * 0.9)[None, None] * (wall * fac)[..., None]
        uloc = np.clip((uu - (uc - sw / 2)) / sw, 0, 1); vloc = np.clip(1 - (vv - (vc - sh / 2)) / sh, 0, 1)
        pat = _sign_pattern(uloc, vloc, typ, i)
        body = np.maximum(body, m.astype(np.float32))
        emis += col[None, None] * (m * (0.12 + 2.6 * pat))[..., None]
    log('signs: %d of %d P3 sign walls fall in the hi frame' % (used, len(chosen)))
    return dict(emis=emis, body=body)


# ------------------------------------------------------------------ haze + tone (p1_comp)
def haze(img, dep, strength=0.18, col=(0.035, 0.05, 0.13), seed=3):
    d0 = np.load(TC + 'recon30.npz')['dep']
    lo, hi = float(d0.min()), float(d0.max())          # the P3 frame's depth range, so the haze matches the 4k plate
    far = smoothstep(0.0, 1.0, np.clip((dep - lo) / (hi - lo + 1e-6), 0, 1))
    hz = (far ** 1.3) * strength * (0.65 + 0.7 * at_old(fbm_1x(seed)))
    return img * (1 - hz[..., None] * 0.55) + np.array(col, np.float32) * hz[..., None] * 1.1


def tone(x, exposure=1.0):
    x = np.maximum(x * exposure, 0)
    a = 2.51; b = 0.03; c = 2.43; d = 0.59; e = 0.14
    y = (x * (a * x + b)) / (x * (c * x + d) + e)
    return srgb(np.clip(y, 0, 1))


def main():
    log('hi frame %dx%d, K = %.4f hi px per P3 1x px, centre on city_default (%.2f, %.2f)' % (NW, NH, K, CX0, CY0))
    sys.path.insert(0, P3S)
    import p1lib as L                                   # read-only: the terrain G (hf15.npz) for height above ground
    P, idm, dep = recon()
    np.savez_compressed(HI + 'recon_hi.npz', P=P.astype(np.float16), idm=idm, dep=dep.astype(np.float16))
    geo = geo_of(P, idm, L.ground)
    plate = lin(np.asarray(Image.open(CAP + 'window_nonet.png').convert('RGB'), np.float32) / 255)
    log('plate', plate.shape)
    chosen = p3_walls()
    sg = signs(geo, P, chosen)
    r = grade_city(plate, geo, P)
    img = r['img'] * (1 - sg['body'][..., None] * .7) + sg['emis']
    demis = 0.0
    if DETAIL:                                          # set 6: windows, shopfronts, blade signs, street lamps (hi_detail.py)
        import hi_detail as D
        fr = D.Frame(O_NEW, SZ_NEW, NW, NH, RIGHT, UP, FWD)
        gv0 = (np.abs(geo['hag']) < 1.6) & (idm != 7)
        img, demis, _ = D.detail(img, P, geo, dep, r['wet'], gv0, fr, log)
    refl = wet_reflect(r['emis'] + sg['emis'] * .5 + demis * .5, r['wet'])
    out = haze(img + refl * .9, dep, strength=.18)
    Image.fromarray((tone(out) * 255 + .5).astype(np.uint8)).save(HI + 'city_albedo_hi.png')
    gv = (np.abs(geo['hag']) < 1.6) & (idm != 7)
    Image.fromarray((gv * 255).astype(np.uint8)).save(HI + 'ground_vis_hi.png')
    json.dump(dict(K=K, cx0=CX0, cy0=CY0, w=NW, h=NH, size=SZ_NEW, position=list(O_NEW), old_size=SZ_OLD, old_position=list(O_OLD)),
              open(HI + 'hi_frame.json', 'w'), indent=1)
    log('ok', HI + 'city_albedo_hi.png')


if __name__ == '__main__':
    main()
