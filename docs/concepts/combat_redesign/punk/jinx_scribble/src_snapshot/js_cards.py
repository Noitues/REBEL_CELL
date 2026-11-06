"""js_cards: the CARD HAND in Jinx scribble.  Same layout as the black-book card (cost badge top left, big icon, title, type band, rules text, loud tab),
restyled: dark painterly card, neon chalk/marker scribbles, glitch misregistration on the icon and title.  Variants:
 A = night wall  (dark violet body, pink chalk frame, cyan type tape)
 B = paint       (hot-pink painted body, ink panels, cyan chalk)
render_card(name, variant, seed, ss, scale) -> RGBA PIL (canvas = card + 18 px margin each side at 1x), same contract as st_cards.render_card."""
import math, json, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from st_gfx import *
import st_tower as T
import js_doodle as D
import st_cards as K0

CW, CH, M = 176, 250, 18
NW = [False]
CARDS = K0.CARDS
J = K0.J

NPINK = hx('FF2E9A')
NPINK_HI = hx('FF8CCB')
NPINK_DK = hx('8A0E57')
NCYAN = hx('2EEBFF')
NCYAN_HI = hx('C4FCFF')
NCYAN_DK = hx('0B7F93')
CHALK = hx('F6F2FF')
NIGHT0 = hx('120A26')
NIGHT1 = hx('2A1654')
NIGHT2 = hx('432275')
INKB = hx('0A0716')
PAL_BODY = [hx('1B3A78'), hx('5A1A6E'), hx('3C2A94'), hx('0E5A7A'), hx('7A1A60'), hx('241552')]
PAL_BODY_B = [hx('FF6FC0'), hx('E0208A'), hx('A00E62'), hx('FF8CCB'), hx('6B2A9E')]
V_IS_A = [True]
CUR = ['A']

VAR = {
    'A': dict(body0=NIGHT0, body1=NIGHT1, frame=NPINK, frame2=NCYAN, band=hx('170C3A'), title=CHALK, strip=NCYAN, strip_txt=INKB, txt=CHALK, txt_panel=hx('1C1040'), under=NPINK, doodle=NCYAN, doodle2=NPINK, titlebg=hx('0A0618')),
    'B': dict(body0=hx('C4146F'), body1=hx('FF4DB0'), frame=INKB, frame2=NCYAN, band=hx('160B2E'), title=CHALK, strip=INKB, strip_txt=NCYAN_HI, txt=CHALK, txt_panel=hx('1A0D33'), under=NCYAN, doodle=NCYAN, doodle2=NPINK, titlebg=hx('0A0618')),
}


def chalk(cv, m, col, op=1.0, seed=0, glow=0.0, gcol=None, grain=0.55):
    """a chalk / paint-pen mark: broken grain edge, optional neon glow"""
    ss = cv.ss
    if glow > 0:
        cv.paint(blur(m, 2.2 * ss) * glow, gcol if gcol is not None else col, op)
    n = vnoise(cv.H, cv.W, 1.1 * ss, seed + 5, 1)
    n2 = vnoise(cv.H, cv.W, 4.0 * ss, seed + 9, 1)
    a = np.clip(m * (0.62 + grain * (n - 0.42) * 2.0 + 0.25 * (n2 - 0.5)), 0, 1)
    cv.paint(blur(a, 0.28 * ss), col, op)


def strokes(cv, lines, w, col, seed, op=1.0, glow=0.0, gcol=None, glitch=0.0, wob=0.35, taper=(0.12, 0.2), ink=0.0, gl_cols=(None, None)):
    for i, ln in enumerate(lines):
        if len(ln) < 2:
            continue
        m = stroke_mask(cv, ln, w, w * 0.8, wob=wob, seed=seed + i * 7, smooth=len(ln) > 3, taper=taper)
        if glitch:
            a, b = gl_cols
            for (dx, dy, c) in ((-glitch, glitch * 0.5, a), (glitch, -glitch * 0.4, b)):
                if c is not None:
                    chalk(cv, shift(m, dx * cv.ss, dy * cv.ss), c, 0.8 * op, seed + 31 + i)
        if ink:
            cv.paint(blur(grow(m, ink * cv.ss), 0.3 * cv.ss), INKB, 0.9 * op)
        chalk(cv, m, col, op, seed + i, glow, gcol)


