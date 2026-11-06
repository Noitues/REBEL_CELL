"""wp_cards: the card hand in WPAP FACETED.  Same layout as the black-book card (cost badge top left, big icon, title, type band, rules text),
restyled: chamfered die-cut card, a faceted sunburst art band, an ink seat for the icon, a WHITE title on an ink band (hard pink offset: the legibility fix),
a flat type plate, dark ink rules text on cream.  render_card(name, variant, seed, ss, scale) -> RGBA like st_cards.render_card."""
import math, json, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from st_gfx import Cv, font, text_mask, poly, circle, blur, grow, shrink, shift, extrude, ANTON, MONO
import st_tower as T
import st_cards as K
import wp_lib as L
from wp_lib import WINK

CW, CH, M = K.CW, K.CH, K.M
FD_PLEX = 'IBMPlexSansCondensed-Medium.ttf'
NW = K.NW
J = K.J
CARDS = K.CARDS


def c01(c):
    return np.asarray(c, np.float32) / 255.0


def wtext(cv, txt, x, y, px, fontname=ANTON, fill=(255, 255, 255), ink=None, ink_w=0.0, drop=None, dcol=None, rot=0.0, track=0.0, skew=0.0, op=1.0, clip=None):
    ss = cv.ss
    m = text_mask(cv, txt, x, y, fontname, px, 'mm', skew, rot, track, 0.0, 0)
    m = np.clip((m - 0.5) * 5 + 0.5, 0, 1)
    full = grow(m, ink_w * ss) if ink_w else m
    if drop:
        ex = extrude(full, drop[0] * ss, drop[1] * ss)
        cv.paint(blur(ex, 0.35 * ss) * (clip if clip is not None else 1), c01(dcol), op)
    if ink_w:
        cv.paint(blur(full, 0.35 * ss), c01(ink), op)
    cv.paint(blur(m, 0.35 * ss), c01(fill), op)
    return m


