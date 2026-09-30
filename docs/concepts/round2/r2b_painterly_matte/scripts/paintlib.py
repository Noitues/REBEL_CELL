"""r2b_painterly_matte - shared Pillow post-pass: painted sky, atmospheric perspective,
brush-stroke repaint, canvas grain, split-tone grade, and the crisp UI kit.
Pure Pillow (no numpy). All randomness is seeded."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

W, H = 1920, 1080
FONT_DIR = "C:/Windows/Fonts/"

def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

def solid(color, size=(W, H), mode="RGB"):
    return Image.new(mode, size, color)

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_c(c0, c1, t):
    return tuple(int(round(lerp(c0[i], c1[i], t))) for i in range(len(c0)))

def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x

# ------------------------------------------------------------------ depth
def load_depth(path):
    """Depth pass -> 'L' image, 0 near .. 255 far (sqrt-encoded distance / DMAX); sky = 255."""
    im = Image.open(path).convert("RGBA")
    r, g, b, a = im.split()
    sky = solid(255, im.size, "L")
    return Image.composite(r, sky, a)

def depth_mask(depth, fn):
    """Map depth (v in 0..1, sqrt-encoded) through fn -> 0..1, as an 'L' mask."""
    lut = [int(255 * clamp01(fn(i / 255.0))) for i in range(256)]
    return depth.point(lut)

# ------------------------------------------------------------------ sky
SKIES = {
    "day":   {"top": (40, 92, 186), "mid": (108, 158, 214), "hor": (232, 222, 200),
              "cl_lit": (255, 250, 236), "cl_mid": (226, 230, 238), "cl_sh": (150, 166, 198), "stars": 0,
              "banks": [(180, 250, 760, 230, 255), (1760, 300, 560, 300, 255), (950, 320, 700, 70, 200), (1300, 250, 300, 90, 170)]},
    "night": {"top": (6, 9, 26), "mid": (18, 24, 58), "hor": (92, 52, 96),
              "cl_lit": (130, 80, 128), "cl_mid": (48, 42, 84), "cl_sh": (18, 20, 44), "stars": 260, "lit_below": True,
              "banks": [(180, 250, 760, 230, 235), (1760, 300, 560, 300, 235), (950, 320, 700, 70, 190)]},
    "alarm": {"top": (14, 4, 12), "mid": (48, 10, 26), "hor": (168, 36, 30),
              "cl_lit": (210, 64, 48), "cl_mid": (92, 22, 36), "cl_sh": (28, 8, 20), "stars": 60, "lit_below": True,
              "banks": [(180, 250, 760, 230, 240), (1760, 300, 560, 300, 240), (950, 320, 700, 70, 200)]},
}

def painted_sky(kind, seed=7, horizon=0.36):
    """Gradient + cumulus banks + loose diagonal brushwork, like the reference's sky."""
    P = SKIES[kind]
    rng = random.Random(seed)
    sky = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(sky)
    hy = int(H * horizon)
    for y in range(H):
        t = y / max(1, hy)
        if t < 0.55:
            c = lerp_c(P["top"], P["mid"], t / 0.55)
        elif t < 1.0:
            c = lerp_c(P["mid"], P["hor"], ((t - 0.55) / 0.45) ** 1.3)
        else:
            c = P["hor"]
        d.line([(0, y), (W, y)], fill=c)
    # stars
    for i in range(P["stars"]):
        x, y = rng.uniform(0, W), rng.uniform(0, hy * 0.8)
        v = rng.randint(120, 230)
        d.point((x, y), fill=(v, v, min(255, v + 20)))
    # cumulus masses: puffs inside a dome-shaped envelope, shaded per puff
    cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cl)
    below = P.get("lit_below", False)
    for (cx, cy, w, h, a) in P["banks"]:
        puffs = []
        for i in range(int(w * h / 700)):
            u = rng.uniform(-1, 1)
            top = h * (1 - u * u) ** 0.8
            y = cy - rng.uniform(0, top)
            x = cx + u * w / 2 + rng.gauss(0, 8)
            r = rng.uniform(0.10, 0.22) * h * (0.45 + 0.55 * (1 - u * u))
            puffs.append((y, x, r))
        puffs.sort()
        for (y, x, r) in puffs:
            sh = 1 if not below else -1
            cd.ellipse([x - r * 1.05 + r * 0.1, y - r + r * 0.28 * sh, x + r * 1.05 + r * 0.1, y + r + r * 0.28 * sh], fill=P["cl_sh"] + (a,))
            cd.ellipse([x - r * 0.95, y - r * 0.95, x + r * 0.95, y + r * 0.95], fill=P["cl_mid"] + (a,))
            lr = r * 0.62
            lx, ly = x - r * 0.22, y - r * 0.3 * sh
            cd.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=P["cl_lit"] + (a,))
        # flat shadowed base
        cd.ellipse([cx - w * 0.5, cy - h * 0.08, cx + w * 0.5, cy + h * 0.12], fill=P["cl_sh"] + (int(a * 0.9),))
    for i in range(14):  # thin high streaks
        x = rng.uniform(0, W); y = rng.uniform(H * 0.04, H * 0.2); w = rng.uniform(120, 380)
        cd.ellipse([x - w, y - 5, x + w, y + 5], fill=P["cl_mid"] + (70,))
    cl = cl.filter(ImageFilter.GaussianBlur(2.5))
    sky.paste(cl, (0, 0), cl)
    return sky

