"""E8 drawing library, round 2: option A units (cream HP segments grouped per sector, red chevron stacks, cyan shield bracket, steel armor cap, sealed hatching + padlock),
H's thin floating slice bars, one fate glyph (shot-dead X) per unit, gun tracers (armor bounce / shield pop), Trigger paths, future wave arcs, the Adjuster as a rim satellite,
Twist ghost chips. Every count comes from the frame dicts built by dump8.py from the E8 sim."""
import sys, math, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cv_lib import *
import bb_lib as B
import crests15 as _c15
import cv_board as CB
import cv_over as O

STEEL = (150, 162, 182)
STEEL_HI = (226, 233, 246)
CREAM = (255, 244, 214)
SOCK = (8, 10, 20)
SOCK_LINE = (120, 135, 152)
GOLD = (255, 196, 40)


def _g_ring(d, m):
    d.ellipse([30, 30, 482, 482], fill=255)
    d.ellipse([130, 130, 382, 382], fill=0)
    for a in (0, 120, 240):
        x, y = 256 + 90 * math.sin(math.radians(a)), 256 - 90 * math.cos(math.radians(a))
        d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=0)


def _g_trig(d, m):
    d.ellipse([60, 60, 452, 452], outline=255, width=44)
    d.rectangle([232, 10, 280, 150], fill=255)
    d.rectangle([232, 362, 280, 502], fill=255)
    d.rectangle([10, 232, 150, 280], fill=255)
    d.rectangle([362, 232, 502, 280], fill=255)
    d.ellipse([206, 206, 306, 306], fill=255)


def _g_strike(d, m):
    d.polygon([(300, 20), (110, 290), (240, 290), (190, 492), (410, 200), (280, 200)], fill=255)


def _g_hold(d, m):
    d.rectangle([110, 70, 220, 442], fill=255)
    d.rectangle([292, 70, 402, 442], fill=255)


def _g_bounce(d, m):
    d.line([(40, 120), (240, 380)], fill=255, width=70)
    d.line([(240, 380), (470, 120)], fill=255, width=70)
    d.polygon([(470, 60), (370, 90), (440, 190)], fill=255)


_c15.CUSTOM['U_RING'] = B._mk(_g_ring)
_c15.CUSTOM['C_TRIG'] = B._mk(_g_trig)
_c15.CUSTOM['C_STRIKE'] = B._mk(_g_strike)
_c15.CUSTOM['C_HOLD'] = B._mk(_g_hold)
_c15.CUSTOM['X_BOUNCE'] = B._mk(_g_bounce)
KIND['Ring'] = ('ZERO-DAY', 'U_RING')
KCOL['Ring'] = (255, 120, 215)
KNAME['Ring'] = 'RING'
CB.slice_value = lambda w, c: None          # no digits on slices


# ----------------------------------------------------------------------------- geometry helpers
def span(u):
    return 60 * u['s'] - 30, 60 * (u['s'] + u['w'] - 1) + 30


def rmid(d):
    ri, ro = CB.ring_geom(d)
    return (ri + ro) / 2


def tan(ang):
    th = math.radians(ang)
    return math.cos(th), math.sin(th)


def pt(r, ang, off=0.0):
    x, y = ppx(C, r, ang)
    tx, ty = tan(ang)
    return (x + tx * off, y + ty * off)


def sectors(u):
    return [(u['s'] + q) % 6 for q in range(u['w'])]


DEPTH_DIM = {0: 0, 1: 0, 2: 26}


def socket(L, r0, r1, a0, a1, alpha=235):
    L.poly(L.band(C, r0, r1, a0, a1), fill=SOCK + (alpha,), outline=SOCK_LINE, w=1.4)


# ----------------------------------------------------------------------------- unit pieces
def cell_outline(L, u, col=None, w=None):
    ri, ro = CB.ring_geom(u['dep'])
    lane = LANE[u['dep']]
    a0, a1 = span(u)
    c = col or lane['col']
    ww = w or lane['w']
    if u['w'] == 6:
        for r in (ri + 4, ro - 4):
            L.line(L.arc_pts(C, r, a0, a0 + 360, 120), c, ww, dash=lane['dash'])
    else:
        pts = L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3)
        L.line(pts + [pts[0]], c, ww, dash=lane['dash'])


