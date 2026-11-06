import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r26/"
Bq = "D:/rc_scratch/g1/r25/"
B = "D:/rc_scratch/g1/r26/"
P = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3 + 360 + 600))
items = [(Bq + "plan.png", "r25 plan"), (B + "plan.png", "r26 plan"), (Bq + "hot.png", "r25 hotspot (zoom 3)"), (B + "hot.png", "r26 hotspot (zoom 3)"), (B + "lowrise.png", "r26 low-rise close-up: strips vs a grid"), (B + "amber.png", "r26 amber close-up")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(Bq + "plan.png"), "r25, real 320 px"), (C.load(B + "plan.png"), "r26, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 640), t), (i * 640, 1620))
box = (60, 560, 700, 960)
sheet.paste(C.label(plate.crop(box).resize((960, 600)), "plate lower-left crop"), (0, 1980))
sheet.paste(C.label(C.load(B + "plan.png").crop(box).resize((960, 600)), "r26 lower-left crop"), (960, 1980))
sheet.save(OUT + "compare_r25_r26.jpg", quality=92)
