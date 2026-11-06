"""de_lib: sRGB -> CIE Lab (D65) and CIE76 dE, WCAG ratio, L*.  Shared by the card palette search and the dE table."""
import numpy as np

WHITE_D65 = np.array([0.95047, 1.0, 1.08883])


def hx(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


def lin(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(c):
    l = lin(c)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = l @ M.T / WHITE_D65
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1)


def de76(c1, c2):
    return float(np.linalg.norm(lab(c1) - lab(c2)))


def Y(c):
    l = lin(c)
    return float(0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2])


def Lstar(c):
    return float(lab(c)[0])


def ratio(a, b):
    la, lb = Y(a), Y(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def hexs(c):
    return '#%02X%02X%02X' % tuple(int(round(float(v) * 255)) for v in c)


TOKENS = {'SOAK': '3A7EF3', 'SCHEDULE': 'FF8C1A', 'BOSS_GOLD': 'FFC428', 'TRACE': 'A03CFF', 'NET_CYAN': '5CE1FF',
          'HARM': 'FF4433', 'GAIN': '7BE07B', 'PLAN': 'FFE200'}
