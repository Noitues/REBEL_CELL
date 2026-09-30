"""A one-point-perspective night alley built from big calm triangles, lit by its neon signs
(coloured spill on walls and ground, wet reflections, haze pools). Combat backdrop."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, tri, gradient, NEON, line2,
                     catenary, layer, composite, Lights)

WALL_L = R('#06050a', '#100c14', '#1a141e', '#261c28', '#342634', '#463242', '#5a4052')
WALL_R = R('#04060c', '#0a0e16', '#121824', '#1c2432', '#283240', '#36424e', '#48545e')
GROUND = R('#020206', '#06060e', '#0e0c18', '#181424', '#241e34', '#383048')

SIGNS = [('L', 0.08, 0.1, 0.45, 'magenta', False), ('L', 0.3, 0.15, 0.5, 'acid', True),
         ('L', 0.55, 0.2, 0.55, 'cyan', False), ('R', 0.12, 0.08, 0.4, 'sodium', False),
         ('R', 0.36, 0.2, 0.52, 'magenta', False), ('R', 0.62, 0.25, 0.58, 'cyan', False),
         ('L', 0.2, 0.62, 0.7, 'sodium', False), ('R', 0.05, 0.6, 0.66, 'acid', False)]


def draw_alley(seed='alley', far=(700, 250, 1220, 620)):
    fx0, fy0, fx1, fy1 = far
    img = gradient(lambda u, v: mix(hexc('#06060e'), hexc('#2a1430'), v)).convert('RGB')
    d = ImageDraw.Draw(img)
    rng = random.Random(str(seed))
    wl = [(0, -200), (fx0, fy0), (fx0, fy1), (0, H + 120)]
    wr = [(W, -200), (fx1, fy0), (fx1, fy1), (W, H + 120)]
    # sign geometry first: the signs light everything around them
    specs, lights = [], []
    for n, (side, u, va, vb, neon, broken) in enumerate(SIGNS):
        wq = wl if side == 'L' else wr
        du = 0.07 if vb - va > 0.15 else 0.2
        q = [bil(wq)(u, va), bil(wq)(u + du, va), bil(wq)(u + du, vb), bil(wq)(u, vb)]
        c = bil(q)(0.5, 0.5)
        size = abs(q[1][0] - q[0][0]) + abs(q[3][1] - q[0][1])
        lights.append((c, 180 + size * 0.9, ramp(NEON[neon], 0.65), 0.25 if broken else 0.55))
        specs.append((n, side, wq, u, du, va, vb, neon, broken, q))
    L = Lights(lights, cell=120.0)
    # far opening: sodium smog and distant tower silhouettes (big facets)
    facet(d, bil([(fx0, fy0 - 400), (fx1, fy0 - 400), (fx1, fy1), (fx0, fy1)]), 3, 3,
          lambda u, v, i, j, k, rc: ramp(R('#0a0814', '#1e1224', '#3a1e30', '#6a3430', '#a05a34'),
                                         0.2 + 0.7 * v ** 1.5 + rc.uniform(-0.04, 0.04)), (seed, 'far'), 0.3)
    x = fx0
    while x < fx1:
        w = rng.uniform(30, 70)
        top = rng.uniform(fy0 - 120, fy1 - 150)
        facet(d, bil([(x, top), (x + w, top), (x + w, fy1), (x, fy1)]), 1, 1,
              toner(R('#06040a', '#0e0a14', '#18101c', '#221824'), rng.uniform(0.2, 0.8), var=0.05), (seed, 'ft', x), 0.3)
        x += w * rng.uniform(0.7, 1.0)
    # walls: big calm facets, tinted by the signs
    for name, wq, st in (('L', wl, WALL_L), ('R', wr, WALL_R)):
        def cf(u, v, i, j, k, rc, name=name, st=st):
            t = 0.55 - 0.4 * u + 0.12 * (0.5 - v) + rc.uniform(-0.05, 0.05)
            if j % 2 == 1 and hsh(i, j, ord(name)) < 0.4:
                t -= 0.14
            if rc.random() < 0.06:
                return ramp(R('#140806', '#2e120a', '#4e2010', '#6e3418'), 0.3 + 0.5 * (1 - u))
            return ramp(st, t)
        facet(d, bil(wq), 6, 6, L.wrap(cf, bil(wq)), (seed, 'wall', name), 0.3)
    gq = [(fx0, fy1), (fx1, fy1), (W, H + 120), (0, H + 120)]

    def gf(u, v, i, j, k, rc):
        t = 0.3 + 0.3 * v + rc.uniform(-0.05, 0.05)
        if rc.random() < 0.1:
            t += 0.25
        return ramp(GROUND, t)
    facet(d, bil(gq), 6, 5, L.wrap(gf, bil(gq)), (seed, 'ground'), 0.35)
    # pipes and a fire escape
    for wq, vs in ((wl, (0.18, 0.21, 0.55)), (wr, (0.3, 0.33, 0.7))):
        for v in vs:
            a, b = bil(wq)(0, v), bil(wq)(1, v)
            line2(d, a, b, 7 if v != vs[1] else 4, ramp(R('#140a08', '#301810', '#582c18'), 0.5))
            line2(d, (a[0], a[1] - 2), (b[0], b[1] - 1), 1.5, ramp(R('#301810', '#7a4830'), 0.7))
    for k in range(5):
        u0, u1 = 0.15 + k * 0.08, 0.2 + k * 0.08
        line2(d, bil(wr)(u0, 0.35 + k * 0.02), bil(wr)(u1, 0.5 + k * 0.01), 3, ramp(WALL_R, 0.15))
    # signs: small dense facets
    lay, ld = layer(img)
    for (n, side, wq, u, du, va, vb, neon, broken, q) in specs:
        facet(d, bil(q), 1, 1, toner(R('#040406', '#0c0c10'), 0.5), (seed, 'sb', n), 0.0)
        st = NEON[neon]

        def sf(uu, vv, i, j, k, rc, st=st, broken=broken):
            if broken and rc.random() < 0.35:
                return None
            if broken and rc.random() < 0.3:
                return ramp(st, 0.2)
            return ramp(st, 0.7 + rc.uniform(-0.22, 0.25))
        facet(d, bil(q), 3 if du > 0.1 else 2, 12 if du < 0.1 else 3, sf, (seed, 'sg', n), 0.3)
        if broken:
            continue
        # wet reflection streak + haze pool on the ground below the sign
        foot = bil(wq)(u + du / 2, 1.0)
        if foot[1] > H + 60:
            foot = (foot[0], H - 10)
        toward = (960 - foot[0]) * 0.3
        rq = [(foot[0] - 26, foot[1] - 20), (foot[0] + 26, foot[1] - 20), (foot[0] + toward + 44, foot[1] + 220),
              (foot[0] + toward - 44, foot[1] + 220)]
        facet(ld, bil(rq), 2, 5, lambda uu, vv, i, j, k, rc, st=st: None if rc.random() < 0.2 else
              ramp(st, 0.7 + rc.uniform(-0.15, 0.2)) + (int(190 * (1 - vv) ** 1.2) + 20,), (seed, 'rf', n), 0.35)
        c = bil(q)(0.5, 0.75)
        facet(ld, polar(c[0], c[1], 150, 110, 0, 2 * math.pi, 0, 1), 7, 2,
              lambda uu, vv, i, j, k, rc, st=st: ramp(st, 0.5) + (int(55 * (1 - vv) + rc.uniform(0, 12)),),
              (seed, 'hz', n), 0.35, wrap_u=True)
    img = composite(img, lay)
    d = ImageDraw.Draw(img)
    for k in range(9):
        v1, v2 = rng.uniform(0.05, 0.5), rng.uniform(0.05, 0.5)
        u1, u2 = rng.uniform(0.0, 0.8), rng.uniform(0.0, 0.8)
        a, b = bil(wl)(u1, v1), bil(wr)(u2, v2)
        for s in range(rng.randint(1, 3)):
            catenary(d, a, (b[0], b[1] + s * 4), rng.uniform(40, 140) + s * 6, 2.0, ramp(WALL_L, 0.05), n=16)
    return img
