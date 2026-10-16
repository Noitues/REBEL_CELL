"""Street round 2: the sign texture library (PIL). One texture per planned sign, from its style, word and hue.

python r2_signs.py <seed>  ->  D:/rc_scratch/street_r2/signs_s<seed>/<sign id>.png (+ mega.png)

Styles: box (shop / secondary box sign), blade (vertical stacked letters), wall (hero poster board), ad (one of the
storyboard's ad plates, read-only from storyboard/scratch/ads), holo (black = additive), shop (lit shopfront glazing with
a fascia word). Pixel size follows the sign's aspect; text is drawn to fit, so a sign never clips its word.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SBS = os.path.normpath(os.path.join(HERE, "..", "..", "storyboard", "scripts"))
sys.path.insert(0, SBS)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
import numpy as np  # noqa: E402

import ui31 as K  # noqa: E402

SCR = "D:/rc_scratch/street_r2"
ADS = os.path.join(os.path.dirname(SBS), "scratch", "ads")
PALE = (235, 230, 245)


def c8(col, k=1.0):
    return tuple(int(max(0, min(255, v * 255 * k))) for v in col)


def fit_font(d, s, font, w, h):
    lo, hi = 6, 600
    while hi - lo > 1:
        m = (lo + hi) // 2
        f = K.F(font, m)
        b = d.textbbox((0, 0), s, font=f, anchor="lt")
        if b[2] - b[0] <= w and b[3] - b[1] <= h:
            lo = m
        else:
            hi = m
    return K.F(font, lo)


def glow(im, k=0.55, r=8):
    a = np.asarray(im.convert("RGB"), np.float32)
    g = np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(r)), np.float32)
    return Image.fromarray(np.clip(a + k * g, 0, 255).astype(np.uint8))


def grad(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    return im


def size_for(aspect, long_px=768):
    if aspect >= 1:
        return long_px, max(64, int(long_px / aspect))
    return max(64, int(long_px * aspect)), long_px


def box(word, sub, col, aspect, r):
    w, h = size_for(aspect)
    im = grad(w, h, c8(col, 0.10), (6, 4, 12))
    d = ImageDraw.Draw(im)
    f = fit_font(d, word, K.ANTON, int(w * 0.84), int(h * (0.50 if sub else 0.62)))
    d.text((w // 2, int(h * (0.42 if sub else 0.5))), word, font=f, fill=c8(col), anchor="mm")
    if sub:
        f2 = fit_font(d, sub, K.MONO, int(w * 0.6), int(h * 0.16))
        d.text((w // 2, int(h * 0.80)), sub, font=f2, fill=PALE, anchor="mm")
    t = max(4, h // 18)
    d.rectangle((t, t, w - t, h - t), outline=c8(col, 0.9), width=t)
    return glow(im)


def blade(word, sub, col, aspect, r):
    w, h = size_for(aspect)
    im = grad(w, h, (16, 4, 24), (4, 2, 10))
    d = ImageDraw.Draw(im)
    ch = [c for c in word if c != " "]
    n = len(ch) + (1 if sub else 0)
    pitch = (h - 0.08 * h) / max(1, n)
    f = fit_font(d, "W", K.ANTON, int(w * 0.78), int(pitch * 0.86))
    y = 0.04 * h + pitch / 2
    for c in ch:
        d.text((w // 2, int(y)), c, font=f, fill=c8(col), anchor="mm")
        y += pitch
    if sub:
        f2 = fit_font(d, sub, K.MONO, int(w * 0.8), int(pitch * 0.4))
        d.text((w // 2, int(y)), sub, font=f2, fill=PALE, anchor="mm")
    t = max(4, w // 22)
    d.rectangle((t, t, w - t, h - t), outline=c8(col, 0.9), width=t)
    return glow(im, 0.6)


def wall(word, sub, col, aspect, r):
    """A hero poster: a hue field, a graphic (rings / bars / chevrons by seed), the word large, a sub line."""
    w, h = size_for(aspect, 1024)
    im = grad(w, h, c8(col, 0.30), c8(col, 0.05))
    d = ImageDraw.Draw(im)
    g = r.randrange(3)
    acc = c8(col, 1.0)
    if g == 0:
        cx, cy = int(w * 0.78), int(h * 0.45)
        for k in range(5):
            rr = int(h * (0.12 + 0.08 * k))
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=c8(col, 0.9 - 0.15 * k), width=max(3, h // 70))
    elif g == 1:
        for k in range(7):
            x = int(w * (0.62 + 0.05 * k))
            d.rectangle((x, int(h * (0.15 + 0.07 * (k % 3))), x + max(6, w // 60), int(h * 0.85)), fill=c8(col, 0.9 - 0.08 * k))
    else:
        for k in range(4):
            y = int(h * (0.25 + 0.15 * k))
            d.line([(int(w * 0.62), y), (int(w * 0.78), y + int(h * 0.08)), (int(w * 0.94), y)], fill=c8(col, 0.95 - 0.15 * k),
                   width=max(4, h // 40))
    f = fit_font(d, word, K.ANTON, int(w * 0.56), int(h * 0.42))
    d.text((int(w * 0.06), int(h * 0.42)), word, font=f, fill=(250, 248, 255), anchor="lm")
    d.line([(int(w * 0.06), int(h * 0.66)), (int(w * 0.5), int(h * 0.66))], fill=acc, width=max(3, h // 60))
    f2 = fit_font(d, sub or "24 H", K.MONO, int(w * 0.4), int(h * 0.11))
    d.text((int(w * 0.06), int(h * 0.78)), sub or "24 H", font=f2, fill=PALE, anchor="lm")
    t = max(6, h // 40)
    d.rectangle((t, t, w - t, h - t), outline=acc, width=t)
    return glow(im, 0.45)


def ad(name, aspect):
    im = Image.open(os.path.join(ADS, name + ".png")).convert("RGB")
    w, h = im.size
    a0 = w / h
    if aspect > a0:          # crop height
        nh = int(w / aspect)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    else:
        nw = int(h * aspect)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    return im


def holo(word, sub, col, aspect, r):
    w, h = size_for(aspect)
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = fit_font(d, word, K.ANTON, int(w * 0.8), int(h * 0.5))
    d.text((w // 2, int(h * 0.42)), word, font=f, fill=c8(col), anchor="mm")
    if sub:
        f2 = fit_font(d, sub, K.MONO, int(w * 0.6), int(h * 0.14))
        d.text((w // 2, int(h * 0.78)), sub, font=f2, fill=PALE, anchor="mm")
    d.rectangle((6, 6, w - 6, h - 6), outline=c8(col), width=5)
    for y in range(0, h, 4):
        d.line([(0, y), (w, y)], fill=(0, 0, 0), width=1)
    rr, gg, bb = im.split()
    rr = rr.transform(im.size, Image.AFFINE, (1, 0, -3, 0, 1, 0))
    bb = bb.transform(im.size, Image.AFFINE, (1, 0, 3, 0, 1, 0))
    return Image.merge("RGB", (rr, gg, bb))


def shop(word, col, aspect, r):
    """Lit shopfront glazing: a warm / hue interior gradient, mullions, shelf silhouettes, a fascia band with a word."""
    w, h = size_for(aspect, 1024)
    warm = r.random() < 0.5
    top = (255, 214, 160) if warm else c8(col, 0.95)
    im = grad(w, h, tuple(int(v * 0.55) for v in top), tuple(int(v * 0.95) for v in top))
    d = ImageDraw.Draw(im)
    fb = int(h * 0.26)
    d.rectangle((0, 0, w, fb), fill=(14, 10, 20))
    f = fit_font(d, word, K.ANTON, int(w * 0.35), int(fb * 0.7))
    d.text((int(w * 0.05), fb // 2), word, font=f, fill=c8(col), anchor="lm")
    # shelves with small lit goods, a dark door, mullions over all
    for k in range(3):
        y = int(fb + (h - fb) * (0.3 + 0.22 * k))
        d.rectangle((0, y, w, y + 4), fill=(40, 30, 44))
        x = r.randint(4, 30)
        while x < w - 20:
            gw = r.randint(8, 22)
            gc = r.choice([c8(col), (255, 240, 220), (120, 220, 255), (255, 120, 190)])
            d.rectangle((x, y - r.randint(10, 26), x + gw, y), fill=tuple(int(v * 0.8) for v in gc))
            x += gw + r.randint(4, 28)
    dx = int(w * r.uniform(0.15, 0.75))
    d.rectangle((dx, int(h * 0.38), dx + int(h * 0.38), h), fill=(18, 14, 22))
    n = max(2, int(aspect * 1.4))
    for k in range(1, n):
        x = int(w * k / n)
        d.rectangle((x - 3, fb, x + 3, h), fill=(20, 16, 26))
    return im


def make(seed):
    plan = json.load(open(os.path.join(SCR, "plan_s%s.json" % seed)))
    out = os.path.join(SCR, "signs_s%s" % seed)
    os.makedirs(out, exist_ok=True)
    n = 0
    for s in plan["signs"]:
        t = s["tex"]
        r = random.Random(t["seed"])
        aspect = (s["u1"] - s["u0"]) / max(0.05, s["z1"] - s["z0"])
        st = t["style"]
        if st == "box":
            im = box(t["word"], t.get("sub", ""), s["col"], aspect, r)
        elif st == "blade":
            im = blade(t["word"], t.get("sub", ""), s["col"], aspect, r)
        elif st == "wall":
            im = wall(t["word"], t.get("sub", ""), s["col"], aspect, r)
        elif st == "ad":
            im = ad(t["ad"], aspect)
        elif st == "holo":
            im = holo(t["word"], t.get("sub", ""), s["col"], aspect, r)
        else:
            im = shop(t["word"], s["col"], aspect, r)
        im.save(os.path.join(out, s["id"] + ".png"))
        n += 1
    m = plan.get("mega")
    if m:
        ad(m["tex"]["ad"], 2.4 if m["kind"] == "arch" else 16 / 9).save(os.path.join(out, "mega.png"))
    print("sign textures", n, "->", out)


if __name__ == "__main__":
    make(sys.argv[1] if len(sys.argv) > 1 else "1")
