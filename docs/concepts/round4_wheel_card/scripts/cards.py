"""Round 4 cards: C-A faceted print, C-B data chip, C-C sticker card, C-D terminal card."""
import math
import random
from common import *
import sticker_lib as SL

CARDS = [
    dict(key='backspin', title='BACKSPIN', short='BACKSPIN', cost=1, type='WHEEL', rarity='Common',
         picto=[('ccw', None), ('num', '9')], text=['Spin a wheel 9 ticks', 'counter-clockwise.']),
    dict(key='arcflash', title='ARC FLASH', short='ARC FLASH', cost=2, type='HACK', rarity='Uncommon',
         picto=[('bolt', None), ('num', '3'), ('all', None)], text=['Deal 3 damage to', 'every enemy.']),
    dict(key='bulwark', title='BULWARK', short='BULWARK', cost=2, type='SYSTEM', rarity='Uncommon',
         picto=[('defend', None), ('num', '12')], text=['Gain 12 block.']),
    dict(key='leech', title='LEECH WORM', short='LEECH', cost=3, type='HACK', rarity='Rare',
         picto=[('worm', None), ('num', '1/2')], text=['Slice under your pointer', 'gets PARASITE. Exhaust.']),
]
RAM = ramp_of('#9BE8FF')
PAPERR = R('#2a2620', '#4a443a', '#6e6656', '#948a74', '#b8ac90', '#d4c8aa', '#ece2c8')


# ------------------------------------------------------------------ illustrations (flat Cv2 facets, no outlines)
def art_bg(d, x, y, w, h, stops, seed):
    facet(d, bil([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]), max(2, int(w / 40)), max(2, int(h / 40)),
          toner(stops, 0.3, gu=-0.25, gv=-0.3, var=0.05, flip=0.08), seed, 0.3)


def art(d, key, x, y, w, h):
    cx, cy, s = x + w / 2, y + h / 2, min(w, h)
    if key == 'backspin':
        art_bg(d, x, y, w, h, TYPE['WHEEL'], 'a_bs')
        cols = ['attack', 'defend', 'evade', 'attack', 'afflict', 'miss']
        for k in range(6):
            a0 = -math.pi / 2 + k * math.pi / 3
            facet(d, polar(cx, cy + s * 0.04, 1, 1, a0, a0 + math.pi / 3, s * 0.08, s * 0.32), 2, 1,
                  lambda u, v, i, j, kk, rc, c=cols[k], a=a0: ramp(SLICE[c], 0.42 + 0.2 * math.cos(a + 2.2) + rc.uniform(-0.03, 0.03)),
                  ('bsw', k), 0.2)
        fpoly(d, circ(cx, cy + s * 0.04, s * 0.09, 6), ramp(METAL, 0.6))
        arrow_ccw(d, cx, cy + s * 0.04, s * 0.42, max(3, s * 0.07), ramp(TYPE['WHEEL'], 0.72))
    elif key == 'arcflash':
        art_bg(d, x, y, w, h, TYPE['HACK'], 'a_af')
        heads = [(x + w * 0.2, y + h * 0.72), (x + w * 0.5, y + h * 0.78), (x + w * 0.8, y + h * 0.7)]
        src = (x + w * 0.5, y + h * 0.16)
        rng = random.Random(4)
        for hx, hy in heads:
            pts = [src] + [(src[0] + (hx - src[0]) * t + rng.uniform(-s * 0.06, s * 0.06), src[1] + (hy - src[1]) * t)
                           for t in (0.25, 0.5, 0.75)] + [(hx, hy - s * 0.1)]
            for a, b in zip(pts, pts[1:]):
                line2(d, a, b, max(2, s * 0.04), ramp_of('#9BE8FF')[5])
        for k, (hx, hy) in enumerate(heads):
            fpoly(d, circ(hx, hy, s * 0.12, 6, ry=s * 0.09), ramp(MER, 0.5 + 0.1 * k))
            fpoly(d, circ(hx, hy + 1, s * 0.035, 5), ramp(SLICE['attack'], 0.8))
        fpoly(d, circ(src[0], src[1], s * 0.08, 8), ramp(SODIUM, 0.8))
    elif key == 'bulwark':
        art_bg(d, x, y, w, h, TYPE['SYSTEM'], 'a_bw')
        for k in range(4):
            px = x + w * (0.1 + k * 0.21)
            top = y + h * (0.16 + 0.05 * (k % 2))
            fpoly(d, [(px, top), (px + w * 0.2, top - h * 0.03), (px + w * 0.21, y + h * 0.9), (px + 2, y + h * 0.92)],
                  ramp(STEEL, 0.45 + 0.12 * (k % 2)))
            fpoly(d, [(px + w * 0.2, top - h * 0.03), (px + w * 0.21, y + h * 0.9), (px + w * 0.23, y + h * 0.9),
                      (px + w * 0.22, top)], ramp(STEEL, 0.2))
        glyph(d, 'defend', cx, cy, s * 0.5, ramp(TYPE['SYSTEM'], 0.62), ramp(STEEL, 0.45))
    elif key == 'leech':
        art_bg(d, x, y, w, h, R('#140618', '#2a0c34', '#44185a', '#5e2478'), 'a_lw')
        facet(d, polar(cx, cy + h * 0.5, 1, 1, -math.pi / 2 - 0.5, -math.pi / 2 + 0.5, s * 0.25, s * 0.85), 3, 2,
              lambda u, v, i, j, k, rc: ramp(SLICE['attack'], 0.45 + rc.uniform(-0.04, 0.04)), 'lw_sl', 0.2)
        pts = [(x + w * (0.22 + 0.09 * k), y + h * (0.42 + 0.12 * math.sin(k * 0.9))) for k in range(7)]
        for k, (px, py) in enumerate(pts):
            fpoly(d, circ(px, py, s * (0.07 - 0.004 * k), 8), ramp(SLICE['afflict'], 0.55 + 0.05 * (k % 2)))
        hx, hy = pts[0]
        fpoly(d, circ(hx - s * 0.03, hy, s * 0.03, 5), ramp(SLICE['attack'], 0.85))