def poly_(cv, pts):
    return poly(cv, pts)


def rrect(cv, x0, y0, x1, y1, seed, amp=1.2):
    m = poly(cv, [(x0, y0), (x1, y0 - 0.8), (x1 + 0.6, y1), (x0 - 0.5, y1 + 0.7)])
    return warp(m, amp * cv.ss, 14 * cv.ss, seed)


def painterly(cv, region, c0, c1, seed, tone=(0.0, 1.0), strokes_n=34, extra=None):
    """dark painterly base: vertical-ish gradient, then wide dry-brush strokes in nearby tones, a spray mist and fine grain"""
    ss = cv.ss
    X, Y = cv.grid()
    t = np.clip((Y + 0) / CH, 0, 1)
    col = lerp(c0[None, None, :], c1[None, None, :], t[..., None])
    cv.paint(region, col)
    r = np.random.default_rng(seed)
    for k in range(strokes_n):
        x = r.uniform(-10, CW + 10)
        y = r.uniform(-10, CH + 10)
        a = math.radians(r.choice([-62, -50, 28, 40, -70]) + r.uniform(-10, 10))
        L = r.uniform(30, 90)
        pts = [(x, y), (x + L * 0.5 * math.cos(a) + r.uniform(-6, 6), y + L * 0.5 * math.sin(a)), (x + L * math.cos(a), y + L * math.sin(a))]
        w = r.uniform(6, 20)
        m = stroke_mask(cv, pts, w, w * 0.6, wob=1.0, seed=seed + k, taper=(0.25, 0.4))
        n = vnoise(cv.H, cv.W, 1.4 * ss, seed + k, 1)
        # dry brush: streaks along the stroke
        m = m * np.clip((n - 0.25) * 2.2, 0, 1)
        cc = PAL_BODY[int(r.integers(0, len(PAL_BODY)))] if V_IS_A[0] else PAL_BODY_B[int(r.integers(0, len(PAL_BODY_B)))]
        cv.paint(blur(m, 0.5 * ss) * region, cc, r.uniform(0.35, 0.65))
    g = vnoise(cv.H, cv.W, 0.9 * ss, seed + 3, 1)
    cv.paint(region * np.clip((g - 0.5) * 0.35, 0, 1), CHALK, 0.30)
    cv.paint(region * np.clip((0.5 - g) * 0.45, 0, 1), INKB, 0.40)


def cost_badge(cv, x, y, cost, V, r=18.0, seed=0):
    ss = cv.ss
    c = warp(circle(cv, x, y, r + 3.2), 0.5 * ss, 8 * ss, seed)
    cv.paint(blur(shift(c, 1.6 * ss, 2.6 * ss), 1.6 * ss), INKB, 0.6)
    cv.paint(blur(grow(c, 1.0 * ss), 0.3 * ss), INKB)
    ring = np.clip(c - circle(cv, x, y, r - 1.5), 0, 1)
    cv.paint(blur(ring, 0.3 * ss), CHALK, 0.96)
    coin = circle(cv, x, y, r - 1.8)
    # misregistered pink plate under the cyan coin
    cv.paint(blur(shift(coin, 2.6 * ss, 1.8 * ss), 0.3 * ss), NPINK, 0.95)
    X, Y = cv.grid()
    tt = np.clip((Y - (y - r)) / (2 * r), 0, 1)
    cv.paint(blur(coin, 0.3 * ss), lerp(NCYAN_HI[None, None, :], hx('18C4E0')[None, None, :], tt[..., None]))
    gl = np.clip(coin - shift(coin, 2.4 * ss, 3.2 * ss), 0, 1) * coin
    cv.paint(blur(gl, 0.4 * ss), WHITE, 0.6)
    if NW[0]:
        for q in range(int(cost)):
            xq = x + (q - (int(cost) - 1) / 2) * 6.0
            st_ = stroke_mask(cv, [(xq, y - 8), (xq + 0.5, y + 8)], 2.8, 2.4, wob=0.15, seed=seed + q, taper=(0.05, 0.08))
            cv.paint(blur(st_, 0.3 * ss), INKB)
    else:
        tag_text(cv, str(cost), x + 0.3, y + 0.9, 29, ANTON, fill=INKB, fill2=INKB, ink=NCYAN_HI, rim=NCYAN_HI, drop=NPINK, drop_off=(1.0, 0.9), outline=0.0, rim_w=0.0, wob=0.0, hi=False, shadow=False)


