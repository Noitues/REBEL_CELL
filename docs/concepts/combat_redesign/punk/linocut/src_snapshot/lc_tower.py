"""lc_tower: the LINOCUT wheel.  The Cell cut its own board in lino and pulled a print: a black key block (carved plate, bone chisel cuts), a hot-pink second block printed 1.5 px off register,
a scissor-cut pink halo around the plate (like a sticker), bone-paper hub starburst.  Patches f1_tower's look functions; the data/grammar functions (HP blocks, pips, break state, soak, trim, hover arcs) are f1_tower's, unchanged.
Import this module BEFORE calling f1_tower.render_tower."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import f1_tower as FT
import f1_icons as FI
from f1_lib import smooth, warp, outline_mask, arc_pts, pol, font, ANTON_F
from lc_lib import *

CT = FT.CT
R_IN, R_OUT = FT.R_IN, FT.R_OUT
FT.KRAFT = HOT
ICON_PX = 56
VARIANT = ['A']
PALS = {
    'A': dict(halo=HOT, plate=KEY, cut=BONE, wedge=HOT, wedge_cut=KEY, wedge_hi=(255, 205, 232), icon=KEY, icon_in=BONE, icon_hi=BONE, hub=BONE, hub_off=HOT, hub_ink=KEY, hub_ink2=HOT, lit=1),
    'B': dict(halo=BONE, plate=HOT, cut=KEY, wedge=KEY, wedge_cut=HOT, wedge_hi=BONE, icon=HOT, icon_in=KEY, icon_hi=BONE, hub=KEY, hub_off=BONE, hub_ink=BONE, hub_ink2=HOT, lit=-1),
}


def P():
    return PALS[VARIANT[0]]
                     # the brace clamp's tape piece is a pink cut strip


def _grow(m, px, S):
    return ndi.binary_dilation(m > 0.5, iterations=max(1, int(px * S))).astype(np.float32)


def _shrink(m, px, S):
    return ndi.binary_erosion(m > 0.5, iterations=max(1, int(px * S))).astype(np.float32)


def _shift(m, dx, dy, S):
    return np.roll(np.roll(m, int(round(dy * S)), 0), int(round(dx * S)), 1)


def text_mask_c(cv, text, c, px, font_path=ANTON_F, spacing=0.0):
    S = cv.S
    f = font(font_path, px * S)
    im = Image.new('L', (cv.W, cv.H), 0)
    d = ImageDraw.Draw(im)
    if spacing:
        wtot = sum(f.getlength(ch) for ch in text) + spacing * S * (len(text) - 1)
        x = c[0] * S - wtot / 2
        for ch in text:
            d.text((x, c[1] * S), ch, font=f, fill=255, anchor='lm')
            x += f.getlength(ch) + spacing * S
    else:
        d.text((c[0] * S, c[1] * S), text, font=f, fill=255, anchor='mm')
    return np.asarray(im, np.float32) / 255.0


# ------------------------------------------------------------------ plate, halo, carved border
DOODLE_ANG = (90, 150, 270, 322)


def page_disc(cv):
    S = cv.S
    r = cv.r
    # 1. the hot-pink halo: a scissor-cut sticker edge around the plate (second block)
    halo_pts = jag_disc((CT[0] + 0.8, CT[1] + 0.6), 195.3, r, step=(7, 15), amp=2.3)
    halo = cv.poly_mask(halo_pts)
    sh = _shift(halo, 4, 5, S)
    cv.over(ndi.gaussian_filter(sh, 3.0 * S), (6, 4, 12), 0.62)
    cv.over(halo, P()['halo'], 1.0)
    # carved ticks across the halo: black chisel nicks
    nick = []
    for k in range(46):
        a = k * 360 / 46 + r.uniform(-3, 3)
        p0 = pol(CT, 190.5, a)
        p1 = pol(CT, 197.5 + r.uniform(-0.5, 1.0), a + r.uniform(-3, 3))
        nick.append((p0[0], p0[1], p1[0], p1[1], r.uniform(1.4, 2.2), r.uniform(-0.8, 0.8)))
    cv.over(lens_mask(cv, nick), KEY, 0.85)
    # 2. the black key plate, 1.5 px off register against the pink
    plate_pts = jag_disc(CT, 190.4, r, step=(6, 13), amp=1.1)
    plate = cv.poly_mask(plate_pts)
    cv.over(ink_grain(cv, plate, 0.7), P()['plate'], 1.0)
    # 3. carved rim: a ring of bone chisel ticks between the slices' outer arc and the plate edge
    ticks = []
    for k in range(120):
        a = k * 3.0 + r.uniform(-0.6, 0.6)
        if any(abs(((a - d + 180) % 360) - 180) < 7 for d in DOODLE_ANG):
            continue
        L = r.choice([5.0, 6.5, 8.0, 3.8])
        p0 = pol(CT, 181.5 + r.uniform(-0.4, 0.6), a)
        p1 = pol(CT, 181.5 + L, a + r.uniform(-1.6, 1.6))
        ticks.append((p0[0], p0[1], p1[0], p1[1], r.uniform(1.5, 2.3), r.uniform(-0.5, 0.5)))
    cv.over(lens_mask(cv, ticks), P()['cut'], 0.92)
    # 4. sunburst between the slices (the cuts between the wedges): bone lenses radiating from the hub ring
    rays = []
    for k in range(6):
        ag = 60 * k + 30
        for q in range(7):
            aa = ag + r.uniform(-3.2, 3.2)
            ra = r.uniform(74, 120) + q * 9
            rb = ra + r.uniform(9, 22)
            if rb > 176:
                rb = 176
            if rb - ra < 4:
                continue
            p0 = pol(CT, ra, aa)
            p1 = pol(CT, rb, aa + r.uniform(-0.8, 0.8))
            rays.append((p0[0], p0[1], p1[0], p1[1], r.uniform(1.4, 2.4), r.uniform(-0.6, 0.6)))
    cv.over(lens_mask(cv, rays), P()['cut'], 0.85)
    # 5. hub ring: two broken bone circles around the HP band
    for rr, w in ((50.0, 1.5), (66.6, 1.6)):
        segs = []
        a = r.uniform(0, 30)
        while a < 360 - 20:
            L = r.uniform(25, 70)
            a1 = min(a + L, 358)
            pts = arc_pts(CT, rr, a, a1, 2.0)
            for i in range(len(pts) - 1):
                segs.append((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], w * (0.6 + 0.4 * math.sin(math.pi * i / max(1, len(pts) - 1))) * 1.4, 0))
            a = a1 + r.uniform(5, 14)
        cv.over(lens_mask(cv, segs, 0.3), P()['cut'], 0.75)
    return plate


def construction(cv):
    return


def tape_strips(cv):
    return


def doodles(cv):
    """four bold bone cut-outs on the rim between the slices: star, spark, X, zig"""
    S = cv.S
    c = P()['cut']
    r_ = 185.5

    def star(cen, rr):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = rr if i % 2 == 0 else rr * 0.42
            pts.append((cen[0] + rad * math.cos(ang), cen[1] + rad * math.sin(ang)))
        return cv.poly_mask(pts)
    cv.over(star(pol(CT, r_, 90), 6.2), c, 0.95)
    sp = []
    cen = pol(CT, r_, 150)
    for i in range(8):
        a = i * math.pi / 4
        sp.append((cen[0], cen[1], cen[0] + 6.4 * math.cos(a), cen[1] + 6.4 * math.sin(a), 2.4, 0.0))
    cv.over(lens_mask(cv, sp), c, 0.95)
    cen = pol(CT, r_, 270)
    xs = [(cen[0] - 4.6, cen[1] - 4.6, cen[0] + 4.6, cen[1] + 4.6, 3.0, 0.3), (cen[0] - 4.6, cen[1] + 4.6, cen[0] + 4.6, cen[1] - 4.6, 3.0, -0.3)]
    cv.over(lens_mask(cv, xs), c, 0.95)
    p0, p1 = pol(CT, r_, 322 - 6), pol(CT, r_, 322 + 6)
    zz = []
    pts = [p0]
    for i in range(1, 5):
        t = i / 5
        pts.append((p0[0] + (p1[0] - p0[0]) * t + (3.0 if i % 2 else -3.0) * math.cos(math.radians(322)), p0[1] + (p1[1] - p0[1]) * t + (3.0 if i % 2 else -3.0) * math.sin(math.radians(322))))
    pts.append(p1)
    for i in range(len(pts) - 1):
        zz.append((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2.4, 0))
    cv.over(lens_mask(cv, zz, 0.3), c, 0.95)


# ------------------------------------------------------------------ slices
def draw_wedge(cv, w, cons=True):
    S = cv.S
    r = cv.r
    s = w['sector']
    am = 60 * s
    half = 25.6
    pts = (jag_arc(CT, R_OUT, am - half, am + half, r, (9, 18), 0.9)
           + jag_path(pol(CT, R_OUT, am + half), pol(CT, R_IN, am + half), r, (9, 16), 0.9)[1:]
           + jag_arc(CT, R_IN, am + half, am - half, r, (9, 16), 0.8)[1:]
           + jag_path(pol(CT, R_IN, am - half), pol(CT, R_OUT, am - half), r, (9, 16), 0.9)[1:-1])
    solid = cv.poly_mask(pts)
    bone = _grow(solid, 2.3, S)
    cv.over(ink_grain(cv, bone, 0.4), BONE, 0.97)                       # the paper showing around the pink: keyline that varies 0..3.6 px (misregister)
    pink = _shift(_shrink(solid, 0.3, S), 1.5, 1.1, S)
    pink = pink * (1 - (ndi.gaussian_filter(smooth(*pink.shape, 14 * S, r), 1.0) > 1.9).astype(np.float32) * 0.0)
    cv.over(ink_grain(cv, pink, 0.9), P()['wedge'], 1.0)
    # --- carved shade: black lens gouges, denser toward the bottom right of the slice
    ci = pol(CT, 0.5 * (R_IN + R_OUT), am)
    ic = pol(CT, FT.ICON_R, am)
    reg = _shrink(pink, 2.6, S)
    gl = []
    ang = math.radians(-42)
    ux, uy = math.cos(ang), math.sin(ang)          # hatch direction
    vx, vy = -uy, ux                               # across the hatch
    off = -62.0 + r.uniform(0, 3)
    while off < 62.0:
        th = r.uniform(0.22, 0.62)
        run = []
        for tt in np.arange(-70, 70, 1.5):
            x, y = ci[0] + vx * off + ux * tt, ci[1] + vy * off + uy * tt
            ok = False
            rr_ = math.hypot(x - CT[0], y - CT[1])
            da = abs(((math.degrees(math.atan2(x - CT[0], -(y - CT[1]))) - am + 180) % 360) - 180)
            if R_IN + 5 < rr_ < 157 and da < 24 and math.hypot(x - ic[0], y - ic[1]) > 30.5:
                sh = P()['lit'] * ((x - ci[0]) * 0.62 + (y - ci[1]) * 0.78) / 46.0 + 0.30
                ok = sh > th
            if ok:
                run.append((x, y))
            elif run:
                if len(run) >= 3:
                    gl.append((run[0][0], run[0][1], run[-1][0], run[-1][1], r.uniform(1.4, 2.3), r.uniform(-0.9, 0.9)))
                run = []
        if len(run) >= 3:
            gl.append((run[0][0], run[0][1], run[-1][0], run[-1][1], r.uniform(1.4, 2.3), r.uniform(-0.9, 0.9)))
        off += r.uniform(4.0, 5.4)
    g = lens_mask(cv, gl) * reg
    cv.over(g, P()['wedge_cut'], 0.96)
    # --- bone chisel highlights on the lit (top-left) side
    hl = []
    for _ in range(90):
        rr = r.uniform(R_IN + 4, 156)
        aa = am + r.uniform(-24, 24)
        x, y = pol(CT, rr, aa)
        if math.hypot(x - ic[0], y - ic[1]) < 32.0:
            continue
        lit = -P()['lit'] * (((x - ci[0]) * 0.62 + (y - ci[1]) * 0.78) / 40.0) + 0.1
        if r.random() > np.clip(lit, 0, 1) ** 1.4 * 0.55:
            continue
        L = r.uniform(6, 13)
        ang = math.radians(-42 + r.uniform(-7, 7))
        dx, dy = math.cos(ang) * L / 2, math.sin(ang) * L / 2
        hl.append((x - dx, y - dy, x + dx, y + dy, r.uniform(1.0, 1.7), r.uniform(-0.8, 0.8)))
    cv.over(lens_mask(cv, hl) * reg, P()['wedge_hi'], 0.9)
    return solid


def draw_icon(cv, w, solid):
    """the E10 silhouettes cut as black key-block shapes with a bone chisel line; the shield's inner panel is cut through to the paper"""
    S = cv.S
    t = w['t']
    am = 60 * w['sector']
    c = pol(CT, FT.ICON_R, am)
    white, dark = FI.mask_for(t, ICON_PX, S)
    n = white.shape[0]
    x0, y0 = int(c[0] * S - n / 2), int(c[1] * S - n / 2)
    wm = FT.solidify(white, S)
    wm = FT.solidify(warp(wm, 0.5 * S, 7 * S, cv.r), S)
    full = np.clip(wm + dark, 0, 1)
    halo = np.clip(ndi.gaussian_filter(outline_mask(full, S, 2.0), 0.3 * S / 4 * 1.5) * 1.6, 0, 1)
    shd = _shift(full, 2.2, 2.4, S)
    cv.over(np.clip(shd - full, 0, 1), HOT_D if VARIANT[0] == 'A' else (0, 0, 0), 0.95, x0, y0)              # the pink's darker offset: the misregistered print
    cv.over(halo, BONE, 0.97, x0, y0)
    cv.over(np.clip(wm, 0, 1), P()['icon'], 1.0, x0, y0)
    if dark.max() > 0:
        cv.over(np.clip(dark, 0, 1), P()['icon_in'], 1.0, x0, y0)
    inner = _shrink(wm, 1.0, S)
    hi = np.clip(inner - _shift(inner, 2.6, 2.6, S), 0, 1)
    hi = np.clip(hi - _shift(inner, 4.2, 4.2, S) * 0 , 0, 1)
    cv.over(ndi.gaussian_filter(hi, 0.3 * S), P()['icon_hi'], 0.92, x0, y0)
    return x0, y0, full


