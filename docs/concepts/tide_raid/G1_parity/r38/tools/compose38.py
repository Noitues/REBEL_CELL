import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r38/"
A = "D:/rc_scratch/g1/r37/"
B = "D:/rc_scratch/g1/r38/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 5))
items = [(A + "plan.png", "r37 plan"), (B + "plan.png", "r38 plan (layout P0)"), (A + "seed3.png", "r37 seed 3"), (B + "seed3.png", "r38 seed 3"), (B + "hot.png", "r38 hotspot"), (B + "bay.png", "r38 bay close-up"), (B + "a_park.png", "anchor: park edge"), (B + "a_cross.png", "anchor: highway crossing"), (B + "a_shore.png", "anchor: shoreline")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r37_r38.jpg", quality=88)
