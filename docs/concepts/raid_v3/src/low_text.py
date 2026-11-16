"""low_text: three low-text directions for the raid screen (designer ask after set 6), each as a plan + a place plate, a sheet,
and a word count per plate.

    python low_text.py                 -> raid_v3/low_text/lt_{A,B,C}_{plan,place}.png, lt_sheet.jpg, lt_counts.json

  A  Pictogram   every non-document panel is pictures + numbers: a wave strip under a stamped corp header (INCOMING), wordless
                 CREW stickers (callsign + glyph + level pips), icon rows, an icon forecast strip, a price-dot shop.
  B  Diegetic    no HUD panels: stickers, the Cell's pencil on the map and the glass, and one corp document (the intercepted
                 work order, full text) on the right.
  C  Medium      A's pictograms for everything live and numeric, the work order kept as a document but folded to a corner
                 (seal + ROUND 1 · 8) at rest and unfolded on the place plate; one short icon forecast strip.

Built on raid_v3_city (set 6 map, routes, beacons, units, pencil) and raid_kit (vinyl, glass, pencil); nothing there changes.
Text that stays on screen is drawn at >= 16 px cap height (Anton >= 19 px, Share Tech Mono >= 23 px on screen).  Every string
drawn is registered with say() (or doc() for the corp document) so the word counts come from the plates themselves.
"""
import json, math, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import raid_v3_city as V
import raid_kit as K
from raid_kit import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, HARM, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                      W, H, SS, F_all, glass, stick, S_GAIN, S_HARM, S_HI, S_MID, S_SCHED, TEAL, TEAL_D, TEAL_HI)

OUTD = V.OUT + 'low_text/'
G = V.G
CAP_A, CAP_M = 0.86, 0.70                 # cap height / font size (measured, lt_measure.py)
GOLD = (255, 210, 40)
PINK_T, PINK_B = (255, 110, 196), (222, 24, 136)
DIM = (120, 132, 146)

# ------------------------------------------------------------------ the text registry (word counts come from what is drawn)
SHOWN, DOC, SMALL = [], [], []


def say(*ss):
    SHOWN.extend(s for s in ss if s)


def doc(*ss):
    DOC.extend(s for s in ss if s)


def classify(strings):
    """words = tokens with 2+ letters (callsigns, item names included); labels = 1-letter tokens and cell / key / level codes;
    numbers = digit runs"""
    w = l = n = 0
    for s in strings:
        for t in re.findall(r'[A-Za-z0-9]+', s):
            a = sum(ch.isalpha() for ch in t)
            if a >= 2:
                w += 1
            elif a == 1:
                l += 1
            else:
                n += 1
    return dict(words=w, labels=l, numbers=n)


def T(d, xy, s, size, col, font='a', anchor='lm', register=True, where=None):
    """screen text with the cap-height check (logs anything under 16 px cap)"""
    f = TR.font(ANTON if font == 'a' else MONO, size)
    cap = size * (CAP_A if font == 'a' else CAP_M)
    if cap < 15.95:
        SMALL.append((s, round(cap, 1)))
    text(d, xy, s, f, col if len(col) == 4 else col + (255,), anchor=anchor)
    if register:
        (where if where is not None else SHOWN).append(s)
    return d.textlength(s, font=f) / SS


# ------------------------------------------------------------------ pictograms (SS draw, screen coords)
def _P(x, y, r, pts):
    return [(S(x + px * r), S(y + py * r)) for px, py in pts]


def ico(d, kind, x, y, r, col=TEXT_HI, shadow=True, alpha=255):
    a = alpha
    fill, ink = col + (a,), INK + (a,)
    ow = S(max(1.6, r * 0.13))

    def poly(pts, f=fill):
        if shadow:
            d.polygon([(px + S(1.5), py + S(2)) for px, py in pts], fill=ink)
        d.polygon(pts, fill=f, outline=ink, width=ow)

    if kind == 'shield':
        poly(_P(x, y, r, [(-.82, -.92), (.82, -.92), (.82, -.05), (0, 1.0), (-.82, -.05)]))
        d.line(_P(x, y, r, [(0, -.7), (0, .7)]), fill=(255, 255, 255, int(a * .5)), width=S(r * .12))
    elif kind == 'drop':
        pts = [(0, -1.05)] + [(.64 * math.cos(math.radians(t)), .34 + .64 * math.sin(math.radians(t))) for t in range(-30, 211, 12)]
        poly(_P(x, y, r, pts))
        d.ellipse([S(x - r * .3), S(y + r * .05), S(x - r * .08), S(y + r * .35)], fill=(255, 255, 255, int(a * .55)))
    elif kind == 'heart':
        pts = []
        for k in range(48):
            t = k / 48 * 2 * math.pi
            pts.append((16 * math.sin(t) ** 3 / 17, (-(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) / 17 + .08))
        poly(_P(x, y, r, pts))
    elif kind == 'skull':
        if shadow:
            d.ellipse([S(x - r * .82 + 1.5), S(y - r * .98 + 2), S(x + r * .82 + 1.5), S(y + r * .5 + 2)], fill=ink)
        d.rounded_rectangle([S(x - r * .46), S(y + r * .1), S(x + r * .46), S(y + r * .95)], radius=S(r * .12), fill=fill, outline=ink, width=ow)
        d.ellipse([S(x - r * .82), S(y - r * .98), S(x + r * .82), S(y + r * .5)], fill=fill, outline=ink, width=ow)
        d.rectangle([S(x - r * .40), S(y + r * .2), S(x + r * .40), S(y + r * .5)], fill=fill)
        for sx in (-1, 1):
            d.ellipse([S(x + sx * .34 * r - r * .21), S(y - r * .32), S(x + sx * .34 * r + r * .21), S(y + r * .08)], fill=ink)
        for tx in (-.2, 0, .2):
            d.line([(S(x + tx * r), S(y + r * .58)), (S(x + tx * r), S(y + r * .92))], fill=ink, width=S(max(1.2, r * .07)))
    elif kind == 'flame':
        poly(_P(x, y, r, [(.05, -1.0), (.42, -.42), (.72, -.05), (.72, .42), (.42, .86), (0, 1.0), (-.46, .86), (-.74, .38), (-.6, -.15),
                          (-.3, .12), (-.3, -.42)]))
        poly(_P(x, y + r * .3, r * .5, [(0, -.9), (.5, .1), (.35, .8), (0, 1.0), (-.35, .8), (-.5, .1)]), f=(255, 236, 140, a))
    elif kind == 'eye':
        pts = [(math.cos(t) * 1.0, math.sin(t) * .55 * (1 if math.sin(t) > 0 else 1)) for t in np.linspace(0, 2 * math.pi, 40)]
        pts = [(px, py * (1 - abs(px) ** 2 * .45)) for px, py in pts]
        poly(_P(x, y, r, pts), f=(240, 236, 226, a))
        d.ellipse([S(x - r * .36), S(y - r * .36), S(x + r * .36), S(y + r * .36)], fill=col + (a,), outline=ink, width=ow)
        d.ellipse([S(x - r * .13), S(y - r * .13), S(x + r * .13), S(y + r * .13)], fill=ink)
    elif kind in ('undo', 'reroll'):
        R_ = r * .72
        arcs = [(200, 470)] if kind == 'undo' else [(30, 160), (210, 340)]
        for a0, a1 in arcs:
            for wdt, c_ in ((r * .42, ink), (r * .24, fill)):
                d.arc([S(x - R_), S(y - R_), S(x + R_), S(y + R_)], a0, a1, fill=c_, width=S(wdt))
            t = math.radians(a1 if kind == 'reroll' else a0)
            hx, hy = x + R_ * math.cos(t), y + R_ * math.sin(t)
            dx, dy = (-math.sin(t), math.cos(t)) if kind == 'reroll' else (math.sin(t), -math.cos(t))
            nx, ny = math.cos(t), math.sin(t)
            hp = [(hx + dx * r * .5, hy + dy * r * .5), (hx + nx * r * .38 - dx * r * .08, hy + ny * r * .38 - dy * r * .08),
                  (hx - nx * r * .38 - dx * r * .08, hy - ny * r * .38 - dy * r * .08)]
            d.polygon([(S(px), S(py)) for px, py in hp], fill=fill, outline=ink, width=S(1.4))
    elif kind == 'place':                                   # a cell with the drop arrow: "if placed here"
        q = [(0, .25), (.95, .62), (0, 1.0), (-.95, .62)]
        d.polygon(_P(x, y, r, q), fill=(90, 214, 240, int(a * .25)), outline=(90, 214, 240, a), width=S(2.2))
        poly(_P(x, y, r, [(-.22, -1.0), (.22, -1.0), (.22, -.25), (.5, -.25), (0, .4), (-.5, -.25), (-.22, -.25)]), f=GOLD + (a,))
    elif kind == 'tick':
        for wdt, c_ in ((r * .5, ink), (r * .3, fill)):
            d.line(_P(x, y, r, [(-.8, 0), (-.25, .6), (.85, -.7)]), fill=c_, width=S(wdt), joint='curve')


def path_chip(d, x, y, letter, r=15, col=(200, 30, 40)):
    """the route letter as on the map's entry marks: a red ring with the letter"""
    d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(250, 240, 236, 255), outline=col + (255,), width=S(3))
    text(d, (x, y + 1), letter, TR.font(ANTON, 22), col + (255,))
    SHOWN.append(letter)


