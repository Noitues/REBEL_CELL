import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
from PIL import Image
R = "D:/rc_scratch/g1/r25/"
plate = Image.open("D:/rc_scratch/g1/r19/plate.png").convert("RGB")
sheet = Image.new("RGB", (1800, 1200))
box = (60, 560, 700, 960)
tiles = [("plate crop (plan scale)", plate.crop(box).resize((600, 375)))]
for n, t in (("A", "A street pools + tiny white points"), ("B", "B + brighter amber points"), ("C", "C lifted bodies, strong street + base warmth")):
    tiles.append((t, C.load(R + n + "_plan.png").crop(box).resize((600, 375))))
for i, (t, im) in enumerate(tiles[:3]):
    sheet.paste(C.label(im, t), (i * 600, 0))
sheet.paste(C.label(tiles[3][1], tiles[3][0]), (0, 400))
for i, n in enumerate("ABC"):
    sheet.paste(C.label(C.load(R + n + "_amber.png").crop((300, 100, 900, 500)), n + " close-up (zoom 3)"), (i * 600, 800))
sheet.paste(Image.new("RGB", (1200, 375)), (600, 400))
for i, n in enumerate("ABC"):
    pass
sq = [C.squint(C.load(R + n + "_plan.png"), 600) for n in "ABC"]
for i, s in enumerate(sq):
    sheet.paste(C.label(s.crop((0, 0, 600, 337)), "320 px squint " + "ABC"[i]), (600 * i if i else 600, 400) if i < 2 else (1200, 400))
sheet.save("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r25/amber_options.jpg", quality=92)
