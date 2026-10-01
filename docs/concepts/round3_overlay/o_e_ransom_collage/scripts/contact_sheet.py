"""contact_sheet.jpg: 2x2 of the four stills; run after the other scripts."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collage_lib import OUT, BLACK
from PIL import Image

names = ["01_combat.png", "02_city.png", "03_shop.png", "04_lifecycle.png"]
tw, th, g = 960, 540, 12
sheet = Image.new("RGB", (tw * 2 + g * 3, th * 2 + g * 3), BLACK)
for i, n in enumerate(names):
    im = Image.open(OUT + n).convert("RGB").resize((tw, th), Image.LANCZOS)
    sheet.paste(im, (g + (i % 2) * (tw + g), g + (i // 2) * (th + g)))
sheet.save(OUT + "contact_sheet.jpg", quality=90)
print("ok")
