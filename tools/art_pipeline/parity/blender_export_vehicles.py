"""M14 asset parity: the City Grid vehicles (ART-5 5c) from the concept round's own Blender builders.

Run inside Blender 5.2 (headless):

    blender -b --factory-startup --python tools/art_pipeline/parity/blender_export_vehicles.py -- <concepts> <out_dir>

`<concepts>` is the `docs/concepts` folder of an extraction of tag `art-concepts-r43`. The concept modules
build a whole city when imported, so this wrapper takes the builder functions out of their source with
`ast` and runs them verbatim (drawing code unchanged; designer ruling 2026-10-05):

  * `round38_city_unified/scripts/unified38.py : flying_car` (the CLOSE sky-lane car) on the accumulator
    classes of `target_corps.py` (`Acc`, `rid`, `box`, ...);
  * `round20_raid_world/scripts/district20.py : heli_geo` and `drone_geo` (the Heat chopper and drone) on
    that module's own `Acc`, `box`, `obox`, `beam`, `ring`.

Each accumulator's faces become one mesh. Vertex colour (COLOR_0) = the face colour the builder gave it, and
the second UV layer's U carries the part id the game's sky_car shader reads (flying car only: 0 body,
1 lane stripe, 2 head light, 3 tail light, 4 cabin, 5 under-glow; classified from the builder's own face
colours, the lane colour being a sentinel). Writes `flying_car.glb`, `chopper.glb` (objects `body`, `neon`,
`blades`) and `drone.glb` (objects `body`, `neon`) plus `vehicles_manifest.json`.
"""
from __future__ import annotations

import ast
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
CONCEPTS, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)

LANE_SENTINEL = (0.31, 0.69, 0.91)
BLADE_COL = (0.1, 0.1, 0.12)


def pick(path: str, names: list[str]) -> ast.Module:
    """The top-level defs / classes / simple assigns of the file at `path` whose name is in `names`."""
    tree = ast.parse(open(path, encoding="utf-8-sig").read())
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            keep.append(node)
    got = {n.name for n in keep}
    missing = set(names) - got
    if missing:
        raise SystemExit("missing in %s: %s" % (path, sorted(missing)))
    mod = ast.Module(body=keep, type_ignores=[])
    return ast.fix_missing_locations(mod)


def run(path: str, names: list[str], ns: dict) -> None:
    exec(compile(pick(path, names), path, "exec"), ns)


def base_ns(rng_seed: int) -> dict:
    return {"math": math, "random": random, "bmesh": bmesh, "bpy": bpy, "Vector": Vector,
            "rng": random.Random(rng_seed), "vrng": random.Random(rng_seed), "FRNG": random.Random(1901), "OLD": False}


def close(a, b, eps=0.02):
    return all(abs(a[i] - b[i]) < eps for i in range(3))


def mesh_of(acc, name: str, classify=None, keep=None, tone=None):
    """A Blender object from accumulator `acc`'s faces (those `keep(col)` accepts); loop colours + part-id UV.
    `tone` (a body colour): vertex colour = min(1, colour / tone), so the game's material albedo stays the tuned
    body tone and the concept's palette survives as relative tones."""
    bm = acc.bm
    faces = [f for f in bm.faces if keep is None or keep(tuple(f[acc.col])[:3])]
    if not faces:
        return None
    nb = bmesh.new()
    cl = nb.loops.layers.color.new("Col")
    uv0 = nb.loops.layers.uv.new("UVMap")
    uv1 = nb.loops.layers.uv.new("part")
    for f in faces:
        col = tuple(f[acc.col])[:3]
        nf = nb.faces.new([nb.verts.new(v.co) for v in f.verts])
        part = float(classify(col)) if classify else 0.0
        if tone is not None:
            col = tuple(min(1.0, col[i] / tone[i]) for i in range(3))
        for lp in nf.loops:
            lp[cl] = (col[0], col[1], col[2], 1.0)
            lp[uv0].uv = (0.0, 0.0)
            lp[uv1].uv = (part, 0.0)
    me = bpy.data.meshes.new(name)
    nb.to_mesh(me)
    nb.free()
    for p in me.polygons:
        p.use_smooth = False
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export(objs: list, path: str) -> None:
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_yup=True, export_apply=True)
    for extra in ({"export_vertex_color": "ACTIVE"}, {"export_active_vertex_color_when_no_material": True}):
        kw.update(extra)
    try:
        bpy.ops.export_scene.gltf(**kw)
    except TypeError:
        kw.pop("export_vertex_color", None)
        bpy.ops.export_scene.gltf(**kw)
    print("wrote", path)
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(me)


for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

manifest = {"schema": "rebel_cell.art_export/1", "asset": "city_vehicles",
            "source": {"tag": "art-concepts-r43", "drawing_code": "unchanged (ast-extracted builders run verbatim)",
                       "driver": "tools/art_pipeline/parity/blender_export_vehicles.py"}, "items": []}

