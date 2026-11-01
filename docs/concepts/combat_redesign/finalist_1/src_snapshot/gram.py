"""gram: the grammar pass (VISUAL_PLAN B-F) applied to the E10 board in its CURRENT style.
Monkeypatches the E10 generator at import-free call sites (asm_r2 pipeline) and renders full plates for the option sets.
CFG: time A (heat: value+contour+notch/pips) | B (dial: contour constant, fuse dial glyphs) | C (frost: contour constant, frosted future rings)
     hp   A (cross-hatch) | B (hazard stripe) | C (drain core)
     wave A (queue tickets, top-left) | B (rim belt) | None (E10 arcs)
     colour True (reduced set applied) | False (E10 colours)
"""
import sys, os, math, copy
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import asm_r2 as A
A.setup()
import gramlib as GL
from gramlib import *
import cv_lib
from cv_lib import C, RS, W, H, L2, ppx, KCOL, NOW
import build10 as B10
import wc2, wc2_run as WCR
import wr2_units as W2U, wr_units as WU, wr_geo, wr2_lib, wr2_cells, wr_cells
import r2_arcs as A2, o_arcs, r2_misc as M2, r2_ground as G2, o_ground as OG
import hud2
import cv_board as CB
import e8lib as E8
import r2_glyphs as RG
import asm_tokens as TK
import wr2_sets

CFG = dict(time='A', hp='A', wave='A', colour=True, lanes_out=True)
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png'

SLATE = {'Packet': (61, 84, 102), 'Worm': (75, 74, 110), 'Jammer': (45, 93, 105), 'Payload': (91, 85, 96), 'Ring': (85, 97, 122)}
ORIG = {}


def patch_all(name, new):
    """replace every module-level binding of the E10 function `name` (the same object) by `new`"""
    old = ORIG.get(name)
    if old is None:
        return
    for m in list(sys.modules.values()):
        if m is not None and getattr(m, name, None) is old:
            try:
                setattr(m, name, new)
            except Exception:
                pass


def keep(mod, name):
    ORIG[name] = getattr(mod, name)
    return ORIG[name]


T = lambda: CFG['time']
HOT, COLD, FAR = 0, 1, 2


# ============================================================================================ colours / washes
def kind_wash(kind, dep, ramp=None):
    base = SLATE.get(kind) or SLATE['Ring']
    if not CFG['colour']:
        return ORIG['kind_wash'](kind, dep, ramp)
    k = (0.0, 0.20, 0.38)[dep] if ramp is None else ramp[dep]
    sat = (1.0, 0.62, 0.38)[dep]
    lum = 0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]
    g = tuple(lum + (base[i] - lum) * sat for i in range(3))
    return tuple(int(round(v + ((10, 8, 30)[i] - v) * k * 0.9)) for i, v in enumerate(g))


# ============================================================================================ unit cell outline + token ring
def cell_marker_pos(u):
    ri, ro = CB.ring_geom(u['dep'])
    a = 60 * u['s'] - 30 + 9.5
    return ppx(C, ri + 10.5, a), a


def outline(L, u, col=None, w=None):
    if col is not None or not CFG['colour']:
        return ORIG['outline'](L, u, col, w)
    k = u['dep']
    poly = WU.u_poly(u)
    pp = poly + [poly[0]]
    t = T()
    if t == 'A':
        ww = (4.0, 2.6, 2.0)[k]
    else:
        ww = (3.8, 2.8, 2.2)[k]
    c = grade(ENAMEL, k)
    L.line(pp, INK, (4.0 if k < 2 else 3.0) + 4.5 if t == 'A' else ww + 4.5)
    if t == 'A' and k == FAR:
        dotted(L, poly, c, dia=4.0, pitch=9.0, ink=False, closed=True)
    else:
        L.line(pp, c, ww)
    if k == HOT and t == 'A':
        glow_line(L, pp, ENAMEL, ww + 3, blur=4, strength=0.40)
        L.line(pp, ENAMEL, ww)
    (x, y), a = cell_marker_pos(u)
    if t == 'A':
        if k == HOT:
            end_notch(L, x, y, 0, col=ENAMEL, s=5.6)
        else:
            pips(L, x - (5 * (k - 1)), y, k, 90, 10.0, 3.0)
    elif t == 'B':
        dial(L, x, y, k, r=6.8)


