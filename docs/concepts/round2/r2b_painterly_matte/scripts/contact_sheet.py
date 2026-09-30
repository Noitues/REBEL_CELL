"""Builds contact_sheet.jpg from the five stills. Usage: python contact_sheet.py <stills_dir> <out.jpg>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

STILLS, OUT = sys.argv[1], sys.argv[2]
names = [("01_city_day.png", "01  City - day"), ("02_city_night.png", "02  City - night"),
         ("03_city_suspicion.png", "03  City - high suspicion"), ("04_combat.png", "04  Combat"), ("05_shop.png", "05  Shop")]
TW, TH, PAD, LAB = 760, 428, 24, 40
sheet = Image.new("RGB", (PAD + 2 * (TW + PAD), 90 + 3 * (TH + LAB + PAD)), (22, 20, 18))
d = ImageDraw.Draw(sheet)
ft = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 30)
fl = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 20)
d.text((PAD, 26), "r2b_painterly_matte  -  painterly matte-painting style", font=ft, fill=(236, 214, 160))
for i, (fn, label) in enumerate(names):
    im = Image.open(os.path.join(STILLS, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    col, row = i % 2, i // 2
    if i == 4:
        col = 0.5
    x = int(PAD + col * (TW + PAD)); y = 90 + row * (TH + LAB + PAD)
    sheet.paste(im, (x, y))
    d.rectangle([x - 1, y - 1, x + TW, y + TH], outline=(180, 140, 70))
    d.text((x, y + TH + 8), label, font=fl, fill=(230, 220, 200))
sheet.save(OUT, quality=88)
print("saved", OUT)
