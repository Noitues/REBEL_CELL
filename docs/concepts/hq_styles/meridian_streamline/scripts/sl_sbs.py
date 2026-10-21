"""Pack meridian_streamline.png + the sbs: current golden plate | art deco | streamline (JPEG, 3 panels)."""
import os
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.normpath(os.path.join(HERE, ".."))
src = sys.argv[1] if len(sys.argv) > 1 else r"D:/rc_scratch/hq_styles/meridian_streamline/final/plate.png"
sl = Image.open(src).convert("RGB")
sl.save(os.path.join(OUT, "meridian_streamline.png"))
W, H = 960, 540
ims = [Image.open(os.path.join(C, "golden_plates", "hq_meridian_overview.png")).convert("RGB"),
       Image.open(os.path.join(C, "art_deco", "03_meridian_deco.png")).convert("RGB"), sl]
names = ["current golden plate", "art deco", "streamline moderne"]
sheet = Image.new("RGB", (W * 3, H + 28), (12, 12, 14))
d = ImageDraw.Draw(sheet)
for i, (im, n) in enumerate(zip(ims, names)):
    sheet.paste(im.resize((W, H), Image.LANCZOS), (i * W, 28))
    d.text((i * W + 10, 8), n, fill=(230, 230, 230))
sheet.save(os.path.join(OUT, "meridian_streamline_sbs.jpg"), quality=90)