def picto(d, items, x, y, hgt, col, bg):
    """Pictogram row starting at x (left), vertically centred on y. Returns end x."""
    for kind, val in items:
        if kind == 'ccw':
            arrow_ccw(d, x + hgt * 0.5, y, hgt * 0.36, max(2, hgt * 0.13), col)
            x += hgt * 1.05
        elif kind == 'bolt':
            bolt(d, x + hgt * 0.4, y, hgt * 0.95, col)
            x += hgt * 0.85
        elif kind == 'defend':
            glyph(d, 'defend', x + hgt * 0.45, y, hgt * 0.9, col, bg)
            x += hgt * 0.95
        elif kind == 'worm':
            for k in range(4):
                fpoly(d, circ(x + hgt * (0.2 + k * 0.2), y + hgt * 0.12 * math.sin(k * 1.4), hgt * 0.16, 6), col)
            x += hgt * 1.0
        elif kind == 'all':
            for k in range(3):
                fpoly(d, circ(x + hgt * (0.22 + k * 0.3), y, hgt * 0.14, 6), col)
            x += hgt * 0.95
        elif kind == 'num':
            text(d, x, y + 1, val, hgt * 0.95, col, anchor='lm', style=None, path=ANTON)
            x += text_w(val, hgt * 0.95, style=None) * 0.62 + hgt * 0.35
    return x


