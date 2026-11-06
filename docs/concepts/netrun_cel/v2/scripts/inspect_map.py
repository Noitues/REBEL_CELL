import json
from PIL import Image, ImageDraw
rows = json.load(open('D:/rc_scratch/netrun_cel/city/lots.json'))
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json'))
POLY = [(1070, 400), (1500, 330), (1590, 700), (1150, 800)]
def inside(p, poly):
    x, y = p; c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
sel = [r for r in rows if inside((r[2], r[3]), POLY)]
print('lots in poly', len(sel))
I = [r[0] for r in sel]; J = [r[1] for r in sel]
print('i range', min(I), max(I), 'j range', min(J), max(J))
i0, i1, j0, j1 = min(I) - 6, max(I) + 6, min(J) - 6, max(J) + 6
S = 12
img = Image.new('RGB', ((i1 - i0 + 1) * S, (j1 - j0 + 1) * S), (10, 10, 20)); dr = ImageDraw.Draw(img)
cls = {(r[0], r[1]): r[4] for r in rows}
hts = {(r[0], r[1]): r[5] for r in rows}
inpoly = {(r[0], r[1]) for r in sel}
for (i, j), c in cls.items():
    if not (i0 <= i <= i1 and j0 <= j <= j1): continue
    col = (30, 30, 40)
    if 'K' in c: col = (30, 110, 50)
    if 'B' in c: col = (80, 80, 170) if hts[(i, j)] < 12 else (150, 120, 220)
    if 'S' in c: col = (200, 200, 60)
    if 'P' in c: col = (230, 90, 140)
    if 'W' in c: col = (20, 40, 120)
    x = (i - i0) * S; y = (j - j0) * S
    dr.rectangle((x, y, x + S - 2, y + S - 2), fill=col)
    if (i, j) in inpoly: dr.rectangle((x, y, x + S - 2, y + S - 2), outline=(255, 255, 255))
img.save('D:/rc_scratch/netrun_cel/city/map.png'); print(img.size)
# solace HQ rect
print(d['hqs'])
