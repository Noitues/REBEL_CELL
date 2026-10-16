"""Rebel Cell: export the round 15 fist glyph (crests15.fist, cropped to its bounding box) as a 128 x 128 grid for the
Blender build (Blender's Python has no PIL): python fist_mask.py -> ../scratch/fist_mask.json (row 0 = north).
Cells: 1 = the fist (red windows), 2 = a detail LINE (inside the fist's filled silhouette but not drawn: the finger
splits, the thumb edge, the cuff: the lines that go dark in the blackout, round 34), 0 = outside.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import crests15  # noqa: E402

N = 128
f = crests15.fist()
m = f.crop(f.getbbox()).resize((N, N))
on = [[m.getpixel((x, y)) > 128 for x in range(N)] for y in range(N)]
# outside = flood fill from the border through 'off' cells; 'off' cells not reached are the interior lines
out = [[False] * N for _ in range(N)]
stack = [(x, y) for x in range(N) for y in (0, N - 1)] + [(x, y) for y in range(N) for x in (0, N - 1)]
while stack:
    x, y = stack.pop()
    if not (0 <= x < N and 0 <= y < N) or out[y][x] or on[y][x]:
        continue
    out[y][x] = True
    stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
grid = [[1 if on[y][x] else (0 if out[y][x] else 2) for x in range(N)] for y in range(N)]
# the line cells are thin: grow them by one cell so a 12 BU block grid catches them
g2 = [row[:] for row in grid]
for y in range(N):
    for x in range(N):
        if grid[y][x] == 2:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < N and 0 <= y + dy < N and grid[y + dy][x + dx] == 1:
                    g2[y + dy][x + dx] = 2
dest = os.path.join(os.path.dirname(HERE), "scratch", "fist_mask.json")
json.dump({"n": N, "grid": g2}, open(dest, "w"))
print("fist mask", dest, "fist", sum(r.count(1) for r in g2), "lines", sum(r.count(2) for r in g2))
