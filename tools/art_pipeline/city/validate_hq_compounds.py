"""ART-8 8p validator hook: the HQ compound exports, their manifests and the layout tables agree.

  python tools/art_pipeline/city/validate_hq_compounds.py      (exit 0 = PASS)

Per corporation: manifest.json exists with the shared export fields; every listed file exists with its size and
sha256; the .glb is glTF 2.0 with vertex colours (COLOR_0), no normals and only the known role materials; the
scripts hash matches the current pipeline (a stale export fails); the anchors are LAYERS rows of SLOTS slots, each
snapped onto a surface of the model, sorted left to right on screen; and content/city/hq_compounds/<corp>.tres holds
the same anchors. tools/validate_content.gd repeats the manifest / file checks inside Godot.
"""
import hashlib
import json
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import hq_compound_spec as SPEC  # noqa: E402

MAX_GLB_BYTES = 6 * 1024 * 1024
FIELDS = ["schema", "asset", "corp", "source", "settings", "origin", "footprint", "files", "triangles", "materials", "anchors"]
ROLES = {"hq_toon", "hq_lit", "hq_neon", "hq_win", "hq_sign", "hq_beam"}


def glb_json(path):
    data = open(path, "rb").read()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67 or version != 2:
        return None
    clen, ctype = struct.unpack_from("<II", data, 12)
    if ctype != 0x4E4F534A:
        return None
    return json.loads(data[20:20 + clen].decode("utf-8"))


def check(corp, errors):
    def err(msg):
        errors.append("%s: %s" % (corp, msg))
    d = os.path.join(ROOT, "assets", "city", "hq_compounds", corp)
    mp = os.path.join(d, "manifest.json")
    if not os.path.isfile(mp):
        err("no manifest.json")
        return
    m = json.load(open(mp))
    for f in FIELDS:
        if f not in m:
            err("manifest has no '%s'" % f)
    if errors:
        return
    if m["corp"] != corp or m["asset"] != "hq_compound":
        err("manifest names %s / %s" % (m["corp"], m["asset"]))
    import make_hq_compounds
    if m["source"].get("scripts_sha256") != make_hq_compounds.scripts_sha256():
        err("stale export: the pipeline scripts changed since it was built (re-run make_hq_compounds.py)")
    for f in m["files"]:
        p = os.path.join(d, f["path"])
        if not os.path.isfile(p):
            err("missing file %s" % f["path"])
            continue
        b = open(p, "rb").read()
        if len(b) != f["bytes"] or hashlib.sha256(b).hexdigest() != f["sha256"]:
            err("%s does not match its manifest entry" % f["path"])
        if len(b) > MAX_GLB_BYTES:
            err("%s is %d bytes (budget %d)" % (f["path"], len(b), MAX_GLB_BYTES))
        if f["kind"] == "gltf":
            g = glb_json(p)
            if g is None or g.get("asset", {}).get("version") != "2.0":
                err("%s is not glTF 2.0 binary" % f["path"])
                continue
            for mesh in g.get("meshes", []):
                for prim in mesh["primitives"]:
                    a = prim["attributes"]
                    if "COLOR_0" not in a:
                        err("mesh %s has no COLOR_0" % mesh.get("name"))
                    if "NORMAL" in a:
                        err("mesh %s exports normals" % mesh.get("name"))
            names = {mat.get("name") for mat in g.get("materials", [])}
            if not names <= ROLES:
                err("unknown materials %s" % sorted(names - ROLES))
    A = m["anchors"]
    rows = A["layers"]
    if len(rows) != SPEC.LAYERS or any(len(r) != SPEC.SLOTS for r in rows):
        err("anchors are not %d rows of %d" % (SPEC.LAYERS, SPEC.SLOTS))
        return
    if A["central_server"] is None or A["entry"] is None or any(p is None for r in rows for p in r):
        err("an anchor found no surface under it")
        return
    for li, r in enumerate(rows):
        keys = [p[0] - p[2] for p in r]  # screen right = Blender +x +y = Godot +x -z
        if any(b <= a for a, b in zip(keys, keys[1:])):
            err("row %d is not left to right on screen" % (li + 1))
    ortho = float(m["settings"]["reference_camera"]["ortho"])
    named = [("%d%s" % (li + 1, "abcd"[si]), p) for li, r in enumerate(rows) for si, p in enumerate(r)] + [("server", A["central_server"])]
    scr = [(n, SPEC.screen_px(p, ortho)) for n, p in named]
    for i, (na, pa) in enumerate(scr):
        for nb, pb in scr[i + 1:]:
            dpx = math.dist(pa, pb)
            if dpx < SPEC.MIN_SLOT_PX:
                err("slots %s and %s are %.0f px apart at the reference framing (min %.0f)" % (na, nb, dpx, SPEC.MIN_SLOT_PX))
    for s in m.get("slot_surfaces", []):
        if s["surface"] is None or not (s["z"] - SPEC.SNAP_BELOW <= s["surface"] <= s["z"] + 3.0):
            err("layer %d slot %d: surface %s for nominal z %s" % (s["layer"], s["slot"], s["surface"], s["z"]))
    tp = os.path.join(ROOT, "content", "city", "hq_compounds", corp + ".tres")
    if not os.path.isfile(tp):
        err("no layout table %s" % os.path.relpath(tp, ROOT))
        return
    t = open(tp).read()
    mm = re.search(r"layer_slots = PackedVector3Array\(([^)]*)\)", t)
    vals = [float(x) for x in mm.group(1).split(",")] if mm else []
    flat = [c for r in rows for p in r for c in p]
    if len(vals) != len(flat) or any(abs(a - b) > 1e-3 for a, b in zip(vals, flat)):
        err("layout table slots differ from the manifest anchors")
    for key, field in (("central_server", "central_server"), ("entry", "entry")):
        mv = re.search(r"%s = Vector3\(([^)]*)\)" % field, t)
        v = [float(x) for x in mv.group(1).split(",")] if mv else []
        if len(v) != 3 or any(abs(a - b) > 1e-3 for a, b in zip(v, A[key])):
            err("layout table %s differs from the manifest" % field)
    if 'asset_dir = "res://assets/city/hq_compounds/%s"' % corp not in t:
        err("layout table asset_dir is not this folder")


def main(argv):
    corps = argv or SPEC.CORPS
    errors = []
    for corp in corps:
        check(corp, errors)
    for e in errors:
        print("  - " + e)
    print("HQ COMPOUNDS: " + ("PASS (%d)" % len(corps) if not errors else "FAIL (%d)" % len(errors)))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
