"""sp_tower: the SPIDER-PUNK COLLAGE player wheel.  The Cell cut its wheel out of a punk poster and pasted it up.
Variant A "POSTER": black photocopy disc with a scissor-cut spiked rim, six magenta cut-paper wedges with jagged lightning sides, yellow lightning shards between them,
Ben-Day halftone shading, white cut edges + black offset drops, ransom-note hub.
Variant B "GIG FLYER": newsprint disc with xerox-halftone shadow, cobalt shards, yellow-edged magenta wedges, hub = a vinyl record with a magenta label.
Grammar (HP ring, pips, break/brace/soak/trim marks) is the F1 grammar, reused unchanged."""
import math, sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import f1_tower as F
from f1_tower import (TW, CT, R_PAGE, R_HUB, R_IN, R_OUT, ICON_R, ICON_PX, PIP_R, TRIM0, TRIM1, SHADOW_DIR,
                      draw_hp_ring, draw_pips, draw_break_state, draw_brace_plate, draw_soak_mark, draw_trim, draw_hover_arcs,
                      solidify, bbox, wedge_mask)
from sp_lib import *
import f1_icons as FI

VARIANT = ['A']
F.KRAFT = (252, 206, 40)        # the brace clamp's tape strip is print-yellow in this style
HALF = 24.6


def V():
    return VARIANT[0]


# ------------------------------------------------------------------ page
def spiked_disc(cv, r_in, r_out, n, jit=0.0, rot=0.0):
    pts = burst_pts(CT, r_in, r_out, n, rot=rot, jit=jit, r=cv.r)
    return solid(warp(cv.poly_mask(pts), 0.45 * cv.S, 18 * cv.S, cv.r), cv.S)


def page_A(cv):
    S = cv.S
    m = spiked_disc(cv, 186.5, 193.5, 30, jit=0.012, rot=3)
    n = smooth(cv.H, cv.W, 14 * S / 4, cv.r)
    base = np.empty((cv.H, cv.W, 3), np.float32)
    base[:] = (30, 20, 46)
    base += n[..., None] * 3.0
    cut_layer(cv, m, base, edge=1.8, drop=(4.0, 5.0), drop_a=0.7)
    # purple Ben-Day patch on the margin and in the gaps (the poster background)
    rf = radial_field(cv, CT, 60, 196)
    ht = halftone(cv, np.clip(rf * 1.1 - 0.35, 0, 1), 4.6, 15)
    cv.over(ht * m, (150, 96, 235), 0.95)
    ht2 = halftone(cv, np.clip(1 - rf * 1.3, 0, 1) * 0.8, 4.6, 75)
    cv.over(ht2 * m, COB, 0.75)
    return m


def page_B(cv):
    S = cv.S
    m = spiked_disc(cv, 188.5, 192.5, 54, jit=0.01, rot=1)
    pap = paper_rgb(cv, 'plain', tuple(int(c * 0.80) for c in NEWS), strength=0.7)
    cut_layer(cv, m, pap, edge=1.8, drop=(4.0, 5.0), drop_a=0.7)
    # xerox shadow: black halftone growing toward the bottom right, magenta halftone top left
    f = linear_field(cv, (CT[0] - 120, CT[1] - 140), (CT[0] + 150, CT[1] + 170))
    cv.over(halftone(cv, np.clip((f - 0.25) * 1.4, 0, 1), 4.2, 45) * m, (30, 24, 40), 0.95)
    cv.over(halftone(cv, np.clip((0.55 - f) * 1.2, 0, 1), 4.2, 15) * m, MAG, 0.75)
    return m