def tok_ring(L, x, y, R, dep, dead=False):
    if not CFG['colour']:
        return ORIG['ring'](L, x, y, R, dep, dead)
    col = (150, 150, 160) if dead else grade(ENAMEL, dep)
    w = (3.0, 2.4, 2.0)[dep]
    WU._ring_full(L, x, y, R - w / 2, w, col)


def lane_base_style(L, x, y, r, dep, fillcol):
    if not CFG['colour']:
        return ORIG['lane_base_style'](L, x, y, r, dep, fillcol)
    L.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * 0.72) for v in fillcol) + (255,))
    L.ellipse([x - r, y - r, x + r, y + r], outline=grade(ENAMEL, dep), w=(2.6, 2.2, 1.8)[dep])


# ============================================================================================ chevrons (threat family)
def stack(L, u, ang, n_solid, n_hollow, dim=0.0):
    if not CFG['colour']:
        return ORIG['stack'](L, u, ang, n_solid, n_hollow, dim)
    k = u['dep']
    n = n_solid + n_hollow
    st = W2U.chev_params(u, n)
    ri, ro = CB.ring_geom(u['dep'])
    col = grade(HARM_UP, k)
    pt = E8.pt

    def cp(i):
        r = ri + st['start'] + i * st['pitch']
        return [pt(r + st['depth'], ang, -st['half']), pt(r, ang, 0), pt(r + st['depth'], ang, st['half'])]
    if k == HOT:
        for i in range(n):
            glow_line(L, cp(i), HARM, st['w'] + 2, blur=3, strength=0.30)
    for i in range(n_hollow):       # growth to come: hollow V, solid channel (no dash)
        p = cp(n_solid + i)
        L.line(p, INK, st['w'] + 4.5)
        L.line(p, col, st['w'])
        L.line(p, INK, max(1.4, st['w'] - 3.4))
    ww = (6.0, 5.0, 4.4)[k] if T() != 'A' else (6.0, 4.8, 4.0)[k]
    for col_, w in ((INK, ww + 4.5), (col, ww)):
        for i in range(n_solid):
            L.line(cp(i), col_, w)
    r = ri + st['start'] + (n - 1) * st['pitch'] + st['depth'] + 5.25 + 1.2
    a, b = pt(r, ang, -15), pt(r, ang, 15)
    L.line([a, b], INK, 3.8)
    L.line([a, b], mixc(col, BED, 0.1), 1.4)


# ============================================================================================ landing arcs
CUR = {'k': 0}


def a2_frame(L, r, a0, a1, lane, opt):
    if not CFG['colour']:
        return ORIG['frame'](L, r, a0, a1, lane, opt)
    k = CUR['k']
    HALF = A2.HALF
    da = 57.3 / r
    cap = HALF * da
    n = max(8, int((a1 - a0) / 3))
    ae = a1 - 0.9 * HALF * da
    outer = [ppx(C, r + HALF, a0 + cap + (ae - a0 - cap) * i / n) for i in range(n + 1)]
    inner = [ppx(C, r - HALF, ae - (ae - a0 - cap) * i / n) for i in range(n + 1)]
    tipp = [ppx(C, r, a1)]
    start = [ppx(C, r + HALF * math.cos(math.radians(t)), a0 + cap - cap * math.sin(math.radians(t))) for t in range(0, 181, 20)]
    pts = outer + tipp + inner + start
    L.poly(pts, fill=(7, 9, 17, 214))
    c = grade(ENAMEL, k)
    t = T()
    ww = (3.0, 2.2, 1.8)[k]
    L.line(pts + [pts[0]], INK, 6.4)
    if t == 'A' and k == FAR:
        dotted(L, pts, c, dia=3.6, pitch=8.5, ink=False, closed=True)
    else:
        if t == 'A' and k == HOT:
            glow_line(L, pts + [pts[0]], ENAMEL, 5, blur=4, strength=0.35)
        L.line(pts + [pts[0]], c if not (t == 'A' and k == HOT) else ENAMEL, ww)


