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
# ART-8 8w: DISPATCH's stage is round 34's Tokyo canyon (kit26 / street34 / cfg28 in vendor_r34/; the rest vendor_r43/).
VENDOR_SOURCE_CANYON = ("art-concepts-r43:docs/concepts/round34_rebel_cell/scripts @ d14b8f61158918f302e8e3baf5d39fc734dbde15 "
                        "(vendor_r34/) + " + VENDOR_SOURCE + " (vendor_r43/)")
SOLACE_SETTINGS = {"build_solace_v5_compound.py": {"look": "aaa2", "interior_atlas": "imap_atlas.jpg",
                                                  "park_radius_unit": "RB0 120 district units x 1.5"}}
VENDOR_SOURCE_SOLACE = "art-pass:docs/concepts/solace_vertical/hq/scripts @ 73dd33c9 (v5 plates; vendor_solace_v5/)"
MANIFEST_SCHEMA = "rebel_cell.art_export/1"
MATERIALS = {
    "hq_toon": "toon: 3-band ramp x vertex colour (tone baked); alpha = part bit -> ROUGHNESS (ink material edges)",
    "hq_lit": "floodlit toon: as hq_toon plus a warm self-light (heroes26 LIT)",
    "hq_neon": "emissive: vertex colour x neon gain (strips, trims, beacons)",
    "hq_win": "emissive windows: vertex colour x window gain",
    "hq_sign": "emissive diegetic signage (corp sign colour)",
    "hq_beam": "translucent light cone (emissive, alpha 0.22)",
    "hq_sx_skin": "Solace v5 PBR: lime glossy helix skin (vertex colour = base, back side = office wall)",
    "hq_sx_porc": "Solace v5 PBR: dark porcelain (jambs, deck undersides, crown slabs)",
    "hq_sx_neon": "Solace v5 emissive: vertex colour x alpha gain (frame rings, rungs, rings, crown halo, path lights)",
    "hq_sx_office": "Solace v5 built-floor interiors: vertex colour, alpha = emission gain",
    "hq_sx_glass": "Solace v5 clear glass (transparent + fresnel)",
    "hq_sx_metal": "Solace v5 metal (posts, rails, stair ribbon, core)",
    "hq_sx_win": "Solace v5 interior-mapped window patch: NORMAL = window normal, UV0 = (u, dz), UV1 = (variant, blind), COLOR = tint + lit",
    "hq_sx_stone": "Solace v5 plinth stone",
    "hq_sx_ground": "Solace v5 lawn / paths (vertex colour)",
    "hq_sx_plain": "Solace v5 trees, trunks, lamp posts",
    "hq_sx_water": "Solace v5 ponds",
}


def source_files():
    files = ["build_hq_compound.py", "build_solace_v5_compound.py", "build_dispatch_canyon.py", "hq_compound_spec.py", "make_hq_compounds.py",
             "validate_hq_compounds.py", "hq_compound_toon.gdshader", "id_ground.py"]
    for v in ("vendor_r43", "vendor_r34", "vendor_solace_v5"):
        files += [v + "/" + f for f in sorted(os.listdir(os.path.join(HERE, v))) if f.endswith(".py")]
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
        r = subprocess.run([blender, "-b", "--factory-startup", "--python", os.path.join(HERE, SPEC.layout(corp)["builder"]), "--", corp, out],
                           stdout=fh, stderr=subprocess.STDOUT, timeout=1200)
    if r.returncode != 0 or "DONE" not in open(log, encoding="utf-8", errors="replace").read():
        raise SystemExit("Blender failed for %s (see %s)" % (corp, log))
    return out


def extra_files(corp, dst):
    """Solace v5: the interior-mapping atlas (6 variants x 5 faces, 3240 x 2520) next to the glb."""
    if corp != "solace":
        return []
    p = os.path.join(dst, "imap_atlas.jpg")
    shutil.copyfile(os.path.join(HERE, "vendor_solace_v5", "imap_atlas.jpg"), p)
    return [{"path": "imap_atlas.jpg", "kind": "texture", "bytes": os.path.getsize(p), "sha256": sha256(p)}]


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
    if info.get("footprint_radius"):  # a circle (Solace v5): the city clears the lots under it; min / max is its bounding square
        rad = float(info["footprint_radius"])
        gmin, gmax = [-rad, gmin[1], -rad], [rad, gmax[1], rad]
    cam_t, cam_o = L["camera"]
    man = {
        "schema": MANIFEST_SCHEMA,
        "asset": "hq_compound",
        "corp": corp,
        "source": {"script": "tools/art_pipeline/city/" + L["builder"], "spec": "tools/art_pipeline/city/hq_compound_spec.py",
                   "driver": "tools/art_pipeline/city/make_hq_compounds.py",
                   "vendor": VENDOR_SOURCE_CANYON if L["builder"] == "build_dispatch_canyon.py" else (VENDOR_SOURCE_SOLACE if L["builder"] == "build_solace_v5_compound.py" else VENDOR_SOURCE), "commit": git_commit(),
                   "scripts_sha256": scripts_sha256()},
        "settings": {"blender": info["blender"], "state": info["state"], "units": "1 BU = 1 m", "up": "+Y (glTF; Blender (x, y, z) -> (x, z, -y))",
                     "tone": list(SPEC.TONE), "ramp_tint": list(SPEC.RAMP_TINT[corp]), "pitch_deg": L["pitch"], "yaw_deg": L["yaw"],
                     "reference_camera": {"target": gd(cam_t), "ortho": cam_o}, "normals": "exported (PBR look)" if L["builder"] == "build_solace_v5_compound.py" else "none (facet normal from screen derivatives)",
                     "layered_sprites": "dropped: 1D chose real-time Godot 3D", **SOLACE_SETTINGS.get(L["builder"], {})},
        "origin": L.get("origin", "the compound's ground centre (plaza centre) at (0, 0, 0); place it on the HQ lot's centre"),
        "place_lot": list(L["lot_centre"]) if "lot_centre" in L else None,
        "footprint": {"min": [round(v, 3) for v in gmin], "max": [round(v, 3) for v in gmax],
                      "size": [round(gmax[k] - gmin[k], 3) for k in range(3)], **({"radius": info["footprint_radius"]} if info.get("footprint_radius") else {})},
        "files": [{"path": info["glb"], "kind": "gltf", "bytes": os.path.getsize(glb), "sha256": sha256(glb)}] + extra_files(corp, dst),
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