# ------------------------------------------------------------------ C-A faceted print
def card_A(c, w, h, afford=True):
    img, d = new_layer(w, h)
    small = w < 160
    rar = ramp_of(RARITY_HEX[c['rarity']])
    ty = TYPE[c['type']]
    # paper border
    facet(d, bil([(0, 0), (w, 0), (w, h), (0, h)]), max(3, int(w / 40)), max(4, int(h / 40)),
          toner(PAPERR, 0.72, gu=-0.1, gv=-0.15, var=0.04, flip=0.05), ('pa', c['key'], w), 0.3)
    # rarity edge: a coloured frame band + a corner flag
    e = max(3, w * 0.025)
    for q in ([(0, 0), (w, 0), (w, e), (0, e)], [(0, h - e), (w, h - e), (w, h), (0, h)], [(0, 0), (e, 0), (e, h), (0, h)],
              [(w - e, 0), (w, 0), (w, h), (w - e, h)]):
        fpoly(d, q, rar[4])
    fpoly(d, [(w - w * 0.22, 0), (w, 0), (w, w * 0.22)], rar[4])
    m = w * 0.06
    # title
    ty_title = h * 0.085
    text(d, w * 0.58 if not small else w * 0.6, ty_title, c['title'] if not small else c['short'],
         h * (0.058 if not small else 0.075), INK, anchor='mm', style='Bold Condensed')
    # art
    ax, ay, aw, ah = m, h * 0.15, w - 2 * m, h * (0.4 if not small else 0.42)
    art(d, c['key'], ax, ay, aw, ah)
    # type band
    by = ay + ah
    bh = h * (0.065 if not small else 0.075)
    fpoly(d, [(m, by), (w - m, by), (w - m, by + bh), (m, by + bh)], ty[4])
    text(d, w / 2, by + bh / 2 + 1, c['type'], bh * 0.78, INK, anchor='mm', style='Bold')
    # pictogram row: big at every size
    ph = h * (0.1 if not small else 0.15)
    py = by + bh + ph * 0.85
    picto(d, c['picto'], m + w * 0.04, py, ph, INK, PAPERR[5])
    if not small:
        for k, ln in enumerate(c['text']):
            text(d, w / 2, py + ph * 0.95 + k * h * 0.052, ln, h * 0.042, INK, anchor='mm', style='SemiBold')
        text(d, w - m, h - m * 1.1, c['rarity'].upper(), h * 0.034, rar[2], anchor='rm', style='Bold')
    # cost gem
    gr = w * (0.13 if not small else 0.19)
    gc = (gr * 0.95, gr * 0.95)
    gst = RAM if afford else ramp_of('#FF4656')
    gem(d, gc[0], gc[1], gr, gr, gst, ('cg', c['key'], w), n=6, base=0.55)
    text(d, gc[0], gc[1] + 1, str(c['cost']), gr * 1.05, INK, anchor='mm', style=None, path=ANTON)
    return to1x(img)


