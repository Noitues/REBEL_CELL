"""ART-8 8p: one corporation's HQ compound, static, as glTF 2.0 (Blender 5.2 headless).

  blender -b --factory-startup --python build_hq_compound.py -- <corp> <outdir>
    -> <outdir>/<corp>_compound.glb + <outdir>/build_info.json (bounds, triangles, anchors, slot surface check)

The model is the locked round 43 compound (art-concepts-r43 docs/concepts/round43_hq_mechanics/scripts, vendored
unchanged in vendor_r43/, the same exec chain as that round's hq_scene.py) with every moving part held at rest or left
out until G12: Meridian's crane stands parked (portal, keep house, boom level; no trolley load) and no train runs;
Solace's helix does not turn; Halcyon's eye stands at its still angle without the searchlight cone; Orbital's silo
doors are shut and the rocket is down; DISPATCH (REBEL_CELL) is the static base. The surrounding city is NOT built
(ART-5's CityModel draws it): the compound stops at its plaza.

Look (spike 1D, real time): faceted Cv2 geometry, flat facets. Each vertex colour is the concept's face colour times
its per-triangle tone jitter (target_corps.mat_toon: 0.86..1.12), linear; alpha carries a part-id bit (0 / 1) that
the toon shader writes to ROUGHNESS so the spike's ink pass draws material edges between parts. Materials carry the
role in their name (hq_toon, hq_lit, hq_neon, hq_win, hq_sign, hq_beam); hq_compound_toon.gdshader shades them.
No normals are exported: the toon shader takes the facet normal from screen derivatives, as the spike does.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "vendor_r43")
sys.path.insert(0, HERE)
import hq_compound_spec as SPEC  # noqa: E402

_args = sys.argv[sys.argv.index("--") + 1:]
CORP_ARG, OUT_ARG = _args[0], os.path.abspath(_args[1])
os.makedirs(OUT_ARG, exist_ok=True)
os.environ["COMPOUND"] = ""  # the static compound: no per-frame moving parts
sys.argv = [sys.argv[0], "--", CORP_ARG + "_hq", OUT_ARG, "static"]

# ------------------------------------------------------------------ the round 43 exec chain (hq_scene.py preamble)
_HERE = V
_SRC = open(os.path.join(V, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials (defines CORP, KIND, scene, Acc, SOLID, NEON, WIN, ...)

JOB = CORP + "_hq"
VIEW = "static"
STATE = "dispatch" if CORP == "rebel_cell" else ""
rng = random.Random(2525 + sum(map(ord, JOB)))
LAY = {"centre": [0.0, 0.0], "terr": {}, "buildings": [], "hqs": {}, "radius": 0}
CX, CY = 0.0, 0.0
U = 6.0
KH = U / 41.64


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 27.5
exec(open(os.path.join(V, "heroes24.py"), encoding="utf-8-sig").read())
KN = CORP_KNOBS[CORP]
exec("\n".join(_SRC[504:682]))  # container(), ziggurat(), depot()
for _f in ("heroes25.py", "heroes26.py", "heroes27.py"):
    exec(open(os.path.join(V, _f), encoding="utf-8-sig").read())
if CORP == "meridian":
    for _f in ("heroes28.py", "heroes29.py", "heroes30.py", "heroes31.py"):
        exec(open(os.path.join(V, _f), encoding="utf-8-sig").read())
if "MOVE_FRAMES" not in globals():
    MOVE_FRAMES = []
exec(open(os.path.join(V, "heroes42.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(V, "heroes43.py"), encoding="utf-8-sig").read())


def build_at(fn, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    """hq_scene.build_at: run a builder around the origin, then scale and move what it added."""
    accs = [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values())
    before = {id(a): len(a.bm.verts) for a in accs}
    objs0 = set(bpy.data.objects)
    fn()
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for acc in [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values()):
        m = before.get(id(acc), 0)
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            x0, y0 = v.co.x * s, v.co.y * s
            v.co.x = x0 * cr - y0 * sr + dx
            v.co.y = x0 * sr + y0 * cr + dy
            v.co.z *= s
    for o in set(bpy.data.objects) - objs0:
        x0, y0 = o.location[0] * s, o.location[1] * s
        o.location = (x0 * cr - y0 * sr + dx, x0 * sr + y0 * cr + dy, o.location[2] * s)
        o.rotation_euler = (o.rotation_euler[0], o.rotation_euler[1], o.rotation_euler[2] + math.radians(rot))
        o.scale = (s, s, s)


# ------------------------------------------------------------------ static compounds (moving parts at rest / out)
def meridian_static():
    fort_v29_static()
    bolts_ladders_catwalks()
    faceted_water(S30 + 6.2, S30 + 11.5)
    rail_yard()
    build_at(lambda: crane_dyn(0.0, 6.0, 14.0, False), rot=90.0)  # the keep, parked: boom level, spreader up, no load


STATIC = {"meridian": meridian_static, "solace": solace43, "halcyon": civic_core26,
          "orbital": lambda: orbital_parts(0.0, 0.0), "rebel_cell": rebel_base}
STATIC[CORP]()

# ------------------------------------------------------------------ objects, vertex colours, role materials
import bmesh  # noqa: E402,F811
import numpy as np  # noqa: E402

TONE = (0.86, 1.12)


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


for o in list(bpy.data.objects):  # sign text (Blender fonts) -> meshes, coloured as the sign material
    if o.type == "FONT":
        bpy.context.view_layer.objects.active = o
        for s in bpy.context.view_layer.objects.selected:
            s.select_set(False)
        o.select_set(True)
        bpy.ops.object.convert(target="MESH")
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.data.materials and o.data.materials[0] == SIGNM:
        me = o.data
        n = sum(len(p.loop_indices) for p in me.polygons)
        ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
        c = tuple(KN["sign"]) + (0.0,)
        ca.data.foreach_set("color", list(c) * n)
        me.materials[0] = role_mat("sign")
        o.name = "hq_%s_sign_%s" % (CORP, o.name)

objs = []
for acc, role, toned in ((SOLID, "toon", True), (LIT, "lit", True), (NEON, "neon", False), (WIN, "win", False),
                         (BEAM, "beam", False)):
    objs.append(acc_object(acc, role, "hq_%s_%s" % (CORP, role), toned))
if EYE_ACC:  # Halcyon's eye: its own nodes (pivot = the pylon axis) so G12 can turn it; the searchlight cone stays out
    EYE_ACC.pop("beam").bm.free()
    eye_objs = [acc_object(EYE_ACC["solid"], "toon", "hq_%s_eye_toon" % CORP, True),
                acc_object(EYE_ACC["neon"], "neon", "hq_%s_eye_neon" % CORP, False)]
    for o in eye_objs:
        if o is not None:
            o.rotation_euler = (0.0, 0.0, math.radians(28.0))  # hq_scene EYE_STILL: the still / combat angle
for g in MOVE_FRAMES:  # unused per-frame accumulators of the vendored rounds
    for a in g.values():
        try:
            a.bm.free()
        except Exception:
            pass
for o in list(bpy.data.objects):  # nothing else: no lights, cameras or stray empties in the export
    if o.type not in ("MESH",):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ anchors: every slot must sit on a surface
from mathutils import Vector  # noqa: E402

L = SPEC.layout(CORP)
dg = bpy.context.evaluated_depsgraph_get()


def surface(p):
    hit, loc, _n, _i, _o, _m = scene.ray_cast(dg, Vector((p[0], p[1], p[2] + 3.0)), Vector((0, 0, -1)), distance=60.0)
    return round(loc.z, 3) if hit else None


LIFT = 0.3  # an anchor stands this far above the surface it snaps to


def snap(p):
    """The slot on the model: the first surface under (x, y, nominal z + 3), lifted; None when there is none."""
    s = surface(p)
    return None if s is None else [round(p[0], 3), round(p[1], 3), round(s + LIFT, 3)]


checks = []
anchors = []
for li, row in enumerate(L["rows"]):
    out_row = []
    for si, p in enumerate(row):
        a = snap(p)
        checks.append(dict(layer=li + 1, slot=si, z=p[2], surface=None if a is None else round(a[2] - LIFT, 3)))
        out_row.append(a)
    anchors.append(out_row)
srv_anchor = snap(L["server"])
entry_anchor = [round(c, 3) for c in L["entry"]]  # the street outside the compound: not snapped (no city here)
srv_surface = None if srv_anchor is None else round(srv_anchor[2] - LIFT, 3)

# ------------------------------------------------------------------ bounds, triangles, export
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
glb = os.path.join(OUT_ARG, "%s_compound.glb" % CORP)
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, use_selection=False, export_apply=True,
                          export_texcoords=False, export_normals=False, export_vertex_color="ACTIVE",
                          export_all_vertex_colors=False, export_materials="EXPORT", export_extras=True,
                          export_cameras=False, export_lights=False, export_animations=False)
info = dict(corp=CORP, glb=os.path.basename(glb), bounds_blender=dict(min=[round(x, 3) for x in mins], max=[round(x, 3) for x in maxs]),
            triangles=tris, slot_surfaces=checks, server_surface=srv_surface, state=STATE or "static",
            anchors_blender=dict(rows=anchors, server=srv_anchor, entry=entry_anchor, lift=LIFT),
            blender=bpy.app.version_string)
json.dump(info, open(os.path.join(OUT_ARG, "build_info.json"), "w"), indent=1)
print("DONE", CORP, json.dumps(tris), flush=True)