def lit_cell(L, u):
    """the unit's screen is lit: a kind-coloured wash over the cell art, well above the dark empty sectors; the deepest ring a touch dimmer"""
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    kc = KCOL[u['kind']]
    if u['w'] == 6:
        L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=tuple(int(v * 0.55) for v in kc) + (150,))
    else:
        L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=tuple(int(v * (0.72 if u['dep'] == 0 else 0.55)) for v in kc) + (205 if u['dep'] == 0 else 150,))
    a = DEPTH_DIM[u['dep']]
    if a:
        if u['w'] == 6:
            L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=(2, 3, 8, a))
        else:
            L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=(2, 3, 8, a))


def token_pos_e10(u):
    ri, ro = CB.ring_geom(u['dep'])
    ang = 60 * u['s'] - 58 / rmid(u['dep']) * 57.3
    return ppx(C, ri + 31, ang)


def token_pos(u):
    import wr2_lib
    return wr2_lib.token_pos_r2(u, 'R')      # ASSEMBLY: the R2 token rule (38 px from the start cap)


def token(L, u, r=24, dead=False, dots=0):
    x, y = token_pos(u)
    k = L.k
    L.glow(lambda dd: dd.ellipse([(x - 32) * k, (y - 32) * k, (x + 32) * k, (y + 32) * k], fill=(4, 6, 14, 190)), blur=4)
    O.lane_base_style(L, x, y, r, u['dep'], KCOL[u['kind']])
    L.glyph(KIND[u['kind']][1], r * 1.55, (x, y), (150, 150, 160) if dead else WHITE)
    for i in range(dots):
        L.ellipse([x - (dots - 1) * 6 + i * 12 - 3.5, y + r + 3, x - (dots - 1) * 6 + i * 12 + 3.5, y + r + 10], fill=WHITE, outline=INK, w=1.2)
    return x, y


def hp_row(L, u, hp, mx, lose=0, shield=0, shmx=0):
    """cream segments in a dark socket along the outer edge, GROUPED PER SECTOR (a small gap at each sector boundary).
    lit = HP left; lose = segments that WILL be lost this END TURN (cream with a red slash). Shield pips = a cyan bracket over the first share of the row, dashed once lost."""
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    r0, r1 = ro - 14, ro - 6
    rm = (r0 + r1) / 2
    w = u['w']
    per = max(1, mx // w)
    socket(L, r0 - 2.5, r1 + 2.5, a0 + 4, a1 - 4)
    sec_w = (a1 - a0) / w
    gap = 3.4 / rm * 57.3
    idx = 0
    for q in range(w):
        sa0 = a0 + q * sec_w + 8
        sa1 = a0 + (q + 1) * sec_w - 8
        sw = (sa1 - sa0) / per
        for i in range(per):
            if idx < hp:
                pts = L.band(C, r0, r1, sa0 + i * sw + gap / 2, sa0 + (i + 1) * sw - gap / 2)
                L.poly(pts, fill=CREAM, outline=INK, w=1.0)
                if idx >= hp - lose:
                    m = sa0 + (i + 0.5) * sw
                    L.line([ppx(C, r0 - 1, m - sw * 0.35), ppx(C, r1 + 1, m + sw * 0.35)], RED, 2.6)
            idx += 1
    if shmx:
        share = (a1 - a0 - 8) * min(1.0, shmx / max(mx, 1))
        live = share * shield / shmx
        s0 = a0 + 5
        if shield:
            for col, ww in ((INK, 8), (CYAN, 4.2)):
                L.line(L.arc_pts(C, ro - 3, s0, s0 + live, 12), col, ww)
                for a in (s0, s0 + live):
                    L.line([ppx(C, ro - 3, a), ppx(C, ro - 19, a)], col, ww)
        if shield < shmx:
            L.line(L.arc_pts(C, ro - 3, s0 + live, s0 + share, 12), CYAN + (150,), 2, dash=(4, 4))


def armor_cap(L, u):
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    ca0, ca1 = a0 + 3, a1 - 3
    L.poly(L.band(C, ro - 7, ro + 1, ca0, ca1), fill=STEEL, outline=INK, w=1.8)
    L.poly(L.band(C, ro - 3.5, ro - 1, ca0 + 1.5, ca1 - 1.5), fill=STEEL_HI)
    L.poly(L.band(C, ro - 7, ro - 5.2, ca0 + 1.5, ca1 - 1.5), fill=(70, 80, 100))
    n = max(3, int((ca1 - ca0) / 12))
    for i in range(1, n):
        a = ca0 + (ca1 - ca0) * i / n
        x, y = ppx(C, ro - 3.5, a)
        L.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(40, 48, 64))


