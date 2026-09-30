"""Still 07: the black-market shop from the outside. A storefront wedged into a gritty street under a
tall vertical MODEM neon sign whose light spills over walls and the wet street; the shop UI sits in a
panel beside it."""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel, skew_rect, tri, gem, gradient,
                     text, text_w, NEON, line2, catenary, layer, composite, rain, smog, Lights, HAND)
import ui

SOOT = R('#05050a', '#0c0b14', '#15131e', '#201c2a', '#2c2636', '#3a3244', '#4c4254')
BRICK = R('#0a0506', '#160a0c', '#241014', '#34181c', '#462226', '#5a2e30', '#6e3c3a')
CONC = R('#070708', '#0f0f12', '#18181c', '#232228', '#302e34', '#403c42', '#524c52')
GROUND = R('#020206', '#06060e', '#0e0c18', '#181424', '#241e34', '#383048')

SIGN_X0, SIGN_X1, SIGN_Y0, SIGN_Y1 = 640, 780, 36, 600


def lights():
    L = []
    for k in range(6):
        y = SIGN_Y0 + 40 + k * (SIGN_Y1 - SIGN_Y0 - 80) / 5
        L.append((((SIGN_X0 + SIGN_X1) / 2, y), 380, ramp(NEON['magenta'], 0.62), 0.17))
    L.append(((520, 628), 300, ramp(NEON['cyan'], 0.6), 0.4))       # CYBER SHOP sign
    L.append(((520, 800), 330, ramp(NEON['sodium'], 0.6), 0.3))     # shop interior glow
    L.append(((110, 520), 260, ramp(NEON['sodium'], 0.6), 0.35))     # street lamp
    L.append(((1060, 360), 240, ramp(NEON['acid'], 0.6), 0.3))      # neighbour's sign
    return Lights(L, cell=150.0)


def facade(d, Lt, x0, x1, y0, y1, st, seed, cols, rows, win_rows=True):
    def cf(u, v, i, j, k, rc):
        t = 0.5 - 0.25 * v + rc.uniform(-0.05, 0.05)
        if win_rows and j % 2 == 1 and hsh(i, j, len(str(seed))) < 0.55:
            if hsh(i, j, 3, len(str(seed))) < 0.12:
                return ramp(NEON['sodium'], 0.25 + 0.1 * rc.random())
            t -= 0.2
        if hsh(i, 7, len(str(seed))) < 0.3 and v > 0.3:
            t -= 0.1  # grime streak
        if rc.random() < 0.05:
            return ramp(ui.RUST, 0.25)
        return ramp(st, t)
    q = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    facet(d, bil(q), cols, rows, Lt.wrap(cf, bil(q)), seed, 0.25)


