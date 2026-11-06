"""sg_ui: the other player-owned pieces: YOU tally strip (taped paper on the HUD), SEND IT, nameplate, plus the UNDO terminal chip (S family, not player-styled)."""
import math, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T
import st_cards as K


def tape_piece(cv, x, y, w, h, rot, seed, col=None, op=0.93):
    """a strip of masking tape centred at (x,y), torn zig-zag ends"""
    ss = cv.ss
    col = hx('E8DDB4') if col is None else col
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = []
    n = 7
    r = np.random.default_rng(seed)
    for side in (-1, 1):
        for i in range(n + 1):
            t = (i / n - 0.5) * h
            ex = side * (w / 2 + (1.3 if i % 2 else -1.3) * (0.7 + 0.6 * r.random()))
            pts.append((ex, t * side * -1 if side == 1 else t))
    # build polygon: right side down, left side up
    right = [(w / 2 + (1.5 if i % 2 else -0.4) * (0.6 + 0.8 * r.random()), (i / n - 0.5) * h) for i in range(n + 1)]
    left = [(-w / 2 - (1.5 if i % 2 else -0.4) * (0.6 + 0.8 * r.random()), (i / n - 0.5) * h) for i in range(n, -1, -1)]
    P = [(x + px * c - py * s_, y + px * s_ + py * c) for (px, py) in right + left]
    m = poly(cv, P)
    cv.paint(blur(shift(m, 0.8 * ss, 1.6 * ss), 1.0 * ss) * 0.4, INK)
    cv.paint(blur(m, 0.3 * ss), col, op)
    tex = vnoise(cv.H, cv.W, 1.7 * ss, seed, 1)
    cv.paint(blur(m * (tex > 0.55), 0.4 * ss), WHITE, 0.10)
    cv.paint(blur(np.clip(m - shrink(m, 0.9 * ss), 0, 1), 0.3 * ss) * 0.0, INK)
    return m


def you_strip(f, ss=3, nw=False):
    """the YOU tally on a taped paper strip: 15 painted segments in 3 groups of 5; the pending run (lost at END TURN, harm) is red cross-hatch"""
    x0, y0, w, h = 1068, 96, 346, 52
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    core, full = torn_mask(w - 14, h - 10, rough=1.4, seed=17, ss=ss, fibre=1.6)
    cm = np.zeros((cv.H, cv.W), np.float32); fm = np.zeros((cv.H, cv.W), np.float32)
    ox, oy = 7 * ss, 5 * ss
    cm[oy:oy + core.shape[0], ox:ox + core.shape[1]] = core
    fm[oy:oy + full.shape[0], ox:ox + full.shape[1]] = full
    cv.paint(blur(shift(fm, 1.5 * ss, 2.6 * ss), 2.0 * ss) * 0.6, INK)
    ptex, ridge = paper(w - 14, h - 10, seed=4, ss=ss, wrinkle=0.3)
    pt = np.zeros((cv.H, cv.W, 3), np.float32) + PAPER
    pt[oy:oy + ptex.shape[0], ox:ox + ptex.shape[1]] = ptex
    cv.paint(fm, pt * 0.96)
    cv.paint(cm, pt)
    # label: YOU, marker
    if nw:
        K.scribble_tag(cv, x0 + 38, y0 + 25, 0.55, PINK, 4)
    else:
        tag_text(cv, 'YOU', x0 + 40, y0 + 26, 28, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=CHROME, drop=PINK_DK, drop_off=(1.6, 1.9), outline=1.6, rim_w=0.9, skew=0.12, rot=-3, wob=0.25, seed=2, track=0.4)
    # pink underline swoosh
    sw = stroke_mask(cv, [(x0 + 16, y0 + 40), (x0 + 38, y0 + 42), (x0 + 62, y0 + 39)], 3.0, 1.4, wob=0.3, seed=5, taper=(0.1, 0.4))
    cv.paint(blur(sw, 0.3 * ss), PINK)
    # segments
    segs = []
    xs = x0 + 72
    wseg, hseg, pitch = 12.6, 17, 15.6
    n_pend = f['hp'] - f['pv']['hp_after']
    n_lit = f['pv']['hp_after']
    idx = 0
    for g in range(3):
        for k in range(5):
            xx = xs + g * (5 * pitch + 8) + k * pitch
            segs.append(xx)
    for i, xx in enumerate(segs):
        m = poly(cv, [(xx, y0 + 27 - hseg / 2), (xx + wseg, y0 + 27 - hseg / 2), (xx + wseg, y0 + 27 + hseg / 2), (xx, y0 + 27 + hseg / 2)])
        m = grow(shrink(m, 2.2 * ss), 2.2 * ss)
        m = warp(m, 0.35 * ss, 6 * ss, 200 + i)
        ring = grow(m, 1.5 * ss)
        lit = i < n_lit
        cv.paint(blur(ring, 0.3 * ss), INK)
        if lit:
            cv.paint(blur(m, 0.3 * ss), GAIN)
            g = np.clip(m - shift(m, 0.8 * ss, 1.2 * ss), 0, 1) * m
            cv.paint(blur(g, 0.25 * ss), WHITE, 0.85)
        elif i < n_lit + n_pend:
            cv.paint(blur(m, 0.3 * ss), hx('2A0F16'))
            hm = hatch_mask(cv, m, (45, 135), 3.7, 1.15, 0.2, seed=300 + i)
            cv.paint(blur(hm, 0.25 * ss), HARM)
            cv.paint(blur(np.clip(m - shrink(m, 1.4 * ss), 0, 1), 0.2 * ss), HARM)
    # tape at both ends
    tape_piece(cv, x0 + 12, y0 + 7, 34, 15, -32, 3)
    tape_piece(cv, x0 + w - 14, y0 + h - 8, 34, 15, -28, 4)
    return cv.to_image(), (x0, y0)


