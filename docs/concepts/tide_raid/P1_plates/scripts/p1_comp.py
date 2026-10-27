"""P1 compositor (numpy, linear light). Layers from Blender (.npy premultiplied linear RGBA) + the Godot plate + depth.
build(beat, cfg) -> float32 linear image (H,W,3) before UI; tone() -> sRGB 8-bit."""
import os, json, math, numpy as np
from PIL import Image
from scipy import ndimage as ndi
import p1lib as L

W, H = 1920, 1080
WORK = L.WORK
LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4).astype(np.float32)


def srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055).astype(np.float32)


def load_plate():
    return lin(np.asarray(Image.open(WORK + 'depth15/window_nonet.png').convert('RGB'), np.float32) / 255)


_dep = None


def depth_norm():
    global _dep
    if _dep is None:
        z = np.load(WORK + 'recon15.npz')
        d = z['dep'].astype(np.float32)
        _dep = (d - d.min()) / (d.max() - d.min() + 1e-6)
    return _dep


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def blur(a, s):
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s, mode='nearest') for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s, mode='nearest')


def noise2(seed, sc, shape=(H, W)):
    rng = np.random.RandomState(seed)
    g = rng.rand(shape[0] // sc + 3, shape[1] // sc + 3).astype(np.float32)
    z = ndi.zoom(g, sc, order=3)[:shape[0], :shape[1]]
    return z


def fbm(seed, shape=(H, W)):
    n = noise2(seed, 128, shape) * .5 + noise2(seed + 1, 48, shape) * .3 + noise2(seed + 2, 16, shape) * .2
    return (n - n.min()) / (n.max() - n.min())


def route_distance(polys_px, shape=(H, W)):
    """screen distance (px) to the nearest route polyline (de-emphasis off the route)."""
    m = np.ones(shape, bool)
    from PIL import ImageDraw
    im = Image.new('L', (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(im)
    for p in polys_px:
        d.line([tuple(q) for q in p], fill=255, width=3)
    m = np.asarray(im) > 0
    if not m.any():
        return np.full(shape, 999.0, np.float32)
    return ndi.distance_transform_edt(~m).astype(np.float32)


def softcap(x, cap, knee=0.6):
    """compress highlights above cap*knee smoothly toward cap"""
    t = cap * knee
    over = np.maximum(x - t, 0)
    return np.where(x > t, t + (cap - t) * (1 - np.exp(-over / max(cap - t, 1e-6))), x)


def grade_plate(P, route_dist=None, dim=0.92, sat=1.45, off_route=0.28, corridor=None, cap=None, contrast=1.15):
    """jack-in WORLD GRADE, vivid night (art-pass ruling: keep the night but vivid): saturation up, mids held, indigo shadows, windows/street
    lights/park greens kept; window yellow-orange pulled toward warm white so the ONLY signal yellow is the E beam. Off-route city dims only PARTLY."""
    sys_path_fix()
    import lib as PL
    a = srgb(P)
    lum = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    a = lum + (a - lum) * sat
    a = np.clip(a, 0, 1) ** contrast * dim + 0.010
    a[..., 2] += (1 - lum[..., 0]) * 0.022
    h, s_, v = PL._hsv(np.clip(a, 0, 1))
    band = np.clip(1 - np.abs(h - 42) / 34, 0, 1)
    s_ = s_ * (1 - .55 * band)
    a = PL._rgb(h, s_, v)
    g = lin(np.clip(a, 0, 1))
    if route_dist is not None:
        f = 1 - off_route * smoothstep(90, 420, route_dist)
        g = g * f[..., None]
    if corridor is not None:
        g = g * (1 - 0.22 * corridor[..., None])
    return g


_pf = [False]


def sys_path_fix():
    if not _pf[0]:
        import sys
        if L.H2 not in sys.path:
            sys.path.insert(0, L.H2)
        _pf[0] = True


def haze(img, strength=0.38, col=(0.035, 0.05, 0.13), rain=True, seed=3):
    d = depth_norm()
    far = d
    far = smoothstep(0.0, 1.0, far)
    f = fbm(seed)
    hz = (far ** 1.3) * strength * (0.65 + 0.7 * f)
    out = img * (1 - hz[..., None] * 0.55) + np.array(col, np.float32) * hz[..., None] * 1.1
    return out


def rain_layer(seed=5, density=900, slope=0.28, length=(18, 46), k=0.05):
    from PIL import ImageDraw
    rng = np.random.RandomState(seed)
    im = Image.new('L', (W * 2, H * 2), 0)
    d = ImageDraw.Draw(im)
    for _ in range(density):
        x = rng.randint(0, W * 2); y = rng.randint(0, H * 2); ln = rng.randint(*length) * 2
        d.line([(x, y), (x - ln * slope, y + ln)], fill=int(rng.randint(60, 220)), width=1 + int(rng.rand() < .3))
    im = im.resize((W, H), Image.LANCZOS)
    return (np.asarray(im, np.float32) / 255) * k


def bloom(emis, sig=(3, 9, 26, 70), wts=(0.45, 0.35, 0.28, 0.2)):
    out = np.zeros_like(emis)
    for s, w in zip(sig, wts):
        out += blur(emis, s) * w
    return out


def tone(x, exposure=1.0, white=3.0):
    """soft filmic shoulder (Reinhard-extended on luminance-preserving channels) -> sRGB float"""
    x = np.maximum(x * exposure, 0)
    a = 2.51; b = 0.03; c = 2.43; d = 0.59; e = 0.14
    y = (x * (a * x + b)) / (x * (c * x + d) + e)
    return srgb(np.clip(y, 0, 1))


def layers(beat, passes=('world_occ', 'world_ghost', 'heads_occ', 'heads_ghost', 'spill')):
    base = WORK + beat + '/b_'
    out = {}
    for p in passes:
        f = base + p + '.npy'
        if os.path.exists(f):
            out[p] = np.load(f).astype(np.float32)
    return out


def vstreak(emis, sy=34, sx=2.2, k=0.5):
    """light columns: anisotropic glow (tall) from bright vertical emitters (tower spines, flash columns) through the rain haze"""
    out = np.zeros_like(emis)
    for c in range(3):
        a = ndi.gaussian_filter(emis[..., c], (sy, sx), mode='nearest')
        out[..., c] = a
    return out * k


def hstreak(emis, sx=90, sy=2.0, k=0.35):
    """anamorphic lens streak (impact flashes)"""
    out = np.zeros_like(emis)
    for c in range(3):
        out[..., c] = ndi.gaussian_filter(emis[..., c], (sy, sx), mode='nearest')
    return out * k


def tiltshift(img, top=0.16, bot=0.14, smax=1.8):
    """very light depth-of-field: the far (top) and near (bottom) bands soften; the route band stays sharp"""
    yy = np.arange(H, dtype=np.float32)[:, None] / H
    w = np.maximum(smoothstep(top, 0.0, yy), smoothstep(1 - bot, 1.0, yy))
    b = blur(img, smax)
    return img * (1 - w[..., None]) + b * w[..., None]
