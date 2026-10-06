"""ART-3 6w: the raid's building nodes as uplink pads (v1), exported from the round 40 concept's own drawing code.
Blender 5.2 headless.

  blender -b --factory-startup --python tools/art_pipeline/raid/build_uplink_pads_v1.py -- <outdir>
      -> <outdir>/uplink_pads.glb + <outdir>/uplink_pads.info.json
  python tools/art_pipeline/raid/build_uplink_pads_v1.py assemble <outdir>
      -> assets/raid/uplink/uplink_pads.glb + manifest.json (rebel_cell.art_export/1, as 5e's roof props)

Bible v2 4.8 / 4.1: "Risers run from the socket into the node's building and up the facade to a B uplink pad on the
roof (the pad face is the socket's twin; a lime beacon mast at its corner)". The concept draws them in
unified40.py lines 404-434 ("the Cell's nodes: uplink pads + risers (raid language B)"), vendored unchanged by 5e in
tools/art_pipeline/city/concept_r40/ (ported from art-pass ace98b9) on concept_r31's target_corps.py primitives
(box, strip, beam). This script runs exactly those lines (drawing code unchanged; designer ruling 2026-10-05), in
two pieces the game stands on each node building:

  * `uplink_pad` = lines 420-428 (the dark pad box with its lime trim, the mast and its lime cap) on a square
    stand-in footprint whose pad half-size `hs` comes out as 1 BU, at roof height 0, centred on the origin: the
    game scales it in X / Z to the node building's own `hs` (0.32 x its footprint's shorter side, the concept's
    rule) and stands it on the roof top;
  * `uplink_riser` = lines 430-433 (three lime traces up the corner facing the socket) with the corner at the
    origin and the roof at RISER_H: the game stands it on the building's corner nearest the node's street and
    scales it in Y to the roof height.

Export per art_export/1 (5e / 8p): one node per piece, its toon and neon parts as one mesh with two materials
(lm_toon, lm_neon), COLOR_0 = linear base colour x the per-face tone jitter, alpha = the part value; no normals.
"""
import json
import os
import sys
import textwrap

_HERE = os.path.dirname(os.path.abspath(__file__))
_CITY = os.path.join(_HERE, "..", "city")
VENDOR = os.path.join(_CITY, "concept_r40", "unified40.py")
PRIMS = os.path.join(_CITY, "concept_r31", "target_corps.py")
# unified40.py line ranges (1-based, inclusive) and the text each starts with (the vendored file is unchanged).
BLOCKS = {
    "uplink_pad": (420, 428, "xs, ys = [p[0] for p in q], [p[1] for p in q]"),
    "uplink_riser": (430, 433, "k = min(range(len(q)), key=lambda i: math.hypot(q[i][0] - sx, q[i][1] - sy))"),
}
# The stand-in footprint: a square whose pad half-size is 1 BU (hs = side x 0.32).
HALF_SIDE = 1.0 / 0.64
RISER_H = 10.0
SEED = 4041
TONE = (0.86, 1.12)
PART_ALPHA = (0.55, 1.0)
LIME = (0.83, 1.0, 0.0)
SCRIPTS = ["tools/art_pipeline/raid/build_uplink_pads_v1.py", "tools/art_pipeline/city/concept_r40/unified40.py",
           "tools/art_pipeline/city/concept_r31/target_corps.py"]
PIECES = ["uplink_pad", "uplink_riser"]


def block(lines, rng_):
    a, b, head = rng_
    src = "\n".join(lines[a - 1:b])
    if not src.strip().startswith(head):
        raise SystemExit("unified40.py changed: line %d does not start with %r" % (a, head))
    return textwrap.dedent(src)