def a2_marks(L, r, th, px, k):
    """the time mark on a landing arc's start cap: A = END notch (HOT) / pips (COLD, FAR); B = fuse dial; C = pips"""
    t = T()
    fr = A2.Fr(r, th, px)
    if t == 'B':
        dial(L, fr.x, fr.y, k, r=8.0)
        return 22
    if k == HOT:
        end_notch(L, fr.x, fr.y, th + 90, col=HARM_UP, s=7.0)
        return 22
    pips(L, fr.x - 5 * (k - 1) * 0 , fr.y, k, 90 + th * 0, 11.0, 3.4) if False else None
    for i in range(k):
        fd = A2.Fr(r, th, px + i * 11)
        L.ellipse([fd.x - 4.8, fd.y - 4.8, fd.x + 4.8, fd.y + 4.8], fill=INK)
        L.ellipse([fd.x - 3.2, fd.y - 3.2, fd.x + 3.2, fd.y + 3.2], fill=TMID)
    return 11 * k + 8


def landing_arcs(L, f, sel, only=None, extra=None):
    if not CFG['colour']:
        return ORIG['landing_arcs'](L, f, sel, only, extra)
    items = A2.layout_items(f, only, extra)
    S = lambda key: sel.get(key, 'P')
    for it in items:
        u, k = it['u'], it['k']
        CUR['k'] = k
        r = A2.LANE_R[min(it['lane'], 2)]
        a0, a1 = it['a0'], it['a1']
        lane = A2.LANE[u['dep']]
        a2_frame(L, r, a0, a1, lane, S('frame'))
        wd = A2.disc(L, r, a0, 22, u, lane, S('disc'))
        px = 22 + wd / 2 + 3
        if u.get('wear'):
            px += A2.wear(L, r, a0, px + 12, S('wear'))
        if f.get('twr') and f['twr'][1] and f['twr'][0] == u['dep'] and k > 0:
            px += A2.twist_mark(L, r, a0, px + 13, S('twist'), f['twr'][1]) + 2
        px += a2_marks(L, r, a0, px + 11, k)
        ng = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
        ns = u['land_hit'] - ng
        for q in range(u['w']):
            sec = (it['s0'] + q) % 6
            th = 60 * (it['s0'] + q)
            thr = u['land_through'].get(str(sec), 0)
            sk = u['land_soak'].get(str(sec), 0)
            br = u['land_brace'].get(str(sec), 0)
            A2.REG['arcs'].append(dict(uid=u['id'], sector=sec, solid=ns, hollow=ng, diamonds=thr, soak=sk, brace=br, check=int(not thr and not br and not sk), k=k, now_dot=int(k == 0), wear=int(bool(u.get('wear'))), lane=it['lane']))
            n_items = ns + ng
            wch = A2.chev_width(n_items, S('achev'))
            gap = 14
            wdi = A2.diam_width(thr, S('diam')) + sk * 24 + (26 if br else 0) + (26 if (not thr and not br and not sk) else 0)
            tot = wch + gap + wdi
            x0 = -tot / 2
            arc_chevrons(L, r, th, x0, ns, ng, S('achev'), k)
            x1 = x0 + wch + gap
            if br:
                A2.brace_mark(L, r, th, x1, S('brace'))
                x1 += 26
            if thr:
                arc_diamonds(L, r, th, x1, thr, S('diam'), k)
                x1 += A2.diam_width(thr, S('diam'))
            for i in range(sk):
                A2.soak_mark(L, r, th, x1, S('soak'))
                x1 += 24
            if not thr and not br and not sk:
                A2.check_mark(L, r, th, x1, S('check'))
    return items


