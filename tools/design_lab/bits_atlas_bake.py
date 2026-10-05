"""Bakes shaders/kit/bits_atlas.png, the binary bits' glyph atlas (ART-1 1B; ART_BIBLE v2 §6.3).

Four 48 px cells in a row: `0`, `1`, `+` and a bit-rot block, white Share Tech Mono with a
same-colour outline of about 1/22 of the cell (the bits are tinted by the particle colour).
Run from the project folder: python tools/design_lab/bits_atlas_bake.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "assets/fonts/ShareTechMono-Regular.ttf"
OUT = ROOT / "shaders/kit/bits_atlas.png"
CELL = 48
SS = 4
GLYPHS = ["0", "1", "+", None]


def main() -> None:
    size = CELL * SS
    atlas = Image.new("RGBA", (CELL * len(GLYPHS), CELL), (0, 0, 0, 0))
    font = ImageFont.truetype(str(FONT), int(size * 0.86))
    for i, g in enumerate(GLYPHS):
        m = Image.new("L", (size, size), 0)
        d = ImageDraw.Draw(m)
        if g is None:
            # bit-rot: a broken block of three bars
            for k, (x0, x1) in enumerate([(0.28, 0.72), (0.22, 0.58), (0.40, 0.78)]):
                y = 0.26 + k * 0.18
                d.rectangle([x0 * size, y * size, x1 * size, (y + 0.11) * size], fill=255)
        else:
            stroke = max(1, size // 22)
            d.text((size / 2, size / 2), g, font=font, fill=255, anchor="mm", stroke_width=stroke, stroke_fill=255)
        m = m.filter(ImageFilter.GaussianBlur(SS * 0.35)).resize((CELL, CELL), Image.LANCZOS)
        cell = Image.new("RGBA", (CELL, CELL), (255, 255, 255, 0))
        cell.putalpha(m)
        atlas.paste(cell, (i * CELL, 0))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
