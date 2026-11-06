"""F Rebel Tag: squint strips (320 px + 4 px blur at 1920), deutan/tritan sims, contact sheet."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from ft_lib import *

OUT = os.path.abspath(os.path.join(HERE, ".."))
NAMES = ["01_decay", "02_draw", "03_plan", "04_forecast", "05_response", "06_playout_impact", "07_playout_home", "08_aftermath",
         "09_hq_step", "10_city_lost", "11_panels_removed", "12_reveal_sealed_hunter"]
os.makedirs(os.path.join(OUT, "squint"), exist_ok=True)
os.makedirs(os.path.join(OUT, "colorblind"), exist_ok=True)


def strip(im):
    a = im.resize((320, 180), Image.LANCZOS)
    b = im.filter(ImageFilter.GaussianBlur(4)).resize((320, 180), Image.LANCZOS)
    s = Image.new("RGB", (644, 180), (0, 0, 0))
    s.paste(a, (0, 0))
    s.paste(b, (324, 0))
    return s


for n in NAMES:
    p = os.path.join(OUT, n + ".png")
    if os.path.exists(p):
        strip(Image.open(p).convert("RGB")).save(os.path.join(OUT, "squint", n + "_squint.png"))
for n in ("04_forecast", "06_playout_impact", "07_playout_home"):
    p = os.path.join(OUT, n + ".png")
    if os.path.exists(p):
        im = Image.open(p).convert("RGB")
        for k in ("deutan", "tritan"):
            cvd(im, k).save(os.path.join(OUT, "colorblind", f"{n}_{k}.png"))

CW, CH = 600, 338
cols, pad, lab = 3, 14, 22
rows = (len(NAMES) + cols - 1) // cols
cell_h = lab + CH + 4 + 94 + pad
sheet = Image.new("RGB", (cols * (CW + pad) + pad, rows * cell_h + pad + 46), (14, 12, 20))
d = ImageDraw.Draw(sheet)
d.text((pad, 8), "F  REBEL TAG / STREET HACK  -  the Infected Tide raid as the Cell defacing the corp's AR", font=F_ANTON(24), fill=(246, 240, 222))
for i, n in enumerate(NAMES):
    p = os.path.join(OUT, n + ".png")
    if not os.path.exists(p):
        continue
    r, c = divmod(i, cols)
    x = pad + c * (CW + pad)
    y = 46 + pad + r * cell_h
    d.text((x, y), n.replace("_", " "), font=F_MONO(15), fill=(180, 200, 210))
    sheet.paste(Image.open(p).convert("RGB").resize((CW, CH), Image.LANCZOS), (x, y + lab))
    sp = Image.open(os.path.join(OUT, "squint", n + "_squint.png")).resize((int(644 * 94 / 180), 94), Image.LANCZOS)
    sheet.paste(sp, (x, y + lab + CH + 4))
sheet.save(os.path.join(OUT, "sheet.jpg"), quality=88)
print("post done")
