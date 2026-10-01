"""Ransom-note collage overlay toolkit (Pillow + numpy, seeded).

Everything is drawn at SS x supersampling onto an RGBA overlay, then reduced
with LANCZOS so cut edges stay razor sharp but anti-aliased.
"""
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance

SS = 2
ROOT = "C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass/"
OUT = ROOT + "docs/concepts/round3_overlay/o_e_ransom_collage/"
BASE_COMBAT = ROOT + "docs/concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png"
BASE_CITY = ROOT + "docs/concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png"
BASE_SHOP = ROOT + "docs/concepts/round2/r2c_v2_modem/modem_shop.png"

# ---- strict palette ---------------------------------------------------------
PINK = (255, 38, 132)
BLACK = (13, 11, 14)
WHITE = (246, 242, 232)
YEL = (220, 255, 0)
PAL = {"P": PINK, "K": BLACK, "W": WHITE, "Y": YEL}

F = "C:/Windows/Fonts/"
# "magazines": heavy display faces of very different families
MAG_FONTS = [
    F + "impact.ttf", F + "ariblk.ttf", F + "BOD_BLAR.TTF", F + "COOPBL.TTF",
    F + "ROCKEB.TTF", F + "ELEPHNT.TTF", F + "FRAHV.TTF",
    F + "GILSANUB.TTF", F + "BERNHC.TTF", F + "BRITANIC.TTF", F + "GOUDYSTO.TTF",
    F + "timesbd.ttf", F + "seguibl.ttf",
]
NUM_FONTS = [F + "impact.ttf", F + "ariblk.ttf", F + "COOPBL.TTF", F + "ROCKEB.TTF",
             F + "FRAHV.TTF", F + "BOD_BLAR.TTF", F + "timesbd.ttf"]
TYPE_FONT = F + "courbd.ttf"
UI_FONT = F + "bahnschrift.ttf"

# letter colour schemes (fg, bg) all from the strict palette
SCHEMES = [("K", "W"), ("W", "K"), ("K", "P"), ("P", "K"), ("K", "Y"),
           ("W", "P"), ("Y", "K"), ("P", "W")]

_font_cache = {}


def font(path, size):
    key = (path, int(size))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, int(size))
    return _font_cache[key]


