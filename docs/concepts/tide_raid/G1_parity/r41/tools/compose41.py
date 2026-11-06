import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r41/"
A = "D:/rc_scratch/g1/r40/"
B = "D:/rc_scratch/g1/r41/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 5))
items = [(A + "plan.png", "r40 plan"), (B + "plan.png", "r41 plan"), (A + "apron.png", "r40 bay apron"), (B + "apron.png", "r41 bay apron (quay, tree line, warehouses)"), (A + "park.png", "r40 north park"), (B + "park.png", "r41 north park (lit paths, lamps)"), (B + "sw.png", "r41 south-west low-rise"), (B + "slab.png", "r41 slab west of the Solace park (lawn dressing)"), (B + "seed3.png", "r41 seed 3"), (B + "hot.png", "r41 hotspot")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r40_r41.jpg", quality=88)
