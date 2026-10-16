"""Shared helpers for the decision sheets: fonts, the spec's luma measure (PIPELINE_SPEC 12.1), exposure solve."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "C:/Windows/Fonts/"
BG = (14, 14, 20)
INK = (232, 232, 240)
DIM = (150, 150, 165)
LIME = (212, 255, 0)
ORANGE = (255, 140, 26)
RED = (255, 70, 80)
CYAN = (90, 220, 255)


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype(FONT_DIR + ("consolab.ttf" if bold else "consola.ttf"), size)
    return ImageFont.truetype(FONT_DIR + ("segoeuib.ttf" if bold else "segoeui.ttf"), size) if bold and _has("segoeuib.ttf") \
        else ImageFont.truetype(FONT_DIR + ("bahnschrift.ttf" if bold else "segoeui.ttf"), size)


def _has(name):
    import os
    return os.path.exists(FONT_DIR + name)


def luma(a8):
    """Rec.709 luma of an 8-bit sRGB array, values / 255 (PIPELINE_SPEC 12.1)."""
    a = a8.astype(np.float32) / 255.0
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def stats(a8):
    y = luma(a8)
    return dict(median=float(np.median(y)), under=float((y < 0.10).mean()), over=float((y > 0.85).mean()))


def s2l(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def l2s(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def expose(a8, k):
    """A linear-light exposure change (k = gain) on an 8-bit sRGB image; highlights clip as a render would."""
    lin = s2l(a8.astype(np.float32) / 255.0)
    return (l2s(lin * k) * 255.0 + 0.5).astype(np.uint8)


def solve_median(a8, target, sub=4):
    """The gain whose result has the target median luma (bisection in stops on a subsampled copy)."""
    small = a8[::sub, ::sub]
    lo, hi = -4.0, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        m = np.median(luma(expose(small, 2.0 ** mid)))
        if m < target:
            lo = mid
        else:
            hi = mid
    return 2.0 ** ((lo + hi) / 2)


def fit(im, w, h):
    """Cover-crop to w x h."""
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(draw, xy, text, fnt, width, fill=INK, gap=6):
    x, y = xy
    for ln in wrap(draw, text, fnt, width):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + gap
    return y
