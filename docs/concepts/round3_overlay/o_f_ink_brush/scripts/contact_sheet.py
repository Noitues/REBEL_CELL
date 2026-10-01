"""contact_sheet.jpg -- the four renders in a 2x2 grid with labels."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
names = ["01_combat.png", "02_city.png", "03_shop.png", "04_lifecycle.png"]
TW, TH, PAD, HEAD = 940, 529, 14, 56
sheet = Image.new("RGB", (PAD * 3 + TW * 2, HEAD + PAD * 3 + TH * 2 + 28), (18, 17, 21))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 26)
fs = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 16)
d.text((PAD, 16), "o_f_ink_brush  //  SUMI INK + WATERCOLOUR overlay over Cv2", font=f, fill=(236, 230, 220))
for i, n in enumerate(names):
    im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    x = PAD + (i % 2) * (TW + PAD)
    y = HEAD + (i // 2) * (TH + PAD + 14)
    sheet.paste(im, (x, y))
    d.text((x, y + TH + 2), n, font=fs, fill=(255, 92, 168))
sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=90)
