"""MODEM CYBER SHOP screen in the v2 gritty geo-vector style (uniform triangle facets).

Layout follows ref6 sub-image 05: tall MODEM neon at left with CYBER SHOP under it, BUY/SELL/TRADE
stickers bottom-left, a figure on a walkway, MICROCHIPS and CARD BUILDER panels in the centre,
SHOP NOTES and INVENTORY on the right, and a pink marker scrawl "UPGRADE OR DIE!".
Usage: python modem.py   (writes ../modem_shop.png)
"""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel, skew_rect, tri, gem,
                     gradient, text, text_w, NEON, line2, catenary, layer, composite, rain, smog, finalize, HAND,
                     poly_fpos)
from alley import draw_alley
import ui

PINK = hexc('#ff4fb4')
GLASS = R('#030308', '#06060e', '#0a0a16', '#10101e', '#161628', '#1e1e34')
EDGE = NEON['cyan']


# ------------------------------------------------------------------ backdrop
def backdrop():
    img = draw_alley('modem_street', far=(860, 60, 1260, 520), signs=True)
    img = smog(img, 'msmog', [(120, 200, 50, 120), (430, 220, 50, 120)], R('#140c1c', '#22142a', '#321a34', '#40202e'))
    lay, d = layer(img)
    # MODEM light spilling over the left wall and down onto the wet street (translucent facets)
    facet(d, bil([(0, 0), (520, 0), (720, 1080), (0, 1080)]), 8, 12,
          lambda u, v, i, j, k, rc: ramp(NEON['magenta'], 0.55) + (int(max(0, 95 * (1 - u) ** 1.6 * (1 - abs(v - 0.45))
                                                                              + rc.uniform(-12, 12))),),
          'spill', 0.35)
    # faceted magenta reflection streak on the wet street under the sign
    for k in range(12):
        y = 760 + k * 26
        w = 160 + k * 16
        cx = 180 + k * 22
        q = [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 + 8, y + 20), (cx - w / 2 + 8, y + 20)]
        a = max(40, 210 - k * 14)
        facet(d, bil(q), 3, 1, lambda u, v, i, j, kk, rc, a=a: None if rc.random() < 0.25 else
              ramp(NEON['magenta'], 0.7 + rc.uniform(-0.15, 0.2)) + (int(a * rc.uniform(0.6, 1.0)),), ('mref', k), 0.35)
    img = composite(img, lay)
    img = rain(img, 'mrain', n=900, col=(170, 170, 210), alpha=(30, 80), length=(40, 110))
    return img


def walkway(d):
    """Foreground metal walkway with railing (bottom centre-left)."""
    deck = [(170, 960), (1060, 960), (1120, 1080), (120, 1080)]

    def cf(u, v, i, j, k, rc):
        t = 0.35 + 0.3 * v + (0.08 if i % 2 == 0 else -0.04) + rc.uniform(-0.06, 0.06)
        if rc.random() < 0.1:
            return ramp(ui.RUST, 0.35)
        return ramp(ui.METAL, t * 0.7)
    facet(d, bil(deck), 18, 3, cf, 'deck', 0.3)
    # railing: posts and rails
    for x in range(200, 1060, 70):
        line2(d, (x, 960), (x - 6, 850), 5, ramp(ui.METAL, 0.3))
        line2(d, (x - 1, 960), (x - 7, 850), 1.5, ramp(NEON['magenta'], 0.5))
    line2(d, (180, 850), (1060, 850), 7, ramp(ui.METAL, 0.35))
    line2(d, (180, 848), (1060, 848), 2, ramp(NEON['magenta'], 0.6))
    line2(d, (180, 905), (1060, 905), 4, ramp(ui.METAL, 0.25))
    # stair down to the right
    for k in range(6):
        y = 880 + k * 20
        line2(d, (1060 + k * 18, y), (1150 + k * 18, y), 5, ramp(ui.METAL, 0.3 + 0.03 * k))


