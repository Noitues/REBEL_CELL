"""sp_cards: the CARD HAND in Spider-Punk collage, on the F1 black-book layout (cost badge top-left, big icon, title, type band, rules text, Trace tab top-right).
A = POSTER card: white cut-paper sheet, purple/magenta poster panel with a yellow lightning shard, YELLOW title strip with BLACK letters.
B = FLYER card: black photocopy sheet, yellow panel with a cobalt sunburst, WHITE title strip with BLACK letters.
Game information is unchanged: cost, title, type, rules text, multiplier, loud (Trace) tab."""
import math, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T
import st_cards as K0

CW, CH, M = K0.CW, K0.CH, K0.M
CX = 80.0          # content centre: the next card overlaps the right 20 px of this one, so text lives left of x=158
NW = K0.NW
CARDS = K0.CARDS
J = K0.J

C_MAG = hx('FF2D96'); C_MAG_D = hx('B20A68'); C_MAG_L = hx('FF8CC8')
C_YEL = hx('FFCC00'); C_YEL_D = hx('D69600')
C_COB = hx('283CF5'); C_COB_D = hx('141C8C')
C_PUR = hx('4A208A'); C_PUR_D = hx('260E54')
C_NEWS = hx('E6E0CC'); C_NEWS_D = hx('BAB2A0')
C_BLK = hx('0E0C14'); C_CUT = hx('FCFAF4')
C_RAM = hx('1A8FB8')


def ht(cv, dens, pitch, ang, gain=1.0):
    X, Y = cv.grid()
    a = math.radians(ang)
    u = X * math.cos(a) + Y * math.sin(a)
    v = -X * math.sin(a) + Y * math.cos(a)
    fu = (u % pitch) - pitch / 2
    fv = (v % pitch) - pitch / 2
    d = np.hypot(fu, fv)
    rad = np.sqrt(np.clip(dens, 0, 1)) * pitch * 0.62 * gain
    return np.clip((rad - d) * cv.ss + 0.5, 0, 1).astype(np.float32)


def cut(cv, m, fill, edge=2.0, drop=(2.4, 3.6), drop_a=0.9, edge_col=None, op=1.0):
    ss = cv.ss
    edge_col = C_CUT if edge_col is None else edge_col
    e = grow(m, edge * ss) if edge else m
    if drop:
        cv.paint(shift(e, drop[0] * ss, drop[1] * ss), C_BLK, drop_a * op)
    if edge:
        cv.paint(e, edge_col, op)
    if isinstance(fill, np.ndarray) and fill.ndim == 3:
        cv.paint(m, fill, op)
    else:
        cv.paint(m, fill, op)


def scissor(cv, pts, rough=0.7, seed=0):
    m = poly(cv, pts)
    return np.clip((blur(warp(m, rough * cv.ss, 22 * cv.ss, seed), 0.45 * cv.ss) - 0.5) * 8 + 0.5, 0, 1)


def paper_tex(cv, base, seed, strength=0.05):
    n = vnoise(cv.H, cv.W, 3.0 * cv.ss, seed, 2) - 0.5
    n2 = vnoise(cv.H, cv.W, 30.0 * cv.ss, seed + 4, 2) - 0.5
    return np.clip(base[None, None, :] * (1 + (n * 0.5 + n2 * 0.7) * strength * 2)[..., None], 0, 1)


def bolt_poly(pts_c, w0, w1):
    """a lightning shard polygon from a zig-zag centre line (list of (x,y)) with width tapering w0 -> w1 -> point"""
    L, R = [], []
    n = len(pts_c) - 1
    for i, (x, y) in enumerate(pts_c):
        if i < n:
            dx, dy = pts_c[i + 1][0] - x, pts_c[i + 1][1] - y
        else:
            dx, dy = x - pts_c[i - 1][0], y - pts_c[i - 1][1]
        L_ = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L_, dx / L_
        w = (w0 + (w1 - w0) * i / n) * (1.0 if i < n else 0.0)
        L.append((x + nx * w / 2, y + ny * w / 2))
        R.append((x - nx * w / 2, y - ny * w / 2))
    return L + R[::-1]