def send_it(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 1640, 880, 275, 150
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    # slab
    P = [cv.p(a, b) for a, b in ((1666, 920), (1888, 916), (1892, 1002), (1664, 1006))]
    slab = pil_mask(cv.H, cv.W, lambda d: d.polygon(P, fill=255))
    slab = warp(slab, 1.8 * ss, 16 * ss, 9)
    slab = grow(shrink(slab, 6 * ss), 6 * ss)
    ex = extrude(grow(slab, 5.6 * ss), 5.0 * ss, 6.2 * ss)
    cv.paint(blur(shift(ex, 3 * ss, 5 * ss), 4.0 * ss) * 0.55, INK)
    cv.paint(blur(ex, 0.5 * ss), PINK_DK * 0.85)
    cv.paint(blur(grow(slab, 5.6 * ss), 0.4 * ss), INK)
    tt = np.clip((Y - 880) / 150.0, 0, 1)
    cv.paint(blur(grow(slab, 3.2 * ss), 0.35 * ss), lerp(WHITE[None, None, :], CHROME_DK[None, None, :], tt[..., None] ** 0.7))
    col = lerp((PINK * 0.55 + PINK_HI * 0.45)[None, None, :], PINK[None, None, :], np.clip((Y - 915) / 95.0, 0, 1)[..., None] ** 1.1)
    spray(cv, slab, col, seed=22, grain=0.55, soft=0.5, over_d=0.0)
    glare = np.clip(slab - shift(slab, 6.0 * ss, 7.0 * ss), 0, 1) * slab
    cv.paint(blur(glare, 0.35 * ss) * 0.9, PINK_HI * 0.55 + WHITE * 0.45)
    shade = blur(np.clip(slab - shift(slab, -9 * ss, -11 * ss), 0, 1) * slab, 2.6 * ss)
    cv.paint(shade * 0.7 * slab, PINK_DK)
    sp = (vnoise(cv.H, cv.W, 1.3 * ss, 33, 1) > 0.85).astype(np.float32)
    cv.paint(blur(sp, 0.5 * ss) * slab * 0.3, PINK_DK)
    # wildstyle arrows pointing the way (chrome)
    for (ax, ay, sgn) in ((1685, 962, 1), (1871, 962, -1)):
        pts = [(ax + sgn * 11, ay - 8), (ax - sgn * 5, ay), (ax + sgn * 11, ay + 8), (ax + sgn * 6, ay)]
        am = poly(cv, pts)
        cv.paint(blur(grow(am, 1.5 * ss), 0.3 * ss), INK)
        cv.paint(blur(am, 0.3 * ss), PINK_HI)
    if nw:
        Pa = [(1735, 946), (1790, 946), (1790, 930), (1830, 959), (1790, 988), (1790, 972), (1735, 972)]
        am = poly(cv, Pa)
        am = warp(am, 0.5 * ss, 6 * ss, 12)
        cv.paint(blur(extrude(grow(am, 3.0 * ss), 4.4 * ss, 5.2 * ss), 0.5 * ss), PINK_DD)
        cv.paint(blur(grow(am, 3.0 * ss), 0.4 * ss), INK)
        cv.paint(blur(am, 0.4 * ss), lerp(WHITE[None, None, :], CHROME[None, None, :], np.clip((Y - 930) / 60.0, 0, 1)[..., None]))
    else:
        tag_text(cv, 'SEND IT', 1777, 959, 66, ANTON, fill=WHITE, fill2=CHROME, ink=INK, rim=INK, drop=PINK_DD, drop_off=(4.4, 5.2), outline=3.0, rim_w=0.0, skew=0.14, rot=-2.2, track=1.5,
                 wob=0.4, seed=5, hi=False)
    # drips off the slab's bottom edge (keylined so they read on the wall)
    for (dxp, ln, wd, sd) in ((1702, 17, 4.2, 1), (1792, 11, 3.6, 2), (1859, 20, 4.4, 3)):
        yb = 1002
        dm = drip_mask(cv, dxp, yb - 2, ln, wd, seed=sd)
        cv.paint(blur(grow(dm, 1.7 * ss), 0.3 * ss) * (1 - slab), INK)
        cv.paint(blur(grow(dm, 1.7 * ss), 0.3 * ss) * slab * 0, INK)
        cv.paint(blur(dm, 0.35 * ss), PINK)
        cv.paint(blur(np.clip(dm - shift(dm, 1.0 * ss, 0), 0, 1), 0.3 * ss) * 0.8, PINK_HI)
    tape_piece(cv, 1670, 922, 36, 15, -35, 8)
    tape_piece(cv, 1884, 1000, 36, 15, -32, 9)
    return cv.to_image(scale=scale), (x0, y0)


def nameplate(variant='A', ss=3, scale=1, nw=False):
    x0, y0, w, h = 14, 948, 250, 126
    cv = Cv(x0, y0, w, h, ss)
    X, Y = cv.grid()
    core, full = torn_mask(204, 82, rough=1.8, seed=44, ss=ss)
    ox, oy = 26 * ss, 24 * ss
    cm = np.zeros((cv.H, cv.W), np.float32); fm = np.zeros((cv.H, cv.W), np.float32)
    cm[oy:oy + core.shape[0], ox:ox + core.shape[1]] = core
    fm[oy:oy + full.shape[0], ox:ox + full.shape[1]] = full
    cv.paint(blur(shift(fm, 2 * ss, 4 * ss), 3 * ss) * 0.6, INK)
    ptex, _ = paper(204, 82, seed=14, ss=ss, wrinkle=0.35)
    pt = np.zeros((cv.H, cv.W, 3), np.float32) + PAPER
    pt[oy:oy + ptex.shape[0], ox:ox + ptex.shape[1]] = ptex
    cv.paint(fm, pt * 0.96); cv.paint(cm, pt)
    # crest sticker (pink disc) + marker lines
    cx_, cy_ = 28 + 24, 948 + 24 + 41
    disc = circle(cv, cx_ + 8, cy_, 24)
    cv.paint(blur(shift(disc, 1.5 * ss, 2.5 * ss), 1.6 * ss) * 0.5, INK)
    cv.paint(blur(grow(disc, 1.2 * ss), 0.3 * ss), INK)
    spray(cv, disc, PINK, seed=3, grain=0.5, soft=0.6, over_d=0.0)
    cm_ = T.glyph_mask('WC2_CREST', 32, cv, cx_ + 8, cy_)
    cv.paint(blur(extrude(cm_, 1.6 * ss, 1.8 * ss), 0.3 * ss), PINK_DK)
    cv.paint(blur(grow(cm_, 1.4 * ss), 0.3 * ss), INK)
    cv.paint(blur(cm_, 0.3 * ss), WHITE)
    if nw:
        for q in range(9):
            xq = 128 + q * 9 + (q // 5) * 8
            st_ = stroke_mask(cv, [(xq, cy_ - 22), (xq + 0.6, cy_ - 2)], 4.4, 3.8, wob=0.2, seed=60 + q, taper=(0.05, 0.08))
            cv.paint(blur(grow(st_, 1.4 * ss), 0.3 * ss), INK)
            cv.paint(blur(st_, 0.3 * ss), PINK)
        bar = stroke_mask(cv, [(126, cy_ + 16), (170, cy_ + 15), (212, cy_ + 17)], 6, 5, wob=0.3, seed=61, taper=(0.05, 0.05))
        cv.paint(blur(bar, 0.3 * ss), ZINE, 0.85)
    else:
        tag_text(cv, 'CELL-9', 160, cy_ - 11, 38, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=CHROME, drop=PINK_DK, drop_off=(2.8, 3.2), outline=2.2, rim_w=1.2, skew=0.15, rot=-2, wob=0.3, seed=2, track=0.6)
        K.marker_text(cv, '// BREAKER', 160, cy_ + 20, 22, ZINE, seed=3, rot=-1.2)
    tape_piece(cv, 38, 962, 38, 15, -38, 5)
    tape_piece(cv, 238, 1034, 38, 15, -34, 6)
    return cv.to_image(scale=scale), (x0, y0)


def undo_chip():
    x0, y0, w, h = 1660, 872, 240, 60
    im = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def R(b, **k):
        d.rounded_rectangle([v * 3 for v in b], radius=8 * 3, **k)
    R((20, 6, 216, 46), fill=(5, 13, 28, 237), outline=(92, 225, 255, 255), width=5)
    f = font(MONO, 22 * 3)
    d.text((34 * 3, 26 * 3), 'UNDO', font=f, fill=(242, 246, 255, 255), anchor='lm')
    R((184, 14, 208, 38), fill=(5, 13, 28, 237), outline=(92, 225, 255, 255), width=4)
    d.text((196 * 3, 26 * 3), 'Z', font=font(MONO, 17 * 3), fill=(92, 225, 255, 255), anchor='mm')
    im = im.resize((w, h), Image.LANCZOS).rotate(-1.5, resample=Image.BICUBIC, center=(w / 2, h / 2))
    return im, (x0, y0)
