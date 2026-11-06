"""js_slices: per-slice-type colour AND texture for the Jinx scribble wheel (designer request 2026-11-01).
Types on the wheel: BURST (game ZERO-DAY), SHIELD (SANDBOX), TURRET (EXPLOIT), REPAIR (PATCH).
Each type has its own colour and its own scribble texture; same type = same look.  Pending-loss cross-hatch gets an ink underlay so it
reads on every colour.  install() after js_tower.install()."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from f1_lib import *
import f1_tower as FT
import js_tower as JT
import js_doodle as D
from f1_tower import CT, R_IN, R_OUT, ICON_R, solidify, wedge_mask, bbox
from js_tower import neon, placed, NP, NP_L, NP_D, NC, NC_L, CHALKC, INKB

_orig_break = FT.draw_break_state

# type -> dict(A=(body_dark_hi, body_dark_lo, vivid, plate), B=(fill, fill_light, fill_dark, ink_pattern, plate))
PALA = {
    'BURST':  dict(c0=(96, 10, 60), c1=(150, 18, 92), viv=(255, 46, 154), plate=NC, name='NEON PINK'),
    'SHIELD': dict(c0=(6, 62, 96), c1=(10, 96, 132), viv=(40, 222, 255), plate=(255, 70, 170), name='CYAN'),
    'TURRET': dict(c0=(40, 70, 6), c1=(66, 104, 10), viv=(190, 255, 50), plate=NC, name='ACID LIME'),
    'REPAIR': dict(c0=(104, 48, 4), c1=(158, 74, 6), viv=(255, 138, 30), plate=NC, name='SAFETY ORANGE'),
}
PALB = {
    'BURST':  dict(fill=(255, 112, 26), lt=(255, 170, 90), dk=(150, 40, 6), name='HOT ORANGE'),
    'SHIELD': dict(fill=(46, 112, 255), lt=(130, 170, 255), dk=(10, 30, 130), name='ELECTRIC BLUE'),
    'TURRET': dict(fill=(250, 214, 28), lt=(255, 240, 130), dk=(130, 100, 0), name='PAINT YELLOW'),
    'REPAIR': dict(fill=(255, 46, 154), lt=(255, 140, 205), dk=(130, 8, 80), name='HOT PINK'),
}
TEXNAME = {'BURST': 'POW starburst + sparks', 'SHIELD': 'fish scales', 'TURRET': 'reticle + dot grid', 'REPAIR': 'plus crosses'}


def pal(t):
    return (PALA if JT.VAR[0] == 'A' else PALB)[t]


def viv(t):
    p = pal(t)
    return p['viv'] if JT.VAR[0] == 'A' else p['fill']


# ------------------------------------------------------------------ textures (PIL drawn at supersample, then chalked)
def _pat_masks(cv, t, s):
    S = cv.S
    r = cv.r
    am = 60 * s
    L = cv.new_mask()
    F = cv.new_mask()
    dl, df = ImageDraw.Draw(L), ImageDraw.Draw(F)
    ic = pol(CT, ICON_R, am)
    P = lambda p: (p[0] * S, p[1] * S)
    j = lambda: float(r.normal(0, 0.45))
    lw = lambda w: max(1, int(w * S))
    if t == 'BURST':
        n = 11
        pts = []
        for k in range(n * 2):
            a = math.pi * 2 * k / (n * 2) + 0.3
            rad = (r.uniform(46, 56) if k % 2 == 0 else r.uniform(30, 36))
            pts.append((ic[0] + rad * math.cos(a) + j(), ic[1] + rad * math.sin(a) + j()))
        pts.append(pts[0])
        df.polygon([P(p) for p in pts], fill=255)
        dl.line([P(p) for p in pts], fill=255, width=lw(2.5), joint='curve')
        # sparks outside the star: short ticks between spikes
        for k in range(9):
            a = math.pi * 2 * (k + r.uniform(-0.2, 0.2)) / 9 + 0.1
            r0, r1 = r.uniform(60, 64), r.uniform(70, 78)
            dl.line([P((ic[0] + r0 * math.cos(a), ic[1] + r0 * math.sin(a))), P((ic[0] + r1 * math.cos(a), ic[1] + r1 * math.sin(a)))], fill=255, width=lw(2.2))
        # a lightning zig on the hub side
        zc = pol(CT, 90, am - 8 if s % 2 else am + 8)
        zz = [(zc[0] - 5, zc[1] - 9), (zc[0] + 3, zc[1] - 3), (zc[0] - 3, zc[1] + 2), (zc[0] + 5, zc[1] + 9)]
        dl.line([P(p) for p in zz], fill=255, width=lw(2.4), joint='curve')
    elif t == 'SHIELD':
        rows = list(np.arange(86.0, 160.0, 15.0))
        for ri, rr_ in enumerate(rows):
            step = 17.0
            ang_step = math.degrees(step / rr_)
            for k in range(-5, 6):
                a = am + (k + 0.5 * (ri % 2)) * ang_step
                c = pol(CT, rr_, a)
                p2 = pol(CT, rr_ + 1.0, a)
                th = math.degrees(math.atan2(p2[1] - c[1], p2[0] - c[0]))
                rad = 9.6
                bb = [(c[0] - rad) * S, (c[1] - rad) * S, (c[0] + rad) * S, (c[1] + rad) * S]
                dl.ellipse(bb, fill=0)
                dl.arc(bb, th - 95, th + 95, fill=255, width=lw(3.0))
                df.ellipse(bb, fill=0)
                df.arc(bb, th - 95, th + 95, fill=255, width=lw(3.0))
        # fill: a soft lighter scale cap (outer half) to give the scales volume
    elif t == 'TURRET':
        for rad, w_ in ((33.0, 2.2), (42.0, 1.8)):
            bb = [(ic[0] - rad) * S, (ic[1] - rad) * S, (ic[0] + rad) * S, (ic[1] + rad) * S]
            a0 = r.uniform(0, 40)
            dl.arc(bb, a0, a0 + 330, fill=255, width=lw(w_))
        for k in range(4):
            a = math.pi / 2 * k + math.radians(r.uniform(-4, 4))
            dl.line([P((ic[0] + 28 * math.cos(a), ic[1] + 28 * math.sin(a))), P((ic[0] + 49 * math.cos(a), ic[1] + 49 * math.sin(a)))], fill=255, width=lw(2.2))
        for rr_ in np.arange(86.0, 160.0, 11.5):
            ang_step = math.degrees(11.5 / rr_)
            for k in range(-6, 7):
                c = pol(CT, rr_, am + (k + 0.5 * (int(rr_ / 11.5) % 2)) * ang_step)
                if math.hypot(c[0] - ic[0], c[1] - ic[1]) < 49:
                    continue
                d_ = 3.1
                dl.ellipse([(c[0] - d_) * S, (c[1] - d_) * S, (c[0] + d_) * S, (c[1] + d_) * S], fill=255)
    elif t == 'REPAIR':
        for ri, rr_ in enumerate(np.arange(88.0, 160.0, 15.5)):
            ang_step = math.degrees(17.0 / rr_)
            for k in range(-5, 6):
                c = pol(CT, rr_, am + (k + 0.5 * (ri % 2)) * ang_step)
                if math.hypot(c[0] - ic[0], c[1] - ic[1]) < 33:
                    continue
                arm = 6.2
                dl.line([P((c[0] - arm + j(), c[1] + j())), P((c[0] + arm + j(), c[1] + j()))], fill=255, width=lw(3.1))
                dl.line([P((c[0] + j(), c[1] - arm + j())), P((c[0] + j(), c[1] + arm + j()))], fill=255, width=lw(3.1))
    return np.asarray(L, np.float32) / 255.0, np.asarray(F, np.float32) / 255.0


def paint_texture(cv, t, s, solid):
    S = cv.S
    am = 60 * s
    L, F = _pat_masks(cv, t, s)
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    inner = ndi.binary_erosion(solid > 0.5, iterations=int(3.4 * S)).astype(np.float32)
    zone = inner * ((rr < 158.5) & (rr > R_IN + 4)).astype(np.float32)
    zone = ndi.gaussian_filter(zone, 0.6 * S)
    ic = pol(CT, ICON_R, am)
    clear = 1 - np.clip(cv.circle_mask(ic, 27.5), 0, 1)
    Lm = ndi.gaussian_filter(L, 0.38 * S)
    Lm = np.clip((Lm - 0.25) * 2.4, 0, 1)
    n = smooth(cv.H, cv.W, 0.9 * S / 4 * 1.6, cv.r)
    Lm = np.clip(Lm * (0.84 + 0.30 * n), 0, 1) * zone * clear
    Fm = ndi.gaussian_filter(F, 0.5 * S) * zone
    A = JT.VAR[0] == 'A'
    p = pal(t)
    if A:
        v = p['viv']
        cv.over(Fm, v, 0.22)
        cv.over(np.clip(ndi.gaussian_filter(Lm, 1.6 * S) * 1.4, 0, 1) * zone, v, 0.3)     # neon glow
        cv.over(Lm, v, 0.95)
    else:
        cv.over(Fm, p['lt'], 0.55)
        cv.over(Lm, (28, 10, 44), 0.86)
    return Lm


# ------------------------------------------------------------------ wedge
def draw_wedge(cv, w, cons=True):
    S = cv.S
    r = cv.r
    s = w['sector']
    am = 60 * s
    t = w['t']
    A = JT.VAR[0] == 'A'
    p = pal(t)
    reg = wedge_mask(cv, s, R_IN, R_OUT, 26.0, jit=0.9)
    solid = solidify(reg, S)
    y0, y1, x0, x1 = bbox(solid, 14 * S)
    sub = solid[y0:y1, x0:x1]
    yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float32)
    rr = np.hypot(xx / S - CT[0], yy / S - CT[1])
    tt = np.clip((rr - R_IN) / (R_OUT - R_IN), 0, 1)[..., None]
    v = viv(t)
    halo = ndi.gaussian_filter(solid, 3.4 * S)
    cv.over(np.clip(halo * 1.5, 0, 1) * (1 - solid), v if A else NC, 0.42 if A else 0.28)
    drop = np.roll(np.roll(solid, int(3.0 * S), 0), int(4.0 * S), 1)
    cv.over(np.clip(drop - solid, 0, 1), INKB, 0.97)
    if A:
        c0, c1 = np.array(p['c0'], np.float32), np.array(p['c1'], np.float32)
        cv.over_rgb(solid, c0 * (1 - tt) + c1 * tt)
        tone = [tuple(min(255, int(c * 1.35)) for c in p['c1']), tuple(int(c * 0.7) for c in p['c0']), tuple(int(c * 0.5 + 0.5 * q) for c, q in zip(p['c1'], v))]
        for i in range(12):
            a = am + r.uniform(-24, 24)
            rad = r.uniform(R_IN + 8, R_OUT - 8)
            ang = math.radians(r.choice([-50, 40, -30, 60]) + r.uniform(-12, 12))
            L = r.uniform(18, 46)
            c = pol(CT, rad, a)
            m, mx0, my0 = stroke_mask(cv, [c, (c[0] + L * math.cos(ang), c[1] + L * math.sin(ang))], r.uniform(5, 12), 'round', 0, 1.0, 30, (0.3, 0.4))
            nz = smooth(*m.shape, 1.1 * S / 4 * 1.6, r)
            m = np.clip(m * np.clip(nz * 0.9 + 0.4, 0, 1) * 1.3, 0, 1)
            cv.over(placed(cv, m, mx0, my0) * solid, tone[int(r.integers(0, 3))], r.uniform(0.3, 0.55))
    else:
        f = np.array(p['fill'], np.float32)
        cv.over_rgb(solid, f * (1 - tt * 0.15) + np.array(p['lt'], np.float32) * (tt * 0.15))
        fill_region(cv, sub, x0, y0, p['fill'], ang=34 + r.uniform(-8, 8), nib=7.5, over=1.8, miss=(r.choice([-1, 1]) * 1.7, r.choice([-1, 1]) * 1.4), jit=0.5, clip=0.6, alpha=0.5)
        for i in range(10):
            a = am + r.uniform(-24, 24)
            rad = r.uniform(R_IN + 8, R_OUT - 8)
            ang = math.radians(r.choice([-50, 40, -30, 60]) + r.uniform(-12, 12))
            L = r.uniform(16, 40)
            c = pol(CT, rad, a)
            m, mx0, my0 = stroke_mask(cv, [c, (c[0] + L * math.cos(ang), c[1] + L * math.sin(ang))], r.uniform(4, 10), 'round', 0, 1.0, 30, (0.3, 0.4))
            nz = smooth(*m.shape, 1.1 * S / 4 * 1.6, r)
            m = np.clip(m * np.clip(nz * 0.9 + 0.4, 0, 1) * 1.3, 0, 1)
            cv.over(placed(cv, m, mx0, my0) * solid, p['lt'] if r.random() < 0.5 else p['dk'], r.uniform(0.3, 0.5))
        strip = np.clip(sub - np.roll(np.roll(sub, int(-10 * S), 0), int(-8 * S), 1), 0, 1)
        hatch_region(cv, strip, x0, y0, p['dk'], ang=135, pitch=3.2, w=1.2, alpha=0.6, over=0.3, jit=0.25, cross=False)
    paint_texture(cv, t, s, solid)
    # outline: plate first (misregistered), the key on top
    a0, a1 = am - 25.6, am + 25.6
    edges = [lambda: arc_pts(CT, R_OUT, a0 - 1.5, a1 + 1.5, 0.8), lambda: [pol(CT, R_OUT + 3, a1), pol(CT, R_IN - 3, a1)],
             lambda: arc_pts(CT, R_IN, a1 + 1.8, a0 - 1.8, 0.8), lambda: [pol(CT, R_IN - 3, a0), pol(CT, R_OUT + 3, a0)]]
    plate = p['plate'] if A else NC
    for col, wd, sh, gl in ((plate, 2.2, (2.6, -1.9), 0.0), (v if A else INKB, 4.2 if A else 4.8, (0, 0), 0.6 if A else 0.0)):
        for e in edges:
            neon(cv, [(q[0], q[1]) for q in e()], col, wd, 0.96, gl, wob=0.55, taper=(0.03, 0.06), wl=24, grain=0.22, shift=sh)
    if not A:
        for e in edges:
            neon(cv, [(q[0], q[1]) for q in e()], NC, 1.6, 0.9, 0.0, wob=0.5, taper=(0.03, 0.06), wl=24, grain=0.22, shift=(3.0, 2.4))
    for q in range(2):
        p0 = pol(CT, R_IN + 12 + q * 5, am - 22 + q * 2)
        p1 = pol(CT, R_OUT - 24 - q * 6, am - 18 + q * 3)
        neon(cv, [p0, p1], (255, 255, 255) if A else CHALKC, 2.0, 0.4, 0.0, wob=0.4, taper=(0.15, 0.45), clip=solid)
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    if ha < hp:                # glitch tear (a loss is pending)
        rrg = np.random.default_rng(40 + s)
        for q in range(3):
            ya = (CT[1] + rrg.uniform(-55, 55)) * S
            hh = int(rrg.uniform(1.4, 2.8) * S)
            band = np.zeros((cv.H, cv.W), np.float32)
            band[int(ya):int(ya) + hh, :] = 1.0
            sh = int(rrg.choice([-1, 1]) * rrg.uniform(5, 9) * S)
            moved = np.roll(solid, sh, 1)
            cv.over(band * moved * solid, NC if q % 2 == 0 else NP_L, 0.9)
            cv.over(band * np.clip(moved - solid, 0, 1), NC if q % 2 == 0 else NP, 0.75)
    return solid


def draw_break_state(cv, w, solid):
    """pending whole-slice loss: ink wash + ink underlay hatch + cause-colour hatch on top + ink then cause edge, so the hatch reads on any slice colour"""
    S = cv.S
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    if not (hp > 0 and ha == 0):
        return _orig_break(cv, w, solid)
    am = 60 * w['sector']
    col = FT.SOAKC if w.get('soaked') else FT.HARMC
    ix, iy = pol(CT, ICON_R, am)
    clear = 1 - np.clip(cv.circle_mask((ix, iy), 31), 0, 1)
    reg = solid * clear
    cv.over(reg, (14, 6, 22), 0.16)
    y0, y1, x0, x1 = bbox(reg, 2)
    sub = reg[y0:y1, x0:x1]
    st = cv.r.bit_generator.state
    hatch_region(cv, sub, x0, y0, INKB, ang=45, pitch=5.4, w=3.0, alpha=0.9, over=1.0, jit=0.5, cross=True)
    cv.r.bit_generator.state = st
    hatch_region(cv, sub, x0, y0, col, ang=45, pitch=5.4, w=1.9, alpha=0.96, over=1.0, jit=0.5, cross=True)
    edge = np.clip(ndi.gaussian_filter(outline_mask(solid, S, 2.2, inner=2.2), 0.4) * 1.5, 0, 1)
    edge2 = np.clip(ndi.gaussian_filter(outline_mask(solid, S, 3.6, inner=0.6), 0.4) * 1.5, 0, 1)
    cv.over(edge2, INKB, 0.95)
    cv.over(edge, col, 0.98)
    x, y = pol(CT, R_OUT - 22, am + 17)
    for sg in (1, -1):
        pp = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
        ballpoint(cv, pp, INKB, 7.6, 1.0, wob=0.3, wl=9, taper=(0, 0))
    for sg in (1, -1):
        pp = [(x - 7, y - sg * 7), (x + 7, y + sg * 7)]
        marker(cv, pp, col, w=4.6, alpha=1.0, wob=0.3, grain=0.05, taper=(0, 0))


def doodles(cv):
    """only the margin doodles in the gaps between slices (wedge interiors now carry the type texture)"""
    r_ = 184.6
    kinds = ['star', 'x', 'tally', 'bolt', 'star4', 'x']
    cols = [NC, NP, NC, NP, NC, NC]
    for g, k, c in zip([30, 90, 150, 210, 270, 330], kinds, cols):
        JT.doodle_on(cv, JT._g(k, pol(CT, r_, g), 4.8), c, 1.8, 0.4)


def install():
    FT.draw_wedge = draw_wedge
    FT.draw_break_state = draw_break_state
    FT.doodles = doodles
