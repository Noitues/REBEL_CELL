"""Runner for panel 1 (whole city, A2 hero camera).

python deco_run_city.py <tag> <res_k> <spp> [cpu] [cfg=json] [off]
Output: D:/rc_scratch/art_deco/city/<tag>/hero_aaa_*.npy, plate.png (post_city.aaa, soft, exposure solved to the target median).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CITY = os.path.normpath(os.path.join(HERE, "..", "..", "city_all_corps", "scripts"))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = r"D:/rc_scratch/art_deco/city"


def main():
    tag, res_k, spp = sys.argv[1], sys.argv[2], sys.argv[3]
    args = sys.argv[4:]
    cpu = "cpu" in args
    cfg = {}
    for a in args:
        if a.startswith("cfg="):
            cfg = json.loads(a[4:])
    out = os.path.join(OUT, tag)
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ)
    env["DECO_CFG"] = json.dumps(cfg)
    if cpu:
        env["CITY_CPU"] = "1"
    log = os.path.join(out, "blender.log")
    script = os.path.join(HERE, "deco_blender_off.py" if "off" in args else "deco_blender_city.py")
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "-t", "6", "--factory-startup", "--python", script, "--", "aaa", "hero", out, res_k, spp],
                           stdout=f, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    txt = open(log, errors="replace").read()
    print("city", tag, "exit", r.returncode, "TRACEBACK" if "Traceback" in txt else "ok", "wall %.0f s" % wall, flush=True)
    for l in txt.splitlines():
        if l.startswith(("TIME", "[deco]")):
            print(l[:300])
    if r.returncode or "Traceback" in txt:
        return 3
    sys.path.insert(0, CITY)
    sys.dont_write_bytecode = True
    import numpy as np
    import post_city as PC
    from PIL import Image
    target = float(cfg.get("target", 0.15))
    plate_png = os.path.join(out, "plate.png")
    PC.aaa(os.path.join(out, "hero_aaa"), plate_png, target=target, soft=True)
    a = np.asarray(Image.open(plate_png).convert("L"), np.float32) / 255.0
    print("plate", plate_png, "median %.3f" % float(np.median(a)))
    json.dump(dict(wall=wall, median=float(np.median(a))), open(os.path.join(out, "stats.json"), "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
