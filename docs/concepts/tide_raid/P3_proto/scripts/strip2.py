import sys
from pathlib import Path
from PIL import Image, ImageDraw
d = Path(sys.argv[1]); out = sys.argv[2]; picks = [int(x) for x in sys.argv[3].split(",")]; cols = int(sys.argv[4])
w = 640; h = 360
rows = (len(picks) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h))
for i, n in enumerate(picks):
    p = d / ("f_%04d.png" % n)
    if p.exists():
        im = Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS)
        ImageDraw.Draw(im).text((6, 5), "f%d" % n, fill=(255, 255, 255))
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out)