def blender_main(outdir):
    sys.argv = [sys.argv[0], "--", "meridian_regular", outdir]
    src = open(PRIMS, encoding="utf-8-sig").read().splitlines()
    g = globals()
    exec("\n".join(src[0:314]), g)  # target_corps: scene reset, Acc, box, beam, strip, rid, materials
    g["rng"] = __import__("random").Random(SEED)
    u40 = open(VENDOR, encoding="utf-8-sig").read().splitlines()
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

    a = HALF_SIDE
    stand_in = {
        "uplink_pad": dict(c=(0.0, 0.0), q=[(-a, -a), (a, -a), (a, a), (-a, a)], zt=0.0, sx=0.0, sy=-10.0),
        "uplink_riser": dict(c=(0.0, 0.0), q=[(0.0, 0.0)], zt=RISER_H, sx=0.0, sy=0.0),
    }
    info = {"pieces": {}, "blender": bpy.app.version_string, "seed": SEED, "riser_h": RISER_H, "pad_half": 1.0}
    keep = []
    for piece in PIECES:
        g["SOLID"], g["NEON"] = Acc("solid"), Acc("neon")
        g["CNEON"] = g["NEON"]  # unified40's city neon accumulator is the neon role
        g["LIME"] = LIME
        g.update(stand_in[piece])
        exec(block(u40, BLOCKS[piece]), g)
        parts = [o for o in (to_object(g["SOLID"], "solid", piece + "__solid"), to_object(g["NEON"], "neon", piece + "__neon")) if o]
        bpy.ops.object.select_all(action="DESELECT")
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        if len(parts) > 1:
            bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active
        o.name = piece
        o.data.name = piece
        xs = [v.co.x for v in o.data.vertices]
        ys = [v.co.y for v in o.data.vertices]
        zs = [v.co.z for v in o.data.vertices]
        info["pieces"][piece] = {"min": [min(xs), min(zs), -max(ys)], "max": [max(xs), max(zs), -min(ys)],
                                 "triangles": sum(len(p.vertices) - 2 for p in o.data.polygons),
                                 "materials": [m.name for m in o.data.materials]}
        keep.append(o)
    for o in list(bpy.data.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    path = os.path.join(outdir, "uplink_pads.glb")
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
    with open(os.path.join(outdir, "uplink_pads.info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    print("EXPORTED", path, os.path.getsize(path), flush=True)
    print("DONE", flush=True)


def assemble(outdir):
    import hashlib
    import shutil
    import subprocess
    root = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
    dst = os.path.join(root, "assets", "raid", "uplink")
    os.makedirs(dst, exist_ok=True)
    shutil.copyfile(os.path.join(outdir, "uplink_pads.glb"), os.path.join(dst, "uplink_pads.glb"))
    info = json.load(open(os.path.join(outdir, "uplink_pads.info.json"), encoding="utf-8"))
    h = hashlib.sha256()
    for s in SCRIPTS:
        h.update(s.encode("utf-8"))
        h.update(open(os.path.join(root, s), "rb").read().replace(b"\r\n", b"\n"))
    glb = os.path.join(dst, "uplink_pads.glb")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    man = {
        "schema": "rebel_cell.art_export/1",
        "asset": "uplink_pads",
        "about": "ART-3 6w raid uplink pads + risers (bible 4.8 raid language B). Built by "
                 "tools/art_pipeline/raid/build_uplink_pads_v1.py; do not edit by hand.",
        "source": {"script": SCRIPTS[0], "vendor": "art-concepts-r43:docs/concepts/round40_city_unified/scripts/unified40.py @ ace98b9 "
                   "(tools/art_pipeline/city/concept_r40/, lines 420-428 pad and 430-433 riser) on target_corps.py (concept_r31/)",
                   "scripts": SCRIPTS, "commit": commit, "scripts_sha256": h.hexdigest()},
        "settings": {"blender": info["blender"], "version": "v1", "units": "1 BU = 1 m", "seed": info["seed"],
                     "up": "+Y (glTF; Blender (x, y, z) -> (x, z, -y))", "tone": list(TONE), "part_alpha": list(PART_ALPHA),
                     "normals": "none (facet normal from screen derivatives)", "pad_half": info["pad_half"],
                     "riser_h": info["riser_h"], "exporter": info["exporter_settings"]},
        "origin": "uplink_pad: the pad's centre on the roof at (0, 0, 0), pad half-size 1 BU (scale X / Z to the "
                  "building's); uplink_riser: the building's corner on the ground, roof at riser_h (scale Y)",
        "materials": ["lm_toon", "lm_neon"],
        "pieces": info["pieces"],
        "files": [{"path": "uplink_pads.glb", "bytes": os.path.getsize(glb), "sha256": hashlib.sha256(open(glb, "rb").read()).hexdigest()}],
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
