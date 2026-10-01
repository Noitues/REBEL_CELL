"""08 stamps: VICTORY, DEFEATED, SOLD, JACK IN, LETHAL, PHASE 2 as graphic headline stamps."""
import math
import random
from PIL import Image, ImageDraw, ImageChops
from kit import *

IMPACT = 'C:/Windows/Fonts/impact.ttf'
STENCIL = 'C:/Windows/Fonts/STENCIL.TTF'
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'
POS = [(400, 330), (960, 330), (1520, 330), (400, 760), (960, 760), (1520, 760)]


def word(s, size, path, stops, seed, depth=(5, 7), style='Bold', ink_w=None, bands=True, single=None):
    """Faceted, cel-banded, ink-outlined lettering with an extruded ink shadow. Returns an RGBA image."""
    f = ftxt(size, path, style if path == BAHN else None)
    bb = f.getbbox(s)
    pad = int(40 * SS)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    sw = int((ink_w or max(3, size * 0.07)) * SS)
    mf = Image.new('L', (w, h), 0)
    mi = Image.new('L', (w, h), 0)
    org = (pad - bb[0], pad - bb[1])
    ImageDraw.Draw(mf).text(org, s, font=f, fill=255)
    ImageDraw.Draw(mi).text(org, s, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ink = Image.new('RGBA', (w, h), INK + (255,))
    dx, dy = depth
    steps = int(max(abs(dx), abs(dy)))
    for k in range(steps, 0, -1):
        out.paste(ink, (int(dx * k / steps * SS), int(dy * k / steps * SS)), mi)
    out.paste(ink, (0, 0), mi)
    fill = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fill)
    W1, H1 = w / SS, h / SS
    top, bot = pad / SS + 4, H1 - pad / SS - 4

    def col(u, v, i, j, k, rc):
        if single is not None:
            return bcol(stops, single, rc.uniform(-0.04, 0.04))
        y = v * H1
        rel = (y - top) / max(1, bot - top)
        b = 2 if rel < 0.42 - 0.1 * (u - 0.5) else (1 if rel < 0.8 else 0)
        return bcol(stops, b, rc.uniform(-0.04, 0.04))
    facet(fd, bil([(0, 0), (W1, 0), (W1, H1), (0, H1)]), max(4, int(W1 / 34)), max(3, int(H1 / 30)), col, (seed, 'f'),
          0.3)
    out.paste(fill, (0, 0), mf)
    return out


def grunge(im, seed, n=160, size=(2, 7)):
    """Knock out small triangles (worn rubber stamp)."""
    rng = random.Random(str(seed))
    a = im.getchannel('A')
    d = ImageDraw.Draw(a)
    for _ in range(n):
        x, y = rng.uniform(0, im.width), rng.uniform(0, im.height)
        s = rng.uniform(*size) * SS
        d.polygon([(x, y), (x + s, y + s * 0.3), (x + s * 0.2, y + s)], fill=0)
    im.putalpha(a)
    return im


def place(img, im, cx, cy, ang=0):
    paste_rot(img, im, cx, cy, ang)


def victory(img, d, cx, cy):
    burst = [(cx + 200 * math.cos(a) * (1 if k % 2 == 0 else 0.62), cy + 120 * math.sin(a) * (1 if k % 2 == 0 else 0.62))
             for k, a in enumerate([math.pi * j / 9 for j in range(18)])]
    shape(d, burst, GOLD, 'v_burst', ink=3.6, nu=18, nv=2, form=0.6, bias=-0.1)
    banner = [(cx - 230, cy - 46), (cx + 230, cy - 60), (cx + 218, cy + 52), (cx - 222, cy + 62)]
    shape(d, banner, PAPER, 'v_banner', ink=3.6, nu=10, nv=2, bias=0.2)
    chips(d, banner, 'vb', n=10, col=ramp(PAPER, 0.3))
    place(img, word('VICTORY', 92, IMPACT, GOLD, 'v'), cx, cy, -2)


def defeated(img, d, cx, cy):
    scrap = [(cx - 220, cy - 80), (cx + 210, cy - 92), (cx + 226, cy + 86), (cx - 214, cy + 96)]
    shape(d, scrap, PAPER, 'd_scrap', ink=3.0, nu=8, nv=3, bias=0.15)
    st, sd = layer_img(440, 170)
    for r, w in ((0, 7), (14, 3)):
        q = [(10 + r, 10 + r), (430 - r, 10 + r), (430 - r, 160 - r), (10 + r, 160 - r)]
        for k in range(4):
            line2(sd, q[k], q[(k + 1) % 4], w, ramp(RED, 0.45) + (255,))
    tw = word('DEFEATED', 70, STENCIL, RED, 'df', depth=(0, 0), ink_w=0.01, single=1)
    st.alpha_composite(tw, (int(st.width / 2 - tw.width / 2), int(st.height / 2 - tw.height / 2)))
    st = grunge(st, 'dg', n=420, size=(2, 6))
    place(img, st, cx, cy, -8)


