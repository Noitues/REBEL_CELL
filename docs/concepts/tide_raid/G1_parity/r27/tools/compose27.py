import sys, json
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image, ImageDraw
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r27/"
Bq = "D:/rc_scratch/g1/r26/"
B = "D:/rc_scratch/g1/r27/"
P = (960, 540)
cols = {1: (150, 255, 70), 2: (176, 110, 255), 3: (255, 140, 26), 4: (205, 240, 255), 5: (41, 219, 166), 0: (120, 120, 120)}
rows = json.load(open(B + "plan_prisms.json"))
base = C.load(B + "plan.png").convert("RGBA")
ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
for r in rows:
    k = r[6]; x, y = r[2], r[3]
    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=cols[k] + (230,))
for name, x, y in json.load(open(B + "plan_hqs.json")):
    d.rectangle((x - 16, y - 16, x + 16, y + 16), outline=(255, 255, 255, 255), width=4)
    d.text((x + 20, y - 8), name, fill=(255, 255, 255, 255), font=C.FONT)
dbg = Image.alpha_composite(base, ov).convert("RGB")
sheet = Image.new("RGB", (1920, 540 * 3 + 360 + 540))
items = [(Bq + "plan.png", "r26 plan"), (B + "plan.png", "r27 plan"), (B + "hot.png", "r27 hotspot (zoom 3)"), (B + "seed3.png", "r27 seed 3"),
         (B + "bayix.png", "red box: interchange by the bay"), (B + "riverw.png", "red box: river edge, traffic, towers"),
         (B + "land3.png", "red box: park ground"), (B + "hwy.png", "red box: traffic streaks on the city highway")]
for i, (p, t) in enumerate(items[:6]):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(Bq + "plan.png"), "r26, real 320 px"), (C.load(B + "plan.png"), "r27, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 640), t), (i * 640, 1620))
sheet.paste(C.label(dbg.resize(P, Image.LANCZOS), "corp-weight debug map (dot = building's corp colour, box = HQ)"), (0, 1980))
sheet.paste(C.label(C.load(B + "land3.png", P), "park ground (zoom 2)"), (960, 1980))
sheet.save(OUT + "compare_r26_r27.jpg", quality=90)
