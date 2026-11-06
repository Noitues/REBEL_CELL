"""f1_icons: the E10 slice silhouettes (twin-pod BURST, single-missile TURRET, split-heater SHIELD, bandage REPAIR) as float masks, to be re-inked by the F1 hand.
mask_for(name, px_screen, S) -> (white_mask, dark_mask)  square arrays of side int(px*S*1.3), centred"""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

_cache = {}
GL = {'BURST': 'WC2_BURST_B', 'TURRET': 'WC2_TURRET_A', 'REPAIR': 'WC2_REPAIR_P'}


def _glyph(name, px):
    import wc_tower as T
    g = T.glyph_rgba(name, px, max(2.0, px * 0.07), fill=(255, 255, 255), edge=(12, 10, 22))
    a = np.asarray(g, np.float32) / 255.0
    al = a[..., 3]
    lum = a[..., :3].mean(-1)
    white = np.clip((al - 0.5) * 4, 0, 1) * np.clip((lum - 0.55) * 6, 0, 1)
    return white


def _shield(px):
    n = int(px)
    im = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(im)
    k = px * 0.5
    c = (n / 2, n / 2)

    def P(pts):
        return [(c[0] + x * k * 2, c[1] + y * k * 2) for x, y in pts]
    outer = [(-0.46, -0.50), (0.46, -0.50), (0.46, 0.10), (0.0, 0.58), (-0.46, 0.10)]
    d.polygon(P(outer), fill=255)
    w = np.asarray(im, np.float32) / 255.0
    im2 = Image.new('L', (n, n), 0)
    ImageDraw.Draw(im2).polygon(P([(0.06, -0.38), (0.36, -0.38), (0.36, 0.06), (0.06, 0.40)]), fill=255)
    dk = np.asarray(im2, np.float32) / 255.0
    return w * (1 - dk), dk


def mask_for(name, px, S):
    key = (name, int(px), S)
    if key in _cache:
        return _cache[key]
    n = int(px * S * 1.4)
    target = px * S * 0.92
    if name == 'SHIELD':
        w, dk = _shield(int(px * S * 1.1))
    else:
        w = _glyph(GL[name], int(px * S * 1.1))
        dk = np.zeros_like(w)
    ys, xs = np.nonzero(w > 0.3)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    w = w[y0:y1, x0:x1]
    dk = dk[y0:y1, x0:x1]
    k = target / max(w.shape)
    if abs(k - 1) > 0.02:
        im = Image.fromarray((w * 255).astype(np.uint8)).resize((max(1, int(w.shape[1] * k)), max(1, int(w.shape[0] * k))), Image.LANCZOS)
        w = np.asarray(im, np.float32) / 255.0
        im = Image.fromarray((dk * 255).astype(np.uint8)).resize((w.shape[1], w.shape[0]), Image.LANCZOS)
        dk = np.asarray(im, np.float32) / 255.0
    out_w = np.zeros((n, n), np.float32)
    out_d = np.zeros((n, n), np.float32)
    h, ww = w.shape
    oy, ox = (n - h) // 2, (n - ww) // 2
    out_w[oy:oy + h, ox:ox + ww] = w
    out_d[oy:oy + h, ox:ox + ww] = dk
    _cache[key] = (out_w, out_d)
    return _cache[key]
