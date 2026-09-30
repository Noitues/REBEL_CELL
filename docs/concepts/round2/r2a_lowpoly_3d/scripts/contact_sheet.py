"""R2A LOW-POLY 3D: labelled contact sheet of the five stills (Pillow only)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(BASE, "..", "..", "..", ".."))
FONT = os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf")
STILLS = [("01_city_day.png", "01  CITY / DAY"), ("02_city_night.png", "02  CITY / NIGHT"),
          ("03_city_suspicion.png", "03  CITY / HIGH SUSPICION"), ("04_combat.png", "04  COMBAT"),
          ("05_shop.png", "05  BLACK-MARKET SHOP")]


def main():
    tw, th = 960, 540
    pad, lab = 24, 44
    cols = 2
    rows = 3
    W = cols * tw + (cols + 1) * pad
    H = 90 + rows * (th + lab) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), (221, 206, 188))
    d = ImageDraw.Draw(sheet)
    ft = ImageFont.truetype(FONT, 46)
    fl = ImageFont.truetype(FONT, 26)
    d.text((pad, 22), "R2A  LOW-POLY 3D  -  flat-shaded facets, soft key light, muted warm palette", font=ft,
           fill=(58, 40, 52))
    for k, (fn, label) in enumerate(STILLS):
        p = os.path.join(BASE, "stills", fn)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        c, r = k % cols, k // cols
        x = pad + c * (tw + pad)
        y = 90 + pad + r * (th + lab + pad)
        if k == 4:
            x = (W - tw) // 2
        sheet.paste(im, (x, y))
        d.text((x, y + th + 6), label, font=fl, fill=(58, 40, 52))
    out = os.path.join(BASE, "contact_sheet.jpg")
    sheet.save(out, quality=88, optimize=True)
    print("SHEET", out)


if __name__ == "__main__":
    main()