def arc_chevrons(L, r, th, x0, ns, ng, opt, k):
    p = A2.CH[opt]
    col = grade(HARM_UP, k)
    for i in range(ng + ns):
        hollow = i >= ns
        xc = x0 + p['pitch'] / 2 + i * p['pitch']
        fr = A2.Fr(r, th, xc)
        q = [fr.q(-p['hw'], p['dp'] / 2), fr.q(0, -p['dp'] / 2), fr.q(p['hw'], p['dp'] / 2)]
        if hollow:
            L.line(q, INK, p['ink'] + 2.2)
            L.line(q, col, p['col'] + 1.8)
            L.line(q, INK, max(1.6, p['col'] - 1.8))
        else:
            if k == HOT:
                glow_line(L, q, HARM, p['col'] + 1, blur=3, strength=0.30)
            L.line(q, INK, p['ink'])
            L.line(q, col, p['col'])


def arc_diamonds(L, r, th, x0, n, opt, k):
    d = A2.DI[opt]
    col = grade(HARM_UP, k)
    for i in range(n):
        fr = A2.Fr(r, th, x0 + d['pitch'] / 2 + i * d['pitch'])
        A2.diamond(L, fr.x, fr.y, d['rw'], d['rh'], fill=col, ink=2.6)


def arc_wear(L, r, th, px, opt):
    fr = A2.Fr(r, th, px)
    hl, hh = 10.0, 5.6
    core = A2.rseg(fr, hl - 2.6, hh - 2.6, 0.6, 2)
    seg_shape(L, core, 2.6, 'harm', pitch=3.6, lw=1.2, opt=CFG['hp'])
    return 2 * hl + 8


# ============================================================================================ threat trim on the tower rim
def trim2(kind='A', R=139.5):
    def trim(L, f):
        seen = {}
        for u in f['units']:
            fz = u['fate']
            if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
                continue
            for (sec, sl, hit, tohp) in fz['hits']:
                seen.setdefault(sec, set()).add(fz['k'])
        t = T()

        def arc(a0, a1, k):
            pts = L.arc_pts(C, R, a0, a1)
            if not CFG['colour']:
                return ORIG_TRIM_ARC(L, pts, k)
            c = grade(HARM, k)
            if k == 0:
                if t == 'A':
                    glow_line(L, pts, HARM, 11, blur=4, strength=0.40)
                L.line(pts, INK, 6 + 4.4)
                L.line(pts, HARM_UP if t == 'A' else HARM, 6)
            elif k == 1:
                L.line(pts, INK, 4 + 4.4)
                L.line(pts, c, 3.6)
            else:
                L.line(pts, INK, 3.4 + 4.4)
                if t == 'A':
                    dotted(L, pts, c, dia=3.4, pitch=7.0, ink=False)
                else:
                    L.line(pts, c, 2.6)
        for sec, ks in seen.items():
            mm = 60 * sec
            zones = {2: (-26.5, -9.5), 1: (-8.5, 8.5), 0: (9.5, 26.5)}
            for k in sorted(ks):
                arc(mm + zones[k][0], mm + zones[k][1], k)
    return trim


def ORIG_TRIM_ARC(L, pts, k):
    pass


