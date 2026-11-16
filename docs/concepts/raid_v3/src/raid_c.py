"""raid_c: set 7, the six raid plates in direction C (the happy medium, designer pick after low_text), plus the sheet.

    python raid_c.py [plan place shop playback site aftermath sheet]      -> raid_v3/r3_*.png, r3_sheet.jpg, insp/c_counts.json

C = pictograms and numbers for everything live (low_text's A pieces), ONE corp document kept as a document (the intercepted work
order, folded to a corner at rest: seal, ROUND n · units, and the next round as icons with counts), the after-action report
kept as corp paper.  Icons: raid_icons (bible glyph grammar; the LOCKED set where it has one, proposals where not).
Unfold during a drag: hold Tab (shown on r3_place); the corner's next-round row covers the common need without unfolding.
Every string drawn is registered (low_text.say / doc), so the word counts come from the plates.  Text >= 16 px cap.
"""
import json, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import raid_v3_city as V
import raid_kit as K
import raid_v3 as R
import low_text as LT
import raid_icons as RI
from raid_kit import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, HARM, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                      W, H, SS, F_all, glass, stick, S_GAIN, S_HARM, S_HI, S_MID, S_SCHED, TEAL, TEAL_D, TEAL_HI)

G = V.G
OUT = V.OUT
GOLD = (255, 210, 40)
RED_H = (236, 40, 90)
say, T = LT.say, LT.T


# ------------------------------------------------------------------ glyphs into the low_text pieces
GMAP = {'heart': 'core', 'shield': 'holds', 'skull': 'kills', 'drop': 'leak', 'flame': 'heat', 'undo': 'undo', 'reroll': 'reroll',
        'place': 'place', 'lock': 'locked', 'spin': 'resolving', 'evacuate': 'evacuate', 'tab': 'tab'}
_ico0 = LT.ico


def gpaste(im, name, x, y, px, col=(255, 255, 255), alpha=255):
    """a raid glyph centred at (x, y) screen px, long side px screen, onto an SS image"""
    g = RI.glyph(name, int(S(px)), col, alpha=alpha)
    im.alpha_composite(g, (int(S(x) - g.width / 2), int(S(y) - g.height / 2)))
    return g.width / SS


def ico_c(d, kind, x, y, r, col=TEXT_HI, shadow=True, alpha=255):
    if kind == 'coin':
        IR.ram_coin(d, x, y, None, None, r=r * 0.9)
    elif kind in GMAP:
        gpaste(d._image, GMAP[kind], x, y, 2 * r, col, alpha)
    else:
        _ico0(d, kind, x, y, r, col, shadow, alpha)


LT.ico = ico_c


def op_c(oid, curl=None, grey=False):
    key = ('opc', oid, curl, grey)
    if key in LT._C:
        return LT._C[key]
    o = K.OPS[oid]
    w, h, pad = K.OPW, K.OPH, K.OPPAD
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    body.paste(K._op_body(o['shape'], w, h), (S(pad), S(pad)))

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        gm = IR.glyph_mask(o['g'], S(42))
        gx, gy = ox + S(w / 2) - gm.width // 2, oy + S(h * 0.25) - gm.height // 2
        art.paste(Image.new('RGBA', gm.size, PAPER + (255,)), (gx + S(2), gy + S(2)), gm)
        art.paste(Image.new('RGBA', gm.size, INK + (255,)), (gx, gy), gm)
        K.anton_name(d, ox + S(w / 2), oy + S(h * 0.56), oid, 46 if len(oid) <= 3 else 42)
        n = o['lvl']
        py_ = oy + S(h * (0.82 if o['shape'] != 'shield' else 0.78))
        for k in range(n):
            px = ox + S(w / 2 + (k - (n - 1) / 2) * 22)
            d.polygon([(px, py_ - S(8)), (px + S(8), py_), (px, py_ + S(8)), (px - S(8), py_)], fill=PAPER + (255,), outline=INK + (255,), width=S(2.4))

    sd = K.vinyl(body, o['col'][0], o['col'][1], deco, border=8, curl=curl, grey=grey)
    LT._C[key] = sd
    return sd


def wpn_c(name, stars, cost=None, curl=None, grey=False):
    """the weapon gear tag: the weapon glyph (bible grammar, ~34 px on screen in CREW and the shop) + its stars"""
    key = ('wc', name, stars, cost, curl, grey)
    if key in LT._C:
        return LT._C[key]
    g = RI.glyph(name, S(84))
    gw = g.width / SS
    lead = 46 if cost is not None else 0
    w, h, pad = int(lead + 14 + gw + 12 + stars * 22 + 14), 66, 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    ImageDraw.Draw(body).polygon([(S(pad + 10), S(pad)), (S(pad + w), S(pad)), (S(pad + w - 10), S(pad + h)), (S(pad), S(pad + h))], fill=255)

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        art.alpha_composite(g, (int(ox + S(lead + 14)), int(oy + S(h / 2) - g.height / 2)))
        x = ox + S(lead + 14 + gw + 12)
        for k in range(stars):
            d.polygon([(S(px) + x, S(py) + oy) for px, py in K.star_poly(k * 22, h / 2, 10)], fill=GOLD + (255,), outline=INK + (255,))
        if cost is not None:
            LT.big_dot(d, ox + S(24), oy + S(h / 2), cost)

    sd = K.vinyl(body, (58, 52, 70), (22, 19, 28), deco, border=6, curl=curl, grey=grey, ext=4)
    LT._C[key] = sd
    return sd


