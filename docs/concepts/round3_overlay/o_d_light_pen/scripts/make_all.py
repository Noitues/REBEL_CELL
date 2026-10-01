"""Render all four sheets + the contact sheet into the o_d_light_pen folder."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from lightpen import OUT_DIR, font
import combat, city, shop, lifecycle

names = ["01_combat.png", "02_city.png", "03_shop.png", "04_lifecycle.png"]
for mod, name in zip((combat, city, shop, lifecycle), names):
    mod.render(OUT_DIR + name)
    print("rendered", name, flush=True)

W, H = 1920, 1080
tw, th = 940, 529
sheet = Image.new("RGB", (tw * 2 + 60, th * 2 + 150), (11, 12, 17))
d = ImageDraw.Draw(sheet)
d.text((20, 18), "O_D  LIGHT PEN  -  the Cell writes on the world in hand-drawn light",
       font=font(40, "Bold Condensed"), fill=(236, 230, 240))
for i, name in enumerate(names):
    im = Image.open(OUT_DIR + name).convert("RGB").resize((tw, th), Image.LANCZOS)
    x = 20 + (i % 2) * (tw + 20)
    y = 80 + (i // 2) * (th + 30)
    sheet.paste(im, (x, y))
sheet.save(OUT_DIR + "contact_sheet.jpg", quality=90)
print("contact sheet done")
