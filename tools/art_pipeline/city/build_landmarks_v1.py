"""ART-5 5b: build the five corporation landmarks (v1): Blender 5.2 headless -> glTF 2.0 + manifests.

  python tools/art_pipeline/city/build_landmarks_v1.py blender [jobs|all] [glb,preview] [-j N]
  python tools/art_pipeline/city/build_landmarks_v1.py post [jobs|all]        # finish the Blender previews
  python tools/art_pipeline/city/build_landmarks_v1.py sheets <godot shots>   # comparison crops (after landmark_review)
  python tools/art_pipeline/city/build_landmarks_v1.py assemble               # copy into assets/, write manifests

Scratch output goes to %TEMP%/a5b/build/<job>/ (override with LANDMARK_SCRATCH). Assets: assets/city/landmarks/<corp>/
<job>.glb + manifest.json (source scripts, commit, settings, files with sizes and sha256, footprint and origin
convention, roles, animation). REBEL_CELL also gets rebel_cell_crest_mask.png (the crest rule for the CityModel's
window shader). tools/landmark_asset_checks.gd (called by tools/validate_content.gd) checks every manifest and file.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import landmark_spec_v1 as SPEC  # noqa: E402

BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
SCRATCH = os.environ.get("LANDMARK_SCRATCH", os.path.join(os.environ.get("TEMP", "/tmp"), "a5b", "build"))
ASSETS = os.path.join(ROOT, "assets", "city", "landmarks")
SCRIPTS = ["landmark_spec_v1.py", "landmark_build_v1.py", "landmark_district_v1.py", "landmark_crest_v1.py",
           "landmark_post_v1.py", "gltf_anim_v1.py", "build_landmarks_v1.py"] + ["concept_r31/%s.py" % n for n in
                                                            ("target_corps", "heroes24", "heroes25", "heroes26", "heroes27",
                                                             "heroes28", "heroes29", "heroes30", "heroes31")]


def jobs_of(arg):
    return list(SPEC.JOBS) if arg in (None, "all") else arg.split(",")


def run_blender(job, actions):
    out = os.path.join(SCRATCH, job)
    os.makedirs(out, exist_ok=True)
    log = os.path.join(SCRATCH, "log_%s.txt" % job)
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "landmark_build_v1.py"), "--",
                            job, out, actions], stdout=f, stderr=subprocess.STDOUT, timeout=3600)
    txt = open(log, encoding="utf-8", errors="replace").read()
    ok = r.returncode == 0 and "DONE" in txt and "Traceback" not in txt
    print("%-22s %s %.0fs  (%s)" % (job, "ok" if ok else "FAILED", time.time() - t0, log), flush=True)
    return ok


def git_head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        return "unknown"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


MANIFEST_SCHEMA = "rebel_cell.art_export/1"  # the shared export convention (8p HQ compounds, DECISIONS 8p)


def scripts_sha256():
    """One hash over the pipeline (path + LF-normalised content of every source script), as 8p's make_hq_compounds;
    tools/landmark_asset_checks.gd recomputes it, so an export older than its pipeline fails validation."""
    h = hashlib.sha256()
    for f in SCRIPTS:
        h.update(f.encode())
        h.update(open(os.path.join(HERE, f), "rb").read().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def footprint(info):
    """Min / max / size in the Godot frame (static geometry; moving parts are in `animation`)."""
    lo, hi = info["bounds_gltf"]["min"], info["bounds_gltf"]["max"]
    return dict(min=lo, max=hi, size=[round(hi[k] - lo[k], 3) for k in range(3)])


def lot_rect(job, info):
    sp = SPEC.JOBS[job]
    lots = {"hq": SPEC.HQ_LOTS, "site": SPEC.SITE_LOTS, "district": SPEC.DISTRICT_LOTS}[sp["kind"]]
    half = lots * SPEC.LOT_BU / 2
    lo, hi = info["bounds_gltf"]["min"], info["bounds_gltf"]["max"]
    over = max(abs(lo[0]), abs(lo[2]), abs(hi[0]), abs(hi[2])) - half
    return dict(lots=[lots, lots], bu=[lots * SPEC.LOT_BU, lots * SPEC.LOT_BU], overhang_bu=round(max(0.0, over), 2))


def ref_cam(sp):
    """The job's reference camera in the Godot frame (Blender (x, y, z) -> (x, z, -y))."""
    if sp["cam"] == "iso":
        return dict(kind="iso", yaw_deg=SPEC.YAW, pitch_deg=SPEC.PITCH, ortho=sp["iso_ortho"], target_up_bu=SPEC.CREST_LIFT_BU)
    loc, tgt, lens = sp["cam"]
    g = lambda p: [round(p[0], 3), round(p[2], 3), round(-p[1], 3)]  # noqa: E731
    import math
    return dict(kind="perspective", position=g(loc), target=g(tgt), lens_mm=lens, sensor_mm=36.0,
                hfov_deg=round(math.degrees(2 * math.atan(18.0 / lens)), 3))


