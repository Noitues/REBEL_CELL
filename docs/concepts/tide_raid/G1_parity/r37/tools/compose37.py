import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r37/"
A = "D:/rc_scratch/g1/r36/after/"
B = "D:/rc_scratch/g1/r37/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 4))
for i, (p, t) in enumerate([(A + "plan.png", "r36 plan"), (B + "plan.png", "r37 plan"), (A + "seed3.png", "r36 seed 3"), (B + "seed3.png", "r37 seed 3"), (B + "ix.png", "r37 interchange close-up (bay crossing)"), (B + "avend.png", "r37 avenue-end close-up (park side)"), (B + "hot.png", "r37 hotspot")]):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r36_r37.jpg", quality=90)
