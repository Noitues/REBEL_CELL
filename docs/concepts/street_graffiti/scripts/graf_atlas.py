"""Procedural street-graffiti wall atlas (seeded, PIL only). Runs outside Blender.

python graf_atlas.py <outdir> [seed] [W] [H] [density]
Writes <outdir>/graf_albedo.png (RGBA: paint colour + coverage alpha) and graf_glow.png (L: fluorescent paint strength,
0 for black outlines / posters, 1 for fluoro fills). The tile wraps in both axes (every element is pasted with wrap), so
the Blender overlay can box-project it over any facade.

Layers, oldest first: buffed patches and faded old pieces -> wheat-paste posters (kana / kanji) -> big bubble pieces
(extrude, black + light outlines, two-colour gradient fill, highlights, drips, overspray halo) -> chrome throw-ups ->
characters (skull masks) -> tags (hand script) over everything.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
FW = r"C:/Windows/Fonts/"
F_HEAVY = [os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"), FW + "ariblk.ttf", FW + "seguibl.ttf", FW + "SHOWG.TTF"]
F_TAG = [FW + "Inkfree.ttf", FW + "segoesc.ttf", FW + "segoescb.ttf", FW + "segoepr.ttf", FW + "segoeprb.ttf"]
F_JP = FW + "YuGothB.ttc"

# fluoro spray palette (sRGB); the Cell's own tokens lead (CELL_PINK, CELL_ACID, NET_CYAN, NEON_VIOLET)
FLUO = [(255, 61, 168), (212, 255, 0), (92, 225, 255), (176, 77, 255), (255, 140, 26), (255, 226, 0), (255, 40, 90),
        (60, 255, 170), (255, 90, 230), (40, 140, 255)]
WORDS = ["REBEL", "CELL", "JACKIN", "NETRUN", "HACK", "RIOT", "GHOST", "FREENET", "BURNIT", "NOCORP", "ZERO", "VANDAL",
         "KAOS", "GLITCH", "R3BEL", "SPLICE", "OVERRIDE", "DEADNET", "CREW", "BREACH"]
JP_WORDS = ["反乱", "細胞", "自由", "電脳", "幽霊", "ハック", "ネット", "暴動", "侵入", "ゼロ"]
TAGS = ["kz", "Rx!", "sn0w", "VEX", "mira", "D3K", "oni", "TAKO", "zer0", "nyx", "BLK", "jinx", "RUST", "kage", "pix",
        "SKOR", "ume", "volt", "hex", "rebel", "cell", "NEKO", "LUX", "dmn", "ky0", "ghst"]


class Wall:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.glow = Image.new("L", (W, H), 0)

    def put(self, im, glow, x, y):
        """alpha-composite an element (and its glow, masked by the element's alpha) with wrap in both axes."""
        x, y = int(x) % self.W, int(y) % self.H
        a = im.getchannel("A")
        for dx in (0, -self.W):
            for dy in (0, -self.H):
                if x + dx + im.width <= 0 or y + dy + im.height <= 0:
                    continue
                self.rgba.alpha_composite(im, (x + dx, y + dy)) if (x + dx >= 0 and y + dy >= 0) else self._paste_neg(im, x + dx, y + dy)
                # glow: replace under the element's alpha (new paint covers old glow)
                cur = self.glow.crop((x + dx, y + dy, x + dx + im.width, y + dy + im.height))
                g = glow if glow is not None else Image.new("L", im.size, 0)
                self.glow.paste(Image.composite(g, cur, a), (x + dx, y + dy))

    def _paste_neg(self, im, x, y):
        cx, cy = max(0, -x), max(0, -y)
        sub = im.crop((cx, cy, im.width, im.height))
        self.rgba.alpha_composite(sub, (x + cx, y + cy))


def font(path, size):
    return ImageFont.truetype(path, size)


def word_mask(rng, word, size, wild=0.0):
    """Letters drawn one by one with jitter (rotation, rise, scale, overlap) -> L mask, bubble-rounded."""
    fp = rng.choice(F_HEAVY[:3])
    pad = size
    letters = []
    for ch in word:
        s = int(size * rng.uniform(0.85, 1.15) * (1.0 + 0.15 * wild * rng.uniform(-1, 1)))
        f = font(fp, s)
        bb = f.getbbox(ch)
        w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
        im = Image.new("L", (w + 40, h + 40), 0)
        ImageDraw.Draw(im).text((20 - bb[0] + 10, 20 - bb[1] + 10), ch, font=f, fill=255)
        im = im.rotate(rng.uniform(-14, 14) * (0.5 + wild), resample=Image.BICUBIC, expand=True)
        letters.append(im)
    tw = sum(int(l.width * 0.80) for l in letters) + pad * 2
    th = max(l.height for l in letters) + pad * 2
    m = Image.new("L", (tw, th), 0)
    x = pad
    for i, l in enumerate(letters):
        y = pad + (th - 2 * pad - l.height) // 2 + int(math.sin(i * 1.3 + rng.random() * 6) * size * 0.10 * (1 + wild))
        m.paste(ImageChops.lighter(m.crop((x, y, x + l.width, y + l.height)), l), (x, y))
        x += int(l.width * rng.uniform(0.58, 0.72))
    # bubble: blur + threshold rounds every corner; wild pieces get arrows / spurs
    r = max(2, size // 14)
    m = m.filter(ImageFilter.GaussianBlur(r)).point(lambda v: 255 if v > 110 else 0)
    if wild > 0.4:
        d = ImageDraw.Draw(m)
        for _ in range(int(3 + 4 * wild)):
            bb = m.getbbox()
            x0 = rng.uniform(bb[0], bb[2])
            y0 = rng.choice([bb[1] + size * 0.2, bb[3] - size * 0.2])
            ang = rng.uniform(-0.6, 0.6) + (0 if rng.random() < 0.5 else math.pi)
            L = size * rng.uniform(0.4, 0.8)
            tip = (x0 + math.cos(ang) * L, y0 - abs(math.sin(ang)) * L * (1 if y0 < (bb[1] + bb[3]) / 2 else -1))
            w = size * 0.12
            d.polygon([(x0 - w, y0), (x0 + w, y0), tip], fill=255)
    return m.crop(m.getbbox()) if m.getbbox() else m


def dilate(m, n):
    n = max(1, int(n))   # round dilation: blur then a low threshold (MaxFilter is far too slow at this size)
    return m.filter(ImageFilter.GaussianBlur(n * 0.55)).point(lambda v: 255 if v > 14 else 0)


def grad_fill(size, c0, c1, rng, bands=True):
    w, h = size
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    t = np.clip(t + 0.15 * np.sin(np.linspace(0, rng.uniform(2, 6), w, dtype=np.float32))[None, :], 0, 1)
    if bands:   # fade band: a third colour stripe through the middle (classic piece fill)
        t = t ** rng.uniform(0.7, 1.4)
    a, b = np.array(c0, np.float32), np.array(c1, np.float32)
    rgb = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8), "RGB")