# ------------------------------------------------------------------ C-B data chip
def card_B(c, w, h, afford=True):
    img, d = new_layer(w, h)
    small = w < 160
    ty = TYPE[c['type']]
    shell = [mix(col, (10, 10, 14), 0.45) for col in ty]
    ch = w * 0.12
    outline = [(ch, 0), (w - ch, 0), (w, ch), (w, h - ch * 0.4), (w - ch * 0.4, h), (ch * 0.4, h), (0, h - ch * 0.4), (0, ch)]
    rar = c['rarity']
    if rar == 'Uncommon':
        # translucent shell: internal traces visible through it
        trace_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(trace_layer)
        fpoly(td, outline, ramp(DARK, 0.3) + (255,))
        rng = random.Random(c['key'])
        for k in range(14):
            y0 = rng.uniform(0.1, 0.9) * h
            x0 = rng.uniform(0.05, 0.5) * w
            line2(td, (x0, y0), (x0 + rng.uniform(0.2, 0.45) * w, y0), max(1, w * 0.008), ramp(SODIUM, 0.5) + (255,))
        img.alpha_composite(trace_layer)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        facet(ImageDraw.Draw(lay), poly_fpos(outline, (w / 2, h / 2)), 16, 3,
              lambda u, v, i, j, k, rc: ramp(shell, 0.55 + 0.12 * (0.5 - v) + rc.uniform(-0.04, 0.04)) + (150,),
              ('sh', c['key'], w), 0.25, wrap_u=True)
        img.alpha_composite(lay)
    else:
        facet(d, poly_fpos(outline, (w / 2, h / 2)), 16, 3,
              lambda u, v, i, j, k, rc: ramp(shell, 0.5 + 0.14 * (0.5 - v) + rc.uniform(-0.03, 0.03)),
              ('sh', c['key'], w), 0.25, wrap_u=True)
        if rar == 'Rare':
            holo = SL.holo_tex(img.width, img.height, seed=5, phase=0.2, sat=0.6)
            m = Image.new('L', img.size, 0)
            ImageDraw.Draw(m).polygon([(p[0] * SS, p[1] * SS) for p in outline], fill=120)
            holo.putalpha(m)
            img.alpha_composite(holo)
            d = ImageDraw.Draw(img)
    d = ImageDraw.Draw(img)
    # grip ridges
    for k in range(5):
        y = h * 0.035 + k * h * 0.012
        line2(d, (w * 0.3, y), (w * 0.7, y), max(1, h * 0.005), ramp(shell, 0.25))
    # label window (paper label with the illustration)
    lx, ly, lw, lh = w * 0.09, h * 0.11, w * 0.82, h * (0.62 if not small else 0.6)
    fpoly(d, [(lx, ly), (lx + lw, ly), (lx + lw, ly + lh), (lx, ly + lh)], PAPERR[5])
    art(d, c['key'], lx + w * 0.03, ly + h * 0.07, lw - w * 0.06, lh * (0.58 if not small else 0.6))
    text(d, lx + lw / 2, ly + h * 0.04, c['title'] if not small else c['short'], h * (0.045 if not small else 0.07), INK,
         anchor='mm', style='Bold Condensed')
    ph = h * (0.085 if not small else 0.12)
    py = ly + lh - ph * 0.75
    picto(d, c['picto'], lx + w * 0.05, py, ph, INK, PAPERR[5])
    if not small:
        ty0 = ly + lh + h * 0.012
        fpoly(d, [(lx, ty0), (lx + lw, ty0), (lx + lw, ty0 + h * 0.105), (lx, ty0 + h * 0.105)], ramp(DARK, 0.15))
        for k, ln in enumerate(c['text']):
            text(d, w / 2, ty0 + h * 0.03 + k * h * 0.045, ln, h * 0.038, CREAM, anchor='mm', style='SemiBold')
    # type embossed + contact edge
    text(d, w * 0.1, h * (0.9 if not small else 0.83), c['type'], h * (0.035 if not small else 0.06), ramp(ty, 0.75),
         anchor='lm', style='Bold')
    n = 9 if not small else 6
    for k in range(n):
        x0 = w * 0.12 + k * (w * 0.76) / n
        fpoly(d, [(x0, h * 0.94), (x0 + w * 0.76 / n * 0.62, h * 0.94), (x0 + w * 0.76 / n * 0.62, h * 0.995), (x0, h * 0.995)],
              ramp(HAZ, 0.6 if k % 2 else 0.5))
    # cost LED
    lr = w * (0.085 if not small else 0.14)
    lc = (w - lr * 1.5, lr * 1.5)
    lst = RAM if afford else ramp_of('#FF4656')
    fpoly(d, circ(lc[0], lc[1], lr * 1.25, 16), ramp(DARK, 0.2))
    fpoly(d, circ(lc[0], lc[1], lr, 16), lst[5])
    fpoly(d, circ(lc[0] - lr * 0.3, lc[1] - lr * 0.3, lr * 0.3, 8), lst[6])
    text(d, lc[0], lc[1] + 1, str(c['cost']), lr * 1.35, INK, anchor='mm', style=None, path=ANTON)
    # rarity tag
    if not small:
        text(d, w * 0.9, h * 0.9, {'Common': 'MATTE', 'Uncommon': 'CLEAR', 'Rare': 'HOLO'}.get(rar, rar.upper()), h * 0.03,
             ramp(ty, 0.7), anchor='rm', style='Bold')
    return to1x(img)


