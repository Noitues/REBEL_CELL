"""Usage: python r1_vs_r2.py <r1.png> <r2.png> <out.jpg> : round 1 | round 2 side by side, labelled."""
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
a = Image.open(sys.argv[1]).convert("RGB").resize((960, 540), Image.LANCZOS)
b = Image.open(sys.argv[2]).convert("RGB").resize((960, 540), Image.LANCZOS)
s = Image.new("RGB", (1920, 560))
s.paste(a, (0, 20))
s.paste(b, (960, 20))
d = ImageDraw.Draw(s)
d.text((8, 4), "round 1 (837124d2)", fill=(255, 255, 255))
d.text((968, 4), "round 2", fill=(255, 255, 255))
s.save(sys.argv[3], quality=90)
