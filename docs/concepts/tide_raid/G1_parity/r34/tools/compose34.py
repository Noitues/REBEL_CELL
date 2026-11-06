import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r34/"
A = "D:/rc_scratch/g1/r33/"
B = "D:/rc_scratch/g1/r34/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3))
river = C.load(B + "ave.png").crop((0, 760, 1200, 940)).resize((960, 144), Image.LANCZOS)
for i, (p, t) in enumerate([(A + "plan.png", "r33 plan"), (B + "plan.png", "r34 plan"), (A + "seed3.png", "r33 seed 3"), (B + "seed3.png", "r34 seed 3"), (B + "bay.png", "r34 bay close-up")]):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.paste(C.label(river, "river strip (reference blue)"), (960, 1080))
sheet.save(OUT + "compare_r33_r34.jpg", quality=90)