def cost_coin(cv, x, y, cost, r=17.5, seed=0):
    ss = cv.ss
    c = circle(cv, x, y, r + 3.0)
    c = warp(c, 0.4 * ss, 8 * ss, seed)
    cv.paint(blur(shift(c, 1.6 * ss, 2.8 * ss), 1.6 * ss), C_BLK, 0.7)
    cv.paint(blur(c, 0.3 * ss), C_BLK)
    cv.paint(blur(grow(circle(cv, x, y, r + 0.2), 1.5 * ss), 0.3 * ss), C_CUT)
    coin = circle(cv, x, y, r - 0.6)
    X, Y = cv.grid()
    tt = np.clip((Y - (y - r)) / (2 * r), 0, 1)
    cv.paint(blur(coin, 0.3 * ss), lerp(CYAN[None, None, :], hx('2AB4E0')[None, None, :], tt[..., None]))
    cv.paint(ht(cv, np.clip(tt * 1.2 - 0.3, 0, 1), 3.0, 45) * coin, C_RAM, 0.8)
    if NW[0]:
        for q in range(int(cost)):
            xq = x + (q - (int(cost) - 1) / 2) * 6.0
            st_ = stroke_mask(cv, [(xq, y - 8), (xq + 0.5, y + 8)], 2.6, 2.2, wob=0.15, seed=seed + q, taper=(0.05, 0.08))
            cv.paint(blur(st_, 0.3 * ss), C_BLK)
    else:
        tag_text(cv, str(cost), x + 0.2, y + 1.0, 28, ANTON, fill=C_BLK, fill2=C_BLK, ink=C_CUT, rim=C_CUT, drop=C_RAM, drop_off=(0.8, 0.9), outline=0.0, rim_w=0.0, wob=0.0, hi=False, shadow=False)


def loud_tab(cv, lx, ly2, loud, seed=0):
    ss = cv.ss
    box = poly(cv, [(lx - 20, ly2 - 12), (lx + 20, ly2 - 12), (lx + 20, ly2 + 12), (lx - 20, ly2 + 12)])
    box = warp(box, 0.5 * ss, 8 * ss, seed + 80)
    cut(cv, box, hx('A03CFF'), edge=1.6, drop=(1.2, 2.2), op=1.0)
    eye = circle(cv, lx - 9, ly2, 7.2)
    cv.paint(blur(grow(eye, 1.0 * ss), 0.3 * ss), C_BLK)
    e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
    cv.paint(blur(e2, 0.3 * ss), WHITE)
    cv.paint(blur(circle(cv, lx - 9, ly2, 2.9), 0.3 * ss), C_BLK)
    if NW[0]:
        for q in range(int(loud)):
            st_ = stroke_mask(cv, [(lx + 8 + q * 6, ly2 - 7), (lx + 8.5 + q * 6, ly2 + 7)], 2.8, 2.4, wob=0.1, seed=q, taper=(0.05, 0.05))
            cv.paint(blur(st_, 0.3 * ss), WHITE)
    else:
        tag_text(cv, '+' + str(loud), lx + 10.5, ly2 + 0.5, 19, ANTON, fill=WHITE, fill2=WHITE, ink=C_BLK, rim=C_BLK, drop=C_BLK, outline=1.4, rim_w=0, wob=0, hi=False, shadow=False)


