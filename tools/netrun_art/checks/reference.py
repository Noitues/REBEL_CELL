"""Reference comparison: run the image checks on the art-pass golden inputs and compare with `rules_check.md`.

`--mode reference` of NA03_NA04_ANSWERS O-7: boxes, masks, crops, skyline ranges and facade bands come from the
art-pass `pvc_config.json`, and the view scopes are the reference ones (image id sets). The golden images are NOT in
this repo: pass the folder that holds them (`{C}/` in the config maps to it) on the command line.
The value band is the spec 12.1 band (one mode, build ruling O-3): rows whose R-VAL-1 verdict differs only
because of the band are listed as expected differences, not as mismatches.
"""
import glob
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .. import io
from . import image_checks as IC
from . import metrics as M
from .report import FAIL, NA, PASS, WARN, Record

NOT_AAA2 = {"c_dyn_ov", "c_v6", "p_city_main", "a_mainline_w3", "a_sb_hq"}
SIDE_IDS = {"c_aaa2r3", "c_proof", "c_dyn_ov", "p_sb_closed", "p_sb_reveal", "p_f0340"}
CITY_IDS = {"c_v6", "p_city_night", "p_city_main", "p_city_v1"}
RULE_SCOPE = {"R-SIL-1": "side", "R-SIL-2": "side", "R-DET-1": "side", "R-DET-2": "side",
              "R-CALM-1": "netrun", "R-CALM-2": "netrun", "R-HUE-1": "street_city", "R-HUE-2": "street_city",
              "R-FOCUS-1": "landmark", "R-HOR-1": "city", "R-REP-1": "all"}
RC_COLUMNS = ["R-SIL-1", "R-SIL-2", "R-CALM-1", "R-CALM-2", "R-DET-1", "R-DET-2", "R-HUE-1", "R-HUE-2",
              "R-VAL-1", "R-VAL-2", "R-VAL-3", "R-FOCUS-1", "R-HOR-1", "R-REP-1"]


def reference_scope(scope: str, k: str, spec: Dict[str, Any], has_landmark: bool, has_sky: bool) -> bool:
    """The reference `rule_applies` (run_proc_vs_custom.py, commit ded90765) on image id and config."""
    if scope == "all":
        return True
    if scope == "landmark":
        return has_landmark
    if scope == "side":
        return k in SIDE_IDS or spec.get("view") == "side"
    if scope == "street_city":
        return k in SIDE_IDS or k in CITY_IDS or spec.get("view") in ("side", "street_close")
    if scope == "netrun":
        return k not in CITY_IDS and not k.startswith("a_") and k != "p_tethys"
    if scope == "city":
        return k in CITY_IDS and has_sky
    return False


def collect(cfg_json: Dict[str, Any], concepts: str) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """`{id: spec-with-path}` for every golden image that exists, and the list of missing ones."""
    imgs: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []
    for pair in cfg_json["pairs"]:
        for k, spec in pair["images"].items():
            path = os.path.normpath(spec["path"].replace("{C}", concepts))
            if os.path.exists(path):
                imgs[k] = dict(spec, path=path)
            else:
                missing.append(f"{k}: {path}")
        for g in pair.get("globs", []):
            for p in sorted(glob.glob(g["pattern"])):
                if "thumb" in os.path.basename(p):
                    continue
                imgs["g_" + os.path.splitext(os.path.basename(p))[0]] = {
                    "role": g["role"], "path": p, "facade": g.get("facade", [0, 0, 1, 1])}
    return imgs, missing


def measure_image(k: str, spec: Dict[str, Any], cfg: Dict[str, Any]) -> List[Record]:
    """Check records of one golden image in reference mode (work-size image, config masks and boxes)."""
    comp = cfg["composition"]
    im = M.load_rgb(spec["path"], spec.get("crop"))
    rgb = M.work_array(im, comp["work_w"])
    valid = M.valid_mask(rgb.shape, spec.get("mask"))
    L = M.luma(rgb)
    mv = M.composition_metrics(rgb, valid, comp["constants"], spec.get("facade", [0, 0, 1, 1]),
                               spec.get("skyline"), spec.get("landmark"))
    recs = IC.evaluate_rules(
        mv, lambda rid, rule: (reference_scope(RULE_SCOPE[rid], k, spec, "lm_ratio" in mv, "sky_std" in mv), "reference scope"),
        cfg)
    stats = M.value_stats(L, valid, cfg["value"])
    recs += IC.value_band_records(stats, {"look": "aaa2" if k not in NOT_AAA2 else "reference-excluded"}, cfg)
    return recs


