"""02 enemies: The Manifest (Meridian boss), Claims Adjuster (Solace elite), collections drone (Meridian
regular). Each with its corporation's wheel-bezel ring segment underneath."""
import math
import random
from kit import *

XS = [400, 960, 1520]
BUST_Y = 400
SUIT = R('#04060a', '#0a0e16', '#141a24', '#1e2632', '#2a3442', '#3a4656', '#4e5c6c')
COAT = R('#1a2420', '#3a4a44', '#5e726a', '#8aa098', '#b4c8c0', '#d8e8e2', '#f2faf6')


def bezel(d, cx, corp, seed):
    """A top ring segment of the corporation's wheel bezel."""
    cy, ro, ri = 1030, 220, 168
    a0, a1 = math.radians(-148), math.radians(-32)
    st = MER if corp == 'mer' else SOL
    n = 22

    def col(u, v, i, j, k, rc):
        ang = a0 + (a1 - a0) * u
        lam = 0.5 + 0.5 * math.cos(ang - math.radians(-125))
        b = band_from(0.15 + 0.7 * lam)
        if corp == 'mer':
            # container corrugation: alternating ribs, every 6th a dark hazard block
            if i % 6 == 5:
                return bcol(DARK, 1)
            b = max(0, b - (i % 2))
        return bcol(st, b, rc.uniform(-0.03, 0.03))
    facet(d, polar(cx, cy, ro, ro, a0, a1, ri / ro, 1.0), n * 2, 2, col, ('bz', seed), 0.15)
    # inner/outer lips
    for r0, r1, b in ((ri - 10, ri, 0), (ro, ro + 8, 2)):
        facet(d, polar(cx, cy, r1, r1, a0, a1, r0 / r1, 1.0), n, 1,
              lambda u, v, i, j, k, rc, b=b: bcol(METAL, b, rc.uniform(-0.03, 0.03)), ('lip', seed, r0), 0.1)
    if corp == 'mer':
        # container stripes: two pale bands running round the ring
        for rr in (ri + 14, ro - 14):
            pts = [(cx + rr * math.cos(a0 + (a1 - a0) * t / 30), cy + rr * math.sin(a0 + (a1 - a0) * t / 30)) for t in range(31)]
            for k in range(30):
                if k % 4 != 3:
                    line2(d, pts[k], pts[k + 1], 4, bcol(PAPER, 2))
        for k in range(1, 6):
            ang = a0 + (a1 - a0) * k / 6
            bx, by = cx + (ri + ro) / 2 * math.cos(ang), cy + (ri + ro) / 2 * math.sin(ang)
            shape(d, circle_pts(bx, by, 6, n=6), METAL, ('rv', seed, k), ink=1.8)
    else:
        # helix dots: two interleaved sine strands of dots
        for s in (0, 1):
            for t in range(40):
                ang = a0 + (a1 - a0) * (t + 0.5) / 40
                rr = (ri + ro) / 2 + (ro - ri) * 0.3 * math.sin(t * 0.55 + s * math.pi)
                x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
                front = math.cos(t * 0.55 + s * math.pi) > 0
                r = 4.6 if front else 3.0
                col = bcol(PAPER, 2) if front else bcol(SOL, 0)
                shape(d, circle_pts(x, y, r, n=6), [col] * 7, ('hd', s, t), ink=1.2 if front else 0)
    outer = [(cx + ro * math.cos(a0 + (a1 - a0) * t / 30), cy + ro * math.sin(a0 + (a1 - a0) * t / 30)) for t in range(31)]
    inner = [(cx + ri * math.cos(a1 - (a1 - a0) * t / 30), cy + ri * math.sin(a1 - (a1 - a0) * t / 30)) for t in range(31)]
    ink_poly(d, outer + inner, 3.6, ('bzink', seed))
    rust_streaks(d, outer[8:22] + [(cx, cy - ri)], ('bzr', seed), n=5, length=(10, 26))


