"""Cutaway kit: geometry accumulators + toon shading + modules + props (runs inside Blender, but only needs mathutils).
Everything is flat-colour emission with per-face toon bands (3 bands) and banded light pools; ink comes from Freestyle
for layer 'ink' only (structure); layer 'fx' (windows, LEDs, hatch, floor tiles) has no ink."""
import math
import random
from mathutils import Vector


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexc(h):
    h = h.lstrip('#')
    return tuple(lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


PAL = {k: hexc(v) for k, v in dict(
    ink='#0b0716', sky='#1a0f2c', haze='#3a2358',
    lime='#96FF46', lime_d='#52b52c', lime_dd='#2c6e2e', lime_p='#DFFFB8',
    teal='#2a7a70', teal_d='#1c5560', teal_dd='#123640',
    pink='#FF4696', pink_d='#a02a63', cyan='#3FE6FF', cyan_d='#1e8fb0', amber='#FFB938', violet='#7a4bd6',
    metal='#56697c', metal_d='#2e3b4a', metal_dd='#1c2430', white='#E8F4EA', dark='#10151f',
    floor_a='#24585a', floor_b='#1e4c50', slab='#2d3350', slab_d='#1f2438', soil='#3a2a2a',
    wood='#8a5a3a', wood_l='#a97a52', paper='#d8d2b8', glass='#6fd6e0').items()}

L_DIR = Vector((-0.5, -0.3, 0.81)).normalized()
HAZE_COL = PAL['haze']


class Geo:
    def __init__(self):
        self.layers = {'ink': ([], [], []), 'fx': ([], [], [])}    # verts, faces, cols
        self.lights = []        # dict(p=Vector, col=(r,g,b), r=radius, zone=None|(x0,y0,z0,x1,y1,z1), k=strength)
        self.room_zone = None   # bbox of the lit room: faces inside get ambient dim + pools
        self.amb = 0.62
        self.haze_k = 0.0       # per-scene: distance haze scale
        self.mirror = False


G = Geo()


def reset():
    global G
    G = Geo()
    return G


def _lightamt(c, smooth=False):
    amt = 0.0
    tint = [0.0, 0.0, 0.0]
    for l in G.lights:
        z = l['zone']
        if z is not None and not (z[0] <= c.x <= z[3] and z[1] <= c.y <= z[4] and z[2] <= c.z <= z[5]):
            continue
        d = (c - l['p']).length
        a = max(0.0, 1 - d / l['r']) ** 1.6 if smooth else (1.0 if d < l['r'] * 0.45 else (0.5 if d < l['r'] * 0.85 else 0.0))
        a *= l.get('k', 1.0)
        if a > 0:
            amt = max(amt, a)
            for i in range(3):
                tint[i] += l['col'][i] * a
    return amt, tint


def _haze(c):
    # farther from camera = larger (y - x); mix toward haze colour
    t = (c.y - c.x - 6.0) / 46.0 * G.haze_k
    return max(0.0, min(0.7, t))


def face(layer, pts, base, n, emit=False, k=1.0):
    p = [Vector(q) for q in pts]
    c = sum(p, Vector()) / len(p)
    n = Vector(n).normalized()
    if emit:
        tone = 1.0 if n.z > 0.5 else (0.92 if n.y < -0.5 else 0.8)
        col = [b * tone * k for b in base]
    else:
        d = n.dot(L_DIR)
        band = 1.0 if d >= 0.55 else (0.72 if d >= 0.12 else 0.5)
        col = [b * band * k for b in base]
        z = G.room_zone
        inroom = z is not None and z[0] <= c.x <= z[3] and z[1] <= c.y <= z[4] and z[2] <= c.z <= z[5]
        if inroom:
            col = [x * G.amb for x in col]
        amt, tint = _lightamt(c, layer == 'ground')
        if amt > 0:
            col = [col[i] * (1 + 0.9 * amt) + tint[i] * (0.30 if layer == 'ground' else 0.30) * amt for i in range(3)]
    h = _haze(c)
    if h > 0:
        hk = h * (0.55 if emit else 1.0)
        col = [col[i] * (1 - hk) + HAZE_COL[i] * hk for i in range(3)]
    verts, faces, cols = G.layers[layer]
    o = len(verts)
    for q in pts:
        verts.append((q[0], q[1], -q[2] if G.mirror else q[2]))
        cols.append((col[0], col[1], col[2], 1.0))
    faces.append(tuple(range(o, o + len(pts))))


def box(layer, x, y, z, w, d, h, col, emit=False, skip=(), k=1.0):
    x1, y1, z1 = x + w, y + d, z + h
    F = {
        'top': ([(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)], (0, 0, 1)),
        'bot': ([(x, y, z), (x, y1, z), (x1, y1, z), (x1, y, z)], (0, 0, -1)),
        'front': ([(x, y, z), (x1, y, z), (x1, y, z1), (x, y, z1)], (0, -1, 0)),
        'back': ([(x, y1, z), (x, y1, z1), (x1, y1, z1), (x1, y1, z)], (0, 1, 0)),
        'right': ([(x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1)], (1, 0, 0)),
        'left': ([(x, y, z), (x, y, z1), (x, y1, z1), (x, y1, z)], (-1, 0, 0)),
    }
    for nm, (pts, n) in F.items():
        if nm in skip:
            continue
        face(layer, pts, col, n, emit, k)


def cyl(layer, cx, cy, z, r, h, col, seg=10, emit=False, cap=True, k=1.0, r2=None):
    r2 = r if r2 is None else r2
    a = [(2 * math.pi * i / seg + math.pi / seg) for i in range(seg)]
    for i in range(seg):
        a0, a1 = a[i], a[(i + 1) % seg]
        am = (a0 + a1) / 2 if i < seg - 1 else (a0 + a1 + 2 * math.pi) / 2
        n = (math.cos(am), math.sin(am), 0)
        pts = [(cx + r * math.cos(a0), cy + r * math.sin(a0), z), (cx + r * math.cos(a1), cy + r * math.sin(a1), z),
               (cx + r2 * math.cos(a1), cy + r2 * math.sin(a1), z + h), (cx + r2 * math.cos(a0), cy + r2 * math.sin(a0), z + h)]
        face(layer, pts, col, n, emit, k)
    if cap:
        face(layer, [(cx + r2 * math.cos(t), cy + r2 * math.sin(t), z + h) for t in a], col, (0, 0, 1), emit, k)


def pyr(layer, cx, cy, z, r, h, col, seg=4, emit=False, k=1.0, rot=0.0):
    a = [(2 * math.pi * i / seg + rot) for i in range(seg)]
    ap = (cx, cy, z + h)
    for i in range(seg):
        a0, a1 = a[i], a[(i + 1) % seg]
        am = (a0 + a1) / 2 if i < seg - 1 else (a0 + a1 + 2 * math.pi) / 2
        n = (math.cos(am) * h, math.sin(am) * h, r * 0.8)
        face(layer, [(cx + r * math.cos(a0), cy + r * math.sin(a0), z), (cx + r * math.cos(a1), cy + r * math.sin(a1), z), ap], col, n, emit, k)


def quad_x(layer, x, y0, y1, z0, z1, col, nx=1, emit=True, k=1.0):
    """vertical quad in a plane x=const facing +-x"""
    face(layer, [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], col, (nx, 0, 0), emit, k)


def quad_y(layer, y, x0, x1, z0, z1, col, ny=-1, emit=True, k=1.0):
    face(layer, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], col, (0, ny, 0), emit, k)


