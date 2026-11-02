"""glyph helpers from the street toolkit (E10 glyph library -> masks on a Cv canvas)"""
import numpy as np
from scipy import ndimage as ndi
from st_gfx import *


def glyph_mask(name, px, cv, x, y, rot=0.0):
    from cv_lib import glyph_rgba
    ss = cv.ss
    g = glyph_rgba(name, int(px * ss), max(2, int(px * ss * 0.075)), fill=(255, 255, 255))
    a = np.asarray(g, np.float32) / 255.0
    m = np.clip((a[..., 3] - 0.5) * 3, 0, 1) * (a[..., :3].min(-1) > 0.8)
    m = ndi.gaussian_filter(m, 0.4 * ss)
    if rot:
        m = ndi.rotate(m, -rot, reshape=False, order=1)
    out = np.zeros((cv.H, cv.W), np.float32)
    px0, py0 = cv.p(x, y)
    ox, oy = int(round(px0 - m.shape[1] / 2)), int(round(py0 - m.shape[0] / 2))
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(cv.H, oy + m.shape[0]), min(cv.W, ox + m.shape[1])
    if ys1 > ys0 and xs1 > xs0:
        out[ys0:ys1, xs0:xs1] = m[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out
