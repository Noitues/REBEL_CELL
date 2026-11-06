import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r23/"
Bq = "D:/rc_scratch/g1/r22/"
B = "D:/rc_scratch/g1/r23/"
P = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3 + 360))
items = [(Bq + "plan.png", "r22 plan"), (B + "plan.png", "r23 plan"), (Bq + "hot.png", "r22 hotspot (zoom 3)"), (B + "hot.png", "r23 hotspot (zoom 3)"), (B + "amber.png", "r23 amber district close-up (zoom 3)"), (B + "seed3.png", "r23 seed 3")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
plate = plate.crop((0, 0, plate.width // 2, plate.height))
for i, (im, t) in enumerate([(plate, "plate, real 320 px"), (C.load(Bq + "plan.png"), "r22, real 320 px"), (C.load(B + "plan.png"), "r23, real 320 px")]):
    sheet.paste(C.label(C.squint(im, 640), t), (i * 640, 1620))
sheet.save(OUT + "compare_r22_r23.jpg", quality=92)
n = Image.new("RGB", (1920, 540))
n.paste(C.label(Image.open(B + "nr_before/overview_seed1/beauty.png").convert("RGB").resize(P), "netrun overview, r22 code"), (0, 0))
n.paste(C.label(Image.open(B + "nr_after/overview_seed1/beauty.png").convert("RGB").resize(P), "netrun overview, r23 code"), (960, 0))
n.save(OUT + "netrun_before_after_r23.png")
