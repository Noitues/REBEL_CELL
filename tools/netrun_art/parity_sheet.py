"""Street look parity sheet (A-020 / B-002 P0): golden plate on top, Godot at the plate's camera below, the 12 numbers of both.

    cd tools && python -m netrun_art.parity_sheet [--views street_overview,street_decision] [--seed 1]
                 [--art-repo <art-pass worktree>] [--ref art-pass] [--out docs/art_review/PARITY] [--keep]

What it does, per view:
 1. reads the plate (png, id png, capture.json) from art-pass with `git show` (read-only; falls back to the worktree file) into
    a %TEMP% folder. A plate image is never written into the repo.
 2. renders Godot twice through `tools/city/na23_lab.tscn` (windowed, `tools/run_windowed.py` only, IdCapture): once at our own
    NetrunCameraRig camera, once at the plate's camera (`--plate_dir`).
 3. stacks plate (top) over Godot-at-plate-camera (bottom) at one scale, labelled, into `<out>/<view>_seed<N>.jpg`.
 4. prints the 12 numbers of both (`netrun_art.checks` image checks) and the camera table (plate / ours / delta).
Views: street_overview, street_decision (na23_lab states overview / decision). city_a2_* and hq_*_{overview,decision} are not wired yet.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from .checks import image_checks as IC

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_ART_REPO = "D:/rc_art/art-pass"
PLATE_DIR = "docs/concepts/golden_plates"
STATE_OF = {"street_overview": "overview", "street_decision": "decision"}
CAM_LABEL = {
    "ours": "GODOT {v} seed {seed}: our NetrunCameraRig camera (same rig model; pitch and lens as the plate, position is layout-bound), IdCapture 1920x1080",
    "plate": "GODOT {v} seed {seed}: our street focus + yaw with the plate pitch, dist, lens, shift (can sit inside a wall: layouts differ)",
}


def fetch_plate(art_repo: str, ref: str, view: str, dest: str) -> Dict[str, str]:
    """Copies `<view>.png`, `_id.png` and `_capture.json` of the golden plate into `dest` (git show first, file second)."""
    os.makedirs(dest, exist_ok=True)
    out: Dict[str, str] = {}
    for suffix in (".png", "_id.png", "_capture.json"):
        rel = f"{PLATE_DIR}/{view}{suffix}"
        target = os.path.join(dest, view + suffix)
        r = subprocess.run(["git", "-C", art_repo, "show", f"{ref}:{rel}"], capture_output=True)
        if r.returncode == 0 and r.stdout:
            data = r.stdout
        else:
            src = os.path.join(art_repo, rel)
            if not os.path.exists(src):
                raise SystemExit(f"plate file missing: {ref}:{rel} (and {src})")
            with open(src, "rb") as f:
                data = f.read()
        with open(target, "wb") as f:
            f.write(data)
        out[suffix] = target
    return out


def plate_folder(plates: Dict[str, str], view: str, dest: str) -> str:
    """A capture folder (beauty.png, id.png, capture.json) for the checks, built from the fetched plate."""
    os.makedirs(dest, exist_ok=True)
    shutil.copyfile(plates[".png"], os.path.join(dest, "beauty.png"))
    shutil.copyfile(plates["_id.png"], os.path.join(dest, "id.png"))
    shutil.copyfile(plates["_capture.json"], os.path.join(dest, "capture.json"))
    return dest


def run_lab(godot_out: str, states: List[str], seed: int, plate_dir: Optional[str], log: str, timeout: int) -> int:
    """One windowed na23_lab run (shots into `godot_out`, one `<state>_seed<N>` folder each)."""
    lab_args = [f"--seed={seed}", f"--shots={godot_out}", f"--states={','.join(states)}", "--size=1920x1080"]
    if plate_dir:
        lab_args.append(f"--plate_dir={plate_dir}")
    cmd = [sys.executable, os.path.join(REPO, "tools", "run_windowed.py"), "--log", log, "--timeout", str(timeout), "--",
           "--resolution", "1920x1080", "res://tools/city/na23_lab.tscn", "--"] + lab_args
    return subprocess.run(cmd, cwd=REPO).returncode


def _font(size: int) -> ImageFont.ImageFont:
    """A monospace font of `size` (consolas, DejaVu, else the PIL default)."""
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def stack_sheet(plate_png: str, godot_png: str, out: str, labels: Tuple[str, str]) -> None:
    """Plate over Godot, both 1920 x 1080 full scale (a 1920 x 2200 JPEG), each with a label strip above it."""
    strip = 40
    f = _font(22)
    sheet = Image.new("RGB", (1920, 2 * (1080 + strip)), (16, 16, 22))
    d = ImageDraw.Draw(sheet)
    for i, (path, label) in enumerate(zip((plate_png, godot_png), labels)):
        y = i * (1080 + strip)
        d.text((10, y + 8), label, font=f, fill=(235, 235, 235))
        sheet.paste(Image.open(path).convert("RGB").resize((1920, 1080), Image.LANCZOS), (0, y + strip))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out, "JPEG", quality=88)


def numbers(folder: str, cfg: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, str]]:
    """The measured 12 numbers of a capture folder and the status of every check record `{id: status}`."""
    recs, measured = IC.check_capture_folder(folder, cfg)
    status = {str(r["id"]): str(r.get("status", "?")) for r in recs}
    return measured, status


def fmt(v: Any) -> str:
    """A number as 4 significant digits, `-` for none or NaN."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def numbers_table(plate: Dict[str, float], godot: Dict[str, float], p_st: Dict[str, str], g_st: Dict[str, str]) -> str:
    """Side-by-side markdown of the measured values (plate | Godot at plate camera | delta) and the rule statuses."""
    rows = ["| number | plate | Godot | delta |", "|---|---|---|---|"]
    for k in sorted(set(plate) | set(godot)):
        a, b = plate.get(k), godot.get(k)
        ok = isinstance(a, (int, float)) and isinstance(b, (int, float)) and not (math.isnan(a) or math.isnan(b))
        rows.append(f"| {k} | {fmt(a)} | {fmt(b)} | {fmt(b - a) if ok else '-'} |")
    rows += ["", "| check | plate | Godot |", "|---|---|---|"]
    for k in sorted(set(p_st) | set(g_st)):
        if p_st.get(k) != g_st.get(k) or "fail" in (p_st.get(k), g_st.get(k)):
            rows.append(f"| {k} | {p_st.get(k, '-')} | {g_st.get(k, '-')} |")
    return "\n".join(rows)


