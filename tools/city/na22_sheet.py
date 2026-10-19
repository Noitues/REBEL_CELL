"""NA-22 capture sheet (1920x1080): the street canyon at look_blend 0 / 0.5 / 1, the same lb 1 frame large beside the golden
street_overview plate, the calibration line (median, under 0.10, over 0.85, luma p99 against the plate and the 12.8 tolerances)
and the HQ page (mainline look by spec 4.2; no look_blend row).
Usage: python tools/city/na22_sheet.py --canyon <dir with street_lb*/beauty.png> --hq <hq beauty.png> --golden <plate.png> --out <jpg>"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

import na22_stats

TOL = {"median": 0.02, "under_010": 0.05, "over_085": 0.01}
P99_MIN = 0.70


def font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canyon", required=True)
    ap.add_argument("--hq", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f, fs = font(15), font(13)
    sheet = Image.new("RGB", (1920, 1080), (16, 16, 22))
    d = ImageDraw.Draw(sheet)
    lbs = [("0p0", "look_blend 0"), ("0p5", "look_blend 0.5"), ("1p0", "look_blend 1")]
    for i, (tag, label) in enumerate(lbs):
        p = os.path.join(a.canyon, "street_lb%s" % tag, "beauty.png")
        sheet.paste(Image.open(p).convert("RGB").resize((640, 360), Image.LANCZOS), (i * 640, 20))
        d.text((i * 640 + 6, 3), "Street canyon, Godot, %s" % label, font=f, fill=(235, 235, 235))
    y0 = 380
    big = Image.open(os.path.join(a.canyon, "street_lb1p0", "beauty.png")).convert("RGB").resize((960, 540), Image.LANCZOS)
    gold = Image.open(a.golden).convert("RGB").resize((960, 540), Image.LANCZOS)
    sheet.paste(big, (0, y0 + 20))
    sheet.paste(gold, (960, y0 + 20))
    d.text((6, y0 + 3), "Street canyon, Godot, look_blend 1 (street wash, edge trims, lights-out facades, carpet, sky glow, haze; tan cone gone)", font=f, fill=(235, 235, 235))
    d.text((966, y0 + 3), "GOLDEN street_overview (Blender)", font=f, fill=(235, 235, 235))
    ys = y0 + 20 + 540
    s_g = na22_stats.stats(a.golden)
    s_c = na22_stats.stats(os.path.join(a.canyon, "street_lb1p0", "beauty.png"))
    rows = [("median luma", "median", "%.3f", 1.0, "tol %.2f" % TOL["median"]),
            ("under 0.10", "under_010", "%.1f %%", 100.0, "tol %d pp" % round(TOL["under_010"] * 100)),
            ("over 0.85", "over_085", "%.2f %%", 100.0, "tol %d pp" % round(TOL["over_085"] * 100))]
    x = 8
    d.text((x, ys + 4), "Calibration (street canyon, lb 1) vs golden street_overview:", font=f, fill=(235, 235, 235))
    for i, (name, key, fmt, k, tol) in enumerate(rows):
        diff = abs(s_c[key] - s_g[key])
        ok = diff <= TOL[key]
        txt = "  %-12s %s vs %s   %s   %s" % (name, fmt % (s_c[key] * k), fmt % (s_g[key] * k), tol, "PASS" if ok else "FAIL")
        d.text((x, ys + 24 + i * 18), txt, font=fs, fill=(150, 230, 150) if ok else (240, 150, 120))
    ok99 = s_c["p99"] >= P99_MIN
    d.text((x, ys + 24 + 3 * 18), "  %-12s %.3f vs %.3f   min %.2f   %s" % ("luma p99", s_c["p99"], s_g["p99"], P99_MIN, "PASS" if ok99 else "FAIL"), font=fs,
           fill=(150, 230, 150) if ok99 else (240, 150, 120))
    d.text((x, ys + 24 + 4 * 18), "Plates read-only (art-pass 63be54f6). Text 1.0, 1920x1080 frames downscaled.", font=fs, fill=(170, 170, 180))
    hq = Image.open(a.hq).convert("RGB").resize((240, 135), Image.LANCZOS)
    sheet.paste(hq, (1920 - 240 - 8, ys + 8))
    d.text((1920 - 240 - 8 - 330, ys + 8), "HQ page: mainline look (spec 4.2),", font=fs, fill=(235, 235, 235))
    d.text((1920 - 240 - 8 - 330, ys + 26), "no look_blend row (HQ stays mainline).", font=fs, fill=(235, 235, 235))
    sheet.save(a.out, quality=88)
    print("sheet", a.out)


if __name__ == "__main__":
    main()
