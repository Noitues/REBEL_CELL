"""Side view: compare_side.jpg = the designer's mockup + V1 / V2 / V3 mid-run, labelled (2 x 2)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import ui31 as K  # noqa: E402

OUT = os.path.dirname(HERE)
CW, CH, BAR = 960, 540, 44
tiles = [("designer_mockup.webp", "MOCKUP  (designer, the idea)"),
         ("V1_mid.png", "V1  CUTAWAY STREET  (night elevation, lit cables)"),
         ("V2_mid.png", "V2  SECTION DRAWING  (schematic plate, pencil plan)"),
         ("V3_mid.png", "V3  DOLLHOUSE DOLLY  (3/4 depth, power-cut bloom)")]
img = Image.new("RGBA", (CW * 2, (CH + BAR) * 2), (8, 6, 14, 255))
for n, (f, lab) in enumerate(tiles):
    im = Image.open(os.path.join(OUT, f)).convert("RGB")
    s = min(CW / im.width, CH / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x, y = (n % 2) * CW, (n // 2) * (CH + BAR)
    img.paste(im, (x + (CW - im.width) // 2, y + BAR + (CH - im.height) // 2))
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + CW, y + BAR], fill=(5, 13, 28))
    K.text(img, (x + 16, y + BAR / 2), lab, K.F(K.MONO, 20), (212, 255, 0) if n else (230, 230, 240), "lm", 0.6)
img.convert("RGB").save(os.path.join(OUT, "compare_side.jpg"), quality=90)
print("saved compare_side.jpg")