def keycap(d, x, y, w, label=None, h=34):
    d.rounded_rectangle([S(x + 1), S(y + 3), S(x + w + 1), S(y + h + 3)], radius=S(6), fill=INK + (255,))
    d.rounded_rectangle([S(x), S(y), S(x + w), S(y + h)], radius=S(6), fill=(30, 40, 52, 255), outline=CYAN + (200,), width=S(1.6))
    if label:
        T(d, (x + w / 2, y + h / 2 + 1), label, 22, TEXT_HI, anchor='mm')


# ------------------------------------------------------------------ wordless stickers
_C = {}


def big_dot(d, x, y, n):
    d.ellipse([x - S(23), y - S(23), x + S(23), y + S(23)], fill=GOLD + (255,), outline=INK + (255,), width=S(3.5))
    d.text((x, y + S(1)), str(n), font=ImageFont.truetype(ANTON, S(32)), fill=INK + (255,), anchor='mm')


def op_lt(oid, curl=None):
    """the operative sticker without its role and level words: glyph, callsign, level as pips"""
    key = ('op', oid, curl)
    if key in _C:
        return _C[key]
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

    sd = K.vinyl(body, o['col'][0], o['col'][1], deco, border=8, curl=curl)
    _C[key] = sd
    return sd


def _wpn_icon(d, name, x, y, s):
    """weapon pictogram in paper with an ink edge, centred at (x, y) SS, s = half size SS"""
    P, I = PAPER + (255,), INK + (255,)
    if name == 'SMG':                                       # a three-round burst
        for k in range(3):
            cx = x + (k - 1) * s * .62
            d.rounded_rectangle([cx - s * .2, y - s * .5, cx + s * .2, y + s * .5], radius=s * .2, fill=P, outline=I, width=S(2))
            d.rectangle([cx - s * .2, y + s * .12, cx + s * .2, y + s * .22], fill=I)
    elif name == 'RAIL':                                    # a beam through rings
        d.line([(x - s * 1.1, y), (x + s * 1.1, y)], fill=I, width=int(s * .36))
        d.line([(x - s * 1.1, y), (x + s * 1.1, y)], fill=P, width=int(s * .16))
        for k in (-.6, 0, .6):
            d.ellipse([x + k * s - s * .16, y - s * .52, x + k * s + s * .16, y + s * .52], outline=I, width=S(4))
            d.ellipse([x + k * s - s * .16, y - s * .52, x + k * s + s * .16, y + s * .52], outline=P, width=S(2))
    elif name == 'SHOTGUN':                                 # a spread of pellets
        for a in (-26, 0, 26):
            t = math.radians(a)
            x1, y1 = x - s * .9 + s * 1.7 * math.cos(t), y + s * 1.7 * math.sin(t) * .8
            d.line([(x - s * .9, y), (x1, y1)], fill=I, width=S(5))
            d.line([(x - s * .9, y), (x1, y1)], fill=P, width=S(2.4))
            d.ellipse([x1 - s * .2, y1 - s * .2, x1 + s * .2, y1 + s * .2], fill=P, outline=I, width=S(2))
    else:                                                   # JAMMER: waves
        d.ellipse([x - s * .9 - s * .2, y - s * .2, x - s * .9 + s * .2, y + s * .2], fill=P, outline=I, width=S(2))
        for k, rr in enumerate((.6, 1.0, 1.4)):
            bb = [x - s * .9 - rr * s, y - rr * s, x - s * .9 + rr * s, y + rr * s]
            d.arc(bb, -40, 40, fill=I, width=S(5))
            d.arc(bb, -40, 40, fill=P, width=S(2.4))


