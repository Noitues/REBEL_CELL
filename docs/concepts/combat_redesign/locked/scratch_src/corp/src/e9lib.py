"""E9 drawing library = e8lib + Brace plate, soak marks, rim landing chips (hit at landing with growth ghosted + wear + turns until), a 0-step HOLD glyph on the bezel,
no seal, pink recoloured (pink = unit screens only; the lane +1 line is pale blue), rider in lavender. Every count comes from the frame dicts built by dump9.py."""
import sys, math, os
sys.dont_write_bytecode = True
from e8lib import *
import e8lib as E8
import bb_lib as B
import crests15 as _c15

SOAK_C = (255, 150, 40)
LAV = (190, 160, 255)
PALE = (120, 170, 255)


def _g_brace(d, m):
    d.rounded_rectangle([90, 70, 422, 400], radius=40, outline=255, width=64)
    d.rectangle([30, 200, 110, 300], fill=255)
    d.rectangle([402, 200, 482, 300], fill=255)
    d.polygon([(256, 140), (330, 256), (256, 372), (182, 256)], fill=255)


_c15.CUSTOM['C_BRACE'] = B._mk(_g_brace)


# ----------------------------------------------------------------------------- bezel with a distinct 0-step glyph (hollow ring + HOLD bars, never a dim gap)
def bezel9(L, sched):
    b0, b1 = RS['bz0'] + 3, RS['bz0'] + 29
    for i in range(60):
        a = 6 * i
        L.line([ppx(C, RS['bz1'] - 7, a), ppx(C, RS['bz1'] - (3 if i % 10 else 1), a)], (255, 190, 110) if i % 10 == 0 else (150, 100, 55), 1.2)
    names = ['THIS TURN', 'NEXT', 'THEN']
    cum = 0
    for k, v in enumerate(sched):
        live = k == 0
        if v == 0:
            span_ = 40
            a0, a1 = cum + 0.8, cum + span_ - 0.8
            L.poly(L.band(C, b0, b1, a0, a1), fill=(14, 10, 6, 235), outline=(255, 190, 110) if not live else WHITE, w=2.4)
            x, y = ppx(C, (b0 + b1) / 2, a0 + 6)
            L.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(10, 9, 16), outline=(255, 190, 110) if not live else WHITE, w=2.6)
            L.glyph('C_HOLD', 15, (x, y), (255, 190, 110) if not live else WHITE)
            L.arc_text(C, (b0 + b1) / 2 - 1, a0 + 24, 'HOLD ' + names[k].split()[0], 16, (255, 190, 110), 'mono')
            cum += span_
            continue
        span_ = 60 * v
        a0, a1 = cum + 0.8, cum + span_ - 0.8
        L.poly(L.band(C, b0, b1, a0, a1), fill=(255, 150, 40) if live else O.ORG_D, outline=ORANGE, w=1.6)
        txt = '+%d %s' % (v, names[k])
        lab_deg = len(txt) * 10.2 / ((b0 + b1) / 2) * 57.3
        nch = int(span_ / 12)
        for j in range(nch):
            am = a0 + (a1 - a0) * (j + 0.5) / nch
            if am < a0 + 6 + lab_deg + 4:
                continue
            p = [ppx(C, b0 + 5, am - 2.4), ppx(C, (b0 + b1) / 2, am + 2.4), ppx(C, b1 - 5, am - 2.4)]
            L.line(p, (255, 230, 170) if live else (170, 100, 35), 1.8)
        L.arc_text(C, (b0 + b1) / 2 - 1, a0 + 6 + lab_deg / 2, txt, 17, INK if live else (255, 190, 110), 'mono')
        cum += span_


# ----------------------------------------------------------------------------- tower: Brace plate, soak marks, slice bars
def brace_plate(L, s):
    """a heavy cream plate clamped round the slice: bold cream outline with ink under it, 4 rivets, a glyph disc: clearly not the cyan unit shield"""
    pts = L.band(C, RS['s0'] + 3, RS['s1'] - 1, 60 * s - 28, 60 * s + 28)
    L.poly(pts, fill=(255, 244, 214, 38), outline=INK, w=12)
    L.poly(pts, fill=None, outline=CREAM, w=7)
    for a, r in ((60 * s - 26, RS['s0'] + 9), (60 * s + 26, RS['s0'] + 9), (60 * s - 26, RS['s1'] - 8), (60 * s + 26, RS['s1'] - 8)):
        x, y = ppx(C, r, a)
        L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=INK, outline=CREAM, w=2.2)
    x, y = ppx(C, RS['s0'] + 30, 60 * s)
    L.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(26, 22, 14, 250), outline=CREAM, w=3)
    L.glyph('C_BRACE', 20, (x, y), CREAM)