def sealed_marks(L, u):
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    for k in range(0, 360, 3):
        L.line([ppx(C, ri + 5, a0 + k), ppx(C, ro - 5, a0 + k + 7)], (255, 255, 255, 115), 2.0)
    x, y = ppx(C, (ri + ro) / 2, a0 + 1)
    L.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(10, 9, 16), outline=WHITE, w=3)
    L.glyph('X_LOCK', 28, (x, y), WHITE)


def chev_stack(L, ri, ang, n, col=RED):
    """n nested V chevrons, 28 px wide, pointing inward; a stem only on stacks of 2 or more"""
    for col_, w in ((INK, 10.5), (col, 6)):
        for i in range(n):
            r = ri + 9 + i * 9.5
            L.line([pt(r + 9, ang, -14), pt(r, ang, 0), pt(r + 9, ang, 14)], col_, w)
        if n > 1:
            L.line([pt(ri + 9, ang, 0), pt(ri - 5, ang, 0)], col_, w)


def chevrons(L, u, hit, col=RED):
    ri, ro = CB.ring_geom(u['dep'])
    for q in range(u['w']):
        chev_stack(L, ri, 60 * (u['s'] + q), hit, col)


def warded_mark(L, u):
    ri, ro = CB.ring_geom(u['dep'])
    ang = 60 * u['s'] + 10
    x, y = ppx(C, ri + 31, ang + (30 / rmid(u['dep'])) * 57.3)
    L.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(30, 22, 4, 240), outline=GOLD, w=2.4)
    L.glyph('X_LOCK', 14, (x, y), GOLD)


def dead_x(L, u):
    """the one fate glyph: shot dead = a 26 px green X disc at the cell's inward edge"""
    ang = 60 * (u['s'] + (u['w'] - 1) / 2)
    ri, ro = CB.ring_geom(u['dep'])
    x, y = pt(ri + 31, ang, 34 if u['w'] == 1 else 48)
    L.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(10, 30, 14, 250), outline=GREEN, w=3)
    L.line([(x - 6.5, y - 6.5), (x + 6.5, y + 6.5)], GREEN, 4)
    L.line([(x + 6.5, y - 6.5), (x - 6.5, y + 6.5)], GREEN, 4)


def tower_slice_bars(L, f):
    """H's thin floating bars: one capsule per slice HP (the sim's max), lit green, lost dim dashed; cracked = zigzag; broken = dark slice + red X, ability lost."""
    for w in f['wheel']:
        s = w['sector']
        mx, hp = w['mx'], w['hp']
        hp_after = w.get('hp_after', hp)
        a0, a1 = 60 * s - 24, 60 * s + 24
        n = mx
        seg = (a1 - a0 - 6) / n
        for i in range(n):
            pts = L.arc_pts(C, RS['s1'] - 11, a0 + 3 + i * seg + 1.5, a0 + 3 + (i + 1) * seg - 1.5, 8)
            if i < hp:
                lose = i >= hp_after
                L.line(pts, INK, 11)
                L.line(pts, (255, 150, 140) if lose else GREEN, 7)
                if lose:
                    m = a0 + 3 + (i + 0.5) * seg
                    L.line([ppx(C, RS['s1'] - 16, m - 3), ppx(C, RS['s1'] - 6, m + 3)], RED, 2.4)
            else:
                L.line(pts, SOCK_LINE + (140,), 1.8, dash=(2, 4))
        if hp == 0:
            L.poly(L.band(C, RS['s0'], RS['s1'], 60 * s - 28, 60 * s + 28), fill=(4, 4, 10, 170))
            x, y = ppx(C, 95, 60 * s)
            L.line([(x - 18, y - 18), (x + 18, y + 18)], RED, 7)
            L.line([(x + 18, y - 18), (x - 18, y + 18)], RED, 7)
        elif hp < mx:
            m = 60 * s
            p = [ppx(C, RS['s1'] - 3, m - 6), ppx(C, RS['s1'] - 9, m - 2), ppx(C, RS['s1'] - 15, m + 3), ppx(C, RS['s1'] - 21, m - 1)]
            L.line(p, INK, 4.5)
            L.line(p, (255, 255, 255), 2)


