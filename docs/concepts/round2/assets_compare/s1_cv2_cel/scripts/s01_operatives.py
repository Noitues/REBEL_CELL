"""01 operatives: Polaroid busts, 2 columns (Breaker, Ghost) x 4 rows (neutral, hurt, triumphant, flatlined)."""
import math
import random
from PIL import Image, ImageDraw, ImageOps
from kit import *

PW, PH = 214, 236          # polaroid
PHOTO = 188                # photo square
COLS = {'breaker': 860, 'ghost': 1260}
ROWS = ['neutral', 'hurt', 'triumphant', 'flatlined']
ROW_Y = [212, 452, 692, 932]   # polaroid centres
STATE_BG = {'neutral': STEEL, 'hurt': RED, 'triumphant': GOLD, 'flatlined': DARK}
JACKET = R('#100806', '#26120a', '#422014', '#5e3020', '#7a4430', '#965e44', '#b8826a')
HOODC = R('#06060c', '#10101c', '#1c1c30', '#2a2a44', '#3c3c5c', '#545478', '#74749a')
HAIR = R('#050304', '#0e0806', '#1a100a', '#2a1a10', '#3c2618', '#523624', '#6a4a34')


def rot(pts, c, ang):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]


def photo_bg(d, state, seed):
    st = STATE_BG[state]
    facet(d, bil([(0, 0), (PHOTO, 0), (PHOTO, PHOTO), (0, PHOTO)]), 4, 4,
          lambda u, v, i, j, k, rc: bcol(st, 1 if u + v < 1.0 else 0, rc.uniform(-0.04, 0.04)), ('pbg', seed), 0.3)
    # a wall seam and a hanging cable for place
    line2(d, (0, PHOTO * 0.62), (PHOTO, PHOTO * 0.58), 2, mix(ramp(st, 0.2), BG, 0.2))


def eyes(d, c, state, glow=None, w=10):
    for s in (-1, 1):
        x, y = c[0] + s * w, c[1]
        if state == 'flatlined':
            line2(d, (x - 4, y - 4), (x + 4, y + 4), 2.2, INK)
            line2(d, (x - 4, y + 4), (x + 4, y - 4), 2.2, INK)
        elif glow:
            tri(d, [(x - 5, y), (x + 5, y - 2), (x + 3, y + 3)], glow)
        else:
            h = 1.5 if state == 'hurt' and s > 0 else 3.2
            tri(d, [(x - 5, y), (x + 5, y - 1), (x + 1, y + h)], INK)
        # brow
        if not glow:
            by = y - 7 - (2 if state == 'triumphant' else 0)
            tilt = 2.5 if state == 'hurt' else (-1.5 if state == 'neutral' else -3)
            line2(d, (x - 6 * s, by + tilt * s * 0), (x + 6 * s, by - tilt), 2.6, INK)


