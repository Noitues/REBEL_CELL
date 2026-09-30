"""HQ double-helix tower, modelled in Blender, cel-shaded (flat triangulated facets, 3 hard toon
bands, Freestyle ink, painted grime) to composite into r2_city_wide_helix/city_day.png.

usage:
  blender -b --factory-startup --python helix_scene.py -- sprite  <out_rgba.png> <out_meta.json> [samples]
  blender -b --factory-startup --python helix_scene.py -- preview <out.png> [samples]

Projection (from r2_city_wide_helix/scripts/city.py Cam + default_cam):
  sx = ox + (x*ca - y*sa)*S ;  sy = oy + ((x*sa + y*ca)*se - z*ce)*S      az=24, el=38
That mapping is a mirror image of a physical camera, so city (x, y, z) is placed in Blender at
(x, -y, z); an orthographic camera then reproduces it exactly (ortho_scale = 1920 / S).
"""
import json
import math
import os
import random
import sys
import bmesh
import bpy
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_blend as Bl

args = T.arg_list()
KIND = args[0] if args else "sprite"
OUT = args[1]
META = args[2] if (KIND == "sprite" and len(args) > 2) else None
SAMPLES = int(args[3] if KIND == "sprite" and len(args) > 3 else (args[2] if KIND == "preview" and len(args) > 2 else 32))

# ------------------------------------------------------------------ city projection (city.py)
LOT_X, LOT_Y, ST = 5.0, 4.2, 1.8
NBX, NBY = 7, 4
LX = NBX * LOT_X + (NBX + 1) * ST
LY = NBY * LOT_Y + (NBY + 1) * ST
SLAB = 2.6
AZ, EL = 24.0, 38.0
ca, sa = math.cos(math.radians(AZ)), math.sin(math.radians(AZ))
ce, se = math.cos(math.radians(EL)), math.sin(math.radians(EL))
S = 1880.0 / (LX * ca + LY * sa) * 0.74
OX = 960 - (-LY * sa + LX * ca) / 2 * S + 40
OY = 1040 - (LX * sa + LY * ca) * se * S - SLAB * 0.55 * S


def city_px(x, y, z):
    return OX + (x * ca - y * sa) * S, OY + ((x * sa + y * ca) * se - z * ce) * S


# ------------------------------------------------------------------ helix design (city units)
CX, CY = 43.4, 1.9          # axis, as in helix.py
RI, RO = 2.7, 5.5           # hollow core / outer radius
FL = 0.78                   # floor height
NFL = 4                     # floors per strand slab
TH = FL * NFL               # slab thickness (3.9)
PITCH = 17.0                # height per full turn
TURNS = 3.0
Z0 = 1.2                    # podium height
PLAZA_R = 6.4
SEG_PER_TURN = 32
ENTRY = math.atan2(6.9 - CY, 48.5 - CX)     # toward the route's end node


def zb(t):
    return Z0 + PITCH * t / (2 * math.pi)


def W(x, y, z):
    """city -> Blender (mirror y)."""
    return Vector((x, -y, z))


def cyl_pt(r, a, z):
    return W(CX + r * math.cos(a), CY + r * math.sin(a), z)


# ------------------------------------------------------------------ scene
sc = T.reset()
T.MODE["name"] = "day"
T.MODE["grit"] = 0.7
T.MODE["steps"] = True
PREVIEW = KIND == "preview"
T.setup_render(sc, w=(1400 if PREVIEW else 1920), h=(1800 if PREVIEW else 2000), samples=SAMPLES,
               transparent=not PREVIEW, bg="#b3ab96", line=(3.4 if PREVIEW else 2.8), crease=120.0)
T.compositor(sc, bloom=(0.95, 0.5, 6))
wbg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
wbg.inputs[1].default_value = 0.5
# city light: LIGHT = (-0.45, 0.55, 0.78) (toward the light, city coords)
L = W(-0.45, 0.55, 0.78).normalized()
sun = T.sun(2.8, "#ffd49a", angle=6)
sun.rotation_euler = L.to_track_quat("Z", "Y").to_euler()
rng = random.Random(4242)


def M(h, **kw):
    return T.paint(h, **kw)


def mesh_obj(bm, name, mats):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    T.link_obj(o)
    for m in mats:
        me.materials.append(m)
    return o


