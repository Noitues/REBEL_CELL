"""Round 9 rebuild: the 31 program images as true low-poly art (512-unit canvas, 1024 px).

Same subjects, compositions and colour families as round 8's icons8.py; every outline is
straight polygon edges, every shape is triangulated into toon-banded facets with ink.
draw(name) -> RGBA 1024 image.
"""
import math
import random
from lowpolyicon import Icon, ngon, arc, bar, rect, thick_path, flames, mix, INK

BONE = (238, 214, 214)
BONE_PINK = (246, 196, 214)
STEEL = (150, 184, 206)
STEEL_D = (96, 128, 152)
WOOD = (214, 132, 78)
WOOD_D = (160, 86, 52)
FIRE_R = (236, 52, 52)
FIRE_O = (255, 128, 30)
FIRE_Y = (255, 214, 80)
MAGENTA = (255, 60, 200)
VIOLET = (170, 70, 230)
POISON = (196, 90, 255)
CYAN = (92, 225, 255)
GREEN = (110, 220, 110)
GREEN_D = (50, 150, 80)
DARK = (44, 40, 58)
GREYC = (176, 176, 186)
PAPER = (244, 232, 222)
RED = (255, 50, 70)


# ------------------------------------------------------------------ shared parts
def fire(ic, cx, base, w, h, seed, n=6):
    ic.poly(flames(cx, base, w, h, n, seed), FIRE_R, emis=True, ink=8)
    ic.poly(flames(cx, base, w * 0.74, h * 0.74, max(3, n - 1), seed + 3), FIRE_O, emis=True, ink=0)
    ic.poly(flames(cx, base, w * 0.42, h * 0.46, 3, seed + 7, sharp=0.8), FIRE_Y, emis=True, ink=0)


def skull(ic, cx, cy, s, bone=BONE, eye=FIRE_O, crack=False, jaw=0.0):
    # cranium: 16 straight edges over the top, angular cheekbones, a boxy jaw
    top = arc(cx, cy, s, s * 0.98, 160, 380, 12)
    cran = [top[0]] + top[1:] + [(cx + s * 0.86, cy + s * 0.32), (cx + s * 0.6, cy + s * 0.66), (cx - s * 0.6, cy + s * 0.66),
                                   (cx - s * 0.86, cy + s * 0.32)]
    jy = cy + s * (0.62 + jaw)
    jawp = [(cx - s * 0.58, jy), (cx + s * 0.58, jy), (cx + s * 0.52, jy + s * 0.5), (cx - s * 0.52, jy + s * 0.5)]
    ic.group([cran, jawp], bone, ink=9, seg=s * 0.42)
    ic.ink(jawp, 5)
    # teeth gaps
    for k in range(5):
        x = cx + (-0.4 + k * 0.2) * s
        ic.line((x, jy + s * 0.06), (x, jy + s * 0.46), max(4, s * 0.06), INK)
    for sx in (-1, 1):
        eyep = [(cx + sx * 0.12 * s, cy - 0.06 * s), (cx + sx * 0.72 * s, cy - 0.28 * s), (cx + sx * 0.64 * s, cy + 0.22 * s),
                (cx + sx * 0.2 * s, cy + 0.3 * s)]
        ic.poly(eyep, eye, emis=True, ink=7, seg=s * 0.2)
    ic.poly([(cx, cy + 0.34 * s), (cx - 0.13 * s, cy + 0.56 * s), (cx + 0.13 * s, cy + 0.56 * s)], DARK, ink=5, seg=99)
    if crack:
        pts = [(cx + 0.1 * s, cy - 0.98 * s), (cx + 0.2 * s, cy - 0.72 * s), (cx + 0.08 * s, cy - 0.56 * s),
               (cx + 0.22 * s, cy - 0.36 * s)]
        for a, b in zip(pts, pts[1:]):
            ic.line(a, b, 6, INK)


def bomb(ic, cx, cy, r, mark=True):
    ic.poly(ngon(cx, cy, r, n=14), DARK, ink=9, seg=r * 0.5, light=0.08)
    ic.poly(rect(cx - r * 0.2, cy - r * 1.12, cx + r * 0.2, cy - r * 0.86), (120, 120, 140), ink=6)
    fuse = [(cx, cy - r * 1.1), (cx + r * 0.25, cy - r * 1.4), (cx + r * 0.55, cy - r * 1.45), (cx + r * 0.72, cy - r * 1.3)]
    ic.poly(thick_path(fuse, 9), (200, 170, 120), ink=5, seg=99)
    ic.star(cx + r * 0.78, cy - r * 1.36, r * 0.32, FIRE_Y)
    if mark:
        skull(ic, cx, cy + r * 0.04, r * 0.36, bone=(255, 120, 190), eye=DARK)


