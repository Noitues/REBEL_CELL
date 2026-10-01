"""Round 12 MODEM facade (v2 layout): build one option in one lighting state, render beauty + aux passes.

Usage (headless):
  blender -b --factory-startup --python scene.py -- <f1|f2|f3> <rain|day|night> <out_prefix>
Writes <out_prefix>_beauty.npy, _id.npy (object index, depth), _nrm.npy, _ids.json, _layout.json.

Layout (camera at x=0 looking +y, eye 6 m, lens shift so the vanishing point sits at x~636):
  shop tower on the left (sign + recessed foyer), a narrow alley straight ahead between the tower and
  the smaller front building (right), the alley stair climbs and turns right behind the front building,
  the shop's low wing shows above the front building, a layered city behind, wet street in front.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flib as F
from flib import Mesh, hexl, scl, sx_to_x

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SIGN_PNG = os.path.join(ROOT, 'round4_modem_sign', 'sign_rgba.png')

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['f1', 'rain', os.path.join(HERE, '..', 'scratch', 'test')]
OPT, STATE, OUT = args[0], args[1], os.path.abspath(args[2])
VAR_B = os.environ.get('MF_VAR', '') == 'b'   # f1b: magenta spill, no dangling cables, lower sun, brighter billboard

# ------------------------------------------------------------------ layout (from screen targets)
D_SIGN = 22.0
PX0, PX1, PY0 = 52, 212, 26                      # sign plate on screen (x0, x1, top)
SX0, SX1 = sx_to_x(PX0, D_SIGN), sx_to_x(PX1, D_SIGN)
SW = SX1 - SX0
SH = SW * 1034 / 250
SZ0 = 3.5                                        # sign bottom (world); vertical lens shift follows
SZ1 = SZ0 + SH
F.CAM['shy'] = ((SZ1 - F.CAM['h']) / D_SIGN - (F.H / 2 - PY0) / (F.H / 2) * F.VT) / (2 * F.HT)
YS = D_SIGN + 0.3                                # shop facade
XA0, XA1 = -2.0, 2.0                             # alley walls
YF, YFB, HF = 19.0, 28.5, 7.0                    # front building: front, back, height
XFR = 13.0
YW, ZWING = 41.0, 12.0                           # shop's low wing (behind the front building)
Y_KERB = 18.3
RX0, RX1 = SX0 + 0.3, XA0 - 1.0                  # foyer recess in the tower
RD, RZ = 3.0, 3.0                                # recess depth, height
Y_ST0, Y_ST1, Z_LAND = 26.0, 36.0, 4.5           # alley stair
Y_BACK = 46.0                                    # building closing the alley
STATE_K = {'rain': dict(wet=1.0, emi=1.0, lit=0.4), 'day': dict(wet=0.25, emi=0.6, lit=0.08),
           'night': dict(wet=0.9, emi=1.35, lit=0.55)}[STATE]
assert RX1 - RX0 > 4.0, (RX0, RX1)


def tone(base, var=0.32, grime=0.3, streaks=0.0, n=14, seed=0, top=0.0):
    """Per-triangle colour: strong jitter (visible facets), darker toward the bottom, optional streaks."""
    b = hexl(base) if isinstance(base, str) else base
    rs = random.Random(str(('st', seed)))
    cols = [rs.random() for _ in range(n)]

    def f(s, t, rng):
        k = 1 + rng.uniform(-var, var)
        hue = (rng.uniform(0.93, 1.07), 1.0, rng.uniform(0.93, 1.07))
        k *= 1 - grime * (1 - t) ** 3
        k *= 1 - top * t ** 4
        if streaks:
            c = cols[min(n - 1, int(s * n))]
            if c < streaks and t > 0.25 + c:
                k *= 0.7
        return tuple(b[i] * k * hue[i] for i in range(3))
    return f


def stripes(base, n, dark=0.72, var=0.22, axis='s'):
    def f(s, t, rng):
        v = s if axis == 's' else t
        k = (1 + rng.uniform(-var, var)) * (dark if int(v * n) % 2 else 1.0) * (1 - 0.2 * (1 - t) ** 2)
        return scl(hexl(base), k)
    return f


def wetfn_ground(x0, y0, dx, dy, base=0.35, puddle=0.9, seed=0):
    """Wet floor: puddles from a cheap seeded noise of the world position."""
    rs = random.Random(str(('pud', seed)))
    waves = [(rs.uniform(0.15, 0.6), rs.uniform(0.15, 0.6), rs.uniform(0, 6.28), rs.uniform(0, 6.28)) for _ in range(5)]

    def f(s, t, rng):
        x, y = x0 + s * dx, y0 + t * dy
        n = sum(math.sin(a * x + p) * math.sin(b * y * 0.7 + q) for a, b, p, q in waves) / 2.2
        k = STATE_K['wet']
        if n > 0.25:
            return (min(1.0, puddle * k + 0.05), 0.02)
        return (base * k * rng.uniform(0.7, 1.1), 0.22 + 0.2 * rng.random())
    return f


def cyl(m, p0, p1, r, n=6, **kw):
    """Low-poly prism pipe from p0 to p1."""
    import mathutils
    a, b = mathutils.Vector(p0), mathutils.Vector(p1)
    ax = (b - a)
    d = ax.normalized()
    up = mathutils.Vector((0, 0, 1)) if abs(d.z) < 0.9 else mathutils.Vector((1, 0, 0))
    e1 = d.cross(up).normalized()
    e2 = d.cross(e1).normalized()
    for i in range(n):
        t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        o = a + (e1 * math.cos(t0) + e2 * math.sin(t0)) * r
        q = a + (e1 * math.cos(t1) + e2 * math.sin(t1)) * r
        m.grid(tuple(o), tuple(q - o), tuple(ax), **dict(kw, seed=(kw.get('seed', 0), i)))


def catenary(m, p0, p1, sag, r=0.03, col=None, n=10):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(tuple(p0[k] + (p1[k] - p0[k]) * t for k in range(3)))
        pts[-1] = (pts[-1][0], pts[-1][1], pts[-1][2] - sag * math.sin(math.pi * t))
    for a, b in zip(pts, pts[1:]):
        cyl(m, a, b, r, n=4, cell=6, col=col or hexl('#121316'))


def stair_x(m, x0, z0, x1, z1, y0, y1, col, step=0.3, rail=True):
    """Straight stair rising along x: treads, stringers, rails."""
    run, rise = x1 - x0, z1 - z0
    n = max(2, int(abs(rise) / step))
    for i in range(n):
        x = x0 + run * i / n
        z = z0 + rise * (i + 1) / n
        m.box(min(x, x + run / n), max(x, x + run / n) + 0.04, y0, y1, z - 0.06, z, cell=3, col=col, var=0.08, faces='ft')
    ang = math.atan2(rise, run)
    L = math.hypot(run, rise) / 2
    c = (x0 + run / 2, 0, z0 + rise / 2)
    ax = (math.cos(ang) * L, 0, math.sin(ang) * L)
    for yy in (y0, y1):
        m.obox((c[0], yy, c[2] - 0.12), ax, (0, 0.04, 0), (-math.sin(ang) * 0.12, 0, math.cos(ang) * 0.12),
               col=scl(col, 0.8), var=0.05)
        if rail:
            m.obox((c[0], yy, c[2] + 0.95), ax, (0, 0.025, 0), (-math.sin(ang) * 0.025, 0, math.cos(ang) * 0.025),
                   col=scl(col, 1.15), var=0.05)


def stair_y(m, y0, z0, y1, z1, x0, x1, col, step=0.28):
    """Straight stair rising along +y (away from the camera)."""
    n = max(2, int((z1 - z0) / step))
    for i in range(n):
        y = y0 + (y1 - y0) * i / n
        z = z0 + (z1 - z0) * (i + 1) / n
        m.box(x0, x1, y, y + (y1 - y0) / n + 0.02, z - (z1 - z0) / n, z, cell=0.6, col=col, var=0.2, faces='ft')


def glyph_box(m, x, y, z, w, h, col, seed, cols=9, rows=3, frame='#1d1f24', face='-y'):
    """Unreadable lightbox: emissive blocks in a glyph-ish pattern (no letters)."""
    rng = random.Random(str(('gl', seed)))
    if face == '-y':
        m.box(x - 0.08, x + w + 0.08, y, y + 0.2, z - 0.08, z + h + 0.08, cell=3, col=hexl(frame), faces='fltd')
    else:   # facing +x (on an alley wall at x = x)
        m.box(x - 0.2, x, y - 0.08, y + w + 0.08, z - 0.08, z + h + 0.08, cell=3, col=hexl(frame), faces='rftd')
    for i in range(cols):
        for j in range(rows):
            if rng.random() < 0.55:
                cw, ch = w / cols, h / rows
                k = rng.uniform(0.5, 1.0)
                ww, hh = cw * rng.uniform(0.4, 0.95), ch * rng.uniform(0.4, 0.9)
                if face == '-y':
                    m.grid((x + i * cw + 0.03, y - 0.01, z + j * ch + 0.03), (ww, 0, 0), (0, 0, hh), cell=3,
                           col=scl(col, 0.4), emi=scl(col, k))
                else:
                    m.grid((x + 0.01, y + i * cw + 0.03, z + j * ch + 0.03), (0, ww, 0), (0, 0, hh), cell=3,
                           col=scl(col, 0.4), emi=scl(col, k))


def win_grid(name, face, plane, us, zs, w, h, palette, frame_col, seed, skip=None, ac=0.0, lit=None):
    """Windows on a facade: face '-y' (plane = y, u = x) or '+x' (plane = x, u = y)."""
    m = Mesh(name, 'window')
    fr = Mesh(name + '_fr')
    rng = random.Random(str(('win', seed)))
    lit_p = STATE_K['lit'] if lit is None else lit
    for u in us:
        for z in zs:
            if skip and skip(u, z):
                continue
            on = rng.random() < lit_p
            ec = rng.choice(palette)
            emi = scl(ec, rng.uniform(0.35, 0.8)) if on else (0, 0, 0)
            col = scl(ec, 0.3) if on else hexl('#161a24')
            if face == '-y':
                m.grid((u, plane - 0.03, z), (w, 0, 0), (0, 0, h), cell=0.5, col=col, var=0.3, emi=emi, wet=(0.3, 0.08))
                fr.box(u - 0.1, u + w + 0.1, plane - 0.18, plane, z - 0.14, z, cell=2, col=frame_col, var=0.1, faces='ftlr')
                fr.box(u + w / 2 - 0.04, u + w / 2 + 0.04, plane - 0.08, plane, z, z + h, cell=3, col=frame_col, faces='f')
                if ac and rng.random() < ac:
                    ux = u + rng.uniform(-0.1, w - 0.7)
                    fr.box(ux, ux + 0.8, plane - 0.55, plane, z - 0.75, z - 0.2, cell=0.4,
                           col=hexl(rng.choice(['#8d8a80', '#7b8288', '#9a9284'])), var=0.15, faces='fltrd')
            else:
                m.grid((plane + 0.03, u, z), (0, w, 0), (0, 0, h), cell=0.5, col=col, var=0.3, emi=emi, wet=(0.3, 0.08))
                fr.box(plane, plane + 0.18, u - 0.1, u + w + 0.1, z - 0.14, z, cell=2, col=frame_col, var=0.1, faces='rtf')
                if ac and rng.random() < ac:
                    uy = u + rng.uniform(-0.1, w - 0.7)
                    fr.box(plane, plane + 0.55, uy, uy + 0.8, z - 0.75, z - 0.2, cell=0.4,
                           col=hexl(rng.choice(['#8d8a80', '#7b8288', '#9a9284'])), var=0.15, faces='frtd')
    m.build()
    fr.build()


WARM = [hexl('#ffcf8a'), hexl('#ffb36b'), hexl('#9ff3ff'), hexl('#ff7ad1'), hexl('#ffe3b0')]
PAL = {
    'f1': dict(wall='#8a5a4c', side='#7a5248', fb='#5d6e70', fb2='#4c5a5e', recess='#2c2a30', floor='#8a857c',
               road='#40424a', wing='#7a5a50', accent='#ff4fb4', alley='#62f0d8', steel='#4f555c', screen='#4fe8ff'),
    'f2': dict(wall='#5e6e74', side='#56646a', fb='#6a4a3e', fb2='#35565e', recess='#2a2b2e', floor='#8a857a',
               road='#40424a', wing='#56646a', accent='#ffb030', alley='#8cff6a', steel='#62666a', screen='#4fe8ff'),
    'f3': dict(wall='#706a62', side='#645e58', fb='#56665a', fb2='#4a5a50', recess='#2b2a2a', floor='#86817a',
               road='#40424a', wing='#6a645c', accent='#5fd8ff', alley='#5fd8ff', steel='#585c62', screen='#4fe8ff'),
}


# ------------------------------------------------------------------ shared masses
def ground(pal):
    st = Mesh('street', 'ground')
    st.grid((-40, 4.0, 0), (90, 0, 0), (0, Y_KERB - 4.0, 0), cell=1.1, colfn=tone(pal['road'], 0.25, 0),
            wetfn=wetfn_ground(-40, 4.0, 90, Y_KERB - 4.0, seed=1, base=0.5))
    # lane paint (faded), a drain grate
    for x0 in (-14, -4, 6, 16, 26):
        st.grid((x0, 9.0, 0.01), (3.2, 0, 0), (0, 0.25, 0), cell=2, col=hexl('#9a9688'), var=0.2,
                wetfn=wetfn_ground(x0, 9, 3, 0.25, seed=5))
    st.build()
    pv = Mesh('pavement', 'ground')
    pv.grid((-40, Y_KERB, 0.18), (80, 0, 0), (0, YS - Y_KERB, 0), cell=0.9, colfn=tone(pal['floor'], 0.25, 0),
            wetfn=wetfn_ground(-40, Y_KERB, 80, YS - Y_KERB, base=0.45, seed=2))
    pv.grid((XA0, YS, 0.18), (XA1 - XA0, 0, 0), (0, Y_ST0 - YS, 0), cell=0.7, colfn=tone(pal['floor'], 0.28, 0),
            wetfn=wetfn_ground(XA0, YS, 4, Y_ST0 - YS, base=0.55, seed=3))
    pv.build()
    kb = Mesh('kerb', 'ground')
    kb.grid((-40, Y_KERB, 0.0), (80, 0, 0), (0, 0, 0.18), cell=1.2, col=hexl('#9a958c'), var=0.15)
    kb.build()
    far = Mesh('far_ground', 'ground')
    far.grid((-80, Y_BACK, 0), (220, 0, 0), (0, 200, 0), cell=6.0, col=hexl(pal['road']), var=0.15)
    far.build()


def shop_tower(pal, facade_colfn, side_colfn):
    t = Mesh('shop_tower', 'shop')
    top = 34.0
    t.grid((-40, YS, 0.18), (RX0 + 40, 0, 0), (0, 0, top), cell=0.9, colfn=facade_colfn(0))
    t.grid((RX1, YS, 0.18), (XA0 - RX1, 0, 0), (0, 0, top), cell=0.9, colfn=facade_colfn(1))
    t.grid((RX0, YS, RZ), (RX1 - RX0, 0, 0), (0, 0, top - RZ), cell=0.9, colfn=facade_colfn(2))
    t.grid((XA0, YS, 0.18), (0, 18, 0), (0, 0, top), cell=0.9, colfn=side_colfn)           # alley wall (+x)
    t.build()
    r = Mesh('foyer_recess', 'shop')
    rc = pal['recess']
    r.grid((RX0, YS + RD, 0.18), (RX1 - RX0, 0, 0), (0, 0, RZ - 0.18), cell=0.6, colfn=tone(rc, 0.3, 0.2))  # back
    r.grid((RX0, YS + RD, 0.18), (0, -RD, 0), (0, 0, RZ), cell=0.6, colfn=tone(rc, 0.3, 0.2))              # left side
    r.grid((RX1, YS, 0.18), (0, RD, 0), (0, 0, RZ), cell=0.6, colfn=tone(rc, 0.3, 0.2))                    # right side
    r.grid((RX0, YS + RD, RZ), (RX1 - RX0, 0, 0), (0, -RD, 0), cell=0.7, colfn=tone('#232227', 0.3, 0))  # soffit
    r.grid((RX0, YS, 0.2), (RX1 - RX0, 0, 0), (0, RD, 0), cell=0.5, colfn=tone(pal['floor'], 0.25, 0),
           wetfn=wetfn_ground(RX0, YS, RX1 - RX0, RD, base=0.6, seed=7))
    r.build()
    # display screens + door at the back of the recess (cyan glow)
    sc = Mesh('foyer_screens', 'window')
    sc_col = hexl(pal['screen'])
    rng = random.Random('screens')
    x = RX0 + 0.4
    for k in range(4):
        w = 0.9
        hz = 1.0 + 0.5 * (k % 2)
        sc.grid((x, YS + RD - 0.05, 0.9), (w, 0, 0), (0, 0, hz), cell=0.3, col=scl(sc_col, 0.3), var=0.3,
                emifn=lambda s, t, r: scl(sc_col, (0.45 + 0.4 * t) * r.uniform(0.7, 1.15)), wet=(0.4, 0.05))
        x += w + 0.25
    dx = RX1 - 1.6
    sc.grid((dx, YS + RD - 0.05, 0.2), (1.1, 0, 0), (0, 0, 2.3), cell=0.3, col=scl(sc_col, 0.3), var=0.3,
            emifn=lambda s, t, r: scl(sc_col, 0.7 * r.uniform(0.75, 1.1)), wet=(0.4, 0.05))
    # soffit strip light
    sc.box(RX0 + 0.3, RX1 - 0.3, YS + 0.4, YS + 0.55, RZ - 0.06, RZ, cell=3, col=hexl('#e8fbff'),
           emi=scl(hexl('#e8fbff'), 0.8), faces='fd')
    sc.build()
    fr = Mesh('foyer_frames')
    fr.box(RX0, RX1, YS - 0.3, YS, RZ - 0.1, RZ + 0.35, cell=0.6, colfn=tone('#2a2c33', 0.3, 0), faces='fd')
    fr.box(dx - 0.12, dx, YS + RD - 0.2, YS + RD, 0.2, 2.5, cell=3, col=hexl('#1e2026'), faces='f')
    fr.box(dx + 1.1, dx + 1.22, YS + RD - 0.2, YS + RD, 0.2, 2.5, cell=3, col=hexl('#1e2026'), faces='f')
    fr.box(RX0 + 0.2, dx - 0.4, YS + RD - 0.8, YS + RD - 0.1, 0.2, 0.85, cell=0.5, colfn=tone('#3a3640', 0.3, 0),
           faces='ft')   # display counter
    fr.build()


def sign_and_spill_geo():
    s = SW / 250.0
    rect = (SX0 - 70 * s, SZ1 + 70 * s - 1174 * s, SX0 - 70 * s + 390 * s, SZ1 + 70 * s)
    F.sign_plane(SIGN_PNG, rect, D_SIGN, {'rain': 1.0, 'day': 1.0, 'night': 1.12}[STATE])
    br = Mesh('sign_brackets')
    for z in (SZ0 + 0.6, (SZ0 + SZ1) / 2, SZ1 - 0.6):
        for x in (SX0 + 0.25, SX1 - 0.25):
            br.box(x - 0.06, x + 0.06, D_SIGN + 0.02, YS, z - 0.06, z + 0.06, cell=3, col=hexl('#2a2c30'),
                   faces='ftlr')
    br.build()


def figure():
    """A lone silhouette in the foyer (scale + story)."""
    m = Mesh('figure', 'figure')
    c = hexl('#141218')
    x, y = RX1 - 2.6, YS + 0.6
    m.obox((x - 0.12, y, 0.6), (0.09, 0, 0), (0, 0.1, 0), (0.0, 0, 0.42), col=c, var=0.2)
    m.obox((x + 0.12, y, 0.6), (0.09, 0, 0), (0, 0.1, 0), (0.03, 0, 0.42), col=c, var=0.2)
    m.obox((x, y, 1.35), (0.27, 0, 0), (0, 0.16, 0), (0, 0, 0.36), col=c, var=0.2)       # coat
    m.obox((x, y, 0.95), (0.3, 0, 0), (0, 0.18, 0), (0, 0, 0.12), col=c, var=0.2)        # coat hem
    m.obox((x + 0.02, y, 1.86), (0.11, 0, 0), (0, 0.12, 0), (0, 0, 0.13), col=c, var=0.2)  # head
    m.obox((x + 0.02, y, 2.0), (0.2, 0, 0), (0, 0.2, 0), (0, 0, 0.025), col=c, var=0.2)  # hat brim
    m.build()


def alley(pal):
    """Narrow passage between the tower and the front building: wet floor, stair up, turn right, door light."""
    stc = hexl(pal['steel'])
    a = Mesh('alley_stair', 'alley')
    stair_y(a, Y_ST0, 0.18, Y_ST1, Z_LAND, XA0 + 0.3, XA1 - 0.3, hexl('#6a665e'))
    a.box(XA0, XA1 + 6, Y_ST1, Y_BACK - 0.01, Z_LAND - 0.3, Z_LAND, cell=0.8, colfn=tone('#5e5a54', 0.3, 0), faces='ftl')
    a.build()
    s2 = Mesh('alley_turn', 'alley')
    stair_x(s2, XA1 - 1.4, Z_LAND, XA1 + 6.0, Z_LAND + 4.4, Y_ST1 + 2.0, Y_ST1 + 3.4, stc)
    s2.box(XA1 + 6.0, XA1 + 10.0, Y_ST1 + 1.8, Y_ST1 + 3.6, Z_LAND + 4.25, Z_LAND + 4.4, cell=2, col=stc, faces='ftd')
    s2.build()
    # rails along the main stair
    rl = Mesh('alley_rails', 'alley')
    for x in (XA0 + 0.35, XA1 - 0.35):
        ang = math.atan2(Z_LAND, Y_ST1 - Y_ST0)
        L = math.hypot(Y_ST1 - Y_ST0, Z_LAND) / 2
        rl.obox((x, (Y_ST0 + Y_ST1) / 2, Z_LAND / 2 + 1.0), (0.025, 0, 0), (0, math.cos(ang) * L, math.sin(ang) * L),
                (0, -math.sin(ang) * 0.03, math.cos(ang) * 0.03), col=stc)
    rl.build()
    # light strips under the stair rails (cold glow) + door light at the landing
    lc = hexl(pal['alley'])
    ls = Mesh('alley_lights', 'window')
    for x in (XA0 + 0.06, XA1 - 0.06):
        ls.grid((x, Y_ST0, 0.5), (0, Y_ST1 - Y_ST0, Z_LAND), (0, 0, 0.08), cell=4, col=lc, emi=scl(lc, 1.3))
    ls.grid((-1.0, Y_BACK - 0.04, Z_LAND), (1.3, 0, 0), (0, 0, 2.3), cell=0.4, col=scl(lc, 0.3), var=0.3,
            emifn=lambda s, t, r: scl(lc, (0.6 + 0.4 * t) * r.uniform(0.8, 1.1)))
    ls.box(-1.25, 0.55, Y_BACK - 0.6, Y_BACK, Z_LAND + 2.45, Z_LAND + 2.6, cell=3, col=hexl('#2a2a2e'), faces='fd')
    ls.build()
    # building closing the alley + bridge over it
    bk = Mesh('alley_back', 'shop')
    bk.grid((-14, Y_BACK, 0), (28, 0, 0), (0, 0, 24), cell=1.0, colfn=tone(pal['side'], 0.3, 0.3, seed='bk'))
    bk.build()
    br = Mesh('alley_bridge', 'shop')
    br.box(XA0, XA1, 33.0, 36.0, 9.5, 12.0, cell=0.7, colfn=tone(pal['wall'], 0.3, 0.1), faces='fdt')
    br.build()
    win_grid('bridge_win', '-y', 33.0, [XA0 + 0.4, XA0 + 1.8, XA0 + 3.2], [10.2], 0.9, 1.2, WARM, hexl('#2a2a2a'),
             'br', lit=STATE_K['lit'] + 0.2)
    # hanging cables + small glyph signs on the alley walls
    cb = Mesh('alley_cables')
    rng = random.Random('cables')
    for k in range(2 if VAR_B else 7):    # f1b: only cables spanning wall to wall at the alley mouth
        y = YS + 1.0 + k * 2.6
        z0 = rng.uniform(5.0, 9.0)
        p0, p1 = (XA0, y, z0), (XA1, y + rng.uniform(-1, 1), z0 + rng.uniform(-1, 1))
        if VAR_B:   # both ends on a wall, below the front building's roof, with anchor brackets
            p0, p1 = (XA0, y, 5.6 + 0.5 * k), (XA1, y + 0.4, 5.0 + 0.4 * k)
            for q, dx in ((p0, 0.12), (p1, -0.12)):
                cb.box(min(q[0], q[0] + dx), max(q[0], q[0] + dx), q[1] - 0.06, q[1] + 0.06, q[2] - 0.08, q[2] + 0.08,
                       cell=3, col=hexl('#2a2c30'), faces='fltrd')
        catenary(cb, p0, p1, rng.uniform(0.4, 1.2))
    cb.build()
    gs = Mesh('alley_signs', 'window')
    glyph_box(gs, XA0, YS + 3.5, 4.6, 1.8, 0.7, hexl(pal['accent']), seed=11, cols=6, rows=2, face='+x')
    glyph_box(gs, XA0, YS + 9.0, 6.8, 1.2, 0.5, hexl('#7dffb0'), seed=12, cols=4, rows=2, face='+x')
    gs.build()
    # steam vent box on the alley floor
    v = Mesh('alley_vent')
    v.box(XA0 + 0.1, XA0 + 0.9, YS + 2.0, YS + 2.8, 0.18, 0.9, cell=0.4, colfn=tone('#5a5e62', 0.3, 0), faces='flrt')
    v.build()


def front_details(pal, seed):
    """Storefront shutters with grime/posters, AC units, pipes, cables, holo ad, ledge lights, roof clutter."""
    rng = random.Random(str(('fd', seed)))
    sh = Mesh('fb_shutters')
    for i, x0 in enumerate((XA1 + 0.8, XA1 + 5.9)):
        open_h = 1.0 if i == 1 else 0.0
        sh.grid((x0, YF - 0.06, 0.18 + open_h), (4.6, 0, 0), (0, 0, 2.9 - open_h), cell=0.45,
                colfn=lambda s, t, r: scl(hexl('#7a7e82'), (0.7 if int(t * 22) % 2 else 1.0) * (1 + r.uniform(-0.25, 0.25))
                                          * (1 - 0.45 * (1 - t) ** 2)))
        sh.box(x0 - 0.15, x0 + 4.75, YF - 0.3, YF, 3.1, 3.4, cell=1.0, col=hexl('#3a3c40'), var=0.15, faces='fd')
    sh.build()
    lit = Mesh('fb_shoplight', 'window')
    wc = hexl('#ffb860')
    lit.grid((XA1 + 5.9, YF - 0.02, 0.18), (4.6, 0, 0), (0, 0, 1.0), cell=0.4, col=scl(wc, 0.3),
             emifn=lambda s, t, r: scl(wc, (0.5 + 0.4 * t) * r.uniform(0.8, 1.1)))
    lit.build()
    po = Mesh('fb_posters')
    pcols = ['#c84a6a', '#4ab0c8', '#d8c050', '#8a5ac8', '#5ac88a']
    for k in range(9):
        x = XA1 + 1.0 + rng.uniform(0, 9.5)
        z = rng.uniform(0.8, 2.3)
        w, h = rng.uniform(0.45, 0.8), rng.uniform(0.6, 1.0)
        c = hexl(rng.choice(pcols))
        po.grid((x, YF - 0.09, z), (w, 0, 0), (0, 0, h), cell=0.3,
                colfn=lambda s, t, r, c=c: scl(c, r.uniform(0.25, 0.5) if r.random() < 0.7 else 0.15))
    po.build()
    ac = Mesh('fb_ac')
    for x in (XA1 + 2.6, XA1 + 7.9):
        z = rng.uniform(4.3, 5.3)
        ac.box(x, x + 0.95, YF - 0.6, YF, z, z + 0.65, cell=0.35,
               colfn=tone(rng.choice(['#9a968c', '#8a9096', '#a09888']), 0.3, 0), faces='fltrd')
    for y in (YF + 2.5, YF + 6.5):     # on the alley-side wall
        ac.box(XA1 - 0.6, XA1, y, y + 0.95, 4.6, 5.25, cell=0.35, colfn=tone('#9a968c', 0.3, 0), faces='flrtd')
    ac.build()
    pp = Mesh('fb_pipes')
    for x in (XA1 + 0.35, XFR - 0.4):
        cyl(pp, (x, YF - 0.15, 0.18), (x, YF - 0.15, HF), 0.08, cell=3, col=hexl('#4a4e54'), var=0.1)
    cyl(pp, (XA1 + 0.35, YF - 0.25, 3.8), (XFR, YF - 0.25, 3.8), 0.07, cell=3, col=hexl('#3e4248'), var=0.1)
    pp.build()
    cb = Mesh('fb_cables')
    for k in range(3):
        catenary(cb, (XA1 + 0.3, YF - 0.3, 6.4 - k * 0.3), (XA1 + 4 + k * 3, YF - 0.3, 6.2), 0.5 + 0.2 * k, r=0.025)
    catenary(cb, (XA1, YF + 0.5, 6.2), (XA0, YS + 0.5, 7.0), 1.0, r=0.03)     # across the alley mouth
    catenary(cb, (XA1, YF + 3.0, 5.6), (XA0, YS + 3.0, 8.0), 1.2, r=0.025)
    cb.build()
    # ledge lights under the cornice (front + alley side) and the small holo ad on a bracket
    ll = Mesh('fb_ledge', 'window')
    lc = hexl(pal['accent'])
    ll.grid((XA1, YF - 0.42, HF - 0.12), (XFR - XA1, 0, 0), (0, 0, 0.08), cell=4, col=lc, emi=scl(lc, 1.0))
    ll.grid((XA1 - 0.42, YFB, HF - 0.12), (0, YF - YFB, 0), (0, 0, 0.08), cell=4, col=lc, emi=scl(lc, 1.0))
    ll.build()
    co = Mesh('fb_cornice', 'front')
    co.box(XA1 - 0.4, XFR, YF - 0.4, YFB, HF - 0.05, HF + 0.35, cell=0.8, colfn=tone('#3a3e44', 0.3, 0), faces='flt')
    co.build()
    ho = Mesh('fb_holo', 'window')
    hc = hexl('#56f2ff') if OPT != 'f3' else hexl('#ff6ad8')
    ho.box(XA1 + 0.9, XA1 + 1.0, YF - 1.3, YF, 5.6, 5.7, cell=3, col=hexl('#2a2a2a'), faces='ft')
    glyph_box(ho, XA1 + 0.2, YF - 1.35, 4.2, 1.5, 1.3, hc, seed=('holo', seed), cols=4, rows=4, frame='#101418')
    ho.build()
    rc = Mesh('fb_roof', 'front')
    x = XA1 + 1.0
    while x < XFR - 2:
        w = rng.uniform(0.9, 2.2)
        h = rng.uniform(0.5, 1.4)
        rc.box(x, x + w, YF + 0.8, YF + 0.8 + rng.uniform(0.8, 1.8), HF + 0.35, HF + 0.35 + h, cell=0.6,
               colfn=tone(rng.choice(['#6a6e72', '#5a5e63', '#7b776f']), 0.3, 0), faces='flt')
        x += w + rng.uniform(0.6, 3.0)
    cyl(rc, (XA1 + 7.5, YF + 4, HF + 0.35), (XA1 + 7.5, YF + 4, HF + 3.3), 1.2, n=8, cell=1.0, col=hexl('#6b5a48'),
        var=0.2)
    for x in (XA1 + 3.0, XA1 + 9.0):
        cyl(rc, (x, YF + 2.0, HF + 0.35), (x, YF + 2.0, HF + 4.5), 0.04, n=4, cell=6, col=hexl('#222222'))
    rc.build()


def front_building(pal):
    if OPT == 'f2':     # two rows of stacked shipping containers, each its own ink silhouette
        ccols = ['#6a4a3e', '#35565e', '#5e5e58', '#6e5238', '#3e4a60', '#5e3c3c', '#4a5c48', '#665c48']
        rng2 = random.Random('cont')
        hc = HF / 2
        for row in (0, 1):
            x0 = XA1 + (0.9 if row else 0.0)
            k = 0
            while x0 < XFR:
                ln = 12.2 if rng2.random() < 0.7 else 6.1
                c = Mesh('f2_cont_%d_%d' % (row, k), 'front')
                base = ccols[(row * 3 + k) % len(ccols)]
                c.grid((x0, YF, row * hc), (ln - 0.05, 0, 0), (0, 0, hc - 0.04), cell=0.55, colfn=stripes(base, int(ln / 0.34)))
                c.grid((x0, YFB, row * hc), (0, YF - YFB, 0), (0, 0, hc - 0.04), cell=0.55,
                       colfn=stripes(base, 9, axis='t'))
                c.grid((x0, YF, row * hc + hc - 0.04), (ln - 0.05, 0, 0), (0, YFB - YF, 0), cell=1.0,
                       colfn=tone(base, 0.25, 0))
                if k == 0:
                    for yy in (YF + 0.4, YF + 1.0, YFB - 1.0, YFB - 0.4):
                        c.box(x0 - 0.08, x0, yy - 0.03, yy + 0.03, row * hc + 0.15, row * hc + hc - 0.2, cell=3,
                              col=hexl('#2a2a2a'), faces='fl')
                c.build()
                x0 += ln + (0.05 if row == 0 else rng2.uniform(0.2, 1.2))
                k += 1
    else:
        m = Mesh('front', 'front')
        m.box(XA1, XFR, YF, YFB, 0.18, HF, cell=1.0, colfn=tone(pal['fb'], 0.28, 0.35, seed='fb'), faces='flt')
        m.build()
        if OPT == 'f3':     # market stall awnings over the shutters
            aw = Mesh('f3_awnings')
            for k, x0 in enumerate((XA1 + 0.6, XA1 + 5.7)):
                aw.obox((x0 + 2.5, YF - 0.8, 3.55), (2.55, 0, 0), (0, 0.8, -0.32), (0, 0.012, 0.03), cell=0.6,
                        colfn=stripes(['#4a7a8a', '#8a5a3a', '#6a7a4a', '#7a4a6a'][k], 18, 0.75))
            aw.build()
        else:
            aw = Mesh('f1_awning')
            aw.obox((XA1 + 9.1, YF - 0.8, 3.6), (2.6, 0, 0), (0, 0.8, -0.3), (0, 0.012, 0.03), cell=0.6,
                    colfn=stripes('#8a2e3e', 16, 0.7))
            aw.build()
    front_details(pal, OPT)


def side_row(pal):
    """Deeper, simpler buildings right of the front building: calm mid-values, a few lit windows."""
    m = Mesh('side_row', 'shop')
    m.box(XFR + 1.5, 70, 31.0, 40.0, 0, 9.5, cell=1.1, colfn=tone(scl(hexl(pal['fb2']), 0.6), 0.28, 0.3, seed='side'), faces='flt')
    m.box(XFR + 1.3, 70, 30.8, 40.0, 9.5, 9.9, cell=1.2, colfn=tone('#3a3e44', 0.25, 0), faces='ft')
    m.build()
    win_grid('side_win', '-y', 31.0, [XFR + 5.0 + 2.6 * k for k in range(14)], [2.0, 5.6], 1.3, 1.5, WARM,
             hexl('#30302e'), 'side', lit=STATE_K['lit'] * 0.8)
    lp = Mesh('street_lamp')
    cyl(lp, (XFR + 5.0, Y_KERB + 0.4, 0.18), (XFR + 5.0, Y_KERB + 0.4, 6.5), 0.09, cell=3, col=hexl('#2a2c30'))
    cyl(lp, (XFR + 5.0, Y_KERB + 0.4, 6.5), (XFR + 3.8, Y_KERB + 0.4, 6.8), 0.07, cell=3, col=hexl('#2a2c30'))
    lp.build()
    lh = Mesh('street_lamp_head', 'window')
    lc = hexl('#ffd9a0')
    lh.box(XFR + 3.4, XFR + 4.2, Y_KERB + 0.2, Y_KERB + 0.6, 6.55, 6.75, cell=3, col=lc, emi=scl(lc, 1.2), faces='fdlt')
    lh.build()


def wing(pal, colfn):
    """The shop's low right wing behind the front building (the part the front building covers)."""
    m = Mesh('shop_wing', 'shop')
    m.box(XA1, 60, YW, YW + 14, 0, ZWING, cell=1.0, colfn=colfn, faces='flt')
    m.box(XA1, 60, YW - 0.2, YW + 0.2, ZWING, ZWING + 0.9, cell=0.9, colfn=colfn, faces='ft')
    m.build()
    win_grid('wing_win', '-y', YW, [XA1 + 1.0 + 2.3 * k for k in range(18)], [8.6], 1.2, 1.4, WARM, hexl('#33302e'),
             'wing', lit=STATE_K['lit'] + 0.15)


