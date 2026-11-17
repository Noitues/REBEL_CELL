"""Crop strip of the lost room in t5_lost frames (fix a check), centred on the frame's loss-red pixels. Args: capture dir, out."""
import os, sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
idx = [27, 33, 39, 45, 52, 60]
tiles = []
for i in idx:
    im = Image.open(os.path.join(src, "t5_lost", "f_%04d.jpg" % i)).convert("RGB")
    sm = im.resize((480, 270)); k = im.width / 480.0
    xs, ys = [], []
    for y in range(270):
        for x in range(480):
            r, g, b = sm.getpixel((x, y))
            if r > 170 and g < 80 and b < 90:
                xs.append(x); ys.append(y)
    cx, cy = (sum(xs) / len(xs) * k, sum(ys) / len(ys) * k) if xs else (im.width / 2, im.height / 2)
    cx, cy = min(max(cx, 330), im.width - 330), min(max(cy, 220), im.height - 220)
    tiles.append((i, im.crop((int(cx - 330), int(cy - 220), int(cx + 330), int(cy + 220))), len(xs)))
w, h = 660, 440
sh = Image.new("RGB", (w * 3, (h + 30) * 2), (12, 13, 18))
d = ImageDraw.Draw(sh)
for k, (i, t, n) in enumerate(tiles):
    x, y = (k % 3) * w, (k // 3) * (h + 30)
    sh.paste(t, (x, y))
    d.text((x + 8, y + h + 8), "t5_lost %.2f s, 1:1 crop of the 1280x720 frame on the lost room (%d red px)" % (i / 30.0, n), fill=(230, 230, 225))
sh.save(out, quality=90)