def quad_z(layer, z, x0, x1, y0, y1, col, emit=False, k=1.0):
    face(layer, [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], col, (0, 0, 1), emit, k)


# ------------------------------------------------------------------ prop context (local -> world, 4 rotations)
class Ctx:
    def __init__(self, ox, oy, z0, w, d, rot, seed=0):
        self.ox, self.oy, self.z0, self.w, self.d, self.rot = ox, oy, z0, w, d, rot
        self.R = random.Random(seed)

    def _xy(self, u, v):
        r = self.rot
        if r == 0:
            return self.ox + u, self.oy + v
        if r == 1:
            return self.ox + self.d - v, self.oy + u
        if r == 2:
            return self.ox + self.w - u, self.oy + self.d - v
        return self.ox + v, self.oy + self.w - u

    def box(self, u, v, z, uw, vd, h, col, emit=False, layer='ink', skip=(), k=1.0):
        a = self._xy(u, v)
        b = self._xy(u + uw, v + vd)
        x, y = min(a[0], b[0]), min(a[1], b[1])
        self_w, self_d = abs(a[0] - b[0]), abs(a[1] - b[1])
        box(layer, x, y, self.z0 + z, self_w, self_d, h, col, emit, skip, k)

    def cyl(self, u, v, z, r, h, col, seg=10, emit=False, layer='ink', cap=True, k=1.0, r2=None):
        x, y = self._xy(u, v)
        cyl(layer, x, y, self.z0 + z, r, h, col, seg, emit, cap, k, r2)

    def pyr(self, u, v, z, r, h, col, seg=4, emit=False, layer='ink', k=1.0):
        x, y = self._xy(u, v)
        pyr(layer, x, y, self.z0 + z, r, h, col, seg, emit, k, self.R.random())

    def led(self, u, v, z, uw, vd, h, col):
        self.box(u, v, z, uw, vd, h, col, emit=True, layer='fx')


P = PAL


def screen(c, u, v, z, uw, h, col=None, depth=0.04):
    """emissive screen on the front (v) face"""
    c.box(u, v - depth, z, uw, depth, h, col or P['cyan'], emit=True, layer='fx')


# ------------------------------------------------------------------ props (local frame: u across, v depth, front at v=0)
def p_vat(c, w=1, d=1, bank=False):
    for i in range(w):
        cu = i + 0.5
        c.box(cu - 0.46, 0.04, 0, 0.92, d - 0.08, 0.28, P['metal_d'])
        c.led(cu - 0.4, -0.01, 0.1, 0.8, 0.03, 0.06, P['lime'])
        c.cyl(cu, d / 2, 0.28, 0.4, 1.95, P['lime_d'], seg=10, emit=True, cap=False)
        c.cyl(cu, d / 2, 1.9, 0.4, 0.28, P['lime'], seg=10, emit=True, cap=True)            # foam band
        c.box(cu - 0.26, d / 2 - 0.46, 0.5, 0.1, 0.05, 1.4, P['lime_p'], emit=True, layer='fx')   # glass highlight
        for b in range(3):
            c.box(cu - 0.2 + 0.18 * b, d / 2 - 0.46, 0.7 + 0.45 * b, 0.07, 0.04, 0.07, P['lime_p'], emit=True, layer='fx')
        c.cyl(cu, d / 2, 2.18, 0.46, 0.22, P['metal'], seg=10)
        c.box(cu - 0.08, d / 2 - 0.08, 2.4, 0.16, 0.16, 0.2, P['metal_d'])
    if bank:
        c.box(0, d - 0.12, 2.15, w, 0.12, 0.1, P['metal_d'])      # shared pipe


def p_vat_bank(c):
    p_vat(c, 3, 1, bank=True)


def p_bench(c):
    c.box(0, 0.05, 0, 3, 0.9, 0.82, P['teal_d'])
    c.box(-0.04, 0, 0.82, 3.08, 1.0, 0.1, P['white'])
    c.led(0.1, -0.01, 0.4, 2.8, 0.03, 0.05, P['lime'])
    c.box(0.25, 0.3, 0.92, 0.35, 0.3, 0.3, P['metal'])           # microscope
    c.cyl(0.9, 0.5, 0.92, 0.1, 0.22, P['lime'], seg=6, emit=True)
    c.cyl(1.2, 0.5, 0.92, 0.08, 0.3, P['pink'], seg=6, emit=True)
    c.box(1.8, 0.55, 0.92, 0.7, 0.06, 0.48, P['metal_dd'])
    c.box(1.85, 0.5, 1.0, 0.6, 0.04, 0.34, P['cyan'], emit=True, layer='fx')


def p_centrifuge(c):
    c.box(0.1, 0.1, 0, 0.8, 0.8, 0.7, P['metal'])
    c.cyl(0.5, 0.5, 0.7, 0.34, 0.2, P['metal_d'], seg=8)
    c.cyl(0.5, 0.5, 0.9, 0.28, 0.06, P['pink'], seg=8, emit=True)
    c.led(0.2, 0.08, 0.3, 0.6, 0.03, 0.06, P['cyan'])


def p_incubator(c):
    c.box(0.05, 0.1, 0, 1.9, 0.8, 0.5, P['metal_d'])
    c.box(0.15, 0.18, 0.5, 1.7, 0.64, 0.38, P['cyan_d'], emit=True)
    c.box(0.15, 0.18, 0.88, 1.7, 0.64, 0.08, P['metal'])
    c.led(0.2, 0.08, 0.2, 1.6, 0.03, 0.06, P['lime'])


def p_monitor_cart(c):
    c.box(0.3, 0.3, 0, 0.4, 0.4, 0.15, P['metal_d'])
    c.box(0.46, 0.46, 0.15, 0.08, 0.08, 0.8, P['metal'])
    c.box(0.12, 0.36, 0.95, 0.76, 0.14, 0.5, P['metal_dd'])
    screen(c, 0.17, 0.36, 1.02, 0.66, 0.36, P['cyan'])
    c.led(0.22, 0.33, 1.1, 0.3, 0.02, 0.04, P['lime'])


def p_helix_tank(c):
    c.cyl(1, 1, 0, 0.95, 0.35, P['metal_d'], seg=10)
    c.cyl(1, 1, 0.35, 0.72, 2.45, P['lime_dd'], seg=12, emit=True, cap=False)
    c.cyl(1, 1, 0.35, 0.99, 0.06, P['lime'], seg=12, emit=True, cap=False)
    c.cyl(1, 1, 2.8, 0.82, 0.3, P['metal'], seg=12)
    c.cyl(1, 1, 3.1, 0.35, 0.18, P['metal_d'], seg=8)
    n = 26
    for i in range(n):
        t = i / (n - 1)
        a = t * math.pi * 5
        z = 0.5 + t * 2.2
        for s, col in ((0, P['pink']), (math.pi, P['lime_p'])):
            c.box(1 + 0.45 * math.cos(a + s) - 0.07, 1 + 0.45 * math.sin(a + s) - 0.07, z, 0.15, 0.15, 0.15, col, emit=True, layer='fx')
        if i % 3 == 0:
            c.box(1 - 0.05, 1 - 0.05, z + 0.03, 0.1, 0.1, 0.09, P['lime'], emit=True, layer='fx')
    for k in range(2):
        c.cyl(0.35 + k * 1.3, 0.2, 0.0, 0.06, 0.4, P['metal'], seg=6)
    c.led(0.4, -0.03, 0.15, 1.2, 0.03, 0.07, P['lime'])