def wpn_lt(name, stars, cost=None, curl=None, grey=False):
    key = ('w', name, stars, cost, curl, grey)
    if key in _C:
        return _C[key]
    lead = 44 if cost is not None else 0
    w, h, pad = int(lead + 16 + 78 + 10 + stars * 22 + 14), 60, 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    ImageDraw.Draw(body).polygon([(S(pad + 10), S(pad)), (S(pad + w), S(pad)), (S(pad + w - 10), S(pad + h)), (S(pad), S(pad + h))], fill=255)

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        _wpn_icon(d, name, ox + S(lead + 16 + 39), oy + S(h / 2), S(28))
        x = ox + S(lead + 16 + 78 + 12)
        for k in range(stars):
            d.polygon([(S(px) + x, S(py) + oy) for px, py in K.star_poly(k * 22, h / 2, 10)], fill=GOLD + (255,), outline=INK + (255,))
        if cost is not None:
            big_dot(d, ox + S(22), oy + S(h / 2), cost)

    sd = K.vinyl(body, (58, 52, 70), (22, 19, 28), deco, border=6, curl=curl, grey=grey, ext=4)
    _C[key] = sd
    return sd


def dev_lt(kind, cost=None, curl=None):
    """devices without their words: the barricade is its hazard stripes, the mine a fused star, the sentry an eye on a barrel"""
    key = ('d', kind, cost, curl)
    if key in _C:
        return _C[key]
    w, h = K.DEVSZ[kind]
    pad = 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    body.paste(K._dev_body(kind, w, h), (S(pad), S(pad)))

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        if kind == 'BARRICADE':
            st = Image.new('L', art.size, 0); sd_ = ImageDraw.Draw(st)
            for k in range(-4, 14):
                x = ox + S(k * 22)
                sd_.polygon([(x, oy), (x + S(11), oy), (x + S(11) - S(h * 0.62), oy + S(h * 0.62)), (x - S(h * 0.62), oy + S(h * 0.62))], fill=255)
            st = SL.ImageChops.multiply(st, body.point(lambda v: 255 if v > 128 else 0))
            art.paste(Image.new('RGBA', art.size, INK + (255,)), (0, 0), st)
        elif kind == 'MINE':
            cx, cy = ox + S(w / 2), oy + S(h / 2)
            d.ellipse([cx - S(14), cy - S(14), cx + S(14), cy + S(14)], fill=INK + (255,))
            d.ellipse([cx - S(6), cy - S(6), cx + S(6), cy + S(6)], fill=(255, 90, 60, 255))
        elif kind == 'SENTRY':
            cx, cy = ox + S(w * 0.42), oy + S(h / 2)
            d.ellipse([cx - S(20), cy - S(20), cx + S(20), cy + S(20)], fill=INK + (255,))
            d.ellipse([cx - S(11), cy - S(11), cx + S(11), cy + S(11)], fill=(150, 230, 255, 255))
            d.ellipse([cx - S(4), cy - S(4), cx + S(4), cy + S(4)], fill=INK + (255,))
        if cost is not None:
            big_dot(d, ox + S(8), oy + S(6), cost)

    top, bot = K.DEV[kind]
    sd = K.vinyl(body, top, bot, deco, border=6, curl=curl, ext=4)
    _C[key] = sd
    return sd


def safe_lt():
    """the Safehouse as a house with the core's heart (no words)"""
    key = ('safe',)
    if key in _C:
        return _C[key]
    w, h, pad = 118, 104, 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    ImageDraw.Draw(body).polygon([(S(pad + x * w), S(pad + y * h)) for x, y in [(0.5, 0), (1, 0.36), (1, 1), (0, 1), (0, 0.36)]], fill=255)

    def deco(d, art):
        ico(d, 'heart', pad + w / 2, pad + h * 0.62, 30, (255, 236, 244))

    sd = K.vinyl(body, PINK_T, PINK_B, deco, border=7, ext=5)
    _C[key] = sd
    return sd


# ------------------------------------------------------------------ the map (shared by all three)
def map_base(img, F, words, place=False, pencil='icons', seed=0):
    occ = set(V.PLACED.values()) | {V.BARR, V.SAFE}
    V.draw_grid(img, F, legal=V.legal_cells(V.RA + V.RB, occ) if place else (), labels=False)
    V.routes_ground(img)
    for oid, (c, r) in sorted(V.PLACED.items(), key=lambda kv: G.cc(*kv[1])[1]):
        V.beacon(img, oid, c, r)
    bx, by = G.cc(*V.BARR)
    if words:
        stick(img, K.dev_sticker('BARRICADE'), bx, by - 6, -33, scale=V.STICK['barricade']); say('BARRICADE')
    else:
        stick(img, dev_lt('BARRICADE'), bx, by - 6, -33, scale=V.STICK['barricade'])
    py, pr = Wax(PEN_Y, 11 + seed), Wax(PEN_R, 12 + seed)
    ps = Wax(PEN_Y, 13 + seed)
    V.routes(pr); say('A', 'B')
    V.wall_hp(py, 6, 3); say('6 → 3')
    lx, ly = V.leak_at()
    sx, sy = G.cc(*V.SAFE)
    strike = None
    if not place:
        if pencil == 'words':
            pr.text('2 leak', lx, ly, 32, angle=-6); say('2 leak')
        else:
            pen_drop(pr, lx - 26, ly - 2, 17); pr.text('2', lx + 12, ly, 38, angle=-6); say('2')
        pr.arrow([(lx + 12, ly - 22), (lx + 22, ly - 40), (sx - 8, sy + 46)], width=6, head=14)
        K.pen_arrow_num(pr, 8, 6, sx - 150, sy + 10, 30); say('8 → 6')
        if pencil == 'words':                                # B: the kill forecast also lives in pencil, under the core note
            kx, ky = sx - 196, sy + 70
            py.x(kx, ky, 12, 6); py.text('6/8', kx + 50, ky + 2, 34, angle=-6); say('6/8')
    else:
        hc, hr = V.HOVER
        c0, c1, r0, r1 = max(hc - 1, 0), min(hc + 2, G.nc), max(hr - 1, 0), min(hr + 2, G.nr)
        V.pen_hatch_quad(py, [G.sp(c0, r0), G.sp(c1, r0), G.sp(c1, r1), G.sp(c0, r1)])
        hx, hy = G.cc(*V.HOVER)
        py.circle(hx, hy, 54, 34, width=6, start=-2.2, over=0.5, tilt=0)
        for (c, r), s_ in V.BEST:
            x, y = G.cc(c, r)
            if (c, r) == V.HOVER:
                py.text(s_, x - 6, y - 62, 40, angle=-6)
            else:
                py.text(s_, x, y + 2, 30, angle=-6)
            say(s_)
        if pencil == 'words':
            pr.text('2 leak', lx, ly, 32, angle=-6); say('2 leak')
            py.text('safe', sx - 140, sy + 10, 32, angle=-6); say('safe')
            kx, ky = sx - 196, sy + 70
            py.x(kx, ky, 12, 6); py.text('8/8', kx + 50, ky + 2, 34, angle=-6); say('8/8')
        else:
            pen_drop(pr, lx - 26, ly - 2, 17); pr.text('2', lx + 12, ly, 38, angle=-6); say('2')
            py.tick(sx - 128, sy + 14, 18, 7)
        py.text('0', lx + 4, ly + 42, 40, angle=-6); say('0')
        strike = (lx, ly)
        hold = (hx + 175, hy + 150)
        py.arrow([(hold[0] - 58, hold[1] - 46), (hold[0] - 96, hold[1] - 92), (hx + 62, hy + 12), (hx + 40, hy + 2)], width=6, head=16)
    py.ink_ss(img); pr.ink_ss(img)
    if strike:
        lx, ly = strike
        ps.stroke(ps.wobble([(lx - 50, ly + 8), (lx + 50, ly - 8)], 0.6), 6, taper=False)
        ps.ink_ss(img)
    x, y = G.cc(*V.SAFE)
    if words:
        stick(img, K.place_sticker('SAFE', 'HOUSE', PINK_T, PINK_B), x, y - 12, -3, scale=V.STICK['safe']); say('SAFE', 'HOUSE')
    else:
        stick(img, safe_lt(), x, y - 12, -3, scale=V.STICK['safe'])
    V.units_at_rest(img); say('5', '3')


