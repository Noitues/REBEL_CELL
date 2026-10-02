"""Round 18: the raid district around the Cell's HQ, authored in Blender 5.2 (headless).

Run:  blender -b --factory-startup --python district.py -- <variant> <heat> <outdir> [preview] [day]
  variant: setup = defences standing on their node pads, no threats
           wave  = setup + threat units on the routes, defences firing (tracers)
  heat:    1..3 = escalation props (helicopters + searchlight cones, drones, police strobes, corp billboards)
Writes into <outdir>/<variant>_h<heat>_*: beauty_night (+ beauty_day with 'day'), glow_night (+ glow_day),
  normal.png, id.png (ink passes), pos.npy (world position per pixel, float16, for the street-plane
  decals in post) and scene.json (searchlight pools, unit spots).
The grid NODES and LINKS are NOT modelled here: they are decals evaluated in post on the ground plane
(finish.py), exactly like a ground decal shader would do in Godot. Only things that stand ON a pad
(defences, node hardware) and things above the street (traffic, highways, helicopters) are geometry.
Style: round 6 / round 11 restyle: jittered triangle facets, 3 toon bands, ink lines in post.
All randomness is seeded.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["setup", "1", "."]
VARIANT, HEAT, OUTDIR = argv[0], int(argv[1]), os.path.abspath(argv[2])
PREVIEW = "preview" in argv[3:]
DAY = "day" in argv[3:]
RES = (960, 540) if PREVIEW else (LY.RW, LY.RH)
os.makedirs(OUTDIR, exist_ok=True)
TAG = "%s_h%d" % (VARIANT, HEAT)
rng = random.Random(1801)          # city: same for every variant
vrng = random.Random(1800 + HEAT * 7 + (50 if VARIANT == "wave" else 0))  # variant props

# ------------------------------------------------------------------ scene reset
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 8 if PREVIEW else 24
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.film_transparent = False
try:
    scene.eevee.shadow_ray_count = 1
    scene.eevee.shadow_step_count = 4
    scene.eevee.shadow_resolution_scale = 0.5
except Exception:
    pass

# ------------------------------------------------------------------ colours
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.36, 0.88, 1.0), (1.0, 0.24, 0.66), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
GREEN, VIOLET = (0.48, 0.88, 0.48), (0.78, 0.35, 1.0)
HALCYON = (0.55, 0.48, 1.0)       # corp_halcyon #8C7BFF
BLUE = (0.16, 0.42, 1.0)
GUNMETAL = (0.20, 0.21, 0.25)
FONT = "C:/Windows/Fonts/bahnschrift.ttf"


# ------------------------------------------------------------------ geometry accumulator (round 11)
class Acc:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.col = self.bm.faces.layers.float_color.new("col")
        self.fj = self.bm.faces.layers.float.new("fj")
        self.bid = self.bm.faces.layers.float_color.new("bid")

    def face(self, pts, col, bid, fj=None, r=None):
        r = r or rng
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f[self.col] = (col[0], col[1], col[2], 1.0)
        f[self.fj] = r.random() if fj is None else fj
        f[self.bid] = (bid[0], bid[1], bid[2], 1.0)
        return f

    def facet_quad(self, a, b, c, d, col, bid, jit=0.035, r=None):
        r = r or rng
        A, B, C, D = map(Vector, (a, b, c, d))
        n = (B - A).cross(D - A)
        size = max((B - A).length, (D - A).length)
        if n.length < 1e-6 or size < 2.5:
            self.face([a, b, c, d], col, bid, r=r)
            return
        n.normalize()
        u, v = r.uniform(0.3, 0.7), r.uniform(0.3, 0.7)
        P = A.lerp(B, u).lerp(D.lerp(C, u), v) + n * r.uniform(-jit, jit) * size
        for p, q in ((A, B), (B, C), (C, D), (D, A)):
            self.face([tuple(p), tuple(q), tuple(P)], col, bid, r=r)

    def obj(self, mat, name=None):
        me = bpy.data.meshes.new(name or self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name or self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        for p in me.polygons:
            p.use_smooth = False
        return ob


SOLID, NEON, WIN = Acc("solid"), Acc("neon"), Acc("win")
BEAMS = Acc("beams")        # searchlight cones (additive, hidden in data passes)


def rid(r=None):
    r = r or rng
    return (r.random(), r.random(), r.random())


def box(x0, y0, z0, x1, y1, z1, col, taper=0.0, facet=True, bid=None, top=True, acc=None, r=None):
    acc = acc or SOLID
    r = r or rng
    bid = bid or rid(r)
    t = taper
    b = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    u = [(x0 + t, y0 + t, z1), (x1 - t, y0 + t, z1), (x1 - t, y1 - t, z1), (x0 + t, y1 - t, z1)]
    for q in [(b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])]:
        if facet and acc is SOLID:
            acc.facet_quad(*q, col, bid, r=r)
        else:
            acc.face(list(q), col, bid, r=r)
    if top:
        if facet and acc is SOLID:
            acc.facet_quad(u[0], u[1], u[2], u[3], col, bid, jit=0.01, r=r)
        else:
            acc.face(u, col, bid, r=r)
    return bid


def obox(cx, cy, z0, L, Wd, Hh, ang, col, acc=None, bid=None, r=None, taper=0.0, facet=False):
    """Oriented box centred at cx, cy (heading ang radians along L)."""
    acc = acc or SOLID
    r = r or rng
    bid = bid or rid(r)
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v, z):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca, z)
    hl, hw = L / 2, Wd / 2
    tl, tw = hl - taper, hw - taper
    b = [P(-hl, -hw, z0), P(hl, -hw, z0), P(hl, hw, z0), P(-hl, hw, z0)]
    u = [P(-tl, -tw, z0 + Hh), P(tl, -tw, z0 + Hh), P(tl, tw, z0 + Hh), P(-tl, tw, z0 + Hh)]
    for q in [(b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])]:
        if facet and acc is SOLID:
            acc.facet_quad(*q, col, bid, r=r)
        else:
            acc.face(list(q), col, bid, r=r)
    acc.face(u, col, bid, r=r)
    acc.face(list(reversed(b)), col, bid, r=r)
    return bid


def prism(cx, cy, z0, z1, rad, n, col, acc=None, bid=None, rot=0.0, r1=None, r=None, facet=True):
    acc = acc or SOLID
    r = r or rng
    bid = bid or rid(r)
    r1 = rad if r1 is None else r1
    lo = [(cx + rad * math.cos(rot + 2 * math.pi * i / n), cy + rad * math.sin(rot + 2 * math.pi * i / n), z0) for i in range(n)]
    hi = [(cx + r1 * math.cos(rot + 2 * math.pi * i / n), cy + r1 * math.sin(rot + 2 * math.pi * i / n), z1) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        if facet and acc is SOLID:
            acc.facet_quad(lo[i], lo[j], hi[j], hi[i], col, bid, r=r)
        else:
            acc.face([lo[i], lo[j], hi[j], hi[i]], col, bid, r=r)
    acc.face(hi, col, bid, r=r)
    return bid


def beam(p0, p1, w, col, acc=None, bid=None, r=None):
    acc = acc or SOLID
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized() * (w / 2)
    b = d.cross(a).normalized() * (w / 2)
    c0 = [p0 + a + b, p0 - a + b, p0 - a - b, p0 + a - b]
    c1 = [p1 + a + b, p1 - a + b, p1 - a - b, p1 + a - b]
    bid = bid or rid(r)
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(c0[i]), tuple(c0[j]), tuple(c1[j]), tuple(c1[i])], col, bid, r=r)
    acc.face([tuple(v) for v in c1], col, bid, r=r)
    acc.face([tuple(v) for v in reversed(c0)], col, bid, r=r)


def strip(acc, p0, p1, w, z, col, r=None):
    p0, p1 = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    d = (p1 - p0).normalized()
    n = Vector((-d.y, d.x, 0)) * (w / 2)
    acc.face([tuple(p0 + n), tuple(p0 - n), tuple(p1 - n), tuple(p1 + n)], col, (0, 0, 0), r=r)


def ring(acc, cx, cy, z, rad, w, col, n=24, r=None):
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p = [(cx + (rad - w / 2) * math.cos(a0), cy + (rad - w / 2) * math.sin(a0), z),
             (cx + (rad + w / 2) * math.cos(a0), cy + (rad + w / 2) * math.sin(a0), z),
             (cx + (rad + w / 2) * math.cos(a1), cy + (rad + w / 2) * math.sin(a1), z),
             (cx + (rad - w / 2) * math.cos(a1), cy + (rad - w / 2) * math.sin(a1), z)]
        acc.face(p, col, (0, 0, 0), r=r)


WIN_COLS = [(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]


def windows(x0, y0, z0, x1, y1, z1, p=0.35, sx=2.6, sz=3.4, ww=1.2, wh=1.0, cols=None, faces=(0, 3)):
    """Window quads (only the faces the camera sees: 0 = -y, 3 = -x; plus 1/2 for the skyline)."""
    cols = cols or WIN_COLS
    o = 0.07
    walls = [((x0, y0 - o), (x1, y0 - o)), ((x1 + o, y0), (x1 + o, y1)), ((x1, y1 + o), (x0, y1 + o)), ((x0 - o, y1), (x0 - o, y0))]
    for fi in faces:
        (ax, ay), (bx, by) = walls[fi]
        L = math.hypot(bx - ax, by - ay)
        nx = int((L - 1.0) / sx)
        nz = int((z1 - z0 - 1.5) / sz)
        if nx < 1 or nz < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        off = (L - nx * sx) / 2
        for i in range(nx):
            for k in range(nz):
                if rng.random() > p:
                    continue
                c = rng.choice(cols)
                s = 0.55 + 0.45 * rng.random()
                c = (c[0] * s, c[1] * s, c[2] * s)
                t0 = off + i * sx + (sx - ww) / 2
                z = z0 + 1.2 + k * sz
                pa = (ax + ux * t0, ay + uy * t0)
                pb = (ax + ux * (t0 + ww), ay + uy * (t0 + ww))
                WIN.face([(pa[0], pa[1], z), (pb[0], pb[1], z), (pb[0], pb[1], z + wh), (pa[0], pa[1], z + wh)], c, (0, 0, 0))


def roof_trim(x0, y0, x1, y1, z, col, w=0.4):
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        beam((a[0], a[1], z), (b[0], b[1], z), w, col, acc=NEON)


def text_obj(s, loc, rot, size, mat, extrude=0.15):
    cu = bpy.data.curves.new("t_" + s, "FONT")
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT)
    except Exception:
        pass
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("t_" + s, cu)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


# ------------------------------------------------------------------ materials (round 11)
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
    el[0].position = 0.0
    el[1].position = 0.12
    el.new(0.32)
    col = attr(nt, "col")
    fj = attr(nt, "fj")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.86
    mr.inputs["To Max"].default_value = 1.12
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
    return m, ramp


def mat_glow(name):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = attr(nt, "col")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    L(col.outputs["Color"], sc.inputs[0])
    L(sc.outputs[0], mix.inputs[6])
    L(mix.outputs[2], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m, sc, mix


def mat_flat(name, rgb):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(rgb) + (1,)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m, em


def mat_additive(name, image=None, strength=1.0):
    """Additive light: Transparent + Emission (colour attribute, optionally x an image's luminance)."""
    m = bpy.data.materials.new(name)
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        m.blend_method = "BLEND"
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    add = nt.nodes.new("ShaderNodeAddShader")
    col = attr(nt, "col")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = strength
    L = nt.links.new
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = "Closest"
        uv = nt.nodes.new("ShaderNodeUVMap")
        L(uv.outputs[0], tex.inputs[0])
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        L(col.outputs["Color"], mul.inputs[6])
        L(tex.outputs["Color"], mul.inputs[7])
        L(mul.outputs[2], sc.inputs[0])
    else:
        L(col.outputs["Color"], sc.inputs[0])
    L(sc.outputs[0], em.inputs["Color"])
    L(tr.outputs[0], add.inputs[0])
    L(em.outputs[0], add.inputs[1])
    L(add.outputs[0], out.inputs[0])
    return m, sc


TOON, RAMP = mat_toon()
NEONM, NEON_SC, NEON_MIX = mat_glow("neon")
WINM, WIN_SC, WIN_MIX = mat_glow("win")
SIGNM, SIGN_EM = mat_flat("sign", PINK)
BEAMM, BEAM_SC = mat_additive("beam", strength=0.1)


# ------------------------------------------------------------------ camera (orthographic, from layout)
cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = LY.CAM["ortho"]
cam_data.clip_start = 1.0
cam_data.clip_end = 3000
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = LY.cam_location()
r_, u_, f_ = LY.cam_basis()
cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()


# ------------------------------------------------------------------ occlusion guard
# Screen points that must stay visible: node pads + unit height, entries, and the link / route streets.
def _sample_seg(a, b, step):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]