def p_rack(c, w=1, d=1, n=None):
    n = n or w
    for i in range(n):
        u = i * w / n
        ww = w / n
        c.box(u + 0.04, 0.06, 0, ww - 0.08, d - 0.1, 2.35, P['metal_d'])
        c.box(u + 0.04, 0.02, 0.06, ww - 0.08, 0.05, 2.25, P['metal_dd'])
        for j in range(9):
            zz = 0.2 + j * 0.24
            colr = (P['lime'], P['cyan'], P['lime'], P['pink'], P['cyan'], P['lime'])[(i * 5 + j * 3) % 6]
            c.led(u + 0.1, -0.012, zz, ww * 0.55, 0.03, 0.07, colr)
            c.led(u + ww * 0.72, -0.012, zz, 0.07, 0.03, 0.07, P['white'] if (i + j) % 4 else P['pink'])
        c.led(u + 0.08, -0.012, 2.25, ww - 0.2, 0.03, 0.05, P['lime'])


def p_rack_row(c):
    p_rack(c, 4, 1, n=4)


def p_cooling(c):
    c.box(0.04, 0.08, 0, 1.92, 0.84, 1.5, P['metal'])
    for i in range(2):
        c.cyl(0.5 + i, -0.0, 0.35, 0.36, 0.05, P['metal_dd'], seg=8)
        c.cyl(0.5 + i, -0.05, 0.35, 0.18, 0.04, P['cyan'], seg=8, emit=True, layer='fx')
    c.box(0, 0.04, 1.5, 2.0, 0.92, 0.12, P['cyan_d'], emit=True)


def p_console(c):
    c.box(0.0, 0.3, 0, 2.0, 0.7, 0.8, P['metal_d'])
    c.box(-0.05, 0.25, 0.8, 2.1, 0.8, 0.1, P['metal'])
    for i in range(2):
        c.box(0.1 + i * 0.95, 0.65, 0.9, 0.85, 0.08, 0.5, P['metal_dd'])
        screen(c, 0.15 + i * 0.95, 0.65, 0.97, 0.75, 0.36, (P['cyan'], P['lime'])[i])
    c.led(0.1, 0.25, 0.2, 1.8, 0.03, 0.06, P['pink'])


def p_ups(c):
    c.box(0.1, 0.1, 0, 0.8, 0.8, 1.05, P['metal_d'])
    c.led(0.2, 0.08, 0.2, 0.6, 0.03, 0.4, P['lime_d'])
    c.led(0.2, 0.08, 0.7, 0.6, 0.03, 0.08, P['amber'])
    c.box(0.1, 0.1, 1.05, 0.8, 0.8, 0.1, P['metal'])


def p_cable_tray(c):
    c.box(0, 0.2, 0, 3, 0.6, 0.12, P['metal_d'])
    c.led(0.1, 0.35, 0.12, 2.8, 0.1, 0.05, P['pink'])
    c.led(0.1, 0.55, 0.12, 2.8, 0.06, 0.05, P['lime'])


def p_core_tower(c):
    c.box(0.15, 0.15, 0, 1.7, 1.7, 0.35, P['metal_d'])
    c.box(0.45, 0.45, 0.35, 1.1, 1.1, 2.55, P['metal_dd'])
    c.box(0.55, 0.42, 0.6, 0.9, 0.04, 2.0, P['cyan'], emit=True, layer='fx')
    for j in range(8):
        c.led(0.58, 0.395, 0.7 + j * 0.24, 0.84, 0.03, 0.06, P['white'] if j % 2 else P['lime'])
    c.box(0.38, 0.38, 2.9, 1.24, 1.24, 0.16, P['metal'])
    c.cyl(1, 1, 3.15, 0.85, 0.07, P['cyan'], seg=12, emit=True, layer='fx', cap=False)
    c.cyl(1, 1, 3.35, 0.6, 0.06, P['lime'], seg=12, emit=True, layer='fx', cap=False)
    c.box(0.0, 0.0, 0.0, 0.25, 2.0, 0.12, P['pink'], emit=True, layer='fx')
    c.box(0.0, 0.0, 0.0, 2.0, 0.25, 0.12, P['pink'], emit=True, layer='fx')


def p_planter(c):
    c.box(0.0, 0.1, 0, 2.0, 0.8, 0.45, P['wood'])
    c.box(0.06, 0.16, 0.45, 1.88, 0.68, 0.06, P['soil'])
    for i in range(6):
        u = 0.2 + i * 0.32
        v = 0.32 + 0.36 * ((i * 7) % 3) / 2
        col = (P['lime_d'], P['lime'], P['lime_dd'])[i % 3]
        c.pyr(u, v, 0.5, 0.22, 0.5 + 0.1 * (i % 2), col, seg=5, emit=True, k=0.85)
        if i % 2 == 0:
            c.box(u - 0.04, v - 0.04, 1.0, 0.08, 0.08, 0.08, P['pink'], emit=True, layer='fx')


def p_plant_tank(c):
    c.box(0.1, 0.1, 0, 0.8, 0.8, 0.3, P['metal_d'])
    c.box(0.14, 0.14, 0.3, 0.72, 0.72, 1.7, P['cyan_d'], emit=True, k=0.55)
    c.pyr(0.5, 0.5, 0.35, 0.3, 0.8, P['lime_d'], seg=5, emit=True, k=0.85)
    c.pyr(0.5, 0.5, 0.9, 0.25, 0.8, P['lime'], seg=5, emit=True, k=0.85)
    c.pyr(0.5, 0.5, 1.4, 0.18, 0.5, P['lime_p'], seg=5, emit=True, k=0.85)
    c.box(0.1, 0.1, 2.0, 0.8, 0.8, 0.1, P['metal'])
    c.led(0.2, 0.08, 0.1, 0.6, 0.03, 0.05, P['pink'])


def p_seed_wall(c):
    c.box(0, 0.35, 0, 3, 0.65, 2.55, P['metal_d'])
    for i in range(6):
        for j in range(7):
            col = (P['lime'], P['amber'], P['cyan'], P['pink'])[(i * 3 + j * 5) % 4] if (i + j) % 3 else P['metal']
            c.box(0.1 + i * 0.47, 0.3, 0.2 + j * 0.34, 0.4, 0.05, 0.28, P['metal_dd'])
            c.led(0.2 + i * 0.47, 0.265, 0.3 + j * 0.34, 0.2, 0.03, 0.06, col)
    c.led(0.05, 0.3, 2.45, 2.9, 0.04, 0.06, P['lime'])


def p_grow_lamp(c):
    c.box(0.45, 0.45, 0, 0.1, 0.1, 2.0, P['metal'])
    c.box(0.3, 0.3, 0, 0.4, 0.4, 0.1, P['metal_d'])
    c.box(0.05, 0.2, 2.0, 0.9, 0.6, 0.14, P['metal_dd'])
    c.box(0.1, 0.25, 1.95, 0.8, 0.5, 0.06, P['pink'], emit=True, layer='fx')
    for i in range(3):
        c.box(0.2 + i * 0.25, 0.4, 2.14, 0.12, 0.12, 0.08, P['pink'], emit=True, layer='fx')


