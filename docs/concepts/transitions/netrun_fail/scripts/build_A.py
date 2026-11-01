"""Design A: the CRT feed of the netrun street cuts to signal loss; DISPATCH speaks on a clean line."""
from nf_lib import *


def backdrop():
    a = to_f(street_img(1.0))
    a = grade(a, 0.66, 0.42, (0.88, 0.98, 1.12))
    a = bands_f(a, [(150, 70, 26, .10), (330, 26, -40, .22), (720, 14, 30, .15), (1010, 70, -22, .25)], seed=4)
    # rolling tracking bar, soft
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    bar = np.exp(-((yy - 520) / 62.0) ** 2) * 0.10
    a = a + bar
    a = chroma_f(a, 3)
    a = static_f(a, 0.028, seed=7)
    a = vignette_f(a, 0.55, 0.5)
    a = pink_edge(a, 0.28)
    return a


def build():
    ph = PHR()
    bgf = backdrop()
    bg_only = to_img(scan_f(bgf, 0.10))
    img = up2(to_img(bgf))

    # ---- top feed bar
    x0, y0, x1, y1 = 78, 40, 1150, 94
    rrect(img, [x0, y0, x1, y1], 8, fill=TBG, outline=A(PINK, 150), width=2)
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        line(img, [cx + sx * 22, cy, cx, cy, cx, cy + sy * 22], PINK, 3.5)
    text(img, (x0 + 22, 54), '> FEED  //  NETRUN: SEED VAULT EXCHANGE  //  ELITE ROUTER 5 OF 7', font('mono', 24), PINK)
    ph.add([x0 + 505, 48, x1 - 14, 86], 1)
    text(img, (x1 - 22, 55), 'NO SIGNAL', font('mono', 20), LO, 'ra')

    # ---- the headline
    f = font('anton', 170)
    Lg = Image.new('RGBA', img.size, (0, 0, 0, 0))
    text(Lg, (92, 140), 'SIGNAL', f, A(PINK, 255))
    text(Lg, (92, 320), 'LOST', f, A(PINK, 255))
    img = glow(img, Lg, 26, 0.55)
    split_text(img, (92, 140), 'SIGNAL', f, HI, px=6, stroke=7)
    split_text(img, (92, 320), 'LOST', f, HI, px=6, stroke=7)
    # a torn static slice through the headline, as if the feed is still tearing
    sl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    rect(sl, [60, 330, 700, 342], fill=A(HI, 70))
    rect(sl, [120, 400, 780, 407], fill=A(PINK, 90))
    img.alpha_composite(sl)
    text(img, (96, 560), 'the operative flatlined. the run is over.', font('mono', 28), MID)

    # ---- portrait tile (bible: flatlined = greyed, static, NO SIGNAL, red pencil X, flatline)
    tx0, ty0, tx1, ty1 = 96, 640, 396, 1000
    rrect(img, [tx0, ty0, tx1, ty1], 10, fill=A(INK, 245), outline=A(MID, 130), width=2)
    bust = breaker_bust(280, 290)
    b = np.asarray(bust.convert('RGB'), np.float32) / 255
    b = grade(b, 0.55, 0.0)
    b = bands_f(b, [(40 * K, 10 * K, 18 * K, .3), (150 * K, 6 * K, -26 * K, .4), (230 * K, 20 * K, 22 * K, .25)], seed=9)
    b = static_f(b, 0.09, seed=3)
    b = scan_f(b, 0.28, 4)
    img.alpha_composite(to_img(b).convert('RGBA'), (S(tx0 + 10), S(ty0 + 44)))
    # flatline across the lower fifth
    pts = [tx0 + 14, ty0 + 300]
    for i in range(1, 23):
        pts += [tx0 + 14 + i * 12.2, ty0 + 300 + (0 if i not in (4, 5, 6) else (-26 if i == 5 else (14 if i == 6 else -8)))]
    line(img, pts, A(INK, 255), 7)
    line(img, pts, (205, 214, 224, 255), 3)
    ellipse(img, [tx0 + 14, ty0 + 17, tx0 + 28, ty0 + 31], fill=LO); text(img, (tx0 + 36, ty0 + 12), 'CELL-9 // BREAKER', font('mono', 20), HI)
    text(img, (tx1 - 14, ty0 + 14), 'R1', font('mono', 18), LO, 'ra')
    ph.add([tx1 - 52, ty0 + 8, tx1 - 8, ty0 + 36], 9)
    V2.grease(img, [(tx0 + 34, ty0 + 70), (tx1 - 30, ty0 + 290)], col=PRED, width=11, seed=2)
    V2.grease(img, [(tx1 - 36, ty0 + 66), (tx0 + 30, ty0 + 286)], col=PRED, width=11, seed=5)
    stamp(img, 'FLATLINED', tx0 + 150, ty0 + 232, (255, 68, 51, 255), rot=-9, size=40)

    # ---- DISPATCH (clean system text, never zine-styled: GDD 8.2)
    dx0, dy0, dx1, dy1 = 440, 690, 1140, 1000
    term_panel(img, [dx0, dy0, dx1, dy1], edge=CYAN, title='> DISPATCH', tag='SYSTEM', tag_col=LO)
    fm = font('mono', 27)
    lines = ['signal lost at node 5. CELL-9 is gone,', 'and so is everything they carried that', 'was not banked. the cell holds.', '', 'pick who goes next.']
    for i, s in enumerate(lines):
        text(img, (dx0 + 28, dy0 + 70 + i * 42), s, fm, HI)
    rect(img, [dx0 + 28 + tw('pick who goes next.', fm) + 6, dy0 + 70 + 4 * 42 + 4, dx0 + 28 + tw('pick who goes next.', fm) + 22, dy0 + 70 + 4 * 42 + 28], fill=CYAN)
    ph.add([dx0 + 20, dy0 + 62, dx1 - 20, dy0 + 70 + 5 * 42], 7)

    # ---- run log panel
    px0, py0, px1, py1 = 1200, 120, 1850, 900
    term_panel(img, [px0, py0, px1, py1], edge=PINK, title='> RUN LOG  //  SEED VAULT EXCHANGE', tag='NETRUN')
    lab = font('mono', 21)
    val = font('anton', 29)
    xl, xv = px0 + 26, px0 + 232
    y = py0 + 66

    def row(l, v, col=HI):
        nonlocal y
        text(img, (xl, y + 5), l, lab, LO)
        text(img, (xv, y), v, val, col)
        y += 41

    def head(s, col):
        nonlocal y
        y += 8
        text(img, (xl, y), s, font('mono', 21), col)
        line(img, [xl + tw(s, font('mono', 21)) + 14, y + 13, px1 - 26, y + 13], A(col, 80), 1.5)
        y += 40

    row('OPERATIVE', 'CELL-9 // BREAKER  R1')
    row('STATUS', 'FLATLINED', HARM)
    chip(img, xv + 190, y - 41 + 2, 'HP 0/60', HARM, size=22, h=34)
    row('REACHED', 'ELITE ROUTER 5 OF 7')
    ph.add([xv - 6, y - 41 - 2, px1 - 24, y - 4], 1)
    row('LAST FIGHT', 'THE ADJUSTER  ·  TURN 2')
    ph.add([xv - 6, y - 41 - 2, px1 - 24, y - 4], 2)
    head('> LOST WITH CELL-9', HARM)
    y3 = y
    for (l, v) in FACTS['lost']:
        text(img, (xl, y + 5), l, lab, LO)
        chip(img, xv, y, '−' + v, HARM, size=24, h=34)
        y += 41
    ph.add([xl - 8, y3 - 4, px1 - 24, y - 4], 3)
    head('> KEPT', GAIN)
    text(img, (xl, y + 5), 'BANKED', lab, LO)
    chip(img, xv, y, 'SCHEMATICS + ARMORY', GAIN, size=22, h=34)
    ph.add([xv - 6, y - 4, px1 - 24, y + 38], 9)
    y += 41
    text(img, (xl, y + 5), 'HOME SERVER', lab, LO)
    chip(img, xv, y, '50/50  HOLDS', GAIN, size=22, h=34)
    ph.add([xv - 6, y - 4, xv + 190, y + 38], 6)
    y += 41
    head('> CAMPAIGN', AMBER)
    text(img, (xl, y + 5), 'HEAT', lab, AMBER)
    heat_meter(img, xv, y + 6, 220, 20, 52, 63)
    text(img, (xv + 242, y), '52→63', font('anton', 29), HI)
    chip(img, xv + 340, y, '+11', PINK, size=22, h=34)
    ph.add([xl - 8, y - 4, px1 - 24, y + 40], 4)
    y += 41
    text(img, (xl, y + 5), 'CREW', lab, LO)
    text(img, (xv, y), '4 → 3', val, HI)
    ph.add([xv - 6, y - 4, xv + 120, y + 38], 5)

    # ---- exit
    sticker(img, 'GRID VIEW', 1560, 1010, 270, 58, PINK, None, rot=-1.5, size=38)
    text(img, (1730, 1000), '[G]', font('mono', 22), LO)
    ph.add([1418, 976, 1710, 1046], 8)

    full = down(grain(img, 3, 1))
    full = to_img(scan_f(to_f(full), 0.10))
    return bg_only, full, ph.items
