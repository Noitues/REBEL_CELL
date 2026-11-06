import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
for a in sys.argv[2:]:
    x, y = map(int, a.split(","))
    px = [im.getpixel((x+dx, y+dy)) for dx in (-2,0,2) for dy in (-2,0,2)]
    m = tuple(sum(p[i] for p in px)//9 for i in range(3))
    print(a, m)
