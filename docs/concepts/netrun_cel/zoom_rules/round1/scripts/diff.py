import sys
from PIL import Image, ImageChops
a = Image.open(sys.argv[1]).convert("RGB"); b = Image.open(sys.argv[2]).convert("RGB")
d = ImageChops.difference(a, b)
bbox = d.getbbox()
px = d.load()
mx = 0; nz = 0
w, h = d.size
for y in range(h):
    for x in range(w):
        v = max(px[x, y])
        if v:
            nz += 1
            mx = max(mx, v)
print("size", a.size, "diff bbox", bbox, "nonzero px", nz, "max channel diff", mx)
