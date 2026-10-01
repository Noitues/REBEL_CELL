"""03 landmarks: Freight Ziggurat (Meridian), Civic Pyramid (Halcyon), Orbital Tether (Orbital), each on a
plinth, rendered with the city's 3D cel painter (same camera angles as the city)."""
import math
from kit import *
from city import Cam, B, bil3
from toon import ToonPainter

XS = [400, 960, 1520]
GROUND_Y = 770


def cam_at(cx):
    az, el, S = 24.0, 38.0, 31.0
    c = Cam(az, el, S, 0, 0)
    px, py = c.p(0, 0, 0)
    return Cam(az, el, S, cx - px, GROUND_Y - py)


def draw_list(tp, prims):
    cam = tp.cam

    def key(p):
        if p['k'] == 'box':
            x, y, z = (p['x0'] + p['x1']) / 2, (p['y0'] + p['y1']) / 2, p['z0']
        elif p['k'] == 'pyr':
            x, y, z = (p['x0'] + p['x1']) / 2, (p['y0'] + p['y1']) / 2, p['z0']
        else:
            x, y, z = p.get('x', 0), p.get('y', 0), p.get('z', 0)
        return (round(z, 2) if p.get('stack') else 0, cam.depth(x, y), z)
    for p in prims:
        if p['k'] == 'fn':
            p['fn']()
        else:
            tp.item(dict(prims=[p]))


def plinth(fam='concrete'):
    p = B(-7, -7, 7, 7, -1.4, 0, fam, 'plinth', grime=True)
    return p


def ziggurat(tp):
    P = []
    steps = [(4.4, 0, 2.6), (3.4, 2.6, 5.0), (2.4, 5.0, 7.2), (1.4, 7.2, 9.0)]
    for n, (r, z0, z1) in enumerate(steps):
        b = B(-r + 0.6, -r - 1.4, r + 0.6, r - 1.4, z0, z1, 'mer', ('zig', n), win='sodium')
        b['stack'] = True
        P.append(b)
    # control house on top
    t = B(-0.4, -2.2, 1.2, -0.8, 9.0, 10.2, 'metal', 'zig_top')
    t['stack'] = True
    P.append(t)
    # container yard on the plinth (front-right)
    cols = ['mer', 'rust', 'oily', 'sol', 'mer', 'hal', 'rust']
    k = 0
    for gx in range(3):
        for gy in range(2):
            for lvl in range(2 if (gx + gy) % 2 == 0 else 1):
                x0, y0 = -5.6 + gx * 2.3, 3.6 + gy * 1.0
                c = B(x0, y0, x0 + 2.1, y0 + 0.85, lvl * 0.8, lvl * 0.8 + 0.8, cols[k % len(cols)], ('ctr', k),
                      grime=False)
                c['stack'] = False
                P.append(c)
                k += 1
    # crane: mast, jib, counter-jib, hanging container
    cam = tp.cam

    def crane():
        mx, my = 5.0, 4.4
        tp.item(dict(prims=[B(mx - 0.18, my - 0.18, mx + 0.18, my + 0.18, 0, 13.0, 'mer', 'mast', grime=False)]))
        tp.item(dict(prims=[B(mx - 9.0, my - 0.14, mx + 1.8, my + 0.14, 12.6, 13.1, 'mer', 'jib', grime=False)]))
        tp.item(dict(prims=[B(mx + 1.0, my - 0.4, mx + 1.8, my + 0.4, 11.8, 12.6, 'concrete', 'cw', grime=False)]))
        a, b = cam.p(mx - 7.5, my, 12.6), cam.p(mx - 7.5, my, 4.4)
        ink_line(tp.d, a, b, 2.0, 'cable')
        tp.item(dict(prims=[B(mx - 8.6, my - 0.42, mx - 6.4, my + 0.42, 3.6, 4.4, 'sol', 'hang', grime=False)]))
        # lattice ticks on the mast
        for z in range(1, 13):
            p0, p1 = cam.p(mx + 0.18, my + 0.18, z - 0.5), cam.p(mx + 0.18, my - 0.18, z)
            line2(tp.d, p0, p1, 1.2, INK)
    P.append(dict(k='fn', fn=crane, x=5.0, y=4.6, z=0))
    draw_list(tp, P)


