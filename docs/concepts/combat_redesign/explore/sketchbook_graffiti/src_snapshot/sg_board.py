"""style board 1920x1280: manifesto, swatches, line/brush samples, type, one card + one slice large."""
import sys, os, json, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from sg_lib import *
from sg_icons import *
import sg_tower as ST
import sg_hand as SH

OUT = 'D:/rc_scratch/combat_redesign/sketchbook_graffiti/out/'
W, H, S = 1920, 1280, 2
cv = Canvas(W, H, S, seed=404)
r = cv.r
# ground: black book cover (dark, faint paper tooth)
g = np.empty((cv.H, cv.W, 3), np.float32)
g[:] = (22, 18, 30)
g += smooth(cv.H, cv.W, 30, r)[..., None] * 2.2 + smooth(cv.H, cv.W, 2, r)[..., None] * 1.6
cv.over_rgb(np.ones((cv.H, cv.W), np.float32), np.clip(g, 0, 255))


def sheet(x0, y0, x1, y1, kind='dot', rot=0.0, tint=PAPER, rough=1.6):
    pts = [(x0 + r.uniform(-2, 2), y0 + r.uniform(-2, 2)), (x1 + r.uniform(-2, 2), y0 + r.uniform(-2, 2)), (x1 + r.uniform(-2, 2), y1 + r.uniform(-2, 2)), (x0 + r.uniform(-2, 2), y1 + r.uniform(-2, 2))]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a = math.radians(rot)
    pts = [(cx + (px - cx) * math.cos(a) - (py - cy) * math.sin(a), cy + (px - cx) * math.sin(a) + (py - cy) * math.cos(a)) for px, py in pts]
    m = cv.poly_mask(pts)
    t, rim = torn_mask(cv, m, rough=rough, fringe=1.0)
    cv.over(ndi.gaussian_filter(np.roll(np.roll(t, int(5 * S), 0), int(6 * S), 1), 5 * S), (0, 0, 0), 0.6)
    cv.over_rgb(t, paper_rgb(cv, kind, tint, pitch=12.0))
    cv.over(np.clip(rim, 0, 1) * 0.5, (252, 250, 244), 1.0)
    return t


def left_text(text, x, y, px, col=INK, fnt=HAND_F, bold=0.0, alpha=0.95, rot=0.0):
    L = font(fnt, px * S).getlength(text) / S
    tag_text(cv, text, (x + L / 2, y), px, fnt=fnt, col=col, alpha=alpha, bold=bold, rot=rot, wob=0.25)


def mono_label(text, x, y, px=13, col=(70, 70, 86)):
    L = font(MONO_F, px * S).getlength(text) / S
    tag_text(cv, text, (x + L / 2, y), px, fnt=MONO_F, col=col, alpha=0.95, wob=0.0)


# ------------------------------------------------------------------ title
letters(cv, 'SKETCHBOOK GRAFFITI', (470, 62), 54, fill=PINK, extrude=5, ink_w=2.6, ink=INK, ext_col=(8, 6, 14), rot=-1.2, miss=(2, 1.6), spacing=2, hatch_ext=True)
# keep the dark ground readable: add a paper outline under the title so ink shows
tag_text(cv, 'PLAYER FAMILY  //  wheel + hand  //  the Cell draws its own board', (452, 118), 21, fnt=HAND_F, col=(235, 230, 245), alpha=0.95)
doodle_star(cv, (860, 52), 14, (235, 230, 245), 1.4)
doodle_spark(cv, (60, 118), 14, PINK, 1.4, n=9)

# ------------------------------------------------------------------ sheet 1: manifesto
sheet(36, 150, 690, 610, 'dot', -0.8)
tape(cv, (120, 158), 90, 26, -6)
tape(cv, (610, 604), 80, 24, -5)
left_text('WHAT MAKES IT OURS', 66, 196, 30, INK, MARKER_F)
ink_line_y = 214
wavy = lambda p0, p1: None
ballpoint(cv, [(66, 214), (360, 211)], PINK, 2.6, 0.9, wob=0.6, wl=30)
lines = [
    ('1.  Paper, not glass.', 'Everything drawn on paper is the Cell\'s.', 'Everything on glass belongs to the corp.'),
    ('2.  One ink, one hand.', 'Pink marker (#FF3DA8) says "ours". The tower', 'and the cards are drawn by the same pen.'),
    ('3.  Drawn twice.', 'Ballpoint construction first, chisel marker after;', 'the fill misses the line by a hair, on purpose.'),
    ('4.  Hatching means "going".', 'Red hatch = the enemy takes it. Blue = your soak.', 'Pink = we take it. Hand-hatched, never dashed.'),
    ('5.  Never glows, never perfect.', 'Tape, staples and doodles stay on the tower and', 'the cards, never on an enemy cell.'),
]
y = 248
for h1, a, b in lines:
    left_text(h1, 66, y, 22, (28, 40, 128), MARKER_F, alpha=0.98)
    left_text(a, 78, y + 26, 19, INK)
    left_text(b, 78, y + 48, 19, INK)
    y += 76