# ------------------------------------------------------------------ hub
def draw_hub(cv, name='BREAKER'):
    S = cv.S
    r = cv.r
    c = CT
    pts = []
    nb = 14
    for i in range(nb * 2):
        a = i * 360.0 / (nb * 2) + r.uniform(-2, 2)
        rad = (46.4 if i % 2 == 0 else 41.6) + r.uniform(-0.8, 0.8)
        pts.append(pol(c, rad, a))
    star = cv.poly_mask(pts)
    # pink second block, off register
    pk = _shift(_grow(star, 2.2, S), 2.6, 2.0, S)
    cv.over(pk, P()['hub_off'], 1.0)
    cv.over(np.clip(outline_mask(star, S, 1.6), 0, 1) * 0.0, KEY, 1.0)
    cv.over(ink_grain(cv, star, 0.5), P()['hub'], 1.0)
    ex, ey = c[0], c[1] - 15.0
    bolt = [(ex + 2.8, ey - 9.5), (ex - 5.4, ey + 1.0), (ex - 0.4, ey + 1.0), (ex - 3.2, ey + 10.2), (ex + 5.8, ey - 2.2), (ex + 0.6, ey - 2.2)]
    bm = cv.poly_mask(bolt)
    cv.over(_shift(bm, 1.2, 1.2, S), P()['hub_ink2'], 1.0)
    cv.over(bm, P()['hub_ink'], 1.0)
    if name:
        tm = text_mask_c(cv, name, (c[0], c[1] + 10.0), 15.2, ANTON_F, spacing=0.7)
        cv.over(_shift(tm, 1.1, 1.1, S), P()['hub_ink2'], 1.0)
        cv.over(tm, P()['hub_ink'], 1.0)


