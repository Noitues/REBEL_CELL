"""Aurelian HQ design pass: three massing thumbnails (quick Eevee, 960 x 540) from each concept's OVERVIEW camera.

"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python thumbs.py -- <out_dir> [A,B,C]

Every concept is the SAME canonical full-city colosseum (aurelian_landmark.canonical, spec 8.6b); they differ only in
where the route lives (aurelian_landmark.slots). The route is a MOCK 10-layer fixture graph (D10: more than 7 layers;
the last layer is THE CONCORDAT VAULT); the city around is a seeded block field (seed 7301) standing in for the map.
  A  CAVEA DESCENT     the four seating rings (far half, facing in) then the arena gates; the vault in the Rostrum
  B  LOGGIA AND CAVEA  up the outer colonnade (three loggia tiers + the attic, near face), round the rim walk, then
                       down the four seating rings (far half) to the vault in the Rostrum
  C  HYPOGEUM          two seating rings, then down through the cut-open arena floor into the hypogeum (three
                       underground rings); the vault at the bottom under the Rostrum column
Units: city BU (1 floor = 1.9 BU), x east, y north.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aurelian_landmark as AL

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
WHICH = (argv[1] if len(argv) > 1 else "A,B,C").split(",")
os.makedirs(OUT, exist_ok=True)

LAYERS = [2, 3, 3, 4, 3, 3, 4, 3, 2, 1]          # MOCK fixture: 10 layers, 28 nodes (the last = the vault)
TRAV = (0.86, 0.78, 0.62)
GILT = (0.788, 0.639, 0.353)
PORPHYRY = (0.23, 0.08, 0.15)
CAM = {"A": dict(bearing=200.0, pitch=42.0, lens=36.0, dist=112.0, tgt=(0.0, 4.0, 5.0)),
       "B": dict(bearing=200.0, pitch=40.0, lens=36.0, dist=116.0, tgt=(0.0, 2.0, 7.0)),
       "C": dict(bearing=200.0, pitch=54.0, lens=36.0, dist=110.0, tgt=(0.0, 4.0, 0.0))}


# ------------------------------------------------------------------ face accumulators (one mesh per accumulator)
class Acc:
    def __init__(self, name, kind):
        self.name, self.kind = name, kind
        self.v, self.f, self.c, self.e = [], [], [], []

    def face(self, pts, col, uv=None, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0, k=None):
        b = len(self.v)
        self.v += [tuple(p) for p in pts]
        self.f.append(tuple(range(b, b + len(pts))))
        self.c.append(tuple(col) + (1.0,))
        self.e.append(tuple(min(1.0, w * wl) for w in wc) + (1.0,) if k is None else tuple(col) + (1.0,))

    def flush(self, mat):
        if not self.f:
            return
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        a = me.attributes.new("col", "FLOAT_COLOR", "FACE")
        a.data.foreach_set("color", [x for c in self.c for x in c])
        a2 = me.attributes.new("emi", "FLOAT_COLOR", "FACE")
        a2.data.foreach_set("color", [x for c in self.e for x in c])
        me.validate()
        ob = bpy.data.objects.new(self.name, me)
        ob.data.materials.append(mat)
        bpy.context.scene.collection.objects.link(ob)


def mat_surface(name, rough=0.6, emit_k=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except (AttributeError, TypeError):
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    ae = nt.nodes.new("ShaderNodeAttribute")
    ae.attribute_name = "emi"
    nt.links.new(at.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit_k > 0:
        nt.links.new(ae.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit_k
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_emit(name, k):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except (AttributeError, TypeError):
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    nt.links.new(at.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = k
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def mat_city(name):
    """Dark facades with a noise-thresholded window field (object-space), a thumbnail stand-in for the map city."""
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except (AttributeError, TypeError):
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (4.2, 4.2, 2.6)
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 1.0
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.interpolation = "CONSTANT"
    cr.color_ramp.elements[0].color = (0, 0, 0, 1)
    cr.color_ramp.elements[1].position = 0.80
    cr.color_ramp.elements[1].color = (1.0, 0.72, 0.42, 1)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], vo.inputs["Vector"])
    nt.links.new(vo.outputs["Color"], cr.inputs["Fac"])
    nt.links.new(at.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(cr.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.4
    b.inputs["Roughness"].default_value = 0.7
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ the city_build primitives (same signatures)
def circle(cx, cy, r, n, a0=0.0, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def prism(acc, pts, z0, z1, col, ts=1.0, top=True, bottom=False, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0,
          top_col=None, uvs=(1.0, 1.0), vz0=None):
    n = len(pts)
    cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    tp = [(cx + (x - cx) * ts, cy + (y - cy) * ts) for (x, y) in pts]
    for i in range(n):
        j = (i + 1) % n
        a, c = pts[i], pts[j]
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (tp[j][0], tp[j][1], z1), (tp[i][0], tp[i][1], z1)], col, None,
                 wc, wl, wm, bid, wet)
    if top:
        acc.face([(x, y, z1) for (x, y) in tp], top_col or col)
    if bottom:
        acc.face([(x, y, z0) for (x, y) in reversed(pts)], col)


def box(acc, x0, y0, z0, x1, y1, z1, col, **kw):
    return prism(acc, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, col, **kw)


def cyl(acc, cx, cy, z0, z1, r, n, col, ts=1.0, **kw):
    return prism(acc, circle(cx, cy, r, n), z0, z1, col, ts=ts, **kw)


def bar(acc, p0, p1, w, col, **kw):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return
    d.normalize()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    s = d.cross(up).normalized() * (w / 2)
    t = d.cross(s).normalized() * (w / 2)
    cs = [s + t, -s + t, -s - t, s - t]
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(p0 + cs[i]), tuple(p0 + cs[j]), tuple(p1 + cs[j]), tuple(p1 + cs[i])], col)


def ring_line(acc, cx, cy, z, r, w, col, n=48, ry=None, **kw):
    ry = r if ry is None else ry
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        bar(acc, (cx + r * math.cos(t0), cy + ry * math.sin(t0), z), (cx + r * math.cos(t1), cy + ry * math.sin(t1), z),
            w, col)


def annulus(acc, cx, cy, z, r0, r1, col, n=48, k0=1.0, k1=1.0, z1=None, **kw):
    z1 = z if z1 is None else z1
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        acc.face([(cx + r0 * math.cos(t0), cy + r0 * k0 * math.sin(t0), z1), (cx + r0 * math.cos(t1), cy + r0 * k0 * math.sin(t1), z1),
                  (cx + r1 * math.cos(t1), cy + r1 * k1 * math.sin(t1), z), (cx + r1 * math.cos(t0), cy + r1 * k1 * math.sin(t0), z)],
                 col)


def sc(c, k):
    return tuple(v * k for v in c)


SPOTS = []
CONE = None


def spot_at(target, frm, col, power, cone=30.0):
    SPOTS.append(dict(loc=frm, tgt=target, col=col, power=power, cone=cone))


# ------------------------------------------------------------------ scene pieces
def city(acc, rs):
    """A dense block field to the lot edge (no belt, spec 8.2): 6 BU lots, a street every 4 lots."""
    for i in range(-24, 24):
        for j in range(-22, 22):
            if i % 4 == 0 or j % 4 == 0:
                continue
            x0, y0 = i * 6.0 + 0.6, j * 6.0 + 0.6
            cx, cy = x0 + 2.4, y0 + 2.4
            if (cx / 37.5) ** 2 + (cy / 31.5) ** 2 < 1.0:
                continue
            d = math.hypot(cx, cy)
            if d > 150:
                continue
            h = rs.uniform(5, 16) + (rs.uniform(0, 26) if rs.random() < 0.18 else 0) + 0.05 * max(0.0, d - 40)
            if CONE is not None:                         # spec 7 stand-in: buildings between the camera and the bowl -> stub
                ux, uy = CONE
                al, la = cx * ux + cy * uy, abs(-cx * uy + cy * ux)
                if al > 0 and la < 44.0:
                    h = min(h, 3.8)
            box(acc, x0, y0, 0, x0 + 4.8, y0 + 4.8, h, sc((0.10, 0.10, 0.12), rs.uniform(0.7, 1.2)))


def room(acc_body, acc_front, s, state):
    """A cut-open room box behind its front face (the kit cutaway, city units), front lit in its state colour."""
    w, d, h = s["size"]
    px, py, pz = s["pos"]
    nx, ny, _ = s["normal"]
    tx, ty = -ny, nx
    if s["kind"] == "vault":
        return
    corners = []
    for (a, b) in ((-1, 0), (1, 0), (1, -1), (-1, -1)):
        corners.append((px + tx * a * w / 2 + nx * b * d, py + ty * a * w / 2 + ny * b * d))
    prism(acc_body, corners, pz, pz + h, PORPHYRY)
    col = AL.state_colour(state)
    kk = {"walked": 0.5, "current": 1.0, "option": 1.0, "reach": 0.55}.get(state, 0.4)
    inset = 0.25
    f = [(px + tx * (w / 2 - inset) + nx * 0.03, py + ty * (w / 2 - inset) + ny * 0.03),
         (px - tx * (w / 2 - inset) + nx * 0.03, py - ty * (w / 2 - inset) + ny * 0.03)]
    acc_front.face([(f[0][0], f[0][1], pz + 0.25), (f[1][0], f[1][1], pz + 0.25), (f[1][0], f[1][1], pz + h - 0.25),
                    (f[0][0], f[0][1], pz + h - 0.25)][::-1], sc(col, kk))


def link_path(a, b):
    """Polyline between two room fronts: along the rim walk for the attic -> cavea crossing, else straight."""
    pa = Vector(a["pos"]) + Vector((0, 0, 1.2)) + Vector(a["normal"]) * 0.4
    pb = Vector(b["pos"]) + Vector((0, 0, 1.2)) + Vector(b["normal"]) * 0.4
    if a["kind"] == "attic" and b["kind"] == "cavea":
        r = AL.RING_R[0] + 0.1
        t0 = math.radians(a["t"])
        t1 = t0 + ((math.radians(b["t"]) - t0 + math.pi) % (2 * math.pi)) - math.pi      # the short way round
        zr = AL.RING_Z[0] + 0.6
        pts = [pa, Vector((pa.x, pa.y, zr))]
        for k in range(1, 24):
            t = t0 + (t1 - t0) * k / 24
            x, y = AL.ell(t, r)
            pts.append(Vector((x, y, zr)))
        pts += [Vector((pb.x, pb.y, zr)), pb]
        return pts
    if a["kind"] == b["kind"] and a["level"] == b["level"] and a["kind"] in ("cavea", "loggia", "attic", "hypogeum", "arena"):
        L = a["level"]
        r = math.hypot(a["pos"][0], a["pos"][1] / AL.BK)
        t0, t1 = math.radians(a["t"]), math.radians(b["t"])
        pts = []
        for k in range(13):
            t = t0 + (t1 - t0) * k / 12
            x, y = AL.ell(t, r)
            nr = AL.ell_normal(t, r, a["kind"] != "loggia" and a["kind"] != "attic")
            pts.append(Vector((x + nr[0] * 0.4, y + nr[1] * 0.4, a["pos"][2] + 1.2)))
        return pts
    return [pa, pb]


def hypogeum(SURF, NEON):
    """Concept C: the arena floor cut open; three underground rings stepping down to the vault under the column."""
    r4 = AL.RING_R[4]
    prism(SURF, circle(0, 0, r4, 64, ry=r4 * AL.BK)[::-1], -12.5, 3.0, (0.30, 0.25, 0.22), top=False)
    rs_ = [r4, r4 * 0.82, r4 * 0.60, r4 * 0.38]
    zs_ = [0.0, -2.2, -5.0, -7.8, -11.0]
    for k in range(3):
        annulus(SURF, 0, 0, zs_[k + 1], rs_[k + 1], rs_[k], (0.34, 0.27, 0.22), n=64, k0=AL.BK, k1=AL.BK)
        prism(SURF, circle(0, 0, rs_[k + 1], 64, ry=rs_[k + 1] * AL.BK), zs_[k + 2], zs_[k + 1], (0.22, 0.17, 0.15), top=False)
        ring_line(NEON, 0, 0, zs_[k + 1] + 0.05, rs_[k + 1], 0.3, GILT, n=64, ry=rs_[k + 1] * AL.BK)
        for m in range(24):                                    # the cell walls (radial)
            t = 2 * math.pi * m / 24
            x0, y0 = AL.ell(t, rs_[k + 1])
            x1, y1 = AL.ell(t, rs_[k])
            bar(SURF, (x0, y0, zs_[k + 1] + 1.3), (x1, y1, zs_[k + 1] + 1.3), 0.35, (0.40, 0.32, 0.26))
    annulus(SURF, 0, 0, -11.0, 0.0, rs_[3], (0.30, 0.10, 0.16), n=48, k0=AL.BK, k1=AL.BK)
    cyl(SURF, 0, 0, -11.0, 3.0, 2.0, 16, (0.80, 0.74, 0.62))           # the pier carrying the Rostrum
    for k in range(8):                                             # the vault: a lit drum at the bottom
        t = 2 * math.pi * k / 8
        bar(SURF, (3.4 * math.cos(t), 3.4 * math.sin(t), -11.0), (3.4 * math.cos(t), 3.4 * math.sin(t), -8.0), 0.4, TRAV)
    cyl(NEON, 0, 0, -10.8, -8.4, 2.4, 20, sc((1.0, 0.85, 0.5), 0.8))


def scene(concept):
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    SPOTS.clear()
    SURF, SMOOTH, NEON, LIT, CITY = (Acc("surf", "s"), Acc("smooth", "s"), Acc("neon", "e"), Acc("roomfront", "e"),
                                     Acc("city", "c"))
    RB = Acc("roombody", "s")
    S = AL.slots(LAYERS, concept)
    open_bays = []
    for s in S:
        if s["kind"] == "loggia":
            t = math.radians(s["t"])
            rate = math.hypot(AL.A * math.sin(t), AL.A * AL.BK * math.cos(t))
            dt = (s["size"][0] / 2 + 0.5) / rate
            open_bays.append((s["tier"], t - dt, t + dt))
    import types
    ctx = types.SimpleNamespace(SURF=SURF, SMOOTH=SMOOTH, NEON=NEON, prism=prism, box=box, cyl=cyl, bar=bar,
                                ring_line=ring_line, annulus=annulus, circle=circle, sc=sc, spot_at=spot_at,
                                district=dict(mat=[TRAV], sec=GILT), CP=None, hq=(0.0, 0.0), arena_open=(concept == "C"))
    AL.canonical(ctx, 0.0, 0.0, open_bays=open_bays)
    if concept == "C":
        hypogeum(SURF, NEON)
    global CONE
    b_ = math.radians(CAM[concept]["bearing"])
    CONE = (math.sin(b_), math.cos(b_))
    city(CITY, random.Random(7301))
    annulus(SURF, 0, 0, -0.02, AL.RING_R[4], 220.0, (0.035, 0.035, 0.04), n=64, k0=AL.BK, k1=1.0)     # ground (open over the arena)
    # mock route states: layer 0 walked, layer 1 node 1 current, its next-layer edges options, the rest ahead
    E = AL.fixture_edges(LAYERS)
    cur = (1, 1)
    opts = {b for (a, b) in E if a == cur}
    by = {(s["layer"], s["node"]): s for s in S}
    st = {}
    for s in S:
        key = (s["layer"], s["node"])
        st[key] = ("walked" if s["layer"] == 0 and s["node"] == 0 else "grey" if s["layer"] == 0 else
                   "current" if key == cur else "option" if key in opts else "reach")
    for s in S:
        room(RB, LIT, s, st[(s["layer"], s["node"])])
    for (a, b) in E:
        sa, sb = st[a], st[b]
        if sa == "grey":
            continue
        col = (AL.state_colour("walked") if (sa == "walked" and sb == "current") else
               AL.state_colour("option") if (a == cur) else sc(AL.state_colour("reach"), 0.45))
        pts = link_path(by[a], by[b])
        for p, q in zip(pts[:-1], pts[1:]):
            bar(NEON, tuple(p), tuple(q), 0.16, col)
    v = by[(len(LAYERS) - 1, 0)]
    ring_line(NEON, 0, 0, v["pos"][2] + 0.15, 5.9, 0.3, (1.0, 0.17, 0.2), n=48)       # the TARGET (red pencil stand-in)
    materials = dict(surf=mat_surface("m_surf", 0.55, 0.9), smooth=mat_surface("m_smooth", 0.4, 0.9),
                     neon=mat_emit("m_neon", 2.2), roomfront=mat_emit("m_front", 2.6), city=mat_city("m_city"),
                     roombody=mat_surface("m_rb", 0.6))
    for acc in (SURF, SMOOTH, NEON, LIT, CITY, RB):
        acc.flush(materials[acc.name])
    for i, sp in enumerate(SPOTS):
        ld = bpy.data.lights.new("spot%d" % i, "SPOT")
        ld.energy = sp["power"] * 0.12
        ld.color = sp["col"]
        ld.spot_size = math.radians(sp["cone"])
        ld.spot_blend = 0.8
        ob = bpy.data.objects.new("spot%d" % i, ld)
        ob.location = sp["loc"]
        ob.rotation_euler = (Vector(sp["tgt"]) - Vector(sp["loc"])).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.collection.objects.link(ob)
    if concept == "C":                                  # the hypogeum's own warm work light
        lp = bpy.data.lights.new("pit", "POINT")
        lp.energy, lp.color, lp.shadow_soft_size = 6.0e3, (1.0, 0.78, 0.5), 3.0
        ob = bpy.data.objects.new("pit", lp)
        ob.location = (0.0, 2.0, -3.0)
        bpy.context.scene.collection.objects.link(ob)
    ld = bpy.data.lights.new("moon", "SUN")
    ld.energy = 0.08
    ld.color = (0.6, 0.7, 1.0)
    ob = bpy.data.objects.new("moon", ld)
    ob.rotation_euler = (math.radians(55), 0, math.radians(140))
    bpy.context.scene.collection.objects.link(ob)
    return S


def render(concept, name):
    sc_ = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc_.render.engine = eng
            break
        except TypeError:
            continue
    try:
        sc_.eevee.taa_render_samples = 16
    except AttributeError:
        pass
    w = bpy.data.worlds.new("w")
    try:
        w.use_nodes = True
    except (AttributeError, TypeError):
        pass
    bg = w.node_tree.nodes.get("Background") or next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.010, 0.012, 0.022, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc_.world = w
    sc_.render.resolution_x, sc_.render.resolution_y = 960, 540
    sc_.render.resolution_percentage = 100
    sc_.view_settings.view_transform = "AgX"
    sc_.view_settings.exposure = 0.0
    c = CAM[concept]
    cd = bpy.data.cameras.new("cam")
    cd.lens = c["lens"]
    cd.sensor_width = 36.0
    cd.clip_end = 3000
    cam = bpy.data.objects.new("cam", cd)
    sc_.collection.objects.link(cam)
    sc_.camera = cam
    b, p = math.radians(c["bearing"]), math.radians(c["pitch"])
    tgt = Vector(c["tgt"])
    off = Vector((math.sin(b) * math.cos(p), math.cos(b) * math.cos(p), math.sin(p)))
    cam.location = tgt + off * c["dist"]
    cam.rotation_euler = (-off).to_track_quat("-Z", "Y").to_euler()
    sc_.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


for which in WHICH:
    S = scene(which)
    render(which, "thumb_" + which)
    print("rendered", which, "slots", len(S), flush=True)