doodle_arrow(cv, (630, 300), (655, 262), BLUE, 1.2, curve=8, head=7)

# ------------------------------------------------------------------ sheet 2: swatches + line grammar
sheet(722, 140, 1288, 612, 'graph', 0.7)
tape(cv, (800, 146), 80, 24, 7)
tape(cv, (1220, 608), 80, 24, 5)
left_text('INKS', 752, 186, 28, INK, MARKER_F)
sw = [('PAPER #F2EEE4', PAPER), ('PINK #FF3DA8', PINK), ('INK #111111', INK), ('BALLPOINT #2C3E9E', BLUE)]
x = 756
for i, (nm, col) in enumerate(sw):
    c = (x + 34, 252)
    m = cv.circle_mask(c, 30)
    m = warp(m, 1.2 * S, 14 * S, r)
    solid = np.clip((ndi.gaussian_filter(m, 0.5) - 0.5) * 6, 0, 1)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(solid, S, 1.8), 0.4) * 1.5, 0, 1), INK, 0.97)
    if col == PAPER:
        cv.over(solid, PAPER, 1.0)
    else:
        fill_region(cv, solid, 0, 0, col, ang=30 + i * 12, nib=7, over=1.5, miss=(1.4, 1.0), clip=1.0)
    mono_label(nm, x - 4, 304, 11)
    x += 134
left_text('information inks (one meaning each)', 752, 336, 19, (60, 60, 80))
for i, (nm, col, lab) in enumerate((('HARM', HARM, 'the enemy takes it'), ('SOAK', SOAK, 'your soak'), ('GAIN', GAIN, 'your life'), ('PINK', PINK, 'we take it'))):
    x0 = 756 + i * 134
    reg = cv.poly_mask([(x0, 352), (x0 + 112, 350), (x0 + 112, 392), (x0, 394)])
    sol = np.clip((ndi.gaussian_filter(reg, 0.5) - 0.5) * 6, 0, 1)
    cv.over(sol, (16, 16, 24), 0.96)
    if nm == 'GAIN':
        fill_region(cv, sol, 0, 0, GAIN, ang=20, nib=6, over=1, clip=0.5)
    else:
        hatch_region(cv, sol, 0, 0, col, ang=45, pitch=4.2, w=1.5, alpha=0.95, over=0.0, jit=0.2, cross=True)
        cv.over(np.clip(ndi.gaussian_filter(edge_ring(sol, S, 2.0), 0.4) * 1.4, 0, 1), col, 0.97)
    cv.over(np.clip(ndi.gaussian_filter(outline_mask(sol, S, 1.4), 0.4) * 1.5, 0, 1), INK, 0.95)
    mono_label(nm, x0 - 2, 408, 10.5)
    mono_label(lab, x0 - 2, 422, 10)

left_text('LINES', 752, 452, 28, INK, MARKER_F)
# L2 painted stroke (chisel, taper)
marker(cv, [(760, 490), (900, 484), (1010, 492)], PINK, w=9, nib='chisel', ang=38, wob=1.2, wl=60, taper=(0.1, 0.35))
mono_label('L2 painted stroke: ours', 1030, 492, 10.5)
ballpoint(cv, [(760, 520), (840, 514), (930, 522), (1010, 516)], BLUE, 1.0, 0.9, wob=1.0, wl=40)
mono_label('construction: ballpoint', 1030, 520, 10.5)
marker(cv, [(760, 546), (1010, 544)], PINK_L, w=15, nib='round', alpha=0.8, mode='mult', wob=0.6, taper=(0.02, 0.02))
mono_label('highlighter: bands under HP', 1030, 546, 10.5)
# L10 double line
marker(cv, [(760, 572), (900, 570), (1010, 573)], PINK, w=3.4, wob=0.8, wl=50, taper=(0.05, 0.05))
marker(cv, [(760, 580), (900, 578), (1010, 581)], PINK, w=3.4, wob=0.8, wl=50, taper=(0.05, 0.05))
mono_label('L10 double line: protects', 1030, 576, 10.5)
# hatch edges + dotted
for i in range(1):
    pass
for k in range(30):
    cv.over(cv.circle_mask((760 + k * 9, 600), 1.8), (110, 110, 130), 0.85)
mono_label('L8 dots: two+ turns away', 1030, 600, 10.5)