def threat_trim(L, f):
    seen = set()
    for u in f['units']:
        fz = u['fate']
        if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
            continue
        for (sec, sl, hit, tohp) in fz['hits']:
            seen.add((sec, fz['k']))
    for (sec, k) in sorted(seen):
        if k == 0:
            L.line(L.arc_pts(C, RS['s1'] - 1, 60 * sec - 25, 60 * sec + 25), RED, 5.5)
        elif k == 1:
            L.line(L.arc_pts(C, RS['s1'] + 3, 60 * sec - 25, 60 * sec + 25), (255, 61, 168), 3, dash=(8, 5))
        else:
            L.line(L.arc_pts(C, RS['s1'] + 7, 60 * sec - 25, 60 * sec + 25), (236, 240, 255), 2.4, dash=(4, 6))


def gun_tracers(L, f):
    """decide state: each gun's default target. BURST = 2 shots (two lines), TURRET = 1. Result glyph at the end: white spark = hit, steel ricochet = bounced off armor,
    cyan pop = shield pip lost, padlock = wasted on the seal, gold ricochet = ward; an idle gun says NO TARGET."""
    for g in f['guns']:
        s = g['sector']
        if not g['shots'] or g['shots'][0]['uid'] is None:
            L.line([ppx(C, RS['s1'] + 2, 60 * s), ppx(C, RS['c0'] + 14, 60 * s)], CYAN, 2, dash=(4, 8))
            if NOW['words']:
                xx_, yy_ = ppx(C, RS['c0'] + 30, 60 * s)
                L.rect([xx_ - 52, yy_ - 12, xx_ + 52, yy_ + 12], fill=(6, 12, 24, 235), outline=CYAN, w=2, r=6)
                L.text((xx_, yy_ + 1), 'NO TARGET', 16, 'mono', fill=CYAN)
            continue
        shots = [sh for sh in g['shots'] if sh['uid'] is not None]
        n = len(shots)
        for i, sh in enumerate(shots):
            off = 24 + (i - (n - 1) / 2) * 9
            d = sh['dep']
            ri, ro = CB.ring_geom(d)
            p0 = pt(RS['s1'] + 3, 60 * s, off)
            boss = sh['uid'] == 0
            p1 = pt(RS['bz1'] + 6, 60 * s, off) if boss else pt(ri + 16, 60 * s, off)
            L.line([p0, p1], INK, 6.5)
            L.line([p0, p1], CYAN, 3.6, dash=(10, 4))
            ri = RS['bz1'] - 14 if boss else ri
            x, y = p1
            if sh['result'] == 'armor':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), STEEL_HI)
            elif sh['result'] == 'ward':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), GOLD)
            elif sh['result'] == 'sealed':
                L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 9, 16), outline=WHITE, w=2.4)
                L.glyph('X_LOCK', 13, (x, y), WHITE)
            elif sh['result'] == 'shield':
                L.ellipse([x - 8, y - 8, x + 8, y + 8], fill=CYAN, outline=INK, w=2)
                for a_ in range(0, 360, 60):
                    L.line([(x + 10 * math.cos(math.radians(a_)), y + 10 * math.sin(math.radians(a_))), (x + 15 * math.cos(math.radians(a_)), y + 15 * math.sin(math.radians(a_)))], CYAN, 2.4)
            else:
                L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255), outline=CYAN, w=2.6)