# ============================================================================================ HP: tower ring + slice pips
def pip(L, st, r, a0, a1, w=7.0):
    rad = 2.6
    da = math.degrees(rad / r)
    b0, b1 = a0 + da, a1 - da
    hw = max(0.6, w / 2 - rad)
    core = L.band(C, r - hw, r + hw, b0, b1)
    m = {'lit': 'lit', 'harm': 'harm', 'soak': 'soak', 'mend': 'mend', 'gone': 'gone'}[st]
    tick = None
    if st == 'mend':
        am = (a0 + a1) / 2
        x, y = ppx(C, r + w / 2 + 3.5, am)
        tick = [(x, y - 2.6), (x + 2.6, y + 1.4), (x - 2.6, y + 1.4)]
        a_ = math.radians(am)
        ux, uy = math.sin(a_), -math.cos(a_)
        tick = [(x + ux * 2.6, y + uy * 2.6), (x - ux * 1.4 - uy * 2.6, y - uy * 1.4 + ux * 2.6), (x - ux * 1.4 + uy * 2.6, y - uy * 1.4 - ux * 2.6)]
    seg_shape(L, core, rad, m, ink_w=1.3, pitch=3.4 if w < 8 else 4.0, lw=1.25, tick_pts=tick, opt=CFG['hp'])


def hp_ring2(kind='A', r0=150.0, r1=157.0, off=0.0):
    def ring(L, hp, hp_after, mx):
        L.poly(L.band(C, r0 - 1.6, r1 + 1.6, 0, 359.9), fill=(4, 5, 9, 255))
        rc, w = (r0 + r1) / 2, r1 - r0
        n_per = 5
        ngrp = mx // n_per
        g1, g2 = 2.5, 9.0
        seg = (360 / ngrp - g2 - (n_per - 1) * g1) / n_per
        taken = max(0, hp - hp_after)
        for i in range(mx):
            grp, j = divmod(i, n_per)
            a0 = off + grp * 360 / ngrp + g2 / 2 + j * (seg + g1)
            # the pending run starts at the needle and runs clockwise; kept next; gone last
            st = 'harm' if i < taken else ('lit' if i < taken + hp_after else 'gone')
            pip(L, st, rc, a0, a0 + seg, w)
    return ring