def plate(cv, pts, col, ink=True, drop=(2.2, 2.8), dcol=WINK, ink_w=1.8, op=1.0):
    ss = cv.ss
    m = poly(cv, pts)
    if drop:
        ex = extrude(m, drop[0] * ss, drop[1] * ss)
        cv.paint(blur(ex, 0.3 * ss), c01(dcol))
    if ink:
        cv.paint(blur(grow(m, ink_w * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(m, 0.3 * ss), c01(col), op)
    return m


def sunburst(cv, cx, cy, region, ramp, seed, accent, glint, n=13):
    """flat triangular rays from the icon centre, clipped to region; colour by lit side, one accent ray, one glint ray"""
    X, Y = cv.grid()
    ang = np.arctan2(Y - cy, X - cx)
    r = np.random.default_rng(seed)
    cuts = np.sort(r.uniform(-math.pi, math.pi, n))
    idx = np.searchsorted(cuts, ang) % n
    rgb = np.zeros((cv.H, cv.W, 3), np.float32)
    cols = []
    lx, ly = L.SHADOW_DIR
    for i in range(n):
        a_mid = (cuts[i - 1] + cuts[i]) / 2 if i > 0 else (cuts[-1] - 2 * math.pi + cuts[0]) / 2
        lit = -(math.cos(a_mid) * lx + math.sin(a_mid) * ly)
        t = 0.5 + 0.5 * lit + r.normal(0, 0.24)
        cols.append(ramp[int(np.clip(t, 0, 0.999) * len(ramp))])
    # the accent ray: the darkest-side ray, the glint ray: the lightest
    order = sorted(range(n), key=lambda i: cols.index(cols[i]))
    ai = int(r.integers(0, n))
    cols[ai] = accent
    gi = (ai + n // 2 + 1) % n
    cols[gi] = glint
    for i in range(n):
        rgb[idx == i] = cols[(i) % n]
    cv.paint(region, rgb / 255.0)


def card_wp(name, seed=0, ss=3):
    P = L.P()
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    cv = Cv(-M, -M, CW + 2 * M, CH + 2 * M, ss)
    X, Y = cv.grid()
    ch = 16
    shape = [(0, 0), (CW - ch, 0), (CW, ch), (CW, CH), (ch, CH), (0, CH - ch)]
    cm = poly(cv, shape)
    # hard offset drop (magenta plane) then ink border
    ex = extrude(cm, 5.0 * ss, 6.0 * ss)
    cv.paint(ex * (1 - grow(cm, 2.6 * ss)) , c01((120, 12, 92)))
    cv.paint(blur(grow(cm, 2.8 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(cm, 0.3 * ss), c01(L.CREAM))
    # ---- art band
    x0, y0, x1, y1 = 8, 8, CW - 8, 126
    ab = poly(cv, [(x0, y0), (x1 - 14, y0), (x1, y0 + 14), (x1, y1), (x0, y1)]) * cm
    cv.paint(blur(grow(ab, 2.0 * ss), 0.3 * ss), c01(WINK))
    icx, icy = CW / 2, 66
    sunburst(cv, icx, icy, blur(ab, 0.3 * ss), P['card_band'], seed * 3 + 5, P['accent'], P['glint'])
    # cost-side shade plane: one flat dark triangle in the lower right corner of the band
    tri = poly(cv, [(x1, y1), (x1, y1 - 46), (x1 - 70, y1)]) * ab
    cv.paint(blur(tri, 0.3 * ss), c01(WINK), 0.34)
    # ink seat (octagon) + pink keyline
    def octa(r, rot=22.5):
        return [(icx + r * math.cos(math.radians(rot + 45 * k)), icy + r * math.sin(math.radians(rot + 45 * k))) for k in range(8)]
    seat = poly(cv, octa(41))
    cv.paint(blur(extrude(grow(seat, 2.2 * ss), 3.0 * ss, 3.6 * ss), 0.3 * ss) * (1 - grow(seat, 2.2 * ss)) * ab, c01(WINK))
    cv.paint(blur(grow(seat, 2.4 * ss), 0.3 * ss) * ab, c01(WINK))
    cv.paint(blur(seat, 0.3 * ss) * ab, c01((32, 10, 56)))
    kl = np.clip(poly(cv, octa(37.4)) - poly(cv, octa(35.8)), 0, 1)
    cv.paint(blur(kl, 0.3 * ss) * ab, c01(L.PINK_))
    gm = T.glyph_mask(spec['g'], 62, cv, icx, icy - 1)
    cv.paint(blur(shift(gm, 2.2 * ss, 2.2 * ss), 0.3 * ss) * ab, c01(L.PINK_))
    cv.paint(blur(grow(gm, 1.7 * ss), 0.3 * ss) * ab, c01(WINK))
    cv.paint(blur(gm, 0.3 * ss) * ab, c01(L.WHITE_))
    # multiplier
    if spec.get('mult'):
        pm = plate(cv, [(112, 94), (162, 90), (164, 120), (114, 124)], WINK, ink=False, drop=(2.2, 2.6), dcol=P['accent'])
        wtext(cv, '\u00d7' + spec['mult'], 138, 107, 30, ANTON, fill=(255, 255, 255), ink=WINK, ink_w=0.0, rot=-3)
    # ---- title band: ink plate with a white title (no pink on pink)
    tb = poly(cv, [(0, 130), (CW, 124), (CW, 160), (0, 166)]) * cm
    cv.paint(blur(extrude(tb, 0, 3.0 * ss), 0.3 * ss) * (1 - tb) * cm, c01(P['accent']))
    cv.paint(blur(tb, 0.3 * ss), c01(WINK))
    nm = spec['nm']
    ft_ = font(ANTON, 36 * ss)
    wt_ = ft_.getlength(nm) / ss + 1.2 * len(nm)
    pxt = 36 if wt_ <= 138 else 36 * 138 / wt_
    wtext(cv, nm, CW / 2, 144.5, pxt, ANTON, fill=(255, 255, 255), drop=(2.6, 3.0), dcol=L.PINK_, rot=-2.2, track=1.2, ink=WINK, ink_w=0.0)
    # ---- type plate
    fam = spec['fam']
    col = P['tower_band'] if fam == 'TOWER' else P['wave_band']
    tw = 76 if fam == 'TOWER' else 66
    ty = 178
    plate(cv, [(CW / 2 - tw / 2 - 5, ty - 11), (CW / 2 + tw / 2 + 5, ty - 12.5), (CW / 2 + tw / 2 - 3, ty + 11), (CW / 2 - tw / 2 - 11, ty + 12.5)], col, drop=(2.0, 2.6), dcol=WINK)
    wtext(cv, fam, CW / 2 - 3, ty + 0.4, 19, ANTON, fill=WINK if fam == 'TOWER' else (255, 255, 255), track=1.6, rot=-1.4)
    # ---- rules text
    txt = spec['txt']
    px = 22
    f = font(FD_PLEX, px * ss)
    while f.getlength(txt) / ss > CW - 46 and px > 15:
        px -= 1
        f = font(FD_PLEX, px * ss)
    ly = 207
    wtxt = f.getlength(txt) / ss
    bar = poly(cv, [(CW / 2 - 7 - wtxt / 2 - 4, ly + 13.5), (CW / 2 - 7 + wtxt / 2 + 6, ly + 11.5), (CW / 2 - 7 + wtxt / 2 + 4, ly + 16.5), (CW / 2 - 7 - wtxt / 2 - 6, ly + 18.5)])
    cv.paint(blur(bar, 0.3 * ss) * cm, c01(L.PINK_))
    wtext(cv, txt, CW / 2 - 7, ly, px, FD_PLEX, fill=WINK, ink_w=0.0, rot=-0.8)
    # ---- owner mark: three flat triangles (pink / secondary ink / violet), bottom right
    bx, by = CW - 26, CH - 17
    for k, (cc, d) in enumerate(((L.PINK_, (-9, 5)), (P['accent'], (0, -6)), ((150, 96, 255), (9, 5)))):
        tri2 = poly(cv, [(bx + d[0] - 7, by + d[1] + 6), (bx + d[0] + 7, by + d[1] + 6), (bx + d[0], by + d[1] - 8)])
        cv.paint(blur(grow(tri2, 1.2 * ss), 0.3 * ss) * cm, c01(WINK))
        cv.paint(blur(tri2, 0.3 * ss) * cm, c01(cc))
    # ---- cost badge: cyan hexagon (RAM), two flat planes
    hx_, hy_ = 21, 21
    hexa = [(hx_ + 19 * math.cos(math.radians(30 + 60 * k)), hy_ + 19 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    hm = poly(cv, hexa)
    cv.paint(blur(extrude(grow(hm, 2.0 * ss), 2.4 * ss, 3.0 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(grow(hm, 2.2 * ss), 0.3 * ss), c01(WINK))
    cv.paint(blur(hm, 0.3 * ss), c01((26, 143, 184)))
    up = poly(cv, [hexa[3], hexa[4], hexa[5], hexa[0], (hx_ + 2, hy_ - 4), ])
    up = poly(cv, [(hx_ - 19, hy_ - 12), (hx_ + 8, hy_ - 19), (hx_ + 19, hy_ - 10), (hx_ + 1, hy_ + 2), (hx_ - 19, hy_ + 9)]) * hm
    cv.paint(blur(up, 0.3 * ss), c01((92, 225, 255)))
    wtext(cv, str(cost), hx_ + 0.5, hy_ + 1.2, 27, ANTON, fill=WINK)
    if loud:
        lx, ly2 = CW - 54, 17
        bx_ = poly(cv, [(lx - 21, ly2 - 12), (lx + 18, ly2 - 14), (lx + 22, ly2 + 12), (lx - 18, ly2 + 14)])
        cv.paint(blur(extrude(grow(bx_, 2.4 * ss), 2.2 * ss, 2.8 * ss), 0.3 * ss), c01(WINK))
        cv.paint(blur(grow(bx_, 2.4 * ss), 0.3 * ss), c01(WINK))
        cv.paint(blur(bx_, 0.3 * ss), c01((160, 60, 255)))
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(blur(e2, 0.3 * ss), c01(L.WHITE_))
        cv.paint(blur(circle(cv, lx - 9, ly2, 2.9), 0.3 * ss), c01(WINK))
        wtext(cv, '+' + str(loud), lx + 11, ly2 + 0.6, 21, ANTON, fill=(255, 255, 255))
    return cv


def render_card(name, variant='A', seed=0, ss=3, scale=1):
    cv = card_wp(name, seed, ss)
    return cv.to_image(scale=scale)


if __name__ == '__main__':
    import asm_r2 as A
    A.setup()
    L.VAR[0] = sys.argv[1] if len(sys.argv) > 1 else 'A'
    ims = [render_card(n, 'A', seed=s, ss=4, scale=2) for n, s in (('Brace', 1), ('Spin3', 4), ('Trigger', 7), ('Twist', 10))]
    w = sum(i.width for i in ims)
    sheet = Image.new('RGBA', (w, ims[0].height), (30, 24, 44, 255))
    x = 0
    for i in ims:
        sheet.alpha_composite(i, (x, 0))
        x += i.width
    sheet.convert('RGB').save('D:/rc_scratch/combat_redesign/punk/wpap_faceted/out/cards_%s.png' % L.VAR[0])
