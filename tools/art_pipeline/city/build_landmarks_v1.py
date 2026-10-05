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


def footprint(job, info):
    sp = SPEC.JOBS[job]
    lots = {"hq": SPEC.HQ_LOTS, "site": SPEC.SITE_LOTS, "district": SPEC.DISTRICT_LOTS}[sp["kind"]]
    half = lots * SPEC.LOT_BU / 2
    lo, hi = info["bounds_concept"]["min"], info["bounds_concept"]["max"]
    over = max(abs(lo[0]), abs(lo[1]), abs(hi[0]), abs(hi[1])) - half
    return dict(lots=[lots, lots], bu=[lots * SPEC.LOT_BU, lots * SPEC.LOT_BU], overhang_bu=round(max(0.0, over), 2),
                note="origin = centre of the lot rectangle on the ground; the model may overhang its rectangle by overhang_bu "
                     "(lamps, rails, steps); the city should keep that margin clear of tall buildings")


def ref_cam(sp):
    """The job's reference camera in glTF / Godot coordinates (Blender (x, y, z) -> (x, z, -y))."""
    if sp["cam"] == "iso":
        return dict(kind="iso", yaw=SPEC.YAW, pitch=SPEC.PITCH, ortho=sp["iso_ortho"], target_up_bu=SPEC.CREST_LIFT_BU)
    loc, tgt, lens = sp["cam"]
    g = lambda p: [round(p[0], 3), round(p[2], 3), round(-p[1], 3)]  # noqa: E731
    import math
    return dict(kind="perspective", position=g(loc), target=g(tgt), lens_mm=lens, sensor_mm=36.0,
                hfov_deg=round(math.degrees(2 * math.atan(18.0 / lens)), 3))


def assemble():
    head = git_head()
    total = 0
    for corp in SPEC.CORPS:
        d = os.path.join(ASSETS, corp)
        os.makedirs(d, exist_ok=True)
        files, entries = [], []
        for job, sp in SPEC.JOBS.items():
            if sp["corp"] != corp:
                continue
            src = os.path.join(SCRATCH, job, job + ".glb")
            info = json.load(open(os.path.join(SCRATCH, job, job + ".info.json"), encoding="utf-8"))
            dst = os.path.join(d, job + ".glb")
            shutil.copyfile(src, dst)
            files.append(dst)
            entries.append(dict(job=job, file=job + ".glb", kind=sp["kind"], what=sp["what"], references=sp["refs"],
                                states=info["states"], seed=info["seed"], triangles=info["triangles"], roles=info["roles"],
                                animation=info["animation"], bounds_gltf=info["bounds_gltf"], footprint=footprint(job, info),
                                state_nodes=[n for n in info["nodes"] if "__state_" in n and n.count("__") == 1],
                                reference_camera=ref_cam(sp),
                                exporter=info["exporter_settings"], blender=info["blender"]))
        if corp == "rebel_cell":
            import landmark_post_v1 as POST
            mp = os.path.join(d, "rebel_cell_crest_mask.png")
            entries.append(POST.crest_mask(mp))
            files.append(mp)
        man = dict(
            about="ART-5 5b landmark (bible 4.4). Built by tools/art_pipeline/city/build_landmarks_v1.py; do not edit by hand.",
            corp=corp, version=SPEC.VERSION, source_commit=head,
            source_scripts=["tools/art_pipeline/city/" + s for s in SCRIPTS],
            concept_source="art-concepts-r43 (art-pass 097a6c0 round 31 builders; d14b8f6 round 34 crest)",
            coordinates=dict(units="1 glTF unit = 1 BU; 1 lot = %.0f BU" % SPEC.LOT_BU, up="+Y",
                             frame="glTF x = lot x, glTF z = lot y (CityIsoCamera.lot_to_world), origin = centre of the job's lot rectangle at ground level",
                             front="as the concept built them: HQs are symmetric or face the iso camera's side (+x, +z); Meridian's gate faces +x and its rail yard runs along x at z = -34 / -40 (the round 31 combat camera looks from -z); a Site's front faces +z (lot +y: screen lower-left, as in the locked Site renders)"),
            materials=dict(
                note="COLOR_0 is linear: rgb = base colour x the per-triangle tone jitter (0.86-1.12) for toon roles; alpha = a part id (toon roles: write it to ROUGHNESS 0.5-1.0 for material-edge ink) or a window's own seeded value (window roles)",
                lm_toon="3-band toon (spike city_building light(): ramp shadow / mid / lit on N.L, edges 0.118 / 0.363)",
                lm_toon_lines="lm_toon, darkened toward (8, 6, 12)/255 by 0.55 x reveal q (REBEL_CELL detail-line buildings)",
                lm_lit="lm_toon + emission 0.42 x colour (floodlit towers)",
                lm_neon="emissive colour x neon gain (night 1.0, day 0.75)",
                lm_window="emissive colour x window gain (night 1.0; day 0.55 mixed 0.55 toward dark glass (0.10, 0.14, 0.20))",
                lm_window_ring="lm_window, visible while alpha > reveal q (+/- 0.12 flicker band at the front): the blackout ring",
                lm_window_lines="lm_window, visible while alpha < (1 - q) x 0.85: lit detail lines before the reveal",
                lm_window_fist_home="red fist windows, home look (70 % density baked)",
                lm_window_fist_dispatch="red fist windows, DISPATCH look (90 %, glitch rows, a few white); show instead of _home",
                lm_beam="additive translucent light cone, emission colour x 0.22",
                lm_sign="flat emissive sign colour (corp sign colour)"),
            settings=dict(lot_bu=SPEC.LOT_BU, hq_lots=SPEC.HQ_LOTS, site_lots=SPEC.SITE_LOTS, site_scale=SPEC.SITE_SCALE,
                          site_rot_deg=SPEC.SITE_ROT, camera=dict(yaw=SPEC.YAW, pitch=SPEC.PITCH)),
            landmarks=entries,
            files=[dict(path=os.path.relpath(p, ROOT).replace("\\", "/"), bytes=os.path.getsize(p), sha256=sha256(p)) for p in files])
        with open(os.path.join(d, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(man, f, indent=1)
            f.write("\n")
        sz = sum(x["bytes"] for x in man["files"])
        total += sz
        print("%-11s %8.1f KB  %s" % (corp, sz / 1024, ", ".join("%s %.0f KB" % (os.path.basename(x["path"]), x["bytes"] / 1024) for x in man["files"])))
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
