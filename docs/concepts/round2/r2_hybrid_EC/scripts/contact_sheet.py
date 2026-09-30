"""Labelled contact sheet of the seven hybrid stills -> ../contact_sheet.jpg"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ST = os.path.join(ROOT, "stills")
ITEMS = [("01_city_day.png", "01  City - day"),
         ("02_city_night.png", "02  City - night"),
         ("03_suspicion_day.png", "03  Suspicion - day"),
         ("04_suspicion_night.png", "04  Suspicion - night"),
         ("05_combat.png", "05  Combat"),
         ("06_spinner_closeup.png", "06  Spinner close-up"),
         ("07_shop.png", "07  Black-market shop")]
TW, TH, PAD, LAB = 800, 450, 24, 44
cols, rows = 2, 4
sheet = Image.new("RGB", (cols * TW + (cols + 1) * PAD, rows * (TH + LAB) + (rows + 1) * PAD + 70), (34, 28, 30))
d = ImageDraw.Draw(sheet)
try:
    f_t = ImageFont.truetype("C:/Windows/Fonts/GILLUBCD.TTF", 40)
    f_l = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)
except OSError:
    f_t = f_l = ImageFont.load_default()
d.text((PAD, 18), "R2 HYBRID E+C  -  painted gritty world, faceted-crystal digital layer", font=f_t, fill=(255, 226, 170))
for i, (fn, lab) in enumerate(ITEMS):
    im = Image.open(os.path.join(ST, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    c, r = i % cols, i // cols
    x = PAD + c * (TW + PAD)
    y = 70 + PAD + r * (TH + LAB + PAD)
    if i == len(ITEMS) - 1 and len(ITEMS) % 2:
        x = (sheet.width - TW) // 2
    sheet.paste(im, (x, y))
    d.text((x + 4, y + TH + 8), lab, font=f_l, fill=(240, 232, 214))
sheet.save(os.path.join(ROOT, "contact_sheet.jpg"), quality=86)
print("sheet ok")
