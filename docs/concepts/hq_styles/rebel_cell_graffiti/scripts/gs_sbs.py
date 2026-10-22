"""Side-by-side: top = current F1b night | graffiti exterior; bottom = current shop_v5 | graffiti interior.

python gs_sbs.py <exterior.png> <interior.png> <out.jpg>
"""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ext, inn, out = sys.argv[1:4]
cells = [(CON + "/round12_modem_facade/f1b_night.png", "CURRENT  F1b night"), (ext, "GRAFFITI  exterior"),
         (CON + "/round34_firmware_daemons/shop_v5.png", "CURRENT  shop_v5"), (inn, "GRAFFITI  interior")]
W, H = 960, 540
sheet = Image.new("RGB", (W * 2, H * 2), (8, 8, 12))
f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 22)
for i, (p, lab) in enumerate(cells):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, 8 + d.textlength(lab, font=f) + 16, 40], fill=(0, 0, 0))
    d.text((16, 12), lab, font=f, fill=(255, 255, 255))
    sheet.paste(im, ((i % 2) * W, (i // 2) * H))
sheet.save(out, quality=90)
print("wrote", out)
