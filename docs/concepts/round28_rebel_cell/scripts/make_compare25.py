"""Round 25: hq_compare.jpg - per corp: city-map crop | close-up night | close-up day (or the variant) | combat | Site."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROWS = [("meridian", "MERIDIAN  -  Container Castle", (255, 140, 26), ["hq_meridian_city.png", "hq_meridian_close_night.png", "hq_meridian_close_day.png", "combat_meridian.png", "site_meridian_night.png"]),
        ("solace", "SOLACE  -  the Double Helix", (150, 255, 70), ["hq_solace_city.png", "hq_solace_close_night.png", "hq_solace_close_day.png", "combat_solace.png", "site_solace_night.png"]),
        ("halcyon", "HALCYON  -  the Civic Core", (176, 120, 255), ["hq_halcyon_city.png", "hq_halcyon_close_night.png", "hq_halcyon_close_day.png", "combat_halcyon.png", "site_halcyon_night.png"]),
        ("orbital", "ORBITAL  -  the Silo Crescent", (205, 240, 255), ["hq_orbital_city.png", "hq_orbital_close_night.png", "hq_orbital_close_night_open.png", "combat_orbital.png", "site_orbital_night.png"]),
        ("rebel_cell", "REBEL_CELL  -  the Cell's base / DISPATCH", (232, 20, 30), ["hq_rebel_cell_city.png", "hq_rebel_cell_close_night.png", "hq_rebel_cell_close_night_dispatch.png", "combat_rebel_cell.png", "site_rebel_cell_night.png"])]
COLS = ["CITY MAP CROP", "CLOSE-UP NIGHT (home / closed)", "CLOSE-UP DAY  |  OPEN  |  DISPATCH", "COMBAT", "REGULAR SITE"]
tw, th = 400, 225
f1 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 30)
f2 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 16)
W = 20 + 5 * (tw + 8)
H = 92 + len(ROWS) * (th + 40)
sh = Image.new("RGB", (W, H), (14, 13, 20))
d = ImageDraw.Draw(sh)
d.text((14, 12), "ROUND 25  -  the boss target IS the HQ: one model for the city map and the combat close-up", font=f1, fill=(240, 236, 226))
for c, t in enumerate(COLS):
    d.text((20 + c * (tw + 8), 60), t, font=f2, fill=(255, 214, 64))
for r, (corp, cap, col, files) in enumerate(ROWS):
    y = 84 + r * (th + 40)
    d.text((20, y), cap, font=f2, fill=col)
    for c, fn in enumerate(files):
        p = os.path.join(OUT, fn)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            k = max(tw / im.width, th / im.height)
            im = im.resize((int(im.width * k + 1), int(im.height * k + 1)), Image.LANCZOS)
            x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
            sh.paste(im.crop((x0, y0, x0 + tw, y0 + th)), (20 + c * (tw + 8), y + 20))
sh.save(os.path.join(OUT, "hq_compare.jpg"), quality=87)
print("hq_compare.jpg")
