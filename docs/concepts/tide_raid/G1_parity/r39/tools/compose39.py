import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r39/"
A = "D:/rc_scratch/g1/r38/"
B = "D:/rc_scratch/g1/r39/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 4))
items = [(A + "plan.png", "r38 plan"), (B + "plan.png", "r39 plan"), (B + "seed3.png", "r39 seed 3"), (B + "hot.png", "r39 hotspot (avenue crossings)"), (B + "park.png", "r39 north park close-up (paths, ponds, lawn under the deck)"), (B + "shore.png", "r39 shoreline (bank highlight)"), (B + "cross.png", "r39 river / bay crossing close-up")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r38_r39.jpg", quality=88)
