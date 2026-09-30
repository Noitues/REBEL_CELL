"""Pillow post-pass (no numpy).

  python post.py city   <render_rgba.png> <out.png> <day|night|alarm>
      painted backdrop (soft radial light + big brush blotches + grain) under the diorama, vignette.
  python post.py over   <plate.png> <fg_rgba.png> <out.png> <combat|shop>
      city plate pushed back (blur, darken, tint) under the transparent UI/prop render.
"""
import random
import sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

W, H = 1920, 1080
BACK = {  # centre colour, edge colour, blotch colours
    "day": ("#a8a07a", "#4e4a3c", ["#b2a67e", "#8a8266", "#9a9478", "#6e6a58"]),
    "night": ("#1e2433", "#07090f", ["#262c3c", "#1a1f2c", "#2c2436", "#141820"]),
    "alarm": ("#42122a", "#12050c", ["#5a1a30", "#3a0f24", "#6a1a2a", "#2a0a1e"]),
}


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def radial(size, inner, outer, cx=0.5, cy=0.46, rx=0.62, ry=0.72, steps=48):
    """Smooth radial gradient built from concentric blurred ellipses."""
    im = Image.new("RGB", size, hx(outer))
    d = ImageDraw.Draw(im)
    a, b = hx(inner), hx(outer)
    for i in range(steps):
        t = i / (steps - 1)
        k = 1.0 - t
        col = tuple(int(b[j] + (a[j] - b[j]) * (t ** 1.3)) for j in range(3))
        w_, h_ = size[0] * rx * k * 1.4, size[1] * ry * k * 1.4
        d.ellipse([size[0] * cx - w_, size[1] * cy - h_, size[0] * cx + w_, size[1] * cy + h_], fill=col)
    return im.filter(ImageFilter.GaussianBlur(40))


def brush_blotches(im, cols, seed, n=70, alpha=38):
    rng = random.Random(seed)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        rw, rh = rng.uniform(80, 320), rng.uniform(25, 90)
        c = hx(rng.choice(cols))
        # a "stroke": a few overlapping skewed ellipses along a direction
        ang = rng.uniform(-0.5, 0.5)
        for k in range(5):
            ox = k * rw * 0.35
            oy = ox * ang
            d.ellipse([x + ox - rw / 2, y + oy - rh / 2, x + ox + rw / 2, y + oy + rh / 2], fill=c + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    return Image.alpha_composite(im.convert("RGBA"), layer)


def grain(im, amt=10, seed=3):
    n = Image.effect_noise(im.size, 40).convert("L")
    n = n.point(lambda v: 128 + (v - 128) * amt // 40)
    rgb = im.convert("RGB")
    over = Image.merge("RGB", (n, n, n))
    return ImageChops.overlay(rgb, over) if hasattr(ImageChops, "overlay") else rgb


def vignette(im, strength=0.45):
    mask = radial(im.size, "#ffffff", "#000000", rx=0.72, ry=0.8, cy=0.5)
    mask = mask.convert("L").point(lambda v: int(255 * (1 - strength) + v * strength))
    black = Image.new("RGB", im.size, (0, 0, 0))
    return Image.composite(im.convert("RGB"), black, mask)


def backdrop(mode, seed=11):
    c_in, c_out, cols = BACK[mode]
    bg = radial((W, H), c_in, c_out)
    bg = brush_blotches(bg, cols, seed)
    if mode == "alarm":
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(glow)
        d.ellipse([W * 0.15, H * 0.55, W * 0.85, H * 1.25], fill=(255, 40, 70, 70))
        bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(120)))
    if False:
        rng = random.Random(seed + 1)
        d = ImageDraw.Draw(bg)
        for _ in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, H * 0.55)
            r = rng.choice((1, 1, 1.5, 2))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 225, 255, rng.randint(60, 160)))
    return bg


def smog(im, mode, seed=5):
    """Painted smog bands drifting across the scene (lighter, yellowish by day)."""
    rng = random.Random(seed)
    col = {"day": (190, 178, 130), "night": (70, 80, 100), "alarm": (120, 40, 70)}[mode]
    a = {"day": 55, "night": 38, "alarm": 42}[mode]
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(26):
        y = rng.uniform(H * 0.1, H * 0.95)
        x = rng.uniform(-200, W)
        d.ellipse([x, y - rng.uniform(20, 50), x + rng.uniform(400, 900), y + rng.uniform(20, 50)], fill=col + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    return Image.alpha_composite(im.convert("RGBA"), layer)


def rain(im, mode, seed=9, n=900):
    """Painted rain: thin slanted streaks, a few brighter ones."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base = {"day": (220, 215, 195), "night": (170, 190, 230), "alarm": (230, 150, 170)}[mode]
    for _ in range(n):
        x, y = rng.uniform(-100, W), rng.uniform(-50, H)
        L = rng.uniform(25, 70)
        a = rng.randint(35, 90)
        d.line([x, y, x + L * 0.22, y + L], fill=base + (a,), width=rng.choice((1, 1, 2)))
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(im.convert("RGBA"), layer)


def city(src, out, mode):
    fg = Image.open(src).convert("RGBA")
    bg = backdrop(mode)
    im = Image.alpha_composite(bg, fg)
    im = smog(im, mode)
    im = rain(im, mode)
    im = grain(im, 7)
    im = vignette(im, 0.35 if mode == "day" else 0.5)
    im.save(out)


def over(plate, fg_path, out, kind):
    pl = Image.open(plate).convert("RGBA")
    bg = backdrop("night")
    pl = Image.alpha_composite(bg, pl).convert("RGB")
    # push back: soften, darken, cool/warm tint
    pl = pl.resize((W, H)).filter(ImageFilter.GaussianBlur(5 if kind == "combat" else 7))
    pl = ImageEnhance.Brightness(pl).enhance(0.62 if kind == "combat" else 0.55)
    pl = ImageEnhance.Color(pl).enhance(0.85)
    tint = Image.new("RGB", (W, H), hx("#2a1a3a") if kind == "combat" else hx("#3a2418"))
    pl = Image.blend(pl, tint, 0.28)
    pl = rain(smog(pl, "night"), "night", n=700).convert("RGB")
    pl = vignette(pl, 0.55)
    fg = Image.open(fg_path).convert("RGBA")
    # soft painted drop shadow under the props / UI
    sh = fg.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
    shadow = Image.new("RGBA", (W, H), (8, 4, 12, 0))
    shadow.putalpha(sh)
    base = pl.convert("RGBA")
    base.alpha_composite(shadow, (8, 14))
    im = Image.alpha_composite(base, fg)
    im = grain(im, 6)
    im.convert("RGB").save(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "city":
        city(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "over":
        over(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    print("post ok", sys.argv[1:])
