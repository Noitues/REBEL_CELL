"""Pack meridian_mughal_v5.png and meridian_mughal_v4_v5.jpg (v2 final | v3 final)."""
import os
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
R = r"D:/rc_scratch/hq_styles/meridian_mughal"
v3 = Image.open(R + "/final5/plate.png").convert("RGB")
v3.save(os.path.join(OUT, "meridian_mughal_v5.png"))
v2 = Image.open(os.path.join(OUT, "meridian_mughal_v4.png")).convert("RGB")
W, H = 1280, 720
sheet = Image.new("RGB", (W * 2, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (im, n) in enumerate(((v2, "v4"), (v3, "v5: white walls and arcade, streets and trucks, mixed rusted containers"))):
    sheet.paste(im.resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), n, fill=(230, 230, 230))
sheet.save(os.path.join(OUT, "meridian_mughal_v4_v5.jpg"), quality=90)
