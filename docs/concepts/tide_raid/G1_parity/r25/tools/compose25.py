import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r25/"
Bq = "D:/rc_scratch/g1/r24/"
B = "D:/rc_scratch/g1/r25/"
P = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3 + 360 + 400))
items = [(Bq + "plan.png", "r24 plan"), (B + "plan.png", "r25 plan"), (Bq + "hot.png", "r24 hotspot (zoom 3)"), (B + "hot.png", "r25 hotspot (zoom 3)"), (B + "amber.png", "r25 amber close-up (zoom 3)"), (B + "seed3.png", "r25 seed 3")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
y = 1620
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(Bq + "plan.png"), "r24, real 320 px"), (C.load(B + "plan.png"), "r25, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 640), t), (i * 640, y))
box = (60, 560, 700, 960)
pc = plate.crop(box); rc = C.load(B + "plan.png").crop(box)
sheet.paste(C.label(pc.resize((960, 600)), "plate lower-left crop (same scale)"), (0, 1980))
sheet.paste(C.label(rc.resize((960, 600)), "r25 lower-left crop"), (960, 1980))
sheet = sheet.crop((0, 0, 1920, 2580))
sheet.save(OUT + "compare_r24_r25.jpg", quality=92)
