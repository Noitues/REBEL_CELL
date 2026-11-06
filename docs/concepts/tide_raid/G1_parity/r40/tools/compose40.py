import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r40/"
A = "D:/rc_scratch/g1/r39/"
B = "D:/rc_scratch/g1/r40/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 5))
items = [(A + "plan.png", "r39 plan"), (B + "plan.png", "r40 plan (layout P1)"), (B + "seed3.png", "r40 seed 3"), (B + "hot.png", "r40 hotspot"), (B + "apron.png", "r40 bay apron close-up"), (B + "park.png", "r40 north park"), (B + "sky.png", "r40 skyline, wide (height field)"), (B + "street.png", "r40 street-level anchor, dense core")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r39_r40.jpg", quality=88)
