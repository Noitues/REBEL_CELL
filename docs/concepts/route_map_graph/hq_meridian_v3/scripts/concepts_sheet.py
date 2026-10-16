"""Meridian v3: the three massing thumbnails side by side with one-line captions -> ../concepts_sheet.png

python concepts_sheet.py <thumb dir>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
CAP = [
    ("A  GATEHOUSE GANTRY  (recommended)",
     "The crane IS the gatehouse: two crenellated tower-legs ride the E / W walls, the battlemented span carries the keep."),
    ("B  SLEWING DONJON",
     "A round keep in the bailey slews a long jib with a castellated counterweight over walls, trucks and train."),
    ("C  QUAYSIDE KEEP",
     "A ship-to-shore crane straddles the rail as the castle's gatehouse; its boom reaches south over the bailey."),
]


def font(sz, bold=False):
    for f in (("consolab.ttf" if bold else "consola.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            continue
    return ImageFont.load_default()


W, H = 960, 540
PAD, CH = 16, 74
sheet = Image.new("RGB", (3 * W + 4 * PAD, H + CH + 2 * PAD + 44), (12, 12, 16))
d = ImageDraw.Draw(sheet)
d.text((PAD, PAD), "MERIDIAN HQ v3: three massing concepts (Workbench, overview angle: high 3/4 from the SSW)",
       fill=(255, 150, 40), font=font(26, True))
for k, w in enumerate("ABC"):
    im = Image.open(os.path.join(SRC, "thumb_%s.png" % w)).convert("RGB")
    x = PAD + k * (W + PAD)
    y = PAD + 44
    sheet.paste(im, (x, y))
    if k == 0:
        d.rectangle([x - 3, y - 3, x + W + 2, y + H + 2], outline=(255, 150, 40), width=3)
    d.text((x, y + H + 10), CAP[k][0], fill=(255, 150, 40) if k == 0 else (235, 235, 235), font=font(22, True))
    d.text((x, y + H + 40), CAP[k][1], fill=(190, 190, 195), font=font(15))
sheet.save(os.path.join(os.path.dirname(HERE), "concepts_sheet.png"))
print("saved", sheet.size)
