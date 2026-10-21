"""Runner for the netrun street panel (decision camera, art seed 1), street-graffiti look.

python graf_run_street.py <tag> <res_w> <spp> [cpu] [cfg={json}] [look.<key>=json ...]
  cfg: graffiti look cfg (graf_street.apply_street); cfg.fog_col sets the fog scatter colour; cfg.target the median
Output: D:/rc_scratch/graffiti/street/<tag>/ (npy passes, job, log, plate.png). Never writes into the repo.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph", "street_r2", "scripts"))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SRC = r"D:/rc_scratch/street_r2"
OUT = r"D:/rc_scratch/graffiti/street"


def main():
    tag, rw, spp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    args = sys.argv[4:]
    cfg, extra = {}, {}
    for a in args:
        if a.startswith("cfg="):
            cfg = json.loads(a[4:])
        elif a.startswith("look."):
            k, _, v = a[5:].partition("=")
            extra[k] = json.loads(v)
    out = os.path.join(OUT, tag)
    os.makedirs(out, exist_ok=True)
    job = json.load(open(os.path.join(SRC, "job_finals_s1_dec_closed.json")))
    job["frames"][0]["res"] = [rw, rw * 9 // 16]
    job["frames"][0]["name"] = "F_dec_closed"
    job["spp"] = spp
    if "cam_lens" in cfg:
        job["frames"][0]["persp"]["lens"] = cfg["cam_lens"]
    if "cam_sy" in cfg:
        job["frames"][0]["persp"]["sy"] = cfg["cam_sy"]
    if "fog_col" in cfg:
        job["look"]["scatter"] = list(cfg["fog_col"])
    job["look"].update(extra)
    jp, cp = os.path.join(out, "job.json"), os.path.join(out, "cams.json")
    json.dump(job, open(jp, "w"))
    json.dump([], open(cp, "w"))
    env = dict(os.environ, NET36="net_scope.json", GRAF_CFG=json.dumps(cfg))
    if "cpu" in args:
        env["GRAF_CPU"] = "1"
    log = os.path.join(out, "blender.log")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "-t", "6", "--factory-startup", "--python", os.path.join(HERE, "graf_blender_street.py"), "--",
                            "meridian_hq", out, cp, jp], stdout=f, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    txt = open(log, errors="replace").read()
    print("street", tag, "exit", r.returncode, "TRACEBACK" if "Traceback" in txt else "ok", "wall %.0f s" % wall, flush=True)
    for l in txt.splitlines():
        if l.startswith("[graf]"):
            print(l[:300])
    if r.returncode or "Traceback" in txt:
        return 3
    sys.path.insert(0, ST)
    sys.path.insert(1, os.path.normpath(os.path.join(ST, "..", "..", "storyboard", "scripts")))
    sys.dont_write_bytecode = True
    import numpy as np
    import r2_compose as RC
    from PIL import Image
    RC.rdir = lambda seed: out
    RC.TARGET_MEDIAN = float(cfg.get("target", 0.15))
    t = RC.SB.T["b6"] - 0.1
    im, e = RC.solved(1, "F_dec_closed", t)
    im = im.resize((1920, 1080), Image.LANCZOS)
    p = os.path.join(out, "plate.png")
    im.save(p)
    a = np.asarray(im.convert("L"), np.float32) / 255.0
    print("plate", p, "median %.3f" % float(np.median(a)), "exposure %.3f" % e, flush=True)
    json.dump(dict(wall=wall, median=float(np.median(a)), exposure=e), open(os.path.join(out, "stats.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
