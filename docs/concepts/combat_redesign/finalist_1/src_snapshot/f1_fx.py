"""f1_fx: slice-wide overlay effects in the F1 hand (stills = the peak frame).  Families keep their own material (VISUAL_PLAN G):
FX-P protect = a taped black-book page + a marker double line (paper, no glow, hard block shadow)
FX-H harm    = print: red halftone flood (6 px, 45 deg) from the rim, black krackle, a 3 px misregistered dark-red plate on the impact
FX-P soak    = an indigo marker funnel on the wedge axis
All drawn in tower coordinates (CT) on a Canvas that sits exactly over the tower image."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from f1_lib import *
import f1_tower as FT
from f1_tower import CT, R_IN, R_OUT, solidify, tapered_outline, block_drop, bbox

HARMC = (255, 68, 51)
HARM_D = (156, 31, 20)
SOAKC = (58, 126, 243)
KRAFT = (198, 154, 98)


def wedge_region(cv, s, r0, r1, half=26.0):
    reg = cv.band_mask(CT, r0, r1, 60 * s - half, 60 * s + half, step=0.7)
    return reg


def halftone(cv, region, s, depth, pitch=6.0, col=HARMC, alpha=1.0, off=(0, 0), flood_from_rim=True):
    """Ben-Day dot field, 45 deg screen.  Coverage 1 at the rim falling to 0 at `depth` px inside it."""
    S = cv.S
    H_, W_ = region.shape
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    x = xx / S - off[0]
    y = yy / S - off[1]
    rho = np.hypot(x - CT[0], y - CT[1])
    cov = np.clip(1 - (R_OUT + 2 - rho) / depth, 0, 1) ** 0.85
    u = (x + y) / math.sqrt(2)
    v = (x - y) / math.sqrt(2)
    du = (u / pitch) - np.floor(u / pitch) - 0.5
    dv = (v / pitch) - np.floor(v / pitch) - 0.5
    d = np.hypot(du, dv) * pitch
    rad = 0.74 * np.sqrt(cov) * pitch / 2 * 1.45
    dots = np.clip((rad - d) * S + 0.5, 0, 1) * (cov > 0.02)
    cv.over(dots * region, col, alpha)


def krackle(cv, p, r=11.0, ang=0.0, n=9):
    pts = []
    for k in range(n * 2):
        rr = r * (1.0 if k % 2 == 0 else 0.34) * cv.r.uniform(0.75, 1.15)
        pts.append(pol(p, rr, ang + k * 180.0 / n + cv.r.uniform(-5, 5)))
    m = cv.poly_mask(pts)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, cv.S, 1.6), 0.4) * 1.5, 0, 1), HARMC, 1.0)
    cv.over(m, INK, 1.0)


def spark_star(cv, p, r=6.0):
    pts = [pol(p, r if k % 2 == 0 else r * 0.38, k * 45 + cv.r.uniform(-6, 6)) for k in range(8)]
    m = cv.poly_mask(pts)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, cv.S, 1.3), 0.4) * 1.5, 0, 1), INK, 1.0)
    cv.over(m, WHITE, 1.0)


def chevron_stack(cv, s, n=3, r0=203.0, step=11.5, col=HARMC, stop_r=None, wiggle=0.0):
    """stencil chevrons (T family) stacked along the slice axis, pointing at the tower, flat HARM with a hard ink keyline"""
    am = 60 * s
    for i in range(n):
        r_ = r0 + i * step
        if stop_r is not None and r_ < stop_r:
            continue
        pts = [pol(CT, r_ + 11.0, am - 5.6), pol(CT, r_ - 3.0, am), pol(CT, r_ + 11.0, am + 5.6)]
        ballpoint(cv, pts, INK, 8.6, 1.0, wob=0.1, wl=12, taper=(0, 0))
        marker(cv, pts, col, w=4.6, alpha=1.0, wob=0.1, wl=12, taper=(0, 0), grain=0.0, rough=0.0, pool=0.0)


# ------------------------------------------------------------------ FX-P: shield block (the page plate slams over the outer 40 percent)
def shield_block(cv, s, ticks=1, w=None):
    S = cv.S
    am = 60 * s
    reg = wedge_region(cv, s, 147.0, R_OUT + 1.5, 25.3)
    reg = warp(reg, 0.8 * S, 9 * S, cv.r)
    t, rim = torn_mask(cv, reg, rough=0.8, fringe=0.7)
    solid = solidify(t, S)
    block_drop(cv, solid, 4.0, 5.0)
    tapered_outline(cv, solid, 2.8, 5.4)
    n = smooth(*solid.shape, 4 * S, cv.r)
    cv.over(np.clip(solid * (0.95 + 0.05 * n), 0, 1), (246, 242, 232), 1.0)
    # a slim pink fold band on the inner edge, a marker double line (L10) across the plate, tally ticks, two kraft tapes
    for rr in (152.4, 157.6):
        pts = arc_pts(CT, rr, am - 21.5, am + 21.5, 0.8)
        marker(cv, pts, INK, w=2.6, alpha=0.98, wob=0.4, wl=40, taper=(0.04, 0.04), grain=0.05)
    if w is not None:
        FT.draw_pips(cv, w)                       # the plate carries the pip sockets: HP stays readable under the protection
    for sg in (-1, 1):
        tape(cv, pol(CT, 150.0, am + sg * 21.5), 20, 9, am + sg * 21.5 + 90, col=KRAFT, alpha=0.88)
    # incoming chevrons stop at the plate's rim edge; white ink sparks where they hit
    chevron_stack(cv, s, 3, r0=204.0, step=12.5)
    for sg in (-1, 1):
        spark_star(cv, pol(CT, R_OUT + 9.5, am + sg * 11.0), 6.2)
    spark_star(cv, pol(CT, R_OUT + 14.0, am), 7.6)
    # a hand impact ring pinged off the plate
    sketch_circle(cv, pol(CT, R_OUT + 3.0, am), 15.0, INK, 1.1, passes=1, alpha=0.9, over=20)


# ------------------------------------------------------------------ FX-H: shield break (the same plate in shards, red flood behind, wedge goes dark)
def shield_break(cv, s):
    S = cv.S
    am = 60 * s
    wedge = wedge_region(cv, s, R_IN, R_OUT, 26.0)
    # the flood: a dark wash and the halftone, then the misregistered plate
    cv.over(wedge * 0.0 + np.clip(wedge, 0, 1) * 0, INK, 0.0)
    plate = wedge_region(cv, s, 142.0, R_OUT + 1.5, 25.3)
    plate = warp(plate, 0.8 * S, 9 * S, cv.r)
    t, rim = torn_mask(cv, plate, rough=0.8, fringe=0.7)
    solid = solidify(t, S)
    cv.over(np.clip(solid, 0, 1) * 0.0, INK, 0.0)
    cv.over(np.clip(ndi.gaussian_filter(wedge, 2.0 * S), 0, 1) * wedge, INK, 0.55)       # wedge goes dark
    halftone(cv, wedge, s, 56.0, 6.0, HARMC, 1.0)
    halftone(cv, wedge, s, 56.0, 6.0, HARM_D, 0.9, off=(3.0, 2.0))                      # 3 px misregistered plate
    halftone(cv, wedge, s, 56.0, 6.0, HARMC, 1.0)
    # the plate in 7 shards
    seeds = []
    for q in range(7):
        a = am + cv.r.uniform(-21, 21)
        rr = cv.r.uniform(134, 172)
        seeds.append(pol(CT, rr, a))
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    d = np.stack([np.hypot(xx / S - sx, yy / S - sy) for sx, sy in seeds], 0)
    lab = d.argmin(0)
    for q, (sx, sy) in enumerate(seeds):
        sh = (lab == q) * solid
        if sh.max() <= 0.02:
            continue
        dirv = np.array([sx - CT[0], sy - CT[1]])
        dirv /= np.hypot(*dirv) + 1e-9
        mv = cv.r.uniform(5, 26)
        dx, dy = int(round(dirv[0] * mv * S)), int(round(dirv[1] * mv * S))
        sh2 = np.roll(np.roll(sh, dy, 0), dx, 1)
        sh2s = np.roll(np.roll(sh2, int(3 * S), 0), int(3 * S), 1)
        cv.over(np.clip(sh2s - sh2, 0, 1), HARM_D, 0.9)                           # misregistered red plate peeking under the shard
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(sh2, S, 2.0), 0.4) * 1.5, 0, 1), INK, 1.0)
        cv.over(sh2, (246, 242, 232), 1.0)
        if q % 2 == 0:
            hatch_region(cv, ndi.binary_erosion(sh2 > 0.5, iterations=int(2.5 * S)).astype(np.float32), 0, 0, (150, 146, 138), ang=45, pitch=3.4, w=0.8, alpha=0.6, over=0.0, jit=0.2)
    for sg, rr in ((-1, 3.0), (1, 4.0)):
        krackle(cv, pol(CT, R_OUT + 6.0, am + sg * 15.0), 11.0 + rr * 2, ang=cv.r.uniform(0, 60))
    krackle(cv, pol(CT, R_OUT + 4.0, am + 2.0), 15.0, ang=20)
    chevron_stack(cv, s, 3, r0=205.0, step=12.5)


# ------------------------------------------------------------------ FX-H: hit lands (pip lost): halftone flood across the outer 50 percent + krackle at the rim
def hit_land(cv, s, pips=1):
    S = cv.S
    am = 60 * s
    wedge = wedge_region(cv, s, R_IN, R_OUT, 26.0)
    halftone(cv, wedge, s, 52.0, 6.0, HARM_D, 0.9, off=(3.0, 2.0))
    halftone(cv, wedge, s, 52.0, 6.0, HARMC, 1.0)
    krackle(cv, pol(CT, R_OUT + 6.0, am - 9.0), 12.0, ang=10)
    krackle(cv, pol(CT, R_OUT + 5.0, am + 10.0), 9.0, ang=40)
    chevron_stack(cv, s, 3, r0=205.0, step=12.5)


# ------------------------------------------------------------------ FX-H: slice break (ability lost): black-out, halftone fade over the icon, a red stencil X in the outer corner
def slice_break(cv, s):
    S = cv.S
    am = 60 * s
    wedge = wedge_region(cv, s, R_IN, R_OUT, 26.0)
    cv.over(wedge, (10, 8, 18), 0.72)
    halftone(cv, wedge, s, 120.0, 6.0, HARMC, 0.55)
    x, y = pol(CT, R_OUT - 22, am + 17)
    for sg in (1, -1):
        p = [(x - 8, y - sg * 8), (x + 8, y + sg * 8)]
        ballpoint(cv, p, INK, 9.0, 1.0, wob=0.2, wl=9, taper=(0, 0))
    for sg in (1, -1):
        p = [(x - 8, y - sg * 8), (x + 8, y + sg * 8)]
        marker(cv, p, HARMC, w=5.6, alpha=1.0, wob=0.2, grain=0.04, taper=(0, 0))
    krackle(cv, pol(CT, R_OUT + 6.0, am - 4.0), 12.0, ang=25)
    chevron_stack(cv, s, 3, r0=205.0, step=12.5)


# ------------------------------------------------------------------ FX-P: brace block (the clamp closes round the whole wedge; the landing stops at the clamp)
def brace_clamp(cv, s, ghost=False):
    """the clamp itself: a taped paper frame round the whole wedge, a marker double line down the rail, pink jaws at the corners (also the hover ghost)"""
    S = cv.S
    am = 60 * s
    outer = wedge_region(cv, s, R_IN - (8.0 if ghost else 5.0), R_OUT + (13.0 if ghost else 8.0), 29.4 if ghost else 27.8)
    inner = wedge_region(cv, s, R_IN + 1.0, R_OUT - 1.5, 25.2)
    ring = np.clip(outer - inner, 0, 1)
    ring = warp(ring, 0.6 * S, 8 * S, cv.r)
    solid = solidify(ring, S)
    block_drop(cv, solid, 3.0, 4.0)
    tapered_outline(cv, solid, 2.2, 4.4)
    cv.over(solid, (255, 206, 232) if ghost else (246, 242, 232), 1.0)
    for off_, w_ in ((-1.7, 2.2), (1.7, 2.2)):                       # the L10 double line down the clamp rail
        rr = R_OUT + 2.4 + off_
        marker(cv, arc_pts(CT, rr, am - 25.0, am + 25.0, 0.8), PINK if ghost else INK, w=2.0 if ghost else 1.7, alpha=0.97, wob=0.3, wl=40, taper=(0.04, 0.04), grain=0.05)
    for sg in (-1, 1):
        for rr in (R_IN + 12.0, R_OUT - 12.0):
            pts = [pol(CT, rr - 8, am + sg * 25.0), pol(CT, rr + 8, am + sg * 25.0)]
            marker(cv, pts, INK, w=5.0, alpha=1.0, wob=0.1, taper=(0, 0), grain=0.04)
            marker(cv, pts, PINK, w=2.2, alpha=1.0, wob=0.1, taper=(0, 0), grain=0.1)
        tape(cv, pol(CT, R_OUT + 1.0, am + sg * 24.5), 18, 8, am + sg * 24.5, col=KRAFT, alpha=0.88)


def brace_block(cv, s):
    """FX-P brace block: the clamp closes round the whole wedge, an impact ring pings off it, and the landing's chevrons crumple at the clamp"""
    am = 60 * s
    brace_clamp(cv, s)
    p = pol(CT, R_OUT + 14.0, am)
    sketch_circle(cv, p, 16.0, INK, 1.4, passes=2, alpha=0.9, over=24)
    for i in range(3):
        r_ = 207.0 + i * 8.5
        pts = [pol(CT, r_ + 8, am - 5 + i * 1.0), pol(CT, r_ - 3.0 + (i % 2), am + (i - 1) * 1.5), pol(CT, r_ + 8, am + 5 - i * 0.8)]
        ballpoint(cv, pts, INK, 8.0, 1.0, wob=0.4, wl=12, taper=(0, 0))
        marker(cv, pts, HARMC, w=3.8, alpha=1.0, wob=0.4, wl=12, taper=(0, 0), grain=0.0, rough=0.0, pool=0.0)
    spark_star(cv, pol(CT, R_OUT + 10.0, am - 12.0), 6.0)
    spark_star(cv, pol(CT, R_OUT + 10.0, am + 12.0), 6.0)


