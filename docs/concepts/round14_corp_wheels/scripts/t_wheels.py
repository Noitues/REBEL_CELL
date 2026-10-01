"""Quick check of d4corp: python t_wheels.py <corp> -> ../scratch/t_<corp>.png (regular, elite, boss p1-p3)."""
import os
import sys
import time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCR = os.path.join(os.path.dirname(HERE), "scratch")
os.makedirs(SCR, exist_ok=True)
from PIL import Image
import d4corp as D
import specs14 as S
import frames as F

corp = sys.argv[1] if len(sys.argv) > 1 else "meridian"
reg, eli = S.PICKS[corp]
ims = []
t = time.time()
for s in (S.enemy(reg, corp, "regular")[0], S.enemy(eli, corp, "elite")[0], S.boss(corp, 1)[0], S.boss(corp, 2)[0], S.boss(corp, 3)[0]):
    im, c, m = D.render(s, ss=1, hp_number=True)
    im, c = F.fit(im, c, 1, 150)
    ims.append(im)
    print("wheel %.1fs" % (time.time() - t), flush=True)
W = sum(i.width for i in ims) + 20 * len(ims)
sheet = Image.new("RGBA", (W, max(i.height for i in ims)), (22, 20, 28, 255))
x = 0
for im in ims:
    sheet.alpha_composite(im, (x, 0))
    x += im.width + 20
sheet.convert("RGB").save(os.path.join(SCR, "t_%s.png" % corp))
