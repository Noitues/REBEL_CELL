"""Round 19 UI mediums.

  STICKERS   (sticker_lib19, local copy, gloss_k): only for things that never change - cards, node types,
             buttons, the screen title. Sheen is subtle at rest (gloss_k 0.22); one sticker per frame may show
             the animated sweep (gloss_k 1).
  PENCIL     (tg_lib grease pencil, imported in place from round3 o_a_tactical_glass): flavour, plans, and
             STATIC tactical states only (DOWN, LOST, INCOMING, the drag-hover arrow + circle, a reroute).
  PANELS     three candidate mediums for the node summary / raid incoming / threat intel:
               terminal(): CRT panel in the C screens & data language (recommended)
               dossier():  clipped case file under acrylic glass
               holo():     projected holo readout with its emitter
  LIVE       info that changes every step (feed, speed, damage, HP, integrity) is never a sticker:
               L1 street HUD (decal, netdecal19 pad(hud=...)), L2 inlay only, L3 diegetic floats (shards, numerals).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TG = os.path.abspath(os.path.join(HERE, "..", "..", "round3_overlay", "o_a_tactical_glass", "scripts"))
sys.path.insert(1, TG)
import sticker_lib19 as SL  # noqa: E402
import tg_lib as T  # noqa: E402

S = SL.SS
PINK, CYAN, GREEN, VIOLET, AMBER = (255, 61, 168), (92, 225, 255), (123, 224, 123), (200, 90, 255), (255, 176, 0)
LIME, HARM, HALCYON, PAPER, INKC = (212, 255, 0), (255, 68, 51), (140, 123, 255), (244, 241, 233), (14, 12, 20)
ICE = (178, 235, 255)
Y_PEN, R_PEN = (1.00, 0.86, 0.16), (0.97, 0.13, 0.12)
FILL_YELLOW = ("grad", (255, 238, 96), (232, 176, 22))
FILL_PINK = ("grad", (255, 96, 172), (222, 18, 112))
FILL_RED = ("grad", (255, 88, 80), (204, 20, 22))
SL.YELLOW, SL.CORAL, SL.TEAL = (255, 219, 41), (247, 33, 31), (255, 36, 136)


def F(path, size):
    return ImageFont.truetype(path, int(round(size)))


def f2pil(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def pil2f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


# ------------------------------------------------------------------ stickers
def word_sticker(lines, size, fills, seed=1, border=16, gloss_k=0.22, curl=None):
    if isinstance(lines, str):
        lines = [lines]
    art = SL.lettering(lines, size, fills, key_w=5, extrude=8, seed=seed, jitter=4.0, track=1, holo_seed=seed + 40)
    return SL.build_sticker(art, border=border, material="gloss", seed=seed, close=border * 1.25, gloss_k=gloss_k, curl=curl)


def place(img_f, sd, cx, cy, angle=0.0, **kw):
    c = f2pil(img_f).convert("RGBA")
    c = SL.place(c, sd, cx, cy, angle=angle, **kw)
    return pil2f(c)


class Pen:
    """Draw on sticker art (SS) in 1x units."""

    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    def text(self, x, y, s, font=SL.PLEX, size=16, col=PAPER, anchor="la"):
        self.d.text((x * S, y * S), s, font=F(font, size * S), fill=tuple(col) + (255,), anchor=anchor)

    def rect(self, x0, y0, x1, y1, col, r=0):
        if r:
            self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=tuple(col) + (255,))
        else:
            self.d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=tuple(col) + (255,))

    def glyph(self, path, cx, cy, size, col):
        g = Image.open(path).convert("RGBA").split()[3].resize((int(size * S), int(size * S)), Image.LANCZOS)
        lay = Image.new("RGBA", g.size, tuple(col) + (255,))
        lay.putalpha(g)
        self.img.alpha_composite(lay, (int((cx - size / 2) * S), int((cy - size / 2) * S)))


def card_sticker(w, h, fn, face=(16, 15, 24), seed=5, gloss_k=0.22, radius=10, border=7):
    art = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
    p = Pen(art)
    p.rect(0, 0, w - 1, h - 1, face, r=radius)
    fn(p)
    return SL.build_sticker(art, border=border, material="gloss", seed=seed, gloss_k=gloss_k)


GLYPHS = os.path.abspath(os.path.join(HERE, "..", "..", "round17_slice_system", "glyphs"))


def gpath(name):
    return os.path.join(GLYPHS, name + ".png")


def asset_card(name, glyph, hp, copies, desc, col, seed, gloss_k=0.22):
    def fn(p):
        p.rect(10, 10, 140, 76, (30, 28, 42), r=8)
        p.glyph(gpath(glyph), 75, 43, 54, col)
        p.text(12, 84, name, SL.ANTON, 21, PAPER)
        p.text(12, 114, "INT %d" % hp, SL.MONO, 13, col)
        p.text(138, 114, "x%d" % copies, SL.MONO, 13, PAPER, "ra")
        y = 134
        for line in desc:
            p.text(12, y, line, SL.PLEX, 12, (190, 186, 205))
            y += 15
        p.rect(0, 0, 149, 5, col, r=2)
    return card_sticker(150, 172, fn, seed=seed, gloss_k=gloss_k)


# defence assets (GDD A.5 + art_asset appendix): name, glyph, integrity, copies, effect lines, colour
TRAY = [("TURRET", "picto_target", 10, 1, ["4 dmg, range 1", "first in path"], CYAN),
        ("RAILGUN", "slice_zero_day", 10, 0, ["8 dmg, range 2", "hardest hitter"], CYAN),
        ("ICE LOCK", "state_frozen", 8, 1, ["holds a threat", "for 2 steps"], ICE),
        ("FLAK ARRAY", "placeholder_storm", 9, 1, ["2 dmg x3, range 1", "weakest threat"], AMBER),
        ("DECOY", "placeholder_phishing", 12, 1, ["pull 3: threats", "route to it"], VIOLET),
        ("TAR PIT", "state_locked", 4, 2, ["holds 3 steps", "fragile"], GREEN)]


# ------------------------------------------------------------------ grease pencil
def pencil_layer(seed):
    return T.Layer(np.random.default_rng(seed))


def jitter_path(pts, rng, amp=2.0, step=6):
    p = T.resample(np.array(pts, float), step)
    n = len(p)
    t = np.linspace(0, 1, n)
    for f in (0.8, 1.7):
        ph = rng.random() * 6
        d = np.stack([np.sin(2 * math.pi * (f * t * n / 40 + ph)), np.cos(2 * math.pi * (f * t * n / 47 + ph))], 1)
        p = p + d * amp * rng.uniform(0.5, 1.0)
    return T.chaikin(p, 2)


def pencil_composite(base, L):
    L.light()
    return T.composite(base, L, darken=0.24, shadow=0.4)


def pen_x(L, x, y, r, col=R_PEN, w=6.5):
    L.wax_stroke(np.array([(x - r, y - r * 0.85), (x + r, y + r * 0.8)]), w, col)
    L.wax_stroke(np.array([(x + r, y - r * 0.85), (x - r * 0.95, y + r * 0.9)]), w, col)


def pen_text(L, text, x, y, cap, col, w=4.4, angle=-0.03, align="center"):
    L.strokes(T.letter_strokes(text, x, y, cap, w, col, L.rng, angle=angle, align=align))


def pen_circle(L, x, y, rx, ry, col, w=6.5, turns=1.12):
    L.wax_stroke(T.hand_circle(x, y, rx, ry, L.rng, turns=turns), w, col)


def pen_arrow(L, pts, col, w=6.0, head=20, dashed=False):
    L.strokes(T.arrow_strokes(jitter_path(pts, L.rng, 1.2, 4), w, col, L.rng, head=head, dashed=dashed, dash=22, gap=14))


# ------------------------------------------------------------------ panels: content model
# rows: ("h", text) heading | ("t", text, col) | ("kv", key, value, col) | ("node", glyph, name, chip, chipcol, sub)
#       ("bar", label, frac, col) | ("sep",) | ("route", letter, who, rule) | ("big", text, col)
def _measure(rows):
    h = 0
    for r in rows:
        h += {"h": 34, "t": 20, "kv": 22, "node": 38, "bar": 22, "sep": 10, "route": 40, "big": 46}[r[0]]
    return h


def _draw_rows(d, rows, x0, y0, w, mode, sc=S):
    """Shared row layout; colours / fonts adapt per medium."""
    mono = lambda s: F(SL.MONO, s * sc)  # noqa: E731
    anton = lambda s: F(SL.ANTON, s * sc)  # noqa: E731
    ink = {"terminal": (190, 225, 240), "dossier": (34, 30, 36), "holo": (220, 250, 255)}[mode]
    dim = {"terminal": (110, 140, 160), "dossier": (95, 88, 82), "holo": (150, 210, 225)}[mode]
    head = {"terminal": CYAN, "dossier": (24, 20, 26), "holo": (200, 255, 120)}[mode]
    y = y0
    glyph_draws = []
    for r in rows:
        k = r[0]
        if k == "h":
            d.text((x0 * sc, (y + 4) * sc), r[1], font=anton(22) if mode != "terminal" else mono(19), fill=head)
            y += 34
        elif k == "t":
            col = r[2] if len(r) > 2 and mode != "dossier" else (r[2] if len(r) > 2 and mode == "dossier" and r[2] == HARM else ink)
            d.text((x0 * sc, y * sc), r[1], font=mono(13), fill=col)
            y += 20
        elif k == "kv":
            d.text((x0 * sc, y * sc), r[1], font=mono(13), fill=dim)
            col = r[3] if mode != "dossier" else ((150, 30, 20) if r[3] == HARM else (24, 20, 26))
            d.text(((x0 + w) * sc, (y - 3) * sc), r[2], font=anton(19) if mode != "terminal" else mono(16), fill=col, anchor="ra")
            y += 22
        elif k == "node":
            glyph_draws.append((r[1], x0 + 12, y + 14, r[4]))
            d.text(((x0 + 30) * sc, y * sc), r[2], font=mono(14), fill=ink)
            d.text(((x0 + 30) * sc, (y + 17) * sc), r[5], font=mono(11), fill=dim)
            f = mono(12)
            tw = f.getlength(r[3]) / sc + 12
            cc = r[4]
            if mode == "terminal":
                d.rectangle([(x0 + w - tw) * sc, (y + 3) * sc, (x0 + w) * sc, (y + 21) * sc], outline=cc, width=max(1, int(sc)))
                d.text(((x0 + w - tw / 2) * sc, (y + 12) * sc), r[3], font=f, fill=cc, anchor="mm")
            elif mode == "dossier":   # rubber stamp
                sc_col = (170, 30, 25) if cc in (HARM, AMBER) else (30, 110, 50) if cc == GREEN else (150, 30, 110)
                d.rectangle([(x0 + w - tw) * sc, (y + 2) * sc, (x0 + w) * sc, (y + 22) * sc], outline=sc_col, width=int(2 * sc))
                d.text(((x0 + w - tw / 2) * sc, (y + 12) * sc), r[3], font=anton(13 * 1.0), fill=sc_col, anchor="mm")
            else:
                d.text(((x0 + w) * sc, (y + 12) * sc), r[3], font=anton(15), fill=cc, anchor="rm")
            y += 38
        elif k == "bar":
            d.text((x0 * sc, y * sc), r[1], font=mono(12), fill=dim)
            bx0, bx1 = x0 + 110, x0 + w
            n = 16
            for i in range(n):
                on = i < round(r[2] * n)
                xa = bx0 + i * (bx1 - bx0) / n
                fill = r[3] if on else ((40, 52, 66) if mode != "dossier" else (200, 194, 180))
                d.rectangle([xa * sc, (y + 3) * sc, (xa + (bx1 - bx0) / n - 2) * sc, (y + 13) * sc], fill=fill)
            y += 22
        elif k == "sep":
            d.line([(x0 * sc, (y + 4) * sc), ((x0 + w) * sc, (y + 4) * sc)], fill=dim, width=1)
            y += 10
        elif k == "route":
            cc = HARM if mode != "dossier" else (170, 30, 25)
            d.ellipse([x0 * sc, y * sc, (x0 + 24) * sc, (y + 24) * sc], outline=cc, width=int(2 * sc))
            d.text(((x0 + 12) * sc, (y + 12) * sc), r[1], font=anton(15), fill=cc, anchor="mm")
            d.text(((x0 + 34) * sc, y * sc), r[2], font=mono(13), fill=ink)
            d.text(((x0 + 34) * sc, (y + 17) * sc), r[3], font=mono(11), fill=dim)
            y += 40
        elif k == "big":
            col = r[2] if mode != "dossier" else (24, 20, 26)
            sz = 34
            while sz > 16 and anton(sz).getlength(r[1]) > w * sc:
                sz -= 1
            d.text((x0 * sc, y * sc), r[1], font=anton(sz), fill=col)
            y += 46
    return glyph_draws


def _paste_glyphs(img, glyph_draws, sc, mode):
    for name, cx, cy, col in glyph_draws:
        size = 22
        g = Image.open(gpath(name)).convert("RGBA").split()[3].resize((int(size * sc), int(size * sc)), Image.LANCZOS)
        c = col if mode != "dossier" else (30, 26, 30)
        lay = Image.new("RGBA", g.size, tuple(c) + (255,))
        lay.putalpha(g)
        img.alpha_composite(lay, (int((cx - size / 2) * sc), int((cy - size / 2) * sc)))


def terminal(title, rows, w=310, accent=CYAN, seed=1):
    """CRT panel, C screens & data language: navy glass, cyan edge, corner brackets, mono, scanlines, hex ghost."""
    h = _measure(rows) + 58
    sc = S
    im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w * sc - 1, h * sc - 1], fill=(5, 13, 28, 232))
    rng = np.random.default_rng(seed)
    fh = F(SL.MONO, 9 * sc)
    for yy in range(28, h - 8, 12):          # faint hex dump behind
        txt = " ".join("%02X" % v for v in rng.integers(0, 256, 22))
        d.text((6 * sc, yy * sc), txt, font=fh, fill=(20, 48, 70, 255))
    d.rectangle([0, 0, w * sc - 1, 24 * sc], fill=(10, 34, 52, 255))
    d.text((10 * sc, 12 * sc), "> " + title, font=F(SL.MONO, 14 * sc), fill=accent, anchor="lm")
    d.rectangle([(w - 18) * sc, 7 * sc, (w - 10) * sc, 17 * sc], fill=accent)          # cursor
    d.rectangle([0, 0, w * sc - 1, h * sc - 1], outline=tuple(int(c * 0.75) for c in accent), width=sc)
    L = 14
    for (cx, cy, sx, sy) in ((0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)):   # corner brackets
        d.line([(cx * sc, cy * sc), ((cx + sx * L) * sc, cy * sc)], fill=accent, width=2 * sc)
        d.line([(cx * sc, cy * sc), (cx * sc, (cy + sy * L) * sc)], fill=accent, width=2 * sc)
    gd = _draw_rows(d, rows, 14, 34, w - 28, "terminal")
    _paste_glyphs(im, gd, sc, "terminal")
    a = np.asarray(im, np.float32) / 255.0
    sl = (np.arange(a.shape[0]) // sc) % 3 == 0                                     # scanlines
    a[sl, :, :3] *= 0.78
    im = Image.fromarray((a * 255).astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS)
    return dict(img=im, kind="terminal")


def dossier(title, rows, w=310, seed=1, stamp=None):
    """A clipped case file under acrylic glass."""
    h = _measure(rows) + 70
    sc = S
    pad = 18
    W, H = w + 2 * pad, h + 2 * pad
    im = Image.new("RGBA", (W * sc, H * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # glass plate (slightly larger than the paper), screws
    d.rounded_rectangle([0, 0, W * sc - 1, H * sc - 1], 10 * sc, fill=(210, 225, 235, 46), outline=(235, 245, 255, 120), width=sc)
    for (x, y) in ((8, 8), (W - 8, 8), (8, H - 8), (W - 8, H - 8)):
        d.ellipse([(x - 4) * sc, (y - 4) * sc, (x + 4) * sc, (y + 4) * sc], fill=(170, 175, 185, 255), outline=(60, 60, 70, 255))
    # paper
    rng = np.random.default_rng(seed)
    paper = Image.new("RGBA", (w * sc, h * sc), (233, 223, 198, 255))
    pd = ImageDraw.Draw(paper)
    n = (rng.random((h * sc // 6 + 1, w * sc // 6 + 1)) * 18).astype(np.uint8)
    grain = Image.fromarray(n).resize((w * sc, h * sc), Image.BICUBIC)
    paper = Image.composite(Image.new("RGBA", paper.size, (210, 198, 170, 255)), paper, grain)
    pd = ImageDraw.Draw(paper)
    pd.rectangle([0, 0, w * sc, 30 * sc], fill=(214, 202, 172, 255))
    pd.text((12 * sc, 15 * sc), title, font=F(SL.MONO, 15 * sc), fill=(30, 26, 30), anchor="lm")
    pd.text(((w - 10) * sc, 15 * sc), "CASE 03-7", font=F(SL.MONO, 10 * sc), fill=(110, 100, 90), anchor="rm")
    gd = _draw_rows(pd, rows, 14, 42, w - 28, "dossier")
    _paste_glyphs(paper, gd, sc, "dossier")
    if stamp:
        st = Image.new("RGBA", (180 * sc, 60 * sc), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rectangle([2 * sc, 2 * sc, 178 * sc, 58 * sc], outline=(175, 25, 25, 200), width=3 * sc)
        sd.text((90 * sc, 30 * sc), stamp, font=F(SL.ANTON, 30 * sc), fill=(175, 25, 25, 200), anchor="mm")
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        paper.alpha_composite(st, ((w - 200) * sc, (h - 110) * sc))
    paper = paper.rotate(-1.2, expand=False, resample=Image.BICUBIC)
    im.alpha_composite(paper, (pad * sc, pad * sc))
    # paperclip
    cx = pad + 40
    for k, (rx, ry) in enumerate(((9, 26), (6, 18))):
        d2 = ImageDraw.Draw(im)
        d2.rounded_rectangle([(cx - rx) * sc, (pad - 12 + k * 4) * sc, (cx + rx) * sc, (pad - 12 + ry * 2 + k * 4) * sc], rx * sc,
                             outline=(150, 155, 165, 255), width=2 * sc)
    # glass sheen band
    a = np.asarray(im, np.float32) / 255.0
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    t = (xx / a.shape[1] * 0.8 + yy / a.shape[0] * 0.5)
    sheen = np.exp(-((t - 0.38) / 0.05) ** 2) * 0.16
    a[..., :3] = a[..., :3] * (1 - sheen[..., None]) + sheen[..., None]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA").resize((W, H), Image.LANCZOS)
    return dict(img=im, kind="dossier")


def holo(title, rows, w=310, col=(120, 230, 255), seed=1):
    """A projected holo readout: translucent, scanlined, chromatic fringe, with its emitter bar and light fan."""
    h = _measure(rows) + 56
    fan = 60
    sc = S
    W, H = w, h + fan
    lay = Image.new("RGBA", (W * sc, H * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w * sc - 1, h * sc - 1], fill=col + (30,), outline=col + (200,), width=sc)
    d.text((12 * sc, 14 * sc), title, font=F(SL.ANTON, 22 * sc), fill=col + (255,), anchor="lm")
    txt = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    gd = _draw_rows(td, rows, 14, 34, w - 28, "holo")
    _paste_glyphs(txt, gd, sc, "holo")
    # chromatic fringe: a red copy left, a blue copy right
    a = np.asarray(txt, np.float32)
    fr = np.zeros_like(a)
    fr[:, :-2 * sc, 0] = a[:, 2 * sc:, 3] * 0.6
    fr[:, 2 * sc:, 2] = a[:, :-2 * sc, 3] * 0.6
    fr[..., 3] = np.maximum(np.roll(a[..., 3], 2 * sc, 1), np.roll(a[..., 3], -2 * sc, 1)) * 0.35
    lay = Image.alpha_composite(lay, Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8), "RGBA"))
    lay = Image.alpha_composite(lay, txt)
    # emitter bar + light fan below
    d = ImageDraw.Draw(lay)
    d.rectangle([(w * 0.3) * sc, (H - 6) * sc, (w * 0.7) * sc, H * sc - 1], fill=(200, 210, 220, 255))
    fan_im = Image.new("L", lay.size, 0)
    ImageDraw.Draw(fan_im).polygon([(0, h * sc), (w * sc, h * sc), (w * 0.7 * sc, (H - 6) * sc), (w * 0.3 * sc, (H - 6) * sc)], fill=70)
    fan_im = fan_im.filter(ImageFilter.GaussianBlur(4 * sc))
    lay = Image.alpha_composite(Image.composite(Image.new("RGBA", lay.size, col + (255,)), Image.new("RGBA", lay.size, (0, 0, 0, 0)), fan_im), lay)
    a = np.asarray(lay, np.float32) / 255.0
    sl = (np.arange(a.shape[0]) // sc) % 3 == 0
    a[sl, :, 3] *= 0.6
    flick = (np.random.default_rng(seed).random(a.shape[0] // (4 * sc) + 1) > 0.94)
    rows_f = np.repeat(flick, 4 * sc)[:a.shape[0]]
    a[rows_f, :, 3] *= 0.4
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA").resize((W, H), Image.LANCZOS)
    return dict(img=im, kind="holo")


def put_panel(img_f, panel, x, y, glow=0.6):
    """Composite a panel at top-left x, y. Terminal and holo glow (additive bloom); dossier casts a shadow."""
    im = panel["img"]
    a = np.asarray(im, np.float32) / 255.0
    h, w = a.shape[:2]
    H, W = img_f.shape[:2]
    x0, y0 = int(x), int(y)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya:
        return img_f
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0]
    out = img_f.copy()
    reg = out[ya:yb, xa:xb]
    al = sub[..., 3:4]
    if panel["kind"] == "dossier":
        sh = Image.fromarray((al[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8))
        sh = np.asarray(sh, np.float32)[..., None] / 255.0 * 0.5
        sh = np.roll(np.roll(sh, 8, 0), 6, 1)
        reg *= 1 - sh
    if panel["kind"] == "holo":
        # the projection dims what is behind it (a light-absorbing scrim) so the readout keeps contrast
        body = Image.fromarray((np.clip(al[..., 0] * 4, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))
        body = np.asarray(body, np.float32)[..., None] / 255.0
        reg *= 1 - 0.62 * body
        reg[:] = reg + sub[..., :3] * al * 1.1
    else:
        reg[:] = reg * (1 - al) + sub[..., :3] * al
    if glow and panel["kind"] != "dossier":
        lum = sub[..., :3] * al * (sub[..., :3].max(axis=2, keepdims=True) > 0.45)
        bl = Image.fromarray((np.clip(lum, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
        reg[:] = reg + np.asarray(bl, np.float32) / 255.0 * glow
    return np.clip(out, 0, 1.2)


# ------------------------------------------------------------------ live: L3 diegetic floats
def shards(img_f, x, y, rng, n=26, col=(255, 90, 70), spread=60, size=13):
    """Binary shards: 0/1 glyphs bursting from a hit point (the combat damage language), with streaks + glow."""
    H, W = img_f.shape[:2]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = F(SL.MONO, size)
    for _ in range(n):
        a = rng.uniform(-math.pi * 0.95, -0.05)
        r = rng.uniform(8, spread)
        px, py = x + math.cos(a) * r, y + math.sin(a) * r * 0.8
        d.line([(x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.4), (px, py)], fill=col + (60,), width=1)
        d.text((px, py), rng.choice(["0", "1"]), font=f, fill=col + (int(rng.uniform(150, 255)),), anchor="mm")
    return _add_layer(img_f, lay, glow=0.8)


def float_number(img_f, x, y, txt, col=(255, 90, 70), size=34):
    H, W = img_f.shape[:2]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = F(SL.ANTON, size)
    d.text((x + 2, y + 2), txt, font=f, fill=(0, 0, 0, 160), anchor="mm")
    d.text((x, y), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=1, stroke_fill=(255, 230, 220, 255))
    return _add_layer(img_f, lay, glow=0.7)


def holo_bar(img_f, x, y, frac, col=(255, 90, 70), w=70, segs=10, label=None):
    H, W = img_f.shape[:2]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(segs):
        on = i < round(frac * segs)
        xa = x - w / 2 + i * w / segs
        d.rectangle([xa, y, xa + w / segs - 2, y + 6], fill=col + ((230,) if on else (55,)))
    d.line([(x - w / 2 - 2, y - 3), (x - w / 2 - 2, y + 9)], fill=col + (200,), width=1)
    if label:
        d.text((x - w / 2, y - 6), label, font=F(SL.MONO, 11), fill=col + (220,), anchor="lb")
    return _add_layer(img_f, lay, glow=0.5)


def _add_layer(img_f, lay, glow=0.6):
    a = np.asarray(lay, np.float32) / 255.0
    al = a[..., 3:4]
    out = img_f * (1 - al) + a[..., :3] * al
    bl = np.asarray(lay.split()[3].filter(ImageFilter.GaussianBlur(5)), np.float32)[..., None] / 255.0
    colm = np.asarray(lay.convert("RGB").filter(ImageFilter.GaussianBlur(5)), np.float32) / 255.0
    return np.clip(out + colm * glow * 1.4 * (bl > 0.01), 0, 1.2)


def speed_terminal(active="2x", step="07 / 30", accent=CYAN):
    """Playout speed controls as a live terminal strip (changes state, so never a sticker)."""
    w, h = 430, 46
    sc = S
    im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w * sc - 1, h * sc - 1], fill=(5, 13, 28, 232), outline=tuple(int(c * 0.75) for c in accent), width=sc)
    x = 10
    for lab in ("1x", "2x", "4x", "SKIP"):
        bw = 52 if lab != "SKIP" else 70
        on = lab == active
        d.rectangle([x * sc, 8 * sc, (x + bw) * sc, 38 * sc], fill=accent if on else (12, 30, 46), outline=accent, width=sc)
        d.text(((x + bw / 2) * sc, 23 * sc), lab, font=F(SL.MONO, 16 * sc), fill=(5, 13, 28) if on else accent, anchor="mm")
        x += bw + 8
    d.text(((x + 8) * sc, 23 * sc), "STEP " + step, font=F(SL.MONO, 15 * sc), fill=(190, 225, 240), anchor="lm")
    return dict(img=im.resize((w, h), Image.LANCZOS), kind="terminal")
