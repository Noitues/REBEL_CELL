"""Contact sheet (<= 1280 px wide) of the Solace THE BLOOM stills -> stills/solace/solace_sheet.jpg."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

import solace_lib as L

NAMES = ["S_clean", "S_creep", "S_close", "S_catch", "S_caught_strip", "H_bloom_overview", "R_20", "R_60", "R_90"]
TW, TH, M = 416, 234, 8
sheet = Image.new("RGB", (3 * TW + 4 * M, 3 * (TH + 22) + M), (14, 8, 14))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(NAMES):
    im = Image.open(os.path.join(L.OUT, n + ".png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
    x, y = M + (i % 3) * (TW + M), M + (i // 3) * (TH + 22)
    sheet.paste(im, (x, y + 18))
    d.text((x, y + 9), n, font=L.font(14), fill=(255, 70, 150), anchor="lm")
sheet.save(os.path.join(L.OUT, "solace_sheet.jpg"), quality=88)
print(sheet.size)