def drips(mask, rng, n, maxlen, w):
    """vertical paint drips from the bottom edge of a mask (returns L mask of drips only)."""
    a = np.asarray(mask) > 0
    H, W = a.shape
    out = Image.new("L", mask.size, 0)
    d = ImageDraw.Draw(out)
    cols = [c for c in range(0, W, 3) if a[:, c].any()]
    for _ in range(n if cols else 0):
        c = rng.choice(cols)
        y = int(np.nonzero(a[:, c])[0].max())
        L = rng.uniform(0.2, 1.0) * maxlen
        ww = max(1, w * rng.uniform(0.5, 1.1))
        d.line([(c, y - 2), (c, min(H - 1, y + L))], fill=255, width=int(ww))
        d.ellipse([c - ww * 0.6, y + L - ww * 0.4, c + ww * 0.6, y + L + ww * 0.8], fill=255)
    return out


def piece(rng, size, wild, old=False):
    word = rng.choice(WORDS)
    m = word_mask(rng, word, size, wild)
    o1 = max(3, size // 12)       # light inner outline
    o2 = max(5, size // 7)        # black outer outline
    ext = max(4, size // 6)       # 3D extrude
    pad = o2 + ext + size // 2
    W, H = m.width + 2 * pad, m.height + 2 * pad + size
    base = Image.new("L", (W, H), 0)
    base.paste(m, (pad, pad))
    c0, c1 = rng.sample(FLUO, 2)
    ext_col = tuple(int(v * 0.35) for v in rng.choice(FLUO))
    light = rng.choice([(250, 250, 245), rng.choice(FLUO)])
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("L", (W, H), 0)
    # overspray halo
    halo = dilate(base, o2 * 2).filter(ImageFilter.GaussianBlur(size * 0.25))
    hc = rng.choice(FLUO)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), hc).split(), halo.point(lambda v: int(v * 0.45)))))
    glow.paste(halo.point(lambda v: int(v * 0.5)), (0, 0))
    # extrude: stacked offset copies (down-right), black outline round all of it
    ex = Image.new("L", (W, H), 0)
    dx, dy = rng.choice([(1, 1), (-1, 1), (1, 0.6)])
    b1 = dilate(base, o1)
    for k in range(0, ext, 2):
        ex = ImageChops.lighter(ex, ImageChops.offset(b1, int(dx * k), int(dy * k)))
    outer = dilate(ImageChops.lighter(ex, dilate(base, o1)), o2 - o1)
    dr = drips(base, rng, int(3 + 6 * rng.random()), size * 0.9, size * 0.07)
    outer = ImageChops.lighter(outer, dilate(dr, 2))
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (8, 6, 12)).split(), outer)))
    glow.paste(0, mask=outer)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), ext_col).split(), ex)))
    li = dilate(base, o1)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), light).split(), li)))
    glow.paste(110 if light[0] > 240 and light[2] > 240 else 230, mask=li)
    fill = grad_fill((W, H), c0, c1, rng)
    fm = ImageChops.lighter(base, dr)
    im.alpha_composite(Image.merge("RGBA", (*fill.split(), fm)))
    glow.paste(255, mask=fm)
    # highlights: white dots / short cut-lines along the upper-left of each letter
    hl = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hl)
    a = np.asarray(base) > 0
    ys, xs = np.nonzero(a)
    for _ in range(int(10 + 25 * rng.random())):
        if len(xs) == 0:
            break
        i = rng.randrange(len(xs))
        r = size * rng.uniform(0.02, 0.05)
        hd.ellipse([xs[i] - r, ys[i] - r, xs[i] + r, ys[i] + r], fill=255)
    hl = ImageChops.multiply(hl, base)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (255, 255, 255)).split(), hl)))
    if old:   # faded, sun-bleached: lower alpha, desaturated
        rgb = im.convert("RGB")
        rgb = Image.blend(rgb, rgb.convert("L").convert("RGB"), 0.55)
        im = Image.merge("RGBA", (*rgb.split(), im.getchannel("A").point(lambda v: int(v * 0.55))))
        glow = glow.point(lambda v: int(v * 0.25))
    return im, glow


