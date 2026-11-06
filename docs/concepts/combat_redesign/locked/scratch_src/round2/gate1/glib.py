"""gate1 shared helpers: sRGB -> luminance, CIE L*, Lab, dE76; polar coords about the board centre. Read-only on every input."""
import numpy as np
from PIL import Image

CC = (536, 540)
ROOT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
FINAL = ROOT + 'final/'
HOVER = ROOT + 'hover/'
NAME = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
CORPS = ['neutral', 'solace', 'meridian']


def plates():
    out = []
    for c in CORPS:
        for b, n in NAME.items():
            out.append((b, c, n + ('' if c == 'neutral' else '_' + c)))
    return out


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float64)


def lin(rgb):
    c = rgb / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lum(rgb):
    c = lin(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar_y(Y):
    Y = np.asarray(Y, dtype=np.float64)
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


def Lstar(rgb):
    return lstar_y(lum(rgb))


def lab(rgb):
    c = lin(np.asarray(rgb, dtype=np.float64))
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T
    wp = np.array([0.95047, 1.0, 1.08883])
    t = xyz / wp
    f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def de(lab_img, hexcol):
    t = lab(hexrgb(hexcol)) if isinstance(hexcol, str) else lab(np.asarray(hexcol, dtype=np.float64))
    return np.sqrt(((lab_img - t) ** 2).sum(-1))


def de_cols(c1, c2):
    a = lab(hexrgb(c1) if isinstance(c1, str) else np.asarray(c1, dtype=np.float64))
    b = lab(hexrgb(c2) if isinstance(c2, str) else np.asarray(c2, dtype=np.float64))
    return float(np.sqrt(((a - b) ** 2).sum()))


def polar(shape=(1080, 1920), c=CC):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    r = np.hypot(xx - c[0], yy - c[1])
    th = np.degrees(np.arctan2(xx - c[0], -(yy - c[1]))) % 360
    return r, th, xx, yy


def pct(a, q):
    a = np.asarray(a)
    return float(np.percentile(a, q)) if a.size else float('nan')


def contrast(Ya, Yb):
    hi, lo = max(Ya, Yb), min(Ya, Yb)
    return (hi + 0.05) / (lo + 0.05)


def hexof(rgb):
    return '#%02X%02X%02X' % tuple(int(round(v)) for v in rgb)


def modal(rgb_pix, q=4):
    """modal colour by quantised bins (q levels per 8-bit step)."""
    if len(rgb_pix) == 0:
        return None, 0
    k = (np.asarray(rgb_pix) // q).astype(np.int64)
    key = k[:, 0] * 65536 + k[:, 1] * 256 + k[:, 2]
    u, cnt = np.unique(key, return_counts=True)
    i = int(np.argmax(cnt))
    sel = key == u[i]
    return np.asarray(rgb_pix)[sel].mean(0), int(cnt[i])
