"""Round 32 backdrop fix: the old fist-shaped red roads under REBEL_CELL become normal streets.

Works on the 2560x1440 night map (round 30 city_night_hq_v6.jpg, which already carries the latest
Meridian container fortress, the same render as hq_meridian_city.jpg). Saturated-red road pixels
inside the Cell district are re-graded to the night asphalt of the surrounding grid; their red
bloom on neighbouring facades is pulled back to neutral. Read-only on round 30.

  python scripts/defist.py     -> scratch/defist_check.png (before | after crop)
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONC = os.path.dirname(ROOT)
V6 = os.path.join(CONC, 'round30_meridian_castle', 'city_night_hq_v6.jpg')
DISTRICT = (820, 820, 1720, 1440)          # 2560 px box around the fist district
ASPHALT = np.array([30, 26, 46], np.float32)


def redness(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r - np.maximum(g, b)) / (r + 1.0)
    return np.clip((m - 0.38) / 0.25, 0, 1) * np.clip((r - 70) / 60, 0, 1)


TX, TY = 14.35, 7.17                         # one iso street step on the 2560 map (round 26 cm: 34x17 city px x Z)
OFFS = [(a, b) for a in range(-7, 8) for b in range(-7, 8) if 4 <= abs(a) + abs(b) <= 9]
LABEL = (1150, 1130, 1356, 1182)             # REBEL_CELL label (kept)
HQB = (1140, 1170, 1440, 1340)               # the Cell's base buildings: never a clone source


def defist(img):
    """Fill the fist roads with city blocks cloned a few iso steps away (regionally coherent choice
    of the least-red candidate), then neutralise the leftover red road glow."""
    a = np.asarray(img.convert('RGB'), np.float32).copy()
    x0, y0, x1, y1 = DISTRICT
    sub = a[y0:y1, x0:x1]
    road = redness(sub)
    mi = Image.fromarray(((road > 0.25) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(11))
    mi = mi.filter(ImageFilter.GaussianBlur(1.0))
    m = np.asarray(mi, np.float32)[..., None] / 255
    lx0, ly0, lx1, ly1 = LABEL
    m[ly0 - y0:ly1 - y0, lx0 - x0:lx1 - x0] = 0
    best, best_s = sub.copy(), np.full(sub.shape[:2], 9.0, np.float32)
    for (i, j) in OFFS:
        dx, dy = int(round(TX * (i - j))), int(round(TY * (i + j)))
        sx0, sy0 = x0 + dx, y0 + dy
        if sx0 < 0 or sy0 < 0 or sx0 + (x1 - x0) > a.shape[1] or sy0 + (y1 - y0) > a.shape[0]:
            continue
        cand = a[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
        r = redness(cand)
        s = np.asarray(Image.fromarray((np.clip(r, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15))
                       .filter(ImageFilter.GaussianBlur(36)), np.float32) / 255 + 0.002 * (abs(i) + abs(j))
        hx0, hy0, hx1, hy1 = HQB
        yy, xx = np.mgrid[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
        s = s + 5.0 * ((xx > hx0 - 20) & (xx < hx1 + 20) & (yy > hy0 - 20) & (yy < hy1 + 20))
        take = s < best_s
        best[take] = cand[take]
        best_s[take] = s[take]
    sub = sub * (1 - m) + best * m
    a[y0:y1, x0:x1] = sub
    sub = a[y0:y1, x0:x1]
    w = redness(sub)
    w[ly0 - y0 - 6:ly1 - y0 + 6, lx0 - x0 - 6:lx1 - x0 + 6] = 0
    # soften: grow a touch so anti-aliased road edges go too
    wi = Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    w = np.asarray(wi, np.float32)[..., None] / 255
    lum = sub.mean(axis=2, keepdims=True)
    street = ASPHALT * (0.75 + 0.5 * np.clip(lum / 90, 0, 1.4))
    out = sub * (1 - w) + street * w
    # red bloom on facades: desaturate the remaining red cast near the roads
    near = np.asarray(wi.filter(ImageFilter.GaussianBlur(10)), np.float32)[..., None] / 255
    l2 = out.mean(axis=2, keepdims=True)
    cast = np.clip(out[..., :1] - out[..., 2:3], 0, None) / 255
    k = np.clip(near * 1.6, 0, 0.8) * np.clip(cast * 3, 0, 1)
    neutral = l2 * np.array([0.92, 0.9, 1.15], np.float32)
    out = out * (1 - k) + neutral * k
    # feather the district box edge
    fy = np.minimum(np.arange(y1 - y0), np.arange(y1 - y0)[::-1])[:, None]
    fx = np.minimum(np.arange(x1 - x0), np.arange(x1 - x0)[::-1])[None, :]
    fe = np.clip(np.minimum(fx, fy) / 30.0, 0, 1)[..., None]
    a[y0:y1, x0:x1] = sub * (1 - fe) + out * fe
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def night_v6():
    return defist(Image.open(V6))


if __name__ == '__main__':
    src = Image.open(V6).convert('RGB')
    fixed = defist(src)
    box = (760, 800, 1780, 1440)
    a, b = src.crop(box), fixed.crop(box)
    out = Image.new('RGB', (a.width * 2 + 10, a.height))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + 10, 0))
    p = os.path.join(ROOT, 'scratch', 'defist_check.png')
    out.resize((out.width // 2, out.height // 2), Image.LANCZOS).save(p)
    print(p)
