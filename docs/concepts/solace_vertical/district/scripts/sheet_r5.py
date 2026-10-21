"""Round-5 sheet, 2560 wide: the base close-up large, then the four views (2 x 2). python sheet_r5.py <dir> <out.jpg>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
W = 2560
BG, FG, LIME = (14, 12, 22), (232, 238, 228), (150, 255, 70)
def font(sz, bold=False):
    f = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
    return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()
def st(n):
    a = np.asarray(Image.open(os.path.join(D, n)).convert("RGB")).astype(np.float32) / 255.0
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    return "median %.2f, %.1f%% > 0.95" % (np.median(l), (l > 0.95).mean() * 100)
def put(s, d, n, cap, x, y, w, h, fs):
    d.text((x + 8, y + 2), cap + "  (" + st(n) + ")", font=font(fs), fill=LIME)
    s.paste(Image.open(os.path.join(D, n)).convert("RGB").resize((w, h), Image.LANCZOS), (x, y + fs + 12))
HW = W // 2
hh = int((HW - 6) * 9 / 16)
bw = 1700
bh = int(bw * 9 / 16)
H = 54 + 38 + bh + 14 + 2 * (hh + 34 + 8) + 4
s = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(s)
d.text((24, 8), "SOLACE DISTRICT round 5: raised circular plinth (3 tiers, lit edges) with stairs at N, E, S, W landing on park paths", font=font(32, True), fill=FG)
y = 54
put(s, d, "D_base_r5.png", "D_base_r5: AAA-2 night close-up, ~62 BU from the plinth centre, 35 deg down", 3, y, bw, bh, 24)
d.text((bw + 30, y + 80), "Plinth: r 35 / 29.5 / 24 BU, tiers 1.1 BU each.\nStairs: 16 steps, 10.4 BU wide, N/E/S/W,\nfoot on the old corridors at r 36 where the\nfootpaths start. Lit lime edge on each tier,\npink ring and lime base ring on top.\nRaid-day cel darkened to median 0.54.", font=font(26), fill=FG)
y += 38 + bh + 14
put(s, d, "D_raid_park_r5.png", "D_raid_park_r5 (cel + ink night)", 3, y, HW - 6, hh, 22)
put(s, d, "D_raid_day_park_r5.png", "D_raid_day_park_r5 (cel + ink day, darkened)", HW + 3, y, HW - 6, hh, 22)
y += hh + 34 + 8
put(s, d, "D_night_park_r5.png", "D_night_park_r5 (AAA-2 night)", 3, y, HW - 6, hh, 22)
put(s, d, "D_day_park_r5.png", "D_day_park_r5 (AAA-2 day)", HW + 3, y, HW - 6, hh, 22)
s.save(OUT, quality=88)
print(s.size)
