"""Image checks: 12.1 value band, 12.2 landmark ratio, 12.7 composition rules, renderer comparison.

Input is a capture folder holding `beauty.png`, `id.png` (R = class byte), optional `depth.png` (16-bit, BU x 100) and `capture.json` (CHECKS_SPEC 1.1; the
optional scope keys `kind, view, look, look_blend, corp, exempt{}` of NA03_NA04_ANSWERS O-1). Any PNG size is
accepted. Every threshold and tolerance comes from `composition.json`. PNG in, records out; no Blender or Godot.
"""
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

from .. import io
from . import metrics as M
from .report import FAIL, NA, PASS, WARN, Record, record

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "composition.json")
EXEMPT_KEYS = ("hover_cut", "red_seq", "flash")

Applies = Callable[[str, Dict[str, Any]], Tuple[bool, str]]


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """The `checks` block of `composition.json` (or of the file at `path`)."""
    return io.load(path or CONFIG_PATH)["checks"]


def _in(x: float, lo_hi: Sequence[float]) -> bool:
    return lo_hi[0] <= x <= lo_hi[1]


# ---------------------------------------------------------------- 12.1
def is_day(capture: Dict[str, Any], cfg: Dict[str, Any]) -> bool:
    """True for a day frame: `capture.json` `time == "day"` (default "night"). Only a capture without `time` (the
    concept plates) falls back to its stem being listed in `landmark_ratio.day_stems`."""
    t = capture.get("time")
    if t is None:
        return capture.get("stem") in cfg["landmark_ratio"].get("day_stems", [])
    return t == "day"


def exempt_reason(capture: Dict[str, Any]) -> str:
    """Why 12.1 does not apply to this capture (empty string = it applies)."""
    ex = capture.get("exempt") or {}
    for k in EXEMPT_KEYS:
        if ex.get(k):
            return f"exempt: {k}"
    look = capture.get("look")
    if look == "blend" or (0 < float(capture.get("look_blend", 0) or 0) < 1):
        return "look blend frame: reported only"
    return ""


def value_band_records(stats: Dict[str, float], capture: Dict[str, Any], cfg: Dict[str, Any]) -> List[Record]:
    """12.1 records R-VAL-1/2/3 from `value_stats` values and the capture scope keys."""
    c = cfg["value"]
    m, u, o = stats["median"], stats["under_010"], stats["over_085"]
    th1 = {"pass": c["median_pass"], "warn": c["median_warn"]}
    th2, th3 = c["under_010"], c["over_085_max"]
    why = exempt_reason(capture)
    look = capture.get("look")
    if not why and is_day(capture, cfg):
        why = "day frame: report only"
    if not why and look == "mainline":
        ok = _in(m, c["mainline_median"])
        return [record("R-VAL-1", PASS if ok else FAIL, m, c["mainline_median"], "mainline look: held to the capture median"),
                record("R-VAL-2", NA, u, th2, "mainline look"), record("R-VAL-3", NA, o, th3, "mainline look")]
    if not why and look != "aaa2":
        why = "capture.json has no look" if look is None else f"look {look}"
    if why:
        return [record("R-VAL-1", NA, m, th1, why), record("R-VAL-2", NA, u, th2, why), record("R-VAL-3", NA, o, th3, why)]
    if _in(m, c["median_pass"]):
        s1 = PASS
    elif any(_in(m, w) for w in c["median_warn"]):
        s1 = WARN
    else:
        s1 = FAIL
    return [record("R-VAL-1", s1, m, th1, ""),
            record("R-VAL-2", PASS if _in(u, th2) else FAIL, u, th2, ""),
            record("R-VAL-3", PASS if o <= th3 else FAIL, o, th3, "")]