# ------------------------------------------------------------------ C-C sticker card
def card_C_art(c, w, h, afford=True):
    """The printed face of the sticker (at SL.SS), padded for the die-cut border."""
    small = w < 160
    S = SL.SS
    P = int(30 * S)
    W2, H2 = int(w * S) + 2 * P, int(h * S) + 2 * P
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = P / S, P / S       # lowpoly coords are 1x * SS; S == SS
    ty = TYPE[c['type']]
    rr = int(w * 0.08 * S)
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([P, P, P + w * S, P + h * S], radius=rr, fill=255)
    face = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    facet(fd, bil([(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)]), 4, 5,
          toner([mix(col, (8, 8, 12), 0.6) for col in ty], 0.4, gv=-0.25, var=0.04, flip=0.05), ('cc', c['key'], w), 0.3)
    face.putalpha(ImageChops.multiply(face.getchannel('A'), m))
    im.alpha_composite(face)
    d = ImageDraw.Draw(im)
    art(d, c['key'], ox + w * 0.06, oy + h * 0.17, w * 0.88, h * (0.4 if not small else 0.44))
    text(d, ox + w * 0.58, oy + h * 0.09, c['title'] if not small else c['short'], h * (0.065 if not small else 0.085),
         CREAM, anchor='mm', style=None, path=ANTON)
    # type ribbon
    by = oy + h * (0.59 if not small else 0.63)
    fpoly(d, [(ox, by), (ox + w, by), (ox + w, by + h * 0.06), (ox, by + h * 0.06)], ty[4])
    text(d, ox + w / 2, by + h * 0.03 + 1, c['type'], h * 0.048, INK, anchor='mm', style='Bold')
    ph = h * (0.1 if not small else 0.15)
    py = by + h * 0.06 + ph * 0.85
    picto(d, c['picto'], ox + w * 0.1, py, ph, CREAM, ramp(DARK, 0.3))
    if not small:
        for k, ln in enumerate(c['text']):
            text(d, ox + w / 2, py + ph * 0.9 + k * h * 0.05, ln, h * 0.04, CREAM, anchor='mm', style='SemiBold')
        for k in range({'Common': 1, 'Uncommon': 2, 'Rare': 3}.get(c['rarity'], 4)):
            fpoly(d, circ(ox + w * 0.86 - k * w * 0.06, oy + h * 0.95, w * 0.018, 5, -math.pi / 2), ramp_of(RARITY_HEX[c['rarity']])[4])
    # cost dot (yellow vinyl dot)
    gr = w * (0.12 if not small else 0.18)
    gx, gy = ox + gr * 0.95, oy + gr * 0.95
    fpoly(d, circ(gx, gy, gr, 24), INK)
    fpoly(d, circ(gx, gy, gr * 0.86, 24), SL.YELLOW if afford else (150, 146, 140))
    text(d, gx, gy + 1, str(c['cost']), gr * 1.15, INK, anchor='mm', style=None, path=ANTON)
    return im


def card_C(c, w, h, afford=True, curl=None, phase=0.0):
    art_im = card_C_art(c, w, h, afford)
    holo = c['rarity'] == 'Rare'
    sd = SL.build_sticker(art_im, border=max(5, w * 0.045), material='gloss', close=6, gloss_pos=0.3 + phase,
                          seed=len(c['key']), holo_border=holo, holo_phase=phase, curl=curl)
    return sd


