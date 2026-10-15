"""Side-by-side: our render crops vs. matching crops of the designer's 2077 screencaps (reference only; this sheet
is a critique aid and nothing here may be copied into renders or assets).
usage: python crit_side_by_side.py <render.png> <screencap_dir> <out.jpg>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R, CAPS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
R1 = os.path.join(CAPS, "EbXy1G7WAAE6iep.jpg")
R2 = os.path.join(CAPS, "all-cyberpunk-2077-ncw3-4k-screenshots-and-gange-renders-v0-p02h2jzr2yn51.webp")
R3 = os.path.join(CAPS, "xkjuWSYJPxdEwzSFbPJ72A.jpg")
ROWS = [
    ("A  STREET LEVEL: wet asphalt", (0, 560, 1280, 690), R1, (0, 640, 2048, 1152),
     "R1 EbXy1G7WAAE6iep.jpg (Japantown, rain)"),
    ("B  SKYLINE: windows, signage, practicals", (180, 88, 1130, 330), R2, (900, 0, 2900, 820),
     "R2 ...p02h2jzr2yn51.webp (Japantown gate, night)"),
    ("C  FOG / STEAM above the street", (200, 84, 1280, 210), R1, (700, 0, 1400, 560),
     "R1 EbXy1G7WAAE6iep.jpg (steam column)"),
    ("D  SCALE + GREEBLE DENSITY (R3 is a day shot: use for density only)", (300, 110, 700, 420), R3, (250, 0, 1450, 700),
     "R3 xkjuWSYJ...jpg (day)"),
]
RH = 300            # row image height
GAP, HEAD = 16, 34
COLW = 820          # each column width


def font(sz):
    for f in ("C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


FH, FS = font(18), font(14)


def stats(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    s = np.asarray(im.convert("HSV"))[..., 1].astype(np.float32) / 255.0
    return "median L %.2f  p95 %.2f  black(<0.1) %2d%%  sat %.2f" % (np.median(L), np.percentile(L, 95),
                                                                     100 * (L < 0.1).mean(), s.mean())


def fit(im):
    """Fit inside COLW x RH, keep aspect, centre on black."""
    k = min(COLW / im.width, RH / im.height)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    c = Image.new("RGB", (COLW, RH), (6, 4, 10))
    c.paste(im, ((COLW - im.width) // 2, (RH - im.height) // 2))
    return c


W = COLW * 2 + GAP * 3
H = len(ROWS) * (RH + HEAD + 26 + GAP) + 50
sheet = Image.new("RGB", (W, H), (14, 10, 22))
d = ImageDraw.Draw(sheet)
d.text((GAP, 12), "REBEL_CELL c_real_test (left)  vs  designer's Cyberpunk 2077 screencaps (right) - REFERENCE ONLY",
       font=FH, fill=(255, 230, 0))
render = Image.open(R).convert("RGB")
y = 50
for title, rbox, ref, fbox, flabel in ROWS:
    d.text((GAP, y), title, font=FH, fill=(255, 255, 255))
    y += HEAD
    a = render.crop(rbox)
    b = Image.open(ref).convert("RGB").crop(fbox)
    sheet.paste(fit(a), (GAP, y))
    sheet.paste(fit(b), (GAP * 2 + COLW, y))
    d.text((GAP, y + RH + 4), "OURS  " + stats(a), font=FS, fill=(255, 120, 140))
    d.text((GAP * 2 + COLW, y + RH + 4), flabel + "  " + stats(b), font=FS, fill=(120, 230, 255))
    y += RH + 26 + GAP
sheet.save(OUT, quality=88)
print("wrote", OUT, sheet.size)
