"""Hover (p2b) pieces: cell outline, path, slice highlight, trim, tag. Options A/B/C; 'cur' = E10."""
import sys, math, random
sys.dont_write_bytecode = True
from a_kit import *
from a_plan import wax_v
import build10 as B10

J = B10.J


def hv_unit(f):
    return [u for u in f['units'] if u['id'] == J['hover']['id']][0]


def brackets(L, pts_pairs, col=LIME, w=5.5):
    for pts in pts_pairs:
        L.line(list(pts), INK, w + 4.5)
    for pts in pts_pairs:
        L.line(list(pts), col, w)


def band_brackets(L, ri, ro, a0, a1, arm=24, col=LIME, w=5.5):
    out = []
    for r_edge, rs in ((ri, 1), (ro, -1)):
        for ang, sg in ((a0, 1), (a1, -1)):
            da = arm / r_edge * 57.3
            corner = ppx(C, r_edge, ang)
            along = [ppx(C, r_edge, ang + sg * da * k / 4) for k in range(5)]
            rad = ppx(C, r_edge + rs * arm, ang)
            out.append(along[::-1] + [corner, rad])
    brackets(L, out, col, w)


def cell_outline(L, f, opt):
    u = hv_unit(f)
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    if opt == 'A':          # lime corner brackets (2.10)
        band_brackets(L, ri + 4, ro - 4, a0 + 3, a1 - 3, 26)
    elif opt == 'B':        # one plan-yellow outline, solid 4 px (path and outline are one pencil hand)
        pts = L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3)
        L.line(pts + [pts[0]], INK, 8.5)
        L.line(pts + [pts[0]], YEL, 4)
    else:                   # white inner hairline + lime ticks at the edge midpoints and the two ends
        pts = L.band(C, ri + 6, ro - 6, a0 + 4, a1 - 4)
        L.line(pts + [pts[0]], (255, 255, 255, 190), 1.6)
        am = (a0 + a1) / 2
        ticks = []
        for r_, dr in ((ri + 4, 1), (ro - 4, -1)):
            ticks.append([ppx(C, r_, am), ppx(C, r_, am), ppx(C, r_ + dr * 16, am)])
        rm = (ri + ro) / 2
        for a_, sg in ((a0 + 3, 1), (a1 - 3, -1)):
            ticks.append([ppx(C, rm, a_), ppx(C, rm, a_), ppx(C, rm, a_ + sg * 16 / rm * 57.3)])
        brackets(L, ticks, LIME, 5)


def path_pts(f):
    path = J['hover']['path']
    pts = []
    for i in range(len(path) - 1):
        (d0, s0), (d1, s1) = path[i], path[i + 1]
        r0, r1 = rmid(d0), rmid(d1)
        a0, a1 = 60 * s0, 60 * s1
        if a1 < a0:
            a1 += 360
        for j in range(0 if i == 0 else 1, 21):
            t = j / 20
            pts.append(ppx(C, r0 + (r1 - r0) * t, a0 + (a1 - a0) * t))
    return pts


def hover_path(L, f, opt):
    pts = path_pts(f)
    tip = pts[-1]
    d_ = math.atan2(tip[1] - pts[-4][1], tip[0] - pts[-4][0])
    if opt == 'A':          # continuous wax, open hand-drawn arrowhead, start dot on the cell
        wax(L, pts, YEL, 7, 11, 0.8)
        wax_v(L, tip, d_, 19, YEL, 12, 7)
        x, y = pts[0]
        L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(6, 3, 8, 235))
        L.ellipse([x - 4.2, y - 4.2, x + 4.2, y + 4.2], fill=YEL)
    elif opt == 'B':        # stippled: a tapped dot per 13 px, one open arrow
        dots = []
        acc = 0
        last = pts[0]
        rnd = random.Random(4)
        for p in pts[1:]:
            acc += math.hypot(p[0] - last[0], p[1] - last[1])
            last = p
            if acc >= 13:
                acc = 0
                dots.append((p[0] + rnd.uniform(-1, 1), p[1] + rnd.uniform(-1, 1)))
        for x, y in dots:
            L.ellipse([x - 6.4, y - 6.4, x + 6.4, y + 6.4], fill=(6, 3, 8, 235))
        for x, y in dots:
            L.ellipse([x - 4.2, y - 4.2, x + 4.2, y + 4.2], fill=YEL)
        wax_v(L, tip, d_, 20, YEL, 13, 6.5)
    else:                   # soft wide highlighter wax underneath + one sharp pencil line, hooked tip
        sub = L2()
        wax(sub, pts, YEL, 17, 14, 0.5, ink=False, grain=1.4)
        sub.im.putalpha(sub.im.split()[3].point(lambda v: int(v * 0.34)))
        L.im.alpha_composite(sub.im)
        wax(L, pts, YEL, 4.4, 15, 0.9)
        for sg in (-0.7, 0.7):
            hook = [tip, (tip[0] - 15 * math.cos(d_ + sg), tip[1] - 15 * math.sin(d_ + sg))]
            wax(L, hook, YEL, 4.4, 16, 0.2)


