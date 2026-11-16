"""Contact sheet of candidate room cells from the locked route-view render (AAA2r3_plate.png, 2560 x 1440).
Run: python cells_sheet.py  -> D:/rc_scratch/street_b/cells_sheet.png
"""
from PIL import Image, ImageDraw

from sb_cells import CELLS, SRC

im = Image.open(SRC).convert("RGB")
tiles = []
for name, box in CELLS.items():
    pad = 10
    c = im.crop((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)).resize(
        ((box[2] - box[0] + 2 * pad) * 2, (box[3] - box[1] + 2 * pad) * 2), Image.NEAREST)
    d = ImageDraw.Draw(c)
    d.rectangle([2 * pad, 2 * pad, c.width - 2 * pad, c.height - 2 * pad], outline=(255, 255, 255))
    d.text((4, 2), name, fill=(255, 255, 0))
    tiles.append(c)
W = sum(t.width for t in tiles) + 10 * len(tiles)
H = max(t.height for t in tiles)
out = Image.new("RGB", (W, H), (20, 20, 20))
x = 0
for t in tiles:
    out.paste(t, (x, 0))
    x += t.width + 10
out.save("D:/rc_scratch/street_b/cells_sheet.png")
