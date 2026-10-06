"""ART-5 5e: the city's roof props (v1), exported from the round 40 concept's own drawing code. Blender 5.2 headless.

  blender -b --factory-startup --python build_roof_props_v1.py -- <outdir>
      -> <outdir>/roof_props.glb + <outdir>/roof_props.info.json
  python build_roof_props_v1.py assemble <outdir>
      -> assets/city/roof_props/roof_props.glb + manifest.json (rebel_cell.art_export/1, as 5b's landmarks)

Ported from art-pass ace98b9 docs/concepts/round40_city_unified/scripts/unified40.py (vendored unchanged in
concept_r40/; its primitives are target_corps.py, the same file as concept_r31/target_corps.py). The concept draws
the props inside city_building(): AC units / vents, a water tank on legs, an antenna with a red aircraft light and a
holo billboard panel standing on the roof (unified40.py lines 204-227). This script runs exactly those lines, one
prop per run, with a scripted stand-in for the building's seeded random `r` (every chance passes, `uniform` gives its
range's middle, `choice` the variant asked for, `randint` one) on a 20 x 20 BU roof at height 0, so each prop comes
out centred on the origin at its middle size: AC 0.9 x 0.7 x 0.55, tank r 0.8 on 0.9 legs, antenna 5 BU, billboard
5.75 BU wide. The game places them by the concept's own rules (CityRoofProps: ts >= 0.99, footprint > 2 BU, AC 0-2,
tank 18 %, antenna h > 22 at 45 %, billboard h > 14 at 16 %), scaling the antenna and the billboard to their drawn
size. The four billboard colours are four meshes (the concept's `hc` choice). Export per art_export/1 (8p / 5b):
one node per prop, its toon and neon parts as one mesh with two materials (lm_toon, lm_neon), COLOR_0 = linear base
colour x the per-face tone jitter, alpha = the part value; no normals.
"""
import json
import os
import sys
import textwrap

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
VENDOR = os.path.join(_HERE, "concept_r40", "unified40.py")
PRIMS = os.path.join(_HERE, "concept_r31", "target_corps.py")
# unified40.py line ranges (1-based, inclusive) and the text each starts with (the vendored file is unchanged).
BLOCKS = {
    "ac": (204, 206, "for _ in range(r.randint(0, 2)):"),
    "tank": (207, 211, "if r.random() < 0.18:"),
    "antenna": (212, 217, "if h > 22 and r.random() < 0.45:"),
    "billboard": (218, 227, "if h > 14 and r.random() < 0.16:"),
}
CYL36 = (231, 237, "def cyl36(")
BILLBOARD_COLOURS = 4
# The stand-in building the blocks draw on: a 20 x 20 BU flat roof at z 0, tall enough for every prop.
ROOF = dict(x0=-10.0, x1=10.0, y0=-10.0, y1=10.0, zt=0.0, h=30.0)
SEED = 4040
TONE = (0.86, 1.12)
PART_ALPHA = (0.55, 1.0)
RED = (1.0, 0.15, 0.12)
SCRIPTS = ["tools/art_pipeline/city/build_roof_props_v1.py", "tools/art_pipeline/city/concept_r40/unified40.py",
           "tools/art_pipeline/city/concept_r31/target_corps.py"]
PROPS = ["ac", "tank", "antenna"] + ["billboard_%d" % k for k in range(BILLBOARD_COLOURS)]
# The size each prop is drawn at (BU) and the concept's range the game scales it over.
DRAWN = {"antenna_h": [5.0, 3.0, 7.0], "billboard_w": [5.75, 4.0, 7.5]}


def block(lines, rng_):
    a, b, head = rng_
    src = "\n".join(lines[a - 1:b])
    if not src.strip().startswith(head):
        raise SystemExit("unified40.py changed: line %d does not start with %r" % (a, head))
    return textwrap.dedent(src)


class Scripted:
    """The building's random `r`, scripted: every chance passes, ranges give their middle, choice gives `pick`."""

    def __init__(self, pick=0):
        self.pick = pick

    def random(self):
        return 0.0

    def uniform(self, a, b):
        return (a + b) * 0.5

    def randint(self, a, b):
        return 1

    def choice(self, seq):
        return seq[self.pick % len(seq)]