def city(pal):
    """Layered towers with lit windows, haze does the rest; a distant holo billboard."""
    rng = random.Random('city')
    lit = {'rain': 0.28, 'day': 0.04, 'night': 0.42}[STATE]
    layers = [(62, 0.55, (24, 55)), (95, 0.75, (35, 80)), (150, 1.0, (50, 120)), (230, 1.3, (60, 150))]
    n = 0
    for li, (y, sc, hr) in enumerate(layers):
        x = -110 - rng.uniform(0, 20)
        while x < 220:
            w = rng.uniform(9, 22) * sc
            h = rng.uniform(*hr)
            yy = y + rng.uniform(-6, 6)
            m = Mesh('tower_%d' % n, 'city')
            base = hexl(rng.choice(['#3e4658', '#465064', '#3a4050', '#4a4a5c', '#3c4a54']))
            m.box(x, x + w, yy, yy + w, 0, h, cell=2.2 * sc, colfn=tone(base, 0.25, 0.2, seed=n), faces='flt')
            if rng.random() < 0.4:   # setback crown
                m.box(x + w * 0.2, x + w * 0.8, yy + w * 0.2, yy + w * 0.8, h, h + rng.uniform(6, 18), cell=2.2 * sc,
                      colfn=tone(base, 0.25, 0.1, seed=n + 1), faces='flt')
            m.build()
            wm = Mesh('tower_win_%d' % n, 'citywin')
            rows = int(h / 3.2)
            c_pal = WARM[:3] + [hexl('#9ff3ff'), hexl('#ffe3b0')]
            cols = max(1, int(w / 1.6))
            band = rng.random() < 0.3
            wr = random.Random(str(("cw", n))) if VAR_B else rng   # f1b: window lights do not shift the city layout between states
            for i in range(cols):
                for j in range(1, rows):
                    if wr.random() < lit * (1.6 if band and j % 3 == 0 else 1.0):
                        c = wr.choice(c_pal)
                        wm.grid((x + (i + 0.3) * w / cols, yy - 0.05, j * 3.2), (0.35 * w / cols, 0, 0), (0, 0, 1.1),
                                cell=6, col=scl(c, 0.3), emi=scl(c, wr.uniform(0.3, 0.65)))
            if h > 70 and rng.random() < 0.6:   # red beacon
                wm.box(x + w / 2 - 0.4, x + w / 2 + 0.4, yy + w / 2 - 0.4, yy + w / 2 + 0.4, h, h + 0.8, cell=3,
                       col=hexl('#ff3030'), emi=scl(hexl('#ff3030'), 1.2), faces='flt')
            wm.build()
            x += w + rng.uniform(2, 10) * sc
            n += 1
    # holo billboard on a mid tower (unreadable)
    hb = Mesh('holo_billboard', 'citywin')
    hx, hy = (24.0, 61.0) if VAR_B else (20.0, 72.0)
    hb.box(hx - 1, hx + 19, hy + 1, hy + 18, 0, 34, cell=3, colfn=tone('#3a4050', 0.25, 0.2), faces='flt')
    bk = 1.35 if VAR_B else 1.0
    bw, bh = (12, 7) if VAR_B else (17, 10)
    glyph_box(hb, hx, hy, 21, bw, bh, scl(hexl('#ff4fd0'), bk), seed='bill', cols=7, rows=5, frame='#1a1424')
    glyph_box(hb, hx + 1.5, hy - 0.3, 15, bw - 3, 3.5 if VAR_B else 5, scl(hexl('#56f2ff'), bk), seed='bill2', cols=8, rows=3, frame='#101820')
    hb.build()