DOOD = {
    'Brace': lambda: [('xmark', (26, 28, 7)), ('arrow', ((148, 112), (122, 104))), ('tally', (146, 30))],
    'Spin3': lambda: [('spiral', (28, 112, 12)), ('star4', (150, 30, 8)), ('xmark', (150, 108, 6))],
    'Trigger': lambda: [('bolt', (28, 108, 22)), ('star5', (146, 112, 8)), ('xmark', (26, 30, 6))],
    'Twist': lambda: [('crown', (30, 30, 20, 13)), ('arrow', ((140, 112), (150, 90))), ('star4', (30, 108, 7))],
}


def doodle_lines(kind, a):
    if kind == 'xmark':
        return D.xmark(*a)
    if kind == 'arrow':
        return D.arrow(*a)
    if kind == 'tally':
        return D.tally(a[0], a[1], 5, 11)
    if kind == 'spiral':
        return D.spiral(*a)
    if kind == 'star4':
        return D.star4(*a)
    if kind == 'star5':
        return D.star5(*a)
    if kind == 'bolt':
        return D.bolt(*a)
    if kind == 'crown':
        return D.crown(*a)
    return []


def card(name, V, seed=0, ss=3):
    spec = CARDS[name]
    cost, loud = J['cards'][name]
    cv = Cv(-M, -M, CW + 2 * M, CH + 2 * M, ss)
    X, Y = cv.grid()
    r_ = np.random.default_rng(seed)
    # ---- card body: rough-cut painted board
    body = rrect(cv, 1, 1, CW - 1, CH - 1, seed + 5, amp=1.7)
    body = np.clip((blur(body, 0.5 * ss) - 0.5) * 4 + 0.5, 0, 1)
    cv.paint(blur(shift(body, 3.0 * ss, 5.0 * ss), 3.0 * ss), INKB, 0.55)
    cv.paint(blur(grow(body, 2.2 * ss), 0.3 * ss), INKB)
    painterly(cv, body, V['body0'], V['body1'], seed + 11, extra=(NPINK if V is VAR['A'] else NCYAN), strokes_n=34)
    # spray mist in the corner (pink low-left in A, cyan in B), the Jinx wall haze
    mist = blur(circle(cv, 40, 245, 70), 18 * ss) * body
    cv.paint(mist * 0.5, NPINK if V is VAR['A'] else NCYAN, 0.55)
    # ---- frame: broken chalk line 5 px in, with a cyan misregistered copy
    inner = rrect(cv, 5.5, 5.5, CW - 5.5, CH - 5.5, seed + 8, amp=1.0)
    ring = np.clip(grow(inner, 0.9 * ss) - grow(inner, -0.9 * ss) if False else (blur(inner, 0.2) - shrink(inner, 1.7 * ss)), 0, 1)
    brk = (vnoise(cv.H, cv.W, 22 * ss, seed + 4, 1) > 0.22).astype(np.float32)
    chalk(cv, blur(shift(ring * brk, -1.8 * ss, 1.4 * ss), 0.3 * ss), V['frame2'], 0.85, seed + 3)
    chalk(cv, blur(ring * brk, 0.3 * ss), V['frame'] if V is VAR['A'] else INKB, 1.0, seed + 6, glow=0.5 if V is VAR['A'] else 0.0, gcol=NPINK)

    # ---- art band
    ab = rrect(cv, 9, 10, CW - 9, 128, seed + 40, amp=1.2) * body
    cv.paint(blur(grow(ab, 1.5 * ss), 0.3 * ss), INKB)
    cv.paint(ab, V['band'])
    # panel brushwork inside the band (dark teal/violet dry strokes)
    for k in range(30):
        x = r_.uniform(0, CW)
        y = r_.uniform(10, 128)
        a = math.radians(r_.choice([-60, 35, -45]) + r_.uniform(-8, 8))
        L = r_.uniform(24, 70)
        m = stroke_mask(cv, [(x, y), (x + L * math.cos(a), y + L * math.sin(a))], r_.uniform(5, 14), 3, wob=0.8, seed=seed + 200 + k, taper=(0.3, 0.4))
        m = m * np.clip((vnoise(cv.H, cv.W, 1.3 * ss, seed + 300 + k, 1) - 0.3) * 2.0, 0, 1)
        cv.paint(blur(m, 0.4 * ss) * ab, (PAL_BODY if V_IS_A[0] else PAL_BODY_B)[int(r_.integers(0, 6 if V_IS_A[0] else 5))], 0.55)
    icx, icy = CW / 2, 69
    # neon halo: pink bloom + scribble rings
    cv.paint(blur(circle(cv, icx, icy, 40), 12 * ss) * ab, NPINK_DK, 0.9)
    cv.paint(blur(circle(cv, icx, icy, 34), 9 * ss) * ab, NPINK, 0.55)
    for k, (rr, col, gl) in enumerate(((46, NPINK, 0.7), (52, NCYAN, 0.55))):
        ln = D.circle_s(icx + r_.uniform(-1.5, 1.5), icy + r_.uniform(-1.5, 1.5), rr, a0=r_.uniform(0, 360), over=56 + 14 * k, n=44, squash=0.97)
        m = stroke_mask(cv, ln[0], 3.0 - 0.6 * k, 2.2, wob=0.5, seed=seed + 60 + k, taper=(0.1, 0.3)) * ab
        chalk(cv, m, col, 1.0, seed + 61 + k, glow=gl)
    # doodles in the band corners
    for kind, a in DOOD[name]():
        ln = doodle_lines(kind, a)
        cc = V['doodle'] if kind in ('xmark', 'star4', 'spiral') else V['doodle2']
        strokes(cv, [[(p[0], p[1]) for p in l] for l in ln], 3.0, cc, seed + 90, glow=0.5, taper=(0.1, 0.2), wob=0.3)
    # the icon: chalk-white silhouette, cyan + pink misregistered plates, ink keyline
    gm = T.glyph_mask(spec['g'], 68, cv, icx, icy - 1)
    gm = warp(gm, 0.35 * ss, 6 * ss, seed + 21)
    cv.paint(blur(shift(gm, 3.6 * ss, 2.6 * ss), 0.35 * ss) * ab, NPINK)
    cv.paint(blur(shift(gm, -3.4 * ss, -1.8 * ss), 0.35 * ss) * ab, NCYAN)
    cv.paint(blur(grow(gm, 1.9 * ss), 0.3 * ss) * ab, INKB)
    cv.paint(blur(gm, 0.3 * ss) * ab, CHALK)
    # glitch bar: a thin horizontal slice of the icon displaced sideways
    gy = icy - 8 + (seed % 4) * 4
    band = ((Y > gy) & (Y < gy + 3.2)).astype(np.float32)
    cv.paint(blur(shift(gm, 6 * ss, 0), 0.3 * ss) * band * ab, NCYAN_HI)
    if spec.get('mult'):
        if NW[0]:
            for q in range(int(spec['mult'])):
                st_ = stroke_mask(cv, [(114 + q * 9, 88), (115 + q * 9, 108)], 4.4, 3.8, wob=0.2, seed=seed + q, taper=(0.05, 0.08))
                cv.paint(blur(grow(st_, 1.5 * ss), 0.3 * ss), INKB)
                cv.paint(blur(st_, 0.3 * ss), CHALK)
        else:
            tag_text(cv, '\u00d7' + spec['mult'], 125, 102, 34, ANTON, fill=CHALK, fill2=NCYAN_HI, ink=INKB, rim=INKB, drop=NPINK, drop_off=(2.4, 2.6), outline=2.0, rim_w=0.0, skew=0.12, rot=-4, wob=0.3, hi=False, seed=seed)

    # ---- title: ink strip with a pink chalk underline; big chalk-white Anton with cyan / pink plates behind it
    ty0, ty1 = 131, 163
    ts = rrect(cv, 6, ty0, CW - 6, ty1, seed + 44, amp=0.9) * body
    cv.paint(blur(shift(ts, 1.6 * ss, 2.4 * ss), 1.4 * ss), INKB, 0.5)
    cv.paint(blur(ts, 0.3 * ss), V['titlebg'], 0.9)
    ul = stroke_mask(cv, [(10, ty1 - 1.2), (60, ty1 - 2.4), (120, ty1 - 0.6), (CW - 10, ty1 - 1.6)], 2.6, 1.8, wob=0.5, seed=seed + 45, taper=(0.02, 0.2)) * body
    chalk(cv, ul, NPINK if V is VAR['A'] else NCYAN, 1.0, seed + 46, glow=0.4)
    if NW[0]:
        bar = stroke_mask(cv, [(30, 147), (CW / 2, 145), (CW - 30, 148)], 15, 12, wob=0.5, seed=seed + 4, taper=(0.04, 0.05))
        cv.paint(blur(bar, 0.4 * ss), CHALK)
    else:
        ft_ = font(ANTON, 40 * ss)
        wt_ = ft_.getlength(spec['nm']) / ss + 0.9 * len(spec['nm'])
        pxt_ = 36 if wt_ <= 130 else 36 * 130 / wt_
        tm = text_mask(cv, spec['nm'], CW / 2, 147.5, ANTON, pxt_, 'mm', 0.12, -2.0, 0.9, 0.3, seed)
        cv.paint(blur(shift(tm, 3.4 * ss, 2.6 * ss), 0.35 * ss), NPINK)
        cv.paint(blur(shift(tm, -2.8 * ss, -1.8 * ss), 0.35 * ss), NCYAN)
        cv.paint(blur(grow(tm, 1.7 * ss), 0.3 * ss), INKB)
        cv.paint(blur(tm, 0.3 * ss), CHALK)
    # ---- type tape: neon strip, ink marker text
    ty = 178
    tw_ = 78 if spec['fam'] == 'TOWER' else 68
    tp = rrect(cv, CW / 2 - tw_ / 2, ty - 10, CW / 2 + tw_ / 2, ty + 10, seed + 61, amp=0.7)
    cv.paint(blur(shift(tp, 1.2 * ss, 2.0 * ss), 1.1 * ss), INKB, 0.55)
    cv.paint(blur(shift(tp, 2.2 * ss, 1.6 * ss), 0.3 * ss), NPINK if V is VAR['A'] else NCYAN)
    cv.paint(blur(tp, 0.3 * ss), V['strip'])
    if not NW[0]:
        tm = text_mask(cv, spec['fam'], CW / 2 + 0.5, ty + 0.6, MARKER, 16, 'mm', 0.0, 0.8, 0.5, 0.2, seed + 31)
        cv.paint(blur(tm, 0.3 * ss), V['strip_txt'])
    # ---- rules text: chalk marker on a dark panel, underlined in the neon
    pn = rrect(cv, 9, 195, CW - 9, 233, seed + 66, amp=0.9) * body
    cv.paint(blur(pn, 0.3 * ss), V['txt_panel'], 0.92 if V is VAR['A'] else 0.96)
    cv.paint(blur(grow(pn, 1.2 * ss) - pn, 0.3 * ss), INKB, 0.9)
    txt = spec['txt']
    px = 21
    f = font(MARKER, px * ss)
    while f.getlength(txt) / ss > CW - 56 and px > 14:
        px -= 1
        f = font(MARKER, px * ss)
    ly = 211
    tcx = CW / 2 - 7
    if NW[0]:
        for q, wq in enumerate((0.7, 0.45)):
            st_ = stroke_mask(cv, [(CW / 2 - wq * 70, ly - 6 + q * 15), (CW / 2 + wq * 70, ly - 6 + q * 15 + 0.8)], 4.0, 3.4, wob=0.3, seed=seed + q, taper=(0.05, 0.05))
            cv.paint(blur(st_, 0.3 * ss), CHALK, 0.85)
    else:
        tm = text_mask(cv, txt, tcx + 0.5, ly, MARKER, px, 'mm', 0.0, -0.8, 0.0, 0.25, seed + 32)
        cv.paint(blur(grow(tm, 1.0 * ss), 0.3 * ss), INKB, 0.7)
        cv.paint(blur(tm, 0.3 * ss), CHALK)
    wtxt = f.getlength(txt) / ss
    uln = stroke_mask(cv, [(tcx - wtxt / 2 - 2, ly + 14), (tcx - wtxt / 4, ly + 15.4), (tcx + wtxt / 4, ly + 13.8), (tcx + wtxt / 2 + 3, ly + 14.8)], 2.0, 1.2, wob=0.5, seed=seed + 36, taper=(0.1, 0.25))
    chalk(cv, uln, V['under'], 1.0, seed + 37, glow=0.5)
    if spec.get('num') and not NW[0]:
        x1_ = tcx + wtxt / 2
        pk = stroke_mask(cv, [(x1_ - 13, ly + 12), (x1_ - 7, ly + 14.5), (x1_ + 2, ly + 12.2)], 3.4, 2.0, wob=0.3, seed=seed + 33, taper=(0.1, 0.3))
        chalk(cv, pk, NCYAN if V is VAR['A'] else NPINK, 1.0, seed + 38, glow=0.4)
    # a crude face, bottom right, on the margin (ownership mark; no letters)
    fl = D.face(CW - 17, 241, 6.2, a=-8)
    strokes(cv, fl, 1.5, NPINK if V is VAR['A'] else CHALK, seed + 120, glow=0.3, taper=(0.1, 0.1), wob=0.15)
    # ---- stickers: cost badge (system cyan coin) and the loud (Trace) tab
    cost_badge(cv, 18, 20, cost, V, 17.5, seed + 70)
    if loud:
        lx, ly2 = CW - 54, 17
        box = rrect(cv, lx - 20, ly2 - 12, lx + 20, ly2 + 12, seed + 80, amp=0.6)
        cv.paint(blur(shift(box, 1.2 * ss, 2.4 * ss), 1.6 * ss), INKB, 0.5)
        cv.paint(blur(grow(box, 2.6 * ss), 0.3 * ss), INKB)
        cv.paint(blur(grow(box, 1.5 * ss), 0.3 * ss), CHALK)
        cv.paint(blur(box, 0.3 * ss), VIOLET)
        eye = circle(cv, lx - 9, ly2, 7.2)
        cv.paint(blur(grow(eye, 1.0 * ss), 0.3 * ss), INKB)
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(blur(e2, 0.3 * ss), WHITE)
        cv.paint(blur(circle(cv, lx - 9, ly2, 2.9), 0.3 * ss), INKB)
        if NW[0]:
            for q in range(int(loud)):
                st_ = stroke_mask(cv, [(lx + 8 + q * 6, ly2 - 7), (lx + 8.5 + q * 6, ly2 + 7)], 2.8, 2.4, wob=0.1, seed=q, taper=(0.05, 0.05))
                cv.paint(blur(st_, 0.3 * ss), WHITE)
        else:
            tag_text(cv, '+' + str(loud), lx + 10.5, ly2 + 0.5, 19, ANTON, fill=WHITE, fill2=WHITE, ink=INKB, rim=INKB, drop=INKB, outline=1.4, rim_w=0, wob=0, hi=False, shadow=False)
    return cv


def render_card(name, variant='A', seed=0, ss=3, scale=1):
    V = VAR[variant]
    V_IS_A[0] = variant == 'A'
    cv = card(name, V, seed, ss)
    return cv.to_image(scale=scale)


if __name__ == '__main__':
    import time
    import asm_r2 as A
    A.setup()
    t = time.time()
    SS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    var = sys.argv[1] if len(sys.argv) > 1 else 'A'
    ims = [render_card(n, var, seed=s, ss=SS, scale=2) for n, s in (('Brace', 1), ('Spin3', 4), ('Trigger', 7), ('Twist', 10))]
    W = sum(i.width for i in ims)
    sheet = Image.new('RGBA', (W, ims[0].height), (30, 26, 44, 255))
    x = 0
    for i in ims:
        sheet.alpha_composite(i, (x, 0))
        x += i.width
    sheet.save('D:/rc_scratch/combat_redesign/punk/jinx_scribble/out/cards_%s.png' % var)
    print(time.time() - t)
