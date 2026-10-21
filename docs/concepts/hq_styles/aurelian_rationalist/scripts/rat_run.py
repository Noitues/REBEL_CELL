"""Driver: python rat_run.py <quality: eevee|mini|test|art> [tag] [key=json ...]   (keys prefixed rat. go to the style cfg)
Output in D:/rc_scratch/hq_styles/aurelian_rationalist/<tag>/ (job, log, passes, plate.png). Cycles qualities with GPU: run
under rat_gpu.py (the shared lock); `cpu=true` previews need no lock."""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
AUR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_aurelian", "scripts"))
sys.path.insert(0, AUR)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUTROOT = r"D:/rc_scratch/hq_styles/aurelian_rationalist"


def main():
    q = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 and "=" not in sys.argv[2] else q
    extra, rat = {}, {}
    for kv in sys.argv[2:]:
        if "=" in kv:
            k, _, v = kv.partition("=")
            (rat if k.startswith("rat.") else extra)[k[4:] if k.startswith("rat.") else k] = json.loads(v)
    import hq_run  # noqa: F401  (aur_env.setup + the Aurelian frame patch on hq_jobs)
    import hq_jobs as J
    import hq_post as PO
    import numpy as np
    out = os.path.join(OUTROOT, tag)
    os.makedirs(out, exist_ok=True)
    frames = [f for f, _ in J.stills() if f["name"] == "H_overview"]
    qual = dict(J.QUAL["final"] if q == "art" else J.QUAL[q])
    if q == "art":
        qual.update(res=[1920, 1080], samples=int(os.environ.get("RAT_SPP", "52")), threshold=0.015)
    job = dict(qual, out=out, frames=frames, force=True, rat=rat)
    job.update(extra)
    jp = os.path.join(out, "job.json")
    json.dump(job, open(jp, "w"), indent=1)
    log = os.path.join(out, "blender.log")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "rat_blender.py"), "--", jp],
                           stdout=f, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    bad = "Traceback" in open(log, errors="replace").read()
    print(tag, "exit", r.returncode, "TRACEBACK" if bad else "ok", "wall %.0f s" % wall, flush=True)
    if bad or r.returncode:
        return 3
    post = {"shadow_tint": [0.46, 0.50, 0.55], "sat": 0.85}
    post.update(job.get("post") or {})
    for k_, v_ in post.items():
        PO.P[k_] = v_
    import hq_preset as HP
    stops = HP.PRESET["hq"].get("frame_stops", {}).get("H_overview", 0.0)
    ex = PO.P["exposure"] * 2.0 ** stops * 2.0 ** float(job.get("exp_stops", 0.0))
    target = float(job.get("target", 0.16))
    stem = os.path.join(out, "H_overview")
    hist = []
    for it in range(5):
        PO.P["exposure"] = ex
        plate = PO.finish(stem, 0.0, t=2.0)
        med = float(np.median(np.asarray(plate.convert("L"), np.float32) / 255.0))
        hist.append((ex, med))
        if abs(med - target) < 0.006 or job.get("fixed_exposure"):
            break
        ex *= (target / max(med, 1e-3)) ** 1.15
    print("exposure", ["%.3f->%.3f" % h for h in hist], flush=True)
    p = os.path.join(out, "plate.png")
    plate.save(p)
    print("plate", p, plate.size, "median %.3f" % med, flush=True)
    json.dump(dict(wall=wall, median=med, exposure=ex), open(os.path.join(out, "stats.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
