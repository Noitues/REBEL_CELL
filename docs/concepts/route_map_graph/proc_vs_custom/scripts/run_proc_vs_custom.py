"""Procedural vs custom: metrics tables and comparison sheets, in one command.

    python docs/concepts/route_map_graph/proc_vs_custom/scripts/run_proc_vs_custom.py [--only p1_street,p3_city]

Reads pvc_config.json next to this file, measures every image that exists (CPU only,
PIL + numpy), and writes into proc_vs_custom/:
- sheet_<pair>.jpg            the comparison sheet (about 2400 px wide)
- metrics/<pair>.csv / .md    one row per image
- metrics/METRICS.md          every table in one file (linked from COMPARISON.md)
- metrics/all_metrics.json    raw numbers, including the top-6 hue clusters
- metrics/rules_check.md      the proposed generator rules checked against every image
Missing optional images are skipped and listed, so it can be re-run as new renders land.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pvc_metrics as M  # noqa: E402

OUT = os.path.dirname(HERE)
CONCEPTS = os.path.normpath(os.path.join(OUT, "..", ".."))
SHEET_W = 2400
PAD = 20
ROLE_COL = {"custom": (255, 176, 64), "procedural": (80, 220, 255), "anchor": (190, 255, 120)}
BG = (14, 13, 18)
FG = (225, 225, 230)
DIM = (140, 140, 150)

# Proposed generator rules with the metric that tests them (see COMPARISON.md).
# Each: id, text, metric key, op, threshold, which roles/views it applies to.
RULES = [
    ("R-SIL-1", "lit-mass skyline std >= 0.15 frame heights", "lit_std", ">=", 0.15, "side"),
    ("R-SIL-2", "lit-mass skyline std >= 0.08 in every 1/4-frame window", "lit_min_q_std", ">=", 0.08, "side"),
    ("R-CALM-1", "netrun views: detail CV (64 px tiles) 0.45-0.85", "detail_cv", "between", (0.45, 0.85), "netrun"),
    ("R-CALM-2", "netrun views: calm tiles 12-32 %", "calm_share", "between", (0.12, 0.32), "netrun"),
    ("R-DET-1", "street: mean Sobel >= 0.028", "sobel_mean", ">=", 0.028, "side"),
    ("R-DET-2", "street: >= 450 bright blobs per MP", "blobs_per_mp", ">=", 450, "side"),
    ("R-HUE-1", "street/city: hue entropy >= 3.8 bits", "hue_entropy_bits", ">=", 3.8, "street_city"),
    ("R-HUE-2", "street/city: top hue cluster <= 45 %", "hue_top_share", "<=", 0.45, "street_city"),
    ("R-VAL-1", "AAA-2: median luma 0.12-0.17", "median", "between", (0.12, 0.17), "aaa2"),
    ("R-VAL-2", "AAA-2: 25-40 % of pixels under 0.10", "under_010", "between", (0.25, 0.40), "aaa2"),
    ("R-VAL-3", "AAA-2: at most 2.5 % over 0.85", "over_085", "<=", 0.025, "aaa2"),
    ("R-FOCUS-1", "landmark mean luma >= 1.5x its ring", "lm_ratio", ">=", 1.5, "landmark"),
    ("R-HOR-1", "city horizon: built-top std >= 0.015 in every 1/4 window", "sky_min_q_std", ">=", 0.015, "city"),
    ("R-REP-1", "facade tile autocorr p90 <= 0.60 (guard)", "rep_p90", "<=", 0.60, "all"),
]
# Images rendered in the AAA-2 look (the r3 value band applies). Glob hits (g_*) are AAA-2 kit renders.
NOT_AAA2 = {"c_dyn_ov", "c_v6", "p_city_main", "a_mainline_w3", "a_sb_hq"}
SIDE_IDS = {"c_aaa2r3", "c_proof", "c_dyn_ov", "p_sb_closed", "p_sb_reveal", "p_f0340"}
CITY_IDS = {"c_v6", "p_city_night", "p_city_main", "p_city_v1"}


def font(size: int, bold: bool = False):
    names = ["consolab.ttf", "arialbd.ttf"] if bold else ["consola.ttf", "arial.ttf"]
    for n in names:
        p = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def resolve(p: str) -> str:
    return os.path.normpath(p.replace("{C}", CONCEPTS))


def collect(pair: dict):
    imgs, missing = {}, []
    for k, spec in pair["images"].items():
        path = resolve(spec["path"])
        if os.path.exists(path):
            imgs[k] = dict(spec, path=path)
        elif spec.get("optional"):
            missing.append(f"{k}: {path}")
        else:
            missing.append(f"{k} (REQUIRED): {path}")
    for g in pair.get("globs", []):
        for p in sorted(glob.glob(g["pattern"])):
            if "thumb" in os.path.basename(p):
                continue
            k = "g_" + os.path.splitext(os.path.basename(p))[0]
            imgs[k] = {"role": g["role"], "label": g["label_prefix"] + os.path.basename(p), "path": p,
                       "facade": g.get("facade", [0, 0, 1, 1])}
    return imgs, missing


def fmt(v, kind="f3"):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "-"
    if kind == "pct":
        return f"{v * 100:.1f}%"
    if kind == "f2":
        return f"{v:.2f}"
    if kind == "f4":
        return f"{v:.4f}"
    return f"{v:.3f}"


COLS = [
    ("median", "median", "f3"), ("<0.10", "under_010", "pct"), (">0.85", "over_085", "pct"),
    ("lm ratio", "lm_ratio", "f2"), ("lm p95r", "lm_p95_ratio", "f2"),
    ("sobel", "sobel_mean", "f4"), ("HF up", "hf_upper", "f3"), ("HF low", "hf_lower", "f3"),
    ("detail CV", "detail_cv", "f2"), ("calm", "calm_share", "pct"),
    ("hue H", "hue_entropy_bits", "f2"), ("chroma", "chroma_share", "pct"),
    ("rep med", "rep_median", "f2"), ("rep p90", "rep_p90", "f2"), ("tiled", "rep_tiled_share", "pct"),
    ("sky std", "sky_std", "f3"), ("sky minQ", "sky_min_q_std", "f3"),
    ("lit std", "lit_std", "f3"), ("lit minQ", "lit_min_q_std", "f3"),
    ("blobs/MP", "blobs_per_mp", "f2"), ("focal", "focal_conc", "pct"),
]


def hue_str(r):
    return " ".join(f"{c['hue_deg']:.0f}°:{c['share'] * 100:.0f}%" for c in r.get("clusters", []))


def write_tables(pair, imgs, res, mdir):
    rows = []
    for k in imgs:
        r = res[k]
        rows.append([k, imgs[k]["role"]] + [fmt(r.get(key), kd) for _, key, kd in COLS] + [hue_str(r)])
    head = ["id", "role"] + [c[0] for c in COLS] + ["top-6 hues (deg:share)"]
    with open(os.path.join(mdir, pair["id"] + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    md = [f"### {pair['title']}", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    md += ["| " + " | ".join(r) + " |" for r in rows]
    md += ["", "Images:", ""]
    md += [f"- `{k}`: {imgs[k]['label']} (`{os.path.relpath(imgs[k]['path'], OUT) if imgs[k]['path'].startswith(CONCEPTS) else imgs[k]['path']}`)"
           + (f"; landmark = {imgs[k].get('landmark_name')}" if imgs[k].get("landmark_name") else "") for k in imgs]
    text = "\n".join(md) + "\n"
    with open(os.path.join(mdir, pair["id"] + ".md"), "w", encoding="utf-8") as f:
        f.write(text)
    return text


def rule_applies(scope, k, spec, r):
    if scope == "all":
        return True
    if scope == "aaa2":
        return k not in NOT_AAA2
    if scope == "landmark":
        return "lm_ratio" in r
    if scope == "side":
        return k in SIDE_IDS
    if scope == "street_city":
        return k in SIDE_IDS or k in CITY_IDS
    if scope == "netrun":
        return k not in CITY_IDS and not k.startswith("a_") and k != "p_tethys"
    if scope == "city":
        return k in CITY_IDS and "sky_std" in r
    return False


def check_rules(all_res, all_specs):
    lines = ["# Proposed rules checked against every image", "",
             "Generated by `run_proc_vs_custom.py`. PASS / FAIL per image with the measured value; "
             "`n/a` = the rule does not apply to that view.", "", "Rules:", ""]
    lines += [f"- **{rid}**: {text}" for rid, text, *_ in RULES]
    lines += ["", "| image | role | " + " | ".join(r[0] for r in RULES) + " |", "|" + "---|" * (2 + len(RULES))]
    table = {k: [] for k in all_res}
    for rid, text, key, op, thr, scope in RULES:
        for k, r in all_res.items():
            cells = table[k]
            if key == "hf_lower_vs_upper":
                val = r["hf_lower"] / r["hf_upper"] if r.get("hf_upper") else float("nan")
            else:
                val = r.get(key, float("nan"))
            if not rule_applies(scope, k, all_specs[k], r) or val is None or np.isnan(val):
                cells.append("n/a")
                continue
            ok = (thr[0] <= val <= thr[1]) if op == "between" else (val <= thr if op == "<=" else val >= thr)
            cells.append(("PASS " if ok else "**FAIL** ") + (f"{val:.3f}" if abs(val) < 10 else f"{val:.0f}"))
    for k, cells in table.items():
        lines.append(f"| {k} | {all_specs[k]['role']} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- sheet drawing
def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    sw, sh = im.size
    s = max(w / sw, h / sh)
    im = im.resize((max(w, int(sw * s + 0.5)), max(h, int(sh * s + 0.5))), Image.LANCZOS)
    x0 = (im.size[0] - w) // 2
    y0 = (im.size[1] - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def label_band(d, x, y, w, text, role):
    col = ROLE_COL.get(role, FG)
    d.rectangle([x, y, x + 8, y + 26], fill=col)
    d.text((x + 16, y + 2), text, font=font(20, True), fill=col)


def analysis_panel(spec, r, w):
    """Luma map with the measured structures drawn on it, plus the palette swatches."""
    src = M.open_src(spec["path"], spec.get("crop"))
    sw, sh = src.size
    h = int(w * sh / sw)
    lum = M.luma(np.asarray(src.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255.0)
    g = (np.clip(lum, 0, 1) ** 0.8 * 255).astype(np.uint8)
    im = Image.fromarray(np.stack([g, g, g], -1))
    d = ImageDraw.Draw(im)
    for b in spec.get("mask") or []:
        d.rectangle([b[0] * w, b[1] * h, b[2] * w, b[3] * h], fill=(40, 0, 0))
    if spec.get("facade") and spec["facade"] != [0, 0, 1, 1]:
        b = spec["facade"]
        d.rectangle([b[0] * w, b[1] * h, b[2] * w - 1, b[3] * h - 1], outline=(255, 90, 200), width=1)
    if spec.get("landmark"):
        b = spec["landmark"]
        d.rectangle([b[0] * w, b[1] * h, b[2] * w, b[3] * h], outline=(255, 255, 0), width=2)
    if "profile" in r:
        prof = r["profile"]
        y1 = r["range"][1]
        n = len(prof)
        pts = [(i * w / n, (y1 - prof[i]) * h) for i in range(0, n, 2)]
        d.line(pts, fill=(0, 255, 120), width=2)
        pl = r["profile_lit"]
        pts = [(i * w / n, (y1 - pl[i]) * h) for i in range(0, n, 2)]
        d.line(pts, fill=(255, 150, 0), width=2)
    # palette strip
    ph = 40
    out = Image.new("RGB", (w, h + ph + 4), BG)
    out.paste(im, (0, 0))
    dd = ImageDraw.Draw(out)
    x = 0
    for c in r.get("clusters", []):
        cw = max(30, int(w * c["share"]))
        cw = min(cw, w - x)
        if cw <= 0:
            break
        dd.rectangle([x, h + 4, x + cw - 2, h + ph], fill=tuple(c["rgb"]))
        dd.text((x + 3, h + 8), f"{c['hue_deg']:.0f}°", font=font(13), fill=(0, 0, 0))
        dd.text((x + 3, h + 22), f"{c['share'] * 100:.0f}%", font=font(13), fill=(0, 0, 0))
        x += cw
    return out


def make_sheet(pair, imgs, res, missing, path_out):
    tiles = []   # (y, image) pieces, built top-down on a tall canvas then cropped
    canvas = Image.new("RGB", (SHEET_W, 9000), BG)
    d = ImageDraw.Draw(canvas)
    y = PAD
    d.text((PAD, y), pair["title"], font=font(34, True), fill=FG)
    y += 46
    d.text((PAD, y), "Amber = custom (hand-built). Cyan = procedural. Same pixel scale in each row. "
           "Analysis strip: luma map; yellow box = landmark; green line = built-mass top (texture); orange line = lit-mass top; pink box = facade band; "
           "red = masked UI.", font=font(17), fill=DIM)
    y += 36
    colw = (SHEET_W - 3 * PAD) // 2
    for row in pair["rows"]:
        hs = []
        for i, k in enumerate(row):
            if k not in imgs:
                d.text((PAD + i * (colw + PAD), y + 30), f"missing: {k}", font=font(20), fill=(255, 80, 80))
                hs.append(60)
                continue
            src = M.open_src(imgs[k]["path"], imgs[k].get("crop"))
            h = int(colw * src.size[1] / src.size[0])
            label_band(d, PAD + i * (colw + PAD), y, colw, imgs[k]["label"], imgs[k]["role"])
            canvas.paste(src.resize((colw, h), Image.LANCZOS), (PAD + i * (colw + PAD), y + 32))
            hs.append(h + 32)
        y += max(hs) + PAD
    # crops
    crops = pair.get("crops") or []
    if crops:
        n = len(crops)
        cw = (SHEET_W - (n + 1) * PAD) // n
        d.text((PAD, y), "Matched detail crops (top = custom, bottom = procedural)", font=font(24, True), fill=FG)
        y += 36
        hmax = 0
        for i, c in enumerate(crops):
            x = PAD + i * (cw + PAD)
            keys = list(c["boxes"].keys())
            d.text((x, y), c["name"], font=font(20, True), fill=FG)
            yy = y + 28
            b0 = c["boxes"][keys[0]]
            k0 = keys[0]
            if k0 not in imgs:
                continue
            s0 = M.open_src(imgs[k0]["path"], imgs[k0].get("crop"))
            asp = ((b0[3] - b0[1]) * s0.size[1]) / ((b0[2] - b0[0]) * s0.size[0])
            ch = int(cw * min(max(asp, 0.45), 0.62))   # one cell height per row keeps the sheet compact
            for k in keys:
                if k not in imgs:
                    continue
                s = M.open_src(imgs[k]["path"], imgs[k].get("crop"))
                b = c["boxes"][k]
                W, H = s.size
                piece = s.crop((int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H)))
                canvas.paste(fit_cover(piece, cw, ch), (x, yy))
                role = imgs[k]["role"]
                d.rectangle([x, yy, x + cw - 1, yy + ch - 1], outline=ROLE_COL[role], width=3)
                d.text((x + 8, yy + 6), "CUSTOM" if role == "custom" else "PROCEDURAL", font=font(16, True),
                       fill=ROLE_COL[role])
                yy += ch + 8
            hmax = max(hmax, yy - y)
        y += hmax + PAD
    # analysis strip
    mains = [k for row in pair["rows"] for k in row if k in imgs]
    d.text((PAD, y), "Analysis", font=font(24, True), fill=FG)
    y += 34
    aw = (SHEET_W - (len(mains) + 1) * PAD) // max(1, len(mains))
    aw = min(aw, 780)
    hmax = 0
    for i, k in enumerate(mains):
        p = analysis_panel(imgs[k], res[k], aw)
        x = PAD + i * (aw + PAD)
        canvas.paste(p, (x, y))
        r = res[k]
        t = [f"{k}  ({imgs[k]['role']})",
             f"median {fmt(r['median'])}  <0.10 {fmt(r['under_010'], 'pct')}  >0.85 {fmt(r['over_085'], 'pct')}",
             f"landmark/ring {fmt(r.get('lm_ratio'), 'f2')}  focal conc {fmt(r['focal_conc'], 'pct')}",
             f"sobel {fmt(r['sobel_mean'], 'f4')}  HF up {fmt(r['hf_upper'])} / low {fmt(r['hf_lower'])}",
             f"hue entropy {fmt(r['hue_entropy_bits'], 'f2')} bits  chroma {fmt(r['chroma_share'], 'pct')}",
             f"repetition med {fmt(r['rep_median'], 'f2')}  p90 {fmt(r['rep_p90'], 'f2')}  tiled {fmt(r['rep_tiled_share'], 'pct')}",
             f"skyline std {fmt(r.get('sky_std'))} (min 1/4 {fmt(r.get('sky_min_q_std'))})  "
             f"lit {fmt(r.get('lit_std'))} (min 1/4 {fmt(r.get('lit_min_q_std'))})",
             f"bright blobs/MP {fmt(r['blobs_per_mp'], 'f2')}  detail CV {fmt(r['detail_cv'], 'f2')}  "
             f"calm tiles {fmt(r['calm_share'], 'pct')}"]
        ty = y + p.size[1] + 6
        for line in t:
            d.text((x, ty), line, font=font(16), fill=ROLE_COL.get(imgs[k]["role"], FG) if line is t[0] else FG)
            ty += 21
        hmax = max(hmax, ty - y)
    y += hmax + PAD
    # compact table of every image in the pair
    d.text((PAD, y), "All measured images in this pair (metrics/" + pair["id"] + ".md has the full table)",
           font=font(22, True), fill=FG)
    y += 32
    keycols = [("median", "median", "f3"), ("<0.10", "under_010", "pct"), (">0.85", "over_085", "pct"),
               ("lm", "lm_ratio", "f2"), ("sobel", "sobel_mean", "f4"), ("HFup", "hf_upper", "f3"),
               ("HFlow", "hf_lower", "f3"), ("detCV", "detail_cv", "f2"), ("calm", "calm_share", "pct"), ("hueH", "hue_entropy_bits", "f2"), ("rep90", "rep_p90", "f2"),
               ("tiled", "rep_tiled_share", "pct"), ("skyStd", "sky_std", "f3"), ("litStd", "lit_std", "f3"), ("litMinQ", "lit_min_q_std", "f3"),
               ("focal", "focal_conc", "pct")]
    hdr = f"{'id':<26}" + "".join(f"{c[0]:>9}" for c in keycols)
    d.text((PAD, y), hdr, font=font(17, True), fill=DIM)
    y += 24
    for k in imgs:
        line = f"{k[:25]:<26}" + "".join(f"{fmt(res[k].get(c[1]), c[2]):>9}" for c in keycols)
        d.text((PAD, y), line, font=font(17), fill=ROLE_COL.get(imgs[k]["role"], FG))
        y += 22
    if missing:
        y += 6
        d.text((PAD, y), "Not found (skipped): " + "; ".join(os.path.basename(m) for m in missing), font=font(15),
               fill=(255, 120, 120))
        y += 22
    y += PAD
    canvas.crop((0, 0, SHEET_W, y)).save(path_out, quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma list of pair ids")
    ap.add_argument("--no-sheets", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "pvc_config.json"), encoding="utf-8"))
    mdir = os.path.join(OUT, "metrics")
    os.makedirs(mdir, exist_ok=True)
    only = set(x for x in a.only.split(",") if x)
    all_json, all_md, all_res, all_specs = {}, [], {}, {}
    for pair in cfg["pairs"]:
        if only and pair["id"] not in only:
            continue
        imgs, missing = collect(pair)
        res = {}
        for k, spec in imgs.items():
            print(f"[{pair['id']}] measuring {k}", flush=True)
            res[k] = M.measure(spec["path"], spec)
        all_md.append(write_tables(pair, imgs, res, mdir))
        if missing:
            all_md.append("Skipped (not found): " + "; ".join(missing) + "\n")
        for k in res:
            all_res[k] = res[k]
            all_specs[k] = imgs[k]
            all_json[k] = {kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for kk, vv in res[k].items()
                           if kk not in ("profile", "profile_lit")}
            all_json[k]["label"] = imgs[k]["label"]
            all_json[k]["path"] = imgs[k]["path"]
            all_json[k]["pair"] = pair["id"]
        if not a.no_sheets:
            out = os.path.join(OUT, f"sheet_{pair['id']}.jpg")
            make_sheet(pair, imgs, res, missing, out)
            print("wrote", out, flush=True)
    if not only:
        with open(os.path.join(mdir, "METRICS.md"), "w", encoding="utf-8") as f:
            f.write("# Metrics, every pair\n\nGenerated by `scripts/run_proc_vs_custom.py`; definitions in "
                    "`scripts/pvc_metrics.py` (module docstring).\n\n" + "\n".join(all_md))
        with open(os.path.join(mdir, "all_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(all_json, f, indent=1)
        with open(os.path.join(mdir, "rules_check.md"), "w", encoding="utf-8") as f:
            f.write(check_rules(all_res, all_specs))
    print("done")


if __name__ == "__main__":
    main()