# ------------------------------------------------------------------ options
def build_f1(pal):
    """Tenement: brick, window grid, zig-zag fire escape, AC units."""
    fac = lambda i: tone(pal['wall'], 0.3, 0.2, streaks=0.35, n=26, seed=('f1', i))
    shop_tower(pal, fac, tone(pal['side'], 0.3, 0.25, streaks=0.3, n=20, seed='f1s'))
    zs = [RZ + 1.0 + 3.1 * k for k in range(9)]
    win_grid('f1_win', '-y', YS, [-14.5, -12.6, SX1 + 0.9, SX1 + 3.0], zs, 1.25, 1.7, WARM, hexl('#4a3a36'), 1,
             skip=lambda x, z: z < RZ + 0.5 or (SX0 - 1.2 < x < SX1 + 0.3), ac=0.35)
    win_grid('f1_win_side', '+x', XA0, [YS + 1.5, YS + 4.5, YS + 7.5, YS + 10.5], zs[1:], 1.2, 1.6, WARM,
             hexl('#4a3a36'), 2, ac=0.3)
    fe = Mesh('f1_fire_escape')
    stc = hexl(pal['steel'])
    x0, x1 = SX1 + 0.6, XA0 - 0.2
    for k, z in enumerate(zs[1:6]):
        zz = z - 0.2
        fe.box(x0, x1, YS - 1.2, YS, zz - 0.1, zz, cell=3, col=stc, var=0.08, faces='ftd')
        fe.box(x0, x1, YS - 1.22, YS - 1.16, zz + 0.95, zz + 1.02, cell=3, col=stc, faces='ft')
        for x in (x0, (x0 + x1) / 2, x1):
            fe.box(x - 0.025, x + 0.025, YS - 1.22, YS - 1.17, zz, zz + 1.0, cell=3, col=stc, faces='fr')
        if k:
            a, b = (x0 + 0.3, x1 - 0.3) if k % 2 else (x1 - 0.3, x0 + 0.3)
            stair_x(fe, a, zz - 3.1, b, zz, YS - 1.1, YS - 0.3, stc)
    fe.build()
    p = Mesh('f1_pipes')
    cyl(p, (XA0 - 0.25, YS - 0.15, 0.18), (XA0 - 0.25, YS - 0.15, 34), 0.09, cell=3, col=hexl('#3d3f44'), var=0.1)
    p.build()
    alley(pal)
    front_building(pal)
    wing(pal, tone(pal['wing'], 0.3, 0.2, seed='w1'))
    side_row(pal)


