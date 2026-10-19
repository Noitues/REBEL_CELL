"""NA-25 capture sheet (1920x1080): the street entry's key frames from tools/city/na25_lab.gd.
Row 1-2: the jack-in (dive, REVEAL, MARK, ZOOM, CHOOSE); row 3: the jack-out (reverse) and the skip (before / after).
Usage: python tools/city/na25_sheet.py --shots <dir with fwd_*.png rev_*.png skip_*.png> --out <jpg> [--beats "<text>"]"""
import argparse
import glob
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
COLS = 4
TW, TH = W // COLS, 270

LABELS = {
    "00.00": "dive 0.0 s  (HQ page pose)",
    "01.50": "dive 1.5 s",
    "03.00": "dive end / REVEAL 0 s",
    "04.50": "REVEAL 1.5 s",
    "06.00": "REVEAL 3.0 s",
    "07.00": "MARK 0.4 s (hold from 7.64 s)",
    "07.80": "MARK hold",
    "09.00": "ZOOM 0.6 s",
    "end": "CHOOSE (end state)",
}


def font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def tile(sheet: Image.Image, path: str, col: int, row: int, label: str, f: ImageFont.ImageFont) -> None:
    if not os.path.exists(path):
        return
    im = Image.open(path).convert("RGB").resize((TW, TH - 18), Image.LANCZOS)
    x, y = col * TW, row * TH
    sheet.paste(im, (x, y + 18))
    ImageDraw.Draw(sheet).text((x + 4, y + 2), label, font=f, fill=(235, 235, 235))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = font(13)
    sheet = Image.new("RGB", (W, H), (16, 16, 22))
    plan = [
        ("hq_0.png", "HQ side  3a terminal types (0.7 s)"), ("hq_1.png", "HQ side  3b binary rain (2.0 s)"),
        ("hq_2.png", "HQ side  3c CRT collapse (2.8 s)"), ("hq_4.png", "switch under NIGHT_SKY, then the dive"),
        ("fwd_00.00.png", "3d dive 0.0 s (HQ page pose)"), ("fwd_01.50.png", "3d dive 1.5 s"),
        ("fwd_03.00.png", "dive end = street OVERVIEW"), ("fwd_04.50.png", "4 REVEAL 1.5 s"),
        ("fwd_06.00.png", "4 REVEAL 3.0 s"), ("fwd_07.00.png", "5 MARK 0.4 s"),
        ("fwd_07.80.png", "5 MARK hold"), ("fwd_09.00.png", "6 ZOOM 0.6 s"),
        ("fwd_end.png", "7 CHOOSE (end state)"), ("rev_06.00.png", "JACK OUT reverse, REVEAL part"),
        ("rev_end.png", "JACK OUT end: HQ page pose"), ("skip_after.png", "SKIP at 4.0 s: the CHOOSE state, same frame"),
    ]
    for i, (name, label) in enumerate(plan):
        tile(sheet, os.path.join(a.shots, name), i % COLS, i // COLS, label, f)
    sheet.save(a.out, quality=88)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