# ---- textures ---------------------------------------------------------------
def paper_fill(w, h, col, rng, grain=7, gloss=0.06):
    """Flat paper colour with fibre grain and a faint gloss sweep."""
    r = np.random.default_rng(rng.randrange(1 << 30))
    base = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)
    n = r.normal(0, grain, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    n = np.kron(n, np.ones((2, 2), np.float32))[:h, :w]
    fib = r.normal(0, grain * 0.6, (h, 1)).astype(np.float32)  # horizontal fibres
    g = np.linspace(-1, 1, w, dtype=np.float32)[None, :] * 0.6 + np.linspace(-1, 1, h, dtype=np.float32)[:, None] * 0.4
    sweep = np.clip(1 - np.abs(g - rng.uniform(-0.4, 0.4)) * 2.2, 0, 1) * 255 * gloss
    base += (n + fib + sweep)[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


def halftone_dots(w, h, dot_col, spacing, radius_fn, angle=45, bg=None):
    """Rotated-grid halftone. radius_fn(x, y) -> radius in px (0..spacing*0.7)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0) if bg is None else bg + (255,))
    d = ImageDraw.Draw(img)
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    diag = int(math.hypot(w, h)) + spacing
    for gy in range(-diag, diag, spacing):
        for gx in range(-diag, diag, spacing):
            x = w / 2 + gx * ca - gy * sa
            y = h / 2 + gx * sa + gy * ca
            if x < -spacing or y < -spacing or x > w + spacing or y > h + spacing:
                continue
            rr = radius_fn(x, y)
            if rr > 0.4:
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=dot_col + (255,))
    return img


def halftone_from_gray(gray, dot_col, spacing, angle=45, gamma=1.0, maxr=0.72, bg=None):
    """gray: L image, dark -> big dots."""
    arr = np.asarray(gray, np.float32) / 255.0
    h, w = arr.shape

    def rf(x, y):
        xi = min(w - 1, max(0, int(x)))
        yi = min(h - 1, max(0, int(y)))
        v = (1 - arr[yi, xi]) ** gamma
        return math.sqrt(v) * spacing * maxr
    return halftone_dots(w, h, dot_col, spacing, rf, angle, bg)


# ---- geometry -----------------------------------------------------------------
def jag_rect(w, h, rng, cut=0.12, extra=True):
    """Scissor-cut quadrilateral-ish polygon inside a w x h box (with margin)."""
    j = lambda s: rng.uniform(0, cut) * s
    pts = [(j(w), j(h)), (w - j(w), j(h)), (w - j(w), h - j(h)), (j(w), h - j(h))]
    if extra:
        # one or two extra snips on random edges
        out = []
        for i in range(4):
            out.append(pts[i])
            if rng.random() < 0.45:
                a, b = pts[i], pts[(i + 1) % 4]
                t = rng.uniform(0.3, 0.7)
                mx, my = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                # push inward a little
                cx, cy = w / 2, h / 2
                k = rng.uniform(0.0, 0.07)
                out.append((mx + (cx - mx) * k, my + (cy - my) * k))
        pts = out
    return pts


def star_poly(cx, cy, r_out, r_in, n, rng, jitter=0.18, rot=0.0):
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n + rng.uniform(-0.12, 0.12) / n * math.pi
        r = r_out if i % 2 == 0 else r_in
        r *= 1 + rng.uniform(-jitter, jitter)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def arrow_poly(x0, y0, x1, y1, w0, w1, head_len, head_w, barb=0.35):
    """Tapered cut-paper arrow wedge from (x0,y0) to tip (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    hx, hy = x1 - ux * head_len, y1 - uy * head_len
    bx, by = hx - ux * head_len * barb, hy - uy * head_len * barb  # barb notch
    return [
        (x0 + nx * w0 / 2, y0 + ny * w0 / 2),
        (hx + nx * w1 / 2, hy + ny * w1 / 2),
        (bx + nx * head_w / 2, by + ny * head_w / 2),
        (x1, y1),
        (bx - nx * head_w / 2, by - ny * head_w / 2),
        (hx - nx * w1 / 2, hy - ny * w1 / 2),
        (x0 - nx * w0 / 2, y0 - ny * w0 / 2),
        (x0 - ux * w0 * 0.6, y0 - uy * w0 * 0.6),  # fishtail end
    ]


def poly_bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---- pieces -----------------------------------------------------------------
class Piece:
    """A cut paper element: RGBA image placed by centre with rotation/scale."""

    def __init__(self, img, x, y, rot=0.0, sx=1.0, sy=1.0, shadow=(7, 9), sh_col=BLACK,
                 sh_alpha=235, alpha=1.0, back_col=None, ghost=0):
        self.img, self.x, self.y, self.rot = img, x, y, rot
        self.sx, self.sy = sx, sy
        self.shadow, self.sh_col, self.sh_alpha = shadow, sh_col, sh_alpha
        self.alpha = alpha
        self.back_col = back_col
        self.ghost = ghost

    def copy(self, **kw):
        p = Piece(self.img, self.x, self.y, self.rot, self.sx, self.sy, self.shadow,
                  self.sh_col, self.sh_alpha, self.alpha, self.back_col)
        for k, v in kw.items():
            setattr(p, k, v)
        return p

    def render(self):
        im = self.img
        if self.sx < 0 and self.back_col is not None:
            # flipped over: we see the plain paper back
            back = Image.new("RGBA", im.size, self.back_col + (255,))
            back.putalpha(im.getchannel("A"))
            im = back.transpose(Image.FLIP_LEFT_RIGHT)
        w = max(2, int(im.width * abs(self.sx)))
        h = max(2, int(im.height * abs(self.sy)))
        if (w, h) != im.size:
            im = im.resize((w, h), Image.LANCZOS)
        if self.rot:
            im = im.rotate(self.rot, Image.BICUBIC, expand=True)
        if self.alpha < 1:
            a = im.getchannel("A").point(lambda v: int(v * self.alpha))
            im.putalpha(a)
        return im


def draw_pieces(canvas, pieces, soft=True):
    """Draw pieces in order; each casts a hard offset shadow (+ faint soft one)."""
    for p in pieces:
        im = p.render()
        ox = int(p.x - im.width / 2)
        oy = int(p.y - im.height / 2)
        a = im.getchannel("A")
        if p.shadow is not None:
            dx, dy = p.shadow
            if soft:
                sa = a.filter(ImageFilter.GaussianBlur(9 * SS)).point(lambda v: int(v * 0.35 * p.alpha))
                sh = Image.new("RGBA", im.size, BLACK + (0,))
                sh.putalpha(sa)
                canvas.alpha_composite(sh, (ox + int(dx * 1.6), oy + int(dy * 1.6)))
            sh = Image.new("RGBA", im.size, p.sh_col + (0,))
            sh.putalpha(a.point(lambda v: int(v * p.sh_alpha / 255 * p.alpha)))
            canvas.alpha_composite(sh, (ox + int(dx), oy + int(dy)))
        canvas.alpha_composite(im, (ox, oy))


def shape_piece(pts, col, rng, halftone=None, edge=True, pad=6):
    """Polygon cut from paper of colour col. halftone=(dot_col, spacing, angle, radius_frac)."""
    x0, y0, x1, y1 = poly_bbox(pts)
    w, h = int(x1 - x0) + pad * 2, int(y1 - y0) + pad * 2
    lp = [(px - x0 + pad, py - y0 + pad) for px, py in pts]
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(lp, fill=255)
    paper = paper_fill(w, h, col, rng).convert("RGBA")
    if halftone:
        dc, sp, ang, rf = halftone
        ht = halftone_dots(w, h, dc, sp, (lambda x, y, r=sp * rf: r) if not callable(rf) else rf, ang)
        paper.alpha_composite(ht)
    if edge:
        # cut edge catches light: thin lighter rim on the lit (top-left) side
        rim = ImageChops.subtract(mask, ImageChops.offset(mask, 2, 2))
        lite = tuple(min(255, c + 60) for c in col)
        layer = Image.new("RGBA", (w, h), lite + (0,))
        layer.putalpha(rim.point(lambda v: int(v * 0.8)))
        paper.alpha_composite(layer)
    paper.putalpha(mask)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return paper, cx, cy


def letter_img(ch, fpath, size, fg, bg, rng, style="tile", halftone=False):
    """One ransom letter as RGBA (unrotated). style: tile | diecut | bare."""
    fnt = font(fpath, size)
    bb = fnt.getbbox(ch)
    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
    if style == "tile":
        px = int(size * rng.uniform(0.10, 0.22))
        py = int(size * rng.uniform(0.08, 0.18))
        W, H = gw + 2 * px, gh + 2 * py
        pts = jag_rect(W, H, rng, cut=0.10)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        img = paper_fill(W, H, PAL[bg], rng).convert("RGBA")
        if halftone:
            dot = PINK if bg in ("W", "Y") else (WHITE if bg == "P" else PINK)
            sp = max(6, int(size * 0.075))
            ang = rng.choice([15, 45, 75])
            grad = lambda x, y, W=W, H=H, sp=sp: sp * 0.48 * max(0.0, (x / W + y / H) / 2 - 0.15)
            img.alpha_composite(halftone_dots(W, H, dot, sp, grad, ang))
        gl = Image.new("L", (W, H), 0)
        ImageDraw.Draw(gl).text((px - bb[0], py - bb[1]), ch, font=fnt, fill=255)
        fgl = Image.new("RGBA", (W, H), PAL[fg] + (0,))
        fgl.putalpha(gl)
        img.alpha_composite(fgl)
        rim = ImageChops.subtract(mask, ImageChops.offset(mask, 2, 2))
        lite = tuple(min(255, c + 70) for c in PAL[bg])
        rl = Image.new("RGBA", (W, H), lite + (0,))
        rl.putalpha(rim.point(lambda v: int(v * 0.7)))
        img.alpha_composite(rl)
        img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
        return img
    # die-cut: the glyph itself cut out with a paper border
    b = int(size * 0.07) + 2
    W, H = gw + 4 * b, gh + 4 * b
    gl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gl).text((2 * b - bb[0], 2 * b - bb[1]), ch, font=fnt, fill=255)
    k = b * 2 + 1
    border = gl.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))
    # angularise the border: threshold hard
    border = border.point(lambda v: 255 if v > 90 else 0)
    img = paper_fill(W, H, PAL[bg], rng).convert("RGBA")
    fgl = paper_fill(W, H, PAL[fg], rng, grain=5).convert("RGBA")
    fgl.putalpha(gl)
    img.alpha_composite(fgl)
    img.putalpha(border)
    return img


