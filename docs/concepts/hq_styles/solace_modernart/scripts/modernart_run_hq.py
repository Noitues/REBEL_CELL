"""Art-deco runner for the four HQ overview panels (halcyon, meridian_v3, orbital, solace).

python deco_run_hq.py <corp> <quality> [tag] [key=json ...]
  corp: halcyon | meridian | orbital | solace
  quality: eevee | mini | test | art (1920x1080 Cycles, spp from DECO_SPP, default 56)
Output (never inside the repo): D:/rc_scratch/hq_styles/solace_modernart/<corp>/<tag>/  (npy passes, job json, log, plate png)
The base pipeline's own scripts are imported, not edited; hq_scene.py is exec'd with a hook inserted in front of its
render section (modernart_blender_hq.py). Cycles qualities must run under the GPU lock (deco_gpu.py does that).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RMG = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph"))
DIRS = {"halcyon": "hq_halcyon", "meridian": "hq_meridian_v3", "orbital": "hq_orbital", "solace": "hq_solace"}
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUTROOT = r"D:/rc_scratch/hq_styles/solace_modernart"
HAZE_ABS = {"halcyon": 0.0025, "meridian": 0.0025, "orbital": 0.0020, "solace": 0.0015}   # absolute haze density per corp (deco fog)
HAZE0 = {"halcyon": 0.0002, "meridian": 0.0005, "orbital": 0.0003, "solace": 0.0006}   # the base presets' haze


def main():
    corp, q = sys.argv[1], sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 and "=" not in sys.argv[3] else q
    extra = {}
    for kv in sys.argv[3:]:
        if "=" in kv:
            k, _, v = kv.partition("=")
            extra[k] = json.loads(v)
    sdir = os.path.join(RMG, DIRS[corp], "scripts")
    sys.path.insert(0, sdir)
    sys.dont_write_bytecode = True
    import hq_jobs as J
    import hq_graph as G
    out = os.path.join(OUTROOT, corp, tag)
    os.makedirs(out, exist_ok=True)
    frames = [f for f, _ in J.stills() if f["name"] == "H_overview"]
    qual = dict(J.QUAL["final"] if q == "art" else J.QUAL[q])
    if q == "art":
        qual.update(res=[1920, 1080], samples=int(os.environ.get("DECO_SPP", "56")), threshold=0.015)
    job = dict(qual, out=out, frames=frames, force=True)
    if corp == "halcyon":
        lay = os.path.join(out, "layout.json")
        G.dump(lay, G.WALK_LATE)
        job.update(layout=lay)
        import hq_cam as CR
        job["ov_pose"] = CR.overview(G.WALK_LATE).to_json()
        job["occ_dir"] = out
    job["deco"] = dict(corp=corp)
    if corp == "solace":
        job["no_section"] = True       # the v4 overview plate has no section cut (the city stands full height)
    for k_ in list(extra):
        if k_.startswith('d.'):
            job['deco'][k_[2:]] = extra.pop(k_)
    haze_abs = float(extra.pop("haze_abs", HAZE_ABS[corp]))
    job["haze_k"] = haze_abs / HAZE0[corp]
    job.setdefault("glow_k", 1.5)
    job.update(extra)
    job["scene_src"] = os.path.join(sdir, "hq_scene.py")
    jp = os.path.join(out, "job.json")
    json.dump(job, open(jp, "w"), indent=1)
    log = os.path.join(out, "blender.log")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "modernart_blender_hq.py"), "--",
                            jp], stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    wall = time.time() - t0
    bad = "Traceback" in open(log, errors="replace").read()
    print(corp, tag, "exit", r.returncode, "TRACEBACK" if bad else "ok", "wall %.0f s" % wall, flush=True)
    if bad or r.returncode:
        return 3
    # post: the pipeline's own finish (hq_post), exposure solved to the target median (deco grade: charcoal, less saturated)
    import hq_post as PO
    import hq_compose  # noqa: F401  (pulls the same preset)
    import numpy as np
    HP = sys.modules.get("hq_preset") or sys.modules.get("halcyon_preset")
    post = {"shadow_tint": [0.42, 0.52, 0.56], "sat": 1.0}
    post.update(job.get("post") or {})
    for k_, v_ in post.items():
        PO.P[k_] = v_
    key = "halcyon" if corp == "halcyon" else "hq"
    stops = HP.PRESET[key].get("frame_stops", {}).get("H_overview", 0.0)
    e0 = PO.P["exposure"] * 2.0 ** stops
    target = float(job.get("target", 0.165))
    stem = os.path.join(out, "H_overview")
    ex, plate, med = e0 * 2.0 ** float(job.get("exp_stops", 0.0)), None, 0.0
    hist = []
    for it in range(5):
        PO.P["exposure"] = ex
        plate = PO.finish(stem, 0.0, t=2.0)
        med = float(np.median(np.asarray(plate.convert("L"), np.float32) / 255.0))
        hist.append((ex, med))
        if abs(med - target) < 0.006 or job.get("exp_stops") is not None and it == 0 and "target" not in job:
            break
        ex = ex * (target / max(med, 1e-3)) ** 1.15
    print("exposure", ["%.3f->%.3f" % h for h in hist], flush=True)
    p = os.path.join(out, "plate.png")
    plate.save(p)
    import numpy as np
    print("plate", p, plate.size, "median %.3f" % med, flush=True)
    json.dump(dict(wall=wall, median=med, exposure=ex), open(os.path.join(out, "stats.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