# ------------------------------------------------------------------ sheet 3: type
sheet(1320, 150, 1884, 612, 'ruled', -0.6)
tape(cv, (1400, 156), 80, 24, -4)
tape(cv, (1810, 606), 80, 24, -6)
left_text('TYPE', 1350, 196, 28, INK, MARKER_F)
letters(cv, 'BRACE  SPIN 3', (1604, 262), 46, fill=PINK, extrude=3.5, ink_w=2.0, rot=-2, miss=(1.6, 1.2))
mono_label('Permanent Marker: titles, hub, SEND IT  (flat fill, ink outline, block drop)', 1346, 312, 10.5)
left_text('Turn the tower 3   Block a slice', 1350, 350, 24, (28, 40, 128), HAND_F, bold=0.5)
mono_label('Ink Free: rules text, ballpoint blue, always underlined by hand', 1346, 380, 10.5)
sticker = (1380, 438)
for i, (n, col) in enumerate((('1', CYAN), ('0', CYAN))):
    cx = 1380 + i * 56
    cv.over(cv.circle_mask((cx, 440), 24), (250, 250, 246), 1.0)
    cv.over(cv.circle_mask((cx, 440), 21), INK, 1.0)
    cv.over(cv.circle_mask((cx, 440), 19.4), CYAN, 1.0)
    tag_text(cv, n, (cx, 441), 30, fnt=ANTON_F, col=INK, alpha=1.0, wob=0.0)
mono_label('Anton: RAM coin (the system keeps its own)', 1500, 440, 10.5)
doodle_star(cv, (1370, 520), 12, INK, 1.2)
doodle_spark(cv, (1420, 520), 12, INK, 1.1, n=8)
doodle_arrow(cv, (1460, 530), (1530, 508), BLUE, 1.2, curve=7, head=6)
doodle_cross(cv, (1566, 520), 7, INK, 1.2)
doodle_zig(cv, (1600, 520), (1660, 520), BLUE, 1.1, n=5, amp=6)
mono_label('doodle kit: star, spark, arrow, X, zig. Tower + cards only', 1346, 566, 10.5)

# ------------------------------------------------------------------ bottom row: card A, slice, card B, squint
big = cv.down()
base = big.convert('RGBA')

# ------------------------------------------------------------------ large card + slice (hi-res crops)
ca = SH.render_card('Spin3', 'A', 1, S=4, ret_cv=True).rgba()
cb = SH.render_card('Trigger', 'B', 1, S=4, ret_cv=True).rgba()
J = json.load(open('D:/rc_scratch/combat_redesign/sketchbook_graffiti/state_e10.json'))
tw, tcv = ST.render_tower(J['f1'], 'A')
trgb = tcv.rgba()
# slice crop: sector 3 (SHIELD, one pip lost) + sector 2 (TURRET breaking) region around the lower right of the wheel
ox, oy = int(ST.CT[0] * 4), int(ST.CT[1] * 4)
crop = trgb.crop((ox + int(34 * 4), oy + int(-4 * 4), ox + int(170 * 4), oy + int(150 * 4)))
res = Image.new('RGBA', (1920, 1280), (0, 0, 0, 0))


def put(im, x, y, w=None, shadow=True):
    if w:
        im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    if shadow:
        pad = 24
        bigim = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        bigim.paste(im, (pad, pad))
        sh = drop_shadow(bigim, (5, 7), 9, 0.7)
        base.alpha_composite(sh, (x - pad, y - pad))
    base.alpha_composite(im, (x, y))


put(ca, 36, 640, 420)
put(crop, 520, 650, 460)
put(cb, 1030, 640, 420)
# squint thumbnails of the plate
try:
    pa = Image.open(OUT + 'plate_A_p1.png').convert('RGB')
    grey = pa.convert('L').convert('RGB')
    th = grey.resize((380, 214), Image.LANCZOS)
    th2 = pa.resize((380, 214), Image.LANCZOS)
    base.alpha_composite(th2.convert('RGBA'), (1490, 650))
    base.alpha_composite(th.convert('RGBA'), (1490, 880))
except Exception as e:
    print('no plate yet', e)

final = base.convert('RGB')
# captions on the dark ground (hand voice)
cv2 = Canvas(W, H, 2, seed=5)
tag_text(cv2, 'CARD A: torn black-book page', (246, 1236), 21, fnt=HAND_F, col=(235, 230, 245), alpha=0.95)
tag_text(cv2, 'SLICE: fill misses the line, hatch = going', (740, 1236), 21, fnt=HAND_F, col=(235, 230, 245), alpha=0.95)
tag_text(cv2, 'CARD B: index card, chisel border', (1240, 1236), 21, fnt=HAND_F, col=(235, 230, 245), alpha=0.95)
tag_text(cv2, 'squint test: colour / greyscale, 380 px', (1680, 1120), 20, fnt=HAND_F, col=(235, 230, 245), alpha=0.95)
cap = cv2.down()
fr = final.convert('RGBA')
fr.alpha_composite(cap)
fr.convert('RGB').save(OUT + 'style_board.jpg', quality=93)
print('board ok')
