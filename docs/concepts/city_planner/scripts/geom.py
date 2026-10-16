"""Geometry + noise helpers for the city planner maps (pure python / numpy)."""
import math
import random

import numpy as np

TAU = math.pi * 2


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def plen(p):
    return sum(dist(p[i], p[i + 1]) for i in range(len(p) - 1))


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def rot(pt, ang, c=(0.0, 0.0)):
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def _cr(p0, p1, p2, p3, t, alpha=0.5):
    """Centripetal Catmull-Rom (Barry-Goldman) point at t in [0,1] between p1 and p2."""
    def tj(ti, a, b):
        d = dist(a, b)
        return ti + max(d, 1e-6) ** alpha
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    tt = t1 + (t2 - t1) * t
    def L(a, b, ta, tb):
        w = (tt - ta) / (tb - ta)
        return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)
    A1 = L(p0, p1, t0, t1)
    A2 = L(p1, p2, t1, t2)
    A3 = L(p2, p3, t2, t3)
    B1 = L(A1, A2, t0, t2)
    B2 = L(A2, A3, t1, t3)
    return L(B1, B2, t1, t2)


def catmull(pts, closed=False, step=3.0):
    pts = [tuple(p) for p in pts]
    if len(pts) < 3:
        return resample(pts, step)
    if closed:
        P = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        P = [(2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])] + pts + \
            [(2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])]
    out = []
    for i in range(1, len(P) - 2):
        p1, p2 = P[i], P[i + 1]
        n = max(2, int(dist(p1, p2) / step))
        for k in range(n):
            out.append(_cr(P[i - 1], p1, p2, P[i + 2], k / n))
    if not closed:
        out.append(pts[-1])
    return out


def resample(p, step):
    if len(p) < 2:
        return list(p)
    out = [p[0]]
    acc = 0.0
    for i in range(len(p) - 1):
        a, b = p[i], p[i + 1]
        d = dist(a, b)
        if d == 0:
            continue
        pos = step - acc
        while pos <= d:
            t = pos / d
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            pos += step
        acc = d - (pos - step)
    if dist(out[-1], p[-1]) > 1e-6:
        out.append(p[-1])
    return out


def cum(p):
    c = [0.0]
    for i in range(len(p) - 1):
        c.append(c[-1] + dist(p[i], p[i + 1]))
    return c


def pt_at(p, s, c=None):
    """Point and tangent angle at arclength s."""
    c = c or cum(p)
    s = max(0.0, min(c[-1], s))
    for i in range(len(p) - 1):
        if c[i + 1] >= s:
            d = c[i + 1] - c[i]
            t = 0 if d == 0 else (s - c[i]) / d
            a, b = p[i], p[i + 1]
            return ((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t),
                    math.atan2(b[1] - a[1], b[0] - a[0]))
    return p[-1], 0.0


def sub(p, f0, f1):
    """Sub-polyline between arclength fractions f0..f1."""
    c = cum(p)
    L = c[-1]
    s0, s1 = f0 * L, f1 * L
    out = [pt_at(p, s0, c)[0]]
    for i in range(len(p)):
        if s0 < c[i] < s1:
            out.append(p[i])
    out.append(pt_at(p, s1, c)[0])
    return out