def bone_bar(ic, a, b, w, col):
    ic.poly(bar(a, b, w), col, ink=8, seg=w * 1.2)
    for p in (a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        for s in (-1, 1):
            ic.poly(ngon(p[0] + nx * s * w * 0.55, p[1] + ny * s * w * 0.55, w * 0.62, n=7), col, ink=8, seg=99)


def flask(ic, cx, cy, r, liquid, glass=(200, 190, 230)):
    neck = rect(cx - r * 0.26, cy - r * 1.62, cx + r * 0.26, cy - r * 0.8)
    body = ngon(cx, cy, r, n=14, rot=-math.pi / 2 + math.pi / 14)
    ic.group([neck, body], glass, ink=10, seg=r * 0.5, light=0.1)
    # liquid: the body below a flat surface, a bright facet cluster
    lv = cy - r * 0.15
    liq = [p for p in body if p[1] >= lv]
    side = []
    for k in range(len(body)):
        a, b = body[k], body[(k + 1) % len(body)]
        if (a[1] - lv) * (b[1] - lv) < 0:
            t = (lv - a[1]) / (b[1] - a[1])
            side.append((a[0] + (b[0] - a[0]) * t, lv))
    liq = sorted(liq, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    left = min(side, key=lambda p: p[0])
    right = max(side, key=lambda p: p[0])
    poly = [right] + [p for p in sorted(liq, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))] + [left]
    ic.poly(poly, liquid, emis=True, ink=4, seg=r * 0.36)
    ic.poly(rect(cx - r * 0.34, cy - r * 1.86, cx + r * 0.34, cy - r * 1.58), WOOD, ink=7)
    # glass glint
    ic.solid([(cx - r * 0.66, cy - r * 0.42), (cx - r * 0.5, cy - r * 0.62), (cx - r * 0.44, cy - r * 0.2)], (250, 250, 255))


def envelope(ic, x0, y0, x1, y1, col=PAPER, open_flap=True):
    ic.poly(rect(x0, y0, x1, y1), col, ink=8)
    cx = (x0 + x1) / 2
    ic.poly([(x0, y0), (x1, y0), (cx, (y0 + y1) / 2 + 6)], mix(col, (180, 160, 170), 0.35), ink=6, seg=999)
    if open_flap:
        ic.poly([(x0, y0), (x1, y0), (cx, y0 - (y1 - y0) * 0.55)], mix(col, (255, 255, 255), 0.2), ink=6, seg=999)


def hook(ic, cx, top, bottom, col=(200, 210, 230)):
    ic.line((cx, 0), (cx, top), 3, (220, 220, 230))
    curve = [(cx, top)] + [(cx, bottom - 40)] + arc(cx - 34, bottom - 40, 34, 40, 0, 180, 8)[1:] + [(cx - 68, bottom - 70)]
    ic.poly(thick_path(curve, 16), col, ink=7, seg=40)
    ic.poly([(cx - 68, bottom - 70), (cx - 84, bottom - 52), (cx - 72, bottom - 92)], col, ink=6, seg=99)
    ic.poly(ngon(cx, top, 12, n=6), col, ink=6)


def bricks(ic, x0, y0, x1, y1, rows, col, seed=0):
    h = (y1 - y0) / rows
    bw = (x1 - x0) / 4
    rng = random.Random(seed)
    for r in range(rows):
        off = bw / 2 if r % 2 else 0
        x = x0 - off
        while x < x1 - 1:
            a = max(x0, x)
            b = min(x1, x + bw)
            if b - a > 8:
                c = mix(col, (255, 255, 255), rng.uniform(-0.05, 0.12)) if rng.random() < 0.7 else mix(col, (0, 0, 0), 0.1)
                ic.poly(rect(a + 3, y0 + r * h + 3, b - 3, y0 + (r + 1) * h - 3), c, ink=5, seg=h * 0.9)
            x += bw


def chip(ic, x0, y0, x1, y1, col=(70, 70, 88)):
    for k in range(6):
        t = (k + 0.5) / 6
        for (a, b) in (((x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y0 - 22)), ((x0 + (x1 - x0) * t, y1), (x0 + (x1 - x0) * t, y1 + 22)),
                       ((x0, y0 + (y1 - y0) * t), (x0 - 22, y0 + (y1 - y0) * t)), ((x1, y0 + (y1 - y0) * t), (x1 + 22, y0 + (y1 - y0) * t))):
            ic.poly(bar(a, b, 12), (210, 190, 120), ink=4, seg=99)
    ic.poly(rect(x0, y0, x1, y1), col, ink=9, seg=60)
    ic.poly(rect(x0 + 40, y0 + 40, x1 - 40, y1 - 40), mix(col, (0, 0, 0), 0.3), ink=5, seg=60, flat=True)


def cloud(ic, cx, cy, s, col, ink=9):
    polys = [ngon(cx - s * 0.55, cy + s * 0.08, s * 0.42, n=11), ngon(cx - s * 0.1, cy - s * 0.2, s * 0.56, n=13),
             ngon(cx + s * 0.48, cy - s * 0.02, s * 0.46, n=12), rect(cx - s * 0.9, cy + s * 0.05, cx + s * 0.9, cy + s * 0.46)]
    ic.group(polys, col, ink=ink, seg=s * 0.34, centre=(cx - s * 0.1, cy - s * 0.1))


def magnifier(ic, cx, cy, r, inner):
    ic.poly(bar((cx + r * 0.7, cy + r * 0.7), (cx + r * 1.6, cy + r * 1.6), r * 0.34), (70, 70, 84), ink=9, seg=40)
    ring = ngon(cx, cy, r, n=18)
    ic.poly(ring, (190, 190, 205), ink=10, seg=r * 0.5)
    glass = ngon(cx, cy, r * 0.8, n=18)
    inner(glass)
    ic.ink(glass, 6)


def static(ic, pts, seed, cols=((40, 40, 48), (120, 120, 130), (200, 200, 210), (70, 70, 80))):
    rng = random.Random(seed)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    r = (max(xs) - min(xs)) / 2
    ic.solid(pts, cols[0])
    for _ in range(140):
        a = rng.uniform(0, 6.283)
        d = r * math.sqrt(rng.random()) * 0.92
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        s = rng.uniform(5, 13)
        ic.solid([(x, y), (x + s, y + rng.uniform(-3, 3)), (x + rng.uniform(-2, 6), y + s)], rng.choice(cols[1:]))


def shield_pts(cx, y0, w, h):
    return [(cx - w / 2, y0), (cx + w / 2, y0), (cx + w / 2, y0 + h * 0.45), (cx + w * 0.3, y0 + h * 0.8), (cx, y0 + h),
            (cx - w * 0.3, y0 + h * 0.8), (cx - w / 2, y0 + h * 0.45)]


def padlock(ic, cx, cy, w, col=STEEL, password=False):
    sh = arc(cx, cy - w * 0.32, w * 0.34, w * 0.42, 180, 360, 8)
    ic.poly(thick_path(sh, w * 0.12), (200, 210, 225), ink=8, seg=40)
    body = rect(cx - w / 2, cy - w * 0.32, cx + w / 2, cy + w * 0.42)
    ic.poly(body, col, ink=10, seg=w * 0.3)
    if password:
        ic.poly(rect(cx - w * 0.4, cy - w * 0.06, cx + w * 0.4, cy + w * 0.2), (14, 30, 40), ink=5, flat=True)
        ic.text(cx, cy + w * 0.07, '* * *', w * 0.2, CYAN, glow=True)
    else:
        ic.poly(ngon(cx, cy - w * 0.02, w * 0.1, n=8), DARK, ink=4, seg=99)
        ic.poly([(cx - w * 0.05, cy), (cx + w * 0.05, cy), (cx + w * 0.07, cy + w * 0.22), (cx - w * 0.07, cy + w * 0.22)], DARK,
                ink=4, seg=99)


def bug(ic, cx, cy, s, col, mark=None):
    for k, (ay, sx) in enumerate([(y, x) for y in (-0.15, 0.15, 0.45) for x in (-1, 1)]):
        a = (cx + sx * s * 0.3, cy + ay * s)
        b = (cx + sx * s * 0.75, cy + (ay - 0.12) * s)
        c = (cx + sx * s * 0.95, cy + (ay + 0.25) * s)
        ic.poly(thick_path([a, b, c], 12), DARK, ink=5, seg=99)
    ic.poly(ngon(cx, cy + s * 0.18, s * 0.42, s * 0.55, n=10), col, ink=9, seg=s * 0.3)
    ic.poly(ngon(cx, cy - s * 0.5, s * 0.24, n=8), mix(col, (0, 0, 0), 0.35), ink=8, seg=99)
    for sx in (-1, 1):
        ic.line((cx + sx * s * 0.1, cy - s * 0.68), (cx + sx * s * 0.3, cy - s * 0.95), 6, INK)
    if mark:
        ic.text(cx, cy + s * 0.2, mark, s * 0.36, (240, 255, 240), glow=True)


# ------------------------------------------------------------------ the 31 images
def flaming_skull(ic):
    fire(ic, 256, 380, 440, 330, 3, n=7)
    skull(ic, 256, 248, 132, eye=FIRE_O)


def fire_(ic):
    fire(ic, 256, 450, 400, 400, 11, n=6)


def bomb_(ic):
    bomb(ic, 240, 300, 150)


def skull_(ic):
    skull(ic, 256, 236, 168, bone=BONE_PINK, eye=MAGENTA, crack=True)


def skull_fuse(ic):
    skull(ic, 256, 266, 150, bone=BONE, eye=FIRE_O)
    fuse = [(256, 118), (300, 80), (350, 76), (380, 96)]
    ic.poly(thick_path(fuse, 10), (200, 170, 120), ink=5, seg=99)
    ic.star(392, 92, 40, FIRE_Y)


def crossbones(ic):
    bone_bar(ic, (110, 390), (402, 150), 36, BONE)
    bone_bar(ic, (110, 150), (402, 390), 36, BONE)
    skull(ic, 256, 230, 118, bone=BONE_PINK, eye=MAGENTA)


def poison_vial(ic):
    flask(ic, 256, 320, 150, POISON)
    skull(ic, 256, 330, 50, bone=(250, 245, 250), eye=DARK)
    for (x, y) in ((176, 200), (340, 470)):
        ic.poly([(x, y - 18), (x + 10, y + 4), (x, y + 12), (x - 10, y + 4)], POISON, emis=True, ink=4, seg=99)


def bio_bug(ic):
    bug(ic, 256, 280, 190, (230, 70, 110))
    for k in range(3):
        a = -math.pi / 2 + k * 2 * math.pi / 3
        ic.poly(ngon(256 + 40 * math.cos(a), 310 + 40 * math.sin(a), 30, n=7), DARK, ink=0, seg=99)
    ic.poly(ngon(256, 310, 16, n=7), (230, 70, 110), ink=4, seg=99)


def storm_cloud(ic):
    cloud(ic, 256, 210, 210, (120, 90, 150))
    bolt = [(270, 280), (220, 380), (256, 380), (226, 470), (316, 350), (278, 350), (306, 280)]
    ic.poly(bolt, FIRE_Y, emis=True, ink=7, seg=50)
    rng = random.Random(4)
    for _ in range(14):
        x, y = rng.uniform(90, 430), rng.uniform(320, 470)
        if 200 < x < 330:
            continue
        ic.poly(rect(x, y, x + 12, y + 12), POISON, emis=True, ink=3, seg=99)


def trojan_horse(ic):
    for x in (130, 200, 310, 380):
        ic.poly(ngon(x, 440, 26, n=8), WOOD_D, ink=7, seg=99)
    ic.poly(rect(90, 400, 420, 424), WOOD_D, ink=7, seg=60)
    for x in (140, 196, 300, 356):
        ic.poly(rect(x, 300, x + 32, 404), WOOD, ink=7, seg=40)
    body = [(110, 222), (130, 200), (360, 196), (384, 214), (390, 300), (120, 306)]
    tail = [(110, 222), (56, 260), (64, 280), (116, 262)]
    neck = [(318, 204), (372, 104), (410, 112), (392, 214)]
    head = [(366, 104), (390, 70), (438, 78), (470, 118), (466, 136), (420, 134), (404, 120)]
    ic.group([body, tail, neck, head], WOOD, ink=10, seg=60)
    for k in range(5):
        y = 220 + k * 16
        ic.line((130, y), (370, y - 2), 3, mix(WOOD, INK, 0.5))
    for k in range(6):
        y0 = 102 + k * 18
        x0 = 360 - k * 8
        ic.poly([(x0, y0), (x0 - 26, y0 + 4), (x0 - 4, y0 + 14)], (190, 90, 80), ink=4, seg=99)
    ic.poly(rect(210, 222, 290, 290), (18, 10, 16), ink=6, flat=True, seg=99)
    skull(ic, 250, 250, 26, bone=(255, 120, 150), eye=DARK)
    ic.gd.rectangle([210 * 2, 222 * 2, 290 * 2, 290 * 2], fill=(255, 40, 90))
    ic.poly([(214, 292), (290, 292), (300, 334), (224, 334)], WOOD_D, ink=6, seg=99)
    ic.poly(ngon(436, 100, 8, n=6), RED, emis=True, ink=3, seg=99)


def envelope_bomb(ic):
    envelope(ic, 110, 280, 402, 450)
    bomb(ic, 256, 240, 92, mark=True)
    ic.poly(rect(130, 330, 382, 450), PAPER, ink=8, seg=60)
    ic.poly([(130, 330), (256, 410), (382, 330)], mix(PAPER, (180, 160, 170), 0.3), ink=6, seg=999)


def phish_hook(ic):
    hook(ic, 300, 60, 330)
    env = [(150, 330), (340, 330), (340, 450), (150, 450)]
    ic.poly(env, PAPER, ink=8, seg=60)
    ic.poly([(150, 330), (340, 330), (245, 400)], mix(PAPER, (180, 160, 170), 0.35), ink=6, seg=999)
    ic.poly(ngon(300, 420, 18, n=8), RED, emis=True, ink=4, seg=99)


def hook_password(ic):
    hook(ic, 300, 60, 330)
    ic.poly(rect(130, 330, 380, 440), (40, 30, 50), ink=8, seg=60, flat=True)
    ic.text(255, 385, '* * *', 54, MAGENTA, glow=True)


def burning_wall(ic):
    fire(ic, 256, 236, 420, 210, 21, n=7)
    bricks(ic, 60, 230, 452, 470, 5, STEEL)


def wall_shield(ic):
    bricks(ic, 60, 120, 452, 470, 7, STEEL, seed=3)
    ic.poly(shield_pts(256, 150, 220, 290), (210, 240, 252), ink=11, seg=70)
    ic.poly(shield_pts(256, 190, 140, 190), CYAN, ink=6, seg=60, emis=True)


def vault_door(ic):
    ic.poly(rect(48, 170, 90, 340), STEEL_D, ink=8, seg=60)
    for k in range(12):
        a = 2 * math.pi * k / 12
        c = (256 + 208 * math.cos(a), 256 + 208 * math.sin(a))
        ic.poly(ngon(c[0], c[1], 14, n=4, rot=a + math.pi / 4), (200, 225, 240), ink=5, seg=99)
    ic.poly(ngon(256, 256, 196, n=20), STEEL, ink=11, seg=64)
    ic.poly(ngon(256, 256, 150, n=20), STEEL_D, ink=6, seg=56, light=-0.1)
    ic.ink(ngon(256, 256, 120, n=20), 4)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p0 = (256, 256)
        p1 = (256 + 104 * math.cos(a), 256 + 104 * math.sin(a))
        ic.poly(bar(p0, p1, 26), (220, 236, 246), ink=7, seg=40)
        ic.poly(ngon(p1[0], p1[1], 20, n=8), (220, 236, 246), ink=7, seg=99)
    ic.ink(ngon(256, 256, 70, n=16), 18)
    ic.poly(ngon(256, 256, 70, n=16), (220, 236, 246), ink=0, seg=40)
    ic.poly(ngon(256, 256, 48, n=16), STEEL_D, ink=6, seg=40)
    ic.poly(ngon(256, 256, 26, n=10), (230, 242, 250), ink=6, seg=99)


def steel_safe(ic):
    ic.poly(rect(90, 90, 422, 430), STEEL_D, ink=11, seg=90)
    ic.poly(rect(120, 120, 392, 400), STEEL, ink=7, seg=80)
    for x in (110, 380):
        ic.poly(rect(x, 430, x + 30, 460), DARK, ink=6, seg=99)
    ic.poly(ngon(256, 250, 80, n=16), (220, 236, 246), ink=8, seg=40)
    ic.poly(ngon(256, 250, 56, n=16), STEEL_D, ink=5, seg=40)
    for k in range(12):
        a = 2 * math.pi * k / 12
        ic.line((256 + 62 * math.cos(a), 250 + 62 * math.sin(a)), (256 + 74 * math.cos(a), 250 + 74 * math.sin(a)), 4, INK)
    ic.poly(bar((256, 250), (256, 200), 14), (240, 244, 250), ink=5, seg=99)
    ic.poly(bar((330, 340), (370, 340), 18), (220, 236, 246), ink=6, seg=99)
    ic.poly(ngon(380, 150, 10, n=8), (60, 230, 110), emis=True, ink=4, seg=99)


def riveted_shield(ic):
    ic.poly(shield_pts(256, 70, 330, 400), STEEL, ink=12, seg=80)
    ic.poly(shield_pts(256, 110, 250, 300), STEEL_D, ink=6, seg=70, light=-0.05)
    ic.poly([(240, 110), (272, 110), (272, 372), (256, 410), (240, 372)], CYAN, ink=5, seg=60, emis=True)
    for (x, y) in [(120, 100), (392, 100), (110, 220), (402, 220), (150, 330), (362, 330), (256, 450)]:
        ic.poly(ngon(x, y, 13, n=6), (230, 240, 250), ink=5, seg=99)


def blast_door(ic):
    ic.poly(rect(70, 70, 442, 450), DARK, ink=11, seg=120, flat=True)
    for x0, x1 in ((90, 250), (262, 422)):
        ic.poly(rect(x0, 90, x1, 430), STEEL, ink=8, seg=80)
        for y in (130, 260, 390):
            for x in (x0 + 26, x1 - 26):
                ic.poly(ngon(x, y, 10, n=6), (230, 240, 250), ink=4, seg=99)
        for k in range(4):
            y = 180 + k * 46
            ic.poly([(x0 + 40, y), (x1 - 40, y), (x1 - 40, y + 16), (x0 + 40, y + 16)], mix((255, 200, 40), (0, 0, 0), 0.15 * (k % 2)),
                    ink=4, seg=99)
    ic.glowline((256, 92), (256, 428), 8, CYAN)


def padlock_password(ic):
    padlock(ic, 256, 300, 280, password=True)


def padlock_(ic):
    padlock(ic, 256, 300, 260)


def anon_mask(ic):
    mask = [(256, 64), (348, 92), (402, 170), (410, 270), (370, 380), (300, 452), (212, 452), (142, 380), (102, 270), (110, 170),
            (164, 92)]
    ic.poly(mask, (236, 236, 246), ink=11, seg=72)
    # planar cheekbones: two big shaded planes
    for sx in (-1, 1):
        cheek = [(256 + sx * 40, 300), (256 + sx * 148, 266), (256 + sx * 112, 380), (256 + sx * 52, 410)]
        ic.poly(cheek, (200, 200, 220), ink=4, seg=70, light=-0.12 * sx)
        ic.poly(bar((256 + sx * 90, 290), (256 + sx * 76, 360), 12), VIOLET, ink=3, seg=99)
    for sx in (-1, 1):
        slit = [(256 + sx * 30, 236), (256 + sx * 138, 206), (256 + sx * 132, 236), (256 + sx * 40, 260)]
        ic.poly(slit, GREEN, emis=True, ink=7, seg=40)
    ic.glowline((150, 248), (362, 248), 5, CYAN)
    smile = arc(256, 352, 80, 26, 20, 160, 6)
    for a, b in zip(smile, smile[1:]):
        ic.line(a, b, 6, (120, 60, 200))
    ic.line((300, 70), (320, 150), 5, INK)
    ic.line((320, 150), (300, 190), 5, INK)


def cloud_(ic):
    cloud(ic, 286, 270, 190, GREEN)
    for k, y in enumerate((220, 270, 320)):
        ic.poly(bar((40, y), (130 - k * 20, y), 12), (200, 255, 200), ink=4, seg=99)


def key_(ic):
    bow = ngon(160, 330, 96, n=12)
    shaft = bar((230, 280), (450, 130), 40)
    bit1 = [(394, 168), (430, 216), (404, 232), (370, 186)]
    bit2 = [(340, 204), (370, 250), (346, 264), (318, 220)]
    ic.group([bow, shaft, bit1, bit2], GREEN, ink=10, seg=60)
    ic.ink(ngon(160, 330, 44, n=10), 8)
    ic.solid(ngon(160, 330, 44, n=10), (0, 0, 0, 0))
    ic.d.polygon([(x * 2, y * 2) for x, y in ngon(160, 330, 42, n=10)], fill=(0, 0, 0, 0))
    ic.star(130, 220, 40, (230, 255, 220))


def fingerprint(ic):
    for k in range(7):
        r = 40 + k * 26
        pts = arc(256, 290, r * 0.8, r, 150, 390, 12)
        ic.poly(thick_path(pts, 12), GREEN if k % 2 else GREEN_D, ink=5, seg=40)
    ic.glowline((80, 300), (432, 300), 6, (160, 255, 160))


def chip_repair(ic):
    chip(ic, 130, 130, 382, 382)
    crack = [(160, 170), (230, 250), (210, 290), (290, 350)]
    for a, b in zip(crack, crack[1:]):
        ic.line(a, b, 9, INK)
    trace = [(140, 300), (230, 300), (260, 260), (370, 260)]
    for a, b in zip(trace, trace[1:]):
        ic.glowline(a, b, 7, GREEN)
    ic.star(262, 262, 34, (220, 255, 210))


def magnifier_static(ic):
    magnifier(ic, 216, 216, 156, lambda g: static(ic, g, 5))


def unplugged_chip(ic):
    chip(ic, 120, 150, 330, 360, (90, 90, 104))
    cable = [(440, 470), (440, 380), (400, 340), (390, 300)]
    ic.poly(thick_path(cable, 18), DARK, ink=6, seg=60)
    ic.poly(rect(370, 250, 412, 300), (170, 170, 180), ink=6, seg=99)
    for x in (378, 398):
        ic.poly(rect(x, 228, x + 8, 250), (220, 200, 120), ink=3, seg=99)
    ic.text(390, 140, 'z', 56, (200, 200, 210))
    ic.text(436, 96, 'z', 40, (200, 200, 210))


def magnifier_code(ic):
    def inner(g):
        ic.solid(g, (10, 30, 18))
        rng = random.Random(9)
        for k in range(8):
            y = 120 + k * 26
            x = 100 + rng.uniform(0, 40)
            ic.line((x, y), (x + rng.uniform(60, 180), y), 9, GREEN if k % 3 else (180, 255, 180))
            ic.gd.line([(x * 2, y * 2), ((x + 100) * 2, y * 2)], fill=(40, 160, 60), width=12)
    magnifier(ic, 216, 216, 156, inner)


def debug_bug(ic):
    bug(ic, 256, 270, 190, GREEN_D, mark='</>')


def password(ic):
    ic.poly(rect(70, 130, 442, 400), (60, 70, 86), ink=11, seg=100, flat=True)
    ic.poly(rect(70, 130, 442, 172), (120, 200, 140), ink=6, seg=100)
    ic.poly(rect(110, 210, 402, 280), (14, 30, 20), ink=6, seg=100, flat=True)
    ic.text(256, 246, '* * * *', 56, GREEN, glow=True)
    ic.poly(rect(300, 316, 402, 370), GREEN, ink=6, seg=60)
    ic.text(351, 343, 'OK', 30, (20, 40, 24))


DRAW = {'flaming_skull': flaming_skull, 'fire': fire_, 'bomb': bomb_, 'skull': skull_, 'skull_fuse': skull_fuse,
        'crossbones': crossbones, 'poison_vial': poison_vial, 'bio_bug': bio_bug, 'storm_cloud': storm_cloud,
        'trojan_horse': trojan_horse, 'envelope_bomb': envelope_bomb, 'phish_hook': phish_hook, 'hook_password': hook_password,
        'burning_wall': burning_wall, 'wall_shield': wall_shield, 'vault_door': vault_door, 'steel_safe': steel_safe,
        'riveted_shield': riveted_shield, 'blast_door': blast_door, 'padlock_password': padlock_password, 'padlock': padlock_,
        'anon_mask': anon_mask, 'cloud': cloud_, 'key': key_, 'fingerprint': fingerprint, 'chip_repair': chip_repair,
        'magnifier_static': magnifier_static, 'unplugged_chip': unplugged_chip, 'magnifier_code': magnifier_code,
        'debug_bug': debug_bug, 'password': password}


def draw(name):
    ic = Icon()
    DRAW[name](ic)
    return ic.done()
