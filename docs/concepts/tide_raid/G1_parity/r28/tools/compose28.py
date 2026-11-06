import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r28/"
Bq = "D:/rc_scratch/g1/r27/"
B = "D:/rc_scratch/g1/r28/"
P = (960, 540)
r6 = Image.open("D:/rc_art/art-pass/docs/concepts/round6_city_restyle/views/restyle_night_crop.png").convert("RGB")
sh = Image.new("RGB", (1920, 540))
sh.paste(C.label(r6.resize(P, Image.LANCZOS), "round 6 night crop (target)"), (0, 0))
sh.paste(C.label(C.load(B + "hot.png", P), "Godot r28 hotspot (zoom 3)"), (960, 0))
sh.save(OUT + "lookdev_vs_round6.jpg", quality=92)
sheet = Image.new("RGB", (1920, 540 * 4))
items = [(Bq + "plan.png", "r27 plan"), (B + "plan.png", "r28 plan"), (Bq + "hot.png", "r27 hotspot"), (B + "hot.png", "r28 hotspot"),
         (B + "ave_dim.png", "street A/B: dim avenues (0.25)"), (B + "ave_full.png", "street A/B: round-6 strength (1.4)"), (Bq + "seed3.png", "r27 seed 3"), (B + "seed3.png", "r28 seed 3")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r27_r28.jpg", quality=90)
C.load(B + "hwy.png").save(OUT + "highway_closeup_r28.png")
