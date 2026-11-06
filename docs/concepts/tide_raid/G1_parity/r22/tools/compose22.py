import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r22/"
Bq = "D:/rc_scratch/g1/r21/"
B = "D:/rc_scratch/g1/r22/"
P = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3 + 360))
items = [(Bq + "plan.png", "r21 plan"), (B + "plan.png", "r22 plan"), (Bq + "hot.png", "r21 hotspot (zoom 3)"), (B + "hot.png", "r22 hotspot (zoom 3)"), (B + "amber.png", "r22 amber district close-up (zoom 3)"), (B + "seed3.png", "r22 seed 3")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(Bq + "plan.png"), "r21, real 320 px"), (C.load(B + "plan.png"), "r22, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 640), t), (i * 640, 1620))
sheet.save(OUT + "compare_r21_r22.jpg", quality=92)