def build_f2(pal):
    """Converted garage: corrugated cladding, hazard I-beam over the foyer, half-raised roll shutter."""
    fac = lambda i: stripes(pal['wall'], 140, 0.8, 0.25)
    shop_tower(pal, fac, stripes(pal['side'], 60, 0.8, 0.25))
    win = Mesh('f2_bandwin', 'window')
    fr = Mesh('f2_bands')
    rng = random.Random('f2w')
    for z in (6.2, 10.4, 14.6, 18.8):
        for xa, xb in ((-14, SX0 - 0.3), (SX1 + 0.3, XA0)):
            fr.box(xa, xb, YS - 0.2, YS, z - 0.25, z, cell=1.0, colfn=tone('#30353a', 0.25, 0), faces='ftd')
        x = -14.0
        while x < XA0 - 1.2:
            if not (SX0 - 0.4 < x + 1.1 and x < SX1 + 0.4):
                on = rng.random() < STATE_K['lit']
                ec = rng.choice(WARM)
                win.grid((x, YS - 0.1, z), (1.1, 0, 0), (0, 0, 1.4), cell=0.5, col=scl(ec, 0.25) if on else hexl('#141820'),
                         var=0.3, emi=scl(ec, rng.uniform(0.4, 0.8)) if on else (0, 0, 0), wet=(0.35, 0.08))
            x += 1.25
    win.build()
    fr.build()
    ib = Mesh('f2_ibeam')
    ib.box(RX0 - 0.6, XA0, YS - 0.5, YS - 0.1, RZ, RZ + 0.55, cell=0.4,
           colfn=lambda s, t, r: hexl('#d8a52c') if int(s * 40 + t * 2) % 2 else hexl('#2a2a2a'), faces='fdr')
    ib.build()
    rs = Mesh('f2_roll')
    for k in range(7):
        z = RZ - 0.05 - k * 0.12
        rs.box(RX0 + 0.1, RX1 - 0.1, YS + 0.3, YS + 0.38, z - 0.11, z, cell=0.8, colfn=tone('#7c8085', 0.3, 0), faces='fd')
    rs.build()
    wt = Mesh('f2_tank')
    cyl(wt, (0.0, 34.5, 12.0), (0.0, 34.5, 15.0), 1.3, n=9, cell=1.0, col=hexl('#6b5a48'), var=0.2)
    wt.build()
    alley(pal)
    front_building(pal)
    wing(pal, stripes(pal['wing'], 120, 0.8, 0.25))
    side_row(pal)


