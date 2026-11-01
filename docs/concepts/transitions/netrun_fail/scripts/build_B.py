"""Design B: the run's node route as a grease-pencil map; the failed node is struck."""
from nf_lib import *
sys.path.insert(0, ROOT + 'cohesion/supporting_r42/scripts')
import r42lib as R42

NODES = {  # id: (x, y, kind)
    '1a': (140, 840, 'F'), '1b': (140, 690, 'F'), '1c': (140, 540, 'F'),
    '2a': (330, 770, 'F'), '2b': (330, 620, 'T'), '2c': (330, 470, 'F'),
    '3a': (520, 850, 'M'), '3b': (520, 700, 'F'), '3c': (520, 550, 'E'), '3d': (520, 400, 'F'),
    '4a': (710, 760, 'T'), '4b': (710, 600, 'M'), '4c': (710, 440, 'R'),
    '5a': (900, 640, 'E'), '5b': (900, 500, 'F'), '5c': (900, 340, 'T'),
    '6a': (1090, 560, 'F'), '6b': (1090, 400, 'E'),
    '7a': (1250, 470, 'R'),
}
EDGES = ['1a-2a', '1b-2a', '1b-2b', '1c-2c', '2a-3a', '2a-3b', '2b-3b', '2b-3c', '2c-3d', '3a-4a', '3b-4a', '3b-4b',
         '3c-4b', '3d-4c', '4a-5a', '4b-5a', '4b-5b', '4c-5c', '5a-6a', '5b-6a', '5b-6b', '5c-6b', '6a-7a', '6b-7a']
WALK = ['1a', '2a', '3b', '4a', '5a']
WTAG = {'1a': 'ROUTER 1', '2a': 'ROUTER 2', '3b': 'ROUTER 3', '4a': 'TERMINAL 4'}


def path(a, b):
    (x0, y0, _), (x1, y1, _) = NODES[a], NODES[b]
    k = (x1 - x0) * .34
    return [(x0, y0), (x0 + k, y0), (x1 - k, y1), (x1, y1)]


def dashed(img, pts, col, width, on=16, off=12):
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        seg = math.hypot(bx - ax, by - ay)
        t = 0
        while t < seg:
            e = min(t + on, seg)
            out.append([ax + (bx - ax) * t / seg, ay + (by - ay) * t / seg, ax + (bx - ax) * e / seg, ay + (by - ay) * e / seg])
            t += on + off
    for s in out:
        line(img, s, col, width)


def backdrop():
    im = R42.backdrop('plan_r42.png')
    m = R42.soft_rect((60, 120, 1300, 1000), 80)
    g = R42.grade(im, m, None, 'strong')
    a = to_f(g.convert('RGB'))
    a = grade(a, 0.80, 0.55, (0.92, 0.98, 1.08))
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)), np.float32) / 255
    # extra dim under the map so the lines lead, soft, and under the right panel
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = a * (0.80 + 0.20 * np.exp(-(((xx - 700) / 650) ** 2 + ((yy - 580) / 420) ** 2)))[..., None]
    a = vignette_f(a, 0.5, 0.55)
    a = pink_edge(a, 0.45)
    return a


