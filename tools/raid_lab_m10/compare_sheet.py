"""Comparison sheet of the L7 raid lab against the Blender target frames: each target frame (left) next to the lab still that
shows the same moment (right), one row per frame, with a caption under each row.

    python tools/raid_lab_m10/compare_sheet.py [--out D:/rc_tmp/raid_design_lab/lab_l7]

Reads the stills in <out>/shots and <out>/shots_breach (made by capture_l7.py) and writes <out>/comparison_sheet.png. A lab still is
found by the label at the end of its file name (the number in front changes with the capture's beats).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "docs" / "design" / "raid_concepts" / "raid_target"

# (target file, lab folder, lab label, caption)
PAIRS = [
    ("raid_target_1_plan.png", "shots", "r1_plan_levers", "PLAN: levers placed, sealed lines, kit, Heat"),
    ("raid_target_2_reveal.png", "shots", "r1_decision", "REVEAL: real line lit, spoof window open"),
    ("raid_target_3_impact.png", "shots_breach", "r1_stamp_slam", "IMPACT: stamp with the rules' tier name"),
]


def find(folder: Path, label: str) -> Path | None:
    hits = sorted(p for p in folder.glob("*.png") if p.stem.endswith(label))
    return hits[0] if hits else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="D:/rc_tmp/raid_design_lab/lab_l7")
    args = ap.parse_args()
    out = Path(args.out)
    cell_w, cell_h = 960, 540
    cap_h = 34
    sheet = Image.new("RGB", (cell_w * 2, (cell_h + cap_h) * len(PAIRS)), (8, 10, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(ROOT / "assets" / "fonts" / "ShareTechMono-Regular.ttf"), 18)
    except OSError:
        font = ImageFont.load_default()
    for row, (target, folder, label, caption) in enumerate(PAIRS):
        y = row * (cell_h + cap_h)
        t_img = Image.open(TARGETS / target).convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
        sheet.paste(t_img, (0, y))
        lab = find(out / folder, label)
        if lab is not None:
            l_img = Image.open(lab).convert("RGB")
            # The lab is 1280x720 (16:9): fit it to the same cell.
            l_img = l_img.resize((cell_w, cell_h), Image.LANCZOS)
            sheet.paste(l_img, (cell_w, y))
            note = "lab: %s/%s" % (folder, lab.name)
        else:
            note = "lab still not found (%s/*%s)" % (folder, label)
        draw.rectangle([0, y + cell_h, cell_w * 2, y + cell_h + cap_h], fill=(14, 18, 36))
        draw.text((12, y + cell_h + 7), "target: %s" % target, fill=(255, 210, 77), font=font)
        draw.text((cell_w + 12, y + cell_h + 7), "%s   (%s)" % (note, caption), fill=(232, 236, 245), font=font)
    dest = out / "comparison_sheet.png"
    sheet.save(dest)
    print("wrote", dest)


if __name__ == "__main__":
    main()
