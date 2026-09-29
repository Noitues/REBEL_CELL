"""RISO PUNK ZINE: print pass over a Blender render.

python post.py <in.png> <out.png> [--glitch STRENGTH] [--seed N]

1. misregistration: the red plate is nudged 2 px (spot inks never line up);
2. a faint dot screen in the shadows (the page was printed, not lit);
3. xerox grain + paper fibre;
4. --glitch: the Heat glitch (feedback 11): sliced horizontal displacement,
   RGB plate split and a few bright scan bands. Off in Options = skip this step.
"""
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riso_print import grain, halftone


def misregister(img, dx=2, dy=1):
    r, g, b = img.split()
    r2 = ImageChops.offset(r, dx, dy)
    b2 = ImageChops.offset(b, -1, 0)
    return Image.merge("RGB", (r2, g, b2))


def dot_screen(img, amount=0.09):
    lum = img.convert("L")
    dark = lum.point(lambda v: max(0, 150 - v))  # ink goes where it's dark
    dots = halftone(dark, 5, 22)
    ink_ = Image.new("RGB", img.size, (10, 8, 16))
    mask = dots.point(lambda v: int(v * amount))
    return Image.composite(ink_, img, mask)


def glitch(img, strength, seed):
    rng = random.Random(seed)
    w, h = img.size
    out = img.copy()
    # sliced horizontal displacement
    for _ in range(int(14 * strength)):
        y = rng.randrange(0, h - 10)
        bh = rng.randint(2, int(14 * strength) + 3)
        dx = rng.randint(-int(40 * strength), int(40 * strength))
        band = img.crop((0, y, w, y + bh))
        out.paste(ImageChops.offset(band, dx, 0), (0, y))
    # plate split in a few zones
    r, g, b = out.split()
    split = Image.merge("RGB", (ImageChops.offset(r, int(6 * strength), 0), g, ImageChops.offset(b, -int(5 * strength), 0)))
    zone = Image.new("L", (w, h), 0)
    zd = ImageDraw.Draw(zone)
    for _ in range(4):
        y = rng.randrange(0, h)
        zd.rectangle((0, y, w, y + rng.randint(30, 140)), fill=255)
    zone = zone.filter(ImageFilter.GaussianBlur(6))
    out = Image.composite(split, out, zone)
    # hot scan bands (HARM tint), very sparse
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for _ in range(3):
        y = rng.randrange(0, h)
        od.rectangle((0, y, w, y + rng.randint(1, 3)), fill=(255, 68, 51, int(90 * strength)))
    for y in range(0, h, 3):
        od.line((0, y, w, y), fill=(0, 0, 0, int(22 * strength)))
    out = Image.alpha_composite(out.convert("RGBA"), over).convert("RGB")
    return out


def hunted_grade(img):
    """HUNTED Heat: the city is overprinted with a HARM-red plate: desaturate 25%,
    multiply a warm red, and a red halftone creeping in from the edges."""
    grey = img.convert("L").convert("RGB")
    img = Image.blend(img, grey, 0.25)
    img = ImageChops.multiply(img, Image.new("RGB", img.size, (255, 214, 204)))
    w, h = img.size
    edge = Image.new("L", (w // 8, h // 8), 0)
    px = edge.load()
    for y in range(h // 8):
        for x in range(w // 8):
            dx = abs(x / (w / 8) - 0.5) * 2
            dy = abs(y / (h / 8) - 0.5) * 2
            px[x, y] = int(max(0.0, max(dx, dy) - 0.55) / 0.45 * 150)
    edge = edge.resize((w, h), Image.BILINEAR)
    dots = halftone(edge, 7, 15)
    return Image.composite(Image.new("RGB", (w, h), (255, 68, 51)), img, dots.point(lambda v: int(v * 0.22)))


def tiltshift(img, y0, y1, top_r=4.0, bot_r=2.0):
    """Ortho tilt-shift (feedback 7.3): sharp band y0..y1 (fractions of height); blur
    ramps up toward the top (far city) and a little toward the bottom (near table)."""
    w, h = img.size
    a, b = int(y0 * h), int(y1 * h)
    out = img
    for r, lo, hi, top in ((top_r * 0.45, 0, a, True), (top_r, 0, a, True), (bot_r, b, h, False)):
        bl = img.filter(ImageFilter.GaussianBlur(r))
        m = Image.new("L", (1, h), 0)
        for y in range(h):
            if top and y < a:
                t = (a - y) / max(1, a)
                v = min(1.0, t * (1.6 if r < top_r else 1.0)) ** (1.0 if r < top_r else 1.8)
            elif not top and y > b:
                v = (y - b) / max(1, h - b)
            else:
                v = 0.0
            m.putpixel((0, y), int(255 * v))
        out = Image.composite(bl, out, m.resize((w, h)))
    return out


def main():
    a = sys.argv[1:]
    src, dst = a[0], a[1]
    g = float(a[a.index("--glitch") + 1]) if "--glitch" in a else 0.0
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 1
    img = Image.open(src).convert("RGB")
    if "--tiltshift" in a:
        y0, y1 = (float(v) for v in a[a.index("--tiltshift") + 1].split(","))
        img = tiltshift(img, y0, y1)
    if "--overlay" in a:
        ov = Image.open(a[a.index("--overlay") + 1]).convert("RGBA")
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    img = misregister(img)
    img = dot_screen(img)
    img = grain(img, 16, seed, size_div=1)
    img = grain(img, 10, seed + 1, size_div=3)
    if g > 0:
        img = glitch(img, g, seed)
    if "--hunted" in a:
        img = hunted_grade(img)
    img.save(dst)
    print("post ->", dst)


if __name__ == "__main__":
    main()
