"""Render the combined overlay kit: three screens, the kit sheet, the lifecycle and the contact sheet.

Run from anywhere:  python build_all.py   (Pillow + numpy, all randomness seeded)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import OUT, MK
from PIL import Image, ImageDraw
import s01_combat, s02_city, s03_shop, s04_kit_sheet, s05_lifecycle


def contact_sheet():
    names = ["01_combat.png", "02_city.png", "03_shop.png", "04_kit_sheet.png", "05_lifecycle.png"]
    pad, tw, th = 14, 624, 351
    sheet = Image.new("RGB", (pad * 4 + tw * 3, pad * 3 + th * 2 + 54), (13, 13, 17))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), "combined overlay kit  //  spray verbs + vinyl stickers + grease pencil + light spill over Cv2",
           font=MK.bahn(24, "Bold"), fill=(236, 236, 230))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = pad + (i % 3) * (tw + pad)
        y = 54 + pad + (i // 3) * (th + pad)
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=90)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    s01_combat.build()
    s02_city.build()
    s03_shop.build()
    s04_kit_sheet.build()
    s05_lifecycle.build()
    contact_sheet()