# ---------------------------------------------------------------- the flying car (round 38 unified38.flying_car)
tc = os.path.join(CONCEPTS, "round38_city_unified", "scripts", "target_corps.py")
ns = base_ns(1936)
run(tc, ["Acc", "rid", "box"], ns)
ns["SOLID"], ns["CNEON"] = ns["Acc"]("solid"), ns["Acc"]("cneon")
run(os.path.join(CONCEPTS, "round38_city_unified", "scripts", "unified38.py"), ["flying_car"], ns)
ns["flying_car"]({"x": 0.0, "y": 0.0, "z": 0.0, "dx": 1.0, "dy": 0.0, "col": LANE_SENTINEL}, 1.0)


def car_part(col):
    if close(col, (1.0, 0.97, 0.85)):
        return 2
    if close(col, (1.0, 0.12, 0.1)):
        return 3
    if close(col, LANE_SENTINEL):
        return 1
    if close(col, tuple(v * 0.7 for v in LANE_SENTINEL)):
        return 5
    if close(col, (0.08, 0.1, 0.16)) or close(col, (0.1, 0.12, 0.2)):
        return 4
    return 0


car_solid = mesh_of(ns["SOLID"], "car_solid", car_part)
car_neon = mesh_of(ns["CNEON"], "car_neon", car_part)
# one object: join the two
for o in (car_solid, car_neon):
    o.select_set(True)
bpy.context.view_layer.objects.active = car_solid
bpy.ops.object.join()
car_solid.name = "flying_car"


def dump_tris(ob, path: str) -> None:
    """The mesh as plain triangles for CityMotionMeshes (a MultiMesh car needs per-vertex CUSTOM0, and the
    imported glb mesh cannot be read back headless): {"unit": ..., "tris": [[x,y,z, part] x3, ...]} in the
    concept's axes (nose +X, up +Z, Y = side). Positions rounded to 1e-4."""
    me = ob.data
    me.calc_loop_triangles()
    part = me.uv_layers["part"].data
    tris = []
    for t in me.loop_triangles:
        tri = []
        for k in range(3):
            v = me.vertices[t.vertices[k]].co
            tri.append([round(v.x, 4), round(v.y, 4), round(v.z, 4), int(part[t.loops[k]].uv[0] + 0.5)])
        tris.append(tri)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"schema": "rebel_cell.art_export/1", "made_by": "unified38.flying_car(c, s=1.0)",
                   "axes": "concept: nose +X, up +Z, side Y", "parts": "0 body, 1 lane, 2 head, 3 tail, 4 cabin, 5 glow",
                   "tris": tris}, fh, separators=(",", ":"))
        fh.write("\n")
    print("wrote", path, len(tris), "triangles")


dump_tris(car_solid, os.path.join(OUT, "flying_car_tris.json"))
export([car_solid], os.path.join(OUT, "flying_car.glb"))
manifest["items"].append({"file": "flying_car.glb", "made_by": "unified38.flying_car(c, s=1.0)",
                          "note": "UV2.u = part id (0 body, 1 lane stripe, 2 head, 3 tail, 4 cabin, 5 under-glow); concept axes: nose +X, up +Z"})

# ---------------------------------------------------------------- the chopper and drone (round 20 district20)
d20 = os.path.join(CONCEPTS, "round20_raid_world", "scripts", "district20.py")
for fn, name in (("heli_geo", "chopper"), ("drone_geo", "drone")):
    ns = base_ns(1801)
    ns.update({"RED": (1.0, 0.15, 0.12), "GREEN": (0.48, 0.88, 0.48), "HALCYON": (0.55, 0.48, 1.0), "BLUE": (0.16, 0.42, 1.0),
               "GUNMETAL": (0.20, 0.21, 0.25)})
    run(d20, ["Acc", "rid", "box", "obox", "beam", "ring", fn], ns)
    ns["SOLID"], ns["NEON"] = ns["Acc"]("solid"), ns["Acc"]("neon")
    ns[fn]()
    if name == "chopper":
        body = mesh_of(ns["SOLID"], "body", keep=lambda c: not close(c, BLADE_COL), tone=(0.52, 0.49, 0.70))
        blades = mesh_of(ns["SOLID"], "blades", keep=lambda c: close(c, BLADE_COL))
        neon = mesh_of(ns["NEON"], "neon", keep=lambda c: not close(c, (0.3, 0.3, 0.36)))
        ring = mesh_of(ns["NEON"], "blade_ring", keep=lambda c: close(c, (0.3, 0.3, 0.36)))
        objs = [o for o in (body, neon, blades, ring) if o]
    else:
        body = mesh_of(ns["SOLID"], "body", tone=(0.40, 0.38, 0.48))
        neon = mesh_of(ns["NEON"], "neon")
        objs = [o for o in (body, neon) if o]
    names = [o.name for o in objs]
    export(objs, os.path.join(OUT, name + ".glb"))
    manifest["items"].append({"file": name + ".glb", "made_by": "district20.%s()" % fn,
                              "note": "concept axes: nose +X, up +Z; objects: " + ", ".join(names)})

with open(os.path.join(OUT, "vehicles_manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=1)
    fh.write("\n")
