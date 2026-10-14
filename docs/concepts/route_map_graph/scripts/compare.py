"""Route map graph: contact sheets.
python compare.py [first A bold]
  first -> compare.jpg       the current build (W3_ROUTE, AFTER frame) beside A / B / C mid-run
  A     -> compare_A.jpg     A1-A4, rest and hover
  bold  -> compare_bold.jpg  A4 (best A), S, X1, X2, rest and hover
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import ui31 as K  # noqa: E402

OUT = os.path.dirname(HERE)
BUILD = r"D:\Godot\rebel_cell\docs\art_review\PLAN1\W3_ROUTE.jpg"
BG = (14, 12, 20)


def tile(path, w, h):
    return Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)


def sheet(rows, cols, cells, w, h, title, lab_h=34, head=56):
    """cells: list of (image, label) row-major."""
    W = cols * w + (cols + 1) * 12
    H = head + rows * (h + lab_h) + (rows + 1) * 12
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((14, head / 2), title, font=K.F(K.MONO, 24), fill=(235, 238, 245), anchor="lm")
    for k, (img, lab) in enumerate(cells):
        r, c = divmod(k, cols)
        x = 12 + c * (w + 12)
        y = head + 12 + r * (h + lab_h + 12)
        d.text((x + 2, y + lab_h / 2), lab, font=K.F(K.MONO, 19), fill=(255, 210, 120), anchor="lm")
        im.paste(img, (x, y + lab_h))
    return im


def first():
    b = Image.open(BUILD).convert("RGB")
    crop = b.crop((803, 68, 1600, 520)).resize((960, 544), Image.LANCZOS)
    cells = [(crop, "CURRENT BUILD (W3_ROUTE, main @ 8727fd3c): start of run"),
             (tile(os.path.join(OUT, "A_mid.png"), 960, 544), "A  CABLE GRAPH ON THE CITY (mid-run)"),
             (tile(os.path.join(OUT, "B_mid.png"), 960, 544), "B  LIFTED SCHEMATIC (mid-run)"),
             (tile(os.path.join(OUT, "C_mid.png"), 960, 544), "C  BRANCH LANES (mid-run)")]
    sheet(2, 2, cells, 960, 544, "ROUTE MAP GRAPH  //  the build vs the three directions").save(
        os.path.join(OUT, "compare.jpg"), quality=88)
    print("saved compare.jpg")


def pairs(names, title, out):
    cells = []
    for n, lab in names:
        cells.append((tile(os.path.join(OUT, n + "_rest.png"), 800, 450), lab + "  //  rest"))
        cells.append((tile(os.path.join(OUT, n + "_hover.png"), 800, 450), lab + "  //  hover option 2 (Rack)"))
    sheet(len(names), 2, cells, 800, 450, title).save(os.path.join(OUT, out), quality=86)
    print("saved", out)


if __name__ == "__main__":
    which = sys.argv[1:] or ["first", "A", "bold"]
    if "first" in which:
        first()
    if "A" in which:
        pairs([("A1", "A1 BLOOM CLIMB"), ("A2", "A2 ROOFTOP BEACONS"), ("A3", "A3 STREET CURRENT"), ("A4", "A4 POWER CUT")],
              "DIRECTION A ITERATED  //  the route blooms up the buildings (mid-run)", "compare_A.jpg")
    if "bold" in which:
        pairs([("A4", "A4 POWER CUT (best A)"), ("S", "S STREET LEVEL"), ("X1", "X1 LIGHT GRID"), ("X2", "X2 DENSE NET"), ("X3", "X3 NEON STREET (designer mockup)")],
              "GO BOLD  //  best A, street level, three cyberspaces (mid-run)", "compare_bold.jpg")
