"""Glyph atlas for the E concept: vector glyphs drawn into a Lyr mask (255 = shape, 0 = cut-out)."""
import math
import numpy as np
from lib import *


def _p(c, r, pts):
    return [(c[0] + x * r, c[1] + y * r) for x, y in pts]


def g_house(ly, c, r):
    ly.poly(_p(c, r, [(-1, -.02), (0, -1), (1, -.02), (.76, -.02), (.76, .88), (-.76, .88), (-.76, -.02)]))
    ly.rr(c[0] - .22 * r, c[1] + .25 * r, c[0] + .22 * r, c[1] + .9 * r, 1, 0)


def g_flame(ly, c, r):
    ly.poly(_p(c, r, [(0, -1), (.55, -.1), (.6, .45), (.25, .95), (-.25, .95), (-.6, .45), (-.4, 0), (-.15, .2)]))
    ly.ell((c[0], c[1] + .55 * r), .2 * r, .28 * r, 0)


def g_shield(ly, c, r, check=False):
    ly.poly(_p(c, r, [(-.9, -.85), (.9, -.85), (.9, .1), (0, 1.05), (-.9, .1)]))
    if check:
        ly.line(_p(c, r, [(-.42, -.02), (-.1, .38), (.48, -.4)]), r * .3, 0)


def g_heart(ly, c, r, crack=True, shatter=False):
    ly.ell((c[0] - .5 * r, c[1] - .3 * r), .56 * r, v=255)
    ly.ell((c[0] + .5 * r, c[1] - .3 * r), .56 * r, v=255)
    ly.poly(_p(c, r, [(-1.04, -.05), (0, 1.0), (1.04, -.05)]))
    if crack or shatter:
        ly.line(_p(c, r, [(.06, -.75), (-.2, -.15), (.24, .22), (-.02, .75)]), r * (.28 if shatter else .2), 0)
    if shatter:
        ly.line(_p(c, r, [(-.9, .3), (-.3, .1), (.3, .4), (.9, .0)]), r * .22, 0)


def g_towerdown(ly, c, r):
    ly.poly(_p(c, r, [(-.8, -.9), (.15, -.9), (.15, .9), (-.8, .9)]))
    for y in (-.5, -.1, .3, .7):
        ly.line(_p(c, r, [(-.62, y), (-.0, y)]), r * .12, 0)
    ly.poly(_p(c, r, [(.4, -.3), (.98, -.3), (.69, .55)]))


def g_untouched(ly, c, r):
    ly.ell(c, r * .92, v=255, outline=True, ow=max(1.6, r * .26))
    ly.ell(c, r * .22, v=255)


def g_skull(ly, c, r):
    ly.ell((c[0], c[1] - r * .12), r * .88, r * .8, 255)
    ly.rr(c[0] - r * .5, c[1] + r * .3, c[0] + r * .5, c[1] + r * .98, r * .12, 255)
    ly.ell((c[0] - r * .33, c[1] - r * .1), r * .24, v=0)
    ly.ell((c[0] + r * .33, c[1] - r * .1), r * .24, v=0)
    ly.poly(_p(c, r, [(0, .12), (-.1, .3), (.1, .3)]), 0)
    for k in (-.2, 0, .2):
        ly.line(_p(c, r, [(k, .62), (k, .98)]), r * .09, 0)


def g_x(ly, c, r, w=None):
    w = r * .4 if w is None else w
    ly.line(_p(c, r, [(-1, -1), (1, 1)]), w)
    ly.line(_p(c, r, [(1, -1), (-1, 1)]), w)


def g_wrench(ly, c, r):
    ly.line(_p(c, r, [(-.75, .75), (.3, -.3)]), r * .42)
    ly.ell((c[0] + .5 * r, c[1] - .5 * r), r * .52, v=255)
    ly.poly(_p(c, r, [(.5, -.5), (1.2, -1.0), (1.0, -.1)]), 0)


def g_broom(ly, c, r):
    ly.line(_p(c, r, [(-.9, .9), (.4, -.4)]), r * .26)
    ly.poly(_p(c, r, [(.1, -.9), (1.0, -.05), (.1, .15), (-.15, -.65)]))


def g_snow(ly, c, r):
    for k in range(3):
        a = math.radians(60 * k + 15)
        ly.line([(c[0] - r * math.cos(a), c[1] - r * math.sin(a)), (c[0] + r * math.cos(a), c[1] + r * math.sin(a))], r * .22)


def g_chev(ly, c, r, n=2):
    for i in range(n):
        o = (i - (n - 1) / 2) * r * .8
        ly.line(_p((c[0] + o, c[1]), r, [(-.45, -.9), (.45, 0), (-.45, .9)]), r * .36)


def g_plus(ly, c, r):
    ly.line(_p(c, r, [(-1, 0), (1, 0)]), r * .5)
    ly.line(_p(c, r, [(0, -1), (0, 1)]), r * .5)