def soak_marks(L, s):
    """orange chevrons in the slice, pointing at it: this slice takes the overflow pips instead of your HP"""
    for r in (86, 100):
        p = [pt(r + 8, 60 * s, -13), pt(r, 60 * s, 0), pt(r + 8, 60 * s, 13)]
        L.line(p, INK, 10)
        L.line(p, SOAK_C, 6)
    L.line(L.arc_pts(C, RS['s1'] - 1, 60 * s - 26, 60 * s + 26), INK, 9)
    L.line(L.arc_pts(C, RS['s1'] - 1, 60 * s - 26, 60 * s + 26), SOAK_C, 5.5)


def tower_slice_bars(L, f):
    for w in f['wheel']:
        s = w['sector']
        mx, hp = w['mx'], w['hp']
        hp_after = w.get('hp_after', hp)
        soaked = w.get('soaked', 0)
        a0, a1 = 60 * s - 24, 60 * s + 24
        n = mx
        seg = (a1 - a0 - 6) / n
        top = max(hp, hp_after)
        for i in range(n):
            pts = L.arc_pts(C, RS['s1'] - 11, a0 + 3 + i * seg + 1.5, a0 + 3 + (i + 1) * seg - 1.5, 8)
            if i < hp_after:
                L.line(pts, INK, 11)
                L.line(pts, GREEN if i < hp else (170, 240, 170), 7)
                if i >= hp:
                    L.line(pts, WHITE + (200,), 2, dash=(3, 3))
            elif i < hp:
                lost_i = hp - 1 - i                  # 0 = the last segment, lost first
                by_soak = lost_i < soaked
                L.line(pts, INK, 11)
                L.line(pts, SOAK_C if by_soak else (255, 150, 140), 7)
                m = a0 + 3 + (i + 0.5) * seg
                L.line([ppx(C, RS['s1'] - 16, m - 3), ppx(C, RS['s1'] - 6, m + 3)], (255, 255, 255), 2.4)
            else:
                L.line(pts, SOCK_LINE + (140,), 1.8, dash=(2, 4))
        if hp == 0:
            L.poly(L.band(C, RS['s0'], RS['s1'], 60 * s - 28, 60 * s + 28), fill=(4, 4, 10, 170))
            x, y = ppx(C, 95, 60 * s)
            L.line([(x - 18, y - 18), (x + 18, y + 18)], RED, 7)
            L.line([(x + 18, y - 18), (x - 18, y + 18)], RED, 7)
        elif hp_after == 0:
            x, y = ppx(C, 95, 60 * s + 16)
            col = SOAK_C if soaked else RED
            L.line([(x - 14, y - 14), (x + 14, y + 14)], INK, 11)
            L.line([(x + 14, y - 14), (x - 14, y + 14)], INK, 11)
            L.line([(x - 14, y - 14), (x + 14, y + 14)], col + (230,), 6)
            L.line([(x + 14, y - 14), (x - 14, y + 14)], col + (230,), 6)
        elif hp < mx and hp_after == hp:
            m = 60 * s
            p = [ppx(C, RS['s1'] - 3, m - 6), ppx(C, RS['s1'] - 9, m - 2), ppx(C, RS['s1'] - 15, m + 3), ppx(C, RS['s1'] - 21, m - 1)]
            L.line(p, INK, 4.5)
            L.line(p, (255, 255, 255), 2)
        if w.get('brace'):
            brace_plate(L, s)
        if w.get('soak'):
            soak_marks(L, s)


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
            L.line(L.arc_pts(C, RS['s1'] + 3, 60 * sec - 25, 60 * sec + 25), PALE, 3, dash=(8, 5))
        else:
            L.line(L.arc_pts(C, RS['s1'] + 7, 60 * sec - 25, 60 * sec + 25), (236, 240, 255), 2.4, dash=(4, 6))


# ----------------------------------------------------------------------------- rim landing chip for EVERY landing unit
def chip_size(u, k):
    n = u['land_hit']
    ghost = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
    solid = n - ghost
    w = 12 + 32 + 8 + 17 * n + (22 if u.get('wear') else 0) + 8 + (16 if k == 0 else 12 * k) + 8
    return w, solid, ghost