ORIGIN = {"hq": "the landmark's ground centre (plaza centre) at (0, 0, 0); place it on the HQ lot rectangle's centre",
          "site": "the Site's ground centre at (0, 0, 0); place it on the centre of its 6 x 6 lot block",
          "district": "the palm (the crest's anchor) on the ground at (0, 0, 0); place it on the centre of the Cell's district"}
MATERIALS = {
    "lm_toon": "toon: 3-band ramp x vertex colour (tone baked); alpha = part value 0.55-1.0 -> ROUGHNESS (ink material edges)",
    "lm_toon_lines": "lm_toon, darkened toward (8, 6, 12)/255 by 0.55 x reveal q (REBEL_CELL detail-line buildings)",
    "lm_lit": "lm_toon + emission 0.25 x colour (floodlit towers; LandmarkLook.lit_emission)",
    "lm_neon": "emissive: vertex colour x neon gain (night 1.0, day 0.75)",
    "lm_win": "emissive windows: vertex colour x window gain (day: 0.55, mixed 0.55 toward dark glass); alpha = the window's seeded value",
    "lm_win_ring": "lm_win, visible while alpha > reveal q (+/- 0.12 flicker band at the front): the blackout ring",
    "lm_win_lines": "lm_win, visible while alpha < (1 - q) x 0.85: lit detail lines before the reveal",
    "lm_win_fist_home": "red fist windows, home look (70 % density baked) x LandmarkLook.fist_gain",
    "lm_win_fist_dispatch": "red fist windows, DISPATCH look (90 %, glitch rows, a few white); show instead of _home",
    "lm_beam": "translucent light cone: vertex colour at 0.22 over what is behind, no depth write (no ink)",
    "lm_sign": "emissive diegetic signage (corp sign colour)",
}


