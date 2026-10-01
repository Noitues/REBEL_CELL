"""Render the TACTICAL GLASS overlay concept (round 3).

python render_all.py   -> writes 01_combat.png 02_city.png 03_shop.png 04_lifecycle.png
                          contact_sheet.jpg into the parent folder.
All randomness is seeded.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tg_lib as T  # noqa: E402
from tg_lib import SS  # noqa: E402

OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, '..', '..', '..', '..'))
BASE_COMBAT = os.path.join(ROOT, 'docs/concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png')
BASE_CITY = os.path.join(ROOT, 'docs/concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png')
BASE_SHOP = os.path.join(ROOT, 'docs/concepts/round2/r2c_v2_modem/modem_shop.png')


def c255(c, a=255):
    return (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), a)


# ============================================================================ props
def faceted_portrait(w, h, rng):
    """Crew photo in the Cv2 language: a smooth portrait, then triangulated."""
    im = Image.new('RGB', (w, h), (14, 22, 30))
    d = ImageDraw.Draw(im)
    for i in range(h):
        t = i / h
        d.line([0, i, w, i], fill=(int(18 + 20 * (1 - t)), int(30 + 14 * (1 - t)), int(44 + 10 * (1 - t))))
    d.polygon([(0, h), (0, .84 * h), (.22 * w, .74 * h), (.40 * w, .70 * h), (.60 * w, .70 * h),
               (.78 * w, .74 * h), (w, .82 * h), (w, h)], fill=(34, 32, 40))
    d.polygon([(.30 * w, .74 * h), (.40 * w, .62 * h), (.60 * w, .62 * h), (.70 * w, .74 * h),
               (.56 * w, .80 * h), (.44 * w, .80 * h)], fill=(48, 46, 58))
    d.rectangle([.43 * w, .54 * h, .57 * w, .70 * h], fill=(140, 96, 86))
    d.ellipse([.30 * w, .17 * h, .70 * w, .62 * h], fill=(196, 140, 118))
    d.polygon([(.28 * w, .36 * h), (.30 * w, .18 * h), (.45 * w, .09 * h), (.66 * w, .12 * h),
               (.74 * w, .30 * h), (.71 * w, .44 * h), (.66 * w, .27 * h), (.40 * w, .25 * h)], fill=(26, 22, 30))
    d.polygon([(.30 * w, .33 * h), (.71 * w, .31 * h), (.71 * w, .40 * h), (.30 * w, .42 * h)], fill=(255, 60, 150))
    d.polygon([(.44 * w, .52 * h), (.56 * w, .52 * h), (.52 * w, .55 * h), (.47 * w, .55 * h)], fill=(120, 70, 66))
    a = np.asarray(im, np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn = xx / w
    a = a * (0.55 + 0.6 * (1 - xn))[..., None]
    a += (T.smoothstep(0.45, 0.0, xn) * 0.22)[..., None] * np.array([1.0, 0.2, 0.6])
    a += (T.smoothstep(0.62, 1.0, xn) * 0.18)[..., None] * np.array([0.1, 0.8, 1.0])
    a = np.clip(a, 0, 1)
    # triangulate
    out = Image.new('RGB', (w, h))
    od = ImageDraw.Draw(out)
    nx, ny = 11, 13
    sx, sy = w / nx, h / ny
    P = np.zeros((ny + 1, nx + 1, 2))
    for j in range(ny + 1):
        for i in range(nx + 1):
            jx = 0 if i in (0, nx) else rng.uniform(-0.38, 0.38) * sx
            jy = 0 if j in (0, ny) else rng.uniform(-0.38, 0.38) * sy
            P[j, i] = (i * sx + jx, j * sy + jy)
    for j in range(ny):
        for i in range(nx):
            q = [P[j, i], P[j, i + 1], P[j + 1, i + 1], P[j + 1, i]]
            tris = [(q[0], q[1], q[2]), (q[0], q[2], q[3])] if rng.random() < 0.5 else \
                [(q[0], q[1], q[3]), (q[1], q[2], q[3])]
            for tri in tris:
                cx = sum(p[0] for p in tri) / 3
                cy = sum(p[1] for p in tri) / 3
                col = a[int(min(h - 1, cy)), int(min(w - 1, cx))] * rng.uniform(0.93, 1.07)
                od.polygon([tuple(p) for p in tri], fill=tuple(int(min(1, v) * 255) for v in col))
    return out


def id_badge(rng):
    w, h = 214 * SS, 292 * SS
    card = Image.new('RGBA', (w, h), (234, 232, 224, 255))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, w, 54 * SS], fill=(18, 18, 20, 255))
    d.polygon([(w - 70 * SS, 0), (w, 0), (w, 54 * SS), (w - 100 * SS, 54 * SS)], fill=c255(T.PINK))
    for k in range(4):
        x = w - 96 * SS + k * 14 * SS
        d.polygon([(x, 54 * SS), (x + 7 * SS, 54 * SS), (x + 7 * SS + 30 * SS, 0), (x + 30 * SS, 0)], fill=(18, 18, 20, 255))
    d.text((14 * SS, 30 * SS), 'CELL', font=T.stencil(22 * SS), fill=(238, 236, 228, 255), anchor='lm')
    d.text((82 * SS, 31 * SS), '// CREW', font=T.bahn(14 * SS), fill=(160, 160, 160, 255), anchor='lm')
    ph = faceted_portrait(124 * SS, 146 * SS, rng)
    d.rectangle([14 * SS - 2 * SS, 66 * SS - 2 * SS, 14 * SS + 124 * SS + 2 * SS, 66 * SS + 146 * SS + 2 * SS], fill=(20, 20, 22, 255))
    card.paste(ph, (14 * SS, 66 * SS))
    fx = 148 * SS
    d.text((fx, 70 * SS), 'OP', font=T.bahn(12 * SS, 'SemiBold Condensed'), fill=(110, 110, 110, 255))
    d.text((fx, 84 * SS), '03', font=T.stencil(34 * SS), fill=(20, 20, 22, 255))
    d.text((fx, 130 * SS), 'CLR', font=T.bahn(12 * SS, 'SemiBold Condensed'), fill=(110, 110, 110, 255))
    d.rectangle([fx, 146 * SS, fx + 50 * SS, 166 * SS], fill=c255(T.PINK))
    d.text((fx + 25 * SS, 156 * SS), 'RED', font=T.bahn(14 * SS), fill=(255, 255, 255, 255), anchor='mm')
    d.text((fx, 178 * SS), 'BLD', font=T.bahn(12 * SS, 'SemiBold Condensed'), fill=(110, 110, 110, 255))
    d.text((fx, 192 * SS), 'O-', font=T.bahn(16 * SS), fill=(20, 20, 22, 255))
    d.text((14 * SS, 218 * SS), 'K. VOSS', font=T.bahn(30 * SS), fill=(18, 18, 20, 255))
    d.text((14 * SS, 250 * SS), 'NETRUNNER  //  ID 09-114-K', font=T.bahn(12 * SS, 'SemiBold Condensed'), fill=(90, 90, 92, 255))
    x = 14 * SS
    while x < w - 14 * SS:
        bw = int(rng.choice([1, 1, 2, 3]) * SS)
        d.rectangle([x, 270 * SS, x + bw - 1, 284 * SS], fill=(20, 20, 22, 255))
        x += bw + int(rng.choice([1, 2]) * SS)
    img = T.laminate(card, rng, margin=8, radius=12, glare=0.30, glare_pos=0.36,
                     hole=(115, 15, 40, 9))
    return img


def badge_clip():
    """Chrome strap clip that goes through the badge slot."""
    w, h = 54 * SS, 40 * SS
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    a = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([4 * SS, 14 * SS, w - 4 * SS, h - 2 * SS], 5 * SS, fill=255)
    mm = np.asarray(m, np.float32) / 255
    t = yy / h
    metal = 0.35 + 0.55 * np.exp(-((t - 0.45) / 0.12) ** 2) + 0.25 * np.exp(-((t - 0.8) / 0.05) ** 2)
    a[..., 0] = metal * 0.95
    a[..., 1] = metal * 0.97
    a[..., 2] = metal * 1.0
    a[..., 3] = mm
    # strap (dark nylon) going up
    strap = (np.abs(xx - w / 2) < 9 * SS) & (yy < 18 * SS)
    a[strap, :3] = 0.10 + 0.04 * np.sin(yy[strap] / 2.0)[:, None]
    a[strap, 3] = 1
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    for rx in (14 * SS, w - 14 * SS):
        d.ellipse([rx - 3 * SS, 25 * SS, rx + 3 * SS, 31 * SS], fill=(60, 62, 66, 255), outline=(220, 224, 230, 255))
    return im


def heat_card(rng):
    w, h = 230 * SS, 300 * SS
    card = Image.new('RGBA', (w, h), (20, 20, 23, 255))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, w, 22 * SS], fill=(255, 214, 40, 255))
    for k in range(-2, 16):
        x = k * 22 * SS
        d.polygon([(x, 22 * SS), (x + 11 * SS, 22 * SS), (x + 33 * SS, 0), (x + 22 * SS, 0)], fill=(20, 20, 23, 255))
    d.text((16 * SS, 34 * SS), 'HEAT', font=T.stencil(40 * SS), fill=(238, 236, 228, 255))
    d.text((w - 16 * SS, 40 * SS), 'KANAL\nWARD', font=T.bahn(12 * SS, 'SemiBold Condensed'), fill=(140, 140, 140, 255),
           anchor='ra', align='right')
    d.text((14 * SS, 78 * SS), '62', font=T.stencil(118 * SS), fill=c255(T.ORANGE))
    d.text((w - 16 * SS, 170 * SS), '/100', font=T.bahn(18 * SS), fill=(150, 150, 150, 255), anchor='rb')
    segs = 10
    gx0, gy0, gw, gh = 16 * SS, 196 * SS, w - 32 * SS, 14 * SS
    sw = gw / segs
    for i in range(segs):
        x = gx0 + i * sw
        fill = c255(T.ORANGE) if i < 6 else ((255, 140, 60, 255) if i == 6 else (52, 52, 56, 255))
        if i == 6:
            d.rectangle([x + 1 * SS, gy0, x + sw * 0.2, gy0 + gh], fill=fill)
            d.rectangle([x + sw * 0.2, gy0, x + sw - 2 * SS, gy0 + gh], fill=(52, 52, 56, 255))
        else:
            d.rectangle([x + 1 * SS, gy0, x + sw - 2 * SS, gy0 + gh], fill=fill)
    for i, lab in enumerate(['0', '50', '100']):
        d.text((gx0 + gw * i / 2, gy0 + gh + 4 * SS), lab, font=T.bahn(10 * SS, 'SemiBold Condensed'),
               fill=(120, 120, 120, 255), anchor='ma')
    d.line([16 * SS, 232 * SS, w - 16 * SS, 232 * SS], fill=(60, 60, 64, 255), width=SS)
    d.text((16 * SS, 286 * SS), 'STATUS', font=T.bahn(10 * SS, 'SemiBold Condensed'), fill=(110, 110, 110, 255), anchor='lb')
    return T.laminate(card, rng, margin=7, radius=10, glare=0.24, glare_pos=0.55)


def house_card(rng):
    w, h = 430 * SS, 360 * SS
    card = Image.new('RGBA', (w, h), (26, 28, 34, 255))
    d = ImageDraw.Draw(card)
    for x in range(0, w, 20 * SS):
        d.line([x, 0, x, h], fill=(60, 110, 130, 70), width=1)
    for y in range(0, h, 20 * SS):
        d.line([0, y, w, y], fill=(60, 110, 130, 70), width=1)
    d.rectangle([0, 0, w, 40 * SS], fill=(14, 14, 16, 255))
    d.text((16 * SS, 20 * SS), 'MODEM', font=T.stencil(22 * SS), fill=(238, 236, 228, 255), anchor='lm')
    d.text((112 * SS, 21 * SS), '// HOUSE RULE 01', font=T.bahn(15 * SS), fill=(150, 150, 150, 255), anchor='lm')
    d.rectangle([w - 46 * SS, 10 * SS, w - 14 * SS, 30 * SS], fill=c255(T.PINK))
    for (x, y) in [(18, 58), (412, 58), (18, 342), (412, 342)]:
        X, Y = x * SS, y * SS
        d.line([X - 8 * SS, Y, X + 8 * SS, Y], fill=(220, 220, 220, 140), width=SS)
        d.line([X, Y - 8 * SS, X, Y + 8 * SS], fill=(220, 220, 220, 140), width=SS)
    d.text((w - 18 * SS, h - 14 * SS), 'NO REFUNDS. NO NAMES.', font=T.bahn(11 * SS, 'SemiBold Condensed'),
           fill=(120, 130, 140, 255), anchor='rb')
    return T.laminate(card, rng, margin=6, radius=10, glare=0.20, glare_pos=0.62)


def chalk_marker_prop(length=300, width=30, color=T.PINK):
    """A paper-wrapped china marker, drawn horizontally with the tip at the left."""
    w, h = length, width + 20
    a = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cy = h / 2
    r = width / 2
    v = (yy - cy) / r
    body = (np.abs(v) <= 1) & (xx > 44)
    tipzone = xx <= 44
    taper = np.clip((xx - 4) / 40, 0.18, 1)
    tip = tipzone & (np.abs(v) <= taper) & (xx > 4)
    nz = np.sqrt(np.clip(1 - v ** 2, 0, 1))
    shade = 0.35 + 0.65 * np.clip(nz * 0.8 - v * 0.45, 0, 1.2)
    spec = np.exp(-((v + 0.45) / 0.12) ** 2) * 0.5
    paper = np.array([0.80, 0.78, 0.72])
    stripe = ((xx + v * 10) % 38 < 2.5)
    col = paper[None, None, :] * shade[..., None]
    col[stripe] *= 0.55
    band = (xx > 44) & (xx < 64)
    col[band] = np.array(color) * shade[band][:, None]
    tcol = np.array(color)[None, None, :] * (shade[..., None] * 0.9)
    col = np.where(tip[..., None], tcol, col)
    col += spec[..., None]
    a[..., :3] = np.clip(col, 0, 1)
    a[..., 3] = (body | tip).astype(np.float32)
    # string pull tab
    im = Image.fromarray((a * 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    d.line([(150, cy - r + 1), (156, cy - r - 8), (166, cy - r - 9)], fill=(200, 60, 60, 255), width=2)
    return im


# ============================================================================ base edits
def washed_execute(base):
    """Combat: the GO medallion becomes a washed-out digital EXECUTE button."""
    img = base.copy()
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = T.smoothstep(150, 120, np.sqrt((xx - 1760) ** 2 + (yy - 892) ** 2))
    lum = (img * np.array([0.3, 0.59, 0.11])).sum(2, keepdims=True)
    washed = lum * 0.42 + 0.10
    img = img * (1 - 0.82 * m[..., None]) + washed * (0.82 * m[..., None])
    pil = T.to_img(img).convert('RGBA')
    ov = Image.new('RGBA', pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.polygon([(1648, 852), (1866, 852), (1878, 866), (1878, 958), (1662, 958), (1648, 944)], fill=(30, 32, 36, 235))
    d.line([(1648, 852), (1866, 852), (1878, 866)], fill=(120, 120, 124, 200), width=2)
    d.text((1763, 893), 'EXECUTE', font=T.bahn(46, 'SemiBold'), fill=(150, 150, 152, 255), anchor='mm')
    d.text((1763, 936), 'SPIN BOTH WHEELS', font=T.bahn(16, 'SemiBold'), fill=(110, 110, 112, 255), anchor='mm')
    pil.alpha_composite(ov)
    return T.to_f(pil)


def shop_buttons(base):
    """Shop: cover the old BUY/SELL/TRADE stickers with washed-out digital buttons."""
    pil = T.to_img(base).convert('RGBA')
    ov = Image.new('RGBA', pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([24, 762, 298, 1056], fill=(15, 20, 34, 255))
    for (y0, y1, lab) in [(780, 896, 'PURCHASE'), (926, 1040, 'EXIT')]:
        d.rectangle([36, y0, 286, y1], fill=(22, 30, 46, 255))
        for x in range(36, 286, 14):
            d.line([x, y0, x + 7, y0], fill=(70, 120, 140, 255), width=2)
            d.line([x, y1, x + 7, y1], fill=(70, 120, 140, 255), width=2)
        for y in range(y0, y1, 14):
            d.line([36, y, 36, y + 7], fill=(70, 120, 140, 255), width=2)
            d.line([286, y, 286, y + 7], fill=(70, 120, 140, 255), width=2)
        d.polygon([(36, y0), (50, y0), (36, y0 + 14)], fill=(90, 150, 170, 255))
        d.polygon([(286, y1), (272, y1), (286, y1 - 14)], fill=(90, 150, 170, 255))
        d.text((161, (y0 + y1) / 2), lab, font=T.bahn(38, 'SemiBold'), fill=(96, 118, 130, 255), anchor='mm')
    pil.alpha_composite(ov)
    return T.to_f(pil)


# ============================================================================ verb layer
def combat_verb_strokes(rng):
    st = []
    st += T.letter_strokes('SEND IT', 1706, 868, 72, 16.5, T.PINK, rng, angle=-0.10, slant=0.18, tracking=0.17)
    st += [(T.chaikin(T.resample([(1548, 952), (1680, 940), (1810, 920), (1880, 905)], 8), 2), 9.5, T.PINK)]
    return st


def render_verb(seed, progress=1.0, glint=None, wipe=None, glint_gain=1.0):
    rng = np.random.default_rng(seed)
    strokes = combat_verb_strokes(np.random.default_rng(seed + 1))
    L = T.Layer(rng, 1460, 760, 460, 300)
    part = T.cut_strokes(strokes, progress)
    L.strokes(part)
    L.light(glint=glint, glint_gain=glint_gain)
    if wipe is not None:
        apply_wipe(L, wipe, np.random.default_rng(seed + 7))
    tip = None
    if part and progress < 1:
        tip = part[-1][0][-1]
    return L, tip


def apply_wipe(L, p, rng):
    H2, W2 = L.a.shape
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
    curve = 0.16 * W2 * (((yy / H2) - 0.55) * 2) ** 2
    fx = -0.10 * W2 + p * 1.25 * W2 - curve
    d = fx - xx
    wiped = T.smoothstep(-5 * SS, 7 * SS, d)
    sm_rgb = T.blur(L.rgb, 16 * SS, axes=(1,))
    sm_a = T.blur(L.a, 16 * SS, axes=(1,))
    sh = 22 * SS
    sm_rgb = np.roll(sm_rgb, sh, 1)
    sm_a = np.roll(sm_a, sh, 1)
    sm_rgb[:, :sh] = 0
    sm_a[:, :sh] = 0
    rows = T.blur(rng.random(H2).astype(np.float32)[:, None].repeat(4, 1), 1.2, axes=(0,))[:, 0]
    rows = (rows - rows.min()) / max(1e-6, rows.max() - rows.min())
    streak = (0.35 + 0.65 * rows)[:, None] * (0.8 + 0.2 * T.noise(H2, W2, 30, rng))
    pile = np.exp(-np.clip(d, 0, None) / (30 * SS))
    residue = (0.10 + 0.75 * pile) * streak * (1 - 0.8 * p ** 3)
    res = np.clip(residue, 0, 1)
    L.a = L.a * (1 - wiped) + sm_a * res * wiped
    L.rgb = L.rgb * (1 - wiped[..., None]) + sm_rgb * (res * wiped)[..., None]


# ============================================================================ screens
def combat_main(rng):
    L = T.Layer(rng)
    T.print_ticks(L, rng)
    # crisp printed reticle on the cracked slice
    T.print_reticle(L, 1444, 502, 78, (255, 120, 40, 210))
    L.flush_print()
    # ID badge with chrome clip, strap gaffer-taped to the glass
    L.paste(T.make_tape(110, 34, rng, 'gaffer'), 174, 118, angle=-6, height=0.2)
    L.paste(id_badge(rng), 172, 306, angle=3.5, height=0.3)
    L.paste(badge_clip(), 170, 150, angle=3.5, height=0.4)
    # target annotation
    L.wax_stroke(T.hand_circle(1444, 504, 50, 46, rng, turns=1.15), 7.5, T.RED)
    L.strokes(T.letter_strokes('HIT IT', 1742, 588, 44, 10.5, T.RED, rng, angle=-0.06))
    L.strokes(T.arrow_strokes(T.bezier((1652, 582), (1560, 600), (1500, 538)), 7.5, T.RED, rng, head=22))
    # tactical note (white) with a yellow margin bracket
    L.strokes(T.letter_strokes('SLICE 6 CRACKED\nBACKDOOR FIRST\nTHEN BRUTE IT', 182, 532, 21, 5.2, T.WHITE, rng,
                               angle=-0.035, align='left', line_gap=1.5))
    L.wax_stroke(T.chaikin(T.resample([(40, 494), (36, 530), (38, 572)], 6), 2), 6, T.YELLOW)
    L.wax_stroke([(118, 548), (126, 554), (232, 548)], 4.5, T.YELLOW)
    L.light()
    return L


def city_main(rng):
    L = T.Layer(rng)
    T.print_ticks(L, rng)
    T.print_dashed_circle(L, 1605, 662, 72, (255, 60, 50, 200), width=1.8, ticks=12)
    T.print_dashed_circle(L, 1605, 662, 116, (255, 60, 50, 140), width=1.4, dash=6, gap=10)
    T.print_text(L, 1605 + 118, 662 + 8, 'R2', T.bahn(13 * SS, 'SemiBold Condensed'), (255, 80, 70, 200))
    L.flush_print()
    # planned path (yellow, hand-dashed) + waypoints
    path = T.chaikin(T.resample([(748, 654), (818, 712), (960, 744), (1112, 736), (1214, 690), (1262, 636)], 10), 3)
    L.strokes(T.arrow_strokes(path, 7, T.YELLOW, rng, head=24, dashed=True, dash=30, gap=17))
    L.flush_print()
    T.print_waypoint(L, 895, 738, '1')
    T.print_waypoint(L, 1165, 718, '2')
    L.flush_print()
    # target
    L.wax_stroke(T.hand_circle(1293, 588, 50, 60, rng), 8, T.ORANGE)
    L.strokes(T.letter_strokes('HIT THIS', 1462, 466, 38, 9.5, T.ORANGE, rng, angle=-0.07))
    L.strokes(T.arrow_strokes(T.bezier((1395, 494), (1350, 500), (1338, 540)), 6.5, T.ORANGE, rng, head=18))
    # home
    L.wax_stroke(T.hand_circle(712, 612, 46, 66, rng, turns=1.1), 8, T.PINK)
    L.strokes(T.letter_strokes('OURS', 566, 704, 42, 10.5, T.PINK, rng, angle=-0.05))
    L.wax_stroke(T.chaikin(T.resample([(508, 736), (570, 732), (628, 726)], 8), 2), 6.5, T.PINK)
    # threat
    L.strokes(T.letter_strokes('THEM', 1772, 548, 46, 11, T.RED, rng, angle=0.05))
    L.strokes(T.arrow_strokes(T.bezier((1712, 580), (1680, 610), (1640, 622)), 7, T.RED, rng, head=18))
    # heat poster
    L.paste(heat_card(rng), 1776, 906, angle=-3, height=0.3)
    L.paste(T.make_tape(86, 28, rng), 1680, 760, angle=32, height=0.35)
    L.paste(T.make_tape(86, 28, rng), 1872, 768, angle=-28, height=0.35)
    L.strokes(T.letter_strokes('FLAGGED', 1772, 1006, 32, 8.0, T.RED, rng, angle=-0.09))
    box = [(1676, 978), (1872, 958), (1878, 1030), (1680, 1046), (1672, 980)]
    L.wax_stroke(T.chaikin(T.resample(box, 8), 1), 5.5, T.RED)
    L.light()
    return L


def shop_main(rng):
    L = T.Layer(rng)
    T.print_ticks(L, rng)
    L.flush_print()
    # house rule card over the old scrawl
    L.paste(house_card(rng), 1632, 528, angle=1.4, height=0.3)
    L.paste(T.make_tape(120, 34, rng, 'gaffer'), 1420, 352, angle=40, height=0.35)
    L.paste(T.make_tape(120, 34, rng, 'gaffer'), 1846, 348, angle=-38, height=0.35)
    L.strokes(T.letter_strokes('UPGRADE\nOR DIE.', 1628, 552, 66, 13.5, T.YELLOW, rng, angle=-0.05, line_gap=1.42))
    L.wax_stroke(T.chaikin(T.resample([(1546, 656), (1650, 650), (1756, 638)], 8), 2), 8, T.PINK)
    # price tags (masking tape + red grease)
    for (cx, price) in [(448, '30'), (706, '50'), (963, '40'), (1222, '60')]:
        ang = rng.uniform(-9, 9)
        L.paste(T.make_tape(74, 30, rng), cx + 64, 552, angle=ang, height=0.3)
        L.strokes(T.letter_strokes(price, cx + 64, 553, 18, 4.8, T.RED, rng, angle=-math.radians(ang)))
    # THIS ONE!
    L.wax_stroke(T.hand_circle(1222, 646, 124, 140, rng, turns=1.12, angle=0.08), 9, T.PINK)
    L.strokes(T.letter_strokes('THIS ONE!', 1196, 862, 44, 11, T.PINK, rng, angle=-0.05))
    L.strokes(T.arrow_strokes(T.bezier((1350, 852), (1392, 830), (1356, 778)), 7, T.PINK, rng, head=20))
    # verbs
    L.strokes(T.letter_strokes('BUY', 160, 838, 62, 14.5, T.PINK, rng, angle=-0.08))
    L.strokes(T.letter_strokes('LEAVE', 158, 984, 50, 12, T.WHITE, rng, angle=-0.06))
    L.light(glint=0.16, glint_gain=0.8)
    return L


SMUDGE = {
    'combat': [(330, 980, 70, 52, 0.4, 'print'), (1520, 150, 60, 46, -0.6, 'print'), (920, 690, 300, 70, -0.25, 'wipe')],
    'city': [(1480, 250, 64, 50, 0.3, 'print'), (360, 840, 260, 64, 0.2, 'wipe'), (1050, 960, 58, 46, -0.2, 'print')],
    'shop': [(1290, 990, 64, 50, 0.5, 'print'), (390, 430, 60, 46, -0.3, 'print'), (870, 880, 280, 60, -0.1, 'wipe')],
}


def finish(img, key, seed, corner='tr', band=0.30):
    return T.acrylic(img, np.random.default_rng(seed), SMUDGE[key], corner, band)


def main():
    os.makedirs(OUT, exist_ok=True)
    # ---------------- combat
    base = washed_execute(T.to_f(Image.open(BASE_COMBAT)))
    Lc = combat_main(np.random.default_rng(101))
    pre = T.composite(base, Lc)
    V, _ = render_verb(500, 1.0, glint=0.42, glint_gain=0.7)
    combat = T.composite(pre, V)
    T.to_img(finish(combat, 'combat', 11)).save(os.path.join(OUT, '01_combat.png'))
    print('combat')
    # ---------------- city
    base = T.to_f(Image.open(BASE_CITY))
    Lm = city_main(np.random.default_rng(202))
    city = T.composite(base, Lm)
    T.to_img(finish(city, 'city', 12, corner='tr', band=0.26)).save(os.path.join(OUT, '02_city.png'))
    print('city')
    # ---------------- shop
    base = shop_buttons(T.to_f(Image.open(BASE_SHOP)))
    Ls = shop_main(np.random.default_rng(303))
    shop = T.composite(base, Ls)
    T.to_img(finish(shop, 'shop', 13, corner='bl', band=0.40)).save(os.path.join(OUT, '03_shop.png'))
    print('shop')
    # ---------------- lifecycle
    lifecycle(pre)
    print('lifecycle')
    contact_sheet()


CROP = (1470, 770, 1920, 1070)  # 450 x 300


def state_crop(pre, **kw):
    V, tip = render_verb(500, **kw)
    img = T.composite(pre, V)
    img = finish(img, 'combat', 11)
    x0, y0, x1, y1 = CROP
    return T.to_img(img[y0:y1, x0:x1]), tip


def lifecycle(pre):
    W, H = 1920, 1080
    bg = T.to_img(pre).filter(ImageFilter.GaussianBlur(18))
    bg = Image.eval(bg, lambda v: int(v * 0.28))
    canvas = bg.convert('RGBA')
    d = ImageDraw.Draw(canvas)
    d.text((48, 40), 'SEND IT', font=T.stencil(54), fill=(255, 44, 142, 255))
    d.text((300, 50), 'VERB LIFECYCLE  //  TACTICAL GLASS', font=T.bahn(30), fill=(225, 224, 218, 255))
    d.text((300, 88), 'grease pencil on the planning acrylic, over the washed-out system word EXECUTE',
           font=T.bahn(20, 'SemiBold'), fill=(140, 140, 140, 255))
    PW, PH = 600, 400
    xs = [42, 660, 1278]
    py = 140
    stages = [
        ('01', 'WRITE', 'stroke by stroke in writing order, ~0.55 s, short pen-lifts between letters; the marker tip leads',
         dict(progress=0.62), [dict(progress=p) for p in (0.15, 0.4, 0.7, 1.0)], ['0.08 s', '0.22 s', '0.38 s', '0.55 s']),
        ('02', 'IDLE', 'a thin glint sweeps across the wax every ~3.2 s; the wax relief catches the key light',
         dict(progress=1.0, glint=0.52, glint_gain=1.6),
         [dict(progress=1.0, glint=g, glint_gain=1.6) for g in (0.25, 0.42, 0.6, 0.85)], ['0.0 s', '0.25 s', '0.5 s', '0.75 s']),
        ('03', 'WIPE', 'a palm drags across as the page leaves: pigment smears, piles at the front, leaves a pink haze',
         dict(progress=1.0, wipe=0.5), [dict(progress=1.0, wipe=p) for p in (0.2, 0.45, 0.7, 1.0)],
         ['0.06 s', '0.14 s', '0.22 s', '0.30 s']),
    ]
    for (num, name, desc, main_kw, thumbs, tl), x in zip(stages, xs):
        crop, tip = state_crop(pre, **main_kw)
        panel = crop.resize((PW, PH), Image.LANCZOS).convert('RGBA')
        if tip is not None:
            sx = (tip[0] - CROP[0]) * PW / (CROP[2] - CROP[0])
            sy = (tip[1] - CROP[1]) * PH / (CROP[3] - CROP[1])
            prop = chalk_marker_prop(330, 34)
            prop = prop.rotate(-122, resample=Image.BICUBIC, expand=True)
            # the tip sits at the left-middle of the unrotated image; find it after rotation
            ang = math.radians(122)
            ox, oy = -330 / 2 + 4, 0
            rx = ox * math.cos(ang) - oy * math.sin(ang)
            ry = ox * math.sin(ang) + oy * math.cos(ang)
            px, py2 = int(sx - (prop.width / 2 + rx)), int(sy - (prop.height / 2 + ry))
            shadow = Image.new('RGBA', prop.size, (0, 0, 0, 0))
            shadow.putalpha(prop.getchannel('A').point(lambda v: int(v * 0.55)))
            shadow = shadow.filter(ImageFilter.GaussianBlur(8))
            tmp = Image.new('RGBA', panel.size, (0, 0, 0, 0))
            tmp.paste(shadow, (px + 18, py2 + 22), shadow)
            panel.alpha_composite(tmp)
            tmp = Image.new('RGBA', panel.size, (0, 0, 0, 0))
            tmp.paste(prop, (px, py2), prop)
            panel.alpha_composite(tmp)
        canvas.paste(panel, (x, py))
        d.rectangle([x - 1, py - 1, x + PW, py + PH], outline=(230, 230, 225, 120), width=1)
        for (cx, cy) in [(x, py), (x + PW, py), (x, py + PH), (x + PW, py + PH)]:
            d.line([cx - 10, cy, cx + 10, cy], fill=(230, 230, 225, 200), width=1)
            d.line([cx, cy - 10, cx, cy + 10], fill=(230, 230, 225, 200), width=1)
        d.text((x, py + PH + 18), num, font=T.stencil(40), fill=(255, 44, 142, 255))
        d.text((x + 64, py + PH + 22), name, font=T.stencil(34), fill=(235, 234, 228, 255))
        d.multiline_text((x, py + PH + 72), wrap(desc, 62), font=T.bahn(19, 'SemiBold'), fill=(160, 160, 160, 255), spacing=5)
        ty = py + PH + 140
        tw, th = 140, 93
        for k, (kw, lab) in enumerate(zip(thumbs, tl)):
            c, _ = state_crop(pre, **kw)
            tx = x + k * (tw + 13)
            canvas.paste(c.resize((tw, th), Image.LANCZOS), (tx, ty))
            d.rectangle([tx - 1, ty - 1, tx + tw, ty + th], outline=(200, 200, 195, 90), width=1)
            d.text((tx, ty + th + 8), lab, font=T.bahn(15, 'SemiBold Condensed'), fill=(150, 150, 150, 255))
        if num != '03':
            d.text((x + PW + 9, py + PH / 2), '>', font=T.stencil(30), fill=(255, 210, 40, 220), anchor='lm')
    d.text((W - 48, H - 30), 'REBEL_CELL // ROUND 3 OVERLAY // O_A TACTICAL GLASS', font=T.bahn(14, 'SemiBold'),
           fill=(110, 110, 110, 255), anchor='rb')
    # timeline + build notes
    ty = 880
    d.line([42, ty, 1878, ty], fill=(200, 200, 195, 120), width=1)
    for x, lab in [(42, 'PAGE IN'), (340, 'WRITTEN  0.55 s'), (960, 'IDLE LOOP  3.2 s glint period'),
                   (1580, 'PAGE OUT  wipe 0.30 s'), (1878, '')]:
        d.line([x, ty - 8, x, ty + 8], fill=(255, 210, 40, 230), width=2)
        if lab:
            d.text((x + 8, ty - 30), lab, font=T.bahn(16, 'SemiBold Condensed'), fill=(200, 200, 195, 255))
    notes = [
        ('WAX', 'per-stroke mesh with a bristle-streak texture; a write mask (UV.x = arc length) reveals it; '
                'height map -> normal-lit with one key light'),
        ('GLASS', 'one full-screen sheen pass: reflection band, corner streaks, smudge haze; '
                  'all overlay casts a 4 px offset shadow onto the screen'),
        ('WIPE', 'screen-space smear shader: a curved front sweeps the verb layer, '
                 'directional blur + streak noise, then the layer frees'),
    ]
    for i, (h_, t_) in enumerate(notes):
        x = 42 + i * 618
        d.text((x, ty + 30), h_, font=T.stencil(26), fill=(255, 44, 142, 255))
        d.multiline_text((x, ty + 66), wrap(t_, 64), font=T.bahn(17, 'SemiBold'), fill=(150, 150, 150, 255), spacing=5)
    canvas.convert('RGB').save(os.path.join(OUT, '04_lifecycle.png'))


def wrap(s, n):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        if len(cur) + len(w_) + 1 > n:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    lines.append(cur)
    return '\n'.join(lines)


def contact_sheet():
    names = ['01_combat.png', '02_city.png', '03_shop.png', '04_lifecycle.png']
    sheet = Image.new('RGB', (1920, 1080), (10, 10, 12))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).resize((952, 535), Image.LANCZOS)
        sheet.paste(im, (4 + (i % 2) * 960, 4 + (i // 2) * 540))
    sheet.save(os.path.join(OUT, 'contact_sheet.jpg'), quality=88)


if __name__ == '__main__':
    main()
