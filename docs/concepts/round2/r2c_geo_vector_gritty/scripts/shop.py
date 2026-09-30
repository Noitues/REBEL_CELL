"""Still 05: a cramped back-alley black-market stall. Dripping awning, caged goods, cable clutter,
battered vendor, flickering sign, prices scrawled on tape."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel, skew_rect, tri, gem, gradient,
                     text, text_w, NEON, poly_fpos, line2, catenary, layer, composite, rain, smog, HAND)
from alley import draw_alley
import ui

HOOD = R('#050404', '#0e0b09', '#1a1510', '#281f17', '#372a1f', '#4a382a', '#604a38')
CORR = R('#060606', '#0e0d0c', '#181614', '#24201c', '#322b24', '#42382e')


def stall_back(d):
    def cf(u, v, i, j, k, rc):
        t = 0.45 + (0.12 if i % 2 == 0 else -0.08) - 0.2 * v + rc.uniform(-0.06, 0.06)
        if rc.random() < 0.1:
            return ramp(ui.RUST, 0.3 + 0.3 * rc.random())
        return ramp(CORR, t)
    facet(d, bil([(0, 250), (W, 250), (W, 620), (0, 620)]), 40, 4, cf, 'corr', 0.15)


def awning(d, lay_d):
    # striped canvas, sagging, stained
    def cf(u, v, i, j, k, rc):
        st = R('#0a1414', '#12262a', '#1c3a3c', '#2c5250', '#446a64') if i % 2 == 0 else \
            R('#140806', '#2a120c', '#441e14', '#5e2c1c', '#7a3e28')
        t = 0.75 - 0.4 * v + rc.uniform(-0.08, 0.08)
        if hsh(i, 3, 7) < 0.3 and v > 0.3:
            t -= 0.2  # water stains
        return ramp(st, t)
    facet(d, bil([(-20, 150), (W + 20, 150), (W + 40, 262), (-40, 262)]), 26, 3, cf, 'awn', 0.25)
    # scalloped edge and drips
    rng = random.Random(404)
    n = 26
    for k in range(n):
        x0 = -40 + k * (W + 80) / n
        x1 = x0 + (W + 80) / n
        st = R('#0a1414', '#1c3a3c', '#2c5250') if k % 2 == 0 else R('#140806', '#441e14', '#5e2c1c')
        tri(d, [(x0, 262), (x1, 262), ((x0 + x1) / 2, 290)], ramp(st, 0.55))
        tri(d, [((x0 + x1) / 2, 262), (x1, 262), ((x0 + x1) / 2, 290)], ramp(st, 0.25))
        if rng.random() < 0.7:
            dx = (x0 + x1) / 2
            L = rng.uniform(20, 90)
            lay_d.polygon([((dx - 1.5) * SS, 290 * SS), ((dx + 1.5) * SS, 290 * SS), (dx * SS, (290 + L) * SS)],
                          fill=(180, 200, 210, 110))
            for m in range(rng.randint(1, 3)):
                yy = 300 + L + rng.uniform(10, 260)
                lay_d.polygon([((dx - 3) * SS, yy * SS), ((dx + 3) * SS, yy * SS), (dx * SS, (yy + 9) * SS)],
                              fill=(180, 200, 220, 120))


def sign(d):
    panel(d, skew_rect(960 - 380, 22, 760, 110, 18), ui.DARK, 0.35, 'signbg', nu=12, nv=2, gv=-0.3)
    # neon tube frame made of triangles, with dead segments
    rng = random.Random(9)
    x0, x1, y0, y1 = 960 - 360, 960 + 370, 32, 122
    per = []
    for k in range(20):
        per.append(((x0 + 18) + (x1 - x0 - 18) * k / 20, y0, 'h'))
        per.append((x0 + (x1 - x0 - 18) * k / 20, y1, 'h'))
    for (x, y, _) in per:
        if rng.random() < 0.15:
            tri(d, [(x, y - 3), (x + 30, y - 3), (x + 15, y + 3)], ramp(NEON['magenta'], 0.15))
            continue
        tri(d, [(x, y - 3), (x + 30, y - 3), (x + 15, y + 3)], ramp(NEON['magenta'], 0.55 + 0.3 * rng.random()))
    # flickering letters: one letter half-dead
    word = 'BLACK MARKET'
    size = 64
    total = text_w(word, size)
    x = 966 - total / 2
    for n, ch in enumerate(word):
        wch = text_w(word[:n + 1], size) - text_w(word[:n], size)
        dead = n == 9  # the second K
        col = ramp(NEON['magenta'], 0.2) if dead else ramp(NEON['magenta'], 0.8)
        text(d, x, 80, ch, size, col, anchor='lm', shadow=None if dead else hexc('#3a0628'))
        x += wch
    ui.tape_strip(d, 1250, 138, 250, 3, 'signtape', h=28, alpha=235)
    text(d, 1250, 138, 'no names / no refunds', 22, hexc('#2a2218'), anchor='mm', style=None, path=HAND)


def vendor(d):
    cx = 960
    cloak = [(880, 390), (1040, 390), (1190, 480), (1240, 640), (680, 640), (730, 480)]
    facet(d, poly_fpos(cloak, (960, 560)), 12, 3, toner(HOOD, 0.45, gu=0.3, gv=0.2, var=0.08, flip=0.15), 'cloak', 0.3,
          wrap_u=True)
    # patches sewn on the cloak
    for n, (px, py) in enumerate(((820, 560), (1080, 520), (990, 600))):
        q = [(px, py), (px + 50, py - 6), (px + 54, py + 38), (px + 4, py + 42)]
        facet(d, bil(q), 2, 2, toner(ui.RUST if n % 2 else R('#0a1414', '#1c3a3c', '#2c5250', '#446a64'), 0.5,
                                     var=0.1), ('patch', n), 0.3)
        for s in range(4):
            line2(d, (px + 4 + s * 13, py - 4), (px + 8 + s * 13, py + 4), 1.5, ramp(ui.PAPER, 0.5))
    hood = [(960, 160), (1030, 190), (1082, 262), (1104, 360), (1078, 440), (842, 440), (816, 360), (838, 262), (890, 190)]
    facet(d, poly_fpos(hood, (960, 330)), 18, 3, toner(HOOD, 0.6, gu=0.35, gv=0.25, var=0.08, flip=0.15), 'hood', 0.3,
          wrap_u=True)
    face = [(960, 250), (1016, 290), (1030, 370), (1000, 420), (920, 420), (890, 370), (904, 290)]
    facet(d, poly_fpos(face, (960, 350)), 14, 2, toner(HOOD, 0.08, var=0.05, flip=0.1), 'face', 0.3, wrap_u=True)

    def visor(u, v, i, j, k, rc):
        if i == 5 and k == 0:
            return ramp(ui.DARK, 0.3)  # dead facet
        return ramp(NEON['cyan'], 0.65 + rc.uniform(-0.2, 0.2))
    facet(d, bil([(cx - 64, 322), (cx + 64, 322), (cx + 60, 354), (cx - 60, 354)]), 7, 1, visor, 'visor', 0.3)
    line2(d, (cx + 18, 320), (cx + 34, 356), 2.5, ui.INK)  # cracked lens
    # respirator and hoses
    gem(d, cx, 392, 30, 22, ui.METAL, 'resp', n=6, base=0.45)
    for s in (-1, 1):
        pts = [(cx + s * 26, 396), (cx + s * 52, 420), (cx + s * 64, 452), (cx + s * 90, 470)]
        for k in range(3):
            line2(d, pts[k], pts[k + 1], 12, ramp(ui.METAL, 0.2))
            line2(d, pts[k], pts[k + 1], 3, ramp(ui.METAL, 0.45))
    for s in (-1, 1):
        hx = cx + s * 170
        tri(d, [(hx - 34, 622), (hx + 34, 622), (hx, 588)], ramp(HOOD, 0.7 if s < 0 else 0.45))
        tri(d, [(hx - 34, 622), (hx + 34, 622), (hx + s * 10, 640)], ramp(HOOD, 0.35))


def cage(d, x0, y0, x1, y1, seed):
    col = ramp(ui.METAL, 0.3)
    hi = ramp(ui.METAL, 0.6)
    x = x0
    while x <= x1:
        line2(d, (x, y0), (x, y1), 4, col)
        line2(d, (x - 1, y0), (x - 1, y1), 1.2, hi)
        x += 42
    for y in (y0, y1):
        line2(d, (x0 - 6, y), (x1 + 6, y), 8, ramp(ui.RUST, 0.35))
        line2(d, (x0 - 6, y - 3), (x1 + 6, y - 3), 1.5, ramp(ui.RUST, 0.7))
    # padlock
    px, py = x1 - 30, (y0 + y1) / 2
    gem(d, px, py + 12, 16, 18, ui.RUST, ('lock', seed), n=6, base=0.55)
    line2(d, (px - 9, py + 2), (px - 9, py - 10), 3.5, col)
    line2(d, (px + 9, py + 2), (px + 9, py - 10), 3.5, col)
    line2(d, (px - 9, py - 10), (px + 9, py - 10), 3.5, col)


def price_tape(d, cx, y, price, seed, ang=-4):
    s = f'{price} cr'
    w = 120
    ui.tape_strip(d, cx, y, w, ang, seed, h=34, alpha=240)
    text(d, cx, y + 1, s, 30, hexc('#1a1410'), anchor='mm', style=None, path=HAND)


def part_slice(d, x, y):
    facet(d, polar(x, y + 90, 160, 160, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 0.2, 1.0), 5, 3,
          lambda u, v, i, j, k, rc: ramp(ui.RUST, 0.5) if rc.random() < 0.12 else
          ramp(ui.KIND['hack'], 0.55 - 0.3 * (u - 0.5) + rc.uniform(-0.1, 0.1)), 'pslice', 0.3)
    facet(d, polar(x, y + 90, 160, 160, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 1.0, 1.12), 8, 1,
          lambda u, v, i, j, k, rc: ramp(NEON['sodium'] if i % 2 == 0 else ui.DARK, 0.5), 'pslicer', 0.1)
    text(d, x, y - 10, '+2', 32, ui.CREAM, anchor='mm', shadow=ui.INK)


def part_pointer(d, x, y):
    pst = R('#1a0c06', '#4a1e0c', '#9a4412', '#e07a1c', '#ffc060', '#fff0c0')
    for s, off in ((-1, -32), (1, 32)):
        top, tip, w = y - 80, y + 60, 30
        cx = x + off
        tri(d, [(cx - w, top), (cx, top - 8), (cx, tip)], ramp(pst, 0.85 if s < 0 else 0.7))
        tri(d, [(cx, top - 8), (cx + w, top), (cx, tip)], ramp(pst, 0.45 if s < 0 else 0.35))
        tri(d, [(cx + w, top), (cx + w * 0.45, top + (tip - top) * 0.45), (cx, tip)], ramp(pst, 0.25))
        tri(d, [(cx - w * 0.4, top + 20), (cx, top + 12), (cx - w * 0.1, top + 40)], ramp(ui.RUST, 0.35))


def part_hub(d, x, y):
    def rim(u, v, i, j, k, rc):
        lam = 0.5 + 0.5 * math.cos(u * 2 * math.pi - ui.LIGHT_DIR)
        if rc.random() < 0.25:
            return ramp(ui.RUST, 0.2 + 0.6 * lam)
        return ramp(ui.METAL, 0.2 + 0.65 * lam + rc.uniform(-0.08, 0.08))
    # gear teeth
    for k in range(12):
        a = k * 2 * math.pi / 12
        p0 = (x + 92 * math.cos(a - 0.12), y + 92 * math.sin(a - 0.12))
        p1 = (x + 92 * math.cos(a + 0.12), y + 92 * math.sin(a + 0.12))
        p2 = (x + 110 * math.cos(a), y + 110 * math.sin(a))
        tri(d, [p0, p1, p2], ramp(ui.METAL, 0.3 + 0.4 * (0.5 + 0.5 * math.cos(a - ui.LIGHT_DIR))))
    facet(d, polar(x, y, 95, 95, 0, 2 * math.pi, 0.6, 1.0), 12, 1, rim, 'phubr', 0.2, wrap_u=True)
    facet(d, polar(x, y, 95, 95, 0, 2 * math.pi, 0.0, 0.6), 12, 2, toner(ui.DARK, 0.45, var=0.12, flip=0.2), 'phubd', 0.25,
          wrap_u=True)
    gem(d, x, y, 34, 34, NEON['sodium'], 'phubg', n=6, base=0.5)


def tag(d, x, y, rng, st):
    """An angular graffiti tag: zig-zag strokes of sharp triangles, not letters."""
    pts = [(x, y + rng.uniform(20, 60))]
    for k in range(7):
        px, py = pts[-1]
        pts.append((px + rng.uniform(14, 50), y + (rng.uniform(-10, 30) if k % 2 else rng.uniform(40, 100))))
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 7, dx / L * 7
        c = mix(ramp(st, rng.uniform(0.45, 0.75)), hexc('#2a2622'), 0.25)
        tri(d, [(a[0] + nx, a[1] + ny), (a[0] - nx, a[1] - ny), (b[0] + dx * 0.15, b[1] + dy * 0.15)], c)
    # underline swoosh and a drip
    tri(d, [(x - 10, y + 100), (pts[-1][0] + 30, y + 92), (x + 20, y + 110)], mix(ramp(st, 0.4), hexc('#2a2622'), 0.3))
    tri(d, [(x + 40, y + 100), (x + 46, y + 100), (x + 43, y + 140)], mix(ramp(st, 0.4), hexc('#2a2622'), 0.3))


def counter(d):
    def cf(u, v, i, j, k, rc):
        t = 0.5 - 0.35 * v + (0.08 if i % 2 == 0 else -0.05) + rc.uniform(-0.08, 0.08)
        if rc.random() < 0.07:
            return ramp(ui.RUST, 0.12 + 0.18 * rc.random())
        return ramp(ui.METAL, t * 0.8)
    facet(d, bil([(0, 640), (W, 640), (W, 880), (0, 880)]), 32, 4, cf, 'cfront', 0.3)
    facet(d, bil([(0, 612), (W, 612), (W, 642), (0, 642)]), 48, 1,
          lambda u, v, i, j, k, rc: ramp(ui.METAL, 0.6) if rc.random() < 0.1 else
          ramp(NEON['sodium'] if i % 2 == 0 else ui.DARK, 0.5 + rc.uniform(-0.1, 0.1)), 'hazard', 0.1)
    # graffiti glyph cluster on the counter
    rng = random.Random(77)
    for gx, gy, st in ((180, 700, NEON['acid']), (1480, 690, NEON['magenta']), (1320, 810, NEON['cyan'])):
        tag(d, gx, gy, rng, st)
    # floor
    facet(d, bil([(0, 880), (W, 880), (W, H), (0, H)]), 16, 3,
          lambda u, v, i, j, k, rc: ramp(R('#020203', '#06060a', '#0e0e14', '#1a1a22', '#2a2a34'),
                                         0.3 + 0.2 * v + (0.35 if rc.random() < 0.1 else 0) + rc.uniform(-0.08, 0.08)),
          'floor', 0.35)


def render():
    img = draw_alley('shop_alley', far=(780, 170, 1140, 420), signs=True)
    img = Image.blend(img, gradient(lambda u, v: hexc('#050507')), 0.3)
    img = rain(img, 'srain_far', n=500, col=(150, 160, 180), alpha=(30, 70), length=(40, 90), region=(0, 0, W, 300))
    img = img.convert('RGBA')
    d = ImageDraw.Draw(img)
    stall_back(d)
    vendor(d)
    # goods on shelves inside cages
    for x0, x1 in ((50, 720), (1200, 1870)):
        line2(d, (x0, 560), (x1, 560), 10, ramp(ui.RUST, 0.45))
    wares = [('attack', 'SPIKE STORM', 2, ['Deal 4, three', 'times'], 'blade', 60),
             ('block', 'MIRROR WALL', 1, ['GUARD 6. Reflect', 'half'], 'shield', 75),
             ('hack', 'GHOST KEY', 2, ['Skip a foe', 'slice'], 'eye', 110)]
    cage(d, 50, 285, 720, 590, 'L')
    for k, (kind, title, cost, lines, icon, price) in enumerate(wares):
        cx = 160 + k * 225
        cimg = ui.card_image(kind, title, cost, lines, icon, ('shop', k), tape=(100, 10, 80, (-8, 5, -3)[k]))
        ui.paste_card(img, cimg, cx, 425, (1 - k) * 3.0)
    parts = [(1320, part_slice, 'OVERCLOCK SLICE', 150), (1540, part_pointer, 'TWIN-FANG POINTER', 90),
             (1760, part_hub, 'FLYWHEEL HUB', 120)]
    for k, (x, fn, name, price) in enumerate(parts):
        fn(d, x, 420)
    cage(d, 1200, 285, 1870, 590, 'R')
    for k, (x, fn, name, price) in enumerate(parts):
        panel(d, skew_rect(x - 95, 522, 190, 28, 6), ui.DARK, 0.3, ('pn', k), nu=3, nv=1)
        text(d, x, 536, name, 17, ui.CREAM, anchor='mm', style='Bold SemiCondensed')
    for k, (kind, title, cost, lines, icon, price) in enumerate(wares):
        price_tape(d, 160 + k * 225, 598, price, ('ptc', k), ang=(-5, 3, -2)[k])
    for k, (x, fn, name, price) in enumerate(parts):
        price_tape(d, x, 598, price, ('ptp', k), ang=(4, -3, 2)[k])
    counter(d)
    lay, ld = layer(img)
    awning(d, ld)
    sign(d)
    # cable clutter over everything at the top
    rng = random.Random(12)
    for k in range(14):
        a = (rng.uniform(-50, 900), rng.uniform(0, 160))
        b = (rng.uniform(1000, 1970), rng.uniform(0, 160))
        if rng.random() < 0.5:
            a, b = (a[0] * 0.4, a[1]), (b[0] * 0.6, b[1])
        catenary(d, a, b, rng.uniform(30, 120), rng.uniform(2, 4), ramp(ui.DARK, rng.uniform(0.1, 0.3)), n=16)
    for k in range(5):
        x = rng.uniform(100, 1800)
        line2(d, (x, 0), (x + rng.uniform(-20, 20), rng.uniform(100, 250)), 3, ramp(ui.DARK, 0.2))
    img = composite(img, lay).convert('RGBA')
    d = ImageDraw.Draw(img)
    # quote on tape, buttons, credits
    ui.tape_strip(d, 960, 760, 640, -1.5, 'quote', h=52, alpha=235)
    text(d, 960, 761, "fresh ICE-breakers. don't ask where from.", 30, hexc('#1a1410'), anchor='mm', style=None,
         path=HAND)
    panel(d, skew_rect(1600, 36, 280, 64, 14), ui.DARK, 0.35, 'cred', nu=5, nv=1, gv=-0.3)
    gem(d, 1648, 68, 22, 26, NEON['sodium'], 'credg', n=6, base=0.55)
    text(d, 1684, 68, '240 CR', 34, ui.CREAM, anchor='lm')
    panel(d, skew_rect(70, 950, 330, 84, 16), ui.DARK, 0.4, 'reroll', nu=5, nv=1, gv=-0.3)
    text(d, 110, 992, 'REROLL', 32, ui.CREAM, anchor='lm')
    ui.tape_strip(d, 330, 992, 100, 6, 'rrtape', h=34, alpha=240)
    text(d, 330, 993, '25 cr', 28, hexc('#1a1410'), anchor='mm', style=None, path=HAND)

    def leave(u, v, i, j, k, rc):
        if rc.random() < 0.1:
            return ramp(ui.METAL, 0.45)
        return ramp(NEON['cyan'], 0.5 - 0.25 * (v - 0.5) + rc.uniform(-0.1, 0.1))
    facet(d, bil(skew_rect(1500, 940, 360, 104, 22)), 6, 2, leave, 'leave', 0.3)
    text(d, 1640, 993, 'LEAVE', 50, ui.INK, anchor='mm')
    for k in range(2):
        ax = 1760 + k * 30
        tri(d, [(ax, 970), (ax + 26, 993), (ax, 1016)], ramp(R('#021a2a', '#063a50', '#0a5a70'), 0.3 + 0.4 * k))
    return img.convert('RGB')
