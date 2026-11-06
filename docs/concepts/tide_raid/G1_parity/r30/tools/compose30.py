import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r30/"
A = "D:/rc_scratch/g1/r29/"
B = "D:/rc_scratch/g1/r30/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 4))
r6 = Image.open("D:/rc_art/art-pass/docs/concepts/round6_city_restyle/views/restyle_night_crop.png").convert("RGB")
items = [(A + "plan.png", "r29 plan"), (B + "plan.png", "r30 plan"), (A + "hot.png", "r29 hotspot"), (B + "hot.png", "r30 hotspot"), (B + "seed3.png", "r30 seed 3"), (B + "hwy.png", "r30 highway close-up"), (B + "ave.png", "r30 avenue close-up")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.paste(C.label(r6.resize(Q, Image.LANCZOS), "round 6 night crop (avenue reference)"), (960, 1620))
sheet.save(OUT + "compare_r29_r30.jpg", quality=90)
