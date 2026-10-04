"""Base maps for round 26.

Night: round 25's city_night_hq_v3.jpg (the round 6 map with the new HQs, same framing).
Day: there is no v3 day map yet, so it is derived: the round 6 day map everywhere the v3 night map
matches the round 6 night map, and inside the changed areas (new HQs, the cleared fist roads) the v3
night pixels graded to day with a per-channel curve fitted from round 6 night -> round 6 day.
Read-only on every earlier round; output goes to this round's scratch/.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONC = os.path.dirname(ROOT)
R6V = os.path.join(CONC, 'round6_city_restyle', 'views')
V3 = os.path.join(CONC, 'round25_hq_targets', 'city_night_hq_v3.jpg')
SCR = os.path.join(ROOT, 'scratch')


# round 31: the title screen must not show the baked-in territory labels. Each label box (in the
# 1920x1080 frame of cm.CROP) is covered by a clone of the city a few iso blocks away, feathered.
# (frame box x0, y0, x1, y1), clone offset in base px (multiples of the iso street step).
LABEL_PATCHES = [((840, 188, 1130, 252), (-112, 56)),
                 ((45, 478, 255, 548), (112, 56)),
                 ((1580, 582, 1810, 652), (-112, -56)),
                 ((805, 832, 1078, 902), (-140, -70))]


def night():
    import defist  # round 32: latest map (v6, Meridian fortress) with the fist roads replaced by city blocks
    img = defist.night_v6()
    k = 1320 / 1920.0
    for (x0, y0, x1, y1), (dx, dy) in LABEL_PATCHES:
        bx0, by0 = int(600 + x0 * k), int(560 + y0 * k)
        bx1, by1 = int(600 + x1 * k), int(560 + y1 * k)
        pad = 8
        src = img.crop((bx0 - pad + dx, by0 - pad + dy, bx1 + pad + dx, by1 + pad + dy))
        m = Image.new('L', src.size, 0)
        from PIL import ImageDraw
        ImageDraw.Draw(m).rectangle([pad // 2, pad // 2, src.size[0] - pad // 2, src.size[1] - pad // 2], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(3))
        img.paste(src, (bx0 - pad, by0 - pad), m)
    return img


def day():
    path = os.path.join(SCR, 'base_day_v3.png')
    if os.path.exists(path):
        return Image.open(path).convert('RGB')
    n6 = np.asarray(Image.open(os.path.join(R6V, 'restyle_night_full.png')).convert('RGB'), np.float32)
    d6 = np.asarray(Image.open(os.path.join(R6V, 'restyle_day_full.png')).convert('RGB'), np.float32)
    v3i = night()
    v3 = np.asarray(v3i, np.float32)
    # changed areas: large, smoothed differences only (ignores jpeg noise)
    diff = np.abs(v3 - n6).mean(axis=2)
    m = Image.fromarray(np.clip(diff * 4, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
    m = np.asarray(m, np.float32) / 255
    m = np.clip((m - 0.25) / 0.35, 0, 1)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
                   .filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None] / 255
    # night -> day grade: per channel, a monotone curve from matched quantiles of round 6
    graded = np.empty_like(v3)
    q = np.linspace(0, 100, 101)
    lum_n = n6.mean(axis=2)
    for c in range(3):
        xs = np.percentile(n6[..., c], q)
        ys = np.percentile(d6[..., c], q)
        xs = np.maximum.accumulate(xs + np.arange(len(xs)) * 1e-3)
        graded[..., c] = np.interp(v3[..., c], xs, ys)
    # keep the new HQs' own light: lift saturation back a little from the night colours
    g_l = graded.mean(axis=2, keepdims=True)
    v_l = v3.mean(axis=2, keepdims=True) + 1
    chroma = (v3 - v_l) / v_l * g_l
    graded = np.clip(g_l + chroma * 0.8 + (graded - g_l) * 0.4, 0, 255)
    out = d6 * (1 - m) + graded * m
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    os.makedirs(SCR, exist_ok=True)
    img.save(path)
    Image.fromarray((m[..., 0] * 255).astype(np.uint8)).save(os.path.join(SCR, 'day_mask.png'))
    return img


if __name__ == '__main__':
    im = day()
    im.crop((600, 560, 1920, 1302)).save(os.path.join(SCR, 'day_v3_crop.png'))