def pen_drop(p, x, y, r):
    pts = [(x, y - r * 1.1)] + [(x + .66 * r * math.cos(math.radians(t)), y + .3 * r + .66 * r * math.sin(math.radians(t))) for t in range(-30, 211, 15)]
    p.stroke(p.wobble(pts + [pts[0]], 0.5), 5, taper=False)


def held(img, words, hx, hy):
    hold = (hx + 175, hy + 150)
    hs = 0.86 * V.UI_S
    L = Layer(); d = L.d
    for k, (ox, oy) in enumerate(((60, 66), (76, 44), (42, 82))):
        d.line([(S(hold[0] + ox), S(hold[1] + oy)), (S(hold[0] + ox + 34), S(hold[1] + oy + 42))], fill=(235, 230, 255, 80 - k * 18), width=S(3))
    comp(img, L)
    if words:
        stick(img, K.op_sticker('RUNE', curl=0.30), hold[0], hold[1], 9, scale=hs, lift=1.0)
        stick(img, K.wpn_sticker('SHOTGUN', 1), hold[0] + 72 * hs - 8, hold[1] - 66 * hs - 10, 16, scale=0.72 * V.UI_S, lift=1.0)
        say('RUNE', 'BRUISER', 'L1', 'SHOTGUN')
    else:
        stick(img, op_lt('RUNE', curl=0.30), hold[0], hold[1], 9, scale=hs, lift=1.0)
        stick(img, wpn_lt('SHOTGUN', 1), hold[0] + 72 * hs - 8, hold[1] - 66 * hs - 10, 16, scale=0.72 * V.UI_S, lift=1.0)
        say('RUNE')
    V.cursor(img, hx + 10, hy + 8)


# ------------------------------------------------------------------ left column pieces (screen coords)
def core_lt(img, core=8, lose=0):
    """the core tape without words: the heart, eight cells, the number (forecast loss hatched red)"""
    L = Layer(); d = L.d
    x0, x1, y0, h = 16, 392, 12, 64
    tape = [(S(x0 + 4), S(y0)), (S(x1 - 4), S(y0 + 3)), (S(x1 - 7), S(y0 + h)), (S(x0), S(y0 + h - 3))]
    IR.poly_shadow(d, tape, 4, 5)
    d.polygon(tape, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
    ico(d, 'heart', x0 + 34, y0 + h / 2, 21, (236, 40, 90))
    cmax = 8
    px0, px1 = x0 + 66, x1 - (112 if lose else 70)
    pw = (px1 - px0 - 5 * (cmax - 1)) / cmax
    for k in range(cmax):
        x = px0 + k * (pw + 5); box = [S(x), S(y0 + 18), S(x + pw), S(y0 + h - 18)]
        if k < core - lose:
            d.rectangle(box, fill=IR.GAIN + (255,), outline=INK + (255,), width=S(2))
        else:
            d.rectangle(box, fill=PAPER + (255,))
            for t in range(-1, 5):
                d.line([(S(x + t * 7), S(y0 + h - 18)), (S(x + t * 7 + 10), S(y0 + 18))], fill=HARM + (255,), width=S(2.2))
            d.rectangle(box, outline=INK + (255,), width=S(2))
    s_ = '%d' % core if not lose else '%d \u2192 %d' % (core, core - lose)
    T(d, (x1 - 16, y0 + h / 2 + 1), s_, 30, INK if not lose else (200, 24, 30), anchor='rm')
    comp(img, L)


def rows_lt(img, rnd=1, rmax=4, credits=7, cost=0):
    """round pips + the credit coin, no labels"""
    L = Layer(); d = L.d
    glass(d, (16, 86, 196, 132))
    for k in range(rmax):
        x, y = 40 + k * 38, 109
        r = 11 if k + 1 == rnd else 8
        on = k + 1 <= rnd
        q = [(S(x), S(y - r)), (S(x + r), S(y)), (S(x), S(y + r)), (S(x - r), S(y))]
        d.polygon(q, fill=(CYAN if k + 1 == rnd else (40, 70, 84)) + (255,) if on else (12, 18, 24, 255), outline=(CYAN if on else (70, 110, 126)) + (255,), width=S(2))
    glass(d, (208, 86, 392, 132))
    IR.ram_coin(d, 236, 109, None, None, r=14)
    s_ = str(credits) if not cost else '%d \u2192 %d' % (credits, credits - cost)
    T(d, (262, 110), s_, 30, TEXT_HI if not cost else (255, 120, 110))
    comp(img, L)


def crew_lt(img, held_=None, words=False):
    """CREW (full roster, option B): stickers in full colour, a placed one gets the pencil tick only (the beacon shows where)"""
    def fn(Lm):
        py = Wax(PEN_Y, 91)
        for oid, (x, y, ang) in K.CREW_POS.items():
            o = K.OPS[oid]
            sd = K.op_sticker(oid) if words else op_lt(oid)
            if oid == held_:
                K.liner(Lm, sd, x, y, ang)
                continue
            stick(Lm, sd, x, y, ang)
            if words:
                stick(Lm, K.wpn_sticker(o['wpn'], o['stars']), x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2], scale=0.82)
                say(oid, o['role'], 'L%d' % o['lvl'], o['wpn'])
            else:
                stick(Lm, wpn_lt(o['wpn'], o['stars']), x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2], scale=0.82)
                say(oid)
            if oid in V.PLACED:
                py.tick(x + 4, y + 106, 17, 7)
        py.ink_ss(Lm)
    V.ui(img, fn, (0, 0))


