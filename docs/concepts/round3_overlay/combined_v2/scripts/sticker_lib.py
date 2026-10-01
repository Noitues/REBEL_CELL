"""Die-cut vinyl sticker toolkit for combined_v2 (copied from o_c_vinyl_sticker: purer white border, stronger cut line).

Everything is built at SS x resolution and downsampled on placement for clean edges.
Units passed to the public functions are final (1x) pixels unless noted.
"""
import math
import random
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

ROOT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
FONT_DIR = ROOT + r"\assets\fonts"
ANTON = FONT_DIR + r"\Anton-Regular.ttf"
MARKER = FONT_DIR + r"\PermanentMarker-Regular.ttf"
PLEX = FONT_DIR + r"\IBMPlexSansCondensed-Medium.ttf"
MONO = FONT_DIR + r"\ShareTechMono-Regular.ttf"

SS = 2

# Overlay palette (kept deliberately small)
VINYL = (246, 243, 236)     # die-cut white
INK = (20, 17, 24)          # printed black
INK_DEEP = (9, 8, 12)       # extrude
YELLOW = (255, 222, 30)     # signal yellow
YELLOW_LO = (255, 186, 18)
CORAL = (255, 70, 86)       # threat / flag accent
CORAL_LO = (214, 38, 64)
KRAFT = (182, 142, 92)
TEAL = (52, 212, 206)
PEN_Y = (255, 228, 46)      # paint pen yellow
PEN_W = (250, 248, 242)     # paint pen white
BACK = (224, 221, 214)      # sticker back (adhesive side)


# ------------------------------------------------------------------ mask helpers
def dilate(m, r):
    if r <= 0:
        return m
    b = m.filter(ImageFilter.GaussianBlur(r / 2.0))
    return b.point(lambda v: 255 if v > 6 else 0)


def erode(m, r):
    if r <= 0:
        return m
    return ImageOps.invert(dilate(ImageOps.invert(m), r))


def shift(m, dx, dy):
    o = Image.new(m.mode, m.size, 0)
    o.paste(m, (int(round(dx)), int(round(dy))))
    return o


def mul(a, b):
    return ImageChops.multiply(a, b)


def scale_mask(m, k):
    return m.point(lambda v: int(v * k))


def solid(size, color, mask=None):
    im = Image.new("RGBA", size, color + (255,) if len(color) == 3 else color)
    if mask is not None:
        im.putalpha(mask)
    return im


def over(base, color, mask):
    """Composite a flat colour through an L mask onto RGBA base (in place-ish)."""
    layer = Image.new("RGBA", base.size, tuple(color[:3]) + (0,))
    layer.putalpha(mask)
    return Image.alpha_composite(base, layer)


def grad_field(w, h, fn, n=64):
    """Smooth L field: fn(u,v)->0..1 sampled on n x n grid and resized (fine for smooth fns)."""
    small = Image.new("L", (n, n))
    px = small.load()
    for y in range(n):
        for x in range(n):
            px[x, y] = int(max(0.0, min(1.0, fn(x / (n - 1), y / (n - 1)))) * 255)
    return small.resize((w, h), Image.BILINEAR)


def diag(w, h, angle_deg):
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    pr = [x * w * ca + y * h * sa for x in (0, 1) for y in (0, 1)]
    mn, mx = min(pr), max(pr)
    return grad_field(w, h, lambda u, v: (u * w * ca + v * h * sa - mn) / (mx - mn))


def band_lut(center, width, peak=1.0):
    return [int(255 * peak * math.exp(-(((i / 255.0) - center) / width) ** 2)) for i in range(256)]