def assemble():
    head = git_head()
    ssha = scripts_sha256()
    total = 0
    for corp in SPEC.CORPS:
        d = os.path.join(ASSETS, corp)
        os.makedirs(d, exist_ok=True)
        files, entries, blender = [], [], ""
        for job, sp in SPEC.JOBS.items():
            if sp["corp"] != corp:
                continue
            info = json.load(open(os.path.join(SCRATCH, job, job + ".info.json"), encoding="utf-8"))
            dst = os.path.join(d, job + ".glb")
            shutil.copyfile(os.path.join(SCRATCH, job, job + ".glb"), dst)
            files.append((dst, "gltf"))
            blender = info["blender"]
            entries.append(dict(job=job, kind=sp["kind"], file=job + ".glb", what=sp["what"], origin=ORIGIN[sp["kind"]],
                                footprint=footprint(info), lot_rect=lot_rect(job, info), states=info["states"],
                                state_nodes=[n for n in info["nodes"] if "__state_" in n and n.count("__") == 1],
                                triangles=info["triangles_by_role"], animation=info["animation"], seed=info["seed"],
                                reference_camera=ref_cam(sp), references=["docs/art_reference/" + r for r in sp["refs"]]))
        if corp == "rebel_cell":
            import landmark_post_v1 as POST
            mp = os.path.join(d, "rebel_cell_crest_mask.png")
            entries.append(POST.crest_mask(mp))
            files.append((mp, "mask"))
        main_entry = entries[0]
        man = dict(
            schema=MANIFEST_SCHEMA, asset="landmark", corp=corp,
            about="ART-5 5b landmark (bible 4.4). Built by tools/art_pipeline/city/build_landmarks_v1.py; do not edit by hand.",
            source=dict(script="tools/art_pipeline/city/landmark_build_v1.py", spec="tools/art_pipeline/city/landmark_spec_v1.py",
                        driver="tools/art_pipeline/city/build_landmarks_v1.py",
                        vendor="art-concepts-r43:docs/concepts/round31_meridian_combat/scripts @ 097a6c0 (concept_r31/); "
                               "round34_rebel_cell/scripts/map34.py @ d14b8f6 (landmark_crest_v1)",
                        scripts=["tools/art_pipeline/city/" + s for s in SCRIPTS], commit=head, scripts_sha256=ssha),
            settings=dict(blender=blender, version=SPEC.VERSION, units="1 BU = 1 m; 1 lot = %.0f BU" % SPEC.LOT_BU,
                          up="+Y (glTF; Blender (x, y, z) -> (x, z, -y)); glTF x = lot x, z = lot y (CityIsoCamera.lot_to_world)",
                          tone=list(SPEC.TONE), part_alpha=list(SPEC.PART_ALPHA), ramp_tint="LandmarkLook.corp_tint (target_corps.TINT)",
                          pitch_deg=SPEC.PITCH, yaw_deg=SPEC.YAW, normals="none (facet normal from screen derivatives)",
                          layered_sprites="dropped: 1D chose real-time Godot 3D",
                          site_scale=SPEC.SITE_SCALE, site_rot_deg=SPEC.SITE_ROT,
                          front="as the concept built them: Meridian's gate faces +x, its rail yard runs along x at z = -34 / -40; "
                                "a Site's front faces +z (lot +y, screen lower-left, as the locked Site renders)"),
            origin=main_entry["origin"], footprint=main_entry["footprint"],
            materials=MATERIALS, landmarks=entries,
            files=[dict(path=os.path.basename(p), kind=k, bytes=os.path.getsize(p), sha256=sha256(p)) for p, k in files],
            validator="tools/landmark_asset_checks.gd (from tools/validate_content.gd): manifest keys, files, sizes, sha256, stale pipeline")
        with open(os.path.join(d, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(man, f, indent=1)
            f.write("\n")
        sz = sum(x["bytes"] for x in man["files"])
        total += sz
        print("%-11s %8.1f KB  %s" % (corp, sz / 1024, ", ".join("%s %.0f KB" % (x["path"], x["bytes"] / 1024) for x in man["files"])))
    print("TOTAL %.2f MB" % (total / 1024 / 1024))


def main():
    a = sys.argv[1:]
    jn = 1
    if "-j" in a:
        i = a.index("-j")
        jn = int(a[i + 1])
        del a[i:i + 2]
    cmd = a[0]
    if cmd == "blender":
        jobs = jobs_of(a[1] if len(a) > 1 else None)
        actions = a[2] if len(a) > 2 else "glb"
        with ThreadPoolExecutor(max_workers=jn) as ex:
            res = list(ex.map(lambda j: run_blender(j, actions), jobs))
        sys.exit(0 if all(res) else 1)
    if cmd == "post":
        import landmark_post_v1 as POST
        for j in jobs_of(a[1] if len(a) > 1 else None):
            POST.finish_job(j, os.path.join(SCRATCH, j), ROOT)
        return
    if cmd == "sheets":
        import landmark_post_v1 as POST
        POST.sheets(SCRATCH, a[1], ROOT)
        return
    if cmd == "assemble":
        assemble()
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