def p_cistern(c):
    c.cyl(0.5, 0.5, 0, 0.4, 1.0, P['teal'], seg=8)
    c.cyl(0.5, 0.5, 1.0, 0.44, 0.15, P['metal'], seg=8)
    c.led(0.2, 0.08, 0.5, 0.6, 0.03, 0.06, P['cyan'])


def p_seed_tree(c):
    c.cyl(1, 1, 0, 0.95, 0.4, P['metal_d'], seg=10)
    c.cyl(1, 1, 0.4, 0.88, 0.18, P['soil'], seg=10)
    c.cyl(1, 1, 0.58, 0.14, 1.6, P['wood'], seg=6)
    cols = (P['lime_dd'], P['lime_d'], P['lime'])
    for k, (du, dv, zz, rr) in enumerate([(0, 0, 1.7, 0.85), (-0.45, 0.2, 1.4, 0.6), (0.45, -0.1, 1.5, 0.6), (0.1, 0.35, 2.3, 0.6), (-0.2, -0.3, 2.45, 0.5), (0.0, 0.0, 2.75, 0.45)]):
        c.pyr(1 + du, 1 + dv, zz, rr, 0.75, cols[k % 3], seg=5, emit=True, k=0.85)
    for k in range(9):
        a = k * 2.4
        c.box(1 + 0.6 * math.cos(a) - 0.06, 1 + 0.55 * math.sin(a) - 0.06, 1.9 + (k % 4) * 0.28, 0.12, 0.12, 0.12, (P['pink'], P['amber'])[k % 2], emit=True, layer='fx')
    c.led(0.3, -0.03, 0.15, 1.4, 0.03, 0.07, P['pink'])


def p_desk(c):
    c.box(0, 0.35, 0, 2, 0.6, 0.78, P['wood'])
    c.box(-0.04, 0.3, 0.78, 2.08, 0.7, 0.07, P['white'])
    c.box(0.3, 0.7, 0.85, 0.7, 0.06, 0.45, P['metal_dd'])
    screen(c, 0.35, 0.7, 0.92, 0.6, 0.32, P['cyan'])
    c.box(1.2, 0.5, 0.85, 0.5, 0.35, 0.04, P['paper'])
    c.box(0.55, -0.15, 0.0, 0.5, 0.45, 0.5, P['pink_d'])            # chair
    c.box(0.55, -0.15, 0.5, 0.5, 0.45, 0.08, P['pink'])


def p_cabinet(c):
    c.box(0.1, 0.15, 0, 0.8, 0.7, 1.45, P['metal'])
    for j in range(3):
        c.led(0.2, 0.12, 0.2 + j * 0.45, 0.6, 0.03, 0.06, P['amber'])
        c.box(0.15, 0.12, 0.1 + j * 0.45, 0.7, 0.03, 0.02, P['metal_dd'], layer='fx')


def p_shelf_stack(c):
    c.box(0.0, 0.3, 0, 2, 0.6, 2.25, P['metal_d'])
    for j in range(5):
        c.box(0.05, 0.28, 0.1 + j * 0.44, 1.9, 0.06, 0.06, P['metal'], layer='fx')
        u = 0.1
        i = 0
        while u < 1.8:
            ww = 0.18 + 0.1 * ((i * 5 + j * 3) % 3)
            col = (P['paper'], P['amber'], P['cyan_d'], P['pink_d'], P['lime_d'])[(i + j * 2) % 5]
            c.box(u, 0.22, 0.16 + j * 0.44, ww, 0.07, 0.3, col, layer='fx')
            u += ww + 0.04
            i += 1


def p_copier(c):
    c.box(0.1, 0.1, 0, 0.8, 0.8, 0.9, P['metal'])
    c.box(0.1, 0.1, 0.9, 0.8, 0.8, 0.12, P['white'])
    c.led(0.2, 0.08, 0.5, 0.3, 0.03, 0.06, P['lime'])


def p_archive_tower(c):
    c.box(0.1, 0.1, 0, 1.8, 1.8, 0.3, P['metal_d'])
    for i in range(3):
        for j in range(8):
            c.box(0.2 + i * 0.55, 0.45, 0.35 + j * 0.3, 0.5, 0.9, 0.26, P['metal'])
            col = (P['amber'], P['cyan'], P['lime'], P['pink'])[(i * 3 + j) % 4]
            c.led(0.3 + i * 0.55, 0.415, 0.42 + j * 0.3, 0.3, 0.03, 0.06, col)
    c.box(0.15, 0.4, 2.8, 1.7, 1.0, 0.1, P['metal'])
    c.box(0.55, -0.1, 1.1, 0.9, 0.04, 0.55, P['cyan'], emit=True, layer='fx', k=0.8)   # holo file card


def p_box_pile(c):
    c.box(0.1, 0.1, 0, 0.8, 0.7, 0.4, P['paper'])
    c.box(0.15, 0.15, 0.4, 0.6, 0.5, 0.35, P['wood'])
    c.box(0.3, 0.2, 0.75, 0.4, 0.4, 0.15, P['paper'])
    c.led(0.2, 0.08, 0.2, 0.3, 0.03, 0.08, P['pink'])


def p_reception(c):
    c.box(0, 0.2, 0, 3, 0.7, 1.05, P['teal_d'])
    c.box(-0.05, 0.15, 1.05, 3.1, 0.85, 0.1, P['white'])
    c.led(0.1, 0.17, 0.35, 2.8, 0.03, 0.08, P['lime'])
    c.box(1.2, 0.55, 1.15, 0.7, 0.06, 0.4, P['metal_dd'])
    screen(c, 1.25, 0.55, 1.2, 0.6, 0.3, P['lime'])


def p_kiosk(c):
    c.box(0.2, 0.2, 0, 0.6, 0.6, 1.5, P['metal_d'])
    c.box(0.15, 0.15, 1.0, 0.7, 0.2, 0.6, P['metal_dd'])
    screen(c, 0.2, 0.15, 1.08, 0.6, 0.44, P['lime'])
    c.led(0.25, 0.18, 0.3, 0.5, 0.03, 0.06, P['pink'])


def p_seats(c):
    for i in range(2):
        c.box(0.1 + i * 0.95, 0.2, 0, 0.8, 0.6, 0.4, P['teal'])
        c.box(0.1 + i * 0.95, 0.65, 0.4, 0.8, 0.14, 0.45, P['teal_d'])
    c.led(0.1, 0.18, 0.1, 1.8, 0.03, 0.05, P['lime'])


def p_planter_lobby(c):
    c.box(0.1, 0.1, 0, 0.8, 0.8, 0.5, P['metal_d'])
    c.pyr(0.5, 0.5, 0.5, 0.38, 1.0, P['lime_d'], seg=5, emit=True, k=0.85)
    c.pyr(0.5, 0.5, 1.0, 0.28, 0.6, P['lime'], seg=5, emit=True, k=0.85)
    c.led(0.2, 0.08, 0.2, 0.6, 0.03, 0.05, P['lime'])


def p_emblem_sculpture(c):
    c.cyl(1, 1, 0, 0.95, 0.2, P['metal_d'], seg=12)
    c.cyl(1, 1, 0.2, 0.75, 0.05, P['lime'], seg=12, emit=True, layer='fx')
    n = 30
    for i in range(n):
        t = i / (n - 1)
        a = t * math.pi * 4
        z = 0.35 + t * 2.4
        for s, col in ((0, P['lime']), (math.pi, P['cyan'])):
            c.box(1 + 0.35 * math.cos(a + s) - 0.08, 1 + 0.35 * math.sin(a + s) - 0.08, z, 0.17, 0.17, 0.17, col, emit=True, layer='fx')
    c.cyl(1, 1, 0.3, 0.06, 2.6, P['metal'], seg=6)


