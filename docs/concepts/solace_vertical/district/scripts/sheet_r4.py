"""Round-4 sheet, 2560 wide: row 1 D_raid (r3) | D_raid_park; row 2 D_night_park | D_day_park; D_raid_day_park small tile. python sheet_r4.py <dir> <out.jpg>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
W = 2560
BG, FG, LIME, DIM = (14, 12, 22), (232, 238, 228), (150, 255, 70), (190, 190, 215)
def font(sz, bold=False):
    f = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
    return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()
def st(n):
    a = np.asarray(Image.open(os.path.join(D, n)).convert("RGB")).astype(np.float32) / 255.0
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    return "median %.2f, %.1f%% > 0.95" % (np.median(l), (l > 0.95).mean() * 100)
def put(s, d, n, cap, x, y, w, h, fs, col):
    d.text((x + 8, y + 2), cap + "  (" + st(n) + ")", font=font(fs), fill=col)
    s.paste(Image.open(os.path.join(D, n)).convert("RGB").resize((w, h), Image.LANCZOS), (x, y + fs + 12))
HW = W // 2
h1 = int((HW - 6) * 9 / 16)
tiny_w = 640
tiny_h = 360
H = 54 + (h1 + 34) + 14 + (h1 + 34) + 14 + (tiny_h + 34) + 8
s = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(s)
d.text((24, 8), "SOLACE DISTRICT round 4: direction D as one continuous park (no street grid, no lot pads)", font=font(32, True), fill=FG)
y = 54
put(s, d, "D_raid.png", "D_raid (round 3): gridded streets and pads, cel + ink night", 3, y, HW - 6, h1, 22, DIM)
put(s, d, "D_raid_park.png", "D_raid_park: one park, curving paths and lanes, ponds, tree clumps; same raid camera", HW + 3, y, HW - 6, h1, 22, LIME)
y += h1 + 34 + 14
put(s, d, "D_night_park.png", "D_night_park: Cycles AAA-2 night", 3, y, HW - 6, h1, 22, LIME)
put(s, d, "D_day_park.png", "D_day_park: Cycles AAA-2 daylight", HW + 3, y, HW - 6, h1, 22, LIME)
y += h1 + 34 + 14
put(s, d, "D_raid_day_park.png", "D_raid_day_park: cel + ink daylight", 3, y, tiny_w, tiny_h, 20, LIME)
d.text((tiny_w + 40, y + 60), "Park rules: rolling lawn flat under buildings and clearings, organic clearings round the helix and the hospital,\nlit footpaths (lime) and three service lanes (dark, edge-lit) winding along the old corridors and out into the city streets,\nponds, tree clumps, a double tree line at the soft boundary; bundles, kits and lighting as round 3.", font=font(24), fill=FG)
s.save(OUT, quality=88)
print(s.size)