PROTECT_HARD, PROTECT_SOFT = [], []
for k, n in LY.NODES.items():
    rr = 13.0 if k != "core" else 15.0
    for i in range(12):
        a = 2 * math.pi * i / 12
        for z in (0.0, 10.0):
            PROTECT_HARD.append((n[0] + rr * math.cos(a), n[1] + rr * math.sin(a), z))
for e in LY.ENTRIES.values():
    for i in range(8):
        a = 2 * math.pi * i / 8
        PROTECT_HARD.append((e[0] + 10 * math.cos(a), e[1] + 10 * math.sin(a), 0.0))
for a_, b_ in LY.LINKS:
    for p in _sample_seg(LY.pt(a_), LY.pt(b_), 5.0):
        PROTECT_SOFT.append((p[0], p[1], 0.0))
for rid_ in LY.ROUTES:
    ps = LY.route_points(rid_)
    for i in range(len(ps) - 1):
        for p in _sample_seg(ps[i], ps[i + 1], 5.0):
            PROTECT_SOFT.append((p[0], p[1], 0.0))
PH = [LY.project(*p) for p in PROTECT_HARD]
PS = [LY.project(*p) for p in PROTECT_SOFT]


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _inside(h, p):
    n = len(h)
    if n < 3:
        return False
    for i in range(n):
        a, b = h[i], h[(i + 1) % n]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0:
            return False
    return True


def occludes(x0, y0, x1, y1, h, pts):
    cs = [LY.project(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0.0, h)]
    hull = _hull([(round(c[0], 2), round(c[1], 2)) for c in cs])
    dmax = max(c[2] for c in cs)
    xs, ys = [c[0] for c in cs], [c[1] for c in cs]
    bb = (min(xs), min(ys), max(xs), max(ys))
    for p in pts:
        if p[2] < dmax - 1.0 and bb[0] <= p[0] <= bb[2] and bb[1] <= p[1] <= bb[3]:
            # the point is behind the building's front; test against the screen hull
            if _inside(hull, (p[0], p[1])):
                return True
    return False


def cap_height(x0, y0, x1, y1, h):
    while h > 5.0 and occludes(x0, y0, x1, y1, h, PH):
        h *= 0.8
    while h > 9.0 and occludes(x0, y0, x1, y1, h, PS):
        h *= 0.85
    return h


# ------------------------------------------------------------------ ground + streets
ASPH = (0.15, 0.15, 0.19)
LOT = (0.25, 0.24, 0.29)
EXT = 420
box(-EXT, -EXT, -1, EXT, EXT, 0, ASPH, facet=False)


def street_lines():
    """Ordinary street glow: dim, so the network decals own the brightest ground light."""
    for x in LY.STREETS_X:
        w = LY.street_w("x", x)
        strip(SOLID, (x, -EXT), (x, EXT), w - 1.0, 0.015, (0.12, 0.11, 0.15))
        strip(NEON, (x - w / 2 + 0.8, -EXT), (x - w / 2 + 0.8, EXT), 0.3, 0.03, AMBER)
        strip(NEON, (x + w / 2 - 0.8, -EXT), (x + w / 2 - 0.8, EXT), 0.3, 0.03, AMBER)
        y = -EXT
        while y < EXT:  # dashed centre line
            strip(NEON, (x, y), (x, y + 3.0), 0.25, 0.03, (0.55, 0.55, 0.6))
            y += 7.0
    for y in LY.STREETS_Y:
        w = LY.street_w("y", y)
        strip(SOLID, (-EXT, y), (EXT, y), w - 1.0, 0.016, (0.12, 0.11, 0.15))
        strip(NEON, (-EXT, y - w / 2 + 0.8), (EXT, y - w / 2 + 0.8), 0.3, 0.03, AMBER)
        strip(NEON, (-EXT, y + w / 2 - 0.8), (EXT, y + w / 2 - 0.8), 0.3, 0.03, AMBER)
        x = -EXT
        while x < EXT:
            strip(NEON, (x, y), (x + 3.0, y), 0.25, 0.03, (0.55, 0.55, 0.6))
            x += 7.0
    # zebra crossings at every intersection (white-ish, dim)
    for x in LY.STREETS_X:
        for y in LY.STREETS_Y:
            wx, wy = LY.street_w("x", x), LY.street_w("y", y)
            for k in range(-3, 4):
                for side in (-1, 1):
                    yy = y + side * (wy / 2 + 1.6)
                    strip(NEON, (x + k * 2.0, yy - 1.0), (x + k * 2.0, yy + 1.0), 0.9, 0.025, (0.3, 0.3, 0.34))
                    xx = x + side * (wx / 2 + 1.6)
                    strip(NEON, (xx - 1.0, y + k * 2.0), (xx + 1.0, y + k * 2.0), 0.9, 0.025, (0.3, 0.3, 0.34))


street_lines()


def car(x, y, ang, r, lit=True):
    L, Wd = r.uniform(4.2, 5.4), 2.1
    c = r.choice([(0.55, 0.55, 0.6), (0.2, 0.22, 0.3), (0.6, 0.18, 0.2), (0.85, 0.7, 0.3), (0.3, 0.5, 0.6)])
    obox(x, y, 0.3, L, Wd, 1.1, ang, c, r=r)
    obox(x - math.cos(ang) * 0.3, y - math.sin(ang) * 0.3, 1.4, L * 0.55, Wd * 0.85, 0.7, ang, tuple(v * 0.7 for v in c), r=r)
    if lit:
        ca, sa = math.cos(ang), math.sin(ang)
        hx, hy = x + ca * L / 2, y + sa * L / 2
        tx, ty = x - ca * L / 2, y - sa * L / 2
        strip(NEON, (hx, hy), (hx + ca * 6, hy + sa * 6), 1.6, 0.06, (0.35, 0.33, 0.28), r=r)  # headlight pool
        strip(NEON, (hx - sa * 0.7, hy + ca * 0.7), (hx - sa * 0.7 + ca * 0.25, hy + ca * 0.7 + sa * 0.25), 0.5, 0.9, WHITE, r=r)
        strip(NEON, (hx + sa * 0.7, hy - ca * 0.7), (hx + sa * 0.7 + ca * 0.25, hy - ca * 0.7 + sa * 0.25), 0.5, 0.9, WHITE, r=r)
        strip(NEON, (tx, ty), (tx - ca * 0.3, ty - sa * 0.3), 1.8, 0.9, RED, r=r)