def manifest(d, cx, cy):
    """Meridian's routing core: a faceted core in a hex cradle, ringed by containers and routing rails."""
    hexo = circle_pts(cx, cy, 210, 190, n=6, a0=math.pi / 6)
    shape(d, hexo, METAL, 'm_hex', nu=12, nv=3, ink=4.4)
    rust_streaks(d, hexo, 'mh', n=7, length=(14, 40))
    hexi = circle_pts(cx, cy, 168, 152, n=6, a0=math.pi / 6)
    shape(d, hexi, DARK, 'm_hexi', nu=12, nv=2, ink=3.0, form=-0.6)
    # routing rails (conveyor arcs)
    for k, rr in enumerate((140, 118)):
        pts = circle_pts(cx, cy, rr, rr * 0.9, n=36)
        for m in range(36):
            if (m + k * 2) % 9 < 6:
                line2(d, pts[m], pts[(m + 1) % 36], 5, bcol(MER, 1))
    # containers riding the rails
    rng = random.Random(5)
    for m in range(8):
        ang = 2 * math.pi * m / 8 + 0.2
        bx, by = cx + 140 * math.cos(ang), cy + 126 * math.sin(ang)
        w, h = 38, 24
        rect = [(bx - w / 2, by - h / 2), (bx + w / 2, by - h / 2), (bx + w / 2, by + h / 2), (bx - w / 2, by + h / 2)]
        st = [MER, RUSTR, STEEL, MER, SOL][m % 5]
        extrude(d, rect, (5, 6), st, ('crate', m), ink=2.6, front_kw=dict(nu=8, nv=1, form=0.6))
        for r in range(1, 4):
            line2(d, (bx - w / 2 + r * w / 4, by - h / 2 + 3), (bx - w / 2 + r * w / 4, by + h / 2 - 3), 1.4, bcol(st, 0))
    # the core: a big faceted sphere with an orange heart
    core = circle_pts(cx, cy, 86, n=18)
    shape(d, core, MER, 'core', nu=18, nv=4, ink=4.0, form=1.3, bias=0.05)
    heart = circle_pts(cx + 6, cy + 4, 34, n=8)
    shape(d, heart, GOLD, 'heart', nu=8, nv=2, ink=2.6, bias=0.4)
    # barcode eye
    for k in range(9):
        x = cx - 26 + k * 6.5
        h = 22 if k % 3 else 30
        line2(d, (x, cy + 4 - h / 2), (x, cy + 4 + h / 2), 2.8 if k % 2 else 1.6, INK)
    # routing cables out of the cradle
    for s in (-1, 1):
        for k in range(3):
            a = (cx + s * 200, cy - 60 + k * 50)
            b = (cx + s * 250, cy - 120 + k * 80)
            ink_line(d, a, b, 6, ('cab', s, k))
            line2(d, a, b, 3, bcol(DARK, 2))
    bevel(d, hexo[4], hexo[5], off=4, w=2.4)


def adjuster(d, cx, cy):
    """Solace elite: clinical coat over a dark suit, a twin-lens visor, a claim tablet in each hand."""
    body = [(cx - 190, cy + 230), (cx - 160, cy + 80), (cx - 80, cy + 30), (cx, cy + 44), (cx + 80, cy + 30),
            (cx + 160, cy + 80), (cx + 190, cy + 230)]
    shape(d, body, COAT, 'a_coat', nu=16, nv=3, ink=4.2)
    suit = [(cx - 50, cy + 40), (cx, cy + 52), (cx + 50, cy + 40), (cx + 30, cy + 230), (cx - 30, cy + 230)]
    shape(d, suit, SUIT, 'a_suit', ink=3.0)
    tie = [(cx - 8, cy + 50), (cx + 8, cy + 50), (cx + 12, cy + 150), (cx, cy + 166), (cx - 12, cy + 150)]
    shape(d, tie, SOL, 'a_tie', ink=2.4)
    # helix lanyard badge
    badge = [(cx + 70, cy + 110), (cx + 112, cy + 104), (cx + 116, cy + 160), (cx + 74, cy + 166)]
    shape(d, badge, PAPER, 'a_badge', ink=2.6, bias=0.2)
    for t in range(8):
        y = cy + 114 + t * 6
        line2(d, (cx + 82 + 8 * math.sin(t * 0.9), y), (cx + 104 - 8 * math.sin(t * 0.9), y), 2, bcol(SOL, 1))
    line2(d, (cx + 40, cy + 40), (cx + 90, cy + 106), 2.4, bcol(SOL, 1))
    # neck + head
    shape(d, [(cx - 22, cy - 20), (cx + 22, cy - 20), (cx + 24, cy + 40), (cx - 24, cy + 40)], SKIN, 'a_neck', ink=2.6,
          bias=-0.2)
    head = [(cx - 50, cy - 110), (cx, cy - 140), (cx + 50, cy - 110), (cx + 58, cy - 60), (cx + 36, cy - 6),
            (cx, cy + 6), (cx - 36, cy - 6), (cx - 58, cy - 60)]
    shape(d, head, SKIN, 'a_head', nu=16, nv=3, ink=3.8)
    hair = [(cx - 58, cy - 92), (cx - 46, cy - 132), (cx, cy - 150), (cx + 50, cy - 134), (cx + 60, cy - 96),
            (cx + 10, cy - 116)]
    shape(d, hair, SUIT, 'a_hair', ink=3.2)
    # twin-lens visor: two claims read at once
    bar = [(cx - 64, cy - 82), (cx + 64, cy - 82), (cx + 62, cy - 66), (cx - 62, cy - 66)]
    shape(d, bar, METAL, 'a_bar', ink=2.6)
    for s in (-1, 1):
        lens = circle_pts(cx + s * 30, cy - 74, 22, 18, n=8)
        shape(d, lens, SOL, ('a_lens', s), ink=3.0, bias=0.35)
        tri(d, [(cx + s * 30 - 10, cy - 80), (cx + s * 30 + 2, cy - 84), (cx + s * 30 - 6, cy - 72)], bcol(PAPER, 2))
    line2(d, (cx - 14, cy - 28), (cx + 16, cy - 30), 3, INK)
    # two claim tablets
    for s in (-1, 1):
        tx = cx + s * 150
        tab = [(tx - 46, cy - 40), (tx + 46, cy - 48), (tx + 50, cy + 70), (tx - 42, cy + 78)]
        extrude(d, tab, (s * 6, 8), METAL, ('tab', s), ink=3.2)
        scr = [(tx - 36, cy - 30), (tx + 36, cy - 36), (tx + 39, cy + 58), (tx - 32, cy + 64)]
        cel_fill(d, scr, SOL, ('scr', s), nu=4, nv=3, bias=0.15)
        for r in range(4):
            line2(d, (tx - 26, cy - 14 + r * 18), (tx + 24 - r * 7, cy - 18 + r * 18), 2.4, bcol(SOL, 0))
        tri(d, [(tx + 6, cy + 40), (tx + 28, cy + 36), (tx + 18, cy + 56)], ramp(NEON['red'], 0.75))  # DENIED mark
        hand = circle_pts(tx + s * -36, cy + 78, 18, 14, n=7)
        shape(d, hand, SKIN, ('hand', s), ink=2.6)


