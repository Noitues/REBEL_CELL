"""Solarpunk v1 | v2 comparison (960x540 panels)."""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
srcs = [("solarpunk v1", "solace_solarpunk.png"), ("solarpunk v2 (concrete + neon trim)", "solace_solarpunk_v2.png")]
W, H = 960, 540
sheet = Image.new("RGB", (W * 2, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(srcs):
    sheet.paste(Image.open(os.path.join(OUT, p)).convert("RGB").resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), lab, fill=(220, 220, 220))
sheet.save(os.path.join(OUT, "solace_solarpunk_v1_v2.jpg"), quality=90)
