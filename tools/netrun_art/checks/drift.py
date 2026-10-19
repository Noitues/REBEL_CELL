"""Drift compare of our image checks against golden plates (PIPELINE_SPEC 12.8, read-only on the plates).

    python -m netrun_art.checks.drift PLATES_DIR --work WORK_DIR --out DRIFT.md

`PLATES_DIR` holds `<stem>.png`, `<stem>_id.png`, `<stem>_capture.json`, `<stem>_values.json` (the plate files are
only read; the check triple is copied into `WORK_DIR/<stem>/`). Run from the `tools` folder. Image values only: the
derive fields of a concept plate are null. Each value is held to `checks.tolerance.renderer`.
"""
import argparse
import os
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

from .. import io
from . import image_checks as IC

Row = Dict[str, Any]
# plate values.json key -> (our check id, status key in the plate's checks.status)
VALUE_CHECKS = {"median": ("R-VAL-1", "R-VAL-1"), "under_010": ("R-VAL-2", "R-VAL-2"),
                "over_085": ("R-VAL-3", "R-VAL-3"), "ratio": ("12.2 ratio", "landmark_ratio")}


def list_stems(plates_dir: str) -> List[str]:
    """Plate stems (sorted) that have a beauty, id and capture file."""
    out = []
    for n in sorted(os.listdir(plates_dir)):
        if n.endswith("_capture.json"):
            stem = n[: -len("_capture.json")]
            if os.path.exists(os.path.join(plates_dir, stem + ".png")) and \
                    os.path.exists(os.path.join(plates_dir, stem + "_id.png")):
                out.append(stem)
    return out


def _stage(plates_dir: str, work_dir: str, stem: str) -> str:
    """Copy one plate's triple into a capture folder under `work_dir`."""
    folder = os.path.join(work_dir, stem)
    os.makedirs(folder, exist_ok=True)
    shutil.copyfile(os.path.join(plates_dir, stem + ".png"), os.path.join(folder, "beauty.png"))
    shutil.copyfile(os.path.join(plates_dir, stem + "_id.png"), os.path.join(folder, "id.png"))
    shutil.copyfile(os.path.join(plates_dir, stem + "_capture.json"), os.path.join(folder, "capture.json"))
    return folder


def _fmt(v: Any) -> str:
    return "-" if v is None else f"{float(v):.4f}"