def band(r0, r1, z_off, thick, t0, t1, phase, name, mats, seg=None, mat_fn=None):
    """Helical band (closed): radii r0..r1, bottom at zb(t)+z_off, height `thick`."""
    bm = bmesh.new()
    n = max(2, int(abs(t1 - t0) / (2 * math.pi) * (seg or SEG_PER_TURN)))
    rings = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = t + phase
        z = zb(t) + z_off
        rings.append([bm.verts.new(cyl_pt(r0, a, z)), bm.verts.new(cyl_pt(r1, a, z)),
                      bm.verts.new(cyl_pt(r1, a, z + thick)), bm.verts.new(cyl_pt(r0, a, z + thick))])
    for i in range(n):
        A, Bv = rings[i], rings[i + 1]
        for k in range(4):
            f = bm.faces.new((A[k], A[(k + 1) % 4], Bv[(k + 1) % 4], Bv[k]))
            if mat_fn:
                f.material_index = mat_fn(i, k)
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    return mesh_obj(bm, name, mats)


def oriented_boxes(parts, name, mats, bev=0.0):
    """parts: (center Vector, x_axis Vector, size (sx, sy, sz), mat_idx) - boxes with z up."""
    bm = bmesh.new()
    for c, xa, s, mi in parts:
        xa = xa.normalized()
        za = Vector((0, 0, 1))
        ya = za.cross(xa).normalized()
        mt = Matrix((xa * s[0], ya * s[1], za * s[2])).transposed()
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = c + mt @ v.co
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    o = mesh_obj(bm, name, mats)
    if bev:
        T.bevel(o, bev, 1)
    return o


# palettes (city FAM mids) and neon
CORP, BRICK, CONC = "#557a8e", "#6e3a2c", "#6a665c"   # A: slate/steel, B: brick/rust
CYAN, MAGENTA, SODIUM = "#3fd8f0", "#ec4aa0", "#ffa436"
GLASS = M("#1e2c30", gloss=0.5, stroke=0.1)
WIN_LIT = T.glow("#ffb45a", 1.6)
WIN_CY = T.glow("#78eaff", 1.4)

T_END = TURNS * 2 * math.pi
for s, (fam, neon, name) in enumerate(((CORP, CYAN, "strandA"), (BRICK, MAGENTA, "strandB"))):
    phase = s * math.pi
    body_m = M(fam, streak_axis=2, streak=8, stroke=0.25, seed=s)
    top_m = M("#4a5866" if s == 0 else "#4a2a22", stroke=0.2)
    band(RI, RO, 0.0, TH, 0.0, T_END, phase, name, [body_m, top_m],
         mat_fn=lambda i, k: 1 if k == 2 else 0)
    # floor lips / continuous balconies on the outer face (concrete), thinner lips on the inner face
    for f in range(1, NFL):
        band(RO - 0.05, RO + 0.34, f * FL - 0.06, 0.12, 0.0, T_END, phase, name + "_lip%d" % f,
             [M("#8a8578", stroke=0.2)])
        band(RI - 0.18, RI + 0.05, f * FL - 0.05, 0.08, 0.0, T_END, phase, name + "_ilip%d" % f,
             [M("#6a665c", stroke=0.2)])
    # railing band on the rooftop edge and the neon strip along the outer edge
    band(RO - 0.12, RO + 0.06, TH, 0.28, 0.0, T_END, phase, name + "_rail", [M("#4a4a4e", gloss=0.3)])
    band(RO + 0.02, RO + 0.2, TH - 0.42, 0.2, 0.0, T_END, phase, name + "_neon", [T.glow(neon, 3.2)])
    # window grids: outer + inner faces, per floor, facet boxes following the curve
    parts = []
    n_out = int(T_END * RO / 0.72)
    for f in range(NFL):
        for i in range(n_out):
            t = (i + 0.5) / n_out * T_END
            a = t + phase
            z = zb(t) + f * FL + FL * 0.52
            tangent = (cyl_pt(1, a + 0.01, 0) - cyl_pt(1, a - 0.01, 0)).normalized()
            r_ = rng.random()
            mi = 1 if r_ < 0.14 else (2 if r_ < 0.2 else 0)
            parts.append((cyl_pt(RO + 0.02, a, z), tangent, (0.4, 0.1, FL * 0.5), mi))
        n_in = int(T_END * RI / 0.8)
        for i in range(n_in):
            t = (i + 0.5) / n_in * T_END
            a = t + phase
            z = zb(t) + f * FL + FL * 0.52
            tangent = (cyl_pt(1, a + 0.01, 0) - cyl_pt(1, a - 0.01, 0)).normalized()
            r_ = rng.random()
            mi = 1 if r_ < 0.18 else (2 if r_ < 0.24 else 0)
            parts.append((cyl_pt(RI - 0.02, a, z), tangent, (0.36, 0.1, FL * 0.5), mi))
    oriented_boxes(parts, name + "_win", [GLASS, WIN_LIT, WIN_CY])
    # balconies: jutting slabs with railings every so often on the outer face
    bal = []
    for k in range(int(TURNS * 7)):
        t = (k + 0.3 + rng.uniform(-0.2, 0.2)) / (TURNS * 7) * T_END
        a = t + phase
        f = rng.randint(1, NFL - 1)
        z = zb(t) + f * FL
        tangent = (cyl_pt(1, a + 0.01, 0) - cyl_pt(1, a - 0.01, 0)).normalized()
        c = cyl_pt(RO + 0.55, a, z + 0.05)
        bal.append((c, tangent, (1.3, 0.7, 0.1), 0))
        bal.append((cyl_pt(RO + 0.88, a, z + 0.3), tangent, (1.3, 0.05, 0.42), 1))
    oriented_boxes(bal, name + "_bal", [M("#8a8578"), M("#3a3a3e", gloss=0.3)])
    # rooftop at the strand's top: penthouse, AC units, antenna
    t_top = T_END - 0.28
    a = t_top + phase
    ztop = zb(t_top) + TH
    tangent = (cyl_pt(1, a + 0.01, 0) - cyl_pt(1, a - 0.01, 0)).normalized()
    roof = [(cyl_pt((RI + RO) / 2, a, ztop), tangent, (1.6, 1.6, 1.1), 0),
            (cyl_pt((RI + RO) / 2 + 0.6, a - 0.35, ztop), tangent, (0.6, 0.5, 0.45), 1),
            (cyl_pt((RI + RO) / 2 - 0.6, a - 0.5, ztop), tangent, (0.6, 0.5, 0.45), 1)]
    oriented_boxes(roof, name + "_roof", [M(fam, stroke=0.2), M("#9a9a92", gloss=0.2)], bev=0.05)
    base_ant = cyl_pt((RI + RO) / 2, a + 0.05, ztop + 1.1)
    T.cyl(0.07, 4.2, tuple(base_ant), M("#3a3a3e"), verts=6, bev=0)
    T.cyl(0.18, 0.25, tuple(base_ant + Vector((0, 0, 4.2))), T.glow("#ff3a3a", 5), verts=8, bev=0)

