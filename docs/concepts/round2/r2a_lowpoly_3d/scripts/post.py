"""R2A LOW-POLY 3D: Pillow post-pass (no numpy). The reference's soft finish:
gentle desaturation, a warm cast, a soft vignette and a whisper of seeded grain.

python post.py <in.png> <out.png> <day|night|alert|combat|shop>
"""
import random
import sys
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

GRADES = {
    #          sat   warm (r,g,b mult)     vignette colour  strength  grain
    "day":    (0.86, (1.03, 1.0, 0.94), (96, 64, 60), 0.42, 5),
    "night":  (0.92, (1.02, 0.98, 1.0), (14, 8, 22), 0.55, 5),
    "alert":  (0.9, (1.04, 0.97, 0.97), (30, 4, 12), 0.6, 6),
    "combat": (0.9, (1.02, 0.99, 0.97), (18, 10, 26), 0.5, 5),
    "shop":   (0.88, (1.03, 0.99, 0.95), (24, 12, 22), 0.5, 5),
}


def vignette_mask(w, h, strength):
    g = Image.radial_gradient("L").resize((w, h), Image.BILINEAR)
    # 0 at centre -> 255 at corners; keep the middle clean, ease into the edges
    return g.point(lambda v: int(max(0, min(255, (v - 110) * 1.9 * strength))))


def main():
    src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    sat, warm, vcol, vstr, grain = GRADES[mode]
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im = ImageEnhance.Color(im).enhance(sat)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * warm[0])))
    g = g.point(lambda v: min(255, int(v * warm[1])))
    b = b.point(lambda v: min(255, int(v * warm[2])))
    im = Image.merge("RGB", (r, g, b))
    # a very slight softening, like the reference's gentle render
    im = Image.blend(im, im.filter(ImageFilter.GaussianBlur(0.8)), 0.35)
    dark = Image.new("RGB", (w, h), vcol)
    im = Image.composite(dark, im, vignette_mask(w, h, vstr))
    if grain:
        rng = random.Random(4242)
        noise = Image.frombytes("L", (w, h), rng.randbytes(w * h))
        noise = noise.point(lambda v: 128 + (v - 128) * grain // 64)
        n3 = Image.merge("RGB", (noise, noise, noise))
        im = ImageChops.overlay(im, n3)
    im.save(dst, optimize=True)
    print("POST", dst)


if __name__ == "__main__":
    main()
