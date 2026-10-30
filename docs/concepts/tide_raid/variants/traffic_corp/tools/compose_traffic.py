"""Traffic-corp variant sheets: per view an r43 | variant pair (JPG), the squint pairs (heavy blur at 1/16 scale) and compare.jpg. Run by path: python compose_traffic.py"""
import os
from PIL import Image, ImageDraw, ImageFilter

S = "D:/rc_scratch/traffic/"
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/variants/traffic_corp/"
VIEWS = [
    ("plan", S + "cap/plan_b.png", S + "cap/plan_v.png", "plan (seed 7, plate camera)"),
    ("closeup", S + "cap/cu_b.png", S + "cap/cu_v.png", "downtown close-up, street level + deck (zoom 5 at lot -57,3)"),
]


def label(im, text):
    im = im.copy()
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10 + 7 * len(text), 20), fill=(8, 8, 20))
    d.text((5, 4), text, fill=(255, 255, 255))
    return im


def squint(im):
    """Heavy blur at 1/16 scale: blur at full size, shrink to 1/16, show enlarged x4 (smooth) so it can be judged by eye."""
    small = im.filter(ImageFilter.GaussianBlur(10)).resize((im.width // 16, im.height // 16), Image.LANCZOS)
    return small.resize((im.width // 4, im.height // 4), Image.BICUBIC)


os.makedirs(OUT, exist_ok=True)
rows = []
sq = []
for name, a, b, title in VIEWS:
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")
    pair = Image.new("RGB", (ia.width * 2, ia.height))
    pair.paste(label(ia, "r43 " + title), (0, 0))
    pair.paste(label(ib, "variant: traffic carries the corp colour"), (ia.width, 0))
    pair.save(OUT + "%s_r43_vs_variant.jpg" % name, quality=90)
    rows.append((label(ia.resize((960, 540), Image.LANCZOS), "r43 " + name), label(ib.resize((960, 540), Image.LANCZOS), "variant " + name)))
    sa, sb = squint(ia), squint(ib)
    sq.append((sa, sb))
sheet = Image.new("RGB", (1920, 540 * len(rows)))
for i, (x, y) in enumerate(rows):
    sheet.paste(x, (0, i * 540))
    sheet.paste(y, (960, i * 540))
sheet.save(OUT + "compare.jpg", quality=88)
w, h = sq[0][0].size
ss = Image.new("RGB", (w * 2 + 8, (h + 8) * len(sq)), (20, 20, 20))
for i, (x, y) in enumerate(sq):
    ss.paste(x, (0, i * (h + 8)))
    ss.paste(y, (w + 8, i * (h + 8)))
ss.save(OUT + "squint_r43_vs_variant.png")
print("done")
