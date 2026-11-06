import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image, ImageDraw
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r36/"
A = "D:/rc_scratch/g1/r36/"
B = "D:/rc_scratch/g1/r36/after/"
im = Image.open(A + "hc.png").convert("RGB")
d = ImageDraw.Draw(im)
marks = [((540, 300), "(a) strip below ground rise: flat quad at lot-centre height"), ((420, 120), "(a)/(c) mid-avenue dark gap"), ((150, 520), "(d) crossing: perpendicular strip overlaps in another hue"), ((820, 560), "(a) lot rim / kerb pokes through"), ((1030, 300), "(c) open-run stop")]
for (x, y), t in marks:
    d.ellipse((x - 45, y - 30, x + 45, y + 30), outline=(255, 40, 40), width=3)
    d.text((min(x + 50, 700), y - 6), t, fill=(255, 255, 255), font=C.FONT)
im.save(OUT + "avenue_cuts_before.jpg", quality=92)
Q = (960, 540)
sheet = Image.new("RGB", (1920, 540 * 4))
for i, (p, t) in enumerate([(A + "plan.png", "r35 plan"), (B + "plan.png", "r36 plan"), (A + "hot.png", "r35 hotspot"), (B + "hot.png", "r36 hotspot"), (B + "seed3.png", "r36 seed 3"), (B + "ave.png", "r36 avenue close-up 1"), (B + "ave2.png", "r36 avenue close-up 2")]):
    sheet.paste(C.label(C.load(p, Q), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r35_r36.jpg", quality=90)
