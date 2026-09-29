"""Contact sheet of the five NEON INK stills.  python contact_sheet.py"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, "..", "stills")
OUT = os.path.join(HERE, "..", "contact_sheet.jpg")
FONT = os.path.join(HERE, "..", "..", "..", "..", "assets", "fonts", "ShareTechMono-Regular.ttf")
items = [("01_combat.png", "01 COMBAT"), ("02_city_night.png", "02 CITY GRID - NIGHT"), ("03_heat.png", "03 HEAT - HUNTED"),
         ("04_hq_modem.png", "04 MODEM CYBER SHOP"), ("05_marker_strip.png", "05 MARKER STRIP")]
tw, th, pad, lab = 944, 531, 24, 40
sheet = Image.new("RGB", (pad + 2 * (tw + pad), 90 + 3 * (th + lab + pad)), (6, 8, 14))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype(FONT, 26); fb = ImageFont.truetype(FONT, 40)
except OSError:
    f = fb = ImageFont.load_default()
d.text((pad, 24), "REBEL_CELL concept A - NEON INK", fill=(255, 61, 168), font=fb)
for i, (fn, name) in enumerate(items):
    im = Image.open(os.path.join(ST, fn)).convert("RGB").resize((tw, th), Image.LANCZOS)
    col, row = i % 2, i // 2
    x = pad + col * (tw + pad); y = 90 + row * (th + lab + pad)
    if i == 4:
        x = pad + (tw + pad) // 2
    d.text((x, y), name, fill=(92, 225, 255), font=f)
    sheet.paste(im, (x, y + lab))
sheet.save(OUT, quality=88)
print("sheet", OUT)