def pyramid(tp):
    P = []
    tiers = [(5.0, 0, 1.6), (4.0, 1.6, 3.2), (3.0, 3.2, 4.8), (2.0, 4.8, 6.4)]
    for n, (r, z0, z1) in enumerate(tiers):
        b = B(-r, -r, r, r, z0, z1, 'hal', ('tier', n), win='cyan' if n < 3 else None)
        b['stack'] = True
        P.append(b)
    pyr = dict(k='pyr', x0=-2.0, y0=-2.0, x1=2.0, y1=2.0, z0=6.4, z1=9.4, fam='hal', bid='apex', stack=True)
    P.append(pyr)
    cam = tp.cam

    def colonnade():
        # columns along the front and right faces of the base tier
        for k in range(9):
            x = -4.6 + k * 1.15
            tp.item(dict(prims=[B(x - 0.16, 5.2, x + 0.16, 5.52, 0, 1.5, 'concrete', ('colf', k), grime=False)]))
        for k in range(9):
            y = 4.6 - k * 1.15
            tp.item(dict(prims=[B(5.2, y - 0.16, 5.52, y + 0.16, 0, 1.5, 'concrete', ('colr', k), grime=False)]))
        tp.item(dict(prims=[B(-5.2, 5.0, 5.6, 5.7, 1.5, 1.85, 'concrete', 'archf', grime=False)]))
        tp.item(dict(prims=[B(5.0, -5.2, 5.7, 5.7, 1.5, 1.85, 'concrete', 'archr', grime=False)]))

    def halo():
        z, ro, ri = 11.2, 3.4, 2.6
        n = 36
        pts_o = [cam.p(ro * math.cos(2 * math.pi * k / n), ro * math.sin(2 * math.pi * k / n), z) for k in range(n)]
        pts_i = [cam.p(ri * math.cos(2 * math.pi * k / n), ri * math.sin(2 * math.pi * k / n), z) for k in range(n)]
        for k in range(n):
            q = [pts_i[k], pts_o[k], pts_o[(k + 1) % n], pts_i[(k + 1) % n]]
            ang = 2 * math.pi * (k + 0.5) / n
            b = 2 if math.sin(ang) < -0.2 else (1 if math.cos(ang) < 0.3 else 0)
            quad_fill(tp.d, q, CELL, b, ('halo', k), 1, 1)
        ink_poly(tp.d, pts_o, 3.2, 'halo_o')
        ink_poly(tp.d, pts_i, 2.4, 'halo_i')
        # glow ticks
        for k in range(0, n, 3):
            line2(tp.d, pts_o[k], (pts_o[k][0], pts_o[k][1] - 10), 2, ramp(NEON['cyan'], 0.8))
    P.append(dict(k='fn', fn=colonnade, x=5.0, y=5.0, z=0))
    P.append(dict(k='fn', fn=halo, x=-9, y=-9, z=99, stack=True))
    draw_list(tp, P)


def tether(tp):
    P = []
    b = B(-3.2, -3.2, 3.2, 3.2, 0, 2.0, 'orb', 'pod', win='cyan')
    b['stack'] = True
    P.append(b)
    nd = B(-1.3, -1.3, 1.3, 1.3, 2.0, 15.5, 'orb', 'needle', win='cyan', taper=0.55)
    nd['stack'] = True
    P.append(nd)
    sp = dict(k='pyr', x0=-0.6, y0=-0.6, x1=0.6, y1=0.6, z0=15.5, z1=19.0, fam='orb', bid='spire', stack=True)
    P.append(sp)
    cam = tp.cam

    def ring():
        z, ro, ri = 8.0, 2.6, 1.0
        n = 24
        po = [cam.p(ro * math.cos(2 * math.pi * k / n), ro * math.sin(2 * math.pi * k / n), z) for k in range(n)]
        pi = [cam.p(ri * math.cos(2 * math.pi * k / n), ri * math.sin(2 * math.pi * k / n), z) for k in range(n)]
        pb = [cam.p(ro * math.cos(2 * math.pi * k / n), ro * math.sin(2 * math.pi * k / n), z - 0.6) for k in range(n)]
        for k in range(n):
            ang = 2 * math.pi * (k + 0.5) / n
            if math.sin(ang + 0.4) > 0:   # visible outer wall
                quad_fill(tp.d, [po[k], po[(k + 1) % n], pb[(k + 1) % n], pb[k]], ORB, 0, ('rw', k), 1, 1)
            quad_fill(tp.d, [pi[k], po[k], po[(k + 1) % n], pi[(k + 1) % n]], ORB, 2 if math.sin(ang) < 0 else 1,
                      ('rt', k), 1, 1)
        ink_poly(tp.d, hull(po + pb), 3.2, 'ring_o')
        for k in range(0, n, 2):
            tri(tp.d, [po[k], (po[k][0] + 3, po[k][1] - 2), (po[k][0], po[k][1] + 3)], ramp(NEON['cyan'], 0.9))
    P.append(dict(k='fn', fn=ring, x=-9, y=-9, z=8.0, stack=True))
    draw_list(tp, P)
    # tether into the sky with a climber pod
    top = cam.p(0, 0, 19.0)
    sky = (top[0] + 6, top[1] - 520)
    ink_line(tp.d, top, sky, 4.0, 'tether')
    line2(tp.d, top, sky, 1.6, ramp(NEON['cyan'], 0.85))
    my = top[1] - (top[1] - sky[1]) * 0.55
    mx = top[0] + 6 * 0.55
    pod = [(mx - 14, my - 10), (mx + 14, my - 10), (mx + 18, my + 8), (mx - 18, my + 8)]
    shape(tp.d, pod, ORB, 'climber', ink=2.6)
    tri(tp.d, [(mx - 4, my - 2), (mx + 4, my - 2), (mx, my + 4)], ramp(NEON['cyan'], 0.9))


