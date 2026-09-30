"""A one-point-perspective back alley built from triangles (combat backdrop and shop setting)."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, tri, gradient, NEON, line2, catenary,
                     layer, composite)

WALL_L = R('#070606', '#120e0c', '#1e1814', '#2c221c', '#3e3026', '#524034', '#6a5444')
WALL_R = R('#05070a', '#0c1014', '#141a20', '#1e262c', '#2a343a', '#3a464a', '#4e5a5c')
GROUND = R('#030304', '#08080a', '#101014', '#1a1a20', '#26262e', '#3a3842')


def wall_pt(wq, u, v):
    return bil(wq)(u, v)


def draw_alley(seed='alley', far=(700, 250, 1220, 620), signs=True, bright=1.0):
    fx0, fy0, fx1, fy1 = far
    img = gradient(lambda u, v: mix(hexc('#0a0a10'), hexc('#2a2018'), v)).convert('RGB')
    d = ImageDraw.Draw(img)
    rng = random.Random(str(seed))
    # far opening: sodium smog with distant tower silhouettes
    facet(d, bil([(fx0, fy0 - 400), (fx1, fy0 - 400), (fx1, fy1), (fx0, fy1)]), 6, 6,
          lambda u, v, i, j, k, rc: ramp(R('#0c0c14', '#1e1a20', '#3a2a22', '#6a4426', '#a0662c'), 0.2 + 0.7 * v ** 1.5
                                         + rc.uniform(-0.06, 0.06)), (seed, 'far'), 0.3)
    x = fx0
    while x < fx1:
        w = rng.uniform(20, 60)
        top = rng.uniform(fy0 - 120, fy1 - 150)
        facet(d, bil([(x, top), (x + w, top), (x + w, fy1), (x, fy1)]), 1, 3,
              toner(R('#06060a', '#0e0c12', '#18141a', '#221c20'), rng.uniform(0.2, 0.8), var=0.1), (seed, 'ft', x), 0.3)
        for _ in range(int(w * (fy1 - top) / 900)):
            lx, ly = rng.uniform(x + 3, x + w - 3), rng.uniform(top + 4, fy1 - 4)
            tri(d, [(lx, ly), (lx + 3, ly), (lx + 1.5, ly + 3)], ramp(NEON['sodium'], rng.uniform(0.3, 0.6)))
        x += w * rng.uniform(0.7, 1.0)
    # the two walls
    wl = [(0, -200), (fx0, fy0), (fx0, fy1), (0, H + 120)]
    wr = [(W, -200), (fx1, fy0), (fx1, fy1), (W, H + 120)]
    for name, wq, st in (('L', wl, WALL_L), ('R', wr, WALL_R)):
        def cf(u, v, i, j, k, rc, name=name, st=st):
            t = 0.6 - 0.45 * u + 0.15 * (0.5 - v) + rc.uniform(-0.07, 0.07)
            if j % 3 == 1 and hsh(i, j, ord(name)) < 0.5:
                t -= 0.18  # dark window recesses
            if hsh(i, ord(name), 9) < 0.3 and v > 0.4:
                t -= 0.1  # grime streaks
            if rc.random() < 0.08:
                return ramp(R('#140806', '#2e120a', '#4e2010', '#6e3418'), 0.3 + 0.6 * (1 - u))
            return ramp(st, t * bright)
        facet(d, bil(wq), 12, 12, cf, (seed, 'wall', name), 0.3)
    # ground: wet, faceted, sky shine
    gq = [(fx0, fy1), (fx1, fy1), (W, H + 120), (0, H + 120)]

    def gf(u, v, i, j, k, rc):
        t = 0.3 + 0.3 * v + rc.uniform(-0.08, 0.08)
        if rc.random() < 0.12:
            t += 0.3
        return ramp(GROUND, t)
    facet(d, bil(gq), 10, 8, gf, (seed, 'ground'), 0.35)
    # pipes running along the walls toward the vanishing point
    for wq, vs in ((wl, (0.18, 0.21, 0.55)), (wr, (0.3, 0.33, 0.7))):
        for v in vs:
            a, b = wall_pt(wq, 0, v), wall_pt(wq, 1, v)
            line2(d, a, b, 7 if v != vs[1] else 4, ramp(R('#1a0c08', '#3e1c10', '#6a3418'), 0.5))
            line2(d, (a[0], a[1] - 2), (b[0], b[1] - 1), 1.5, ramp(R('#3e1c10', '#8a5030'), 0.7))
    # fire escape zigzag on the right wall
    for k in range(5):
        u0, u1 = 0.15 + k * 0.08, 0.2 + k * 0.08
        line2(d, wall_pt(wr, u0, 0.35 + k * 0.02), wall_pt(wr, u1, 0.5 + k * 0.01), 3, ramp(WALL_R, 0.15))
    lay, ld = layer(img)
    if signs:
        # stacked vertical signs on both walls, some broken, with puddle reflections on the ground
        specs = [('L', 0.08, 0.1, 0.45, 'magenta', False), ('L', 0.3, 0.15, 0.5, 'acid', True),
                 ('L', 0.55, 0.2, 0.55, 'cyan', False), ('R', 0.12, 0.08, 0.4, 'sodium', False),
                 ('R', 0.36, 0.2, 0.52, 'magenta', True), ('R', 0.62, 0.25, 0.58, 'cyan', False),
                 ('L', 0.2, 0.62, 0.7, 'sodium', False)]
        for n, (side, u, va, vb, neon, broken) in enumerate(specs):
            wq = wl if side == 'L' else wr
            du = 0.07 if vb - va > 0.15 else 0.2
            q = [wall_pt(wq, u, va), wall_pt(wq, u + du, va), wall_pt(wq, u + du, vb), wall_pt(wq, u, vb)]
            facet(d, bil(q), 1, 1, toner(R('#040406', '#0c0c10'), 0.5), (seed, 'sb', n), 0.0)
            st = NEON[neon]

            def sf(uu, vv, i, j, k, rc, st=st, broken=broken):
                if broken and rc.random() < 0.35:
                    return None
                if broken and rc.random() < 0.3:
                    return ramp(st, 0.2)
                return ramp(st, 0.6 + rc.uniform(-0.25, 0.3))
            facet(d, bil(q), 2 if du > 0.1 else 1, 6 if du < 0.1 else 2, sf, (seed, 'sg', n), 0.3)
            if not broken:
                foot = wall_pt(wq, u + du / 2, 1.0)
                toward = (960 - foot[0]) * 0.25
                rq = [(foot[0] - 20, foot[1] - 10), (foot[0] + 20, foot[1] - 10), (foot[0] + toward + 30, foot[1] + 160),
                      (foot[0] + toward - 30, foot[1] + 160)]
                if foot[1] < H + 50:
                    facet(ld, bil(rq), 2, 4, lambda uu, vv, i, j, k, rc, st=st: None if rc.random() < 0.3 else
                          ramp(st, 0.55 + rc.uniform(-0.2, 0.2)) + (int(140 * (1 - vv)) + 20,), (seed, 'rf', n), 0.35)
    img = composite(img, lay)
    d = ImageDraw.Draw(img)
    # cables strung across the alley
    for k in range(9):
        v1, v2 = rng.uniform(0.05, 0.5), rng.uniform(0.05, 0.5)
        u1, u2 = rng.uniform(0.0, 0.8), rng.uniform(0.0, 0.8)
        a, b = wall_pt(wl, u1, v1), wall_pt(wr, u2, v2)
        for s in range(rng.randint(1, 3)):
            catenary(d, a, (b[0], b[1] + s * 4), rng.uniform(40, 140) + s * 6, 2.0, ramp(WALL_L, 0.05), n=16)
    return img
