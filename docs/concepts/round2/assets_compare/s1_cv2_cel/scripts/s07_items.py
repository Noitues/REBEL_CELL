"""07 items: Adrenal Loop daemon, Barbed Wire firmware chip, an ATK 6 slice tile for sale, currency icons."""
import math
from kit import *
from icons import slice_icon, PINK

XS = [400, 960, 1520]
TOP_Y = 380


def daemon(d, cx, cy, r=130):
    # notched coin rim (uncommon: cell cyan)
    rim = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        rr = r if k % 2 == 0 else r * 0.93
        rim.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    extrude(d, rim, (6, 10), CELL, 'dm_rim', ink=4.2, front_kw=dict(nu=32, nv=2, form=1.1))
    disc = circle_pts(cx, cy, r * 0.76, n=20)
    shape(d, disc, DARK, 'dm_disc', ink=3.0, form=-0.6, nu=20, nv=2)
    # loop arrow around a heart
    n = 28
    a0, a1 = math.radians(120), math.radians(120 + 300)
    pts = [(cx + r * 0.56 * math.cos(a0 + (a1 - a0) * k / n), cy + r * 0.56 * math.sin(a0 + (a1 - a0) * k / n)) for k in
           range(n + 1)]
    for k in range(n):
        line2(d, pts[k], pts[k + 1], 15, INK)
    for k in range(n):
        line2(d, pts[k], pts[k + 1], 9, bcol(CELL, 2 if pts[k][1] < cy else 1))
    ex, ey = pts[-1]
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = math.cos(a1), math.sin(a1)
    head = [(ex + tx * 26, ey + ty * 26), (ex + nx * 18, ey + ny * 18), (ex - nx * 18, ey - ny * 18)]
    shape(d, head, CELL, 'dm_head', ink=3.0, bias=0.3)
    heart = []
    for k in range(24):
        t = 2 * math.pi * k / 24
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        heart.append((cx + x * r * 0.022, cy + y * r * 0.022 + 4))
    extrude(d, heart, (3, 5), PINK, 'dm_heart', ink=3.4, front_kw=dict(nu=24, nv=2, form=1.2))
    # +2 pip
    ink_text(d, cx + r * 0.2, cy + r * 0.3, '+2', 26, bcol(PINK, 2))
    rust_streaks(d, rim[20:30], 'dmr', n=4)


def firmware(d, cx, cy, w=230, h=170):
    board = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2 - 26),
             (cx + w / 2 - 26, cy + h / 2), (cx - w / 2, cy + h / 2)]
    # pins
    for k in range(7):
        x = cx - w / 2 + 22 + k * (w - 44) / 6
        for s in (-1, 1):
            pin = [(x - 6, cy + s * h / 2), (x + 6, cy + s * h / 2), (x + 6, cy + s * (h / 2 + 18)), (x - 6, cy + s * (h / 2 + 18))]
            shape(d, pin, GOLD, ('pin', k, s), ink=2.0, flat=1 if s < 0 else 0)
    extrude(d, board, (6, 10), METAL, 'fw', ink=4.0, front_kw=dict(nu=10, nv=4, form=0.8))
    # traces
    for k in range(5):
        y = cy - h / 2 + 22 + k * 26
        line2(d, (cx - w / 2 + 14, y), (cx - w / 2 + 50, y), 2.4, bcol(LIME, 1))
        line2(d, (cx + w / 2 - 50, y), (cx + w / 2 - 14, y), 2.4, bcol(LIME, 1))
    # die with barbed wire coil
    die = [(cx - 62, cy - 52), (cx + 62, cy - 52), (cx + 62, cy + 52), (cx - 62, cy + 52)]
    shape(d, die, DARK, 'fw_die', ink=3.0, form=-0.5)
    pts = [(cx - 54 + k * 6, cy + 18 * math.sin(k * 0.9)) for k in range(19)]
    for a, b in zip(pts, pts[1:]):
        line2(d, a, b, 5, INK)
        line2(d, a, b, 2.6, bcol(METAL, 2))
    for k in range(2, 18, 3):
        x, y = pts[k]
        for s in (-1, 1):
            tri(d, [(x - 3, y), (x + 3, y), (x + s * 2, y + s * 12)], bcol(METAL, 2))
            ink_line(d, (x, y), (x + s * 2, y + s * 12), 1.2, ('barb', k, s))
    slice_icon(d, 'DEFEND', cx + 40, cy - 30, 30, seed='fw_def')
    ink_text(d, cx - 30, cy + 40, 'FW', 18, bcol(LIME, 2), stroke=1, shadow=None)
    rust_streaks(d, board, 'fwr', n=4)
    chips(d, board, 'fwc', n=8)