# ------------------------------------------------------------------ v3 floor clutter
def p_crate(c):
    c.box(0.12, 0.12, 0, 0.76, 0.76, 0.62, P['wood'])
    c.box(0.1, 0.1, 0.62, 0.8, 0.8, 0.08, P['wood_l'])
    c.box(0.08, 0.1, 0.12, 0.84, 0.03, 0.05, P['metal_d'], layer='fx')
    c.led(0.3, 0.08, 0.35, 0.2, 0.03, 0.06, P['amber'])


def p_crate_stack(c):
    c.box(0.08, 0.1, 0, 0.84, 0.8, 0.55, P['wood'])
    c.box(0.14, 0.16, 0.55, 0.7, 0.66, 0.5, P['metal'])
    c.box(0.12, 0.14, 1.05, 0.74, 0.7, 0.06, P['metal_d'])
    c.led(0.25, 0.12, 0.7, 0.4, 0.03, 0.07, P['lime'])
    c.led(0.3, 0.08, 0.2, 0.2, 0.03, 0.06, P['pink'])


def p_barrel(c):
    c.cyl(0.5, 0.5, 0, 0.36, 0.85, P['teal_d'], seg=8)
    c.cyl(0.5, 0.5, 0.82, 0.38, 0.06, P['metal'], seg=8)
    c.cyl(0.5, 0.5, 0.4, 0.375, 0.08, P['amber'], seg=8, emit=True, cap=False, layer='fx')
    c.led(0.42, 0.12, 0.55, 0.16, 0.03, 0.12, P['lime'])


def p_cable_run(c):
    # floor cable bundle: a bent run of dark conduits with a lit strip and two junction boxes
    c.box(0.1, 0.55, 0, 1.2, 0.14, 0.1, P['metal_dd'], layer='fx')
    c.box(1.16, 0.3, 0, 0.14, 0.4, 0.1, P['metal_dd'], layer='fx')
    c.box(1.16, 0.3, 0, 0.7, 0.14, 0.1, P['metal_dd'], layer='fx')
    c.box(0.1, 0.38, 0, 0.8, 0.1, 0.08, P['pink_d'], layer='fx')
    c.box(0.06, 0.32, 0, 0.22, 0.3, 0.2, P['metal_d'])
    c.box(1.72, 0.22, 0, 0.22, 0.3, 0.2, P['metal_d'])
    c.led(0.12, 0.3, 0.2, 0.16, 0.03, 0.05, P['lime'])
    c.led(0.2, 0.58, 0.1, 1.0, 0.1, 0.03, P['cyan'])


def p_box_small(c):
    c.box(0.1, 0.14, 0, 0.5, 0.45, 0.28, P['paper'])
    c.box(0.5, 0.45, 0, 0.4, 0.42, 0.2, P['wood'])
    c.box(0.14, 0.18, 0.28, 0.3, 0.3, 0.14, P['wood_l'])
    c.led(0.14, 0.11, 0.1, 0.3, 0.03, 0.06, P['pink'])


# ------------------------------------------------------------------ v3 event room (back-room clinic / meeting)
def p_holo_table(c):
    c.cyl(1, 1, 0, 0.9, 0.18, P['metal_d'], seg=12)
    c.cyl(1, 1, 0.18, 0.5, 0.6, P['metal_dd'], seg=10)
    c.cyl(1, 1, 0.78, 1.0, 0.1, P['metal'], seg=12)
    c.cyl(1, 1, 0.88, 0.86, 0.04, P['violet'], seg=12, emit=True, layer='fx')
    c.pyr(1, 1, 0.92, 0.7, 1.45, P['violet'], seg=8, emit=True, k=0.75)
    for k, (z, r) in enumerate([(1.1, 0.62), (1.55, 0.48), (2.0, 0.3)]):
        c.cyl(1, 1, z, r, 0.05, P['cyan'], seg=10, emit=True, cap=False, layer='fx')
    for k in range(5):
        a = k * 1.3
        c.box(1 + 0.5 * math.cos(a) - 0.06, 1 + 0.5 * math.sin(a) - 0.06, 1.2 + (k % 3) * 0.3, 0.12, 0.12, 0.12, P['lime_p'], emit=True, layer='fx')
    for k in range(4):                                    # stools
        a = k * math.pi / 2 + 0.7
        c.cyl(1 + 0.98 * math.cos(a), 1 + 0.98 * math.sin(a), 0, 0.2, 0.42, P['pink_d'], seg=6)
    c.led(0.5, -0.03, 0.15, 1.0, 0.03, 0.07, P['violet'])


def p_exam_bed(c):
    c.box(0.1, 0.2, 0, 1.8, 0.6, 0.45, P['metal_d'])
    c.box(0.05, 0.12, 0.45, 1.9, 0.76, 0.2, P['white'])
    c.box(0.05, 0.12, 0.65, 0.5, 0.76, 0.12, P['teal'])                     # raised head rest
    c.box(0.05, 0.1, 0.45, 1.9, 0.03, 0.05, P['metal'], layer='fx')
    c.led(0.2, 0.17, 0.2, 1.5, 0.03, 0.06, P['lime'])
    c.box(1.6, 0.0, 0.0, 0.2, 0.2, 0.9, P['metal'])                         # side arm + monitor
    screen(c, 1.5, 0.0, 0.7, 0.4, 0.22, P['cyan'])


def p_privacy_screen(c):
    for k in range(3):
        u = 0.08 + k * 0.62
        c.box(u, 0.38 + (0.12 if k % 2 else 0.0), 0, 0.6, 0.06, 1.6, P['teal'])
        c.box(u, 0.36 + (0.12 if k % 2 else 0.0), 1.5, 0.6, 0.1, 0.1, P['metal_d'])
        c.led(u + 0.1, 0.34 + (0.12 if k % 2 else 0.0), 0.5 + 0.18 * k, 0.4, 0.03, 0.05, P['lime'])
    c.box(0.02, 0.4, 0.0, 0.08, 0.08, 1.7, P['metal_d'])
    c.box(1.9, 0.4, 0.0, 0.08, 0.08, 1.7, P['metal_d'])


def p_folding_chairs(c):
    for i in range(2):
        c.box(0.12 + i * 0.95, 0.2, 0, 0.7, 0.6, 0.4, P['metal_d'])
        c.box(0.1 + i * 0.95, 0.15, 0.4, 0.74, 0.62, 0.08, P['pink_d'])
        c.box(0.1 + i * 0.95, 0.68, 0.48, 0.74, 0.1, 0.4, P['pink'])


def p_med_cabinet(c):
    c.box(0.12, 0.2, 0, 0.76, 0.65, 1.65, P['white'])
    c.box(0.18, 0.17, 0.5, 0.64, 0.03, 1.0, P['cyan_d'], emit=True, layer='fx')
    c.led(0.42, 0.14, 1.0, 0.16, 0.03, 0.4, P['lime'])
    c.led(0.3, 0.14, 1.12, 0.4, 0.03, 0.16, P['lime'])
    c.led(0.2, 0.14, 0.2, 0.5, 0.03, 0.06, P['amber'])