# ------------------------------------------------------------------ skybridges across the core

t0 = math.radians(180 - AZ)      # bridge axis perpendicular to the view: bridges show side-on in the core
bparts, bglow = [], []
for k in range(6):
    t = t0 + k * math.pi         # evenly spaced heights, PITCH/2 apart
    if t > T_END - 0.3:
        t = T_END - 0.4
    a = t
    z = zb(t) + 0.35
    axis = (cyl_pt(1, a, 0) - cyl_pt(0, a, 0)).normalized()
    c = W(CX, CY, 0) + Vector((0, 0, z))
    Lb = 2 * RI + 1.2
    bparts.append((c, axis, (Lb, 2.2, 1.5), 0))                       # walkway body (1.5 = ~1.9 floors)
    bparts.append((c + Vector((0, 0, 1.5)), axis, (Lb + 0.1, 2.4, 0.16), 1))   # roof slab
    for side in (-1, 1):
        perp = Vector((0, 0, 1)).cross(axis).normalized()
        for w in range(6):
            off = -Lb / 2 + 0.8 + w * (Lb - 1.6) / 5
            bglow.append((c + axis * off + perp * (1.11 * side) + Vector((0, 0, 0.4)), axis, (0.6, 0.06, 0.75),
                          0 if (w + k) % 3 else 1))
oriented_boxes(bparts, "bridges", [M(CONC, stroke=0.25, streak_axis=0), M("#3a3a3e")])
oriented_boxes(bglow, "bridge_win", [T.glow("#9ff0ff", 1.3), T.glow("#ffc27a", 1.5)])

# ------------------------------------------------------------------ podium / plaza + entrance
bm = bmesh.new()
N = 24
lo = [bm.verts.new(cyl_pt(PLAZA_R, 2 * math.pi * i / N, 0.0)) for i in range(N)]
hi = [bm.verts.new(cyl_pt(PLAZA_R, 2 * math.pi * i / N, Z0)) for i in range(N)]
for i in range(N):
    j = (i + 1) % N
    bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