def traffic():
    """Parked and moving cars on streets that carry no network link (busy city, calm network streets)."""
    net_streets = set()
    for a, b in LY.LINKS:
        pa, pb = LY.pt(a), LY.pt(b)
        net_streets.add(("x", pa[0]) if pa[0] == pb[0] else ("y", pa[1]))
    for x in LY.STREETS_X:
        dens = 0.25 if ("x", x) in net_streets else 1.0
        for y in range(-EXT, EXT, 11):
            if rng.random() < 0.28 * dens and not LY.is_intersection_reserved(x, y, 16):
                side = rng.choice([-1, 1])
                car(x + side * 3.6, y + rng.uniform(0, 6), math.pi / 2 if side > 0 else -math.pi / 2, rng)
    for y in LY.STREETS_Y:
        if y == 90:
            continue  # under the highway: keep it clear
        dens = 0.25 if ("y", y) in net_streets else 1.0
        for x in range(-EXT, EXT, 11):
            if rng.random() < 0.28 * dens and not LY.is_intersection_reserved(x, y, 16):
                side = rng.choice([-1, 1])
                car(x + rng.uniform(0, 6), y + side * 3.6, 0.0 if side < 0 else math.pi, rng)


traffic()

# ------------------------------------------------------------------ city blocks
FAMS = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36),
        (0.40, 0.38, 0.46), (0.46, 0.36, 0.44), (0.34, 0.38, 0.48)]
TRIMS = [AMBER, AMBER, CYAN, PINK, VIOLET, GREEN]
BUILDINGS = []   # (x0, y0, x1, y1, top) for billboards


def hw_corridor(x0, y0, x1, y1):
    for axis, v, decks in LY.HIGHWAYS:
        lo, hi = v - 16, v + 16
        if axis == "y" and y1 > lo and y0 < hi:
            return True
        if axis == "x" and x1 > lo and x0 < hi:
            return True
    return False


def building(x0, y0, x1, y1, h, c, corp=False):
    h = cap_height(x0, y0, x1, y1, h)
    taper = rng.choice([0, 0, 0, 0.5, 0.9]) if h > 16 else 0
    box(x0, y0, 0, x1, y1, h, c, taper=taper)
    faces = (0, 3) if h < 40 else (0, 1, 2, 3)
    windows(x0 + taper, y0 + taper, 0, x1 - taper, y1 - taper, h, p=0.34 if h > 18 else 0.22, faces=faces)
    top = h
    if h > 18 and rng.random() < 0.5:
        i = min(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.28)
        h2 = h + rng.uniform(4, 16)
        box(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, tuple(v * 1.05 for v in c))
        windows(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, p=0.3, faces=faces)
        top = h2
        x0, y0, x1, y1 = x0 + i, y0 + i, x1 - i, y1 - i
    if rng.random() < 0.55 or corp:
        roof_trim(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, top + 0.15, HALCYON if corp else rng.choice(TRIMS))
    if rng.random() < 0.45:
        cx, cy = rng.uniform(x0 + 1, x1 - 3), rng.uniform(y0 + 1, y1 - 3)
        box(cx, cy, top, cx + 2.2, cy + 2.2, top + 1.5, (0.3, 0.3, 0.34), facet=False)
    if top > 30 and rng.random() < 0.6:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        beam((mx, my, top), (mx, my, top + rng.uniform(6, 12)), 0.3, (0.25, 0.25, 0.3))
        z = top + 6
        NEON.face([(mx - 0.6, my, z), (mx + 0.6, my, z), (mx + 0.6, my, z + 1.2), (mx - 0.6, my, z + 1.2)], RED, (0, 0, 0))
    BUILDINGS.append((x0, y0, x1, y1, top))


def entry_corp(x, y):
    """True if a block corner near this point belongs to a Halcyon entry Site."""
    for e in LY.ENTRIES.values():
        if math.hypot(x - e[0], y - e[1]) < 34:
            return True
    return False


def fill_city():
    xs, ys = LY.STREETS_X, LY.STREETS_Y
    xs_full = [-EXT - 20] + xs + [EXT + 20]
    ys_full = [-EXT - 20] + ys + [EXT + 20]
    hb = LY.HQ_BLOCK
    for i in range(len(xs_full) - 1):
        for j in range(len(ys_full) - 1):
            xa, xb = xs_full[i], xs_full[i + 1]
            ya, yb = ys_full[j], ys_full[j + 1]
            if (xa, ya, xb, yb) == hb:
                continue
            bx0 = xa + (LY.street_w("x", xa) / 2 if xa in xs else 0) + 2.0
            bx1 = xb - (LY.street_w("x", xb) / 2 if xb in xs else 0) - 2.0
            by0 = ya + (LY.street_w("y", ya) / 2 if ya in ys else 0) + 2.0
            by1 = yb - (LY.street_w("y", yb) / 2 if yb in ys else 0) - 2.0
            # keep the elevated highway corridor clear
            if 90 in (ya, yb):
                if ya == 90:
                    by0 = max(by0, 90 + 17)
                if yb == 90:
                    by1 = min(by1, 90 - 13)
            if 220 in (xa, xb):
                if xa == 220:
                    bx0 = max(bx0, 220 + 13)
                if xb == 220:
                    bx1 = min(bx1, 220 - 13)
            # sidewalk / lot plate
            box(bx0 - 1.2, by0 - 1.2, 0, bx1 + 1.2, by1 + 1.2, 0.35, LOT, facet=False)
            nx = rng.choice([2, 2, 3])
            ny = rng.choice([2, 2, 3])
            cw, ch = (bx1 - bx0) / nx, (by1 - by0) / ny
            for a in range(nx):
                for b in range(ny):
                    if rng.random() < 0.08:
                        continue
                    lx0 = bx0 + a * cw + rng.uniform(0.6, 2.2)
                    lx1 = bx0 + (a + 1) * cw - rng.uniform(0.6, 2.2)
                    ly0 = by0 + b * ch + rng.uniform(0.6, 2.2)
                    ly1 = by0 + (b + 1) * ch - rng.uniform(0.6, 2.2)
                    cx, cy = (lx0 + lx1) / 2, (ly0 + ly1) / 2
                    p = LY.project(cx, cy)
                    if not (-260 < p[0] < LY.W + 260 and -500 < p[1] < LY.H + 300):
                        continue
                    d = math.hypot(cx - 30, cy - 0)
                    far = max(0.0, min(1.0, (d - 90) / 200))
                    h = rng.uniform(7, 15) + far * rng.uniform(10, 70)
                    if p[1] < 260:   # the skyline at the top of the frame: taller
                        h += rng.uniform(0, 40)
                    corp = entry_corp(cx, cy)
                    c = rng.choice(FAMS)
                    if corp:
                        c = rng.choice([(0.40, 0.38, 0.58), (0.36, 0.34, 0.54)])
                        h = max(h, 22)
                    building(lx0, ly0, lx1, ly1, h, c, corp=corp)


