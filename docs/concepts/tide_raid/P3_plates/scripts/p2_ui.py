"""P2 UI marks drawn with the pass-2 kit primitives: SITES LOST ink-black tile, draining DOWN ring, pencil tallies, cracked HOME ring."""
import sys, math
import numpy as np
import p1lib as L
sys.path.insert(0, L.H2)
import lib as PL
from lib import Cv, Lyr, hexc, blur as pblur, WHITE, INK, TIER, pbox
import hy, ui, glyphs

OCHRE = hexc('C98410')
K = 0.643


def sites_lost_tile(cv, c, r=30, num=None, k=1.0):
    """SITES LOST tile: ink-black solid hex, white 2.4 px rim, bold ochre diagonal hatch (clipped to the hex), tower-down glyph in white on ink."""
    bx = (c[0] - r - 14, c[1] - r - 14, c[0] + r + 14, c[1] + r + 14)
    o = Lyr(bx); f = Lyr(bx); rim = Lyr(bx); hat = Lyr(bx); g = Lyr(bx, ss=3); gk = Lyr(bx, ss=3)
    o.poly(hy.hexpts(c, r + 5), 255)
    f.poly(hy.hexpts(c, r), 255)
    rim.line(hy.hexpts(c, r) + [hy.hexpts(c, r)[0]], 2.6, 255)
    for i in range(-6, 8):
        x = c[0] + i * 9.0
        hat.line([(x - r, c[1] + r), (x + r, c[1] - r)], 4.6, 255)
    hm = f.m * hat.m
    cv.overL(o, INK, .97 * k)
    cv.overL(f, INK * 1.4, .98 * k)
    cv.over(OCHRE, hm, .95 * k, f.off)
    # glyph plate: ink disc so the white glyph reads over the hatch
    d = Lyr(bx); d.ell(c, r * .58, v=255)
    cv.overL(d, INK, .96 * k)
    glyphs.g_towerdown(g, c, r * .5)
    cv.over(WHITE * .96, g.m, 1.0 * k, g.off)
    cv.over(WHITE, rim.m, .96 * k, rim.off)
    if num is not None:
        x = c[0] + r + 12
        ui.ntext(cv, (x, c[1] + 1), str(num), int(r * 1.25), OCHRE * .8 + WHITE * .2, anchor='lm', stroke=3, k=k)


def tile(cv, c, tier, num=None, r=30, k=1.0):
    if tier == 'SITES_LOST':
        sites_lost_tile(cv, c, r, num, k)
    else:
        hy.hex_tile(cv, c, tier, num, r=r, k=k)


def drain_ring(cv, B, frac, r=50, k=1.0):
    """the DOWN clock as a drained ring on the ground: bright white arc = turns left, drained part = ink-plum hatch ticks with an ink under-stroke."""
    bx = (B[0] - r - 20, B[1] - r * K - 20, B[0] + r + 20, B[1] + r * K + 20)
    base = Lyr(bx); left = Lyr(bx); drain = Lyr(bx)
    full = SC_ring(B, r, 72, 0, 360)
    base.line(full + [full[0]], 11.0, 255)
    a_end = -90 + 360 * frac
    left.line(SC_ring(B, r, 60, -90, a_end), 7.0, 255)
    dr = SC_ring(B, r, 60, a_end, 270)
    drain.line(dr, 7.0, 255, dash=(3, 4))
    cv.overL(base, INK, .9 * k)
    cv.neonL(left, WHITE * .95, core=.95 * k, g1=(3, .5 * k), g2=None)
    cv.over(hexc('7A2E78'), drain.m, .85 * k, drain.off)


def SC_ring(c, r, n, a0, a1):
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * K * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def pencil_tally(cv, c, n=6, seed=2, size=34, col=None, k=1.0):
    """five-bar gate tally in white china pencil: n marks (strokes 1-4 vertical, 5th diagonal)."""
    rng = np.random.RandomState(seed)
    bx = (c[0] - size * 2, c[1] - size, c[0] + size * 2.5, c[1] + size)
    ly = Lyr(bx)
    x = c[0]
    for i in range(n):
        g = i // 5
        j = i % 5
        if j < 4:
            xx = x + g * size * 1.7 + j * size * .32 + rng.uniform(-1.5, 1.5)
            ly.line([(xx + rng.uniform(-2, 2), c[1] - size * .5), (xx + rng.uniform(-2, 2), c[1] + size * .5)], 4.0, 255)
        else:
            x0 = x + g * size * 1.7 - size * .15
            ly.line([(x0 + rng.uniform(-2, 2), c[1] + size * .45), (x0 + size * 1.4, c[1] - size * .45)], 4.0, 255)
    cv.overL(ly, INK, .55 * k)
    cv.addL(ly, (col if col is not None else hexc('F6F1E4')), .95 * k)


def cracked_ring(cv, home, r=94, seed=5, k=1.0):
    """HOME ring cracked: jagged ink cuts across the white ring and tick gauge (6 gaps), a few hairline cracks into the deck."""
    rng = np.random.RandomState(seed)
    bx = (home[0] - r - 40, home[1] - r * K - 40, home[0] + r + 40, home[1] + r * K + 40)
    cut = Lyr(bx, ss=3); hair = Lyr(bx, ss=3)
    for i in range(6):
        a = math.radians(rng.uniform(-170, 20) + i * 10)
        cx, cy = home[0] + r * math.cos(a), home[1] + r * K * math.sin(a)
        pts = [(cx, cy)]
        for j in range(5):
            a2 = a + rng.uniform(-.5, .5)
            pts.append((pts[-1][0] + math.cos(a2) * 9 + rng.uniform(-5, 5), pts[-1][1] + math.sin(a2) * 7 + rng.uniform(-4, 4)))
        cut.line(pts, 6.5, 255)
        hair.line(pts, 1.8, 255)
    cv.over(INK, cut.m, .95 * k, cut.off)
    cv.over(WHITE, hair.m, .7 * k, hair.off)