def storefront(d, Lt, lay_d):
    # recess and interior glow (caged shelves visible under the half-open shutter)
    q = [(330, 700), (730, 700), (730, 890), (330, 890)]

    def inside(u, v, i, j, k, rc):
        t = 0.28 + 0.25 * v + rc.uniform(-0.08, 0.08)
        return mix(ramp(NEON['sodium'], t), ramp(NEON['magenta'], t), 0.35 if u > 0.6 else 0.0)
    facet(d, bil(q), 5, 3, inside, 'inside', 0.3)
    # goods silhouettes and cage bars
    rng = random.Random(5)
    for k in range(7):
        gx = 350 + k * 54
        gy = rng.uniform(790, 840)
        tri(d, [(gx, 870), (gx + 40, 870), (gx + 20, gy)], ramp(SOOT, 0.3))
        tri(d, [(gx + 20, gy), (gx + 40, 870), (gx + 30, 870)], ramp(SOOT, 0.15))
    for x in range(340, 730, 26):
        line2(d, (x, 745), (x, 890), 3, ramp(SOOT, 0.2))
    line2(d, (330, 870), (730, 870), 8, ramp(ui.RUST, 0.35))
    # half-open roll-up shutter with graffiti tags
    sq = [(322, 640), (738, 640), (738, 745), (322, 745)]

    def shut(u, v, i, j, k, rc):
        t = 0.45 + (0.12 if j % 2 == 0 else -0.1) + rc.uniform(-0.04, 0.04)
        if rc.random() < 0.08:
            return ramp(ui.RUST, 0.35)
        return ramp(ui.METAL, t)
    facet(d, bil(sq), 6, 6, Lt.wrap(shut, bil(sq)), 'shutter', 0.1)
    for gx, st in ((360, NEON['acid']), (560, NEON['cyan'])):
        pts = [(gx, 700)]
        for k in range(6):
            pts.append((pts[-1][0] + rng.uniform(12, 26), 668 + (rng.uniform(0, 12) if k % 2 else rng.uniform(40, 60))))
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            tri(d, [(a[0] - 4, a[1]), (a[0] + 4, a[1]), b], mix(ramp(st, 0.6), hexc('#2a2630'), 0.25))
    # door frame pillars
    for x in (300, 738):
        facet(d, bil([(x, 600), (x + 22, 600), (x + 22, 895), (x, 895)]), 1, 3, toner(CONC, 0.35, var=0.05), ('pil', x), 0.2)
    # CYBER SHOP sign above the shutter (small dense facets)
    cq = [(360, 606), (700, 606), (700, 650), (360, 650)]
    facet(d, bil(cq), 1, 1, toner(SOOT, 0.1), 'cyb_bg', 0.0)
    for x in range(366, 694, 16):
        tri(d, [(x, 609), (x + 12, 609), (x + 6, 613)], ramp(NEON['cyan'], 0.75))
        tri(d, [(x, 647), (x + 12, 647), (x + 6, 643)], ramp(NEON['cyan'], 0.6))
    text(d, 530, 629, 'CYBER SHOP', 30, ramp(NEON['cyan'], 0.9), anchor='mm', shadow=ramp(NEON['cyan'], 0.3), sh=2)
    # dripping awning over the shop window
    for k in range(14):
        x0 = 300 + k * 33
        st = R('#061a22', '#0e3444', '#18505e') if k % 2 == 0 else R('#1a0a10', '#3a1420', '#582030')
        tri(d, [(x0, 655), (x0 + 33, 655), (x0 + 16, 690)], ramp(st, 0.6))
        tri(d, [(x0 + 16, 655), (x0 + 33, 655), (x0 + 16, 690)], ramp(st, 0.3))
        if hsh(k, 9) < 0.6:
            L = 20 + 60 * hsh(k, 11)
            lay_d.polygon([((x0 + 15) * SS, 690 * SS), ((x0 + 18) * SS, 690 * SS), ((x0 + 16.5) * SS, (690 + L) * SS)],
                          fill=(200, 210, 230, 120))