def hover_sectors(f):
    return [h[0] for h in J['hover']['fate']['hits']]


def trim_hover(L, f, skip_hover):
    """threat_trim for every unit; the hovered unit's own trims are skipped when the hover highlight replaces them"""
    seen = set()
    hid = J['hover']['id']
    for u in f['units']:
        fz = u['fate']
        if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
            continue
        if skip_hover and u['id'] == hid:
            continue
        for (sec, sl, hit, tohp) in fz['hits']:
            seen.add((sec, fz['k']))
    for (sec, k) in sorted(seen):
        if k == 0:
            L.line(L.arc_pts(C, RS['s1'] - 1, 60 * sec - 25, 60 * sec + 25), RED, 5.5)
        elif k == 1:
            L.line(L.arc_pts(C, RS['s1'] + 3, 60 * sec - 25, 60 * sec + 25), PALE, 3, dash=(8, 5))
        else:
            L.line(L.arc_pts(C, RS['s1'] + 7, 60 * sec - 25, 60 * sec + 25), (236, 240, 255), 2.4, dash=(4, 6))


def hover_slice(L, f, opt):
    for sec in hover_sectors(f):
        a0, a1 = 60 * sec - 25, 60 * sec + 25
        if opt == 'A':      # yellow rim arc in the trim slot
            L.line(L.arc_pts(C, RS['s1'] - 1, a0, a1), INK, 10)
            L.line(L.arc_pts(C, RS['s1'] - 1, a0, a1), YEL, 5.5)
        elif opt == 'B':    # pencil end ticks across the rim, no new arc
            for a in (a0 - 1, a1 + 1):
                wax(L, [ppx(C, RS['s1'] - 16, a), ppx(C, RS['s1'] + 12, a)], YEL, 5, 21 + sec, 0.3)
        else:               # wedge outline in wax, 3.4 px
            pts = L.band(C, RS['s0'] + 3, RS['s1'] - 2, 60 * sec - 28, 60 * sec + 28)
            wax(L, pts + [pts[0]], YEL, 3.4, 31 + sec, 0.4)


# ----------------------------------------------------------------------------- hover tag
def rtext(L, xy, s, px, col=WHITE, bold=True, anchor='lm'):
    f = BB.plex(int(px * L.k), bold)
    L.d.text((xy[0] * L.k, xy[1] * L.k), s, font=f, fill=tuple(col) + (255,), anchor=anchor)
    return f.getlength(s) / L.k


def rw(L, s, px=20, bold=True):
    return BB.plex(int(px * L.k), bold).getlength(s) / L.k


def tag_texts():
    hv = J['hover']
    fz = hv['fate']
    sl = [('%s %d' % (h[1], h[3])) for h in fz['hits']]
    head = '%s%s x%d' % (hv['kind'].upper(), ' ARMOR' if hv['df'] == 'armor' else '', hv['w'])
    hp = 'HP %d/%d' % (hv['hp'], hv['mx'])
    hit = 'hit %d now (+%d grown)' % (hv['hit'], hv['grown'])
    land = 'lands in %d: %d per slice' % (fz['k'], fz['hits'][0][2])
    cost = 'after our guns it costs you %d HP:' % sum(h[3] for h in fz['hits'])
    return head, hp, hit, land, cost, sl


