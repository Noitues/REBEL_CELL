"""the card hand in the black-book hand.  render_card(name, variant) -> RGBA PIL (CW x CH at 1x)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from sg_lib import *
from sg_icons import *

CW, CH = 188, 256
CARDS = {
    'Brace': dict(icon='BRACE', title='BRACE', tag='TOWER', rules='Block a slice'),
    'Spin3': dict(icon='SPIN', title='SPIN 3', tag='TOWER', rules='Turn the tower 3', mult='3'),
    'Trigger': dict(icon='TRIGGER', title='TRIGGER', tag='WAVE', rules='Resolve a unit', loud='+1'),
    'Twist': dict(icon='TWIST', title='TWIST', tag='WAVE', rules='Turn one ring 1'),
}
COSTS = {'Brace': 1, 'Spin3': 1, 'Trigger': 1, 'Twist': 0}
SEEDS = {'Brace': 3, 'Spin3': 7, 'Trigger': 13, 'Twist': 19}


def rot_rect(c, w, h, ang):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def sticker_disc(cv, c, r, fill, label, fnt_px=19, tcol=INK):
    S = cv.S
    sh = cv.circle_mask((c[0] + 1.4, c[1] + 1.8), r + 2.2)
    cv.over(ndi.gaussian_filter(sh, 1.2 * S), (10, 8, 16), 0.35)
    cv.over(cv.circle_mask(c, r + 2.2), (250, 250, 246), 1.0)      # die-cut white margin
    ink_edge(cv, cv.circle_mask(c, r + 2.2), 0, 0, (60, 60, 70), 0.7, 0.55, wob=0.3)
    m = cv.circle_mask(c, r)
    cv.over(ndi.gaussian_filter(outline_mask(m, S, 1.6), 0.3) * 1.5, INK, 0.97)
    cv.over(m, fill, 1.0)
    # sheen
    marker(cv, [pol(c, r * 0.6, -50), pol(c, r * 0.6, 20)], (235, 252, 255), w=1.6, alpha=0.6, wob=0.1, grain=0)
    tag_text(cv, label, (c[0], c[1] + 1.0), fnt_px, fnt=ANTON_F, col=tcol, alpha=1.0, wob=0.1)


def card_shape(cv, V, rect, bites=True):
    S = cv.S
    x0, y0, x1, y1 = rect
    jit = lambda: cv.r.uniform(-1.2, 1.2)
    pts = [(x0 + jit(), y0 + jit()), (x1 + jit(), y0 + jit() - 1), (x1 + jit(), y1 + jit()), (x0 + jit(), y1 + jit() + 1)]
    m = cv.poly_mask(pts)
    if bites:
        for yy in np.arange(y0 + 14, y1 - 8, 15.5):
            m = np.clip(m - cv.circle_mask((x0 + 0.3 + cv.r.uniform(-0.6, 0.6), yy + cv.r.uniform(-1, 1)), 3.1), 0, 1)
    return m


def card_text(cv, name, V):
    pass


def wavy(cv, p0, p1, amp=2.0, n=6, col=BLUE, w=0.9, alpha=0.85):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    d = p1 - p0
    nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9)
    t = np.linspace(0, 1, 40)
    pts = [p0 + d * u + nrm * amp * math.sin(u * n * 2 * math.pi) for u in t]
    ballpoint(cv, pts, col, w, alpha, wob=0.15, wl=20)


def type_tag(cv, tag, c, V):
    S = cv.S
    if tag == 'TOWER':      # square-cornered highlighter box with a crenel doodle
        w, h = 58, 17
        pts = rot_rect(c, w, h, -1.5)
        m = cv.poly_mask(pts)
        m = warp(m, 0.5 * S, 9 * S, cv.r)
        marker(cv, [(c[0] - w / 2 + 3, c[1] + 0.3), (c[0] + w / 2 - 3, c[1] - 0.6)], PINK_L, w=h - 1, nib='chisel', ang=90, alpha=0.8, wob=0.3, mode='mult', taper=(0, 0), rough=0.4)
        ink_edge(cv, m, 0, 0, INK, 1.1, 0.9, wob=0.5)
        letters(cv, 'TOWER', (c[0], c[1] + 0.8), 12, fill=INK, ink_w=0, outline=False, miss=(0, 0), wob=0.1, spacing=0.8)
    else:                   # pill with a wave squiggle
        w, h = 58, 17
        pts = []
        for a in np.linspace(-90, 90, 14):
            pts.append((c[0] + w / 2 - h / 2 + h / 2 * math.cos(math.radians(a)) * 1.0, c[1] + h / 2 * math.sin(math.radians(a))))
        for a in np.linspace(90, 270, 14):
            pts.append((c[0] - w / 2 + h / 2 + h / 2 * math.cos(math.radians(a)), c[1] + h / 2 * math.sin(math.radians(a))))
        m = cv.poly_mask(pts)
        m = warp(m, 0.5 * S, 9 * S, cv.r)
        marker(cv, [(c[0] - w / 2 + 6, c[1] + 0.2), (c[0] + w / 2 - 6, c[1] - 0.5)], PINK_L, w=h - 1, nib='round', alpha=0.8, wob=0.3, mode='mult', taper=(0, 0), rough=0.4)
        ink_edge(cv, m, 0, 0, INK, 1.1, 0.9, wob=0.5)
        wavy(cv, (c[0] - w / 2 + 6, c[1] + 0.6), (c[0] - w / 2 + 17, c[1] + 0.6), 2.2, 2, INK, 1.0, 0.9)
        letters(cv, 'WAVE', (c[0] + 9, c[1] + 0.8), 12, fill=INK, ink_w=0, outline=False, miss=(0, 0), wob=0.1, spacing=0.8)


def draw_loud(cv, c, ang, txt):
    S = cv.S
    pts = rot_rect(c, 34, 28, ang)
    m = cv.poly_mask(pts)
    m = warp(m, 0.3 * S, 8 * S, cv.r)
    sh = np.roll(np.roll(m, int(1.6 * S), 0), int(1.6 * S), 1)
    cv.over(ndi.gaussian_filter(sh, 1.2 * S), (10, 8, 16), 0.4)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, S, 2.0), 0.3) * 1.5, 0, 1), (250, 250, 246), 1.0)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(m, S, 0.9, inner=0), 0.3) * 1.5, 0, 1) * 0, INK, 0.0)
    cv.over(m, VIOLET, 1.0)
    ink_edge(cv, m, 0, 0, INK, 1.0, 0.95, wob=0.3)
    ex, ey = c[0] - 7.5, c[1]
    eye = [(ex + 7 * math.cos(math.radians(a)) , ey + 4.2 * math.sin(math.radians(a))) for a in np.linspace(0, 360, 20)]
    em = cv.poly_mask(eye)
    cv.over(em, WHITE, 1.0)
    cv.over(cv.circle_mask((ex, ey), 2.4), INK, 1.0)
    tag_text(cv, txt, (c[0] + 8.5, c[1] + 0.5), 14, fnt=ANTON_F, col=WHITE, alpha=1.0, wob=0.1)


def render_card(name, variant='A', cost=None, S=4, seed=None, ret_cv=False):
    C = CARDS[name]
    cost = COSTS[name] if cost is None else cost
    cv = Canvas(CW, CH, S, seed=SEEDS[name] + (0 if variant == 'A' else 50))
    r = cv.r
    A = variant == 'A'
    rect = (8, 10, 180, 246)
    shape = card_shape(cv, variant, rect, bites=A)
    if A:
        t, rim = torn_mask(cv, shape, rough=1.4, fringe=0.9)
        pap = paper_rgb(cv, 'graph', PAPER, pitch=12.0)
    else:
        t, rim = torn_mask(cv, shape, rough=0.5, fringe=0.5)
        pap = paper_rgb(cv, 'ruled', (246, 242, 232), pitch=15.0)
    cv.over_rgb(t, pap)
    cv.over(np.clip(rim, 0, 1) * 0.5, (252, 250, 244), 1.0)
    if not A:   # heavy black chisel border
        ring = outline_mask(t, S, 3.0, inner=0)
        inner = ndi.binary_erosion(t > 0.5, iterations=int(0.4 * S))
        bord = edge_ring(ndi.binary_erosion(t > 0.5, iterations=int(2.6 * S)).astype(np.float32), S, 3.2)
        bord = warp(bord, 0.8 * S, 12 * S, r)
        cv.over(np.clip(ndi.gaussian_filter(bord, 0.4) * 1.4, 0, 1), INK, 0.97)
    # ---- art panel
    ax0, ay0, ax1, ay1 = (18, 44, 170, 138) if A else (20, 46, 168, 140)
    pj = lambda: r.uniform(-1.3, 1.3)
    panel = cv.poly_mask([(ax0 + pj(), ay0 + pj()), (ax1 + pj(), ay0 + pj()), (ax1 + pj(), ay1 + pj()), (ax0 + pj(), ay1 + pj())])
    panel = warp(panel, 0.8 * S, 20 * S, r)
    psol = np.clip((ndi.gaussian_filter(panel, 0.5) - 0.5) * 6, 0, 1)
    if not A:
        ex = np.zeros_like(psol)
        for k in range(1, int(5 * S) + 1):
            ex = np.maximum(ex, np.roll(np.roll(psol, int(k * 0.8), 0), int(k * 0.8), 1))
        ex = np.clip(ex - psol, 0, 1)
        cv.over(ex, INK, 0.97)
        hatch_region(cv, ex, 0, 0, (228, 222, 210), ang=135, pitch=3.1, w=0.8, alpha=0.5, over=0.2, jit=0.15)
    ink_edge(cv, psol, 0, 0, INK, 2.6 if A else 3.2, 0.97, wob=0.9, rough='out')
    fill_region(cv, psol, 0, 0, PINK, ang=28 if A else -62, nib=8.0, over=1.6, miss=(1.6, 1.2), jit=0.5, clip=1.0)
    strip = np.clip(psol - np.roll(np.roll(psol, int(-8 * S), 0), int(-8 * S), 1), 0, 1)
    hatch_region(cv, strip, 0, 0, (120, 14, 70), ang=135, pitch=3.0, w=1.0, alpha=0.7, over=0.3, jit=0.2)
    ic = ((ax0 + ax1) / 2 + (0 if not C.get('mult') else -10), (ay0 + ay1) / 2 + 1)
    # energy lines behind the icon
    for k in range(12):
        a = k * 30 + r.uniform(-6, 6)
        marker(cv, [pol(ic, 44, a), pol(ic, 58 + r.uniform(0, 12), a)], PINK_L, w=2.2 if k % 2 else 3.2, alpha=0.65, wob=0.2, taper=(0.1, 0.5), grain=0.1)
    draw_icon(cv, C['icon'], ic, 76, 0.0, shadow=((100, 10, 66), 0.65))
    # shine strokes (upper left)
    for q in range(3):
        marker(cv, [(ax0 + 10 + q * 6, ay0 + 20 - q * 3 + 6), (ax0 + 22 + q * 6, ay0 + 8 - q * 3 + 6)], (255, 255, 255), w=2.0 - q * 0.3, alpha=0.8, wob=0.1, taper=(0.1, 0.4))
    # multiplier
    if C.get('mult'):
        mx, my = ax1 - 28, ay0 + 36
        for sg in (1, -1):
            ballpoint(cv, [(mx - 22 - 5.5, my - sg * 5.5), (mx - 22 + 5.5, my + sg * 5.5)], INK, 6.0, 1.0, wob=0.2, wl=8, taper=(0, 0))
        for sg in (1, -1):
            marker(cv, [(mx - 22 - 5.2, my - sg * 5.2), (mx - 22 + 5.2, my + sg * 5.2)], PAPER, w=3.0, alpha=1.0, wob=0.2, grain=0.05, taper=(0, 0))
        letters(cv, C['mult'], (mx + 1, my + 1), 44, fill=PAPER, extrude=3, ink_w=1.8, rot=5, miss=(1.2, 1.0), ext_col=INK)
    # ---- cost
    sticker_disc(cv, (24, 30) if A else (26, 32), 13.5, CYAN, str(cost), 20)
    # ---- title
    title_c = (94, 168)
    letters(cv, C['title'], title_c, 31 if len(C['title']) < 7 else 26, fill=PINK if A else INK, extrude=3.2, ink_w=1.9, rot=-2.0 if A else 1.5, miss=(1.4, 1.1),
            fill_mode='flat', ext_col=INK if A else PINK_D)
    # ---- type tag
    type_tag(cv, C['tag'], (60, 199), None)
    # ---- rules text
    tag_text(cv, C['rules'], (94, 223), 18, fnt=HAND_F, col=(28, 40, 128), alpha=1.0, wob=0.3, rot=-1.0 if A else 0.5, bold=0.5)
    wavy(cv, (36, 235.5), (152, 234.5), 1.4, 7, BLUE, 0.9, 0.75)
    # loud tab
    if C.get('loud'):
        draw_loud(cv, (152, 30), 6, C['loud'])
    # ---- doodles
    if A:
        doodle_star(cv, (172, 154), 5.5, BLUE, 0.9)
        doodle_spark(cv, (22, 152), 7, BLUE, 0.8, n=7)
        doodle_arrow(cv, (140, 196), (166, 188), BLUE, 0.9, curve=5, head=4)
        doodle_cross(cv, (18, 196), 3, BLUE, 0.9)
        tape(cv, (94, 12), 54, 17, -3 + r.uniform(-3, 3))
        tape(cv, (176, 244), 30, 14, 42)
    else:
        staple(cv, (30, 17), 18)
        doodle_star(cv, (160, 196), 6, INK, 1.0)
        doodle_spark(cv, (168, 232), 6, INK, 0.9, n=6)
        tape(cv, (170, 14), 38, 14, 38, col=(228, 232, 238))
    return cv if ret_cv else cv.down()


if __name__ == '__main__':
    import time
    t = time.time()
    v = sys.argv[1] if len(sys.argv) > 1 else 'A'
    ims = [render_card(n, v) for n in CARDS]
    W = CW * 4
    sheet = Image.new('RGBA', (W, CH), (40, 28, 60, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (i * CW, 0))
    sheet.save('D:/rc_scratch/combat_redesign/sketchbook_graffiti/out/cards_%s.png' % v)
    print(time.time() - t)
