import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r32/"
A = "D:/rc_scratch/g1/r31/"
B = "D:/rc_scratch/g1/r32/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 4))
ave = C.load(B + "ave.png")
river = ave.crop((0, 760, 1200, 940)).resize((960, 144), Image.LANCZOS)
items = [(A + "plan.png", "r31 plan"), (B + "plan.png", "r32 plan"), (A + "seed3.png", "r31 seed 3"), (B + "seed3.png", "r32 seed 3"), (A + "ave.png", "r31 avenue close-up"), (B + "ave.png", "r32 avenue close-up"), (B + "bay.png", "r32 bay close-up")]
for i, (p, t) in enumerate(items):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.paste(C.label(river, "r32 river strip (crop of the avenue close-up, y 760-940)"), (960, 1620))
sheet.save(OUT + "compare_r31_r32.jpg", quality=90)