def build():
    ph = PHR()
    bgf = backdrop()
    bg_only = to_img(bgf)
    img = up2(bg_only)

    # --------------- links
    glowL = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for e in EDGES:
        a, b = e.split('-')
        pts = path(a, b)
        flat = [c for p in pts for c in p]
        walked = a in WALK and b in WALK
        line(img, flat, A(INK, 175), 12 if walked else 9)
        if walked:
            line(glowL, flat, A(LIME, 255), 8)
    img = glow(img, glowL, 8, 0.8)
    for e in EDGES:
        a, b = e.split('-')
        pts = path(a, b)
        if a in WALK and b in WALK:
            flat = [c for p in pts for c in p]
            line(img, flat, LIME, 7)
        else:
            dashed(img, pts, A(MID, 150), 4)
    # the route beyond the loss: the dashed link out of the struck node is cut
    cx, cy = (NODES['5a'][0] + 62, NODES['5a'][1] - 14)
    V2.grease(img, [(cx - 14, cy + 22), (cx + 14, cy - 22)], col=PRED, width=7, seed=11)

    # --------------- nodes
    for k, (x, y, kind) in NODES.items():
        if k in WALK and k != '5a':
            node_icon(img, x, y, kind, LIME)
            ellipse(img, [x + 14, y - 44, x + 40, y - 18], fill=LIME, outline=INK, width=2)
            line(img, [x + 20, y - 31, x + 25, y - 25, x + 35, y - 38], INK, 3.5)
            if k in WTAG:
                text(img, (x, y + 50), WTAG[k], font('mono', 18), HI, 'ma', stroke=3, stroke_fill=INK)
        elif k == '5a':
            node_icon(img, x, y, kind, HARM, r=34)
        else:
            col = {'E': (255, 140, 26, 255)}.get(kind, MID)
            node_icon(img, x, y, kind, A(col, 120), dim=0.6, fillc=(8, 14, 28, 200))
    text(img, (NODES['7a'][0], NODES['7a'][1] + 52), 'RACK', font('mono', 18), A(MID, 200), 'ma', stroke=3, stroke_fill=INK)

    # --------------- the fall: struck node, fallen token, pencil
    fx, fy, _ = NODES['5a']
    V2.grease_circle(img, fx, fy, 56, col=PRED, width=7, seed=3)
    V2.grease(img, [(fx - 40, fy - 40), (fx + 40, fy + 40)], col=PRED, width=11, seed=1)
    V2.grease(img, [(fx + 42, fy - 38), (fx - 40, fy + 42)], col=PRED, width=11, seed=6)
    # operative token lying on its side next to the node (route-page pink sword token, greyed)
    tx, ty = fx + 84, fy + 72
    ellipse(img, [tx - 24, ty - 24, tx + 24, ty + 24], fill=A(INK, 240), outline=A(MID, 200), width=3)
    sword_glyph(img, tx, ty, 17, A(LO, 255), rot=-100)
    text(img, (fx - 14, fy + 62), 'ELITE 5', font('mono', 19), HARM, 'ma', stroke=3, stroke_fill=INK)
    ph.add([fx - 66, fy + 56, fx + 38, fy + 88], 1)
    hand(img, (fx + 150, fy + 190), 'LOST HERE', 62, PRED, rot=-5)
    V2.grease(img, [(fx + 70, fy + 156), (fx + 56, fy + 126), (fx + 40, fy + 104)], col=PRED, width=7, seed=8)
    poly(img, [(fx + 30, fy + 90), (fx + 30, fy + 114), (fx + 52, fy + 106)], fill=PRED)

    # --------------- top HUD (r42 route-page chips with the loss written onto them)
    x0, y0, x1, y1 = 78, 28, 1010, 98
    rrect(img, [x0, y0, x1, y1], 8, fill=TBG, outline=A(CYAN, 130), width=2)
    for (cx_, cy_, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        line(img, [cx_ + sx * 20, cy_, cx_, cy_, cx_, cy_ + sy * 20], CYAN, 3.5)
    text(img, (x0 + 22, y0 + 8), 'HEAT', font('mono', 16), AMBER)
    text(img, (x0 + 22, y0 + 24), '63', font('anton', 40), AMBER)
    text(img, (x0 + 84, y0 + 10), 'FLAGGED', font('mono', 20), AMBER)
    heat_meter(img, x0 + 84, y0 + 38, 250, 16, 52, 63)
    chip(img, x0 + 352, y0 + 18, '+11', PINK, size=22, h=34)
    ph.add([x0 + 14, y0 + 6, x0 + 410, y1 - 6], 4)
    line(img, [x0 + 430, y0 + 12, x0 + 430, y1 - 12], A(CYAN, 80), 1.5)
    text(img, (x0 + 450, y0 + 8), 'HP', font('mono', 16), LO)
    ellipse(img, [x0 + 450, y0 + 34, x0 + 466, y0 + 50], fill=HARM)
    text(img, (x0 + 478, y0 + 22), '0', font('anton', 40), HARM)
    text(img, (x0 + 504, y0 + 32), '/60', font('mono', 20), LO)
    line(img, [x0 + 580, y0 + 12, x0 + 580, y1 - 12], A(CYAN, 80), 1.5)
    text(img, (x0 + 600, y0 + 8), 'CYCLES', font('mono', 16), LO)
    text(img, (x0 + 600, y0 + 22), '160', font('anton', 40), A(LO, 255))
    line(img, [x0 + 590, y0 + 58, x0 + 700, y0 + 28], PRED, 5)
    text(img, (x0 + 722, y0 + 22), '0', font('anton', 40), HARM)
    ph.add([x0 + 592, y0 + 6, x0 + 760, y1 - 6], 3)
    text(img, (x1 - 22, y0 + 24), 'NETRUN', font('mono', 20), LO, 'ra')

    # --------------- run ledger panel
    px0, py0, px1, py1 = 1350, 120, 1850, 870
    term_panel(img, [px0, py0, px1, py1], edge=PINK, title='> RUN SUMMARY', tag='SEED VAULT')
    split_text(img, (px0 + 28, py0 + 62), 'NETRUN LOST', font('anton', 72), HI, px=3, stroke=4)
    y = py0 + 158
    text(img, (px0 + 30, y), 'CELL-9 // BREAKER  R1', font('anton', 30), HI)
    ph.add([px0 + 240, y + 2, px0 + 330, y + 38], 9)
    chip(img, px0 + 308, y - 2, 'FLATLINED', HARM, size=22, h=34)
    y += 46
    text(img, (px0 + 30, y + 4), 'REACHED', font('mono', 21), LO)
    text(img, (px0 + 170, y), 'NODE 5 OF 7', font('anton', 28), HI)
    ph.add([px0 + 160, y - 2, px0 + 380, y + 36], 1)
    y += 38
    text(img, (px0 + 30, y + 4), 'LAST FIGHT', font('mono', 21), LO)
    text(img, (px0 + 170, y), 'THE ADJUSTER · T2', font('anton', 28), HI)
    ph.add([px0 + 160, y - 2, px0 + 440, y + 36], 2)
    y += 52

    def head(s, col):
        nonlocal y
        text(img, (px0 + 30, y), s, font('mono', 21), col)
        line(img, [px0 + 30 + tw(s, font('mono', 21)) + 14, y + 13, px1 - 28, y + 13], A(col, 80), 1.5)
        y += 40
    head('> LOST WITH CELL-9', HARM)
    y3 = y
    for (l, v) in FACTS['lost']:
        text(img, (px0 + 30, y + 5), l, font('mono', 21), LO)
        chip(img, px0 + 190, y, '−' + v, HARM, size=24, h=34)
        y += 41
    ph.add([px0 + 22, y3 - 4, px1 - 26, y - 4], 3)
    y += 4
    head('> KEPT', GAIN)
    text(img, (px0 + 30, y + 5), 'BANKED', font('mono', 21), LO)
    chip(img, px0 + 190, y, 'SCHEMATICS + ARMORY', GAIN, size=22, h=34)
    ph.add([px0 + 182, y - 4, px1 - 26, y + 38], 9)
    y += 41
    text(img, (px0 + 30, y + 5), 'HOME SERVER', font('mono', 21), LO)
    chip(img, px0 + 190, y, '50/50  HOLDS', GAIN, size=22, h=34)
    ph.add([px0 + 182, y - 4, px0 + 372, y + 38], 6)
    y += 41
    text(img, (px0 + 30, y + 5), 'CREW', font('mono', 21), LO)
    text(img, (px0 + 190, y), '4 → 3', font('anton', 29), HI)
    ph.add([px0 + 182, y - 4, px0 + 300, y + 38], 5)

    # --------------- DISPATCH line and exit
    bx0, by0, bx1, by1 = 78, 960, 1290, 1020
    rrect(img, [bx0, by0, bx1, by1], 8, fill=TBG, outline=A(CYAN, 130), width=2)
    for (cx_, cy_, sx, sy) in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
        line(img, [cx_ + sx * 18, cy_, cx_, cy_, cx_, cy_ + sy * 18], CYAN, 3.5)
    text(img, (bx0 + 22, by0 + 16), '> DISPATCH', font('mono', 22), CYAN)
    text(img, (bx0 + 190, by0 + 16), 'signal lost at node 5. nothing unbanked came back. the cell holds.', font('mono', 23), HI)
    ph.add([bx0 + 180, by0 + 8, bx1 - 14, by1 - 8], 7)
    sticker(img, 'GRID VIEW', 1600, 975, 270, 58, PINK, None, rot=-1.5, size=38)
    text(img, (1770, 965), '[G]', font('mono', 22), LO)
    ph.add([1458, 941, 1750, 1011], 8)

    full = down(grain(img, 3, 1))
    return bg_only, full, ph.items