def bolts(cv, m):
    """jagged lightning shards in the gaps between slices (under the wedges): they poke out of the page rim"""
    S = cv.S
    for k in range(6):
        a = 30 + 60 * k
        bm = lightning(cv, a, 54, 199, CT, w0=9.0 if V() == 'A' else 12.0, w1=5.5 if V() == 'A' else 8.0, zig=4.4 if V() == 'A' else 5.2, n=6, phase=1 if k % 2 == 0 else -1)
        bm = solid(warp(bm, 0.4 * S, 20 * S, cv.r), S)
        if V() == 'A':
            fill = np.empty((cv.H, cv.W, 3), np.float32)
            fill[:] = YEL
            rf = radial_field(cv, CT, 60, 200)
            ht = halftone(cv, np.clip(rf * 1.1 - 0.15, 0, 1), 3.6, 45)
            fill = fill * (1 - ht[..., None] * 0.55) + np.asarray(YEL_D, np.float32) * ht[..., None] * 0.55
            cut_layer(cv, bm, fill, edge=1.5, drop=(2.4, 3.2))
        else:
            fill = np.empty((cv.H, cv.W, 3), np.float32)
            fill[:] = COB
            rf = radial_field(cv, CT, 60, 200)
            ht = halftone(cv, np.clip(0.9 - rf * 0.8, 0, 1), 3.6, 45)
            fill = fill * (1 - ht[..., None] * 0.7) + np.asarray((120, 150, 255), np.float32) * ht[..., None] * 0.7
            cut_layer(cv, bm, fill, edge=1.5, drop=(2.4, 3.2))


def margin_scraps(cv):
    """newsprint and zine scraps pasted on the rim, in the gaps (angles with no pin): never over a pip, HP block or trim mark"""
    for i, a in enumerate((90, 150, 270, 330) if V() == 'A' else (90, 270, 330)):
        c = pol(CT, 184.0, a)
        rot = a + 90 + (6 if i % 2 else -5)
        scrap_text(cv, (c[0], c[1], 21, 9), rot, tint=NEWS if V() == 'A' else (236, 230, 214), seed=i + 3)


# ------------------------------------------------------------------ wedges
def wedge_poly(s, phase, zz=2.3):
    am = 60 * s
    pts = list(arc_pts(CT, R_OUT, am - HALF, am + HALF, 1.0))
    nz = 5
    for j in range(1, nz):
        r = R_OUT - (R_OUT - R_IN) * j / nz
        off = zz * (1 if (j + phase) % 2 else -1)
        pts.append(pol(CT, r, am + HALF + math.degrees(off / r)))
    pts += list(arc_pts(CT, R_IN, am + HALF, am - HALF, 1.0))
    for j in range(nz - 1, 0, -1):
        r = R_OUT - (R_OUT - R_IN) * j / nz
        off = zz * (1 if (j + phase + 1) % 2 else -1)
        pts.append(pol(CT, r, am - HALF + math.degrees(off / r)))
    return pts


def draw_wedge(cv, w):
    S = cv.S
    s = w['sector']
    am = 60 * s
    m = solid(warp(cv.poly_mask(wedge_poly(s, s)), 0.35 * S, 22 * S, cv.r), S)
    ic = pol(CT, ICON_R, am)
    d = np.array(SHADOW_DIR, np.float32)
    t = linear_field(cv, (ic[0] - d[0] * 75, ic[1] - d[1] * 75), (ic[0] + d[0] * 75, ic[1] + d[1] * 75))
    n = smooth(cv.H, cv.W, 2.0 * S / 4, cv.r)
    if V() == 'A':
        c0, c1, dots, edge_col = np.array(MAG, np.float32), np.array((236, 22, 128), np.float32), MAG_D, CUT
        edge = 2.1
    else:
        c0, c1, dots, edge_col = np.array((255, 70, 165), np.float32), np.array((244, 36, 140), np.float32), (170, 24, 150), YEL
        edge = 2.5
    fill = c0 + (c1 - c0) * t[..., None] + n[..., None] * 2.2
    ht = halftone(cv, np.clip((t - 0.28) * 1.5, 0, 1) * 0.95, 4.0, 45 + 9 * s)
    fill = fill * (1 - ht[..., None] * 0.9) + np.asarray(dots, np.float32) * ht[..., None] * 0.9
    if V() == 'B':        # xerox grit: a black halftone crescent on the inner end, toward the hub
        rf = 1 - radial_field(cv, CT, R_IN, R_IN + 40)
        g = halftone(cv, np.clip(rf * 0.9, 0, 1), 3.4, 15) * m
        fill = fill * (1 - g[..., None] * 0.8) + np.asarray((26, 18, 36), np.float32) * g[..., None] * 0.8
    xx, yy = grids(cv)
    ang_ = np.degrees(np.arctan2(yy - CT[1], xx - CT[0]))
    ray = (np.sin(np.radians(ang_) * 22.0) > 0.35).astype(np.float32) * np.clip(radial_field(cv, CT, R_IN, R_IN + 30), 0, 1)
    lighter = np.asarray(MAG_L if V() == 'A' else (255, 120, 190), np.float32)
    fill = fill * (1 - ray[..., None] * 0.22) + lighter * ray[..., None] * 0.22
    cut_layer(cv, m, fill, edge=edge, drop=(3.0, 4.2), edge_col=edge_col)
    sc = pol(CT, 160.0, am - 19.5)
    scrap_text(cv, (sc[0], sc[1], 18, 10), am - 19.5 + 90 - 8, tint=NEWS if V() == 'A' else (236, 230, 214), seed=s + 7)
    tp = pol(CT, 79.0, am + 18.5)
    tape(cv, tp, 18, 8, am + 18.5 + 90 + 20, col=(252, 206, 40), alpha=0.92)
    # a second thin ink line just inside the cut edge, hand-drawn, like a marker trace on the cut paper
    inner = ndi.binary_erosion(m > 0.5, iterations=max(1, int(1.6 * S))).astype(np.float32)
    ring = np.clip(ndi.gaussian_filter(outline_mask(inner, S, 0.9, inner=0.9), 0.3) * 1.5, 0, 1)
    cv.over(ring, (120, 8, 70) if V() == 'A' else (90, 10, 90), 0.55)
    return m