def drift_rows(plates_dir: str, work_dir: str, cfg: Optional[Dict[str, Any]] = None,
               stems: Optional[List[str]] = None) -> Tuple[List[Row], List[str]]:
    """Rows `{plate, check, ours, theirs, delta, tol, status, verdict}` for every plate, and the list of stems run."""
    cfg = cfg or IC.load_config()
    tol = cfg["tolerance"]["renderer"]
    rules = cfg["composition"]["rules"]
    rows: List[Row] = []
    done: List[str] = []
    for stem in stems or list_stems(plates_dir):
        folder = _stage(plates_dir, work_dir, stem)
        recs, measured = IC.check_capture_folder(folder, cfg)
        status = {r["id"]: r for r in recs}
        vpath = os.path.join(plates_dir, stem + "_values.json")
        theirs_all = io.load(vpath) if os.path.exists(vpath) else None
        checks = (theirs_all or {}).get("checks", {})
        baseline = set(checks.get("baseline", []))
        done.append(stem)

        def add(check: str, ours: Any, theirs: Any, rec_id: str, theirs_key: str, limit: float) -> None:
            rec = status.get(rec_id, {})
            st = rec.get("status", "n/a")
            tags = []
            if theirs_key in baseline:
                tags.append("baseline" if st == "fail" else "baseline (theirs)")
            if "pre-accepted" in rec.get("note", ""):
                tags.append("pre-accepted")
            if "report only" in rec.get("note", ""):
                tags.append("report-only")
            if theirs_all is None:
                verdict, delta = "n/a (no values.json)", None
            elif theirs is None:
                verdict, delta = "n/a (theirs null)", None
            elif IC.M.is_nan(ours):
                verdict, delta = "DRIFT (ours undefined)", None
            else:
                delta = abs(float(ours) - float(theirs))
                verdict = "ok" if delta <= limit else "DRIFT"
            if tags:
                verdict += " [" + ", ".join(tags) + "]"
            rows.append({"plate": stem, "check": check, "ours": ours, "theirs": theirs, "delta": delta,
                         "tol": limit, "status": st, "verdict": verdict})

        t = theirs_all or {}
        for key, (label, tkey) in VALUE_CHECKS.items():
            mkey = "ratio" if key == "ratio" else key
            theirs_v = t.get("ratio_median") if key == "ratio" else t.get(key)
            lim = tol["lm_ratio"] if key == "ratio" else tol[key if key != "median" else "median"]
            rec_id = "12.2" if key == "ratio" else label
            ours_v = measured.get(mkey)
            if key == "ratio" and ours_v is None and status.get("12.2", {}).get("value") is not None:
                ours_v = status["12.2"]["value"]
            add(label, ours_v, theirs_v, rec_id, tkey, lim)
        comp = t.get("composition", {})
        for rid in sorted(rules):
            metric = rules[rid]["metric"]
            lim_abs = tol["absolute"].get(metric)
            ours_v = measured.get(metric)
            theirs_v = comp.get(rid)
            if lim_abs is not None:
                lim = lim_abs
            else:
                lim = tol["relative"] * max(abs(float(ours_v)) if ours_v is not None and not IC.M.is_nan(ours_v) else 0.0,
                                            abs(float(theirs_v)) if theirs_v is not None else 0.0, 1e-9)
            if theirs_all is not None and theirs_v is None and status.get(rid, {}).get("status") == "n/a":
                continue
            add(rid, ours_v, theirs_v, rid, rid, lim)
        rr = status.get("12.6.route", {})
        rows.append({"plate": stem, "check": "12.6 route never occluded", "ours": rr.get("value"), "theirs": None,
                     "delta": None, "tol": None, "status": rr.get("status", "n/a"),
                     "verdict": rr.get("status", "n/a") + (": " + rr["note"] if rr.get("note") else "")})
    return rows, done


def to_markdown(rows: List[Row]) -> str:
    """The row table."""
    lines = ["| plate | check | ours | theirs | delta | tol | our status | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['plate']} | {r['check']} | {_fmt(r['ours'])} | {_fmt(r['theirs'])} | {_fmt(r['delta'])} | "
                     f"{_fmt(r['tol'])} | {r['status']} | {r['verdict'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def summary_markdown(rows: List[Row], stems: List[str]) -> str:
    """Per-plate counts of ok / DRIFT / n/a rows."""
    lines = ["| plate | ok | DRIFT | n/a |", "|---|---|---|---|"]
    for s in stems:
        v = [r["verdict"] for r in rows if r["plate"] == s and r["check"] != "12.6 route never occluded"]
        lines.append(f"| {s} | {sum(x.startswith('ok') for x in v)} | {sum(x.startswith('DRIFT') for x in v)} | "
                     f"{sum(x.startswith('n/a') for x in v)} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    """Run the compare; print the markdown and write it to `--out` when given. Always exits 0 (a report, not a gate)."""
    ap = argparse.ArgumentParser(prog="netrun_art.checks.drift")
    ap.add_argument("plates")
    ap.add_argument("--work", required=True, help="scratch folder for the staged capture triples")
    ap.add_argument("--out", help="markdown file for the rows")
    a = ap.parse_args(argv)
    rows, stems = drift_rows(a.plates, a.work)
    md = "## Summary\n\n" + summary_markdown(rows, stems) + "\n## Rows\n\n" + to_markdown(rows)
    sys.stdout.write(md)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
