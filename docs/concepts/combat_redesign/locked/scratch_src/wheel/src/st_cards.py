"""sg_cards: the CARD HAND in street-graffiti.  A = wheat-paste posters (torn paper, tape type band, tag title, sticker cost);
B = die-cut vinyl stickers (thick paper border, stencil print with misregistered key, peeling corner).
Game information is unchanged: cost, title, type, rules text, multiplier, loud (Trace) tab."""
import math, json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T

CW, CH, M = 176, 250, 18
NW = [False]      # nowords proxy: bars and tally strokes instead of words and digits

J = json.load(open('D:/rc_scratch/combat_redesign/locked/wheel/state_e10.json'))
CARDS = {
    'Brace': dict(fam='TOWER', g='C_BRACE', txt='Block a slice', nm='BRACE', num=None),
    'Spin3': dict(fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 3', nm='SPIN 3', num='3', mult='3'),
    'Trigger': dict(fam='WAVE', g='C_TRIG', txt='Resolve a unit', nm='TRIGGER', num=None),
    'Twist': dict(fam='WAVE', g='C_TWIST', txt='Turn one ring 1', nm='TWIST', num='1'),
    'Strike': dict(fam='TOWER', g='C_STRIKE', txt='Hit a unit for 2', nm='STRIKE', num='2'),
}


def cvc(ss=3):
    cv = Cv(-M, -M, CW + 2 * M, CH + 2 * M, ss)
    return cv


def place_mask(cv, a, x, y):
    """a is a mask built at its own size: nothing"""
    return a


def marker_text(cv, txt, x, y, px, color=ZINE, anchor='mm', rot=0.0, seed=0, wob=0.25, op=1.0):
    m = text_mask(cv, txt, x, y, MARKER, px, anchor, 0.0, rot, 0.0, wob, seed)
    cv.paint(blur(m, 0.3 * cv.ss), color, op)
    return m


def scribble_tag(cv, x, y, scale, color, seed, ink=True, ss_op=1.0):
    """an abstract tag mark (no letters): a fast zig-zag with an arrowhead, two dots and an underline swoosh"""
    k = scale
    zz = [(x - 26 * k, y + 5 * k), (x - 14 * k, y - 9 * k), (x - 2 * k, y + 7 * k), (x + 10 * k, y - 9 * k), (x + 22 * k, y + 3 * k)]
    st = stroke_mask(cv, zz, 5.2 * k, 3.4 * k, wob=0.4, seed=seed, taper=(0.1, 0.12), smooth=True)
    ah = poly(cv, [(x + 20 * k, y - 6 * k), (x + 33 * k, y + 4 * k), (x + 19 * k, y + 10 * k)])
    st = np.maximum(st, ah)
    for (dx_, dy_) in ((-28, -9), (-20, -14)):
        st = np.maximum(st, circle(cv, x + dx_ * k, y + dy_ * k, 1.9 * k))
    sw = stroke_mask(cv, [(x - 28 * k, y + 15 * k), (x, y + 18 * k), (x + 30 * k, y + 12 * k)], 3.0 * k, 1.2 * k, wob=0.3, seed=seed + 3, taper=(0.1, 0.4))
    st = np.maximum(st, sw)
    if ink:
        cv.paint(blur(grow(st, 1.2 * cv.ss), 0.3 * cv.ss), INK, ss_op * 0.9)
    cv.paint(blur(st, 0.3 * cv.ss), color, ss_op)
    return st


def cost_sticker(cv, x, y, cost, r=19.0, rot=0.0, seed=0):
    ss = cv.ss
    c = circle(cv, x, y, r + 3.6)
    c = warp(c, 0.5 * ss, 8 * ss, seed)
    sh = blur(shift(c, 1.5 * ss, 3.0 * ss), 2.0 * ss)
    cv.paint(sh, INK, 0.55)
    cv.paint(blur(grow(c, 1.1 * ss), 0.3 * ss), INK)
    cv.paint(blur(c, 0.3 * ss), PAPER)
    coin = circle(cv, x, y, r - 0.4)
    cv.paint(blur(coin, 0.3 * ss), hx('1A8FB8'))
    inner = circle(cv, x, y, r - 2.2)
    X, Y = cv.grid()
    tt = np.clip((Y - (y - r)) / (2 * r), 0, 1)
    cv.paint(blur(inner, 0.3 * ss), lerp(CYAN[None, None, :], hx('2AB4E0')[None, None, :], tt[..., None]))
    # gloss crescent
    gl = np.clip(inner - shift(inner, 3.0 * ss, 4.2 * ss), 0, 1) * inner
    cv.paint(blur(gl, 0.5 * ss), WHITE, 0.7)
    if NW[0]:
        for q in range(int(cost)):
            xq = x + (q - (int(cost) - 1) / 2) * 6.0
            st_ = stroke_mask(cv, [(xq, y - 8), (xq + 0.5, y + 8)], 2.6, 2.2, wob=0.15, seed=seed + q, taper=(0.05, 0.08))
            cv.paint(blur(st_, 0.3 * ss), INK)
    else:
        tag_text(cv, str(cost), x + 0.2, y + 0.8, 28, ANTON, fill=INK, fill2=INK, ink=PAPER, rim=PAPER, drop=hx('1A8FB8'), drop_off=(0.9, 1.0), outline=0.0, rim_w=0.0, wob=0.0, hi=False, shadow=False)


# ==================================================================== A: wheat-paste poster
def card_A(name, seed=0, ss=3):
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    cv = cvc(ss)
    X, Y = cv.grid()
    core, full = torn_mask(CW, CH, rough=2.4, seed=seed + 5, ss=ss)
    # the paste sheet lives in canvas coords: pad the torn mask into the canvas
    pad = M * ss
    cm = np.zeros((cv.H, cv.W), np.float32); fm = np.zeros((cv.H, cv.W), np.float32)
    cm[pad:pad + core.shape[0], pad:pad + core.shape[1]] = core
    fm[pad:pad + full.shape[0], pad:pad + full.shape[1]] = full
    # glue squeeze-out halo + paper
    cv.paint(blur(grow(fm, 2.4 * ss), 1.4 * ss) * 0.28, hx('E7E2D6'))
    ptex, ridge = paper(CW, CH, seed=seed + 11, ss=ss, wrinkle=0.45)
    pt = np.zeros((cv.H, cv.W, 3), np.float32) + PAPER
    pt[pad:pad + ptex.shape[0], pad:pad + ptex.shape[1]] = ptex
    fibre = np.clip(fm - cm, 0, 1)
    cv.paint(fm, pt * 0.97)
    cv.paint(cm, pt)
    cv.paint(fibre * 0.5, WHITE)
    # horizontal fold crease and glue wrinkles (soft dark + light line)
    cy_ = 120 + (seed % 3) * 4
    crease = np.exp(-((Y - cy_) ** 2) / 0.9) * 0.10 * cm
    cv.paint(crease, hx('7A705E'))
    cv.paint(np.exp(-((Y - cy_ - 1.6) ** 2) / 0.9) * 0.18 * cm, WHITE)

    # ---------------------------------------------------------------- art band: a painted wall chunk
    ab = np.zeros((cv.H, cv.W), np.float32)
    x0, y0, x1, y1 = 9, 10, CW - 9, 128
    P = [cv.p(a, b) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    ab = pil_mask(cv.H, cv.W, lambda d: d.polygon(P, fill=255))
    ab = warp(ab, 1.6 * ss, 14 * ss, seed + 40) * cm
    cv.paint(blur(grow(ab, 1.4 * ss), 0.4 * ss), INK)
    wall(cv, ab, seed=seed + 2, base=hx('2A2234'), hi=hx('4A3F58'), strength=1.15)
    # old buffed marks
    r_ = np.random.default_rng(seed)
    for k in range(5):
        xa = r_.uniform(16, CW - 16); ya = r_.uniform(16, 120)
        sc = stroke_mask(cv, [(xa, ya), (xa + r_.uniform(10, 26), ya + r_.uniform(-8, 8)), (xa + r_.uniform(26, 44), ya + r_.uniform(-10, 10))], 2.2, 3.5, wob=1.0, seed=seed + k, taper=(0.2, 0.3))
        cv.paint(blur(sc, 0.8 * ss) * 0.12 * ab, hx('7A6C8E'))
    # spray bloom + fat-cap ring behind the icon
    icx, icy = CW / 2, 66
    bloom = circle(cv, icx, icy, 46)
    cv.paint(blur(bloom, 15 * ss) * ab * 0.9, PINK_LO)
    rb = np.random.default_rng(seed + 90)
    rays = np.zeros((cv.H, cv.W), np.float32)
    for q in range(16):
        a = math.radians(q * 22.5 + rb.uniform(-5, 5))
        r0_, r1_ = rb.uniform(44, 50), rb.uniform(58, 82)
        rays = np.maximum(rays, stroke_mask(cv, [(icx + r0_ * math.cos(a), icy + r0_ * math.sin(a)), (icx + r1_ * math.cos(a), icy + r1_ * math.sin(a))], 4.2, 0.8, smooth=False, wob=0.2, seed=q))
    cv.paint(blur(rays, 0.4 * ss) * ab * 0.55, PINK_LO)
    disc = circle(cv, icx, icy, 40)
    disc = warp(disc, 1.4 * ss, 12 * ss, seed + 3)
    col = lerp(PINK_LO[None, None, :], PINK[None, None, :], np.clip(0.2 + (icy - Y + 40) / 80.0 * 0.6 + 0.2, 0, 1)[..., None])
    spray(cv, disc * ab, col, seed=seed + 9, grain=0.55, soft=0.8, over_d=0.5, over_s=5.5, over_op=0.7, clip=ab)
    ring = stroke_mask(cv, [(icx + 47 * math.cos(math.radians(a)), icy + 47 * math.sin(math.radians(a))) for a in range(-200, 120, 12)], 4.6, 2.2, wob=0.6, seed=seed + 4, taper=(0.1, 0.3))
    ring = ring * ab
    cv.paint(blur(grow(ring, 1.3 * ss), 0.3 * ss), INK)
    cv.paint(blur(ring, 0.4 * ss), PAPER)
    # the icon: white stencil silhouette, ink keyline, pink-dark extruded drop
    gm = T.glyph_mask(spec['g'], 66, cv, icx, icy - 1)
    gm = warp(gm, 0.4 * ss, 6 * ss, seed + 21)
    cv.paint(blur(extrude(gm, 4.0 * ss, 4.6 * ss), 0.4 * ss) * ab, PINK_DK)
    cv.paint(blur(grow(gm, 2.6 * ss), 0.35 * ss) * ab, INK)
    cv.paint(blur(gm, 0.3 * ss) * ab, WHITE)
    # sticker-tag stars (glints)
    for (gx, gy, gr) in ((icx - 54, icy - 36, 5.5), (icx + 52, icy + 30, 4.2)):
        pts = []
        for q in range(8):
            rad = gr if q % 2 == 0 else gr * 0.28
            a = math.pi / 4 * q - math.pi / 2
            pts.append((gx + rad * math.cos(a), gy + rad * math.sin(a)))
        st = poly(cv, pts)
        cv.paint(blur(grow(st, 1.0 * ss), 0.3 * ss) * ab, INK)
        cv.paint(blur(st, 0.3 * ss) * ab, PAPER)
    if spec.get('mult'):                                                 # the multiplier, painted on the wall as a stencil
        if NW[0]:
            for q in range(int(spec['mult'])):
                st_ = stroke_mask(cv, [(114 + q * 9, 88), (115 + q * 9, 108)], 4.4, 3.8, wob=0.2, seed=seed + q, taper=(0.05, 0.08))
                cv.paint(blur(grow(st_, 1.5 * ss), 0.3 * ss), INK)
                cv.paint(blur(st_, 0.3 * ss), PAPER)
        else:
            tag_text(cv, '\u00d7' + spec['mult'], 125, 100, 34, ANTON, fill=PAPER, fill2=CHROME, ink=INK, rim=INK, drop=PINK, drop_off=(2.4, 2.8), outline=2.0, rim_w=0.0, skew=0.14, rot=-4, wob=0.3, hi=False, seed=seed)
        # ensure it stays inside the band
    # specks of overspray running over the paper under the band edge
    od = np.clip(blur(ab, 4.0 * ss) * 1.8 - 0.35, 0, 1) * (1 - ab) * cm
    dots = (r_.random(ab.shape) < od * 0.015).astype(np.float32)
    cv.paint(np.clip(ndi.gaussian_filter(dots, 0.5 * ss) * 4, 0, 1) * 0.5, PINK_LO)

    # ---------------------------------------------------------------- title: a fat tag, overlapping the band's lower edge
    if NW[0]:
        bar = stroke_mask(cv, [(30, 142), (CW / 2, 139), (CW - 30, 143)], 15, 12, wob=0.5, seed=seed + 4, taper=(0.04, 0.05))
        cv.paint(blur(grow(bar, 2.5 * ss), 0.4 * ss), INK)
        cv.paint(blur(bar, 0.4 * ss), PINK)
    else:
      ft_ = font(ANTON, 40 * ss)
      wt_ = ft_.getlength(spec['nm']) / ss + 0.8 * len(spec['nm'])
      pxt_ = 40 if wt_ <= 118 else 40 * 118 / wt_
      tag_text(cv, spec['nm'], CW / 2 - 1, 141, pxt_, ANTON, fill=PINK, fill2=PINK_LO, ink=INK, rim=CHROME, drop=PINK_DK, drop_off=(3.2, 3.8), outline=2.5, rim_w=1.6,
               skew=0.16, rot=-3.0, track=0.8, wob=0.35, seed=seed)

    # ---------------------------------------------------------------- type tape strip
    ty = 170
    tw_ = 74 if spec['fam'] == 'TOWER' else 66
    tp = [(CW / 2 - tw_ / 2 - 2, ty - 10), (CW / 2 + tw_ / 2 + 1, ty - 11), (CW / 2 + tw_ / 2 + 3, ty + 10), (CW / 2 - tw_ / 2, ty + 11)]
    # zig-zag torn ends
    tpm = poly(cv, tp)
    zz = np.abs(((X - (CW / 2 - tw_ / 2 - 2)) * 1.2) % 3.2 - 1.6) < 0.8
    tpm = warp(tpm, 0.7 * ss, 6 * ss, seed + 60)
    cv.paint(blur(shift(tpm, 1.0 * ss, 1.6 * ss), 1.0 * ss) * 0.35, INK)
    cv.paint(blur(tpm, 0.3 * ss), hx('C69A62'), 0.97)
    cv.paint(blur(tpm * (vnoise(cv.H, cv.W, 2 * ss, seed, 1) > 0.5), 0.5 * ss), WHITE, 0.10)
    if not NW[0]:
        marker_text(cv, spec['fam'], CW / 2 + 0.5, ty + 0.5, 17, ZINE, rot=0.8, seed=seed + 31)

    # ---------------------------------------------------------------- rules text (marker on paper) with a pink underline on the number
    txt = spec['txt']
    px = 21
    f = font(MARKER, px * ss)
    while f.getlength(txt) / ss > CW - 68 and px > 14:
        px -= 1; f = font(MARKER, px * ss)
    ly = 206
    m_ = None
    if NW[0]:
        for q, wq in enumerate((0.7, 0.45)):
            st_ = stroke_mask(cv, [(CW / 2 - wq * 70, ly - 6 + q * 15), (CW / 2 + wq * 70, ly - 6 + q * 15 + 0.8)], 4.0, 3.4, wob=0.3, seed=seed + q, taper=(0.05, 0.05))
            cv.paint(blur(st_, 0.3 * ss), ZINE, 0.85)
    else:
        m = marker_text(cv, txt, CW / 2 + 0.5, ly, px, ZINE, rot=-0.8, seed=seed + 32)
    wtxt = f.getlength(txt) / ss
    ul = stroke_mask(cv, [(CW / 2 - wtxt / 2 - 3, ly + 13.2), (CW / 2 - wtxt / 4, ly + 14.6), (CW / 2 + wtxt / 4, ly + 13.0), (CW / 2 + wtxt / 2 + 4, ly + 14.0)], 1.9, 1.1, wob=0.5, seed=seed + 36, taper=(0.1, 0.25))
    cv.paint(blur(ul, 0.3 * ss), hx('2C3E9E'), 0.92)
    if spec.get('num') and not NW[0]:
        w_ = f.getlength(txt) / ss
        x1_ = CW / 2 + w_ / 2
        pk = stroke_mask(cv, [(x1_ - 13, ly + 12), (x1_ - 7, ly + 14.5), (x1_ + 2, ly + 12.2)], 3.2, 2.0, wob=0.3, seed=seed + 33, taper=(0.1, 0.3))
        cv.paint(blur(pk, 0.3 * ss), PINK)
    # tiny marker scribble tag, bottom right (abstract: ownership, no letters)
    scribble_tag(cv, CW - 38, 231, 0.62, PINK, seed + 50)

    # ---------------------------------------------------------------- stickers: cost (RAM coin, system cyan) and the loud (Trace) tab
    cost_sticker(cv, 18, 20, cost, 17.5, seed=seed + 70)
    if loud:
        lx, ly2 = CW - 54, 17
        box = poly(cv, [(lx - 20, ly2 - 12), (lx + 20, ly2 - 12), (lx + 20, ly2 + 12), (lx - 20, ly2 + 12)])
        box = warp(box, 0.5 * ss, 8 * ss, seed + 80)
        sh = blur(shift(box, 1.2 * ss, 2.4 * ss), 1.6 * ss)
        cv.paint(sh, INK, 0.5)
        cv.paint(blur(grow(box, 3.4 * ss), 0.3 * ss), INK)
        cv.paint(blur(grow(box, 2.5 * ss), 0.3 * ss), PAPER)
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

    # paper over-wash: edge darkening (glue), vignette, and slight cold grade
    ed = np.clip(1 - (np.minimum.reduce([X + 0, CW - X, Y + 0, CH - Y])) / 10.0, 0, 1) * cm
    cv.paint(ed * 0.0, INK)
    return cv


def render_card(name, variant='A', seed=0, ss=3, scale=1):
    cv = card_A(name, seed, ss) if variant == 'A' else card_B(name, seed, ss)
    im = cv.to_image(scale=scale)
    if variant != 'A':
        return im
    k = scale
    # a second, older poster sheet peeking out underneath: another torn sheet, tilted, offset, darker (wheat-paste stack)
    core, full = torn_mask(CW - 4, CH - 10, rough=2.8, seed=seed + 77, ss=k)
    ox, oy = (M + 2) * k, (M + 7) * k
    a = np.zeros((im.height, im.width), np.float32)
    a[oy:oy + full.shape[0], ox:ox + full.shape[1]] = full
    tex = paper(CW - 4, CH - 10, seed=seed + 78, ss=k, wrinkle=0.2)[0] * np.array([0.86, 0.84, 0.79], np.float32)
    rgb = np.zeros((im.height, im.width, 3), np.float32) + hx('CFC8B6')
    rgb[oy:oy + tex.shape[0], ox:ox + tex.shape[1]] = tex
    ui = Image.fromarray((np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1) * 255).astype(np.uint8), 'RGBA')
    ui = ui.rotate(2.6 if seed % 2 else -2.6, resample=Image.BICUBIC, center=(im.width / 2, im.height / 2 + 20 * k)).transform(im.size, Image.AFFINE, (1, 0, (-4 if seed % 2 else 4) * k, 0, 1, 3 * k))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sha = im.split()[3].filter(ImageFilter.GaussianBlur(2.5 * k)).point(lambda v: int(v * 0.5))
    out.alpha_composite(ui)
    sh_im = Image.new('RGBA', im.size, (20, 12, 30, 0)); sh_im.putalpha(sha)
    out.alpha_composite(sh_im, (k, 2 * k))
    out.alpha_composite(im)
    return out


def card_B(name, seed=0, ss=3):
    import sg_B
    return sg_B.card_B(name, seed, ss)


if __name__ == '__main__':
    import sys, time
    sys.dont_write_bytecode = True
    import asm_r2
    t = time.time()
    names = ['Brace', 'Spin3', 'Trigger', 'Twist']
    ims = [render_card(n, 'A', seed=i * 3 + 1) for i, n in enumerate(names)]
    sheet = Image.new('RGBA', (ims[0].width * 4 + 40, ims[0].height + 20), (40, 36, 52, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (10 + i * (im.width + 6), 10))
    sheet.save('D:/rc_scratch/combat_redesign/street_graffiti/work/cards_A.png')
    sheet.resize((sheet.width * 2 // 1, sheet.height * 2 // 1), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/street_graffiti/work/cards_A_view.png')
    print('cards', round(time.time() - t, 1))