def dev_c(kind, cost=None, curl=None):
    """a device: a blocky vinyl tile in the device colour (defences are blocky), its glyph in white"""
    key = ('dc', kind, cost, curl)
    if key in LT._C:
        return LT._C[key]
    w, h, pad = 104, 88, 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    ImageDraw.Draw(body).rounded_rectangle([S(pad), S(pad), S(pad + w), S(pad + h)], radius=S(14), fill=255)
    g = RI.glyph(kind, S(64))

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        if kind == 'BARRICADE':                              # the hazard band along the bottom edge, the barricade's identity
            st = Image.new('L', art.size, 0); sd_ = ImageDraw.Draw(st)
            for k in range(-2, 9):
                x = ox + S(k * 18)
                sd_.polygon([(x, oy + S(h - 16)), (x + S(9), oy + S(h - 16)), (x + S(1), oy + S(h)), (x - S(8), oy + S(h))], fill=255)
            st = SL.ImageChops.multiply(st, body.point(lambda v: 255 if v > 128 else 0))
            art.paste(Image.new('RGBA', art.size, INK + (255,)), (0, 0), st)
        art.alpha_composite(g, (int(ox + S(w / 2) - g.width / 2), int(oy + S(h / 2 - (6 if kind == 'BARRICADE' else 0)) - g.height / 2)))
        if cost is not None:
            LT.big_dot(d, ox + S(8), oy + S(6), cost)

    top, bot = K.DEV[kind]
    sd = K.vinyl(body, top, bot, deco, border=6, curl=curl, ext=4)
    LT._C[key] = sd
    return sd


LT.wpn_lt = wpn_c
LT.dev_lt = dev_c
LT.op_lt = lambda oid, curl=None: op_c(oid, curl)


# ------------------------------------------------------------------ chrome
def crew_c(img, placed=(), held=None, away=None, kills=None, weapons=None, merge=False):
    def fn(Lm):
        py, pr = Wax(PEN_Y, 91), Wax(PEN_R, 92)
        for oid, (x, y, ang) in K.CREW_POS.items():
            o = K.OPS[oid]
            gone = bool(away and oid in away)
            sd = op_c(oid, grey=gone)
            if oid == held:
                K.liner(Lm, sd, x, y, ang)
                continue
            stick(Lm, sd, x, y, ang)
            stick(Lm, wpn_c(o['wpn'], (weapons or {}).get(oid, o['stars']), grey=gone), x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2], scale=0.82)
            say(oid)
            if gone:
                pr.text(away[oid], x - 4, y + 106, 34, angle=-6); say(away[oid])
            elif oid in placed:
                py.tick(x + 4, y + 106, 17, 7)
            if kills and oid in kills:
                py.x(x - 30, y + 106, 12, 6); py.text(str(kills[oid]), x + 10, y + 108, 40, angle=-6); say(str(kills[oid]))
        if merge:                                            # pencil: star + star -> two stars, and the arrow onto RUNE's tag
            p = Wax(PEN_Y, 7)
            K.pen_star(p, 250, 742, 14); p.text('+', 280, 744, 34); K.pen_star(p, 310, 742, 14)
            p.arrow([(336, 744), (356, 742), (378, 743)], width=5, head=10)
            K.pen_star(p, 404, 742, 14); K.pen_star(p, 436, 740, 14)
            p.arrow([(534, 428), (546, 452), (534, 474)], width=5, head=12)
            p.ink_ss(Lm)
        py.ink_ss(Lm); pr.ink_ss(Lm)
        if merge:
            sx, sy, sa = K.CREW_POS['RUNE']
            wx, wy = sx + K.WPN_OFF[0], sy + K.WPN_OFF[1]
            stick(Lm, wpn_c('SHOTGUN', 1, cost=3, curl=0.16), wx - 8, wy - 58, 3, scale=0.84, lift=0.7)
    V.ui(img, fn, (0, 0))


