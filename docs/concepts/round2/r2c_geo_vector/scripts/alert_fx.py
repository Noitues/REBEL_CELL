"""High-suspicion extras: faceted searchlight beams, helicopters, drones, roof alarms."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import SS, R, ramp, toner, facet, bil, tri, NEON
from city import inter, LX, LY

BEAM = R('#6a0a18', '#b81c2c', '#f04a4a', '#ff9a8a', '#fff0e8')
GUN = R('#050204', '#120810', '#22141e', '#3a2430', '#5a3a44')


def beam(d, cam, src, g, r, seed):
    ca, sa = cam.ca, cam.sa
    left = cam.p(g[0] - r * ca, g[1] + r * sa, 0)
    right = cam.p(g[0] + r * ca, g[1] - r * sa, 0)
    facet(d, bil([src, src, right, left]), 4, 8, toner(BEAM, 0.72, gu=0.25, gv=-0.2, var=0.12, flip=0.2, alpha=(85, 165)),
          ('beam', seed), 0.35)
    facet(d, lambda u, v: cam.p(g[0] + r * v * math.cos(u * 2 * math.pi), g[1] + r * v * math.sin(u * 2 * math.pi), 0.1),
          10, 2, toner(BEAM, 0.85, var=0.1, flip=0.2, alpha=(150, 215)), ('spot', seed), 0.2, wrap_u=True)


def heli(d, x, y, s, seed, flip=1):
    rc = random.Random(str(seed))
    f = flip

    def P(px, py):
        return (x + px * s * f, y + py * s)
    body = [P(-1.0, -0.2), P(0.2, -0.45), P(0.9, -0.1), P(0.6, 0.35), P(-0.6, 0.35)]
    # body as fan of triangles
    c = P(0, 0)
    for k in range(len(body)):
        a, b = body[k], body[(k + 1) % len(body)]
        tri(d, [a, b, c], ramp(GUN, 0.35 + 0.5 * rc.random()))
    # cockpit glass
    tri(d, [P(0.2, -0.45), P(0.9, -0.1), P(0.45, -0.05)], ramp(NEON['red'], 0.55))
    tri(d, [P(0.45, -0.05), P(0.9, -0.1), P(0.6, 0.2)], ramp(NEON['red'], 0.3))
    # tail
    tri(d, [P(-0.9, -0.15), P(-2.4, -0.25), P(-0.8, 0.2)], ramp(GUN, 0.55))
    tri(d, [P(-2.4, -0.25), P(-2.6, -0.8), P(-2.2, -0.2)], ramp(GUN, 0.7))
    # rotor blades (thin triangles)
    tri(d, [P(0.0, -0.5), P(-2.2, -0.62), P(-2.2, -0.55)], ramp(GUN, 0.8))
    tri(d, [P(0.0, -0.5), P(2.0, -0.44), P(2.0, -0.38)], ramp(GUN, 0.9))
    tri(d, [P(-0.1, -0.45), P(0.1, -0.45), P(0.0, -0.6)], ramp(GUN, 0.95))
    # lights
    for (px, py, st) in ((-2.4, -0.3, NEON['red']), (0.5, 0.36, NEON['amber'])):
        q = P(px, py)
        tri(d, [(q[0] - 6, q[1]), (q[0], q[1] - 7), (q[0] + 6, q[1])], ramp(st, 0.9))
        tri(d, [(q[0] - 6, q[1]), (q[0], q[1] + 7), (q[0] + 6, q[1])], ramp(st, 0.6))


def drone(d, x, y, s, seed):
    rc = random.Random(str(seed))
    pts = [(x, y - s), (x + s * 1.3, y), (x, y + s * 0.7), (x - s * 1.3, y)]
    tri(d, [pts[0], pts[1], (x, y)], ramp(GUN, 0.8))
    tri(d, [pts[1], pts[2], (x, y)], ramp(GUN, 0.4))
    tri(d, [pts[2], pts[3], (x, y)], ramp(GUN, 0.3))
    tri(d, [pts[3], pts[0], (x, y)], ramp(GUN, 0.65))
    for sx in (-1, 1):
        a = (x + sx * s * 1.3, y)
        tri(d, [a, (a[0] + sx * s * 0.9, a[1] - s * 0.5), (a[0] + sx * s * 0.9, a[1] - s * 0.2)], ramp(GUN, 0.9))
    tri(d, [(x - s * 0.45, y + s * 0.1), (x + s * 0.45, y + s * 0.1), (x, y + s * 0.55)], ramp(NEON['red'], 0.85))


def beacon(d, x, y, r, seed):
    rc = random.Random(str(seed))
    n = 8
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        rr = r * (1.0 if k % 2 == 0 else 0.55)
        p = (x + rr * math.cos(am), y + rr * 0.8 * math.sin(am))
        q0 = (x + r * 0.3 * math.cos(a0), y + r * 0.24 * math.sin(a0))
        q1 = (x + r * 0.3 * math.cos(a1), y + r * 0.24 * math.sin(a1))
        tri(d, [q0, p, (x, y)], ramp(NEON['red'], 0.5 + 0.4 * rc.random()))
        tri(d, [p, q1, (x, y)], ramp(NEON['red'], 0.3 + 0.4 * rc.random()))


def apply(img, cam, cp, items):
    # searchlights first (translucent faceted overlay), then solid aircraft and alarms
    base = img.convert('RGBA')
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    helis = [((300.0, 250.0), inter(2, 3), 3.0, -1), ((905.0, 175.0), inter(4, 2), 2.7, 1),
             ((1590.0, 250.0), inter(7, 3), 2.6, 1)]
    drones_lit = [((1210.0, 150.0), (inter(3, 1)[0] + 2.0, inter(3, 1)[1] + 1.2), 1.6),
                  ((620.0, 120.0), inter(2, 1), 1.4)]
    for n, (src, g, r, fl) in enumerate(helis):
        beam(od, cam, src, g, r, n)
    for n, (src, g, r) in enumerate(drones_lit):
        beam(od, cam, src, g, r, 10 + n)
    img = Image.alpha_composite(base, ov).convert('RGB')
    d = ImageDraw.Draw(img)
    # roof alarm beacons on the tallest buildings
    roofs = [p for it in items for p in it['prims'] if p[0] == 'box' and p[6] > 6.0]
    roofs.sort(key=lambda p: (-p[6], p[10]))
    for n, p in enumerate(roofs[:10]):
        x0, y0, x1, y1, z1 = p[1], p[2], p[3], p[4], p[6]
        sx, sy = cam.p((x0 + x1) / 2, (y0 + y1) / 2, z1 + 0.2)
        beacon(d, sx, sy, 18, ('bc', n))
    for n, (src, g, r, fl) in enumerate(helis):
        heli(d, src[0], src[1], 30, ('heli', n), fl)
    for n, (src, g, r) in enumerate(drones_lit):
        drone(d, src[0], src[1], 16, ('dl', n))
    rng = random.Random(99)
    for n in range(12):
        sx = rng.uniform(420, 1700)
        sy = rng.uniform(110, 330)
        drone(d, sx, sy, rng.uniform(10, 14), ('dr', n))
    return img
