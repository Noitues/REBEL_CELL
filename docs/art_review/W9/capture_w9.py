"""W9 review captures (art pass, ART_BIBLE §12): runs the W10 harness
(tools/visual_qa/capture_pack.py) with W9 settings seeded into each run's private
user:// folder, so no harness file changes. Then builds the review images.

    python docs/art_review/W9/capture_w9.py --work <scratch dir> [--only a,b] [--compose-only]

Variants (each a capture_pack run with its own --out under --work):
  off          grid, combat_start, title, hq, options at 1.0 mouse (the "before" of each)
  deutan/protan/tritan   grid, combat_start with Settings.colorblind_mode set
  sim_off / sim_deutan   the W10 deutan SIMULATION filter rendered in-engine
                         (--filter-mode shader, layer 128) over no correction / over the
                         deutan correction (layer 127): the harness keeps working and the
                         simulated viewer sees the corrected frame
  hc           title, hq, combat_start with Settings.high_contrast
  scale2       every screen at text scale 2.0, mouse, with contact sheets (W8's damage list)
Write as a file on purpose: never run Python from stdin on this machine.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PACK = ROOT / "tools" / "visual_qa" / "capture_pack.py"
W10_BASE = ROOT / "docs" / "art_review" / "W10" / "baseline"

VARIANTS = {
    "off": ({}, ["grid", "combat_start", "title", "hq", "options"], []),
    "deutan": ({"colorblind_mode": "deutan"}, ["grid", "combat_start"], []),
    "protan": ({"colorblind_mode": "protan"}, ["grid", "combat_start"], []),
    "tritan": ({"colorblind_mode": "tritan"}, ["grid", "combat_start"], []),
    "sim_off": ({}, ["grid", "combat_start"], ["--filters", "deutan", "--filter-mode", "shader"]),
    "sim_deutan": ({"colorblind_mode": "deutan"}, ["grid", "combat_start"], ["--filters", "deutan", "--filter-mode", "shader"]),
    "hc": ({"high_contrast": True}, ["title", "hq", "combat_start"], []),
    "scale2": ({}, [], ["--scales", "2.0", "--sheets"]),
}


def combos(extra: list[str]) -> list[str]:
    scale = extra[extra.index("--scales") + 1] if "--scales" in extra else "1.0"
    flt = extra[extra.index("--filters") + 1] if "--filters" in extra and "--filter-mode" in extra else "none"
    return ["%s_mouse_re-off_%s" % (scale, flt)]


def capture(work: Path, name: str) -> None:
    settings, screens, extra = VARIANTS[name]
    out = work / name
    out.mkdir(parents=True, exist_ok=True)
    for combo in combos(extra):
        user = out / "_runs" / "_user" / combo / "Godot" / "app_userdata" / "REBEL_CELL"
        user.mkdir(parents=True, exist_ok=True)
        seeded = dict(settings, tutorial_done=True)
        (user / "settings.json").write_text(json.dumps(seeded), encoding="utf-8")
    cmd = [sys.executable, str(PACK), "--out", str(out), "--inputs", "mouse"] + extra
    if name != "scale2":
        cmd.append("--no-lint")
    if screens:
        cmd += ["--screens", ",".join(screens)]
    print("capture_w9:", name, flush=True)
    subprocess.run(cmd, cwd=str(ROOT), stdin=subprocess.DEVNULL, check=False)


def shot(work: Path, name: str, screen: str) -> Image.Image:
    _s, _sc, extra = VARIANTS[name]
    return Image.open(work / name / combos(extra)[0] / (screen + ".png")).convert("RGB")


def label(img: Image.Image, text: str) -> Image.Image:
    img = img.copy()
    d = ImageDraw.Draw(img)
    w = int(d.textlength(text)) + 16
    d.rectangle([0, 0, w, 22], fill=(0, 0, 0))
    d.text((8, 5), text, fill=(242, 246, 255))
    return img


def grid(cells: list[list[Image.Image]], cell_w: int = 640) -> Image.Image:
    cell_h = cell_w * 9 // 16
    out = Image.new("RGB", (cell_w * len(cells[0]), cell_h * len(cells)), (0, 0, 0))
    for r, row in enumerate(cells):
        for c, im in enumerate(row):
            out.paste(im.resize((cell_w, cell_h), Image.LANCZOS), (c * cell_w, r * cell_h))
    return out


def compose(work: Path) -> None:
    for mode in ("deutan", "protan", "tritan"):
        cells = [[label(shot(work, "off", s), "%s - off" % s), label(shot(work, mode, s), "%s - %s correction" % (s, mode))]
                 for s in ("grid", "combat_start")]
        grid(cells).save(HERE / ("colorblind_%s.jpg" % mode), quality=85)
    cells = [[label(shot(work, "sim_off", s), "%s - deutan SIMULATION, no correction" % s),
              label(shot(work, "sim_deutan", s), "%s - deutan SIMULATION of the deutan correction" % s)]
             for s in ("grid", "combat_start")]
    grid(cells).save(HERE / "colorblind_deutan_simulated.jpg", quality=85)
    cells = [[label(shot(work, "off", s), "%s - normal" % s), label(shot(work, "hc", s), "%s - high contrast" % s)]
             for s in ("title", "hq", "combat_start")]
    grid(cells).save(HERE / "high_contrast.jpg", quality=85)
    before = W10_BASE / "1.0_mouse" / "options.jpg"
    if before.exists():
        b = Image.open(before).convert("RGB")
        a = shot(work, "off", "options")
        grid([[label(b, "options - before (art-pass, W10 baseline)"), label(a, "options - after W9 (new rows)")]]).save(
            HERE / "options_before_after.png", optimize=True)
    sheets = work / "scale2" / "sheets"
    dst = HERE / "text_scale_2.0"
    if sheets.exists():
        dst.mkdir(exist_ok=True)
        for p in sorted(sheets.glob("combo_*.*")):
            Image.open(p).convert("RGB").save(dst / (p.stem + ".jpg"), quality=85)
        for f in ("lint_report.md",):
            if (work / "scale2" / f).exists():
                shutil.copy(work / "scale2" / f, dst / f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--compose-only", action="store_true")
    a = ap.parse_args()
    work = Path(a.work).resolve()
    names = [n for n in a.only.split(",") if n] or list(VARIANTS)
    if not a.compose_only:
        for n in names:
            capture(work, n)
    compose(work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