# ------------------------------------------------------------------ the Cell's HQ (CORE)
def hq():
    x0, y0, x1, y1 = 10 + LY.AW / 2 + 2, -50 + LY.AW / 2 + 2, 80 - LY.SW / 2 - 2, 20 - LY.SW / 2 - 2
    box(x0 - 1, y0 - 1, 0, x1 + 1, y1 + 1, 0.35, LOT, facet=False)
    cx, cy = (x0 + x1) / 2 + 2, (y0 + y1) / 2 + 2
    # podium: an old telecom exchange
    box(x0 + 2, y0 + 2, 0, x1 - 2, y1 - 2, 12, (0.36, 0.33, 0.40))
    windows(x0 + 2, y0 + 2, 0, x1 - 2, y1 - 2, 12, p=0.5, cols=[(1.0, 0.42, 0.72), (1.0, 0.68, 0.28)])
    roof_trim(x0 + 2.2, y0 + 2.2, x1 - 2.2, y1 - 2.2, 12.2, PINK, w=0.55)
    # loading bay doors facing the CORE pad (the -x and -y faces)
    for k in range(3):
        yy = y0 + 8 + k * 9
        box(x0 + 1.4, yy, 0, x0 + 2, yy + 6, 5.5, (0.08, 0.07, 0.09), facet=False)
        NEON.face([(x0 + 1.3, yy, 5.8), (x0 + 1.3, yy + 6, 5.8), (x0 + 1.3, yy + 6, 6.3), (x0 + 1.3, yy, 6.3)], PINK, (0, 0, 0))
    # hex tower, stepped, with a crown
    prism(cx, cy, 12, 44, 15, 6, (0.38, 0.35, 0.44), rot=0.3)
    for z in range(16, 44, 4):
        for i in range(6):
            a0 = 0.3 + 2 * math.pi * i / 6
            a1 = 0.3 + 2 * math.pi * (i + 1) / 6
            if rng.random() < 0.55:
                p0 = (cx + 15.08 * math.cos(a0), cy + 15.08 * math.sin(a0))
                p1 = (cx + 15.08 * math.cos(a1), cy + 15.08 * math.sin(a1))
                for t in (0.15, 0.4, 0.65):
                    if rng.random() < 0.6:
                        q0 = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
                        q1 = (p0[0] + (p1[0] - p0[0]) * (t + 0.18), p0[1] + (p1[1] - p0[1]) * (t + 0.18))
                        WIN.face([(q0[0], q0[1], z), (q1[0], q1[1], z), (q1[0], q1[1], z + 1.6), (q0[0], q0[1], z + 1.6)],
                                 rng.choice([(1.0, 0.42, 0.72), (1.0, 0.68, 0.28), (0.45, 0.9, 1.0)]), (0, 0, 0))
    prism(cx, cy, 44, 52, 12, 6, (0.32, 0.30, 0.38), rot=0.3)
    ring(NEON, cx, cy, 44.2, 15.2, 0.9, PINK, n=6)
    ring(NEON, cx, cy, 52.2, 12.2, 0.7, PINK, n=6)
    prism(cx, cy, 52, 58, 7, 6, (0.28, 0.26, 0.32), rot=0.3)
    # pirate antennas, dishes, a big cable bundle
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.2
        px, py = cx + 9 * math.cos(a), cy + 9 * math.sin(a)
        hh = rng.uniform(8, 20)
        beam((px, py, 52), (px, py, 52 + hh), 0.4, (0.25, 0.25, 0.3))
        NEON.face([(px - 0.6, py, 52 + hh - 1), (px + 0.6, py, 52 + hh - 1), (px + 0.6, py, 52 + hh), (px - 0.6, py, 52 + hh)], PINK, (0, 0, 0))
    beam((cx, cy, 58), (cx, cy, 86), 0.8, (0.22, 0.22, 0.26))
    for z in (66, 74, 82):
        ring(NEON, cx, cy, z, 1.6, 0.35, PINK, n=8)
    for (a, z) in ((0.9, 30), (-0.6, 38), (2.4, 24)):
        px, py = cx + 15.5 * math.cos(a), cy + 15.5 * math.sin(a)
        prism(px, py, z, z + 1.2, 3.2, 10, (0.6, 0.6, 0.64), r1=4.2, facet=False)
    # big pink neon CELL hex emblem on the two visible faces
    text_obj("CORE", (x0 + 1.2, (y0 + y1) / 2, 8.6), (math.radians(90), 0, math.radians(-90)), 4.6, SIGNM)
    text_obj("REBEL_CELL", ((x0 + x1) / 2, y0 + 1.2, 8.6), (math.radians(90), 0, 0), 3.4, SIGNM)
    BUILDINGS.append((cx - 7, cy - 7, cx + 7, cy + 7, 58))


# ------------------------------------------------------------------ elevated highways + flying traffic
def highways():
    for axis, v, decks in LY.HIGHWAYS:
        for di, z in enumerate(decks):
            off = (-5.5 if di == 0 else 5.5) if len(decks) > 1 else 0.0
            w = 12.0
            c = (0.30, 0.29, 0.34)
            if axis == "y":
                yc = v + off
                box(-EXT, yc - w / 2, z - 1.6, EXT, yc + w / 2, z, c, facet=False)
                for s in (-1, 1):   # barriers with neon strip
                    box(-EXT, yc + s * w / 2 - 0.4, z, EXT, yc + s * w / 2 + 0.4, z + 1.2, (0.24, 0.23, 0.27), facet=False)
                    strip(NEON, (-EXT, yc + s * (w / 2 + 0.45)), (EXT, yc + s * (w / 2 + 0.45)), 0.35, z + 0.9, CYAN if di else AMBER)
                for x in range(-EXT, EXT, 24):
                    if di == 0 or len(decks) == 1:
                        box(x - 1.4, yc - 1.4, 0, x + 1.4, yc + 1.4, z - 1.6, (0.27, 0.26, 0.31))
                    else:
                        box(x - 1.2, yc - 1.2, 0, x + 1.2, yc + 1.2, z - 1.6, (0.27, 0.26, 0.31))
                for lane in (-3.0, 3.0):
                    for k in range(26):
                        x0 = vrng.uniform(-EXT, EXT)
                        L = vrng.uniform(10, 30)
                        strip(NEON, (x0, yc + lane), (x0 + L, yc + lane), 0.5, z + 0.05, WHITE if lane > 0 else RED, r=vrng)
                    for k in range(10):
                        x0 = vrng.uniform(-EXT, EXT)
                        car(x0, yc + lane, 0.0 if lane > 0 else math.pi, vrng)
            else:
                xc = v + off
                box(xc - w / 2, -EXT, z - 1.6, xc + w / 2, EXT, z, c, facet=False)
                for s in (-1, 1):
                    box(xc + s * w / 2 - 0.4, -EXT, z, xc + s * w / 2 + 0.4, EXT, z + 1.2, (0.24, 0.23, 0.27), facet=False)
                    strip(NEON, (xc + s * (w / 2 + 0.45), -EXT), (xc + s * (w / 2 + 0.45), EXT), 0.35, z + 0.9, PINK)
                for y in range(-EXT, EXT, 24):
                    box(xc - 1.4, y - 1.4, 0, xc + 1.4, y + 1.4, z - 1.6, (0.27, 0.26, 0.31))
                for lane in (-3.0, 3.0):
                    for k in range(22):
                        y0 = vrng.uniform(-EXT, EXT)
                        L = vrng.uniform(10, 30)
                        strip(NEON, (xc + lane, y0), (xc + lane, y0 + L), 0.5, z + 0.05, WHITE if lane > 0 else RED, r=vrng)
    # a ramp from the lower deck down toward the west of the district
    for k in range(12):
        x = -150 - k * 6
        z = 12 - k * 1.0
        box(x - 3, 90 - 11 - 6, z - 1.4, x + 3, 90 - 11 + 6, z, (0.30, 0.29, 0.34), facet=False)


def flyers():
    """Flying vehicles on three sky lanes, each with a light trail."""
    for lane_z, n in ((34, 9), (46, 7), (60, 5)):
        for k in range(n):
            x = vrng.uniform(-260, 300)
            y = vrng.uniform(-200, 260)
            ang = vrng.choice([0.0, math.pi / 2, math.pi, -math.pi / 2]) + vrng.uniform(-0.1, 0.1)
            p = LY.project(x, y, lane_z)
            # keep them off the node pads on screen
            if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 80 for q in [LY.project(n_[0], n_[1]) for n_ in LY.NODES.values()]):
                continue
            obox(x, y, lane_z, 4.5, 2.2, 1.2, ang, (0.5, 0.52, 0.6), r=vrng)
            ca, sa = math.cos(ang), math.sin(ang)
            col = vrng.choice([CYAN, PINK, WHITE, AMBER])
            beam((x - ca * 2.3, y - sa * 2.3, lane_z + 0.6), (x - ca * 18, y - sa * 18, lane_z + 0.6), 0.45, col, acc=NEON, r=vrng)
            box(x - 0.4, y - 0.4, lane_z - 0.4, x + 0.4, y + 0.4, lane_z, col, acc=NEON, facet=False, r=vrng)


# ------------------------------------------------------------------ hologram billboards
def make_ad_image(name, seed, kind):
    """A fake ad: blocky unreadable 'text' rows, a logo shape, scanlines (luminance only)."""
    w, h = 192, 108
    r = np.random.default_rng(seed)
    a = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    if kind == 0:     # face/circle logo left + text rows right
        a += ((xx - 50) ** 2 + (yy - 54) ** 2 < 36 ** 2) * 0.55
        a += ((xx - 50) ** 2 + (yy - 54) ** 2 < 24 ** 2) * 0.35
        for row in range(4):
            y0 = 22 + row * 18
            x = 100
            while x < 180:
                L = int(r.integers(4, 18))
                a[y0:y0 + 9, x:min(180, x + L)] = 0.9 if row == 0 else 0.6
                x += L + 4
    elif kind == 1:   # big chevron product + bar
        a += (np.abs(xx - 96) + yy * 0.8 < 70) * (np.abs(xx - 96) + yy * 0.8 > 44) * 0.8
        a[84:98, 30:162] = 0.9
    else:             # corp halo ring + slogan bars (Halcyon "COMPLY")
        d = np.sqrt((xx - 96) ** 2 + ((yy - 46) * 1.4) ** 2)
        a += ((d > 26) & (d < 36)) * 0.9
        for k in range(5):
            x0 = 34 + k * 26
            a[84:96, x0:x0 + 20] = 0.85
    a *= 0.75 + 0.25 * (yy % 3 != 0)
    a = np.clip(a + 0.22, 0, 1)
    img = bpy.data.images.new(name, w, h, alpha=False)
    px = np.dstack([a, a, a, np.ones_like(a)])[::-1].reshape(-1)
    img.pixels.foreach_set(px.astype(np.float32))
    img.pack()
    return img


HOLO_IMGS = [make_ad_image("ad%d" % k, 70 + k, k) for k in range(3)]
HOLO_MATS = [mat_additive("holo%d" % k, image=HOLO_IMGS[k], strength=1.6) for k in range(3)]
HOLO_ACC = {k: Acc("holo%d" % k) for k in range(3)}


