"""Round 24: targets_compare.jpg - every corp's target (boss night, boss cool day, regular night); Meridian from round 11."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
R11 = os.path.join(OUT, "..", "round11_combat_target")
CORPS = [("meridian", "MERIDIAN  -  The Manifest / container depot", (255, 140, 26)),
         ("solace", "SOLACE  -  Renewal Engine / Implant Provisioning Hub", (150, 255, 70)),
         ("halcyon", "HALCYON  -  The Civic Core / enforcement precinct", (176, 120, 255)),
         ("orbital", "ORBITAL  -  The Commons Array / Ground Station Alpha", (205, 240, 255)),
         ("rebel_cell", "REBEL_CELL  -  DISPATCH / Relay Rooftop", (232, 20, 30))]
ROWS = ["boss night", "boss day (cool)", "regular night"]
tw, th = 480, 270


def src(corp, row):
    if corp == "meridian":
        return os.path.join(R11, ["target_building_night.png", "target_building_day_cool.png", "scratch/backdrops/regular_night.png"][row])
    return os.path.join(OUT, "target_%s_%s.png" % (corp, ["boss_night", "boss_day", "regular_night"][row]))


f1 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 30)
f2 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 16)
W = 290 + 3 * (tw + 10)
H = 60 + len(CORPS) * (th + 34)
sh = Image.new("RGB", (W, H), (14, 13, 20))
d = ImageDraw.Draw(sh)
d.text((16, 14), "ROUND 24  TARGET BUILDINGS  -  combat backdrops per corp", font=f1, fill=(240, 236, 226))
for c, r in enumerate(ROWS):
    d.text((290 + c * (tw + 10), 44), r.upper(), font=f2, fill=(255, 214, 64))
for i, (corp, cap, col) in enumerate(CORPS):
    y = 66 + i * (th + 34)
    d.rectangle([10, y, 16, y + th], fill=col)
    for k, word in enumerate(cap.split("  -  ")):
        d.text((24, y + 6 + k * 26), word if k == 0 else "", font=f2, fill=col)
    lines = cap.split("  -  ")[1].split(" / ")
    for k, ln in enumerate(lines):
        d.text((24, y + 40 + k * 22), ("boss: " if k == 0 else "reg: ") + ln, font=f2, fill=(205, 205, 215))
    for r in range(3):
        p = src(corp, r)
        if os.path.exists(p):
            sh.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (290 + r * (tw + 10), y))
sh.save(os.path.join(OUT, "targets_compare.jpg"), quality=88)
print("targets_compare.jpg")
