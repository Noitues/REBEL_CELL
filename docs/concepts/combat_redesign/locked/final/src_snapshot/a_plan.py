"""Plan / preview marks on the board: trigger path, twist badge, refund placement, resolve fire lines. Options A/B/C ('cur' handled by render)."""
import sys, math, random
sys.dont_write_bytecode = True
from a_kit import *
import cv_board as CB9

PTHREAT = (255, 28, 44)


def wax_v(L, tip, ang, size=16, col=YEL, seed=5, w=6):
    """open hand-drawn arrowhead: two strokes back from the tip (ang in radians = direction of travel)"""
    j = random.Random(seed)
    for sgn in (1, -1):
        a = ang + math.pi + sgn * 0.52
        p = (tip[0] + size * math.cos(a) + j.uniform(-1, 1), tip[1] + size * math.sin(a) + j.uniform(-1, 1))
        wax(L, [p, tip], col, w, seed + int(sgn), 0.3)


def scribble(L, x, y, r=14, seed=3, col=YEL):
    """cross-out: a rotated zigzag of 6 hatches over the token"""
    rnd = random.Random(seed)
    pts = []
    n = 7
    th = math.radians(-38)
    for i in range(n):
        u = -r + 2 * r * (i % 2)
        v = -r * 0.9 + 1.8 * r * i / (n - 1)
        pts.append((x + u * math.cos(th) - v * math.sin(th) + rnd.uniform(-1, 1), y + u * math.sin(th) + v * math.cos(th) + rnd.uniform(-1, 1)))
    wax(L, pts, col, 4.4, seed, 0.4)


def trigger_path(L, f, tr, opt):
    for ei, e in enumerate(tr['entries']):
        if e[0] == 'refund':
            continue
        sec = e[1]
        ang = 60 * sec
        ri1, ro1 = CB.ring_geom(tr['dep'])
        r_from = ro1 - 12
        p0 = ppx(C, r_from, ang)
        if e[0] == 'unit':
            r_to = rmid(e[2])
            x, y = ppx(C, r_to, ang)
            dirv = math.atan2(y - p0[1], x - p0[0])
            if opt == 'A':                    # wax line, hand X on the target
                wax(L, [p0, (x - 7 * math.cos(dirv), y - 7 * math.sin(dirv))], YEL, 7, 10 + ei, 0.6)
                wax_x(L, x, y, 13, YEL, 20 + ei)
            elif opt == 'B':                  # line with an open arrowhead, the target scribbled out
                q = (x - 22 * math.cos(dirv), y - 22 * math.sin(dirv))
                wax(L, [p0, q], YEL, 7, 10 + ei, 0.6)
                wax_v(L, q, dirv, 15, YEL, 30 + ei)
                scribble(L, x, y, 15, 40 + ei)
            else:                             # origin dot, line, the target circled and crossed (reticle)
                L.ellipse([p0[0] - 6, p0[1] - 6, p0[0] + 6, p0[1] + 6], fill=(6, 3, 8, 235))
                L.ellipse([p0[0] - 3.5, p0[1] - 3.5, p0[0] + 3.5, p0[1] + 3.5], fill=YEL)
                wax(L, [p0, (x - 23 * math.cos(dirv), y - 23 * math.sin(dirv))], YEL, 7, 10 + ei, 0.6)
                wax_x(L, x, y, 10, YEL, 20 + ei, circle=True)
        else:                                 # reaches the tower: threat pencil to the slice rim
            hit = e[3]
            q = ppx(C, RS['s1'] + 8, ang)
            wax(L, [p0, q], PTHREAT, 7, 50 + ei, 0.6)
            chev_stack(L, RS['s1'] - 10, ang, hit, RED)


def tag_of(f, ring):
    lane = LANE[ring]
    return lane['name'] + (' W%d' % (f['rings_wave'][ring] + 1) if f['rings_wave'][ring] >= 0 else '')


