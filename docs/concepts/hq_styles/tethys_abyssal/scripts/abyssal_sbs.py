"""Side by side: the current golden plate (left) | the abyssal plate (right), 1920 x 540 jpg.
python abyssal_sbs.py <abyssal.png> <out.jpg>"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, "..", "..", "..", "golden_plates", "hq_tethys_overview.png"))
a = Image.open(G).convert("RGB").resize((960, 540), Image.LANCZOS)
b = Image.open(sys.argv[1]).convert("RGB").resize((960, 540), Image.LANCZOS)
im = Image.new("RGB", (1920, 540))
im.paste(a, (0, 0))
im.paste(b, (960, 0))
d = ImageDraw.Draw(im)
d.text((10, 8), "current (golden plate)", fill=(255, 255, 255))
d.text((970, 8), "abyssal", fill=(255, 255, 255))
im.save(sys.argv[2], quality=90)
