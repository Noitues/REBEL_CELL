"""the player wheel (tower hub + 6 slices + slice HP + player HP ring + threat trim) in the black-book hand.
render_tower(f, variant) -> RGBA PIL image TW x TW at 1x (centre at (TW/2, TW/2))."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from sg_lib import *
from sg_icons import *

TW = 346
CT = (TW / 2, TW / 2)
PAGE_R = 161.0
R_IN, R_OUT = 51.0, 123.0
ICON_R = 91.0
PIP_R = 130.0
TRIM_R = 140.0
RING_R0, RING_R1 = 150.0, 157.0

LANE1 = (176, 112, 108)     # COLD red (70 percent value, 45 percent chroma)
LANE2 = (128, 98, 100)      # FAR red (50 percent value, 25 percent chroma)

VAR = {
    'A': dict(page='dot', fill_ang=35, extrude=False, shine=False, hub='bubble', band='highlighter', constr=BLUE, wedge_edge=1.7, seed=11),
    'B': dict(page='graph', fill_ang=-58, extrude=True, shine=True, hub='burst', band='ink', constr=(86, 90, 104), wedge_edge=2.8, seed=23),
}


def wedge_poly_mask(cv, s, r0, r1, half, jitter=1.1):
    reg = cv.band_mask(CT, r0, r1, 60 * s - half, 60 * s + half)
    return warp(reg, jitter * cv.S, 26 * cv.S, cv.r)


def ang_of(s):
    return 60 * s


def hp_segments(hp, hp_after, mx=15):
    """15 segments, three groups of 5 clockwise from the 30 deg spoke; returns list of (a0, a1, state)"""
    out = []
    ngrp, per = 3, 5
    gap_g, gap_s = 9.0, 2.6
    gspan = 360.0 / ngrp - gap_g
    seg = (gspan - (per - 1) * gap_s) / per
    for i in range(mx):
        g, j = divmod(i, per)
        a0 = 30 + g * 120 + gap_g / 2 + j * (seg + gap_s)
        st = 'lit' if i < hp_after else ('harm' if i < hp else 'gone')
        out.append((a0, a0 + seg, st))
    return out


def seg_region(cv, r0, r1, a0, a1):
    return cv.band_mask(CT, r0, r1, a0, a1, step=0.6)


def draw_block(cv, r, w, a0, a1, state, V, soak=False, ink_w=1.7):
    """one HP block (painted).  state lit | harm | soak | mend | gone"""
    S = cv.S
    rc = r
    cr = lambda px: math.degrees(px / rc)
    reg = cv.band_mask(CT, rc - w / 2, rc + w / 2, a0, a1, step=0.5)
    reg = warp(reg, 0.45 * S, 6 * S, cv.r)
    solid = np.clip((ndi.gaussian_filter(reg, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(solid, S, ink_w), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    if state == 'gone':
        cv.over(solid, (14, 16, 22), 0.95)
        cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 0.9), 0.3) * 1.5, 0, 1), (120, 126, 140), 0.9)
        return
    if state == 'harm':
        gl = ndi.gaussian_filter(solid, 2.6 * S)
        cv.over(np.clip(gl * 1.6, 0, 1), HARM, 0.34)
    cv.over(ring, INK, 0.98)
    if state == 'lit':
        fm = np.roll(np.roll(solid, int(0.7 * S), 0), int(0.5 * S), 1)
        n = smooth(*fm.shape, 3 * S / 4 * 1.5, cv.r)
        cv.over(np.clip(fm * (0.94 + 0.06 * n), 0, 1), GAIN, 0.97)
        hl = np.roll(solid, int(-1.2 * S), 0) * (1 - np.roll(solid, int(-0.2 * S), 0)) * 0
        # marker highlight streak
        pts = [pol(CT, rc - w * 0.18, a0 + (a1 - a0) * 0.12), pol(CT, rc - w * 0.18, a0 + (a1 - a0) * 0.62)]
        marker(cv, pts, (214, 255, 214), w=1.3, alpha=0.5, wob=0.1, grain=0.0, rough=0.0, taper=(0.1, 0.4))
    else:
        col = {'harm': HARM, 'soak': SOAK, 'mend': GAIN}[state]
        cv.over(solid, (14, 14, 22), 0.97)
        inner = np.clip(ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.0 * S))).astype(np.float32), 0, 1)
        if state in ('harm', 'soak'):
            hatch_region(cv, inner, 0, 0, col, ang=45, pitch=2.9, w=1.15, alpha=0.95, over=0.0, jit=0.1, cross=True)
            edge = np.clip(ndi.gaussian_filter(outline_mask(inner, S, 1.0, inner=1.0), 0.3) * 1.6, 0, 1)
            cv.over(edge, col, 0.98)
            if state == 'soak':     # 5 px chevron notch cut into the outer edge
                am = (a0 + a1) / 2
                x, y = pol(CT, rc + w / 2 + 0.2, am)
                x2, y2 = pol(CT, rc - 0.2, am)
                tg = (math.cos(math.radians(am)), math.sin(math.radians(am)))
                p = [(x + tg[0] * 4.2, y + tg[1] * 4.2), (x2, y2), (x - tg[0] * 4.2, y - tg[1] * 4.2)]
                ballpoint(cv, p, INK, 2.2, 1.0, wob=0.0, wl=9, taper=(0, 0))
        else:    # mend: dark socket + gain outline + plus
            edge = np.clip(ndi.gaussian_filter(outline_mask(inner, S, 1.1, inner=1.1), 0.3) * 1.6, 0, 1)
            cv.over(edge, GAIN, 0.98)
            am = (a0 + a1) / 2
            x, y = pol(CT, rc, am)
            ballpoint(cv, [(x - 3.4, y), (x + 3.4, y)], GAIN, 1.5, 1.0, wob=0, taper=(0, 0))
            ballpoint(cv, [(x, y - 3.4), (x, y + 3.4)], GAIN, 1.5, 1.0, wob=0, taper=(0, 0))


def slice_pip_states(w):
    mx, hp, ha, sk = w['mx'], w['hp'], w.get('hp_after', w['hp']), w.get('soaked', 0)
    out = []
    for i in range(mx):
        if i < ha and i < hp:
            out.append('lit')
        elif i < ha:
            out.append('mend')
        elif i < hp:
            out.append('soak' if (hp - 1 - i) < sk else 'harm')
        else:
            out.append('gone')
    return out


def trim_data(f):
    seen = {}
    for u in f['units']:
        fz = u['fate']
        if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
            continue
        for (sec, sl, hit, tohp) in fz['hits']:
            seen.setdefault(sec, set()).add(fz['k'])
    return seen


def draw_trim(cv, f):
    """T family: stencil, flat colour, hard ink keyline, no texture.  HOT = filled + glow + END notch; COLD = thinner, desaturated, one bead; FAR = dotted, two beads"""
    S = cv.S
    zones = {2: (-26.5, -9.5), 1: (-8.5, 8.5), 0: (9.5, 26.5)}
    for sec, ks in trim_data(f).items():
        mm = 60 * sec
        for k in sorted(ks):
            a0, a1 = zones[k]
            a0 += mm; a1 += mm
            if k == 0:
                reg = cv.band_mask(CT, TRIM_R - 3.2, TRIM_R + 3.2, a0, a1, step=0.5)
                gl = ndi.gaussian_filter(reg, 3.0 * S)
                cv.over(np.clip(gl * 1.6, 0, 1), HARM, 0.38)
                k1 = np.clip(ndi.gaussian_filter(outline_mask(reg, S, 2.2), 0.4) * 1.5, 0, 1)
                cv.over(k1, INK, 1.0)
                cv.over(reg, HARM, 1.0)
                # END notch: 8 px wedge notch toward the tower
                am = (a0 + a1) / 2
                tip = pol(CT, TRIM_R - 3.2 - 8.0, am)
                b0 = pol(CT, TRIM_R - 3.0, am - 3.2)
                b1 = pol(CT, TRIM_R - 3.0, am + 3.2)
                tri = cv.poly_mask([b0, b1, tip])
                cv.over(np.clip(ndi.gaussian_filter(outline_mask(tri, S, 1.8), 0.4) * 1.5, 0, 1), INK, 1.0)
                cv.over(tri, HARM, 1.0)
            elif k == 1:
                reg = cv.band_mask(CT, TRIM_R - 2.0, TRIM_R + 2.0, a0, a1, step=0.5)
                cv.over(np.clip(ndi.gaussian_filter(outline_mask(reg, S, 1.6), 0.4) * 1.5, 0, 1), INK, 0.95)
                cv.over(reg, LANE1, 1.0)
                bx, by = pol(CT, TRIM_R + 7.5, a0 + 1.5)
                cv.over(cv.circle_mask((bx, by), 2.0), TEXT_MID, 1.0)
            else:   # dotted
                n = int(math.radians(a1 - a0) * TRIM_R / 8.2)
                for i in range(n + 1):
                    a = a0 + (a1 - a0) * i / max(1, n)
                    p = pol(CT, TRIM_R, a)
                    cv.over(cv.circle_mask(p, 3.4), INK, 0.95)
                    cv.over(cv.circle_mask(p, 2.1), LANE2, 1.0)
                for j in range(2):
                    bx, by = pol(CT, TRIM_R + 7.5, a0 + 1.5 + j * 3.2)
                    cv.over(cv.circle_mask((bx, by), 2.0), TEXT_MID, 1.0)


TEXT_MID = (175, 192, 214)


def draw_wedges(cv, f, V):
    S = cv.S
    r = cv.r
    for w in f['wheel']:
        s = w['sector']
        hp, ha = w['hp'], w.get('hp_after', w['hp'])
        reg = wedge_poly_mask(cv, s, R_IN, R_OUT, 26.0)
        solid = np.clip((ndi.gaussian_filter(reg, 0.5) - 0.5) * 6, 0, 1)
        ang = V['fill_ang'] + r.uniform(-9, 9) + (60 * s if V['extrude'] else 0) * 0
        if V['extrude']:
            # 3D block: shifted copy in ink with hand hatch, heavy chisel outline
            ex = np.zeros_like(solid)
            for k in range(1, int(5.5 * S) + 1):
                ex = np.maximum(ex, np.roll(np.roll(solid, int(k * 0.78), 0), int(k * 0.78), 1))
            ex = np.clip(ex - solid, 0, 1)
            ex = warp(ex, 0.4 * S, 8 * S, r)
            cv.over(ex, INK, 0.97)
            hatch_region(cv, ex, 0, 0, (228, 222, 210), ang=135, pitch=3.1, w=0.8, alpha=0.5, over=0.2, jit=0.15)
        ink_edge(cv, solid, 0, 0, INK, V['wedge_edge'] * 1.25, 0.97, wob=0.9, rough='out')
        miss = (r.uniform(0.8, 2.0) * (1 if r.random() > .5 else -1), r.uniform(0.8, 1.8) * (1 if r.random() > .5 else -1))
        fill_region(cv, solid, 0, 0, PINK, ang=ang, nib=7.5, over=1.6, miss=miss, jit=0.5, clip=1.0)
        # darker shading hatch on the lower right edge (ballpoint)
        strip = np.clip(solid - np.roll(np.roll(solid, int(-7 * S), 0), int(-7 * S), 1), 0, 1)
        hatch_region(cv, strip, 0, 0, (120, 14, 70), ang=135, pitch=3.0, w=1.0, alpha=0.7, over=0.3, jit=0.2)
        # brush highlight strokes (light pink) near the upper left
        am = 60 * s
        for q in range(2):
            p0 = pol(CT, R_IN + 14 + q * 5, am - 23 + q * 2)
            p1 = pol(CT, R_OUT - 20 - q * 6, am - 19 + q * 3)
            marker(cv, [p0, p1], PINK_L, w=2.6, nib='chisel', ang=30, alpha=0.5, wob=0.5, taper=(0.15, 0.45))
        if V['shine']:   # graffiti shine: short white chisel strokes
            for q in range(3):
                p0 = pol(CT, R_IN + 8 + q * 3.8, am - 20 + q * 1.5)
                p1 = pol(CT, R_IN + 8 + q * 3.8 + 9 - q * 2, am - 17 + q * 1.4)
                marker(cv, [p0, p1], (255, 255, 255), w=1.7, nib='round', alpha=0.8, wob=0.1, taper=(0.1, 0.3))
        yield w, s, solid, am


def draw_slice_states(cv, f, V, wedges):
    S = cv.S
    for w, s, solid, am in wedges:
        hp, ha = w['hp'], w.get('hp_after', w['hp'])
        brk = hp > 0 and ha == 0
        soakd = bool(w.get('soaked'))
        if brk:
            col = SOAK if soakd else HARM
            # cross-hatch whole wedge, icon clearance disc
            ix, iy = pol(CT, ICON_R, am)
            clear = 1 - cv.circle_mask((ix, iy), 27)
            reg = solid * clear
            # a wash first (so it reads in greyscale), then hatch
            cv.over(reg, (20, 12, 30), 0.30)
            hatch_region(cv, reg, 0, 0, col, ang=45, pitch=5.2, w=1.9, alpha=0.93, over=1.0, jit=0.5, cross=True)
            edge = np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.0, inner=2.0), 0.4) * 1.5, 0, 1)
            cv.over(edge, col, 0.97)
        w['_brk'] = brk


def draw_break_x(cv, f):
    """stencil X in the outer corner (never over the icon)"""
    S = cv.S
    for w in f['wheel']:
        hp, ha = w['hp'], w.get('hp_after', w['hp'])
        if hp > 0 and ha == 0:
            col = SOAK if w.get('soaked') else HARM
            x, y = pol(CT, 109, 60 * w['sector'] + 19)
            for sg in (1, -1):
                p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
                ballpoint(cv, p, INK, 7.4, 1.0, wob=0.3, wl=9, taper=(0, 0))
            for sg in (1, -1):
                p = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
                marker(cv, p, col, w=4.4, alpha=1.0, wob=0.3, grain=0.05, taper=(0, 0))


def draw_pips(cv, f, V):
    for w in f['wheel']:
        s = w['sector']
        sts = slice_pip_states(w)
        n = len(sts)
        bl, bg = 35.0, 5.0
        tot = n * bl + (n - 1) * bg
        cr = lambda px: math.degrees(px / PIP_R)
        a = 60 * s - cr(tot) / 2
        for i, st in enumerate(sts):
            a0 = a + cr(i * (bl + bg))
            draw_block(cv, PIP_R, 8.0, a0, a0 + cr(bl), st, V, ink_w=1.5)


def draw_hp_ring(cv, f, V):
    S = cv.S
    segs = hp_segments(f['hp'], f['pv']['hp_after'], f['maxhp'])
    rc = (RING_R0 + RING_R1) / 2
    # band under the ring
    if V['band'] == 'highlighter':
        for g in range(3):
            a0 = 30 + g * 120 + 3.3
            a1 = 30 + (g + 1) * 120 - 3.3
            pts = arc_pts(CT, rc, a0, a1, 1.0)
            marker(cv, pts, PINK_L, w=12.5, nib='round', alpha=0.75, wob=0.4, wl=60, mode='mult', taper=(0.02, 0.02), grain=0.2)
    else:
        for g in range(3):
            a0 = 30 + g * 120 + 3.0
            a1 = 30 + (g + 1) * 120 - 3.0
            pts = arc_pts(CT, rc, a0, a1, 1.0)
            marker(cv, pts, INK, w=12.5, nib='round', alpha=0.96, wob=0.35, wl=60, taper=(0.02, 0.02), grain=0.08)
    for a0, a1, st in segs:
        draw_block(cv, rc, RING_R1 - RING_R0, a0, a1, st, V, ink_w=1.5)


def draw_hub(cv, V, name='BREAKER'):
    S = cv.S
    r = cv.r
    c = CT
    if V['hub'] == 'bubble':
        # throw-up bubble: scalloped outline
        pts = []
        nb = 11
        for i in range(nb * 14 + 1):
            a = i / (nb * 14) * 360
            bump = 1 + 0.085 * abs(math.sin(math.radians(a * nb / 2)))
            pts.append(pol(c, 41.5 * bump, a))
        reg = cv.poly_mask(pts)
        reg = warp(reg, 0.5 * S, 9 * S, r)
        solid = np.clip((ndi.gaussian_filter(reg, 0.5) - 0.5) * 6, 0, 1)
        sh = np.roll(np.roll(solid, int(3.2 * S), 0), int(3.2 * S), 1)
        cv.over(np.clip(sh - solid, 0, 1), INK, 0.96)
        cv.over(solid, PAPER, 1.0)
        # pink inner glow band
        ring = edge_ring(solid, S, 3.0)
        cv.over(np.roll(np.roll(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.6, inner=2.6), 0.3) * 1.5, 0, 1), int(0.0), 0), 0, 1), PINK, 0.0)
        ink_edge(cv, solid, 0, 0, INK, 2.2, 0.98, wob=0.6)
        inner = ndi.binary_erosion(solid > 0.5, iterations=int(4.2 * S)).astype(np.float32)
        ring2 = np.clip(ndi.gaussian_filter(outline_mask(inner, S, 2.4, inner=0.0), 0.3) * 1.2, 0, 1)
        marker(cv, arc_pts(c, 33.5, -150, 160, 1.0), PINK, w=2.6, alpha=0.95, wob=0.5, taper=(0.1, 0.1))
    else:
        pts = []
        n = 14
        for i in range(n * 2):
            a = i * 180 / n + 8
            pts.append(pol(c, 44 if i % 2 == 0 else 31.5, a))
        reg = cv.poly_mask(pts)
        reg = warp(reg, 0.5 * S, 9 * S, r)
        solid = np.clip((ndi.gaussian_filter(reg, 0.5) - 0.5) * 6, 0, 1)
        sh = np.roll(np.roll(solid, int(3.4 * S), 0), int(3.4 * S), 1)
        cv.over(np.clip(sh - solid, 0, 1), INK, 0.96)
        ink_edge(cv, solid, 0, 0, INK, 2.8, 0.98, wob=0.6)
        cv.over(solid, PAPER, 1.0)
        fill_region(cv, solid * (1 - np.roll(solid, 0, 0) * 0) * ndi.binary_erosion(solid > 0.5, iterations=int(3.2 * S)).astype(np.float32), 0, 0, PINK, ang=-30, nib=4.5, over=1.0, miss=(0.8, 0.8), alpha=0.7)
    # emblem: a lightning bolt in a hand-drawn ring (the Breaker), above the name
    ex, ey = c[0], c[1] - 15
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(bm, S, 1.5), 0.4) * 1.5, 0, 1), INK, 0.98)
    cv.over(np.roll(np.roll(bm, int(0.5 * S), 0), int(0.5 * S), 1), PINK, 0.98)
    # name
    if name:
        letters(cv, name, (c[0], c[1] + 12), 14.5, fill=INK if V['hub'] == 'bubble' else PAPER, ink=INK, extrude=0, ink_w=1.2 if V['hub'] != 'bubble' else 0.0, outline=V['hub'] != 'bubble', miss=(0, 0), wob=0.25, spacing=0.4)


def page_disc(cv, V):
    S = cv.S
    disc = cv.circle_mask(CT, PAGE_R)
    t, rim = torn_mask(cv, disc, rough=1.5, fringe=1.0)
    pap = paper_rgb(cv, V['page'], PAPER, pitch=11.0 if V['page'] == 'dot' else 12.0, strength=1.0)
    # soft vignette / page stain toward the rim
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    pap *= (1 - 0.06 * np.clip((rr - 110) / 50, 0, 1))[..., None]
    cv.over_rgb(t, pap)
    # lighter fibre rim
    cv.over(np.clip(rim, 0, 1) * 0.55, (252, 250, 244), 1.0)
    return t


def construction(cv, V):
    col = V['constr']
    r = cv.r
    cv_ = CT
    sketch_circle(cv, CT, 47.0, col, 0.85, passes=2, alpha=0.7)
    sketch_circle(cv, CT, 125.8, col, 0.85, passes=2, alpha=0.7)
    sketch_circle(cv, CT, 146.2, col, 0.7, passes=1, alpha=0.5)
    for k in range(6):
        a = 60 * k + 30
        sketch_line(cv, pol(CT, 18, a), pol(CT, 160.5, a), col, 0.85, passes=2, alpha=0.62, over=2.2)
        # ticks at the end
        for rr_ in (124, 148):
            p0 = pol(CT, rr_ - 3, a); p1 = pol(CT, rr_ + 3, a)
            ballpoint(cv, [pol(p0, 0, 0)] if False else [pol(CT, rr_, a - 1.6), pol(CT, rr_, a + 1.6)], col, 0.8, 0.6, wob=0.1, wl=8)
    # compass pivot cross
    sketch_line(cv, (CT[0] - 6, CT[1]), (CT[0] + 6, CT[1]), col, 0.8, alpha=0.6)
    sketch_line(cv, (CT[0], CT[1] - 6), (CT[0], CT[1] + 6), col, 0.8, alpha=0.6)


def tape_rim(cv, V):
    rim = 152.0
    ang = [30, 150, 270] if V['band'] == 'highlighter' else [30, 150, 270]
    for a in ang:
        c = pol(CT, rim + 2, a)
        rot = a - 90 + cv.r.uniform(-8, 8)
        tape(cv, c, 25, 10.5, rot + 90 - 90 + 90, col=(236, 226, 190) if V['band'] == 'highlighter' else (228, 232, 238), alpha=0.82)


def render_tower(f, variant='A', name='BREAKER', S=4):
    V = VAR[variant]
    cv = Canvas(TW, TW, S, seed=V['seed'])
    page_disc(cv, V)
    construction(cv, V)
    wedges = list(draw_wedges(cv, f, V))
    draw_slice_states(cv, f, V, wedges)
    # icons
    GN = {'BURST': 'BURST', 'TURRET': 'TURRET', 'SHIELD': 'SHIELD', 'REPAIR': 'REPAIR'}
    for w, s, solid, am in wedges:
        c = pol(CT, ICON_R, am)
        rot = {'BURST': 0, 'TURRET': 0, 'SHIELD': 0, 'REPAIR': 0}[w['t']]
        draw_icon(cv, GN[w['t']], c, 52, rot, shadow=((90, 10, 60), 0.55) if variant == 'B' else None)
    draw_break_x(cv, f)
    draw_pips(cv, f, V)
    draw_trim(cv, f)
    draw_hp_ring(cv, f, V)
    draw_hub(cv, V, name)
    tape_rim(cv, V)
    return cv.down(), cv


if __name__ == '__main__':
    import json, time
    t = time.time()
    J = json.load(open('D:/rc_scratch/combat_redesign/sketchbook_graffiti/state_e10.json'))
    f = J['f1']
    v = sys.argv[1] if len(sys.argv) > 1 else 'A'
    im, _ = render_tower(f, v)
    bg = Image.new('RGBA', im.size, (40, 28, 60, 255))
    bg.alpha_composite(im)
    bg.save('D:/rc_scratch/combat_redesign/sketchbook_graffiti/out/tower_%s.png' % v)
    print(time.time() - t)
