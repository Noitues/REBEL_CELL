"""Stencil & spray overlay toolkit (Pillow + numpy only, seeded).

Every mark is built as a float mask, then "sprayed": crisp core, speckled
overspray halo, black stencil shadow, optional glossy drips.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS = "C:/Windows/Fonts/"
IMPACT = FONTS + "impact.ttf"
STENCIL = FONTS + "STENCIL.TTF"
BAHN = FONTS + "bahnschrift.ttf"
COUR = FONTS + "courbd.ttf"

# Palette: hot pink, white, toxic yellow + black stencil shadow
PINK = np.array([255, 36, 136], np.float32) / 255
WHITE = np.array([244, 242, 234], np.float32) / 255
YELLOW = np.array([222, 255, 34], np.float32) / 255
BLACK = np.array([10, 9, 12], np.float32) / 255
PAPER = np.array([232, 226, 210], np.float32) / 255


# ----------------------------------------------------------------- basics
def blur(a, s):
    """Gaussian blur of a 2D float array via FFT (zero padded)."""
    if s <= 0.05:
        return a.astype(np.float32).copy()
    p = int(3 * s) + 2
    ap = np.pad(a.astype(np.float32), p, mode="constant")
    H, W = ap.shape
    F = np.fft.rfft2(ap)
    fy = np.fft.fftfreq(H)[:, None]
    fx = np.fft.rfftfreq(W)[None, :]
    G = np.exp(-2 * (math.pi ** 2) * s * s * (fx * fx + fy * fy))
    out = np.fft.irfft2(F * G, s=ap.shape)
    return out[p:-p, p:-p].astype(np.float32)


def fbm(h, w, rng, scales=(64, 24, 8), weights=(0.55, 0.3, 0.15)):
    """Cheap fractal value noise in 0..1."""
    acc = np.zeros((h, w), np.float32)
    for sc, wt in zip(scales, weights):
        gh, gw = max(2, h // sc + 2), max(2, w // sc + 2)
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC)
        acc += np.asarray(im, np.float32) / 255 * wt
    acc -= acc.min()
    acc /= max(1e-6, acc.max())
    return acc


def to_mask(img_l, ss):
    """Downsample a supersampled L image to a float mask."""
    w, h = img_l.size
    small = img_l.resize((w // ss, h // ss), Image.LANCZOS)
    return np.clip(np.asarray(small, np.float32) / 255, 0, 1)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    xs, ys = max(0, dx), max(0, dy)
    xe, ye = min(w, w + dx), min(h, h + dy)
    out[ys:ye, xs:xe] = a[ys - dy:ye - dy, xs - dx:xe - dx]
    return out


def roughen(img_l, rng, amp=0.18, rad=1.4):
    """Hand-cut stencil edge: blur, add noise, re-threshold (at supersample)."""
    a = np.asarray(img_l, np.float32) / 255
    h, w = a.shape
    n = fbm(h, w, rng, scales=(40, 12), weights=(0.6, 0.4)) - 0.5
    b = blur(a, rad) + n * amp
    return Image.fromarray(((b > 0.5) * 255).astype(np.uint8), "L")


# ----------------------------------------------------------------- layer
class Layer:
    """Local straight-alpha RGBA accumulator in float."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    def over(self, color, alpha):
        alpha = np.clip(alpha, 0, 1).astype(np.float32)
        col = np.broadcast_to(np.asarray(color, np.float32), self.rgb.shape) if np.ndim(color) == 1 else color
        na = alpha + self.a * (1 - alpha)
        safe = np.where(na > 1e-5, na, 1)
        self.rgb = (col * alpha[..., None] + self.rgb * (self.a * (1 - alpha))[..., None]) / safe[..., None]
        self.a = na

    def erase(self, amount):
        self.a = self.a * (1 - np.clip(amount, 0, 1))

    def to_image(self):
        arr = np.dstack([np.clip(self.rgb, 0, 1), np.clip(self.a, 0, 1)[..., None]])
        return Image.fromarray((arr * 255 + 0.5).astype(np.uint8), "RGBA")


