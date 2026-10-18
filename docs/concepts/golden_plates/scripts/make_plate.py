"""Golden plate writer (PIPELINE_SPEC 12.8 / 12.0). CPU only: PIL + numpy.

Library + CLI. One plate = four files in the output folder:
  <stem>.png            the no-UI beauty plate (8-bit sRGB, copied byte for byte when it already is RGB)
  <stem>_id.png         R = class from a saved Blender Object Index pass, G = B = 0 (HQ passes carry no room ids)
  <stem>_capture.json   the 12.0 capture.json: pose (derive v2 shape), resolution, scope keys, provenance
  <stem>_values.json    median / under_010 / over_085, the 12.2 landmark ratios, 12.7 composition metrics, check statuses

CLI:   python make_plate.py <spec.json> [--out DIR]
spec.json keys (see build_all.py for the real ones):
  stem, kind (hq|street|city), view (overview|decision|city), corp, beauty (path), index (path to *_index.npy or null),
  camera (dict: loc, tgt, yaw, pitch, dist, lens, shift_x, shift_y), resolution [w, h] (optional),
  look ("aaa2"|"mainline"|"blend"|null), exempt {hover_cut, red_seq, flash}, day (bool: value band reported only),
  source {...free provenance...}, pending [str, ...], extra_values {...} (merged into values: ratio_mean etc. from another tool)
  accepted [{check, note}] (pre-accepted warns, 12.8)

Index pass -> 12.0 class map (the passes are written by hq_scene.py `Acc(name, mat, pass_index, coll)`):
  0 sky -> 0         1 landmark compound -> 1     2 city (and sky dome, city emit) -> 2
  3 -> 4  (spec.class_map overrides: Rebel Cell maps 3 -> 1, AD 2026-10-18; NOT link structure in the HQ passes: Solace uses 3 for the plaza apron ring, Rebel Cell for the MAINFRAME
          sign quad; mapped to 4 so the 12.2 masks {1,5,6} / {0,2} stay identical to hq_values.py)
  4 ground -> 4      5 rooms -> 5                 6 landmark movers -> 6
  7 light streaks -> 4 (not in any 12.2 mask)
Class 3 (link structure) therefore never appears in an HQ plate.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PVC = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph", "proc_vs_custom", "scripts"))
sys.path.insert(0, PVC)
import pvc_metrics as PM  # noqa: E402

CLASS_MAP = {0: 0, 1: 1, 2: 2, 3: 4, 4: 4, 5: 5, 6: 6, 7: 4}
LANDMARK_CLASSES = (1, 5, 6)
BACKGROUND_CLASSES = (0, 2)
GROW = 0.35                                    # 12.2: the landmark box grown 35 %

# 12.1 / 12.2 / 12.7 bands (provisional where the spec says so)
MEDIAN_PASS, MEDIAN_WARN = (0.11, 0.17), (0.09, 0.19)
UNDER_BAND, OVER_MAX = (0.25, 0.40), 0.025
RATIO_PASS = (1.5, 2.0)
COMP_RULES = {                                 # rule: (metric key in pvc_metrics.measure, op, limit)
    "R-SIL-1": ("lit_std", ">=", 0.15), "R-SIL-2": ("lit_min_q_std", ">=", 0.08),
    "R-DET-1": ("sobel_mean", ">=", 0.028), "R-DET-2": ("blobs_per_mp", ">=", 450.0),
    "R-CALM-1": ("detail_cv", "range", (0.45, 0.85)), "R-CALM-2": ("calm_share", "range", (0.12, 0.32)),
    "R-HUE-1": ("hue_entropy_bits", ">=", 3.8), "R-HUE-2": ("hue_top_share", "<=", 0.45),
    "R-FOCUS-1": ("lm_ratio", ">=", 1.5), "R-HOR-1": ("sky_min_q_std", ">=", 0.015),
    "R-REP-1": ("rep_p90", "<=", 0.60),
}
SCOPE = {                                      # 12.7 defaults: rules measured per kind
    "hq": ("R-CALM-1", "R-CALM-2", "R-FOCUS-1", "R-REP-1"),       # corp HQ views are exempt from R-HUE
    "street": ("R-SIL-1", "R-SIL-2", "R-DET-1", "R-DET-2", "R-CALM-1", "R-CALM-2", "R-HUE-1", "R-HUE-2", "R-REP-1"),
    "city": ("R-HUE-1", "R-HUE-2", "R-HOR-1", "R-REP-1"),
}


def r4(x):
    """Round to 1e-4 half up (12.8 parity rule 1). NaN / inf -> None."""
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return math.floor(x * 1e4 + 0.5) / 1e4


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return r4(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def dump_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(clean(obj), f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def luma(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def load_class(index_path, shape, class_map=None):
    """Saved Object Index pass -> uint8 class image of `shape` (h, w)."""
    idx = np.load(index_path)
    if idx.ndim == 3:
        idx = idx[..., 0]
    r = np.rint(idx).astype(np.int16)
    if r.shape != tuple(shape):
        im = Image.fromarray(r.astype(np.uint8)).resize((shape[1], shape[0]), Image.NEAREST)
        r = np.asarray(im).astype(np.int16)
    unknown = sorted(set(np.unique(r).tolist()) - set(CLASS_MAP))
    if unknown:
        raise ValueError("unmapped pass indices %s in %s" % (unknown, index_path))
    lut = np.zeros(256, np.uint8)
    for k, v in {**CLASS_MAP, **(class_map or {})}.items():
        lut[k] = v
    return lut[r], np.unique(r).tolist()


def write_id(cls, path):
    out = np.zeros(cls.shape + (3,), np.uint8)
    out[..., 0] = cls
    Image.fromarray(out, "RGB").save(path, optimize=True)


def landmark_masks(cls):
    lm = np.isin(cls, LANDMARK_CLASSES)
    if not lm.any():
        return lm, None, None
    ys, xs = np.nonzero(lm)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    gy, gx = int((y1 - y0) * GROW), int((x1 - x0) * GROW)
    box = np.zeros_like(lm)
    box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
    bg = box & np.isin(cls, BACKGROUND_CLASSES)
    return lm, bg, (int(x0), int(y0), int(x1), int(y1))


def _eta2(L, c):
    tot = float(L.var())
    if tot <= 0:
        return 0.0
    m = float(L.mean())
    return sum(float((c == k).sum()) * (float(L[c == k].mean()) - m) ** 2 for k in np.unique(c)) / L.size / tot


def alignment_score(L, cls):
    """Sanity check that the index pass belongs to this beauty plate: share of luma variance explained by the class
    image (eta squared, 2x downsampled) divided by the same with the classes shifted 25-40 px. Above 1 = aligned
    (post bloom and fog blur the edges, so 1.2-3.6 is typical)."""
    L2, c2 = L[::2, ::2], cls[::2, ::2]
    e0 = _eta2(L2, c2)
    sh = [_eta2(L2, np.roll(np.roll(c2, dy, 0), dx, 1)) for dy, dx in ((25, 25), (-25, 25), (25, -25), (-25, -25), (0, 40), (40, 0))]
    return e0 / max(float(np.mean(sh)), 1e-9)


def status_band(v, lo_pass, hi_pass, lo_warn, hi_warn):
    if lo_pass <= v <= hi_pass:
        return "pass"
    if lo_warn <= v <= hi_warn:
        return "warn"
    return "fail"


def rule_status(rule, value):
    if value is None:
        return "n/a"
    _, op, lim = COMP_RULES[rule]
    if op == ">=":
        return "pass" if value >= lim else "fail"
    if op == "<=":
        return "pass" if value <= lim else "fail"
    return "pass" if lim[0] <= value <= lim[1] else "fail"


def composition_spec(kind, view, box_norm):
    spec = {}
    if kind == "street":
        if view == "overview":
            spec["skyline"] = [0.0, 0.85]
            spec["facade"] = [0.0, 0.10, 1.0, 0.80]
    elif kind == "city":
        spec["skyline"] = [0.05, 0.40]
    return spec


def compute_values(beauty_path, cls, spec):
    """The values file content (not yet rounded) and the check statuses."""
    kind, view = spec["kind"], spec["view"]
    rgb = np.asarray(Image.open(beauty_path).convert("RGB"), np.float32) / 255.0
    L = luma(rgb)
    out = {"median": float(np.median(L)), "under_010": float((L < 0.10).mean()), "over_085": float((L > 0.85).mean()),
           "ratio_median": None, "ratio_mean": None, "ratio_peak": None}
    status, notes = {}, {}
    day = bool(spec.get("day"))
    sv = status_band(out["median"], *MEDIAN_PASS, *MEDIAN_WARN)
    if day:
        status["R-VAL-1"] = status["R-VAL-2"] = status["R-VAL-3"] = "n/a"
        notes["R-VAL-1"] = "day plate: median target 0.25 (3.7); recorded and reported only until the AD sets a day band"
    else:
        status["R-VAL-1"] = sv
        status["R-VAL-2"] = "pass" if UNDER_BAND[0] <= out["under_010"] <= UNDER_BAND[1] else "fail"
        status["R-VAL-3"] = "pass" if out["over_085"] <= OVER_MAX else "fail"

    box_norm = None
    if cls is not None:
        lm, bg, bbox = landmark_masks(cls)
        if bbox is None:
            status["landmark_ratio"] = "fail" if kind == "hq" else "n/a"
            notes["landmark_ratio"] = "landmark absent" if kind == "hq" else "no landmark pixels in frame"
        else:
            h, w = L.shape
            box_norm = [bbox[0] / w, bbox[1] / h, bbox[2] / w, bbox[3] / h]
            if bg is not None and bg.any():
                bgm = float(np.median(L[bg]))
                out["ratio_median"] = float(np.median(L[lm])) / max(bgm, 1e-4)
                out["ratio_mean"] = float(L[lm].mean()) / max(bgm, 1e-4)
                out["ratio_peak"] = float(np.percentile(L[lm], 99)) / max(bgm, 1e-4)
                rv = r4(out["ratio_median"])
                status["landmark_ratio"] = "pass" if RATIO_PASS[0] <= rv <= RATIO_PASS[1] else (
                    "warn" if rv > RATIO_PASS[1] else "fail")
                notes["landmark_ratio"] = ("ratio_median is gated; ratio_mean = mean(lm)/median(bg), "
                                           "ratio_peak = p99(lm)/median(bg) (post_tethys convention); landmark bbox px %s" % (list(bbox),))
            else:
                status["landmark_ratio"] = "n/a"
                notes["landmark_ratio"] = "empty local-background mask"
    else:
        status["landmark_ratio"] = "n/a"
        notes["landmark_ratio"] = ("no id pass: ratio_median is null" if kind != "street"
                                   else "street: no landmark expected in frame (12.8)")
    for k, v in (spec.get("extra_values") or {}).items():
        if out.get(k) is None:
            out[k] = v
    if spec.get("extra_values_note"):
        notes["landmark_ratio"] = (notes.get("landmark_ratio", "") + "; " + spec["extra_values_note"]).strip("; ")

    # 12.7 composition: measured on the beauty with pvc_metrics, only for the rules scoped to the kind
    m = PM.measure(beauty_path, composition_spec(kind, view, box_norm))
    rules = list(SCOPE[kind])
    if kind == "street" and view != "overview":
        rules = [r for r in rules if r not in ("R-SIL-1", "R-SIL-2")]          # skyline range only for the OVERVIEW (O-7)
    if "R-FOCUS-1" in rules and box_norm is not None:       # empty ring (landmark box fills the frame) -> n/a, never a crash
        Lw = PM.luma(PM.load_work(beauty_path))
        try:
            m.update(PM.landmark(Lw, np.ones(Lw.shape, bool), box_norm))
        except (IndexError, ValueError):
            notes["R-FOCUS-1"] = "empty ring: the landmark box fills the frame (n/a, 12.0 O-4)"
    comp = {r: None for r in COMP_RULES}
    for r in rules:
        key = COMP_RULES[r][0]
        v = m.get(key)
        if r == "R-FOCUS-1" and box_norm is None:
            v = None
        comp[r] = None if v is None else float(v)
        status[r] = rule_status(r, r4(comp[r]) if comp[r] is not None else None)
    for r in COMP_RULES:
        if r not in rules:
            status[r] = "n/a"
    if kind == "hq" and "R-FOCUS-1" in rules and box_norm is None:
        notes["R-FOCUS-1"] = "no id pass: landmark box unavailable"
    out["composition"] = comp
    report_only = ["R-CALM-1", "R-CALM-2"] if kind == "hq" else []          # AD ruling 2026-10-18 (12.7)
    baseline = sorted(k for k, v in status.items() if v == "fail" and k not in report_only)
    out["checks"] = {"status": status, "baseline": baseline, "report_only": report_only, "notes": notes,
                     "exempt": spec.get("exempt") or {"hover_cut": False, "red_seq": False, "flash": False},
                     "pre_accepted": spec.get("accepted") or []}
    out["inputs"] = {k: None for k in ("city.json", "net.json", "run_graph.json", "zoned.json", "derive_run.json")}
    return out, L


# ------------------------------------------------------------------ pose helpers
def pose_from_loc_tgt(loc, tgt, lens, shift_x, shift_y):
    """Rig convention: yaw 0 = north (+y), clockwise; pitch positive looking down; dist = |tgt - loc|."""
    d = [tgt[i] - loc[i] for i in range(3)]
    hz = math.hypot(d[0], d[1])
    return {"loc": list(loc), "tgt": list(tgt), "yaw": math.degrees(math.atan2(d[0], d[1])),
            "pitch": math.degrees(math.atan2(-d[2], hz)), "dist": math.sqrt(sum(x * x for x in d)),
            "lens": lens, "shift_x": shift_x, "shift_y": shift_y}


def full_camera(c):
    cam = {k: c[k] for k in ("loc", "tgt", "yaw", "pitch", "dist", "lens", "shift_x", "shift_y")}
    cam["ortho"] = False
    cam["zoom_dive"] = c.get("zoom_dive")
    cam["zoom_detail"] = c.get("zoom_detail")
    for k in ("loc_note", "yaw_note", "zoom_job"):
        if k in c:
            cam[k] = c[k]
    return cam


# ------------------------------------------------------------------ main
def build_plate(spec, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    stem = spec["stem"]
    im = Image.open(spec["beauty"])
    dst = os.path.join(out_dir, stem + ".png")
    if im.mode == "RGB" and im.format == "PNG":
        shutil.copyfile(spec["beauty"], dst)
    else:
        im.convert("RGB").save(dst, optimize=True)
    w, h = im.size
    cls, used = (None, None)
    align = None
    if spec.get("index"):
        cls, used = load_class(spec["index"], (h, w), {int(k): v for k, v in (spec.get("class_map") or {}).items()})
        write_id(cls, os.path.join(out_dir, stem + "_id.png"))
    vals, L = compute_values(dst, cls, spec)
    if cls is not None:
        align = alignment_score(L, cls)
        vals["checks"]["notes"]["id_alignment"] = (
            "class-variance share / shifted-class share = %s (above 1 = the index pass matches this beauty plate)" % r4(align))
    cap = {
        "version": 1, "stem": stem, "kind": spec["kind"], "view": spec["view"], "corp": spec.get("corp", ""),
        "look": spec.get("look"), "exempt": vals["checks"]["exempt"],
        "resolution": [w, h], "layout_seed": None, "run": None, "anim_t": None, "art_seeds": None,
        "camera": full_camera(spec["camera"]) if spec.get("camera") else None,
        "source": dict(spec.get("source") or {}, index_pass_indices=used),
        "pending": list(spec.get("pending") or []),
    }
    dump_json(os.path.join(out_dir, stem + "_capture.json"), cap)
    dump_json(os.path.join(out_dir, stem + "_values.json"), vals)
    return {"stem": stem, "vals": vals, "align": align, "has_id": cls is not None, "res": [w, h]}


if __name__ == "__main__":
    a = sys.argv[1:]
    out = os.path.normpath(os.path.join(HERE, ".."))
    if "--out" in a:
        out = a[a.index("--out") + 1]
    s = json.load(open(a[0], encoding="utf-8"))
    r = build_plate(s, out)
    print(r["stem"], "median", r4(r["vals"]["median"]), "ratio_median", r4(r["vals"]["ratio_median"]), "id", r["has_id"],
          "align", r4(r["align"]))