def build_f3(pal):
    """Kiosk stack: concrete core, cantilevered pods with lit hatches, pipe bundles, sign on a scaffold."""
    fac = lambda i: tone(pal['wall'], 0.3, 0.2, streaks=0.4, n=30, seed=('f3', i))
    shop_tower(pal, fac, tone(pal['side'], 0.3, 0.25, streaks=0.4, n=20, seed='f3s'))
    rng = random.Random('pods')
    pods = Mesh('f3_pods')
    hatch = Mesh('f3_hatches', 'window')
    pod_cols = ['#3f6f78', '#8a5442', '#5d6a3e', '#6a5a7a', '#8a7a5a', '#4a5560']

    def pod(x, y_face, z, w, h, dep, face):
        col = rng.choice(pod_cols)
        on = rng.random() < STATE_K['lit'] + 0.15
        ec = rng.choice(WARM)
        emi = scl(ec, rng.uniform(0.4, 0.8)) if on else (0, 0, 0)
        hc = scl(ec, 0.25) if on else hexl('#151820')
        if face == '-y':
            pods.box(x, x + w, y_face - dep, y_face, z, z + h, cell=0.55, colfn=tone(col, 0.3, 0.15, seed=(x, z)),
                     faces='flrtd')
            hx = x + rng.uniform(0.3, max(0.35, w - 1.3))
            hatch.grid((hx, y_face - dep - 0.03, z + 0.5), (1.0, 0, 0), (0, 0, min(1.0, h - 0.8)), cell=0.4, col=hc,
                       var=0.3, emi=emi, wet=(0.3, 0.1))
            pods.obox((hx + 0.5, y_face - dep - 0.3, z + min(1.65, h - 0.2)), (0.65, 0, 0), (0, 0.32, -0.12),
                      (0, 0.01, 0.03), cell=2, col=hexl('#8a8f94'), var=0.15)
        else:
            pods.box(XA0, XA0 + dep, x, x + w, z, z + h, cell=0.55, colfn=tone(col, 0.3, 0.15, seed=(x, z)),
                     faces='frtdb')
            hy = x + rng.uniform(0.3, max(0.35, w - 1.3))
            hatch.grid((XA0 + dep + 0.03, hy, z + 0.5), (0, 1.0, 0), (0, 0, min(1.0, h - 0.8)), cell=0.4, col=hc,
                       var=0.3, emi=emi, wet=(0.3, 0.1))
    z = RZ + 1.2
    while z < 26:
        x = SX1 + 1.0 + rng.uniform(0, 0.4)
        while x < XA0 - 1.6:
            w = min(rng.uniform(1.8, 3.0), XA0 - 0.1 - x)
            pod(x, YS, z, w, rng.uniform(2.0, 2.6), rng.uniform(0.6, 1.3), '-y')
            x += w + rng.uniform(0.2, 0.8)
        for xx in (-15.5, -13.2):
            if rng.random() < 0.7:
                pod(xx, YS, z + rng.uniform(-0.5, 0.5), 2.0, 2.2, rng.uniform(0.6, 1.1), '-y')
        z += 3.0
    for yy, zz in ((YS + 2.0, 5.2), (YS + 6.0, 4.4), (YS + 4.0, 8.2), (YS + 9.0, 7.0), (YS + 12, 10.0)):
        pod(yy, None, zz, 2.6, 2.2, 0.9, '+x')
    pods.build()
    hatch.build()
    pp = Mesh('f3_pipes')
    for k, x in enumerate((SX1 + 0.4, SX1 + 0.62, SX1 + 0.84)):
        cyl(pp, (x, YS - 0.2 - 0.05 * k, 0.18), (x, YS - 0.2 - 0.05 * k, 34), 0.08 + 0.02 * k, cell=3,
            col=hexl(['#6b6f74', '#7a4a32', '#4b5257'][k]), var=0.1)
    for z in (RZ + 0.6, 12.2):
        for xa, xb in ((-16, SX0 - 0.5), (SX1 + 0.5, XA0)):
            cyl(pp, (xa, YS - 0.35, z), (xb, YS - 0.35, z), 0.11, cell=3, col=hexl('#5b6066'), var=0.1)
    pp.build()
    sc = Mesh('f3_scaffold')
    for x in (SX0 - 0.2, SX1 + 0.2):
        cyl(sc, (x, YS - 0.5, RZ + 0.4), (x, YS - 0.5, SZ1 + 0.8), 0.07, cell=3, col=hexl('#4b5257'))
    for zz in (SZ0 - 0.15, SZ1 + 0.5):
        cyl(sc, (SX0 - 0.4, YS - 0.5, zz), (SX1 + 0.4, YS - 0.5, zz), 0.07, cell=3, col=hexl('#4b5257'))
    sc.build()
    alley(pal)
    front_building(pal)
    wing(pal, tone(pal['wing'], 0.3, 0.2, seed='w3'))
    side_row(pal)


