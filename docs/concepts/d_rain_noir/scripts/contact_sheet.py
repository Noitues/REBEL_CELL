"""Contact sheet of the five stills with labels (pure Pillow). Usage: python contact_sheet.py STILLS_DIR OUT.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "assets", "fonts"))
mono = ImageFont.truetype(os.path.join(FONTS, "ShareTechMono-Regular.ttf"), 20)
anton = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), 44)
src, out = sys.argv[1], sys.argv[2]
items = [("01_combat.png", "01 COMBAT: two lit instruments on a dark console; city a rain-blurred silhouette"),
         ("02_city_night.png", "02 CITY NIGHT: stacked highways, holo ads, patchy fog, tilt-shift, one net plane"),
         ("03_heat.png", "03 HEAT HUNTED: helicopter searchlights, drone swarms, red/blue rims, glitch"),
         ("04_hq_modem.png", "04 MODEM: the original vertical sign as real neon; spill on wet street + glass"),
         ("05_marker_strip.png", "05 MARKER: write-on, drips hold, page leaves while drips run")]
TW, TH, G = 960, 540, 24
W = 2 * TW + 3 * G
H = 90 + 3 * (TH + 44 + G)
sheet = Image.new("RGB", (W, H), (5, 7, 11))
d = ImageDraw.Draw(sheet)
d.text((G, 18), "RAIN NOIR CINEMATIC", font=anton, fill=(242, 246, 255))
d.text((G + 470, 40), "concept artist D  //  d_rain_noir  //  REBEL_CELL concept round", font=mono, fill=(122, 136, 156))
for i, (fn, label) in enumerate(items):
    im = Image.open(os.path.join(src, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    col, row = i % 2, i // 2
    x = G + col * (TW + G)
    y = 90 + row * (TH + 44 + G)
    if i == 4:
        x = (W - TW) // 2
    sheet.paste(im, (x, y))
    d.line((x, y + TH + 6, x + 60, y + TH + 6), fill=(255, 61, 168), width=3)
    d.text((x, y + TH + 12), label, font=mono, fill=(175, 192, 214))
sheet.save(out, quality=88)
print("SHEET", out, sheet.size)
