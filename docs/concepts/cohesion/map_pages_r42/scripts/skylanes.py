"""Round 38: the round 26 v4 sky lanes as data shared by Blender (car MODELS) and the post (streak cars).

Pure Python. Roads run along the game's avenues (lot lines) + the cloverleaf / stack / spiral loops, each at its own
height in world units (1 lot = 6 u). cars(t) places every car for loop time t (whole car gaps per loop: seamless).
"""
import math
import random

import layout36 as L

SKY_COLS = [(1.0, 0.27, 0.75), (0.31, 0.86, 1.0), (1.0, 0.77, 0.24), (0.67, 0.47, 1.0), (0.35, 1.0, 0.78), (1.0, 0.47, 0.24),
            (0.95, 0.95, 1.0)]


def _line(i0, j0, i1, j1, n=60):
    return [(i0 + (i1 - i0) * k / n, j0 + (j1 - j0) * k / n) for k in range(n + 1)]


def _circle(ci, cj, r, n=48):
    return [(ci + r * math.cos(2 * math.pi * k / n), cj + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


ROADS = [("A_low", _line(-95, 4, 95, 4), 22.0), ("A_high", _line(-95, 4.6, 70, 4.6), 34.0), ("B", _line(6, -95, 6, 95), 52.0),
         ("C", _line(-90, -5, 16, -5), 28.0), ("F", _line(-10, -95, -10, 95), 44.0), ("D", _line(-60, 43, 95, 43), 24.0),
         ("E", _line(17, 20, 17, 95), 40.0), ("G", _line(-95, 30, 60, 30), 30.0), ("H", _line(28, -95, 28, 30), 36.0),
         ("clover", _circle(-10, 4, 2.4), 33.0), ("stack", _circle(17, 43, 5.5), 62.0), ("spiral", _circle(16, -2.6, 2.4), 20.0)]
GAP = 14.0
SPEED_GAPS = 4


def _seg(pts):
    wp = [L.W(p) for p in pts]
    return [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(wp, wp[1:])]


def at(seg, s):
    for a, b, Ls in seg:
        if s <= Ls:
            u = s / Ls if Ls else 0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), ((b[0] - a[0]) / (Ls or 1), (b[1] - a[1]) / (Ls or 1))
        s -= Ls
    a, b, Ls = seg[-1]
    return b, ((b[0] - a[0]) / (Ls or 1), (b[1] - a[1]) / (Ls or 1))


def cars(t):
    """Every car: dict(x, y, z, dx, dy (heading), col, length, lane). Deterministic (seeded)."""
    rng = random.Random(2626)
    out = []
    for name, pts, z in ROADS:
        seg = _seg(pts)
        total = sum(s[2] for s in seg)
        if total < 1:
            continue
        n = int(total / GAP)
        for side in (-1, 1):
            off = rng.uniform(0, GAP)
            for c in range(n):
                skip = rng.random() < 0.22
                col = SKY_COLS[rng.randrange(len(SKY_COLS))]
                Lc = rng.uniform(8.0, 14.0)
                if skip:
                    continue
                s = (off + c * GAP + side * t * SPEED_GAPS * GAP) % total
                p, dv = at(seg, s)
                x, y = p[0] + dv[1] * side * 0.9, p[1] - dv[0] * side * 0.9
                out.append(dict(x=x, y=y, z=z, dx=dv[0] * side, dy=dv[1] * side, col=col, length=Lc, road=name))
    return out


def guide_dots(step=8.0):
    out = []
    for name, pts, z in ROADS:
        seg = _seg(pts)
        total = sum(s[2] for s in seg)
        s0 = 0.0
        while s0 < total:
            p, dv = at(seg, s0)
            for side in (-1, 1):
                out.append((p[0] + dv[1] * side * 1.6, p[1] - dv[0] * side * 1.6, z))
            s0 += step
    return out
