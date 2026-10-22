"""Streamline Moderne runner for the Meridian overview (patches the base pipeline hq_meridian_v3 at run time, edits nothing).

python mg_run_hq.py <quality: eevee|mini|test|art> [tag] [key=json ...]     output: D:/rc_scratch/hq_styles/meridian_mughal/<tag>/
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RMG = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph"))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUTROOT = r"D:/rc_scratch/hq_styles/meridian_mughal"
HAZE0 = 0.0005


def main():
    q = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 and "=" not in sys.argv[2] else q
    extra = {}
    for kv in sys.argv[2:]:
        if "=" in kv:
            k, _, v = kv.partition("=")
            extra[k] = json.loads(v)
    sdir = os.path.join(RMG, "hq_meridian_v3", "scripts")
    sys.path.insert(0, sdir)
    sys.dont_write_bytecode = True
    import hq_jobs as J
    out = os.path.join(OUTROOT, tag)
    os.makedirs(out, exist_ok=True)
    frames = [f for f, _ in J.stills() if f["name"] == "H_overview"]
    qual = dict(J.QUAL["final"] if q == "art" else J.QUAL[q])
    if q == "art":
        qual.update(res=[1920, 1080], samples=int(os.environ.get("SL_SPP", "52")), threshold=0.015)
    job = dict(qual, out=out, frames=frames, force=True)
    job["deco"] = {}
    for k_ in list(extra):
        if k_.startswith("d."):
            job["deco"][k_[2:]] = extra.pop(k_)
    job["haze_k"] = float(extra.pop("haze_abs", 0.0022)) / HAZE0
    job.setdefault("glow_k", 1.5)
    job.update(extra)
    job["scene_src"] = os.path.join(sdir, "hq_scene.py")
    jp = os.path.join(out, "job.json")
    json.dump(job, open(jp, "w"), indent=1)
    log = os.path.join(out, "blender.log")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "mg_blender_hq.py"), "--", jp],
                           stdout=f, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    bad = "Traceback" in open(log, errors="replace").read()
    print(tag, "exit", r.returncode, "TRACEBACK" if bad else "ok", "wall %.0f s" % wall, flush=True)
    if bad or r.returncode:
        return 3
    import hq_post as PO
    import hq_compose  # noqa: F401
    import numpy as np
    HP = sys.modules.get("hq_preset")
    post = {"shadow_tint": [0.46, 0.50, 0.58], "sat": 0.92}
    post.update(job.get("post") or {})
    for k_, v_ in post.items():
        PO.P[k_] = v_
    stops = HP.PRESET["hq"].get("frame_stops", {}).get("H_overview", 0.0)
    e0 = PO.P["exposure"] * 2.0 ** stops
    target = float(job.get("target", 0.14))
    stem = os.path.join(out, "H_overview")
    ex, plate, med = e0 * 2.0 ** float(job.get("exp_stops", 0.0)), None, 0.0
    hist = []
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
