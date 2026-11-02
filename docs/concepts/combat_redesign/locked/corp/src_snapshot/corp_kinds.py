"""corp_kinds: per-skin unit-kind wash separation.  A corp tint blended over the kind washes pulls them together (dE falls);
skin.kind_gain = (ring0, ring1, ring2) pushes the four kind washes apart again, in Lab, away from their common mean, BEFORE the corp material goes on.
gain 1.0 = the original washes.  The gains are solved by de_kinds.py (solve) so that the skinned min dE2000 is not below the unskinned min dE2000 per ring."""
import sys
sys.dont_write_bytecode = True
import numpy as np
import gram as G

KINDS4 = ['Packet', 'Worm', 'Jammer', 'Payload']
_D65 = np.array([0.95047, 1.0, 1.08883])
_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])


def rgb2lab(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = (c @ _M.T) / _D65
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def lab2rgb(lab):
    fy = (lab[0] + 16) / 116
    fx, fz = fy + lab[1] / 500, fy - lab[2] / 200
    f = np.array([fx, fy, fz])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * _D65
    c = np.linalg.solve(_M, xyz)
    c = np.clip(c, 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return tuple(int(round(v * 255)) for v in np.clip(c, 0, 1))


_base = [None]


def gained_wash(gains):
    base = _base[0]

    def kw(kind, dep, ramp=None):
        w = base(kind, dep, ramp)
        g = gains[dep]
        if abs(g - 1.0) < 1e-6 or kind not in KINDS4:
            return w
        labs = np.array([rgb2lab(base(k, dep, ramp)) for k in KINDS4])
        m = labs.mean(0)
        return lab2rgb(m + g * (rgb2lab(w) - m))
    return kw


def use(gains):
    """install the gained wash on gram (None or (1,1,1) = the original); returns the restore callable"""
    if _base[0] is None:
        _base[0] = G.kind_wash
    prev = G.kind_wash
    G.kind_wash = gained_wash(gains) if gains else _base[0]
    return lambda: setattr(G, 'kind_wash', prev)