def folded(img, rounds, now=0, heat=25):
    """the work order folded to a corner: seal, ROUND n · units, and the NEXT round printed under it as small icons with
    counts (the shop's look-ahead without unfolding); the unfold chevron + the Tab key on the glass; Heat beside it"""
    w, h = 340, 132
    pim = Image.new('RGBA', (S(w), S(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(pim)
    body = [(0, 0), (w, 0), (w, h - 30), (w - 30, h), (0, h)]
    d.polygon([(S(x), S(y)) for x, y in body], fill=(236, 230, 214, 255))
    rng = np.random.default_rng(5)
    for _ in range(300):
        d.point((rng.uniform(0, S(w)), rng.uniform(0, S(h))), fill=(212, 204, 186, 255))
    d.polygon([(S(w), S(h - 30)), (S(w - 30), S(h - 30)), (S(w - 30), S(h))], fill=(206, 198, 180, 255), outline=(170, 162, 146, 255))
    LT.seal(d, 44, 46, 30)
    n = sum(g[3] for g in rounds[now][1])
    T(d, (88, 44), 'ROUND %d \u00b7 %d' % (now + 1, n), 34, INK, where=LT.DOC)
    d.rectangle([S(88), S(66), S(250), S(68)], fill=TEAL_D + (255,))
    st = Image.new('L', (S(80), S(40)), 0); sd = ImageDraw.Draw(st)
    sd.rectangle([S(2), S(2), S(120), S(60)], outline=255, width=S(3.5))
    pim.paste(Image.new('RGBA', st.size, (196, 30, 40, 200)), (S(w - 46), S(4)), st.rotate(7, resample=Image.BICUBIC))
    if now + 1 < len(rounds):                                # the next round, printed small and grey: number, icons, counts
        y = 102
        d.ellipse([S(14), S(y - 13), S(40), S(y + 13)], fill=(96, 92, 86, 255))
        T(d, (27, y + 1), str(now + 2), 20, (236, 230, 214), anchor='mm', where=LT.DOC)
        gx = 52
        for path, kind, label, cnt in rounds[now + 1][1]:
            ic = V.icon_img(kind, 1.0, 9, ring=False)
            ic = ic.copy(); ic.putalpha(ic.split()[3].point(lambda v: int(v * 0.8)))
            pim.alpha_composite(ic, (int(S(gx + 10) - ic.width / 2), int(S(y) - ic.height / 2)))
            gx += 24 + T(d, (gx + 24, y + 1), '\u00d7%d' % cnt, 22, (70, 66, 60), where=LT.DOC) + 16
    LT.put_paper(img, pim, LT.RX0 + 12 + w / 2, 14 + h / 2, -2.0)
    L = Layer(); d = L.d
    cx, cy = LT.RX0 + 12 + w / 2, 14 + h + 16
    d.line([(S(cx - 14), S(cy - 4)), (S(cx), S(cy + 6)), (S(cx + 14), S(cy - 4))], fill=CYAN + (220,), width=S(3))
    LT.keycap(d, cx + 26, cy - 15, 48)
    comp(img, L)
    gpaste(img, 'tab', cx + 50, cy + 2, 26, TEXT_HI)
    L = Layer(); d = L.d
    gpaste(img, 'heat', LT.RX1 - 70, cy, 28, (255, 120, 60))
    T(d, (LT.RX1 - 50, cy + 1), str(heat), 30, TEXT_HI)
    comp(img, L)
    return 14 + h + 34


def right_c(img, F, rounds, peeled=None, locked=False, busy=False, unfold=False, heat=25):
    y = folded(img, rounds, heat=heat)
    y = LT.shop_lt(img, y + 8, peeled=peeled)
    LT.reroll_lt(img, y + 12)
    if locked:                                               # the shop is locked during the round: dimmed, the locked glyph
        L = Layer(); L.d.rectangle([S(LT.RX0), S(y - 198), S(LT.RX1), S(y + 60)], fill=(6, 8, 12, 150)); comp(img, L)
        gpaste(img, 'locked', (LT.RX0 + LT.RX1) / 2, y - 80, 52, TEXT_HI)
    if busy:
        stick(img, K.greyed(K.verb_sticker('SEND IT')), 1765, 708, 4, scale=0.9 * V.UI_S); say('SEND', 'IT')
        L = Layer(); d = L.d
        glass(d, (1700, 756, 1830, 800))
        comp(img, L)
        gpaste(img, 'resolving', 1765, 778, 30, CYAN)
    else:
        LT.send_lt(img, F)
    if unfold:                                               # held Tab: the order unfolds over the shop (works mid-drag)
        LT.memo(img, LT.RX0 - 16, 14, 404, rounds, ang=-0.6, crease=True)
        L = Layer(); d = L.d
        LT.keycap(d, LT.RX0 - 70, 470, 48)
        d.rounded_rectangle([S(LT.RX0 - 70), S(470 + 4), S(LT.RX0 - 22), S(470 + 38)], radius=S(6), outline=GOLD + (255,), width=S(2.4))
        comp(img, L)
        gpaste(img, 'tab', LT.RX0 - 46, 489, 26, GOLD)


def left_c(img, core=8, lose=0, rnd=1, rmax=4, credits=7, cost=0, undo=True, **crew):
    LT.core_lt(img, core, lose)
    LT.rows_lt(img, rnd, rmax, credits, cost)
    crew_c(img, **crew)
    if undo:
        LT.undo_lt(img)


def strip_c(img, items, box=(560, 956, 1360, 1008)):
    """the one short glass strip (low_text.strip + tick segments, stars, ghost units)"""
    x0, y0, x1, y1 = box
    ym = (y0 + y1) / 2

    def run(d, x, draw):
        for it in items:
            k = it[0]
            if k == 'chip':
                if draw:
                    LT.path_chip(d, x + 15, ym, it[1], r=15)
                x += 36
            elif k == 'ico':
                if draw:
                    ico_c(d, it[1], x + 16, ym, 16, it[2])
                x += 38
            elif k == 'txt':
                f = TR.font(ANTON, 30)
                if draw:
                    T(d, (x, ym + 1), it[1], 30, it[2])
                x += d.textlength(it[1], font=f) / SS + 12
            elif k == 'sep':
                if draw:
                    d.ellipse([S(x + 8), S(ym - 3), S(x + 14), S(ym + 3)], fill=S_MID + (255,))
                x += 26
            elif k == 'ticks':                                # n of m tick segments
                n, m = it[1], it[2]
                for j in range(m):
                    if draw:
                        d.rectangle([S(x + j * 14), S(ym - 10), S(x + j * 14 + 10), S(ym + 10)], fill=(CYAN if j < n else (40, 70, 84)) + (255,),
                                    outline=INK + (255,), width=S(1.5))
                x += m * 14 + 10
            elif k == 'stars':
                for j in range(it[1]):
                    if draw:
                        d.polygon([(S(x + 11 + px), S(ym + py)) for px, py in K.star_poly(0, 0, 12)], fill=GOLD + (255,), outline=INK + (255,), width=S(2))
                    x += 24
                x += 4
            elif k == 'unit':
                if draw:
                    ic = V.icon_img(it[1], 1.0, 11, ring=False).copy()
                    ic.putalpha(ic.split()[3].point(lambda v: int(v * it[2])))
                    d._image.alpha_composite(ic, (int(S(x + 16) - ic.width / 2), int(S(ym) - ic.height / 2)))
                x += 36
            elif k == 'glyph':
                if draw:
                    gpaste(d._image, it[1], x + 18, ym, it[3] if len(it) > 3 else 32, it[2])
                x += (it[3] if len(it) > 3 else 32) + 8
        return x

    L = Layer(); d = L.d
    wdt = run(d, 0, False)
    cx = (x0 + x1) / 2
    bx0, bx1 = cx - wdt / 2 - 22, cx + wdt / 2 + 22
    glass(d, (bx0, y0, bx1, y1))
    comp(img, L)
    L = Layer(); d = L.d
    run(d, bx0 + 22, True)
    comp(img, L)


PLAN_STRIP = [('chip', 'A'), ('ico', 'shield', S_GAIN), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2', S_HARM), ('sep',),
              ('ico', 'heart', RED_H), ('txt', '8 \u2192 6', S_HARM), ('sep',), ('ico', 'skull', S_HI), ('txt', '6/8', S_HI)]


def map_objs(img, placed=None, barricade=True):
    tops = {}
    for oid, (c, r) in sorted((placed or V.PLACED).items(), key=lambda kv: G.cc(*kv[1])[1]):
        tops[oid] = V.beacon(img, oid, c, r)
    if barricade:
        bx, by = G.cc(*V.BARR)
        stick(img, dev_c('BARRICADE'), bx, by - 6, -12, scale=V.STICK['barricade'] * 1.05)
    return tops


LT_MAP0 = LT.map_base


def map_base_c(img, F, words, place=False, pencil='icons', seed=0):
    """low_text.map_base with the device tile on the map (the barricade stuck flatter: it is a tile now, not a bar)"""
    _ds = K.dev_sticker
    LT_MAP0(img, F, words, place, pencil, seed)


# ------------------------------------------------------------------ plates
def blank():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))


def plate_plan():
    F = F_all(); img = blank()
    LT.map_base(img, F, words=False, place=False, pencil='icons')
    left_c(img, 8, 2, placed=V.PLACED)
    right_c(img, F, V.ROUNDS)
    strip_c(img, PLAN_STRIP)
    return img


def plate_place():
    F = F_all(); img = blank()
    LT.map_base(img, F, words=False, place=True, pencil='icons')
    LT.held(img, False, *G.cc(*V.HOVER))
    left_c(img, 8, 0, placed=V.PLACED, held='RUNE')
    right_c(img, F, V.ROUNDS, unfold=True)
    strip_c(img, [('ico', 'place', GOLD), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2 \u2192 0', S_GAIN), ('sep',),
                  ('ico', 'heart', RED_H), ('txt', '8', S_GAIN), ('sep',), ('ico', 'skull', S_HI), ('txt', '8/8', S_HI)])
    return img


def plate_shop():
    F = F_all(); img = blank()
    LT.map_base(img, F, words=False, place=False, pencil='icons', seed=4)
    left_c(img, 8, 2, cost=3, placed=V.PLACED, merge=True)
    right_c(img, F, V.ROUNDS, peeled='SHOTGUN')
    strip_c(img, [('glyph', 'SHOTGUN', TEXT_HI, 44), ('stars', 1), ('txt', '+', S_PLAN_()), ('stars', 1), ('txt', '\u2192', S_MID), ('stars', 2), ('sep',),
                  ('ico', 'coin', CYAN), ('txt', '7 \u2192 4', S_HI)])
    return img


def S_PLAN_():
    return K.S_PLAN


_ico_prev = LT.ico


def _coin(d, kind, x, y, r, col=TEXT_HI, shadow=True, alpha=255):
    if kind == 'coin':
        IR.ram_coin(d, x, y, None, None, r=r * 0.9)
    else:
        ico_c(d, kind, x, y, r, col, shadow, alpha)


def plate_playback():
    F = F_all(); img = blank()
    V.draw_grid(img, F, labels=False)
    V.routes_ground(img)
    placed = dict(V.PLACED, RUNE=V.HOVER)
    for oid in ('KAI', 'VEX'):
        V.reach_outline(img, V.cheb(*placed[oid], K.OPS[oid]['reach']), K.OPS[oid]['col'][0], alpha=120)
    tops = map_objs(img, placed=placed)
    V.unit(img, 'trooper', *G.cc(*V.ENT_A), 1.0, count=3, alpha=0.38)
    V.unit(img, 'bike', *G.cc(*V.ENT_B), 1.0, count=1, alpha=0.38)
    say('3', '1')
    hx, hy = G.cc(*V.BARR_UP)
    bx, by = G.cc(5, 5)
    L = Layer()
    ux, uy = G.cc(6, 5)[0] - bx, G.cc(6, 5)[1] - by
    for k in range(5):
        L.d.line([(S(bx + ux * (0.35 + k * 0.12)), S(by - 28 + uy * (0.35 + k * 0.12))), (S(bx + ux * (0.45 + k * 0.12)), S(by - 28 + uy * (0.45 + k * 0.12)))],
                 fill=(170, 230, 230, 140 - k * 24), width=S(3))
    comp(img, L)
    pr0 = Wax(PEN_R, 10); V.routes(pr0); pr0.ink_ss(img); say('A', 'B')
    V.unit(img, 'trooper', hx, hy, 0.5, pips=('H',), r=22)
    V.unit(img, 'bike', bx, by, 0.5, pips=('S',), r=22); say('H', 'S')
    kx, ky = tops['KAI']; vx, vy = tops['VEX']
    V.tracer(img, (kx, ky), (hx + 8, hy - 28), K.OPS['KAI']['col'][1])
    ex, ey = G.cc(*V.BARR_UP2)
    V.tracer(img, (kx, ky), (ex + 4, ey - 24), K.OPS['KAI']['col'][1])
    V.tracer(img, (vx, vy), (bx - 12, by - 28), K.OPS['VEX']['col'][1])
    V.unit_bits(img, 'trooper', ex, ey, spread=52)
    py = Wax(PEN_Y, 9)
    py.text('2', hx + 58, hy - 82, 32, angle=-6); py.text('1', bx + 58, by - 82, 32, angle=-6); say('2', '1')
    V.wall_hp(py, 6, 4); say('6 \u2192 4')
    for (x, y) in ((kx + 52, ky - 34), (vx + 52, vy - 40)):
        py.x(x, y, 11, 6)
    py.ink_ss(img)
    sx, sy = G.cc(*V.SAFE)
    stick(img, LT.safe_lt(), sx, sy - 12, -3, scale=V.STICK['safe'])
    K.pop(img, F, hx - 76, hy - 80, '\u22124'); K.pop(img, F, bx + 40, by - 108, '\u22123'); say('4', '3')
    # HELD + BOMBARD x2 as a pictogram pill: the H status pip and the mine glyph x2 (no words)
    L = Layer(); d = L.d
    px_, py_ = hx - 214, hy - 34
    d.rounded_rectangle([S(px_ - 70 + 3), S(py_ - 24 + 4), S(px_ + 76 + 3), S(py_ + 24 + 4)], radius=S(24), fill=INK + (255,))
    d.rounded_rectangle([S(px_ - 70), S(py_ - 24), S(px_ + 76), S(py_ + 24)], radius=S(24), fill=(255, 110, 196, 255), outline=INK + (255,), width=S(3))
    pc = V.PIP['H'][0]
    d.ellipse([S(px_ - 58), S(py_ - 16), S(px_ - 26), S(py_ + 16)], fill=pc + (255,), outline=INK + (255,), width=S(2.5))
    T(d, (px_ - 42, py_ + 1), 'H', 22, INK, anchor='mm')
    T(d, (px_ - 20, py_ + 1), '+', 26, INK, anchor='mm')
    comp(img, L)
    gpaste(img, 'MINE', px_ + 10, py_ - 1, 34)
    L = Layer(); T(L.d, (px_ + 32, py_ + 2), '\u00d72', 26, INK); comp(img, L)
    left_c(img, 8, 0, placed=placed)
    right_c(img, F, V.ROUNDS, locked=True, busy=True)
    strip_c(img, [('ticks', 3, 8), ('sep',), ('ico', 'skull', S_GAIN), ('txt', '2', S_GAIN), ('sep',), ('ico', 'drop', S_HI), ('txt', '0', S_HI), ('sep',),
                  ('glyph', 'BARRICADE', TEXT_HI, 30), ('txt', '1', S_HI), ('sep',), ('unit', 'trooper', 0.5), ('txt', '4', S_MID)])
    return img


def plate_site():
    F = F_all(); img = blank()
    V.draw_grid(img, F, labels=False)
    for cells, lt in ((V.SA, 'A'), (V.SB, 'B'), (V.SC, 'C')):
        V.route_ground(img, cells, V.S_ENT[lt], V.SITE)
    V.end_cell(img, V.SITE, col=(150, 236, 130))
    tops = {}
    for oid, cell in (('KAI', V.S_KAI), ('VEX', V.S_VEX)):
        tops[oid] = V.beacon(img, oid, *cell)
    sx, sy = G.cc(*V.SITE)
    cx, cy = G.cc(*V.SCORE)
    py, pr = Wax(PEN_Y, 11), Wax(PEN_R, 12)
    for cells, lt in ((V.SA, 'A'), (V.SB, 'B'), (V.SC, 'C')):
        K.route(pr, V.route_line(cells, V.S_ENT[lt], V.SITE), off=0, head=False)
        K.entry_mark(pr, *V.edge_pt(V.S_ENT[lt], cells[0]), lt); say(lt)
    pr.ink_ss(img)
    # the core: a hex tile with the heart, its 8/8; the site socket with its name
    key = ('corehex',)
    if key not in LT._C:
        w, h, pad = 100, 64, 44
        body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
        ImageDraw.Draw(body).polygon([(S(pad + x * w), S(pad + y * h)) for x, y in [(0.25, 0), (0.75, 0), (1, 0.5), (0.75, 1), (0.25, 1), (0, 0.5)]], fill=255)
        LT._C[key] = K.vinyl(body, LT.PINK_T, LT.PINK_B, lambda d, art: ico_c(d, 'heart', pad + w / 2, pad + h / 2, 22, (255, 236, 244)), border=7, ext=5)
    stick(img, LT._C[key], cx, cy - 4, 3, scale=V.STICK['core'] * 1.2)
    L = Layer(); text(L.d, (cx + 36, cy - 64), '8/8', F['a40'], TEXT_HI + (255,), stroke=2, sfill=INK + (255,)); comp(img, L); say('8/8')
    stick(img, K.place_sticker('B2', None, (150, 236, 130), (62, 170, 70), shape='socket', w=96, h=84), sx, sy - 10, -3, scale=V.STICK['site']); say('B2')
    pr = Wax(PEN_R, 13)
    kx, ky = tops['KAI']; vx, vy = tops['VEX']
    py.arrow([(468, 772), (490, 720), (vx - 30, vy + 64), (vx - 18, vy + 40)], width=6, head=16)
    py.text('C2', 470, 800, 38, angle=-6); say('C2')
    bx_, by_ = G.cc(*V.SB[0])
    LT.pen_drop(pr, bx_ + 86, by_ - 8, 17); pr.text('1', bx_ + 120, by_ - 6, 38, angle=-5); say('1')
    K.pen_arrow_num(pr, 8, 7, cx + 72, cy - 118, 30); say('8 \u2192 7')
    py.ink_ss(img); pr.ink_ss(img)
    for lt, kind, n in (('A', 'trooper', 3), ('B', 'riot', 2), ('C', 'drone', 2)):
        V.unit(img, kind, *G.cc(*V.S_ENT[lt]), 1.0, count=n); say(str(n))
    who_defends(img, F)
    evac_chip(img)
    left_c(img, 8, 1, rnd=1, rmax=3, placed=('KAI', 'VEX'), away={'MOTH': 'A1', 'RUNE': 'D4'})
    right_c(img, F, V.SROUNDS)
    strip_c(img, [('chip', 'A'), ('ico', 'drop', S_GAIN), ('txt', '0', S_GAIN), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '1', S_HARM), ('sep',),
                  ('chip', 'C'), ('ico', 'drop', S_GAIN), ('txt', '0', S_GAIN), ('sep',), ('ico', 'heart', RED_H), ('txt', '8 \u2192 7', S_HARM), ('sep',),
                  ('ico', 'skull', S_HI), ('txt', '6/7', S_HI)])
    return img


