"""Three-panel side by side: current golden plate | art nouveau | modern art."""
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

C = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(C, "hq_styles", "solace_modernart")
srcs = [("current golden plate", os.path.join(C, "golden_plates", "hq_solace_overview.png")),
        ("art nouveau", os.path.join(C, "hq_styles", "solace_nouveau", "solace_nouveau.png")),
        ("modern art", os.path.join(OUT, "solace_modernart.png"))]
W, H = 960, 540
sheet = Image.new("RGB", (W * 3, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(srcs):
    sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), lab, fill=(220, 220, 220))
sheet.save(os.path.join(OUT, "solace_modernart_sbs.jpg"), quality=90)
