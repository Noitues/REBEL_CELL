"""Round-3 sheet, 2560 wide: row 1 Godot raid now | D_raid | D_raid_day; row 2 D_night | D_day. python sheet_r3.py <district_dir> <out.jpg>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
GODOT = r"D:\rc_scratch\solace_v1\godot_now\00_solace_raid.png"
W = 2560
BG, FG, LIME, DIM = (14, 12, 22), (232, 238, 228), (150, 255, 70), (190, 190, 215)
def font(sz, bold=False):
    f = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
    return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()
def st(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    return "median %.2f, %.1f%% > 0.95" % (np.median(l), (l > 0.95).mean() * 100)
tw, th = W // 3, 480
CW, CH = W // 2, 720
H = 56 + 2 * 34 + th + 20 + CH + 10
s = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(s)
d.text((24, 8), "SOLACE DISTRICT round 3: direction D at the game's raid zoom (cel + ink), and in daylight", font=font(32, True), fill=FG)
row1 = [(GODOT, "Godot raid now (Solace, night): target", None), (os.path.join(D, "D_raid.png"), "D_raid: cel + ink, night, yaw 135 / pitch 40 / ortho 300", 1), (os.path.join(D, "D_raid_day.png"), "D_raid_day: cel + ink, daylight", 1)]
y = 56
for k, (p, cap, st_) in enumerate(row1):
    im = Image.open(p).convert("RGB").resize((tw - 6, th), Image.LANCZOS)
    d.text((k * tw + 10, y + 2), cap + ("  (" + st(p) + ")" if st_ else ""), font=font(20), fill=DIM if k == 0 else LIME)
    s.paste(im, (k * tw + 3, y + 34))
y += 34 + th + 14
for k, (nm, cap) in enumerate((("D_night.png", "D_night: Cycles AAA-2 night (unchanged)"), ("D_day.png", "D_day: Cycles AAA-2 daylight, warm sun, same camera"))):
    p = os.path.join(D, nm)
    d.text((k * CW + 12, y + 2), cap + "  (" + st(p) + ")", font=font(24), fill=LIME)
    s.paste(Image.open(p).convert("RGB").resize((CW - 6, CH - 34), Image.LANCZOS), (k * CW + 3, y + 34))
s = s.crop((0, 0, W, y + 34 + CH - 34 + 8))
s.save(OUT, quality=88)
print(s.size)
