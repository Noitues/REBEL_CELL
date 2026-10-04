"""Scratch inspection: python gif_sheet.py <gif> [n]  -> scratch/probe/gif_sheet.png (n evenly spaced frames)"""
import os
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(sys.argv[1])
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
N = im.n_frames
idx = [round(i * (N - 1) / (n - 1)) for i in range(n)]
fr = []
for i in idx:
    im.seek(i)
    fr.append((i, im.convert("RGB").copy()))
w, h = fr[0][1].size
k = min(1.0, 1800 / (6 * w))
tw, th = int(w * k), int(h * k)
cols = 6
rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for j, (i, f) in enumerate(fr):
    x, y = (j % cols) * tw, (j // cols) * (th + 18)
    sheet.paste(f.resize((tw, th)), (x, y + 18))
    d.text((x + 4, y + 2), "frame %d/%d" % (i, N), fill=(255, 255, 0))
out = os.path.join(os.path.dirname(HERE), "scratch", "probe", "gif_sheet.png")
sheet.save(out)
print(out, N, "frames", os.path.getsize(sys.argv[1]) / 1e6, "MB")
