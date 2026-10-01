import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from PIL import Image, ImageDraw
import icons8 as I
t0 = time.time()
names = list(I.ART)
cols = 8
out = Image.new("RGB", (cols * 260, ((len(names) + cols - 1) // cols) * 290), (14, 12, 20))
d = ImageDraw.Draw(out)
for i, n in enumerate(names):
    im = I.art(n, 250, 0.3)
    x, y = (i % cols) * 260, (i // cols) * 290
    out.paste(im, (x + 5, y + 5), im)
    d.text((x + 10, y + 262), n, fill=(220, 220, 230))
out.save(os.path.join(HERE, "test_art.png"))
print(time.time() - t0)