def breaker(d, state):
    hurt, tri_up = state == 'hurt', state == 'triumphant'
    cx = PHOTO / 2
    # crowbar behind the shoulder (raised overhead when triumphant)
    if tri_up:
        a, b = (150, 186), (128, 8)
    else:
        a, b = (166, 186), (52, 14)
    bar = [(a[0] - 7, a[1]), (a[0] + 7, a[1]), (b[0] + 5, b[1]), (b[0] - 5, b[1])]
    shape(d, bar, METAL, 'bar', nu=2, nv=6, form=0.8, ink=3.2)
    # antenna tip: hooked claw + whip antenna with a red tip
    hx, hy = b
    hook = [(hx - 6, hy + 4), (hx + 14, hy - 8), (hx + 18, hy + 4), (hx + 6, hy + 10)]
    shape(d, hook, METAL, 'hook', ink=2.6)
    line2(d, (hx, hy), (hx - 18, hy - 22), 2, INK)
    tri(d, [(hx - 22, hy - 24), (hx - 14, hy - 26), (hx - 18, hy - 18)], ramp(NEON['red'], 0.8))
    # grip tape
    for k in range(4):
        t = 0.62 + k * 0.06
        px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        line2(d, (px - 8, py + 2), (px + 8, py - 2), 3.4, ramp(RED, 0.5))
    # heavy jacket
    tilt = 7 if hurt else 0
    jacket = [(4, 188), (14, 142), (46, 118), (cx, 130), (PHOTO - 46, 118), (PHOTO - 14, 142), (PHOTO - 4, 188)]
    shape(d, jacket, JACKET, 'jacket', nu=14, nv=3, ink=3.6)
    rust_streaks(d, jacket, 'jk', n=3, length=(8, 18))
    chips(d, jacket, 'jk', n=6)
    # padded collar
    for s in (-1, 1):
        col = [(cx + s * 10, 132), (cx + s * 46, 116), (cx + s * 58, 138), (cx + s * 24, 150)]
        shape(d, col, R('#3a2c20', '#5e4a36', '#82684c', '#a68a66', '#c8ae88', '#e2ceac'), ('col', s), ink=2.6)
    # neck + head
    c = (cx, 84)
    neck = [(cx - 14, 100), (cx + 14, 100), (cx + 16, 134), (cx - 16, 134)]
    shape(d, neck, SKIN, 'neck', ink=2.4, bias=-0.15)
    head = [(cx - 24, 62), (cx, 46), (cx + 24, 60), (cx + 30, 86), (cx + 18, 112), (cx, 118), (cx - 18, 112),
            (cx - 28, 86)]
    head = rot(head, c, tilt)
    shape(d, head, SKIN, 'head', nu=16, nv=3, ink=3.4)
    # buzz cut / beanie
    cap = rot([(cx - 27, 70), (cx - 22, 52), (cx, 40), (cx + 24, 50), (cx + 29, 70), (cx, 62)], c, tilt)
    shape(d, cap, HAIR, 'cap', ink=3.0)
    ec = rot([(cx, 82)], c, tilt)[0]
    eyes(d, ec, state)
    # mouth
    m = rot([(cx - 9, 103), (cx + 9, 102)], c, tilt)
    if tri_up:
        tri(d, [(cx - 11, 100), (cx + 11, 99), (cx, 110)], INK)
        tri(d, [(cx - 8, 100), (cx + 8, 99.5), (cx, 103)], hexc('#f4ece0'))
    elif state == 'flatlined':
        line2(d, m[0], m[1], 2.4, INK)
    else:
        line2(d, m[0], (m[1][0], m[1][1] + (3 if hurt else 0)), 2.6, INK)
    # scar
    line2(d, rot([(cx + 14, 70)], c, tilt)[0], rot([(cx + 20, 92)], c, tilt)[0], 1.6, ramp(RED, 0.35))
    if hurt:
        band = rot([(cx - 28, 66), (cx + 28, 62), (cx + 28, 72), (cx - 28, 76)], c, tilt)
        shape(d, band, PAPER, 'bandage', ink=2.2, bias=0.2)
        tri(d, rot([(cx + 8, 66), (cx + 16, 65), (cx + 12, 74)], c, tilt), ramp(RED, 0.45))
        line2(d, rot([(cx - 20, 92)], c, tilt)[0], rot([(cx - 14, 108)], c, tilt)[0], 2.6, ramp(RED, 0.4))
    if tri_up:
        # raised fist
        fist = [(30, 60), (58, 54), (64, 78), (36, 86)]
        line2(d, (40, 150), (46, 84), 18, INK)
        line2(d, (40, 150), (46, 84), 13, bcol(JACKET, 1))
        shape(d, fist, SKIN, 'fist', ink=3.0)


def ghost(d, state):
    hurt, tri_up = state == 'hurt', state == 'triumphant'
    cx = PHOTO / 2
    tilt = -6 if hurt else 0
    c = (cx, 84)
    # slim body, high collar
    body = [(18, 188), (30, 146), (62, 126), (cx, 134), (PHOTO - 62, 126), (PHOTO - 30, 146), (PHOTO - 18, 188)]
    shape(d, body, HOODC, 'body', nu=14, nv=3, ink=3.6)
    # cyan seam on the coat
    glow_lines(d, (cx, 136), (cx - 4, 188), ramp(NEON['cyan'], 0.75), 2)
    # holo key shard (prop)
    if tri_up:
        sh = [(150, 30), (166, 54), (154, 92), (138, 58)]
        line2(d, (150, 160), (152, 92), 16, INK)
        line2(d, (150, 160), (152, 92), 11, bcol(HOODC, 1))
    else:
        sh = [(150, 130), (162, 146), (154, 172), (142, 150)]
    shape(d, sh, CELL, 'shard', ink=2.6, bias=0.35)
    glow_lines(d, (sh[0][0], sh[0][1] + 4), (sh[2][0], sh[2][1] - 4), ramp(NEON['cyan'], 0.95), 1.5)
    # hood
    hood = rot([(cx - 44, 132), (cx - 40, 74), (cx - 20, 38), (cx + 8, 30), (cx + 34, 44), (cx + 46, 80), (cx + 44, 132),
                (cx, 124)], c, tilt)
    shape(d, hood, HOODC, 'hood', nu=16, nv=3, ink=3.8, form=1.2)
    # face in the opening
    face = rot([(cx - 22, 66), (cx, 56), (cx + 22, 66), (cx + 24, 92), (cx + 12, 112), (cx - 12, 112), (cx - 24, 92)],
               c, tilt)
    shape(d, face, SKIN, 'face', ink=2.8, bias=-0.2)
    # face mesh over the lower face
    mesh = rot([(cx - 24, 88), (cx + 24, 88), (cx + 13, 113), (cx - 13, 113)], c, tilt)
    cel_fill(d, mesh, DARK, 'mesh', nu=6, nv=2, bias=0.1)
    q = bil(mesh)
    mc = ramp(NEON['cyan'], 0.7) if state != 'flatlined' else ramp(METAL, 0.5)
    for k in range(1, 5):
        line2(d, q(k / 5, 0), q(k / 5, 1), 1.2, mc)
    for k in range(1, 3):
        line2(d, q(0, k / 3), q(1, k / 3), 1.2, mc)
    for u in (0.2, 0.5, 0.8):
        for v in (0.33, 0.66):
            x, y = q(u, v)
            tri(d, [(x - 2, y), (x + 2, y), (x, y - 3)], ramp(NEON['cyan'], 0.95) if state != 'flatlined' else INK)
    ink_poly(d, mesh, 2.0, 'meshink')
    if hurt:
        # torn mesh: a red glitch slice
        line2(d, q(0.55, 0.1), q(0.85, 0.9), 2.4, ramp(NEON['red'], 0.75))
        tri(d, rot([(cx + 6, 70), (cx + 22, 74), (cx + 10, 80)], c, tilt), ramp(RED, 0.45))
    ec = rot([(cx, 77)], c, tilt)[0]
    glow = None if state == 'flatlined' else ramp(NEON['cyan'], 0.9 if not hurt else 0.6)
    eyes(d, ec, state, glow=glow, w=9)