def holo_plane(cx, cy, z, w, h, col, kind):
    """Vertical billboard plane facing the camera (normal = -fwd on the ground)."""
    rx, ry = r_[0], r_[1]
    acc = HOLO_ACC[kind]
    p = [(cx - rx * w / 2, cy - ry * w / 2, z), (cx + rx * w / 2, cy + ry * w / 2, z),
         (cx + rx * w / 2, cy + ry * w / 2, z + h), (cx - rx * w / 2, cy - ry * w / 2, z + h)]
    f = acc.face(p, col, (0, 0, 0))
    uv = acc.bm.loops.layers.uv.verify()
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    # projector bar + 2 faint emitter rays
    beam((cx - rx * w / 2, cy - ry * w / 2, z - 0.6), (cx + rx * w / 2, cy + ry * w / 2, z - 0.6), 0.6, (0.2, 0.2, 0.24))
    strip(NEON, (cx - rx * w / 2, cy - ry * w / 2), (cx + rx * w / 2, cy + ry * w / 2), 0.3, z - 0.2, col)


def billboards():
    cands = sorted([b for b in BUILDINGS if b[4] > 24], key=lambda b: (round(b[4], 3), b[0], b[1]))
    picks = []
    for b in cands[::-1]:
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        p = LY.project(cx, cy, b[4] + 8)
        if not (120 < p[0] < LY.W - 120 and 40 < p[1] < LY.H - 300):
            continue
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 300 for q in picks):
            continue
        if any(math.hypot(p[0] - qq[0], p[1] - qq[1]) < 140 for qq in [LY.project(n[0], n[1]) for n in LY.NODES.values()]):
            continue
        picks.append(p + (b,))
        if len(picks) >= 7:
            break
    cols = [PINK, CYAN, GREEN, VIOLET, AMBER, CYAN, PINK]
    for i, p in enumerate(picks):
        b = p[3]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        corp = HEAT >= 2 and i % (4 - min(HEAT, 3) + 1) == 0
        col = HALCYON if corp else cols[i % len(cols)]
        kind = 2 if corp else i % 2
        w = rng.uniform(30, 40)
        holo_plane(cx, cy, b[4] + 4, w, w * 0.56, col, kind)
    # facade banners (opaque emissive panels on -x / -y faces), a few
    k = 0
    for b in cands[::-1][len(picks):]:
        if k >= 10:
            break
        x0, y0, x1, y1, top = b
        p = LY.project((x0 + x1) / 2, (y0 + y1) / 2, top * 0.6)
        if not (60 < p[0] < LY.W - 60 and 30 < p[1] < LY.H - 220):
            continue
        if top < 26:
            continue
        col = rng.choice([PINK, CYAN, AMBER, GREEN])
        zc = top * rng.uniform(0.45, 0.7)
        if rng.random() < 0.5:
            yv = y0 - 0.12
            xa = x0 + (x1 - x0) * 0.2
            NEON.face([(xa, yv, zc), (xa + 3.2, yv, zc), (xa + 3.2, yv, zc + 12), (xa, yv, zc + 12)], col, (0, 0, 0))
        else:
            xv = x0 - 0.12
            ya = y0 + (y1 - y0) * 0.3
            NEON.face([(xv, ya + 3.2, zc), (xv, ya, zc), (xv, ya, zc + 12), (xv, ya + 3.2, zc + 12)], col, (0, 0, 0))
        k += 1


# ------------------------------------------------------------------ node hardware (ground level, at the pad edge)
def node_props():
    for key, n in LY.NODES.items():
        x, y, kind = n[0], n[1], n[2]
        ex, ey = x - 7.5, y + 7.5     # back-left corner of the pad (behind the unit on screen? no: left)
        if kind == "relay":
            beam((x + 6.5, y + 6.5, 0), (x + 6.5, y + 6.5, 11), 0.5, GUNMETAL)
            for z in (4, 7, 10):
                beam((x + 5.3, y + 6.5, z), (x + 7.7, y + 6.5, z), 0.25, GUNMETAL)
            box(x + 6.0, y + 6.0, 11, x + 7.0, y + 7.0, 12, GREEN, acc=NEON, facet=False)
        elif kind == "vault":
            box(x + 4.5, y + 4.5, 0, x + 8.5, y + 8.5, 4.5, (0.45, 0.46, 0.5))
            prism(x + 6.5, y + 4.4, 1.2, 1.3, 1.4, 12, (0.7, 0.7, 0.72), facet=False)
            NEON.face([(x + 4.4, y + 5, 3.6), (x + 4.4, y + 8, 3.6), (x + 4.4, y + 8, 4.0), (x + 4.4, y + 5, 4.0)], AMBER, (0, 0, 0))
        elif kind == "proxy":
            beam((x + 6.5, y + 6.5, 0), (x + 6.5, y + 6.5, 5), 0.6, GUNMETAL)
            prism(x + 6.5, y + 6.5, 5, 5.6, 1.0, 10, (0.65, 0.65, 0.7), r1=3.4, facet=False)
        elif kind == "safehouse":
            box(x + 4.0, y + 4.5, 0, x + 9, y + 9, 3.2, (0.42, 0.38, 0.34))
            box(x + 3.9, y + 5.8, 0, x + 4.1, y + 7.4, 2.4, (0.08, 0.07, 0.08), facet=False)
            NEON.face([(x + 3.85, y + 5.8, 2.6), (x + 3.85, y + 7.4, 2.6), (x + 3.85, y + 7.4, 2.9), (x + 3.85, y + 5.8, 2.9)], GREEN, (0, 0, 0))
        elif kind == "firewall":
            # the built-in firewall: a low curved wall of glowing slats on the threat side of the pad
            for i in range(7):
                a0 = math.radians(60 + i * 14)
                a1 = math.radians(60 + (i + 1) * 14 - 3)
                p0 = (x + 9.5 * math.cos(a0), y + 9.5 * math.sin(a0))
                p1 = (x + 9.5 * math.cos(a1), y + 9.5 * math.sin(a1))
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                obox(mx, my, 0, math.hypot(p1[0] - p0[0], p1[1] - p0[1]), 0.9, 3.4, math.atan2(p1[1] - p0[1], p1[0] - p0[0]), (0.32, 0.3, 0.34))
                obox(mx, my, 3.4, math.hypot(p1[0] - p0[0], p1[1] - p0[1]), 0.95, 0.5, math.atan2(p1[1] - p0[1], p1[0] - p0[0]), AMBER, acc=NEON)
    # corporate entry beacons (Halcyon): a pylon at the corner of the entry intersection
    for k, e in LY.ENTRIES.items():
        x, y = e
        bx, by = x + 9.5, y + 9.5
        beam((bx, by, 0), (bx, by, 9), 0.9, (0.22, 0.2, 0.3))
        for z in (3, 6, 9):
            ring(NEON, bx, by, z, 1.2, 0.3, HALCYON, n=8)
        box(bx - 0.7, by - 0.7, 9, bx + 0.7, by + 0.7, 10.4, RED, acc=NEON, facet=False)


# ------------------------------------------------------------------ defences (stand ON the pads)
SPOTS = {}   # unit name -> world point (for labels / tracers in post)


def aim_ang(x, y, tx, ty):
    return math.atan2(ty - y, tx - x)


def turret(x, y, ang, scale=1.0, col=CYAN):
    s = scale
    prism(x, y, 0.3, 1.6 * s, 3.4 * s, 6, (0.30, 0.31, 0.36), rot=0.2, r=vrng)
    ring(NEON, x, y, 1.65 * s, 3.0 * s, 0.35, col, n=6, r=vrng)
    prism(x, y, 1.6 * s, 3.0 * s, 1.4 * s, 8, GUNMETAL, r=vrng)
    obox(x, y, 3.0 * s, 4.2 * s, 3.4 * s, 2.2 * s, ang, (0.42, 0.44, 0.5), taper=0.4 * s, r=vrng, facet=True)
    ca, sa = math.cos(ang), math.sin(ang)
    for side in (-0.75, 0.75):
        px, py = x + ca * 1.6 * s - sa * side * s, y + sa * 1.6 * s + ca * side * s
        beam((px, py, 4.1 * s), (px + ca * 4.8 * s, py + sa * 4.8 * s, 4.3 * s), 0.55 * s, (0.15, 0.15, 0.18), r=vrng)
    strip(NEON, (x - sa * 1.72 * s - ca * 1.5 * s, y + ca * 1.72 * s - sa * 1.5 * s), (x - sa * 1.72 * s + ca * 1.5 * s, y + ca * 1.72 * s + sa * 1.5 * s), 0.4, 4.6 * s, col, r=vrng)
    return (x + ca * 6.4 * s, y + sa * 6.4 * s, 4.3 * s)


