"""Round 43 sheets: compare_r42_r43.jpg (before / after of the two park fixes plus seed 3), raid_grade_beats.jpg (beats 02, 03, 04 r42 | r43 graded) and raid_grade_squint.jpg."""
import os
from PIL import Image, ImageDraw, ImageFilter

G = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/"
OUT = G + "r43/"
S = "D:/rc_scratch/g1/r43/"
Q = (960, 540)


def label(im, text):
    im = im.copy()
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 7 * len(text), 20), fill=(8, 8, 20))
    d.text((5, 4), text, fill=(255, 255, 255))
    return im


def load(p, size=Q):
    return Image.open(p).convert("RGB").resize(size, Image.LANCZOS)


# 1. compare_r42_r43.jpg
items = [
    (S + "cmp/plan_b.png", "r42 plan"), (S + "cmp/plan_a.png", "r43 plan"),
    (S + "cmp/park_b.png", "r42 north park (grey diamonds)"), (S + "cmp/park_a.png", "r43 north park (ground under the lawn)"),
    (S + "cmp/apron_b.png", "r42 apron (grey slab under the deck)"), (S + "cmp/apron_a.png", "r43 apron (dressed)"),
    (S + "cmp/seed3_b.png", "r42 seed 3"), (S + "cmp/seed3_a.png", "r43 seed 3"),
]
sheet = Image.new("RGB", (1920, 540 * 4))
for i, (p, t) in enumerate(items):
    sheet.paste(label(load(p), t), ((i % 2) * 960, (i // 2) * 540))
sheet.save(OUT + "compare_r42_r43.jpg", quality=88)

# 2. raid beats
beats = [("02_forecast", "lab/g_daemon_60/f_0060.png", "lab/n_daemon_60/f_0060.png"),
         ("03_reveal", "lab/g_daemon_150/f_0150.png", "lab/n_daemon_150/f_0150.png"),
         ("04_impact", "lab/g_home_70/f_0070.png", "lab/n_home_70/f_0070.png")]
sheet = Image.new("RGB", (1920, 540 * 3))
sq = Image.new("RGB", (1280, 180 * 3 + 0))
rows = []
for i, (n, g, nog) in enumerate(beats):
    sb = Image.open(G + "final_proposed/%s_side_by_side.png" % n).convert("RGB")
    r42 = sb.crop((sb.width // 2, 0, sb.width, sb.height))
    r43 = Image.open(S + g).convert("RGB")
    sheet.paste(label(r42.resize(Q, Image.LANCZOS), n + "  r42"), (0, i * 540))
    sheet.paste(label(r43.resize(Q, Image.LANCZOS), n + "  r43 raid grade"), (960, i * 540))
    r43.save(OUT + "%s_r43.png" % n)
    r42.save(OUT + "%s_r42.png" % n)
    rows.append((n, r42, r43))
sheet.save(OUT + "raid_grade_beats.jpg", quality=88)

# 3. squint: 320 px wide and a 4 px blur at 1920 (the side_by_side tool's recipe), r42 and r43 pairs per beat
w = 320
cell = (w, int(w * 1080 / 1920))
sq = Image.new("RGB", (cell[0] * 4, cell[1] * 3 * 2))
for i, (n, a, b) in enumerate(rows):
    for j, im in enumerate((a, b)):
        small = im.resize(cell, Image.LANCZOS)
        blur = im.filter(ImageFilter.GaussianBlur(4)).resize(cell, Image.LANCZOS)
        sq.paste(small, (j * 2 * cell[0], i * 2 * cell[1]))
        sq.paste(blur, ((j * 2 + 1) * cell[0], i * 2 * cell[1]))
        # second line: heavier blur (the squint test proper)
        heavy = im.resize((w, cell[1]), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
        sq.paste(heavy, (j * 2 * cell[0], i * 2 * cell[1] + cell[1]))
        heavy2 = im.filter(ImageFilter.GaussianBlur(14)).resize(cell, Image.LANCZOS)
        sq.paste(heavy2, ((j * 2 + 1) * cell[0], i * 2 * cell[1] + cell[1]))
sq = sq.resize((sq.width * 2, sq.height * 2), Image.LANCZOS)
sq.save(OUT + "raid_grade_squint.png")
print("ok")