def sticker_to_img(sd, shadow=1.0, hover=0.0, opacity=1.0, angle=0.0):
    w, h = sd['img'].size
    canvas = Image.new('RGBA', (w // SL.SS + 120, h // SL.SS + 120), (0, 0, 0, 0))
    out = SL.place(canvas, sd, canvas.width / 2, canvas.height / 2, angle=angle, shadow=shadow, hover=hover, opacity=opacity)
    return out


# ------------------------------------------------------------------ C-D terminal card
def card_D(c, w, h, afford=True):
    img, d = new_layer(w, h)
    small = w < 160
    ty = TYPE[c['type']]
    neon = ty[4]
    ch = w * 0.07
    outline = [(ch, 0), (w, 0), (w, h - ch), (w - ch, h), (0, h), (0, ch)]
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    facet(ImageDraw.Draw(lay), poly_fpos(outline, (w / 2, h / 2)), 14, 3,
          lambda u, v, i, j, k, rc: ramp(DARK, 0.35 + 0.15 * (0.5 - v) + rc.uniform(-0.03, 0.03)) + (236,),
          ('gl', c['key'], w), 0.25, wrap_u=True)
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    # glass sheen
    fpoly(d, [(ch, 0), (w * 0.55, 0), (w * 0.2, h * 0.45), (0, h * 0.45), (0, ch)], mix(ramp(DARK, 0.5), (255, 255, 255), 0.04))
    # neon edge by rarity
    rar = c['rarity']
    ew = max(1.5, w * 0.009)
    pts = outline + [outline[0]]
    for a, b in zip(pts, pts[1:]):
        line2(d, a, b, ew * 2.6, mix(neon, (0, 0, 0), 0.6))
        line2(d, a, b, ew, neon)
    if rar in ('Uncommon', 'Rare', 'Boss'):
        inset = w * 0.03
        o2 = [(ch + inset * 0.4, inset), (w - inset, inset), (w - inset, h - ch - inset * 0.4), (w - ch - inset * 0.4, h - inset),
              (inset, h - inset), (inset, ch + inset * 0.4)]
        for a, b in zip(o2 + [o2[0]], o2[1:] + [o2[0]]):
            line2(d, a, b, max(1, ew * 0.6), mix(neon, (0, 0, 0), 0.3))
    if rar == 'Rare':
        gold = ramp_of(RARITY_HEX['Rare'])[5]
        L = w * 0.16
        for (x0, y0, sx, sy) in ((w, 0, -1, 1), (0, h, 1, -1)):
            line2(d, (x0, y0), (x0 + sx * L, y0), ew * 2.2, gold)
            line2(d, (x0, y0), (x0, y0 + sy * L), ew * 2.2, gold)
    # header: cost + title, monospace
    m = w * 0.07
    cs = w * (0.13 if not small else 0.2)
    cst = RAM if afford else ramp_of('#FF4656')
    fpoly(d, [(m, m), (m + cs, m), (m + cs, m + cs), (m, m + cs)], cst[5] if afford else cst[4])
    text(d, m + cs / 2, m + cs / 2 + 1, str(c['cost']), cs * 0.85, INK, anchor='mm', style=None, path=ANTON)
    text(d, m + cs + w * 0.04, m + cs * 0.5, c['title'] if not small else c['short'], h * (0.05 if not small else 0.07), CREAM,
         anchor='lm', style=None, path=MONO)
    if not small:
        text(d, w - m, m + cs * 0.5 + h * 0.045, f'> {c["type"]}', h * 0.034, neon, anchor='rm', style=None, path=MONO)
    # illustration in a thin frame
    ax, ay, aw, ah = m, m + cs + h * 0.03, w - 2 * m, h * (0.36 if not small else 0.4)
    art(d, c['key'], ax, ay, aw, ah)
    for a, b in (((ax, ay), (ax + aw, ay)), ((ax + aw, ay), (ax + aw, ay + ah)), ((ax + aw, ay + ah), (ax, ay + ah)),
                 ((ax, ay + ah), (ax, ay))):
        line2(d, a, b, max(1, ew * 0.7), mix(neon, (0, 0, 0), 0.35))
    for k in range(int(ah / 4)):
        line2(d, (ax, ay + k * 4), (ax + aw, ay + k * 4), 0.6, (0, 0, 0))
    # pictograms in the type colour
    ph = h * (0.09 if not small else 0.14)
    py = ay + ah + ph * 0.9
    picto(d, c['picto'], m + w * 0.02, py, ph, neon, ramp(DARK, 0.3))
    if not small:
        for k, ln in enumerate(c['text']):
            text(d, m, py + ph * 0.9 + k * h * 0.048, ln, h * 0.036, CREAM, anchor='lm', style=None, path=MONO)
        text(d, m, h - m, f'RARITY: {rar.upper()}', h * 0.03, mix(neon, (120, 120, 120), 0.4), anchor='lb', style=None, path=MONO)
    return to1x(img)


# ------------------------------------------------------------------ backs
def back(ver, w, h):
    img, d = new_layer(w, h)
    if ver == 'A':
        facet(d, bil([(0, 0), (w, 0), (w, h), (0, h)]), 6, 8, toner(PAPERR, 0.7, var=0.04), 'bkA', 0.3)
        facet(d, bil([(w * 0.08, h * 0.06), (w * 0.92, h * 0.06), (w * 0.92, h * 0.94), (w * 0.08, h * 0.94)]), 6, 8,
              toner(DARK, 0.35, gv=-0.2, var=0.05), 'bkA2', 0.3)
        fpoly(d, circ(w / 2, h / 2, w * 0.3, 6, math.pi / 6), RAM[4])
        fpoly(d, circ(w / 2, h / 2, w * 0.22, 6, math.pi / 6), ramp(DARK, 0.3))
        bolt(d, w / 2, h / 2, w * 0.3, ramp(SODIUM, 0.75))
        text(d, w / 2, h * 0.84, 'REBEL_CELL', h * 0.05, PAPERR[5], anchor='mm', style='Bold')
    elif ver == 'B':
        ch = w * 0.12
        outline = [(ch, 0), (w - ch, 0), (w, ch), (w, h - ch * 0.4), (w - ch * 0.4, h), (ch * 0.4, h), (0, h - ch * 0.4), (0, ch)]
        facet(d, poly_fpos(outline, (w / 2, h / 2)), 16, 3, toner(DARK, 0.4, var=0.04), 'bkB', 0.25, wrap_u=True)
        rng = random.Random(8)
        for k in range(16):
            y0 = rng.uniform(0.1, 0.85) * h
            x0 = rng.uniform(0.05, 0.5) * w
            line2(d, (x0, y0), (x0 + rng.uniform(0.2, 0.45) * w, y0), max(1, w * 0.006), ramp(SODIUM, 0.45))
        for k in range(9):
            x0 = w * 0.12 + k * (w * 0.76) / 9
            fpoly(d, [(x0, h * 0.94), (x0 + w * 0.05, h * 0.94), (x0 + w * 0.05, h * 0.995), (x0, h * 0.995)], ramp(HAZ, 0.55))
        text(d, w / 2, h * 0.5, 'CELL//ROM', h * 0.06, RAM[5], anchor='mm', style=None, path=MONO)
    elif ver == 'D':
        ch = w * 0.07
        outline = [(ch, 0), (w, 0), (w, h - ch), (w - ch, h), (0, h), (0, ch)]
        facet(d, poly_fpos(outline, (w / 2, h / 2)), 14, 3, toner(DARK, 0.35, var=0.03), 'bkD', 0.25, wrap_u=True)
        for a, b in zip(outline + [outline[0]], outline[1:] + [outline[0]]):
            line2(d, a, b, 2, RAM[4])
        for k in range(12):
            text(d, w * 0.1, h * 0.1 + k * h * 0.065, ''.join(random.Random(k).choice('01') for _ in range(18)), h * 0.035,
                 mix(RAM[4], (0, 0, 0), 0.6), anchor='lm', style=None, path=MONO)
        text(d, w / 2, h / 2, '> JACK IN_', h * 0.06, RAM[5], anchor='mm', style=None, path=MONO)
    return to1x(img)


def back_C(w, h):
    """Sticker backing paper: the peel side."""
    S = SL.SS
    P = int(30 * S)
    im = Image.new('RGBA', (int(w * S) + 2 * P, int(h * S) + 2 * P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([P, P, P + w * S, P + h * S], radius=int(w * 0.08 * S), fill=SL.BACK + (255,))
    for k in range(-8, 14):
        x = P + k * 26 * S
        d.line([(x, P), (x + h * S * 0.5, P + h * S)], fill=(205, 200, 192, 255), width=int(1 * S))
    d.line([(P, P + h * S * 0.62), (P + w * S, P + h * S * 0.55)], fill=(150, 146, 140, 255), width=int(2 * S))
    SL.text_img(d, (P + w * S / 2, P + h * S * 0.36), 'PEEL', SL.ANTON, w * 0.2, SL.INK + (255,))
    SL.text_img(d, (P + w * S / 2, P + h * S * 0.47), 'SLAP ON A WHEEL', SL.PLEX, w * 0.07, (90, 86, 80, 255))
    sd = SL.build_sticker(im, border=max(5, w * 0.045), material='gloss', close=6, gloss_pos=0.34, seed=3)
    return sticker_to_img(sd)


RENDER = {'A': card_A, 'B': card_B, 'D': card_D}
NAMES = {'A': ('C-A', 'FACETED PRINT'), 'B': ('C-B', 'DATA CHIP'), 'C': ('C-C', 'STICKER CARD'), 'D': ('C-D', 'TERMINAL CARD')}


def render_card(ver, c, w, h, afford=True, angle=0.0, hover=0.0, curl=None):
    if ver == 'C':
        sd = card_C(c, w, h, afford, curl=curl)
        return sticker_to_img(sd, hover=hover, angle=angle)
    im = RENDER[ver](c, w, h, afford)
    pad = 40
    can = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', can.size, (0, 0, 0, 0))
    a = im.getchannel('A')
    m = Image.new('L', can.size, 0)
    m.paste(a, (pad + 4 + int(18 * hover), pad + 6 + int(26 * hover)))
    m = m.filter(ImageFilter.GaussianBlur(5 + 10 * hover)).point(lambda v: int(v * 0.6))
    sh.putalpha(m)
    can.alpha_composite(sh)
    can.alpha_composite(im, (pad, pad))
    if angle:
        can = can.rotate(angle, resample=Image.BICUBIC, expand=True)
    return can


def disabled(im):
    g = grey(im)
    dark = Image.new('RGBA', g.size, (10, 10, 14, 0))
    dark.putalpha(g.getchannel('A').point(lambda v: int(v * 0.45)))
    g.alpha_composite(dark)
    d = ImageDraw.Draw(g)
    w, h = g.size
    cx, cy = w / 2, h / 2
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(200, 200, 200, 255), width=5)
    d.line([(cx - 18, cy + 18), (cx + 18, cy - 18)], fill=(200, 200, 200, 255), width=5)
    return g


def need_tag(base, cx, y, ver):
    d = ImageDraw.Draw(base)
    if ver == 'C':
        label(d, cx, y, 'NEED 3 RAM', 22, SL.CORAL, path=MARKER, style=None)
    else:
        d.rectangle([cx - 66, y - 14, cx + 66, y + 14], fill=(140, 20, 34))
        label(d, cx, y, 'NEED 3  HAVE 2', 16, (255, 230, 226), style='Bold')


def card_sheet(ver):
    base = sheet_bg()
    d1 = ImageDraw.Draw(base)
    code, nm = NAMES[ver]
    title(d1, code, nm, 'key info must survive hand size 112 x 148')
    DW, DH = 250, 352
    xs = [170, 450, 730, 1010]
    for k, (c, x) in enumerate(zip(CARDS, xs)):
        paste_c(base, render_card(ver, c, DW, DH), x, 300)
        label(d1, x, 505, f'{c["title"]}  -  {c["rarity"]}', 16)
    label(d1, 590, 535, '1  DETAIL SIZE', 17)
    # card back + greyscale
    bk = back_C(DW, DH) if ver == 'C' else back(ver, DW, DH)
    paste_c(base, bk, 1310, 300)
    label(d1, 1310, 505, '4  CARD BACK', 16)
    g = grey(render_card(ver, CARDS[1], DW, DH))
    paste_c(base, g, 1620, 300)
    label(d1, 1620, 505, '5  GREYSCALE', 16)
    # fanned hand at hand size
    hx, hy = 330, 820
    for k, c in enumerate(CARDS):
        off = k - 1.5
        im = render_card(ver, c, 112, 148, angle=-off * 6)
        paste_c(base, im, hx + off * 100, hy + abs(off) ** 1.6 * 8)
    label(d1, hx, 965, '2  HAND SIZE 112 x 148 (fanned)', 16)
    gh = Image.new('RGBA', (520, 260), (0, 0, 0, 0))
    for k, c in enumerate(CARDS):
        off = k - 1.5
        im = grey(render_card(ver, c, 112, 148, angle=-off * 6))
        paste_c(gh, im, 260 + off * 100, 120 + abs(off) ** 1.6 * 8)
    paste_c(base, gh, 790, 820)
    label(d1, 790, 965, 'hand in greyscale', 16)
    # states on one card (Leech Worm, cost 3, at 1.5x hand size)
    sw, sh = 168, 222
    c = CARDS[3]
    hov = render_card(ver, c, int(sw * 1.08), int(sh * 1.08), hover=1.0,
                      curl=dict(corner='tr', amount=0.14) if ver == 'C' else None)
    paste_c(base, hov, 1190, 790)
    label(d1, 1190, 965, 'HOVER / FOCUS', 16)
    ca = render_card(ver, c, sw, sh, afford=False)
    paste_c(base, ca, 1440, 800)
    need_tag(base, 1440, 925, ver)
    label(d1, 1440, 965, "CAN'T AFFORD", 16)
    dis = disabled(render_card(ver, c, sw, sh))
    paste_c(base, dis, 1690, 800)
    label(d1, 1690, 965, 'DISABLED', 16)
    label(d1, 1440, 1010, '3  STATES', 17)
    out = os.path.join(OUT, f'card_{ver}.png')
    base.convert('RGB').save(out, optimize=True)
    print('wrote', os.path.basename(out))


if __name__ == '__main__':
    import sys as _s
    for v in (_s.argv[1:] or ['A', 'B', 'C', 'D']):
        card_sheet(v)
