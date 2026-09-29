"""W3 review strips: frames (f000.png ...) from tools/design_lab/w3_strips.tscn -> one JPG.

    python docs/art_review/W3/make_strip.py <frames dir> <out.jpg> <title> [step seconds] [crop x,y,w,h] [columns]

Each frame is cropped (default: the whole 1280x720), scaled to a 400 px wide thumbnail,
labelled with its time, and laid out in rows; saved as JPG q85. Written as a file on purpose
(never run Python from stdin on this machine).
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

src = Path(sys.argv[1])
out = Path(sys.argv[2])
title = sys.argv[3]
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.1
crop = tuple(int(v) for v in sys.argv[5].split(",")) if len(sys.argv) > 5 and sys.argv[5] else None
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 4
frames = sorted(src.glob("f*.png"))
thumbs = []
for f in frames:
    im = Image.open(f).convert("RGB")
    if crop:
        x, y, w, h = crop
        im = im.crop((x, y, x + w, y + h))
    tw = 400
    im = im.resize((tw, round(im.height * tw / im.width)))
    thumbs.append(im)
if not thumbs:
    sys.exit("no frames in %s" % src)
tw, th = thumbs[0].size
rows = (len(thumbs) + cols - 1) // cols
head = 28
sheet = Image.new("RGB", (cols * tw, head + rows * (th + 18)), (6, 8, 22))
d = ImageDraw.Draw(sheet)
d.text((8, 8), title, fill=(242, 238, 228))
for i, im in enumerate(thumbs):
    x = (i % cols) * tw
    y = head + (i // cols) * (th + 18)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + th + 3), "+%.2f s" % (i * step), fill=(175, 192, 214))
out.parent.mkdir(parents=True, exist_ok=True)
sheet.save(out, "JPEG", quality=85)
print("strip", out, sheet.size)