_CELL = re.compile(r"^(?:\*\*FAIL\*\*|FAIL|PASS|n/a)(?: (\S+))?$")


def parse_rules_check(text: str) -> Dict[str, Dict[str, Tuple[str, Optional[str]]]]:
    """`{image: {rule: (PASS|FAIL|n/a, value text)}}` from `rules_check.md`."""
    rows: Dict[str, Dict[str, Tuple[str, Optional[str]]]] = {}
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| image") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 2 + len(RC_COLUMNS):
            continue
        row = {}
        for col, cell in zip(RC_COLUMNS, cells[2:]):
            if cell == "n/a":
                row[col] = ("n/a", None)
                continue
            m = _CELL.match(cell)
            if not m:
                raise ValueError(f"bad cell {cell!r}")
            row[col] = ("FAIL" if "FAIL" in cell else "PASS", m.group(1))
        rows[cells[0]] = row
    return rows


def _fmt(v: float) -> str:
    return f"{v:.3f}" if abs(v) < 10 else f"{v:.0f}"


def compare(measured: Dict[str, List[Record]], rc: Dict[str, Dict[str, Tuple[str, Optional[str]]]]) -> Dict[str, Any]:
    """Compare our records with the reference rows.

    Per rule id: rows compared, matched, expected differences (R-VAL-1 band only) and mismatches. A mismatch is a
    different verdict class or a different printed value.
    """
    summary = {rid: {"compared": 0, "matched": 0, "expected": 0, "mismatch": 0} for rid in RC_COLUMNS}
    expected: List[str] = []
    mismatches: List[str] = []
    not_measured = [k for k in rc if k not in measured]
    for k, row in rc.items():
        if k not in measured:
            continue
        mine = {r["id"]: r for r in measured[k]}
        for rid in RC_COLUMNS:
            ref_status, ref_val = row[rid]
            r = mine[rid]
            s = summary[rid]
            s["compared"] += 1
            ours = "n/a" if r["status"] == NA else ("FAIL" if r["status"] == FAIL else "PASS")
            val = _fmt(r["value"]) if (r["value"] is not None and ours != "n/a") else None
            if ours == ref_status and val == ref_val:
                s["matched"] += 1
            elif rid == "R-VAL-1" and ref_status == "FAIL" and r["status"] in (PASS, WARN) and ref_val == val:
                s["expected"] += 1
                expected.append(f"{k} R-VAL-1 median {val}: RC FAIL (0.12-0.17), spec {r['status']} (band 0.11-0.17, warn to 0.09/0.19)")
            else:
                s["mismatch"] += 1
                mismatches.append(f"{k} {rid}: RC {ref_status} {ref_val}, ours {r['status']} {val}")
    return {"summary": summary, "expected": expected, "mismatches": mismatches, "not_measured": not_measured}


def run_reference(config_json_path: str, rc_path: str, concepts: str, cfg: Optional[Dict[str, Any]] = None,
                  ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Measure every golden image that exists and compare with `rules_check.md`. Returns `compare()` plus `missing`."""
    cfg = cfg or IC.load_config()
    imgs, missing = collect(io.load(config_json_path), concepts)
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = parse_rules_check(f.read())
    measured = {k: measure_image(k, s, cfg) for k, s in imgs.items() if ids is None or k in ids}
    out = compare(measured, rc)
    out["missing"] = missing
    out["measured"] = sorted(measured)
    return out


def summary_markdown(res: Dict[str, Any]) -> str:
    """Markdown comparison table (one row per check id) plus the expected differences and mismatches."""
    lines = ["| check id | rows compared | matched | expected differences | mismatches |", "|---|---|---|---|---|"]
    tot = {"compared": 0, "matched": 0, "expected": 0, "mismatch": 0}
    for rid in RC_COLUMNS:
        s = res["summary"][rid]
        lines.append(f"| {rid} | {s['compared']} | {s['matched']} | {s['expected']} | {s['mismatch']} |")
        for k in tot:
            tot[k] += s[k]
    lines.append(f"| total cells | {tot['compared']} | {tot['matched']} | {tot['expected']} | {tot['mismatch']} |")
    lines += ["", f"images measured {len(res['measured'])}; reference rows not measured {len(res['not_measured'])}: "
              + ", ".join(res["not_measured"])]
    if res.get("missing"):
        lines.append("images missing: " + "; ".join(res["missing"]))
    lines += ["", "Expected differences (band only):"] + [f"- {e}" for e in res["expected"]]
    lines += ["", "Mismatches:"] + [f"- {m}" for m in res["mismatches"]]
    return "\n".join(lines) + "\n"
