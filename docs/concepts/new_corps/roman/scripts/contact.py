"""Debug: a 2x2 contact sheet of preview PNGs (scratch only). python contact.py out.png a.png b.png [c.png d.png]"""
import sys
from PIL import Image

ims = [Image.open(p).convert("RGB") for p in sys.argv[2:]]
w, h = 960, 540
sheet = Image.new("RGB", (w * 2, h * ((len(ims) + 1) // 2)), (0, 0, 0))
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h)), ((i % 2) * w, (i // 2) * h))
sheet.save(sys.argv[1])
print(sys.argv[1])