# ------------------------------------------------------------------ atmosphere
def atmosphere(img, depth, haze_color, start=0.36, end=0.95, max_amt=0.85, power=1.3, alpha=None):
    m = depth_mask(depth, lambda v: max_amt * clamp01((v - start) / (end - start)) ** power)
    if alpha is not None:  # only veil geometry, never the painted sky
        m = ImageChops.multiply(m, alpha.filter(ImageFilter.GaussianBlur(1)))
    return Image.composite(solid(haze_color, img.size), img, m)

def haze_band(img, y0, y1, color, amt):
    """Low-lying haze band near the horizon (painted mist between layers)."""
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    for y in range(max(0, y0), min(img.size[1], y1)):
        t = (y - y0) / max(1, (y1 - y0))
        d.line([(0, y), (img.size[0], y)], fill=int(255 * amt * math.sin(t * math.pi)))
    return Image.composite(solid(color, img.size), img, m.filter(ImageFilter.GaussianBlur(20)))

def bloom(img, threshold=200, radii=(6, 22, 60), gains=(0.7, 0.5, 0.35)):
    lum = img.convert("L").point(lambda v: 255 if v > threshold else int(255 * (v / threshold) ** 6))
    bright = Image.composite(img, solid((0, 0, 0), img.size), lum)
    out = img
    for r, g in zip(radii, gains):
        b = bright.filter(ImageFilter.GaussianBlur(r))
        b = b.point(lambda v, g=g: int(v * g))
        out = ImageChops.add(out, b)
    return out

def glow_dot(layer, x, y, r, color, alpha=255):
    d = ImageDraw.Draw(layer)
    d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))

