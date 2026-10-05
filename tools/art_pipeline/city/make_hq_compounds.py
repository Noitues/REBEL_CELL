"""ART-8 8p: build every HQ compound, its manifest and its layout table, then validate.

  python tools/art_pipeline/city/make_hq_compounds.py [corp ...] [--blender <exe>] [--no-build]

Per corporation (hq_compound_spec.CORPS):
  1. Blender 5.2 headless runs build_hq_compound.py -> <corp>_compound.glb (glTF 2.0, the primary export: 1D chose
     real-time Godot 3D) + build_info.json, in a scratch folder under %TEMP%;
  2. the .glb goes to assets/city/hq_compounds/<corp>/ with manifest.json (source scripts, commit, scripts hash,
     settings, origin, footprint, triangles, materials, anchors);
  3. content/city/hq_compounds/<corp>.tres (HqCompoundLayoutData) is written from the snapped anchors;
  4. validate_hq_compounds.py checks it all.
The layered-sprite export is dropped (DECISIONS "Art direction — ART-8 8p HQ compound prep").
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import hq_compound_spec as SPEC  # noqa: E402

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
ASSETS = os.path.join(ROOT, "assets", "city", "hq_compounds")
CONTENT = os.path.join(ROOT, "content", "city", "hq_compounds")
SCRATCH = os.path.join(os.environ.get("TEMP", os.path.join(ROOT, ".tmp")), "hq_compound_build")
VENDOR_SOURCE = "art-concepts-r43:docs/concepts/round43_hq_mechanics/scripts @ 36d1f34de595297787d06f4f0cc8075018a8b744"
MANIFEST_SCHEMA = "rebel_cell.art_export/1"
MATERIALS = {
    "hq_toon": "toon: 3-band ramp x vertex colour (tone baked); alpha = part bit -> ROUGHNESS (ink material edges)",
    "hq_lit": "floodlit toon: as hq_toon plus a warm self-light (heroes26 LIT)",
    "hq_neon": "emissive: vertex colour x neon gain (strips, trims, beacons)",
    "hq_win": "emissive windows: vertex colour x window gain",
    "hq_sign": "emissive diegetic signage (corp sign colour)",
    "hq_beam": "translucent light cone (emissive, alpha 0.22)",
}


def source_files():
    files = ["build_hq_compound.py", "hq_compound_spec.py", "make_hq_compounds.py", "validate_hq_compounds.py",
             "hq_compound_toon.gdshader"]
    files += ["vendor_r43/" + f for f in sorted(os.listdir(os.path.join(HERE, "vendor_r43"))) if f.endswith(".py")]
    return files


def scripts_sha256():
    h = hashlib.sha256()
    for f in source_files():
        h.update(f.encode())
        h.update(open(os.path.join(HERE, f), "rb").read().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.run(["git", "log", "-1", "--format=%H", "--", "tools/art_pipeline/city"], cwd=ROOT,
                              capture_output=True, text=True, timeout=30).stdout.strip() or "uncommitted"
    except Exception:
        return "unknown"


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def gd(p):
    if p is None:
        return None
    x, y, z = SPEC.to_godot(p)
    return [round(x, 3), round(y, 3), round(z, 3)]


def build(corp, blender):
    out = os.path.join(SCRATCH, corp)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    log = os.path.join(SCRATCH, "blender_%s.log" % corp)
    with open(log, "w") as fh:
        r = subprocess.run([blender, "-b", "--factory-startup", "--python", os.path.join(HERE, "build_hq_compound.py"), "--", corp, out],
                           stdout=fh, stderr=subprocess.STDOUT, timeout=1200)
    if r.returncode != 0 or "DONE" not in open(log, encoding="utf-8", errors="replace").read():
        raise SystemExit("Blender failed for %s (see %s)" % (corp, log))
    return out


def write_manifest(corp, build_dir):
    info = json.load(open(os.path.join(build_dir, "build_info.json")))
    dst = os.path.join(ASSETS, corp)
    os.makedirs(dst, exist_ok=True)
    glb = os.path.join(dst, info["glb"])
    shutil.copyfile(os.path.join(build_dir, info["glb"]), glb)
    L = SPEC.layout(corp)
    A = info["anchors_blender"]
    bmin, bmax = info["bounds_blender"]["min"], info["bounds_blender"]["max"]
    gmin = [bmin[0], bmin[2], -bmax[1]]
    gmax = [bmax[0], bmax[2], -bmin[1]]
    cam_t, cam_o = L["camera"]
    man = {
        "schema": MANIFEST_SCHEMA,
        "asset": "hq_compound",
        "corp": corp,
        "source": {"script": "tools/art_pipeline/city/build_hq_compound.py", "spec": "tools/art_pipeline/city/hq_compound_spec.py",
                   "driver": "tools/art_pipeline/city/make_hq_compounds.py", "vendor": VENDOR_SOURCE, "commit": git_commit(),
                   "scripts_sha256": scripts_sha256()},
        "settings": {"blender": info["blender"], "state": info["state"], "units": "1 BU = 1 m", "up": "+Y (glTF; Blender (x, y, z) -> (x, z, -y))",
                     "tone": list(SPEC.TONE), "ramp_tint": list(SPEC.RAMP_TINT[corp]), "pitch_deg": SPEC.PITCH_DEG, "yaw_deg": SPEC.YAW_DEG,
                     "reference_camera": {"target": gd(cam_t), "ortho": cam_o}, "normals": "none (facet normal from screen derivatives)",
                     "layered_sprites": "dropped: 1D chose real-time Godot 3D"},
        "origin": "the compound's ground centre (plaza centre) at (0, 0, 0); place it on the HQ lot's centre",
        "footprint": {"min": [round(v, 3) for v in gmin], "max": [round(v, 3) for v in gmax],
                      "size": [round(gmax[k] - gmin[k], 3) for k in range(3)]},
        "files": [{"path": info["glb"], "kind": "gltf", "bytes": os.path.getsize(glb), "sha256": sha256(glb)}],
        "triangles": info["triangles"],
        "materials": {k: v for k, v in MATERIALS.items() if k[3:] in info["triangles"]},
        "anchors": {"frame": "godot", "lift": A["lift"], "server_name": L["server_name"],
                    "layers": [[gd(p) for p in row] for row in A["rows"]], "central_server": gd(A["server"]),
                    "entry": gd(A["entry"])},
        "slot_surfaces": info["slot_surfaces"],
        "validator": "python tools/art_pipeline/city/validate_hq_compounds.py; tools/validate_content.gd (manifest + files)",
    }
    json.dump(man, open(os.path.join(dst, "manifest.json"), "w", newline="\n"), indent=1)
    return man


def v3(p):
    return "Vector3(%s, %s, %s)" % tuple(repr(float(x)) for x in p)


def write_tres(corp, man):
    os.makedirs(CONTENT, exist_ok=True)
    A = man["anchors"]
    flat = [c for row in A["layers"] for p in row for c in p]
    lines = [
        '[gd_resource type="Resource" script_class="HqCompoundLayoutData" load_steps=2 format=3]',
        "",
        '[ext_resource type="Script" path="res://scripts/data/hq_compound_layout_data.gd" id="1"]',
        "",
        "[resource]",
        'script = ExtResource("1")',
        'id = &"hq_compound_%s"' % corp,
        'corporation_id = &"%s"' % corp,
        'asset_dir = "res://assets/city/hq_compounds/%s"' % corp,
        "slots_per_layer = %d" % SPEC.SLOTS,
        "layer_slots = PackedVector3Array(%s)" % ", ".join(repr(float(c)) for c in flat),
        "central_server = %s" % v3(A["central_server"]),
        "entry = %s" % v3(A["entry"]),
        "",
    ]
    open(os.path.join(CONTENT, corp + ".tres"), "w", newline="\n").write("\n".join(lines))


def main(argv):
    blender = BLENDER
    corps, build_it = [], True
    i = 0
    while i < len(argv):
        if argv[i] == "--blender":
            blender = argv[i + 1]
            i += 1
        elif argv[i] == "--no-build":
            build_it = False
        else:
            corps.append(argv[i])
        i += 1
    corps = corps or SPEC.CORPS
    for corp in corps:
        bd = build(corp, blender) if build_it else os.path.join(SCRATCH, corp)
        man = write_manifest(corp, bd)
        write_tres(corp, man)
        print("%s: %d bytes, %s tris" % (corp, man["files"][0]["bytes"], sum(man["triangles"].values())), flush=True)
    import validate_hq_compounds
    return validate_hq_compounds.main([])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
