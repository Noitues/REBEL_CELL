"""Pack meridian_mughal_v2.png and meridian_mughal_v1_v2.jpg (v1 CPU preview m6 | v2 final)."""
import os
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
R = r"D:/rc_scratch/hq_styles/meridian_mughal"
v2 = Image.open(R + "/final/plate.png").convert("RGB")
v2.save(os.path.join(OUT, "meridian_mughal_v2.png"))
v1 = Image.open(R + "/m6/plate.png").convert("RGB")      # v1 look-dev preview (1280x720); the v1 final was never rendered (GPU queue)
W, H = 1280, 720
sheet = Image.new("RGB", (W * 2, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (im, n) in enumerate(((v1, "v1: palace dropped in the yard (CPU preview, 8 spp)"), (v2, "v2: one walled ensemble, 8 crane-minarets (GPU final)"))):
    sheet.paste(im.resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), n, fill=(230, 230, 230))
sheet.save(os.path.join(OUT, "meridian_mughal_v1_v2.jpg"), quality=90)