def ransom_word(text, cx, cy, size, rng, fonts=None, schemes=None, rot_range=9,
                kern=-0.04, base_rot=0.0, size_var=(0.82, 1.22), diecut_p=0.25,
                halftone_p=0.3, shadow=(7, 9), sh_col=BLACK, word_gap=0.38):
    """Lay out a word of individual cut letters centred at (cx, cy) along base_rot."""
    fonts = fonts or MAG_FONTS
    schemes = schemes or SCHEMES
    items = []
    last_f, last_s = None, None
    for ch in text:
        if ch == " ":
            items.append(None)
            continue
        f = rng.choice([x for x in fonts if x != last_f])
        s = rng.choice([x for x in schemes if last_s is None or (x[1] != last_s[1] and x != last_s)] or schemes)
        last_f, last_s = f, s
        sz = int(size * rng.uniform(*size_var))
        style = "diecut" if rng.random() < diecut_p else "tile"
        img = letter_img(ch, f, sz, s[0], s[1], rng, style,
                         halftone=(style == "tile" and rng.random() < halftone_p))
        items.append(img)
    total = 0
    widths = []
    for im in items:
        w = size * word_gap if im is None else im.width + size * kern
        widths.append(w)
        total += w
    a = math.radians(-base_rot)
    ux, uy = math.cos(a), math.sin(a)
    t = -total / 2
    pieces = []
    for im, w in zip(items, widths):
        c = t + w / 2
        t += w
        if im is None:
            continue
        dy = rng.uniform(-0.08, 0.08) * size
        x = cx + ux * c - uy * dy
        y = cy + uy * c + ux * dy
        pieces.append(Piece(im, x, y, base_rot + rng.uniform(-rot_range, rot_range),
                            shadow=shadow, sh_col=sh_col, back_col=WHITE))
    return pieces


