"""04 threats: raid threat tokens, each at map size (56 px) and 3x (168 px). Bailiff (Solace, armoured,
slow, heavy), Courier (Meridian, fast, fragile), Customs Agent (Meridian, seals the link behind it)."""
import math
from kit import *

XS = [400, 960, 1520]
BIG, SMALL = 168, 56


def base(d, cx, cy, s, st, seed):
    """Hex map token: corp-coloured rim, dark face, raised edge."""
    w = max(1.6, s * 0.028)
    hexo = circle_pts(cx, cy, s * 0.5, s * 0.5, n=6, a0=math.pi / 6)
    extrude(d, hexo, (0, s * 0.07), st, (seed, 'rim'), ink=w * 1.2, front_kw=dict(nu=12, nv=1, form=0.8))
    hexi = circle_pts(cx, cy, s * 0.4, s * 0.4, n=6, a0=math.pi / 6)
    shape(d, hexi, [mix(c, hexc('#e8dcc4'), 0.75) for c in st], (seed, 'face'), ink=w * 0.8, form=-0.5, nu=12, nv=2, bias=0.25)


def P(cx, cy, s):
    return lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]


def bailiff(d, cx, cy, s, seed='b'):
    w = max(1.4, s * 0.026)
    base(d, cx, cy, s, SOL, seed)
    p = P(cx, cy, s)
    # treads
    for sx in (-1, 1):
        tr = p([(sx * 0.32 - 0.08, 0.14), (sx * 0.32 + 0.08, 0.14), (sx * 0.32 + 0.09, 0.3), (sx * 0.32 - 0.09, 0.3)])
        shape(d, tr, DARK, (seed, 'tr', sx), ink=w, flat=1)
    # wide armoured body
    body = p([(-0.3, -0.12), (0.3, -0.12), (0.36, 0.2), (-0.36, 0.2)])
    extrude(d, body, (0, s * 0.04), STEEL, (seed, 'body'), ink=w * 1.2, front_kw=dict(nu=6, nv=2))
    # head / visor slit
    head = p([(-0.14, -0.3), (0.14, -0.3), (0.18, -0.12), (-0.18, -0.12)])
    shape(d, head, SOL, (seed, 'head'), ink=w)
    line2(d, p([(-0.1, -0.22)])[0], p([(0.1, -0.22)])[0], max(1.2, s * 0.03), ramp(NEON['red'], 0.85))
    # riot shield front plate with stencil bar
    sh = p([(-0.22, -0.04), (0.22, -0.04), (0.2, 0.26), (0, 0.32), (-0.2, 0.26)])
    shape(d, sh, SOL, (seed, 'sh'), ink=w)
    line2(d, p([(-0.14, 0.08)])[0], p([(0.14, 0.08)])[0], max(1.4, s * 0.04), INK)
    if s > 80:
        rust_streaks(d, sh, (seed, 'r'), n=3, length=(s * 0.05, s * 0.12))
    # weight chevrons (heavy / slow)
    for k in range(2):
        y = 0.36 + k * 0.06
        a, b, c = p([(-0.08, y)])[0], p([(0, y + 0.04)])[0], p([(0.08, y)])[0]
        line2(d, a, b, max(1.2, s * 0.022), INK)
        line2(d, b, c, max(1.2, s * 0.022), INK)


