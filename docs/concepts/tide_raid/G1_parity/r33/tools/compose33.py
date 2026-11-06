import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image, ImageDraw
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r33/"
A = "D:/rc_scratch/g1/r32/"
B = "D:/rc_scratch/g1/r33/"
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 3))
ave = C.load(B + "ave.png")
river = ave.crop((0, 760, 1200, 940)).resize((960, 144), Image.LANCZOS)
for i, (p, t) in enumerate([(A + "plan.png", "r32 plan"), (B + "plan.png", "r33 plan"), (A + "seed3.png", "r32 seed 3"), (B + "seed3.png", "r33 seed 3"), (B + "bay.png", "r33 bay close-up")]):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.paste(C.label(river, "river strip (reference blue)"), (960, 1080))
sheet.save(OUT + "compare_r32_r33.jpg", quality=90)
m = Image.new("RGB", (1920, 540))
m.paste(C.label(C.load(B + "mask_plan.png", Q), "plan: river cyan, plan-water blue (none), terrain<=0 magenta, land green dots"), (0, 0))
m.paste(C.label(C.load(B + "mask_seed3.png", Q), "seed 3: same legend"), (960, 0))
m.save(OUT + "water_mask_overlay.jpg", quality=90)
