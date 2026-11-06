"""js_doodle: polyline generators for the Jinx-scribble marks (stars, X marks, arrows, tallies, spirals, crowns, crude faces, bolts).
Each returns a list of polylines [(x, y), ...] in a local frame around (cx, cy); the caller strokes them with its own brush."""
import math
import numpy as np


def rot(pts, cx, cy, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def star5(cx, cy, r, a=-90, r_=None):
    """one continuous pentagram scribble (never closed neatly)"""
    pts = []
    for k in range(6):
        t = math.radians(a + k * 144)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    pts[-1] = (pts[-1][0] + r * 0.12, pts[-1][1] - r * 0.1)
    return [pts]


def star4(cx, cy, r, a=0):
    out = []
    for k in range(2):
        t = math.radians(a + k * 90)
        out.append([(cx - r * math.cos(t), cy - r * math.sin(t)), (cx + r * math.cos(t), cy + r * math.sin(t))])
    return out


def xmark(cx, cy, r, a=8):
    return [rot([(cx - r, cy - r * 0.9), (cx + r, cy + r * 0.9)], cx, cy, a), rot([(cx + r * 0.9, cy - r), (cx - r * 0.9, cy + r * 1.05)], cx, cy, a)]


def arrow(p0, p1, curve=0.18, head=0.28, n=14):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        t = i / n
        b = math.sin(math.pi * t) * curve * L
        pts.append((x0 + dx * t + nx * b, y0 + dy * t + ny * b))
    # tangent at the end
    tx, ty = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]
    tl = math.hypot(tx, ty) + 1e-6
    tx, ty = tx / tl, ty / tl
    hl = head * L
    h1 = (x1 - tx * hl + ty * hl * 0.6, y1 - ty * hl - tx * hl * 0.6)
    h2 = (x1 - tx * hl - ty * hl * 0.6, y1 - ty * hl + tx * hl * 0.6)
    return [pts, [h1, (x1, y1), h2]]


def tally(cx, cy, n=5, h=10, gap=3.4, a=-6):
    out = []
    x0 = cx - (min(n, 4) - 1) * gap / 2
    for i in range(min(n, 4)):
        out.append(rot([(x0 + i * gap, cy - h / 2), (x0 + i * gap + 0.4, cy + h / 2)], cx, cy, a))
    if n >= 5:
        out.append(rot([(x0 - gap * 0.9, cy + h * 0.28), (x0 + 3 * gap + gap * 0.9, cy - h * 0.28)], cx, cy, a))
    return out


def spiral(cx, cy, r, turns=2.2, a=0):
    pts = []
    n = int(30 * turns)
    for i in range(n + 1):
        t = i / n
        pts.append((cx + r * t * math.cos(math.radians(a + t * turns * 360)), cy + r * t * math.sin(math.radians(a + t * turns * 360))))
    return [pts]


def crown(cx, cy, w, h, a=-8):
    pts = [(cx - w / 2, cy + h / 2), (cx - w / 2 - 1, cy - h / 2), (cx - w / 4, cy), (cx, cy - h / 2 - 2), (cx + w / 4, cy), (cx + w / 2 + 1, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2 + 1)]
    return [rot(pts, cx, cy, a)]


def bolt(cx, cy, h, a=10):
    pts = [(cx + h * 0.18, cy - h / 2), (cx - h * 0.2, cy - h * 0.02), (cx + h * 0.12, cy + h * 0.02), (cx - h * 0.22, cy + h / 2)]
    return [rot(pts, cx, cy, a)]


def zig(p0, p1, n=5, amp=3.0):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    pts = [(x0, y0)]
    for i in range(1, n * 2):
        t = i / (n * 2)
        s = amp if i % 2 else -amp
        pts.append((x0 + dx * t + nx * s, y0 + dy * t + ny * s))
    pts.append((x1, y1))
    return [pts]


def circle_s(cx, cy, r, a0=0, over=40, n=40, squash=1.0):
    pts = []
    for i in range(n + 1):
        t = a0 + (360 + over) * i / n
        rr = r * (1 + 0.04 * math.sin(math.radians(t * 2.0)) + 0.06 * i / n)
        pts.append((cx + rr * math.cos(math.radians(t)), cy + rr * squash * math.sin(math.radians(t))))
    return [pts]


def face(cx, cy, r, mood='grin', a=0):
    """crude face: wobbly circle, X or dot eyes, zig-zag grin"""
    out = circle_s(cx, cy, r, a0=200, over=30, squash=1.05)
    ex = r * 0.38
    ey = -r * 0.22
    out += xmark(cx - ex, cy + ey, r * 0.17, a=0)
    out.append([(cx + ex - r * 0.16, cy + ey - r * 0.16), (cx + ex + r * 0.16, cy + ey + r * 0.16)])
    out.append([(cx + ex + r * 0.16, cy + ey - r * 0.16), (cx + ex - r * 0.16, cy + ey + r * 0.16)])
    m = []
    for i in range(7):
        t = i / 6
        m.append((cx - r * 0.5 + r * t, cy + r * 0.34 + (r * 0.12 if i % 2 else -r * 0.04) - r * 0.18 * math.sin(math.pi * t)))
    out.append(m)
    return [rot(p, cx, cy, a) for p in out]


def skull_dots(cx, cy, r):
    return circle_s(cx, cy, r, 0, 20, 24)


def heartbeat(x0, y, w, amp=8, n=1):
    pts = [(x0, y), (x0 + w * 0.3, y), (x0 + w * 0.38, y - amp), (x0 + w * 0.5, y + amp * 1.2), (x0 + w * 0.58, y - amp * 0.4), (x0 + w * 0.66, y), (x0 + w, y)]
    return [pts]
