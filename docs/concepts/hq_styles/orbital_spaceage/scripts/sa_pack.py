"""Pack the Orbital space-age deliverables: the final plate and the three-panel side-by-side
(current golden plate | art deco | space-age), each panel 960 x 540 with a caption.
python sa_pack.py <plate.png>"""
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
plate = sys.argv[1]
shutil.copyfile(plate, os.path.join(OUT, "orbital_spaceage.png"))
panels = [(os.path.join(CON, "golden_plates", "hq_orbital_overview.png"), "current (golden plate)"),
          (os.path.join(CON, "art_deco", "04_orbital_deco.png"), "art deco"),
          (os.path.join(OUT, "orbital_spaceage.png"), "space-age retrofuturism")]
W, H = 960, 540
sheet = Image.new("RGB", (W * 3, H), (0, 0, 0))
try:
    font = ImageFont.truetype("arial.ttf", 22)
except OSError:
    font = ImageFont.load_default()
for i, (p, cap) in enumerate(panels):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 330, 34], fill=(0, 0, 0))
    d.text((10, 6), cap, fill=(235, 240, 245), font=font)
    sheet.paste(im, (i * W, 0))
sheet.save(os.path.join(OUT, "orbital_spaceage_sbs.jpg"), quality=90)
print("packed", sheet.size)
