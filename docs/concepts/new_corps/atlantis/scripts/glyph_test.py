"""Debug: every new-corp glyph mask on one sheet (scratch), at 180 px and at 32 px."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nc_kit as K
from PIL import Image

fns = [K.GLYPHS["aurelian"]["crest"]] + [s[2] for s in K.GLYPHS["aurelian"]["sites"]] + [f for _, f in K.BOSS_OPTIONS["aurelian"]]
fns += [f for _, f in K.CREST_OPTIONS] + [s[2] for s in K.GLYPHS["tethys"]["sites"]] + [f for _, f in K.BOSS_OPTIONS["tethys"]]
W = 200
cols = 10
rows = (len(fns) + cols - 1) // cols
sheet = Image.new("L", (W * cols, (W + 50) * rows), 30)
for i, fn in enumerate(fns):
    x, y = (i % cols) * W, (i // cols) * (W + 50)
    sheet.paste(255, (x + 10, y + 10), K.mask(fn, 180))
    sheet.paste(255, (x + 84, y + W + 4), K.mask(fn, 32))
out = os.path.join(K.SCR, "glyph_test.png")
sheet.save(out)
print(out)