def railgun(x, y, ang, col=CYAN):
    prism(x, y, 0.3, 1.4, 3.6, 8, (0.30, 0.31, 0.36), r=vrng)
    for k in range(3):     # tripod
        a = ang + math.pi + (k - 1) * 0.9
        beam((x, y, 3.2), (x + 3.4 * math.cos(a), y + 3.4 * math.sin(a), 0.4), 0.45, GUNMETAL, r=vrng)
    obox(x, y, 2.6, 3.6, 2.6, 2.0, ang, (0.42, 0.44, 0.5), r=vrng, facet=True)
    ca, sa = math.cos(ang), math.sin(ang)
    p0 = (x - ca * 2.5, y - sa * 2.5, 3.4)
    p1 = (x + ca * 9.5, y + sa * 9.5, 5.4)
    beam(p0, p1, 0.9, (0.18, 0.18, 0.22), r=vrng)
    for t in (0.35, 0.5, 0.65, 0.8):
        q = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t)
        q2 = (q[0] + ca * 0.4, q[1] + sa * 0.4, q[2] + 0.07)
        beam(q, q2, 1.6, col, acc=NEON, r=vrng)
    return p1


def ice_lock(x, y, col=(0.72, 0.92, 1.0)):
    for k in range(4):
        a = math.radians(45 + 90 * k)
        px, py = x + 6.2 * math.cos(a), y + 6.2 * math.sin(a)
        box(px - 0.6, py - 0.6, 0, px + 0.6, py + 0.6, 3.2, GUNMETAL, facet=False, r=vrng)
        prism(px, py, 3.2, 4.8, 0.7, 4, col, acc=NEON, r1=0.05, rot=0.785, r=vrng, facet=False)
    return (x, y, 3)


def flak(x, y, ang, col=AMBER):
    obox(x, y, 0.3, 4.6, 4.6, 1.6, ang, (0.30, 0.31, 0.36), r=vrng)
    ca, sa = math.cos(ang), math.sin(ang)
    for i in (-1, 1):
        for j in (-1, 1):
            px, py = x - sa * i * 1.0 + ca * j * 0.6, y + ca * i * 1.0 + sa * j * 0.6
            beam((px, py, 1.6), (px + ca * 2.4, py + sa * 2.4, 5.0), 0.8, (0.2, 0.2, 0.24), r=vrng)
            box(px + ca * 2.4 - 0.3, py + sa * 2.4 - 0.3, 5.0, px + ca * 2.4 + 0.3, py + sa * 2.4 + 0.3, 5.3, col, acc=NEON, facet=False, r=vrng)
    return (x + ca * 3, y + sa * 3, 5.2)


def sentry(x, y, ang, col=GREEN):
    return turret(x, y, ang, scale=0.72, col=col)


def scaled(s, x, y, fn, *a, z0=0.0, **k):
    """Run a unit builder, then scale the geometry it added about (x, y, 0): toy-scale units read at map zoom."""
    accs = (SOLID, NEON)
    starts = []
    for acc in accs:
        acc.bm.verts.ensure_lookup_table()
        starts.append(len(acc.bm.verts))
    res = fn(*a, **k)
    for acc, st in zip(accs, starts):
        acc.bm.verts.ensure_lookup_table()
        for i in range(st, len(acc.bm.verts)):
            v = acc.bm.verts[i]
            v.co.x = x + (v.co.x - x) * s
            v.co.y = y + (v.co.y - y) * s
            v.co.z = z0 + (v.co.z - z0) * s
    if res is None:
        return None
    return (x + (res[0] - x) * s, y + (res[1] - y) * s, z0 + (res[2] - z0) * s)


US, TS = 1.6, 1.6   # defence / threat toy scale


def defences():
    N = LY.NODES
    fx, fy = N["firewall"][:2]
    SPOTS["fw_turret"] = scaled(US, fx - 2, fy - 2, turret, fx - 2, fy - 2, aim_ang(fx, fy, -60, 20))
    SPOTS["fw_ice"] = scaled(1.0, fx, fy, ice_lock, fx, fy)
    vx, vy = N["vault"][:2]
    SPOTS["railgun"] = scaled(US, vx - 1, vy - 1, railgun, vx - 1, vy - 1, aim_ang(vx, vy, 150, -50))
    cx, cy = N["core"][:2]
    SPOTS["core_turret"] = scaled(US, cx - 1.5, cy - 1.5, turret, cx - 1.5, cy - 1.5, aim_ang(cx, cy, 80, -120), 1.1, PINK)
    sx, sy = N["safe"][:2]
    SPOTS["sentry"] = scaled(US, sx - 1, sy - 1, sentry, sx - 1, sy - 1, aim_ang(sx, sy, 80, -120))
    if VARIANT == "wave":
        px, py = N["proxy"][:2]
        SPOTS["flak"] = scaled(US, px - 1, py - 1, flak, px - 1, py - 1, aim_ang(px, py, -130, 20))


# ------------------------------------------------------------------ threats (Halcyon Civic)
THREATS = []


def rim(x, y, z, L, Wd, ang, col=HALCYON, w=0.45):
    """Hostile glow: a neon rim round a vehicle's top edge so threats read at night."""
    ca, sa = math.cos(ang), math.sin(ang)
    c = [(x + ca * u - sa * v, y + sa * u + ca * v, z) for u, v in ((-L / 2, -Wd / 2), (L / 2, -Wd / 2), (L / 2, Wd / 2), (-L / 2, Wd / 2))]
    for i in range(4):
        beam(c[i], c[(i + 1) % 4], w, col, acc=NEON, r=vrng)


def light_bar(x, y, z, ang, L=2.4):
    ca, sa = math.cos(ang), math.sin(ang)
    for k, c in ((-1, RED), (1, BLUE)):
        px, py = x - sa * k * L / 4, y + ca * k * L / 4
        obox(px, py, z, 0.8, L / 2, 0.5, ang, c, acc=NEON, r=vrng)


def bailiff(x, y, ang):
    rim(x, y, 3.4, 10.0, 4.8, ang)
    rim(x, y, 0.9, 11.2, 5.4, ang, col=(0.35, 0.3, 0.6), w=0.3)
    obox(x, y, 0.4, 11, 5.2, 3.0, ang, (0.66, 0.62, 0.92), taper=0.5, r=vrng, facet=True)
    obox(x, y, 3.42, 9.0, 0.9, 0.12, ang, HALCYON, acc=NEON, r=vrng)
    ca, sa = math.cos(ang), math.sin(ang)
    obox(x + ca * 3.5, y + sa * 3.5, 0.6, 3.0, 5.4, 2.2, ang, (0.24, 0.22, 0.36), taper=0.9, r=vrng)
    obox(x - ca * 1.0, y - sa * 1.0, 3.4, 5.0, 3.8, 1.6, ang, HALCYON, taper=0.5, r=vrng)
    light_bar(x + ca * 1.4, y + sa * 1.4, 5.0, ang)
    strip(NEON, (x - sa * 2.65 - ca * 5, y + ca * 2.65 - sa * 5), (x - sa * 2.65 + ca * 5, y + ca * 2.65 + sa * 5), 0.35, 1.8, HALCYON, r=vrng)
    return (x, y, 6)


def courier(x, y, ang):
    rim(x, y, 2.3, 4.8, 1.5, ang, w=0.3)
    obox(x, y, 1.0, 5.0, 1.6, 1.3, ang, (0.66, 0.62, 0.92), taper=0.3, r=vrng)
    ca, sa = math.cos(ang), math.sin(ang)
    box(x - 0.5, y - 0.5, 2.3, x + 0.5, y + 0.5, 3.2, HALCYON, facet=False, r=vrng)
    beam((x - ca * 2.5, y - sa * 2.5, 1.6), (x - ca * 22, y - sa * 22, 1.6), 0.8, HALCYON, acc=NEON, r=vrng)
    strip(NEON, (x - ca * 2.5, y - sa * 2.5), (x + ca * 2.5, y + sa * 2.5), 2.2, 0.08, tuple(v * 0.6 for v in HALCYON), r=vrng)
    return (x, y, 3.5)


def hauler(x, y, ang):
    rim(x - math.cos(ang) * 1.5, y - math.sin(ang) * 1.5, 5.8, 10.5, 5.0, ang)
    ca, sa = math.cos(ang), math.sin(ang)
    obox(x - ca * 1.5, y - sa * 1.5, 0.6, 10.5, 5.0, 5.2, ang, (0.74, 0.72, 0.86), r=vrng, facet=True)
    obox(x - ca * 1.5, y - sa * 1.5, 5.82, 9.5, 1.0, 0.12, ang, HALCYON, acc=NEON, r=vrng)
    obox(x + ca * 5.4, y + sa * 5.4, 0.6, 3.2, 4.8, 3.8, ang, (0.26, 0.24, 0.36), taper=0.3, r=vrng)
    for k in range(4):   # hazard chevrons on the side
        t = -5.5 + k * 2.6
        px, py = x + ca * t - sa * 2.55, y + sa * t + ca * 2.55
        obox(px, py, 2.4, 1.2, 0.1, 1.2, ang, HALCYON, acc=NEON, r=vrng)
    light_bar(x + ca * 5.4, y + sa * 5.4, 4.4, ang, L=3.2)
    return (x, y, 7)


def inspector(x, y, ang):
    rim(x, y, 2.1, 5.6, 2.8, ang, w=0.35)
    obox(x, y, 0.5, 6.0, 3.0, 1.6, ang, (0.66, 0.62, 0.92), taper=0.4, r=vrng, facet=True)
    ca, sa = math.cos(ang), math.sin(ang)
    obox(x - ca * 0.5, y - sa * 0.5, 2.1, 3.0, 2.4, 1.0, ang, (0.24, 0.22, 0.36), taper=0.3, r=vrng)
    light_bar(x, y, 3.1, ang, L=2.0)
    beam((x - ca * 3, y - sa * 3, 1.0), (x - ca * 16, y - sa * 16, 1.0), 0.6, HALCYON, acc=NEON, r=vrng)
    return (x, y, 4)


