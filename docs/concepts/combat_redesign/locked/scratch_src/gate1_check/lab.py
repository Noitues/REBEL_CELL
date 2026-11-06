import numpy as np
from PIL import Image
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
B = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
C = (536, 540)
def load(p):
    path = p if ('/' in p) else F + p + '.png'
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255
def lin(rgb):
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
def Y(rgb):
    c = lin(rgb); return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
def Ls(y):
    y = np.asarray(y, dtype=np.float64)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)
def Yof(L):
    L = np.asarray(L, dtype=np.float64)
    return np.where(L > 8, ((L + 16) / 116) ** 3, L / 903.3)
def hex2rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
def lab(rgb):
    c = lin(np.asarray(rgb, dtype=np.float64))
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T
    w = np.array([0.95047, 1.0, 1.08883])
    t = xyz / w
    f = np.where(t > 216 / 24389, np.cbrt(t), (24389 / 27 * t + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)
def dE76(a, b):
    return float(np.linalg.norm(lab(a) - lab(b)))
_yy, _xx = np.mgrid[0:1080, 0:1920]
R = np.hypot(_xx - C[0], _yy - C[1])
TH = (np.degrees(np.arctan2(_xx - C[0], -(_yy - C[1]))) + 360) % 360
def polar_mask(r0, r1, a0, a1):
    a0 %= 360; a1 %= 360
    am = (TH >= a0) & (TH < a1) if a0 < a1 else (TH >= a0) | (TH < a1)
    return (R >= r0) & (R < r1) & am
def stats(L_or_y, m, is_y=True):
    y = L_or_y[m]
    return dict(n=int(m.sum()), mean=float(Ls(y.mean())), p95=float(Ls(np.percentile(y, 95))), med=float(Ls(np.median(y))), p50=float(Ls(np.percentile(y, 50))))
