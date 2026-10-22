"""Solace THE BLOOM v2, A Necrosis 3D raid frames (district scene copy, Eevee cel + ink): A3d_raid_20 / _60 / _90.png.

python bloom3d_raid_run.py [20,60,90] [test]
Per percent: calibrate the field threshold `th` by cover-mask renders (Eevee, 480 x 270) so that the infected share of the
visible non-defended area equals the percent; render the cel map with the Bloom world material, re-ink with the clean ink pass,
post (mapraid), then the CRT gauge with the bare Anton %. Finals take the GPU lock "solace_bloom" (Eevee uses the GPU).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

import solace_lib as L
import bloom_gauge as G

BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
RS = os.path.join(HERE, "raid_scene")
SCR = "D:/rc_scratch/solace_v1/bloom3d/raid"
INK = "D:/rc_scratch/solace_v1/district/out/R5_raid_ink.png"
LOCK = "D:/rc_scratch/GPU_LOCK"
CFG = dict(seed=3, defended=[[[0.0, 0.0], 46.0], [[108.0, -60.0], 42.0]], vscale=0.075, vw=0.016, ew=0.35, hatch_k=0.45,
           veins=2.2, edge=6.0, hatch=0.12, plum=[0.035, 0.014, 0.028], pink=[1.0, 0.0612, 0.305])


def blender(cfg_path, size, out, cal=False, extra=()):
    env = dict(os.environ, BLOOM_CFG=cfg_path)
    env.pop("BLOOM_POS", None)
    if cal:
        env["BLOOM_CAL"] = "1"
    cmd = [BL, "--factory-startup", "-b", "--python", os.path.join(RS, "sd_main.py"), "--", "--dir", "D", "--park", "1", "--plinth", "1",
           "--mode", "map", "--view", "raid", "--tod", "night", "--size", size, "--out", out] + list(extra)
    t0 = time.time()
    with open(out + ".log", "w") as f:
        subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
    return time.time() - t0


def share_of(th):
    cfg = dict(CFG, th=th)
    cp = os.path.join(SCR, "cfg_cal.json")
    json.dump(cfg, open(cp, "w"))
    out = os.path.join(SCR, "cal.png")
    blender(cp, "480x270", out, cal=True)
    a = np.asarray(Image.open(out).convert("RGB"), np.float32) / 255.0
    geo = a[..., 2] > 0.3
    nd = geo & (a[..., 1] < 0.5)
    return float(((a[..., 0] > 0.5) & nd).sum() / max(nd.sum(), 1))


def calibrate(pct):
    lo, hi = -60.0, 140.0
    for i in range(7):
        mid = (lo + hi) / 2
        s = share_of(mid)
        print("  cal th %.1f share %.3f" % (mid, s), flush=True)
        if s > pct:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def acquire():
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ("solace_bloom %s raid3d\n" % time.strftime("%Y-%m-%d %H:%M:%S")).encode())
            os.close(fd)
            return
        except FileExistsError:
            time.sleep(30)


def release():
    if os.path.exists(LOCK) and open(LOCK, errors="replace").read().startswith("solace_bloom"):
        os.remove(LOCK)


def main(pcts, test=False):
    os.makedirs(SCR, exist_ok=True)
    res = {}
    size = "640x360" if test else "1920x1080"
    for p in pcts:
        pct = p / 100.0
        th = calibrate(pct)
        cfg = dict(CFG, th=th)
        cp = os.path.join(SCR, "cfg_%d.json" % p)
        json.dump(cfg, open(cp, "w"))
        raw = os.path.join(SCR, "raid_%d_raw.png" % p)
        if not test:
            acquire()
        try:
            t = blender(cp, size, raw)
        finally:
            if not test:
                release()
        share = share_of(th)
        if test:
            clean_ink = INK
        inked = os.path.join(SCR, "raid_%d_inked.png" % p)
        post = os.path.join(SCR, "raid_%d_post.png" % p)
        if not test:
            subprocess.run([sys.executable, os.path.join(RS, "ink.py"), raw, INK, inked, "2.6"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run([sys.executable, os.path.join(RS, "post.py"), "mapraid", inked, post], check=True)
            img = Image.open(post).convert("RGBA")
            panel, num = G.raid_gauge("A", pct)
            img.alpha_composite(panel, (36, 30))
            img.alpha_composite(num, (36 + panel.size[0] + 6, 18))
            arr = np.asarray(img.convert("RGB"), np.float32) / 255.0
            L.save_png(arr, os.path.join(L.OUT, "A3d_raid_%d.png" % p))
            res[p] = dict(th=round(th, 2), share=round(share, 3), render_s=round(t, 1), still=L.metrics(arr))
        else:
            res[p] = dict(th=round(th, 2), share=round(share, 3), render_s=round(t, 1))
        print(p, res[p], flush=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "raid3d_values.json"), "w"), indent=1)


if __name__ == "__main__":
    pcts = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "20,60,90").split(",")]
    main(pcts, len(sys.argv) > 2 and sys.argv[2] == "test")