def undo_lt(img):
    L = Layer(); d = L.d
    glass(d, (16, 690, 132, 738))
    ico(d, 'undo', 46, 714, 17, TEXT_HI, shadow=False)
    keycap(d, 76, 697, 40, 'Z')
    comp(img, L)


# ------------------------------------------------------------------ right column pieces
RX0, RX1 = 1520, 1904


def wave_strip(img, rounds, now=0, heat=25, y0=12):
    """A's INCOMING: a stamped Solace header strip (corp paper) over the waves, one row per round: the round number, then each
    group as its v4 icon with its count; the round that is now lit, later ones dimmed; the A / B route letter where v39 gives it"""
    rowh, hh = 66, 52
    y1 = y0 + hh + len(rounds) * rowh + 12
    L = Layer(); d = L.d
    glass(d, (RX0, y0, RX1, y1), alpha=215)
    # the header: a strip of corp paper, wordmark + the intercept stamp (an eye in a red ring); Heat on the glass beside it
    pts = [(RX0 + 10, y0 + 8), (RX0 + 262, y0 + 6), (RX0 + 264, y0 + hh - 4), (RX0 + 8, y0 + hh - 2)]
    d.polygon([(S(x + 3), S(y + 4)) for x, y in pts], fill=(2, 2, 4, 160))
    d.polygon([(S(x), S(y)) for x, y in pts], fill=(236, 230, 214, 255))
    T(d, (RX0 + 22, y0 + hh / 2 + 1), 'SOLACE', 30, TEAL_D, where=SHOWN)
    d.rectangle([S(RX0 + 22), S(y0 + hh - 13), S(RX0 + 150), S(y0 + hh - 11)], fill=TEAL_D + (255,))
    sx, sy = RX0 + 214, y0 + hh / 2 + 1
    d.ellipse([S(sx - 22), S(sy - 20), S(sx + 22), S(sy + 20)], outline=(196, 30, 40, 230), width=S(3.2))
    ico(d, 'eye', sx, sy, 15, (196, 30, 40), shadow=False)
    ico(d, 'flame', RX1 - 74, y0 + hh / 2, 15, (255, 120, 60))
    T(d, (RX1 - 54, y0 + hh / 2 + 1), str(heat), 30, TEXT_HI)
    comp(img, L)
    y = y0 + hh + 6
    for k, (head, groups) in enumerate(rounds):
        L = Layer(); d = L.d
        lit = k == now
        a = 255 if lit else (150, 120, 105)[min(2, k - now - 1)]
        if lit:
            d.rectangle([S(RX0 + 8), S(y), S(RX1 - 8), S(y + rowh - 8)], fill=(30, 52, 64, 230), outline=S_SCHED + (255,), width=S(3))
        else:
            d.line([(S(RX0 + 14), S(y + rowh - 4)), (S(RX1 - 14), S(y + rowh - 4))], fill=(60, 90, 104, 200), width=S(1))
        cy = y + (rowh - 8) / 2
        d.ellipse([S(RX0 + 20), S(cy - 17), S(RX0 + 54), S(cy + 17)], fill=((236, 230, 214) if lit else (70, 80, 92)) + (255,), outline=INK + (255,), width=S(2))
        T(d, (RX0 + 37, cy + 1), str(k + 1), 24, INK if lit else (200, 206, 214), anchor='mm')
        comp(img, L)
        gx = RX0 + 72
        for path, kind, label, n in groups:
            L = Layer(); d = L.d
            if path:
                path_chip(d, gx + 10, cy, path, r=13)
                gx += 30
            comp(img, L)
            ic = V.icon_img(kind, 1.0, 12, ring=False)
            if not lit:
                ic = ic.copy(); ic.putalpha(ic.split()[3].point(lambda v: int(v * a / 255)))
            img.alpha_composite(ic, (int(S(gx + 14) - ic.width / 2), int(S(cy) - ic.height / 2)))
            L = Layer(); d = L.d
            wtx = T(d, (gx + 32, cy + 2), '\u00d7%d' % n, 24, (TEXT_HI if lit else (170, 180, 190)) + (a,))
            comp(img, L)
            gx += 32 + wtx + 18
        y += rowh
    return y1


def shop_lt(img, y0, words=False, peeled=None, header=False):
    """the sticker sheet: price dots only (A, C); B keeps the worded stickers and a printed BLACK MARKET header"""
    x0, x1, y1 = RX0 + 2, RX1 - 2, y0 + 196
    L = Layer(); d = L.d
    pts = [(x0 + 4, y0), (x1, y0 + 5), (x1 - 3, y1), (x0, y1 - 4)]
    d.polygon([(S(x + 5), S(y + 7)) for x, y in pts], fill=(4, 3, 6, 200))
    d.polygon([(S(x), S(y)) for x, y in pts], fill=(232, 228, 218, 255), outline=(150, 144, 132, 255))
    top = y0 + 12
    if header:
        T(d, (x0 + 16, y0 + 24), 'BLACK MARKET', 24, INK)
        top = y0 + 40
        for xx in range(int(x0 + 10), int(x1 - 10), 14):
            d.line([(S(xx), S(top)), (S(xx + 7), S(top))], fill=(170, 164, 152, 255), width=S(1.5))
    rng = np.random.default_rng(2)
    for _ in range(200):
        d.point((S(rng.uniform(x0 + 6, x1 - 6)), S(rng.uniform(y0 + 6, y1 - 6))), fill=(200, 194, 182, 255))
    comp(img, L)
    sc = 0.62
    ya, yb = top + (y1 - top) * 0.27, top + (y1 - top) * 0.72
    offers = [('w', 'SHOTGUN', 1, 3, (x0 + 104, ya)), ('w', 'RAIL', 1, 4, (x0 + 280, ya)),
              ('d', 'BARRICADE', None, 3, (x0 + 78, yb)), ('d', 'MINE', None, 2, (x0 + 200, yb)), ('d', 'SENTRY', None, 4, (x0 + 300, yb))]
    for k_, nm, st, cost, (x, y) in offers:
        if words:
            sd = K.wpn_sticker(nm, st, cost=cost) if k_ == 'w' else K.dev_sticker(nm, cost=cost)
            say(nm, str(cost))
        else:
            sd = wpn_lt(nm, st, cost=cost) if k_ == 'w' else dev_lt(nm, cost=cost)
            say(str(cost))
        if peeled == nm:
            continue
        K.paste_flat(img, sd, x, y, 0, sc)
    if words:
        for nm in ('SHOTGUN', 'RAIL', 'BARRICADE', 'MINE', 'SENTRY'):
            SMALL.append((nm + ' sticker name', round(22 * sc * CAP_A, 1) if nm in ('BARRICADE', 'MINE', 'SENTRY') else round(28 * sc * CAP_A, 1)))
        SMALL.append(('shop cost dots', round(24 * sc * CAP_A, 1)))
    return y1


