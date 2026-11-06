import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r29/"
A = "D:/rc_scratch/g1/r28/"
B = "D:/rc_scratch/g1/r29/"
P = (640, 360)
r6 = Image.open("D:/rc_art/art-pass/docs/concepts/round6_city_restyle/views/restyle_night_crop.png").convert("RGB")
sh = Image.new("RGB", (1920, 360))
for i, (im, t) in enumerate([(r6, "round 6 night crop (target)"), (C.load(A + "hot.png"), "r28 hotspot"), (C.load(B + "hot.png"), "r29 hotspot")]):
    sh.paste(C.label(im.resize(P, Image.LANCZOS), t), (i * 640, 0))
sh.save(OUT + "lookdev_vs_round6.jpg", quality=92)
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3))
for i, (p, t) in enumerate([(A + "plan.png", "r28 plan"), (B + "plan.png", "r29 plan"), (A + "hot.png", "r28 hotspot"), (B + "hot.png", "r29 hotspot"), (B + "seed3.png", "r29 seed 3"), (B + "hwy.png", "r29 highway close-up")]):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r28_r29.jpg", quality=90)
