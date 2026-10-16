"""Rebel Cell v2 (art director: the round 15 block fist read as a "U"; use the Cell's crest fist): export the crest fist
outline (markers42.fist_mask: the same tucked-thumb fist as the neon sign / the hologram) as a 128 x 128 grid for the
Blender build: python rc_fist_v2.py -> ../scratch/fist_mask_v2.json (row 0 = north). Cells: 1 = the fist (red
windows), 2 = a detail LINE (inside the fist's closed silhouette but not drawn: the finger splits, the thumb edge:
they go dark in the blackout), 0 = outside. The lines are grown so the 12 BU block grid (5 samples a block) keeps them.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import markers42 as MK  # noqa: E402

N = 128
m = MK.fist_mask(512).convert("L")
m = m.crop(m.getbbox())
w, h = m.size
s = max(w, h)
sq = Image.new("L", (s, s), 0)
sq.paste(m, ((s - w) // 2, (s - h) // 2))
on = sq.resize((N, N), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
closed = on.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(17))
line = ImageChops.subtract(closed, on).filter(ImageFilter.MaxFilter(3))
grid = []
for y in range(N):
    row = []
    for x in range(N):
        if line.getpixel((x, y)) > 128 and closed.getpixel((x, y)) > 128:
            row.append(2)
        elif on.getpixel((x, y)) > 128:
            row.append(1)
        else:
            row.append(0)
    grid.append(row)
# keep a line cell only where it separates fist cells (fist on both sides, horizontally or vertically, within 9 cells):
# the closing also capped the finger tips; those cells are outside


def flanked(x, y):
    for (dx, dy) in ((1, 0), (0, 1)):
        a_ = any(0 <= x - k * dx < N and 0 <= y - k * dy < N and grid[y - k * dy][x - k * dx] == 1 for k in range(1, 17))
        b_ = any(0 <= x + k * dx < N and 0 <= y + k * dy < N and grid[y + k * dy][x + k * dx] == 1 for k in range(1, 17))
        if a_ and b_:
            return True
    return False


grid = [[(2 if flanked(x, y) else 0) if grid[y][x] == 2 else grid[y][x] for x in range(N)] for y in range(N)]
# the line crossings: zero cells not reachable from the border (enclosed by fist / lines) become lines
out = [[False] * N for _ in range(N)]
stack = [(x, y) for x in range(N) for y in (0, N - 1)] + [(x, y) for y in range(N) for x in (0, N - 1)]
while stack:
    x, y = stack.pop()
    if not (0 <= x < N and 0 <= y < N) or out[y][x] or grid[y][x] != 0:
        continue
    out[y][x] = True
    stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
grid = [[2 if (grid[y][x] == 0 and not out[y][x]) else grid[y][x] for x in range(N)] for y in range(N)]
dest = os.path.join(os.path.dirname(HERE), "scratch", "fist_mask_v2.json")
json.dump({"n": N, "grid": grid}, open(dest, "w"))
prev = Image.new("RGB", (N, N))
for y in range(N):
    for x in range(N):
        prev.putpixel((x, y), [(0, 0, 0), (230, 30, 40), (90, 90, 110)][grid[y][x]])
prev.resize((512, 512), Image.NEAREST).save(os.path.join(os.path.dirname(HERE), "scratch", "fist_mask_v2.png"))
print("fist mask v2", dest, "fist", sum(r.count(1) for r in grid), "lines", sum(r.count(2) for r in grid))
