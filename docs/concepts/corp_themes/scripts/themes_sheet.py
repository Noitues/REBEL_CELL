"""stills/themes_sheet.jpg (<= 1280 px): one representative still per corp, all 5 corps (Solace's H_bloom_overview included)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw

import theme_lib as T
import solace_lib as L

PICKS = [("solace", "H_bloom_overview", "SOLACE  THE BLOOM", (255, 70, 150)),
         ("halcyon", "G_fixed2", "HALCYON  THE EYE", (140, 240, 235)),
         ("rebel_cell", "B01_plan", "REBEL_CELL  THREE LINES, ONE CLOCK", (255, 80, 90)),
         ("tethys", "H_ov_HIGH", "TETHYS  THE WATER LEVEL", (124, 242, 228)),
         ("aurelian", "H_overview_gates", "AURELIAN  THE RING", (201, 163, 90))]
TW, TH, M = 416, 234, 8
sh = Image.new("RGB", (3 * TW + 4 * M, 2 * (TH + 24) + M), (10, 10, 14))
d = ImageDraw.Draw(sh)
for i, (corp, name, label, col) in enumerate(PICKS):
    im = Image.open(os.path.join(T.STILLS, corp, name + ".png")).convert("RGB").resize((TW, TH), Image.LANCZOS)
    x, y = M + (i % 3) * (TW + M), M + (i // 3) * (TH + 24)
    sh.paste(im, (x, y + 20))
    d.text((x, y + 10), label, font=L.font(13), fill=col, anchor="lm")
x, y = M + 2 * (TW + M), M + (TH + 24)
d.text((x + 6, y + 40), "Campaign themes: one still each.", font=L.font(14), fill=(200, 200, 210))
d.text((x + 6, y + 64), "Full sets: stills/<corp>/<corp>_sheet.jpg", font=L.font(13), fill=(150, 150, 165))
sh.save(os.path.join(T.STILLS, "themes_sheet.jpg"), quality=88)
print(sh.size)