# ----------------------------------------------------------------------------- Trigger path (grease pencil, the player's plan)
def pencil_line(L, pts, col, w=8, dash=None):
    if dash:
        L.line(pts, (6, 3, 8), w + 5, dash=(dash[0] + 3, dash[1] - 1))
        L.line(pts, col, w, dash=dash)
    else:
        L.line(pts, (6, 3, 8), w + 5)
        L.line(pts, col, w)


def pencil_x(L, x, y, col=YEL, r=11):
    L.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=(6, 3, 8, 235))
    L.line([(x - r + 3, y - r + 3), (x + r - 3, y + r - 3)], col, 4)
    L.line([(x + r - 3, y - r + 3), (x - r + 3, y + r - 3)], col, 4)


def trigger_paths(L, f, tr, dashed=False):
    for e in tr['entries']:
        sec = e[1]
        ang = 60 * sec
        r_from = rmid(tr['dep'])
        if e[0] == 'unit':
            tgt = e[2]
            r_to = rmid(tgt)
            pencil_line(L, [ppx(C, r_from, ang), ppx(C, r_to, ang)], YEL, 8, dash=(12, 7) if dashed else None)
            x, y = ppx(C, r_to, ang)
            pencil_x(L, x, y, YEL, 14)
        else:
            hit = e[3]
            pencil_line(L, [ppx(C, r_from, ang), ppx(C, RS['s1'] + 6, ang)], RED, 8, dash=(12, 7) if dashed else None)
            chev_stack(L, RS['s1'] - 10, ang, hit, RED)


# ----------------------------------------------------------------------------- waves beyond the rim: FUTURE waves only (one thin cell arc each); labels engraved at the arc start
ARC_START = 22


def wave_arcs(L, arcs):
    """FUTURE waves only: a thin ghost arc per wave in the wave colour (orange, climax red + hazard ticks) with its unit glyphs sitting on it, a width tick per sector,
    an opaque 22 px W<n> chip at the arc start. The SEALED tag sits on the climax arc where the Ring is."""
    r = RS['bz1'] + 70
    fut = [a for a in arcs if a['state'] == 'future']
    for a in fut:
        col_w = RED if a.get('climax') else ORANGE
        rm = r + 11
        L.line(L.arc_pts(C, rm, ARC_START, ARC_START + 359, 120), col_w + (235,), 3)
        ang = ARC_START
        for (kind, w) in a['units']:
            a1 = ang + 60 * w
            kc = KCOL.get(kind, WHITE)
            m = (ang + a1) / 2
            x, y = ppx(C, rm, m)
            L.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(10, 12, 22, 240), outline=kc, w=2.4)
            L.glyph(KIND[kind][1], 20, (x, y), WHITE)
            for q in range(1, w):
                x2, y2 = ppx(C, rm, ang + 60 * q)
                L.ellipse([x2 - 3.5, y2 - 3.5, x2 + 3.5, y2 + 3.5], fill=WHITE + (200,))
            ang = a1
        if a.get('climax'):
            for k in range(ARC_START, ARC_START + 360, 14):
                L.line([ppx(C, rm - 5, k), ppx(C, rm + 5, k + 6)], (255, 226, 0, 190), 2.4)
            if any(k_ == 'Ring' for k_, _ in a['units']) and NOW['words']:
                xx, yy = ppx(C, rm, 42)
                L.rect([xx - 62, yy - 13, xx + 62, yy + 13], fill=(8, 10, 18, 255), outline=WHITE, w=2.2, r=5)
                L.glyph('X_LOCK', 17, (xx - 46, yy), WHITE)
                L.text((xx - 32, yy + 1), 'SEALED +2', 16, 'mono', fill=WHITE, anchor='lm')
        if NOW['words']:
            x, y = ppx(C, rm, ARC_START - 4.2)
            lab = 'W%d' % (a['wave'] + 1)
            L.rect([x - 22, y - 11, x + 22, y + 11], fill=(8, 10, 18, 255), outline=col_w, w=2, r=5)
            L.text((x, y + 1), lab, 16, 'mono', fill=col_w)
        r += 26


