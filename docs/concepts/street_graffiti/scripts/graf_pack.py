"""Pack the deliverables: NN_<subject>_graffiti.png (1920x1080), NN_<subject>_sbs.jpg (current | graffiti), contact_sheet.jpg.
python graf_pack.py [tags json]   (reads the finals under D:/rc_scratch/graffiti, writes into docs/concepts/street_graffiti/)
tags json: {"city": "g1", "halcyon": "g1", ..., "street": "g1"}; the combat mockup is D:/rc_scratch/graffiti/combat.png.
Contact sheet (2560 wide): the street hero full width, then the combat mockup, then the city and the four HQs.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
CON = os.path.normpath(os.path.join(OUT, ".."))
GP = os.path.join(CON, "golden_plates")
SC = "D:/rc_scratch/graffiti"
FONT = "C:/Windows/Fonts/arialbd.ttf"
PINK = (255, 90, 190)


def panels(tags):
    t = lambda k: tags.get(k, "g1")  # noqa: E731
    return [
        ("01", "netrun_street", SC + "/street/%s/plate.png" % t("street"), GP + "/street_decision.png", "1. Netrun street, decision camera"),
        ("02", "combat_wheel", SC + "/combat.png", CON + "/round41_wheel_stack/combat_typical_v4.png", "2. Combat wheel frame mockup over the street"),
        ("03", "whole_city", SC + "/city/%s/plate.png" % t("city"), GP + "/city_a2_night.png", "3. Whole city, A2 hero camera"),
        ("04", "halcyon", SC + "/halcyon/%s/plate.png" % t("halcyon"), GP + "/hq_halcyon_overview.png", "4. Halcyon HQ"),
        ("05", "meridian", SC + "/meridian/%s/plate.png" % t("meridian"), GP + "/hq_meridian_overview.png", "5. Meridian HQ"),
        ("06", "orbital", SC + "/orbital/%s/plate.png" % t("orbital"), GP + "/hq_orbital_overview.png", "6. Orbital HQ"),
        ("07", "solace", SC + "/solace/%s/plate.png" % t("solace"), GP + "/hq_solace_overview.png", "7. Solace HQ"),
    ]


def med(im):
    return float(np.median(np.asarray(im.convert("L"), np.float32) / 255.0))


def sbs(cur, new):
    c = cur.resize((1280, 720), Image.LANCZOS)
    r = new.resize((1280, 720), Image.LANCZOS)
    sb = Image.new("RGB", (2568, 720), (12, 12, 12))
    sb.paste(c, (0, 0))
    sb.paste(r, (1288, 0))
    dr = ImageDraw.Draw(sb)
    f = ImageFont.truetype(FONT, 26)
    dr.rectangle([0, 0, 190, 40], fill=(0, 0, 0))
    dr.text((10, 6), "CURRENT", font=f, fill=(220, 220, 220))
    dr.rectangle([1288, 0, 1470, 40], fill=(0, 0, 0))
    dr.text((1298, 6), "GRAFFITI", font=f, fill=PINK)
    return sb


def main():
    tags = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    items = []
    for nn, name, new, cur, cap in panels(tags):
        if not os.path.exists(new):
            print("missing", new)
            continue
        d = Image.open(new).convert("RGB")
        if name == "whole_city":   # the CPU render's fog fireflies: a 3 x 3 median before upscaling
            d = d.filter(ImageFilter.MedianFilter(3))
        if d.size != (1920, 1080):
            d = d.resize((1920, 1080), Image.LANCZOS)
        d.save(os.path.join(OUT, "%s_%s_graffiti.png" % (nn, name)))
        sb = sbs(Image.open(cur).convert("RGB"), d)
        sb.save(os.path.join(OUT, "%s_%s_sbs.jpg" % (nn, name)), quality=90)
        items.append((nn, sb, cap, med(d)))
        print(nn, name, "median %.3f" % med(d))
    # sheet: rows 1 and 2 full width (street, combat), then the rest two per row
    f = ImageFont.truetype(FONT, 24)
    full_h = int(2560 * 720 / 2568) + 36
    half_w = 1270
    half_h = int(half_w * 720 / 2568) + 36
    rest = [it for it in items if it[0] not in ("01", "02")]
    tops = [it for it in items if it[0] in ("01", "02")]
    H = len(tops) * full_h + ((len(rest) + 1) // 2) * half_h + 12
    sheet = Image.new("RGB", (2560, H), (14, 12, 18))
    y = 4
    for nn, sb, cap, m in tops:
        ImageDraw.Draw(sheet).text((6, y + 2), "%s   (median %.2f)" % (cap, m), font=f, fill=(245, 225, 240))
        sheet.paste(sb.resize((2560, full_h - 36), Image.LANCZOS), (0, y + 34))
        y += full_h
    for i, (nn, sb, cap, m) in enumerate(rest):
        x, yy = (i % 2) * 1290, y + (i // 2) * half_h
        ImageDraw.Draw(sheet).text((x + 6, yy + 2), "%s   (median %.2f)" % (cap, m), font=f, fill=(245, 225, 240))
        sheet.paste(sb.resize((half_w, half_h - 36), Image.LANCZOS), (x, yy + 34))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("contact_sheet", sheet.size)


if __name__ == "__main__":
    main()
