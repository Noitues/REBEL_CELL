"""Scratch: all 42 new glyphs at 96 / 24 / 16 px for a quick read check.

python icon_check.py
"""
import os
from PIL import Image, ImageDraw
import fwlib as F

names = [f[0] for f in F.FIRMWARE] + [d[0] for d in F.DAEMONS]
img = Image.new("RGBA", (1800, 760), (14, 12, 20, 255))
d = ImageDraw.Draw(img)
for i, n in enumerate(names):
    col, row = i % 14, i // 14
    x, y = 20 + col * 126, 20 + row * 245
    img.alpha_composite(F.icon_rgba(n, 96), (x, y))
    img.alpha_composite(F.icon_rgba(n, 24), (x, y + 110))
    img.alpha_composite(F.icon_rgba(n, 16), (x + 40, y + 114))
    d.text((x, y + 150), n[:16], font=F.L.f_mono(13), fill=(200, 200, 210, 255))
os.makedirs(os.path.join(F.SCRATCH, "probe"), exist_ok=True)
img.save(os.path.join(F.SCRATCH, "probe", "icons.png"))
print("ok")
