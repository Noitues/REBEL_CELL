"""Exposure solve of the AAA-2 street look (A-022 / MATERIAL_SPEC 10 stage 1): the post exposure per framing so the finished frame has a
median luma of 0.14 (the plate solve: secant on the median, then x0.93 steps until at least 26 % of the pixels are under 0.10, as long as the
median stays at or above 0.125; clamp from the config). The numbers go into `content/config/street_route.tres` `look.exposure` ([OVERVIEW, DECISION]).

    cd tools && python -m netrun_art.exposure_solve [--views overview,decision] [--seed 1] [--start 0.6] [--work <dir>] [--keep]

Each probe is one windowed `tools/city/na23_lab.tscn` run through `tools/run_windowed.py` (never a bare windowed godot), `--exposure=<x>`
fixing the post exposure of the rig. Prints one JSON line per view: exposure, median, under_010, over_085, runs.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

from .checks import metrics as M

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_MEDIAN = 0.14
UNDER_WANT = 0.26
MEDIAN_FLOOR = 0.125
STEP = 0.93
CLAMP = (0.2, 2.0)
TOL = 0.004


def probe(state: str, seed: int, exposure: float, work: str, extra: List[str], timeout: int) -> Dict[str, float]:
    """One lab run at `exposure`: the value stats (display luma, dark 0.10, bright 0.85) of the beauty frame."""
    out = os.path.join(work, "probe")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, os.path.join(REPO, "tools", "run_windowed.py"), "--log", os.path.join(work, "lab.log"), "--timeout", str(timeout), "--",
           "--resolution", "1920x1080", "res://tools/city/na23_lab.tscn", "--", f"--seed={seed}", f"--shots={out}", f"--states={state}",
           "--size=1920x1080", f"--exposure={exposure:.5f}"] + extra
    rc = subprocess.run(cmd, cwd=REPO).returncode
    path = os.path.join(out, f"{state}_seed{seed}", "beauty.png")
    if rc != 0 or not os.path.exists(path):
        raise SystemExit(f"probe failed (rc {rc}): {path}")
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    v = M.luma(rgb).ravel()
    return {"median": float(np.median(v)), "under_010": float((v < 0.10).mean()), "over_085": float((v > 0.85).mean())}


def solve(state: str, seed: int, start: float, work: str, extra: List[str], timeout: int) -> Dict[str, object]:
    runs: List[Tuple[float, Dict[str, float]]] = []

    def run(x: float) -> Dict[str, float]:
        x = min(max(x, CLAMP[0]), CLAMP[1])
        s = probe(state, seed, x, work, extra, timeout)
        runs.append((x, s))
        print(f"  {state} exposure {x:.4f}: median {s['median']:.4f} under {s['under_010']:.3f} over {s['over_085']:.4f}", flush=True)
        return s

    x0 = start
    s0 = run(x0)
    x1 = x0 * (TARGET_MEDIAN / max(s0["median"], 0.01)) ** 0.7
    s1 = run(x1)
    for _ in range(4):
        if abs(s1["median"] - TARGET_MEDIAN) <= TOL:
            break
        dm = s1["median"] - s0["median"]
        dx = x1 - x0
        slope = dm / dx if abs(dx) > 1e-6 and abs(dm) > 1e-6 else 0.2
        x2 = x1 + (TARGET_MEDIAN - s1["median"]) / slope
        x0, s0 = x1, s1
        x1 = min(max(x2, CLAMP[0]), CLAMP[1])
        s1 = run(x1)
    best_x, best_s = x1, s1
    # The plate rule: lower the exposure by 7 % while under_010 is short of 26 % and the median stays at or above 0.125.
    for _ in range(4):
        if best_s["under_010"] >= UNDER_WANT:
            break
        x = best_x * STEP
        s = run(x)
        if s["median"] < MEDIAN_FLOOR:
            break
        best_x, best_s = max(x, CLAMP[0]), s
    return {"view": state, "exposure": round(best_x, 4), "median": round(best_s["median"], 4), "under_010": round(best_s["under_010"], 4),
            "over_085": round(best_s["over_085"], 4), "runs": len(runs)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--views", default="overview,decision")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--start", type=float, default=0.6)
    ap.add_argument("--work", default=None)
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--lab-arg", action="append", default=[], help="extra na23_lab argument (e.g. --cfg.fog.peak=0.1)")
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix="exposure_solve_")
    os.makedirs(work, exist_ok=True)
    results = []
    for st in a.views.split(","):
        r = solve(st, a.seed, a.start, work, a.lab_arg, a.timeout)
        print(json.dumps(r), flush=True)
        results.append(r)
    if not a.keep and a.work is None:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