def rim_chips(L, f):
    items = []
    for u in f['units']:
        if u['consumed'] or u['trigdead']:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or 'land_hit' not in u:
            continue
        angs = [60 * s for s in u['land_sectors']]
        x = sum(math.sin(math.radians(a)) for a in angs)
        y = sum(math.cos(math.radians(a)) for a in angs)
        am = math.degrees(math.atan2(x, y)) % 360
        items.append(dict(u=u, ang=am, k=fz['k']))
    items.sort(key=lambda it: it['ang'])
    R = RS['bz1'] + 36
    placed = []
    ad = f['adj']
    if ad['hp'] > 0:
        ax, ay = ppx(C, RS['bz1'] + 51, 60 * ad['s'])
        placed.append((ax - 36, ay - 36, ax + 36, ay + 36))
    for it in items:
        w, solid, ghost = chip_size(it['u'], it['k'])
        it['w'], it['solid'], it['ghost'] = w, solid, ghost
        a = it['ang'] + 4
        for _ in range(60):
            x, y = ppx(C, R, a)
            box = (x - w / 2, y - 22, x + w / 2, y + 22)
            if all(box[2] + 4 < p[0] or box[0] - 4 > p[2] or box[3] + 4 < p[1] or box[1] - 4 > p[3] for p in placed):
                break
            a += 2
        it['pos'] = (x, y)
        placed.append((x - w / 2, y - 22, x + w / 2, y + 22))
    for it in items:
        u, k = it['u'], it['k']
        x, y = it['pos']
        w = it['w']
        lane = LANE[u['dep']]
        L.rect([x - w / 2, y - 21, x + w / 2, y + 21], fill=(8, 10, 18, 250), outline=lane['col'], w=3, r=9)
        gx = x - w / 2 + 6 + 16
        L.ellipse([gx - 16, y - 16, gx + 16, y + 16], fill=tuple(int(v * 0.55) for v in KCOL[u['kind']]) + (255,), outline=KCOL[u['kind']], w=2.4)
        L.glyph(KIND[u['kind']][1], 24, (gx, y), WHITE)
        cx = gx + 16 + 8
        for i in range(u['land_hit']):
            xx = cx + i * 17 + 8
            p = [(xx - 8, y - 6), (xx, y + 5), (xx + 8, y - 6)]
            if i < it['solid']:
                L.line(p, INK, 8)
                L.line(p, RED, 4.6)
            else:
                L.line(p, WHITE + (200,), 2.4, dash=(3, 3))
        cx += 17 * u['land_hit']
        if u.get('wear'):
            L.rect([cx + 2, y - 9, cx + 17, y + 7], fill=GREEN, outline=INK, w=1.6, r=2)
            L.line([(cx + 6, y - 9), (cx + 10, y - 3), (cx + 8, y + 1), (cx + 13, y + 7)], WHITE, 2)
            cx += 22
        cx += 8
        if k == 0:
            L.ellipse([cx, y - 7, cx + 14, y + 7], fill=RED, outline=WHITE, w=2)
        else:
            for i in range(k):
                L.ellipse([cx + i * 12, y - 4.5, cx + i * 12 + 9, y + 4.5], fill=WHITE, outline=INK, w=1.2)


# ----------------------------------------------------------------------------- waves beyond the rim (no seal tag)
def wave_arcs(L, arcs):
    r = RS['bz1'] + 70
    fut = [a for a in arcs if a['state'] == 'future']
    for a in fut:
        col_w = RED if a.get('climax') else ORANGE
        rm = r + 11
        L.line(L.arc_pts(C, rm, E8.ARC_START, E8.ARC_START + 359, 120), col_w + (235,), 3)
        ang = E8.ARC_START
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
            for k in range(E8.ARC_START, E8.ARC_START + 360, 14):
                L.line([ppx(C, rm - 5, k), ppx(C, rm + 5, k + 6)], (255, 226, 0, 190), 2.4)
        if NOW['words']:
            x, y = ppx(C, rm, E8.ARC_START - 4.2)
            lab = 'W%d' % (a['wave'] + 1)
            L.rect([x - 22, y - 11, x + 22, y + 11], fill=(8, 10, 18, 255), outline=col_w, w=2, r=5)
            L.text((x, y + 1), lab, 16, 'mono', fill=col_w)
        r += 26


def warded_mark(L, u):
    """gold shield (not a padlock) on a unit that sits on the Adjuster's sector"""
    ri, ro = CB.ring_geom(u['dep'])
    ang = 60 * u['s'] + 10
    x, y = ppx(C, ri + 31, ang + (30 / rmid(u['dep'])) * 57.3)
    pts = [(x - 10, y - 11), (x + 10, y - 11), (x + 10, y + 2), (x, y + 12), (x - 10, y + 2)]
    L.poly(pts, fill=(40, 30, 6, 245), outline=GOLD, w=2.6)
    L.line([(x, y - 7), (x, y + 6)], GOLD, 2.4)
