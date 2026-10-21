"""Round-2 sheet, 2560 wide: A/B/C night thumbnails on top, D map and D night below. python sheet_r2.py <district_dir> <out.jpg>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
W = 2560
BG, FG, LIME = (14, 12, 22), (232, 238, 228), (150, 255, 70)
def font(sz, bold=False):
    f = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
    return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()
tw, th = W // 3, 480
CW, CH = W // 2, 720
H = 60 + 36 + th + 20 + 84 + CH + 10
s = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(s)
d.text((24, 10), "SOLACE DISTRICT round 2: direction D, mixed bundles (A capsules + B cells + C clinic towers), C hospital", font=font(34, True), fill=FG)
y0 = 60
for k, (key, cap) in enumerate((("A", "A capsule grove (night, round 1)"), ("B", "B culture cells (night, round 1)"), ("C", "C clean ward (night, round 1)"))):
    im = Image.open(os.path.join(D, key + "_night.png")).convert("RGB").resize((tw - 6, th - 0), Image.LANCZOS)
    d.text((k * tw + 10, y0 + 2), cap, font=font(22), fill=(190, 190, 215))
    s.paste(im, (k * tw + 3, y0 + 36))
y = y0 + 36 + th + 20
d.rectangle((0, y, W, y + 84), fill=(24, 20, 36))
d.text((18, y + 4), "D  MIXED BUNDLES", font=font(32, True), fill=LIME)
d.text((18 + 380, y + 12), "cel map view: Eevee ortho, raid zoom, 3 toon bands + ink", font=font(22), fill=(190, 190, 215))
d.text((CW + 18, y + 12), "AAA-2 night hero (v2: emission x0.35, moon key, lighter fog): Cycles, 1920x1080", font=font(22), fill=(190, 190, 215))
d.text((18, y + 46), "seeded Voronoi bundles of ~3-8 lots, one kit each, neighbours differ; lime-leaning B cells with bright pink nuclei; C porcelain hospital; no beam / centre column over the helix", font=font(22), fill=FG)
for c, nm in enumerate(("map", "night")):
    im = Image.open(os.path.join(D, "D_%s.png" % nm)).convert("RGB").resize((CW, CH), Image.LANCZOS)
    s.paste(im, (c * CW, y + 84))
s.save(OUT, quality=88)
print(s.size)
