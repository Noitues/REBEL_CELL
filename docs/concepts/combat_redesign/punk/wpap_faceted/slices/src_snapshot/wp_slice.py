"""wp_slice: per-type slice texture masks (ART CALL 52 slice pass).  Patterns live in the wedge's own frame (u radial, v tangential) so they turn with it.
All masks are hard-edged at SS resolution (AA on the down-sample).  Returns float32 (h,w) 0..1."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np

R_IN, R_OUT = 71.0, 177.0


def frame(h, w, S, x0, y0, CT, am):
    """pixel centres of an SS box starting at SS px (x0,y0) -> (u,v) in 1x px in the wedge frame (u radial from CT, v tangential)"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X = (xx + x0 + 0.5) / S - CT[0]
    Y = (yy + y0 + 0.5) / S - CT[1]
    a = math.radians(am)
    rx, ry = math.sin(a), -math.cos(a)
    tx, ty = math.cos(a), math.sin(a)
    return X * rx + Y * ry, X * tx + Y * ty


def dots(u, v, pitch=8.6, rmin=0.9, rmax=4.5):
    s2 = math.sqrt(2.0)
    p, q = (u + v) / s2, (u - v) / s2
    cp, cq = np.round(p / pitch) * pitch, np.round(q / pitch) * pitch
    uc = (cp + cq) / s2
    t = np.clip((uc - 80.0) / (R_OUT - 80.0), 0, 1)
    r = rmin + (rmax - rmin) * t
    return (np.hypot(p - cp, q - cq) < r).astype(np.float32)


def hexes(u, v, R=10.5, lw=1.5):
    """honeycomb outline: distance to the nearest Voronoi bisector of a triangular lattice (spacing s)"""
    s = R * math.sqrt(3.0)
    best1 = np.full(u.shape, 1e9, np.float32)
    best2 = np.full(u.shape, 1e9, np.float32)
    for off, (ox, oy) in enumerate(((0.0, 0.0), (0.5 * s, 0.5 * s * math.sqrt(3.0)))):
        i0 = np.round((u - ox) / s)
        j0 = np.round((v - oy) / (s * math.sqrt(3.0)))
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                cu = (i0 + di) * s + ox
                cv_ = (j0 + dj) * s * math.sqrt(3.0) + oy
                d = np.hypot(u - cu, v - cv_)
                nb = d < best1
                best2 = np.where(nb, best1, np.minimum(best2, d))
                best1 = np.where(nb, d, best1)
    edge = (best2 ** 2 - best1 ** 2) / (2.0 * s)
    return (edge < lw * 0.5).astype(np.float32)


def rings(u, v, cu, pitch=8.0, lw=2.8, r0=34.0):
    d = np.hypot(u - cu, v)
    k = np.abs((d % pitch) - pitch / 2.0)
    return ((k > pitch / 2.0 - lw / 2.0) & (d > r0)).astype(np.float32)


def plus(u, v, pitch=12.5, arm=3.7, th=2.2):
    j = np.round(u / pitch)
    vv = v - (j % 2) * pitch / 2.0
    i = np.round(vv / pitch)
    dv = vv - i * pitch
    du = u - j * pitch
    return (((np.abs(du) < th / 2) & (np.abs(dv) < arm)) | ((np.abs(dv) < th / 2) & (np.abs(du) < arm))).astype(np.float32)


def pattern(kind, h, w, S, x0, y0, CT, am, icon_r=128.0):
    u, v = frame(h, w, S, x0, y0, CT, am)
    if kind == 'DOTS':
        return dots(u, v)
    if kind == 'HEX':
        return hexes(u, v)
    if kind == 'RINGS':
        return rings(u, v, icon_r)
    if kind == 'PLUS':
        return plus(u, v)
    return np.zeros((h, w), np.float32)


def apply_tone(rgb, m, k_dark=0.58, k_light=0.50):
    """pattern pixels get a value shift of their own facet: darker on light planes, lighter on dark planes (so it survives grey)"""
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0
    dark = rgb * k_dark
    light = rgb + (255.0 - rgb) * k_light
    tone = np.where((lum > 0.5)[..., None], dark, light)
    return rgb * (1 - m[..., None]) + tone * m[..., None]
