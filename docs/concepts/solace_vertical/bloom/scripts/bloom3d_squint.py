"""squint_hq_overview.jpg: clean | Bloom at 320 px wide, plus a gaussian (4 px at 1920 scale) blurred copy of each, labelled."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
import solace_lib as L
BS = "D:/rc_scratch/solace_v1/bloom3d"
c = Image.open(BS + "/clean_hq_overview.png").convert("RGB")
b = Image.open(L.OUT + "/A3d_hq_overview.png").convert("RGB")
w = 320
h = int(c.size[1] * w / c.size[0])
def sm(im): return im.resize((w, h), Image.LANCZOS)
def bl(im): return sm(im.filter(ImageFilter.GaussianBlur(4 * im.size[0] / 1920.0)))
S = Image.new("RGB", (w * 2 + 30, h * 2 + 80), (12, 7, 20))
d = ImageDraw.Draw(S)
for i, (lab, im) in enumerate((("CLEAN", c), ("BLOOM", b))):
    x = 10 + i * (w + 10)
    S.paste(sm(im), (x, 24)); d.text((x, 6), lab, font=L.font(14), fill=(235, 235, 245))
    S.paste(bl(im), (x, 24 + h + 28)); d.text((x, 24 + h + 8), lab + " blurred 4 px", font=L.font(14), fill=(235, 235, 245))
S.save(L.OUT + "/squint_hq_overview.jpg", quality=92)
