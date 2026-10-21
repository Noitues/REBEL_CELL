"""Street-graffiti runner for the four HQ overview panels (halcyon, meridian_v3, orbital, solace).

python graf_run_hq.py <corp> <quality> [tag] [key=json ...]
  corp: halcyon | meridian | orbital | solace
  quality: mini | test | art (1920x1080 Cycles, spp from GRAF_SPP, default 56)
  key=json: job overrides; g.<key>=json goes to the graffiti look cfg (graf_look.apply_hq); haze_k scales the base haze
Output (never inside the repo): D:/rc_scratch/graffiti/<corp>/<tag>/  (npy passes, job json, log, plate png)
The base pipeline's scripts are imported, not edited; hq_scene.py is exec'd with the hook patched in (graf_blender_hq.py).
Cycles qualities must run under the GPU lock (graf_gpu.py).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RMG = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph"))
DIRS = {"halcyon": "hq_halcyon", "meridian": "hq_meridian_v3", "orbital": "hq_orbital", "solace": "hq_solace"}
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUTROOT = r"D:/rc_scratch/graffiti"


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
        qual.update(res=[1920, 1080], samples=int(os.environ.get("GRAF_SPP", "56")), threshold=0.015)
    job = dict(qual, out=out, frames=frames, force=True)
    if corp == "halcyon":
        lay = os.path.join(out, "layout.json")
        G.dump(lay, G.WALK_LATE)
        job.update(layout=lay)
        import hq_cam as CR
        job["ov_pose"] = CR.overview(G.WALK_LATE).to_json()
        job["occ_dir"] = out
    job["graf"] = dict(corp=corp)
    if corp == "solace":
        job["no_section"] = True       # as the deco runner: the v4 overview plate has no section cut
    for k_ in list(extra):
        if k_.startswith("g."):
            job["graf"][k_[2:]] = extra.pop(k_)
    job["haze_k"] = float(extra.pop("haze_k", 1.0))
    job.update(extra)
    job["scene_src"] = os.path.join(sdir, "hq_scene.py")
    jp = os.path.join(out, "job.json")
    json.dump(job, open(jp, "w"), indent=1)
    log = os.path.join(out, "blender.log")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "graf_blender_hq.py"), "--",
                            jp], stdout=f, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    txt = open(log, errors="replace").read()
    bad = "Traceback" in txt
    print(corp, tag, "exit", r.returncode, "TRACEBACK" if bad else "ok", "wall %.0f s" % wall, flush=True)
    for l in txt.splitlines():
        if l.startswith("[graf]"):
            print(l[:300])
    if bad or r.returncode:
        return 3
    # post: the pipeline's own finish (hq_post), exposure solved to the target median
    import hq_post as PO
    import hq_compose  # noqa: F401  (pulls the same preset)
    import numpy as np
    HP = sys.modules.get("hq_preset") or sys.modules.get("halcyon_preset")
    for k_, v_ in (job.get("post") or {}).items():
        PO.P[k_] = v_
    key = "halcyon" if corp == "halcyon" else "hq"
    stops = HP.PRESET[key].get("frame_stops", {}).get("H_overview", 0.0)
    ex = PO.P["exposure"] * 2.0 ** stops
    target = float(job.get("target", 0.16))
    stem = os.path.join(out, "H_overview")
    plate, med, hist = None, 0.0, []
    for it in range(5):
        PO.P["exposure"] = ex
        plate = PO.finish(stem, 0.0, t=2.0)
        med = float(np.median(np.asarray(plate.convert("L"), np.float32) / 255.0))
        hist.append((ex, med))
        if abs(med - target) < 0.006:
            break
        ex = ex * (target / max(med, 1e-3)) ** 1.15
    print("exposure", ["%.3f->%.3f" % h for h in hist], flush=True)
    p = os.path.join(out, "plate.png")
    plate.save(p)
    print("plate", p, plate.size, "median %.3f" % med, flush=True)
    json.dump(dict(wall=wall, median=med, exposure=ex), open(os.path.join(out, "stats.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