def camera_table(plate: Dict[str, Any], ours: Dict[str, Any]) -> str:
    """Pose, FOV and look-at of the plate and of our rig, with deltas (loc, tgt and dist in BU; angles in degrees)."""
    def horiz_fov(lens: float) -> float:
        return math.degrees(2 * math.atan(36.0 / (2 * lens)))
    rows = ["| field | plate | ours | delta |", "|---|---|---|---|"]
    for key in ("loc", "tgt"):
        a, b = plate[key], ours[key]
        rows.append(f"| {key} (x y z) | {', '.join(f'{v:.2f}' for v in a)} | {', '.join(f'{v:.2f}' for v in b)} | "
                    f"{', '.join(f'{y - x:+.2f}' for x, y in zip(a, b))} (|d| {math.dist(a, b):.2f}) |")
    for key, unit in (("dist", "BU"), ("yaw", "deg"), ("pitch", "deg"), ("lens", "mm"), ("shift_x", ""), ("shift_y", "")):
        rows.append(f"| {key} {unit} | {plate[key]:.4f} | {ours[key]:.4f} | {ours[key] - plate[key]:+.4f} |")
    pf, of = horiz_fov(plate["lens"]), horiz_fov(ours["lens"])
    rows.append(f"| horizontal FOV deg (36 mm sensor) | {pf:.2f} | {of:.2f} | {of - pf:+.2f} |")
    return "\n".join(rows)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI: fetch the plates, render Godot, write the sheets, print the numbers and the camera table."""
    ap = argparse.ArgumentParser(prog="netrun_art.parity_sheet")
    ap.add_argument("--views", default="street_overview,street_decision")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--art-repo", default=DEFAULT_ART_REPO)
    ap.add_argument("--ref", default="art-pass")
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "art_review", "PARITY"))
    ap.add_argument("--work", default=None, help="scratch folder (default %%TEMP%%/parity)")
    ap.add_argument("--camera", choices=("ours", "plate"), default="ours",
                    help="ours: our rig camera (default); plate: plate pitch/dist/lens/shift on our street frame")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--keep", action="store_true", help="keep the scratch folder")
    ap.add_argument("--skip-render", action="store_true", help="reuse the renders already in the scratch folder")
    a = ap.parse_args(argv)
    work = a.work or os.path.join(tempfile.gettempdir(), "parity")
    views = [v for v in a.views.split(",") if v]
    for v in views:
        if v not in STATE_OF:
            raise SystemExit(f"view {v} is not wired (street_overview, street_decision only)")
    states = [STATE_OF[v] for v in views]
    plates_dir = os.path.join(work, "plates")
    fetched = {v: fetch_plate(a.art_repo, a.ref, v, plates_dir) for v in views}
    own, at_plate = os.path.join(work, "ours"), os.path.join(work, "at_plate")
    if not a.skip_render:
        for dest, pd, tag in ((own, None, "ours"), (at_plate, plates_dir, "plate")):
            if tag == "plate" and a.camera != "plate":
                continue
            shutil.rmtree(dest, ignore_errors=True)
            os.makedirs(dest, exist_ok=True)
            rc = run_lab(dest, states, a.seed, pd, os.path.join(work, f"lab_{tag}.log"), a.timeout)
            if rc != 0:
                raise SystemExit(f"na23_lab ({tag}) exit {rc}; see {work}/lab_{tag}.log")
    cfg = IC.load_config(None)
    for v in views:
        st = STATE_OF[v]
        gdir = os.path.join(at_plate if a.camera == "plate" else own, f"{st}_seed{a.seed}")
        pdir = plate_folder(fetched[v], v, os.path.join(work, "plate_folder", v))
        plate_cap = json.load(open(fetched[v]["_capture.json"], encoding="utf-8"))["camera"]
        our_cap = json.load(open(os.path.join(own, f"{st}_seed{a.seed}", "capture.json"), encoding="utf-8"))["camera"]
        out = os.path.join(a.out, f"{v}_seed{a.seed}.jpg")
        stack_sheet(fetched[v][".png"], os.path.join(gdir, "beauty.png"), out,
                    (f"GOLDEN PLATE {v} (art-pass {a.ref}, Blender, seed 1)",
                     CAM_LABEL[a.camera].format(v=v, seed=a.seed)))
        p_num, p_st = numbers(pdir, cfg)
        g_num, g_st = numbers(gdir, cfg)
        print(f"\n## {v} seed {a.seed}: sheet {out}\n\n### 12 numbers (Godot, camera {a.camera}, vs plate)\n")
        print(numbers_table(p_num, g_num, p_st, g_st))
        print(f"\n### Camera ({v}): plate vs our NetrunCameraRig at seed {a.seed}\n")
        print(camera_table(plate_cap, our_cap))
    if not a.keep and not a.work:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
