"""Aurelian HQ: the three massing thumbnails on one <= 1280 px JPEG contact sheet -> ../concepts_sheet.jpg

python concepts_sheet.py <thumb dir>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
CAP = [
    ("A  CAVEA DESCENT", ["The four seating rings (far half, facing in), then the arena gates.",
                          "Vault: the Rostrum tholos. Overview pitch 42."]),
    ("B  LOGGIA AND CAVEA  (recommended)", ["Up the outer colonnade (3 loggia tiers + attic, near face), round",
                                             "the rim walk, down the four seating rings. Pitch 40."]),
    ("C  HYPOGEUM", ["Two seating rings, then down through the cut-open arena floor into",
                     "three underground rings; vault under the column. Needs pitch 54."]),
]
GILT = (214, 178, 104)
VERD = (41, 219, 166)


def font(sz, bold=False):
    for f in (("consolab.ttf" if bold else "consola.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            continue
    return ImageFont.load_default()


W, H, PAD, CH, TOP = 624, 351, 10, 64, 40
sheet = Image.new("RGB", (2 * W + 3 * PAD, TOP + 2 * (H + CH) + PAD), (12, 12, 16))
d = ImageDraw.Draw(sheet)
d.text((PAD, 10), "AURELIAN HQ: THE CIRCUS AURELIUS - three massing concepts (quick Eevee, mock 10-layer route)",
       fill=GILT, font=font(18, True))
cells = [(0, 0), (1, 0), (0, 1)]
for k, w in enumerate("ABC"):
    im = Image.open(os.path.join(SRC, "thumb_%s.png" % w)).convert("RGB").resize((W, H), Image.LANCZOS)
    cx, cy = cells[k]
    x, y = PAD + cx * (W + PAD), TOP + cy * (H + CH)
    sheet.paste(im, (x, y))
    if w == "B":
        d.rectangle([x - 2, y - 2, x + W + 1, y + H + 1], outline=GILT, width=3)
    d.text((x, y + H + 6), CAP[k][0], fill=GILT if w == "B" else (235, 235, 235), font=font(16, True))
    for i, line in enumerate(CAP[k][1]):
        d.text((x, y + H + 27 + 17 * i), line, fill=(190, 190, 195), font=font(13))
x, y = PAD + W + PAD, TOP + H + CH
notes = ["All three are the SAME canonical full-city colosseum",
         "(landmarks.py aurelian(): 3 colonnade tiers + attic, 60",
         "columns, 4 stepped seating rings, the Rostrum column and",
         "laurel ring, 4 campanili). Only the route's slots differ.",
         "",
         "Rooms: porphyry cut-away boxes, fronts lit in the state",
         "colour (hq_kit.states). Links: lime walked, orange options,",
         "white ahead. Red ring: THE CONCORDAT VAULT (TARGET).",
         "",
         "City: a seeded block stand-in; buildings in the camera",
         "cone are stubbed (the spec 7 rule, approximated).",
         "Emissive-only massing look: no value checks apply."]
for i, line in enumerate(notes):
    d.text((x + 8, y + 6 + 19 * i), line, fill=VERD if i == 0 else (200, 200, 205), font=font(14, i == 0))
out = os.path.join(os.path.dirname(HERE), "concepts_sheet.jpg")
sheet.save(out, quality=86)
print("saved", out, sheet.size)
