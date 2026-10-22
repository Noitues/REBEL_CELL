"""Slender classical statues (v2): lofted rings and tubes, contrapposto, athletic or draped. Pure geometry into a DAcc
(deco_restyle). Local frame: x = the figure's right, y = forward, z up; `facing` is the world angle of forward (radians)."""
import math
import sys

sys.dont_write_bytecode = True


def _frame(origin, facing):
    fx, fy = math.cos(facing), math.sin(facing)
    rx, ry = fy, -fx

    def L(x, y, z):
        return (origin[0] + x * rx + y * fx, origin[1] + x * ry + y * fy, origin[2] + z)
    return L


def _loft(acc, rings, cap_top=True, cap_bot=False):
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for j in range(n):
            k = (j + 1) % n
            acc.face([a[j], a[k], b[k], b[j]])
    if cap_top:
        acc.face(list(reversed(rings[-1])))
    if cap_bot:
        acc.face(list(rings[0]))


SEG = 12          # ring points (v5 raises these for smooth silhouettes)
TUBE = 8


def _ellipse_ring(L, z, rx, ry, cx=0.0, cy=0.0, n=None):
    n = n or SEG
    return [L(cx + rx * math.cos(2 * math.pi * j / n), cy + ry * math.sin(2 * math.pi * j / n), z) for j in range(n)]


def _tube(acc, L, pts, radii, n=None):
    n = n or TUBE
    """A round tube through local points (x, y, z) with a radius at each."""
    W = [L(*p) for p in pts]
    rings = []
    for i, p in enumerate(W):
        a = W[max(0, i - 1)]
        b = W[min(len(W) - 1, i + 1)]
        t = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ln = math.sqrt(sum(c * c for c in t)) or 1.0
        t = tuple(c / ln for c in t)
        up = (0.0, 0.0, 1.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
        u = (t[1] * up[2] - t[2] * up[1], t[2] * up[0] - t[0] * up[2], t[0] * up[1] - t[1] * up[0])
        ul = math.sqrt(sum(c * c for c in u)) or 1.0
        u = tuple(c / ul for c in u)
        v = (t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0])
        r = radii[i]
        rings.append([tuple(p[k] + r * (math.cos(2 * math.pi * j / n) * u[k] + math.sin(2 * math.pi * j / n) * v[k]) for k in range(3))
                      for j in range(n)])
    _loft(acc, rings, True, True)


def _bar(acc, p0, p1, w):
    acc.bar(p0, p1, w)


def statue(acc, origin, H, facing, kind="athlete", pose=0):
    """origin = foot centre (x, y, z); H = total height in scene units. kind: athlete | draped. pose 0..3 varies the arms."""
    L = _frame(origin, facing)
    s = 1.0 if pose % 2 == 0 else -1.0                       # mirror the contrapposto
    h = H
    if kind == "draped":
        prof = [(0.00, .21, .15, 0.00, 0.00), (0.05, .20, .145, 0.00, 0.00), (0.20, .165, .12, 0.01 * s, 0.01), (0.34, .17, .12, 0.03 * s, 0.0),
                (0.50, .15, .11, 0.025 * s, 0.0), (0.60, .125, .095, 0.0, 0.0), (0.68, .14, .095, -0.015 * s, 0.0),
                (0.76, .165, .09, -0.03 * s, 0.0), (0.80, .12, .08, -0.03 * s, 0.0), (0.82, .05, .05, -0.03 * s, 0.0)]
        rings = [_ellipse_ring(L, z * h, rx * h, ry * h, cx * h, cy * h) for (z, rx, ry, cx, cy) in prof]
        _loft(acc, rings, False)
        # a hanging fold of cloth down one side
        _tube(acc, L, [(-.16 * s * h, .02 * h, .74 * h), (-.19 * s * h, .06 * h, .45 * h), (-.18 * s * h, .06 * h, .08 * h)],
              [.035 * h, .045 * h, .05 * h])
    else:
        # legs: weight on one, the other relaxed and back
        a = .065 * s
        _tube(acc, L, [(a * h, 0, .50 * h), (a * h, .005 * h, .27 * h), (a * h * 0.9, 0, .035 * h)], [.075 * h, .052 * h, .03 * h])
        _tube(acc, L, [(-a * h, 0, .50 * h), (-1.35 * a * h, .075 * h, .28 * h), (-1.5 * a * h, -.07 * h, .035 * h)],
              [.075 * h, .05 * h, .03 * h])
        prof = [(0.48, .115, .085, .01 * s, 0.0), (0.55, .11, .08, 0.0, 0.0), (0.63, .105, .075, -.01 * s, 0.0), (0.71, .150, .085, -.02 * s, 0.0),
                (0.77, .165, .085, -.03 * s, 0.0), (0.80, .09, .07, -.03 * s, 0.0), (0.82, .05, .05, -.03 * s, 0.0)]
        rings = [_ellipse_ring(L, z * h, rx * h, ry * h, cx * h, cy * h) for (z, rx, ry, cx, cy) in prof]
        _loft(acc, rings, False)
        # a short cloth over the hips
        rings2 = [_ellipse_ring(L, z * h, rx * h, ry * h, cx * h, 0) for (z, rx, ry, cx) in ((0.40, .125, .09, .0), (0.47, .12, .09, 0.0), (0.50, .115, .085, .0))]
        _loft(acc, rings2, False)
    # neck and head
    cxh = -.03 * s * h
    head = [(0.82, .05, .05), (0.86, .045, .048), (0.875, .06, .07), (0.91, .075, .085), (0.955, .07, .082), (0.985, .045, .055), (1.0, .018, .02)]
    _loft(acc, [_ellipse_ring(L, z * h, rx * h, ry * h, cxh, .01 * h) for (z, rx, ry) in head])
    # arms
    sh = (.17 * h * s, 0.0, .765 * h)
    sh2 = (-.17 * h * s, 0.0, .765 * h)
    if pose in (0, 1):                     # raised arm with a spear / torch, other arm down
        _tube(acc, L, [(sh[0] + cxh, 0, sh[2]), (.26 * h * s, .02 * h, .85 * h), (.27 * h * s, .05 * h, 1.0 * h)], [.04 * h, .033 * h, .026 * h])
        a0, a1 = L(.27 * h * s, .05 * h, .22 * h), L(.27 * h * s, .05 * h, 1.22 * h)
        acc.bar(a0, a1, .018 * h)
        _tube(acc, L, [(sh2[0] + cxh, 0, sh2[2]), (-.2 * h * s, .03 * h, .60 * h), (-.15 * h * s, .12 * h, .52 * h)], [.038 * h, .03 * h, .024 * h])
    else:                                  # arm out holding a wreath, other bent to the chest
        _tube(acc, L, [(sh[0] + cxh, 0, sh[2]), (.27 * h * s, .09 * h, .72 * h), (.30 * h * s, .19 * h, .66 * h)], [.04 * h, .032 * h, .025 * h])
        _tube(acc, L, [(sh2[0] + cxh, 0, sh2[2]), (-.22 * h * s, .06 * h, .66 * h), (-.08 * h * s, .10 * h, .70 * h)], [.038 * h, .03 * h, .024 * h])
        # a laurel ring in the outstretched hand
        n = SEG
        c = (.30 * h * s, .19 * h, .72 * h)
        rr = .07 * h
        pts = [L(c[0] + rr * math.cos(2 * math.pi * j / n), c[1], c[2] + rr * math.sin(2 * math.pi * j / n)) for j in range(n + 1)]
        for p0, p1 in zip(pts[:-1], pts[1:]):
            acc.bar(p0, p1, .016 * h)