# ------------------------------------------------------------------ FX-P: soak take (an indigo funnel from the rim to the soaking pip)
def soak_take(cv, s):
    S = cv.S
    am = 60 * s
    ax = np.array([math.sin(math.radians(am)), -math.cos(math.radians(am))])
    nx = np.array([-ax[1], ax[0]])

    def P(r, w):
        c = np.array(CT) + ax * r
        return (tuple(c + nx * w), tuple(c - nx * w))
    a1, a2 = P(R_OUT + 24.0, 32.0)
    b1, b2 = P(R_OUT - 20.0, 7.0)
    fun = cv.poly_mask([a1, a2, b2, b1])
    fun = warp(fun, 0.6 * S, 7 * S, cv.r)
    solid = solidify(fun, S)
    block_drop(cv, solid, 3.0, 4.0)
    tapered_outline(cv, solid, 2.4, 4.6)
    fill_region(cv, solid, 0, 0, SOAKC, ang=am + 20, nib=5.6, over=1.0, miss=(1.2, 0.9), alpha=0.97, jit=0.3, clip=0.6)
    for q in range(3):
        p0 = pol(CT, R_OUT + 17 - q * 14, am - 6 + q * 3)
        p1 = pol(CT, R_OUT + 13 - q * 14, am + 6 - q * 3)
        ballpoint(cv, [p0, p1], (220, 236, 255), 1.3, 0.8, wob=0.1, taper=(0.1, 0.3))
    # the overflow chevron shrinks into the funnel mouth
    pts = [pol(CT, R_OUT + 31.0, am - 7), pol(CT, R_OUT + 26.0, am), pol(CT, R_OUT + 31.0, am + 7)]
    ballpoint(cv, pts, INK, 8.0, 1.0, wob=0.1, wl=12, taper=(0, 0))
    marker(cv, pts, HARMC, w=3.8, alpha=1.0, wob=0.1, wl=12, taper=(0, 0), grain=0.0, rough=0.0, pool=0.0)