def twist_badge(L, f, opt):
    ring, dirn = f['twr']
    if not dirn:
        return
    ri, ro = CB.ring_geom(ring)
    x, y = ppx(C, (ri + ro) / 2, 30)
    wd = L.tw(tag_of(f, ring), 17, 'anton') + 14
    xr = x + wd / 2
    n = abs(dirn)
    chev = lambda cx_: [(cx_ - 4, y - 8), (cx_ + 4, y), (cx_ - 4, y + 8)]
    if opt == 'A':          # pill the height of the tag, docked at its right end
        w_ = 30 + 11 * n + 12
        L.rect([xr - 2, y - 12, xr + w_, y + 12], fill=(26, 22, 4, 250), outline=YEL, w=2.4, r=12)
        L.glyph('C_TWIST', 18, (xr + 14, y), YEL)
        for q in range(n):
            L.line(chev(xr + 33 + q * 9), INK, 8)
            L.line(chev(xr + 33 + q * 9), YEL, 4.6)
    elif opt == 'B':        # yellow end cap fused to the tag: ink glyph + one fat ink chevron
        w_ = 24 + 12 * n + 8
        L.rect([xr - 8, y - 12, xr + w_, y + 12], fill=YEL, outline=INK, w=2.2, r=6)
        L.glyph('C_TWIST', 17, (xr + 8, y), INK)
        for q in range(n):
            L.line(chev(xr + 25 + q * 9), INK, 4.6)
    else:                   # pencil: the tag ringed, a clockwise arrow along the ring
        rr = (ri + ro) / 2
        a0 = 30 + (wd / 2 + 8) / rr * 57.3
        pts = [ppx(C, rr, a0 + i * 2.4) for i in range(0, 12)]
        wax(L, pts, YEL, 5.4, 7, 0.4)
        tip = pts[-1]
        d_ = math.atan2(tip[1] - pts[-3][1], tip[0] - pts[-3][0])
        wax_v(L, tip, d_, 13, YEL, 8, 5)
        el = [(x + (wd / 2 + 7) * math.cos(math.radians(t)), y + 17 * math.sin(math.radians(t))) for t in range(-300, 20, 18)]
        wax(L, el, YEL, 3.6, 9, 0.5)


def refund_place(L, f, opt, tok, words=True):
    kl = f['kills'][-1]
    u = [u for u in f['units'] if u['id'] == kl['uid']][0]
    tp0 = token_pos(u)
    tag = 'REFUND'

    def tagbox(cx, cy, w=94):
        L.rect([cx - w / 2, cy - 13, cx + w / 2, cy + 13], fill=(8, 10, 18, 245), outline=CYAN, w=2, r=6)
        if words:
            L.text((cx, cy + 1), tag, 18, 'mono', fill=CYAN)
    if opt == 'A':          # beside, clear of the pencil X: token over the cell's open stretch, tag under it
        x, y = ppx(C, rmid(0) - 1, 203)
        refund_token(L, x, y, 44, tok)
        tagbox(x, y + 42)
    elif opt == 'B':        # pip badge on the dead token's shoulder, tag hangs below the pair
        x, y = tp0[0] + 25, tp0[1] - 20
        refund_token(L, x, y, 40, tok)
        tagbox(tp0[0] + 6, tp0[1] + 45)
    else:                   # ticket: token and tag in one plate bridging the open stretch
        x, y = ppx(C, rmid(0) - 1, 207)
        L.rect([x - 66, y - 22, x + 66, y + 22], fill=(8, 10, 18, 245), outline=CYAN, w=2.2, r=8)
        refund_token(L, x - 40, y, 32, tok)
        if words:
            L.text((x + 14, y + 1), tag, 18, 'mono', fill=CYAN)


def fire_lines(L, f, opt):
    if opt == 'A':
        sub = L2()
        gun_tracers10(sub, f)
        im = sub.im
        im.putalpha(im.split()[3].point(lambda v: int(v * 0.55)))
        L.im.alpha_composite(im)
    elif opt == 'B':        # fired pips on each gun slice rim, one per shot
        for g in f['guns']:
            shots = [s for s in g['shots'] if s['uid'] is not None]
            n = len(shots)
            for i in range(n):
                a = 60 * g['sector'] + (i - (n - 1) / 2) * 9
                x, y = ppx(C, RS['s1'] + 9, a)
                L.ellipse([x - 5.5, y - 5.5, x + 5.5, y + 5.5], fill=CYAN, outline=INK, w=2)
    else:                   # tapering streaks that end on the target's token ring
        for e_ in f['log']:
            if e_[0] == 'fire' and e_[3] is not None:
                s_, dep_ = e_[1], e_[5]
                p0 = ppx(C, RS['s1'] + 3, 60 * s_ + 3)
                p1 = pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)
                n = 8
                for i in range(n):
                    t0, t1 = i / n, (i + 1) / n
                    a = (p0[0] + (p1[0] - p0[0]) * t0, p0[1] + (p1[1] - p0[1]) * t0)
                    b = (p0[0] + (p1[0] - p0[0]) * t1, p0[1] + (p1[1] - p0[1]) * t1)
                    wdt = 5.2 - 3.6 * t0
                    L.line([a, b], (12, 10, 22, 150), wdt + 2.6)
                    L.line([a, b], CYAN + (int(200 - 70 * t0),), wdt)
                x, y = p1
                L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=WHITE + (200,), outline=CYAN + (200,), w=2)