def drone(d, cx, cy):
    """Meridian collections drone: an orange container-striped body, four rotors, a claw, HP plate."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax, ay = cx + sx * 150, cy + sy * 70 - 40
            arm = [(cx + sx * 40, cy + sy * 20 - 6), (ax, ay - 6), (ax, ay + 6), (cx + sx * 40, cy + sy * 20 + 6)]
            shape(d, arm, METAL, ('arm', sx, sy), ink=3.0, nu=4, nv=1)
            rotor = circle_pts(ax, ay - 14, 74, 16, n=12)
            cel_fill(d, rotor, DARK, ('rot', sx, sy), nu=12, nv=1, bias=0.3)
            ink_poly(d, rotor, 2.4, ('rotink', sx, sy))
            line2(d, (ax - 70, ay - 12), (ax + 70, ay - 18), 3, bcol(METAL, 2))
            shape(d, circle_pts(ax, ay - 14, 9, n=6), METAL, ('hubr', sx, sy), ink=2.2)
    body = [(cx - 90, cy - 40), (cx + 90, cy - 40), (cx + 110, cy + 20), (cx + 70, cy + 80), (cx - 70, cy + 80),
            (cx - 110, cy + 20)]
    extrude(d, body, (0, 18), MER, 'dbody', ink=4.0, front_kw=dict(nu=14, nv=3, form=1.0))
    # container stripe
    stripe = [(cx - 100, cy - 2), (cx + 100, cy - 2), (cx + 104, cy + 16), (cx - 104, cy + 16)]
    quad_fill(d, stripe, PAPER, 2, 'dstripe', 6, 1)
    for k in range(-4, 5):
        line2(d, (cx + k * 22, cy - 34), (cx + k * 22, cy - 6), 2, bcol(MER, 0))
    rust_streaks(d, body, 'drust', n=5, length=(10, 30))
    chips(d, body, 'dchip', n=8)
    # red eye
    eye = circle_pts(cx, cy + 50, 20, 16, n=8)
    shape(d, eye, DARK, 'deye', ink=2.6)
    shape(d, circle_pts(cx, cy + 50, 10, n=6), RED, 'deye2', ink=0, bias=0.5)
    # claw
    for s in (-1, 1):
        claw = [(cx + s * 20, cy + 96), (cx + s * 44, cy + 140), (cx + s * 30, cy + 176), (cx + s * 22, cy + 140)]
        shape(d, claw, METAL, ('claw', s), ink=3.0)
    # HP readout plate + aim mark
    plate = [(cx + 130, cy + 70), (cx + 210, cy + 70), (cx + 210, cy + 106), (cx + 130, cy + 106)]
    shape(d, plate, DARK, 'hp', ink=2.6, flat=1)
    text(d, cx + 170, cy + 89, 'HP 6', 22, bcol(MER, 2), anchor='mm')
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        line2(d, (cx - 170 + 18 * math.cos(a), cy + 90 + 18 * math.sin(a)),
              (cx - 170 + 30 * math.cos(a), cy + 90 + 30 * math.sin(a)), 3.4, ramp(NEON['red'], 0.75))


def render():
    img = sheet()
    d = ImageDraw.Draw(img)
    manifest(d, XS[0], BUST_Y)
    adjuster(d, XS[1], BUST_Y)
    drone(d, XS[2], BUST_Y - 20)
    bezel(d, XS[0], 'mer', 'm')
    bezel(d, XS[1], 'sol', 's')
    bezel(d, XS[2], 'mer', 'd')
    labels = [(XS[0], 660, 'THE MANIFEST  -  Meridian boss'), (XS[1], 660, 'CLAIMS ADJUSTER  -  Solace elite'),
              (XS[2], 660, 'COLLECTIONS DRONE  -  Meridian regular')]
    labels += [(x, 1000, t) for x, t in zip(XS, ('Meridian bezel', 'Solace bezel', 'Meridian bezel'))]
    return finish(img, '02_enemies.png', labels, '02', 'ENEMIES  //  BUSTS + WHEEL BEZELS')


if __name__ == '__main__':
    render()
