"""Self-check sheets: each frame beside its lab capture, and a grayscale thumbnail strip.

    python make_sheet.py --dir D:/rc_tmp/raid_design_lab/target/final
Writes <dir>/sheet_compare.png and <dir>/strip_gray.png.
"""
import argparse
import os

from PIL import Image, ImageDraw

LAB = "D:/rc_tmp/raid_design_lab/lab_l5/shots"
PAIRS = [("plan", "02_r1_plan_levers.png"), ("reveal", "06_r1_decision.png"), ("impact", "10_r1_beam_hunter.png")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    cw, ch = 960, 540
    sheet = Image.new("RGB", (cw * 2 + 30, (ch + 10) * len(PAIRS) + 10), (30, 30, 34))
    for i, (nm, lab) in enumerate(PAIRS):
        L = Image.open(os.path.join(LAB, lab)).convert("RGB").resize((cw, ch), Image.LANCZOS)
        M = Image.open(os.path.join(a.dir, nm + ".png")).convert("RGB").resize((cw, ch), Image.LANCZOS)
        y = 10 + i * (ch + 10)
        sheet.paste(L, (10, y))
        sheet.paste(M, (cw + 20, y))
    sheet.save(os.path.join(a.dir, "sheet_compare.png"))
    tw, th = 480, 270
    strip = Image.new("L", (tw * 3 + 40, th + 20), 20)
    for i, (nm, _) in enumerate(PAIRS):
        g = Image.open(os.path.join(a.dir, nm + ".png")).convert("L").resize((tw, th), Image.LANCZOS)
        strip.paste(g, (10 + i * (tw + 10), 10))
    strip.save(os.path.join(a.dir, "strip_gray.png"))
    print("sheets written")


if __name__ == "__main__":
    main()
