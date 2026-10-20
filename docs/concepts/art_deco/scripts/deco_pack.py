"""Pack the deliverables: NN_<subject>_deco.png (1920x1080), NN_<subject>_sbs.jpg, contact_sheet.jpg (<= 2560 px wide).
python deco_pack.py   (reads the finals under D:/rc_scratch/art_deco, writes into docs/concepts/art_deco/)"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
CON = os.path.normpath(os.path.join(OUT, ".."))
GP = os.path.join(CON, "golden_plates")
SC = "D:/rc_scratch/art_deco"
PANELS = [
    ("01", "whole_city", SC + "/city/v3/plate.png", GP + "/city_a2_night.png", "1. Whole city, A2 hero camera"),
    ("02", "halcyon", SC + "/halcyon/g3/plate.png", GP + "/hq_halcyon_overview.png", "2. Halcyon HQ: the ziggurat and its sunburst Eye"),
    ("03", "meridian", SC + "/meridian/g3/plate.png", GP + "/hq_meridian_overview.png", "3. Meridian HQ: the Gatehouse Gantry in brass"),
    ("04", "orbital", SC + "/orbital/g3/plate.png", GP + "/hq_orbital_overview.png", "4. Orbital HQ: sunburst pad, ringed silo"),
    ("05", "solace", SC + "/solace/g3/plate.png", GP + "/hq_solace_overview.png", "5. Solace HQ: the helix in brass ribs"),
    ("06", "netrun_street", SC + "/street/v2/plate.png", GP + "/street_decision.png", "6. Netrun street, decision camera"),
]
FONT = "C:/Windows/Fonts/arialbd.ttf"


def lum_median(im):
    return float(np.median(np.asarray(im.convert("L"), np.float32) / 255.0))


def main():
    sbs_imgs = []
    for nn, name, deco, cur, cap in PANELS:
        d = Image.open(deco).convert("RGB")
        if d.size != (1920, 1080):
            d = d.resize((1920, 1080), Image.LANCZOS)
        d.save(os.path.join(OUT, "%s_%s_deco.png" % (nn, name)))
        c = Image.open(cur).convert("RGB").resize((1280, 720), Image.LANCZOS)
        r = d.resize((1280, 720), Image.LANCZOS)
        sb = Image.new("RGB", (2560 + 8, 720), (12, 12, 12))
        sb.paste(c, (0, 0))
        sb.paste(r, (1288, 0))
        dr = ImageDraw.Draw(sb)
        f = ImageFont.truetype(FONT, 26)
        dr.rectangle([0, 0, 190, 40], fill=(0, 0, 0))
        dr.text((10, 6), "CURRENT", font=f, fill=(220, 220, 220))
        dr.rectangle([1288, 0, 1440, 40], fill=(0, 0, 0))
        dr.text((1298, 6), "DECO", font=f, fill=(255, 200, 90))
        sb.save(os.path.join(OUT, "%s_%s_sbs.jpg" % (nn, name)), quality=90)
        sbs_imgs.append((sb, cap, lum_median(d)))
        print(nn, name, "deco median %.3f" % lum_median(d))
    # contact sheet: 2 columns x 4 rows, each cell 1270 px wide with a caption strip
    cw = 1270
    ch = int(cw * 720 / 2568) + 34
    ch7 = int(2560 * 540 / (3 * 960 + 16)) + 34
    rows = 4
    v1 = Image.open(SC + "/city/prev_v2.png").convert("RGB").resize((1280, 720), Image.LANCZOS)
    v2 = Image.open(SC + "/city/v3/plate.png").convert("RGB").resize((1280, 720), Image.LANCZOS)
    cmp_ = Image.new("RGB", (2568, 720), (12, 12, 12))
    cmp_.paste(v1, (0, 0))
    cmp_.paste(v2, (1288, 0))
    dd = ImageDraw.Draw(cmp_)
    ff = ImageFont.truetype(FONT, 26)
    dd.text((10, 6), "DECO v2", font=ff, fill=(255, 200, 90))
    dd.text((1298, 6), "DECO v3", font=ff, fill=(255, 200, 90))
    cmp_.save(os.path.join(OUT, "01_whole_city_v2_v3.jpg"), quality=90)
    s1 = Image.open(SC + "/street/prev_v1.png").convert("RGB").resize((1280, 720), Image.LANCZOS)
    s2 = Image.open(SC + "/street/v2/plate.png").convert("RGB").resize((1280, 720), Image.LANCZOS)
    c2 = Image.new("RGB", (2568, 720), (12, 12, 12))
    c2.paste(s1, (0, 0)); c2.paste(s2, (1288, 0))
    d2 = ImageDraw.Draw(c2)
    d2.text((10, 6), "STREET v1", font=ff, fill=(255, 200, 90)); d2.text((1298, 6), "STREET v2", font=ff, fill=(255, 200, 90))
    c2.save(os.path.join(OUT, "06_netrun_street_v1_v2.jpg"), quality=90)
    # panel 7: variant A (frame only) and B (full wheel), one sbs: current | A | B
    cur = Image.open(CON + "/round41_wheel_stack/combat_typical_v4.png").convert("RGB")
    A = Image.open(SC + "/panel7_A.png").convert("RGB")
    B = Image.open(SC + "/panel7_A_B.png").convert("RGB")
    A.save(os.path.join(OUT, "07_combat_A_deco.png"))
    B.save(os.path.join(OUT, "07_combat_B_deco.png"))
    sb = Image.new("RGB", (3 * 960 + 16, 540), (12, 12, 12))
    f7 = ImageFont.truetype(FONT, 24)
    for i, (im, lab) in enumerate(((cur, "CURRENT"), (A, "A: FRAME"), (B, "B: FULL WHEEL"))):
        sb.paste(im.resize((960, 540), Image.LANCZOS), (i * 968, 0))
        ImageDraw.Draw(sb).text((i * 968 + 10, 6), lab, font=f7, fill=(255, 210, 110))
    sb.save(os.path.join(OUT, "07_combat_sbs.jpg"), quality=90)
    sbs_imgs.append((sb, "7. Combat wheel: current | A frame only | B full wheel (deco street backdrop)", lum_median(B)))
    print("07", "A %.3f B %.3f" % (lum_median(A), lum_median(B)))
    sheet = Image.new("RGB", (2560, 3 * ch + ch7 + 10), (14, 14, 16))
    f = ImageFont.truetype(FONT, 22)
    for i, (sb, cap, med) in enumerate(sbs_imgs):
        if i == 6:
            t = sb.resize((2560, int(2560 * 540 / sb.width)), Image.LANCZOS)
            x, y = 0, 3 * ch + 4
        else:
            t = sb.resize((cw, int(cw * 720 / 2568)), Image.LANCZOS)
            x, y = (i % 2) * 1290 + 0, (i // 2) * ch + 4
        sheet.paste(t, (x, y + 30))
        ImageDraw.Draw(sheet).text((x + 6, y + 2), cap + "   (deco median %.2f)" % med, font=f, fill=(235, 220, 190))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("contact_sheet", sheet.size)


if __name__ == "__main__":
    main()
