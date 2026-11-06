# usage: python crop.py out.png scale plate:x0,y0,x1,y1 [plate:x0,y0,x1,y1 ...]  (horizontal strip; '/' starts a new row)
import sys
from PIL import Image, ImageDraw
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
B = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
out, sc = sys.argv[1], float(sys.argv[2])
rows, cur = [], []
for a in sys.argv[3:]:
    if a == 'NR':
        rows.append(cur); cur = []; continue
    p, box = a.split(':')
    path = (B + p[3:] if p.startswith('bd/') else F + p) + ('' if p.endswith('.png') else '.png')
    x0, y0, x1, y1 = map(int, box.split(','))
    im = Image.open(path).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((int((x1 - x0) * sc), int((y1 - y0) * sc)), Image.NEAREST if sc >= 1 else Image.LANCZOS)
    d = ImageDraw.Draw(im); d.rectangle((0, 0, len(a) * 6 + 4, 11), fill=(0, 0, 0)); d.text((2, 0), a, fill=(255, 255, 0))
    cur.append(im)
if cur: rows.append(cur)
W = max(sum(i.width for i in r) + 4 * (len(r) - 1) for r in rows)
H = sum(max(i.height for i in r) for r in rows) + 4 * (len(rows) - 1)
S = Image.new('RGB', (W, H), (255, 0, 255))
y = 0
for r in rows:
    x = 0
    for i in r:
        S.paste(i, (x, y)); x += i.width + 4
    y += max(i.height for i in r) + 4
S.save(out)
print(out, S.size)
