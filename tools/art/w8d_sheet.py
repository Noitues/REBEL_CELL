"""Art pass W8d: a review sheet of the campaign end's baked art, as the game tints it.

    python tools/art/w8d_sheet.py <render_dir> <out.jpg>

<render_dir> holds the PNGs from tools/art/render_w8d.gd. Row 1: the five landmarks in their
corp hues (ART_BIBLE 3.6); row 2: the same in greyscale (Rec. 709 luma: the shape names the
corp); row 3: the Cell's hexagon whole, cracked (halves parted + the crack in INK), and the
spray X's overspray in CELL_PINK. Needs Pillow. Run it as a file (never `python -`).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

BG = (10, 12, 24)
TEXT = (235, 235, 225)
CORPS = [("solace", (0x3D, 0xFF, 0x8B), "Solace: DNA helix"), ("meridian", (0xFF, 0x8C, 0x1A), "Meridian: container crane"),
         ("halcyon", (0x8C, 0x7B, 0xFF), "Halcyon: clock tower"), ("orbital", (0x7F, 0xA8, 0xFF), "Orbital: satellite dish"),
         ("rebel_cell", (0xE8, 0x14, 0x1E), "REBEL_CELL: inverted hexagon")]
CELL_PINK = (0xFF, 0x3D, 0xA8)
INK = (0x11, 0x11, 0x11)
CELL = 260
LABEL = 28


def font(size):
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tint(img: Image.Image, rgb) -> Image.Image:
    r, g, b, a = img.split()
    out = Image.merge("RGB", (r, g, b))
    layer = Image.new("RGB", img.size, rgb)
    from PIL import ImageChops
    out = ImageChops.multiply(out, layer)
    out.putalpha(a)
    return out


def fit(img: Image.Image, box: int) -> Image.Image:
    k = min(box / img.width, box / img.height)
    return img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)


def paste_center(sheet, img, x, y, w, h):
    sheet.paste(img, (x + (w - img.width) // 2, y + (h - img.height) // 2), img)


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    cols = 5
    sheet = Image.new("RGB", (cols * CELL, 3 * (CELL + LABEL)), BG)
    d = ImageDraw.Draw(sheet)
    f = font(15)
    for i, (corp, rgb, label) in enumerate(CORPS):
        img = Image.open(src / f"landmark_{corp}.png").convert("RGBA")
        col = fit(tint(img, rgb), CELL - 24)
        paste_center(sheet, col, i * CELL, 0, CELL, CELL)
        d.text((i * CELL + 10, CELL + 4), label, fill=TEXT, font=f)
        grey = col.convert("LA").convert("RGBA")
        paste_center(sheet, grey, i * CELL, CELL + LABEL, CELL, CELL)
        d.text((i * CELL + 10, 2 * CELL + LABEL + 4), label + " (grey)", fill=TEXT, font=f)
    y = 2 * (CELL + LABEL)
    left = tint(Image.open(src / "cell_hex_left.png").convert("RGBA"), CELL_PINK)
    right = tint(Image.open(src / "cell_hex_right.png").convert("RGBA"), CELL_PINK)
    crack = tint(Image.open(src / "cell_hex_crack.png").convert("RGBA"), INK)
    whole = Image.new("RGBA", left.size, (0, 0, 0, 0))
    whole.alpha_composite(left)
    whole.alpha_composite(right)
    paste_center(sheet, fit(whole, CELL - 24), 0, y, CELL, CELL)
    d.text((10, y + CELL + 4), "Cell hexagon", fill=TEXT, font=f)
    broken = Image.new("RGBA", (left.width + 40, left.height + 20), (0, 0, 0, 0))
    broken.alpha_composite(left.rotate(3, resample=Image.BICUBIC), (6, 12))
    broken.alpha_composite(right.rotate(-3, resample=Image.BICUBIC), (34, 4))
    broken.alpha_composite(crack, (20, 8))
    paste_center(sheet, fit(broken, CELL - 24), CELL, y, CELL, CELL)
    d.text((CELL + 10, y + CELL + 4), "cracked (LOST)", fill=TEXT, font=f)
    paste_center(sheet, fit(broken.convert("LA").convert("RGBA"), CELL - 24), 2 * CELL, y, CELL, CELL)
    d.text((2 * CELL + 10, y + CELL + 4), "cracked (grey)", fill=TEXT, font=f)
    spray = tint(Image.open(src / "spray_x.png").convert("RGBA"), CELL_PINK)
    paste_center(sheet, fit(spray, CELL - 24), 3 * CELL, y, CELL, CELL)
    d.text((3 * CELL + 10, y + CELL + 4), "spray overspray", fill=TEXT, font=f)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)
    print("wrote", out)


if __name__ == "__main__":
    main()
