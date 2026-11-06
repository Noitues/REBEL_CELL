import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r21/"
A = "D:/rc_scratch/g1/r19/r19/"
Bq = "D:/rc_scratch/g1/r20/"
B = "D:/rc_scratch/g1/r21/"
P = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 2 + 270))
for i, (p, t) in enumerate([(Bq + "plan.png", "r20 plan"), (B + "plan.png", "r21 plan"), (Bq + "hot.png", "r20 hotspot (zoom 3)"), (B + "hot.png", "r21 hotspot (zoom 3)")]):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(A + "plan.png"), "r19, real 320 px"), (C.load(Bq + "plan.png"), "r20, real 320 px"), (C.load(B + "plan.png"), "r21, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 480), t), (i * 480, 1080))
sheet.save(OUT + "compare_r20_r21.jpg", quality=92)
sh = Image.new("RGB", (1920, 1080))
for i, (p, t) in enumerate([(B + "plan.png", "plan (seed 7)"), (B + "seed3.png", "seed 3"), (B + "seed19.png", "seed 19"), (B + "park.png", "seed 7 park edge and highway, zoom 3.5")]):
    sh.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
sh.save(OUT + "generality_sheet_r21.jpg", quality=92)
h = Image.new("RGB", (1920, 540))
h.paste(C.label(C.load(B + "hot.png", P), "hotspot, holos on"), (0, 0))
h.paste(C.label(C.load(B + "hot_noholo.png", P), "hotspot, holos off (--no-holo)"), (960, 0))
h.save(OUT + "hotspot_holos_on_off_r21.png")
