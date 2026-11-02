"""Build punk/slices_board.jpg: one row per style.

Row = [wheel crop (old | A | B), slice key, plate of the better variant], labelled.
Usage: python make_slices_board.py [style=A|B ...] [style=#rank ...]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "slices_board.jpg")

# order = ranking; (key, title, best variant, rank label, one-line verdict)
STYLES = [
    ("xerox_flyer", "XEROX FLYER (ref 5)", "A", "#1",
     "Cleanest type read: flat spot inks, bold dots/scales/checker/plus, hatch keeps a coloured icon seat on every slice"),
    ("linocut", "TWO-TONE LINOCUT (ref 6)", "A", "#2",
     "Most punk; carved textures read in grey, but hatched slices go muddy maroon/brown and pink BURST vs mint REPAIR share a value"),
    ("spiderpunk_collage", "SPIDER-PUNK COLLAGE (ref 1)", "A", "#3",
     "Loudest poster; good textures and keyed hatch; still loud, yellow TURRET now competes with plan yellow"),
    ("benday_stickerbomb", "BEN-DAY STICKER BOMB (ref 8)", "B", "#4",
     "Best texture shapes (rays, honeycomb, rings, plus) and hatch/soak tests, but pop comic, not punk"),
    ("jinx_scribble", "JINX NEON SCRIBBLE (ref 4)", "B", "#5",
     "B hot paint reads; A's dark tinted bodies go muddy under the hatch; Arcane more than punk"),
    ("mural_graffiti", "SPIDER-VERSE MURAL (ref 2)", "A", "#6",
     "Textures too faint (rings, scales vanish in grey); airbrush still reads synthwave"),
    ("wpap_faceted", "WPAP FACETED (ref 7)", "B", "#7",
     "Multi-colour facets blur the one-colour-per-type rule; under hatch all four types turn the same red"),
]

W = 4300
PAD = 24
LABEL_H = 96
ROW_H = 1000
BG = (18, 16, 26)
FG = (240, 236, 226)
PINK = (255, 61, 168)
DIM = (170, 166, 180)


def font(size, bold=True):
    for name in (["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit(img, box_w, box_h):
    img = img.convert("RGB")
    s = min(box_w / img.width, box_h / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def main():
    over = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    styles = []
    for key, title, var, rank, verdict in STYLES:
        v = over.get(key, var)
        if v.startswith("#"):
            rank, v = v, var
        styles.append((key, title, v, rank, verdict))

    head_h = 120
    H = head_h + len(styles) * (LABEL_H + ROW_H + PAD) + PAD
    board = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(board)
    d.text((PAD, 20), "PUNK SPINNER: PER-SLICE COLOUR + TEXTURE PASS", font=font(56), fill=FG)
    d.text((PAD, 84), "Each row: wheel crop (old | A | B, as delivered)  |  slice key  |  plate of the better variant.  Rows sorted by rank.",
           font=font(26, False), fill=DIM)

    # column widths: wheel crop gets the most, key is tall/narrow, plate 16:9
    key_w = 760
    crop_w = 2100
    plate_w = W - 4 * PAD - key_w - crop_w
    plate_h = int(plate_w * 9 / 16)

    y = head_h
    for key, title, var, rank, verdict in styles:
        sdir = os.path.join(ROOT, key, "slices")
        d.rectangle([0, y, W, y + LABEL_H - 8], fill=(30, 27, 42))
        d.text((PAD, y + 8), f"{rank}  {title}", font=font(44), fill=PINK if rank in ("#1", "#2", "#3") else FG)
        d.text((PAD, y + 58), f"best variant: {var}   -   {verdict}", font=font(26, False), fill=FG)
        y0 = y + LABEL_H
        x = PAD
        crop = fit(Image.open(os.path.join(sdir, "wheel_crop.jpg")), crop_w, ROW_H)
        board.paste(crop, (x, y0 + (ROW_H - crop.height) // 2))
        x += crop_w + PAD
        keyimg = fit(Image.open(os.path.join(sdir, "slice_key.jpg")), key_w, ROW_H)
        board.paste(keyimg, (x + (key_w - keyimg.width) // 2, y0))
        x += key_w + PAD
        plate = fit(Image.open(os.path.join(sdir, f"plate_{var}.png")), plate_w, plate_h)
        py = y0 + (ROW_H - plate.height) // 2
        d.text((x, py - 40), f"plate {var}", font=font(30), fill=FG)
        board.paste(plate, (x, py))
        y = y0 + ROW_H + PAD

    board.save(OUT, quality=90)
    print(OUT, board.size)


if __name__ == "__main__":
    main()