def polaroid(cls, state, seed):
    im, d = layer_img(PW, PH)
    facet(d, bil([(0, 0), (PW, 0), (PW, PH), (0, PH)]), 4, 5,
          lambda u, v, i, j, k, rc: bcol(PAPER, 2 if v < 0.85 else 1, rc.uniform(-0.03, 0.03)), ('pol', seed), 0.3)
    ph, pd = layer_img(PHOTO, PHOTO)
    photo_bg(pd, state, seed)
    (breaker if cls == 'breaker' else ghost)(pd, state)
    if state == 'flatlined':
        g = ImageOps.grayscale(ph.convert('RGB')).convert('RGB')
        g = Image.blend(g, Image.new('RGB', g.size, hexc('#1a1a1e')), 0.35)
        g.putalpha(ph.getchannel('A'))
        ph = g
        pd = ImageDraw.Draw(ph)
    im.alpha_composite(ph, (int(13 * SS), int(12 * SS)))
    d = ImageDraw.Draw(im)
    ink_poly(d, [(13, 12), (13 + PHOTO, 12), (13 + PHOTO, 12 + PHOTO), (13, 12 + PHOTO)], 1.8, ('phink', seed))
    ink_poly(d, [(0, 0), (PW, 0), (PW, PH), (0, PH)], 3.0, ('polink', seed))
    chips(d, [(0, 0), (PW, 0), (PW, PH), (0, PH)], ('pc', seed), n=5, col=ramp(PAPER, 0.35))
    # marker caption on the strip
    text(d, PW / 2, 12 + PHOTO + 18, f'{cls.upper()} - {state}', 19, hexc('#2a2420'), anchor='mm', style=None,
         path=HAND)
    if state == 'flatlined':
        tq = [(-6, 120), (PW + 6, 70), (PW + 6, 100), (-6, 150)]
        cel_fill(d, tq, RED, ('tape', seed), nu=6, nv=1, flat=2)
        ink_poly(d, tq, 2.4, ('tapeink', seed))
        f = ftxt(26)
        tim = Image.new('RGBA', (int(260 * SS), int(40 * SS)), (0, 0, 0, 0))
        ImageDraw.Draw(tim).text((130 * SS, 20 * SS), 'FLATLINED', font=f, fill=hexc('#fff0e6'), anchor='mm')
        tim = tim.rotate(13.5, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(tim, (int(PW / 2 * SS - tim.width / 2), int(110 * SS - tim.height / 2)))
    return im


def render():
    img = sheet()
    labels = []
    for cls, x in COLS.items():
        text(ImageDraw.Draw(img), x, 84, cls.upper(), 24, LABEL, anchor='mm')
    for r, (state, y) in enumerate(zip(ROWS, ROW_Y)):
        text(ImageDraw.Draw(img), 690, y, state.upper(), 22, LABEL, anchor='rm')
        for c, (cls, x) in enumerate(COLS.items()):
            pol = polaroid(cls, state, (cls, state))
            pol = pol.resize((int(pol.width * 0.92), int(pol.height * 0.92)), Image.LANCZOS)
            paste_rot(img, pol, x, y, (-2.5, 1.8, -1.2, 2.4)[r] * (1 if c == 0 else -1))
    return finish(img, '01_operatives.png', labels, '01', 'OPERATIVES  //  POLAROID BUSTS')


if __name__ == '__main__':
    render()