def card(name, V='A', seed=0, ss=3):
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    cv = K0.cvc(ss)
    X, Y = cv.grid()
    R = np.random.default_rng(seed)
    A = V == 'A'
    # ---------------------------------------------------------------- the sheet: a scissor-cut card (white for A, black photocopy for B)
    sheet = scissor(cv, [(2, 3), (CW - 2, 1), (CW - 1, CH - 2), (3, CH)], 0.9, seed + 1)
    if A:
        sh_fill = paper_tex(cv, C_CUT * 0.97, seed + 2, 0.045)
        cut(cv, sheet, sh_fill, edge=0.0, drop=(3.0, 5.0), drop_a=0.9)
    else:
        sh_fill = paper_tex(cv, hx('1C1626'), seed + 2, 0.10)
        cut(cv, sheet, sh_fill, edge=1.6, drop=(3.0, 5.0), drop_a=0.9)
        cv.paint(ht(cv, np.clip(0.55 - (Y / CH) * 0.7, 0, 1), 3.2, 45) * sheet, hx('4A3A66'), 0.8)

    # ---------------------------------------------------------------- the art panel
    px0, py0, px1, py1 = 10, 11, CW - 10, 127
    panel = scissor(cv, [(px0, py0 + 1), (px1, py0), (px1 - 1, py1), (px0 + 1, py1 + 1)], 0.8, seed + 3)
    icx, icy = CX + 4, 66
    if A:
        base = np.empty((cv.H, cv.W, 3), np.float32)
        base[:] = C_PUR
        t = np.clip((Y - py0) / (py1 - py0), 0, 1)
        base = lerp(C_PUR[None, None, :], C_PUR_D[None, None, :], t[..., None])
        # magenta sunburst rays from behind the icon
        ang = np.arctan2(Y - icy, X - icx)
        rays = (np.sin(ang * 9 + 0.4) > 0.05).astype(np.float32)
        rr = np.hypot(X - icx, Y - icy)
        base = base * (1 - rays[..., None] * 0.9) + C_MAG[None, None, :] * rays[..., None] * 0.9
        base = base * (1 - (np.clip(1 - rr / 62, 0, 1) * 0.55)[..., None]) + C_MAG_L[None, None, :] * (np.clip(1 - rr / 62, 0, 1) * 0.55)[..., None]
        base = base * (1 - (ht(cv, np.clip((rr - 30) / 70, 0, 1) * 0.8, 4.2, 45) * rays * 0.7)[..., None]) + C_MAG_D[None, None, :] * (ht(cv, np.clip((rr - 30) / 70, 0, 1) * 0.8, 4.2, 45) * rays * 0.7)[..., None]
        base = base * (1 - (ht(cv, np.clip((rr - 20) / 80, 0, 1) * 0.9, 4.2, 15) * (1 - rays) * 0.8)[..., None]) + C_COB[None, None, :] * (ht(cv, np.clip((rr - 20) / 80, 0, 1) * 0.9, 4.2, 15) * (1 - rays) * 0.8)[..., None]
    else:
        t = np.clip((Y - py0) / (py1 - py0), 0, 1)
        base = lerp(C_YEL[None, None, :], hx('FFB000')[None, None, :], t[..., None])
        ang = np.arctan2(Y - icy, X - icx)
        rays = (np.sin(ang * 8 + 0.2) > 0.1).astype(np.float32)
        rr = np.hypot(X - icx, Y - icy)
        base = base * (1 - rays[..., None] * 0.92) + C_COB[None, None, :] * rays[..., None] * 0.92
        hh = ht(cv, np.clip((rr - 24) / 80, 0, 1) * 0.9, 3.8, 45) * rays
        base = base * (1 - hh[..., None] * 0.8) + hx('8EA0FF')[None, None, :] * hh[..., None] * 0.8
        h2 = ht(cv, np.clip((rr - 24) / 90, 0, 1) * 0.8, 4.0, 15) * (1 - rays)
        base = base * (1 - h2[..., None] * 0.65) + C_MAG[None, None, :] * h2[..., None] * 0.65
    cut(cv, panel, base, edge=1.8, drop=(0, 0), edge_col=C_BLK if A else C_CUT)
    # the yellow (A) / magenta (B) lightning shard crossing behind the icon, clipped to the panel
    zz = [(px0 - 4, py1 - 18), (px0 + 40, py1 - 52), (px0 + 52, py1 - 40), (icx + 28, icy - 20), (icx + 36, icy - 30), (px1 + 4, py0 + 8)]
    bolt = poly(cv, bolt_poly(zz, 17.0, 6.0))
    bolt = np.clip(warp(bolt, 0.5 * ss, 14 * ss, seed + 9) * panel, 0, 1)
    bcol = C_YEL if A else C_MAG
    bfill = np.empty((cv.H, cv.W, 3), np.float32)
    bfill[:] = bcol
    bh = ht(cv, np.clip((Y - py0) / (py1 - py0) * 1.1 - 0.1, 0, 1), 3.4, 45)
    bfill = bfill * (1 - bh[..., None] * 0.5) + (C_YEL_D if A else C_MAG_D)[None, None, :] * bh[..., None] * 0.5
    cv.paint(shift(grow(bolt, 1.4 * ss), 1.6 * ss, 2.2 * ss) * panel, C_BLK, 0.85)
    cv.paint(grow(bolt, 1.3 * ss) * panel, C_CUT)
    cv.paint(bolt * panel, bfill)
    # the icon: white card silhouette, ink keyline, misregistered offset plate
    gm = T.glyph_mask(spec['g'], 68, cv, icx, icy - 1)
    gm = warp(gm, 0.35 * ss, 6 * ss, seed + 21)
    plate = shift(grow(gm, 2.0 * ss), 3.0 * ss, 3.4 * ss)
    cv.paint(blur(plate, 0.4 * ss) * panel, C_MAG if not A else C_YEL)
    cv.paint(blur(grow(gm, 2.6 * ss), 0.35 * ss) * panel, C_BLK)
    cv.paint(blur(gm, 0.3 * ss) * panel, WHITE)
    # multiplier
    if spec.get('mult'):
        if NW[0]:
            for q in range(int(spec['mult'])):
                st_ = stroke_mask(cv, [(114 + q * 9, 88), (115 + q * 9, 108)], 4.4, 3.8, wob=0.2, seed=seed + q, taper=(0.05, 0.08))
                cv.paint(blur(grow(st_, 1.5 * ss), 0.3 * ss), C_BLK)
                cv.paint(blur(st_, 0.3 * ss), C_CUT)
        else:
            tag_text(cv, '\u00d7' + spec['mult'], 128, 99, 36, ANTON, fill=C_YEL if A else C_CUT, fill2=C_YEL if A else C_CUT, ink=C_BLK, rim=C_BLK, drop=C_BLK, drop_off=(2.0, 2.6), outline=2.4, rim_w=0.0, skew=0.12, rot=-5, wob=0.2, hi=False, seed=seed)

    # ---------------------------------------------------------------- the title strip (the readable part): black Anton on yellow (A) / white (B), paper cut, tilted
    ty = 143
    tilt = math.radians(-2.2)
    cs, sn = math.cos(tilt), math.sin(tilt)

    def T_(x, y):
        return (CX + (x - CX) * cs - (y - ty) * sn, ty + (x - CX) * sn + (y - ty) * cs)
    strip = scissor(cv, [T_(9, ty - 17), T_(CX + 72, ty - 16), T_(CX + 71, ty + 17), T_(10, ty + 16)], 0.9, seed + 12)
    cut(cv, strip, paper_tex(cv, C_YEL if A else C_CUT, seed + 13, 0.03), edge=1.0, drop=(2.0, 3.0), edge_col=C_BLK)
    if NW[0]:
        bar = stroke_mask(cv, [(30, 142), (CX, 139), (CW - 30, 143)], 15, 12, wob=0.5, seed=seed + 4, taper=(0.04, 0.05))
        cv.paint(blur(bar, 0.4 * ss), C_BLK)
    else:
        ft_ = font(ANTON, 44 * ss)
        wt_ = ft_.getlength(spec['nm']) / ss + 0.8 * len(spec['nm'])
        pxt_ = 40 if wt_ <= 126 else 40 * 126 / wt_
        mt = text_mask(cv, spec['nm'], CX - 1, ty + 1, ANTON, pxt_, 'mm', 0.14, -2.2, 1.0, 0.25, seed)
        cv.paint(blur(shift(mt, 2.0 * ss, 2.2 * ss), 0.3 * ss), C_MAG if A else C_COB)
        cv.paint(blur(mt, 0.3 * ss), C_BLK)

    # ---------------------------------------------------------------- type band: a cut black strip, white letters (A) / cobalt strip (B)
    by = 177
    tw_ = 76 if spec['fam'] == 'TOWER' else 66
    band = scissor(cv, [(CX - tw_ / 2 - 2, by - 10), (CX + tw_ / 2 + 1, by - 11), (CX + tw_ / 2 + 3, by + 10), (CX - tw_ / 2, by + 11)], 0.6, seed + 14)
    cut(cv, band, C_BLK if A else C_COB, edge=1.2, drop=(1.4, 2.2), edge_col=C_CUT if A else C_BLK)
    if not NW[0]:
        tag_text(cv, spec['fam'], CX + 0.5, by + 0.5, 17, ANTON, fill=C_CUT, fill2=C_CUT, ink=C_BLK, rim=C_BLK, drop=C_BLK, outline=0.0, rim_w=0.0, track=1.8, wob=0.1, hi=False, shadow=False, rot=1.0)

    # ---------------------------------------------------------------- rules text on a newsprint scrap (black marker): big, high contrast
    ly = 214
    scr = scissor(cv, [(12, ly - 22), (CX + 74, ly - 24), (CX + 73, ly + 25), (13, ly + 24)], 0.9, seed + 15)
    cut(cv, scr, paper_tex(cv, C_NEWS if A else hx('EDE8D8'), seed + 16, 0.05), edge=0.0 if A else 0.0, drop=(1.6, 2.6) if A else (0, 0), drop_a=0.7)
    cv.paint(ht(cv, np.clip(((Y - (ly - 24)) / 50) * 0.5, 0, 1) * np.clip(((X - 40) / 110), 0, 1), 3.6, 45) * scr, C_NEWS_D, 0.55)
    txt = spec['txt']
    px = 22
    f = font(MARKER, px * ss)
    while f.getlength(txt) / ss > CW - 58 and px > 14:
        px -= 1
        f = font(MARKER, px * ss)
    if NW[0]:
        for q, wq in enumerate((0.7, 0.45)):
            st_ = stroke_mask(cv, [(CX - wq * 70, ly - 8 + q * 15), (CX + wq * 70, ly - 8 + q * 15 + 0.8)], 4.0, 3.4, wob=0.3, seed=seed + q, taper=(0.05, 0.05))
            cv.paint(blur(st_, 0.3 * ss), C_BLK, 0.9)
    else:
        m = text_mask(cv, txt, CX + 0.5, ly - 2, MARKER, px, 'mm', 0.0, -0.8, 0.0, 0.2, seed + 32)
        cv.paint(blur(m, 0.3 * ss), C_BLK)
    wtxt = f.getlength(txt) / ss
    ul = stroke_mask(cv, [(CX - wtxt / 2 - 3, ly + 14.2), (CX - wtxt / 4, ly + 15.6), (CX + wtxt / 4, ly + 14.0), (CX + wtxt / 2 + 4, ly + 15.0)], 2.4, 1.4, wob=0.5, seed=seed + 36, taper=(0.1, 0.25))
    cv.paint(blur(ul, 0.3 * ss), C_MAG if A else C_COB, 0.95)
    if spec.get('num') and not NW[0]:
        x1_ = CX + wtxt / 2
        pk = stroke_mask(cv, [(x1_ - 14, ly + 12), (x1_ - 7, ly + 15.0), (x1_ + 2, ly + 12.2)], 3.6, 2.2, wob=0.3, seed=seed + 33, taper=(0.1, 0.3))
        cv.paint(blur(pk, 0.3 * ss), C_YEL, 0.95)

    # ---------------------------------------------------------------- cost coin (RAM cyan) and the Trace tab
    cost_coin(cv, 20, 21, cost, 17.0, seed + 70)
    if loud:
        loud_tab(cv, CW - 54, 19, loud, seed)

    # ---------------------------------------------------------------- collage bits on the sheet edge: a tape strip across the top, a small star sticker
    tp = scissor(cv, [(CX - 4, 2), (CX + 24, 0), (CX + 26, 11), (CX - 2, 12)], 0.4, seed + 18)
    cv.paint(blur(shift(tp, 1.0 * ss, 1.8 * ss), 1.0 * ss), C_BLK, 0.35)
    cv.paint(tp, C_YEL if not A else hx('FFDD33'), 0.88)
    star = []
    for q in range(10):
        rad = 8.0 if q % 2 == 0 else 3.4
        a = math.pi / 5 * q - math.pi / 2
        star.append((CW - 28 + rad * math.cos(a), CH - 18 + rad * math.sin(a)))
    sm = poly(cv, star)
    cv.paint(blur(grow(sm, 1.4 * ss), 0.3 * ss), C_BLK)
    cv.paint(blur(sm, 0.3 * ss), C_MAG if A else C_YEL)
    return cv


def render_card(name, V='A', seed=0, ss=4, scale=2):
    return card(name, V, seed, ss).to_image(scale=scale)


if __name__ == '__main__':
    import sys, time, asm_r2
    asm_r2.setup()
    t = time.time()
    names = ['Brace', 'Spin3', 'Trigger', 'Twist']
    for V in ('A', 'B'):
        ims = [render_card(n, V, seed=i * 3 + 1, ss=3, scale=1) for i, n in enumerate(names)]
        sheet = Image.new('RGBA', (ims[0].width * 4 + 40, ims[0].height + 20), (40, 36, 52, 255))
        for i, im in enumerate(ims):
            sheet.alpha_composite(im, (10 + i * (im.width + 6), 10))
        sheet.save('D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/work/_cards_%s.png' % V)
        print(V, round(time.time() - t, 1))