def slice_tile(d, cx, cy):
    r0, r1 = 70, 230
    ccx, ccy = cx, cy + 170
    a0, a1 = math.radians(-120), math.radians(-60)
    side = [(ccx + r1 * math.cos(a0 + (a1 - a0) * k / 10), ccy + r1 * math.sin(a0 + (a1 - a0) * k / 10) + 12) for k in range(11)]
    q = polar(ccx, ccy, r1, r1, a0, a1, r0 / r1, 1.0)
    # thickness
    for k in range(10):
        quad_fill(d, [side[k], side[k + 1],
                      (ccx + r1 * math.cos(a0 + (a1 - a0) * (k + 1) / 10), ccy + r1 * math.sin(a0 + (a1 - a0) * (k + 1) / 10)),
                      (ccx + r1 * math.cos(a0 + (a1 - a0) * k / 10), ccy + r1 * math.sin(a0 + (a1 - a0) * k / 10))],
                  RED, 0, ('ts', k), 1, 1)
    facet(d, q, 6, 4, lambda u, v, i, j, k, rc: bcol(RED, band_from(0.3 + 0.6 * (1 - u) * v + 0.1), rc.uniform(-0.03, 0.03)),
          'tile', 0.28)
    outline = [q(t / 10, 1) for t in range(11)] + [q(1 - t / 10, 0) for t in range(11)]
    ink_poly(d, hull(outline + side), 4.0, 'tile_sil')
    ink_poly(d, outline, 2.2, 'tile_in')
    slice_icon(d, 'ATTACK', cx - 28, cy - 4, 70, seed='tile_atk')
    ink_text(d, cx + 40, cy - 2, '6', 64, hexc('#fff0e6'))
    rust_streaks(d, outline[:11], 'tr', n=3)
    # price tape
    tq = [(cx - 70, cy + 92), (cx + 70, cy + 86), (cx + 72, cy + 126), (cx - 68, cy + 132)]
    shape(d, tq, PAPER, 'price', ink=2.6, nu=4, nv=1, bias=0.3)
    text(d, cx, cy + 110, '60 cycles', 30, hexc('#241c16'), anchor='mm', style=None, path=HAND)