def composite(base, layer_img, x, y, angle=0.0):
    """Alpha composite an RGBA image onto base (RGB PIL) centred-anchor at x,y top-left."""
    if angle:
        cx, cy = layer_img.size[0] / 2, layer_img.size[1] / 2
        layer_img = layer_img.rotate(angle, Image.BICUBIC, expand=True)
        x = int(x + cx - layer_img.size[0] / 2)
        y = int(y + cy - layer_img.size[1] / 2)
    base.paste(layer_img, (int(x), int(y)), layer_img)


def darken_under(base, mask_full, amount=0.35, desat=0.4, spread=24):
    """Lightly darken/desaturate the base under an overlay so it reads."""
    m = blur(mask_full, spread)
    m = np.clip(m / max(1e-6, m.max()), 0, 1)[..., None]
    arr = np.asarray(base.convert("RGB"), np.float32) / 255
    g = arr.mean(axis=2, keepdims=True)
    arr = arr * (1 - desat * m) + g * desat * m
    arr = arr * (1 - amount * m)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB")


# ----------------------------------------------------------------- stencil text
def _cut_bridges(gl, bw, slice_frac=None, slice_w=0, ch=""):
    """Cut stencil bridges into one glyph (L image, 255 = ink)."""
    w, h = gl.size
    pad = Image.new("L", (w + 4, h + 4), 0)
    pad.paste(gl, (2, 2))
    a = np.asarray(pad).copy()
    filled = pad.copy()
    ImageDraw.floodfill(filled, (0, 0), 128)
    holes = (np.asarray(filled) == 0)
    ink = a > 127
    out = a.copy()
    # label holes by repeated flood fill
    hole_img = Image.fromarray((holes * 255).astype(np.uint8), "L")
    hv = np.asarray(hole_img).copy()
    comps = []
    while True:
        ys, xs = np.nonzero(hv == 255)
        if len(ys) == 0:
            break
        tmp = Image.fromarray(hv, "L").copy()
        ImageDraw.floodfill(tmp, (int(xs[0]), int(ys[0])), 100)
        t = np.asarray(tmp)
        comp = t == 100
        hv = np.where(comp, 0, t).astype(np.uint8)
        if comp.sum() > 30:
            comps.append(comp)
    rows = np.nonzero(ink.any(axis=1))[0]
    for comp in comps:
        ys, xs = np.nonzero(comp)
        cx = int(xs.mean())
        if ch in "BDPR":
            cx = int(xs.min() - bw * 0.4)  # bridge at the stem, like a real stencil D
        top, bot = ys.min(), ys.max()
        x0, x1 = cx - bw // 2, cx + bw // 2
        out[: top + 1, x0:x1] = 0
        out[bot:, x0:x1] = 0
    if slice_frac is not None and not comps and len(rows):
        yy = int(rows.min() + (rows.max() - rows.min()) * slice_frac)
        out[yy - slice_w // 2: yy + slice_w // 2, :] = 0
    return Image.fromarray(out[2:-2, 2:-2], "L")


def stencil_text(text, size, font=IMPACT, ss=3, tracking=0.04, variation=None,
                 bridge=0.075, slice_frac=0.56, slice_w=0.035, angle=0.0,
                 rng=None, rough=True, pad=0.5, line_gap=0.0, align="left"):
    """Return (mask float array, (pad_px)) for multi-line stencil text."""
    f = ImageFont.truetype(font, int(size * ss))
    if variation:
        f.set_variation_by_name(variation)
    asc, desc = f.getmetrics()
    lines = text.split("\n")
    bw = max(2, int(size * ss * bridge))
    sw = max(2, int(size * ss * slice_w))
    line_imgs = []
    for line in lines:
        glyphs = []
        x = 0
        for ch in line:
            adv = f.getlength(ch)
            if ch != " ":
                g = Image.new("L", (int(adv + size * ss), asc + desc), 0)
                ImageDraw.Draw(g).text((0, 0), ch, font=f, fill=255)
                g = _cut_bridges(g, bw, slice_frac if slice_frac is not None else None, sw, ch)
                glyphs.append((x, g))
            x += adv + tracking * size * ss
        lw = int(x + size * ss)
        li = Image.new("L", (lw, asc + desc), 0)
        for gx, g in glyphs:
            li.paste(Image.new("L", g.size, 255), (int(gx), 0), g)
        bbox = li.getbbox() or (0, 0, 1, 1)
        line_imgs.append(li.crop((bbox[0], 0, bbox[2], asc + desc)))
    lh = int((asc + desc) * (1 + line_gap))
    W = max(li.size[0] for li in line_imgs)
    P = int(size * ss * pad)
    img = Image.new("L", (W + 2 * P, lh * (len(lines) - 1) + asc + desc + 2 * P), 0)
    for i, li in enumerate(line_imgs):
        ox = P + (W - li.size[0]) // 2 if align == "center" else P
        img.paste(li, (ox, P + i * lh))
    bbox = img.getbbox()
    img = img.crop((bbox[0] - P, bbox[1] - P, bbox[2] + P, bbox[3] + P))
    if rough and rng is not None:
        img = roughen(img, rng, amp=0.16, rad=ss * 0.6)
    if angle:
        img = img.rotate(angle, Image.BICUBIC, expand=True)
    # make size divisible by ss
    w, h = img.size
    img = img.crop((0, 0, w - w % ss, h - h % ss))
    return to_mask(img, ss)


# ----------------------------------------------------------------- spraying
def spray(layer, M, color, rng, halo=9.0, halo_amt=0.5, speck=1.0, grain=0.10,
          core_soft=0.55, mottling=0.14, edge_build=0.25, opacity=1.0, sheen=0.0):
    """Spray colour through mask M onto layer: crisp core + speckled overspray."""
    h, w = M.shape
    core = blur(M, core_soft)
    mot = fbm(h, w, rng, scales=(90, 30, 9), weights=(0.5, 0.3, 0.2))
    fine = rng.random((h, w)).astype(np.float32)
    cov = core * (1 - mottling + mottling * mot) * (1 - grain + grain * fine)
    # paint builds up a touch at the stencil edge
    edge = np.clip(core - blur(core, 2.5), 0, 1)
    cov = np.clip(cov + edge * edge_build, 0, 1)
    near = np.clip(blur(M, halo * 0.30) - core, 0, 1)
    far = np.clip(blur(M, halo) - core, 0, 1)
    hf = np.clip(0.65 * near + 0.45 * far, 0, 1) * halo_amt
    mist = (near * 0.30 + far * 0.18) * halo_amt * (0.6 + 0.8 * mot)
    r = rng.random((h, w)).astype(np.float32)
    # fine one-pixel atomised dots, denser right at the stencil edge
    dots = (r < (hf ** 1.1) * 1.3 * speck).astype(np.float32)
    dots *= 0.35 + 0.65 * rng.random((h, w)).astype(np.float32)
    big = (rng.random((h, w)) < far * halo_amt * 0.010 * speck).astype(np.float32)
    big = np.clip(blur(big, 0.8) * 5, 0, 1)
    alpha = np.clip(cov + mist + dots + big, 0, 1) * opacity
    if sheen:
        # semi-gloss paint skin: faint top-left lift, bottom-right fall-off
        hgt = blur(M, 2.2)
        gy, gx = np.gradient(hgt)
        lit = np.clip(-(gx * -0.6 + gy * -0.8) * 5.0, -1, 1)
        col = np.asarray(color, np.float32)
        lift = np.clip(col + 0.22, 0, 1)
        fall = col * 0.72
        cm = np.where(lit[..., None] > 0, col + (lift - col) * lit[..., None] * sheen,
                      col + (fall - col) * (-lit[..., None]) * sheen)
        layer.over(cm, alpha)
        return alpha
    layer.over(color, alpha)
    return alpha


def stencil_shadow(layer, M, rng, dx=5, dy=6, amt=0.82, halo=7):
    S = shift(M, dx, dy)
    spray(layer, S, BLACK, rng, halo=halo, halo_amt=0.45, speck=0.7, grain=0.06,
          core_soft=1.1, mottling=0.12, edge_build=0.0, opacity=amt)


# ----------------------------------------------------------------- drips
def drip_mask(M, rng, n=6, max_len=120, width=(4, 8), ss=4, lengths=None, picks=None,
              min_gap=28, clear=40):
    """Drips hanging off the bottom edges of mask M.

    Returns (mask, list of drip specs) so the same drips can be re-grown for animation.
    """
    h, w = M.shape
    b = (M > 0.5)
    below = np.zeros_like(b)
    below[:-1] = b[1:]
    edge = b & ~below
    ys, xs = np.nonzero(edge)
    specs = []
    if picks is None:
        order = rng.permutation(len(xs))
        chosen = []
        for i in order:
            x, y = xs[i], ys[i]
            if y > h - 10 or M[y + 1:y + clear, max(0, x - 3):x + 4].max(initial=0) > 0.3:
                continue
            if all(abs(x - cx) > min_gap for cx, _ in chosen):
                chosen.append((x, y))
            if len(chosen) >= n:
                break
        for (x, y) in chosen:
            L = max_len * (0.25 + 0.75 * rng.random() ** 1.6)
            wd = rng.uniform(*width)
            wob = rng.uniform(-1, 1)
            specs.append(dict(x=float(x), y=float(y), L=L, w=wd, wob=wob))
    else:
        specs = [dict(s) for s in picks]
    if lengths is not None:
        for s, f in zip(specs, lengths):
            s["L"] = s["L"] * f
    img = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(img)
    for s in specs:
        x, y, L, wd, wob = s["x"], s["y"], s["L"], s["w"], s["wob"]
        if L < 2:
            continue
        steps = max(4, int(L / 2))
        pts_l, pts_r = [], []
        for k in range(steps + 1):
            t = k / steps
            yy = y + t * L
            xx = x + wob * 2.2 * math.sin(t * 3.1) + 0.6 * math.sin(t * 9 + wob * 5)
            ww = wd * (1.0 - 0.38 * t) * 0.5
            pts_l.append(((xx - ww) * ss, yy * ss))
            pts_r.append(((xx + ww) * ss, yy * ss))
        d.polygon(pts_l + pts_r[::-1], fill=255)
        # root meniscus
        rw = wd * 1.25
        d.polygon([((x - rw) * ss, (y - 2) * ss), ((x + rw) * ss, (y - 2) * ss),
                   ((x + wd * 0.3) * ss, (y + wd * 1.4) * ss), ((x - wd * 0.3) * ss, (y + wd * 1.4) * ss)], fill=255)
        # bulb
        bx = x + wob * 2.2 * math.sin(3.1) + 0.6 * math.sin(9 + wob * 5)
        br = wd * 0.62
        by = y + L
        d.ellipse(((bx - br) * ss, (by - br * 1.5) * ss, (bx + br) * ss, (by + br * 0.9) * ss), fill=255)
    return to_mask(img, ss), specs


def spray_drips(layer, D, color, rng, gloss=1.0):
    """Wet, glossy drips: deeper colour, soft sheen on the lit side, tight tip specular."""
    core = blur(D, 0.45)
    col = np.asarray(color, np.float32)
    layer.over(np.clip(col * 0.86, 0, 1), core)
    hgt = blur(D, 1.4)
    gy, gx = np.gradient(hgt)
    nd = (gx * -0.8 + gy * -0.35)
    lit = np.clip(nd * 7.0, 0, 1) * core
    shd = np.clip(-nd * 7.0, 0, 1) * core
    layer.over(col * 0.42, shd * 0.6)
    layer.over(np.clip(col * 0.55 + 0.42, 0, 1), lit * 0.55 * gloss)
    # tight specular only where the paint is thickest (bulbs and roots)
    thick = np.clip((blur(D, 2.6) - 0.62) * 4.0, 0, 1)
    spec = np.clip(lit * thick * 2.2, 0, 1) ** 1.5
    layer.over(np.array([1, 1, 1], np.float32), spec * 0.9 * gloss)


# ----------------------------------------------------------------- freehand
def catmull(pts, n=200):
    pts = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    segs = len(pts) - 3
    per = max(2, n // segs)
    for i in range(segs):
        p0, p1, p2, p3 = [np.array(p, float) for p in pts[i:i + 4]]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(np.array(pts[-2], float))
    return np.array(out)


def freehand_mask(shape, pts, width, rng, ss=3, taper_in=0.06, taper_out=0.22, jitter=1.2, upto=1.0):
    """Spray-can freehand line: pressure ramps, end flick, slight hand jitter."""
    h, w = shape
    length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
    path = catmull(pts, n=max(60, int(length / 1.2)))
    img = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(img)
    N = len(path)
    last = int(N * upto)
    ph = rng.uniform(0, 6.28)
    for i in range(last):
        t = i / max(1, N - 1)
        p = 1.0
        if t < taper_in:
            p = 0.55 + 0.45 * (t / taper_in)
        if t > 1 - taper_out:
            p = max(0.12, (1 - t) / taper_out) ** 0.8
        p *= 0.9 + 0.1 * math.sin(t * 17 + ph)
        r = width * 0.5 * p
        x, y = path[i] + rng.normal(0, jitter * 0.25, 2)
        d.ellipse(((x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss), fill=255)
    return to_mask(img, ss), path


def spray_freehand(layer, M, color, rng, width, opacity=1.0, mist=0.35):
    """Freehand spray is softer than stencil: soft core edge, speckled fringe, light mist."""
    soft = blur(M, width * 0.08)
    return spray(layer, soft, color, rng, halo=width * 0.75, halo_amt=mist, speck=1.6 * 0.6 / max(mist, 0.1),
                 grain=0.12, core_soft=width * 0.06, mottling=0.18, edge_build=0.0, opacity=opacity)


# ----------------------------------------------------------------- icons
def _l(w, h, ss):
    img = Image.new("L", (w * ss, h * ss), 0)
    return img, ImageDraw.Draw(img)


def icon_reticle(size, ss=4, ring=0.12, dot=True, tick=0.30):
    img, d = _l(size, size, ss)
    S = size * ss
    c = S / 2
    R = S * 0.40
    t = S * ring
    d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    d.ellipse((c - R + t, c - R + t, c + R - t, c + R - t), fill=0)
    r2 = S * 0.07
    if dot:
        d.ellipse((c - r2, c - r2, c + r2, c + r2), fill=255)
    tw = S * 0.05
    for (x0, y0, x1, y1) in [(c - tw, 0, c + tw, S * tick), (c - tw, S * (1 - tick), c + tw, S),
                             (0, c - tw, S * tick, c + tw), (S * (1 - tick), c - tw, S, c + tw)]:
        d.rectangle((x0, y0, x1, y1), fill=255)
    bw = S * 0.04
    for a in (45, 135, 225, 315):
        ang = math.radians(a)
        x0, y0 = c + math.cos(ang) * (R - t - 6), c + math.sin(ang) * (R - t - 6)
        x1, y1 = c + math.cos(ang) * (R + 6), c + math.sin(ang) * (R + 6)
        d.line((x0, y0, x1, y1), fill=0, width=int(bw))
    return to_mask(img, ss)


def icon_eye_crossed(w, h, ss=4):
    """Stencil eye, struck through. Two bridges keep the iris island attached."""
    img, d = _l(w, h, ss)
    W, H = w * ss, h * ss
    cx, cy = W / 2, H / 2

    def almond(x0, x1, amp):
        top, bot = [], []
        for k in range(41):
            t = k / 40
            x = x0 + t * (x1 - x0)
            yy = math.sin(t * math.pi) ** 0.85 * amp
            top.append((x, cy - yy))
            bot.append((x, cy + yy))
        return top + bot[::-1]
    d.polygon(almond(W * 0.02, W * 0.98, H * 0.46), fill=255)
    d.polygon(almond(W * 0.17, W * 0.83, H * 0.27), fill=0)
    r = H * 0.25
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    r3 = H * 0.08
    d.ellipse((cx - r * 0.3 - r3, cy - r * 0.35 - r3, cx - r * 0.3 + r3, cy - r * 0.35 + r3), fill=0)
    # slash: black gap then a solid bar
    d.line((W * 0.14, H * 1.0, W * 0.86, H * 0.0), fill=0, width=int(H * 0.30))
    d.line((W * 0.17, H * 0.97, W * 0.83, H * 0.03), fill=255, width=int(H * 0.15))
    return to_mask(img, ss)


def icon_fist(w, h, ss=4):
    """Raised fist, front view: four knuckled fingers, thumb across, wrist. Gaps are the bridges."""
    img, d = _l(w, h, ss)
    W, H = w * ss, h * ss
    g = W * 0.045
    fw = (W * 0.76) / 4
    for i in range(4):
        x0 = W * 0.12 + i * fw
        top = H * (0.06 if i in (1, 2) else 0.10)
        d.rounded_rectangle((x0 + g * 0.5, top, x0 + fw - g * 0.5, H * 0.50), radius=fw * 0.45, fill=255)
    # thumb across the lower fingers, cut free with a black outline
    d.rounded_rectangle((W * 0.06 - g, H * 0.34 - g, W * 0.66 + g, H * 0.47 + g), radius=H * 0.08, fill=0)
    d.rounded_rectangle((W * 0.06, H * 0.34, W * 0.66, H * 0.47), radius=H * 0.065, fill=255)
    # back of the hand
    d.rounded_rectangle((W * 0.12, H * 0.50 + g, W * 0.88, H * 0.70), radius=W * 0.07, fill=255)
    # wrist and forearm
    d.polygon([(W * 0.28, H * 0.70 + g), (W * 0.72, H * 0.70 + g), (W * 0.76, H), (W * 0.24, H)], fill=255)
    return to_mask(img, ss)


def icon_arrow(w, h, ss=4, bridge=True):
    img, d = _l(w, h, ss)
    W, H = w * ss, h * ss
    d.polygon([(0, H * 0.34), (W * 0.60, H * 0.34), (W * 0.60, H * 0.04), (W, H * 0.5),
               (W * 0.60, H * 0.96), (W * 0.60, H * 0.66), (0, H * 0.66)], fill=255)
    if bridge:
        d.rectangle((W * 0.55, 0, W * 0.55 + W * 0.04, H), fill=0)
        d.rectangle((W * 0.24, 0, W * 0.24 + W * 0.04, H), fill=0)
    return to_mask(img, ss)


def buff_mask(w, h, rng, ss=2, inset=14):
    """Rough rectangular buff (black-out) patch built from overlapping sweeps."""
    img, d = _l(w, h, ss)
    d.rectangle((inset * 2 * ss, inset * 2 * ss, (w - inset * 2) * ss, (h - inset * 2) * ss), fill=255)
    y = inset
    while y < h - inset:
        bh = rng.uniform(26, 44)
        x0 = inset + rng.uniform(-8, 10)
        x1 = w - inset + rng.uniform(-10, 8)
        d.rounded_rectangle((x0 * ss, y * ss, x1 * ss, min(h - inset, y + bh) * ss), radius=bh * ss * 0.5, fill=255)
        y += bh * 0.62
    return blur(to_mask(img, ss), 2.0)
