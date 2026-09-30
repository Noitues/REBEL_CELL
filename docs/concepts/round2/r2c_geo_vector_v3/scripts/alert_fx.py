"""High-suspicion extras: red/blue police strobe cast, faceted searchlights, gunships, drones, roof alarms."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import SS, R, ramp, toner, facet, bil, tri, NEON, layer, composite

BEAM = R('#5a1018', '#a02a34', '#e06a60', '#ffb8a8', '#fff4ec')
GUN = R('#040304', '#0e0a0e', '#1c161c', '#302630', '#4a3c46')


def beam(d, cam, src, g, r, seed):
    ca, sa = cam.ca, cam.sa
    left = cam.p(g[0] - r * ca, g[1] + r * sa, 0)
    right = cam.p(g[0] + r * ca, g[1] - r * sa, 0)
    facet(d, bil([src, src, right, left]), 4, 8, toner(BEAM, 0.7, gu=0.25, gv=-0.2, var=0.12, flip=0.2, alpha=(70, 150)),
          ('beam', seed), 0.35)
    facet(d, lambda u, v: cam.p(g[0] + r * v * math.cos(u * 2 * math.pi), g[1] + r * v * math.sin(u * 2 * math.pi), 0.1),
          10, 2, toner(BEAM, 0.85, var=0.1, flip=0.2, alpha=(140, 210)), ('spot', seed), 0.2, wrap_u=True)


def heli(d, x, y, s, seed, flip=1):
    rc = random.Random(str(seed))
    f = flip

    def P(px, py):
        return (x + px * s * f, y + py * s)
    body = [P(-1.0, -0.2), P(0.2, -0.45), P(0.9, -0.1), P(0.6, 0.35), P(-0.6, 0.35)]
    c = P(0, 0)
    for k in range(len(body)):
        tri(d, [body[k], body[(k + 1) % len(body)], c], ramp(GUN, 0.35 + 0.5 * rc.random()))
    tri(d, [P(0.2, -0.45), P(0.9, -0.1), P(0.45, -0.05)], ramp(NEON['red'], 0.55))
    tri(d, [P(0.45, -0.05), P(0.9, -0.1), P(0.6, 0.2)], ramp(NEON['red'], 0.3))
    tri(d, [P(-0.9, -0.15), P(-2.4, -0.25), P(-0.8, 0.2)], ramp(GUN, 0.55))
    tri(d, [P(-2.4, -0.25), P(-2.6, -0.8), P(-2.2, -0.2)], ramp(GUN, 0.7))
    tri(d, [P(0.0, -0.5), P(-2.2, -0.62), P(-2.2, -0.55)], ramp(GUN, 0.8))
    tri(d, [P(0.0, -0.5), P(2.0, -0.44), P(2.0, -0.38)], ramp(GUN, 0.9))
    for (px, py, st) in ((-2.4, -0.3, NEON['red']), (0.5, 0.36, NEON['blue'])):
        q = P(px, py)
        tri(d, [(q[0] - 6, q[1]), (q[0], q[1] - 7), (q[0] + 6, q[1])], ramp(st, 0.9))
        tri(d, [(q[0] - 6, q[1]), (q[0], q[1] + 7), (q[0] + 6, q[1])], ramp(st, 0.6))


def drone(d, x, y, s, seed, eye=None):
    eye = eye or NEON['red']
    pts = [(x, y - s), (x + s * 1.3, y), (x, y + s * 0.7), (x - s * 1.3, y)]
    tri(d, [pts[0], pts[1], (x, y)], ramp(GUN, 0.8))
    tri(d, [pts[1], pts[2], (x, y)], ramp(GUN, 0.4))
    tri(d, [pts[2], pts[3], (x, y)], ramp(GUN, 0.3))
    tri(d, [pts[3], pts[0], (x, y)], ramp(GUN, 0.65))
    for sx in (-1, 1):
        a = (x + sx * s * 1.3, y)
        tri(d, [a, (a[0] + sx * s * 0.9, a[1] - s * 0.5), (a[0] + sx * s * 0.9, a[1] - s * 0.2)], ramp(GUN, 0.9))
    tri(d, [(x - s * 0.45, y + s * 0.1), (x + s * 0.45, y + s * 0.1), (x, y + s * 0.55)], ramp(eye, 0.85))


def beacon(d, x, y, r, seed):
    rc = random.Random(str(seed))
    for k in range(8):
        a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 1) / 8
        am = (a0 + a1) / 2
        rr = r * (1.0 if k % 2 == 0 else 0.55)
        p = (x + rr * math.cos(am), y + rr * 0.8 * math.sin(am))
        q0 = (x + r * 0.3 * math.cos(a0), y + r * 0.24 * math.sin(a0))
        q1 = (x + r * 0.3 * math.cos(a1), y + r * 0.24 * math.sin(a1))
        tri(d, [q0, p, (x, y)], ramp(NEON['red'], 0.5 + 0.4 * rc.random()))
        tri(d, [p, q1, (x, y)], ramp(NEON['red'], 0.3 + 0.4 * rc.random()))


def strobe_fan(d, x, y, r, st, seed, a_lo, a_hi):
    """A fan of long translucent triangles thrown across the facets from a police light."""
    rc = random.Random(str(seed))
    n = 4
    for k in range(n):
        a0 = a_lo + (a_hi - a_lo) * k / n
        a1 = a0 + (a_hi - a_lo) / n * rc.uniform(0.2, 0.4)
        rr = r * rc.uniform(0.6, 1.0)
        c = ramp(st, rc.uniform(0.45, 0.7)) + (rc.randint(36, 66),)
        pts = [(x, y), (x + rr * math.cos(a0), y + rr * math.sin(a0)), (x + rr * math.cos(a1), y + rr * math.sin(a1))]
        d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=c)


def apply(img, cam, items, theme):
    """Suspicion overlay on the normal day/night lighting: spotlights, police strobes, alarms, aircraft."""
    from city import inter
    beam_ramp = R('#6a6a60', '#a8a89a', '#dcdccc', '#f4f4e8', '#ffffff') if theme == 'day' else         R('#3a4a5a', '#7a90a8', '#b8d0e4', '#e4f2ff', '#ffffff')
    global BEAM
    BEAM = beam_ramp
    lay, od = layer(img)
    vehicles = [p for it in items for p in it['prims'] if p['k'] == 'strobe']
    boost = 1.0 if theme == 'night' else 0.8
    for n, p in enumerate(vehicles):
        sx, sy = cam.p(p['x'], p['y'], p['z'])
        strobe_fan(od, sx, sy, 380, NEON['red'], ('sfr', n), math.pi * 1.1, math.pi * 1.5)
        strobe_fan(od, sx, sy, 380, NEON['blue'], ('sfb', n), math.pi * 1.5, math.pi * 1.9)
    helis = [((300.0, 250.0), inter(2, 3), 3.0, -1), ((905.0, 175.0), inter(4, 2), 2.7, 1),
             ((1590.0, 250.0), inter(7, 3), 2.6, 1)]
    drones_lit = [((1210.0, 150.0), (inter(3, 1)[0] + 2.0, inter(3, 1)[1] + 1.2), 1.6),
                  ((620.0, 120.0), inter(2, 1), 1.4)]
    for n, (src, g, r, fl) in enumerate(helis):
        beam(od, cam, src, g, r, n)
    for n, (src, g, r) in enumerate(drones_lit):
        beam(od, cam, src, g, r, 10 + n)
    img = composite(img, lay)
    d = ImageDraw.Draw(img)
    roofs = [p for it in items for p in it['prims'] if p['k'] == 'box' and p['z1'] > 9.0 and p['win']]
    roofs.sort(key=lambda p: (-p['z1'], str(p['bid'])))
    for n, p in enumerate(roofs[:8]):
        sx, sy = cam.p((p['x0'] + p['x1']) / 2, (p['y0'] + p['y1']) / 2, p['z1'] + 0.2)
        beacon(d, sx, sy, 16, ('bc', n))
    for n, (src, g, r, fl) in enumerate(helis):
        heli(d, src[0], src[1], 32, ('heli', n), fl)
    for n, (src, g, r) in enumerate(drones_lit):
        drone(d, src[0], src[1], 16, ('dl', n))
    rng = random.Random(99)
    for n in range(8):
        drone(d, rng.uniform(420, 1700), rng.uniform(110, 330), rng.uniform(11, 14), ('dr', n))
    return img
