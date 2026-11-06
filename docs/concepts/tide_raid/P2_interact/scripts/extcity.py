"""Extended city for non-16:9 screens: REAL city, not a mirror. The P2 graded city (1920x1080, camera zoom 1.5 about raw px (722,500))
is the exact centre; outside it the raw Godot plate (plates/city_noraid_nonet.png, 1920x1080) supplies the real streets and
buildings, re-graded by a colour map FITTED to the P2 grade on the overlap (quadratic RGB regression), with a normalised-convolution
low-frequency correction so the seam disappears. Weak point: the side pixels are an approximation of the P2 grade (no warmth field,
signs, wet reflections); the Godot build renders the real thing."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

RAW = 'D:/rc_scratch/tide_concepts/plates/city_noraid_nonet.png'
P2C = 'D:/rc_scratch/tide_concepts/p2_base/city_default.png'
CEN = (722.0, 500.0)
ZOOM = 1.5
_C = {}


def raw_img():
    if 'raw' not in _C:
        _C['raw'] = Image.open(RAW).convert('RGB')
    return _C['raw']


def p2_img():
    if 'p2' not in _C:
        _C['p2'] = np.asarray(Image.open(P2C).convert('RGB'), np.float32) / 255
    return _C['p2']


def window(cx, cy, zoom, w, h):
    """raw plate resampled into a w x h window centred on raw px (cx, cy) at `zoom` (float RGB 0..1)."""
    x0, y0 = cx - w / 2 / zoom, cy - h / 2 / zoom
    assert x0 >= -1 and y0 >= -1 and x0 + w / zoom <= 1921 and y0 + h / zoom <= 1081, (x0, y0)
    im = raw_img().resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + w / zoom, y0 + h / zoom))
    im = im.filter(ImageFilter.UnsharpMask(1.4, 60, 2))
    return np.asarray(im, np.float32) / 255


def _feat(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return np.stack([r, g, b, r * r, g * g, b * b, r * g, r * b, g * b, np.ones_like(r)], -1)


def fit():
    if 'M' in _C:
        return _C['M']
    src = window(CEN[0], CEN[1], ZOOM, 1920, 1080)
    dst = p2_img()
    rng = np.random.RandomState(1)
    idx = rng.randint(0, 1920 * 1080, 300000)
    F = _feat(src).reshape(-1, 10)[idx]
    D = dst.reshape(-1, 3)[idx]
    M = np.linalg.lstsq(F, D, rcond=None)[0]
    _C['M'] = M
    return M


def regrade(a):
    return np.clip(_feat(a) @ fit(), 0, 1).astype(np.float32)


def blur(a, s):
    return np.stack([ndi.gaussian_filter(a[..., i], s, mode='nearest') for i in range(a.shape[2])], -1)


def extended(cx, cy, zoom, w, h, feather=60):
    """the P2 city placed into a w x h window (centre raw px (cx, cy), `zoom`), real raw city outside it."""
    ap = regrade(window(cx, cy, zoom, w, h))
    # P2 city resampled into this window: P2 screen p <-> raw r=(p-(960,540))/1.5+CEN ; window s=(r-c)*zoom+(w,h)/2
    s = zoom / ZOOM
    ox = (w / 2) - (cx - CEN[0]) * zoom - 960 * s
    oy = (h / 2) - (cy - CEN[1]) * zoom - 540 * s
    p2 = Image.fromarray((p2_img() * 255 + .5).astype(np.uint8))
    sw, sh = int(round(1920 * s)), int(round(1080 * s))
    p2s = np.asarray(p2.resize((sw, sh), Image.LANCZOS), np.float32) / 255
    ex = np.zeros((h, w, 3), np.float32)
    mk = np.zeros((h, w), np.float32)
    X0, Y0 = int(round(ox)), int(round(oy))
    dx0, dy0 = max(X0, 0), max(Y0, 0)
    dx1, dy1 = min(X0 + sw, w), min(Y0 + sh, h)
    ex[dy0:dy1, dx0:dx1] = p2s[dy0 - Y0:dy1 - Y0, dx0 - X0:dx1 - X0]
    mk[dy0:dy1, dx0:dx1] = 1.0
    # inner mask: eroded by the feather so the seam sits inside the exact image
    mi = ndi.uniform_filter(mk, 3)
    dist = ndi.distance_transform_edt(mk > .5)
    m = np.clip((dist - 4) / feather, 0, 1)
    # low-frequency correction (normalised convolution) so approx matches exact at the seam and relaxes outward
    num = blur((ex - ap) * m[..., None], 50)
    den = blur(m[..., None] * np.ones((1, 1, 1), np.float32), 50) + 1e-4
    corr = num / den
    far = np.clip(1 - ndi.distance_transform_edt(mk < .5) / 260.0, 0, 1)[..., None]
    base = np.clip(ap + corr * far, 0, 1)
    return (base * (1 - m[..., None]) + ex * m[..., None]).astype(np.float32), (X0, Y0, sw, sh)