def who_defends(img, F):
    """who defends B2, as a pictogram card in the margin: the site socket, a shield, then each defender's mini sticker with
    its tick; VEX's came from C2 (a small arrow from the C2 chip)"""
    x0, y0 = 470, 108
    L = Layer(); d = L.d
    glass(d, (x0, y0, x0 + 300, y0 + 148), alpha=200)
    comp(img, L)
    stick(img, K.place_sticker('B2', None, (150, 236, 130), (62, 170, 70), shape='socket', w=96, h=84), x0 + 46, y0 + 42, -3, scale=0.42)
    gpaste(img, 'holds', x0 + 98, y0 + 40, 34, S_GAIN)
    for k, oid in enumerate(('KAI', 'VEX')):
        x = x0 + 160 + k * 96
        stick(img, op_c(oid), x, y0 + 46, -4 + 8 * k, scale=0.36)
    L = Layer(); d = L.d
    T(d, (x0 + 16, y0 + 118), 'C2', 24, S_HI)
    d.line([(S(x0 + 52), S(y0 + 118)), (S(x0 + 232), S(y0 + 118)), (S(x0 + 250), S(y0 + 96))], fill=S_HI + (255,), width=S(2.5))
    d.polygon([(S(x0 + 244), S(y0 + 92)), (S(x0 + 258), S(y0 + 88)), (S(x0 + 254), S(y0 + 103))], fill=S_HI + (255,))
    comp(img, L)
    py = Wax(PEN_Y, 40)
    for k in range(2):
        py.tick(x0 + 190 + k * 96, y0 + 84, 13, 6)
    py.ink_ss(img)
    say('KAI', 'VEX', 'B2')


