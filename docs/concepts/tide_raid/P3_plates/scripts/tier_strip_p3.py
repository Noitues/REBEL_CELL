"""P3 tier strip: greyscale 320 px. Row 1: the five RINGS (crop around each Site, 320 px greyscale x8 nearest). Row 2: the five TILES. Row 3: ring + tile together at the true 320 px size (x1) so the
squint size is visible. Plus a numeric ladder: mean luma inside the ring ellipse minus the ring's surrounding annulus, fill fraction (share of the inner disc darker than the annulus / lighter), at 320 px.
python tier_strip_p3.py -> tier_strip_gray_320.png, tier_ladder.json"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import p1lib as L

O = L.OUT
w = L.load_world()
im = Image.open(O + 'plates/T0_tiers.png').convert('RGB')
g = im.resize((320, 180), Image.LANCZOS).convert('L')
ga = np.asarray(g, np.float32) / 255
tl = {e['site']: e for e in json.load(open(O + 'tile_distances_tiers.json'))}
TIERS = [('t1_a', 'UNTOUCHED'), ('t1_d', 'HOLDS'), ('t2_virus', 'SITES LOST'), ('t3_c', 'DAMAGED'), ('t3_core', 'BREACHED')]
R_BU = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}
try:
    F = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 15)
except Exception:
    F = None
SC = 8
out = Image.new('RGB', (5 * 240 + 12, 640), (8, 6, 20))
d = ImageDraw.Draw(out)
ladder = {}
yy, xx = np.mgrid[0:180, 0:320].astype(np.float32)
for i, (sid, name) in enumerate(TIERS):
    b = np.asarray(w.sites[sid]['B'], float) / 6.0
    c = np.asarray(tl[sid]['centre'], float) / 6.0
    rx = R_BU[name] / 0.2055 / 6.0
    ry = rx * 0.64
    # numeric ladder: inner disc vs annulus (rho 1.35..1.9 x ring radius)
    rho = np.hypot((xx - b[0]) / rx, (yy - b[1]) / ry)
    inner = rho < 0.80
    band = (rho >= 0.80) & (rho < 1.12)
    ann = (rho >= 1.35) & (rho < 1.9)
    bg = float(np.median(ga[ann]))
    ladder[name] = dict(inner_luma=round(float(ga[inner].mean()), 3), band_luma=round(float(ga[band].mean()), 3), surround_luma=round(bg, 3),
                        inner_minus_surround=round(float(ga[inner].mean()) - bg, 3), band_minus_surround=round(float(ga[band].mean()) - bg, 3),
                        inner_std=round(float(ga[inner].std()), 3))
    x0 = 6 + i * 240
    rb = (int(b[0] - 15), int(b[1] - 11), int(b[0] + 15), int(b[1] + 11))
    rc = g.crop(rb).resize((30 * SC, 22 * SC), Image.NEAREST).convert('RGB')
    out.paste(rc, (x0, 8))
    tb = (int(c[0] - 10), int(c[1] - 10), int(c[0] + 10), int(c[1] + 10))
    tc = g.crop(tb).resize((20 * SC, 20 * SC), Image.NEAREST).convert('RGB')
    out.paste(tc, (x0 + 40, 8 + 22 * SC + 8))
    # true size ring + tile (x1 on a dark pad): the squint size
    d.text((x0, 8 + 22 * SC + 8 + 20 * SC + 8), name, fill=(127, 239, 255), font=F)
    d.text((x0, 8 + 22 * SC + 8 + 20 * SC + 28), 'ring in-sur %+.2f band %+.2f' % (ladder[name]['inner_minus_surround'], ladder[name]['band_minus_surround']), fill=(190, 200, 225), font=F)
# true-size strip (x1) at the bottom: whole 320 px tiers plate + the five tile+ring clusters ringed
out2 = Image.new('RGB', (out.width, out.height + 190), (8, 6, 20))
out2.paste(out, (0, 0))
out2.paste(g.convert('RGB'), (6, out.height + 4))
d2 = ImageDraw.Draw(out2)
d2.text((340, out.height + 10), 'the tiers plate at its true 320 px size (greyscale), tile + ring per Site', fill=(160, 170, 200), font=F)
d2.text((340, out.height + 34), 'rows above: ring crops x8, tile crops x8 (nearest). Numbers: luma (0..1) of ring/inner disc minus its surround at 320 px.', fill=(160, 170, 200), font=F)
out2.save(O + 'tier_strip_gray_320.png')
json.dump(ladder, open(O + 'tier_ladder.json', 'w'), indent=1)
print(json.dumps(ladder, indent=1))
