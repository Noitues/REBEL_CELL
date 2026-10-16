"""Street round 2: the image-side rule checks on the clean plates (CPU; the metric code is proc_vs_custom's).

python r2_checks.py <plate.png> [--seed N --shot NAME] ...    print the tests for each plate
python r2_checks.py report                                     write ../metrics_r2.json + ../metrics_r2.md for the stills

Tests (thresholds = proc_vs_custom RULES / spec 12.7): R-SIL-1/2, R-DET-1/2, R-HUE-1/2, R-FOCUS-1 (the landmark box is
the megastructure's projected bounds from the render's anchors, not a hand box), R-REP-1, R-VAL-1/2/3, R-CALM-1/2.
Proxies for the rules without a test yet (spec 12.7):
  foreground.street   lower-band (fg_band) hue entropy and blob count / the full frame's (>= 0.8)
  atmosphere.layers   empty-sky share above the lit skyline (<= sky_max_share); depth-plane median luma from the Z pass
                      (front: the frontage band, mid: 20-90 BU behind it, back: beyond), adjacent steps >= plane_step
  dressing.signs      hero luma ratio (sign box / ring) per hero sign, from the anchors' projected sign centres
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PVC = os.path.normpath(os.path.join(HERE, "..", "..", "proc_vs_custom", "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(1, PVC)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

import pvc_metrics as M  # noqa: E402
import r2_config as CFG  # noqa: E402

SCR = "D:/rc_scratch/street_r2"
R = CFG.RULES_R2
TESTS = [
    ("R-SIL-1", "lit_std", ">=", 0.15), ("R-SIL-2", "lit_min_q_std", ">=", 0.08),
    ("R-DET-1", "sobel_mean", ">=", 0.028), ("R-DET-2", "blobs_per_mp", ">=", 450),
    ("R-HUE-1", "hue_entropy_bits", ">=", 3.8), ("R-HUE-2", "hue_top_share", "<=", 0.45),
    ("R-FOCUS-1", "lm_ratio", ">=", 1.5), ("R-REP-1", "rep_p90", "<=", 0.60),
    ("R-VAL-1", "median", "between", (0.12, 0.17)), ("R-VAL-2", "under_010", "between", (0.25, 0.40)),
    ("R-VAL-3", "over_085", "<=", 0.025), ("R-CALM-1", "detail_cv", "between", (0.45, 0.85)),
    ("R-CALM-2", "calm_share", "between", (0.12, 0.32)),
]


def spec_for(anchors=None, view="side"):
    s = dict(skyline=[0.0, 0.85], facade=[0.0, 0.10, 1.0, 0.80], bands={"upper": [0, 0.0, 1, 0.40], "lower": [0, 0.78, 1, 1.0]})
    b = anchors.get("landmark_box") if anchors else None
    if b and b[0] > -0.02 and b[1] > -0.02 and b[2] < 1.02 and b[3] < 1.02:      # only a landmark that is in frame
        s["landmark"] = [max(0.0, b[0]), max(0.0, b[1]), min(1.0, b[2]), min(1.0, b[3])]
    if view != "side":
        s.pop("skyline")
    return s


def judge(v, op, thr):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return (thr[0] <= v <= thr[1]) if op == "between" else (v <= thr if op == "<=" else v >= thr)


def proxies(path, anchors, zpath=None):
    rgb = M.load_work(path)
    L = M.luma(rgb)
    H, W = L.shape
    valid = np.ones_like(L, bool)
    full = M.palette(rgb, valid)
    fb = int(H * (1 - R["foreground.street"]["fg_band"]))
    low = M.palette(rgb[fb:], valid[fb:])
    bl_full = M.lights(L, valid)["blobs_per_mp"]
    bl_low = M.lights(L[fb:], valid[fb:])["blobs_per_mp"]
    out = dict(fg_hue_ratio=low["hue_entropy_bits"] / max(1e-6, full["hue_entropy_bits"]), fg_blob_ratio=bl_low / max(1e-6, bl_full))
    # empty sky above the lit skyline: rows above the lit profile whose 64 px tile Sobel is under half the median
    sk = M.skyline(L, [0.0, 0.85])
    sob = M.sobel_mag(M.box_blur(L, 2))            # a 2 px blur first: the post's film grain is not detail
    med = float(np.median(sob))
    prof = sk.get("_lit_profile")
    if prof is None:
        # recompute the lit profile the metric uses (first row passing the frame p80 after a 13 px smooth)
        sm = M.box_blur(L, 6)
        thr = np.percentile(L, 80)
        prof = np.array([np.argmax(sm[:, x] > thr) if (sm[:, x] > thr).any() else H for x in range(W)])
    above = np.zeros_like(L, bool)
    for x in range(W):
        above[:int(prof[x]), x] = True
    calm = M.box_blur(sob, 16) < 0.5 * med
    out["sky_empty_share"] = float((above & calm).sum() / (H * W))
    # depth planes from the Z pass
    if zpath and os.path.exists(zpath):
        z = np.load(zpath)[..., 0]
        from PIL import Image
        zz = np.asarray(Image.fromarray(z.astype(np.float32)).resize((W, H), Image.NEAREST))
        dist = anchors["cam"]["dist"] if anchors else 115.0
        bands = dict(front=(zz < dist + 12), mid=(zz >= dist + 12) & (zz < dist + 90), back=(zz >= dist + 90) & (zz < 5000))
        out["planes"] = {k: (float(np.median(L[m])) if m.sum() > 500 else None) for k, m in bands.items()}
    return out


def check(path, anchors=None, zpath=None, view="side"):
    r = M.measure(path, spec_for(anchors, view))
    res = {}
    for tid, key, op, thr in TESTS:
        if view != "side" and tid.startswith("R-SIL"):
            continue
        v = r.get(key)
        res[tid] = dict(value=None if v is None else round(float(v), 4), ok=judge(v, op, thr))
    res["_proxies"] = proxies(path, anchors, zpath)
    res["_raw"] = {k: (round(float(v), 4) if isinstance(v, (int, float)) else None) for k, v in r.items() if not isinstance(v, (list, dict))}
    return res


def fmt(name, res):
    s = [name]
    for tid, v in res.items():
        if tid.startswith("_"):
            continue
        s.append("  %-9s %-5s %s" % (tid, {True: "PASS", False: "FAIL", None: "n/a"}[v["ok"]], v["value"]))
    s.append("  proxies " + json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["_proxies"].items()}))
    return "\n".join(s)


def hero_ratio(path, anchors, plan):
    """dressing.signs proxy: each hero sign's mean luma over its projected centre box / the ring around it."""
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255.0
    L = M.luma(im)
    H, W = L.shape
    out = []
    for s in plan["signs"]:
        if not s.get("hero"):
            continue
        c = (anchors.get("signs") or {}).get(s["id"], [None])[0]
        if not c:
            continue
        x, y = c[0] * W / 1920.0, c[1] * H / 1080.0
        r = 10
        if not (3 * r < x < W - 3 * r and 3 * r < y < H - 3 * r):
            continue
        box = L[int(y - r):int(y + r), int(x - r):int(x + r)]
        big = L[int(y - 3 * r):int(y + 3 * r), int(x - 3 * r):int(x + 3 * r)]
        ring = (big.sum() - box.sum()) / (big.size - box.size)
        out.append(round(float(box.mean() / max(ring, 1e-3)), 2))
    return out


