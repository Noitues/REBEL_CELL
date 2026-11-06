"""Pass 2 additions: sentry dome (H7c: a sentry shields its Site for ONE beam), sentry glyph."""
import math
import numpy as np
from lib import *
from glyphs import *
import ui
import hy

K = 0.643
HOLO = WHITE * .80 + TOW * .20


def g_sentry(ly, c, r):
    """sentry beacon: a dome with a core dot (the shield generator)."""
    ly.arc((c[0], c[1] + r * .5), r * .95, 180, 360, max(2.0, r * .26))
    ly.line([(c[0] - r * .95, c[1] + r * .5), (c[0] + r * .95, c[1] + r * .5)], max(2.0, r * .26), 255)
    ly.ell((c[0], c[1] + r * .02), r * .26, v=255)


def dome_pts(B, r=54, h=84, n=40):
    return [(B[0] + r * math.cos(math.pi * i / n), B[1] - h * math.sin(math.pi * i / n)) for i in range(n + 1)]


def sentry_dome(cv, B, state='charged', k=1.0, hit_at=None, r=54, h=84, seed=3):
    """state: charged (hex dome + full pip) | hit (ripple at hit_at, one cell cracked out, pip emptying) | spent (dashed
    ghost dome, empty pip). A sentry is a Site-local program: it is NOT on the street, it covers the Site itself."""
    col = HOLO
    bx = (B[0] - r - 40, B[1] - h - 70, B[0] + r + 40, B[1] + r * K + 40)
    out, base = Lyr(bx), Lyr(bx)
    pts = dome_pts(B, r, h)
    spent = state == 'spent'
    cs = 13.0
    clip = Lyr(bx)
    clip.poly(pts + [(B[0] - r, B[1])], 255)
    cl = clip.m
    hexm = Lyr(bx)
    for q in range(-6, 7):
        for p in range(-5, 6):
            x = B[0] + q * 1.5 * cs
            y = B[1] - 30 + (p * 1.732 + q * .866) * cs * .8
            hp = [(x + cs * .9 * math.cos(math.radians(60 * i)), y + cs * .9 * .8 * math.sin(math.radians(60 * i))) for i in range(6)]
            if state == 'hit' and hit_at is not None and np.hypot(x - hit_at[0], (y - hit_at[1]) / .8) < 17:
                continue   # a cracked-out cell
            hexm.line(hp + [hp[0]], 1.2, 255, dash=(3, 3) if spent else None)
    cells_m = hexm.m * cl
    out.line(pts, 3.0 if not spent else 2.0, 255, dash=(5, 5) if spent else None)
    base.line(ring_pts(B, r, 60), 3.0 if not spent else 2.0, 255, dash=(5, 5) if spent else None)
    kk = k * (1.0 if not spent else .42)
    cv.add(col, clip.m * (0.07 if not spent else 0.0), 1.0 * kk, clip.off)
    cv.add(col, cells_m, .55 * kk, clip.off)
    cv.neonL(out, col, core=.95 * kk, g1=(3, .55 * kk), g2=(10, .3 * kk))
    cv.neonL(base, col, core=.85 * kk, g1=(3, .4 * kk), g2=None)
    gp = (B[0], B[1] - h - 30)
    gl = Lyr((gp[0] - 30, gp[1] - 30, gp[0] + 30, gp[1] + 30))
    g_sentry(gl, gp, 13)
    cv.over(INK, blur(gl.m, 3) * 1.5, .85 * k, gl.off)
    cv.neonL(gl, col, core=1.0 * kk, g1=(2, .5 * kk), g2=None, white=.3)
    pip = Lyr((gp[0] - 20, gp[1] + 12, gp[0] + 20, gp[1] + 36))
    full = state == 'charged'
    pip.ell((gp[0], gp[1] + 24), 5.2, v=255, outline=not full, ow=2.0)
    cv.over(INK, blur(pip.m, 2) * 1.6, .8 * k, pip.off)
    cv.neonL(pip, col if state != 'hit' else TIER['HOLDS'], core=1.0 * kk, g1=(2, .5 * kk), g2=None)
    if state == 'hit' and hit_at is not None:
        hy.hex_flash(cv, np.array(hit_at), 46, TIER['HOLDS'] * .4 + WHITE * .6, k=.95)