def courier(d, cx, cy, s, seed='c'):
    w = max(1.4, s * 0.026)
    base(d, cx, cy, s, MER, seed)
    p = P(cx, cy, s)
    # speed streaks
    for k in range(3):
        y = -0.1 + k * 0.12
        line2(d, p([(-0.38, y)])[0], p([(-0.18 - k * 0.03, y)])[0], max(1.2, s * 0.025), bcol(MER, 2))
    # sleek forward-leaning hover bike: an arrow
    bike = p([(-0.3, 0.04), (0.4, -0.1), (0.24, 0.12), (-0.26, 0.2)])
    extrude(d, bike, (0, s * 0.03), MER, (seed, 'bike'), ink=w * 1.1, front_kw=dict(nu=6, nv=1))
    # rider: a small lean figure
    torso = p([(-0.02, -0.22), (0.16, -0.16), (0.12, 0.04), (-0.08, 0.06)])
    shape(d, torso, DARK, (seed, 'torso'), ink=w)
    shape(d, circle_pts(*p([(0.14, -0.27)])[0], s * 0.08, n=6), METAL, (seed, 'helm'), ink=w)
    # parcel strapped behind
    box = p([(-0.24, -0.1), (-0.06, -0.1), (-0.06, 0.06), (-0.24, 0.06)])
    shape(d, box, PAPER, (seed, 'box'), ink=w, bias=0.2)
    line2(d, p([(-0.15, -0.1)])[0], p([(-0.15, 0.06)])[0], max(1, s * 0.014), bcol(MER, 1))
    # fragile crack mark
    a, b, c = p([(0.18, -0.36)])[0], p([(0.24, -0.28)])[0], p([(0.2, -0.22)])[0]
    line2(d, a, b, max(1.2, s * 0.02), bcol(PAPER, 2))
    line2(d, b, c, max(1.2, s * 0.02), bcol(PAPER, 2))


def customs(d, cx, cy, s, seed='u'):
    w = max(1.4, s * 0.026)
    base(d, cx, cy, s, MER, seed)
    p = P(cx, cy, s)
    # the link behind it, sealed with a lock
    line2(d, p([(-0.38, 0.12)])[0], p([(0.38, 0.12)])[0], max(2, s * 0.05), bcol(MER, 1))
    lock = p([(0.14, 0.04), (0.32, 0.04), (0.32, 0.22), (0.14, 0.22)])
    shape(d, lock, GOLD, (seed, 'lock'), ink=w, bias=0.2)
    arc = [p([(0.23 + 0.06 * math.cos(a), 0.04 + 0.08 * math.sin(a))])[0] for a in
           [math.pi + math.pi * k / 6 for k in range(7)]]
    for k in range(6):
        line2(d, arc[k], arc[k + 1], max(1.6, s * 0.03), INK)
    # agent: long coat, peaked cap
    coat = p([(-0.2, -0.12), (0.04, -0.12), (0.08, 0.3), (-0.24, 0.3)])
    shape(d, coat, DARK, (seed, 'coat'), ink=w)
    line2(d, p([(-0.08, -0.1)])[0], p([(-0.08, 0.28)])[0], max(1, s * 0.016), bcol(MER, 1))
    shape(d, circle_pts(*p([(-0.08, -0.22)])[0], s * 0.08, n=6), SKIN, (seed, 'head'), ink=w)
    cap = p([(-0.2, -0.28), (0.04, -0.28), (0.08, -0.24), (-0.22, -0.24)])
    shape(d, cap, MER, (seed, 'cap'), ink=w)
    # seal stamp held up
    st = p([(-0.42, -0.36), (-0.24, -0.36), (-0.24, -0.24), (-0.42, -0.24)])
    shape(d, st, RED, (seed, 'stamp'), ink=w)
    line2(d, p([(-0.33, -0.24)])[0], p([(-0.2, -0.1)])[0], max(1.6, s * 0.03), INK)


def render():
    img = sheet()
    d = ImageDraw.Draw(img)
    labels = []
    info = [('BAILIFF  -  Solace', 'armoured, slow, heavy', bailiff),
            ('COURIER  -  Meridian', 'fast, fragile', courier),
            ('CUSTOMS AGENT  -  Meridian', 'seals the link behind it', customs)]
    for x, (name, desc, fn) in zip(XS, info):
        fn(d, x, 400, BIG, (name, 'big'))
        # map-size token on a strip of map link
        mx, my = x, 720
        line2(d, (mx - 140, my + 30), (mx + 140, my - 30), 6, bcol(CELL, 1))
        for dx in (-140, 140):
            shape(d, circle_pts(mx + dx, my + (30 if dx < 0 else -30), 10, n=6), CELL, ('node', x, dx), ink=2.2)
        fn(d, mx, my, SMALL, (name, 'small'))
        labels += [(x, 560, '3x'), (x, 790, 'map size 56 px'), (x, 880, name), (x, 912, desc)]
    return finish(img, '04_threats.png', labels, '04', 'RAID THREAT TOKENS')


if __name__ == '__main__':
    render()