STILLS = [("01_OVERVIEW_closed_s1", 1, "F_ov_closed", "side"), ("02_DECISION_closed_s1", 1, "F_dec_closed", "close"),
          ("03_OVERVIEW_route_overlay_s1", 1, "F_ov_open", "side"), ("04_OVERVIEW_closed_seed2", 2, "F_ov_closed", "side")]


def report():
    root = os.path.dirname(HERE)
    out = {}
    md = ["# Street r2: rule tests on the clean plates", "",
          "Generated by `scripts/r2_checks.py report`. Thresholds: PIPELINE_SPEC 12.7 / proc_vs_custom RULES. "
          "The DECISION plate is a close view: the side-view tests (R-SIL) do not apply, and R-DET-2 / R-FOCUS-1 are reported for reference.", ""]
    for name, seed, shot, view in STILLS:
        p = os.path.join(root, "plates", name + "_plate.png")
        if not os.path.exists(p):
            continue
        an = json.load(open(os.path.join(SCR, "render_s%d" % seed, "anchors_%s.json" % shot)))
        plan = json.load(open(os.path.join(SCR, "plan_s%d.json" % seed)))
        r = check(p, an, os.path.join(SCR, "render_s%d" % seed, shot + "_z.npy"), view)
        r["_proxies"]["hero_lum_ratios"] = hero_ratio(p, an, plan)
        r["_plan_checks"] = plan["checks"]
        out[name] = r
        md.append("## " + name)
        md.append("")
        md.append("| test | result | value |")
        md.append("|---|---|---|")
        for tid, v in r.items():
            if tid.startswith("_"):
                continue
            md.append("| %s | %s | %s |" % (tid, {True: "PASS", False: "**FAIL**", None: "n/a"}[v["ok"]], v["value"]))
        md.append("")
        md.append("Proxies: `" + json.dumps(r["_proxies"], default=float) + "`")
        md.append("")
        md.append("Plan checks: `" + json.dumps({k: v.get("ok") for k, v in plan["checks"].items()}) + "`")
        md.append("")
    json.dump(out, open(os.path.join(root, "metrics_r2.json"), "w"), indent=1, default=float)
    open(os.path.join(root, "metrics_r2.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__" and sys.argv[1] == "report":
    report()
    sys.exit(0)

if __name__ == "__main__":
    a = sys.argv[1:]
    for p in a:
        if not p.endswith(".png"):
            continue
        base = os.path.basename(p)
        seed, shot = None, None
        if base.startswith("s") and "_" in base:          # D:/rc_scratch/street_r2/plates/s<seed>_<shot>.png
            seed, shot = base[1:].split("_", 1)
            shot = shot[:-4]
        an = zp = None
        if seed:
            ap = os.path.join(SCR, "render_s%s" % seed, "anchors_%s.json" % shot)
            an = json.load(open(ap)) if os.path.exists(ap) else None
            zp = os.path.join(SCR, "render_s%s" % seed, shot + "_z.npy")
        view = "close" if "dec" in base else "side"
        print(fmt(base, check(p, an, zp, view)))