def p_iv_stand(c):
    c.box(0.46, 0.46, 0.0, 0.08, 0.08, 1.85, P['metal'])
    c.box(0.15, 0.4, 0.0, 0.7, 0.18, 0.08, P['metal_d'])
    c.box(0.4, 0.15, 0.0, 0.18, 0.7, 0.08, P['metal_d'])
    c.box(0.3, 0.4, 1.35, 0.4, 0.2, 0.5, P['lime'], emit=True, k=0.7)
    c.led(0.4, 0.3, 1.6, 0.2, 0.03, 0.06, P['white'])
    c.box(0.62, 0.46, 1.4, 0.03, 0.03, 0.4, P['cyan'], emit=True, layer='fx')


def p_scanner_arch(c):
    c.box(0.0, 0.2, 0, 0.3, 0.6, 2.1, P['metal_d'])
    c.box(1.7, 0.2, 0, 0.3, 0.6, 2.1, P['metal_d'])
    c.box(0.0, 0.2, 1.85, 2.0, 0.6, 0.3, P['metal'])
    c.box(0.3, 0.22, 0.1, 0.02, 0.56, 1.75, P['cyan'], emit=True, layer='fx')
    c.box(1.68, 0.22, 0.1, 0.02, 0.56, 1.75, P['cyan'], emit=True, layer='fx')
    c.led(0.5, 0.17, 1.95, 1.0, 0.03, 0.08, P['violet'])
    c.led(0.05, 0.17, 0.5, 0.2, 0.03, 0.4, P['lime'])


def p_trestle(c):
    c.box(0.0, 0.2, 0.7, 3.0, 0.7, 0.07, P['white'])
    for u in (0.1, 2.75):
        c.box(u, 0.25, 0, 0.12, 0.6, 0.7, P['metal_d'])
    c.box(0.3, 0.45, 0.77, 0.4, 0.3, 0.04, P['paper'])
    c.box(1.2, 0.5, 0.77, 0.5, 0.06, 0.34, P['metal_dd'])
    screen(c, 1.25, 0.5, 0.82, 0.4, 0.24, P['violet'])
    c.cyl(2.3, 0.55, 0.77, 0.1, 0.16, P['lime'], seg=6, emit=True, layer='fx')


# ------------------------------------------------------------------ v3 shop room (street-level storefront)
GOODS = ['lime', 'amber', 'pink', 'cyan', 'lime_p']


def p_display_island(c):
    c.cyl(1, 1, 0, 0.95, 0.5, P['teal_d'], seg=12)
    c.cyl(1, 1, 0.5, 0.88, 0.06, P['lime_p'], seg=12, emit=True, layer='fx')
    c.cyl(1, 1, 0.56, 0.7, 0.5, P['cyan_d'], seg=12, emit=True, cap=False, k=0.6)
    c.cyl(1, 1, 1.06, 0.74, 0.06, P['metal'], seg=12)
    for k in range(7):
        a = k * 0.9
        rr = 0.35 + 0.15 * (k % 2)
        c.box(1 + rr * math.cos(a) - 0.1, 1 + rr * math.sin(a) - 0.1, 1.12, 0.2, 0.2, 0.18 + 0.05 * (k % 3), P[GOODS[k % 5]], emit=True, layer='fx')
    c.box(0.96, 0.96, 1.1, 0.08, 0.08, 0.4, P['metal'])
    c.cyl(1, 1, 1.5, 0.5, 0.05, P['amber'], seg=10, emit=True, cap=True, layer='fx')
    c.led(0.4, -0.03, 0.2, 1.2, 0.03, 0.07, P['lime'])


def p_counter(c):
    c.box(0, 0.2, 0, 3, 0.7, 0.95, P['teal_d'])
    c.box(-0.05, 0.15, 0.95, 3.1, 0.82, 0.1, P['white'])
    c.led(0.1, 0.17, 0.3, 2.8, 0.03, 0.1, P['amber'])
    c.box(0.3, 0.45, 1.05, 0.45, 0.35, 0.3, P['metal_d'])                     # till
    screen(c, 0.35, 0.45, 1.12, 0.35, 0.16, P['lime'])
    c.box(1.4, 0.4, 1.05, 0.25, 0.25, 0.05, P['metal'])
    c.led(1.45, 0.45, 1.1, 0.15, 0.15, 0.03, P['pink'])
    for k in range(3):
        c.box(2.0 + k * 0.28, 0.5, 1.05, 0.22, 0.2, 0.2 + 0.04 * k, P[GOODS[k + 1]], emit=True, layer='fx')


def p_shelf_unit(c):
    c.box(0.0, 0.3, 0, 3, 0.6, 1.95, P['metal_d'])
    for j in range(4):
        c.box(0.05, 0.26, 0.15 + j * 0.46, 2.9, 0.06, 0.05, P['metal'], layer='fx')
        u = 0.12
        i = 0
        while u < 2.75:
            ww = 0.2 + 0.09 * ((i * 5 + j * 3) % 3)
            c.box(u, 0.22, 0.2 + j * 0.46, ww, 0.07, 0.32, P[GOODS[(i + j * 2) % 5]], emit=(i + j) % 3 == 0, layer='fx')
            u += ww + 0.05
            i += 1
    c.led(0.05, 0.26, 1.9, 2.9, 0.04, 0.05, P['lime_p'])


def p_gondola(c):
    c.box(0.05, 0.2, 0, 1.9, 0.6, 0.35, P['teal_d'])
    c.box(0.05, 0.25, 0.35, 1.9, 0.5, 0.28, P['metal'])
    c.box(0.0, 0.2, 0.62, 2.0, 0.6, 0.05, P['metal_d'])
    for k in range(6):
        c.box(0.1 + k * 0.3, 0.3, 0.67, 0.24, 0.4, 0.22 + 0.06 * (k % 3), P[GOODS[k % 5]], emit=(k % 2 == 0), layer='fx')
    c.box(0.95, 0.47, 0.7, 0.1, 0.06, 0.45, P['metal_dd'])
    c.led(0.1, 0.17, 0.15, 1.8, 0.03, 0.06, P['amber'])


def p_cooler(c):
    c.box(0.1, 0.2, 0, 0.8, 0.65, 1.85, P['metal_d'])
    c.box(0.16, 0.17, 0.2, 0.68, 0.03, 1.45, P['cyan'], emit=True, layer='fx', k=0.7)
    for j in range(4):
        for i in range(2):
            c.box(0.2 + i * 0.32, 0.14, 0.3 + j * 0.34, 0.26, 0.04, 0.24, P[GOODS[(i + j) % 5]], emit=True, layer='fx')
    c.led(0.15, 0.14, 1.75, 0.7, 0.03, 0.06, P['lime_p'])


def p_vending(c):
    c.box(0.1, 0.15, 0, 0.8, 0.75, 1.75, P['pink_d'])
    c.box(0.16, 0.12, 0.9, 0.5, 0.03, 0.7, P['amber'], emit=True, layer='fx')
    for j in range(3):
        c.box(0.2, 0.1, 0.95 + j * 0.2, 0.42, 0.03, 0.1, P[GOODS[j + 1]], emit=True, layer='fx')
    c.led(0.7, 0.1, 1.0, 0.1, 0.03, 0.4, P['lime'])
    c.led(0.2, 0.1, 1.62, 0.6, 0.03, 0.06, P['pink'])


