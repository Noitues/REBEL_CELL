"""xf_slices: per-slice-type colour + texture for the XEROX FLYER wheel (ART CALL 52 follow-up).
Four slice types (BURST, SHIELD, TURRET, REPAIR); each has a spot-ink fill and a tone-on-tone texture that carries the type in grey.
Textures are drawn in the wedge's own frame: u = along the spoke (hub to rim), v = across it."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from xf_gfx import hx

# name, fill, texture ink, texture opacity, texture name
PAL = {
    'A': {   # riso spot inks on the white sheet: magenta, cobalt, sun yellow, green
        'BURST':  dict(fill='FF3DA8', tex='B3126F', op=0.95, name='BIG DOTS'),
        'SHIELD': dict(fill='2A58F0', tex='142C86', op=0.95, name='SCALES'),
        'TURRET': dict(fill='FFD21F', tex='A97D00', op=0.95, name='CHECKER'),
        'REPAIR': dict(fill='4BD67E', tex='11703A', op=0.95, name='PLUS TILES'),
    },
    'B': {   # fluoro inks re-dealt onto the black toner sheet: orange, violet, aqua, lime
        'BURST':  dict(fill='FF5A14', tex='A12D00', op=0.95, dim=0.6, name='BIG DOTS'),
        'SHIELD': dict(fill='7A3CF0', tex='3B1A8A', op=0.95, name='SCALES'),
        'TURRET': dict(fill='3FE0F5', tex='0A7C8C', op=0.95, name='CHECKER'),
        'REPAIR': dict(fill='C5F42E', tex='5C7A00', op=0.95, name='PLUS TILES'),
    },
}
TEXKIND = {'BURST': 'dots', 'SHIELD': 'scales', 'TURRET': 'checker', 'REPAIR': 'plus'}


def palette(var, t):
    p = PAL[var][t]
    return hx(p['fill']), hx(p['tex']), p['op']


def _aa(sd, w=0.45):
    return np.clip(0.5 - sd / w, 0, 1).astype(np.float32)


def frame(cv, am, ctr):
    X, Y = cv.grid()
    dx, dy = X - ctr[0], Y - ctr[1]
    a = math.radians(am)
    ex, ey = math.sin(a), -math.cos(a)
    u = dx * ex + dy * ey
    v = -dx * ey + dy * ex
    return u.astype(np.float32), v.astype(np.float32)


def tex_dots(u, v, p=10.0, r=3.3):
    """staggered round dots (a coarse 45 degree halftone screen)"""
    best = np.full(u.shape, 99.0, np.float32)
    for (ou, ov) in ((0, 0), (p / 2, p / 2)):
        fu = (u - ou) / p
        fv = (v - ov) / p
        fu = (fu - np.round(fu)) * p
        fv = (fv - np.round(fv)) * p
        best = np.minimum(best, np.hypot(fu, fv) - r)
    return _aa(best)


def tex_checker(u, v, c=7.0):
    iu = np.floor(u / c)
    iv = np.floor(v / c)
    odd = ((iu + iv) % 2 == 0)
    # soft edge: distance to the nearest cell edge
    du = np.abs((u / c) - np.round(u / c)) * c
    dv = np.abs((v / c) - np.round(v / c)) * c
    return odd.astype(np.float32)


def tex_plus(u, v, p=20.0, hl=6.6, ht=2.1):
    best = np.full(u.shape, 99.0, np.float32)
    for (ou, ov) in ((0, 0), (p / 2, p / 2)):
        fu = (u - ou) / p
        fv = (v - ov) / p
        x = (fu - np.round(fu)) * p
        y = (fv - np.round(fv)) * p
        s1 = np.maximum(np.abs(x) - hl, np.abs(y) - ht)
        s2 = np.maximum(np.abs(x) - ht, np.abs(y) - hl)
        best = np.minimum(best, np.minimum(s1, s2))
    return _aa(best)


def tex_scales(u, v, r=8.6, lw=1.9):
    """scalloped fish-scale rows: outward half-circles, rows one radius apart, alternate rows offset by one radius"""
    h = r
    out = np.zeros(u.shape, np.float32)
    j0 = int(np.floor(float(u.min()) / h)) - 2
    j1 = int(np.ceil(float(u.max()) / h)) + 1
    for j in range(j0, j1 + 1):
        uc = j * h
        off = (j % 2) * r
        vc = np.round((v - off) / (2 * r)) * (2 * r) + off
        d = np.hypot(u - uc, v - vc)
        ring = _aa(np.abs(d - r) - lw / 2) * (u >= uc - 0.3)
        out = np.maximum(out, ring)
    return out


def texture(kind, cv, am, ctr, ox=0.0):
    u, v = frame(cv, 0 if kind == 'plus' else am, ctr)      # the crosses stay upright on screen
    if kind == 'dots':
        return tex_dots(u, v)
    if kind == 'checker':
        return tex_checker(u, v)
    if kind == 'plus':
        return tex_plus(u, v)
    return tex_scales(u, v)
