"""Round 19: threat vehicle matrix (5 corporations x 3 unit types, base + upgraded), Blender 5.2 headless.

Run: blender -b --factory-startup --python vehicles.py -- <outdir>
Writes veh_beauty.png, veh_glow.png, veh_id.png, veh_normal.png (1920 x 1080 at 3.6x map zoom) and veh_layout.json.
Same camera angle as the raid map (layout.CAM yaw / pitch), same toon + neon materials, so they drop into the map.

Design language (one silhouette family per corporation, readable at map size):
  MERIDIAN   logistics   boxy containers, orange + hazard stripes, amber beacons
  SOLACE     biotech     white rounded capsules, green helix stripe, cool green glow
  HALCYON    civic/police angular wedges, violet, red/blue light bars
  ORBITAL    space       hovering pods + fins + thruster glow, pale blue, star-dot lights
  REBEL_CELL mirror      improvised scrap: asymmetric plates, ram bars, spray-red tags
Upgraded (+): bigger by 10 %, extra armour plates, a second light, rank chevrons on the roof.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else "."
os.makedirs(OUT, exist_ok=True)
rng = random.Random(1919)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.eevee.taa_render_samples = 24
scene.view_settings.view_transform = "Standard"


class Acc:
    def __init__(self, name):
        self.bm = bmesh.new()
        self.col = self.bm.faces.layers.float_color.new("col")
        self.fj = self.bm.faces.layers.float.new("fj")
        self.bid = self.bm.faces.layers.float_color.new("bid")
        self.name = name

    def face(self, pts, col, bid):
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f[self.col] = tuple(col) + (1.0,)
        f[self.fj] = rng.random()
        f[self.bid] = tuple(bid) + (1.0,)

    def obj(self, mat):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        ob = bpy.data.objects.new(self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        return ob


SOLID, NEON = Acc("solid"), Acc("neon")
BID = [None]


def obox(cx, cy, z0, L, W, H, ang, col, acc=None, taper=0.0, front_taper=0.0):
    acc = acc or SOLID
    bid = BID[0]
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v, z):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca, z)
    hl, hw = L / 2, W / 2
    b = [P(-hl, -hw, z0), P(hl, -hw, z0), P(hl, hw, z0), P(-hl, hw, z0)]
    u = [P(-hl + taper, -hw + taper, z0 + H), P(hl - taper - front_taper, -hw + taper, z0 + H),
         P(hl - taper - front_taper, hw - taper, z0 + H), P(-hl + taper, hw - taper, z0 + H)]
    for q in [(b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])]:
        acc.face(list(q), col, bid)
    acc.face(u, col, bid)
    acc.face(list(reversed(b)), col, bid)


def prism(cx, cy, z0, z1, r0, n, col, r1=None, acc=None, axis="z", ang=0.0):
    """Vertical prism, or a horizontal capsule-ish cylinder along heading `ang` when axis='h'."""
    acc = acc or SOLID
    bid = BID[0]
    r1 = r0 if r1 is None else r1
    if axis == "z":
        lo = [(cx + r0 * math.cos(2 * math.pi * i / n), cy + r0 * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
        hi = [(cx + r1 * math.cos(2 * math.pi * i / n), cy + r1 * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
    else:   # horizontal: z0 = centre height, z1 = length
        ca, sa = math.cos(ang), math.sin(ang)

        def P(u, a, r):
            return (cx + u * ca - r * math.cos(a) * sa, cy + u * sa + r * math.cos(a) * ca, z0 + r * math.sin(a))
        lo = [P(-z1 / 2, 2 * math.pi * i / n, r0) for i in range(n)]
        hi = [P(z1 / 2, 2 * math.pi * i / n, r1) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        acc.face([lo[i], lo[j], hi[j], hi[i]], col, bid)
    acc.face(hi, col, bid)
    acc.face(list(reversed(lo)), col, bid)


def beam(p0, p1, w, col, acc=None):
    acc = acc or SOLID
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized() * (w / 2)
    b = d.cross(a).normalized() * (w / 2)
    c0 = [p0 + a + b, p0 - a + b, p0 - a - b, p0 + a - b]
    c1 = [p1 + a + b, p1 - a + b, p1 - a - b, p1 + a - b]
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(c0[i]), tuple(c0[j]), tuple(c1[j]), tuple(c1[i])], col, BID[0])


def rim(cx, cy, z, L, W, ang, col, w=0.35):
    ca, sa = math.cos(ang), math.sin(ang)
    c = [(cx + ca * u - sa * v, cy + sa * u + ca * v, z) for u, v in ((-L / 2, -W / 2), (L / 2, -W / 2), (L / 2, W / 2), (-L / 2, W / 2))]
    for i in range(4):
        beam(c[i], c[(i + 1) % 4], w, col, acc=NEON)


def at(cx, cy, ang, u, v):
    ca, sa = math.cos(ang), math.sin(ang)
    return cx + u * ca - v * sa, cy + u * sa + v * ca


def chevrons(cx, cy, z, ang, col, n=2):
    for k in range(n):
        x, y = at(cx, cy, ang, -1.0 - k * 1.1, 0)
        for s in (-1, 1):
            p0 = at(x, y, ang, 0, 0)
            p1 = at(x, y, ang, -0.8, s * 1.0)
            beam((p0[0], p0[1], z), (p1[0], p1[1], z), 0.3, col, acc=NEON)


def lightbar(cx, cy, z, ang, cols, L=2.4):
    for i, c in enumerate(cols):
        v = (i - (len(cols) - 1) / 2) * (L / len(cols))
        x, y = at(cx, cy, ang, 0, v)
        obox(x, y, z, 0.8, L / len(cols) * 0.9, 0.45, ang, c, acc=NEON)


# ------------------------------------------------------------------ palettes
ORANGE, RUST, DARK = (1.0, 0.55, 0.10), (0.62, 0.28, 0.12), (0.16, 0.15, 0.18)
S_GREEN, S_WHITE = (0.24, 1.0, 0.55), (0.86, 0.9, 0.88)
H_VIO, H_BODY = (0.55, 0.48, 1.0), (0.62, 0.58, 0.88)
O_BLUE, O_BODY = (0.5, 0.66, 1.0), (0.78, 0.82, 0.92)
R_RED, R_BODY = (0.91, 0.08, 0.12), (0.36, 0.30, 0.30)
RED, BLUE, AMBER, WHITE = (1, 0.15, 0.12), (0.16, 0.42, 1.0), (1.0, 0.62, 0.15), (0.95, 0.95, 1.0)


# ------------------------------------------------------------------ vehicles (x, y = centre, a = heading, up = upgraded)
def meridian_courier(x, y, a, up):
    obox(x, y, 1.0, 5.0, 1.8, 1.0, a, DARK, taper=0.2)
    n = 2 if up else 1
    for k in range(n):
        px, py = at(x, y, a, -0.6 - k * 2.0, 0)
        obox(px, py, 2.0, 1.8, 2.0, 1.6, a, ORANGE)
        rim(px, py, 3.6, 1.8, 2.0, a, AMBER, 0.15)
    hx, hy = at(x, y, a, 2.4, 0)
    obox(hx, hy, 1.2, 0.6, 1.4, 0.4, a, WHITE, acc=NEON)
    tx, ty = at(x, y, a, -2.6, 0)
    beam((tx, ty, 1.5), (*at(x, y, a, -10, 0), 1.5), 0.6, ORANGE, acc=NEON)
    if up:
        for s in (-1, 1):
            fx, fy = at(x, y, a, -2.2, s * 1.3)
            obox(fx, fy, 1.4, 1.6, 0.2, 1.4, a, RUST)
        chevrons(x, y, 3.7, a, ORANGE)


def meridian_hauler(x, y, a, up):
    s = 1.1 if up else 1.0
    cx, cy = at(x, y, a, 4.8 * s, 0)
    obox(cx, cy, 0.6, 3.0 * s, 4.6 * s, 3.8 * s, a, (0.85, 0.82, 0.78), front_taper=0.6)
    obox(x - 0, y - 0, 0.6, 1.0, 1.0, 0.2, a, DARK)
    bx, by = at(x, y, a, -1.4 * s, 0)
    obox(bx, by, 0.9, 10 * s, 4.6 * s, 4.6 * s, a, ORANGE)
    for k in range(8):                                  # ribs
        rx, ry = at(bx, by, a, -4.5 * s + k * 1.3 * s, 2.35 * s)
        obox(rx, ry, 1.1, 0.3, 0.12, 4.2 * s, a, RUST)
    for k in range(5):                                  # hazard stripes on the bumper
        hx, hy = at(cx, cy, a, 1.55 * s, -2.0 + k * 1.0)
        obox(hx, hy, 0.7, 0.15, 0.5, 0.6, a, AMBER if k % 2 == 0 else DARK, acc=NEON if k % 2 == 0 else SOLID)
    obox(cx, cy, 4.4 * s, 0.8, 1.0, 0.5, a, AMBER, acc=NEON)
    if up:
        bx2, by2 = at(x, y, a, -1.4 * s, 0)
        obox(bx2, by2, 5.5 * s, 9 * s, 4.4 * s, 3.4 * s, a, RUST)
        for sgn in (-1, 1):
            px, py = at(x, y, a, -1.0, sgn * 2.5 * s)
            obox(px, py, 0.5, 11 * s, 0.3, 1.6, a, DARK)
        chevrons(*at(x, y, a, -1.4 * s, 0), 9.0 * s, a, ORANGE, 3)
        obox(*at(cx, cy, a, 0, 1.2), 4.4 * s, 0.8, 1.0, 0.5, a, AMBER, acc=NEON)


def meridian_tow(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.6, 8 * s, 4.0 * s, 2.4 * s, a, (0.85, 0.82, 0.78), front_taper=0.4)
    cx, cy = at(x, y, a, -1.5 * s, 0)
    beam((cx, cy, 3.0 * s), (*at(x, y, a, -6.5 * s, 0), 7.5 * s), 0.8, ORANGE)        # boom
    hx, hy = at(x, y, a, -6.5 * s, 0)
    beam((hx, hy, 7.5 * s), (hx, hy, 3.0), 0.15, DARK)
    obox(hx, hy, 2.2, 1.2, 2.2, 0.8, a, AMBER, acc=NEON)                              # clamp
    # the seal it drops behind it: a striped barrier
    bx, by = at(x, y, a, -10 * s, 0)
    obox(bx, by, 0.1, 0.8, 7 * s, 1.4, a, DARK)
    for k in range(5):
        px, py = at(bx, by, a, 0, -3 * s + k * 1.5 * s)
        obox(px, py, 1.5, 0.85, 0.7 * s, 0.35, a, AMBER if k % 2 == 0 else RED, acc=NEON)
    obox(*at(x, y, a, 2.5 * s, 0), 3.1 * s, 0.8, 1.2, 0.4, a, AMBER, acc=NEON)
    if up:
        beam((cx, cy, 3.0 * s), (*at(x, y, a, -6.5 * s, 1.8), 7.0 * s), 0.6, ORANGE)
        obox(*at(x, y, a, 0, 0), 3.0 * s, 4 * s, 4.2 * s, 0.4, a, RUST)
        chevrons(*at(x, y, a, 2.0, 0), 3.1 * s, a, ORANGE)


def solace_paramedic(x, y, a, up):
    s = 1.1 if up else 1.0
    prism(x, y, 2.0, 7.0 * s, 1.5 * s, 10, S_WHITE, r1=1.2 * s, axis="h", ang=a)
    for sgn in (-1, 1):
        px, py = at(x, y, a, 0, sgn * 1.7 * s)
        obox(px, py, 0.6, 5 * s, 0.6, 0.5, a, (0.3, 0.32, 0.34))
        obox(px, py, 0.55, 4 * s, 0.65, 0.1, a, S_GREEN, acc=NEON)
    for k in range(4):                                  # helix stripe
        px, py = at(x, y, a, -2.4 * s + k * 1.6 * s, 0)
        obox(px, py, 3.45 * s, 0.4, 1.0, 0.15, a + 0.6 * (1 if k % 2 else -1), S_GREEN, acc=NEON)
    beam((*at(x, y, a, -3.6 * s, 0), 2.0), (*at(x, y, a, -12, 0), 2.0), 0.7, S_GREEN, acc=NEON)
    if up:
        prism(*at(x, y, a, -0.5, 0), 3.5 * s, 4.4 * s, 0.9, 8, S_GREEN, r1=0.4, acc=NEON)
        for sgn in (-1, 1):
            px, py = at(x, y, a, 1.0, sgn * 1.6 * s)
            obox(px, py, 1.6, 3.6, 0.3, 1.4, a, (0.55, 0.6, 0.58))
        chevrons(*at(x, y, a, -1.5, 0), 3.6 * s, a, S_GREEN)


def solace_collector(x, y, a, up):
    s = 1.1 if up else 1.0
    cx, cy = at(x, y, a, 4.8 * s, 0)
    obox(cx, cy, 0.6, 3.0 * s, 4.4 * s, 3.4 * s, a, S_WHITE, taper=0.4, front_taper=0.6)
    obox(*at(x, y, a, -1.0 * s, 0), 0.6, 10 * s, 4.4 * s, 0.6, a, (0.3, 0.32, 0.34))
    n = 4 if up else 3
    for k in range(n):
        px, py = at(x, y, a, -4.6 * s + k * 2.7 * s, 0)
        prism(px, py, 1.2, 4.6 * s, 1.2 * s, 10, (0.75, 0.82, 0.8), r1=1.0 * s)
        prism(px, py, 4.6 * s, 4.9 * s, 1.0 * s, 10, S_GREEN, acc=NEON)
    obox(cx, cy, 4.0 * s, 0.8, 1.6, 0.4, a, S_GREEN, acc=NEON)
    if up:
        for sgn in (-1, 1):
            obox(*at(x, y, a, -1.0 * s, sgn * 2.4 * s), 0.6, 10 * s, 0.3, 2.2, a, (0.55, 0.6, 0.58))
        chevrons(*at(cx, cy, a, -0.3, 0), 4.05 * s, a, S_GREEN)


def solace_doser(x, y, a, up):
    s = 1.1 if up else 1.0
    prism(x, y, 2.6 * s, 6 * s, 1.8 * s, 10, S_WHITE, r1=1.5 * s, axis="h", ang=a)
    for sgn in (-1, 1):                                  # misting arms
        p0 = at(x, y, a, 0.5, sgn * 1.6 * s)
        p1 = at(x, y, a, 0.5, sgn * 5.5 * s)
        beam((*p0, 3.0 * s), (*p1, 3.2 * s), 0.35, (0.5, 0.55, 0.55))
        for k in range(3):
            pk = at(x, y, a, 0.5, sgn * (2.6 + k * 1.2) * s)
            prism(pk[0], pk[1], 1.0, 2.9 * s, 0.3, 6, S_GREEN, r1=0.05, acc=NEON)
    for k in range(4):                                   # hover pods
        px, py = at(x, y, a, (-1.8 if k < 2 else 1.8) * s, (-1.6 if k % 2 else 1.6) * s)
        prism(px, py, 0.6, 1.2, 0.8, 8, (0.4, 0.45, 0.44))
        prism(px, py, 0.55, 0.62, 0.8, 8, S_GREEN, acc=NEON)
    if up:
        prism(*at(x, y, a, -2.2 * s, 0), 4.4 * s, 5.6 * s, 0.9, 8, (0.75, 0.82, 0.8))
        chevrons(*at(x, y, a, 0.5, 0), 4.3 * s, a, S_GREEN)


def halcyon_inspector(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.5, 6.4 * s, 3.0 * s, 1.6, a, H_BODY, taper=0.3, front_taper=1.2)
    obox(*at(x, y, a, -0.6, 0), 2.1, 3.2 * s, 2.4 * s, 1.0, a, (0.24, 0.22, 0.36), taper=0.3)
    rim(x, y, 2.1, 6.0 * s, 2.8 * s, a, H_VIO, 0.3)
    lightbar(*at(x, y, a, -0.4, 0), 3.15, a, [RED, BLUE])
    beam((*at(x, y, a, -3.3 * s, 0), 1.0), (*at(x, y, a, -14, 0), 1.0), 0.6, H_VIO, acc=NEON)
    if up:
        for sgn in (-1, 1):
            obox(*at(x, y, a, 0.8, sgn * 1.6 * s), 0.7, 4.0, 0.25, 1.2, a, (0.4, 0.38, 0.55))
        lightbar(*at(x, y, a, 2.0, 0), 1.9, a, [BLUE, RED], L=2.0)
        chevrons(*at(x, y, a, -1.6, 0), 3.2, a, H_VIO)


def halcyon_bailiff(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.4, 11 * s, 5.2 * s, 3.0 * s, a, H_BODY, taper=0.5)
    obox(*at(x, y, a, 3.5 * s, 0), 0.6, 3.0 * s, 5.4 * s, 2.2 * s, a, (0.24, 0.22, 0.36), taper=0.9)
    obox(*at(x, y, a, -1.0, 0), 3.4 * s, 5.0 * s, 3.8 * s, 1.6, a, H_VIO, taper=0.5)
    rim(x, y, 3.4 * s, 10 * s, 4.8 * s, a, H_VIO, 0.45)
    lightbar(*at(x, y, a, 1.4, 0), 5.0 * s, a, [RED, BLUE])
    if up:
        beam((*at(x, y, a, -1.0, 0), 5.2 * s), (*at(x, y, a, 3.5, 0), 5.6 * s), 0.7, (0.2, 0.2, 0.24))   # turret gun
        for sgn in (-1, 1):
            obox(*at(x, y, a, 0, sgn * 2.8 * s), 0.6, 10 * s, 0.4, 2.0, a, (0.4, 0.38, 0.55))
        chevrons(*at(x, y, a, -3.5, 0), 3.5 * s, a, H_VIO, 3)


def halcyon_lockdown(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.5, 7.5 * s, 3.6 * s, 2.6 * s, a, H_BODY, taper=0.4)
    rim(x, y, 3.1 * s, 7.0 * s, 3.4 * s, a, H_VIO, 0.4)
    lightbar(x, y, 3.15 * s, a, [RED, BLUE])
    # fold-out barrier wall (the link it freezes / seals)
    bx, by = at(x, y, a, -6.5 * s, 0)
    for k in range(5):
        px, py = at(bx, by, a, 0, -4 * s + k * 2 * s)
        obox(px, py, 0.1, 0.7, 1.8 * s, 2.0, a + 0.15 * (k - 2), (0.35, 0.33, 0.45))
        obox(px, py, 2.1, 0.75, 1.8 * s, 0.3, a + 0.15 * (k - 2), (0.7, 0.92, 1.0), acc=NEON)
    if up:
        prism(*at(x, y, a, -1.5, 0), 3.1 * s, 5.0 * s, 0.4, 6, (0.3, 0.3, 0.36))
        prism(*at(x, y, a, -1.5, 0), 5.0 * s, 5.6 * s, 1.0, 8, (0.7, 0.92, 1.0), acc=NEON)
        chevrons(*at(x, y, a, 1.8, 0), 3.2 * s, a, H_VIO)


def orbital_lander(x, y, a, up):
    s = 1.1 if up else 1.0
    z = 6.0
    prism(x, y, z, z + 5.0 * s, 3.8 * s, 8, O_BODY, r1=2.0 * s)
    prism(x, y, z + 5.0 * s, z + 6.2 * s, 2.0 * s, 8, O_BLUE, r1=0.8, acc=NEON)
    for k in range(4):
        aa = math.pi / 4 + k * math.pi / 2
        beam((x + 3.0 * s * math.cos(aa), y + 3.0 * s * math.sin(aa), z + 0.5),
             (x + 4.8 * s * math.cos(aa), y + 4.8 * s * math.sin(aa), z - 2.4), 0.4, (0.3, 0.32, 0.4))
    prism(x, y, z - 0.6, z, 2.6 * s, 10, (1.0, 0.6, 0.3), acc=NEON)
    for k in range(6):                                  # star-dot lights
        aa = k * math.pi / 3
        prism(x + 3.0 * s * math.cos(aa), y + 3.0 * s * math.sin(aa), z + 2.0, z + 2.4, 0.25, 6, WHITE, acc=NEON)
    if up:
        for k in range(4):
            aa = k * math.pi / 2
            obox(x + 3.6 * s * math.cos(aa), y + 3.6 * s * math.sin(aa), z + 1.0, 1.4, 0.3, 3.0, aa + math.pi / 2, (0.55, 0.6, 0.75))
        chevrons(x, y, z + 6.3 * s, a, O_BLUE)


def orbital_skimmer(x, y, a, up):
    s = 1.1 if up else 1.0
    z = 1.6
    obox(x, y, z, 7.0 * s, 2.6 * s, 0.8, a, O_BODY, taper=0.3, front_taper=2.0)
    for sgn in (-1, 1):                                  # fins
        p0 = at(x, y, a, -2.2 * s, sgn * 1.2 * s)
        p1 = at(x, y, a, -3.4 * s, sgn * 3.6 * s)
        beam((*p0, z + 0.5), (*p1, z + 0.4), 0.3, O_BODY)
        obox(*p1, z + 0.2, 0.8, 0.3, 0.4, a, O_BLUE, acc=NEON)
    prism(*at(x, y, a, -3.6 * s, 0), z + 0.4, 1.2, 0.5, 8, (1.0, 0.6, 0.3), axis="h", ang=a, acc=NEON)
    beam((*at(x, y, a, -4.0 * s, 0), z + 0.4), (*at(x, y, a, -16, 0), z + 0.4), 0.5, O_BLUE, acc=NEON)
    obox(x, y, z - 0.2, 6.0 * s, 2.2 * s, 0.2, a, O_BLUE, acc=NEON)       # hover glow
    if up:
        obox(*at(x, y, a, 0.5, 0), z + 0.8, 2.6, 1.6 * s, 0.7, a, (0.55, 0.6, 0.75), taper=0.2)
        chevrons(*at(x, y, a, -0.8, 0), z + 1.55, a, O_BLUE)


def orbital_debris(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.4, 10 * s, 5.0 * s, 1.6, a, (0.4, 0.42, 0.5))
    for sgn in (-1, 1):                                  # crawler tracks
        obox(*at(x, y, a, 0, sgn * 2.7 * s), 0.0, 10.5 * s, 1.0, 1.6, a, DARK)
    n = 9 if up else 6                                   # the debris load (scrap satellites)
    for k in range(n):
        px, py = at(x, y, a, rng.uniform(-4, 4) * s, rng.uniform(-1.8, 1.8) * s)
        hh = rng.uniform(1.2, 2.6)
        obox(px, py, 2.0, rng.uniform(1.2, 2.4), rng.uniform(1.0, 2.0), hh, rng.uniform(0, 3), rng.choice([O_BODY, (0.55, 0.5, 0.45), (0.7, 0.62, 0.4)]))
    for k in range(4):
        px, py = at(x, y, a, -4 + k * 2.6, 2.55 * s)
        prism(px, py, 1.2, 1.5, 0.25, 6, O_BLUE, acc=NEON)
    if up:
        beam((*at(x, y, a, 4.8 * s, -2.6), 0.8), (*at(x, y, a, 4.8 * s, 2.6), 0.8), 0.8, (0.6, 0.62, 0.7))
        chevrons(*at(x, y, a, -2.0, 0), 4.8, a, O_BLUE)


def cell_informant(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.8, 4.0 * s, 1.2, 0.9, a, R_BODY, taper=0.2)
    obox(*at(x, y, a, -1.0, 0), 1.7, 1.6, 1.1, 0.6, a, (0.2, 0.18, 0.2))
    beam((*at(x, y, a, -1.4, 0.3), 1.8), (*at(x, y, a, -1.8, 0.4), 6.0 * s), 0.12, (0.3, 0.3, 0.3))   # antenna
    prism(*at(x, y, a, -1.8, 0.4), 6.0 * s, 6.4 * s, 0.3, 6, R_RED, acc=NEON)
    obox(*at(x, y, a, 1.6, 0), 1.2, 0.5, 1.0, 0.4, a, WHITE, acc=NEON)
    beam((*at(x, y, a, -2.0, 0), 1.2), (*at(x, y, a, -9, 0), 1.2), 0.45, R_RED, acc=NEON)
    if up:
        prism(*at(x, y, a, 0.2, -0.9), 1.0, 2.6, 0.5, 6, (0.5, 0.48, 0.4))           # jury-rigged dish
        chevrons(*at(x, y, a, 0.4, 0), 1.75, a, R_RED, 1)


def cell_loyalist(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(x, y, 0.5, 8.5 * s, 4.0 * s, 3.4 * s, a, R_BODY, taper=0.3)
    for k in range(4):                                   # mismatched armour plates
        px, py = at(x, y, a, -3.2 + k * 2.1, -2.05 * s)
        obox(px, py, 0.9 + rng.uniform(0, 0.5), 1.9, 0.2, rng.uniform(1.4, 2.2), a + rng.uniform(-0.1, 0.1),
             rng.choice([(0.5, 0.45, 0.4), (0.3, 0.32, 0.36), (0.6, 0.25, 0.2)]))
    beam((*at(x, y, a, 4.6 * s, -2.0), 1.0), (*at(x, y, a, 4.6 * s, 2.0), 1.0), 0.6, (0.6, 0.6, 0.62))   # ram bar
    for k in range(3):                                   # spray tags (emissive red scrawls)
        px, py = at(x, y, a, -2.5 + k * 2.2, -2.02 * s)
        obox(px, py, 1.6 + 0.3 * k, 1.4, 0.06, 0.25, a + 0.3, R_RED, acc=NEON)
    rim(x, y, 3.9 * s, 8.0 * s, 3.6 * s, a, R_RED, 0.3)
    if up:
        obox(*at(x, y, a, -1.0, 0), 3.9 * s, 3.2, 2.4, 1.0, a, (0.3, 0.3, 0.32))
        beam((*at(x, y, a, -1.0, 0), 4.6 * s), (*at(x, y, a, 2.6, 0), 4.8 * s), 0.5, (0.2, 0.2, 0.22))
        chevrons(*at(x, y, a, -3.4, 0), 4.0 * s, a, R_RED, 3)


def cell_purger(x, y, a, up):
    s = 1.1 if up else 1.0
    obox(*at(x, y, a, 3.6 * s, 0), 0.5, 2.8 * s, 3.8 * s, 3.0 * s, a, R_BODY, front_taper=0.5)
    obox(*at(x, y, a, -1.4 * s, 0), 0.6, 7.0 * s, 3.8 * s, 0.8, a, (0.25, 0.24, 0.26))
    prism(*at(x, y, a, -1.4 * s, 0), 2.6 * s, 6.4 * s, 1.5 * s, 10, (0.72, 0.62, 0.3), axis="h", ang=a)   # fuel tank
    for k in range(3):
        px, py = at(x, y, a, -3.6 * s + k * 2.2 * s, 0)
        prism(px, py, 2.6 * s, 0.4, 1.55 * s, 10, R_RED, axis="h", ang=a, acc=NEON)
    nx, ny = at(x, y, a, 5.2 * s, 0)
    beam((*at(x, y, a, 2.0, 0), 3.6 * s), (nx, ny, 3.3 * s), 0.5, (0.2, 0.2, 0.22))       # flame nozzle
    beam((nx, ny, 3.3 * s), (*at(x, y, a, 9.5 * s, 0), 2.6), 0.9, (1.0, 0.45, 0.1), acc=NEON)
    if up:
        prism(*at(x, y, a, -1.4 * s, 2.2 * s), 2.0 * s, 5.4 * s, 0.9 * s, 8, (0.72, 0.62, 0.3), axis="h", ang=a)
        chevrons(*at(x, y, a, 3.6 * s, 0), 3.6 * s, a, R_RED)


ROWS = [("MERIDIAN", ORANGE, [("COURIER", "fast", meridian_courier), ("HAULER", "heavy", meridian_hauler), ("TOW TRUCK", "seals a link", meridian_tow)]),
        ("SOLACE", S_GREEN, [("PARAMEDIC", "fast", solace_paramedic), ("COLLECTOR", "heavy", solace_collector), ("DOSER", "corrupts a node", solace_doser)]),
        ("HALCYON", H_VIO, [("INSPECTOR", "fast", halcyon_inspector), ("BAILIFF", "heavy", halcyon_bailiff), ("LOCKDOWN", "freezes a link", halcyon_lockdown)]),
        ("ORBITAL", O_BLUE, [("SKIMMER", "fast", orbital_skimmer), ("DEBRIS FIELD", "slow, crushes", orbital_debris), ("LANDER", "drops in", orbital_lander)]),
        ("REBEL_CELL", R_RED, [("INFORMANT", "mirror: fast", cell_informant), ("LOYALIST", "mirror: heavy", cell_loyalist), ("PURGER", "mirror: burns", cell_purger)])]

# camera: same angle as the raid map, closer (3.6x)
LY.CAM["target"] = (0.0, 0.0, 0.0)
SPRITES = "sprites" in sys.argv     # round 20: Halcyon threat sprites at 4 headings for the gifs (map angle, 4x map zoom)
LY.CAM["ortho"] = 110.0 if SPRITES else 200.0
r_, u_, f_ = LY.cam_basis()
rh = Vector((r_[0], r_[1], 0)).normalized()
fh = Vector((f_[0], f_[1], 0)).normalized()
cam_d = bpy.data.cameras.new("cam")
cam_d.type = "ORTHO"
cam_d.ortho_scale = LY.CAM["ortho"]
cam_d.clip_end = LY.CAM.get("dist", 1500) * 2 + 3000   # round 40: the compat camera stands 5200 away
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = LY.cam_location()
cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()

# ground plate + lanes
ground = Acc("ground")
BID[0] = (0.0, 0.0, 0.0)
ground.face([(-300, -300, 0), (300, -300, 0), (300, 300, 0), (-300, 300, 0)], (0.15, 0.15, 0.19), (0, 0, 0))
layout = []
if SPRITES:
    ROWS = [("HALCYON", H_VIO, [("INSPECTOR", "fast", halcyon_inspector), ("BAILIFF", "heavy", halcyon_bailiff)])]
    HEADS = [0.0, math.pi / 2, math.pi, -math.pi / 2]
    for ui, (name, role, fn) in enumerate(ROWS[0][2]):
        for hi, hd in enumerate(HEADS):
            pos = rh * ((hi - 1.5) * 26.0) - fh * ((ui - 0.5) * 26.0)
            BID[0] = (rng.random(), rng.random(), rng.random())
            fn(pos.x, pos.y, hd, False)
            layout.append(dict(corp="HALCYON", unit=name, head=hi, x=pos.x, y=pos.y))
    ROWS = []
heading = math.pi                              # vehicles drive along the street (world -x), as on the map
COLS = 6
for ri, (corp, ccol, units) in enumerate(ROWS):
    for ci in range(COLS):
        ui, up = ci // 2, ci % 2 == 1
        pos = rh * ((ci - 2.5) * 28.0 + 10.4) - fh * ((ri - 2.0) * 18.0) + fh * 12.2
        x, y = pos.x, pos.y
        # a street lane under each vehicle (aligned with world x, like the map's streets)
        lx = Vector((math.cos(heading), math.sin(heading), 0))
        for sgn in (-1, 1):
            p0 = pos - lx * 8 + Vector((-lx.y, lx.x, 0)) * sgn * 5.0
            p1 = pos + lx * 8 + Vector((-lx.y, lx.x, 0)) * sgn * 5.0
            BID[0] = (0.0, 0.0, 0.0)
            beam((p0.x, p0.y, 0.03), (p1.x, p1.y, 0.03), 0.3, AMBER, acc=NEON)
        BID[0] = (rng.random(), rng.random(), rng.random())
        name, role, fn = units[ui]
        fn(x, y, heading, up)
        layout.append(dict(corp=corp, unit=name, role=role, up=up, x=x, y=y, row=ri, col=ci))

solid = SOLID.obj(None)
TO = None


def attr(nt, name):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_type = "GEOMETRY"
    n.attribute_name = name
    return n


def mat_toon():
    m = bpy.data.materials.new("toon")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position, el[1].position = 0.0, 0.12
    el.new(0.32)
    for e, c in zip(el, [(0.06, 0.055, 0.14), (0.16, 0.14, 0.28), (0.36, 0.32, 0.52)]):
        e.color = c + (1,)
    col = attr(nt, "col")
    fj = attr(nt, "fj")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.9
    mr.inputs["To Max"].default_value = 1.1
    m1 = nt.nodes.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    m1.blend_type = "MULTIPLY"
    m1.inputs["Factor"].default_value = 1.0
    m2 = nt.nodes.new("ShaderNodeVectorMath")
    m2.operation = "SCALE"
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    L(dif.outputs[0], s2r.inputs[0])
    L(s2r.outputs["Color"], bw.inputs[0])
    L(bw.outputs[0], ramp.inputs[0])
    L(col.outputs["Color"], m1.inputs[6])
    L(ramp.outputs["Color"], m1.inputs[7])
    L(fj.outputs["Fac"], mr.inputs["Value"])
    L(m1.outputs[2], m2.inputs[0])
    L(mr.outputs[0], m2.inputs["Scale"])
    L(m2.outputs[0], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m


def mat_emit(name, black=False):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if black:
        em.inputs["Color"].default_value = (0, 0, 0, 1)
    else:
        nt.links.new(attr(nt, "col").outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


TOONM, NEONM, BLACK = mat_toon(), mat_emit("neon"), mat_emit("black", True)
solid.data.materials[0] = TOONM
neon = NEON.obj(NEONM)
gr = ground.obj(TOONM)
if SPRITES:
    gr.hide_render = True
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
sun_d = bpy.data.lights.new("key", "SUN")
sun_d.energy = 3.2
sun = bpy.data.objects.new("key", sun_d)
sun.rotation_euler = (math.radians(46), math.radians(-24), math.radians(-30))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("w")
scene.world = world
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.02, 0.02, 0.04, 1)


def render(name):
    scene.render.filepath = os.path.join(OUT, name)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)


render("veh_beauty.png")
solid.data.materials[0] = BLACK
gr.data.materials[0] = BLACK
render("veh_glow.png")
solid.data.materials[0] = TOONM
gr.data.materials[0] = TOONM
scene.eevee.taa_render_samples = 1
scene.render.filter_size = 0.01
for kind in ("normal", "id"):
    m = bpy.data.materials.new("ov_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if kind == "normal":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5)
        vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(geo.outputs["Normal"], vm.inputs[0])
        nt.links.new(vm.outputs[0], em.inputs["Color"])
    else:
        nt.links.new(attr(nt, "bid").outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    bpy.context.view_layer.material_override = m
    render("veh_%s.png" % kind)
bpy.context.view_layer.material_override = None
for d in layout:
    p = LY.project(d["x"], d["y"], 0.0)
    d["px"], d["py"] = p[0], p[1]
json.dump(dict(items=layout, ortho=LY.CAM["ortho"]), open(os.path.join(OUT, "veh_layout.json"), "w"), indent=1)
print("DONE", flush=True)