def g_zig(ly, c, r):
    ly.line(_p(c, r, [(-1, .4), (-.5, -.6), (0, .5), (.5, -.6), (1, .4)]), r * .36)


def g_detour(ly, c, r):
    ly.arc((c[0], c[1] + r * .25), r * .8, 180, 360, r * .34)
    ly.poly(_p(c, r, [(.78 - .55, .22), (.78 + .55, .22), (.78, .95)]))
    ly.ell((c[0] - .8 * r, c[1] + .25 * r), r * .2, v=255)


def g_wall(ly, c, r):
    """GUARD: firewall = shield of bricks."""
    ly.poly(_p(c, r, [(-.9, -.9), (.9, -.9), (.9, .1), (0, 1.05), (-.9, .1)]))
    for y in (-.35, .15):
        ly.line(_p(c, r, [(-.9, y), (.9, y)]), r * .12, 0)
    for x, y0, y1 in ((0, -.9, -.35), (-.42, -.35, .15), (.42, -.35, .15), (0, .15, .62)):
        ly.line(_p(c, r, [(x, y0), (x, y1)]), r * .12, 0)


def type_polys(typ):
    """pass 2: ONE family of bold solid silhouettes, x = travel direction, unit radius.
    D dart (sharp, swallow-tail), N block cursor in four selection brackets, E bull-horn C (ram).
    Used for the beam HEADS, the type glyph on cards / programs / locks."""
    if typ == 'D':
        return [[(1.12, 0), (-.9, -.88), (-.42, 0), (-.9, .88)]]
    if typ == 'N':
        out = [[(-.52, -.52), (.52, -.52), (.52, .52), (-.52, .52)]]
        t, a = .26, .52
        for sx in (-1, 1):
            for sy in (-1, 1):
                q = 1.08
                out.append([(sx * q, sy * q), (sx * (q - a), sy * q), (sx * (q - a), sy * (q - t)), (sx * (q - t), sy * (q - t)),
                            (sx * (q - t), sy * (q - a)), (sx * q, sy * (q - a))])
        return out
    return [[(-.95, -.95), (1.12, -.95), (.68, -.28), (-.12, -.28), (-.12, .28), (.68, .28), (1.12, .95), (-.95, .95)]]


def g_type(ly, typ, c, r):
    """beam-type silhouette (the same shape the daemon head has)."""
    for poly in type_polys(typ):
        ly.poly(_p(c, r, poly))


def g_lock(ly, c, r, open_=False):
    ly.rr(c[0] - r * .7, c[1] - r * .05, c[0] + r * .7, c[1] + r * .85, r * .15, 255)
    if open_:
        ly.arc((c[0] + r * .15, c[1] - r * .12), r * .5, 200, 360, r * .22)
        ly.line([(c[0] + r * .65, c[1] - r * .12), (c[0] + r * .65, c[1] - r * .45)], r * .22)
    else:
        ly.arc((c[0], c[1] - r * .1), r * .5, 180, 360, r * .22)


def g_eye(ly, c, r):
    """hunter: an almond eye (outlined) with an iris ring and a slit pupil."""
    top = [(c[0] + r * math.cos(math.radians(a)), c[1] - r * .52 * math.sin(math.radians(a))) for a in np.linspace(0, 180, 28)]
    bot = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * .52 * math.sin(math.radians(a))) for a in np.linspace(180, 360, 28)]
    ly.line(top + bot + [top[0]], max(2.5, r * .1), 255)
    ly.ell(c, r * .36, v=255, outline=True, ow=max(2, r * .08))
    ly.ell(c, r * .09, r * .27, 255)
    ly.line([(c[0] - r * 1.08, c[1]), (c[0] - r * 1.3, c[1])], max(2, r * .08), 255)
    ly.line([(c[0] + r * 1.08, c[1]), (c[0] + r * 1.3, c[1])], max(2, r * .08), 255)


def g_tier(ly, tier, c, r):
    {'UNTOUCHED': g_untouched,
     'HOLDS': lambda l, c_, r_: g_shield(l, c_, r_, True),
     'SITES_LOST': g_towerdown,
     'DAMAGED': lambda l, c_, r_: g_heart(l, c_, r_, True),
     'BREACHED': lambda l, c_, r_: g_heart(l, c_, r_, True, True)}[tier](ly, c, r)


def g_card_back(ly, c, w, h):
    ly.rr(c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, 3, 255, outline=True, ow=1.6)


def g_cardx(ly, c, r):
    """CLEAN: an INFECTED card struck out."""
    ly.rr(c[0] - r * .62, c[1] - r * .95, c[0] + r * .62, c[1] + r * .95, r * .14, 255)
    ly.line([(c[0] - r * .32, c[1] - r * .4), (c[0] + r * .32, c[1] + r * .4)], r * .2, 0)
    ly.line([(c[0] + r * .32, c[1] - r * .4), (c[0] - r * .32, c[1] + r * .4)], r * .2, 0)
