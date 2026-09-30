"""Build contact_sheet.jpg from the five stills.  python contact_sheet.py <stills_dir> <out_jpg>"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SHOTS = [("01_city_day.png", "01  City - day"), ("02_city_night.png", "02  City - night"),
         ("03_city_suspicion.png", "03  City - high suspicion"), ("04_combat.png", "04  Combat"),
         ("05_shop.png", "05  Black-market shop")]
TW, TH, PAD, LAB = 760, 428, 24, 46


def main():
    src, out = sys.argv[1], sys.argv[2]
    cols = 2
    rows = 3
    W = cols * TW + (cols + 1) * PAD
    H = 90 + rows * (TH + LAB) + (rows + 1) * PAD
    sheet = Image.new("RGB", (W, H), (16, 6, 28))
    d = ImageDraw.Draw(sheet)
    fh = ImageFont.truetype("C:/Windows/Fonts/AGENCYB.TTF", 54)
    fl = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 26)
    d.text((PAD, 22), "REBEL_CELL  //  r2d_neon_painting  -  vibrant neon digital painting", font=fh, fill=(255, 150, 210))
    for k, (fn, label) in enumerate(SHOTS):
        im = Image.open(os.path.join(src, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
        c, r = k % cols, k // cols
        x = PAD + c * (TW + PAD)
        y = 90 + PAD + r * (TH + LAB + PAD)
        if k == 4:
            x = (W - TW) // 2
        sheet.paste(im, (x, y))
        d.rectangle((x - 2, y - 2, x + TW + 1, y + TH + 1), outline=(255, 80, 180), width=2)
        d.text((x, y + TH + 8), label, font=fl, fill=(235, 225, 255))
    sheet.save(out, quality=88)
    print("wrote", out)


main()
