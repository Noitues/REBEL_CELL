"""hq_tethys: before / after board. python compare.py <before.png> <after.png> <out.jpg>"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tethys_preset as TP  # noqa: E402

a, b = Image.open(sys.argv[1]).convert("RGB"), Image.open(sys.argv[2]).convert("RGB")
W = 1280
a = a.resize((W, int(a.height * W / a.width)), Image.LANCZOS)
b = b.resize((W, int(b.height * W / b.width)), Image.LANCZOS)
out = Image.new("RGB", (W * 2 + 12, max(a.height, b.height) + 40), (10, 12, 20))
out.paste(a, (0, 40))
out.paste(b, (W + 12, 40))
d = ImageDraw.Draw(out)
f = ImageFont.truetype(os.path.join(TP.FONTS, "ShareTechMono-Regular.ttf"), 22)
d.text((10, 8), "ROUND 1: city_all_corps/tethys_flooded_closeup.png", font=f, fill=(170, 190, 230))
d.text((W + 22, 8), "ROUND 2 TEST: pier city, dam + lock, shallow drowned streets, clear water", font=f, fill=(170, 230, 200))
out.save(sys.argv[3], quality=90)