def reroll_lt(img, y0):
    L = Layer(); d = L.d
    glass(d, (RX0, y0, RX0 + 190, y0 + 46))
    ico(d, 'reroll', RX0 + 30, y0 + 23, 17, TEXT_HI, shadow=False)
    big = Image.new('RGBA', (1, 1))
    d.ellipse([S(RX0 + 64), S(y0 + 9), S(RX0 + 92), S(y0 + 37)], fill=GOLD + (255,), outline=INK + (255,), width=S(2.5))
    T(d, (RX0 + 78, y0 + 24), '2', 22, INK, anchor='mm')
    keycap(d, RX0 + 110, y0 + 6, 40, 'Q')
    comp(img, L)


def send_lt(img, F, space=True, y=708):
    cx = 1765
    stick(img, K.verb_sticker('SEND IT'), cx, y, 4, scale=0.9 * V.UI_S); say('SEND', 'IT')
    if space:
        L = Layer(); d = L.d; keycap(d, cx - 70, y + 52, 140)                    # the space bar: a keycap with the space glyph
        d.line([(S(cx - 34), S(y + 62)), (S(cx - 34), S(y + 74)), (S(cx + 34), S(y + 74)), (S(cx + 34), S(y + 62))], fill=TEXT_HI + (255,), width=S(3))
        comp(img, L)


def strip(img, items, box=(560, 956, 1360, 1008)):
    """one short glass strip: icons and numbers, centred"""
    x0, y0, x1, y1 = box
    ym = (y0 + y1) / 2
    # measure, then draw centred
    def run(d, x, draw):
        for it in items:
            k = it[0]
            if k == 'chip':
                if draw:
                    path_chip(d, x + 15, ym, it[1], r=15)
                x += 36
            elif k == 'ico':
                if draw:
                    ico(d, it[1], x + 16, ym, 16, it[2])
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
        return x
    L = Layer(); d = L.d
    wdt = run(d, 0, False)
    cx = (x0 + x1) / 2
    bx0, bx1 = cx - wdt / 2 - 22, cx + wdt / 2 + 22
    glass(d, (bx0, y0, bx1, y1))
    run(d, bx0 + 22, True)
    comp(img, L)


# ------------------------------------------------------------------ the corp document (B, C unfolded) and its folded corner (C)
def memo(img, x0, y0, w, rounds, now=0, site='STATIC ALLEY', ang=-1.0, crease=False):
    """the intercepted Solace work order as a real document, every line at >= 16 px cap; the unit rows are printed v4 icons with
    counts (the round's head line keeps v39's words)"""
    def Td(d, xy, s, size, col, font='a', anchor='lm'):
        return T(d, (xy[0], xy[1]), s, size, col, font=font, anchor=anchor, where=DOC)

    rowh = 66
    ph = 222 + len(rounds) * rowh + 58
    pim = Image.new('RGBA', (S(w), S(ph)), (0, 0, 0, 0))
    d = ImageDraw.Draw(pim)
    d.rectangle([0, 0, S(w), S(ph)], fill=(236, 230, 214, 255))
    rng = np.random.default_rng(11)
    for _ in range(900):
        d.point((rng.uniform(0, S(w)), rng.uniform(0, S(ph))), fill=(212, 204, 186, 255))
    Td(d, (18, 34), 'SOLACE', 38, TEAL_D)
    seal(d, w - 42, 36, 24)
    d.rectangle([S(18), S(62), S(w - 18), S(64.5)], fill=TEAL_D + (255,))
    Td(d, (18, 90), 'WORK ORDER', 23, (96, 90, 80), font='m')
    Td(d, (w - 18, 90), 'SOL-WO-2611-07', 23, (96, 90, 80), font='m', anchor='rm')
    Td(d, (18, 128), 'RAID ORDER \u00b7 %s' % site, 28, INK)
    tw_ = Td(d, (18, 166), 'TARGET  Cell safehouse', 23, (60, 56, 50), font='m')
    d.rectangle([S(26 + tw_), S(156), S(min(w - 18, 26 + tw_ + 70)), S(176)], fill=(18, 16, 20, 255))
    y = 204
    for k, (head, groups) in enumerate(rounds):
        col = INK if k == now else (96, 92, 86)
        n = sum(g[3] for g in groups)
        Td(d, (18, y), 'ROUND %d%s  \u00b7  %d units' % (k + 1, ' (now)' if k == now else '', n), 24, col)
        gx = 26
        gy = y + 32
        for path, kind, label, cnt in groups:
            if path:
                Td(d, (gx, gy), path, 24, (170, 24, 32))
                gx += 20
            ic = V.icon_img(kind, 1.0, 10, ring=False)
            if k != now:
                ic = ic.copy(); ic.putalpha(ic.split()[3].point(lambda v: int(v * 0.6)))
            pim.alpha_composite(ic, (int(S(gx + 12) - ic.width / 2), int(S(gy) - ic.height / 2)))
            gx += 28 + Td(d, (gx + 28, gy + 1), '\u00d7%d' % cnt, 23, (40, 44, 52), font='m') + 22
        d.line([(S(18), S(y + 52)), (S(w - 18), S(y + 52))], fill=(214, 206, 190, 255), width=S(1))
        y += rowh
    if crease:                                              # unfolded: the fold lines it kept
        for cy_ in (112, 192 + 2 * 66 - 10):
            d.line([(0, S(cy_)), (S(w), S(cy_))], fill=(206, 198, 180, 255), width=S(2))
            d.line([(0, S(cy_ + 2)), (S(w), S(cy_ + 2))], fill=(248, 244, 232, 255), width=S(1))
    Td(d, (18, ph - 26), 'AUTHORISED', 23, (110, 104, 96), font='m')
    d.rectangle([S(160), S(ph - 36), S(260), S(ph - 16)], fill=(18, 16, 20, 255))
    st = Image.new('L', (S(236), S(60)), 0); sd = ImageDraw.Draw(st)
    sd.rectangle([S(3), S(3), S(233), S(57)], outline=255, width=S(3.5))
    sd.text((S(118), S(32)), 'INTERCEPTED', font=TR.font(ANTON, 38), fill=255, anchor='mm'); DOC.append('INTERCEPTED')
    noise = (np.random.default_rng(9).random((st.height, st.width)) > 0.25).astype(np.uint8) * 255
    st = SL.ImageChops.multiply(st, Image.fromarray(noise)).rotate(7, expand=True, resample=Image.BICUBIC)
    pim.paste(Image.new('RGBA', st.size, (196, 30, 40, 220)), (S(w - 252), S(ph - 84)), st)
    put_paper(img, pim, x0 + w / 2, y0 + ph / 2, ang)
    return y0 + ph


