"""Tilt-shift + patchy variable fog blur for the iso city (feedback 7.2, 7.3). Pure Pillow.

Blur radius per pixel = distance from the focal depth band (depth pass from city_scene.depth_pass), stronger
into the distance, plus extra blur inside each fog patch (screen positions from *_fog.json), each patch with
its own strength and aspect. Blur levels are blended by a radius map (lerp between neighbouring levels).
Usage: python tiltshift.py BEAUTY.png DEPTH.png FOG.json OUT.png [--k 30] [--band 0.05] [--fogmax 7] [--seed 3]
"""
import argparse, json, math, random
from PIL import Image, ImageChops, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("beauty"); ap.add_argument("depth"); ap.add_argument("fog"); ap.add_argument("out")
ap.add_argument("--k", type=float, default=18.0, help="px of blur per unit depth away from the band (at 1920 wide)")
ap.add_argument("--band", type=float, default=0.1)
ap.add_argument("--fogmax", type=float, default=5.0)
ap.add_argument("--seed", type=int, default=3)
a = ap.parse_args()

ENC = 16.0  # radius map encodes px * ENC in 0..255
im = Image.open(a.beauty).convert("RGB")
W, H = im.size
sc = W / 1920.0
meta = json.load(open(a.fog))
focus = meta["focus"]
dep = Image.open(a.depth).convert("L").resize((W, H))


def lut(v):
    d = v / 255.0
    d = d / 12.92 if d <= 0.04045 else ((d + 0.055) / 1.055) ** 2.4   # depth PNG went through the sRGB view transform
    r = max(0.0, abs(d - focus) - a.band) * a.k * sc * (1.35 if d > focus else 0.85)
    return int(min(255, r * ENC))


R = dep.point(lut)
# fog patches at low res, then up
rng = random.Random(a.seed)
lw, lh = 384, 216
fog = [0.0] * (lw * lh)
for f in meta["fog"]:
    cx, cy, rr = f["x"] * lw, f["y"] * lh, f["r"] * lw * 1.1
    s = rng.uniform(0.25, 1.0) * a.fogmax * sc
    ex = rng.uniform(1.0, 1.8)
    for y in range(lh):
        for x in range(lw):
            q = ((x - cx) / (rr * ex)) ** 2 + ((y - cy) / rr) ** 2
            if q < 4:
                fog[y * lw + x] += math.exp(-q * 2.2) * s
F = Image.new("L", (lw, lh))
F.putdata([int(min(255, v * ENC)) for v in fog])
RF = ImageChops.add(R, F.resize((W, H), Image.BICUBIC))
# UI pixels were written at exactly the focus depth: keep them out of the fog blur so glass UI stays sharp
fs = focus ** (1 / 2.4) * 1.055 - 0.055 if focus > 0.0031308 else focus * 12.92
fv = int(round(fs * 255))
ui_mask = dep.point(lambda v: 255 if abs(v - fv) <= 1 else 0)
R = Image.composite(R, RF, ui_mask)

levels = [0, 1.2, 2.5, 4, 6, 9, 13]
levels = [l * sc for l in levels]
out = im
for i in range(1, len(levels)):
    lo, hi = levels[i - 1], levels[i]
    bl = im.filter(ImageFilter.GaussianBlur(hi))
    m = R.point(lambda v, lo=lo, hi=hi: int(255 * min(1.0, max(0.0, (v / ENC - lo) / (hi - lo)))))
    out = Image.composite(bl, out, m)
out.save(a.out)
print("TILTSHIFT", a.out, "focus", round(focus, 3))