def hatch(L, s, a_lo, a_hi, r0, r1, alpha_dim=0.35, col=INK, icon_r=27, rc=95.5, hcol=HARM):
    """slice about to break: dim + hatch (both directions, A / C) or hazard stripe (B), clear disc round the icon"""
    k = L.k
    lay = Image.new('RGBA', L.im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    band = L.band(C, r0, r1, a_lo, a_hi)
    pp = [(x * k, y * k) for x, y in band]
    d.polygon(pp, fill=col + (int(255 * alpha_dim),))
    mk = Image.new('L', L.im.size, 0)
    md = ImageDraw.Draw(mk)
    xs = [p[0] for p in band]
    ys = [p[1] for p in band]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    hh = (y1 - y0)
    optn = CFG['hp']
    pitch, lw = (7.0, 2.0) if optn != 'B' else (11.0, 4.6)
    t = x0 - hh
    while t < x1 + hh:
        md.line([(t * k, y1 * k), ((t + hh) * k, y0 * k)], fill=255, width=int(lw * k))
        t += pitch
    if optn != 'B':
        t = x0 - hh
        while t < x1 + hh:
            md.line([(t * k, y0 * k), ((t + hh) * k, y1 * k)], fill=255, width=int(lw * k))
            t += pitch
    pm = Image.new('L', L.im.size, 0)
    ImageDraw.Draw(pm).polygon(pp, fill=255)
    ix, iy = ppx(C, rc, 60 * s)
    ImageDraw.Draw(pm).ellipse([(ix - icon_r) * k, (iy - icon_r) * k, (ix + icon_r) * k, (iy + icon_r) * k], fill=0)
    mk = Image.fromarray(np.minimum(np.asarray(mk), np.asarray(pm)))
    h = Image.new('RGBA', L.im.size, hcol + (255,))
    h.putalpha(mk.point(lambda v: int(v * 0.70)))
    lay.alpha_composite(h)
    a = np.asarray(lay.split()[3]).copy()
    cm = Image.new('L', L.im.size, 255)
    ImageDraw.Draw(cm).ellipse([(ix - icon_r) * k, (iy - icon_r) * k, (ix + icon_r) * k, (iy + icon_r) * k], fill=0)
    lay.putalpha(Image.fromarray((a * (np.asarray(cm) / 255.0)).astype(np.uint8)))
    L.im.alpha_composite(lay)


# ============================================================================================ HP: enemy tray ticks
def hp_row(L, u, hp, mx, lose=0, shield=0, shmx=0):
    ly = W2U.cell_layout(u)
    r0, r1 = ly['r0'], ly['r1']
    wp, gp = 18.0, 4.0
    W2U.ST.PIPS[u['id']] = []
    w = u['w']
    per = max(1, mx // w)
    idx = 0
    for q in range(w):
        a_start, tot, rm = W2U.tray_extent(u, q, per, wp, gp)
        tray = W2U.arc_band(ly['t_in'], ly['t_out'], a_start - math.degrees(2.2 / rm), a_start + math.degrees((tot + 2.2) / rm))
        L.poly(tray, fill=(8, 10, 20, 255), outline=INK, w=1.4)
        for i in range(per):
            lit = idx < hp
            lost = lit and idx >= hp - lose
            aa = a_start + math.degrees(i * (wp + gp) / rm)
            ab = aa + math.degrees(wp / rm)
            rad = 2.2
            da = math.degrees(rad / rm)
            core = W2U.arc_band(r0 + rad, r1 - rad, aa + da, ab - da)
            st = 'ours' if lost else ('enemy' if lit else 'gone')
            seg_shape(L, core, rad, st, ink_w=1.0, pitch=3.6, lw=1.2, opt=CFG['hp'], glow=False)
            W2U.ST.PIPS[u['id']].append((aa, ab, r0, r1, lit))
            idx += 1
    if shmx:
        W2U.shield_bracket(L, u, r0, r1, shield, shmx)


def armour_rails(L, u):
    """L10 double line: two solid steel strokes with a 3 px gap along the cell's outer edge, over the tray (armor = reduces each hit)"""
    ly = W2U.cell_layout(u)
    per = max(1, u['mx'] // u['w'])
    for q in range(u['w']):
        a_s, tot, rm = W2U.tray_extent(u, q, per)
        a0 = a_s - math.degrees(2.4 / rm)
        a1 = a_s + math.degrees((tot + 2.4) / rm)
        for rr, wd, c in ((ly['t_out'] - 0.2, 2.2, STEEL_HI), (ly['t_out'] - 5.0, 2.2, STEEL)):
            pts = L.arc_pts(C, rr, a0, a1, 20)
            L.line(pts, INK, wd + 2.4)
        for rr, wd, c in ((ly['t_out'] - 0.2, 2.2, STEEL_HI), (ly['t_out'] - 5.0, 2.2, STEEL)):
            pts = L.arc_pts(C, rr, a0, a1, 20)
            L.line(pts, c, wd)


# ============================================================================================ HUD segments
def hud_seg(L, x, y, kind, w=hud2.SEGW, h=hud2.SEGH, al=255):
    if not CFG['colour']:
        return ORIG['hud_seg'](L, x, y, kind, w, h, al)
    box = [x, y - h / 2, x + w, y + h / 2]
    cold = (al == 153)
    if kind == 'gone':
        L.rect(box, fill=(8, 14, 22, al), outline=hud2.TLO + (al,), w=1.4, r=3)
        return
    if kind in ('lose', 'soak') and not cold:
        core = [(x + 3, y - h / 2 + 3), (x + w - 3, y - h / 2 + 3), (x + w - 3, y + h / 2 - 3), (x + 3, y + h / 2 - 3)]
        seg_shape(L, core, 3.0, 'harm' if kind == 'lose' else 'soak', ink_w=1.2, pitch=3.8, lw=1.2, opt=CFG['hp'], glow=(w >= 9))
        return
    if kind in ('lose', 'through', 'ptl', 'soak') and cold:
        core = [(x + 3, y - h / 2 + 3), (x + w - 3, y - h / 2 + 3), (x + w - 3, y + h / 2 - 3), (x + 3, y + h / 2 - 3)]
        seg_shape(L, core, 3.0, 'cold_soak' if kind == 'soak' else 'cold_harm', ink_w=1.0)
        return
    ORIG['hud_seg'](L, x, y, kind, w, h, al)


# ============================================================================================ gunmetal bezel, tower pink, guns
def dash_line(L, p0, p1, col, w, dash=(12, 6), ink_w=None, alpha=255):
    """gun tracer: one solid stroke (the player's gun): ink keyline + pink, round ends"""
    if not CFG['colour']:
        return ORIG['dash_line'](L, p0, p1, col, w, dash, ink_w, alpha)
    lay = L if alpha == 255 else L2()
    lay.line([p0, p1], INK + (alpha,), w + 4.4)
    lay.line([p0, p1], PINK + (alpha,), w)
    for p in (p0, p1):
        lay.ellipse([p[0] - w / 2 - 1, p[1] - w / 2 - 1, p[0] + w / 2 + 1, p[1] + w / 2 + 1], fill=PINK + (alpha,))
    if alpha != 255:
        L.im.alpha_composite(lay.im)


def install():
    if ORIG:
        return
    keep(wr_geo, 'kind_wash'); keep(W2U, 'outline'); keep(W2U, 'ring'); keep(W2U, 'stack'); keep(W2U, 'hp_row')
    keep(W2U, 'armour_rails'); keep(wc2, 'pip'); keep(wc2, 'hp_ring2'); keep(wc2, 'hatch'); keep(wc2, 'trim2'); keep(wc2, 'dash_line')
    keep(A2, 'frame'); keep(A2, 'landing_arcs'); keep(A2, 'wear'); keep(o_arcs, 'lane_base_style'); keep(hud2, 'seg')
    ORIG['hud_seg'] = ORIG['seg']
    patch_all('kind_wash', kind_wash)
    W2U.outline = outline
    W2U.ring = tok_ring
    W2U.stack = stack
    W2U.hp_row = hp_row
    W2U.armour_rails = armour_rails
    wc2.pip = pip
    wc2.hp_ring2 = hp_ring2
    wc2.hatch = hatch
    wc2.trim2 = trim2
    WCR.E.trim2 = trim2
    WCR.E.hp_ring2 = hp_ring2
    wc2.dash_line = dash_line
    A2.landing_arcs = landing_arcs
    A2.lane_base_style = lane_base_style
    A2.wear = arc_wear
    hud2.seg = hud_seg
    ORIG['hud_seg'] = ORIG['seg']


def colour_install():
    """reduced colour set: slate enemy kinds, gunmetal bezel, pink player, plan soak"""
    import wc_base
    GEO = wr_geo
    GEO.KIND_TABLE.clear()
    GEO.KIND_TABLE.update(SLATE)
    for k_, v_ in SLATE.items():
        KCOL[k_] = tuple(min(255, int(c * TK.KIND_TOKEN_F)) for c in v_)
    for i in range(3):
        wr2_lib.LANE_COL[i] = grade(ENAMEL, i)
        cv_lib.LANE[i]['col'] = grade(ENAMEL, i)
        cv_lib.LANE[i]['dash'] = None
    wr_geo.LANE[2]['dash'] = None
    G2.ENAMEL = GUN_A
    G2.BEZEL_HI = GUN_HI
    OG.BEZEL_HI = GUN_HI
    wc2.CYAN = PINK
    A.CB9.HUB['col'] = PINK
    hud2.SOAK = SOAKC
    TK.SOAK = SOAKC
    A2.SOAK = SOAKC
    tower_pink()


def tower_pink():
    import slicelib as SL
    for k in ("EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH"):
        SL.PROGRAMS[k]["col"] = PINK
