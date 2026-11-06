"""Post: squint strips, deutan/tritan sims, contact sheet. Run after build.py (reads the frame PNGs)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from wt_lib import cvd

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NAMES = ["01_decay", "02_draw", "03_plan", "04_forecast", "05_response", "06_playout_impact", "07_playout_home", "08_aftermath",
         "09_hq_step", "10_city_lost", "11_panels_removed"]
os.makedirs(os.path.join(OUT, "squint"), exist_ok=True)
os.makedirs(os.path.join(OUT, "cvd"), exist_ok=True)


def strip(im):
    a = im.resize((320, 180), Image.LANCZOS)
    b = im.filter(ImageFilter.GaussianBlur(4)).resize((320, 180), Image.LANCZOS)
    s = Image.new("RGB", (644, 180), (0, 0, 0))
    s.paste(a, (0, 0))
    s.paste(b, (324, 0))
    return s


for n in NAMES:
    p = os.path.join(OUT, n + ".png")
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGB")
    strip(im).save(os.path.join(OUT, "squint", n + "_squint.png"))
for n in ("04_forecast", "06_playout_impact", "07_playout_home"):
    im = Image.open(os.path.join(OUT, n + ".png")).convert("RGB")
    for k in ("deutan", "tritan"):
        cvd(im, k).save(os.path.join(OUT, "cvd", f"{n}_{k}.png"))

# contact sheet: 3 columns x 4 rows; frame 600x338, strip below
CW, CH = 600, 338
cols = 3
pad = 14
lab = 22
rows = (len(NAMES) + cols - 1) // cols
cell_h = lab + CH + 4 + 94 + 4 + 94 + pad
sheet = Image.new("RGB", (cols * (CW + pad) + pad, rows * cell_h + pad + 40), (14, 18, 22))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "ShareTechMono-Regular.ttf"), 15)
    f2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), "Anton-Regular.ttf"), 22)
except Exception:
    f = f2 = None
d.text((pad, 8), 'C  WAR TABLE  -  the Infected Tide raid as a tabletop diorama', font=f2, fill=(240, 232, 214))
for i, n in enumerate(NAMES):
    p = os.path.join(OUT, n + ".png")
    if not os.path.exists(p):
        continue
    r, c = divmod(i, cols)
    x = pad + c * (CW + pad)
    y = 40 + pad + r * cell_h
    d.text((x, y), n.replace("_", " "), font=f, fill=(180, 200, 210))
    im = Image.open(p).convert("RGB").resize((CW, CH), Image.LANCZOS)
    sheet.paste(im, (x, y + lab))
    sp = Image.open(os.path.join(OUT, "squint", n + "_squint.png")).resize((int(644 * 94 / 180), 94), Image.LANCZOS)
    sheet.paste(sp, (x, y + lab + CH + 4))
    # deutan thumb for forecast/playout
    if n in ("04_forecast", "06_playout_impact", "07_playout_home"):
        dp = Image.open(os.path.join(OUT, "cvd", n + "_deutan.png")).resize((167, 94), Image.LANCZOS)
        tp = Image.open(os.path.join(OUT, "cvd", n + "_tritan.png")).resize((167, 94), Image.LANCZOS)
        sheet.paste(dp, (x, y + lab + CH + 4 + 98))
        sheet.paste(tp, (x + 171, y + lab + CH + 4 + 98))
sheet.save(os.path.join(OUT, "sheet.jpg"), quality=90)
print("sheet", sheet.size)
