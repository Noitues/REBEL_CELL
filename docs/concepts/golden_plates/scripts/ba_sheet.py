"""Before / after sheet, 1280 px wide: python ba_sheet.py <out.jpg> <before.png> <after.png> [<before.png> <after.png> ...]
One row per pair (before left, after right), each 636 px wide, labelled."""
import sys

from PIL import Image, ImageDraw

out, paths = sys.argv[1], sys.argv[2:]
W = 636
rows = []
for b, a in zip(paths[0::2], paths[1::2]):
    ims = []
    for p, lab in ((b, "before"), (a, "after")):
        im = Image.open(p).convert("RGB")
        im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
        ImageDraw.Draw(im).text((6, 4), lab, fill=(255, 255, 255))
        ims.append(im)
    rows.append(ims)
H = sum(r[0].height + 4 for r in rows)
sheet = Image.new("RGB", (2 * W + 8, H), (12, 12, 14))
y = 0
for l, r in rows:
    sheet.paste(l, (0, y))
    sheet.paste(r, (W + 8, y))
    y += l.height + 4
sheet.save(out, quality=88)
print(out, sheet.size)