def sold(img, d, cx, cy):
    tape = [(cx - 230, cy - 38), (cx + 236, cy - 50), (cx + 238, cy + 30), (cx - 226, cy + 40)]
    shape(d, tape, PAPER, 's_tape', ink=2.8, nu=8, nv=1, bias=0.3)
    st, sd = layer_img(300, 170)
    q = [(12, 12), (288, 12), (288, 158), (12, 158)]
    for k in range(4):
        line2(sd, q[k], q[(k + 1) % 4], 9, ramp(RED, 0.5) + (255,))
    tw = word('SOLD', 104, IMPACT, RED, 'sd', depth=(0, 0), ink_w=0.01, single=1)
    st.alpha_composite(tw, (int(st.width / 2 - tw.width / 2), int(st.height / 2 - tw.height / 2)))
    st = grunge(st, 'sg', n=260)
    place(img, st, cx + 10, cy - 4, 12)


def jack_in(img, d, cx, cy):
    # plug + cable
    plug = [(cx - 230, cy - 30), (cx - 170, cy - 30), (cx - 170, cy + 30), (cx - 230, cy + 30)]
    extrude(d, plug, (4, 6), METAL, 'plug', ink=3.4)
    for s in (-1, 1):
        prong = [(cx - 170, cy + s * 14 - 5), (cx - 142, cy + s * 14 - 5), (cx - 142, cy + s * 14 + 5), (cx - 170, cy + s * 14 + 5)]
        shape(d, prong, GOLD, ('prong', s), ink=2.4)
    ink_line(d, (cx - 230, cy), (cx - 270, cy + 60), 9, 'cable')
    line2(d, (cx - 230, cy), (cx - 270, cy + 60), 4, bcol(DARK, 2))
    place(img, word('JACK IN', 88, BAHN, CELL, 'ji', style='Bold Condensed'), cx + 20, cy, 0)
    for k in range(2):
        x = cx + 150 + k * 30
        chev = [(x, cy - 30), (x + 16, cy - 30), (x + 36, cy), (x + 16, cy + 30), (x, cy + 30), (x + 20, cy)]
        shape(d, chev, CELL, ('jc', k), ink=2.8, bias=0.3)


def lethal(img, d, cx, cy):
    plate = [(cx - 240, cy - 70), (cx + 240, cy - 70), (cx + 240, cy + 70), (cx - 240, cy + 70)]
    # hazard stripes: red / ink diagonals
    facet(d, bil(plate), 16, 2, lambda u, v, i, j, k, rc: bcol(RED, 2 if v < 0.5 else 1, rc.uniform(-0.03, 0.03))
          if (i + (1 if v > 0.5 else 0)) % 2 == 0 else bcol(DARK, 1), 'lt_haz', 0.0)
    inner = [(cx - 220, cy - 48), (cx + 220, cy - 48), (cx + 220, cy + 48), (cx - 220, cy + 48)]
    shape(d, inner, DARK, 'lt_in', ink=2.6, flat=0)
    ink_poly(d, plate, 4.0, 'lt_ink')
    rust_streaks(d, plate, 'ltr', n=6)
    # skull glyph
    sk = [(cx - 196, cy - 26), (cx - 150, cy - 26), (cx - 142, cy + 4), (cx - 156, cy + 30), (cx - 190, cy + 30),
          (cx - 204, cy + 4)]
    shape(d, sk, PAPER, 'skull', ink=2.6, bias=0.3)
    for s in (-1, 1):
        tri(d, [(cx - 173 + s * 14 - 8, cy - 6), (cx - 173 + s * 14 + 8, cy - 6), (cx - 173 + s * 14, cy + 6)], INK)
    for k in range(3):
        line2(d, (cx - 184 + k * 11, cy + 20), (cx - 184 + k * 11, cy + 30), 2, INK)
    place(img, word('LETHAL', 84, IMPACT, PAPER, 'lt'), cx + 40, cy, 0)


def phase2(img, d, cx, cy):
    hexo = circle_pts(cx + 130, cy, 96, n=6, a0=math.pi / 6)
    extrude(d, hexo, (6, 8), MER, 'p_hex', ink=4.0, front_kw=dict(nu=12, nv=2, form=1.0))
    place(img, word('PHASE', 70, IMPACT, PAPER, 'ph'), cx - 90, cy, 0)
    place(img, word('2', 150, IMPACT, RED, 'p2'), cx + 130, cy, 0)
    # crack through the hex
    pts = [(cx + 60, cy - 90), (cx + 96, cy - 40), (cx + 80, cy - 6), (cx + 120, cy + 40), (cx + 104, cy + 92)]
    for a, b in zip(pts, pts[1:]):
        line2(d, a, b, 6, INK)
        line2(d, (a[0] + 3, a[1]), (b[0] + 3, b[1]), 1.6, bcol(MER, 2))


def render():
    img = sheet()
    d = ImageDraw.Draw(img)
    fns = [victory, defeated, sold, jack_in, lethal, phase2]
    names = ['VICTORY', 'DEFEATED', 'SOLD', 'JACK IN', 'LETHAL', 'PHASE 2']
    labels = []
    for (x, y), fn, nm in zip(POS, fns, names):
        fn(img, d, x, y)
        d = ImageDraw.Draw(img)
        labels.append((x, y + 150, nm))
    return finish(img, '08_stamps.png', labels, '08', 'STAMPS  //  HEADLINE WORDS')


if __name__ == '__main__':
    render()
