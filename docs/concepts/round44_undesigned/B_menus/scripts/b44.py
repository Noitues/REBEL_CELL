"""Round 44 B (menu screens): shared helpers.

Everything locked is REUSED, imported in place (no bytecode is written into earlier rounds):
  round33_ui_chrome/scripts/ui31.py + sticker_lib31.py  terminal panel, tabs, toggles, tiles, stickers, pencil, holo
  round33_ui_chrome/scripts/settings.py                 the round 31 options board (tiles helper)
  round34_firmware_daemons/scripts/r31lib.py            card_sticker (the C-C card face the build exports)
  round33 cm.py + roads.py (via city_plate.py)          the title's lit night city
  round41_wheel_stack/combat_typical_v4.png             the locked D4 player wheel (cropped, never redrawn)
Build assets read (read only) from D:/Godot/rebel_cell/assets: corp crests, glyph masters, crew busts.

Designer rulings (round 44 brief change) applied here:
  * focus/hover on a sticker = the peel-back corner curl only (no lime halo on stickers);
  * the rainbow gloss sweep is scheduled: at most ONE sticker mid-sweep per screen (sweep=True);
  * terminal rows keep lime brackets + '>' caret for focus (lime = focus only).
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)                                  # .../round44_undesigned/B_menus
CONC = os.path.dirname(os.path.dirname(B))                 # docs/concepts
SCR = os.path.join(B, 'scratch')
os.makedirs(SCR, exist_ok=True)
sys.path.append(os.path.join(CONC, 'round33_ui_chrome', 'scripts'))
sys.path.append(os.path.join(CONC, 'round34_firmware_daemons', 'scripts'))

import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import sticker_lib31 as SL  # noqa: E402
import ui31 as U  # noqa: E402
import r31lib as R  # noqa: E402

BUILD = 'D:/Godot/rebel_cell'
BA = BUILD + '/assets'
W, H = 1920, 1080
LINER = (247, 247, 242)          # white liner #F7F7F2 (round 32 loot sheet)

# ------------------------------------------------------------------ backdrops
_city = None


def city_backdrop(dim=0.56, blur=5, sat=0.85):
    """The title's lit 3D night city, blurred and dimmed (the world sits behind the panel)."""
    global _city
    if _city is None:
        p = os.path.join(SCR, 'city_f00.png')
        if not os.path.exists(p):
            import city_plate
            city_plate.main()
        _city = Image.open(p).convert('RGB')
    img = U.grade(_city, dim, blur, sat)
    return U.vignette(img, 0.5)


def combat_backdrop(dim=0.34, blur=6, sat=0.6):
    src = Image.open(os.path.join(CONC, 'round41_wheel_stack', 'combat_typical_v4.png')).convert('RGB')
    img = U.grade(src, dim, blur, sat)
    return U.vignette(img, 0.5)


def darken(img, box, k=0.5, blur=40):
    """Soft scrim pool under a panel (concept: world drops to ~55 % around the UI)."""
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=int(255 * k))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    return U.over(img, (3, 2, 8), m)


