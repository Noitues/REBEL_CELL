"""Usage: python strip.py <out.jpg> <cols> <img> [<img> ...] : a contact strip / grid of the frames (each 480x270), numbered."""
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
out = sys.argv[1]
cols = int(sys.argv[2])
files = sys.argv[3:]
w, h = 480, 270
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (10, 8, 16))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im, (x, y))
    d.text((x + 6, y + 4), str(i + 1), fill=(255, 255, 255))
sheet.save(out, quality=90)
print(out, sheet.size)
