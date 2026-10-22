"""Pack the Orbital retro v4 deliverables: orbital_retro_v4.png and orbital_v3_v4.jpg (v3 | v4, 1280 x 720 each).
python sa3_pack.py <v4 plate.png>"""
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
shutil.copyfile(sys.argv[1], os.path.join(OUT, "orbital_retro_v4.png"))
panels = [(os.path.join(OUT, "orbital_retro_v3.png"), "v3 TV network + space corp"), (os.path.join(OUT, "orbital_retro_v4.png"), "v4 fins, doors, buildings")]
W, H = 1280, 720
sheet = Image.new("RGB", (W * 2, H), (0, 0, 0))
try:
    font = ImageFont.truetype("arial.ttf", 26)
except OSError:
    font = ImageFont.load_default()
for i, (p, cap) in enumerate(panels):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 400, 40], fill=(0, 0, 0))
    d.text((10, 7), cap, fill=(235, 240, 245), font=font)
    sheet.paste(im, (i * W, 0))
sheet.save(os.path.join(OUT, "orbital_v3_v4.jpg"), quality=90)
print("packed", sheet.size)