# ------------------------------------------------------------------ stickers (rulings)
def rainbow_sweep(sd, pos=0.42, k=0.7, width=0.045):
    """The scheduled sweep: a diagonal band whose hue runs through the spectrum across its width (rainbow
    gloss), with a bright white core, clipped to the die-cut. Only one sticker per screen carries it."""
    import colorsys
    img = sd['img']
    w, h = img.size
    body = sd['body']
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ca, sa = math.cos(math.radians(28)), math.sin(math.radians(28))
    t = (xx * ca + yy * sa) / (w * ca + h * sa)
    d = (t - pos) / width
    a = np.exp(-d ** 2) * k
    hue = np.clip(d * 0.28 + 0.5, 0, 1)
    lut = np.array([colorsys.hsv_to_rgb(v, 0.55, 1.0) for v in np.linspace(0, 0.85, 256)], np.float32) * 255
    rgb = lut[(hue * 255).astype(np.int32)]
    lay = Image.fromarray(np.dstack([rgb, a[..., None] * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
    lay.putalpha(SL.mul(lay.split()[3], body))
    out = Image.alpha_composite(img, lay)
    core = Image.fromarray((np.exp(-((t - pos) / 0.008) ** 2) * 230).astype(np.uint8))
    out = SL.over(out, (255, 255, 255), SL.mul(core, body))
    sd = dict(sd)
    sd['img'] = out
    return sd


def stk(word, size=60, fill=None, seed=7, focus=False, sweep=False, curl_corner='tr', gloss_k=0.22, curl_px=34, **kw):
    """Sticker word. focus -> peel-back corner curl (designer ruling). sweep -> rainbow gloss mid-sweep."""
    fill = fill or U.FILL_PINK
    sd = U.sticker(word, size, fill, seed=seed, gloss_k=gloss_k, **kw)
    if sweep:
        sd = rainbow_sweep(sd)
    if focus:
        x0, y0, x1, y1 = sd['body'].getbbox()
        L = math.hypot((x1 - x0) / 2, (y1 - y0) / 2)
        sd = SL.apply_curl(sd, corner=curl_corner, amount=min(0.3, curl_px * SL.SS / L))
    return sd


def sw(sd):
    """Width/height of a sticker at 1x."""
    return sd['img'].width / SL.SS, sd['img'].height / SL.SS


def place(img, sd, cx, cy, angle=0.0, focus=False, **kw):
    if focus:
        kw.setdefault('hover', 0.35)
    return SL.place(img, sd, cx, cy, angle=angle, **kw)


# ------------------------------------------------------------------ crests / glyphs / busts
_cc = {}


def crest(corp, size, col=(255, 255, 255)):
    key = (corp, size, col)
    if key not in _cc:
        a = Image.open('%s/wheel/glyphs_interim/crest_%s.png' % (BA, corp)).convert('RGBA').split()[3]
        a = a.resize((size, size), Image.LANCZOS)
        lay = Image.new('RGBA', (size, size), col + (0,))
        lay.putalpha(a)
        _cc[key] = lay
    return _cc[key]


def master(name, size, col=(255, 255, 255)):
    """Glyph from the build's atlas masters (the art pass's own export)."""
    key = ('m', name, size, col)
    if key not in _cc:
        p = '%s/glyphs/masters/%s.png' % (BA, name)
        if not os.path.exists(p):
            p = os.path.join(CONC, 'round17_slice_system', 'glyphs', name + '.png')
        a = Image.open(p).convert('RGBA').split()[3].resize((size, size), Image.LANCZOS)
        lay = Image.new('RGBA', (size, size), col + (0,))
        lay.putalpha(a)
        _cc[key] = lay
    return _cc[key]


def paste_at(img, lay, x, y):
    full = Image.new('RGBA', img.size, (0, 0, 0, 0))
    full.paste(lay, (int(x), int(y)))
    return Image.alpha_composite(img, full)


def glyph_tile(img, x, y, name, col, size=26, pad=5, crest_corp=None):
    """Tooltip glyph row tile: a navy chip with an accent edge, the glyph at 26 px (round 31 tooltip rows)."""
    s = size + 2 * pad
    d = U.BD(img)
    d.rectangle([x, y, x + s, y + s], fill=(8, 18, 34, 255), outline=col + (200,), width=1)
    g = crest(crest_corp, size, col) if crest_corp else master(name, size, col)
    return paste_at(img, g, x + pad, y + pad)


def bust(cls, size, grey=False, frame=0):
    sheet = Image.open('%s/portraits/busts_%s.png' % (BA, cls)).convert('RGBA')
    cw, ch = sheet.width // 4, sheet.height // 4
    c = sheet.crop((frame * cw, 0, frame * cw + cw, ch))
    c = c.crop((10, 0, cw - 10, ch - 20)).resize((size, int(size * (ch - 20) / (cw - 20))), Image.LANCZOS)
    if grey:
        a = c.split()[3]
        c = c.convert('L').convert('RGBA')
        c = Image.blend(c, Image.new('RGBA', c.size, (40, 46, 60, 255)), 0.45)
        c.putalpha(a)
    return c


# ------------------------------------------------------------------ holo chip (intel on a corp)
def holo_chip(img, box, corp, seed=3):
    """Small decrypted-intel chip: corp tint 78 %, 4 px scan lines, RGB-split edge, the crest."""
    x0, y0, x1, y1 = box
    col = U.CORP[corp]
    m = U.rect_mask(img.size, box)
    img = U.over(img, tuple(int(c * 0.18) for c in col), m, 0.9)
    sl = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(sl)
    for yy in range(y0, y1, 4):
        d.line([(x0, yy), (x1, yy)], fill=40)
    rng = random.Random(seed)
    by = rng.randint(y0 + 4, y1 - 10)
    d.rectangle([x0, by, x1, by + 4], fill=70)
    img = U.over(img, col, ImageChops.multiply(sl, m))
    e = ImageChops.subtract(m, SL.erode(m, 1))
    img = U.over(img, (255, 60, 200), SL.shift(e, -2, 0), 0.6)
    img = U.over(img, (60, 230, 255), SL.shift(e, 2, 0), 0.6)
    img = U.add_glow(img, e, col, 6, 0.5)
    img = U.over(img, col, e)
    s = int(min(x1 - x0, y1 - y0) * 0.68)
    cr = crest(corp, s, tuple(min(255, c + 70) for c in col))
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    glow.paste(cr, (int((x0 + x1 - s) / 2), int((y0 + y1 - s) / 2)))
    img = U.add_glow(img, glow.split()[3], col, 5, 0.7)
    return Image.alpha_composite(img, glow)


# ------------------------------------------------------------------ terminal bits
def term_row(img, box, label, focus=False, key=None, accent=U.CYAN, harm=False, sub=None, size=24, caret=True):
    """A menu line: '>' caret + mono caps. Focus = cyan wash + lime brackets + lime caret.
    harm = HARM-edged row (destructive)."""
    x0, y0, x1, y1 = box
    ac = U.HARM if harm else accent
    m = U.rect_mask(img.size, box, chamfer=8)
    if harm:
        img = U.over(img, ac, m, 0.08)
        e = ImageChops.subtract(m, SL.erode(m, 2))
        img = U.over(img, ac, e, 0.85)
    if focus:
        img = U.over(img, ac, m, 0.12)
        img = U.focus_brackets(img, box, gap=4, ln=12)
    cy = (y0 + y1) / 2 - (9 if sub else 0)
    tc = (255, 150, 140) if harm else U.WHITE
    if caret:
        U.text(img, (x0 + 14, cy), '>', U.F(U.MONO, size), U.LIME if focus else (ac if harm else (90, 140, 170)), 'lm')
    U.text(img, (x0 + 44, cy), label, U.F(U.MONO, size), tc, 'lm', 1.6)
    if sub:
        U.text(img, (x0 + 44, cy + 24), sub, U.F(U.MONO, 15), (140, 160, 184) if not harm else (230, 120, 110), 'lm', 0.6)
    if key:
        U.text(img, (x1 - 14, (y0 + y1) / 2), key, U.F(U.MONO, 16), (120, 150, 180), 'rm', 0.8)
    return img


def section(img, x, y, s, col=U.CYAN, glyph=None):
    if glyph:
        img = paste_at(img, master(glyph, 18, col), x, y - 1)
        x += 26
    U.text(img, (x, y + 8), s, U.F(U.MONO, 16), col, 'lm', 2.0)
    return img


def pad_hints(img, x, y, items, col=U.WHITE):
    for g, s in items:
        d = U.BD(img)
        d.ellipse([x, y - 13, x + 26, y + 13], fill=(240, 238, 232, 255), outline=(10, 10, 14, 255), width=2)
        U.text(img, (x + 13, y + 1), g, U.F(U.BAHN, 16, 'Bold'), (14, 14, 20), 'mm')
        x = U.text(img, (x + 34, y), s, U.F(U.MONO, 17), col, 'lm', 0.8) + 30
    return img


def stepper(img, x, y, val, lo_hi='0-13'):
    for k, s in enumerate(('-', None, '+')):
        bx = x + k * 56
        if s:
            img = U.term_button(img, (bx, y, bx + 44, y + 40), s, None, 'idle')
        else:
            U.live_number(img, (bx + 22, y + 20), str(val), 34, U.WHITE, 'mm')
    return img


def save(img, name):
    p = os.path.join(B, name)
    img.convert('RGB').save(p)
    print('wrote', p)
    return p

FILL_WHITE = ('grad', (255, 255, 252), (214, 216, 224))   # neutral white vinyl lettering (quiet stickers)


def bw(sd):
    """Visible (die-cut) width/height of a sticker at 1x, without the padding."""
    bb = sd['img'].split()[3].getbbox()
    return (bb[2] - bb[0]) / SL.SS, (bb[3] - bb[1]) / SL.SS