def type_strip(text, cx, cy, size, rng, fg="K", bg="W", rot=0.0, fpath=None, pad=(0.45, 0.28),
               shadow=(5, 6)):
    """A strip of typewriter text cut from a page."""
    fpath = fpath or TYPE_FONT
    fnt = font(fpath, size)
    bb = fnt.getbbox(text)
    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
    px, py = int(size * pad[0]), int(size * pad[1])
    W, H = gw + 2 * px, gh + 2 * py
    pts = jag_rect(W, H, rng, cut=0.03, extra=False)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    img = paper_fill(W, H, PAL[bg], rng, grain=6).convert("RGBA")
    gl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gl).text((px - bb[0], py - bb[1]), text, font=fnt, fill=255)
    # ink density variation for typewriter
    r = np.random.default_rng(rng.randrange(1 << 30))
    ink = (np.asarray(gl, np.float32) * r.uniform(0.75, 1.0, (H, 1))).astype(np.uint8)
    fgl = Image.new("RGBA", (W, H), PAL[fg] + (0,))
    fgl.putalpha(Image.fromarray(ink, "L"))
    img.alpha_composite(fgl)
    img.putalpha(mask)
    return Piece(img, cx, cy, rot, shadow=shadow, back_col=WHITE)


# ---- base treatment -------------------------------------------------------------
def load_base(path, dim=0.9, desat=0.85):
    im = Image.open(path).convert("RGB")
    im = ImageEnhance.Color(im).enhance(desat)
    im = ImageEnhance.Brightness(im).enhance(dim)
    return im.convert("RGBA")


def darken_under(base, overlay2x, strength=0.45, blur=40):
    """Darken the base under overlay silhouettes so the paper reads."""
    a = overlay2x.getchannel("A").resize(base.size, Image.BILINEAR)
    a = a.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(blur))
    a = a.point(lambda v: int(v * strength))
    dark = Image.new("RGBA", base.size, (8, 6, 10, 0))
    dark.putalpha(a)
    out = base.copy()
    out.alpha_composite(dark)
    return out


def finish(base, overlay2x):
    ov = overlay2x.resize(base.size, Image.LANCZOS)
    out = base.copy()
    out.alpha_composite(ov)
    return out.convert("RGB")


def new_canvas(w=1920, h=1080):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def S(*v):
    """Scale 1x coordinates to supersampled."""
    if len(v) == 1:
        return v[0] * SS
    return tuple(x * SS for x in v)