def throwup(rng, size):
    """quick two-colour chrome throw-up: silver fill, black outline, one fluoro shadow."""
    word = rng.choice(WORDS[:12] + TAGS[:8]).upper()[:5]
    m = word_mask(rng, word, size, 0.1)
    o = max(4, size // 9)
    pad = o * 3 + 4
    W, H = m.width + 2 * pad, m.height + 2 * pad
    base = Image.new("L", (W, H), 0)
    base.paste(m, (pad, pad))
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("L", (W, H), 0)
    sh = ImageChops.offset(dilate(base, o), o, o)
    sc = rng.choice(FLUO)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), sc).split(), sh)))
    glow.paste(255, mask=sh)
    ol = dilate(base, o)
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (6, 6, 8)).split(), ol)))
    glow.paste(0, mask=ol)
    chrome = grad_fill((W, H), (235, 238, 245), (120, 125, 140), rng, bands=False) if rng.random() < 0.7 else \
        grad_fill((W, H), rng.choice(FLUO), (250, 250, 250), rng, bands=False)
    im.alpha_composite(Image.merge("RGBA", (*chrome.split(), base)))
    glow.paste(70, mask=base)
    return im, glow


def tag(rng, size):
    s = rng.choice(TAGS)
    f = font(rng.choice(F_TAG), size)
    bb = f.getbbox(s)
    W, H = bb[2] - bb[0] + size, bb[3] - bb[1] + size * 2
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    sw = max(1, size // 22)
    d.text((size // 2 - bb[0], size // 2 - bb[1]), s, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    if rng.random() < 0.6:   # underline swoosh / crown
        y = size // 2 + bb[3] - bb[1] + size * 0.12
        pts = [(size * 0.3 + i * (W - size * 0.6) / 8, y + math.sin(i * 0.9 + rng.random()) * size * 0.08) for i in range(9)]
        d.line(pts, fill=255, width=max(2, size // 14))
    if rng.random() < 0.5:
        m = ImageChops.lighter(m, drips(m, rng, 4, size * 0.7, max(2, size // 18)))
    m = m.rotate(rng.uniform(-12, 8), resample=Image.BICUBIC, expand=True)
    col = rng.choice(FLUO + [(250, 250, 250), (20, 20, 24), (20, 20, 24)])
    im = Image.merge("RGBA", (*Image.new("RGB", m.size, col).split(), m))
    gv = 0 if sum(col) < 100 else (90 if min(col) > 230 else 255)
    return im, Image.new("L", m.size, gv)


def jp_tag(rng, size):
    """kana / kanji tag: heavy gothic, skewed and stretched like a fast marker hand, one colour."""
    s = rng.choice(JP_WORDS + ["ハク", "ネコ", "鬼", "影", "零"])
    f = font(F_JP, size)
    bb = f.getbbox(s)
    W, H = bb[2] - bb[0] + size, bb[3] - bb[1] + size
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((size // 2 - bb[0], size // 2 - bb[1]), s, font=f, fill=255, stroke_width=max(1, size // 30), stroke_fill=255)
    sk = rng.uniform(-0.35, 0.1)
    m = m.transform((int(W * 1.3), H), Image.AFFINE, (1, sk, -abs(sk) * H if sk < 0 else 0, 0, 1, 0), resample=Image.BICUBIC)
    m = m.resize((int(m.width * rng.uniform(1.0, 1.5)), m.height), Image.BICUBIC)
    if rng.random() < 0.5:
        m = ImageChops.lighter(m, drips(m, rng, 3, size * 0.6, max(2, size // 16)))
    col = rng.choice(FLUO + [(250, 250, 250), (20, 20, 24)])
    im = Image.merge("RGBA", (*Image.new("RGB", m.size, col).split(), m))
    return im, Image.new("L", m.size, 0 if sum(col) < 100 else 220)


def blockbuster(rng, size):
    """heaven-spot roller letters: huge square block capitals, flat fill + thick outline, roller-rough edges."""
    word = rng.choice(["REBEL", "CELL", "RIOT", "HACK", "KAOS", "ZERO", "GHOST", "VEX", "ONI", "BLK", "NYX", "JINX"])
    f = font(F_HEAVY[1], size)   # Arial Black: square, heavy
    bb = f.getbbox(word)
    pad = size // 3
    W, H = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), word, font=f, fill=255)
    m = m.resize((int(W * rng.uniform(1.0, 1.25)), int(H * rng.uniform(1.0, 1.3))), Image.BICUBIC)
    W, H = m.size
    nr = np.random.default_rng(rng.randrange(1 << 30))
    rough = Image.fromarray((nr.random((H // 6 + 1, W // 6 + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    ol = dilate(m, max(6, size // 10))
    ol = ImageChops.multiply(ol, rough.point(lambda v: 255 if v > 40 else 0))
    fill_m = ImageChops.multiply(m, rough.point(lambda v: 255 if v > 25 else 120))
    fc = rng.choice(FLUO + [(245, 245, 240), (245, 245, 240)])
    oc = rng.choice([(8, 8, 10), (8, 8, 10), rng.choice(FLUO)])
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), oc).split(), ol)))
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), fc).split(), fill_m)))
    glow = Image.new("L", (W, H), 0)
    glow.paste(255 if sum(oc) > 100 else 0, mask=ol)
    glow.paste(255 if max(fc) - min(fc) > 60 else 120, mask=fill_m)
    return im, glow


def poster(rng, w, h):
    """wheat-paste poster: paper rectangle, torn edge, kanji headline, a halftone face block; no glow."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    paper = rng.choice([(235, 230, 215), (250, 220, 40), (240, 70, 120), (30, 30, 34), (90, 220, 255)])
    ink = (20, 18, 22) if sum(paper) > 300 else (245, 240, 230)
    pts = []
    for i in range(24):   # torn outline
        t = i / 24
        if t < 0.25:
            p = (t * 4 * w, 0)
        elif t < 0.5:
            p = (w, (t - 0.25) * 4 * h)
        elif t < 0.75:
            p = (w - (t - 0.5) * 4 * w, h)
        else:
            p = (0, h - (t - 0.75) * 4 * h)
        pts.append((min(w - 1, max(0, p[0] + rng.uniform(-6, 6))), min(h - 1, max(0, p[1] + rng.uniform(-6, 6)))))
    d.polygon(pts, fill=paper + (235,))
    f = font(F_JP, int(min(w, h) * 0.32))
    s = rng.choice(JP_WORDS)
    if rng.random() < 0.5:   # vertical kanji column
        y = h * 0.06
        for ch in s:
            d.text((w * 0.08, y), ch, font=f, fill=ink + (255,))
            y += f.size * 1.05
        d.rectangle([w * 0.55, h * 0.1, w * 0.92, h * 0.9], fill=tuple(int(v * 0.6) for v in paper) + (255,))
    else:
        d.text((w * 0.06, h * 0.05), s, font=f, fill=ink + (255,))
        d.rectangle([w * 0.06, h * 0.5, w * 0.94, h * 0.92], fill=tuple(int(v * 0.6) for v in paper) + (255,))
    return im, None


def skull(rng, size):
    """character: a rounded skull / gas-mask face with glowing sockets, black outline."""
    W = H = int(size * 1.6)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    cx, cy = W / 2, H / 2
    d.ellipse([cx - size * 0.55, cy - size * 0.62, cx + size * 0.55, cy + size * 0.35], fill=255)
    d.rounded_rectangle([cx - size * 0.32, cy + 0.1 * size, cx + size * 0.32, cy + size * 0.6], radius=size * 0.1, fill=255)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("L", (W, H), 0)
    ol = dilate(m, max(3, size // 14))
    im.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (6, 6, 8)).split(), ol)))
    c0, c1 = rng.sample(FLUO, 2)
    im.alpha_composite(Image.merge("RGBA", (*grad_fill((W, H), c0, c1, rng).split(), m)))
    glow.paste(255, mask=m)
    d2 = ImageDraw.Draw(im)
    eye = rng.choice(FLUO)
    for sx in (-1, 1):
        e = [cx + sx * size * 0.24 - size * 0.16, cy - size * 0.2, cx + sx * size * 0.24 + size * 0.16, cy + size * 0.08]
        d2.ellipse(e, fill=(6, 6, 8, 255))
        d2.ellipse([e[0] + size * 0.07, e[1] + size * 0.07, e[2] - size * 0.07, e[3] - size * 0.07], fill=eye + (255,))
    for i in range(5):   # teeth
        x = cx - size * 0.25 + i * size * 0.125
        d2.line([(x, cy + size * 0.28), (x, cy + size * 0.56)], fill=(6, 6, 8, 255), width=max(2, size // 30))
    return im, glow


def build(seed=7, W=4096, H=2048, density=1.0):
    rng = random.Random(seed)
    wall = Wall(W, H)
    area = W * H / (4096 * 2048) * density
    # 1. buffed patches (grey / off-colour paint-outs) + faded old pieces
    for _ in range(int(14 * area)):
        w, h = rng.randint(200, 900), rng.randint(120, 500)
        c = rng.choice([(70, 70, 76), (90, 84, 80), (50, 56, 70), (110, 60, 80)])
        p = Image.new("RGBA", (w, h), c + (int(255 * rng.uniform(0.45, 0.8)),))
        wall.put(p, None, rng.randrange(W), rng.randrange(H))
    for _ in range(int(10 * area)):
        im, g = piece(rng, rng.randint(140, 260), rng.random(), old=True)
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    # 2. posters in clusters
    for _ in range(int(9 * area)):
        x0, y0 = rng.randrange(W), rng.randrange(H)
        pw, ph = rng.randint(90, 170), rng.randint(130, 240)
        for i in range(rng.randint(2, 6)):
            im, g = poster(rng, pw, ph)
            wall.put(im, g, x0 + i * (pw + rng.randint(-10, 6)), y0 + rng.randint(-8, 8))
    # 3. big pieces on a loose grid so they cover most of the wall
    nx, ny = max(1, int(5 * W / 4096)), max(1, int(4 * H / 2048))
    cells = [(i, j) for i in range(nx) for j in range(ny)]
    rng.shuffle(cells)
    for (i, j) in cells[:int(len(cells) * min(1.0, 0.85 * density))]:
        im, g = piece(rng, rng.randint(170, 300), rng.random())
        x = (i + rng.uniform(-0.2, 0.3)) * W / nx
        y = (j + rng.uniform(-0.2, 0.3)) * H / ny
        wall.put(im, g, x - im.width * 0.2, y - im.height * 0.2)
    # 4. chrome throw-ups, 5. characters
    for _ in range(int(16 * area)):
        im, g = throwup(rng, rng.randint(90, 170))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    for _ in range(int(5 * area)):
        im, g = skull(rng, rng.randint(140, 260))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    # 6. tags over everything (about a third in kana / kanji)
    for _ in range(int(150 * area)):
        im, g = (jp_tag if rng.random() < 0.33 else tag)(rng, rng.randint(40, 120))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    weather(wall, rng)
    return wall


def build_heaven(seed=11, W=4096, H=2048, density=1.0):
    """the heaven layer: sparse blockbusters and big roller tags on bare wall (most of the tile stays empty)."""
    rng = random.Random(seed)
    wall = Wall(W, H)
    area = W * H / (4096 * 2048) * density
    for _ in range(int(6 * area)):
        im, g = blockbuster(rng, rng.randint(260, 460))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    for _ in range(int(14 * area)):
        im, g = (jp_tag if rng.random() < 0.4 else tag)(rng, rng.randint(120, 260))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    for _ in range(int(6 * area)):
        im, g = throwup(rng, rng.randint(160, 260))
        wall.put(im, g, rng.randrange(W), rng.randrange(H))
    weather(wall, rng)
    return wall


def weather(wall, rng):
    """wear: patchy paint loss (low-frequency noise), spray speckle (high-frequency), a little grime darkening.
    Seeded numpy noise, wraps (built by tiling a small random field and upsampling)."""
    W, H = wall.W, wall.H
    nr = np.random.default_rng(rng.randrange(1 << 30))

    def field(cells, blur):
        f = Image.fromarray((nr.random((cells[1], cells[0])) * 255).astype(np.uint8), "L")
        f = f.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(f, np.float32) / 255
    patch = field((W // 96, H // 96), 6)
    loss = 0.45 + 0.55 * np.clip((patch - 0.20) * 4.0, 0.0, 1.0)   # 1 = paint intact; worn patches fade, never vanish
    speck = nr.random((H, W)).astype(np.float32)
    a = np.asarray(wall.rgba, np.float32)
    k = loss * (0.82 + 0.18 * (speck > 0.08))
    a[..., 3] *= k
    grime = 0.80 + 0.20 * field((W // 24, H // 24), 2)
    a[..., :3] *= grime[..., None]
    wall.rgba = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    g = np.asarray(wall.glow, np.float32) * k
    wall.glow = Image.fromarray(g.clip(0, 255).astype(np.uint8), "L")


SIGN_WORDS = ["カラオケ", "ラーメン", "居酒屋", "電脳館", "質屋", "薬局", "酒場", "ホテル", "漫画", "麻雀", "ゲーム", "占い", "寿司",
              "中古", "修理", "焼肉", "書店", "喫茶", "古着", "電気"]
SIGN_STYLES = [((250, 250, 245), (220, 20, 40)), ((255, 220, 0), (20, 20, 24)), ((220, 20, 40), (255, 255, 255)),
               ((30, 200, 255), (10, 10, 30)), ((18, 14, 26), (255, 61, 168)), ((18, 14, 26), (92, 225, 255)),
               ((255, 140, 26), (20, 10, 10)), ((18, 14, 26), (212, 255, 0))]


def build_signs(seed=3, cols=8, rows=2, cw=256, ch=1024):
    """Tokyo vertical shop signs: one per cell (cw x ch), lit box face + vertical kana / kanji + a border; emission atlas."""
    rng = random.Random(seed)
    im = Image.new("RGB", (cols * cw, rows * ch), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * cw, r * ch
            bg, fg = SIGN_STYLES[(r * cols + c) % len(SIGN_STYLES)]
            d.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=bg)
            d.rectangle([x0 + 10, y0 + 10, x0 + cw - 11, y0 + ch - 11], outline=fg, width=8)
            s = rng.choice(SIGN_WORDS)
            fs = min(int(cw * 0.66), int((ch - 80) / max(1, len(s)) * 0.9))
            f = font(F_JP, fs)
            y = y0 + (ch - len(s) * fs * 1.05) / 2
            for chh in s.replace("ー", "｜"):   # vertical writing: the long-vowel bar stands up
                bb = f.getbbox(chh)
                d.text((x0 + (cw - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1] * 0.5), chh, font=f, fill=fg)
                y += fs * 1.05
    return im


def main():
    out = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
    H = int(sys.argv[4]) if len(sys.argv) > 4 else 2048
    dens = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    os.makedirs(out, exist_ok=True)
    for name, fn, sd in (("graf", build, seed), ("heaven", build_heaven, seed + 4)):
        w = fn(sd, W, H, dens)
        w.rgba.save(os.path.join(out, name + "_albedo.png"))
        w.glow.save(os.path.join(out, name + "_glow.png"))
        a = np.asarray(w.rgba.getchannel("A"), np.float32) / 255
        print("atlas", name, out, w.rgba.size, "coverage %.2f" % float((a > 0.5).mean()))
    build_signs(seed).save(os.path.join(out, "signs.png"))


if __name__ == "__main__":
    main()
