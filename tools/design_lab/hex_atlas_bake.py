"""Bakes shaders/kit/hex_atlas.png, the CRT glass's hex-dump glyph atlas (M14 B1c; ART_BIBLE v2
§1.2 "CRT terminal": a faint scrolling hex-dump; integration review D23).

Sixteen cells in a row, `0` to `F`, white Share Tech Mono (the terminal face) on transparent,
each cell one glyph advance wide and one line (ascent + descent) high at FONT_PX, the glyph on
its baseline, so the shader's character grid (`hex_cell` = the mono advance and line height at
the caption size) maps one cell to one character exactly as the font lays it out. The
shaders tint it with the panel's accent and sample it with mipmaps (imported with
mipmaps/generate). Run from the project folder: python tools/design_lab/hex_atlas_bake.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "assets/fonts/ShareTechMono-Regular.ttf"
OUT = ROOT / "shaders/kit/hex_atlas.png"
FONT_PX = 48
SS = 4
GLYPHS = "0123456789ABCDEF"


def main() -> None:
    big = ImageFont.truetype(str(FONT), FONT_PX * SS)
    ascent, descent = big.getmetrics()
    adv = big.getlength("0")
    cell_w = round(adv / SS)
    cell_h = round((ascent + descent) / SS)
    atlas = Image.new("RGBA", (cell_w * len(GLYPHS), cell_h), (255, 255, 255, 0))
    for i, g in enumerate(GLYPHS):
        m = Image.new("L", (cell_w * SS, cell_h * SS), 0)
        ImageDraw.Draw(m).text((0, ascent), g, font=big, fill=255, anchor="ls")
        m = m.resize((cell_w, cell_h), Image.LANCZOS)
        cell = Image.new("RGBA", (cell_w, cell_h), (255, 255, 255, 0))
        cell.putalpha(m)
        atlas.paste(cell, (i * cell_w, 0))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(OUT)
    print("saved", OUT, atlas.size, "cell", cell_w, cell_h)


if __name__ == "__main__":
    main()