EVAC_TIP = 'Evacuate (give up B2 without a fight, KAI back to HQ)'          # v39's words, kept for the terminal tooltip


def evac_chip(img):
    """EVACUATE as an icon chip: the door-out glyph, the site, KAI going home (mini sticker + arrow to the HQ house)"""
    x0, y0, x1, y1 = 830, 18, 1090, 74
    L = Layer(); d = L.d
    d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=K.GLASS_ + (230,), outline=CYAN + (255,), width=S(2))
    T(d, (x0 + 72, (y0 + y1) / 2 + 1), 'B2', 26, TEXT_HI)
    d.line([(S(x0 + 150), S((y0 + y1) / 2)), (S(x0 + 200), S((y0 + y1) / 2))], fill=TEXT_HI + (255,), width=S(3))
    d.polygon([(S(x0 + 200), S((y0 + y1) / 2 - 7)), (S(x0 + 212), S((y0 + y1) / 2)), (S(x0 + 200), S((y0 + y1) / 2 + 7))], fill=TEXT_HI + (255,))
    comp(img, L)
    gpaste(img, 'evacuate', x0 + 34, (y0 + y1) / 2, 34, S_HARM)
    stick(img, op_c('KAI'), x0 + 128, (y0 + y1) / 2, -4, scale=0.24)
    stick(img, LT.safe_lt(), x0 + 236, (y0 + y1) / 2 - 2, 0, scale=0.3)
    say('B2', 'KAI')
    LT.DOC.append  # (the tooltip text is not on the plate)