def lander(x, y, z):
    prism(x, y, z, z + 5.0, 3.8, 8, (0.66, 0.62, 0.92), r1=2.2, r=vrng)
    prism(x, y, z + 5.0, z + 6.5, 2.2, 8, HALCYON, r1=1.0, r=vrng, facet=False)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        beam((x + 3.0 * math.cos(a), y + 3.0 * math.sin(a), z + 0.5), (x + 4.6 * math.cos(a), y + 4.6 * math.sin(a), z - 2.0), 0.4, GUNMETAL, r=vrng)
    ring(NEON, x, y, z - 0.05, 2.4, 1.0, AMBER, n=10, r=vrng)
    # thruster cone of light down to the street + the landing ring painted by its beam
    cone(x, y, z, x, y, 0.2, 0.9, 6.5, (1.0, 0.55, 0.3), k=0.7)
    ring(NEON, x, y, 0.07, 7.5, 0.6, RED, n=20, r=vrng)
    return (x, y, z + 3)


def customs(x, y, ang):
    rim(x, y, 3.1, 7.0, 3.4, ang, w=0.4)
    obox(x, y, 0.5, 7.5, 3.6, 2.6, ang, (0.66, 0.62, 0.92), taper=0.4, r=vrng, facet=True)
    obox(x, y, 3.12, 6.0, 0.8, 0.12, ang, HALCYON, acc=NEON, r=vrng)
    light_bar(x, y, 3.1, ang)
    ca, sa = math.cos(ang), math.sin(ang)
    # the seal it leaves behind: a barrier of red-violet light across the street
    bx, by = x - ca * 9, y - sa * 9
    obox(bx, by, 0.1, 0.8, 15, 1.6, ang, (0.25, 0.22, 0.3), r=vrng)
    obox(bx, by, 1.7, 0.85, 15.2, 0.35, ang, RED, acc=NEON, r=vrng)
    return (x, y, 4)


def threats():
    T = [("bailiff", bailiff, (114, -50), math.pi),
         ("courier", courier, (88, -46.5), math.pi),
         ("hauler", hauler, (-60, 26), 0.0),
         ("inspector", inspector, (-24, 20), 0.0),
         ("customs", customs, (46, -120), math.pi)]
    for name, fn, (x, y), ang in T:
        SPOTS[name] = scaled(TS, x, y, fn, x, y, ang)
        THREATS.append((name, x, y))
    SPOTS["lander"] = lander(80, -152, 15)
    THREATS.append(("lander", 80, -152))


def tracer(p0, p1, col, w=0.5):
    """A shot: a bright beam from muzzle to target, with a hit flash."""
    beam(p0, p1, w, col, acc=NEON, r=vrng)
    for k in range(5):
        a = vrng.uniform(0, 2 * math.pi)
        b = vrng.uniform(-0.6, 0.9)
        L = vrng.uniform(1.5, 3.5)
        beam(p1, (p1[0] + L * math.cos(a) * math.cos(b), p1[1] + L * math.sin(a) * math.cos(b), p1[2] + L * math.sin(b)), 0.3, (1.0, 0.95, 0.8), acc=NEON, r=vrng)


def firing():
    tracer(SPOTS["fw_turret"], SPOTS["inspector"], CYAN, 0.45)
    tracer(SPOTS["railgun"], SPOTS["bailiff"], (0.8, 0.97, 1.0), 1.1)
    tracer(SPOTS["core_turret"], (46, -120, 3.5), PINK, 0.45)
    tracer(SPOTS["sentry"], SPOTS["customs"], GREEN, 0.4)
    f = SPOTS["flak"]
    for k in range(3):
        tgt = (SPOTS["hauler"][0] + vrng.uniform(-3, 3), SPOTS["hauler"][1] + vrng.uniform(-3, 3), SPOTS["hauler"][2] + vrng.uniform(0, 4))
        tracer(f, tgt, AMBER, 0.3)


# ------------------------------------------------------------------ heat escalation
POOLS = []     # searchlight pools for post: (x, y, radius, strength)


def cone(x0, y0, z0, x1, y1, z1, r0, r1, col, k=1.0, n=16):
    """Additive light cone between two points (hidden in data passes)."""
    p0, p1 = Vector((x0, y0, z0)), Vector((x1, y1, z1))
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized()
    b = d.cross(a).normalized()
    c = tuple(v * k for v in col)
    for i in range(n):
        t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        q = [p0 + (a * math.cos(t0) + b * math.sin(t0)) * r0, p1 + (a * math.cos(t0) + b * math.sin(t0)) * r1,
             p1 + (a * math.cos(t1) + b * math.sin(t1)) * r1, p0 + (a * math.cos(t1) + b * math.sin(t1)) * r0]
        BEAMS.face([tuple(v) for v in q], c, (0, 0, 0), r=vrng)


def helicopter(x, y, z, ang, target=None, gunship=False):
    s = 1.4 if gunship else 1.0
    ca, sa = math.cos(ang), math.sin(ang)
    body = (0.52, 0.49, 0.70)
    rim(x, y, z + 3.2 * s, 8.0 * s, 3.2 * s, ang, col=(1.0, 0.85, 0.6), w=0.35)
    obox(x, y, z, 8.5 * s, 3.6 * s, 3.2 * s, ang, body, taper=0.5, r=vrng, facet=True)
    obox(x + ca * 3.6 * s, y + sa * 3.6 * s, z + 0.6 * s, 2.4 * s, 3.0 * s, 2.0 * s, ang, (0.5, 0.6, 0.75), taper=0.5, r=vrng)
    beam((x - ca * 3.5 * s, y - sa * 3.5 * s, z + 2.2 * s), (x - ca * 11 * s, y - sa * 11 * s, z + 2.8 * s), 0.9 * s, body, r=vrng)
    obox(x - ca * 11 * s, y - sa * 11 * s, z + 2.4 * s, 1.2 * s, 0.3, 2.6 * s, ang, body, r=vrng)
    beam((x, y, z + 3.2 * s), (x, y, z + 4.0 * s), 0.6, GUNMETAL, r=vrng)
    for k in range(4):   # rotor blades (motion is a blurred disc in post)
        a = ang + 0.4 + k * math.pi / 2
        beam((x, y, z + 4.0 * s), (x + 8.5 * s * math.cos(a), y + 8.5 * s * math.sin(a), z + 4.1 * s), 0.5, (0.1, 0.1, 0.12), r=vrng)
    ring(NEON, x, y, z + 4.05 * s, 8.4 * s, 0.25, (0.25, 0.25, 0.3), n=24, r=vrng)
    for side in (-1, 1):
        px, py = x - sa * side * 1.9 * s, y + ca * side * 1.9 * s
        obox(px, py, z + 1.0 * s, 1.2, 0.2, 0.6, ang, RED if side < 0 else GREEN, acc=NEON, r=vrng)
    obox(x, y, z + 3.3 * s, 0.8, 0.8, 0.4, ang, RED, acc=NEON, r=vrng)
    obox(x - ca * 3 * s, y - sa * 3 * s, z + 0.4 * s, 4 * s, 0.25, 0.4, ang, HALCYON, acc=NEON, r=vrng)
    if gunship:
        for side in (-1, 1):
            px, py = x - sa * side * 3.0 * s, y + ca * side * 3.0 * s
            beam((px, py, z + 0.8 * s), (px + ca * 3, py + sa * 3, z + 0.8 * s), 0.9, GUNMETAL, r=vrng)
    if target:
        tx, ty = target
        nx, ny = x + ca * 4.5 * s, y + sa * 4.5 * s
        cone(nx, ny, z, tx, ty, 0.3, 0.7, 9.0, (0.85, 0.9, 1.0), k=1.0)
        POOLS.append((tx, ty, 11.0, 1.0))


def drone(x, y, z, r=None):
    r = r or vrng
    box(x - 0.9, y - 0.9, z, x + 0.9, y + 0.9, z + 0.8, (0.28, 0.26, 0.34), facet=False, r=r)
    for i in (-1, 1):
        for j in (-1, 1):
            beam((x, y, z + 0.6), (x + i * 2.0, y + j * 2.0, z + 0.7), 0.25, GUNMETAL, r=r)
            ring(NEON, x + i * 2.0, y + j * 2.0, z + 0.75, 0.9, 0.15, (0.35, 0.35, 0.42), n=8, r=r)
    box(x - 0.35, y - 0.35, z - 0.25, x + 0.35, y + 0.35, z + 0.05, RED, acc=NEON, facet=False, r=r)


def strobe(x, y, r=None):
    """Police corner unit: a barricade with a red/blue light bar on the street corner."""
    r = r or vrng
    obox(x, y, 0.35, 6.0, 1.2, 1.4, r.uniform(0, math.pi), (0.85, 0.85, 0.88), r=r)
    obox(x, y, 1.75, 6.1, 0.5, 0.3, 0.0, RED, acc=NEON, r=r)
    obox(x + 1.5, y, 1.75, 2.0, 0.55, 0.32, 0.0, BLUE, acc=NEON, r=r)
    ring(NEON, x, y, 0.06, 5.0, 1.4, (0.35, 0.05, 0.08), n=14, r=r)


