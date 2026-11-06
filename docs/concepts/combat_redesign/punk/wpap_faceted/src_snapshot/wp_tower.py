"""wp_tower: the WPAP FACETED player wheel.  A poster plate cut into flat indigo planes, six pink wedges cut into flat pink/violet/secondary-ink planes, ink seats for the icons,
chrome pyramid studs in the gaps (punk jacket), a faceted gem hub with a name band, slanted HP blocks.  No gradients, no blur, no wobble; 2.4 px ink, hard offset drop.
render_tower(f, name, ...) -> (RGBA image TW x TW, canvas).  Same signature and same game data as f1_tower."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import f1_tower as FT
from f1_tower import TW, CT, S_DEF, R_PAGE, R_HUB, R_HP0, R_HP1, R_IN, R_OUT, ICON_R, ICON_PX, PIP_R, PIP_W, TRIM0, TRIM1, bbox, trim_data, hp_states, pip_states
from f1_tower import SOAKC, HARMC, COLD_HARM, FAR_HARM, TMID, GAINC
import f1_icons as FI
from f1_lib import Canvas, pol, arc_pts, outline_mask, text_mask, ANTON_F, MONO_F, PINK, PINK_D, PINK_L
import wp_lib as L
from wp_lib import WINK, WHITE_, CREAM, facet_assign, hatch_mask_local, poly_stroke_mask

VAR = L.VAR


def solidify(m, S):
    return np.clip((ndi.gaussian_filter(m, 0.5 * S / 4 * 1.5) - 0.45) * 6, 0, 1)


def stroke(cv, pts, w, col, alpha=1.0, cap=True):
    cv.over(poly_stroke_mask((cv.H, cv.W), cv.S, pts, w, cap), col, alpha)


def ring_of(solid, S, w):
    return outline_mask(solid, S, w)


def hard_drop(cv, solid, dx, dy, col=WINK, alpha=1.0):
    S = cv.S
    n = int(max(dx, dy) * S)
    ex = np.zeros_like(solid)
    for k in range(1, n + 1):
        ex = np.maximum(ex, np.roll(np.roll(solid, int(round(k * dy / max(dx, dy))), 0), int(round(k * dx / max(dx, dy))), 1))
    ex = np.clip(ex - solid, 0, 1)
    cv.over(ex, col, alpha)
    return ex


def paint_facets(cv, solid, ramp, seed, **kw):
    S = cv.S
    bb = bbox(solid, 2)
    if bb is None:
        return None
    y0, y1, x0, x1 = bb
    sub = solid[y0:y1, x0:x1]
    rgb, ids, n = facet_assign(sub, S, ramp, seed, **kw)
    cv.over_rgb(sub, rgb, x0, y0)
    return sub, x0, y0


def light_edge(cv, solid, k=1.5, col=(255, 222, 240), alpha=0.9):
    S = cv.S
    sh = np.roll(np.roll(solid, int(k * S), 0), int(k * S), 1)
    cv.over(np.clip(solid - sh, 0, 1) * solid, col, alpha)


def ctext(cv, text, c, px, fnt=ANTON_F, fill=WHITE_, ink=WINK, ink_w=1.4, drop=(0.0, 0.0), drop_col=None, spacing=0.0, rot=0.0):
    S = cv.S
    m = text_mask(cv, text, fnt, px, rot, spacing)
    h, w = m.shape
    x0, y0 = int(round(c[0] * S - w / 2)), int(round(c[1] * S - h / 2))
    solid = np.clip((m - 0.5) * 6 + 0.5, 0, 1)
    ring = np.clip(outline_mask(solid, S, ink_w), 0, 1)
    full = np.maximum(solid, ring)
    if drop != (0.0, 0.0):
        n = int(max(abs(drop[0]), abs(drop[1])) * S)
        ex = np.zeros_like(full)
        for k in range(1, n + 1):
            ex = np.maximum(ex, np.roll(np.roll(full, int(round(drop[1] * S * k / n)), 0), int(round(drop[0] * S * k / n)), 1))
        cv.over(ex, drop_col or PINK, 1.0, x0, y0)
    cv.over(ring, ink, 1.0, x0, y0)
    cv.over(solid, fill, 1.0, x0, y0)


# ------------------------------------------------------------------ plate (the poster disc)
def page_disc(cv):
    S = cv.S
    P = L.P()
    disc = cv.circle_mask(CT, R_PAGE)
    hard_drop(cv, disc, 4.0, 5.0, WINK)
    cv.over(ring_of(disc, S, 3.0), WINK)
    paint_facets(cv, disc, P['page'], seed=41, k=6, accent=P['page_acc'], accent_max=0.22, minfrac=0.045, jit=0.28, spread=0.55)
    # neon edge line just inside the plate
    rr = cv.circle_mask(CT, R_PAGE - 1.2) - cv.circle_mask(CT, R_PAGE - 3.0)
    cv.over(np.clip(rr, 0, 1), P['page_edge'], 0.75)
    return disc


def stud(cv, c, r=4.8):
    """chrome pyramid stud seen from above: four flat triangles, ink ring, hard drop"""
    S = cv.S
    x, y = c
    sq = cv.poly_mask([(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)])
    hard_drop(cv, sq, 1.6, 2.0, WINK)
    cv.over(ring_of(sq, S, 1.5), WINK)
    cols = {'t': (250, 252, 255), 'l': (190, 204, 226), 'r': (122, 138, 170), 'b': (62, 74, 104)}
    cv.over(cv.poly_mask([(x - r, y - r), (x + r, y - r), (x, y)]), cols['t'])
    cv.over(cv.poly_mask([(x - r, y - r), (x, y), (x - r, y + r)]), cols['l'])
    cv.over(cv.poly_mask([(x + r, y - r), (x + r, y + r), (x, y)]), cols['r'])
    cv.over(cv.poly_mask([(x - r, y + r), (x + r, y + r), (x, y)]), cols['b'])


def studs(cv):
    for k in range(6):
        stud(cv, pol(CT, 183.5, 30 + 60 * k))


# ------------------------------------------------------------------ HP blocks (slanted parallelograms, flat, hatch = cause colour)
def slant_poly(cv, rc, w, a0, a1, bulge=0.0, sk=1.9):
    r0, r1 = rc - w / 2 - bulge / 2, rc + w / 2 + bulge / 2
    d = math.degrees(sk / rc)
    o = arc_pts(CT, r1, a0 + d, a1 + d, 0.8)
    i = arc_pts(CT, r0, a1 - d, a0 - d, 0.8)
    return cv.poly_mask(np.concatenate([o, i]))


def draw_block(cv, rc, w, a0, a1, state, ink_w=1.6, pitch=None, crossh=None, glow=True):
    S = cv.S
    pend = state in ('harm', 'soak', 'ours')
    solid = slant_poly(cv, rc, w, a0, a1, bulge=2.0 if pend else 0.0)
    if state == 'gone':
        cv.over(ring_of(solid, S, 1.0), (96, 88, 120), 1.0)
        cv.over(solid, (20, 12, 34), 1.0)
        return solid
    col = {'harm': HARMC, 'soak': SOAKC, 'ours': PINK}.get(state)
    if pend and glow:
        halo = ndi.binary_dilation(solid > 0.5, iterations=int(2.2 * S)).astype(np.float32)
        cv.over(np.clip(halo - solid, 0, 1), col, 0.40)
    cv.over(ring_of(solid, S, ink_w), WINK)
    if state == 'lit':
        cv.over(solid, GAINC)
        # one lighter plane on the outer half: a straight cut, not a gradient
        yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
        rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
        cv.over(solid * (rr > rc + 0.06 * w), (196, 250, 196))
    elif pend:
        cv.over(solid, (22, 10, 36))
        inner = ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.2 * S))).astype(np.float32)
        cross = (w >= 12) if crossh is None else crossh
        bb = bbox(inner, 1)
        if bb:
            y0, y1, x0, x1 = bb
            sub = inner[y0:y1, x0:x1]
            hm = hatch_mask_local(*sub.shape, S, 45, pitch or (4.4 if cross else 4.0), 1.5, cross=cross)
            cv.over(hm * sub, col, 1.0, x0, y0)
        cv.over(ring_of(inner, S, 1.0), col, 1.0)
        if state == 'soak':
            am = (a0 + a1) / 2
            x, y = pol(CT, rc + w / 2 + 1.0, am)
            x2, y2 = pol(CT, rc - w * 0.05, am)
            tg = (math.cos(math.radians(am)), math.sin(math.radians(am)))
            stroke(cv, [(x + tg[0] * 4.4, y + tg[1] * 4.4), (x2, y2), (x - tg[0] * 4.4, y - tg[1] * 4.4)], 2.4, WINK)
    elif state == 'mend':
        cv.over(solid, (14, 28, 20))
        inner = ndi.binary_erosion(solid > 0.5, iterations=max(1, int(1.2 * S))).astype(np.float32)
        cv.over(ring_of(inner, S, 1.2), GAINC)
        am = (a0 + a1) / 2
        x, y = pol(CT, rc, am)
        stroke(cv, [(x - 3.4, y), (x + 3.4, y)], 1.7, GAINC, cap=False)
        stroke(cv, [(x, y - 3.4), (x, y + 3.4)], 1.7, GAINC, cap=False)
    return solid


def draw_hp_ring(cv, f):
    mx = f['maxhp']
    sts = hp_states(f['hp'], f['pv']['hp_after'], mx)
    rc, w = (R_HP0 + R_HP1) / 2, R_HP1 - R_HP0
    ngrp, per = 3, 5
    g2, g1 = 9.0, 2.6
    seg = (360 / ngrp - g2 - (per - 1) * g1) / per
    for g in range(ngrp):
        a0 = g * 120 + g2 / 2 - 1.6
        a1 = a0 + 120 - g2 + 3.2
        band = cv.band_mask(CT, rc - w / 2 - 3.0, rc + w / 2 + 3.0, a0, a1, step=0.8)
        cv.over(band, WINK)
    for i, st in enumerate(sts):
        grp, j = divmod(i, per)
        a0 = grp * 120 + g2 / 2 + j * (seg + g1)
        draw_block(cv, rc, w, a0, a0 + seg, st)


def draw_pips(cv, w):
    s = w['sector']
    sts = pip_states(w)
    n = len(sts)
    bl, bg = 36.0, 6.0
    tot = n * bl + (n - 1) * bg
    cr = lambda px: math.degrees(px / PIP_R)
    a = 60 * s - cr(tot) / 2
    for i, st in enumerate(sts):
        a0 = a + cr(i * (bl + bg))
        draw_block(cv, PIP_R, PIP_W, a0, a0 + cr(bl), st, ink_w=1.5, pitch=4.0, crossh=False, glow=False)


# ------------------------------------------------------------------ slices
def wedge_poly(s, r0, r1, half, n=4):
    am = 60 * s
    outer = [pol(CT, r1, am - half + i * 2 * half / n) for i in range(n + 1)]
    inner = [pol(CT, r0, am + half - i * 2 * half / n) for i in range(n + 1)]
    return outer + inner


def draw_wedge(cv, w, cons=True):
    S = cv.S
    P = L.P()
    s = w['sector']
    solid = cv.poly_mask(wedge_poly(s, R_IN, R_OUT, 26.0, 4))
    hard_drop(cv, solid, 3.0, 4.0, WINK)
    cv.over(ring_of(solid, S, 2.4), WINK)
    paint_facets(cv, solid, P['ramp'], seed=100 + 7 * s + (3 if VAR[0] == 'B' else 0), k=4, accent=P['accent'], accent_max=0.26, glint=P['glint'], glint_max=0.14, minfrac=0.06, jit=0.22)
    light_edge(cv, solid)
    return solid


def octagon(c, r, rot=22.5):
    return [pol(c, r, rot + 45 * k) for k in range(8)]


def draw_seat(cv, w):
    P = L.P()
    S = cv.S
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    seat = cv.poly_mask(octagon(c, 30.0))
    hard_drop(cv, seat, 2.0, 2.5, WINK)
    cv.over(ring_of(seat, S, 2.2), WINK)
    cv.over(seat, (30, 10, 52))
    inner = cv.poly_mask(octagon(c, 26.4))
    cv.over(np.clip(inner - cv.poly_mask(octagon(c, 25.2)), 0, 1), PINK, 1.0)


def draw_icon(cv, w, solid):
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = solidify(white, S)
    full = np.clip(wm + dark, 0, 1)
    sh = np.roll(np.roll(full, int(1.8 * S), 0), int(1.8 * S), 1)
    cv.over(np.clip(sh - full, 0, 1), PINK, 1.0, x0, y0)
    cv.over(ring_of(full, S, 1.5), WINK, 1.0, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), WINK, 1.0, x0, y0)
    cv.over(wm, WHITE_, 1.0, x0, y0)
    return x0, y0, full


def draw_break_state(cv, w, solid):
    S = cv.S
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    am = 60 * w['sector']
    if hp > 0 and ha == 0:
        col = SOAKC if w.get('soaked') else HARMC
        ix, iy = pol(CT, ICON_R, am)
        clear = 1 - np.clip(cv.circle_mask((ix, iy), 31), 0, 1)
        reg = solid * clear
        cv.over(reg, (22, 6, 40), 0.32)
        bb = bbox(reg, 2)
        y0, y1, x0, x1 = bb
        sub = reg[y0:y1, x0:x1]
        hm = hatch_mask_local(*sub.shape, S, 45, 6.4, 1.7, cross=True)
        cv.over(hm * sub, col, 1.0, x0, y0)
        edge = np.clip(outline_mask(solid, S, 2.2, inner=2.2), 0, 1)
        cv.over(edge, col, 1.0)
        x, y = pol(CT, R_OUT - 22, am + 17)
        for sg in (1, -1):
            stroke(cv, [(x - 7, y - sg * 7), (x + 7, y + sg * 7)], 7.6, WINK, cap=False)
        for sg in (1, -1):
            stroke(cv, [(x - 7, y - sg * 7), (x + 7, y + sg * 7)], 4.4, col, cap=False)
    elif hp == 0:
        cv.over(solid, (10, 8, 20), 0.9)
    elif hp < w['mx'] and ha == hp:
        pts = [pol(CT, R_OUT - 6, am + 20), pol(CT, R_OUT - 14, am + 17), pol(CT, R_OUT - 19, am + 22), pol(CT, R_OUT - 27, am + 18.5), pol(CT, R_OUT - 33, am + 23.5)]
        stroke(cv, pts, 5.0, WINK, cap=False)
        stroke(cv, pts, 1.9, WHITE_, cap=False)


def draw_brace_plate(cv, s):
    """L10 double line: a flat cream clamp plate on the rim, two solid ink lines, ink jaw bars, two octagon rivets"""
    S = cv.S
    am = 60 * s
    a0, a1 = am - 26.5, am + 26.5
    strip = cv.band_mask(CT, 177.0, 191.0, a0, a1, step=1.0)
    hard_drop(cv, strip, 2.0, 3.0, WINK)
    cv.over(ring_of(strip, S, 1.8), WINK)
    cv.over(strip, CREAM)
    cv.over(cv.band_mask(CT, 177.0, 180.0, a0, a1, step=1.0), (214, 206, 190))
    for rr in (181.4, 186.6):
        stroke(cv, arc_pts(CT, rr, a0 + 3.0, a1 - 3.0, 0.8), 2.4, WINK, cap=False)
    for sg in (-1, 1):
        stroke(cv, [pol(CT, 176.0, am + sg * 24.0), pol(CT, 192.0, am + sg * 24.0)], 3.2, WINK, cap=False)
        x, y = pol(CT, 184.0, am + sg * 20.5)
        cv.over(cv.poly_mask(octagon((x, y), 2.4)), WINK)


def draw_soak_mark(cv, s):
    am = 60 * s
    p = [pol(CT, R_IN + 20, am - 12), pol(CT, R_IN + 11, am), pol(CT, R_IN + 20, am + 12)]
    stroke(cv, p, 10.0, WINK, cap=False)
    stroke(cv, p, 5.4, SOAKC, cap=False)


# ------------------------------------------------------------------ hub: faceted gem + name band
def draw_hub(cv, name='BREAKER'):
    S = cv.S
    P = L.P()
    c = CT
    pts = [pol(c, R_HUB - 2.2, 18 + 36 * k) for k in range(10)]
    solid = cv.poly_mask(pts)
    hard_drop(cv, solid, 3.0, 4.0, WINK)
    cv.over(ring_of(solid, S, 2.6), WINK)
    paint_facets(cv, solid, P['hub'], seed=7 + (5 if VAR[0] == 'B' else 0), k=3, accent=P['accent'], accent_max=0.30, glint=P['glint'], glint_max=0.2, minfrac=0.09, jit=0.18, spread=0.5)
    light_edge(cv, solid, 1.3)
    # name band: a slanted ink plate across the gem
    band = cv.poly_mask([(c[0] - 40, c[1] + 18), (c[0] - 40, c[1] + 1.5), (c[0] + 40, c[1] - 3.5), (c[0] + 40, c[1] + 13.5)])
    band = band * np.clip(cv.circle_mask(c, R_HUB - 1.0), 0, 1)
    cv.over(band, WINK)
    cv.over(np.clip(band - np.roll(band, int(1.4 * S), 0), 0, 1), P['accent'], 1.0)
    ex, ey = c[0], c[1] - 17.0
    bolt = [(ex + 2.5, ey - 9), (ex - 5.0, ey + 1.0), (ex - 0.5, ey + 1.0), (ex - 3.0, ey + 9.5), (ex + 5.5, ey - 2.0), (ex + 0.5, ey - 2.0)]
    bm = cv.poly_mask(bolt)
    cv.over(np.roll(np.roll(bm, int(1.2 * S), 0), int(1.2 * S), 1), PINK)
    cv.over(ring_of(bm, S, 1.4), WINK)
    cv.over(bm, WHITE_)
    if name:
        ctext(cv, name, (c[0], c[1] + 8.4), 15.5, fill=WHITE_, ink=WINK, ink_w=0.6, spacing=0.7, rot=3.4)


# ------------------------------------------------------------------ T family: threat trim (flat, time grammar)
def draw_trim(cv, f, skip_units=None, state_hot=True):
    S = cv.S
    zones = {2: (-26.5, -9.5), 1: (-8.5, 8.5), 0: (9.5, 26.5)}
    for sec, ks in trim_data(f, skip_units).items():
        mm = 60 * sec
        for k in sorted(ks):
            a0, a1 = zones[k]
            a0 += mm
            a1 += mm
            if k == 0:
                reg = cv.band_mask(CT, TRIM0, TRIM1, a0, a1, step=0.8)
                if state_hot:
                    halo = cv.band_mask(CT, TRIM0 - 3.2, TRIM1 + 3.2, a0 - 1.2, a1 + 1.2, step=0.8)
                    cv.over(np.clip(halo - reg, 0, 1), HARMC, 0.38)
                cv.over(ring_of(reg, S, 2.3), WINK)
                cv.over(reg, HARMC)
                am = (a0 + a1) / 2
                tip = pol(CT, TRIM0 - 8.5, am)
                b0 = pol(CT, TRIM0 + 0.5, am - 3.4)
                b1 = pol(CT, TRIM0 + 0.5, am + 3.4)
                tri = cv.poly_mask([b0, b1, tip])
                cv.over(ring_of(tri, S, 1.8), WINK)
                cv.over(tri, HARMC)
            elif k == 1:
                reg = cv.band_mask(CT, TRIM0 + 2.0, TRIM1 - 2.0, a0, a1, step=0.8)
                cv.over(ring_of(reg, S, 1.8), WINK)
                cv.over(reg, COLD_HARM)
                bx, by = pol(CT, TRIM1 + 6.5, a0 + 1.6)
                cv.over(cv.circle_mask((bx, by), 3.1), WINK)
                cv.over(cv.circle_mask((bx, by), 2.0), TMID)
            else:
                rc = (TRIM0 + TRIM1) / 2
                n = int(math.radians(a1 - a0) * rc / 7.4)
                for i in range(n + 1):
                    a = a0 + (a1 - a0) * i / max(1, n)
                    p = pol(CT, rc, a)
                    cv.over(cv.circle_mask(p, 3.5), WINK)
                    cv.over(cv.circle_mask(p, 2.2), FAR_HARM)
                for j in range(2):
                    bx, by = pol(CT, TRIM1 + 6.5, a0 + 1.6 + j * 3.6)
                    cv.over(cv.circle_mask((bx, by), 3.1), WINK)
                    cv.over(cv.circle_mask((bx, by), 2.0), TMID)


# ------------------------------------------------------------------ assembler
def render_tower(f, name='BREAKER', S=S_DEF, seed=11, skip_trim_units=None, hot=True, with_trim=True, ghost=None):
    cv = Canvas(TW, TW, S, seed=seed)
    page_disc(cv)
    wedges = []
    for w in f['wheel']:
        wedges.append((w, draw_wedge(cv, w)))
    for w, solid in wedges:
        draw_break_state(cv, w, solid)
    for w, solid in wedges:
        draw_seat(cv, w)
    for w, solid in wedges:
        draw_icon(cv, w, solid)
    for w, solid in wedges:
        if w.get('brace'):
            draw_brace_plate(cv, w['sector'])
        if w.get('soak'):
            draw_soak_mark(cv, w['sector'])
    for w, solid in wedges:
        draw_pips(cv, w)
    studs(cv)
    draw_hp_ring(cv, f)
    draw_hub(cv, name)
    if with_trim:
        draw_trim(cv, f, skip_trim_units, hot)
    return cv.down(), cv


if __name__ == '__main__':
    import json, time
    t = time.time()
    var = sys.argv[1] if len(sys.argv) > 1 else 'A'
    key = sys.argv[2] if len(sys.argv) > 2 else 'f1'
    VAR[0] = var
    import asm_r2 as A
    A.setup()
    J =json.load(open('D:/rc_scratch/combat_redesign/punk/wpap_faceted/state_e10.json'))
    im, _ = render_tower(J[key])
    bg = Image.new('RGBA', im.size, (20, 18, 32, 255))
    bg.alpha_composite(im)
    bg.save('D:/rc_scratch/combat_redesign/punk/wpap_faceted/out/tower_%s_%s.png' % (var, key))
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/punk/wpap_faceted/out/tower_%s_%s_2x.png' % (var, key))
    print(round(time.time() - t, 1))
