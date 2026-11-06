import json
import sys
from PIL import Image, ImageDraw, ImageFont

R = "D:/rc_scratch/g1/r19/"
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r19/"
FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)


def load(p, size=None):
    im = Image.open(p).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return im


def label(im, text):
    d = ImageDraw.Draw(im)
    w = d.textlength(text, font=FONT) + 16
    d.rectangle((0, 0, w, 30), fill=(8, 8, 20))
    d.text((8, 3), text, fill=(255, 255, 255), font=FONT)
    return im


def squint(im, width_out):
    w, h = im.size
    s = im.resize((320, round(320 * h / w)), Image.BOX)
    return s.resize((width_out, round(width_out * h / w)), Image.BICUBIC)


def compare():
    P = (960, 540)
    sheet = Image.new("RGB", (1920, 540 * 2 + 360), (0, 0, 0))
    pairs = [(R + "r18/plan.png", "r18 plan (rails, dim highways)"), (R + "r19/plan.png", "r19 plan"),
             (R + "r18/hot.png", "r18 hotspot close-up (zoom 3)"), (R + "r19/hot.png", "r19 hotspot close-up (zoom 3)")]
    for i, (p, t) in enumerate(pairs):
        sheet.paste(label(load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
    plate = Image.open("D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/final/01_plan_side_by_side.png").convert("RGB")
    plate = plate.crop((0, 0, plate.width // 2, plate.height))
    for i, (im, t) in enumerate([(plate, "plate 320 px squint"), (load(R + "r18/plan.png"), "r18 320 px squint"), (load(R + "r19/plan.png"), "r19 320 px squint")]):
        sq = squint(im, 640)
        sheet.paste(label(sq, t), (i * 640, 1080))
    sheet.save(OUT + "compare_r18_r19.jpg", quality=92)


def highway():
    P = (960, 540)
    sheet = Image.new("RGB", (1920, 1080))
    items = [(R + "r18/hw1.png", "before (r18) core highway, zoom 4"), (R + "r19/hw1.png", "after (r19)"),
             (R + "r18/hw2.png", "before (r18) interchange, zoom 4"), (R + "r19/hw2.png", "after (r19)")]
    for i, (p, t) in enumerate(items):
        sheet.paste(label(load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
    sheet.save(OUT + "highway_before_after.png")


KCOL = {0: (120, 120, 120), 1: (60, 110, 255), 2: (255, 150, 40), 3: (255, 40, 190), 4: (40, 230, 215), 5: (160, 110, 255), 6: (235, 240, 255), 7: (0, 0, 0), 8: (255, 255, 255)}
KNAME = {1: "cool, dark", 2: "warm amber", 3: "neon dense (magenta)", 4: "teal glass", 5: "violet, mid", 6: "pale cold glass", 7: "dark gap (district border)", 8: "white-hot tower"}


def districts():
    rows = json.load(open(R + "r19/plan_prisms.json"))
    base = load(R + "r19/plan.png")
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for t, h, x, y, yb, k, a in rows:
        if x < -20 or x > 1940 or y < -20 or y > 1100:
            continue
        c = KCOL[a]
        r = 10 if a == 8 else 5
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (215,), outline=(255, 255, 255, 255) if a == 7 else ((0, 0, 0, 255) if a == 8 else None))
    mp = Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")
    sheet = Image.new("RGB", (1920, 540 + 540), (0, 0, 0))
    sheet.paste(label(mp.resize((960, 540), Image.LANCZOS), "district map: one dot per building, coloured by art district"), (0, 0))
    sheet.paste(label(squint(base, 960), "r19 320 px squint"), (960, 0))
    sheet.paste(label(squint(load(R + "r18/plan.png"), 960), "r18 320 px squint (for comparison)"), (0, 540))
    leg = Image.new("RGB", (960, 540), (10, 10, 24))
    dl = ImageDraw.Draw(leg)
    dl.text((20, 14), "legend", fill=(255, 255, 255), font=FONT)
    y = 56
    for k, n in KNAME.items():
        dl.rectangle((20, y, 60, y + 28), fill=KCOL[k], outline=(255, 255, 255))
        dl.text((76, y + 2), n, fill=(255, 255, 255), font=FONT)
        y += 44
    sheet.paste(leg, (960, 540))
    sheet.save(OUT + "district_map.png")


def generality():
    P = (960, 540)
    sheet = Image.new("RGB", (1920, 1080))
    items = [(R + "r19/plan.png", "plan (seed 7)"), (R + "r19/seed3.png", "seed 3"), (R + "r19/seed19.png", "seed 19"), (R + "r19/park.png", "seed 7 park edge and highway, zoom 3.5")]
    for i, (p, t) in enumerate(items):
        sheet.paste(label(load(p, P), t), ((i % 2) * 960, (i // 2) * 540))
    sheet.save(OUT + "generality_sheet_r19.jpg", quality=92)


if __name__ == "__main__":
    for fn in sys.argv[1:]:
        globals()[fn]()