# ------------------------------------------------------------------ aftermath: the report stays corp paper (>= 16 px cap)
def report_paper_c():
    PW, PH = R.PW, R.PH
    im = Image.new('RGBA', (S(PW), S(PH)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S(PW), S(PH)], fill=(238, 233, 220, 255))
    rng = np.random.default_rng(4)
    for _ in range(900):
        d.point((rng.uniform(0, S(PW)), rng.uniform(0, S(PH))), fill=(214, 207, 192, 255))

    def Td(xy, s, size, col, font='a'):
        return T(d, xy, s, size, col, font=font, where=LT.DOC)
    Td((48, 62), 'SOLACE', 50, TEAL_D)
    Td((222, 68), 'Field Operations', 23, (40, 96, 100), font='m')
    d.rectangle([S(48), S(102), S(PW - 48), S(105)], fill=TEAL_D + (255,))
    Td((48, 152), 'AFTER-ACTION REPORT', 42, INK)
    Td((48, 198), 'REF SOL-AAR-2611-07 \u00b7 STATIC ALLEY', 23, (90, 84, 76), font='m')
    for k, (lab, val) in enumerate(R.REPORT):
        y = R.RY0 + k * R.RDY
        Td((48, y), lab, 23, (96, 90, 80), font='m')
        if val is None:
            d.rectangle([S(R.RVX), S(y - 13), S(R.RVX + 250), S(y + 13)], fill=(18, 16, 20, 255))
        else:
            Td((R.RVX, y), val, 25, INK, font='m')
        d.line([(S(48), S(y + 24)), (S(PW - 48), S(y + 24))], fill=(214, 206, 190, 255), width=S(1))
    y = R.RY0 + len(R.REPORT) * R.RDY + 70
    Td((48, y), 'FIELD SUPERVISOR', 23, (96, 90, 80), font='m')
    d.line([(S(300), S(y + 10)), (S(580), S(y + 10))], fill=(120, 112, 100, 255), width=S(1.5))
    sig = [(312 + k * 14, y - 4 + 10 * math.sin(k * 1.3) * (1 if k % 3 else -0.6)) for k in range(18)]
    d.line([(S(x), S(yy)) for x, yy in sig], fill=(30, 40, 90, 255), width=S(2), joint='curve')
    Td((48, PH - 40), 'INTERNAL \u00b7 PAGE 1 OF 1', 23, (130, 122, 108), font='m')
    st = Image.new('L', (S(330), S(96)), 0); sd = ImageDraw.Draw(st)
    sd.rectangle([S(4), S(4), S(326), S(92)], outline=255, width=S(5))
    sd.text((S(165), S(50)), 'CLASSIFIED', font=TR.font(ANTON, 58), fill=255, anchor='mm'); LT.DOC.append('CLASSIFIED')
    noise = (np.random.default_rng(8).random((st.height, st.width)) > 0.22).astype(np.uint8) * 255
    st = SL.ImageChops.multiply(st, Image.fromarray(noise)).rotate(9, expand=True, resample=Image.BICUBIC)
    im.paste(Image.new('RGBA', st.size, (30, 120, 124, 220)), (S(PW - 380), S(118)), st)
    return im