def figure(d, x, y):
    """A hooded figure on the walkway, lit magenta from the left, cyan from the right."""
    body = R('#030305', '#08080c', '#101016', '#1a1a22')
    hood = [(x, y - 150), (x + 26, y - 138), (x + 30, y - 112), (x + 18, y - 96), (x - 18, y - 96), (x - 28, y - 112),
            (x - 24, y - 138)]
    facet(d, poly_fpos(hood, (x, y - 118)), 7, 1, toner(body, 0.5, var=0.1), 'fhood', 0.2, wrap_u=True)
    coat = [(x - 30, y - 96), (x + 32, y - 96), (x + 44, y - 20), (x + 20, y), (x - 20, y), (x - 42, y - 20)]
    facet(d, poly_fpos(coat, (x, y - 50)), 6, 2, toner(body, 0.45, var=0.1), 'fcoat', 0.3, wrap_u=True)
    for s in (-1, 1):
        tri(d, [(x + s * 6, y), (x + s * 18, y), (x + s * 14, y + 70)], ramp(body, 0.4))
        tri(d, [(x + s * 14, y + 70), (x + s * 18, y), (x + s * 20, y + 72)], ramp(body, 0.2))
    # rim light facets
    tri(d, [(x - 28, y - 112), (x - 24, y - 138), (x - 18, y - 118)], ramp(NEON['magenta'], 0.75))
    tri(d, [(x - 42, y - 20), (x - 30, y - 96), (x - 34, y - 40)], ramp(NEON['magenta'], 0.6))
    tri(d, [(x + 44, y - 20), (x + 32, y - 96), (x + 38, y - 50)], ramp(NEON['cyan'], 0.5))
    tri(d, [(x - 8, y - 116), (x + 14, y - 116), (x + 3, y - 108)], ramp(NEON['cyan'], 0.8))  # visor glint