# ----------------------------------------------------------------------------- Adjuster: a gold boss satellite docked on the rim at its sector
def adjuster_satellite(L, a):
    if a['hp'] <= 0:
        return
    ang = 60 * a['s']
    rb = RS['bz1']
    n = a['mx']
    a0, a1 = ang - 12, ang + 12
    r0, r1 = rb + 8, rb + 17
    socket(L, r0 - 2.5, r1 + 2.5, a0 - 1, a1 + 1)
    sw = (a1 - a0) / n
    gap = 3.0 / ((r0 + r1) / 2) * 57.3
    for i in range(n):
        if i < a['hp']:
            L.poly(L.band(C, r0, r1, a0 + i * sw + gap / 2, a0 + (i + 1) * sw - gap / 2), fill=CREAM, outline=INK, w=1.0)
            if i >= a['hp_after']:
                m = a0 + (i + 0.5) * sw
                L.line([ppx(C, r0 - 1, m - sw * 0.35), ppx(C, r1 + 1, m + sw * 0.35)], RED, 2.4)
    if a['df'] == 'armor':
        L.poly(L.band(C, r1 + 3, r1 + 10, a0, a1), fill=STEEL, outline=INK, w=1.6)
        L.poly(L.band(C, r1 + 6, r1 + 8.5, a0 + 1, a1 - 1), fill=STEEL_HI)
    x, y = ppx(C, r1 + 34, ang)
    k = L.k
    L.glow(lambda dd: dd.ellipse([(x - 36) * k, (y - 36) * k, (x + 36) * k, (y + 36) * k], fill=(4, 6, 14, 200)), blur=4)
    for sg in (-1, 1):
        L.line([pt(r1 + 12, ang, sg * 16), pt(rb + 2, ang, sg * 16)], GOLD, 3)
    oct_ = [(x + 27 * math.cos(math.radians(22.5 + 45 * i)), y + 27 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    L.poly(oct_, fill=(40, 32, 12, 255), outline=GOLD, w=3.6)
    L.glyph('X_SKULL', 30, (x, y), WHITE)
    if a['strike']:
        chev_stack(L, rb - 30, ang, a['hit'], RED)


def ward_arc(L, f):
    a = f['adj']
    if a['hp'] > 0:
        L.line(L.arc_pts(C, RS['c0'] - 4, 60 * a['s'] - 26, 60 * a['s'] + 26), (6, 3, 8), 8)
        L.line(L.arc_pts(C, RS['c0'] - 4, 60 * a['s'] - 26, 60 * a['s'] + 26), GOLD, 4.5)


# ----------------------------------------------------------------------------- Twist ghost chips on the rim
def twist_chip(L, ang, r, pips, ring, sgn, col=YEL):
    """ghost chip ON the bezel rim: twist glyph + ring and direction + a short tally (a group of 5, a gap, the rest) of the pips a next-turn Trigger takes off units"""
    x, y = ppx(C, r, ang)
    g1, g2 = min(pips, 5), max(0, pips - 5)
    w = 100 + g1 * 11 + (g2 * 11 + 8 if g2 else 0)
    L.rect([x - w / 2, y - 15, x + w / 2, y + 15], fill=(8, 10, 18, 235), outline=col, w=2.4, r=7)
    L.glyph('C_TWIST', 20, (x - w / 2 + 16, y), col)
    if NOW['words']:
        L.text((x - w / 2 + 34, y + 1), ('+2' if ring == 2 else '+1') + ('>' if sgn > 0 else '<'), 16, 'mono', fill=col, anchor='lm')
    px_ = x - w / 2 + 76
    for i in range(g1):
        L.rect([px_ + i * 11, y - 7, px_ + i * 11 + 8, y + 7], fill=col, outline=INK, w=1.2, r=2)
    for i in range(g2):
        L.rect([px_ + g1 * 11 + 8 + i * 11, y - 7, px_ + g1 * 11 + 8 + i * 11 + 8, y + 7], fill=col, outline=INK, w=1.2, r=2)