def plate_aftermath():
    F = F_all(); img = blank()
    V.draw_grid(img, F, labels=False)
    map_objs(img, placed={}, barricade=True)
    sx, sy = G.cc(*V.SAFE)
    stick(img, LT.safe_lt(), sx, sy - 12, -3, scale=V.STICK['safe'])
    L = Layer(); L.d.rectangle([S(int(520 * V.UI_S)), S(0), S(W - int(520 * V.UI_S)), S(H)], fill=(4, 6, 10, 140)); comp(img, L)
    R.REPORT = [('OPERATION', 'CLEAN SWEEP'), ('TARGET', 'Cell safehouse, grid %s' % G.name(*V.SAFE)), ('DURATION', '4 rounds'),
                ('UNITS COMMITTED', '34'), ('UNITS LOST', '30'), ('UNITS THROUGH', '0'), ('TARGET DAMAGE', 'none'), ('OUTCOME', None),
                ('NEXT ACTION', 'review Heat, resubmit')]
    paper = report_paper_c().rotate(R.PANG, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', paper.size, (4, 3, 6, 0))
    sh.putalpha(paper.split()[3].filter(ImageFilter.GaussianBlur(S(10))).point(lambda v: int(v * 0.6)))
    x, y = int(S(R.PCX) - paper.width / 2), int(S(R.PCY) - paper.height / 2)
    img.alpha_composite(sh, (x + S(10), y + S(16)))
    img.alpha_composite(paper, (x, y))
    P, RVX, RY0, RDY = R.P, R.RVX, R.RY0, R.RDY
    py = Wax(PEN_Y, 13)
    cx, cy = P(RVX + 18, RY0 + 4 * RDY)
    py.circle(cx, cy, 44, 28, width=7, start=-2.4, over=0.5, tilt=-0.03)
    lx, ly = P(560, RY0 + 4 * RDY - 6)
    py.text('30/34', lx, ly, 60, angle=R.PANG - 6); say('30/34')
    for k, dx in ((5, 40), (6, 104)):
        tx, ty = P(RVX + dx, RY0 + k * RDY)
        py.tick(tx, ty, 13, 6)
    hx, hy = P(600, RY0 + 6 * RDY)                       # "HQ untouched" -> a pencil heart with a tick
    hp = [(hx + 18 * 16 * math.sin(t) ** 3 / 17 / 1.0 * 0.06 * 17, hy - 18 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17)
          for t in np.linspace(0, 2 * math.pi, 40)]
    hp = [(hx + 20 * math.sin(t) ** 3, hy - 20 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in np.linspace(0, 2 * math.pi, 40)]
    py.stroke(py.wobble(hp, 0.4), 6, taper=False)
    py.tick(hx + 44, hy, 15, 7)
    py.ink_ss(img)
    hx, hy = P(500, RY0 + 8 * RDY + 70)
    stick(img, K.verb_sticker('HELD', (255, 238, 96), (255, 182, 14), size=110), hx, hy, R.PANG - 7, scale=1.0); say('HELD')
    left_c(img, 8, 0, rnd=4, rmax=4, credits=12, undo=False, kills={'KAI': 11, 'VEX': 9, 'MOTH': 4, 'RUNE': 6})
    # the result panel: icons + numbers
    x0, y0, x1, y1 = LT.RX0, 14, LT.RX1, 300
    L = Layer(); d = L.d
    glass(d, (x0, y0, x1, y1))
    ico_c(d, 'shield', x0 + 34, y0 + 42, 22, S_GAIN)
    for k in range(4):
        x, y = x0 + 72 + k * 34, y0 + 42
        d.polygon([(S(x), S(y - 12)), (S(x + 12), S(y)), (S(x), S(y + 12)), (S(x - 12), S(y))], fill=S_GAIN + (255,), outline=INK + (255,), width=S(2))
    rows = [(('skull', S_HI), '30/34'), (('drop', S_GAIN), '0'), (('heart', RED_H), '8/8'), (('flame', (255, 120, 60)), '25 \u2192 24')]
    for k, ((ic, col), s_) in enumerate(rows):
        x = x0 + 34 + (k % 2) * 186
        y = y0 + 118 + (k // 2) * 76
        ico_c(d, ic, x, y, 20, col)
        T(d, (x + 32, y + 2), s_, 36, S_GAIN if ic in ('drop', 'heart', 'flame') else S_HI)
    comp(img, L)
    stick(img, K.verb_sticker('CONTINUE'), 1765, 708, 4, scale=0.9 * V.UI_S); say('CONTINUE')
    L = Layer(); d = L.d; LT.keycap(d, 1695, 760, 140)
    d.line([(S(1731), S(770)), (S(1731), S(782)), (S(1799), S(782)), (S(1799), S(770))], fill=TEXT_HI + (255,), width=S(3))
    comp(img, L)
    return img


# ------------------------------------------------------------------ main + sheet
PLATES = dict(plan=plate_plan, place=plate_place, shop=plate_shop, playback=plate_playback, site=plate_site, aftermath=plate_aftermath)
CAPS = dict(plan='at rest: A down avenue b, B in along street 6, wall on b4, B leaks 2',
            place='RUNE held, Tab held: the order unfolds; reach hatched, +3 / +2 / +1',
            shop='SHOTGUN peeled onto RUNE: star + star -> two stars, credits 7 -> 4',
            playback='tick 3/8: kills, leaks, held at the wall, still to enter',
            site='B2 crossing: who defends (card), EVACUATE chip, core 8',
            aftermath="Solace after-action report (corp paper), the result in icons")


def sheet(counts):
    names = list(PLATES)
    tw_, th_ = 700, 394
    pad, cap = 12, 76
    cols = 3
    sh = Image.new('RGB', (cols * tw_ + (cols + 1) * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 15); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 10), 'RAID in DEFACE v3: set 7, direction C (pictograms + one folded corp order), bible-grammar icons', font=fb, fill=TEXT_HI)
    for k, n in enumerate(names):
        im = Image.open(OUT + 'r3_%s.png' % n).resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % cols) * (tw_ + pad); y = 54 + pad + (k // cols) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        c = counts.get(n, {})
        d.text((x + 4, y + th_ + 4), '%s   r3_%s.png' % (n, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 34), CAPS[n], font=f, fill=TEXT_MID)
        d.text((x + 4, y + th_ + 54), 'words on screen %s, corp document words %s' % (c.get('words', '?'), c.get('doc_words', '?')), font=f, fill=TEXT_MID)
    sh.save(OUT + 'r3_sheet.jpg', quality=90)
    print('ok', OUT + 'r3_sheet.jpg', flush=True)


if __name__ == '__main__':
    CJ = 'D:/rc_scratch/raid_v3/insp/c_counts.json'
    counts = json.load(open(CJ, encoding='utf-8')) if os.path.exists(CJ) else {}
    todo = [a for a in sys.argv[1:] if not a.startswith('--')] or list(PLATES) + ['sheet']
    for n in todo:
        if n == 'sheet':
            sheet(counts); continue
        LT.SHOWN.clear(); LT.DOC.clear(); LT.SMALL.clear()
        ov = PLATES[n]()
        V.finish(ov, dim=0.8 if n == 'aftermath' else 1.0).save(OUT + 'r3_%s.png' % n)
        c = LT.classify(LT.SHOWN); c['doc_words'] = LT.classify(LT.DOC)['words']; c['small'] = list(LT.SMALL); c['shown'] = list(LT.SHOWN)
        counts[n] = c
        print('ok', n, {k: v for k, v in c.items() if k != 'shown'}, flush=True)
    json.dump(counts, open(CJ, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