def blender_main(outdir):
    sys.argv = [sys.argv[0], "--", "meridian_regular", outdir]
    src = open(PRIMS, encoding="utf-8-sig").read().splitlines()
    g = globals()
    exec("\n".join(src[0:314]), g)  # target_corps: scene reset, Acc, box, beam, rid, materials
    g["rng"] = __import__("random").Random(SEED)
    u40 = open(VENDOR, encoding="utf-8-sig").read().splitlines()
    exec(block(u40, CYL36), g)
    os.makedirs(outdir, exist_ok=True)
    export_mats = {}

    def mat(name):
        if name not in export_mats:
            m = bpy.data.materials.new(name)
            nt = m.node_tree
            nt.nodes.clear()
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
            ca = nt.nodes.new("ShaderNodeVertexColor")
            ca.layer_name = "COLOR_0"
            nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
            bs.inputs["Roughness"].default_value = 1.0
            nt.links.new(bs.outputs[0], out.inputs[0])
            export_mats[name] = m
        return export_mats[name]

    def part_alpha(bid):
        h = math.sin(bid[0] * 12.9898 + bid[1] * 78.233 + bid[2] * 37.719) * 43758.5453
        return PART_ALPHA[0] + (PART_ALPHA[1] - PART_ALPHA[0]) * (h - math.floor(h))

    def to_object(acc, role, name):
        if len(acc.bm.faces) == 0:
            acc.bm.free()
            return None
        o = acc.obj(mat("lm_toon" if role == "solid" else "lm_neon"))
        o.name = name
        me = o.data
        col, fj, bid = me.attributes["col"].data, me.attributes["fj"].data, me.attributes["bid"].data
        dst = me.color_attributes.new("COLOR_0", "FLOAT_COLOR", "CORNER")
        for p in me.polygons:
            c, t = col[p.index].color, fj[p.index].value
            k = (TONE[0] + (TONE[1] - TONE[0]) * t) if role == "solid" else 1.0
            rgba = (c[0] * k, c[1] * k, c[2] * k, part_alpha(bid[p.index].color))
            for li in p.loop_indices:
                dst.data[li].color = rgba
        for nm in ("col", "fj", "bid"):
            me.attributes.remove(me.attributes[nm])
        me.color_attributes.active_color = dst
        me.color_attributes.render_color_index = me.color_attributes.find("COLOR_0")
        return o

    info = {"props": {}, "blender": bpy.app.version_string, "seed": SEED, "drawn": DRAWN}
    keep = []
    for prop in PROPS:
        kind = prop.split("_")[0]
        g["SOLID"], g["NEON"] = Acc("solid"), Acc("neon")
        g["CNEON"] = g["NEON"]  # unified40's city neon accumulator is the neon role
        g["ANTS"] = []
        g["RED"] = RED
        g["r"] = Scripted(int(prop.split("_")[1]) if "_" in prop else 0)
        g.update(ROOF)
        exec(block(u40, BLOCKS[kind]), g)
        parts = [o for o in (to_object(g["SOLID"], "solid", prop + "__solid"), to_object(g["NEON"], "neon", prop + "__neon")) if o]
        bpy.ops.object.select_all(action="DESELECT")
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        if len(parts) > 1:
            bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active
        o.name = prop
        o.data.name = prop
        xs = [v.co.x for v in o.data.vertices]
        ys = [v.co.y for v in o.data.vertices]
        zs = [v.co.z for v in o.data.vertices]
        info["props"][prop] = {"min": [min(xs), min(zs), -max(ys)], "max": [max(xs), max(zs), -min(ys)],
                               "triangles": sum(len(p.vertices) - 2 for p in o.data.polygons),
                               "materials": [m.name for m in o.data.materials]}
        keep.append(o)
    for o in list(bpy.data.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    path = os.path.join(outdir, "roof_props.glb")
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    kw = dict(filepath=path, export_format="GLB", export_yup=True, export_apply=False, export_texcoords=False,
              export_normals=False, export_materials="EXPORT", export_cameras=False, export_lights=False,
              export_animations=False, export_extras=False)
    for k, v in (("export_vertex_color", "ACTIVE"), ("export_all_vertex_colors", False), ("export_tangents", False),
                 ("export_attributes", False), ("export_active_vertex_color_when_no_material", True),
                 ("export_shared_accessors", True)):
        if k in props:
            kw[k] = v
    bpy.ops.export_scene.gltf(**kw)
    info["exporter_settings"] = {k: v for k, v in kw.items() if k != "filepath"}
    with open(os.path.join(outdir, "roof_props.info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    print("EXPORTED", path, os.path.getsize(path), flush=True)
    print("DONE", flush=True)


def assemble(outdir):
    import hashlib
    import shutil
    import subprocess
    root = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
    dst = os.path.join(root, "assets", "city", "roof_props")
    os.makedirs(dst, exist_ok=True)
    shutil.copyfile(os.path.join(outdir, "roof_props.glb"), os.path.join(dst, "roof_props.glb"))
    info = json.load(open(os.path.join(outdir, "roof_props.info.json"), encoding="utf-8"))
    h = hashlib.sha256()
    for s in SCRIPTS:
        h.update(s.replace("tools/art_pipeline/city/", "", 1).encode("utf-8"))
        h.update(open(os.path.join(root, s), "rb").read().replace(b"\r\n", b"\n"))
    glb = os.path.join(dst, "roof_props.glb")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    man = {
        "schema": "rebel_cell.art_export/1",
        "asset": "roof_props",
        "about": "ART-5 5e roof props (bible 4.1: from raid zoom). Built by tools/art_pipeline/city/build_roof_props_v1.py; do not edit by hand.",
        "source": {"script": SCRIPTS[0], "vendor": "art-concepts-r43:docs/concepts/round40_city_unified/scripts/unified40.py @ ace98b9 "
                   "(concept_r40/, lines 204-227 and cyl36 231-237) on target_corps.py (concept_r31/)",
                   "scripts": SCRIPTS, "commit": commit, "scripts_sha256": h.hexdigest()},
        "settings": {"blender": info["blender"], "version": "v1", "units": "1 BU = 1 m", "seed": info["seed"],
                     "up": "+Y (glTF; Blender (x, y, z) -> (x, z, -y))", "tone": list(TONE), "part_alpha": list(PART_ALPHA),
                     "normals": "none (facet normal from screen derivatives)", "drawn": info["drawn"],
                     "exporter": info["exporter_settings"]},
        "origin": "each prop's roof contact centre at (0, 0, 0): stand it on a roof top",
        "materials": ["lm_toon", "lm_neon"],
        "props": info["props"],
        "files": [{"path": "roof_props.glb", "bytes": os.path.getsize(glb), "sha256": hashlib.sha256(open(glb, "rb").read()).hexdigest()}],
    }
    with open(os.path.join(dst, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print("ASSEMBLED", dst)


if __name__ == "__main__":
    if "--" in sys.argv:
        import math  # noqa: F401  (target_corps imports it too)
        import bpy  # noqa: F401
        blender_main(sys.argv[sys.argv.index("--") + 1])
    elif len(sys.argv) >= 3 and sys.argv[1] == "assemble":
        assemble(sys.argv[2])
    else:
        print(__doc__)
