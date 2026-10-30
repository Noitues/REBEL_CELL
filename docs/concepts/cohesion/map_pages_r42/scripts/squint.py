"""squint_<page>.png: 1/16 scale, heavy blur, back up; page and squint side by side (half size)."""
import os, sys
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
for n in sys.argv[1:]:
    im = Image.open(os.path.join(OUT, n + ".png")).convert("RGB")
    s = im.resize((120, 68), Image.BOX).filter(ImageFilter.GaussianBlur(0.6)).resize((1920, 1080), Image.BICUBIC)
    sh = Image.new("RGB", (1920, 540))
    sh.paste(im.resize((960, 540), Image.LANCZOS), (0, 0)); sh.paste(s.resize((960, 540), Image.LANCZOS), (960, 0))
    sh.save(os.path.join(OUT, "squint_%s.png" % n)); print(n)