# ------------------------------------------------------------------ textures
def holo_tex(w, h, seed=1, phase=0.0, sat=0.55):
    rng = random.Random(seed)
    sw, sh = max(4, w // 20), max(4, h // 20)
    small = Image.new("RGB", (sw, sh))
    px = small.load()
    a1, a2, a3 = rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    for y in range(sh):
        for x in range(sw):
            u, v = x / sw, y / sh
            hue = (0.85 * u + 0.55 * v + 0.10 * math.sin(7 * u + a1) + 0.08 * math.sin(6 * v + 3 * u + a2) + phase) % 1.0
            val = 0.93 + 0.07 * math.sin(9 * (u - v) + a3 + phase * 6.28)
            r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            # pull toward silver for a metallic base
            px[x, y] = (int((r * 0.78 + 0.20) * 255), int((g * 0.78 + 0.20) * 255), int((b * 0.78 + 0.22) * 255))
    tex = small.resize((w, h), Image.BICUBIC).convert("RGBA")
    # fine diffraction grating lines
    lines = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(lines)
    step = 5 * SS
    for i in range(-h, w + h, step):
        d.line([(i, 0), (i + h * 0.6, h)], fill=46, width=1)
    tex = over(tex, (255, 255, 255), lines)
    # sparkles
    sp = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sp)
    for _ in range(int(w * h / (900 * SS * SS))):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(0.6, 1.6) * SS
        d.ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(120, 230))
    return over(tex, (255, 255, 255), sp)