def draw_icon(cv, w, sol):
    """the E10 silhouettes cut out of white card: a print-yellow misregistered plate under an ink outline"""
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    ring = np.clip(ndi.gaussian_filter(outline_mask(full, S, 2.0), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    plate = np.roll(np.roll(dilate(full, 2.0, S), int(2.4 * S), 0), int(2.6 * S), 1)
    pc = YEL if V() == 'A' else COB
    cv.over(np.clip(plate - np.clip(full + ring, 0, 1), 0, 1), pc, 0.97, x0, y0)
    cv.over(ring, INK, 0.99, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), INK, 0.98, x0, y0)
        hatch_region(cv, np.clip(dark, 0, 1), x0, y0, (236, 232, 222), ang=45, pitch=3.0, w=0.8, alpha=0.5, over=0.0, jit=0.1)
    fm = np.roll(np.roll(wm, int(0.5 * S), 0), int(0.5 * S), 1)
    cv.over(np.clip(fm, 0, 1), WHITE, 0.99, x0, y0)
    return x0, y0, full


# ------------------------------------------------------------------ hub
def hub_A(cv, name):
    S = cv.S
    c = CT
    # yellow punk burst (cut paper) with a white edge, then a black disc, ransom-note letters and a bolt
    bm = solid(cv.poly_mask(burst_pts(c, 38.5, 47.0, 14, rot=8, jit=0.07, r=cv.r)), S)
    fill = np.empty((cv.H, cv.W, 3), np.float32)
    fill[:] = YEL
    ht = halftone(cv, np.clip(radial_field(cv, c, 20, 48) * 0.9, 0, 1), 3.4, 45)
    fill = fill * (1 - ht[..., None] * 0.55) + np.asarray(YEL_D, np.float32) * ht[..., None] * 0.55
    cut_layer(cv, bm, fill, edge=1.7, drop=(2.6, 3.4))
    disc = cv.circle_mask(c, 35.5)
    disc = solid(warp(disc, 0.3 * S, 14 * S, cv.r), S)
    cut_layer(cv, disc, (22, 16, 32), edge=1.5, drop=(1.5, 2.0))
    cv.over(halftone(cv, np.clip(1 - radial_field(cv, (c[0] - 12, c[1] - 14), 0, 40), 0, 1) * 0.55, 3.2, 15) * disc, MAG, 0.9)
    # bolt emblem
    ex, ey = c[0], c[1] - 17.5
    bolt = [(ex + 3.2, ey - 10), (ex - 6.0, ey + 1.5), (ex - 0.8, ey + 1.5), (ex - 3.6, ey + 10.5), (ex + 6.4, ey - 2.4), (ex + 0.8, ey - 2.4)]
    bm2 = cv.poly_mask(bolt)
    cv.over(dilate(bm2, 1.2, S), CUT, 1.0)
    cv.over(bm2, YEL, 1.0)
    if name:
        ransom(cv, name, (c[0], c[1] + 11.0), 11.2, rot=-3, spacing=0.4, seed=5)


def hub_B(cv, name):
    S = cv.S
    c = CT
    rec = solid(cv.circle_mask(c, 46.0), S)
    cut_layer(cv, rec, (20, 16, 26), edge=1.6, drop=(3.0, 4.0))
    xx, yy = grids(cv)
    rr = np.hypot(xx - c[0], yy - c[1])
    ang = np.degrees(np.arctan2(yy - c[1], xx - c[0]))
    groove = (np.sin(rr * 2.6) * 0.5 + 0.5) * np.clip((rr - 25) / 3, 0, 1) * (rr < 45.2)
    cv.over(groove * 0.16 * rec, (210, 205, 225), 1.0)
    for a0 in (-50, 130):                            # two sheen wedges, the record catching the light
        sh = np.clip(1 - np.abs(((ang - a0 + 180) % 360) - 180) / 16, 0, 1) * (rr > 25) * (rr < 45)
        cv.over(sh * 0.30 * rec, (255, 255, 255), 1.0)
    lab = solid(cv.circle_mask(c, 26.0), S)
    cut_layer(cv, lab, MAG, edge=1.4, drop=(1.0, 1.4), edge_col=YEL)
    cv.over(halftone(cv, np.clip(radial_field(cv, (c[0] - 10, c[1] - 12), 0, 44), 0, 1) * 0.7, 3.2, 45) * lab, MAG_D, 0.9)
    ex, ey = c[0], c[1] - 11.0
    bolt = [(ex + 2.6, ey - 8), (ex - 5.0, ey + 1.2), (ex - 0.6, ey + 1.2), (ex - 3.0, ey + 8.6), (ex + 5.4, ey - 2.0), (ex + 0.6, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(dilate(bm, 1.1, S), INK, 1.0)
    cv.over(bm, YEL, 1.0)
    if name:
        letters(cv, name, (c[0], c[1] + 7.5), 12.6, fnt=ANTON_F, fill=WHITE, ink=INK, extrude=1.2, ext_col=INK, ink_w=1.3, outline=True, miss=(0.3, 0.3), wob=0.1, spacing=0.4, hatch_ext=False)
    spindle = cv.circle_mask((c[0], c[1] + 17.5), 1.6)
    cv.over(spindle, INK, 1.0)


# ------------------------------------------------------------------ assembler
def render_tower(f, name='BREAKER', S=F.S_DEF, seed=11, skip_trim_units=None, hot=True, with_trim=True, ghost=None):
    cv = Canvas(TW, TW, S, seed=seed)
    pm = page_A(cv) if V() == 'A' else page_B(cv)
    bolts(cv, pm)
    wedges = []
    for w in f['wheel']:
        wedges.append((w, draw_wedge(cv, w)))
    for w, sol in wedges:
        draw_break_state(cv, w, sol)
    for w, sol in wedges:
        draw_icon(cv, w, sol)
    for w, sol in wedges:
        if w.get('brace'):
            draw_brace_plate(cv, w['sector'])
        if w.get('soak'):
            draw_soak_mark(cv, w['sector'])
    for w, sol in wedges:
        draw_pips(cv, w)
    # pins and tape on the rim, in the gaps
    if V() == 'A':
        safety_pin(cv, pol(CT, 186.0, 30), 30 + 90 + 14, L=44)
        safety_pin(cv, pol(CT, 186.0, 210), 210 + 90 - 12, L=44)
    else:
        for a in (30, 210):
            tape(cv, pol(CT, 186.0, a), 40, 15, a + 90 + 8, col=(252, 206, 40), alpha=0.95)
    draw_hp_ring(cv, f)
    (hub_A if V() == 'A' else hub_B)(cv, name)
    if with_trim:
        draw_trim(cv, f, skip_trim_units, hot)
    return cv.down(), cv


if __name__ == '__main__':
    import time, asm_r2 as A0
    A0.setup()
    t = time.time()
    J = json.load(open('D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/state_e10.json'))
    key = sys.argv[1] if len(sys.argv) > 1 else 'f1'
    for v in ('A', 'B'):
        VARIANT[0] = v
        im, _ = render_tower(J[key])
        bg = Image.new('RGBA', im.size, (38, 36, 56, 255))
        bg.alpha_composite(im)
        bg.save('D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/work/_tw_%s.png' % v)
        bg.resize((TW * 2, TW * 2), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/work/_tw_%s_2x.png' % v)
        print(v, time.time() - t)
