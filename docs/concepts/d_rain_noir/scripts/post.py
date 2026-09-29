"""RAIN NOIR post pass (pure Pillow): cool shadow grade, lateral chroma fringe, slight vignette, film grain,
optional screen-wide Heat glitch (feedback 11).

Usage: python post.py IN.png OUT.png [--vignette 0.38] [--grain 7] [--fringe 2.5] [--glitch 0..1] [--seed N]
"""
import argparse, math, random
from PIL import Image, ImageChops, ImageDraw, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--vignette", type=float, default=0.38)
ap.add_argument("--grain", type=float, default=7.0, help="noise sigma in 0..255 units")
ap.add_argument("--fringe", type=float, default=2.5, help="px of R/B lateral split at the frame edge")
ap.add_argument("--glitch", type=float, default=0.0)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--desat", type=float, default=0.0, help="0..1 desaturation (Heat HUNTED grade)")
a = ap.parse_args()
rng = random.Random(a.seed)

im = Image.open(a.inp).convert("RGB")
W, H = im.size

# 1. cool the shadows (blue-grey noir); highlights untouched
lum = im.convert("L")
mask = lum.point(lambda v: max(0, 255 - v * 4))
r, g, b = im.split()
cool = Image.merge("RGB", (r.point(lambda v: max(0, v - 2)), g, b.point(lambda v: min(255, v + 5))))
im = Image.composite(cool, im, mask)

if a.desat > 0:
    im = Image.blend(im, im.convert("L").convert("RGB"), a.desat)

# 2. lateral chroma fringe: scale R up and B down about the centre (anamorphic glass)
if a.fringe > 0:
    r, g, b = im.split()
    def scale(ch, s):
        return ch.transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1, 0), resample=Image.BILINEAR)
    s = 1 + a.fringe / (W / 2)
    im = Image.merge("RGB", (scale(r, s), g, scale(b, 1 / s)))

# 3. heat glitch: displaced slices, RGB split bands, scanline flicker, torn HARM lines, dropout blocks
if a.glitch > 0:
    gl = a.glitch
    px = W / 1920.0
    base = im.copy()
    for _ in range(int(10 + 26 * gl)):
        y0 = rng.randrange(0, H - 4)
        h = max(1, int(rng.randrange(2, int(6 + 40 * gl)) * px))
        dx = int(rng.gauss(0, 18 * gl) * px)
        band = base.crop((0, y0, W, y0 + h))
        band = ImageChops.offset(band, dx, 0)
        if rng.random() < 0.5:
            sp = max(1, int(rng.randrange(3, int(6 + 14 * gl)) * px))
            br, bg, bb = band.split()
            band = Image.merge("RGB", (ImageChops.offset(br, sp, 0), bg, ImageChops.offset(bb, -sp, 0)))
        im.paste(band, (0, y0))
    lines = Image.new("L", (1, H), 255)
    lines.putdata([int(255 * (1 - 0.07 * gl)) if y % 3 == 0 else 255 for y in range(H)])
    im = ImageChops.multiply(im, lines.resize((W, H)).convert("RGB"))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(int(3 * gl) + 1):
        y0 = rng.randrange(0, H)
        d.line([(0, y0), (W, y0)], fill=(255, 68, 51, 140), width=1)
    for _ in range(int(8 * gl)):
        x0, y0 = rng.randrange(0, W - 220), rng.randrange(0, H - 30)
        w, h = int(rng.randrange(40, 220) * px), max(2, int(rng.randrange(6, 24) * px))
        blk = ImageOps.mirror(im.crop((x0, y0, x0 + w, y0 + h))).point(lambda v: int(v * 0.7))
        im.paste(blk, (x0, y0))

# 4. vignette (slight: it must still read as game UI)
if a.vignette > 0:
    sw, sh = 192, 108
    v = Image.new("L", (sw, sh))
    px = []
    for y in range(sh):
        for x in range(sw):
            dd = math.hypot((x - sw / 2) / (sw / 2), (y - sh / 2) / (sh / 2)) / math.sqrt(2)
            t = min(1.0, max(0.0, (dd - 0.35) / 0.65)) ** 1.6
            px.append(int(255 * (1 - a.vignette * t)))
    v.putdata(px)
    im = ImageChops.multiply(im, v.resize((W, H), Image.BICUBIC).convert("RGB"))

# 5. grain (zero-mean, slightly stronger in the darks)
if a.grain > 0:
    n = Image.effect_noise((W // 2, H // 2), a.grain).resize((W, H), Image.BILINEAR).convert("RGB")
    im = ImageChops.add(im, n, scale=1.0, offset=-128)

if a.out.lower().endswith(".jpg"):
    im.save(a.out, quality=92)
else:
    im.save(a.out, optimize=True)
print("POST", a.out)