def heat_props():
    N = LY.NODES
    # helicopters: (x, y, z, heading, searchlight target)
    helis = {1: [(235, -10, 70, math.pi * 0.9, LY.ENTRIES["e_east"])],
             2: [(235, -10, 70, math.pi * 0.9, N["vault"][:2]), (-40, 60, 64, -0.7, N["firewall"][:2]),
                 (140, -150, 58, 2.4, N["safe"][:2])],
             3: [(235, -10, 70, math.pi * 0.9, N["vault"][:2]), (-40, 60, 64, -0.7, N["proxy"][:2]),
                 (140, -150, 58, 2.4, N["safe"][:2]), (-110, -80, 72, 0.3, N["relay"][:2]),
                 (60, 60, 82, -2.2, N["firewall"][:2])]}
    for (x, y, z, a, t) in helis.get(HEAT, []):
        scaled(1.9, x, y, helicopter, x, y, z, a, target=t, z0=z)
    if HEAT >= 3:
        scaled(1.9, -10, -190, helicopter, -10, -190, 92, 1.0, target=N["core"][:2], gunship=True, z0=92)
    nd = {1: 4, 2: 12, 3: 26}.get(HEAT, 0)
    k = 0
    tries = 0
    while k < nd and tries < 400:
        tries += 1
        x, y, z = vrng.uniform(-150, 200), vrng.uniform(-200, 120), vrng.uniform(26, 52)
        p = LY.project(x, y, z)
        if not (200 < p[0] < 1700 and 120 < p[1] < 860):
            continue
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 70 for q in [LY.project(n_[0], n_[1]) for n_ in N.values()]):
            continue
        scaled(1.7, x, y, drone, x, y, z, z0=z)
        if HEAT >= 3 and k % 3 == 0:
            cone(x, y, z, x + vrng.uniform(-8, 8), y + vrng.uniform(-8, 8), 0.2, 0.3, 4.0, (1.0, 0.4, 0.45), k=0.8)
        k += 1
    if HEAT >= 2:
        corners = [(150 - 12, -50 + 12), (-130 + 12, 20 - 12), (80 + 12, -190 + 12), (-60 - 13, 90 - 22), (150 + 13, 20 - 12)]
        if HEAT >= 3:
            corners += [(220 - 12, -120 + 12), (-130 - 12, -50 + 12), (80 + 13, 20 - 13), (-200 + 12, 20 + 12), (150 - 13, -190 + 13)]
        for (x, y) in corners:
            strobe(x, y)
    if HEAT >= 3:   # sky searchlights from the corp towers sweep the clouds
        for (x, y) in ((260, 150), (-200, 200), (300, -120)):
            cone(x, y, 40, x - 60, y - 40, 260, 1.0, 14.0, (0.8, 0.85, 1.0), k=0.45)


# ------------------------------------------------------------------ build
fill_city()
hq()
highways()
flyers()
billboards()
node_props()
defences()
if VARIANT == "wave":
    threats()
    firing()
heat_props()

solid = SOLID.obj(TOON)
neon = NEON.obj(NEONM)
win = WIN.obj(WINM)
beams_ob = BEAMS.obj(BEAMM) if len(BEAMS.bm.faces) else None
holo_obs = []
for k, acc in HOLO_ACC.items():
    if len(acc.bm.faces):
        holo_obs.append(acc.obj(HOLO_MATS[k][0], "holo%d" % k))
    else:
        acc.bm.free()

sun_d = bpy.data.lights.new("key", "SUN")
sun_d.energy = 3.2
try:
    sun_d.shadow_maximum_resolution = 0.05
except Exception:
    pass
sun = bpy.data.objects.new("key", sun_d)
sun.rotation_euler = (math.radians(46), math.radians(-24), math.radians(-30))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("w")
scene.world = world
wnt = world.node_tree
bg = wnt.nodes.get("Background")
bg.inputs["Strength"].default_value = 1.0

MODES = {
    "day": dict(ramp=[(0.10, 0.12, 0.22), (0.22, 0.24, 0.33), (0.46, 0.45, 0.42)], neon=0.7, win=0.5, win_mix=0.55,
                glass=(0.10, 0.14, 0.20), sign=(1.0, 0.3, 0.66), world=(0.52, 0.58, 0.68), beam=0.035, holo=0.6),
    "night": dict(ramp=[(0.020, 0.018, 0.055), (0.050, 0.042, 0.11), (0.115, 0.095, 0.21)], neon=1.0, win=1.0, win_mix=0.0,
                  glass=(0.0, 0.0, 0.0), sign=(1.0, 0.24, 0.66), world=(0.03, 0.025, 0.06), beam=0.07, holo=0.85),
}


def set_mode(m):
    M = MODES[m]
    for e, c in zip(RAMP.color_ramp.elements, M["ramp"]):
        e.color = c + (1,)
    NEON_SC.inputs["Scale"].default_value = M["neon"]
    NEON_MIX.inputs["Factor"].default_value = 0.0
    WIN_SC.inputs["Scale"].default_value = M["win"]
    WIN_MIX.inputs["Factor"].default_value = M["win_mix"]
    WIN_MIX.inputs[7].default_value = M["glass"] + (1,)
    SIGN_EM.inputs["Color"].default_value = M["sign"] + (1,)
    BEAM_SC.inputs["Scale"].default_value = M["beam"]
    for m_, sc in HOLO_MATS:
        sc.inputs["Scale"].default_value = M["holo"]
    bg.inputs["Color"].default_value = M["world"] + (1,)


def render(path, fmt="PNG"):
    scene.render.image_settings.file_format = fmt
    if fmt == "PNG":
        scene.render.image_settings.color_depth = "16"
        scene.render.image_settings.color_mode = "RGB"
    else:
        scene.render.image_settings.color_depth = "32"
        scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path, flush=True)


def override_mat(kind):
    m = bpy.data.materials.new("ov_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    if kind == "normal":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5)
        vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        L(geo.outputs["Normal"], vm.inputs[0])
        L(vm.outputs[0], em.inputs["Color"])
    elif kind == "id":
        a = attr(nt, "bid")
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.blend_type = "ADD"
        mx.inputs["Factor"].default_value = 1.0
        L(a.outputs["Color"], mx.inputs[6])
        cc = nt.nodes.new("ShaderNodeCombineColor")
        L(oi.outputs["Random"], cc.inputs[0])
        L(oi.outputs["Random"], cc.inputs[2])
        L(cc.outputs[0], mx.inputs[7])
        L(mx.outputs[2], em.inputs["Color"])
    elif kind in ("pos_hi", "pos_lo"):
        # negative emission is clamped and EEVEE buffers are half float: store pos + 1000 split into
        # floor(/16) (exact small integers) and mod 16 (fine part); save_pos_npy recombines them
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        off = nt.nodes.new("ShaderNodeVectorMath")
        off.operation = "ADD"
        off.inputs[1].default_value = (1000.0, 1000.0, 1000.0)
        L(geo.outputs["Position"], off.inputs[0])
        op = nt.nodes.new("ShaderNodeVectorMath")
        if kind == "pos_hi":
            dv = nt.nodes.new("ShaderNodeVectorMath")
            dv.operation = "DIVIDE"
            dv.inputs[1].default_value = (16.0, 16.0, 16.0)
            L(off.outputs[0], dv.inputs[0])
            op.operation = "FLOOR"
            L(dv.outputs[0], op.inputs[0])
        else:
            op.operation = "MODULO"
            op.inputs[1].default_value = (16.0, 16.0, 16.0)
            L(off.outputs[0], op.inputs[0])
        L(op.outputs[0], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m


def load_exr(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    buf = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    os.remove(path)
    return buf.reshape(h, w, 4)[::-1, :, :3]


def save_pos_npy(hi, lo, npy):
    arr = np.round(load_exr(hi)) * 16.0 + load_exr(lo) - 1000.0
    np.save(npy, arr.astype(np.float32))
    print("POS", npy, arr.shape, flush=True)


P = lambda s: os.path.join(OUTDIR, "%s_%s" % (TAG, s))
modes = ["night"] + (["day"] if DAY else [])
for m in modes:
    set_mode(m)
    render(P("beauty_%s.png" % m))
blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
solid.data.materials[0] = blackm
for m in modes:
    set_mode(m)
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    render(P("glow_%s.png" % m))
solid.data.materials[0] = TOON
# data passes: no transparent light (cones, holograms), hard pixel filter
for ob in ([beams_ob] if beams_ob else []) + holo_obs:
    ob.hide_render = True
bg.inputs["Color"].default_value = (0, 0, 0, 1)
scene.eevee.taa_render_samples = 1
scene.render.filter_size = 0.01
for kind in ("normal", "id"):
    bpy.context.view_layer.material_override = override_mat(kind)
    render(P("%s.png" % kind))
scene.view_settings.view_transform = "Raw" if "Raw" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"
for kind in ("pos_hi", "pos_lo"):
    bpy.context.view_layer.material_override = override_mat(kind)
    render(P(kind + ".exr"), fmt="OPEN_EXR")
save_pos_npy(P("pos_hi.exr"), P("pos_lo.exr"), P("pos.npy"))
bpy.context.view_layer.material_override = None

json.dump(dict(spots={k: list(v) for k, v in SPOTS.items()}, pools=POOLS, threats=THREATS,
               res=list(RES)), open(P("scene.json"), "w"), indent=1)
print("DONE", flush=True)
