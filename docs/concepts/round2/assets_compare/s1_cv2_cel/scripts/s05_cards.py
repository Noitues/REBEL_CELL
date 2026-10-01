"""05 cards: Backspin (Common), Arc Flash (Uncommon), Bulwark (Uncommon), and the card back."""
import math
import random
from kit import *
from icons import slice_icon

CW, CH = 330, 480
XS = [300, 740, 1180, 1620]
CY = 500
RARITY = {'COMMON': (METAL, 1), 'UNCOMMON': (CELL, 2), 'RARE': (GOLD, 3), 'BOSS': (RED, 4)}


def ccw_arrow(d, cx, cy, r, w, col_stops, seed, sweep=(30, 300)):
    a0, a1 = math.radians(sweep[0]), math.radians(sweep[1])
    n = 24
    pts = [(cx + r * math.cos(a0 - (a0 - a1) * k / n * -1), cy - r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy - r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    for k in range(n):
        line2(d, pts[k], pts[k + 1], w + 5, INK)
    for k in range(n):
        line2(d, pts[k], pts[k + 1], w, bcol(col_stops, 2 if k < n / 2 else 1))
    # arrowhead at the end (counter-clockwise travel)
    ex, ey = pts[-1]
    a = a1
    tx, ty = -math.sin(a), -math.cos(a)        # direction of travel (ccw, screen y down)
    nx, ny = math.cos(a), -math.sin(a)
    h = w * 2.4
    head = [(ex + tx * h, ey + ty * h), (ex + nx * h * 0.9, ey + ny * h * 0.9), (ex - nx * h * 0.9, ey - ny * h * 0.9)]
    shape(d, head, col_stops, (seed, 'head'), ink=3.0, bias=0.3)


def wheel(d, cx, cy, r, seed):
    cols = [RED, STEEL, LIME, RED, PURP, GOLD]
    for k in range(6):
        a0, a1 = -math.pi / 2 + k * math.pi / 3, -math.pi / 2 + (k + 1) * math.pi / 3
        facet(d, polar(cx, cy, r, r, a0, a1, 0.28, 1.0), 3, 2,
              lambda u, v, i, j, kk, rc, st=cols[k], a=(a0 + a1) / 2:
              bcol(st, band_from(0.42 + 0.5 * math.cos(a - math.radians(-125))), rc.uniform(-0.03, 0.03)),
              (seed, k), 0.25)
    ring = circle_pts(cx, cy, r, n=24)
    ink_poly(d, ring, 3.4, (seed, 'ring'))
    for k in range(6):
        a = -math.pi / 2 + k * math.pi / 3
        ink_line(d, (cx + r * 0.28 * math.cos(a), cy + r * 0.28 * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a)),
                 2.2, (seed, 'sp', k))
    shape(d, circle_pts(cx, cy, r * 0.3, n=8), METAL, (seed, 'hub'), ink=2.8)
    tri(d, [(cx - 9, cy - r - 14), (cx + 9, cy - r - 14), (cx, cy - r + 6)], bcol(GOLD, 2))
    ink_poly(d, [(cx - 9, cy - r - 14), (cx + 9, cy - r - 14), (cx, cy - r + 6)], 2.2, (seed, 'ptr'))


def art_backspin(d, x0, y0, w, h):
    cx, cy = x0 + w / 2, y0 + h / 2 + 6
    wheel(d, cx, cy, h * 0.34, 'bs_wheel')
    ccw_arrow(d, cx, cy, h * 0.44, 9, CELL, 'bs_arrow', sweep=(-10, 250))
    ink_text(d, cx + w * 0.34, cy + h * 0.24, '9', 54, bcol(CELL, 2))


def art_arcflash(d, x0, y0, w, h):
    heads = [(x0 + w * 0.2, y0 + h * 0.7), (x0 + w * 0.5, y0 + h * 0.76), (x0 + w * 0.8, y0 + h * 0.68)]
    src = (x0 + w * 0.5, y0 + h * 0.14)
    rng = random.Random(7)
    for hx, hy in heads:
        pts = [src]
        for k in range(1, 5):
            t = k / 5
            pts.append((src[0] + (hx - src[0]) * t + rng.uniform(-16, 16), src[1] + (hy - 40 - src[1]) * t))
        pts.append((hx, hy - 24))
        for a, b in zip(pts, pts[1:]):
            line2(d, a, b, 9, INK)
        for a, b in zip(pts, pts[1:]):
            line2(d, a, b, 5, bcol(CELL, 2))
            line2(d, a, b, 2, hexc('#f4feff'))
    for k, (hx, hy) in enumerate(heads):
        body = circle_pts(hx, hy, 30, 24, n=6)
        shape(d, body, MER if k != 1 else SOL, ('afh', k), ink=3.0)
        shape(d, circle_pts(hx, hy + 2, 9, n=5), RED, ('afe', k), ink=2, bias=0.4)
        for s in (-1, 1):
            line2(d, (hx + s * 26, hy - 8), (hx + s * 44, hy - 18), 3, INK)
    burst = [(src[0] + 26 * math.cos(a) * (1 if k % 2 == 0 else 0.45), src[1] + 26 * math.sin(a) * (1 if k % 2 == 0 else 0.45))
             for k, a in enumerate([math.pi * j / 5 for j in range(10)])]
    shape(d, burst, GOLD, 'af_burst', ink=2.6, bias=0.4)


def art_bulwark(d, x0, y0, w, h):
    rng = random.Random(3)
    for k in range(4):
        px = x0 + w * (0.14 + k * 0.2)
        plate = [(px, y0 + h * 0.2 + (k % 2) * 8), (px + w * 0.24, y0 + h * 0.16 + (k % 2) * 8),
                 (px + w * 0.25, y0 + h * 0.9), (px + 2, y0 + h * 0.94)]
        extrude(d, plate, (6, 6), STEEL, ('bw', k), ink=3.0, front_kw=dict(nu=4, nv=3))
        for r in range(3):
            shape(d, circle_pts(px + w * 0.12, y0 + h * (0.3 + r * 0.22), 4, n=5), METAL, ('rv', k, r), ink=1.4)
        rust_streaks(d, plate, ('bwr', k), n=2, length=(12, 30))
    slice_icon(d, 'DEFEND', x0 + w * 0.5, y0 + h * 0.5, 96, seed='bw_icon')


def pict_row(d, x0, y, items):
    """items: list of (kind, value)."""
    x = x0
    for kind, val in items:
        if kind == 'ccw':
            ccw_arrow(d, x + 16, y, 12, 4, CELL, ('pccw', x), sweep=(-10, 250))
            x += 36
        elif kind == 'slice':
            slice_icon(d, val, x + 16, y, 34)
            x += 38
            continue
        elif kind == 'heads':
            for k in range(3):
                shape(d, circle_pts(x + 8 + k * 14, y, 8, 6, n=6), MER, ('ph', x, k), ink=1.6)
            x += 48
            continue
        if kind in ('num', 'ccw'):
            pass
        if val is not None and kind != 'slice':
            ink_text(d, x + 4, y + 1, str(val), 28, CREAM2, anchor='lm', shadow=(1.5, 2))
            x += text_w(str(val), 28) + 14


CREAM2 = hexc('#f2e8d4')


def card(title, ctype, cost, rarity, art, picts, lines, seed):
    im, d = layer_img(CW, CH)
    rst, pips = RARITY[rarity]
    outer = [(0, 0), (CW, 0), (CW, CH), (0, CH)]
    # rarity-coloured frame
    cel_fill(d, outer, rst, (seed, 'frame'), nu=8, nv=10, form=0.7, var=0.04)
    chips(d, outer, (seed, 'fchip'), n=10)
    inner = [(14, 14), (CW - 14, 14), (CW - 14, CH - 14), (14, CH - 14)]
    cel_fill(d, inner, DARK, (seed, 'inner'), nu=8, nv=10, form=-0.4, var=0.03)
    ink_poly(d, inner, 2.6, (seed, 'inink'))
    # title tape
    tape = [(70, 26), (CW - 22, 22), (CW - 20, 64), (72, 68)]
    shape(d, tape, PAPER, (seed, 'tape'), ink=2.6, nu=6, nv=1, bias=0.3)
    ink_text(d, (70 + CW - 20) / 2 + 6, 46, title, 30, hexc('#1e1814'), stroke=0, shadow=None)
    # type
    text(d, CW - 26, 86, ctype, 16, bcol(rst, 2), anchor='rm')
    # art window
    ax, ay, aw, ah = 26, 98, CW - 52, 196
    win = [(ax, ay), (ax + aw, ay), (ax + aw, ay + ah), (ax, ay + ah)]
    cel_fill(d, win, STEEL if art is not art_bulwark else RUSTR, (seed, 'artbg'), nu=6, nv=4, form=0.5, bias=-0.15)
    art(d, ax, ay, aw, ah)
    ink_poly(d, win, 3.0, (seed, 'artink'))
    # pictogram plate
    plate = [(26, 306), (CW - 26, 306), (CW - 26, 352), (26, 352)]
    shape(d, plate, METAL, (seed, 'plate'), ink=2.4, flat=0)
    pict_row(d, 40, 329, picts)
    # text
    for k, ln in enumerate(lines):
        text(d, CW / 2, 380 + k * 26, ln, 20, hexc('#e4dccc'), anchor='mm', style='SemiBold')
    # rarity tag + pips
    tag = [(26, CH - 52), (170, CH - 52), (180, CH - 26), (26, CH - 26)]
    shape(d, tag, rst, (seed, 'rtag'), ink=2.2, flat=2)
    text(d, 34, CH - 39, rarity, 17, hexc('#14100c'), anchor='lm')
    for k in range(pips):
        shape(d, circle_pts(CW - 40 - k * 24, CH - 39, 8, n=6), rst, (seed, 'pip', k), ink=2, bias=0.3)
    # RAM cost gem
    gem_pts = circle_pts(40, 40, 34, n=6, a0=math.pi / 6)
    extrude(d, gem_pts, (3, 5), CELL, (seed, 'gem'), ink=3.4, front_kw=dict(nu=12, nv=2, form=1.2, bias=0.1))
    ink_text(d, 40, 36, str(cost), 36, hexc('#f4feff'))
    text(d, 40, 62, 'RAM', 12, hexc('#04161c'), anchor='mm')
    ink_poly(d, outer, 4.0, (seed, 'outink'))
    return im


def card_back(seed='back'):
    im, d = layer_img(CW, CH)
    outer = [(0, 0), (CW, 0), (CW, CH), (0, CH)]
    cel_fill(d, outer, DARK, (seed, 'bg'), nu=8, nv=10, form=0.6)
    # hex lattice
    for r in range(9):
        for c in range(6):
            x = 30 + c * 56 + (28 if r % 2 else 0)
            y = 34 + r * 52
            hp = circle_pts(x, y, 22, n=6, a0=math.pi / 6)
            ink_poly(d, hp, 1.4, (seed, r, c))
    inner = [(22, 22), (CW - 22, 22), (CW - 22, CH - 22), (22, CH - 22)]
    ink_poly(d, inner, 2.4, (seed, 'in'))
    # Cell mark: a cyan hex badge with a broken-chain bolt
    hexo = circle_pts(CW / 2, CH / 2 - 10, 96, n=6, a0=math.pi / 6)
    extrude(d, hexo, (5, 8), CELL, (seed, 'badge'), ink=4.0, front_kw=dict(nu=12, nv=3, form=1.1))
    hexi = circle_pts(CW / 2, CH / 2 - 10, 70, n=6, a0=math.pi / 6)
    shape(d, hexi, DARK, (seed, 'bi'), ink=2.6, form=-0.5)
    bolt = [(CW / 2 + 14, CH / 2 - 74), (CW / 2 - 30, CH / 2 - 4), (CW / 2 - 2, CH / 2 - 4), (CW / 2 - 16, CH / 2 + 56),
            (CW / 2 + 32, CH / 2 - 22), (CW / 2 + 4, CH / 2 - 22)]
    shape(d, bolt, GOLD, (seed, 'bolt'), ink=3.0, bias=0.2)
    tape = [(60, CH - 110), (CW - 60, CH - 116), (CW - 58, CH - 78), (62, CH - 72)]
    shape(d, tape, RED, (seed, 'tape'), ink=2.4, flat=1)
    ink_text(d, CW / 2, CH - 94, 'REBEL_CELL', 26, hexc('#fff0e6'), stroke=1.5, shadow=None)
    rust_streaks(d, hexo, (seed, 'r'), n=4)
    ink_poly(d, outer, 4.0, (seed, 'outink'))
    return im


def render():
    img = sheet()
    cards = [
        card('BACKSPIN', 'SPIN', 1, 'COMMON', art_backspin, [('ccw', 9)], ['Spin a wheel 9 ticks', 'counter-clockwise.'],
             'bs'),
        card('ARC FLASH', 'ATTACK', 2, 'UNCOMMON', art_arcflash, [('slice', 'ATTACK'), ('num', 3), ('heads', None)],
             ['Deal 3 damage to', 'every enemy.'], 'af'),
        card('BULWARK', 'DEFEND', 2, 'UNCOMMON', art_bulwark, [('slice', 'DEFEND'), ('num', 12)],
             ['Gain 12 block.'], 'bw'),
        card_back(),
    ]
    for k, (c, x) in enumerate(zip(cards, XS)):
        paste_rot(img, c, x, CY, (-1.5, 1.0, -0.8, 1.6)[k])
    labels = [(XS[0], 790, 'BACKSPIN  -  Common'), (XS[1], 790, 'ARC FLASH  -  Uncommon'),
              (XS[2], 790, 'BULWARK  -  Uncommon'), (XS[3], 790, 'CARD BACK')]
    return finish(img, '05_cards.png', labels, '05', 'CARDS')


if __name__ == '__main__':
    render()
