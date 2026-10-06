"""ART-8 8w: DISPATCH's HQ-run stage, the round 34 Tokyo canyon in its DISPATCH state, static, as glTF 2.0 (Blender 5.2).

  blender -b --factory-startup --python build_dispatch_canyon.py -- rebel_cell <outdir>
    -> <outdir>/rebel_cell_compound.glb + <outdir>/build_info.json (the same fields build_hq_compound.py writes)

DECISIONS "Open questions" (resolved 2026-10-05): DISPATCH's HQ run is set in the round 43 Tokyo canyon (round 43
dispatch43.py plays its run ideas on round 34's `canyon_dispatch.jpg`). The canyon is round 34's own builder: the
exec chain of round 34 hq34.py (target_corps.py lines 0-314, heroes24, the container block, heroes25, kit26.py,
street34.py; the first four are byte-identical to vendor_r43/, kit26 / street34 / cfg28 are vendored unchanged in
vendor_r34/ from art-pass d14b8f6) and its `canyon()` hero with DISP on, the still (FRAME -1). What hq34.py builds
round it (the game's city, the painted block, the other HQs) is ART-5's CityModel in the game, so it is not built.

Frame: the canyon's own frame (cfg28: local x across the street, local y along it from the camera end) put into the
Blender world as hq34.py does (+90 deg, `C2W`), with the origin moved to the canyon's midpoint on its centre line, so
the glTF sits on a lot point like a compound (glTF x = lot x, z = lot y). The alley floor (the city's street tile
colour, hq34 GROUND tiles) is added under the pavements, since the city under the canyon is not built here.

Look and export as build_hq_compound.py (art_export/1): vertex colour = face colour x tone, alpha = part bit, role
materials hq_toon / hq_neon / hq_win / hq_sign (signage text, its emission colour), no normals.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V43 = os.path.join(HERE, "vendor_r43")
V34 = os.path.join(HERE, "vendor_r34")
sys.path.insert(0, HERE)
sys.path.insert(0, V34)
import hq_compound_spec as SPEC  # noqa: E402
import cfg28  # noqa: E402

_args = sys.argv[sys.argv.index("--") + 1:]
CORP_ARG, OUT_ARG = _args[0], os.path.abspath(_args[1])
os.makedirs(OUT_ARG, exist_ok=True)
sys.argv = [sys.argv[0], "--", "rebel_cell_hq", OUT_ARG, "static"]

_SRC = open(os.path.join(V43, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials

JOB = "rebel_cell_hq"
VIEW = "close"
IDEA = "canyon"
STATE = "dispatch"
DISP = True
FRAME = -1           # the still (kit26.anim)
CAMSET = "combat"
CORP, KIND = "rebel_cell", "hq"
rng = random.Random(2727)  # hq34.py's seed
L_SPEC = SPEC.layout("rebel_cell")
CX, CY = L_SPEC["lot_centre"]  # the canyon's midpoint (lots): the export's origin
U = 6.0
KH = U / 41.64


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 27.5
LAY = {"centre": [CX, CY], "terr": {}, "buildings": [], "hqs": {}, "radius": 0}
exec(open(os.path.join(V43, "heroes24.py"), encoding="utf-8-sig").read())
KN = CORP_KNOBS[CORP]
exec("\n".join(_SRC[504:682]))  # container(), ziggurat(), depot()
exec(open(os.path.join(V43, "heroes25.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(V34, "kit26.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(V34, "street34.py"), encoding="utf-8-sig").read())

# ------------------------------------------------------------------ the hero (hq34.py "the hero", unchanged maths)
_ox, _oy = W(cfg28.Cfg.canyon_origin())
LCAN = cfg28.Cfg.canyon_len()
GAPS[:] = cfg28.Cfg.canyon_gaps()


def C2W(x, y):
    return (_ox - y, _oy + x)  # canyon frame -> world (+90 deg)


def canyon():
    tokyo_street(0.0, LCAN, seed=27, hmin=7, hfar=4, roof_screens=0.5)
    gr = random.Random(127)
    yb = LCAN + 3.0
    for sx in (-1, 1):
        beam((sx * 4.6, yb, 0), (sx * 4.6, yb, 13), 0.45, (0.2, 0.18, 0.2))
    screen((0, yb, 13), (1, 0, 0), (0, 0, 1), (0, -1, 0), 10, 6, "glyph" if not DISP else "text:REBEL_CELL",
           (0.35, 0.85, 1.0) if not DISP else DRED, (0.95, 0.93, 0.86) if not DISP else DRED2, 5, glitch=0.6 if DISP else 0.0)


build_xf(canyon, _ox, _oy, 90.0)

# The alley floor: hq34's city street tile colour (GROUND tiles), the canyon's length plus its head crossing.
FLOOR = (0.13, 0.13, 0.16)
_fa, _fb = C2W(-SW, -SPEC.CANYON_FLOOR_PAD), C2W(SW, LCAN + SPEC.CANYON_FLOOR_PAD)
SOLID.face([(_fa[0], _fa[1], 0.01), (_fb[0], _fa[1], 0.01), (_fb[0], _fb[1], 0.01), (_fa[0], _fb[1], 0.01)], FLOOR, rid())

# ------------------------------------------------------------------ objects, vertex colours, role materials (as 8p)
import bmesh  # noqa: E402,F811
import numpy as np  # noqa: E402

TONE = SPEC.TONE
# hq34.py's canyon grade for the sign colour: DISPATCH red, at 75 % (round 28 "a darker canyon").
SIGN_RGB = tuple(c * 0.75 for c in (1.0, 0.18, 0.20))


def role_mat(role):
    m = bpy.data.materials.get("hq_" + role) or bpy.data.materials.new("hq_" + role)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "Col"
    nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 1.0
    nt.links.new(bs.outputs[0], out.inputs[0])
    m["hq_role"] = role
    return m


def acc_object(acc, role, name, toned):
    if len(acc.bm.faces) == 0:
        acc.bm.free()
        return None
    me = bpy.data.meshes.new(name)
    acc.bm.to_mesh(me)
    acc.bm.free()
    nf = len(me.polygons)
    col = np.zeros(nf * 4, np.float32)
    me.attributes["col"].data.foreach_get("color", col)
    col = col.reshape(nf, 4)
    fj = np.zeros(nf, np.float32)
    me.attributes["fj"].data.foreach_get("value", fj)
    bid = np.zeros(nf * 4, np.float32)
    me.attributes["bid"].data.foreach_get("color", bid)
    bid = bid.reshape(nf, 4)
    rgb = col[:, :3] * (TONE[0] + fj[:, None] * (TONE[1] - TONE[0])) if toned else col[:, :3]
    part = (bid[:, 0] >= 0.5).astype(np.float32)
    face = np.concatenate([np.clip(rgb, 0.0, 4.0), part[:, None]], axis=1)
    lt = np.zeros(nf, np.int32)
    me.polygons.foreach_get("loop_total", lt)
    corner = np.repeat(face, lt, axis=0).ravel()
    for a in ("col", "fj", "bid"):
        me.attributes.remove(me.attributes[a])
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    ca.data.foreach_set("color", corner)
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = 0
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    me.materials.append(role_mat(role))
    return ob


def emission_rgb(mat):
    """The colour of an emissive signage material (target_corps.mat_flat / kit26.emis_mat), else the sign colour."""
    if mat is not None and mat != SIGNM and mat.node_tree is not None:
        for n in mat.node_tree.nodes:
            if n.type == "EMISSION":
                c = n.inputs["Color"].default_value
                return (c[0], c[1], c[2])
    return SIGN_RGB


SIGN_CURVE_RESOLUTION = 2  # as 5b's landmarks: the default 12 made the signage text heavier than the street
for o in list(bpy.data.objects):  # signage text (Blender fonts) -> meshes, coloured as their emissive material
    if o.type == "FONT":
        o.data.resolution_u = SIGN_CURVE_RESOLUTION
        bpy.context.view_layer.objects.active = o
        for s in bpy.context.view_layer.objects.selected:
            s.select_set(False)
        o.select_set(True)
        bpy.ops.object.convert(target="MESH")
n_sign = 0
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.data.materials and o.data.materials[0] is not None and "hq_role" not in o.data.materials[0]:
        me = o.data
        n = sum(len(p.loop_indices) for p in me.polygons)
        ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
        c = tuple(emission_rgb(me.materials[0])) + (0.0,)
        ca.data.foreach_set("color", list(c) * n)
        me.color_attributes.active_color = ca
        for k in range(len(me.materials)):
            me.materials[k] = role_mat("sign")
        o.name = "hq_rebel_cell_sign_%03d" % n_sign
        n_sign += 1

for acc, role, toned in ((SOLID, "toon", True), (NEON, "neon", False), (WIN, "win", False)):
    acc_object(acc, role, "hq_rebel_cell_%s" % role, toned)
for g in ("BEAM", "LIT"):  # the kit's other accumulators (unused by the canyon): exported only if they hold faces
    if g in globals():
        acc_object(globals()[g], "beam" if g == "BEAM" else "lit", "hq_rebel_cell_%s" % g.lower(), g == "LIT")
for o in list(bpy.data.objects):
    if o.type not in ("MESH",):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ anchors (the spec's canyon slots, snapped)
from mathutils import Vector  # noqa: E402

dg = bpy.context.evaluated_depsgraph_get()


def surface(p):
    hit, loc, _n, _i, _o, _m = scene.ray_cast(dg, Vector((p[0], p[1], p[2] + 3.0)), Vector((0, 0, -1)), distance=60.0)
    return round(loc.z, 3) if hit else None


LIFT = SPEC.ANCHOR_LIFT


def snap(p, seek=(0.0,)):
    """The slot on the model: the first surface under it; a slot over a gap tries the spec's offsets along the street
    (Blender -x is up the canyon) in order, so a rooftop slot lands on a roof."""
    for d in seek:
        q = (p[0] - d, p[1], p[2])
        s = surface(q)
        if s is not None:
            return [round(q[0], 3), round(q[1], 3), round(s + LIFT, 3)]
    return None


checks, anchors = [], []
for li, row in enumerate(L_SPEC["rows"]):
    out_row = []
    for si, p in enumerate(row):
        a = snap(p, L_SPEC["seek"] if p[2] >= L_SPEC["snap_below"] else (0.0,))
        checks.append(dict(layer=li + 1, slot=si, z=p[2], surface=None if a is None else round(a[2] - LIFT, 3)))
        out_row.append(a)
    anchors.append(out_row)
srv_anchor = snap(L_SPEC["server"])
entry_anchor = [round(c, 3) for c in L_SPEC["entry"]]
srv_surface = None if srv_anchor is None else round(srv_anchor[2] - LIFT, 3)

mins, maxs = [1e9] * 3, [-1e9] * 3
tris = {}
for o in bpy.data.objects:
    me = o.data
    me.calc_loop_triangles()
    role = me.materials[0].get("hq_role", "?") if me.materials else "?"
    tris[role] = tris.get(role, 0) + len(me.loop_triangles)
    mw = o.matrix_world
    for v in me.vertices:
        w = mw @ v.co
        for k in range(3):
            mins[k] = min(mins[k], w[k])
            maxs[k] = max(maxs[k], w[k])
glb = os.path.join(OUT_ARG, "rebel_cell_compound.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, use_selection=False, export_apply=True,
                          export_texcoords=False, export_normals=False, export_vertex_color="ACTIVE",
                          export_all_vertex_colors=False, export_materials="EXPORT", export_extras=True,
                          export_cameras=False, export_lights=False, export_animations=False)
info = dict(corp="rebel_cell", glb=os.path.basename(glb), bounds_blender=dict(min=[round(x, 3) for x in mins], max=[round(x, 3) for x in maxs]),
            triangles=tris, slot_surfaces=checks, server_surface=srv_surface, state="dispatch canyon (static)",
            anchors_blender=dict(rows=anchors, server=srv_anchor, entry=entry_anchor, lift=LIFT),
            blender=bpy.app.version_string)
json.dump(info, open(os.path.join(OUT_ARG, "build_info.json"), "w"), indent=1)
print("DONE", "rebel_cell canyon", json.dumps(tris), flush=True)