# ------------------------------------------------------------------ patch + post pass
FT.page_disc = page_disc
FT.construction = construction
FT.tape_strips = tape_strips
FT.doodles = doodles
FT.draw_wedge = draw_wedge
FT.draw_icon = draw_icon
FT.draw_hub = draw_hub
_orig_render = FT.render_tower


def render_tower(*a, **k):
    im, cv = _orig_render(*a, **k)
    return print_texture(im, seed=21, dens=0.010, pink_dens=0.006), cv


FT.render_tower = render_tower

if __name__ == '__main__':
    import json, time
    import asm_r2 as A
    A.setup()
    t = time.time()
    J = json.load(open('D:/rc_scratch/combat_redesign/punk/linocut/state_e10.json'))
    key = sys.argv[1] if len(sys.argv) > 1 else 'f1'
    VARIANT[0] = sys.argv[2] if len(sys.argv) > 2 else 'A'
    im, _ = FT.render_tower(J[key])
    bg = Image.new('RGBA', im.size, (30, 26, 52, 255))
    bg.alpha_composite(im)
    bg.save('D:/rc_scratch/combat_redesign/punk/linocut/out/lc_tower_%s_%s.png' % (key, VARIANT[0]))
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/punk/linocut/out/lc_tower_%s_%s_2x.png' % (key, VARIANT[0]))
    print(time.time() - t)