# ------------------------------------------------------------------ signage
def modem_sign(d):
    x0, x1, y0, y1 = 44, 236, 34, 610
    for y in (90, 330, 560):
        line2(d, (0, y), (x0, y + 10), 7, ramp(ui.METAL, 0.3))
    facet(d, bil([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 5, 16, toner(ui.DARK, 0.3, gu=-0.2, var=0.06, flip=0.1),
          'mbg', 0.3)
    rng = random.Random(3)
    # neon tube frame: dense bright facets, a few dead
    for k in range(40):
        y = y0 + 10 + (y1 - y0 - 20) * k / 40
        for x, s in ((x0 + 8, 1), (x1 - 8, -1)):
            c = ramp(NEON['magenta'], 0.2 if rng.random() < 0.06 else 0.85)
            tri(d, [(x, y), (x, y + 13), (x + s * 6, y + 6)], c)
    for x in range(x0 + 10, x1 - 10, 14):
        for y, s in ((y0 + 8, 1), (y1 - 8, -1)):
            tri(d, [(x, y), (x + 11, y), (x + 5.5, y + s * 6)], ramp(NEON['magenta'], 0.85))
    step = (y1 - y0 - 40) / 5
    for k, ch in enumerate('MODEM'):
        cy = y0 + 20 + step * (k + 0.5)
        text(d, (x0 + x1) / 2 + 4, cy + 4, ch, 104, ramp(NEON['magenta'], 0.25), anchor='mm')
        text(d, (x0 + x1) / 2, cy, ch, 104, ramp(NEON['magenta'], 0.88), anchor='mm')
        cx = (x0 + x1) / 2
        tri(d, [(cx - 34, cy - 6), (cx - 20, cy - 6), (cx - 27, cy + 4)], ramp(NEON['magenta'], 1.0))
    # CYBER SHOP under it
    q = [(30, 628), (250, 628), (250, 760), (30, 760)]
    facet(d, bil(q), 4, 3, toner(ui.DARK, 0.25, var=0.05), 'cbg', 0.3)
    for x in range(36, 244, 13):
        tri(d, [(x, 632), (x + 10, 632), (x + 5, 637)], ramp(NEON['magenta'], 0.7))
        tri(d, [(x, 756), (x + 10, 756), (x + 5, 751)], ramp(NEON['magenta'], 0.55))
    text(d, 140, 672, 'CYBER', 50, ramp(NEON['magenta'], 0.85), anchor='mm', shadow=ramp(NEON['magenta'], 0.25), sh=3)
    text(d, 140, 722, 'SHOP', 50, ramp(NEON['magenta'], 0.85), anchor='mm', shadow=ramp(NEON['magenta'], 0.25), sh=3)


def stickers(img, d):
    """BUY / SELL / TRADE stickers slapped on a post at the lower left."""
    for k, (word, st, ang) in enumerate((('BUY', NEON['cyan'], 4), ('SELL', NEON['magenta'], -3), ('TRADE', NEON['acid'], 2))):
        sim = Image.new('RGBA', (230 * SS, 80 * SS), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sim)

        def margin(u, v, i, j, kk, rc):
            if rc.random() < 0.12:
                return ramp(ui.PAPER, 0.35)
            return ramp(ui.PAPER, 0.62 - 0.2 * v + rc.uniform(-0.08, 0.08))
        facet(sd, bil([(0, 0), (230, 0), (230, 80), (0, 80)]), 6, 2, margin, ('stm', k), 0.35)
        facet(sd, bil([(8, 8), (222, 8), (222, 72), (8, 72)]), 6, 2,
              lambda u, v, i, j, kk, rc: ramp(ui.PAPER, 0.4) if rc.random() < 0.08 else ramp(ui.DARK, 0.3 + rc.uniform(-0.1, 0.1)),
              ('stb', k), 0.35)
        text(sd, 115, 41, word, 46, ramp(st, 0.85), anchor='mm')
        sd.polygon([(230 * SS, 58 * SS), (230 * SS, 80 * SS), (206 * SS, 80 * SS)], fill=(0, 0, 0, 0))
        ui.paste_card(img, sim, 150, 830 + k * 84, ang)
    ui.tape_strip(d, 105, 792, 90, -20, 'sttape', h=24, alpha=230)


# ------------------------------------------------------------------ glass panels
def glass_panel(img, x0, y0, x1, y1, seed, title=None, tab=None, edge=EDGE):
    lay, d = layer(img)
    facet(d, bil([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), max(2, int((x1 - x0) / 90)), max(2, int((y1 - y0) / 90)),
          toner(GLASS, 0.55, gu=-0.15, gv=-0.2, var=0.1, flip=0.1, alpha=(205, 232)), ('gl', seed), 0.3)
    img = composite(img, lay)
    d = ImageDraw.Draw(img)
    # neon edge: a tube of small bright triangles, occasional dead segment, chamfered corner accents
    rng = random.Random(str(seed))
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(L / 16)
        for k in range(n):
            t0, t1 = k / n, (k + 0.8) / n
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            dead = rng.random() < 0.04
            line2(d, p0, p1, 3.2, ramp(edge, 0.25 if dead else 0.8 + rng.uniform(-0.1, 0.1)))
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        tri(d, [(cx, cy), (cx + sx * 26, cy), (cx, cy + sy * 26)], ramp(edge, 0.9))
    if title:
        text(d, x0 + 30, y0 + 34, title, 30, ramp(edge, 0.85), anchor='lm')
        line2(d, (x0 + 18, y0 + 62), (x1 - 18, y0 + 62), 2, ramp(edge, 0.4))
    if tab:
        tw = text_w(tab, 24) + 36
        panel(d, skew_rect(x1 - tw - 24, y0 + 16, tw, 36, 8), ramp_dark(edge), 0.5, ('tab', seed), nu=3, nv=1)
        text(d, x1 - tw / 2 - 20, y0 + 34, tab, 24, ramp(edge, 0.9), anchor='mm')
    return img, d


def ramp_dark(st):
    return [mix(c, hexc('#05050a'), 0.7) for c in st]


def cycle_price(d, x, y, n, st):
    facet(d, polar(x, y, 12, 12, 0, 2 * math.pi, 0.55, 1.0), 8, 1, toner(st, 0.75, var=0.1), ('cy', x, y), 0.1,
          wrap_u=True)
    tri(d, [(x - 3, y), (x + 3, y), (x, y - 5)], ramp(st, 0.9))
    text(d, x + 24, y + 1, str(n), 30, ui.CREAM, anchor='lm')


def chip_icon(d, cx, cy, s, st, seed):
    """A faceted microchip: bevelled frame, pins, stepped core."""
    for k in range(5):
        for side in (-1, 1):
            px = cx - s * 0.6 + k * s * 0.3
            tri(d, [(px - 4, cy + side * s * 0.7), (px + 4, cy + side * s * 0.7), (px, cy + side * s * 0.9)],
                ramp(st, 0.5))
            py = cy - s * 0.6 + k * s * 0.3
            tri(d, [(cx + side * s * 0.7, py - 4), (cx + side * s * 0.7, py + 4), (cx + side * s * 0.9, py)],
                ramp(st, 0.5))
    for r, base in ((0.72, 0.35), (0.5, 0.55), (0.28, 0.85)):
        pts = [(cx - s * r, cy - s * r), (cx + s * r, cy - s * r), (cx + s * r, cy + s * r), (cx - s * r, cy + s * r)]
        inner = [(cx - s * r * 0.7, cy - s * r * 0.7), (cx + s * r * 0.7, cy - s * r * 0.7),
                 (cx + s * r * 0.7, cy + s * r * 0.7), (cx - s * r * 0.7, cy + s * r * 0.7)]
        tones = (0.95, 0.6, 0.3, 0.7)  # top, right, bottom, left bevels
        for k in range(4):
            a, b = pts[k], pts[(k + 1) % 4]
            ia, ib = inner[k], inner[(k + 1) % 4]
            tri(d, [a, b, ib], ramp(st, base + (tones[k] - 0.6) * 0.5))
            tri(d, [a, ib, ia], ramp(st, base + (tones[k] - 0.6) * 0.5 - 0.05))
    facet(d, bil([(cx - s * 0.2, cy - s * 0.2), (cx + s * 0.2, cy - s * 0.2), (cx + s * 0.2, cy + s * 0.2),
                  (cx - s * 0.2, cy + s * 0.2)]), 2, 2, toner(st, 0.9, var=0.08), ('chipc', seed), 0.2)


def upgrade_icon(img, cx, cy, icon, st, seed, ang):
    """Card-builder item: a battered paper card with an ink glyph."""
    cw, ch = 130, 150
    cim = Image.new('RGBA', (cw * SS, ch * SS), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cim)

    def paper(u, v, i, j, k, rc):
        t = 0.66 - 0.2 * v + rc.uniform(-0.07, 0.07)
        if rc.random() < 0.12:
            t -= 0.25
        return ramp(ui.PAPER, t)
    facet(cd, bil([(0, 0), (cw, 0), (cw, ch), (0, ch)]), 4, 5, paper, ('upp', seed), 0.35)
    ui.draw_icon(cd, icon, 22, 24, cw - 44, ch - 48, [mix(c, hexc('#2a1a14'), 0.3) for c in st])
    cd.polygon([(0, 0), (22 * SS, 0), (0, 18 * SS)], fill=(0, 0, 0, 0))
    ui.paste_card(img, cim, cx, cy, ang)


# ------------------------------------------------------------------ scrawl
def scrawl(img):
    lay = Image.new('RGBA', (640 * SS, 420 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for dx, dy in ((0, 0), (2, 0), (0, 2), (2, 2), (1, 1)):
        text(d, 60 + dx, 70 + dy, 'UPGRADE', 88, PINK + (255,), anchor='lm', style=None, path=HAND)
        text(d, 200 + dx, 175 + dy, 'OR', 88, PINK + (255,), anchor='lm', style=None, path=HAND)
        text(d, 150 + dx, 285 + dy, 'DIE!', 96, PINK + (255,), anchor='lm', style=None, path=HAND)
    # lightning bolt and crown doodles in marker strokes
    for a, b in (((450, 130), (400, 240)), ((400, 240), (460, 235)), ((460, 235), (400, 360))):
        line2(d, a, b, 7, PINK + (255,))
    crown = [(170, 392), (174, 360), (196, 378), (216, 352), (236, 378), (258, 360), (262, 392), (170, 392)]
    for k in range(len(crown) - 1):
        line2(d, crown[k], crown[k + 1], 5, PINK + (255,))
    lay = lay.rotate(8, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (int(1340 * SS), int(262 * SS)))


# ------------------------------------------------------------------ render
def render():
    img = backdrop().convert('RGBA')
    d = ImageDraw.Draw(img)
    walkway(d)
    figure(d, 600, 945)
    modem_sign(d)
    stickers(img, d)
    img = img.convert('RGB')
    # MICROCHIPS
    px0, px1 = 320, 1350
    img, d = glass_panel(img, px0, 100, px1, 440, 'chips', title='MICROCHIPS', tab='CYCLE')
    chips = [('SPEED CHIP', NEON['cyan'], 25), ('DEF CHIP', NEON['magenta'], 35), ('SHIELD CHIP', NEON['cyan'], 50),
             ('XP CHIP', NEON['magenta'], 75)]
    cw = (px1 - px0) / 4
    for k, (name, st, price) in enumerate(chips):
        cx = px0 + cw * (k + 0.5)
        if k:
            line2(d, (px0 + cw * k, 185), (px0 + cw * k, 425), 2, ramp(EDGE, 0.35))
        facet(d, bil([(cx - 76, 182), (cx + 76, 182), (cx + 76, 312), (cx - 76, 312)]), 3, 3,
              toner(ramp_dark(st), 0.6, var=0.08), ('cbg', k), 0.3)
        chip_icon(d, cx, 247, 48, st, k)
        text(d, cx, 350, name, 28, ui.CREAM, anchor='mm', style='Bold SemiCondensed')
        cycle_price(d, cx - 36, 398, price, st)
    # CARD BUILDER
    img, d = glass_panel(img, px0, 465, px1, 800, 'cards', title='CARD BUILDER', tab='CYCLE')
    ups = [('+1 SPEED', 'bolt', ui.KIND['block'], 30), ('+2 ARMOR', 'shield', ui.KIND['block'], 50),
           ('+1 REGEN', 'virus', ui.KIND['charge'], 40), ('+1 DAMAGE', 'blade', ui.KIND['hack'], 60)]
    img = img.convert('RGBA')
    for k, (name, icon, st, price) in enumerate(ups):
        cx = px0 + cw * (k + 0.5)
        upgrade_icon(img, cx, 612, icon, st, k, (-4, 3, -2, 5)[k])
    d = ImageDraw.Draw(img)
    for k, (name, icon, st, price) in enumerate(ups):
        cx = px0 + cw * (k + 0.5)
        if k:
            line2(d, (px0 + cw * k, 550), (px0 + cw * k, 785), 2, ramp(EDGE, 0.35))
        text(d, cx, 712, name, 28, ui.CREAM, anchor='mm', style='Bold SemiCondensed')
        cycle_price(d, cx - 36, 758, price, NEON['cyan'])
    img = img.convert('RGB')
    # SHOP NOTES
    img, d = glass_panel(img, 1440, 60, 1880, 330, 'notes', title='SHOP NOTES')
    for k, line in enumerate(('Limited Stock', 'No Refunds', 'Better Chips', 'Better Runs')):
        y = 150 + k * 44
        tri(d, [(1470, y - 8), (1470, y + 8), (1482, y)], ramp(EDGE, 0.8))
        text(d, 1496, y, line, 26, hexc('#d8e4ec'), anchor='lm', style='SemiBold')
    # INVENTORY
    img, d = glass_panel(img, 1470, 720, 1880, 1050, 'inv', title='INVENTORY')
    rows = (('CHIPS', '3'), ('CARDS', '5'), ('CREDITS', '240'))
    for k, (lab, val) in enumerate(rows):
        y = 822 + k * 76
        if k == 0:
            chip_icon(d, 1520, y, 24, EDGE, 'inv0')
        elif k == 1:
            facet(d, bil([(1500, y - 30), (1538, y - 26), (1534, y + 30), (1496, y + 26)]), 2, 3,
                  toner(ui.PAPER, 0.6, var=0.08), 'invc', 0.3)
        else:
            facet(d, polar(1520, y, 28, 28, 0, 2 * math.pi, 0.0, 1.0), 8, 2, toner(NEON['sodium'], 0.6, var=0.12),
                  'invg', 0.2, wrap_u=True)
            facet(d, polar(1520, y, 28, 28, 0, 2 * math.pi, 0.45, 0.62), 8, 1, toner(NEON['sodium'], 0.25), 'invr', 0.1,
                  wrap_u=True)
        text(d, 1570, y, lab, 28, ui.CREAM, anchor='lm', style='Bold SemiCondensed')
        text(d, 1850, y, val, 32, ramp(EDGE, 0.85), anchor='rm')
    img = img.convert('RGBA')
    scrawl(img)
    img = rain(img.convert('RGB'), 'mrain_near', n=180, col=(180, 180, 220), alpha=(25, 55), length=(60, 140))
    return img


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(HERE), 'modem_shop.png')
    finalize(render()).save(out, optimize=True)
    print('wrote', out)
