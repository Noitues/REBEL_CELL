"""Draw the numbered top-10 gap callouts of CRITIQUE.md onto the render, with a key panel on the right
(labels never cover the route). usage: python crit_markup.py <render.png> <out.jpg>"""
import sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
S = 2            # supersample
PANEL = 470      # key panel width (1x px)
src = Image.open(SRC).convert("RGB")
W, H = src.size
src = src.resize((W * S, H * S), Image.LANCZOS)
src = Image.blend(src, Image.new("RGB", src.size, (0, 0, 0)), 0.15)
im = Image.new("RGB", ((W + PANEL) * S, H * S), (12, 8, 20))
im.paste(src, (0, 0))
d = ImageDraw.Draw(im)


def font(sz):
    for f in ("C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(f, sz * S)
        except OSError:
            pass
    return ImageFont.load_default()


FB, FS, FT = font(14), font(12), font(17)
RED, YEL, WHITE = (255, 40, 60), (255, 230, 0), (240, 240, 250)

# (n, key text lines, boxes (1x px of the 1280x720 render), badge position)
CALL = [
    (1, ["EXPOSURE + VEIL", "median L 0.43 vs 2077 refs 0.13-0.16;", "11 % of frame > 0.85 (refs 1-3 %)"],
     [(470, 140, 820, 320)], (470, 140)),
    (2, ["EMISSIVE HIERARCHY INVERTED", "white 'ahead' rooms + street signs", "outshine the orange options"],
     [(878, 420, 960, 470), (998, 460, 1072, 502), (390, 630, 470, 672), (190, 560, 300, 590)], (960, 420)),
    (3, ["NEON CLIPS TO WHITE, PASTEL GRADE", "cores have no hue; bright-pixel sat", "0.17 vs refs 0.19-0.35"],
     [(690, 112, 830, 138), (335, 276, 430, 292), (750, 330, 825, 345)], (830, 112)),
    (4, ["FOG = COTTON BLOBS, NOT STRATA", "no wind shear, no underlight,", "same veil in front of everything"],
     [(200, 84, 465, 135), (840, 84, 1275, 118)], (200, 100)),
    (5, ["NO MEGA-SCALE / ONE DEPTH PLANE", "crowns all end inside frame at", "similar height; no near silhouettes"],
     [(970, 210, 1130, 300), (330, 118, 425, 150)], (1130, 210)),
    (6, ["BARE FACADES", "no AC units, pipes, cables, balconies,", "brackets, wires between towers"],
     [(336, 150, 425, 330)], (336, 330)),
    (7, ["BLANK SIGNS / HOLO", "glowing rectangles, no ad art,", "only one legible sign (HALCYON)"],
     [(880, 200, 940, 268), (885, 112, 960, 175), (330, 300, 360, 380)], (940, 268)),
    (8, ["WINDOW CONFETTI", "same-size pastel dots, random hue,", "no floors, blinds or interiors"],
     [(192, 140, 330, 300), (1140, 400, 1270, 590)], (192, 300)),
    (9, ["DEAD GREY PLAQUES", "unlit/past rooms are flat grey", "boxes, read as UI holes"],
     [(488, 375, 556, 460), (346, 420, 428, 505)], (556, 375)),
    (10, ["STREET + RAIN", "laser line across frame, no vertical", "spec streaks, rain one layer"],
     [(0, 592, 1280, 610), (500, 612, 860, 688)], (860, 612)),
]


def badge(x, y, n):
    r = 12 * S
    d.ellipse((x - r, y - r, x + r, y + r), fill=RED, outline=WHITE, width=2 * S)
    t = str(n)
    bb = d.textbbox((0, 0), t, font=FB)
    d.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=FB, fill=WHITE)


for n, lines, boxes, bp in CALL:
    for (x0, y0, x1, y1) in boxes:
        d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), outline=RED, width=2 * S)
for n, lines, boxes, bp in CALL:
    badge(bp[0] * S, bp[1] * S, n)

# key panel
px = (W + 18) * S
d.text((px, 14 * S), "TOP-10 GAPS vs 2077 (CRITIQUE.md)", font=FT, fill=YEL)
y = 46 * S
for n, lines, boxes, bp in CALL:
    badge(px + 12 * S, y + 9 * S, n)
    d.text((px + 32 * S, y), lines[0], font=FB, fill=YEL)
    yy = y + 19 * S
    for ln in lines[1:]:
        d.text((px + 32 * S, yy), ln, font=FS, fill=WHITE)
        yy += 16 * S
    y = yy + 12 * S

im = im.resize(((W + PANEL) * 3 // 2, H * 3 // 2), Image.LANCZOS)
im.save(OUT, quality=90)
print("wrote", OUT, im.size)