bm.faces.new(hi)
bm.faces.new(lo[::-1])
mesh_obj(bm, "podium", [M(CONC, stroke=0.3, pattern="tiles")])
# low core plinth + lift shaft stub inside the hollow core
T.cyl(RI - 0.3, 0.5, tuple(W(CX, CY, Z0)), M("#4a4840"), verts=16, bev=0)
# entrance: portal block on the podium edge facing the route end, cyan-lit door + light spill on the plaza
ea = ENTRY
tan = (cyl_pt(1, ea + 0.01, 0) - cyl_pt(1, ea - 0.01, 0)).normalized()
rad = (cyl_pt(1, ea, 0) - cyl_pt(0, ea, 0)).normalized()
oriented_boxes([(cyl_pt(RO + 0.3, ea, Z0), tan, (3.0, 1.6, 2.2), 0),
                (cyl_pt(RO + 0.3, ea, Z0 + 2.2), tan, (3.4, 1.9, 0.25), 1)], "portal",
               [M(CORP, stroke=0.2), M("#2a2c30")])
oriented_boxes([(cyl_pt(RO + 1.12, ea, Z0), tan, (1.6, 0.06, 1.7), 0)], "door", [T.glow(CYAN, 2.6)])
T.point(tuple(cyl_pt(RO + 2.2, ea, Z0 + 1.0)), CYAN, 250, 1.0)
spill = bmesh.new()
pts = [spill.verts.new(cyl_pt(RO + 1.2 + (PLAZA_R - RO - 1.2) * v, ea - 0.2 + 0.4 * u, Z0 + 0.02))
       for u, v in ((0, 0), (1, 0), (1, 1), (0, 1))]
spill.faces.new(pts)
o = mesh_obj(spill, "spill", [T.glow(CYAN, 0.9, alpha=0.6)])
for c_ in list(o.users_collection):
    c_.objects.unlink(o)
T.noline_coll().objects.link(o)
# steps from the plaza down to street level at the entrance
steps = []
for k in range(3):
    steps.append((cyl_pt(PLAZA_R + 0.3 + k * 0.35, ea, 0.0), tan, (2.2, 0.36, Z0 - k * 0.4), 0))
oriented_boxes(steps, "steps", [M(CONC, stroke=0.25)])

# ------------------------------------------------------------------ C facets on everything painted
Bl.facet_all(size=0.9, jitter=0.035, seed=11)

# ------------------------------------------------------------------ camera
h_ = Vector((sa, -ca, 0.0))                  # toward the camera (Blender, mirrored)
r_ = Vector((ca, sa, 0.0))                   # screen right
u_ = -h_ * se + Vector((0, 0, 1)) * ce       # screen up
w_ = h_ * ce + Vector((0, 0, 1)) * se        # toward the camera along the view axis
meta = {}
if not PREVIEW:
    EXTRA = 920                              # canvas extends 920 px above the city frame
    RES_W, RES_H = 1920, 1080 + EXTRA
    cx_city, cy_city = 960.0, 540.0 - EXTRA / 2.0   # city-pixel coordinate at the canvas centre
    a_ = (cx_city - OX) / S
    b_ = (OY - cy_city) / S
    C = r_ * a_ + u_ * b_ + w_ * 300.0
    cam_d = bpy.data.cameras.new("ortho")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = RES_W / S
    cam_d.sensor_fit = "HORIZONTAL"
    cam_d.clip_start = 1.0
    cam_d.clip_end = 1000.0
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    cam.matrix_world = Matrix((r_, u_, w_)).transposed().to_4x4()
    cam.location = C
    sc.camera = cam
    bx, by = city_px(CX, CY, 0.0)
    meta = dict(px_per_unit=S, canvas_offset_in_city_px=[0, -EXTRA], canvas_size=[RES_W, RES_H],
                base_center_city_px=[bx, by], base_center_canvas_px=[bx, by + EXTRA],
                axis_city_units=[CX, CY], projection=dict(az=AZ, el=EL, S=S, ox=OX, oy=OY),
                top_z_units=zb(T_END) + TH + 4.45)
else:
    tgt = W(CX, CY, 27.0)
    cam = T.camera(tuple(tgt + Vector((44.0, -52.0, 14.0))), tuple(tgt), lens=40)
T.render(sc, OUT)
if META:
    with open(META, "w") as f:
        json.dump(meta, f, indent=2)
    print("META", meta)
