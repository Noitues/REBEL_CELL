"""Quick check: every corp's kit tiles in one strip -> ../scratch/t_tiles.png"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image
import tiles

os.makedirs(os.path.join(os.path.dirname(HERE), "scratch"), exist_ok=True)
rows = []
for corp, types in tiles.KIT_TYPES.items():
    ims = [tiles.tile(p, v, s, corp, ss=2, scale=0.62, seed=i + 3) for i, (p, v, s) in enumerate(types)]
    W = sum(i.width for i in ims) + 10 * len(ims)
    row = Image.new("RGBA", (W, ims[0].height + 10), (20, 18, 26, 255))
    x = 0
    for im in ims:
        row.alpha_composite(im, (x, 5))
        x += im.width + 10
    rows.append(row)
    print(corp, flush=True)
sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height for r in rows)), (20, 18, 26, 255))
y = 0
for r in rows:
    sheet.alpha_composite(r, (0, y))
    y += r.height
sheet.convert("RGB").save(os.path.join(os.path.dirname(HERE), "scratch", "t_tiles.png"))