# ---------------------------------------------------------------- 12.2
def landmark_ratio_record(L: np.ndarray, idx: Optional[np.ndarray], capture: Dict[str, Any],
                          cfg: Dict[str, Any]) -> Record:
    """12.2 record from native luma and the class array (None when there is no id.png)."""
    c = cfg["landmark_ratio"]
    th = {"pass": c["pass"], "warn_above": c["warn_above"]}
    if capture.get("view") == "hover":
        return record("12.2", NA, None, th, "hover frame exempt")
    if idx is None:
        return record("12.2", NA, None, th, "no id.png")
    st = M.landmark_stats(L, idx, c)
    if st["ratio"] is None and st["landmark"] is None:
        must = capture.get("kind") == c["absent_fail_kind"] and capture.get("view") in c["absent_fail_views"]
        return record("12.2", FAIL if must else NA, None, th, "landmark absent" if must else "no landmark in frame")
    if st["ratio"] is None:
        return record("12.2", NA, None, th, "empty local background")
    r = st["ratio"]
    note = f"landmark share {st['landmark_share']:.4f}"
    if is_day(capture, cfg):
        return record("12.2", NA, r, th, "report only (AD 2026-10-18): never a fail, never a baseline item; " + note)
    status = FAIL if r < c["pass"][0] else (WARN if r > c["warn_above"] else PASS)
    if status == WARN:
        note += _pre_accepted_note(r, capture, c, cfg["tolerance"]["renderer"]["lm_ratio"])
    return record("12.2", status, r, th, note)


def _pre_accepted_note(ratio: float, capture: Dict[str, Any], c: Dict[str, Any], tol: float) -> str:
    """Note for a 12.2 warn: pre-accepted when the capture's stem is listed and the ratio is within `tol` of it."""
    for e in c.get("pre_accepted", []):
        if capture.get("stem") == e["stem"]:
            if ratio <= e["value"] + tol:
                return f"; pre-accepted warn {e['value']} ({e['date']})"
            return f"; NEW: beyond the pre-accepted {e['value']} ({e['date']})"
    return ""


# ---------------------------------------------------------------- 12.6 route never occluded
def _erode(m: np.ndarray, r: int) -> np.ndarray:
    """Binary erosion by a (2r+1) square (art-pass `r2_occlusion.erode`): wipes out lamp posts, cables, antialiased edges."""
    out = m.copy()
    for k in range(1, r + 1):
        out[:, k:] &= m[:, :-k]
        out[:, :-k] &= m[:, k:]
    o2 = out.copy()
    for k in range(1, r + 1):
        o2[k:, :] &= out[:-k, :]
        o2[:-k, :] &= out[k:, :]
    return o2


def route_occlusion_record(ids_rgb: Optional[np.ndarray], cfg: Dict[str, Any],
                           depth_bu: Optional[np.ndarray] = None) -> Record:
    """12.6 "Route never occluded", counted by depth (PIPELINE_SPEC 12.0 / 12.6, art-pass `r2_occlusion.py`).

    `ids_rgb` is the id.png as (h, w, 3) float (R class, G room index, B layer); `depth_bu` is depth.png in BU (already
    divided by `depth_scale`), same size. Per visible route room (class 5 pixels with G > 0) the screen box is grown by
    `grow_px`. A pixel counts when it is an occluder class (city, class 2), inside the grown box, more than `near_bu`
    NEARER than the room front (median depth of the room's own pixels), not a route-column cut surface (class 2 with
    B >= `cut_layer_min`) and not an occlusion stub (G == `stub_room`, B == 0), and it survives an `erode_px` erosion
    of the mask. A neighbour beside the column is not nearer than the front, so it is not counted. Fails when the
    count exceeds `max_px`. n/a without id.png or depth.png.
    """
    c = cfg["route_occlusion"]
    th = {"max_px": c["max_px"], "grow_px": c["grow_px"], "near_bu": c["near_bu"], "erode_px": c["erode_px"]}
    if ids_rgb is None:
        return record("12.6.route", NA, None, th, "no id.png")
    cls = np.round(ids_rgb[..., 0])
    room = np.round(ids_rgb[..., 1])
    layer = np.round(ids_rgb[..., 2])
    rooms = np.isin(cls, c["room_classes"])
    if not rooms.any():
        return record("12.6.route", NA, None, th, "no visible route room")
    if not (rooms & (room > 0)).any():
        return record("12.6.route", NA, None, th, "id.png carries no room indices (G = 0)")
    if depth_bu is None:
        return record("12.6.route", NA, None, th, "no depth.png")
    h, w = cls.shape
    g = int(c["grow_px"])
    occ = np.isin(cls, c["occluder_classes"]) & (layer < c["cut_layer_min"]) & ~((room == c["stub_room"]) & (layer == 0))
    hit = np.zeros((h, w), bool)
    hit_rooms: List[int] = []
    for rid in sorted(int(v) for v in np.unique(room[rooms & (room > 0)])):
        mine = rooms & (room == rid)
        ys, xs = np.nonzero(mine)
        y0, y1 = max(0, ys.min() - g), min(h, ys.max() + 1 + g)
        x0, x1 = max(0, xs.min() - g), min(w, xs.max() + 1 + g)
        front = float(np.median(depth_bu[mine]))
        sub = occ[y0:y1, x0:x1] & (depth_bu[y0:y1, x0:x1] < front - c["near_bu"])
        full = np.zeros((h, w), bool)
        full[y0:y1, x0:x1] = sub
        full = _erode(full, int(c["erode_px"]))
        if full.any():
            hit_rooms.append(rid)
            hit |= full
    n = int(hit.sum())
    note = "no occluder in any room box" if n == 0 else "occluded rooms " + ",".join(str(r) for r in hit_rooms[:8])
    return record("12.6.route", FAIL if n > c["max_px"] else PASS, n, th, note)


