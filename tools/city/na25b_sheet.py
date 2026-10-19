"""NA-25b review sheet (art-pass A-031): the jack-in chain's key frames, the HQ side, the bits dissolve and 1:1 crops.

    python tools/city/na25b_sheet.py <e2e shots dir> <lab shots dir> <out.jpg>

The e2e dir comes from `na25_e2e_lab.tscn --mode=shots`, the lab dir from `na25_lab.tscn --size=1280x720`, both through
tools/run_windowed.py. 12 tiles, 3 columns: the nine of r3 (frame 4 slap, 5 swell, 6 plain breathe, 6 CRT hold, 7 open, HQ-side
covered, HQ-side unslap, bits 0.55, bits 0.30) and three 1:1 crops (the bits at 0.55 and 0.30, the CRT panel).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

TILE = (640, 360)
LABEL_H = 18
COLS = 3
CROP = (640, 360)


def crop_at(img: Image.Image, centre: tuple[int, int]) -> Image.Image:
    x = min(max(centre[0] - CROP[0] // 2, 0), img.width - CROP[0])
    y = min(max(centre[1] - CROP[1] // 2, 0), img.height - CROP[1])
    return img.crop((x, y, x + CROP[0], y + CROP[1]))


def main() -> int:
    e2e, lab, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    crt = Image.open(e2e / "chain_6b_crt_hold.png").convert("RGB")
    bits55 = Image.open(lab / "bits_overview_0.55.png").convert("RGB")
    bits30 = Image.open(lab / "bits_overview_0.30.png").convert("RGB")
    dec55 = Image.open(lab / "bits_decision_0.55.png").convert("RGB")
    dec30 = Image.open(lab / "bits_decision_0.30.png").convert("RGB")
    tiles: list[tuple[str, Image.Image]] = [
        ("4 wheel slaps on: the operative's real class wheel", Image.open(e2e / "chain_4_slap.png")),
        ("5 lens swells: the hub core grows toward the screen", Image.open(e2e / "chain_5_lens_swell.png")),
        ("6 hub covers (hold under 0.5 s): flat class field, emblem native + whole", Image.open(e2e / "chain_6_cover_hold.png")),
        ("6 hold past 0.5 s: CRT on the field (hex column, scanlines, cyan rim, block caret)", crt),
        ("7 the hub burns open: CRT gone, HUD held under the lens", Image.open(e2e / "chain_7_lens_open.png")),
        ("HQ side: lens covers the switch (flat field, nothing else)", Image.open(e2e / "hq_out_cover.png")),
        ("HQ side: the wheel comes off the link", Image.open(e2e / "hq_out_unslap.png")),
        ("bits dissolve 0.55 (ghosted stubs, no black prism)", bits55),
        ("bits dissolve 0.30", bits30),
        ("1:1 crop (1080p): bits 0.55, 0 / 1 glyphs", crop_at(dec55, (600, 400))),
        ("1:1 crop (1080p): bits 0.30, fewer glyphs", crop_at(dec30, (600, 400))),
        ("1:1 crop: the CRT panel (top-right quarter: hex column, scanlines, rim)", crt.crop((640, 0, 1280, 360))),
    ]
    rows = (len(tiles) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TILE[0], rows * (TILE[1] + LABEL_H)), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(tiles):
        img = img.convert("RGB")
        if "1:1 crop" in label:
            tile = img if img.size == TILE else img.resize(TILE)
        else:
            tile = img.resize(TILE, Image.LANCZOS)
        x, y = (i % COLS) * TILE[0], (i // COLS) * (TILE[1] + LABEL_H)
        draw.text((x + 4, y + 3), label, fill=(230, 230, 230))
        sheet.paste(tile, (x, y + LABEL_H))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    print("wrote", out, sheet.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