def modem_sign(d):
    x0, x1, y0, y1 = SIGN_X0, SIGN_X1, SIGN_Y0, SIGN_Y1
    # brackets to the wall
    for y in (80, 300, 540):
        line2(d, (x0 - 70, y), (x0, y + 10), 6, ramp(ui.METAL, 0.3))
        line2(d, (x0 - 70, y + 40), (x0, y + 10), 4, ramp(ui.METAL, 0.2))
    # sign box: dark, small dense facets
    facet(d, bil([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 4, 16, toner(SOOT, 0.2, gu=-0.2, var=0.06, flip=0.1),
          'modem_bg', 0.3)
    # neon tube frame, a few dead segments
    rng = random.Random(3)
    n = 34
    for k in range(n):
        y = y0 + 8 + (y1 - y0 - 16) * k / n
        for x, s in ((x0 + 8, 1), (x1 - 8, -1)):
            c = ramp(NEON['magenta'], 0.2 if rng.random() < 0.08 else 0.8)
            tri(d, [(x, y), (x, y + 12), (x + s * 5, y + 6)], c)
    for x in range(int(x0) + 10, int(x1) - 10, 14):
        tri(d, [(x, y0 + 8), (x + 10, y0 + 8), (x + 5, y0 + 13)], ramp(NEON['magenta'], 0.8))
        tri(d, [(x, y1 - 8), (x + 10, y1 - 8), (x + 5, y1 - 13)], ramp(NEON['magenta'], 0.8))
    # stacked letters
    letters = 'MODEM'
    step = (y1 - y0 - 40) / len(letters)
    for k, ch in enumerate(letters):
        cy = y0 + 20 + step * (k + 0.5)
        text(d, (x0 + x1) / 2 + 3, cy + 3, ch, 96, ramp(NEON['magenta'], 0.25), anchor='mm')
        text(d, (x0 + x1) / 2, cy, ch, 96, ramp(NEON['magenta'], 0.9 if k != 3 else 0.8), anchor='mm')
        # hot core facets on each letter
        tri(d, [((x0 + x1) / 2 - 30, cy - 4), ((x0 + x1) / 2 - 18, cy - 4), ((x0 + x1) / 2 - 24, cy + 4)],
            ramp(NEON['magenta'], 1.0))


def street(d, Lt, lay_d):
    # kerb and sidewalk
    facet(d, bil([(0, 890), (1240, 890), (1240, 915), (0, 915)]), 10, 1, Lt.wrap(toner(CONC, 0.5, var=0.06),
                                                                               bil([(0, 890), (1240, 890), (1240, 915), (0, 915)])), 'kerb', 0.3)
    gq = [(0, 915), (1240, 915), (1240, H), (0, H)]

    def gf(u, v, i, j, k, rc):
        t = 0.3 + 0.25 * v + rc.uniform(-0.05, 0.05)
        if rc.random() < 0.12:
            t += 0.25
        return ramp(GROUND, t)
    facet(d, bil(gq), 8, 3, Lt.wrap(gf, bil(gq)), 'street', 0.35)
    # MODEM reflection: mirrored faceted bands in the puddles
    x0, x1 = SIGN_X0, SIGN_X1
    for k in range(9):
        y = 925 + k * 17
        w = (x1 - x0) * (1 + k * 0.08)
        cx = (x0 + x1) / 2 + k * 3
        a = max(50, 235 - k * 18)
        q = [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 * 1.02, y + 12), (cx - w / 2 * 1.02, y + 12)]
        facet(lay_d, bil(q), 3, 1, lambda u, v, i, j, kk, rc, a=a: None if rc.random() < 0.25 else
              ramp(NEON['magenta'], 0.7 + rc.uniform(-0.15, 0.2)) + (int(a * rc.uniform(0.6, 1.0)),), ('mref', k), 0.35)
    for (cx, st, w) in ((530, NEON['cyan'], 300), (530, NEON['sodium'], 360), (110, NEON['sodium'], 120)):
        q = [(cx - w / 2, 925), (cx + w / 2, 925), (cx + w * 0.6, 1080), (cx - w * 0.6, 1080)]
        facet(lay_d, bil(q), 4, 4, lambda u, v, i, j, k, rc, st=st: None if rc.random() < 0.35 else
              ramp(st, 0.6 + rc.uniform(-0.1, 0.2)) + (int(110 * (1 - v)) + 10,), ('sref', cx, w), 0.35)


def part_icon(d, kind, x, y, s):
    if kind == 'slice':
        facet(d, polar(x, y + s * 0.55, s, s, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 0.2, 1.0), 4, 3,
              toner(ui.KIND['hack'], 0.55, gu=-0.3, var=0.1), 'pi_s', 0.3)
        facet(d, polar(x, y + s * 0.55, s, s, -math.pi / 2 - 0.55, -math.pi / 2 + 0.55, 1.0, 1.14), 8, 1,
              lambda u, v, i, j, k, rc: ramp(NEON['sodium'] if i % 2 == 0 else ui.DARK, 0.5), 'pi_sr', 0.1)
    elif kind == 'pointer':
        pst = R('#1a0c06', '#4a1e0c', '#9a4412', '#e07a1c', '#ffc060', '#fff0c0')
        for off in (-0.22, 0.22):
            cx = x + off * s
            top, tip, w = y - s * 0.5, y + s * 0.45, s * 0.2
            tri(d, [(cx - w, top), (cx, top - 5), (cx, tip)], ramp(pst, 0.85))
            tri(d, [(cx, top - 5), (cx + w, top), (cx, tip)], ramp(pst, 0.4))
    else:
        for k in range(10):
            a = k * 2 * math.pi / 10
            p0 = (x + s * 0.55 * math.cos(a - 0.14), y + s * 0.55 * math.sin(a - 0.14))
            p1 = (x + s * 0.55 * math.cos(a + 0.14), y + s * 0.55 * math.sin(a + 0.14))
            p2 = (x + s * 0.68 * math.cos(a), y + s * 0.68 * math.sin(a))
            tri(d, [p0, p1, p2], ramp(ui.METAL, 0.3 + 0.4 * (0.5 + 0.5 * math.cos(a - ui.LIGHT_DIR))))
        facet(d, polar(x, y, s * 0.58, s * 0.58, 0, 2 * math.pi, 0.0, 1.0), 10, 2, toner(ui.METAL, 0.45, var=0.12),
              'pi_h', 0.2, wrap_u=True)
        gem(d, x, y, s * 0.22, s * 0.22, NEON['sodium'], 'pi_hg', n=6, base=0.5)


def price_tape(d, cx, y, price, seed, ang=-4, w=104):
    ui.tape_strip(d, cx, y, w, ang, seed, h=30, alpha=240)
    text(d, cx, y + 1, f'{price} cr', 26, hexc('#1a1410'), anchor='mm', style=None, path=HAND)


def shop_panel(img, d):
    px0, py0, px1, py1 = 1210, 36, 1890, 1044
    panel(d, [(px0, py0), (px1, py0), (px1, py1), (px0, py1)], ui.DARK, 0.3, 'spanel', nu=3, nv=4, gv=-0.2, var=0.04,
          flip=0.04)
    for k in range(16):
        x = px0 + 16 + k * 22
        tri(d, [(x, py0), (x + 11, py0), (x - 4, py0 + 8)], ramp(NEON['sodium'], 0.6))
    text(d, px0 + 30, py0 + 52, 'MODEM', 44, ramp(NEON['magenta'], 0.85), anchor='lm')
    text(d, px0 + 30, py0 + 92, 'CYBER SHOP  //  NO NAMES, NO REFUNDS', 16, hexc('#a89ca0'), anchor='lm',
         style='Bold SemiCondensed')
    gem(d, px1 - 170, py0 + 56, 20, 24, NEON['sodium'], 'credg', n=6, base=0.55)
    text(d, px1 - 142, py0 + 56, '240 CR', 32, ui.CREAM, anchor='lm')
    # programs
    text(d, px0 + 30, py0 + 150, 'PROGRAMS', 22, hexc('#f0d8c8'), anchor='lm')
    wares = [('attack', 'SPIKE STORM', 2, ['Deal 4, three', 'times'], 'blade', 60),
             ('block', 'MIRROR WALL', 1, ['GUARD 6. Reflect', 'half'], 'shield', 75),
             ('hack', 'GHOST KEY', 2, ['Skip a foe', 'slice'], 'eye', 110)]
    for k, (kind, title, cost, lines, icon, price) in enumerate(wares):
        cimg = ui.card_image(kind, title, cost, lines, icon, ('ext', k))
        cimg = cimg.resize((int(ui.CW * 0.95 * SS), int(ui.CH * 0.95 * SS)), Image.LANCZOS)
        cx = px0 + 130 + k * 215
        ui.paste_card(img, cimg, cx, py0 + 330, (1 - k) * 2.0)
        price_tape(d, cx, py0 + 485, price, ('ptc', k), ang=(-5, 3, -2)[k])
    # rig parts
    text(d, px0 + 30, py0 + 545, 'RIG PARTS', 22, hexc('#f0d8c8'), anchor='lm')
    parts = [('slice', 'OVERCLOCK SLICE', 150), ('pointer', 'TWIN-FANG POINTER', 90), ('hub', 'FLYWHEEL HUB', 120)]
    for k, (kind, name, price) in enumerate(parts):
        cx = px0 + 130 + k * 215
        facet(d, polar(cx, py0 + 650, 88, 88, 0, 2 * math.pi, 0, 1), 6, 1, toner(ui.DARK, 0.5, var=0.05), ('pp', k),
              0.2, wrap_u=True)
        part_icon(d, kind, cx, py0 + 648, 84)
        text(d, cx, py0 + 758, name, 17, ui.CREAM, anchor='mm', style='Bold SemiCondensed')
        price_tape(d, cx, py0 + 796, price, ('ptp', k), ang=(4, -3, 2)[k])
    # buttons
    panel(d, skew_rect(px0 + 30, py1 - 150, 250, 74, 14), ui.DARK, 0.5, 'reroll', nu=3, nv=1, gv=-0.3)
    text(d, px0 + 60, py1 - 113, 'REROLL', 28, ui.CREAM, anchor='lm')
    text(d, px0 + 230, py1 - 112, '25', 24, ramp(NEON['sodium'], 0.8), anchor='mm')

    def leave(u, v, i, j, k, rc):
        return ramp(NEON['cyan'], 0.5 - 0.25 * (v - 0.5) + rc.uniform(-0.08, 0.08))
    facet(d, bil(skew_rect(px1 - 330, py1 - 160, 300, 96, 20)), 4, 2, leave, 'leave', 0.3)
    text(d, px1 - 205, py1 - 111, 'LEAVE', 46, ui.INK, anchor='mm')
    for k in range(2):
        ax = px1 - 110 + k * 28
        tri(d, [(ax, py1 - 134), (ax + 24, py1 - 111), (ax, py1 - 88)], ramp(R('#021a2a', '#063a50', '#0a5a70'), 0.3 + 0.4 * k))


def render():
    Lt = lights()
    img = gradient(lambda u, v: mix(mix(hexc('#05040c'), hexc('#1e0c28'), v), hexc('#3a0e34'), max(0, 0.3 - abs(u - 0.36)) * 1.5)).convert('RGB')
    d = ImageDraw.Draw(img)
    # distant towers (big calm facets)
    rng = random.Random(21)
    x = -30
    while x < 1260:
        w = rng.uniform(80, 180)
        top = rng.uniform(20, 240)
        facet(d, bil([(x, top), (x + w, top), (x + w, 600), (x, 600)]), 1, 2,
              toner(R('#07060e', '#0e0a18', '#150f22', '#1c142c'), rng.uniform(0.3, 0.9), var=0.04), ('bt', x), 0.3)
        x += w * 0.8
    img = smog(img, 'ext_smog_far', [(180, 200, 60, 140)], R('#1a0c2a', '#2a1236', '#3a1a44', '#122838'))
    d = ImageDraw.Draw(img)
    # street buildings: calm facets, lit by the neon
    facade(d, Lt, -20, 300, 120, 895, BRICK, 'bl', 4, 10)
    facade(d, Lt, 300, 760, 250, 600, CONC, 'shopbld', 5, 8)
    facade(d, Lt, 760, 1240, 170, 895, SOOT, 'br', 5, 10)
    facade(d, Lt, 300, 760, 600, 895, CONC, 'shopgf', 3, 2, win_rows=False)
    # neighbour's broken acid sign, AC units, pipes
    facet(d, bil([(1010, 250), (1100, 250), (1100, 470), (1010, 470)]), 2, 7,
          lambda u, v, i, j, k, rc: None if rc.random() < 0.3 else ramp(NEON['acid'], 0.7 + rc.uniform(-0.25, 0.2)),
          'acid_sign', 0.3)
    for (ax, ay) in ((360, 330), (520, 430), (880, 520), (140, 400)):
        facet(d, bil([(ax, ay), (ax + 70, ay), (ax + 70, ay + 46), (ax, ay + 46)]), 2, 1,
              Lt.wrap(toner(CONC, 0.55, gu=-0.3, var=0.08), bil([(ax, ay), (ax + 70, ay), (ax + 70, ay + 46), (ax, ay + 46)])),
              ('ac', ax), 0.3)
        line2(d, (ax + 10, ay + 46), (ax + 12, 895), 3, ramp(ui.RUST, 0.3))
    for x in (290, 752):
        line2(d, (x, 120 if x < 300 else 170), (x, 895), 8, ramp(ui.RUST, 0.25))
    # street lamp
    line2(d, (110, 895), (110, 520), 7, ramp(ui.METAL, 0.25))
    line2(d, (110, 520), (170, 500), 5, ramp(ui.METAL, 0.25))
    tri(d, [(150, 500), (190, 496), (170, 516)], ramp(NEON['sodium'], 0.85))
    # cables strung across the street
    for k in range(8):
        a = (rng.uniform(-40, 300), rng.uniform(120, 420))
        b = (rng.uniform(760, 1260), rng.uniform(170, 460))
        catenary(d, a, b, rng.uniform(40, 130), 2.2, ramp(SOOT, 0.08), n=16)
    lay, ld = layer(img)
    storefront(d, Lt, ld)
    modem_sign(d)
    street(d, Lt, ld)
    # coloured haze around the MODEM sign and the doorway
    for (cx, cy, rx, ry, st, a) in ((710, 330, 260, 330, NEON['magenta'], 40), (530, 760, 260, 130, NEON['sodium'], 35)):
        facet(ld, polar(cx, cy, rx, ry, 0, 2 * math.pi, 0, 1), 8, 2,
              lambda u, v, i, j, k, rc, st=st, a=a: ramp(st, 0.5) + (int(a * (1 - v) + rc.uniform(0, 10)),),
              ('haze', cx), 0.35, wrap_u=True)
    img = composite(img, lay)
    d = ImageDraw.Draw(img)
    img = rain(img, 'ext_rain', n=700, col=(170, 170, 210), alpha=(30, 75), length=(40, 110),
               region=(0, 0, 1260, H))
    img = img.convert('RGBA')
    d = ImageDraw.Draw(img)
    shop_panel(img, d)
    return img.convert('RGB')
