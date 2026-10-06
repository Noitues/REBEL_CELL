"""HQ-B: design | built review sheets for the HQ redesign (docs/art_review/HQ_REDESIGN/build/).

Each row pairs a design image from docs/art_review/HQ_REDESIGN/ with a frame the HQ-B lab captured
(tools/design_lab/hq_b_lab.tscn through tools/run_windowed.py), both at 1280x720, captioned.

Usage (never from stdin on this machine):
    python tools/art_pipeline/hq_redesign/build_sheet.py --frames <dir of s1.0_idle.png ...> --out <sheet.jpg> \
        --pair direction_B.png:s1.0_idle.png:"idle" [--pair ...]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "docs" / "art_review" / "HQ_REDESIGN"
FONT = ROOT / "assets" / "fonts" / "IBMPlexSansCondensed-Medium.ttf"
W, H = 960, 540
CAPTION_H = 40
GAP = 12


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pair", action="append", default=[], help="design.png:frame.png:caption")
    a = ap.parse_args()
    rows = [p.split(":", 2) for p in a.pair]
    sheet = Image.new("RGB", (W * 2 + GAP * 3, (H + CAPTION_H + GAP) * len(rows) + GAP), (12, 12, 20))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 24) if FONT.exists() else ImageFont.load_default()
    for i, (design, frame, caption) in enumerate(rows):
        y = GAP + i * (H + CAPTION_H + GAP)
        for k, (path, label) in enumerate([(DESIGN / design, "DESIGN  " + design), (Path(a.frames) / frame, "BUILT  " + frame + "  //  " + caption)]):
            x = GAP + k * (W + GAP)
            draw.text((x, y + 6), label, fill=(220, 230, 255), font=font)
            if path.exists():
                im = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
                sheet.paste(im, (x, y + CAPTION_H))
            else:
                draw.text((x + 20, y + CAPTION_H + 20), "(none)", fill=(255, 80, 80), font=font)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=80)
    print("sheet", a.out, sheet.size)


if __name__ == "__main__":
    main()
