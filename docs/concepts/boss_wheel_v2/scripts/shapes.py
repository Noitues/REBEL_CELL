"""Boss Wheel v2: a tiny 'skeleton + flesh' drawing helper for silhouettes.

A Pen draws into an L mask at a scale k (pixels per figure unit) with an origin offset, so figures are authored in
their own unit box and drawn at any size. Shapes: blob (closed Catmull-Rom), limb (tapered stroke along a spline),
bone chains from joint angles, ellipses, polygons. Every shape can be drawn with fill 255 (add) or 0 (cut).
"""
import math

from PIL import Image, ImageDraw

from bw_kit import catmull, stroke_poly


class Pen:
    def __init__(self, size, k=1.0, ox=0.0, oy=0.0, flip=False, base=None):
        self.m = base if base is not None else Image.new("L", size, 0)
        self.d = ImageDraw.Draw(self.m)
        self.k, self.ox, self.oy, self.flip = k, ox, oy, flip
        self.W = size[0]

    def P(self, x, y):
        if self.flip:
            x = -x
        return (self.ox + x * self.k, self.oy + y * self.k)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def blob(self, pts, fill=255, n=8):
        self.d.polygon(self.Ps(catmull(pts, n, True)), fill=fill)

    def poly(self, pts, fill=255):
        self.d.polygon(self.Ps(pts), fill=fill)

    def limb(self, pts, w0, w1=None, fill=255, n=8, caps=True):
        w1 = w0 if w1 is None else w1
        cl = catmull(pts, n, False) if len(pts) > 2 else list(pts)
        if len(cl) == 2:
            (x0, y0), (x1, y1) = cl
            cl = [(x0 + (x1 - x0) * t / 6, y0 + (y1 - y0) * t / 6) for t in range(7)]
        poly = stroke_poly(cl, w0, w1)
        self.d.polygon(self.Ps(poly), fill=fill)
        if caps:
            self.dot(cl[0], w0 / 2, fill)
            self.dot(cl[-1], w1 / 2, fill)

    def dot(self, c, r, fill=255):
        x, y = self.P(*c)
        rr = r * self.k
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill)

    def ell(self, cx, cy, rx, ry, fill=255, ang=0.0, n=48):
        a = math.radians(ang)
        pts = [(cx + rx * math.cos(t) * math.cos(a) - ry * math.sin(t) * math.sin(a),
                cy + rx * math.cos(t) * math.sin(a) + ry * math.sin(t) * math.cos(a))
               for t in [2 * math.pi * i / n for i in range(n)]]
        self.poly(pts, fill)

    def line(self, pts, w, fill=255):
        self.d.line(self.Ps(pts), fill=fill, width=max(1, int(round(w * self.k))), joint="curve")

    def rrect(self, x0, y0, x1, y1, r, fill=255):
        a, b = self.P(x0, y0), self.P(x1, y1)
        xs, ys = sorted([a[0], b[0]]), sorted([a[1], b[1]])
        self.d.rounded_rectangle([xs[0], ys[0], xs[1], ys[1]], radius=r * self.k, fill=fill)


def chain(root, segs):
    """Joint positions from a root and [(length, absolute angle deg)] (0 deg = +x, 90 = down)."""
    pts = [root]
    x, y = root
    for ln, ang in segs:
        a = math.radians(ang)
        x, y = x + ln * math.cos(a), y + ln * math.sin(a)
        pts.append((x, y))
    return pts


def leg(p, hip, l1, l2, l3, a1, a2, a3, w0, w1, w2, fill=255, hoof=None):
    """Three-segment animal leg (upper, lower, cannon/paw) drawn as tapered limbs with joint dots."""
    j = chain(hip, [(l1, a1), (l2, a2), (l3, a3)])
    p.limb([j[0], j[1]], w0, w1, fill)
    p.limb([j[1], j[2]], w1, w2, fill)
    p.limb([j[2], j[3]], w2, w2 * 0.9, fill)
    if hoof:
        hx, hy = j[3]
        p.blob([(hx - hoof * 0.7, hy - hoof * 0.3), (hx + hoof, hy - hoof * 0.5), (hx + hoof * 1.1, hy + hoof * 0.6),
                (hx - hoof * 0.8, hy + hoof * 0.6)], fill)
    return j
