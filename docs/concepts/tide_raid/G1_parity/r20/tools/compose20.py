import sys
sys.path.insert(0, "D:/rc_scratch/g1/r19")
import compose as C
C.OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r20/"
A = "D:/rc_scratch/g1/r19/r19/"
B = "D:/rc_scratch/g1/r20/"
from PIL import Image
def compare():
    P = (960, 540)
    sheet = Image.new("RGB", (1920, 540 * 2 + 360))
    pairs = [(A + "plan.png", "r19 plan"), (B + "plan.png", "r20 plan"), (A + "hot.png", "r19 hotspot (zoom 3)"), (B + "hot.png", "r20 hotspot (zoom 3)")]
    for i, (p, t) in enumerate(pairs):
        sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
    plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
    plate = plate.crop((0, 0, plate.width // 2, plate.height))
    for i, (im, t) in enumerate([(plate, "plate, real 320 px downsample"), (C.load(A + "plan.png"), "r19, real 320 px downsample"), (C.load(B + "plan.png"), "r20, real 320 px downsample")]):
        sheet.paste(C.label(C.squint(im, 640), t), (i * 640, 1080))
    sheet.save(C.OUT + "compare_r19_r20.jpg", quality=92)
def generality():
    P = (960, 540)
    sheet = Image.new("RGB", (1920, 1080))
    items = [(B + "plan.png", "plan (seed 7)"), (B + "seed3.png", "seed 3"), (B + "seed19.png", "seed 19"), (B + "park.png", "seed 7 park edge and highway, zoom 3.5")]
    for i, (p, t) in enumerate(items):
        sheet.paste(C.label(C.load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
    sheet.save(C.OUT + "generality_sheet_r20.jpg", quality=92)
compare(); generality()