# ---------------------------------------------------------------- 12.7
def scope_applies(rule: Dict[str, Any], capture: Dict[str, Any], has_landmark: bool, cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """Scope decision for a rule from the capture scope keys (O-1). A scope key the capture lacks is n/a."""
    sc = rule.get("scope", {})
    if sc.get("day_report_only") and is_day(capture, cfg):
        return False, "day frame: report only"
    for key in ("kind", "view"):
        if key in sc:
            v = capture.get(key)
            if v is None:
                return False, f"capture.json has no {key}"
            if v not in sc[key]:
                return False, f"{key} {v} out of scope"
    if sc.get("landmark") and not has_landmark:
        return False, "no landmark in frame"
    return True, ""


def evaluate_rules(metric_values: Dict[str, float], applies: Applies, cfg: Dict[str, Any]) -> List[Record]:
    """One record per 12.7 rule. `applies(rule_id, rule)` returns `(bool, note)`. NaN or missing metric is n/a."""
    out: List[Record] = []
    for rid, rule in cfg["composition"]["rules"].items():
        ok, note = applies(rid, rule)
        val = metric_values.get(rule["metric"])
        if not ok:
            out.append(record(rid, NA, val, rule["value"], note))
            continue
        if M.is_nan(val):
            out.append(record(rid, NA, None, rule["value"], "metric not defined for this frame"))
            continue
        t = rule["value"]
        good = _in(val, t) if rule["op"] == "between" else (val <= t if rule["op"] == "<=" else val >= t)
        out.append(record(rid, PASS if good else FAIL, val, t, rule["rule"]))
    return out


def default_ranges(capture: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[Optional[List[float]], List[float]]:
    """Default skyline range and facade band (NA03_NA04_ANSWERS O-7; 12.7: street views measure R-REP-1 in the facade band only)."""
    comp = cfg["composition"]
    kind, view = capture.get("kind"), capture.get("view")
    sky = None
    if kind == "street" and view == "overview":
        sky = comp["skyline"]["street"]
    elif kind == "city":
        sky = comp["skyline"]["city"]
    facade = comp["facade"]["street_overview"] if kind == "street" else comp["facade"]["default"]
    return sky, facade


# ---------------------------------------------------------------- capture folder
def read_capture(folder: str) -> Dict[str, Any]:
    """`capture.json` of a folder ({} when absent)."""
    p = os.path.join(folder, "capture.json")
    return io.load(p) if os.path.exists(p) else {}


def check_capture_folder(folder: str, cfg: Optional[Dict[str, Any]] = None,
                         thumb_path: Optional[str] = None) -> Tuple[List[Record], Dict[str, float]]:
    """Run 12.1, 12.2, 12.6 route and 12.7 on one capture folder. Returns `(records, measured values)`.

    The measured values (`median`, `under_010`, `over_085`, `ratio`, and the 12.7 metrics) feed `compare_renderers`.
    """
    cfg = cfg or load_config()
    capture = read_capture(folder)
    im = M.load_rgb(os.path.join(folder, "beauty.png"))
    recs: List[Record] = []
    res = capture.get("resolution")
    if res is not None and [int(res[0]), int(res[1])] != [im.width, im.height]:
        recs.append(record("12.0", FAIL, [im.width, im.height], res, "beauty.png size differs from capture.json resolution"))
    L = M.luma(M.to_array(im))
    stats = M.value_stats(L, None, cfg["value"])
    recs += value_band_records(stats, capture, cfg)
    idx = None
    ids_rgb = None
    ip = os.path.join(folder, "id.png")
    if os.path.exists(ip):
        raw = np.asarray(Image.open(ip).convert("RGB")).astype(np.float32)
        ids_rgb = np.stack([M.resize_ids(raw[..., i], im.size) for i in range(3)], axis=-1)
        idx = ids_rgb[..., 0]
    depth_bu = None
    dp = os.path.join(folder, "depth.png")
    if os.path.exists(dp):
        raw_d = np.asarray(Image.open(dp)).astype(np.float32)
        if raw_d.ndim == 3:
            raw_d = raw_d[..., 0]
        depth_bu = M.resize_ids(raw_d, im.size) / float(cfg["route_occlusion"]["depth_scale"])
    recs.append(landmark_ratio_record(L, idx, capture, cfg))
    recs.append(route_occlusion_record(ids_rgb, cfg, depth_bu))
    lm_stats = M.landmark_stats(L, idx, cfg["landmark_ratio"]) if idx is not None else {"ratio": None}
    box = M.box_from_mask(M.class_mask(idx, cfg["landmark_ratio"]["classes_landmark"])) if idx is not None else None
    sky, facade = default_ranges(capture, cfg)
    wrgb = M.work_array(im, cfg["composition"]["work_w"])
    valid = np.ones(wrgb.shape[:2], bool)
    mv = M.composition_metrics(wrgb, valid, cfg["composition"]["constants"], facade, sky, box)
    recs += evaluate_rules(mv, lambda rid, rule: scope_applies(rule, capture, box is not None, cfg), cfg)
    measured = dict(stats)
    measured["ratio"] = lm_stats["ratio"]
    measured.update(mv)
    if thumb_path:
        M.thumbnail(im, cfg["landmark_ratio"]["thumb_w"]).save(thumb_path)
    return recs, measured


def compare_renderers(a: Dict[str, float], b: Dict[str, float], cfg: Dict[str, Any],
                      prefix: str = "RENDERER") -> List[Record]:
    """Compare two measured-value dicts (Blender golden `a`, Godot capture `b`) with `tolerance.renderer`.

    Absolute tolerances: median, under_010, over_085, lm_ratio (applies to `ratio` and `lm_ratio`), and the
    `absolute` map; every other 12.7 metric uses the `relative` tolerance of the larger magnitude.
    """
    tol = cfg["tolerance"]["renderer"]
    absolute = {"median": tol["median"], "under_010": tol["under_010"], "over_085": tol["over_085"],
                "ratio": tol["lm_ratio"], "lm_ratio": tol["lm_ratio"]}
    absolute.update(tol["absolute"])
    out: List[Record] = []
    for k in sorted(set(a) & set(b)):
        va, vb = a[k], b[k]
        if M.is_nan(va) or M.is_nan(vb) or isinstance(va, (list, dict)) or k.endswith("_tiles"):
            continue
        d = abs(float(va) - float(vb))
        if k in absolute:
            lim, kind = absolute[k], "abs"
        else:
            lim, kind = tol["relative"] * max(abs(float(va)), abs(float(vb)), 1e-9), "rel"
        out.append(record(f"{prefix}.{k}", PASS if d <= lim else FAIL, d, lim, f"{kind} tolerance; a={float(va):.4f} b={float(vb):.4f}"))
    return out


def list_captures(root: str) -> List[Tuple[str, str]]:
    """`(name, folder)` pairs under `root`: the folder itself when it holds `beauty.png`, else its subfolders."""
    if os.path.exists(os.path.join(root, "beauty.png")):
        return [(os.path.basename(os.path.normpath(root)), root)]
    out = []
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "beauty.png")):
            out.append((n, p))
    return out
