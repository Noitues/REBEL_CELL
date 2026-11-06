"""crop helper: python crops.py <png> <out.png> <scale> x0,y0,x1,y1 [x0,y0,x1,y1 ...]   -> the crops side by side (NEAREST upscale)"""
import sys
from PIL import Image
src, out, sc = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert('RGB')
tiles = []
for b in sys.argv[4:]:
    x0, y0, x1, y1 = [int(v) for v in b.split(',')]
    c = im.crop((x0, y0, x1, y1))
    tiles.append(c.resize((c.width * sc, c.height * sc), Image.NEAREST))
W = sum(t.width for t in tiles) + 8 * (len(tiles) - 1)
H = max(t.height for t in tiles)
o = Image.new('RGB', (W, H), (255, 0, 255))
x = 0
for t in tiles:
    o.paste(t, (x, 0))
    x += t.width + 8
o.save(out)
print(out, o.size)
