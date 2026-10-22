"""f1b_night | v1 (Cycles rebuild) | v2 (F1b + graffiti), 3 x 960x540.   python gs2_cmp.py <out.jpg>"""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
O = os.path.normpath(os.path.join(HERE, ".."))
cells = [(CON + "/round12_modem_facade/f1b_night.png", "f1b_night (current)"), (O + "/mainframe_shop_exterior_v3.png", "v3 (glowing paint)"),
         (O + "/mainframe_shop_exterior_v4.png", "v4: matte paint, real lights only")]
sheet = Image.new("RGB", (2880, 540))
f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 22)
for i, (p, lab) in enumerate(cells):
    im = Image.open(p).convert("RGB").resize((960, 540), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 500, 24 + d.textlength(lab, font=f), 532], fill=(0, 0, 0))
    d.text((16, 504), lab, font=f, fill=(255, 255, 255))
    sheet.paste(im, (i * 960, 0))
sheet.save(sys.argv[1], quality=90)