def hover_tag(L, f, opt):
    head, hp, hit, land, cost, sl = tag_texts()
    sls = ' + '.join(sl)
    u = hv_unit(f)
    ri, ro = CB.ring_geom(u['dep'])
    LH = 26
    wmax = lambda ls: max(sum(rw(L, s, 20, b) for s, b in ln) for ln in ls)
    if opt == 'A':          # one block, 4 lines <= 41 chars, bottom-left, leader to the cell
        lines = [[(head + '  ' + hp, True), ('  ' + hit, False)], [(land, False)], [(cost, False)], [(sls, True)]]
        w = wmax(lines) + 32
        h = LH * 4 + 18
        x0, y0 = 18, 872
        anc = ppx(C, ro - 6, 233)
        st = (x0 + 190, y0)
        pl = [st, (st[0], (st[1] + anc[1]) / 2 + 20), anc]
        L.line(pl, INK, 6.5)
        L.line(pl, YEL, 2.6)
        L.ellipse([anc[0] - 6, anc[1] - 6, anc[0] + 6, anc[1] + 6], fill=YEL, outline=INK, w=2.4)
        cols = [lines]
    elif opt == 'B':        # datasheet under the cell: header band + 3 rows, notch pointing at the cell
        rows = [[(hit, False), ('   ' + land, False)], [(cost, False)], [(sls, True)]]
        w = max(wmax(rows), rw(L, head + '   ' + hp)) + 32
        h = 34 + LH * 3 + 14
        cx = C[0]
        x0, y0 = cx - w / 2, 920
        tip = (cx, C[1] + ro + 2)
        L.poly([(cx - 14, y0 + 4), tip, (cx + 14, y0 + 4)], fill=(5, 13, 28, 250), outline=YEL, w=2.4)
        cols = None
    else:                   # two columns in the right gutter, leader from the cell's right end
        colA = [[(head, True)], [(hp, True)], [(hit, False)], [(land, False)]]
        colB = [[(cost, False)]] + [[((('+ ' if i else '') + s), True)] for i, s in enumerate(sl)]
        wa, wb = wmax(colA), wmax(colB)
        w = wa + wb + 32 + 24
        h = LH * 4 + 18
        x0, y0 = 1080, 408
        anc = ppx(C, (ri + ro) / 2, 90)
        st = (x0, y0 + 34)
        mid = (x0 - 60, anc[1])
        L.line([anc, mid, st], INK, 6.5)
        L.line([anc, mid, st], YEL, 2.6)
        L.ellipse([anc[0] - 6, anc[1] - 6, anc[0] + 6, anc[1] + 6], fill=YEL, outline=INK, w=2.4)
        cols = [colA, colB]
    L.rect([x0, y0, x0 + w, y0 + h], fill=(5, 13, 28, 252), outline=YEL + (255,), w=2.4, r=8)
    for yy in range(int(y0) + 5, int(y0 + h) - 3, 4):
        L.line([(x0 + 5, yy), (x0 + w - 5, yy)], (0, 0, 0, 30), 1)
    if opt == 'B':
        L.rect([x0 + 3, y0 + 3, x0 + w - 3, y0 + 36], fill=(44, 38, 6, 255), r=6)
        rtext(L, (x0 + 16, y0 + 20), head + '   ' + hp, 20, WHITE, True)
        for i, ln in enumerate(rows):
            xx = x0 + 16
            for s, b in ln:
                xx += rtext(L, (xx, y0 + 36 + 22 + i * LH), s, 20, WHITE, b)
        return
    xs = [x0 + 16] if len(cols) == 1 else [x0 + 16, x0 + 16 + wa + 24]
    for xx0, col in zip(xs, cols):
        for i, ln in enumerate(col):
            xx = xx0
            for s, b in ln:
                xx += rtext(L, (xx, y0 + 22 + i * LH), s, 20, WHITE, b)
    if len(cols) == 2:
        L.line([(x0 + 16 + wa + 12, y0 + 10), (x0 + 16 + wa + 12, y0 + h - 10)], (120, 110, 40), 1.6)