# ------------------------------------------------------------------ lighting states
def lights(pal):
    pink, cyan = (hexl('#f23cff') if VAR_B else hexl('#ff3fa8')), hexl('#3fe0ff')
    k = {'rain': 1.0, 'day': 0.07, 'night': 1.7}[STATE]
    cx, cz = (SX0 + SX1) / 2, (SZ0 + SZ1) / 2
    F.light('AREA', (cx, D_SIGN - 0.3, cz), pink, 3400 * k, size=SW, size_y=SH * 0.85,
            rot=(-math.pi / 2, 0, 0), name='sign_front')
    F.light('AREA', (cx, D_SIGN + 0.05, cz), pink, 550 * k, size=SW * 1.6, size_y=SH,
            rot=(math.pi / 2, 0, 0), shadow=False, name='sign_back')
    F.light('POINT', (cx, D_SIGN - 0.8, SZ0 + 1.2), cyan, 900 * k, size=0.6, name='sign_cyan')
    F.light('POINT', (XA0 + 0.6, YS - 1.5, 4.2), pink, 1500 * k, size=0.8, name='sign_spill_right')
    F.light('POINT', (cx, D_SIGN - 3.5, SZ0 - 0.5), pink, 1600 * k, size=0.8, name='sign_spill_floor')
    kd = {'rain': 1.0, 'day': 0.5, 'night': 1.4}[STATE]
    F.light('AREA', ((RX0 + RX1) / 2, YS + RD - 0.4, 1.6), hexl(pal['screen']), 260 * kd, size=RX1 - RX0, size_y=2.0,
            rot=(-math.pi / 2, 0, 0), name='foyer_glow')
    ac = hexl(pal['alley'])
    F.light('AREA', (0, (Y_ST0 + Y_ST1) / 2, 8.0), ac, 900 * kd, size=3.5, size_y=12, name='alley_wash')
    F.light('POINT', (-0.3, Y_BACK - 1.0, Z_LAND + 2.2), ac, 500 * kd, size=0.3, name='alley_door')
    F.light('POINT', (XA0 + 0.6, YS + 4.4, 4.9), hexl(pal['accent']), 180 * kd, size=0.3, name='alley_sign')
    F.light('POINT', (XA1 + 0.9, YF - 2.0, 4.9), hexl('#56f2ff') if OPT != 'f3' else hexl('#ff6ad8'), 70 * kd,
            size=0.4, name='holo')
    F.light('AREA', (XA1 + 9.0, YF - 0.9, 3.0), hexl('#ffb860'), 160 * kd, size=4.6, size_y=0.5,
            rot=(-math.pi / 2, 0, 0), name='shop_warm')
    F.light('POINT', (XFR + 3.8, Y_KERB + 0.4, 6.3), hexl('#ffcf90'), 120 * kd, size=0.3, name='street_lamp')
    if STATE == 'day':
        F.light('SUN', (0, 0, 40), hexl('#fff0d6'), 7.0, size=math.radians(0.5),
                rot=F.sun_dir_rot((-0.9, 0.4, -0.11) if VAR_B else (-0.88, 0.38, -0.2)), name='sun')
        F.world(hexl('#9fb2c8'), 0.3)
    elif STATE == 'rain':
        F.light('SUN', (0, 0, 40), hexl('#b6c3d6'), 0.6, size=math.radians(12),
                rot=F.sun_dir_rot((-0.3, 0.5, -0.8)), name='sky_sun')
        F.world(hexl('#5d6a82'), 0.6)
    else:
        F.light('SUN', (0, 0, 40), hexl('#5a6aa8'), 0.08, size=math.radians(4),
                rot=F.sun_dir_rot((0.3, 0.6, -0.7)), name='moon')
        F.world(hexl('#1a2038'), 0.22)


