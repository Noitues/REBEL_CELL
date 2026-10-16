"""Street round 2: post + the storyboard UI on the r2 renders (CPU only).

python r2_compose.py plates <seed> [prefix]   finish every <prefix>_* render of the seed into a clean plate (values solve)
python r2_compose.py stills                   the four deliverable stills (1920 x 1080) + their clean plates

The post is the storyboard's (post_aaa.finish, look "real"); the UI is the storyboard's own overlay code (sb_reveal
route_chrome, sb_frames2.street_overlay, sb_ui.title), imported read-only. The exposure is solved per plate on the
clean frame (values.solve: median 0.14), as the spec asks, instead of the storyboard's fixed 0.77 / 0.84.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SBS = os.path.normpath(os.path.join(HERE, "..", "..", "storyboard", "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(1, SBS)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import post_aaa as PA  # noqa: E402
import sb_cams as SB  # noqa: E402
import sb_frames2 as F2  # noqa: E402
import sb_reveal as RV  # noqa: E402
import sb_ui as U  # noqa: E402

SCR = "D:/rc_scratch/street_r2"
ROOT = os.path.dirname(HERE)
STILLS = os.path.join(ROOT, "stills")
PLATES = os.path.join(ROOT, "plates")
TARGET_MEDIAN = 0.14


def rdir(seed):
    return os.path.join(SCR, "render_s%s" % seed)


def luma_median(im):
    a = np.asarray(im.convert("RGB"), np.float32) / 255.0
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return float(np.median(L)), float((L < 0.10).mean()), float((L > 0.85).mean())


def finish(seed, name, exposure, t):
    return PA.finish(rdir(seed), "real", shot=name, t=t, over=dict(exposure=exposure)).convert("RGB")


def solved(seed, name, t, e0=0.8):
    """values.solve: the exposure whose clean plate has median luma TARGET_MEDIAN (secant in log space, 4 steps)."""
    import math
    pts = []
    e = e0
    im = None
    for _ in range(4):
        im = finish(seed, name, e, t)
        m = luma_median(im)[0]
        pts.append((math.log(e), math.log(max(m, 1e-3))))
        if abs(m - TARGET_MEDIAN) < 0.004:
            break
        if len(pts) == 1:
            e = e * (TARGET_MEDIAN / m) ** 1.2
        else:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            k = (y1 - y0) / (x1 - x0) if abs(x1 - x0) > 1e-6 else 1.0
            e = math.exp(x1 + (math.log(TARGET_MEDIAN) - y1) / max(k, 0.2))
        e = min(max(e, 0.35), 2.0)
    # the second target of values.solve: at least 26 % under 0.10, as long as the median stays in its band (>= 0.125)
    for _ in range(4):
        m, under, _o = luma_median(im)
        if under >= 0.26:
            break
        e2 = e * 0.93
        im2 = finish(seed, name, e2, t)
        if luma_median(im2)[0] < 0.125:
            break
        im, e = im2, e2
    return im, e


def anchors(seed, name):
    return json.load(open(os.path.join(rdir(seed), "anchors_%s.json" % name)))


def plates(seed, prefix):
    os.makedirs(os.path.join(SCR, "plates"), exist_ok=True)
    out = {}
    for f in sorted(os.listdir(rdir(seed))):
        if f.startswith(prefix + "_") and f.endswith("_combined.npy"):
            nm = f[:-len("_combined.npy")]
            im, e = solved(seed, nm, SB.T["b4"])
            im = im.resize((1920, 1080), Image.LANCZOS)
            p = os.path.join(SCR, "plates", "s%s_%s.png" % (seed, nm))
            im.save(p)
            out[nm] = dict(path=p, exposure=round(e, 3), values=luma_median(im))
            print(nm, out[nm], flush=True)
    return out


def chrome(img, A, zoom, t):
    ui = RV.route_chrome(img.convert("RGBA"), A, zoom, 1.0)
    return U.title(ui.convert("RGB"), t)


def stills():
    os.makedirs(STILLS, exist_ok=True)
    os.makedirs(PLATES, exist_ok=True)
    rep = {}
    jobs = [("01_OVERVIEW_closed_s1", 1, "F_ov_closed", "ov"), ("02_DECISION_closed_s1", 1, "F_dec_closed", "dec"),
            ("03_OVERVIEW_route_overlay_s1", 1, "F_ov_open", "route"), ("04_OVERVIEW_closed_seed2", 2, "F_ov_closed", "ov")]
    for name, seed, shot, kind in jobs:
        if not os.path.exists(os.path.join(rdir(seed), shot + "_combined.npy")):
            print("missing", seed, shot)
            continue
        t = SB.T["b4"] if kind != "dec" else SB.T["b6"] - 0.1
        pl, e = solved(seed, shot, t)
        pl = pl.resize((1920, 1080), Image.LANCZOS)
        pl.save(os.path.join(PLATES, name + "_plate.png"))
        A = anchors(seed, shot)
        if kind == "ov":
            img = chrome(pl, A, 1.0, t)
        elif kind == "dec":
            img = chrome(pl, A, 0.0, t)
        else:
            f = SB.fr(SB.T["mark"] + RV.marks_len() + 0.3)
            img = F2.street_overlay(pl.convert("RGBA"), A, f)
            img = U.title(img.convert("RGB"), f / SB.FPS)
        img.convert("RGB").save(os.path.join(STILLS, name + ".png"))
        rep[name] = dict(exposure=round(e, 3), values=[round(v, 3) for v in luma_median(pl)], landmark_box=A.get("landmark_box"),
                         sign_lod=A.get("sign_lod"))
        print(name, rep[name], flush=True)
    json.dump(rep, open(os.path.join(PLATES, "plates.json"), "w"), indent=1)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "plates":
        plates(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "T")
    elif w == "stills":
        stills()