def offset_line(p, d):
    out = []
    n = len(p)
    for i in range(n):
        a = p[max(0, i - 1)]
        b = p[min(n - 1, i + 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        out.append((p[i][0] - math.sin(ang) * d, p[i][1] + math.cos(ang) * d))
    return out


def dashes(p, on, off, phase=0.0):
    """Split polyline into dash sub-polylines."""
    c = cum(p)
    L = c[-1]
    out = []
    s = -phase
    while s < L:
        a, b = max(0.0, s), min(L, s + on)
        if b > a:
            seg = [pt_at(p, a, c)[0]]
            for i in range(len(p)):
                if a < c[i] < b:
                    seg.append(p[i])
            seg.append(pt_at(p, b, c)[0])
            out.append(seg)
        s += on + off
    return out


def circle_pts(cx, cy, r, n=72):
    return [(cx + r * math.cos(TAU * i / n), cy + r * math.sin(TAU * i / n)) for i in range(n)]


def ellipse_pts(cx, cy, rx, ry, ang=0.0, n=72):
    out = []
    for i in range(n):
        a = TAU * i / n
        out.append(rot((cx + rx * math.cos(a), cy + ry * math.sin(a)), ang, (cx, cy)))
    return out


def arc_pts(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def rect_pts(cx, cy, w, h, ang=0.0):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [rot((cx + x, cy + y), ang, (cx, cy)) for x, y in pts]


def blob(cx, cy, rx, ry, rng, amp=0.15, n=14, ang=0.0):
    """Irregular closed blob, returned as control points (smooth with catmull)."""
    pts = []
    for i in range(n):
        a = TAU * i / n
        k = 1 + rng.uniform(-amp, amp)
        pts.append(rot((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)), ang, (cx, cy)))
    return pts


def seg_intersections(A, B):
    """All intersection points of polylines A and B (numpy vectorised)."""
    a = np.array(A, dtype=float)
    b = np.array(B, dtype=float)
    p = a[:-1][:, None, :]
    r = (a[1:] - a[:-1])[:, None, :]
    q = b[:-1][None, :, :]
    s = (b[1:] - b[:-1])[None, :, :]
    rxs = r[..., 0] * s[..., 1] - r[..., 1] * s[..., 0]
    qp = q - p
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (qp[..., 0] * s[..., 1] - qp[..., 1] * s[..., 0]) / rxs
        u = (qp[..., 0] * r[..., 1] - qp[..., 1] * r[..., 0]) / rxs
    ok = (np.abs(rxs) > 1e-9) & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
    out = []
    for i, j in zip(*np.nonzero(ok)):
        pt = p[i, 0] + t[i, j] * r[i, 0]
        ang_a = math.atan2(r[i, 0, 1], r[i, 0, 0])
        ang_b = math.atan2(s[0, j, 1], s[0, j, 0])
        out.append(((float(pt[0]), float(pt[1])), ang_a, ang_b))
    return out


class Noise:
    """Cheap smooth fractal noise from random sinusoids. Returns roughly -1..1."""

    def __init__(self, seed=1, octaves=4, wl=200.0, gain=0.55):
        rng = random.Random(seed)
        self.t = []
        amp = 1.0
        tot = 0.0
        for _ in range(octaves):
            for _k in range(3):
                a = rng.uniform(0, TAU)
                self.t.append((math.cos(a) * TAU / wl, math.sin(a) * TAU / wl, rng.uniform(0, TAU), amp))
                tot += amp
            wl *= 0.5
            amp *= gain
        self.norm = tot / 1.6

    def __call__(self, x, y):
        v = 0.0
        for kx, ky, ph, amp in self.t:
            v += amp * math.sin(kx * x + ky * y + ph)
        return v / self.norm

    def np(self, X, Y):
        v = np.zeros_like(X, dtype=float)
        for kx, ky, ph, amp in self.t:
            v += amp * np.sin(kx * X + ky * Y + ph)
        return v / self.norm


def jitter_line(pts, noise, amp, step=3.0):
    """Displace a dense polyline along its normal by noise (for natural coasts, rivers)."""
    p = resample(pts, step)
    out = []
    n = len(p)
    L = plen(p)
    c = cum(p)
    for i, pt in enumerate(p):
        a = p[max(0, i - 1)]
        b = p[min(n - 1, i + 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        taper = min(1.0, c[i] / 40.0, (L - c[i]) / 40.0)
        d = noise(pt[0], pt[1]) * amp * taper
        out.append((pt[0] - math.sin(ang) * d, pt[1] + math.cos(ang) * d))
    return out
