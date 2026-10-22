"""Variants sheet: modern art v1 | warm | solarpunk (960x540 panels)."""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
srcs = [("modern art v1", "solace_modernart.png"), ("A warm modern art", "solace_warm.png"), ("B solarpunk / biophilic", "solace_solarpunk.png")]
W, H = 960, 540
sheet = Image.new("RGB", (W * 3, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(srcs):
    sheet.paste(Image.open(os.path.join(OUT, p)).convert("RGB").resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), lab, fill=(220, 220, 220))
sheet.save(os.path.join(OUT, "solace_variants.jpg"), quality=90)
