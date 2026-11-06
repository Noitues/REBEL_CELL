"""mu_cards: the MURAL cards.  The black-book layout (cost badge top-left, big icon, title, type band, rules text) painted as a wall plaque:
a sprayed sky-and-skyline art panel with a magenta spray disc and a white stencil icon, an ink title slab with a big white (A) or yellow (B) tag title,
a spray-painted type stripe, rules text in dark marker on plaster, ink + white keyline wildstyle outline, drips.  Game information unchanged."""
import math, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T
import st_cards as K

CW, CH, M = K.CW, K.CH, K.M
CARDS = K.CARDS
J = K.J
VAR = ['A']
NW = K.NW


def pal():
    if VAR[0] == 'A':
        return dict(plaster=hx('EFE3C8'), plaster2=hx('D9C7A4'), sky=[hx('FFD25A'), hx('FF8A3C'), hx('F0388C'), hx('7A3CC8')], disc=PINK, disc_lo=PINK_LO,
                    title=hx('FFFFFF'), title2=hx('E8EEFF'), tdrop=PINK, strip=hx('1FC8B4'), glow=hx('FFE27A'), idrop=hx('FF9A28'), city=hx('3A1A6A'), win=hx('FFE27A'))
    return dict(plaster=hx('DCE4EF'), plaster2=hx('B4C2D8'), sky=[hx('2FD6C8'), hx('2E8BE8'), hx('6A46D6'), hx('2A1A78')], disc=PINK, disc_lo=PINK_LO,
                title=hx('FFE44A'), title2=hx('FFB830'), tdrop=hx('2AB8F0'), strip=hx('FFD83A'), glow=hx('FF8AD0'), idrop=hx('3AD0F8'), city=hx('0E0C3A'), win=hx('5CE1FF'))


def skyline(cv, ab, seed, P):
    """dark city silhouettes along the bottom of the art panel with a few lit windows"""
    r = np.random.default_rng(seed + 5)
    m = np.zeros((cv.H, cv.W), np.float32)
    x = 10
    wins = np.zeros_like(m)
    while x < CW - 10:
        w = r.uniform(11, 22)
        h = r.uniform(10, 26)
        m = np.maximum(m, poly(cv, [(x, 128), (x, 128 - h), (x + w, 128 - h), (x + w, 128)]))
        for wy in np.arange(128 - h + 4, 124, 6.5):
            for wx in np.arange(x + 3, x + w - 3, 5.0):
                if r.random() < 0.38:
                    wins = np.maximum(wins, poly(cv, [(wx, wy), (wx + 2.2, wy), (wx + 2.2, wy + 3.0), (wx, wy + 3.0)]))
        x += w + r.uniform(0, 2.5)
    cv.paint(blur(m, 0.35 * cv.ss) * ab, P['city'], 0.92)
    cv.paint(blur(wins * m, 0.3 * cv.ss) * ab, P['win'], 0.9)


