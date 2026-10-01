"""S1 icon set: 9 slice types + 4 statuses, drawn at any size (cel facets + ink, small extrusion)."""
import math
from kit import *

PINK = R('#1e040e', '#4a0a24', '#8a1440', '#c42a62', '#e8588a', '#f490b4', '#fcd0e0')
SLICE_COL = {'ATTACK': RED, 'CRITICAL': RED, 'DEFEND': STEEL, 'SHIELD': CELL, 'EVADE': LIME, 'HEAL': PINK,
             'AFFLICT': PURP, 'DEPLOY': GOLD, 'MISS': METAL}


def U(cx, cy, s, ang=0.0):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return lambda pts: [(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in pts]


def iw(s):
    return max(1.1, s * 0.045)


def solid(d, pts, st, s, seed, off=True, **kw):
    if off and s >= 40:
        extrude(d, pts, (s * 0.03, s * 0.05), st, seed, ink=iw(s), front_kw=kw)
    else:
        shape(d, pts, st, seed, ink=iw(s), **kw)


def blade(d, cx, cy, s, st, seed, ang=45):
    p = U(cx, cy, s, ang)
    b = p([(0, -0.48), (0.09, -0.36), (0.08, 0.12), (-0.08, 0.12), (-0.09, -0.36)])
    solid(d, b, st, s, (seed, 'bl'), nu=6, nv=2)
    guard = p([(-0.24, 0.12), (0.24, 0.12), (0.22, 0.2), (-0.22, 0.2)])
    solid(d, guard, METAL, s, (seed, 'gd'), off=False)
    grip = p([(-0.05, 0.2), (0.05, 0.2), (0.05, 0.38), (-0.05, 0.38)])
    shape(d, grip, DARK, (seed, 'gr'), ink=iw(s) * 0.8)
    shape(d, p([(0, 0.38), (0.08, 0.44), (0, 0.5), (-0.08, 0.44)]), METAL, (seed, 'pm'), ink=iw(s) * 0.8)
    if s >= 40:
        a, b2 = p([(0.0, -0.4)])[0], p([(0.0, 0.08)])[0]
        line2(d, a, b2, max(1, s * 0.02), bcol(st, 2))


def star(cx, cy, r0, r1, n=8, a0=-math.pi / 2):
    return [(cx + (r1 if k % 2 == 0 else r0) * math.cos(a0 + math.pi * k / n),
             cy + (r1 if k % 2 == 0 else r0) * math.sin(a0 + math.pi * k / n)) for k in range(2 * n)]


def slice_icon(d, name, cx, cy, s, seed=None):
    seed = seed or (name, s)
    st = SLICE_COL[name]
    p = U(cx, cy, s)
    if name == 'ATTACK':
        blade(d, cx, cy, s, st, seed)
    elif name == 'CRITICAL':
        solid(d, star(cx, cy, s * 0.22, s * 0.5, 8), GOLD, s, (seed, 'st'), nu=16, nv=1)
        blade(d, cx, cy, s * 0.82, st, seed)
    elif name == 'DEFEND':
        sh = p([(-0.38, -0.4), (0.38, -0.4), (0.36, 0.06), (0, 0.46), (-0.36, 0.06)])
        solid(d, sh, st, s, seed, nu=10, nv=2)
        line2(d, p([(0, -0.34)])[0], p([(0, 0.38)])[0], max(1.2, s * 0.05), INK)
        line2(d, p([(-0.3, -0.06)])[0], p([(0.3, -0.06)])[0], max(1.2, s * 0.05), INK)
    elif name == 'SHIELD':
        hexo = circle_pts(cx, cy, s * 0.46, n=6, a0=math.pi / 6)
        solid(d, hexo, st, s, seed, nu=12, nv=2, form=1.2)
        hexi = circle_pts(cx, cy, s * 0.26, n=6, a0=math.pi / 6)
        shape(d, hexi, st, (seed, 'in'), ink=iw(s) * 0.8, bias=0.35)
        if s >= 40:
            tri(d, p([(-0.06, -0.12), (0.08, -0.04), (-0.02, 0.0)]), bcol(PAPER, 2))
    elif name == 'EVADE':
        for k, dx in enumerate((-0.2, 0.14)):
            ch = p([(dx - 0.16, -0.38), (dx + 0.06, -0.38), (dx + 0.3, 0), (dx + 0.06, 0.38), (dx - 0.16, 0.38),
                    (dx + 0.08, 0)])
            solid(d, ch, st, s, (seed, k), nu=6, nv=1)
        if s >= 40:
            line2(d, p([(-0.48, -0.2)])[0], p([(-0.34, -0.2)])[0], max(1.2, s * 0.04), bcol(st, 2))
            line2(d, p([(-0.48, 0.2)])[0], p([(-0.34, 0.2)])[0], max(1.2, s * 0.04), bcol(st, 2))
    elif name == 'HEAL':
        a, b = 0.14, 0.42
        cr = p([(-a, -b), (a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a),
                (-a, -a)])
        solid(d, cr, st, s, seed, nu=12, nv=1)
    elif name == 'AFFLICT':
        pts = [p([(0, -0.48)])[0]] + [(cx + s * 0.32 * math.cos(a), cy + s * 0.12 + s * 0.32 * math.sin(a)) for a in
                                       [math.radians(x) for x in range(-30, 211, 30)]]
        solid(d, pts, st, s, seed, nu=10, nv=2)
        if s >= 40:
            for dx in (-0.1, 0.1):
                shape(d, circle_pts(*p([(dx, 0.1)])[0], s * 0.06, n=5), DARK, (seed, dx), ink=0)
            line2(d, p([(-0.08, 0.26)])[0], p([(0.08, 0.26)])[0], max(1, s * 0.03), INK)
    elif name == 'DEPLOY':
        for sx in (-1, 1):
            arm = p([(sx * 0.1, -0.04), (sx * 0.42, -0.2), (sx * 0.44, -0.12), (sx * 0.12, 0.06)])
            shape(d, arm, METAL, (seed, 'arm', sx), ink=iw(s) * 0.8)
            rot = p([(sx * 0.42 - 0.18, -0.24), (sx * 0.42 + 0.18, -0.26), (sx * 0.42 + 0.18, -0.2),
                     (sx * 0.42 - 0.18, -0.18)])
            shape(d, rot, DARK, (seed, 'rot', sx), ink=iw(s) * 0.7)
        body = circle_pts(cx, cy + s * 0.06, s * 0.24, s * 0.2, n=6)
        solid(d, body, st, s, seed, nu=6, nv=2)
        shape(d, circle_pts(cx, cy + s * 0.12, s * 0.07, n=5), RED, (seed, 'eye'), ink=iw(s) * 0.6, bias=0.4)
        if s >= 40:
            for k in (-1, 1):
                line2(d, p([(k * 0.1, 0.26)])[0], p([(k * 0.16, 0.42)])[0], max(1.2, s * 0.03), INK)
    elif name == 'MISS':
        ring = circle_pts(cx, cy, s * 0.42, n=16)
        ringi = circle_pts(cx, cy, s * 0.26, n=16)
        for k in range(16):
            if k in (2, 3, 10, 11):
                continue
            q = [ringi[k], ring[k], ring[(k + 1) % 16], ringi[(k + 1) % 16]]
            quad_fill(d, q, st, 1 if k < 8 else 0, (seed, k), 1, 1)
            ink_line(d, ring[k], ring[(k + 1) % 16], iw(s) * 0.9, (seed, 'o', k))
            ink_line(d, ringi[k], ringi[(k + 1) % 16], iw(s) * 0.7, (seed, 'i', k))
        line2(d, p([(-0.34, 0.34)])[0], p([(0.34, -0.34)])[0], max(1.6, s * 0.08), INK)
        line2(d, p([(-0.34, 0.34)])[0], p([(0.34, -0.34)])[0], max(0.8, s * 0.04), bcol(RED, 2))


STATUS = {'CORRUPTED': False, 'OVERCLOCKED': True, 'ENCRYPTED': True, 'PARASITE': False}


def status_icon(d, name, cx, cy, s, seed=None):
    seed = seed or (name, s)
    helps = STATUS[name]
    p = U(cx, cy, s)
    if helps:
        frame = circle_pts(cx, cy, s * 0.48, n=8, a0=math.pi / 8)
        fst = LIME
    else:
        frame = star(cx, cy, s * 0.4, s * 0.5, 10)
        fst = RED
    solid(d, frame, fst, s, (seed, 'fr'), nu=16, nv=1)
    inner = circle_pts(cx, cy, s * 0.34, n=8, a0=math.pi / 8)
    shape(d, inner, DARK, (seed, 'in'), ink=iw(s) * 0.7, form=-0.4)
    q = U(cx, cy, s * 0.62)
    if name == 'CORRUPTED':
        for k, (dx, dy) in enumerate(((-0.08, -0.02), (0.1, 0.06))):
            half = q([(dx - 0.3, dy - 0.3 + k * 0.32), (dx + 0.3, dy - 0.3 + k * 0.32), (dx + 0.3, dy + 0.02 + k * 0.32),
                      (dx - 0.3, dy + 0.02 + k * 0.32)])
            shape(d, half, PURP, (seed, 'h', k), ink=iw(s) * 0.7)
        if s >= 40:
            line2(d, q([(-0.42, 0.06)])[0], q([(0.42, 0.06)])[0], max(1, s * 0.025), ramp(NEON['magenta'], 0.8))
    elif name == 'OVERCLOCKED':
        fl = q([(0, -0.46), (0.22, -0.1), (0.3, 0.2), (0.12, 0.42), (-0.12, 0.42), (-0.3, 0.2), (-0.18, -0.06),
                (-0.06, 0.06)])
        shape(d, fl, MER, (seed, 'fl'), ink=iw(s) * 0.8, bias=0.2)
        fi = q([(0.02, -0.06), (0.14, 0.18), (0.06, 0.36), (-0.08, 0.36), (-0.14, 0.18)])
        shape(d, fi, GOLD, (seed, 'fi'), ink=0, bias=0.5)
    elif name == 'ENCRYPTED':
        body = q([(-0.3, -0.04), (0.3, -0.04), (0.3, 0.4), (-0.3, 0.4)])
        arc = [q([(0.18 * math.cos(a), -0.04 + 0.24 * math.sin(a))])[0] for a in
               [math.pi + math.pi * k / 6 for k in range(7)]]
        for k in range(6):
            line2(d, arc[k], arc[k + 1], max(1.4, s * 0.06), INK)
            line2(d, arc[k], arc[k + 1], max(0.7, s * 0.03), bcol(METAL, 2))
        shape(d, body, CELL, (seed, 'lk'), ink=iw(s) * 0.8)
        shape(d, q([(-0.05, 0.1), (0.05, 0.1), (0.04, 0.28), (-0.04, 0.28)]), DARK, (seed, 'kh'), ink=0)
    elif name == 'PARASITE':
        for sy in (-1, 0, 1):
            for sx in (-1, 1):
                line2(d, q([(sx * 0.12, sy * 0.14)])[0], q([(sx * 0.42, sy * 0.24 - 0.04)])[0], max(1.2, s * 0.035), INK)
        body = circle_pts(*q([(0, 0.04)])[0], s * 0.62 * 0.22, s * 0.62 * 0.32, n=8)
        shape(d, body, PURP, (seed, 'bd'), ink=iw(s) * 0.8)
        shape(d, circle_pts(*q([(0, -0.34)])[0], s * 0.62 * 0.12, n=6), RED, (seed, 'hd'), ink=iw(s) * 0.7)
    # helps / hurts tab: arrow up (green) or down (red) at the lower right
    tx, ty = cx + s * 0.36, cy + s * 0.36
    tab = circle_pts(tx, ty, s * 0.16, n=6)
    shape(d, tab, LIME if helps else RED, (seed, 'tab'), ink=iw(s) * 0.8, bias=0.2)
    a = s * 0.09
    if helps:
        tri(d, [(tx - a, ty + a * 0.5), (tx + a, ty + a * 0.5), (tx, ty - a * 0.8)], INK)
    else:
        tri(d, [(tx - a, ty - a * 0.5), (tx + a, ty - a * 0.5), (tx, ty + a * 0.8)], INK)