# ---- halftone "photo" portrait ----------------------------------------------------
def portrait_gray(w, h, rng):
    """Procedural hooded operative, lit hard from the left (grayscale source)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = 228 - 30 * (yy / h)
    # graphic diagonal backdrop shadow
    g = np.where(yy > h * 0.15 + (xx / w) * h * 0.55, g - 70, g)
    cx, cy = w * 0.47, h * 0.45
    rx, ry = w * 0.235, h * 0.27
    hx = (xx - cx) / (w * 0.39)
    hy = (yy - (cy - h * 0.01)) / (h * 0.41)
    hood = (hx ** 2 + np.where(hy < 0, hy ** 2 * (1 + 0.9 * np.abs(hx)), hy ** 2 * 0.5)) < 1
    shoulders = (yy > h * 0.74) & (np.abs(xx - cx) < w * (0.30 + (yy - h * 0.74) / h * 1.8))
    body = hood | shoulders
    rim = np.clip(1 - np.abs(hx + 0.93) / 0.06, 0, 1) * (yy < h * 0.85)
    g = np.where(body, 62 + 150 * rim, g)
    neck = (np.abs(xx - cx) < rx * 0.48) & (yy > cy) & (yy < cy + ry * 1.45)
    g = np.where(neck, np.where(xx < cx - rx * 0.1, 120, 26), g)
    ny = (yy - cy) / ry
    taper = 1 - 0.36 * np.clip(ny, 0, 1) ** 1.3
    nx = (xx - cx) / (rx * taper)
    r2 = nx ** 2 + ny ** 2
    head = r2 < 1
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    L = np.array([-0.80, -0.30, 0.52])
    L = L / np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    t = np.clip((lam - 0.12) / 0.45, 0, 1)
    shade = 22 + 233 * (t * t * (3 - 2 * t))
    g = np.where(head, shade, g)
    brow = head & (ny < -0.42 + 0.15 * nx)
    g = np.where(brow, g * 0.25, g)
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(img)
    vy = cy - ry * 0.16
    d.polygon([(cx - rx * 1.02, vy - ry * 0.10), (cx + rx * 0.98, vy - ry * 0.16),
               (cx + rx * 0.92, vy + ry * 0.10), (cx - rx * 0.95, vy + ry * 0.15)], fill=18)
    d.polygon([(cx - rx * 0.78, vy + ry * 0.08), (cx - rx * 0.62, vy - ry * 0.11),
               (cx - rx * 0.52, vy - ry * 0.11), (cx - rx * 0.68, vy + ry * 0.09)], fill=250)
    d.line([(cx + rx * 0.1, vy - ry * 0.02), (cx + rx * 0.6, vy - ry * 0.06)], fill=130, width=max(2, int(w * 0.006)))
    d.polygon([(cx - rx * 0.02, vy + ry * 0.14), (cx + rx * 0.12, cy + ry * 0.36),
               (cx + rx * 0.42, cy + ry * 0.40), (cx + rx * 0.10, vy + ry * 0.14)], fill=40)
    d.polygon([(cx - rx * 0.08, vy + ry * 0.14), (cx - rx * 0.16, cy + ry * 0.34),
               (cx - rx * 0.02, cy + ry * 0.36), (cx + rx * 0.0, vy + ry * 0.14)], fill=245)
    d.polygon([(cx - rx * 0.36, cy + ry * 0.58), (cx + rx * 0.28, cy + ry * 0.55),
               (cx + rx * 0.26, cy + ry * 0.61), (cx - rx * 0.30, cy + ry * 0.63)], fill=35)
    d.polygon([(cx - rx * 0.2, cy + ry * 0.80), (cx + rx * 0.3, cy + ry * 0.78),
               (cx + rx * 0.1, cy + ry * 0.9)], fill=70)
    d.polygon([(cx - rx * 0.86, cy + ry * 0.05), (cx - rx * 0.4, cy + ry * 0.22),
               (cx - rx * 0.62, cy + ry * 0.42)], fill=150)
    return img.filter(ImageFilter.GaussianBlur(1.0))


def halftone_photo(w, h, rng, paper=WHITE, ink=BLACK, spot=PINK, spacing=9):
    gray = portrait_gray(w, h, rng)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    img = paper_fill(w, h, paper, rng, grain=5).convert("RGBA")
    # spot-colour plate (pink) slightly misregistered, only in the mids
    pk = halftone_from_gray(gray.point(lambda v: min(255, int(v * 0.8 + 70))), spot, spacing + 3, 15, 1.4, 0.62)
    img.alpha_composite(pk, (0, 0))
    k = halftone_from_gray(gray, ink, spacing, 45, 1.3, 0.64)
    img.alpha_composite(k, (2, 1))
    return img