def main():
    F.reset(samples=int(os.environ.get('MF_SAMPLES', '48')))
    F.TOON['m'] = F.toon_material()
    F.EMIT['node'].outputs[0].default_value = STATE_K['emi']
    F.camera()
    pal = PAL[OPT]
    {'f1': build_f1, 'f2': build_f2, 'f3': build_f3}[OPT](pal)
    sign_and_spill_geo()
    figure()
    city(pal)
    ground(pal)
    lights(pal)
    vents = [F.proj((XA0 + 0.5, YS + 2.4, 1.0)), F.proj((0.6, Y_ST1 + 1.0, Z_LAND + 0.4)),
             F.proj((XA1 + 4.0, YF + 4.0, HF + 0.6))]
    lay = dict(opt=OPT, state=STATE, sign_plate_px=[F.proj((SX0, D_SIGN, SZ1)), F.proj((SX1, D_SIGN, SZ0))],
               alley_mouth_px=[F.proj((XA0, YS, 0.18)), F.proj((XA1, YF, 0.18))], vents_px=vents,
               front_left_px=F.proj((XA1, YF, HF)), cam=F.CAM)
    with open(OUT + '_layout.json', 'w') as fh:
        json.dump(lay, fh, indent=1)
    F.render_all(OUT, aux=os.environ.get('MF_AUX', '1') == '1')
    print('DONE', OUT)


main()