def seal(d, x, y, r):
    """the Solace seal: a teal ring, an inner ring of ticks, the S monogram"""
    d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(206, 226, 220, 255), outline=TEAL_D + (255,), width=S(3))
    for k in range(24):
        a = k * math.pi / 12
        d.line([(S(x + r * .70 * math.cos(a)), S(y + r * .70 * math.sin(a))), (S(x + r * .84 * math.cos(a)), S(y + r * .84 * math.sin(a)))],
               fill=TEAL_D + (255,), width=S(1.2))
    d.text((S(x), S(y + 1)), 'S', font=TR.font(ANTON, r * 1.05), fill=TEAL_D + (255,), anchor='mm')


def put_paper(img, pim, cx, cy, ang):
    pim = pim.rotate(ang, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', pim.size, (2, 2, 4, 0))
    sh.putalpha(pim.split()[3].filter(ImageFilter.GaussianBlur(S(5))).point(lambda v: int(v * 0.7)))
    img.alpha_composite(sh, (int(S(cx) - pim.width / 2 + S(4)), int(S(cy) - pim.height / 2 + S(6))))
    img.alpha_composite(pim, (int(S(cx) - pim.width / 2), int(S(cy) - pim.height / 2)))


def memo_folded(img, rounds, now=0, heat=25):
    """C at rest: the work order folded to a corner of paper under the glass: the seal, ROUND 1 · 8, a dog-ear and the edge of
    the red stamp; the unfold mark (a chevron) on the glass; Heat beside it"""
    w, h = 340, 96
    pim = Image.new('RGBA', (S(w), S(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(pim)
    body = [(0, 0), (w, 0), (w, h - 30), (w - 30, h), (0, h)]
    d.polygon([(S(x), S(y)) for x, y in body], fill=(236, 230, 214, 255))
    rng = np.random.default_rng(5)
    for _ in range(260):
        d.point((rng.uniform(0, S(w)), rng.uniform(0, S(h))), fill=(212, 204, 186, 255))
    d.polygon([(S(w), S(h - 30)), (S(w - 30), S(h - 30)), (S(w - 30), S(h))], fill=(206, 198, 180, 255), outline=(170, 162, 146, 255))
    seal(d, 46, h / 2, 30)
    n = sum(g[3] for g in rounds[now][1])
    T(d, (92, h / 2 - 2), 'ROUND %d \u00b7 %d' % (now + 1, n), 34, INK, where=DOC)
    d.rectangle([S(92), S(h / 2 + 22), S(250), S(h / 2 + 24)], fill=TEAL_D + (255,))
    st = Image.new('L', (S(80), S(40)), 0); sd = ImageDraw.Draw(st)               # the stamp's edge where the fold cuts it
    sd.rectangle([S(2), S(2), S(120), S(60)], outline=255, width=S(3.5))
    pim.paste(Image.new('RGBA', st.size, (196, 30, 40, 200)), (S(w - 46), S(4)), st.rotate(7, resample=Image.BICUBIC))
    put_paper(img, pim, RX0 + 12 + w / 2, 14 + h / 2, -2.0)
    L = Layer(); d = L.d
    cx, cy = RX0 + 12 + w / 2, 14 + h + 14
    d.line([(S(cx - 14), S(cy - 4)), (S(cx), S(cy + 6)), (S(cx + 14), S(cy - 4))], fill=CYAN + (220,), width=S(3))
    ico(d, 'flame', RX1 - 74, 126, 15, (255, 120, 60))
    T(d, (RX1 - 54, 127), str(heat), 30, TEXT_HI)
    comp(img, L)
    return 14 + h + 26


# ------------------------------------------------------------------ B: the Cell's pencil on the glass corner (round, credits, Heat)
def glass_tallies(img, rnd=1, rmax=4, credits=7, heat=25):
    py, pr = Wax(PEN_Y, 61), Wax(PEN_R, 62)
    for k in range(rmax):                                   # rounds: four boxes, the current one circled, done ones crossed
        x, y = 52 + k * 50, 50
        py.stroke(py.wobble([(x - 14, y - 14), (x + 14, y - 14), (x + 14, y + 14), (x - 14, y + 14), (x - 14, y - 14)], 0.5), 5, taper=False)
        if k + 1 < rnd:
            py.x(x, y, 9, 4)
    cx_ = 52 + (rnd - 1) * 50
    py.circle(cx_, 50, 28, 28, width=5, start=-2.0, over=0.4, tilt=0)
    py.circle(278, 50, 18, 18, width=5, start=-1.6, over=0.3, tilt=0)              # a pencil coin
    py.stroke(py.wobble([(278, 39), (278, 61)], 0.3), 4, taper=False)
    py.text(str(credits), 320, 50, 46, angle=-4); say(str(credits))
    fx, fy = 396, 50                                        # Heat: a pencil flame and the number, red
    pr.stroke(pr.wobble([(fx, fy - 22), (fx + 13, fy - 4), (fx + 12, fy + 12), (fx, fy + 20), (fx - 12, fy + 12), (fx - 12, fy - 3), (fx - 5, fy - 10), (fx, fy - 22)], 0.4), 5, taper=False)
    pr.text(str(heat), fx + 42, fy, 44, angle=-4); say(str(heat))
    py.ink_ss(img); pr.ink_ss(img)


# ------------------------------------------------------------------ plates
def plate(direction, kind):
    F = F_all(); img = blank()
    place = kind == 'place'
    rounds = V.ROUNDS
    if direction == 'A':
        map_base(img, F, words=False, place=place, pencil='icons')
        if place:
            held(img, False, *G.cc(*V.HOVER))
        core_lt(img, 8, 0 if place else 2)
        rows_lt(img)
        crew_lt(img, held_='RUNE' if place else None)
        undo_lt(img)
        y = wave_strip(img, rounds)
        y = shop_lt(img, y + 16)
        reroll_lt(img, y + 12)
        send_lt(img, F)
        if place:
            strip(img, [('ico', 'place', GOLD), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2 \u2192 0', S_GAIN), ('sep',),
                        ('ico', 'heart', (236, 40, 90)), ('txt', '8', S_GAIN), ('sep',), ('ico', 'skull', S_HI), ('txt', '8/8', S_HI)])
        else:
            strip(img, [('chip', 'A'), ('ico', 'shield', S_GAIN), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2', S_HARM), ('sep',),
                        ('ico', 'heart', (236, 40, 90)), ('txt', '8 \u2192 6', S_HARM), ('sep',), ('ico', 'skull', S_HI), ('txt', '6/8', S_HI)])
    elif direction == 'B':
        map_base(img, F, words=True, place=place, pencil='words')
        if place:
            held(img, True, *G.cc(*V.HOVER))
        glass_tallies(img)
        crew_lt(img, held_='RUNE' if place else None, words=True)
        y = memo(img, RX0 - 16, 14, 404, rounds)
        y = shop_lt(img, y + 22, words=True, header=True)
        send_lt(img, F, space=False, y=y + 70)
    else:
        map_base(img, F, words=False, place=place, pencil='icons')
        if place:
            held(img, False, *G.cc(*V.HOVER))
        core_lt(img, 8, 0 if place else 2)
        rows_lt(img)
        crew_lt(img, held_='RUNE' if place else None)
        undo_lt(img)
        y = memo_folded(img, rounds)
        y = shop_lt(img, y + 10)
        reroll_lt(img, y + 12)
        send_lt(img, F)
        if place:                                           # the work order unfolded over the shop (as on hover)
            memo(img, RX0 - 16, 14, 404, rounds, ang=-0.6, crease=True)
            strip(img, [('ico', 'place', GOLD), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2 \u2192 0', S_GAIN), ('sep',),
                        ('ico', 'heart', (236, 40, 90)), ('txt', '8', S_GAIN), ('sep',), ('ico', 'skull', S_HI), ('txt', '8/8', S_HI)])
        else:
            strip(img, [('chip', 'A'), ('ico', 'shield', S_GAIN), ('sep',), ('chip', 'B'), ('ico', 'drop', S_HARM), ('txt', '2', S_HARM), ('sep',),
                        ('ico', 'heart', (236, 40, 90)), ('txt', '8 \u2192 6', S_HARM), ('sep',), ('ico', 'skull', S_HI), ('txt', '6/8', S_HI)])
    return img


def blank():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))


# ------------------------------------------------------------------ the set 6 baseline (r3_plan / r3_place), listed from the plates
_CREW6 = ['CREW', 'KAI', 'GUNNER', 'L3', 'SMG', 'VEX', 'SNIPER', 'L2', 'RAIL', 'MOTH', 'TECH', 'L2', 'JAMMER', 'RUNE', 'BRUISER', 'L1', 'SHOTGUN',
          'on c2', 'on e5', 'on a7', 'ON MAP 3', 'BENCH 1', 'DEVICES 1', 'UNDO', '[Z]', 'INCOMING', 'intercepted', 'HEAT 25',
          'BLACK MARKET', 'peel to buy', '5 offers', '3', 'SHOTGUN', '4', 'RAIL', '3', 'BARRICADE', '2', 'MINE', '4', 'SENTRY', 'REROLL (Q)', '2c',
          'START ROUND 1', 'SEND IT', '[SPACE]', 'BARRICADE', 'SAFE', 'HOUSE', '6 \u2192 3', 'A', 'B', '5', '3', 'ROUND', '1/4', 'CREDITS', '7',
          'RAID: STATIC ALLEY'] + list('abcdefg') + [str(k) for k in range(1, 8)]
BASE = dict(plan=_CREW6 + ['CORE 8 \u2192 6', 'FORECAST', 'A holds at b4', 'B 2 leak', 'Core 8 \u2192 6', '6/8 killed', '2 leak', '8 \u2192 6'],
            place=_CREW6 + ['CORE 8/8', 'IF PLACED e7', 'B 2 leak', '0 leak', 'Core safe', '8/8 killed', '2 leak', '0', 'safe', '+3', '+2', '+1',
                            'RUNE', 'BRUISER', 'L1', 'SHOTGUN'])


def sheet(counts):
    tw_, th_ = 960, 540
    pad, cap = 12, 64
    sh = Image.new('RGB', (2 * tw_ + 3 * pad, 3 * (th_ + cap) + 4 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 17); fa = ImageFont.truetype(ANTON, 24); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 10), 'RAID low text: A pictogram / B diegetic / C happy medium (plan + place, on set 6)', font=fb, fill=TEXT_HI)
    names = dict(A='A  pictogram', B='B  diegetic', C='C  happy medium')
    for r, dn in enumerate('ABC'):
        for c, kind in enumerate(('plan', 'place')):
            n = 'lt_%s_%s' % (dn, kind)
            im = Image.open(OUTD + n + '.png').resize((tw_, th_), Image.LANCZOS)
            x = pad + c * (tw_ + pad); y = 54 + pad + r * (th_ + cap + pad)
            sh.paste(im, (x, y))
            ct = counts[n]
            d.text((x + 4, y + th_ + 4), '%s   %s   %s.png' % (names[dn], kind, n), font=fa, fill=TEXT_HI)
            d.text((x + 4, y + th_ + 38), 'words on screen %d (labels %d, numbers %d), corp document words %d   |   set 6 r3_%s: %d words' %
                   (ct['words'], ct['labels'], ct['numbers'], ct['doc_words'], kind, counts['base_' + kind]['words']), font=f, fill=TEXT_MID)
    sh.save(OUTD + 'lt_sheet.jpg', quality=90)
    print('ok', OUTD + 'lt_sheet.jpg', flush=True)


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    counts = {}
    for k in ('plan', 'place'):
        counts['base_' + k] = classify(BASE[k])
    for dn in 'ABC':
        for kind in ('plan', 'place'):
            SHOWN.clear(); DOC.clear(); SMALL.clear()
            ov = plate(dn, kind)
            n = 'lt_%s_%s' % (dn, kind)
            V.finish(ov).save(OUTD + n + '.png')
            c = classify(SHOWN)
            c['doc_words'] = classify(DOC)['words']
            c['shown'] = list(SHOWN)
            c['small'] = list(SMALL)
            counts[n] = c
            print('ok', n, {k: v for k, v in c.items() if k not in ('shown',)}, flush=True)
    json.dump(counts, open('D:/rc_scratch/raid_v3/insp/lt_counts.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    sheet(counts)
