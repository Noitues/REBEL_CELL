"""Still 05: black-market shop. Faceted vendor, counter, cards and spinner parts with prices, sign, exit."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, toner, facet, bil, polar, panel, skew_rect, tri, gem, gradient,
                     text, text_w, NEON, poly_fpos)
import ui

WARM = R('#2b0a24', '#6e1433', '#b8243a', '#e0473a', '#f07a3a', '#f6a94e', '#f9d98e')
HOOD = R('#06040e', '#120a22', '#221238', '#361a4e', '#4e2464', '#6e3478', '#9a4c8a')


def bg(u, v):
    base = mix(hexc('#0b2a36'), hexc('#3a0e2c'), v ** 0.8)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#05060e'), min(1, 0.8 * e ** 2.0))


def shards(d):
    """Big dim background triangles: the poster backdrop."""
    rng = random.Random(515)
    st = R('#08101c', '#0e1c2c', '#16283a', '#20344a', '#2c4058')
    for k in range(16):
        x = rng.uniform(-100, 2020)
        y = rng.uniform(140, 620)
        s = rng.uniform(120, 300)
        a = rng.uniform(0, 2 * math.pi)
        pts = [(x + s * math.cos(a + t), y + s * 0.8 * math.sin(a + t)) for t in (0, 2.3, 4.1)]
        tri(d, pts, ramp(st, rng.uniform(0.2, 0.9)))
    # hanging neon triangle strings across the top
    for row, (y0, stn) in enumerate(((168, 'magenta'), (190, 'cyan'))):
        for k in range(26):
            x = -20 + k * 78 + row * 39
            yy = y0 + 18 * math.sin(k * 0.55 + row)
            tri(d, [(x, yy), (x + 34, yy + 2), (x + 17, yy + 30)], ramp(NEON[stn], 0.45 + 0.5 * rng.random()))


def vendor(d):
    cx = 960
    cloak = [(880, 390), (1040, 390), (1190, 480), (1240, 640), (680, 640), (730, 480)]
    facet(d, poly_fpos(cloak, (960, 560)), 12, 3, toner(HOOD, 0.45, gu=0.3, gv=0.2, var=0.08, flip=0.15), 'cloak', 0.3,
          wrap_u=True)
    hood = [(960, 160), (1030, 190), (1082, 262), (1104, 360), (1078, 440), (842, 440), (816, 360), (838, 262), (890, 190)]
    facet(d, poly_fpos(hood, (960, 330)), 18, 3, toner(HOOD, 0.6, gu=0.35, gv=0.25, var=0.08, flip=0.15), 'hood', 0.3,
          wrap_u=True)
    face = [(960, 250), (1016, 290), (1030, 370), (1000, 420), (920, 420), (890, 370), (904, 290)]
    facet(d, poly_fpos(face, (960, 350)), 14, 2, toner(HOOD, 0.1, var=0.05, flip=0.1), 'face', 0.3, wrap_u=True)
    # visor: saturated cyan triangle cluster
    facet(d, bil([(cx - 64, 322), (cx + 64, 322), (cx + 60, 356), (cx - 60, 356)]), 7, 1,
          toner(NEON['cyan'], 0.7, gu=-0.3, var=0.15, flip=0.25), 'visor', 0.3)
    # mask chevron
    tri(d, [(cx - 36, 378), (cx + 36, 378), (cx, 404)], ramp(NEON['magenta'], 0.55))
    tri(d, [(cx, 378), (cx + 36, 378), (cx, 404)], ramp(NEON['magenta'], 0.35))
    # hands on the counter
    for s in (-1, 1):
        hx = cx + s * 170
        tri(d, [(hx - 34, 612), (hx + 34, 612), (hx, 578)], ramp(HOOD, 0.7 if s < 0 else 0.45))
        tri(d, [(hx - 34, 612), (hx + 34, 612), (hx + s * 10, 630)], ramp(HOOD, 0.35))


def counter(d):
    facet(d, bil([(0, 600), (1920, 600), (1920, 640), (0, 640)]), 22, 1,
          toner(WARM, 0.82, gu=-0.25, var=0.06, flip=0.1), 'ctop', 0.3)
    facet(d, bil([(0, 640), (1920, 640), (1920, 880), (0, 880)]), 24, 4,
          toner(WARM, 0.45, gu=-0.35, gv=-0.35, var=0.08, flip=0.14, famt=0.18), 'cfront', 0.35)
    facet(d, bil([(0, 880), (1920, 880), (1920, 1080), (0, 1080)]), 16, 3,
          toner(R('#03020a', '#08061a', '#120c26', '#1e1436', '#2c1c46'), 0.4, gv=-0.4, var=0.08), 'floor', 0.35)


def part_slice(d, x, y):
    facet(d, polar(x, y + 90, 170, 170, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 0.2, 1.0), 5, 3,
          toner(ui.KIND['hack'], 0.6, gu=-0.4, gv=0.2, var=0.1, flip=0.2), 'pslice', 0.3)
    facet(d, polar(x, y + 90, 170, 170, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 1.0, 1.1), 5, 1,
          toner(R('#120e1e', '#2a2238', '#4a3c5c', '#7a6888', '#c0b0c8'), 0.6, gu=-0.5, var=0.1), 'pslicer', 0.3)
    text(d, x, y - 10, '+2', 34, ui.CREAM, anchor='mm', shadow=ui.INK)


def part_pointer(d, x, y):
    pst = R('#3a0a10', '#8a1a1a', '#e0502a', '#ffb040', '#fff0b0')
    for s, off in ((-1, -34), (1, 34)):
        top, tip, w = y - 90, y + 60, 34
        cx = x + off
        tri(d, [(cx - w, top), (cx, top - 8), (cx, tip)], ramp(pst, 0.95 if s < 0 else 0.8))
        tri(d, [(cx, top - 8), (cx + w, top), (cx, tip)], ramp(pst, 0.55 if s < 0 else 0.4))
        tri(d, [(cx + w, top), (cx + w * 0.45, top + (tip - top) * 0.45), (cx, tip)], ramp(pst, 0.3))


def part_hub(d, x, y):
    def rim(u, v, i, j, k, rc):
        lam = 0.5 + 0.5 * math.cos(u * 2 * math.pi - ui.LIGHT_DIR)
        return ramp(NEON['amber'], 0.2 + 0.7 * lam + rc.uniform(-0.08, 0.08))
    facet(d, polar(x, y, 100, 100, 0, 2 * math.pi, 0.72, 1.0), 12, 1, rim, 'phubr', 0.2, wrap_u=True)
    facet(d, polar(x, y, 100, 100, 0, 2 * math.pi, 0.0, 0.72), 12, 2,
          toner(ui.DARK, 0.45, var=0.12, flip=0.2), 'phubd', 0.25, wrap_u=True)
    gem(d, x, y, 42, 42, R('#0a0814', '#1a1428', '#302640', '#4e4062', '#7a6a8e', '#b4a6c4'), 'phubg', n=6, base=0.55)


def pedestal(d, x, y, seed):
    facet(d, bil([(x - 80, y), (x + 80, y), (x + 70, y + 46), (x - 70, y + 46)]), 4, 1,
          toner(ui.DARK, 0.55, gu=-0.4, var=0.08), ('ped', seed), 0.3)
    facet(d, polar(x, y, 80, 18, 0, 2 * math.pi, 0, 1), 8, 1, toner(ui.DARK, 0.85, gu=0.2, var=0.08), ('pedt', seed), 0.2,
          wrap_u=True)


def render():
    img = gradient(bg).convert('RGBA')
    d = ImageDraw.Draw(img)
    shards(d)
    vendor(d)
    counter(d)
    # sign
    panel(d, skew_rect(960 - 360, 26, 720, 104, 20), NEON['magenta'], 0.55, 'sign', nu=12, nv=2, gu=-0.3, gv=-0.3,
          var=0.1, flip=0.2)
    tri(d, [(600, 130), (620, 26), (655, 26)], ramp(NEON['cyan'], 0.75))
    tri(d, [(1300, 130), (1340, 26), (1320, 130)], ramp(NEON['cyan'], 0.5))
    text(d, 972, 80, 'BLACK MARKET', 64, ui.INK, anchor='mm')
    panel(d, skew_rect(960 - 210, 136, 420, 36, 10), ui.DARK, 0.3, 'signsub', nu=6, nv=1)
    text(d, 966, 155, 'NO NAMES  //  NO REFUNDS', 20, hexc('#ffb3dc'), anchor='mm', style='Bold SemiCondensed')
    # credits
    panel(d, skew_rect(1600, 36, 280, 64, 14), ui.DARK, 0.35, 'cred', nu=5, nv=1, gv=-0.3)
    gem(d, 1648, 68, 22, 26, NEON['amber'], 'credg', n=6, base=0.6)
    text(d, 1684, 68, '240 CR', 34, ui.CREAM, anchor='lm')
    # section labels
    for x, lab in ((370, 'PROGRAMS'), (1580, 'RIG PARTS')):
        text(d, x, 222, lab, 26, hexc('#f0d8c8'), anchor='mm', shadow=ui.INK)
        tri(d, [(x - 80, 242), (x + 80, 242), (x, 250)], ramp(NEON['amber'], 0.7))
    # cards for sale
    wares = [('attack', 'SPIKE STORM', 2, ['Deal 4, three', 'times'], 'blade', 60),
             ('block', 'MIRROR WALL', 1, ['GUARD 6. Reflect', 'half'], 'shield', 75),
             ('hack', 'GHOST KEY', 2, ['Skip a foe', 'slice'], 'eye', 110)]
    for k, (kind, title, cost, lines, icon, price) in enumerate(wares):
        cx = 150 + k * 220
        cimg = ui.card_image(kind, title, cost, lines, icon, ('shop', k))
        ui.paste_card(img, cimg, cx, 410, (1 - k) * 2.5)
        ui.price_tag(d, cx, 566, price, ('ptc', k))
    # spinner parts on pedestals
    parts = [(1360, part_slice, 'OVERCLOCK SLICE', 150), (1580, part_pointer, 'TWIN-FANG POINTER', 90),
             (1800, part_hub, 'FLYWHEEL HUB', 120)]
    for k, (x, fn, name, price) in enumerate(parts):
        pedestal(d, x, 470, k)
        fn(d, x, 360)
        text(d, x, 538, name, 18, ui.CREAM, anchor='mm', style='Bold SemiCondensed', shadow=ui.INK)
        ui.price_tag(d, x, 566, price, ('ptp', k))
    # vendor line on the counter front
    panel(d, skew_rect(960 - 330, 720, 660, 70, 14), ui.DARK, 0.3, 'quote', nu=8, nv=1, gv=-0.3)
    text(d, 966, 755, '"Fresh ICE-breakers. Don\'t ask where from."', 26, hexc('#9ff4ff'), anchor='mm',
         style='SemiBold')
    # buttons
    panel(d, skew_rect(70, 950, 330, 84, 16), ui.DARK, 0.4, 'reroll', nu=5, nv=1, gv=-0.3)
    text(d, 110, 992, 'REROLL', 32, ui.CREAM, anchor='lm')
    text(d, 360, 993, '25 CR', 24, ramp(NEON['amber'], 0.8), anchor='rm')
    panel(d, skew_rect(1500, 940, 360, 104, 22), NEON['cyan'], 0.6, 'leave', nu=6, nv=2, gu=-0.3, gv=-0.3, var=0.1,
          flip=0.2)
    text(d, 1640, 993, 'LEAVE', 50, ui.INK, anchor='mm')
    for k in range(2):
        ax = 1760 + k * 30
        tri(d, [(ax, 970), (ax + 26, 993), (ax, 1016)], ramp(R('#021a2a', '#063a50', '#0a5a70'), 0.3 + 0.4 * k))
    return img.convert('RGB')
