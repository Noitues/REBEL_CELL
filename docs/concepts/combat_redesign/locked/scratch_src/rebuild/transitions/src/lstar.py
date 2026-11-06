"""lstar.py: the reviewer's probe (measure.py, sRGB to CIE L*), as functions.  Every value number reported for the transitions is L*."""
import numpy as np


def lum(rgb):
    """rgb uint8 or float 0..255 array -> linear luminance Y (0..1)"""
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def Lstar_y(y):
    y = np.asarray(y, dtype=np.float64)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def mean_L(rgb, mask=None):
    """L* of the mean luminance (the reviewer's 'mean L*')"""
    y = lum(rgb)
    if mask is not None:
        y = y[mask]
    return float(Lstar_y(y.mean()))


def pct_L(rgb, p, mask=None):
    y = lum(rgb)
    if mask is not None:
        y = y[mask]
    return float(Lstar_y(np.percentile(y, p)))


def L_of(col):
    return float(Lstar_y(lum(np.array(col, dtype=np.float64))))