# ------------------------------------------------------------------ brushwork
def _grad_field(img, scale=4):
    small = img.convert("L").resize((img.size[0] // scale, img.size[1] // scale), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(1.5))
    return small, small.load(), scale

def brush_pass(img, depth, seed=11, step_near=4, step_far=10, default_angle=-0.18,
               jitter=0.06, length=2.3, width=0.85, fine=True):
    """Repaint the image with oriented, tapered strokes. Stroke size grows with distance,
    strokes follow edges (perpendicular to the luminance gradient), flat areas get
    loose diagonal strokes like the reference's sky and ground."""
    rng = random.Random(seed)
    W, H = img.size
    src = img.filter(ImageFilter.GaussianBlur(1.2))
    far = depth_mask(depth, lambda v: clamp01((v - 0.5) / 0.2))  # distant masses sample softer colour
    src = Image.composite(img.filter(ImageFilter.GaussianBlur(3.5)), src, far)
    sp = src.load()
    dp = depth.load()
    gsmall, gp, gs = _grad_field(src)
    gw, gh = gsmall.size
    canvas = src.copy()
    cd = ImageDraw.Draw(canvas)
    shape = [(-0.5, 0.0), (-0.32, 0.5), (0.3, 0.45), (0.5, 0.0), (0.28, -0.42), (-0.3, -0.5)]

    def strokes(step_fn, count_scale, len_scale):
        pts = []
        y = 0.0
        while y < H:
            x = 0.0
            row_step = None
            while x < W:
                v = dp[min(W - 1, int(x)), min(H - 1, int(y))] / 255.0
                s = step_fn(v)
                if s is not None:
                    pts.append((x + rng.uniform(0, s), y + rng.uniform(0, s), s))
                    x += s
                else:
                    x += step_near
                row_step = s if s else step_near
            y += step_near if count_scale else row_step
        rng.shuffle(pts)
        for (px, py, s) in pts:
            ix, iy = min(W - 1, int(px)), min(H - 1, int(py))
            c = sp[ix, iy]
            gx_i, gy_i = min(gw - 2, max(1, ix // gs)), min(gh - 2, max(1, iy // gs))
            gx = gp[gx_i + 1, gy_i] - gp[gx_i - 1, gy_i]
            gy = gp[gx_i, gy_i + 1] - gp[gx_i, gy_i - 1]
            mag = math.hypot(gx, gy)
            if mag > 6:
                ang = math.atan2(gy, gx) + math.pi / 2
            else:
                ang = default_angle + rng.gauss(0, 0.25)
            L = s * length * len_scale * rng.uniform(0.8, 1.25)
            wdt = s * width * rng.uniform(0.8, 1.2)
            if mag > 30:
                L *= 0.7
            ca, sa = math.cos(ang), math.sin(ang)
            poly = [(px + u * L * ca - v * wdt * sa, py + u * L * sa + v * wdt * ca) for (u, v) in shape]
            k = 1.0 + rng.uniform(-jitter, jitter)
            warm = rng.uniform(-jitter, jitter) * 40
            col = (int(min(255, max(0, c[0] * k + warm))), int(min(255, max(0, c[1] * k))),
                   int(min(255, max(0, c[2] * k - warm))))
            cd.polygon(poly, fill=col)

    # big loose pass everywhere, scaled by distance
    strokes(lambda v: step_near + (step_far - step_near) * clamp01((v - 0.25) / 0.6) * 1.0 + 3, False, 1.0)
    if fine:
        # fine pass on the foreground / mid-ground only
        strokes(lambda v: (step_near if v < 0.5 else None), True, 0.8)
    return canvas

def repaint(img, depth, keep_near=0.72, keep_start=0.40, keep_end=0.58, **kw):
    """Brushwork everywhere, blended back toward the crisp render in the foreground."""
    painted = brush_pass(img, depth, **kw)
    keep = depth_mask(depth, lambda v: keep_near * clamp01((keep_end - v) / (keep_end - keep_start)))
    sharp = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    return Image.composite(sharp, painted, keep)

# ------------------------------------------------------------------ finishing
def seeded_noise(size, seed, sigma=40, mean=128):
    rng = random.Random(seed)
    n = size[0] * size[1]
    im = Image.new("L", size)
    im.putdata([max(0, min(255, int(rng.gauss(mean, sigma)))) for _ in range(n)])
    return im

def canvas_grain(img, seed=3, amount=0.10, blotch=0.07):
    """Fine canvas tooth plus low-frequency paint blotches (both from a seeded RNG)."""
    n = seeded_noise((img.size[0] // 2, img.size[1] // 2), seed).resize(img.size, Image.BILINEAR).convert("RGB")
    out = Image.blend(img, ImageChops.overlay(img, n), amount)
    bl = seeded_noise((img.size[0] // 24, img.size[1] // 24), seed + 1, 55).resize(img.size, Image.BICUBIC)
    bl = bl.filter(ImageFilter.GaussianBlur(8)).convert("RGB")
    return Image.blend(out, ImageChops.soft_light(out, bl), min(1.0, blotch * 4))

def split_tone(img, warm=(255, 206, 150), cool=(70, 110, 170), amt_hi=0.35, amt_lo=0.30):
    """Warm sunlit highlights, cool shadows (the reference's light logic)."""
    lum = img.convert("L")
    hi = lum.point(lambda v: int(255 * amt_hi * clamp01((v - 110) / 145.0) ** 1.2))
    lo = lum.point(lambda v: int(255 * amt_lo * clamp01((120 - v) / 120.0)))
    wimg = ImageChops.multiply(img, solid(warm, img.size)).point(lambda v: min(255, int(v * 1.25)))
    cimg = ImageChops.multiply(img, solid(cool, img.size)).point(lambda v: min(255, int(v * 1.9)))
    out = Image.composite(wimg, img, hi)
    return Image.composite(cimg, out, lo)

def vignette(img, strength=0.35, color=(0, 0, 0)):
    rad = Image.radial_gradient("L").resize(img.size, Image.BICUBIC)  # 0 centre -> 255 edge
    rad = rad.point(lambda v: int(255 * strength * clamp01((v - 120) / 135.0) ** 1.6))
    return Image.composite(solid(color, img.size), img, rad)

def color_balance(img, r=1.0, g=1.0, b=1.0, lift=0):
    ch = img.split()
    return Image.merge("RGB", [c.point(lambda v, k=k: max(0, min(255, int(v * k + lift)))) for c, k in zip(ch, (r, g, b))])

def contrast(img, k=1.1, pivot=128):
    return img.point(lambda v: max(0, min(255, int((v - pivot) * k + pivot))))

# ------------------------------------------------------------------ UI kit (crisp, drawn at 2x then downsampled)
GOLD = (214, 172, 92)
GOLD_HI = (255, 226, 150)
GOLD_SH = (112, 78, 34)
ENAMEL = (18, 24, 32)
PATINA = (70, 138, 122)
CYAN = (90, 236, 226)
CRIMSON = (212, 52, 44)
PARCH = (236, 222, 190)

class UI:
    """A 2x supersampled RGBA overlay layer."""
    def __init__(self, size=(W, H), ss=2):
        self.ss = ss
        self.im = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def S(self, v):
        return v * self.ss

    def P(self, pts):
        return [(x * self.ss, y * self.ss) for (x, y) in pts]

    def font(self, name, size):
        return font(name, int(size * self.ss))

    def text(self, xy, s, f, fill, anchor="la", shadow=(0, 0, 0, 170), stroke=0, stroke_fill=None, sh_off=2):
        x, y = xy
        if shadow:
            self.d.text((self.S(x + sh_off), self.S(y + sh_off)), s, font=f, fill=shadow, anchor=anchor)
        self.d.text((self.S(x), self.S(y)), s, font=f, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.ss), stroke_fill=stroke_fill)

    def plate(self, box, fill=ENAMEL + (215,), border=GOLD, bw=2.0, notch=10, inner=True):
        """Brass-framed enamel plate with clipped corners (the UI's base shape)."""
        x0, y0, x1, y1 = box
        n = notch
        pts = [(x0 + n, y0), (x1 - n, y0), (x1, y0 + n), (x1, y1 - n), (x1 - n, y1), (x0 + n, y1), (x0, y1 - n), (x0, y0 + n)]
        self.d.polygon(self.P(pts), fill=fill)
        self.d.line(self.P(pts + [pts[0]]), fill=border + (255,), width=int(bw * self.ss), joint="curve")
        if inner:
            m = 4
            ipts = [(x0 + n + m, y0 + m), (x1 - n - m, y0 + m), (x1 - m, y0 + n + m), (x1 - m, y1 - n - m),
                    (x1 - n - m, y1 - m), (x0 + n + m, y1 - m), (x0 + m, y1 - n - m), (x0 + m, y0 + n + m)]
            self.d.line(self.P(ipts + [ipts[0]]), fill=GOLD_SH + (200,), width=int(1 * self.ss))
        for (cx, cy) in [(x0 + n * 0.5, y0 + n * 0.5), (x1 - n * 0.5, y0 + n * 0.5), (x0 + n * 0.5, y1 - n * 0.5), (x1 - n * 0.5, y1 - n * 0.5)]:
            self.rivet(cx, cy, 2.6)

    def rivet(self, x, y, r):
        self.d.ellipse(self.P([(x - r, y - r), (x + r, y + r)]), fill=GOLD_SH + (255,))
        self.d.ellipse(self.P([(x - r * 0.75, y - r * 0.8), (x + r * 0.5, y + r * 0.45)]), fill=GOLD + (255,))
        self.d.ellipse(self.P([(x - r * 0.5, y - r * 0.6), (x - r * 0.05, y - r * 0.15)]), fill=GOLD_HI + (255,))

    def diamond(self, x, y, r, fill, border=GOLD, bw=2.0):
        pts = [(x, y - r), (x + r * 0.72, y), (x, y + r), (x - r * 0.72, y)]
        self.d.polygon(self.P(pts), fill=fill)
        self.d.line(self.P(pts + [pts[0]]), fill=border + (255,), width=int(bw * self.ss))

    def bar(self, box, frac, color, back=(10, 10, 14, 230), label=None, f=None):
        x0, y0, x1, y1 = box
        self.plate((x0 - 6, y0 - 6, x1 + 6, y1 + 6), fill=(12, 14, 18, 230), notch=6, inner=False)
        self.d.rectangle(self.P([(x0, y0), (x1, y1)]), fill=back)
        xf = x0 + (x1 - x0) * frac
        hi = tuple(min(255, int(c * 1.35)) for c in color)
        self.d.rectangle(self.P([(x0, y0), (xf, y1)]), fill=color + (255,))
        self.d.rectangle(self.P([(x0, y0), (xf, y0 + (y1 - y0) * 0.35)]), fill=hi + (255,))
        # segment ticks
        for k in range(1, 10):
            x = x0 + (x1 - x0) * k / 10
            self.d.line(self.P([(x, y0), (x, y1)]), fill=(0, 0, 0, 110), width=int(1 * self.ss))
        if label and f:
            self.text(((x0 + x1) / 2, (y0 + y1) / 2), label, f, (255, 250, 235, 255), anchor="mm", sh_off=1)

    def finish(self):
        return self.im.resize((self.im.size[0] // self.ss, self.im.size[1] // self.ss), Image.LANCZOS)