def kraft_tex(w, h, seed=3):
    rng = random.Random(seed)
    base = Image.new("RGBA", (w, h), KRAFT + (255,))
    n = Image.effect_noise((w // 2 + 1, h // 2 + 1), 28).resize((w, h), Image.BICUBIC)
    dark = n.point(lambda v: max(0, (128 - v)) * 1)
    light = n.point(lambda v: max(0, (v - 128)) * 1)
    base = over(base, (110, 80, 45), dark)
    base = over(base, (226, 196, 150), light)
    f = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(f)
    for _ in range(int(w * h / (260 * SS * SS))):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.uniform(0, math.pi)
        l = rng.uniform(3, 10) * SS
        d.line([(x, y), (x + math.cos(a) * l, y + math.sin(a) * l)], fill=rng.randint(30, 80), width=1)
    return over(base, (95, 66, 36), f)


def vgrad_tex(w, h, top, bot):
    g = grad_field(w, h, lambda u, v: v)
    a = Image.new("RGBA", (w, h), top + (255,))
    return over(a, bot, g)


# ------------------------------------------------------------------ lettering
def lettering(lines, size, fills, key_w=5, extrude=7, seed=7, jitter=4.0, track=-1,
              line_gap=0.98, font_path=ANTON, pad=90, holo_seed=11, holo_phase=0.0,
              ext_color=INK_DEEP, bevel=True):
    """Chunky die-cut-ready lettering. fills: list per line of 'holo' | (r,g,b) | ('grad',top,bot)."""
    S = SS
    rng = random.Random(seed)
    font = ImageFont.truetype(font_path, int(size * S))
    asc, desc = font.getmetrics()
    kw = int(key_w * S)
    m = kw + 12 * S
    line_layers = []
    for li, text in enumerate(lines):
        glyphs = []
        x = 0
        for ch in text:
            adv = font.getlength(ch)
            if ch == " ":
                x += adv
                continue
            bw, bh = int(adv + 2 * m), int(asc + desc + 2 * m)
            fm = Image.new("L", (bw, bh), 0)
            km = Image.new("L", (bw, bh), 0)
            ImageDraw.Draw(fm).text((m, m + asc), ch, font=font, fill=255, anchor="ls")
            ImageDraw.Draw(km).text((m, m + asc), ch, font=font, fill=255, anchor="ls",
                                    stroke_width=kw, stroke_fill=255)
            ang = rng.uniform(-jitter, jitter)
            dy = rng.uniform(-0.03, 0.03) * size * S
            fm = fm.rotate(ang, Image.BICUBIC)
            km = km.rotate(ang, Image.BICUBIC)
            glyphs.append((fm, km, x - m, dy - m))
            x += adv + track * S
        lw = int(x - track * S) + 2 * m
        lh = int(asc + desc + 2 * m)
        line_layers.append((glyphs, lw, lh))
    W = max(l[1] for l in line_layers)
    lh0 = int((asc + desc) * line_gap)
    H = lh0 * (len(lines) - 1) + line_layers[-1][2]
    P = int(pad * S)
    CW, CH = W + 2 * P, H + 2 * P
    fill_masks = []
    key_all = Image.new("L", (CW, CH), 0)
    for li, (glyphs, lw, lh) in enumerate(line_layers):
        ox = P + (W - lw) // 2 + m
        oy = P + li * lh0 + m
        fmask = Image.new("L", (CW, CH), 0)
        for fm, km, gx, gy in glyphs:
            t = Image.new("L", (CW, CH), 0)
            t.paste(fm, (int(ox + gx), int(oy + gy)))
            fmask = ImageChops.lighter(fmask, t)
            t = Image.new("L", (CW, CH), 0)
            t.paste(km, (int(ox + gx), int(oy + gy)))
            key_all = ImageChops.lighter(key_all, t)
        fill_masks.append(fmask)
    art = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    # extrude (chunky depth)
    ext = Image.new("L", (CW, CH), 0)
    for i in range(1, int(extrude * S) + 1, 2):
        ext = ImageChops.lighter(ext, shift(key_all, i * 0.55, i))
    art = over(art, ext_color, ext)
    art = over(art, INK, key_all)
    for li, fmask in enumerate(fill_masks):
        f = fills[li % len(fills)]
        if f == "holo":
            tex = holo_tex(CW, CH, seed=holo_seed + li, phase=holo_phase + li * 0.17)
        elif isinstance(f, tuple) and f and f[0] == "grad":
            tex = vgrad_tex(CW, CH, f[1], f[2])
        else:
            tex = Image.new("RGBA", (CW, CH), tuple(f) + (255,))
        layer = tex.copy()
        layer.putalpha(fmask)
        art = Image.alpha_composite(art, layer)
        if bevel:
            hl = ImageChops.subtract(fmask, shift(fmask, 0, 3 * S)).filter(ImageFilter.GaussianBlur(0.8 * S))
            art = over(art, (255, 255, 255), scale_mask(hl, 0.55))
            sh = ImageChops.subtract(fmask, shift(fmask, 0, -3 * S)).filter(ImageFilter.GaussianBlur(0.8 * S))
            art = over(art, (0, 0, 0), scale_mask(sh, 0.28))
    return art


# ------------------------------------------------------------------ sticker build
def build_sticker(art, border=12, material="gloss", close=None, body=None, gloss_pos=0.32,
                  gloss_angle=28, curl=None, seed=5, rim=True, holo_border=False, holo_phase=0.0):
    """art: RGBA at SS (with transparent padding). Returns dict(img, lift)."""
    S = SS
    if body is None:
        # v2: always leave room for the thicker die-cut border
        c = close if close is not None else border * 1.6
        extra = int((border + c + 12) * S)
        padded = Image.new("RGBA", (art.size[0] + 2 * extra, art.size[1] + 2 * extra), (0, 0, 0, 0))
        padded.paste(art, (extra, extra))
        art = padded
    w, h = art.size
    a = art.split()[3].point(lambda v: 255 if v > 40 else 0)
    if body is None:
        body = erode(dilate(a, (border + c) * S), c * S)
        body = body.filter(ImageFilter.GaussianBlur(1.2 * S)).point(lambda v: 255 if v > 127 else 0)
    # ---- base material
    if material == "kraft":
        base = kraft_tex(w, h, seed)
    elif material == "clear":
        base = Image.new("RGBA", (w, h), (226, 236, 242, 34))
    elif holo_border:
        base = holo_tex(w, h, seed=seed, phase=holo_phase, sat=0.5)
    else:
        base = vgrad_tex(w, h, (255, 254, 251), (241, 239, 233))
    base = base.copy()
    ba = base.split()[3]
    base.putalpha(mul(ba, body))
    st = Image.alpha_composite(base, art)
    # keep everything within the die-cut
    st.putalpha(ImageChops.lighter(mul(st.split()[3], body), mul(a, body)))
    # ---- vinyl thickness: rim light top-left, rim shade bottom-right
    if rim:
        k = {"kraft": 0.35, "clear": 1.0}.get(material, 0.8)
        hl = ImageChops.subtract(body, shift(body, 2 * S, 2 * S)).filter(ImageFilter.GaussianBlur(0.7 * S))
        sh = ImageChops.subtract(body, shift(body, -2 * S, -2 * S)).filter(ImageFilter.GaussianBlur(0.7 * S))
        st = over(st, (255, 255, 255), scale_mask(hl, 0.85 * k))
        st = over(st, (40, 36, 44), scale_mask(sh, 0.45 * k))
        if material == "clear":
            # clear vinyl: the edge refracts, so it reads as a thin bright line
            edge = ImageChops.subtract(body, erode(body, 1.6 * S))
            st = over(st, (255, 255, 255), scale_mask(edge, 0.55))
        else:
            edge = ImageChops.subtract(body, erode(body, 1.0 * S))
            st = over(st, (34, 30, 38), scale_mask(edge, 0.7))
    # ---- specular gloss
    g = diag(w, h, gloss_angle)
    if material == "kraft":
        soft = g.point(band_lut(gloss_pos, 0.25, 0.10))
        st = over(st, (255, 245, 225), mul(soft, body))
    else:
        soft = g.point(band_lut(gloss_pos, 0.13, 0.30 if material != "clear" else 0.38))
        sharp = g.point(band_lut(gloss_pos + 0.05, 0.016, 0.65))
        sharp2 = g.point(band_lut(gloss_pos + 0.085, 0.007, 0.45))
        spec = ImageChops.lighter(ImageChops.lighter(soft, sharp), sharp2)
        st = over(st, (255, 255, 255), mul(spec, body))
    lift = Image.new("L", (w, h), 0)
    sd = {"img": st, "lift": lift, "body": body, "material": material}
    if curl:
        sd = apply_curl(sd, **curl)
    return sd


def apply_curl(sd, corner="tr", amount=0.16, back=None, flap_shadow=0.45, bend=0.0):
    """Fold a corner back over the sticker (peel). amount = fraction of corner->centre distance."""
    S = SS
    img = sd["img"]
    w, h = img.size
    a = img.split()[3]
    body = sd["body"]
    x0, y0, x1, y1 = body.getbbox()
    C = {"tl": (x0, y0), "tr": (x1, y0), "bl": (x0, y1), "br": (x1, y1)}[corner]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ux, uy = cx - C[0], cy - C[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    if bend:
        ca, sa = math.cos(bend), math.sin(bend)
        ux, uy = ux * ca - uy * sa, ux * sa + uy * ca
    dist = amount * L
    Px, Py = C[0] + ux * dist, C[1] + uy * dist
    dx, dy = -uy, ux
    far = 4 * max(w, h)
    poly = [(Px - dx * far, Py - dy * far), (Px + dx * far, Py + dy * far),
            (Px + dx * far - ux * far, Py + dy * far - uy * far), (Px - dx * far - ux * far, Py - dy * far - uy * far)]
    hp = Image.new("L", (w, h), 0)
    ImageDraw.Draw(hp).polygon(poly, fill=255)
    flap_a = mul(body, hp)
    remain = img.copy()
    remain.putalpha(mul(a, ImageOps.invert(hp)))
    r11, r12, r22 = 2 * dx * dx - 1, 2 * dx * dy, 2 * dy * dy - 1
    c1 = Px - (r11 * Px + r12 * Py)
    c2 = Py - (r12 * Px + r22 * Py)
    flap_ref = flap_a.transform((w, h), Image.AFFINE, (r11, r12, c1, r12, r22, c2), resample=Image.BICUBIC)
    # shading across the fold (cylinder-ish): bright crease, darker toward the tip
    def sfield(u, v):
        X, Y = u * w, v * h
        s = (X - Px) * ux + (Y - Py) * uy
        return s / max(1.0, dist)
    s = grad_field(w, h, sfield, n=96)
    mat = sd["material"]
    bc = back or ((206, 176, 130) if mat == "kraft" else BACK)
    backside = Image.new("RGBA", (w, h), bc + (255,))
    backside = over(backside, (0, 0, 0), s.point(lambda v: int(70 * (v / 255.0) ** 1.3)))
    crease = s.point(lambda v: int(170 * math.exp(-((v / 255.0) / 0.10) ** 2)))
    backside = over(backside, (255, 255, 255), crease)
    # cast shadow of the flap onto the sticker below
    fsh = shift(flap_ref, 4 * S, 7 * S).filter(ImageFilter.GaussianBlur(5 * S))
    remain = over(remain, (0, 0, 0), mul(scale_mask(fsh, flap_shadow), remain.split()[3]))
    out = remain
    backside.putalpha(flap_ref)
    out = Image.alpha_composite(out, backside)
    edge = ImageChops.subtract(flap_ref, erode(flap_ref, 1.2 * S))
    out = over(out, (70, 66, 72), scale_mask(edge, 0.5))
    sd = dict(sd)
    sd["img"] = out
    sd["lift"] = ImageChops.lighter(sd["lift"], flap_a)
    return sd


# ------------------------------------------------------------------ placement
def _to_1x(im, size):
    if im.mode == "RGBA":
        return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")
    return im.resize(size, Image.LANCZOS)


def paste_full(canvas, layer, x, y):
    full = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    full.paste(layer, (int(x), int(y)))
    return Image.alpha_composite(canvas, full)


def place(canvas, sd, cx, cy, angle=0.0, scale=1.0, squash=(1.0, 1.0), shadow=1.0,
          hover=0.0, opacity=1.0, extra_shadow=True):
    img, lift = sd["img"], sd["lift"]
    w, h = img.size
    nw, nh = max(2, int(w * scale * squash[0])), max(2, int(h * scale * squash[1]))
    img = img.resize((nw, nh), Image.BICUBIC)
    lift = lift.resize((nw, nh), Image.BICUBIC)
    img = img.convert("RGBa").rotate(angle, Image.BICUBIC, expand=True).convert("RGBA")
    lift = lift.rotate(angle, Image.BICUBIC, expand=True)
    W1, H1 = img.size[0] // SS, img.size[1] // SS
    img = _to_1x(img, (W1, H1))
    lift = _to_1x(lift, (W1, H1))
    a = img.split()[3]
    x, y = cx - W1 / 2, cy - H1 / 2
    pad = 60
    def shadow_layer(mask, blur, op):
        m = Image.new("L", (W1 + 2 * pad, H1 + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        m = m.filter(ImageFilter.GaussianBlur(blur)) if blur > 0 else m
        lay = Image.new("RGBA", m.size, (6, 4, 10, 0))
        lay.putalpha(scale_mask(m, min(1.0, op)))
        return lay
    if shadow > 0:
        hv = hover
        canvas = paste_full(canvas, shadow_layer(a, 10 + 22 * hv, 0.38 * shadow * (1 - 0.4 * hv)), x - pad + 6 + 26 * hv, y - pad + 10 + 34 * hv)
        if hv < 0.5:
            canvas = paste_full(canvas, shadow_layer(a, 2, 0.55 * shadow * (1 - 2 * hv)), x - pad + 2, y - pad + 3)
        if extra_shadow and lift.getbbox():
            canvas = paste_full(canvas, shadow_layer(lift, 9, 0.55 * shadow), x - pad + 10, y - pad + 16)
    if opacity < 1.0:
        img.putalpha(scale_mask(a, opacity))
    return paste_full(canvas, img, x, y)


# ------------------------------------------------------------------ paint pen
def catmull(pts, n=12):
    if len(pts) < 3:
        return pts
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


class Pen:
    """Accumulates Posca-style strokes in a full-canvas SS mask, then inks them in one pass."""

    def __init__(self, size, color, seed=21):
        self.size = size
        self.color = color
        self.rng = random.Random(seed)
        self.mask = Image.new("L", (size[0] * SS, size[1] * SS), 0)
        self.d = ImageDraw.Draw(self.mask)

    def stroke(self, pts, width=8, taper=True):
        S = SS
        pts = [(x * S, y * S) for x, y in pts]
        n = len(pts)
        for i in range(n - 1):
            t = i / max(1, n - 2)
            wv = width
            if taper:
                wv = width * (0.78 + 0.22 * math.sin(math.pi * min(1.0, t * 1.15)))
            wv = wv * S * (1 + self.rng.uniform(-0.03, 0.03))
            self.d.line([pts[i], pts[i + 1]], fill=255, width=max(1, int(wv)))
            r = wv / 2
            self.d.ellipse([pts[i + 1][0] - r, pts[i + 1][1] - r, pts[i + 1][0] + r, pts[i + 1][1] + r], fill=255)
        r = width * S * 0.39
        self.d.ellipse([pts[0][0] - r, pts[0][1] - r, pts[0][0] + r, pts[0][1] + r], fill=255)

    def wobble(self, pts, amp=1.2):
        return [(x + self.rng.uniform(-amp, amp), y + self.rng.uniform(-amp, amp)) for x, y in pts]

    def circle(self, cx, cy, rx, ry, width=8, start=-2.2, over=0.55, tilt=-0.12, grow=0.07):
        pts = []
        n = 34
        total = 2 * math.pi + over
        for i in range(n + 1):
            t = i / n
            a = start + total * t
            k = 1 + grow * t + 0.025 * math.sin(3 * a + 1.3)
            x, y = rx * k * math.cos(a), ry * k * math.sin(a)
            xr = x * math.cos(tilt) - y * math.sin(tilt)
            yr = x * math.sin(tilt) + y * math.cos(tilt)
            pts.append((cx + xr, cy + yr))
        self.stroke(catmull(pts, 6), width)

    def arrow(self, pts, width=8, head=26, spread=0.5):
        sm = catmull(self.wobble(pts, 1.0), 14)
        self.stroke(sm, width)
        ex, ey = sm[-1]
        px, py = sm[-4]
        ang = math.atan2(ey - py, ex - px)
        for s in (-spread, spread):
            a = ang + math.pi + s
            hx, hy = ex + head * math.cos(a), ey + head * math.sin(a)
            mid = ((ex + hx) / 2 + 1.5, (ey + hy) / 2 - 1.0)
            self.stroke(catmull([(hx, hy), mid, (ex, ey)], 6), width * 0.95, taper=False)

    def text(self, s, x, y, size, angle=0.0, font_path=MARKER, anchor="mm"):
        S = SS
        font = ImageFont.truetype(font_path, int(size * S))
        bb = font.getbbox(s, anchor=anchor)
        m = int(size * S)
        tw, th = bb[2] - bb[0] + 2 * m, bb[3] - bb[1] + 2 * m
        t = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(t).text((m - bb[0], m - bb[1]), s, font=font, fill=255, anchor=anchor,
                               stroke_width=int(0.6 * S), stroke_fill=255)
        t = t.rotate(angle, Image.BICUBIC, expand=True)
        self.mask.paste(255, (int(x * S - t.size[0] / 2), int(y * S - t.size[1] / 2)), t)

    def ink(self, canvas, shadow=0.5):
        m1 = self.mask.resize(self.size, Image.LANCZOS)
        if shadow > 0:
            sh = shift(m1, 2, 3).filter(ImageFilter.GaussianBlur(2.2))
            canvas = over(canvas, (5, 3, 8), scale_mask(sh, shadow))
        lay = Image.new("RGBA", self.size, self.color + (0,))
        lay.putalpha(m1)
        canvas = Image.alpha_composite(canvas, lay)
        # paint body: slight pooling at the edge and a soft satin sheen on top-left edges
        edge = ImageChops.subtract(m1, erode(m1, 2)).filter(ImageFilter.GaussianBlur(0.6))
        canvas = over(canvas, tuple(int(c * 0.8) for c in self.color), mul(scale_mask(edge, 0.45), m1))
        hl = ImageChops.subtract(m1, shift(m1, 1, 2)).filter(ImageFilter.GaussianBlur(0.5))
        canvas = over(canvas, (255, 255, 255), mul(scale_mask(hl, 0.35), m1))
        return canvas


# ------------------------------------------------------------------ misc
def rrect_mask(size, box, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, radius=r, fill=255)
    return m


def text_img(draw, xy, s, path, size, fill, anchor="mm", **kw):
    f = ImageFont.truetype(path, int(size * SS))
    draw.text((xy[0], xy[1]), s, font=f, fill=fill, anchor=anchor, **kw)