def card_M(name, seed=0, ss=3):
    P = pal()
    A = VAR[0] == 'A'
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    cv = Cv(-M, -M, CW + 2 * M, CH + 2 * M, ss)
    X, Y = cv.grid()
    r_ = np.random.default_rng(seed)
    # ---- the plaque: chipped plaster slab with a wildstyle outline and a cast shadow
    core, full = torn_mask(CW, CH, rough=1.5, seed=seed + 5, ss=ss, fibre=1.2)
    pad = M * ss
    cm = np.zeros((cv.H, cv.W), np.float32)
    cm[pad:pad + core.shape[0], pad:pad + core.shape[1]] = core
    sh = blur(shift(cm, 3.5 * ss, 6 * ss), 3.0 * ss)
    cv.paint(sh, hx('080612'), 0.55)
    cv.paint(extrude(cm, 3.0 * ss, 4.4 * ss, steps=10) * (1 - cm), INK, 1.0)
    cv.paint(blur(grow(cm, 3.4 * ss), 0.35 * ss), INK)
    cv.paint(blur(grow(cm, 1.7 * ss), 0.3 * ss), hx('FFFCF4'))
    pl = np.zeros((cv.H, cv.W, 3), np.float32) + P['plaster']
    n1 = vnoise(cv.H, cv.W, 40 * ss, seed + 1, 3)
    n2 = vnoise(cv.H, cv.W, 3.5 * ss, seed + 2, 2)
    spk = ndi.gaussian_filter(r_.random((cv.H, cv.W)).astype(np.float32), 0.5 * ss)
    spk = (spk - spk.mean()) / (spk.std() + 1e-6)
    shade = 1.0 + (n1 - 0.5) * 0.12 + (n2 - 0.5) * 0.05 + spk * 0.012
    pl = lerp(P['plaster'][None, None, :], P['plaster2'][None, None, :], np.clip((Y - 128) / 140.0 * 0.2 + (n1 - 0.5) * 0.5, 0, 1)[..., None]) * shade[..., None]
    cv.paint(cm, np.clip(pl, 0, 1))
    # the wall under the plaster: brick coursing (A) or concrete panel seams and tie holes (B), faint
    if A:
        bh_, bw_ = 10.6, 23.5
        rowi = np.floor(Y / bh_)
        offx = (rowi % 2) * bw_ / 2
        mort = ((Y % bh_) < 1.3) | (((X + offx + 3) % bw_) < 1.3)
        cv.paint(blur(mort.astype(np.float32), 0.45 * ss) * cm, hx('7A4630'), 0.20)
    else:
        mort = (((X + 10) % 88) < 1.3) | (((Y + 5) % 88) < 1.3)
        cv.paint(blur(mort.astype(np.float32), 0.45 * ss) * cm, hx('5A6A88'), 0.22)
        for (hx_, hy_) in ((20, 186), (CW - 20, 186), (20, 238), (CW - 20, 238)):
            cv.paint(blur(circle(cv, hx_, hy_, 2.2), 0.4 * ss) * cm, hx('4A5878'), 0.5)
    # ---- the art panel: a sprayed sky, glow, clouds of colour, city
    x0, y0, x1, y1 = 9, 10, CW - 9, 128
    Pp = [cv.p(a, b) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    ab = pil_mask(cv.H, cv.W, lambda d: d.polygon(Pp, fill=255))
    ab = warp(ab, 1.3 * ss, 14 * ss, seed + 40) * cm
    cv.paint(blur(grow(ab, 2.8 * ss), 0.35 * ss), INK)
    cv.paint(blur(grow(ab, 1.3 * ss), 0.3 * ss), hx('FFFCF4'))
    cv.paint(blur(grow(ab, 0.0), 0.3 * ss), INK)
    tt = np.clip((Y - y0) / (y1 - y0), 0, 1)
    sky = P['sky']
    stops = np.array([0.0, 0.38, 0.72, 1.0])
    col = np.stack([np.interp(tt, stops, [s[c] for s in sky]) for c in range(3)], -1).astype(np.float32)
    spray(cv, ab, col, seed=seed + 3, grain=0.35, soft=0.6, over_d=0.0)
    # clouds / blotches of the other colours, painted soft
    rb = np.random.default_rng(seed + 41)
    for q in range(5):
        cx_, cy_ = rb.uniform(20, CW - 20), rb.uniform(22, 100)
        blob = circle(cv, cx_, cy_, rb.uniform(14, 26))
        c_ = [P['glow'], P['sky'][2], P['strip'], P['sky'][1], P['glow']][q]
        cv.paint(blur(blob, 10 * ss) * ab * 0.42, c_)
    # glow behind the icon
    icx, icy = CW / 2, 66
    cv.paint(blur(circle(cv, icx, icy, 52), 16 * ss) * ab * 0.9, P['glow'], 0.9)
    skyline(cv, ab, seed, P)
    # sprayed rays + the magenta disc
    rb = np.random.default_rng(seed + 90)
    rays = np.zeros((cv.H, cv.W), np.float32)
    for q in range(14):
        a = math.radians(q * 25.7 + rb.uniform(-5, 5))
        r0_, r1_ = rb.uniform(44, 50), rb.uniform(56, 80)
        rays = np.maximum(rays, stroke_mask(cv, [(icx + r0_ * math.cos(a), icy + r0_ * math.sin(a)), (icx + r1_ * math.cos(a), icy + r1_ * math.sin(a))], 4.4, 0.8, smooth=False, wob=0.2, seed=q))
    cv.paint(blur(rays, 0.5 * ss) * ab * 0.5, hx('FFF6D8'))
    disc = warp(circle(cv, icx, icy, 40), 1.1 * ss, 12 * ss, seed + 3)
    cv.paint(blur(grow(disc, 3.0 * ss), 0.35 * ss) * ab, INK)
    cv.paint(blur(grow(disc, 1.4 * ss), 0.3 * ss) * ab, hx('FFFCF4'))
    dcol = lerp(PINK_LO[None, None, :], PINK_HI[None, None, :], np.clip(0.55 - (Y - icy) / 80.0 + (X - icx) / 220.0 * -1 * 0.0, 0, 1)[..., None] * 0.55)
    dcol = lerp(PINK[None, None, :], hx('FFB04A')[None, None, :] if A else hx('FF7AC8')[None, None, :], np.clip(((icy - Y) * 0.62 + (icx - X) * 0.78) / 70.0 * 0.5 + 0.1, 0, 1)[..., None])
    dcol = lerp(dcol, PINK_LO[None, None, :], np.clip(((Y - icy) * 0.78 + (X - icx) * 0.62) / 60.0 - 0.1, 0, 1)[..., None] * 0.8)
    spray(cv, disc * ab, dcol, seed=seed + 9, grain=0.5, soft=0.7, over_d=0.5, over_s=5.0, over_op=0.7, clip=ab)
    # the icon: white stencil, ink keyline, painted drop
    gm = T.glyph_mask(spec['g'], 66, cv, icx, icy - 1)
    gm = warp(gm, 0.35 * ss, 6 * ss, seed + 21)
    cv.paint(blur(extrude(gm, 3.6 * ss, 4.0 * ss), 0.4 * ss) * ab, P['idrop'])
    cv.paint(blur(grow(gm, 2.6 * ss), 0.35 * ss) * ab, INK)
    wcol = lerp(WHITE[None, None, :], hx('FFE9C8')[None, None, :], np.clip((Y - icy) / 36.0, 0, 1)[..., None] ** 2)
    cv.paint(blur(gm, 0.3 * ss) * ab, wcol)
    # glints
    for (gx, gy, gr) in ((icx - 56, icy - 36, 6.0), (icx + 54, icy + 24, 4.4)):
        pts = []
        for q in range(8):
            rad = gr if q % 2 == 0 else gr * 0.28
            a = math.pi / 4 * q - math.pi / 2
            pts.append((gx + rad * math.cos(a), gy + rad * math.sin(a)))
        st = poly(cv, pts)
        cv.paint(blur(grow(st, 1.1 * ss), 0.3 * ss) * ab, INK)
        cv.paint(blur(st, 0.3 * ss) * ab, hx('FFFCF4'))
    if spec.get('mult'):
        if NW[0]:
            for q in range(int(spec['mult'])):
                st_ = stroke_mask(cv, [(112 + q * 9, 86), (113 + q * 9, 106)], 4.4, 3.8, wob=0.2, seed=seed + q, taper=(0.05, 0.08))
                cv.paint(blur(grow(st_, 1.5 * ss), 0.3 * ss), INK)
                cv.paint(blur(st_, 0.3 * ss), PAPER)
        else:
            tag_text(cv, '\u00d7' + spec['mult'], 126, 92, 34, ANTON, fill=hx('FFFCF4'), fill2=P['title2'], ink=INK, rim=INK, drop=PINK, drop_off=(2.4, 2.8), outline=2.2, rim_w=0.0, skew=0.12, rot=-4, wob=0.3, hi=False, seed=seed)
    # overspray off the panel edge onto the plaster
    od = np.clip(blur(ab, 4.0 * ss) * 1.8 - 0.35, 0, 1) * (1 - ab) * cm
    dots = (r_.random(ab.shape) < od * 0.02).astype(np.float32)
    cv.paint(np.clip(ndi.gaussian_filter(dots, 0.5 * ss) * 4, 0, 1) * 0.6, P['sky'][2])

    # ---- title: an ink slab across the panel foot, a big tag title on it (white A / yellow B, ink edge, hot drop)
    sx0, sx1, sy0, sy1 = 6, CW - 6, 127, 158
    slab = poly(cv, [(sx0, sy0 + 1.2), (sx1, sy0 - 0.6), (sx1 - 1, sy1 - 0.8), (sx0 + 1, sy1 + 0.8)])
    slab = warp(slab, 0.8 * ss, 10 * ss, seed + 61) * cm
    cv.paint(blur(shift(slab, 1.5 * ss, 2.4 * ss), 1.2 * ss), hx('080612'), 0.5)
    cv.paint(blur(grow(slab, 1.6 * ss), 0.3 * ss), hx('FFFCF4'))
    cv.paint(blur(slab, 0.3 * ss), INK)
    cv.paint(blur(slab, 6 * ss) * slab * 0.0, INK)
    # a spray edge of the title colour along the slab foot
    foot = stroke_mask(cv, [(sx0 + 3, sy1 - 2.4), (CW / 2, sy1 - 3.2), (sx1 - 3, sy1 - 2.6)], 2.6, 2.0, wob=0.4, seed=seed + 62, taper=(0.05, 0.08))
    cv.paint(blur(foot, 0.5 * ss) * slab, P['tdrop'], 0.9)
    if NW[0]:
        bar = stroke_mask(cv, [(30, 142), (CW / 2, 140), (CW - 30, 143)], 14, 11, wob=0.5, seed=seed + 4, taper=(0.04, 0.05))
        cv.paint(blur(bar, 0.4 * ss), P['title'])
    else:
        ft_ = font(ANTON, 42 * ss)
        wt_ = ft_.getlength(spec['nm']) / ss + 0.8 * len(spec['nm'])
        pxt_ = 42 if wt_ <= 138 else 42 * 138 / wt_
        tag_text(cv, spec['nm'], CW / 2 - 1, 141.5, pxt_, ANTON, fill=P['title'], fill2=P['title2'], ink=INK, rim=INK, drop=P['tdrop'], drop_off=(2.6, 2.8),
                 outline=2.0, rim_w=0.0, skew=0.14, rot=-2.0, track=0.8, wob=0.25, seed=seed, hi=False)

    # ---- type stripe: spray-painted slab with the family in marker
    ty = 172
    tw_ = 76 if spec['fam'] == 'TOWER' else 66
    tp = [(CW / 2 - tw_ / 2 - 2, ty - 10), (CW / 2 + tw_ / 2 + 1, ty - 11), (CW / 2 + tw_ / 2 + 3, ty + 10), (CW / 2 - tw_ / 2, ty + 11)]
    tpm = warp(poly(cv, tp), 0.7 * ss, 6 * ss, seed + 60)
    cv.paint(blur(shift(tpm, 1.2 * ss, 2.0 * ss), 1.0 * ss), hx('080612'), 0.4)
    cv.paint(blur(grow(tpm, 2.2 * ss), 0.3 * ss), INK)
    spray(cv, tpm, P['strip'], seed=seed + 66, grain=0.4, soft=0.6, over_d=0.0)
    if not NW[0]:
        marker_t = K.marker_text(cv, spec['fam'], CW / 2 + 0.5, ty + 0.5, 17, INK, rot=0.8, seed=seed + 31)

    # ---- rules text: dark marker on plaster, pink underline
    txt = spec['txt']
    px = 21
    f = font(MARKER, px * ss)
    while f.getlength(txt) / ss > CW - 66 and px > 14:
        px -= 1
        f = font(MARKER, px * ss)
    ly = 207
    if NW[0]:
        for q, wq in enumerate((0.7, 0.45)):
            st_ = stroke_mask(cv, [(CW / 2 - wq * 70, ly - 6 + q * 15), (CW / 2 + wq * 70, ly - 6 + q * 15 + 0.8)], 4.0, 3.4, wob=0.3, seed=seed + q, taper=(0.05, 0.05))
            cv.paint(blur(st_, 0.3 * ss), hx('1A1426'), 0.9)
    else:
        K.marker_text(cv, txt, CW / 2 + 0.5, ly, px, hx('16101F'), rot=-0.8, seed=seed + 32)
    wtxt = f.getlength(txt) / ss
    ul = stroke_mask(cv, [(CW / 2 - wtxt / 2 - 3, ly + 13.2), (CW / 2 - wtxt / 4, ly + 14.6), (CW / 2 + wtxt / 4, ly + 13.0), (CW / 2 + wtxt / 2 + 4, ly + 14.0)], 2.2, 1.3, wob=0.5, seed=seed + 36, taper=(0.1, 0.25))
    cv.paint(blur(ul, 0.3 * ss), PINK_LO if A else hx('2E6AE0'), 0.95)
    if spec.get('num') and not NW[0]:
        x1_ = CW / 2 + wtxt / 2
        pk = stroke_mask(cv, [(x1_ - 13, ly + 12), (x1_ - 7, ly + 14.5), (x1_ + 2, ly + 12.2)], 3.4, 2.0, wob=0.3, seed=seed + 33, taper=(0.1, 0.3))
        cv.paint(blur(pk, 0.3 * ss), PINK)
    K.scribble_tag(cv, CW - 36, 232, 0.62, PINK, seed + 50)

    # ---- drips off the title slab onto the plaster (left and right of the type stripe)
    for (dx_, ln, wd) in ((22, 17, 5.0), (CW - 24, 12, 4.4)):
        d = drip_mask(cv, dx_ + r_.uniform(-3, 3), sy1 - 1, ln, wd, seed=seed + int(dx_))
        cv.paint(blur(grow(d, 1.5 * ss), 0.3 * ss) * cm, INK)
        cv.paint(blur(d, 0.3 * ss) * cm, P['tdrop'])

    # ---- stickers: cost (RAM coin, system cyan) and the loud (Trace) tab
    K.cost_sticker(cv, 18, 20, cost, 17.5, seed=seed + 70)
    if loud:
        lx, ly2 = CW - 54, 17
        box = poly(cv, [(lx - 20, ly2 - 12), (lx + 20, ly2 - 12), (lx + 20, ly2 + 12), (lx - 20, ly2 + 12)])
        box = warp(box, 0.5 * ss, 8 * ss, seed + 80)
        cv.paint(blur(shift(box, 1.2 * ss, 2.4 * ss), 1.6 * ss), INK, 0.5)
        cv.paint(blur(grow(box, 3.4 * ss), 0.3 * ss), INK)
        cv.paint(blur(grow(box, 2.5 * ss), 0.3 * ss), hx('FFFCF4'))
        cv.paint(blur(box, 0.3 * ss), VIOLET)
        eye = circle(cv, lx - 9, ly2, 7.2)
        cv.paint(blur(grow(eye, 1.0 * ss), 0.3 * ss), INK)
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(blur(e2, 0.3 * ss), WHITE)
        cv.paint(blur(circle(cv, lx - 9, ly2, 2.9), 0.3 * ss), INK)
        if NW[0]:
            for q in range(int(loud)):
                st_ = stroke_mask(cv, [(lx + 8 + q * 6, ly2 - 7), (lx + 8.5 + q * 6, ly2 + 7)], 2.8, 2.4, wob=0.1, seed=q, taper=(0.05, 0.05))
                cv.paint(blur(st_, 0.3 * ss), WHITE)
        else:
            tag_text(cv, '+' + str(loud), lx + 10.5, ly2 + 0.5, 19, ANTON, fill=WHITE, fill2=WHITE, ink=INK, rim=INK, drop=INK, outline=1.4, rim_w=0, wob=0, hi=False, shadow=False)
    return cv


def render_card(name, variant='A', seed=0, ss=3, scale=1):
    VAR[0] = variant
    cv = card_M(name, seed, ss)
    return cv.to_image(scale=scale)


if __name__ == '__main__':
    import sys, time
    sys.dont_write_bytecode = True
    import asm_r2
    t = time.time()
    names = ['Brace', 'Spin3', 'Trigger', 'Twist']
    for vv in sys.argv[1] if len(sys.argv) > 1 else 'AB':
        ims = [render_card(n, vv, seed=i * 3 + 1, ss=3, scale=1) for i, n in enumerate(names)]
        sheet = Image.new('RGBA', (ims[0].width * 4 + 40, ims[0].height + 20), (40, 36, 52, 255))
        for i, im in enumerate(ims):
            sheet.alpha_composite(im, (10 + i * (im.width + 6), 10))
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS)
        sheet.save('D:/rc_scratch/combat_redesign/punk/mural_graffiti/out/cards_%s.png' % vv)
    print('cards', round(time.time() - t, 1))
