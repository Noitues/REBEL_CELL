"""Three-panel side by side: golden plate | art deco | nouveau (run from anywhere)."""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

C = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(C, "hq_styles", "solace_nouveau")
srcs = [("current golden plate", os.path.join(C, "golden_plates", "hq_solace_overview.png")),
        ("art deco", os.path.join(C, "art_deco", "05_solace_deco.png")),
        ("art nouveau", os.path.join(OUT, "solace_nouveau.png"))]
W, H = 960, 540
sheet = Image.new("RGB", (W * 3, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(srcs):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    sheet.paste(im, (i * W, 28))
    d.text((i * W + 10, 8), lab, fill=(220, 220, 220))
sheet.save(os.path.join(OUT, "solace_nouveau_sbs.jpg"), quality=90)