def currency(d, name, cx, cy, s):
    w = max(1.4, s * 0.035)
    if name == 'CYCLES':
        rim = circle_pts(cx, cy, s * 0.46, n=16)
        extrude(d, rim, (s * 0.03, s * 0.06), GOLD, ('cy', s), ink=w * 1.2, front_kw=dict(nu=16, nv=2, form=1.1))
        n = 16
        a0, a1 = math.radians(200), math.radians(200 + 280)
        pts = [(cx + s * 0.26 * math.cos(a0 + (a1 - a0) * k / n), cy + s * 0.26 * math.sin(a0 + (a1 - a0) * k / n))
               for k in range(n + 1)]
        for a, b in zip(pts, pts[1:]):
            line2(d, a, b, max(2, s * 0.1), INK)
        ex, ey = pts[-1]
        tri(d, [(ex - s * 0.1, ey - s * 0.08), (ex + s * 0.1, ey - s * 0.02), (ex, ey + s * 0.12)], INK)
    elif name == 'SCHEMATICS':
        sheet_ = [(cx - s * 0.4, cy - s * 0.32), (cx + s * 0.34, cy - s * 0.4), (cx + s * 0.4, cy + s * 0.32),
                  (cx - s * 0.34, cy + s * 0.4)]
        extrude(d, sheet_, (s * 0.03, s * 0.05), HAL, ('sc', s), ink=w * 1.2, front_kw=dict(nu=4, nv=4, form=0.8))
        g = circle_pts(cx, cy, s * 0.18, n=8)
        for k in range(8):
            a = 2 * math.pi * k / 8
            line2(d, (cx + s * 0.18 * math.cos(a), cy + s * 0.18 * math.sin(a)),
                  (cx + s * 0.27 * math.cos(a), cy + s * 0.27 * math.sin(a)), max(1.6, s * 0.06), bcol(PAPER, 2))
        ink_poly(d, g, max(1.4, s * 0.04), ('scg', s))
        for k in range(8):
            line2(d, g[k], g[(k + 1) % 8], max(1, s * 0.025), bcol(PAPER, 2))
        line2(d, (cx - s * 0.3, cy + s * 0.3), (cx + s * 0.1, cy + s * 0.26), max(1, s * 0.02), bcol(PAPER, 2))
    elif name == 'RAM':
        stick = [(cx - s * 0.46, cy - s * 0.2), (cx + s * 0.46, cy - s * 0.2), (cx + s * 0.46, cy + s * 0.14),
                 (cx - s * 0.46, cy + s * 0.14)]
        extrude(d, stick, (s * 0.03, s * 0.05), CELL, ('rm', s), ink=w * 1.2, front_kw=dict(nu=6, nv=2))
        for k in range(3):
            x = cx - s * 0.3 + k * s * 0.3
            shape(d, [(x - s * 0.1, cy - s * 0.12), (x + s * 0.1, cy - s * 0.12), (x + s * 0.1, cy + s * 0.06),
                      (x - s * 0.1, cy + s * 0.06)], DARK, ('rc', s, k), ink=w * 0.7)
        for k in range(9):
            x = cx - s * 0.4 + k * s * 0.1
            line2(d, (x, cy + s * 0.16), (x, cy + s * 0.27), max(1.2, s * 0.04), bcol(GOLD, 2))
    elif name == 'HEAT':
        warn = [(cx, cy - s * 0.46), (cx + s * 0.48, cy + s * 0.38), (cx - s * 0.48, cy + s * 0.38)]
        extrude(d, warn, (s * 0.03, s * 0.05), RED, ('ht', s), ink=w * 1.2, front_kw=dict(nu=6, nv=2))
        fl = [(cx, cy - s * 0.2), (cx + s * 0.13, cy + s * 0.02), (cx + s * 0.16, cy + s * 0.18), (cx + s * 0.06, cy + s * 0.3),
              (cx - s * 0.08, cy + s * 0.3), (cx - s * 0.16, cy + s * 0.16), (cx - s * 0.08, cy - s * 0.02)]
        shape(d, fl, GOLD, ('hf', s), ink=w * 0.8, bias=0.3)


def render():
    img = sheet()
    d = ImageDraw.Draw(img)
    daemon(d, XS[0], TOP_Y)
    firmware(d, XS[1], TOP_Y)
    slice_tile(d, XS[2], TOP_Y)
    labels = [(XS[0], 560, 'ADRENAL LOOP  -  daemon, Uncommon'), (XS[0], 588, 'each Perfect heals 2'),
              (XS[1], 560, 'BARBED WIRE  -  firmware, Common'), (XS[1], 588, 'DEF slice also deals 2'),
              (XS[2], 560, 'SLICE TILE  -  ATK 6, for sale'), (XS[2], 588, '')]
    for k, name in enumerate(['CYCLES', 'SCHEMATICS', 'RAM', 'HEAT']):
        cx = 480 + k * 320
        currency(d, name, cx, 820, 110)
        currency(d, name, cx + 100, 850, 32)
        labels.append((cx + 20, 930, name))
    return finish(img, '07_items.png', labels, '07', 'ITEMS  //  DAEMON, FIRMWARE, SLICE TILE, CURRENCIES')


if __name__ == '__main__':
    render()
