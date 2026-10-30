"""Round 31 UI chrome kit: shared drawing helpers for every board in this round.

Media (DIRECTION_REVIEW, locked):
  STICKER  = vinyl die-cut, for things that never change (screen titles, primary verbs, card names)
  PENCIL   = opaque waxy grease pencil, yellow plans / red threats, true to the rules
  TERMINAL = the Cell's own systems (CRT glass panels, mono type, live numbers)
  PAPER    = intercepted corp documents (typewriter + stamps)
  HOLO     = decrypted corp intel (corp palette, scan bands, seal)
Everything is drawn at 1x on 1920x1080 canvases unless noted; stickers come from sticker_lib31 (SS=2).
All randomness is seeded.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import sticker_lib31 as SL

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # docs/concepts/round44_undesigned/A_map
CONC = os.path.dirname(os.path.dirname(ROOT))
REPO = os.path.dirname(os.path.dirname(CONC))
SCR = os.path.join(ROOT, 'scratch')
GLYPHS = os.path.join(CONC, 'round17_slice_system', 'glyphs')
FONTS = os.path.join(REPO, 'assets', 'fonts')
WINF = 'C:/Windows/Fonts'

# ------------------------------------------------------------------ type stack
ANTON = os.path.join(FONTS, 'Anton-Regular.ttf')                 # OFL 1.1 (repo)
MONO = os.path.join(FONTS, 'ShareTechMono-Regular.ttf')          # OFL 1.1 (repo)
PLEX = os.path.join(FONTS, 'IBMPlexSansCondensed-Regular.ttf')   # OFL 1.1 (repo)
PLEX_M = os.path.join(FONTS, 'IBMPlexSansCondensed-Medium.ttf')  # OFL 1.1 (repo)
MARKER = os.path.join(FONTS, 'PermanentMarker-Regular.ttf')      # Apache 2.0 (repo)
# Paper: Courier Prime (SIL OFL 1.1), kept in this round's fonts/ (fetch_courier_prime.py). Until the files
# are there, Courier New stands in and PRIME is False (boards say so).
ROUND_FONTS = os.path.join(CONC, "round33_ui_chrome", "fonts")
_CP, _CPB = os.path.join(ROUND_FONTS, 'CourierPrime-Regular.ttf'), os.path.join(ROUND_FONTS, 'CourierPrime-Bold.ttf')
PRIME = os.path.exists(_CP) and os.path.exists(_CPB)
COUR = _CP if PRIME else os.path.join(WINF, 'cour.ttf')
COUR_B = _CPB if PRIME else os.path.join(WINF, 'courbd.ttf')
BAHN = os.path.join(WINF, 'bahnschrift.ttf')                     # Windows system font: concept only

_fc = {}


def F(path, size, var=None):
    key = (path, int(size), var)
    if key not in _fc:
        f = ImageFont.truetype(path, int(size))
        if var:
            try:
                f.set_variation_by_name(var)
            except Exception:
                pass
        _fc[key] = f
    return _fc[key]


# ------------------------------------------------------------------ palette
PINK = (255, 61, 168)
LIME = (212, 255, 0)
CYAN = (92, 225, 255)
GREEN = (123, 224, 123)
VIOLET = (200, 90, 255)
HARM = (255, 68, 51)
AMBER = (255, 176, 0)
GOLD = (255, 210, 77)
WHITE = (240, 238, 232)
DIM = (150, 168, 190)
NAVY = (5, 13, 28)
INK = (17, 17, 17)
PAPER = (242, 238, 228)
PAPER_ALT = (233, 228, 214)
PEN_Y = (255, 214, 10)
PEN_R = (236, 34, 40)
CORP = {'meridian': (255, 140, 26), 'solace': (61, 255, 139), 'halcyon': (140, 123, 255),
        'orbital': (127, 168, 255), 'rebel_cell': (232, 20, 30)}
CORP2 = {'meridian': (40, 26, 12), 'solace': (16, 70, 66), 'halcyon': (255, 176, 40),
         'orbital': (210, 240, 255), 'rebel_cell': (20, 8, 8)}


# ------------------------------------------------------------------ basics
class BD:
    """Blending draw for RGBA images: ImageDraw on an RGBA image REPLACES pixels (alpha included),
    so every call here draws on a clear layer (cropped to the canvas) and composites in place."""

    def __init__(self, img):
        self.img = img

    def __getattr__(self, name):
        def f(*a, **k):
            lay = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            getattr(ImageDraw.Draw(lay), name)(*a, **k)
            self.img.alpha_composite(lay)
        return f


def canvas(w=1920, h=1080, col=(12, 10, 18)):
    return Image.new('RGBA', (w, h), col + (255,))


def fit_cover(img, w, h):
    iw, ih = img.size
    k = max(w / iw, h / ih)
    img = img.resize((int(iw * k + 0.5), int(ih * k + 0.5)), Image.LANCZOS)
    x0, y0 = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x0, y0, x0 + w, y0 + h))


def grade(img, dim=0.55, blur=0.0, sat=1.0, tint=None):
    img = img.convert('RGB')
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img, np.float32)
    if sat != 1.0:
        l = a.mean(axis=2, keepdims=True)
        a = l + (a - l) * sat
    a = a * dim
    if tint:
        a = a * 0.85 + np.array(tint, np.float32) * 0.15 * dim
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def vignette(img, k=0.55, cx=0.5, cy=0.5):
    w, h = img.size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x / w - cx) * 1.2) ** 2 + ((y / h - cy)) ** 2)
    m = np.clip(1 - k * d ** 1.6 * 1.8, 0, 1)[..., None]
    a = np.asarray(img.convert('RGB'), np.float32) * m
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return out


def add_glow(img, mask, col, radius=10, k=1.0):
    """Additive light spill from an L mask (glowing base elements spill light)."""
    g = mask.filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(img, np.float32)
    m = np.asarray(g, np.float32)[..., None] / 255 * k
    a[..., :3] = np.clip(a[..., :3] + m * np.array(col, np.float32), 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def over(img, col, mask, alpha=1.0):
    lay = Image.new('RGBA', img.size, tuple(col[:3]) + (0,))
    if alpha != 1.0:
        mask = mask.point(lambda v: int(v * alpha))
    lay.putalpha(mask)
    return Image.alpha_composite(img, lay)


def rect_mask(size, box, r=0, chamfer=0):
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    if chamfer:
        x0, y0, x1, y1 = box
        d.polygon([(x0, y0), (x1 - chamfer, y0), (x1, y0 + chamfer), (x1, y1), (x0 + chamfer * 0.6, y1),
                   (x0, y1 - chamfer * 0.6)], fill=255)
    elif r:
        d.rounded_rectangle(box, r, fill=255)
    else:
        d.rectangle(box, fill=255)
    return m


def shadow(img, mask, off=(6, 10), blur=12, k=0.6):
    sh = SL.shift(mask, *off).filter(ImageFilter.GaussianBlur(blur))
    return over(img, (3, 2, 8), sh, k)


def text(img, xy, s, font, fill, anchor='la', track=0.0, alpha=255):
    """Draw text with optional tracking (px between glyphs). Returns end x."""
    if alpha < 255:
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        r = text(lay, xy, s, font, fill, anchor, track, 255)
        lay.putalpha(lay.split()[3].point(lambda v: v * alpha // 255))
        img.alpha_composite(lay)
        return r
    d = ImageDraw.Draw(img)
    col = tuple(fill[:3]) + (255,)
    if not track:
        d.text(xy, s, font=font, fill=col, anchor=anchor)
        return xy[0] + font.getlength(s)
    total = sum(font.getlength(c) for c in s) + track * (len(s) - 1)
    x, y = xy
    if anchor[0] == 'm':
        x -= total / 2
    elif anchor[0] == 'r':
        x -= total
    a2 = 'l' + anchor[1]
    for c in s:
        d.text((x, y), c, font=font, fill=col, anchor=a2)
        x += font.getlength(c) + track
    return x


def live_number(img, xy, s, size, col, anchor='lm', track=1.2, glow=0.5):
    """Live values (HP, damage, Heat no.): bare Anton, 2 px dark rim, soft own-colour glow. Never a sticker."""
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text(lay, xy, s, F(ANTON, size), (255, 255, 255), anchor, track)
    m = lay.split()[3]
    rim = SL.dilate(m, 2)
    img2 = add_glow(img, m, col, 10, glow)
    img2 = over(img2, (6, 6, 10), rim, 0.9)
    img2 = over(img2, col, m)
    img.paste(img2)
    return img


def tw(s, font, track=0.0):
    return sum(font.getlength(c) for c in s) + track * max(0, len(s) - 1) if track else font.getlength(s)


# ------------------------------------------------------------------ glyphs
_gc = {}


def glyph(name, size, col=(255, 255, 255)):
    key = (name, size, col)
    if key not in _gc:
        g = Image.open(os.path.join(GLYPHS, name + '.png')).convert('RGBA').resize((size, size), Image.LANCZOS)
        lay = Image.new('RGBA', g.size, col + (0,))
        lay.putalpha(g.split()[3])
        _gc[key] = lay
    return _gc[key]


def paste_glyph(img, name, xy, size, col=(255, 255, 255), anchor='mm'):
    g = glyph(name, size, col)
    x, y = xy
    if anchor == 'mm':
        x, y = x - size // 2, y - size // 2
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    lay.paste(g, (int(x), int(y)))
    return Image.alpha_composite(img, lay)


# ------------------------------------------------------------------ TERMINAL (the Cell's systems)
HEX = '0123456789ABCDEF'


def term_panel(img, box, title=None, accent=CYAN, tag=None, tag_col=None, alpha=236, hexbg=True, seed=1,
               chamfer=16, header=True, glow=0.35, scan=0.10, edge_w=2):
    """Navy CRT glass, accent edge, '> TITLE' header strip, scanlines, faint hex dump, light spill."""
    x0, y0, x1, y1 = [int(v) for v in box]
    W, H = img.size
    m = rect_mask((W, H), (x0, y0, x1, y1), chamfer=chamfer)
    img = shadow(img, m, (5, 8), 10, 0.55)
    img = over(img, NAVY, m, alpha / 255)
    # inner gradient (top a touch lighter: CRT glass)
    gl = Image.new('L', (W, H), 0)
    ImageDraw.Draw(gl).rectangle([x0, y0, x1, y0 + (y1 - y0) // 3], fill=26)
    gl = ImageChops.multiply(gl.filter(ImageFilter.GaussianBlur((y1 - y0) / 6)), m)
    img = over(img, accent, gl, 0.6)
    rng = random.Random(seed)
    if hexbg:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        f = F(MONO, 12)
        for yy in range(y0 + (34 if header and title else 8), y1 - 8, 15):
            s = ' '.join(''.join(rng.choice(HEX) for _ in range(2)) for _ in range(int((x1 - x0 - 16) / 22)))
            d.text((x0 + 10, yy), s, font=f, fill=accent + (14,))
        lay.putalpha(ImageChops.multiply(lay.split()[3], m))
        img = Image.alpha_composite(img, lay)
    # scanlines
    sl = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(sl)
    for yy in range(y0, y1, 3):
        d.line([(x0, yy), (x1, yy)], fill=int(255 * scan))
    img = over(img, (0, 0, 0), ImageChops.multiply(sl, m))
    # edge + spill
    e = ImageChops.subtract(m, SL.erode(m, edge_w))
    if glow:
        img = add_glow(img, e, accent, 9, glow)
    img = over(img, accent, e, 0.8)
    d = BD(img)
    if header and title:
        hy = y0 + 30
        d.rectangle([x0 + 2, y0 + 2, x1 - chamfer - 2, hy], fill=accent + (34,))
        d.line([(x0 + 2, hy), (x1 - 2, hy)], fill=accent + (150,), width=1)
        text(img, (x0 + 12, y0 + 17), '> ' + title, F(MONO, 18), accent, 'lm', track=1.4)
        d.rectangle([x1 - chamfer - 20, y0 + 10, x1 - chamfer - 10, y0 + 20], fill=accent + (220,))
        if tag:
            tc = tag_col or accent
            f = F(MONO, 15)
            twd = tw(tag, f, 1.0)
            d.rectangle([x1 - chamfer - 34 - twd - 12, y0 + 7, x1 - chamfer - 30, y0 + 25], outline=tc + (230,), width=1)
            text(img, (x1 - chamfer - 36 - twd - 6, y0 + 16), tag, f, tc, 'lm', track=1.0)
    # corner ticks bottom-left
    d.line([(x0 + 6, y1 - 6), (x0 + 22, y1 - 6)], fill=accent + (200,), width=2)
    d.line([(x0 + 6, y1 - 6), (x0 + 6, y1 - 22)], fill=accent + (200,), width=2)
    return img


def focus_brackets(img, box, col=LIME, gap=7, ln=16, w=3, glow=True):
    """Keyboard / pad focus: four lime corner brackets just outside the element (always visible)."""
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 - gap, y0 - gap, x1 + gap, y1 + gap
    m = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(m)
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * ln, cy)], fill=255, width=w)
        d.line([(cx, cy), (cx, cy + sy * ln)], fill=255, width=w)
    sh = SL.shift(m, 1, 2).filter(ImageFilter.GaussianBlur(1.2))
    img = over(img, (0, 0, 0), sh, 0.8)
    if glow:
        img = add_glow(img, m, col, 6, 0.7)
    return over(img, col, m)


def term_button(img, box, label, sub=None, state='idle', accent=CYAN, key=None):
    """Secondary button: terminal chip. States idle / hover / pressed / disabled / focus."""
    x0, y0, x1, y1 = box
    if state == 'pressed':
        x0, y0, x1, y1 = x0 + 1, y0 + 2, x1 + 1, y1 + 2
    W, H = img.size
    m = rect_mask((W, H), (x0, y0, x1, y1), chamfer=8)
    dis = state == 'disabled'
    ac = (92, 100, 116) if dis else accent
    if state != 'pressed':
        img = shadow(img, m, (3, 5), 5, 0.5)
    fill_a = {'idle': 0.88, 'hover': 0.92, 'focus': 0.92, 'pressed': 1.0, 'disabled': 0.8}[state]
    img = over(img, NAVY if state != 'pressed' else tuple(int(c * 0.85) for c in accent), m, fill_a)
    if state in ('hover', 'focus'):
        hl = ImageChops.multiply(m, Image.new('L', (W, H), 46))
        img = over(img, accent, hl)
    if dis:
        hatch = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(hatch)
        for k in range(x0 - (y1 - y0), x1, 9):
            d.line([(k, y1), (k + (y1 - y0), y0)], fill=40, width=2)
        img = over(img, (160, 170, 190), ImageChops.multiply(hatch, m))
    e = ImageChops.subtract(m, SL.erode(m, 2))
    if state in ('hover', 'focus'):
        img = add_glow(img, e, accent, 8, 0.8)
    img = over(img, ac, e, 1.0 if state != 'idle' else 0.75)
    tc = INK if state == 'pressed' else ((110, 118, 132) if dis else WHITE)
    f = F(MONO, 22)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2 - (8 if sub else 0)
    lab = ('> ' + label) if state in ('hover', 'focus') else label
    text(img, (cx, cy), lab, f, tc, 'mm', track=1.5)
    if sub:
        sc = INK if state == 'pressed' else ((96, 104, 118) if dis else accent)
        text(img, (cx, cy + 20), sub, F(MONO, 14), sc, 'mm', track=1.2)
    if state == 'focus':
        img = focus_brackets(img, (x0, y0, x1, y1), gap=6, ln=12, w=3)
    return img


def toggle(img, xy, on, state='idle', accent=CYAN):
    """Pill switch, ON = cyan fill + 'ON' word (never colour alone)."""
    x, y = xy
    w, h = 64, 28
    box = (x, y, x + w, y + h)
    d = BD(img)
    dis = state == 'disabled'
    ac = (92, 100, 116) if dis else accent
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, h // 2, fill=255)
    img = over(img, ac if on else (26, 32, 46), m, 0.92 if on else 0.95)
    e = ImageChops.subtract(m, SL.erode(m, 2))
    if on and not dis:
        img = add_glow(img, e, accent, 8, 0.6)
    img = over(img, ac if not on else tuple(min(255, c + 40) for c in ac), e)
    d = BD(img)
    kx = x + w - h // 2 if on else x + h // 2
    d.ellipse([kx - 10, y + 4, kx + 10, y + h - 4], fill=(250, 250, 248) if not dis else (140, 146, 156))
    f = F(MONO, 14)
    if on:
        text(img, (x + 18, y + h / 2 + 1), 'ON', f, NAVY, 'mm', 0.5)
    else:
        text(img, (x + w - 20, y + h / 2 + 1), 'OFF', f, (140, 150, 170), 'mm', 0.5)
    if state == 'focus':
        img = focus_brackets(img, box, gap=6, ln=10, w=3)
    if state == 'hover':
        img = add_glow(img, e, WHITE, 6, 0.35)
    return img


def slider(img, box, value, ticks=(), state='idle', accent=CYAN, readout=None, labels=None):
    """Terminal slider: tick track, cyan fill, a notched handle, mono readout."""
    x0, y0, x1, y1 = box
    cy = (y0 + y1) // 2
    d = BD(img)
    dis = state == 'disabled'
    ac = (92, 100, 116) if dis else accent
    d.rectangle([x0, cy - 3, x1, cy + 3], fill=(26, 34, 50, 240), outline=ac + (120,))
    xv = x0 + (x1 - x0) * value
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rectangle([x0, cy - 3, xv, cy + 3], fill=255)
    if not dis:
        img = add_glow(img, m, accent, 6, 0.6)
    img = over(img, ac, m)
    d = BD(img)
    for i, t in enumerate(ticks):
        tx = x0 + (x1 - x0) * t
        d.line([(tx, cy + 8), (tx, cy + 16)], fill=ac + (200,), width=2)
        if labels:
            text(img, (tx, cy + 28), labels[i], F(MONO, 14), DIM if not dis else (96, 104, 118), 'mm', 0.8)
    hb = (xv - 8, cy - 15, xv + 8, cy + 15)
    hm = Image.new('L', img.size, 0)
    ImageDraw.Draw(hm).rectangle(hb, fill=255)
    img = shadow(img, hm, (2, 3), 3, 0.6)
    d = BD(img)
    d.rectangle(hb, fill=(248, 248, 244) if not dis else (140, 146, 156), outline=NAVY + (255,))
    d.line([(xv, cy - 8), (xv, cy + 8)], fill=NAVY + (255,), width=2)
    if readout:
        text(img, (x1 + 18, cy), readout, F(MONO, 22), WHITE if not dis else (110, 118, 132), 'lm', 1.0)
    if state == 'focus':
        img = focus_brackets(img, (hb[0] - 2, hb[1] - 2, hb[2] + 2, hb[3] + 2), gap=5, ln=8, w=3)
    return img


def tabs(img, xy, names, active, states=None, accent=CYAN, gap=4):
    """Terminal tabs: active = filled header + lime underline is NOT used (lime = focus); active is
    an accent block with dark text, hover is an outline, locked is '???' hatched."""
    x, y = xy
    h = 40
    f = F(MONO, 20)
    states = states or {}
    boxes = []
    for i, n in enumerate(names):
        st = states.get(i, 'active' if i == active else 'idle')
        w = int(tw(n, f, 1.6)) + 36
        box = (x, y, x + w, y + h)
        m = rect_mask(img.size, box, chamfer=8)
        if st == 'active':
            img = over(img, accent, m, 0.95)
            text(img, (x + w / 2, y + h / 2), n, f, NAVY, 'mm', 1.6)
        else:
            img = over(img, NAVY, m, 0.9)
            e = ImageChops.subtract(m, SL.erode(m, 2))
            c = (90, 98, 112) if st == 'locked' else accent
            img = over(img, c, e, 1.0 if st in ('hover', 'focus') else 0.45)
            if st in ('hover', 'focus'):
                img = add_glow(img, e, accent, 6, 0.5)
            tc = (100, 108, 122) if st == 'locked' else (WHITE if st in ('hover', 'focus') else DIM)
            text(img, (x + w / 2, y + h / 2), n, f, tc, 'mm', 1.6)
            if st == 'focus':
                img = focus_brackets(img, box, gap=5, ln=10, w=3)
        boxes.append(box)
        x += w + gap
    d = BD(img)
    d.line([(xy[0], y + h + 1), (x - gap, y + h + 1)], fill=accent + (200,), width=2)
    return img, boxes


# ------------------------------------------------------------------ STICKERS (things that never change)
FILL_PINK = ('grad', (255, 128, 204), (236, 28, 140))
FILL_YELLOW = ('grad', (255, 238, 96), (255, 182, 14))
FILL_LIME = ('grad', (232, 255, 90), (186, 230, 0))
FILL_CYAN = ('grad', (150, 240, 255), (60, 196, 240))
FILL_GREY = ('grad', (178, 176, 182), (128, 126, 134))
FILL_INK = ('grad', (40, 36, 48), (14, 12, 18))
FILL_CALM = ('grad', (84, 92, 110), (36, 40, 52))       # round 32: the calm sticker (CANCEL, safe choices)


def sticker(lines, size=96, fill=FILL_PINK, seed=7, jitter=2.5, border=12, gloss_k=0.22, gloss_pos=0.32,
            curl=None, key_w=5, extrude=7, material='gloss', track=-1, font_path=None):
    art = SL.lettering(lines if isinstance(lines, list) else [lines], size, [fill], key_w=key_w, extrude=extrude,
                       seed=seed, jitter=jitter, track=track, font_path=font_path or ANTON)
    return SL.build_sticker(art, border=border, gloss_k=gloss_k, gloss_pos=gloss_pos, curl=curl, seed=seed,
                            material=material)


def grey_sticker(sd, k=0.8):
    img = sd['img']
    a = img.split()[3]
    g = img.convert('L').convert('RGBA')
    g = Image.blend(g, Image.new('RGBA', g.size, (150, 150, 156, 255)), 0.15)
    g.putalpha(a.point(lambda v: int(v * k)))
    out = dict(sd)
    out['img'] = g
    return out


def focus_sticker(sd, col=LIME):
    """Focus on a sticker: a lime die-cut halo 4 px outside the cut line (same silhouette)."""
    S = SL.SS
    body = sd['img'].split()[3].point(lambda v: 255 if v > 60 else 0)
    ring = ImageChops.subtract(SL.dilate(body, 9 * S), SL.dilate(body, 4 * S))
    lay = Image.new('RGBA', body.size, col + (0,))
    lay.putalpha(ring)
    glow = Image.new('RGBA', body.size, col + (0,))
    glow.putalpha(ring.filter(ImageFilter.GaussianBlur(5 * S)).point(lambda v: int(v * 0.8)))
    img = Image.alpha_composite(Image.alpha_composite(glow, lay), sd['img'])
    out = dict(sd)
    out['img'] = img
    return out


def place(img, sd, cx, cy, **kw):
    return SL.place(img, sd, cx, cy, **kw)


# ------------------------------------------------------------------ GREASE PENCIL (plans / threats)
class Pencil(SL.Pen):
    """Opaque waxy grease pencil: thick, saturated, a dark under-shadow so it reads day and night."""

    def ink(self, canvas, shadow=0.85):
        m1 = self.mask.resize(self.size, Image.LANCZOS)
        sh = SL.shift(m1, 2, 3).filter(ImageFilter.GaussianBlur(2.0))
        canvas = SL.over(canvas, (6, 3, 8), SL.scale_mask(sh, shadow))
        lay = Image.new('RGBA', self.size, self.color + (0,))
        lay.putalpha(m1)
        canvas = Image.alpha_composite(canvas, lay)
        # wax: grain drop-outs + a soft satin edge
        rng = np.random.default_rng(self.rng.randint(0, 999))
        n = rng.random((self.size[1] // 2 + 1, self.size[0] // 2 + 1))
        nimg = Image.fromarray((np.clip((n - 0.86) * 6, 0, 1) * 255).astype(np.uint8)).resize(self.size)
        canvas = SL.over(canvas, tuple(int(c * 0.72) for c in self.color), SL.mul(SL.scale_mask(nimg, 0.55), m1))
        hl = ImageChops.subtract(m1, SL.shift(m1, 1, 2)).filter(ImageFilter.GaussianBlur(0.5))
        canvas = SL.over(canvas, (255, 255, 255), SL.mul(SL.scale_mask(hl, 0.3), m1))
        return canvas


# ------------------------------------------------------------------ PAPER (intercepted corp documents)
def paper_tex(w, h, seed=3, col=PAPER, fold=True):
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)
    n = rng.normal(0, 1, (h // 3 + 1, w // 3 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) - 128
    base += n[..., None] * 0.25
    g = rng.normal(0, 5, (h, w)).astype(np.float32)
    base += g[..., None]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    v = 1 - 0.07 * (((x / w - 0.5) * 2) ** 2 + ((y / h - 0.5) * 2) ** 2)
    base *= v[..., None]
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = random.Random(seed)
    for _ in range(int(w * h / 1800)):
        x0, y0 = r.uniform(0, w), r.uniform(0, h)
        a = r.uniform(0, math.pi)
        l = r.uniform(3, 9)
        d.line([(x0, y0), (x0 + math.cos(a) * l, y0 + math.sin(a) * l)], fill=(150, 140, 120, r.randint(18, 40)))
    if fold:
        fy = int(h * 0.48)
        d.line([(0, fy), (w, fy)], fill=(255, 255, 255, 70), width=2)
        d.line([(0, fy + 2), (w, fy + 2)], fill=(120, 110, 90, 40), width=1)
    img.alpha_composite(lay)
    return img


def paper_panel(img, box, seed=3, angle=0.0, col=PAPER, clip=True):
    """Returns (img, paper layer, origin): caller draws on the layer then calls paste_paper."""
    x0, y0, x1, y1 = box
    p = paper_tex(x1 - x0, y1 - y0, seed, col)
    return p


def paste_paper(img, p, xy, angle=0.0, sh=0.7):
    pr = p.rotate(angle, Image.BICUBIC, expand=True)
    x, y = xy
    x -= (pr.width - p.width) // 2
    y -= (pr.height - p.height) // 2
    full = Image.new('L', img.size, 0)
    full.paste(pr.split()[3], (int(x), int(y)))
    img = shadow(img, full, (8, 12), 14, sh)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    lay.paste(pr, (int(x), int(y)))
    return Image.alpha_composite(img, lay)


def rubber_stamp(s, size, col, angle=-8, seed=5, box=True, font=None, pad=14):
    f = F(font or ANTON, size)
    tw_ = f.getlength(s)
    w, h = int(tw_ + pad * 2 + 12), int(size * 1.3 + pad)
    m = Image.new('L', (w + 20, h + 20), 0)
    d = ImageDraw.Draw(m)
    d.text(((w + 20) / 2, (h + 20) / 2), s, font=f, fill=255, anchor='mm')
    if box:
        d.rectangle([10, 10, w + 10, h + 10], outline=255, width=max(3, size // 12))
        d.rectangle([16, 16, w + 4, h + 4], outline=255, width=1)
    rng = np.random.default_rng(seed)
    n = rng.random((m.height, m.width))
    n2 = np.asarray(Image.fromarray((rng.random((m.height // 6 + 1, m.width // 6 + 1)) * 255).astype(np.uint8))
                    .resize(m.size, Image.BICUBIC), np.float32) / 255
    a = np.asarray(m, np.float32) / 255
    a = a * (n > 0.18) * (0.55 + 0.45 * (n2 > 0.32))
    out = Image.new('RGBA', m.size, col + (0,))
    out.putalpha(Image.fromarray((a * 235).astype(np.uint8)))
    return out.rotate(angle, Image.BICUBIC, expand=True)


def paste_rgba(img, lay, xy, anchor='mm'):
    x, y = xy
    if anchor == 'mm':
        x, y = x - lay.width // 2, y - lay.height // 2
    full = Image.new('RGBA', img.size, (0, 0, 0, 0))
    full.paste(lay, (int(x), int(y)))
    return Image.alpha_composite(img, full)


# ------------------------------------------------------------------ HOLO (decrypted corp intel)
def holo_panel(img, box, corp='halcyon', title=None, seed=4, alpha=0.78, decrypted=True):
    x0, y0, x1, y1 = box
    col = CORP[corp]
    W, H = img.size
    m = rect_mask((W, H), box, chamfer=0)
    dark = tuple(int(c * 0.16) for c in col)
    img = over(img, dark, m, alpha)
    # scan bands + fine lines
    sl = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(sl)
    for yy in range(y0, y1, 4):
        d.line([(x0, yy), (x1, yy)], fill=30)
    rng = random.Random(seed)
    for _ in range(4):
        by = rng.randint(y0, y1 - 12)
        d.rectangle([x0, by, x1, by + rng.randint(3, 10)], fill=44)
    img = over(img, col, ImageChops.multiply(sl, m))
    # chromatic edge
    e = ImageChops.subtract(m, SL.erode(m, 2))
    img = over(img, (255, 60, 200), SL.shift(e, -2, 0), 0.45)
    img = over(img, (60, 230, 255), SL.shift(e, 2, 0), 0.45)
    img = add_glow(img, e, col, 10, 0.6)
    img = over(img, col, e)
    d = BD(img)
    # projector corner marks
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx + sx * 4, cy + sy * 4), (cx + sx * 26, cy + sy * 4)], fill=col + (255,), width=3)
        d.line([(cx + sx * 4, cy + sy * 4), (cx + sx * 4, cy + sy * 26)], fill=col + (255,), width=3)
    if title:
        text(img, (x0 + 16, y0 + 22), title, F(BAHN, 22, 'Bold'), tuple(min(255, c + 60) for c in col), 'lm', 1.5)
    return img


def corp_seal(img, xy, r, corp='halcyon', label='HALCYON CIVIC'):
    col = CORP[corp]
    x, y = xy
    d = BD(img)
    d.ellipse([x - r, y - r, x + r, y + r], outline=col + (230,), width=3)
    d.ellipse([x - r + 7, y - r + 7, x + r - 7, y + r - 7], outline=col + (160,), width=1)
    f = F(MONO, max(9, r // 4))
    for i, ch in enumerate((label + ' * ') * 2):
        a = -math.pi / 2 + i * 2 * math.pi / (len(label + ' * ') * 2)
        rr = r - 14
        lay = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((15, 15), ch, font=f, fill=col + (220,), anchor='mm')
        lay = lay.rotate(-math.degrees(a) - 90, Image.BICUBIC)
        img.alpha_composite(lay, (int(x + rr * math.cos(a) - 15), int(y + rr * math.sin(a) - 15)))
    # the Halcyon eye
    d = BD(img)
    ir = r * 0.42
    d.ellipse([x - ir, y - ir * 0.55, x + ir, y + ir * 0.55], outline=col + (255,), width=3)
    d.ellipse([x - ir * 0.32, y - ir * 0.32, x + ir * 0.32, y + ir * 0.32], fill=col + (255,))
    return img


# ------------------------------------------------------------------ misc
def caption(img, xy, s, col=(170, 168, 180), size=16, anchor='la'):
    return text(img, xy, s, F(MONO, size), col, anchor, 0.8)


def header_bar(img, title, sub=None):
    d = BD(img)
    text(img, (28, 22), title, F(ANTON, 40), WHITE, 'la', 0.8)
    if sub:
        text(img, (30, 76), sub, F(MONO, 17), (160, 160, 176), 'la', 0.6)
    return img


def label_tag(img, xy, s, col=PINK, size=18):
    """Section label on boards: a coloured bar + mono caps."""
    x, y = xy
    d = BD(img)
    d.rectangle([x, y + 2, x + 5, y + size + 4], fill=col + (255,))
    text(img, (x + 13, y), s, F(BAHN, size + 2, 'Bold'), WHITE, 'la', 0.8)
    return img
