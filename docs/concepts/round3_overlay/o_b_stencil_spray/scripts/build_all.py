"""Render all four boards and the contact sheet (seeded, deterministic)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import combat, city, shop, lifecycle
from marks import OUT, bahn


def contact_sheet():
    names = ["01_combat.png", "02_city.png", "03_shop.png", "04_lifecycle.png"]
    pad, tw, th = 16, 952, 536
    sheet = Image.new("RGB", (pad * 3 + tw * 2, pad * 3 + th * 2 + 56), (14, 14, 18))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), "o_b_stencil_spray  //  STENCIL & SPRAY overlay over Cv2", font=bahn(26, "Bold"), fill=(236, 236, 230))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = pad + (i % 2) * (tw + pad)
        y = 56 + pad + (i // 2) * (th + pad)
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=90)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    combat.build()
    city.build()
    shop.build()
    lifecycle.build()
    contact_sheet()