def p_crate_display(c):
    c.box(0.1, 0.14, 0, 0.8, 0.72, 0.4, P['wood'])
    c.box(0.14, 0.18, 0.4, 0.72, 0.64, 0.04, P['soil'])
    for k in range(6):
        c.pyr(0.25 + (k % 3) * 0.25, 0.3 + (k // 3) * 0.3, 0.44, 0.13, 0.22, P[GOODS[k % 5]], seg=5, emit=True, k=0.9)
    c.box(0.4, 0.1, 0.45, 0.2, 0.03, 0.3, P['white'], emit=True, layer='fx')


def p_basket_rack(c):
    c.box(0.1, 0.2, 0, 0.8, 0.6, 0.06, P['metal_d'])
    c.box(0.1, 0.2, 0, 0.06, 0.6, 1.05, P['metal'])
    c.box(0.84, 0.2, 0, 0.06, 0.6, 1.05, P['metal'])
    for j in range(3):
        c.box(0.16, 0.24, 0.12 + j * 0.32, 0.68, 0.52, 0.22, P['teal'])
        c.box(0.18, 0.2, 0.28 + j * 0.32, 0.64, 0.04, 0.04, P['lime_p'], emit=True, layer='fx')


def lerp3(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def place_decal(kind, x, y, s, z0, col, k=1.0, seed=0):
    """flat puddle on the floor: decagon with a brighter streak; layer fx (no ink), just above the floor tiles"""
    r = random.Random(seed)
    cx, cy = x + 0.5 + r.uniform(-0.12, 0.12), y + 0.5 + r.uniform(-0.12, 0.12)
    rx, ry = 0.5 * s * r.uniform(0.9, 1.2), 0.38 * s * r.uniform(0.9, 1.2)
    pts = [(cx + rx * math.cos(2 * math.pi * i / 10), cy + ry * math.sin(2 * math.pi * i / 10), z0 + 0.02) for i in range(10)]
    face('fx', pts, col, (0, 0, 1), True, k)
    hl = lerp3(col, (1, 1, 1), 0.5)
    pts2 = [(cx - rx * 0.45, cy + ry * 0.15, z0 + 0.024), (cx + rx * 0.2, cy + ry * 0.15, z0 + 0.024), (cx + rx * 0.3, cy + ry * 0.35, z0 + 0.024), (cx - rx * 0.3, cy + ry * 0.35, z0 + 0.024)]
    face('fx', pts2, hl, (0, 0, 1), True, k)


BUILD = {
    'vat': p_vat, 'vat_bank': p_vat_bank, 'bench': p_bench, 'centrifuge': p_centrifuge, 'incubator_pod': p_incubator,
    'monitor_cart': p_monitor_cart, 'helix_tank': p_helix_tank, 'rack': p_rack, 'rack_row': p_rack_row, 'cooling': p_cooling,
    'console': p_console, 'ups': p_ups, 'core_tower': p_core_tower, 'cable_tray': p_cable_tray, 'planter': p_planter,
    'plant_tank': p_plant_tank, 'seed_wall': p_seed_wall, 'grow_lamp': p_grow_lamp, 'cistern': p_cistern, 'seed_tree': p_seed_tree,
    'desk': p_desk, 'cabinet': p_cabinet, 'shelf_stack': p_shelf_stack, 'copier': p_copier, 'archive_tower': p_archive_tower,
    'box_pile': p_box_pile, 'reception': p_reception, 'kiosk': p_kiosk, 'seats': p_seats, 'planter_lobby': p_planter_lobby,
    'emblem_sculpture': p_emblem_sculpture,
}


BUILD.update({
    'crate': p_crate, 'crate_stack': p_crate_stack, 'barrel': p_barrel, 'cable_run': p_cable_run, 'box_small': p_box_small,
    'holo_table': p_holo_table, 'exam_bed': p_exam_bed, 'privacy_screen': p_privacy_screen, 'folding_chairs': p_folding_chairs,
    'med_cabinet': p_med_cabinet, 'iv_stand': p_iv_stand, 'scanner_arch': p_scanner_arch, 'trestle': p_trestle,
    'display_island': p_display_island, 'counter': p_counter, 'shelf_unit': p_shelf_unit, 'gondola': p_gondola,
    'cooler': p_cooler, 'vending': p_vending, 'crate_display': p_crate_display, 'basket_rack': p_basket_rack,
})


def place_prop(name, x, y, rot, z0, cat, seed=0):
    w, d, h = cat[name]
    fw, fd = (w, d) if rot % 2 == 0 else (d, w)
    c = Ctx(x, y, z0, w, d, rot, seed)
    BUILD[name](c)
    return fw, fd


# ------------------------------------------------------------------ room shell modules
def hatch_front(layer, plane, a0, a1, z0, z1, col, step=0.2, thick=0.05):
    """diagonal 45 degree hatch on a cut face. plane: ('y', yconst, normal) spans x in a0..a1; ('x', xconst, normal) spans y."""
    ax, c0, nrm = plane
    span = a1 - a0
    h = z1 - z0
    t = -h
    while t < span:
        # line from (t, z0) to (t+h, z1) clipped to the face
        p0 = max(t, 0.0)
        p1 = min(t + h, span)
        if p1 - p0 > 0.02:
            za, zb = z0 + (p0 - t), z0 + (p1 - t)
            if ax == 'y':
                face(layer, [(a0 + p0, c0 + nrm * 0.012, za), (a0 + p0 + thick, c0 + nrm * 0.012, za), (a0 + p1 + thick, c0 + nrm * 0.012, zb), (a0 + p1, c0 + nrm * 0.012, zb)], col, (0, nrm, 0), True)
            else:
                face(layer, [(c0 + nrm * 0.012, a0 + p0, za), (c0 + nrm * 0.012, a0 + p0 + thick, za), (c0 + nrm * 0.012, a0 + p1 + thick, zb), (c0 + nrm * 0.012, a0 + p1, zb)], col, (nrm, 0, 0), True)
        t += step


def room_shell(W, D, z0, spec, h=3.3, corp='lime'):
    """floor slab with hatched cut edge, floor tiles with light pools, back + left walls with window/door modules, neon trim, corner post."""
    T = 0.3
    SL = 0.6
    # slab (extends under the walls); its -y and +x faces are the cut section
    box('ink', -T, -T, z0 - SL, W + T, D + T, SL, P['slab'], skip=())
    quad_z('fx', z0 - 0.0, -T, W, -T, D, P['slab_d'])
    hatch_front('fx', ('y', -T, -1), -T, W, z0 - SL + 0.06, z0 - 0.06, P['lime_dd'], 0.22, 0.05)
    hatch_front('fx', ('x', W, 1), -T, D, z0 - SL + 0.06, z0 - 0.06, P['lime_dd'], 0.22, 0.05)
    # floor tiles (1 cell), inset for panel seams
    for i in range(W):
        for j in range(D):
            a = P['floor_a'] if (i + j) % 2 == 0 else P['floor_b']
            quad_z('fx', z0 + 0.012, i + 0.025, i + 0.975, j + 0.025, j + 0.975, a)
    # neon edge on the cut slab top (front and right)
    box('fx', -T, -T, z0 - 0.02, W + T, 0.1, 0.07, P[corp], emit=True)
    box('fx', W - 0.1, -T, z0 - 0.02, 0.1 + 0.0, D + T, 0.07, P[corp], emit=True)
    # walls
    wins_b = [w for w in spec['windows'] if w[0] == 'back']
    wins_l = [w for w in spec['windows'] if w[0] == 'left']
    door = spec['door']
    WH = h
    sill, head = 1.0, 2.5
    # back wall (y = D .. D+T), spans x -T..W
    def wall_run(axis, length, wins, doors):
        # openings sorted; build solid pieces between them
        ops = sorted([(p, p + 2, 'win') for (_, p, _) in wins] + [(doors, doors + 1.4, 'door')] if doors is not None else [(p, p + 2, 'win') for (_, p, _) in wins])
        return ops
    for axis, length, wins, dpos in (('back', W, wins_b, (door['pos'] if door else None)), ('left', D, wins_l, None)):
        ops = wall_run(axis, length, wins, dpos)
        cur = -T if axis == 'back' else -T
        end = length
        def solid(a, b, zlo, zhi, col, emitf=False):
            if b - a <= 0.001 or zhi - zlo <= 0.001:
                return
            if axis == 'back':
                box('ink', a, D, z0 + zlo, b - a, T, zhi - zlo, col)
            else:
                box('ink', -T, a, z0 + zlo, T, b - a, zhi - zlo, col)
        # inner face is what we see: back wall inner face normal -y, left wall inner face normal +x (box handles)
        for (a, b, kind) in ops:
            solid(cur, a, 0, WH, P['teal_d'])
            if kind == 'win':
                solid(a, b, 0, sill, P['teal_d'])
                solid(a, b, head, WH, P['teal_d'])
                # night glass: dark violet with a few lit city windows + mullion
                gz0, gz1 = sill, head
                if axis == 'back':
                    quad_y('fx', D + 0.1, a, b, z0 + gz0, z0 + gz1, P['sky'], -1, True, 1.0)
                    quad_y('fx', D + 0.09, a, b, z0 + gz0, z0 + gz0 + 0.35, hexc('#3a1f5a'), -1, True)
                    for q in range(5):
                        rr = random.Random(int(a * 17 + q * 5))
                        zz = z0 + gz0 + 0.2 + rr.random() * 1.1
                        uu = a + 0.1 + rr.random() * 1.6
                        quad_y('fx', D + 0.085, uu, uu + 0.14, zz, zz + 0.1, (P['lime_p'], P['pink'], P['amber'], P['cyan'])[q % 4], -1, True)
                    box('fx', a + 0.94, D - 0.04, z0 + gz0, 0.1, 0.06, gz1 - gz0, P['metal_dd'])
                    box('fx', a - 0.04, D - 0.03, z0 + gz0 - 0.04, b - a + 0.08, 0.06, 0.08, P['metal'])
                    box('fx', a - 0.04, D - 0.03, z0 + gz1 - 0.04, b - a + 0.08, 0.06, 0.08, P[corp], emit=True)
                else:
                    quad_x('fx', -0.1, a, b, z0 + gz0, z0 + gz1, P['sky'], 1, True)
                    quad_x('fx', -0.09, a, b, z0 + gz0, z0 + gz0 + 0.35, hexc('#3a1f5a'), 1, True)
                    for q in range(5):
                        rr = random.Random(int(a * 13 + q * 7))
                        zz = z0 + gz0 + 0.2 + rr.random() * 1.1
                        uu = a + 0.1 + rr.random() * 1.6
                        quad_x('fx', -0.085, uu, uu + 0.14, zz, zz + 0.1, (P['pink'], P['lime_p'], P['cyan'], P['amber'])[q % 4], 1, True)
                    box('fx', -0.04, a + 0.94, z0 + gz0, 0.06, 0.1, gz1 - gz0, P['metal_dd'])
                    box('fx', -0.03, a - 0.04, z0 + gz0 - 0.04, 0.06, b - a + 0.08, 0.08, P['metal'])
                    box('fx', -0.03, a - 0.04, z0 + gz1 - 0.04, 0.06, b - a + 0.08, 0.08, P[corp], emit=True)
            else:   # door: frame + lit slab
                solid(a, b, 2.3, WH, P['teal_d'])
                if axis == 'back':
                    box('ink', a, D - 0.02, z0, b - a, 0.05, 2.3, P['metal_dd'])
                    box('fx', a + 0.1, D - 0.04, z0, 0.08, 0.04, 2.3, P[corp], emit=True)
                    box('fx', a + b - a - 0.18, D - 0.04, z0, 0.08, 0.04, 2.3, P[corp], emit=True)
                    box('fx', a + 0.1, D - 0.04, 2.22 + z0, b - a - 0.2, 0.04, 0.08, P[corp], emit=True)
                    quad_y('fx', D - 0.05, a + 0.35, b - 0.35, z0 + 1.2, z0 + 1.7, P['cyan'], -1, True)
            cur = b
        solid(cur, end, 0, WH, P['teal_d'])
        # wainscot band + neon trim on the inner face
        if axis == 'back':
            box('fx', -T, D - 0.03, z0, W + T, 0.04, 1.0, P['teal_dd'], skip=('front',) if False else ())
            box('fx', -T, D - 0.04, z0 + 1.0, W + T, 0.05, 0.07, P[corp], emit=True)
            box('fx', -T, D - 0.04, z0 + WH - 0.16, W + T, 0.05, 0.1, P[corp], emit=True)
        else:
            box('fx', -0.04, 0, z0, 0.04, D, 1.0, P['teal_dd'])
            box('fx', -0.04, 0, z0 + 1.0, 0.05, D, 0.07, P[corp], emit=True)
            box('fx', -0.04, 0, z0 + WH - 0.16, 0.05, D, 0.1, P[corp], emit=True)
    # wall-top caps and corner
    box('ink', -T, D, z0 + WH, W + T, T, 0.1, P['metal_dd'])
    box('ink', -T, -T, z0 + WH, T, D + T, 0.1, P['metal_dd'])
    # corner posts of the cut frame (front-left is hidden, right-back is the visible edge)
    box('ink', W - 0.1, D - 0.1, z0, 0.2, 0.3, WH, P['metal_d'])
    box('fx', W - 0.1, D - 0.1, z0, 0.04, 0.3, WH, P[corp], emit=True)
    # v3 decor: wall screens on the back wall (windowless back-room)
    if spec.get('decor') == 'screens':
        dp = door['pos'] if door else 0
        placed = 0
        for x in (0.7, 3.0, 5.4, 7.2):
            if placed >= 2:
                break
            if x + 1.6 > dp - 0.3 and x < dp + 1.7:
                continue
            quad_y('fx', D - 0.05, x, x + 1.6, z0 + 1.35, z0 + 2.65, hexc('#2a1a55'), -1, True, 1.0)
            box('fx', x - 0.04, D - 0.06, z0 + 1.31, 1.68, 0.03, 0.05, P['violet'], emit=True)
            box('fx', x - 0.04, D - 0.06, z0 + 2.65, 1.68, 0.03, 0.05, P['violet'], emit=True)
            for q in range(4):
                bw = 0.25 + 0.3 * ((q * 5 + placed * 3) % 4) / 3
                quad_y('fx', D - 0.06, x + 0.15, x + 0.15 + bw, z0 + 1.55 + q * 0.26, z0 + 1.7 + q * 0.26, (P['cyan'], P['lime_p'], P['pink'], P['cyan'])[q], -1, True, 0.85)
            placed += 1
