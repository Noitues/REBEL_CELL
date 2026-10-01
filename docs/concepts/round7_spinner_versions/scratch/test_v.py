import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from PIL import Image
import roster as RS, versions as V
t0 = time.time()
b, _ = RS.class_spec("breaker"); b["key"] = "breaker"
r, _ = RS.enemy_spec("route_optimizer"); r["key"] = "route_optimizer"
m, _, _ = RS.boss_specs("meridian"); m["key"] = "the_manifest"
rows = []
for v in (1, 2, 3):
    ims = [V.render_v(s, v, ss=1) for s in (b, r, m)]
    rows.append(ims)
W = 3 * 1260; H = 3 * 1600
out = Image.new("RGB", (W, H), (12, 10, 16))
for j, row in enumerate(rows):
    for i, im in enumerate(row):
        out.paste(im, (i * 1260, j * 1600), im)
out.resize((W // 3, H // 3)).save(os.path.join(HERE, "test_v.png"))
print(time.time() - t0)
