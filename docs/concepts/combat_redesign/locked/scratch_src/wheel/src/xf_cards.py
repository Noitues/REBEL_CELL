"""xf_cards: the card hand in the XEROX FLYER style on the F1 black-book layout (cost badge top-left, big icon, title, type band, rules text).
A = white photocopy sheet, black key plate, magenta + cyan slapped off-register; title is black on a white label (easy to read).
B = black toner sheet with a die-cut white border; title is paper white on black.
Same info as before: cost, title, type, rules text, multiplier, loud (Trace) tab."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from xf_gfx import *
import st_cards as K
import st_tower as T
import xf_tower as XT

CW, CH, M = K.CW, K.CH, K.M
PLEX = 'IBMPlexSansCondensed-Medium.ttf'
VAR = XT.VAR
CARDS = K.CARDS


def isB():
    return VAR[0] == 'B'


def fit_px(fname, txt, maxw, px0, ss):
    px = px0
    while font(fname, px * ss).getlength(txt) / ss > maxw and px > 10:
        px -= 0.5
    return px


def rect(cv, x0, y0, x1, y1, rot=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = []
    for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        dx, dy = x - cx, y - cy
        pts.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return poly(cv, pts)


def card(name, seed=0, ss=4):
    B = isB()
    spec = CARDS[name]
    cost, loud = K.J['cards'][name]
    cv = Cv(-M, -M, CW + 2 * M, CH + 2 * M, ss)
    X, Y = cv.grid()
    base = rect(cv, 0, 0, CW, CH)
    sheet = rough(base, cv, 1.5, 9.0, seed + 5)
    GR = TONER if not B else SHEET            # the "ink" on the sheet (text, rules)
    GROUND = SHEET if not B else TONER
    # block drop: the flyer is stuck to the wall
    cv.paint(blur(shift(sheet, 4 * ss, 6 * ss), 3.0 * ss), hx('08060C'), 0.65)
    if B:
        edge = rough(grow(base, 4.5 * ss), cv, 1.2, 7.0, seed + 6)
        cv.paint(edge, SHEET * 0.93)
        cv.paint(sheet, TONER)
        n = vnoise(cv.H, cv.W, 24 * ss, seed + 1, 2)
        cv.paint(sheet * np.clip((n - 0.55) * 1.2, 0, 1), hx('241F2C'), 0.7)
    else:
        cv.paint(sheet, SHEET[None, None, :] * (0.97 + 0.05 * vnoise(cv.H, cv.W, 30 * ss, seed + 1, 2))[..., None])
        cl = copier_edge(cv, sheet, seed + 3, 5.5, 0.9, (-0.4, 0.8))
        cv.paint(rough(cl, cv, 0.5, 3.0, seed + 8), TONER)
    sp = toner_noise(cv, seed + 7, 0.9, 0.9)
    cv.paint(blur(sp, 0.3 * ss) * sheet, TONER if not B else SHEET, 0.3)

    # ---------------------------------------------------------------- art band
    ab = rough(rect(cv, 9, 10, CW - 9, 128), cv, 0.8, 8.0, seed + 40)
    icx, icy = CW / 2, 66
    if B:
        cv.paint(grow(ab, 2.0 * ss), SHEET * 0.93)
        cv.paint(ab, TONER)
        mg = plate_shift(ab, cv, 2.4, -2.0)
        ink(cv, mg * ab if False else mg, MAG, 0.06, seed + 41)
        # black halftone shade, heavier at the bottom
        cov = ramp(cv, (0, 20), (0, 126), 0.0, 0.72, 1.1)
        ht = halftone(cov, 7.0 * ss, 45, 0, 0, aa=1.0 * ss)
        cv.paint(ht * ab * mg, TONER, 0.97)
        disc = rough(circle(cv, icx, icy, 40), cv, 0.8, 7.0, seed + 3)
        cv.paint(plate_shift(disc, cv, -4.0, 3.0) * ab, CYN)
        cv.paint(grow(disc, 2.0 * ss) * ab, TONER)
        ink(cv, disc * ab, SHEET * 0.96, 0.03, seed + 42)
        gcol, gdrop = TONER, TONER
    else:
        cv.paint(grow(ab, 2.0 * ss), TONER)
        cv.paint(ab, TONER)
        # coarse paper-white halftone: a burst of dots rising from the bottom
        cov = ramp(cv, (0, 126), (0, 20), 0.0, 0.58, 1.3) * 0.9
        rb = np.hypot(X - icx, Y - icy)
        cov = cov * np.clip((rb - 36) / 12.0, 0, 1)
        ht = halftone(cov, 7.0 * ss, 45, 0, 0, aa=1.0 * ss)
        cv.paint(ht * ab, SHEET * 0.93)
        disc = rough(circle(cv, icx, icy, 40), cv, 0.8, 7.0, seed + 3)
        cv.paint(plate_shift(disc, cv, -4.0, 3.0) * ab, CYN)
        ink(cv, plate_shift(disc, cv, 2.4, -2.0) * ab, MAG, 0.05, seed + 42)
        gcol, gdrop = TONER, TONER
    # the icon: paper-white silhouette, hard black key outline + drop
    gm = T.glyph_mask(spec['g'], 66, cv, icx, icy - 1)
    gm = np.clip((blur(gm, 0.3 * ss) - 0.5) * 3 + 0.5, 0, 1)
    cv.paint(extrude(grow(gm, 2.4 * ss), 3.4 * ss, 3.8 * ss) * ab, TONER)
    cv.paint(grow(gm, 2.4 * ss) * ab, TONER)
    cv.paint(gm * ab, hx('FBFAF4'))
    # glints: two cut-out stars
    for (gx, gy, gr) in ((icx - 56, icy - 38, 5.5), (icx + 54, icy + 34, 4.4)):
        pts = []
        for q in range(8):
            rad = gr if q % 2 == 0 else gr * 0.28
            a = math.pi / 4 * q - math.pi / 2
            pts.append((gx + rad * math.cos(a), gy + rad * math.sin(a)))
        cv.paint(poly(cv, pts) * ab, hx('FBFAF4'))
    if spec.get('mult'):
        xtext(cv, '\u00d7' + spec['mult'], 126, 99, 34, ANTON, fill=hx('FBFAF4'), off=(2.4, 2.4), off_col=MAG if not B else TONER,
              edge=TONER, edge_w=2.0, skew=0.12, rot=-4, wob=0.2, seed=seed)

    # ---------------------------------------------------------------- title: a label slab, big and black on white (A) / white on black (B)
    lab = rough(rect(cv, 13, 131, CW - 13, 163, -1.6), cv, 0.5, 7.0, seed + 50)
    if B:
        cv.paint(extrude(grow(lab, 2.2 * ss), 3.0 * ss, 3.4 * ss), SHEET * 0.93)
        cv.paint(grow(lab, 2.0 * ss), SHEET * 0.93)
        ink(cv, lab, MAG, 0.04, seed + 51)
        cv.paint(grow(lab, -0.0), TONER, 0.0)
        tcol, tgh = hx('FBFAF4'), TONER
        lab_in = shrink(lab, 2.6 * ss)
        cv.paint(lab_in, TONER)
        ink(cv, plate_shift(lab_in, cv, 2.0, 2.0), MAG, 0.0, seed + 52, 0.0)
    else:
        cv.paint(extrude(grow(lab, 2.2 * ss), 3.4 * ss, 3.8 * ss), TONER)
        cv.paint(grow(lab, 2.2 * ss), TONER)
        cv.paint(plate_shift(lab, cv, 2.6, 2.2), MAG)
        cv.paint(lab, hx('FBFAF4'))
        tcol = TONER
    nm = spec['nm']
    px = fit_px(ANTON, nm, 130 - 0.9 * len(nm), 38, ss)
    if K.NW[0]:
        bar = rect(cv, 30, 141, CW - 30, 155, -1.6)
        cv.paint(bar, MAG)
    else:
        xtext(cv, nm, CW / 2, 148, px, ANTON, fill=tcol, off=(1.7, 1.7) if not B else (2.2, 2.0), off_col=MAG, skew=0.1, rot=-1.6, track=0.9, wob=0.15, seed=seed + 53, grain=0.02)

    # ---------------------------------------------------------------- type band: a flat cyan block (A) / paper block (B), black type
    ty = 182
    tw_ = 76 if spec['fam'] == 'TOWER' else 66
    tb = rough(rect(cv, CW / 2 - tw_ / 2, ty - 10, CW / 2 + tw_ / 2, ty + 10, 1.2), cv, 0.4, 6.0, seed + 60)
    cv.paint(extrude(grow(tb, 1.6 * ss), 2.4 * ss, 2.8 * ss), TONER if not B else SHEET * 0.93)
    cv.paint(grow(tb, 1.6 * ss), TONER if not B else SHEET * 0.93)
    ink(cv, tb, CYN if not B else hx('FBFAF4'), 0.04, seed + 61)
    if not K.NW[0]:
        xtext(cv, spec['fam'], CW / 2, ty + 0.5, 17, ANTON, fill=TONER, rot=1.2, track=2.0, wob=0.1, seed=seed + 62, grain=0.0)

    # ---------------------------------------------------------------- rules text: big, plain, black (A) / white (B), a magenta highlighter swipe under the number
    txt = spec['txt']
    px = fit_px(PLEX, txt, 142, 23, ss)
    RX = 79
    ly = 212
    wtxt = font(PLEX, px * ss).getlength(txt) / ss
    if spec.get('num') and not K.NW[0]:
        hx_ = RX + wtxt / 2
        sw = rect(cv, hx_ - 13, ly - 9, hx_ + 4, ly + 10, -1.5)
        sw = rough(sw, cv, 0.5, 6.0, seed + 70)
        if B:
            ink(cv, sw, MAG, 0.05, seed + 71)
        else:
            mult(cv, sw, MAG, 1.0)
    if K.NW[0]:
        for q, wq in enumerate((0.7, 0.45)):
            cv.paint(rect(cv, CW / 2 - wq * 70, ly - 7 + q * 15, CW / 2 + wq * 70, ly - 3 + q * 15), GR, 0.9)
    else:
        xtext(cv, txt, RX, ly, px, PLEX, fill=GR, wob=0.1, seed=seed + 72, grain=0.0, rot=-0.5)
    ul = rect(cv, RX - wtxt / 2 - 2, ly + 14, RX + wtxt / 2 + 2, ly + 16.2, -0.6)
    cv.paint(ul, GR if not B else SHEET * 0.95)
    # tag: an abstract magenta zig-zag, bottom right (ownership, no letters)
    K.scribble_tag(cv, CW - 36, 234, 0.55, MAG, seed + 50, ink=True) if not B else K.scribble_tag(cv, CW - 36, 234, 0.55, MAG, seed + 50, ink=False)
    # a registration cross bottom-left
    XT.reg_mark(cv, (16, 234), 4.0, col=GR)

    # ---------------------------------------------------------------- cost coin (RAM coin stays cyan) and the loud (Trace) tab
    cx_, cy_ = 18, 20
    coin = circle(cv, cx_, cy_, 17.5)
    cv.paint(extrude(grow(coin, 2.2 * ss), 2.6 * ss, 3.0 * ss), TONER)
    cv.paint(grow(coin, 2.2 * ss), SHEET * 0.97)
    cv.paint(grow(coin, 0.8 * ss), TONER)
    cv.paint(plate_shift(coin, cv, 2.0, 1.6), MAG)
    cv.paint(shrink(coin, 0.6 * ss), hx('5CE1FF'))
    ht = halftone(ramp(cv, (cx_ - 12, cy_ - 12), (cx_ + 14, cy_ + 16), 0.0, 0.7), 4.6 * ss, 45, 0, 0, aa=1.0 * ss)
    cv.paint(ht * shrink(coin, 1.8 * ss), hx('1A8FB8'))
    if K.NW[0]:
        for q in range(int(cost)):
            xq = cx_ + (q - (int(cost) - 1) / 2) * 6.0
            cv.paint(rect(cv, xq - 1.3, cy_ - 8, xq + 1.3, cy_ + 8), TONER)
    else:
        xtext(cv, str(cost), cx_ + 0.3, cy_ + 1.0, 29, ANTON, fill=TONER, edge=hx('FBFAF4'), edge_w=1.3, wob=0.0, grain=0.0)
    if loud:
        lx, ly2 = CW - 54, 17
        box = rough(rect(cv, lx - 20, ly2 - 12, lx + 20, ly2 + 12, 1.0), cv, 0.4, 6.0, seed + 80)
        cv.paint(extrude(grow(box, 2.4 * ss), 2.4 * ss, 2.8 * ss), TONER)
        cv.paint(grow(box, 2.4 * ss), SHEET * 0.97)
        cv.paint(grow(box, 0.9 * ss), TONER)
        ink(cv, box, VIOLET, 0.03, seed + 81)
        eye = circle(cv, lx - 9, ly2, 7.2)
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(grow(e2, 1.0 * ss), TONER)
        cv.paint(e2, hx('FBFAF4'))
        cv.paint(circle(cv, lx - 9, ly2, 2.9), TONER)
        if K.NW[0]:
            for q in range(int(loud)):
                cv.paint(rect(cv, lx + 7 + q * 6, ly2 - 7, lx + 9.4 + q * 6, ly2 + 7), hx('FBFAF4'))
        else:
            xtext(cv, '+' + str(loud), lx + 10.5, ly2 + 0.5, 19, ANTON, fill=hx('FBFAF4'), edge=TONER, edge_w=1.2, wob=0, grain=0)
    return cv


def render_card(name, variant='A', seed=0, ss=4, scale=1):
    cv = card(name, seed, ss)
    return cv.to_image(scale=scale)


if __name__ == '__main__':
    import time
    import asm_r2
    asm_r2.setup()
    VAR[0] = sys.argv[1] if len(sys.argv) > 1 else 'A'
    t = time.time()
    names = ['Brace', 'Spin3', 'Trigger', 'Twist']
    ims = [render_card(n, 'A', seed=i * 3 + 1, ss=4, scale=2) for i, n in enumerate(names)]
    sheet = Image.new('RGBA', (ims[0].width * 4 + 40, ims[0].height + 20), (30, 26, 44, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (10 + i * (im.width + 6), 10))
    sheet.save('D:/rc_scratch/combat_redesign/locked/wheel/out/cards_%s.png' % VAR[0])
    print('cards', round(time.time() - t, 1))
