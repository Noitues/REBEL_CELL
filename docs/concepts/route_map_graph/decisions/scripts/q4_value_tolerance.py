"""Q4 decision sheet: three approved frames re-exposed to medians 0.10 .. 0.18 (CPU, linear-light exposure on the PNG).

python q4_value_tolerance.py  -> ../Q4_value_tolerance.png (+ ../Q4_value_tolerance.json with every number)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import sheetlib as L  # noqa: E402

RMG = os.path.dirname(os.path.dirname(HERE))
CON = os.path.dirname(RMG)
OUT = os.path.dirname(HERE)
FRAMES = [
    ("STREET OVERVIEW", "storyboard f_0400 (REVEAL, one city)", "D:/rc_scratch/storyboard/full_frames/f_0400.png"),
    ("HQ OVERVIEW", "Halcyon H_overview_v2 (plate, no UI)", os.path.join(RMG, "hq_halcyon/plates/H_overview_v2_plate.png")),
    ("THE CITY", "city_all_corps_night", os.path.join(CON, "city_all_corps/city_all_corps_night.png")),
]
TARGETS = [0.10, 0.12, 0.14, 0.16, 0.18]
W = 2400
LW = 250                       # label column
CW = (W - LW - 20) // 5        # cell width (426)
CH = round(CW * 9 / 16)
PAD = 10


def main():
    rows = []
    for name, sub, p in FRAMES:
        a = np.asarray(Image.open(p).convert("RGB"))
        if a.shape[1] > 1920:                       # measure and show at 1920 (the check's scale is the plate's;
            im = Image.fromarray(a)                 # a resample barely moves the median)
            a = np.asarray(im.resize((1920, round(1920 * im.height / im.width)), Image.LANCZOS))
        base = L.stats(a)
        cells = []
        for t in TARGETS:
            k = L.solve_median(a, t)
            b = L.expose(a, k)
            s = L.stats(b)
            s.update(target=t, stops=math.log2(k))
            cells.append((b, s))
        rows.append((name, sub, a, base, cells))

    head = 330
    rowh = CH + 70
    foot = 370
    H = head + rowh * len(rows) + foot
    sheet = Image.new("RGB", (W, H), L.BG)
    d = ImageDraw.Draw(sheet)
    f_t, f_h, f_b, f_s, f_m = L.font(44, True), L.font(26, True), L.font(22), L.font(19), L.font(20, mono=True)
    d.text((PAD + 10, 18), "Q4  VALUE TOLERANCE  -  how far may a frame's median luma drift from 0.14?", font=f_t, fill=L.INK)
    L.para(d, (PAD + 10, 80),
           "Each row is an approved frame; each column re-exposes it (linear-light exposure on the PNG, no re-render) so its "
           "median Rec.709 luma lands on the column value. Under each cell: the median, the share of pixels under 0.10 "
           "(target 25-40 %, R-VAL-2) and over 0.85 (cap 2.5 %, R-VAL-3), and the exposure change in stops. The bars "
           "above the columns show the candidate pass bands around 0.14.", f_b, W - 40, fill=L.DIM)
    # column headers and the candidate bands
    x0 = LW
    for c, t in enumerate(TARGETS):
        cx = x0 + c * (CW + 5)
        d.text((cx + CW / 2, 196), "median %.2f" % t, font=f_h, fill=L.LIME if t == 0.14 else L.INK, anchor="mt")
    def tx(v):                                       # median value -> x on the header (column centres)
        u = (v - 0.10) / 0.02
        return x0 + CW / 2 + u * (CW + 5)
    for i, (lab, lo, hi, col) in enumerate([("+-0.02  (0.12-0.16)", 0.12, 0.16, L.ORANGE),
                                            ("+-0.03 (0.11-0.17) RECOMMENDED", 0.11, 0.17, L.LIME)]):
        y = 240 + i * 38
        d.rounded_rectangle((tx(lo), y, tx(hi), y + 22), 6, fill=tuple(int(v * 0.35) for v in col), outline=col, width=2)
        d.text((PAD + 10, y - 3), lab, font=f_s, fill=col)
    y = head
    for name, sub, a, base, cells in rows:
        d.text((PAD + 10, y + 6), name, font=f_h, fill=L.INK)
        L.para(d, (PAD + 10, y + 42), sub, f_s, LW - 30, fill=L.DIM)
        th = Image.fromarray(a)
        th = L.fit(th, LW - 30, round((LW - 30) * 9 / 16))
        sheet.paste(th, (PAD + 10, y + 108))
        d.text((PAD + 10, y + 108 + th.height + 6), "as approved", font=f_s, fill=L.DIM)
        d.text((PAD + 10, y + 108 + th.height + 30), "median %.3f" % base["median"], font=f_m, fill=L.INK)
        d.text((PAD + 10, y + 108 + th.height + 54), "<0.10  %4.1f %%" % (base["under"] * 100), font=f_m, fill=L.INK)
        for c, (b, s) in enumerate(cells):
            cx = x0 + c * (CW + 5)
            sheet.paste(L.fit(Image.fromarray(b), CW, CH), (cx, y))
            ok_u = 0.25 <= s["under"] <= 0.40
            ok_o = s["over"] <= 0.025
            d.text((cx + 4, y + CH + 6), "med %.3f" % s["median"], font=f_m, fill=L.INK)
            d.text((cx + 150, y + CH + 6), "<0.10 %4.1f%%" % (s["under"] * 100), font=f_m, fill=L.LIME if ok_u else L.RED)
            d.text((cx + 4, y + CH + 32), "%+.2f stops" % s["stops"], font=f_m, fill=L.DIM)
            d.text((cx + 150, y + CH + 32), ">0.85 %4.1f%%" % (s["over"] * 100), font=f_m, fill=L.LIME if ok_o else L.RED)
        y += rowh
    # footer: reading + recommendation
    y += 10
    d.line((PAD, y, W - PAD, y), fill=(60, 60, 75), width=2)
    y += 18
    d.text((PAD + 10, y), "WHAT THE GRID SHOWS", font=f_h, fill=L.INK)
    obs = []
    for name, sub, a, base, cells in rows:
        u = ", ".join("%.2f: %d %%" % (s["target"], round(s["under"] * 100)) for _, s in cells)
        obs.append("%s - pixels under 0.10 by median: %s." % (name.title(), u))
    yy = y + 40
    for o in obs:
        yy = L.para(d, (PAD + 10, yy), o, f_b, W / 2 - 60, fill=L.DIM)
        yy += 4
    yy = L.para(d, (PAD + 10, yy + 6),
                "The approved work already spreads: these overviews sit at 0.109 (HQ), 0.120 (street) and 0.140 (city); "
                "the approved storyboard holds measure 0.125-0.129 (hovers) up to 0.182 (DECISION, lit frontage + UI). "
                "0.10 reads as black with lights; 0.18 greys the fog and the neon stops popping; 0.12-0.16 is the same "
                "night. The share under 0.10 moves fastest, so it stays its own check. The over-0.85 reds at high "
                "medians come from a plain exposure lift with no display knee; the real grade's knee holds them down.",
                f_b, W / 2 - 60, fill=L.INK)
    rx = W / 2 + 20
    d.text((rx, y), "RECOMMENDATION:  0.14 +-0.03, with a warn margin", font=f_h, fill=L.LIME)
    L.para(d, (rx, y + 40),
           "PASS 0.11-0.17 (+-0.03, about +-0.5 stop). WARN 0.09-0.11 and 0.17-0.19 (reported, never blocks). "
           "FAIL below 0.09 or above 0.19. Keep R-VAL-2 (25-40 % under 0.10) and R-VAL-3 (<= 2.5 % over 0.85) as "
           "separate checks; they catch crushed or washed frames that a median alone misses. Why not +-0.02: it "
           "would fail approved work (the HQ overview at 0.109 and the street at 0.120 sit on or under its edge), "
           "and the eye barely separates 0.12 from 0.14 here. Why not wider: at 0.18 every frame loses its black. "
           "The designer's 'the night city is too dark' is answered by the daytime version and the city grade, "
           "not by widening this band. Exempt frames stay as in 12.1.",
           f_b, W / 2 - 50, fill=L.INK)
    sheet.save(os.path.join(OUT, "Q4_value_tolerance.png"), optimize=True)
    js = [dict(frame=n, source=FRAMES[i][2].replace("\\", "/"), as_approved=base,
               cells=[s for _, s in cells]) for i, (n, sub, a, base, cells) in enumerate(rows)]
    json.dump(js, open(os.path.join(OUT, "Q4_value_tolerance.json"), "w"), indent=1)
    for r in js:
        print(r["frame"], "approved", {k: round(v, 3) for k, v in r["as_approved"].items()})
        for s in r["cells"]:
            print("   ", {k: round(v, 3) for k, v in s.items()})


if __name__ == "__main__":
    main()
