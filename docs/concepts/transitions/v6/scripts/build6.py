"""Transitions storyboard v6: only T2 and T4 redone per the designer's B-107 rulings (DECISIONS 2026-11-16 "transitions v5
rulings", items 5 and 6). v5 stays untouched; v6 started as a byte copy of v5. Writes t02 / t04 strips, sheet.jpg,
flow.jpg, v5_vs_v6.jpg and the netrun-street plates into transitions/v6/. PIL + numpy only (no Godot, no Blender).

The netrun street is the golden plates' paradigm: golden plate hq_rebel_cell_decision (high oblique, square-on to one straight street, underground tiers in section) from the
street camera, each room building cut away with its front wall hidden and the 3D room inside drawn from THAT camera
(one-point perspective on the street camera's eye), nodes joined by lines. T2 only moves the camera; the room is the
same drawing in every frame. Run: python build6.py   (from anywhere)"""
import os, sys, math, random, textwrap, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

R = 'D:/rc_art/art-pass/docs/concepts/'
OUT = R + 'transitions/v6/'
V5 = R + 'transitions/v5/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
W, H = 1920, 1080
Z = 2                     # world supersample
LIME = (212, 255, 0); PINK = (255, 62, 160); AMB = (255, 170, 60); CYAN = (92, 225, 255); WHITE = (240, 242, 248)
TEAL = (60, 230, 190); RED = (232, 30, 40); ORANGE = (255, 150, 40)
KIND = {'router': (56, 158, 255), 'terminal': (77, 242, 128), 'mainframe': (102, 115, 255), 'server_rack': (255, 148, 51),
        'elite': (255, 89, 31), 'safe': LIME}


def AF(s): return ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
def MF(s): return ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', s)
def PF(s): return ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', s)
def HF(s): return ImageFont.truetype(FD + 'PermanentMarker-Regular.ttf', s)
def JF(s): return ImageFont.truetype('C:/Windows/Fonts/YuGothB.ttc', s)
def F(s, b=False): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf', s)


def L(rel):
    p = rel if ':' in rel else R + rel
    return Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS)


def add(im, layer, k=1.0):
    a = np.asarray(im).astype(np.float32); b = np.asarray(layer).astype(np.float32)
    return Image.fromarray(np.clip(a + b * k, 0, 255).astype('uint8'))


def ell(cx, cy, rx, ry): return (cx - rx, cy - ry, cx + rx, cy + ry)


# ================================================================ the street (world, at Z)
STREET_SRC = R + 'golden_plates/hq_rebel_cell_decision.png'   # art lead: THE netrun frame (high oblique, square-on, one street)
VP = (980, 120)           # the high oblique camera's eye above the street (rooms are seen from above: floor visible)
DEPTH = 0.80              # back wall scale (shallow: rooms off the eye keep their props inside the cut)

ROOMS = {   # id: (the golden plate's own lit cut-away room box, 1920 coords, kind, state)
    'r0': ((749, 586, 840, 629), 'safe', 'walked'),          # street-level frontage rooms
    'r1': ((1042, 586, 1133, 629), 'router', 'walked'),
    'r2': ((1037, 768, 1133, 830), 'router', 'next'),        # the chosen room: first underground tier, in section
    'r3': ((1334, 768, 1435, 830), 'terminal', 'next'),
    'r4': ((1133, 850, 1224, 898), 'elite', 'ahead'),        # second tier
    'r5': ((1646, 768, 1747, 830), 'server_rack', 'ahead'),
    'r6': ((1133, 264, 1238, 322), 'router', 'ahead'),       # rooftop rooms
    'r7': ((1334, 365, 1440, 427), 'terminal', 'ahead'),
}
LINKS = [('r0', 'r1', 'walked'), ('r1', 'r2', 'next'), ('r1', 'r3', 'next'), ('r2', 'r4', 'ahead'), ('r3', 'r5', 'ahead'),
         ('r1', 'r6', 'ahead'), ('r6', 'r7', 'ahead')]
GSIGNS = [  # the golden plate's generic boards -> Solace-district words (B-107)
    ((1150, 180, 1279, 246), 'SOLACE CARE+', 'breathe easier.', (61, 255, 139), 'helix'),   # was ORBITAL
    ((907, 206, 1013, 259), 'SPORE', 'ramen bar', (255, 90, 190), 'bowl'),
    ((250, 219, 360, 269), 'GENE CLINIC', 'walk-in', (120, 230, 255), 'cross'),
    ((158, 259, 216, 278), 'MOSS', '', (110, 255, 160), 'leaf'),                             # was HOTEL
    ((1323, 512, 1450, 530), 'HYDRO', '', (255, 196, 80), 'drop'),                          # was HOTEL
    ((1630, 528, 1759, 547), 'CLONE SPA', '', (90, 140, 255), 'drop'),                      # was KARAOKE
    ((1025, 528, 1142, 547), 'SEED BANK', '', (255, 90, 190), 'leaf'),                      # was HOTEL
    ((14, 540, 79, 557), 'PHARMA', '', (255, 90, 190), 'cross'),                            # was HOTEL
]


def golden_signs(im, mainframe=False):
    d = ImageDraw.Draw(im)
    for bx, word, sub, col, ic in GSIGNS:
        if sub:
            im, d = sign(d, im, bx, word, sub, col, ic)
        else:                                            # thin band signs: a neon word on a dark band
            x0, y0, x1, y1 = [v * Z for v in bx]
            d.rectangle((x0, y0, x1, y1), fill=(20, 8, 26))
            g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
            fs = int(min((y1 - y0) * .95, (x1 - x0) / max(4, len(word)) * 1.7))
            gd.text(((x0 + x1) / 2, (y0 + y1) / 2), word, font=AF(fs), fill=col, anchor='mm')
            im = add(im, g.filter(ImageFilter.GaussianBlur(4 * Z)), 1.0); d = ImageDraw.Draw(im)
            d.text(((x0 + x1) / 2, (y0 + y1) / 2), word, font=AF(fs), fill=tuple(min(255, int(c * .4 + 160)) for c in col), anchor='mm')
    if mainframe:   # the real MAINFRAME shop: Rebel Cell territory only; red board over the chosen room's street + blade
        g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
        X0, Y0, X1, Y1 = [v * Z for v in (1025, 724, 1145, 760)]
        d = ImageDraw.Draw(im); d.rectangle((X0, Y0, X1, Y1), fill=(40, 6, 12))
        gd.rectangle((X0, Y0, X1, Y1), outline=(255, 40, 50), width=3 * Z)
        gd.text(((X0 + X1) / 2, (Y0 + Y1) / 2), 'MAINFRAME', font=AF(int((Y1 - Y0) * .7)), fill=(255, 50, 60), anchor='mm')
        im = add(im, g.filter(ImageFilter.GaussianBlur(5 * Z)), 1.0)
        d = ImageDraw.Draw(im)
        d.text(((X0 + X1) / 2, (Y0 + Y1) / 2), 'MAINFRAME', font=AF(int((Y1 - Y0) * .7)), fill=(255, 220, 220), anchor='mm')
        im = vertical_sign(im, 1150, 700, 840, 'MAINFRAME', (255, 50, 60))
    return im


def close_all(base):
    """every room with its front on: above ground a facade with a window grid, underground a concrete section wall"""
    im = base.copy(); d = ImageDraw.Draw(im)
    rng = random.Random(5)
    for rid, (box, _, _) in ROOMS.items():
        x0, y0, x1, y1 = [v * Z for v in box]
        under = box[1] > 700
        d.rectangle((x0 - Z, y0 - Z, x1 + Z, y1 + Z), fill=(34, 30, 34) if under else (30, 24, 36))
        if under:
            for yy in range(int(y0), int(y1), 7 * Z):
                d.line((x0, yy, x1, yy), fill=(44, 40, 44), width=Z)
        else:
            for yy in range(int(y0 + 5 * Z), int(y1 - 4 * Z), 9 * Z):
                for xx in range(int(x0 + 4 * Z), int(x1 - 4 * Z), 9 * Z):
                    on = rng.random() < .45
                    d.rectangle((xx, yy, xx + 4 * Z, yy + 4 * Z), fill=(250, 214, 150) if on else (52, 44, 56))
    return im
SHOP = [  # run8 shop light boxes (x0, x1) on the sign band y 752-795 -> Solace-district words (B-107)
    ((0, 55), 'MYCO'), ((68, 140), 'CARE+'), ((207, 268), 'BIO-TEA'), ((290, 370), 'MOSS&MILK'), ((432, 492), 'SPORE'),
    ((500, 578), 'GENE CLINIC'), ((603, 668), 'HYDRO'), ((673, 745), 'KELP BAR'), ((757, 815), 'DRIP'), ((881, 945), 'SEED BANK'),
    ((955, 1040), 'SOLACE RX'), ((1105, 1170), 'CLONE SPA'), ((1180, 1263), 'GROW+'), ((1330, 1390), 'PHARMA'), ((1400, 1490), 'MOSS&MILK'),
    ((1552, 1615), 'SPORE'), ((1627, 1712), 'GENE CLINIC'), ((1778, 1858), 'HYDRO'), ((1868, 1920), 'MYCO')]
BLADES = [(297, 603, 700, 'CLINIC'), (683, 603, 700, 'SPORE'), (1427, 615, 695, 'CARE+'), (1652, 575, 650, 'HYDRO')]


def shop_signs(im, mainframe=False, z=Z):
    """repaint the run8 light boxes with Solace words: keep each box's own colour, dark mono lettering"""
    d = ImageDraw.Draw(im)
    for (x0, x1), word in SHOP:
        if mainframe and x0 in (881, 955):
            continue
        X0, X1, Y0, Y1 = x0 * z + 2 * z, x1 * z - 2 * z, 754 * z, 794 * z
        if X1 - X0 < 20:
            continue
        reg = np.asarray(im.crop((int(X0), int(Y0), int(X1), int(Y1)))).reshape(-1, 3)
        col = tuple(int(v) for v in np.percentile(reg, 75, axis=0))
        d.rectangle((X0, Y0, X1, Y1), fill=col)
        fs = int(min(26 * z, (X1 - X0) / max(4, len(word)) * 1.55))
        d.text(((X0 + X1) / 2, (Y0 + Y1) / 2), word, font=MF(fs), fill=(30, 20, 60), anchor='mm')
    for x, y0, y1, word in BLADES:
        im = vertical_sign(im, x - 6, y0, y1, word, (120, 230, 255) if word != 'SPORE' else (255, 90, 190))
    if mainframe:   # the real MAINFRAME shop (Rebel Cell territory only): red light box + blade, as on the hq_rebel_cell plate
        g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
        X0, Y0, X1, Y1 = [v * z for v in (881, 748, 1040, 798)]
        d = ImageDraw.Draw(im); d.rectangle((X0, Y0, X1, Y1), fill=(40, 6, 12))
        gd.rectangle((X0, Y0, X1, Y1), outline=(255, 40, 50), width=4 * z)
        gd.text(((X0 + X1) / 2, (Y0 + Y1) / 2), 'MAINFRAME', font=AF(int((Y1 - Y0) * .7)), fill=(255, 50, 60), anchor='mm')
        im = add(im, g.filter(ImageFilter.GaussianBlur(6 * z)), 1.0)
        d = ImageDraw.Draw(im)
        d.rectangle((X0, Y0, X1, Y1), outline=(255, 140, 140), width=2 * z)
        d.text(((X0 + X1) / 2, (Y0 + Y1) / 2), 'MAINFRAME', font=AF(int((Y1 - Y0) * .7)), fill=(255, 220, 220), anchor='mm')
        im = vertical_sign(im, 1046, 520, 745, 'MAINFRAME', (255, 50, 60))
    return im
SIGNS = [  # strip_05 board boxes -> Solace-district words (B-107: no generic LEAFLET / ORBITAL / CHLORO / HOTEL)
    ((872, 446, 1128, 638), 'MOSS & MILK', 'bubble tea . open late', (110, 255, 160), 'leaf'),
    ((1156, 442, 1408, 638), 'GENE CLINIC', 'walk-in . insured', (120, 230, 255), 'cross'),
    ((1452, 446, 1610, 634), 'SPORE', 'ramen bar', (255, 90, 190), 'bowl'),
    ((1628, 450, 1816, 632), 'HYDRO', 'grow supply', (255, 196, 80), 'drop'),
    ((-6, 514, 366, 822), 'SOLACE CARE+', 'breathe easier.', (61, 255, 139), 'helix'),
]


def sign(d, im, box, word, sub, col, icon, z=Z):
    x0, y0, x1, y1 = [v * z for v in box]
    d.rectangle((x0, y0, x1, y1), fill=(14, 10, 24))
    d.rectangle((x0 + 6 * z, y0 + 6 * z, x1 - 6 * z, y1 - 6 * z), outline=col, width=3 * z)
    w = x1 - x0; h = y1 - y0
    # glow layer
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    f = AF(int(min(h * .34, w / max(4, len(word)) * 1.55)))
    tx = (x0 + x1) / 2; ty = y0 + h * .42
    gd.text((tx, ty), word, font=f, fill=col, anchor='mm')
    gd.rectangle((x0 + 6 * z, y0 + 6 * z, x1 - 6 * z, y1 - 6 * z), outline=col, width=6 * z)
    g = g.filter(ImageFilter.GaussianBlur(9 * z))
    im2 = add(im, g, .9); d2 = ImageDraw.Draw(im2)
    d2.text((tx, ty), word, font=f, fill=tuple(min(255, int(c * .35 + 170)) for c in col), anchor='mm')
    d2.text((tx, y0 + h * .74), sub, font=MF(int(h * .1)), fill=col, anchor='mm')
    ix, iy, r = x0 + w * .12, y0 + h * .2, h * .08
    if icon == 'cross':
        d2.rectangle((ix - r * .35, iy - r, ix + r * .35, iy + r), fill=col); d2.rectangle((ix - r, iy - r * .35, ix + r, iy + r * .35), fill=col)
    elif icon == 'leaf':
        d2.ellipse((ix - r, iy - r * .5, ix + r, iy + r * .5), outline=col, width=3 * z); d2.line((ix - r, iy, ix + r, iy), fill=col, width=2 * z)
    elif icon == 'bowl':
        d2.chord((ix - r, iy - r, ix + r, iy + r), 0, 180, fill=col); d2.line((ix - r * .4, iy - r * 1.4, ix - r * .2, iy - r * .2), fill=col, width=2 * z)
    elif icon == 'drop':
        d2.polygon([(ix, iy - r * 1.2), (ix + r * .7, iy + r * .2), (ix, iy + r * .8), (ix - r * .7, iy + r * .2)], fill=col)
    elif icon == 'helix':
        for k in range(14):
            yy = y0 + h * .12 + k * h * .045
            a = k * .7
            d2.line((x1 - w * .12 + math.sin(a) * w * .05, yy, x1 - w * .12 - math.sin(a) * w * .05, yy), fill=col, width=2 * z)
    return im2, ImageDraw.Draw(im2)


def vertical_sign(im, x, y0, y1, word, col, jp=None, z=Z):
    d = ImageDraw.Draw(im)
    w = 34 * z
    d.rectangle((x * z, y0 * z, x * z + w, y1 * z), fill=(14, 10, 24), outline=col, width=2 * z)
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    n = len(word); step = (y1 - y0) * z / (n + .5)
    for i, ch in enumerate(word):
        gd.text((x * z + w / 2, y0 * z + step * (i + .75)), ch, font=JF(int(step * .8)) if jp else AF(int(step * .8)), fill=col, anchor='mm')
    im2 = add(im, g.filter(ImageFilter.GaussianBlur(6 * z)), 1.0)
    d2 = ImageDraw.Draw(im2)
    for i, ch in enumerate(word):
        d2.text((x * z + w / 2, y0 * z + step * (i + .75)), ch, font=JF(int(step * .8)) if jp else AF(int(step * .8)), fill=(255, 255, 255), anchor='mm')
    return im2


class Room:
    """One cut-away room on the street, drawn from the street camera (one-point perspective on VP)."""

    def __init__(self, box, z=Z):
        self.x0, self.y0, self.x1, self.y1 = [v * z for v in box]
        self.vx, self.vy = VP[0] * z, VP[1] * z
        self.k = 1 / DEPTH - 1
        self.ex = (self.vx - self.x0) / (self.x1 - self.x0)
        self.ey = (self.y1 - self.vy) / (self.y1 - self.y0)

    def p(self, x, y, zz):
        fx = self.x0 + x * (self.x1 - self.x0); fy = self.y1 - y * (self.y1 - self.y0)
        s = 1 / (1 + self.k * zz)
        return (self.vx + (fx - self.vx) * s, self.vy + (fy - self.vy) * s)

    def quad(self, d, pts, fill, outline=None, w=1):
        d.polygon([self.p(*q) for q in pts], fill=fill)
        if outline:
            q = [self.p(*q) for q in pts]
            d.line(q + [q[0]], fill=outline, width=w)

    def box(self, d, x0, x1, y0, y1, z0, z1, col, edge=(6, 8, 12), light=1.0):
        c = tuple(int(v * light) for v in col)
        top = tuple(min(255, int(v * 1.35)) for v in c); side = tuple(int(v * .62) for v in c)
        if self.ex > x1:
            self.quad(d, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side, edge, 2)
        if self.ex < x0:
            self.quad(d, [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], side, edge, 2)
        if self.ey > y1:
            self.quad(d, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top, edge, 2)
        if self.ey < y0:
            self.quad(d, [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], side, edge, 2)
        self.quad(d, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], c, edge, 2)

    def face_leds(self, d, x0, x1, y0, y1, zz, rng, cols):
        n = int((y1 - y0) / .06)
        for i in range(1, n):
            y = y0 + i * (y1 - y0) / n
            a = self.p(x0 + (x1 - x0) * .15, y, zz); b = self.p(x0 + (x1 - x0) * rng.uniform(.4, .85), y, zz)
            d.line((a, b), fill=rng.choice(cols), width=2 * Z)


def draw_room(im, rid, kind, lit, z=Z, seed=0, mainframe=False):
    """Paint the room interior into im (world). lit: the room's light colour (corp teal-white, or our lime)."""
    box, _, _ = ROOMS[rid]
    rm = Room(box, z)
    orig = im.copy()
    d = ImageDraw.Draw(im)
    acc = KIND[kind] if kind != 'safe' else LIME
    rng = random.Random(seed + hash(rid) % 997)
    wall = tuple(int(v * .30 + 24) for v in lit); flo = tuple(int(v * .20 + 18) for v in lit); cei = tuple(int(v * .12 + 12) for v in lit)
    sidew = tuple(int(v * .24 + 18) for v in lit)
    rm.quad(d, [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], wall)                 # back wall
    rm.quad(d, [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], flo)                 # floor
    rm.quad(d, [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], cei)                 # ceiling
    rm.quad(d, [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)], sidew)               # left
    rm.quad(d, [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)], sidew)               # right
    for k in range(1, 6):                                                          # floor tiles
        d.line((rm.p(k / 6, 0, 0), rm.p(k / 6, 0, 1)), fill=tuple(int(v * .3 + 20) for v in lit), width=z)
        d.line((rm.p(0, 0, k / 6), rm.p(1, 0, k / 6)), fill=tuple(int(v * .3 + 20) for v in lit), width=z)
    for k in range(1, 5):                                                          # back wall panels
        d.line((rm.p(k / 5, 0, 1), rm.p(k / 5, 1, 1)), fill=tuple(int(v * .12 + 12) for v in lit), width=z)
    d.line((rm.p(0, .92, 1), rm.p(1, .92, 1)), fill=acc, width=2 * z)               # neon trim in the kind colour
    d.line((rm.p(0, .92, 0), rm.p(0, .92, 1)), fill=acc, width=2 * z); d.line((rm.p(1, .92, 0), rm.p(1, .92, 1)), fill=acc, width=2 * z)
    # ceiling light bars
    for zz in (.25, .6):
        d.line((rm.p(.3, .99, zz), rm.p(.7, .99, zz)), fill=tuple(min(255, int(v * .6 + 100)) for v in lit), width=3 * z)
    led = [acc, (240, 245, 255), CYAN, PINK, (40, 60, 70)]
    if kind in ('router', 'elite'):
        for i in range(4):                                                         # racks on the back wall
            x0 = .06 + i * .23
            rm.box(d, x0, x0 + .17, 0, .78, .78, .96, (36, 44, 58))
            rm.face_leds(d, x0, x0 + .17, .05, .74, .78, rng, led)
        big = kind == 'elite'
        rm.box(d, .32, .68, 0, .28, .38, .58, (52, 58, 72))                       # bench
        rm.box(d, .38, .62, .28, .44 if big else .38, .42, .54, (30, 34, 44))      # the router unit
        rm.face_leds(d, .38, .62, .3, .42 if big else .36, .42, rng, [acc, acc, WHITE])
        for ax in (.42, .58):
            d.line((rm.p(ax, .44 if big else .38, .48), rm.p(ax - .03, .62, .48)), fill=(180, 190, 200), width=2 * z)
        # cable tray + drops
        d.line((rm.p(.1, .86, .3), rm.p(.9, .86, .3)), fill=(20, 24, 30), width=6 * z)
        for x in (.2, .5, .8):
            d.line((rm.p(x, .86, .3), rm.p(x, .78, .78)), fill=(14, 16, 20), width=2 * z)
        if big:
            d.ellipse(ell(*rm.p(.5, .18, .3), 30 * z, 9 * z), outline=RED, width=2 * z)
    elif kind == 'terminal':
        rm.box(d, .05, .2, 0, .58, .55, .95, (66, 70, 60))                          # filing cabinets
        rm.box(d, .2, .33, 0, .58, .6, .95, (60, 64, 56))
        rm.box(d, .36, .9, 0, .27, .45, .7, (70, 60, 46))                           # desk
        for i, x in enumerate((.42, .57, .72)):                                     # monitors
            rm.box(d, x, x + .13, .27, .5, .5, .62, (24, 26, 30))
            rm.quad(d, [(x + .015, .3, .5), (x + .115, .3, .5), (x + .115, .47, .5), (x + .015, .47, .5)], acc if i != 1 else CYAN)
        rm.box(d, .55, .7, 0, .3, .22, .35, (30, 30, 36))                           # chair
        rm.quad(d, [(.4, .55, 1), (.75, .55, 1), (.75, .82, 1), (.4, .82, 1)], (150, 120, 80))   # pinboard
        for k in range(6):
            x = .43 + (k % 3) * .1; y = .6 + (k // 3) * .1
            rm.quad(d, [(x, y, 1), (x + .07, y, 1), (x + .07, y + .07, 1), (x, y + .07, 1)], (240, 236, 220))
    elif kind == 'server_rack':
        for row, zz in enumerate((.2, .45, .7)):
            for side in (0, 1):
                x0 = .05 if side == 0 else .62
                rm.box(d, x0, x0 + .33, 0, .8, zz, zz + .16, (34, 40, 54))
                rm.face_leds(d, x0, x0 + .33, .05, .76, zz, rng, led)
        d.line((rm.p(.5, 0, .1), rm.p(.5, 0, .95)), fill=acc, width=2 * z)
    elif kind == 'safe':
        rm.box(d, .08, .5, 0, .2, .55, .8, (90, 70, 60))                            # couch
        rm.box(d, .08, .5, .2, .4, .78, .82, (100, 80, 66))
        rm.box(d, .6, .82, 0, .2, .35, .5, (70, 66, 60))                            # table
        rm.box(d, .66, .7, .2, .34, .4, .44, (40, 40, 40))
        rm.box(d, .7, .95, 0, .25, .8, .95, (110, 90, 50)); rm.box(d, .72, .9, .25, .42, .82, .93, (120, 98, 56))   # crates
        d.ellipse(ell(*rm.p(.68, .36, .42), 6 * z, 6 * z), fill=(255, 230, 150))
    elif kind == 'mainframe':
        for i in range(3):                                                         # shelves with stock
            rm.box(d, .05, .95, i * .26, i * .26 + .03, .82, .97, (60, 52, 70))
            for k in range(7):
                x = .08 + k * .12
                rm.box(d, x, x + .08, i * .26 + .03, i * .26 + .03 + rng.uniform(.08, .16), .85, .94,
                       rng.choice([(200, 60, 60), (60, 160, 220), (230, 200, 70), (180, 180, 190), (120, 90, 200)]))
        rm.box(d, .15, .85, 0, .3, .1, .26, (52, 40, 60))                           # counter
        rm.box(d, .6, .76, .3, .42, .14, .22, (20, 20, 26))                         # till
        rm.quad(d, [(.62, .32, .14), (.74, .32, .14), (.74, .4, .14), (.62, .4, .14)], (255, 60, 80))
        for x in (.3, .7):
            d.line((rm.p(x, 1, .5), rm.p(x, .82, .5)), fill=(30, 30, 30), width=z)
            d.ellipse(ell(*rm.p(x, .8, .5), 9 * z, 5 * z), fill=(255, 210, 160))
    # light: a soft pool of the room light
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    cx, cy = rm.p(.5, .45, .55)
    gd.ellipse(ell(cx, cy, (rm.x1 - rm.x0) * .42, (rm.y1 - rm.y0) * .38), fill=tuple(int(v * .45) for v in lit))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rectangle((rm.x0, rm.y0, rm.x1, rm.y1), fill=255)
    g = Image.composite(g.filter(ImageFilter.GaussianBlur(26 * z)), Image.new('RGB', im.size, (0, 0, 0)), m)
    im = add(im, g, .8)
    d = ImageDraw.Draw(im)
    # seen through the cut only: the interior is clipped to the opening (the side walls beyond it are the building's)
    cm = Image.new("L", im.size, 0); ImageDraw.Draw(cm).rectangle((rm.x0, rm.y0, rm.x1, rm.y1), fill=255)
    im = Image.composite(im, orig, cm); d = ImageDraw.Draw(im)
    # the cut: slab section under the floor (hatched) and the lit rim on the cut edges (golden plates: lit cut edge)
    sl = 10 * z
    d.rectangle((rm.x0 - 3 * z, rm.y1, rm.x1 + 3 * z, rm.y1 + sl), fill=(20, 18, 26))
    for x in range(int(rm.x0), int(rm.x1), 8 * z):
        d.line((x, rm.y1 + sl, x + 8 * z, rm.y1), fill=tuple(int(v * .5) for v in lit), width=z)
    d.rectangle((rm.x0 - 3 * z, rm.y0 - 3 * z, rm.x1 + 3 * z, rm.y1 + sl), outline=tuple(min(255, int(v * .7 + 70)) for v in lit), width=3 * z)
    return im


def room_mask(rid, z=Z, pad=4):
    box, _, _ = ROOMS[rid]
    x0, y0, x1, y1 = [v * z for v in box]
    m = Image.new('L', (W * z, H * z), 0)
    ImageDraw.Draw(m).rectangle((x0 - pad * z, y0 - pad * z, x1 + pad * z, y1 + 14 * z), fill=255)
    return m


def node_pos(rid):
    box = ROOMS[rid][0]
    return ((box[0] + box[2]) / 2, box[1] - 26 if box[1] > 120 else box[3] + 26)


def build_world(open_rooms, won=(), lost=(), mainframe=False, kinds=None, signs=True, links=True, link_a=1.0, flick=None):
    """The netrun street at Z. open_rooms: rooms with the front wall hidden. won: rooms in our colour.
    kinds: override of room kinds (for the per-kind combat frames)."""
    base = Image.open(STREET_SRC).convert('RGB').resize((W * Z, H * Z), Image.LANCZOS)
    if signs:
        base = golden_signs(base, mainframe)
    walls_signed = close_all(base)            # every room with its front wall on (facade / section wall)
    im = walls_signed.copy()
    kinds = kinds or {}
    for rid in open_rooms:
        box, kind, st = ROOMS[rid]
        x0, y0, x1, y1 = [int(v * Z) for v in box]
        ours = rid in won or st == 'walked' or (flick and rid in flick)
        if rid in kinds or (mainframe and rid == 'r2'):   # a kind variant: its own props drawn in the golden room's box
            kind = 'mainframe' if (mainframe and rid == 'r2') else kinds[rid]
            im = draw_room(im, rid, kind, LIME if ours else (150, 255, 225))
        else:                                             # the golden plate's own lit 3D room, as rendered
            im.paste(base.crop((x0, y0, x1, y1)), (x0, y0))
        if ours:
            reg = np.asarray(im.crop((x0, y0, x1, y1))).astype(np.float32)
            lum = reg.mean(2, keepdims=True) / 255
            tgt = np.array(LIME, np.float32)[None, None] * (.25 + lum * 1.0)
            im.paste(Image.fromarray(np.clip(reg * .35 + tgt * .65, 0, 255).astype('uint8')), (x0, y0))
        dd = ImageDraw.Draw(im)
        dd.rectangle((x0 - 2 * Z, y0 - 2 * Z, x1 + 2 * Z, y1 + 2 * Z), outline=LIME if ours else (200, 255, 235), width=2 * Z)
    d = ImageDraw.Draw(im, 'RGBA')
    if links and link_a > 0:
        for a, b, st in LINKS:
            pa, pb = node_pos(a), node_pos(b)
            col = {'walked': LIME, 'next': ORANGE, 'ahead': WHITE}[st]
            if a in won and st == 'next':
                col = LIME
            pts = [(pa[0] * Z, pa[1] * Z), ((pa[0] + pb[0]) / 2 * Z, min(pa[1], pb[1]) * Z - 20 * Z), (pb[0] * Z, pb[1] * Z)]
            al = int(255 * link_a)
            if st == 'ahead':
                for t0 in np.arange(0, 1, .08):
                    q0 = bez(pts, t0); q1 = bez(pts, t0 + .045)
                    d.line((q0, q1), fill=col + (int(al * .8),), width=3 * Z)
            else:
                d.line([bez(pts, t) for t in np.linspace(0, 1, 30)], fill=col + (al,), width=5 * Z, joint='curve')
        for rid, (box, kind, st) in ROOMS.items():
            x, y = node_pos(rid)
            c = KIND[kinds.get(rid, kind)] if rid not in won and st != 'walked' else LIME
            ring = {'walked': LIME, 'next': ORANGE, 'ahead': (200, 200, 210)}[st]
            if rid in won:
                ring = LIME
            if rid in lost:
                ring = RED
            r = 15
            d.ellipse(ell(x * Z, y * Z, (r + 6) * Z, (r + 6) * Z), fill=(10, 10, 16, int(255 * link_a)), outline=ring + (int(255 * link_a),), width=4 * Z)
            d.ellipse(ell(x * Z, y * Z, r * .55 * Z, r * .55 * Z), fill=c + (int(255 * link_a),))
            if st == 'walked' or rid in won:
                d.line(((x - 7) * Z, y * Z, (x - 2) * Z, (y + 6) * Z, (x + 8) * Z, (y - 7) * Z), fill=(10, 10, 16, 255), width=3 * Z)
    return im, walls_signed


def bez(p, t):
    t = min(1, max(0, t))
    return ((1 - t) ** 2 * p[0][0] + 2 * (1 - t) * t * p[1][0] + t * t * p[2][0], (1 - t) ** 2 * p[0][1] + 2 * (1 - t) * t * p[1][1] + t * t * p[2][1])


def close_walls(world, walls, rids, k, seed=1):
    """Rooms closing (k 0 open .. 1 closed): the wall slides down top to bottom with a 0/1 bit edge."""
    im = world.copy(); d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    for i, rid in enumerate(rids):
        kk = min(1, max(0, k * 1.4 - i * .08))
        if kk <= 0:
            continue
        box = ROOMS[rid][0]
        x0, y0, x1, y1 = [v * Z for v in box]
        yb = y0 + (y1 + 14 * Z - y0) * kk
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rectangle((x0 - 4 * Z, y0 - 4 * Z, x1 + 4 * Z, yb), fill=255)
        im = Image.composite(walls, im, m); d = ImageDraw.Draw(im)
        if kk < 1:
            for x in range(int(x0), int(x1), 9 * Z):
                d.text((x, yb - 8 * Z + rng.uniform(-4, 4) * Z), rng.choice('01'), font=MF(13 * Z), fill=rng.choice([LIME, WHITE, CYAN]))
    return im


def open_walls(world_open, world_closed_im, rids, k, seed=2):
    """Walls dissolving to bits (k 0 closed .. 1 open)."""
    im = world_closed_im.copy()
    rng = random.Random(seed)
    for rid in rids:
        box = ROOMS[rid][0]
        x0, y0, x1, y1 = [v * Z for v in box]
        m = Image.new('L', im.size, 0); md = ImageDraw.Draw(m)
        for x in range(int(x0), int(x1), 8 * Z):
            for y in range(int(y0), int(y1 + 14 * Z), 8 * Z):
                if rng.random() < k:
                    md.rectangle((x, y, x + 8 * Z, y + 8 * Z), fill=255)
        im = Image.composite(world_open, im, m)
        d = ImageDraw.Draw(im)
        if 0 < k < 1:
            for _ in range(int(60 * (1 - abs(k - .5) * 2) + 10)):
                d.text((rng.uniform(x0, x1), rng.uniform(y0, y1)), rng.choice('01'), font=MF(14 * Z), fill=rng.choice([LIME, WHITE, CYAN]))
    return im


# ================================================================ camera (moves only; the room never changes)
STREET = dict(cx=960, cy=540, zoom=1.0, roll=0.0, tilt=0.0)
COMBAT = dict(cx=1085, cy=800, zoom=4.2, roll=-2.5, tilt=.05)


def lerp_cam(a, b, t):
    return {k: a[k] + (b[k] - a[k]) * t for k in a}


def ease_io(t): return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def cam(world, c):
    """Frame the world: centre, zoom, roll (deg), tilt (keystone, a pitch stand-in). Output 1920 x 1080."""
    cx, cy, zm, roll, tilt = c['cx'] * Z, c['cy'] * Z, c['zoom'], math.radians(c['roll']), c['tilt']
    hw, hh = W * Z / 2 / zm, H * Z / 2 / zm
    corners = [(-hw * (1 - tilt), -hh), (-hw * (1 + tilt), hh), (hw * (1 + tilt), hh), (hw * (1 - tilt), -hh)]
    q = []
    for x, y in corners:
        q += [cx + x * math.cos(roll) - y * math.sin(roll), cy + x * math.sin(roll) + y * math.cos(roll)]
    return world.transform((W, H), Image.QUAD, q, resample=Image.BICUBIC)


def world_to_screen(c, x, y):
    """Where a world point (1920 coords) lands on screen for camera c (inverse of cam, ignoring tilt)."""
    dx, dy = (x - c['cx']) * c['zoom'], (y - c['cy']) * c['zoom']
    r = -math.radians(c['roll'])
    return (W / 2 + dx * math.cos(r) - dy * math.sin(r), H / 2 + dx * math.sin(r) + dy * math.cos(r))


# ================================================================ HUD bits
def street_hud(im, a=1.0):
    d = ImageDraw.Draw(im, 'RGBA')
    al = int(230 * a)
    d.rectangle((24, 20, 760, 92), fill=(8, 12, 24, al), outline=CYAN + (al,), width=2)
    d.text((40, 30), 'NETRUN', font=AF(36), fill=PINK + (al,))
    d.text((170, 34), 'SEED VAULT EXCHANGE . Glasshouse Row', font=PF(26), fill=WHITE + (al,))
    d.text((40, 70), 'RHEE  run health 24/30  .  layer 2 of 6', font=MF(16), fill=(170, 180, 200, al))
    x = 520
    d.rectangle((480, 1020, 1440, 1062), fill=(8, 12, 24, al), outline=CYAN + (al,), width=2)
    for k, (lab, col) in enumerate((('ROUTER', KIND['router']), ('ELITE', KIND['elite']), ('TERMINAL', KIND['terminal']),
                                   ('RACK', KIND['server_rack']), ('walked', LIME), ('next', ORANGE), ('ahead', WHITE))):
        d.ellipse((x - 8, 1033, x + 8, 1049), fill=col + (al,))
        d.text((x + 14, 1028), lab, font=MF(18), fill=(220, 225, 235, al))
        x += 130
    return im


def pick_pad(im, c, rid='r2'):
    box = ROOMS[rid][0]
    p0 = world_to_screen(c, box[0], box[1]); p1 = world_to_screen(c, box[2], box[3] + 10)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6), outline=PINK + (255,), width=4)
    d.rectangle((p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6), fill=PINK + (40,))
    return im


def pulse(im, c, a='r1', b='r2', t=.6):
    pa, pb = node_pos(a), node_pos(b)
    pts = [pa, ((pa[0] + pb[0]) / 2, min(pa[1], pb[1]) - 20), pb]
    d = ImageDraw.Draw(im)
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    for k in range(10):
        tt = t - k * .03
        if tt < 0:
            continue
        x, y = world_to_screen(c, *bez(pts, tt))
        gd.ellipse(ell(x, y, 16 - k, 16 - k), fill=(255, 255, 255) if k == 0 else ORANGE)
    return add(im, g.filter(ImageFilter.GaussianBlur(3)), 1.0)


# ---- the board pieces cut from the approved v3 plates (wheel only, HUD panels separately)
def wheel_layer(src, r=452, cx=960, cy=546):
    im = L(src).convert('RGBA')
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(ell(cx, cy, r, r), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.5))
    im.putalpha(m)
    return im


def hud_layer(src, boxes):
    im = L(src).convert('RGBA')
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    for b in boxes:
        md.rectangle(b, fill=255)
    im.putalpha(m)
    return im


WIN_HUD = [(22, 18, 515, 105), (18, 105, 305, 160), (575, 14, 905, 110), (1400, 14, 1904, 604), (1400, 615, 1904, 845), (1640, 870, 1904, 990), (18, 815, 522, 880)]
BOARD_HUD = [(0, 0, 560, 200), (1100, 0, 1920, 1080), (0, 760, 560, 1080)]


def over(base, lay, a=1.0):
    out = base.convert('RGBA')
    if a < 1:
        lay = lay.copy(); al = np.asarray(lay.split()[3]).astype(np.float32) * a
        lay.putalpha(Image.fromarray(al.astype('uint8')))
    out.alpha_composite(lay)
    return out.convert('RGB')


def bits_from_disc(im, k, target, seed=4, cx=960, cy=546, r=452, n=900, cols=(LIME, PINK, (40, 205, 190))):
    """Wheel to bits: k 0..1 (0 = bits on the disc, 1 = bits arrived at target)."""
    out = im.copy(); d = ImageDraw.Draw(out)
    rng = random.Random(seed)
    f = MF(20)
    for i in range(n):
        a = rng.uniform(0, math.tau); rr = r * math.sqrt(rng.random())
        sx, sy = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        delay = rng.random() * .5
        t = min(1, max(0, (k - delay) / .5))
        t = t * t
        mx, my = (sx + target[0]) / 2 + rng.uniform(-120, 120), min(sy, target[1]) - rng.uniform(0, 160)
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * target[0] + rng.gauss(0, 6)
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * target[1] + rng.gauss(0, 6)
        if t >= 1 and rng.random() < .7:
            continue
        d.text((x, y), rng.choice('01'), font=f, fill=rng.choice(cols))
    return out


def bits_stream(im, src, dst, k, n=220, seed=6, cols=(LIME, WHITE, CYAN), size=18, spread=50):
    out = im.copy(); d = ImageDraw.Draw(out)
    rng = random.Random(seed)
    for i in range(n):
        t = (k - rng.random() * .6) / .4
        if t < 0 or t > 1:
            continue
        mx, my = (src[0] + dst[0]) / 2, min(src[1], dst[1]) - 180
        x = (1 - t) ** 2 * src[0] + 2 * (1 - t) * t * mx + t * t * dst[0] + rng.gauss(0, spread) * math.sin(math.pi * t)
        y = (1 - t) ** 2 * src[1] + 2 * (1 - t) * t * my + t * t * dst[1] + rng.gauss(0, spread) * math.sin(math.pi * t)
        d.text((x, y), rng.choice('01'), font=MF(size), fill=rng.choice(cols))
    return out


def tint_room(im, c, rid, col, k):
    box = ROOMS[rid][0]
    p0 = world_to_screen(c, box[0], box[1]); p1 = world_to_screen(c, box[2], box[3] + 10)
    x0, y0 = int(min(p0[0], p1[0])), int(min(p0[1], p1[1])); x1, y1 = int(max(p0[0], p1[0])), int(max(p0[1], p1[1]))
    reg = im.crop((x0, y0, x1, y1))
    a = np.asarray(reg).astype(np.float32)
    lum = a.mean(2, keepdims=True) / 255
    tgt = np.array(col, np.float32)[None, None, :] * (.35 + lum * 1.3)
    reg = Image.fromarray(np.clip(a * (1 - k) + tgt * k, 0, 255).astype('uint8'))
    out = im.copy(); out.paste(reg, (x0, y0))
    return out


def reward_panel(im, a=1.0, bits=0.0, seed=9):
    """Netrun reward (won): bits bloom from the room into a terminal-glass panel. bits: 0 solid .. 1 all bits."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 560, 250, 1360, 820
    d.rounded_rectangle((x0, y0, x1, y1), 14, fill=(8, 14, 28, 238), outline=LIME + (255,), width=3)
    d.text((x0 + 36, y0 + 26), 'SITE TAKEN', font=AF(64), fill=LIME)
    d.text((x0 + 36, y0 + 110), 'ROUTER cleared . layer 2 of 6 . the room is ours', font=PF(24), fill=(200, 206, 220))
    items = [('+6', 'credits', 'to the run purse (top left)', LIME), ('+1', 'program', 'BACKDOOR v1 to the deck', CYAN),
             ('24/30', 'run health', 'kept for the street', PINK)]
    for i, (big, lab, sub, col) in enumerate(items):
        yy = y0 + 170 + i * 110
        d.rounded_rectangle((x0 + 36, yy, x1 - 36, yy + 92), 10, fill=(18, 24, 40, 255), outline=col + (200,), width=2)
        d.text((x0 + 60, yy + 10), big, font=AF(54), fill=col)
        d.text((x0 + 260, yy + 14), lab, font=AF(32), fill=WHITE)
        d.text((x0 + 260, yy + 56), sub, font=PF(20), fill=(170, 176, 196))
    d.rounded_rectangle((x1 - 270, y1 - 82, x1 - 36, y1 - 24), 12, fill=WHITE, outline=(20, 10, 30), width=4)
    d.text((x1 - 153, y1 - 53), 'CONTINUE', font=AF(36), fill=PINK, anchor='mm')
    if bits > 0:
        arr = np.asarray(lay).copy()
        rng = np.random.default_rng(seed)
        cell = 10
        hh, ww = arr.shape[0] // cell, arr.shape[1] // cell
        keep = rng.random((hh, ww)) > bits
        mask = np.repeat(np.repeat(keep, cell, 0), cell, 1)
        mask = np.pad(mask, ((0, arr.shape[0] - mask.shape[0]), (0, arr.shape[1] - mask.shape[1])))
        arr[..., 3] = np.where(mask, arr[..., 3], 0)
        lay = Image.fromarray(arr, 'RGBA')
        d = ImageDraw.Draw(lay)
        r_ = random.Random(seed)
        for _ in range(int(1600 * bits * (1 - bits) + 80)):
            d.text((r_.uniform(x0, x1), r_.uniform(y0, y1)), r_.choice('01'), font=MF(18), fill=r_.choice([LIME, CYAN, WHITE]))
    return over(im, lay, a)


def badge_frame(im, label, col=AMB):
    return im


# ================================================================ T2
def t2():
    print('T2 worlds...')
    allr = list(ROOMS)
    W_open, W_walls = build_world(allr)
    W_ours, _ = build_world(['r2'], links=False)                 # combat view: only the chosen room open, the street dressed
    K = []
    k1 = street_hud(pick_pad(cam(W_open, STREET), STREET)); K.append(('K1  0.00 s  netrun street: rooms cut away, front walls hidden, links; pick pad on our next room', k1, 'n'))
    k2 = pulse(street_hud(cam(W_open, STREET), .7), STREET, t=.7); K.append(('K2  0.15 s  click: route pulse runs the link (0.4 s), node pop', k2, 'n'))
    others = [r for r in allr if r != 'r2']
    c3 = lerp_cam(STREET, COMBAT, ease_io(.3)); w3 = close_walls(W_open, W_walls, others, .5)
    K.append(('K3  0.40 s  camera starts toward the combat pose; other rooms get their walls back', cam(w3, c3), 'c'))
    c4 = lerp_cam(STREET, COMBAT, ease_io(.68)); w4 = close_walls(W_open, W_walls, others, 1.0)
    K.append(('K4  0.80 s  camera moving (pan, tilt, roll); ours the only open room', cam(w4, c4), 'c'))
    k5 = cam(W_ours, COMBAT); K.append(('K5  1.20 s  combat pose: the same room, the street, signs and FX stay', k5, 'n'))
    k6 = k5.copy(); d = ImageDraw.Draw(k6, 'RGBA')
    for a0 in range(0, 360, 6):
        d.arc(ell(960, 546, 452, 452), a0, a0 + 3, fill=(255, 255, 255, 160), width=4)
    d.text((960, 1000), 'T3 builds the wheel here (bits from the room)', font=PF(30), fill=WHITE, anchor='mm')
    K.append(('K6  1.20 s  hand-over to T3: where the wheel lands over the room', k6, 'c'))
    for lab, kind, mf in (('K7  1.20 s  TERMINAL (event) in the same pose', 'terminal', False),
                          ('K8  1.20 s  ELITE ROUTER in the same pose', 'elite', False),
                          ('K9  1.20 s  SERVER RACK in the same pose', 'server_rack', False),
                          ('K10 1.20 s  MAINFRAME shop: Rebel Cell territory only, its sign on the building', 'mainframe', True)):
        w_, _ = build_world(['r2'], kinds={'r2': kind}, mainframe=mf, links=False)
        K.append((lab, cam(w_, COMBAT), 'n'))
    W_open.resize((W, H), Image.LANCZOS).save(OUT + 'plates/netrun_street_open.png')
    W_ours.resize((W, H), Image.LANCZOS).save(OUT + 'plates/netrun_street_combat_world.png')
    k5.save(OUT + 'plates/t2_combat_pose.png')
    return K, W_open, W_walls, W_ours


# ================================================================ T4
def t4(W_open, W_walls, W_ours):
    print('T4 worlds...')
    allr = list(ROOMS)
    base = cam(W_ours, COMBAT)
    wheel_w = wheel_layer('takeover_board/v3/v3_win.png'); hud_w = hud_layer('takeover_board/v3/v3_win.png', WIN_HUD)
    wheel_b = wheel_layer('takeover_board/v3/v3_board.png'); hud_b = hud_layer('takeover_board/v3/v3_board.png', BOARD_HUD)
    room_c = world_to_screen(COMBAT, 1085, 806)
    K = []
    w1 = over(over(ImageEnhance.Brightness(base).enhance(.55), wheel_w), hud_w)
    K.append(('W1  0.00 s  WIN: WHEEL TAKEN over the room (combat pose)', w1, 'm'))
    w2 = over(ImageEnhance.Brightness(base).enhance(.7), wheel_w, .35)
    w2 = over(w2, hud_w, .2)
    w2 = bits_from_disc(w2, .35, room_c)
    K.append(('W2  0.15 s  only the wheel breaks to bits; HUD fades; the street stays', w2, 'c'))
    w3 = bits_from_disc(tint_room(base, COMBAT, 'r2', LIME, .55), .85, room_c, n=600)
    K.append(('W3  0.35 s  bits pour into the room; the room turns our colour', w3, 'c'))
    W_won, _ = build_world(['r2'], won=['r2'], links=False)
    won_base = cam(W_won, COMBAT)
    w4 = reward_panel(bits_stream(won_base, room_c, (960, 540), .9, n=500), a=1.0, bits=.55)
    K.append(('W4  0.45 s  the reward screen blooms as bits from the room', w4, 'c'))
    w5 = reward_panel(ImageEnhance.Brightness(won_base).enhance(.6))
    K.append(('W5  0.60 s  reward screen (input: CONTINUE)', w5, 'c'))
    w6 = reward_panel(won_base, a=1.0, bits=.8, seed=12)
    w6 = bits_stream(w6, (700, 420), (140, 56), .7, n=260, cols=(LIME,), size=20, seed=3)       # credits -> run purse
    w6 = bits_stream(w6, (700, 530), (960, 1040), .7, n=200, cols=(CYAN,), size=20, seed=4)     # program -> deck
    w6 = bits_stream(w6, (960, 540), room_c, .8, n=300, cols=(LIME, WHITE), seed=5)              # the rest -> the room
    d = ImageDraw.Draw(w6, 'RGBA')
    d.rectangle((24, 20, 300, 92), fill=(8, 12, 24, 230), outline=LIME + (255,), width=3)
    d.text((40, 30), '+6 cr', font=AF(44), fill=LIME)
    d.rectangle((860, 1010, 1060, 1066), fill=(8, 12, 24, 230), outline=CYAN + (255,), width=3)
    d.text((960, 1038), 'DECK 19', font=AF(32), fill=CYAN, anchor='mm')
    K.append(('W6  close: the screen goes back to bits into the room; each reward flies as bits to where it lands', w6, 'c'))
    W_wonall, _ = build_world(allr, won=['r2'])
    W_wonclosed, _ = build_world(['r2'], won=['r2'], link_a=0)
    c7 = lerp_cam(COMBAT, STREET, ease_io(.5))
    w7 = open_walls(W_wonall, W_wonclosed, [r for r in allr if r != 'r2'], .5)
    K.append(('W7  0.40 s  combat camera reverses (un-roll, un-tilt, pan); walls dissolve again', cam(w7, c7), 'c'))
    w8 = street_hud(cam(W_wonall, STREET))
    K.append(('W8  0.80 s  netrun street: lines and outlines redrawn; our room lime, next rooms ringed', w8, 'n'))
    # ---- lost
    l1 = over(over(ImageEnhance.Brightness(base).enhance(.55), wheel_b), hud_b)
    d = ImageDraw.Draw(l1, 'RGBA')
    d.rectangle((24, 22, 520, 98), fill=(40, 6, 10, 240), outline=RED + (255,), width=3)
    d.text((40, 30), 'RHEE . RUN HEALTH', font=AF(30), fill=WHITE); d.text((500, 30), '0/30', font=AF(40), fill=RED, anchor='ra')
    K.append(('L1  0.00 s  LOST: run health 0 on the wheel', l1, 'm'))
    l2 = bits_from_disc(tint_room(ImageEnhance.Brightness(base).enhance(.7), COMBAT, 'r2', LIME, .6), .55, room_c, n=700)
    K.append(('L2  0.15 s  only the wheel to bits, into the room; the room flickers our colour (1 s)', l2, 'c'))
    l3 = base.copy()
    d = ImageDraw.Draw(l3, 'RGBA')
    for i, on in enumerate((1, 0, 1, 1, 0, 1, 0, 0, 0, 0)):
        d.rectangle((640 + i * 64, 990, 690 + i * 64, 1030), fill=(LIME if on else (60, 230, 190)) + (255,), outline=(10, 10, 10, 255), width=2)
    d.text((960, 960), 'flicker over 1.0 s, then it stays corporate', font=PF(26), fill=WHITE, anchor='mm')
    K.append(('L3  1.15 s  the room stays corporate (flicker over)', l3, 'c'))
    pr = L('transitions/netrun_fail/C_trace_printout.png')
    l4 = ImageEnhance.Brightness(base).enhance(.4)
    page = pr.crop((548, 0, 1384, 1080))
    typed_to = 470
    pg = page.copy(); pd = ImageDraw.Draw(pg)
    pd.rectangle((70, typed_to, 800, 1080), fill=(226, 226, 214))
    pd.rectangle((86, typed_to - 30, 104, typed_to - 6), fill=(30, 30, 30))
    rise = 260
    l4.paste(pg.crop((0, 0, 836, 1080 - rise)), (548, rise))
    d = ImageDraw.Draw(l4)
    rng = random.Random(3)
    for _ in range(1400):
        x = rng.uniform(548, 1384); y = rng.uniform(rise + typed_to - 120, 1080)
        d.text((x, y), rng.choice('01'), font=MF(18), fill=rng.choice([(226, 226, 214), (60, 230, 190), WHITE]))
    K.append(('L4  +0.20 s  the loss screen rises as bits from the bottom and typewriters onto the page', l4, 'c'))
    l5 = over(ImageEnhance.Brightness(base).enhance(.4), hud_layer('transitions/netrun_fail/C_trace_printout.png', [(440, 0, 1480, 1080), (1290, 580, 1580, 780), (1500, 910, 1880, 1010)]))
    K.append(('L5  +0.60 s  loss screen (trace printout, design C); input: GRID VIEW', l5, 'm'))
    W_lost, _ = build_world([r for r in allr if r != 'r2'], lost=['r2'])
    l6 = street_hud(cam(W_lost, STREET), .8)
    box = ROOMS['r2'][0]
    d = ImageDraw.Draw(l6)
    d.rectangle((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 14), outline=RED, width=7)
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), 'LOST', font=AF(34), fill=RED, anchor='mm', stroke_width=4, stroke_fill=(20, 0, 0))
    K.append(('L6  close: camera back to the netrun view; the lost room keeps its wall (no re-dissolve)', l6, 'c'))
    l7 = L(V5 + 'plates/zoom_to/dense_015.jpg')
    K.append(('L7  then: the netrun zoom reverses (the T1 path backwards)', l7, 'g'))
    mp = L('cohesion/map_pages_r42/hq_idle.png')
    d = ImageDraw.Draw(mp)
    for k in (-1, 1):
        d.line((1130 - 30, 390 - 30 * k, 1130 + 30, 390 + 30 * k), fill=RED, width=9)
    d.ellipse(ell(1130, 390, 54, 54), outline=RED, width=5)
    K.append(('L8  the city map: the site stays Solace, the run is over', mp, 'm'))
    W_wonall.resize((W, H), Image.LANCZOS).save(OUT + 'plates/netrun_street_won.png')
    return K


# ================================================================ sheets
COL = {'g': (90, 220, 90), 'm': CYAN, 'c': AMB, 'n': PINK}
TAG = {'g': 'REAL', 'm': 'COMP', 'c': 'CONCEPT', 'n': 'NEW 2D PLATE'}


def badge(d, x, y, kind, s=1.0):
    t = TAG[kind]; f = F(int(18 * s), True)
    w = d.textlength(t, font=f) + 12 * s
    d.rectangle((x, y, x + w, y + 26 * s), fill=COL[kind])
    d.text((x + 6 * s, y + 3 * s), t, font=f, fill=(10, 10, 10))


def strip(title, keys, blocks, cols=3):
    n = len(keys); rows = math.ceil(n / cols)
    tw_, th, g, lab, mx = 616, 347, 24, 36, 36
    f, fb = F(19), F(19, True)
    lines_ = [(h, textwrap.wrap(x, 150) or ['']) for h, x in blocks]
    th_text = sum(len(w) for _, w in lines_) * 25 + len(lines_) * 33 + 20
    top = 70
    Wd = mx * 2 + cols * tw_ + (cols - 1) * g
    S_ = Image.new('RGB', (Wd, top + rows * (th + lab + g) + th_text + 20), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 18), title[:110], font=F(30, True), fill=LIME)
    d.text((Wd - mx - 250, 20), 'DRAFT  v6  Campaign B', font=F(24, True), fill=AMB)
    for i, (lb, im, kind) in enumerate(keys):
        r, c = divmod(i, cols)
        x = mx + c * (tw_ + g); y = top + r * (th + lab + g)
        S_.paste(im.resize((tw_, th), Image.LANCZOS), (x, y))
        d.rectangle((x - 2, y - 2, x + tw_ + 1, y + th + 1), outline=COL[kind], width=3)
        badge(d, x, y, kind)
        d.text((x, y + th + 6), lb[:84], font=F(16, True), fill=(235, 235, 240))
        if c < cols - 1 and i < n - 1:
            d.polygon([(x + tw_ + 4, y + th // 2 - 14), (x + tw_ + 20, y + th // 2), (x + tw_ + 4, y + th // 2 + 14)], fill=LIME)
    y = top + rows * (th + lab + g) + 8
    for h, wr in lines_:
        d.text((mx, y), h, font=fb, fill=AMB); y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222)); y += 25
        y += 8
    return S_


def grid_h(n, cols=3):
    return 70 + math.ceil(n / cols) * (347 + 36 + 24)


from text6 import T2TXT, T4TXT


def sheet6(K2, K4):
    """v6 sheet: the v5 sheet with the T2 and T4 rows rebuilt (other rows are crops of the v5 sheet)."""
    v5 = Image.open(V5 + 'sheet.jpg').convert('RGB')
    tw_, th, g, lw, mx = 230, 130, 8, 300, 20
    rowh = th + 24 + g
    y5 = [64 + i * rowh for i in range(9)] + [64 + 9 * rowh + 60 + i * rowh for i in range(2)]   # T1..T9, T11, T12
    ids = ['t01', 't02', 't03', 't04', 't05', 't06', 't07', 't08', 't09', 't11', 't12']
    cols = max(10, len(K2), len(K4))
    Wd = mx * 2 + lw + cols * (tw_ + g)
    rows_h = len(ids) * rowh + 60 + rowh   # T4 gets two rows (won, lost)
    S_ = Image.new('RGB', (max(Wd, v5.width), 64 + rows_h + 20), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((mx, 14), "REBEL_CELL transitions v6, Campaign B (DRAFT): T2 and T4 redone (B-107); other rows are v5. Green real, cyan comp, amber concept, pink new 2D plate",
           font=F(24, True), fill=LIME)
    y = 64

    def new_row(title, dur, keys, y):
        for k, w in enumerate(textwrap.wrap(title, 30)[:4]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), dur, font=F(14), fill=LIME)
        d.text((mx, y + 120), 'changed in v6 (B-107)', font=F(14, True), fill=PINK)
        for i, (lb, im, kind) in enumerate(keys):
            x = mx + lw + i * (tw_ + g)
            S_.paste(im.resize((tw_, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw_, y + th), outline=COL[kind], width=3)
            badge(d, x, y, kind, .6)
            d.text((x, y + th + 3), lb[:40], font=F(12), fill=(200, 200, 208))

    for i, tid in enumerate(ids):
        if tid == 't02':
            new_row('T2  Street to room: the camera moves into the combat pose; the room does not change', '1.2 s', K2, y); y += rowh
        elif tid == 't04':
            new_row('T4  Fight ends (won): only the wheel to bits, reward, camera back', '0.8 s back', K4[:8], y); y += rowh
            new_row('T4  Fight ends (lost): flicker, loss page from bits, wall stays, zoom out', '0.8 s back', K4[8:], y); y += rowh
        else:
            S_.paste(v5.crop((0, y5[i], v5.width, y5[i] + rowh)), (0, y)); y += rowh
        if tid == 't09':
            d.rectangle((mx, y + 6, S_.width - mx, y + 50), fill=(26, 26, 32), outline=(90, 90, 100), width=2)
            d.text((mx + 14, y + 16), 'T10  PURGE recall: HELD / withdrawn (B-105 ruling 7). Unchanged from v5.', font=F(20, True), fill=(200, 200, 210))
            y += 60
    return S_.crop((0, 0, S_.width, y + 10))


def flow6():
    S_ = Image.new('RGB', (2300, 1330), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((40, 20), 'Transition flow v6 (DRAFT): T2 and T4 redone per B-107; the rest as v5', font=F(38, True), fill=LIME)
    B_ = {}

    def box(k, x, y, label, col=(60, 70, 90), w=360, h=92):
        B_[k] = (x, y, w, h)
        d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(26, 30, 40), outline=col, width=4)
        for j, t in enumerate(label.split('\n')):
            d.text((x + 14, y + 12 + j * 28), t, font=F(23 if j else 24, j == 0), fill=(235, 235, 240) if j == 0 else (190, 195, 205))

    box('map', 760, 560, 'CITY MAP (r42 hq_idle, Solace)\nsites, Heat, CREW / MARKET / DEFENCE', LIME, w=470, h=100)
    box('street', 1330, 560, 'NETRUN STREET (golden plates)\ncut-away rooms, links, signage', LIME, w=440)
    box('room', 1330, 300, 'COMBAT POSE (camera only)\nsame room, walls back on the rest', PINK, w=440)
    box('fight', 1860, 300, 'FIGHT\nDeface v3 wheel over the room', LIME, w=400)
    box('reward', 1860, 560, 'REWARD (won)\nbits from the room', PINK, w=400)
    box('fail', 1860, 820, 'LOSS PAGE (lost)\nbits up, typewriter', PINK, w=400)
    box('hq', 120, 560, 'HQ WORKSHOP\nRECRUIT / WEAPONS / TALENTS', AMB, w=380)
    box('alert', 120, 880, 'RAID ALERT\nany Heat line, 100 included', (232, 20, 30), w=380)
    box('plan', 760, 880, 'RAID: REVIEW > SHOP > PLACE\n(screens_b107)', LIME, w=440)
    box('run', 1330, 880, 'RAID: EXECUTE > RESULT\nheld / TARGET ACQUIRED', LIME, w=440)
    box('lose', 760, 1180, 'DOSSIER (LOSE)\nHQ integrity 0', PINK, w=420)
    box('hqnet', 760, 200, 'HQ NETRUN\nSolace HQ street, BLOCK SERVER v2', AMB, w=440)
    box('win', 1330, 90, 'DOSSIER (WIN)\nslot B, campaign won', LIME, w=420)

    def pt(k, s):
        x, y, w, h = B_[k]
        return {'l': (x, y + h / 2), 'r': (x + w, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[s]

    def arrow(a, b, n, col=LIME, off=(0, 0), side=('r', 'l'), off2=None):
        p, q = pt(a, side[0]), pt(b, side[1])
        o2 = off2 if off2 is not None else off
        p = (p[0] + off[0], p[1] + off[1]); q = (q[0] + o2[0], q[1] + o2[1])
        d.line((p, q), fill=col, width=5)
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        d.polygon([q, (q[0] - 22 * math.cos(ang - .4), q[1] - 22 * math.sin(ang - .4)), (q[0] - 22 * math.cos(ang + .4), q[1] - 22 * math.sin(ang + .4))], fill=col)
        if n:
            mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            d.ellipse((mx_ - 21, my_ - 21, mx_ + 21, my_ + 21), fill=col)
            d.text((mx_ - (13 if n > 9 else 6), my_ - 13), str(n), font=F(22, True), fill=(10, 10, 10))

    arrow('map', 'street', 1, off=(0, -22)); arrow('street', 'map', 5, off=(0, 22), side=('l', 'r'))
    arrow('street', 'room', 2, PINK, side=('t', 'b')); arrow('room', 'fight', 3)
    arrow('fight', 'reward', 4, PINK, side=('b', 't')); arrow('reward', 'street', 4, PINK, side=('l', 'r'), off=(0, 20), off2=(0, 20))
    arrow('reward', 'fail', None, (14, 15, 20), side=('b', 't'))
    d.line((2060, 392, 2060, 410), fill=(14, 15, 20), width=1)
    arrow('fight', 'fail', 4, PINK, side=('r', 'r'), off=(0, 0), off2=(0, 0))
    arrow('fail', 'map', 4, PINK, side=('b', 'b'), off=(0, 0), off2=(120, 0))
    arrow('map', 'alert', 6, (232, 20, 30), side=('b', 't'), off=(-180, 0), off2=(0, 0)); arrow('alert', 'plan', None, (232, 20, 30))
    arrow('map', 'plan', 7, side=('b', 't'), off=(-30, 0)); arrow('plan', 'map', None, side=('t', 'b'), off=(60, 0))
    arrow('plan', 'run', 8); arrow('run', 'map', 8, side=('t', 'r'), off2=(0, 30))
    arrow('map', 'hq', 9, AMB, off=(0, -22), side=('l', 'r')); arrow('hq', 'map', None, AMB, off=(0, 22))
    arrow('run', 'lose', 11, PINK, side=('b', 'r'))
    arrow('map', 'hqnet', 12, AMB, side=('t', 'b')); arrow('hqnet', 'win', 12, AMB)
    d.text((40, 1295), 'Pink = changed in v6 (B-107): T2 combat pose by camera only; T4 won (reward from the room) and lost (loss page, wall stays, zoom out to the map). T10 held.', font=F(20), fill=(215, 215, 222))
    return S_


def vs(K2s, K4s):
    sc = .40
    gw = int(1968 * sc)
    rows = []
    for tid, new in (('t02_street_to_room.jpg', K2s), ('t04_fight_end_to_street_or_fail.jpg', K4s)):
        a = Image.open(V5 + tid).convert('RGB')
        rows.append((tid, a, new))
    tot = 90 + sum(int(max(a.height, b.height) * sc) + 44 for _, a, b in rows)
    S_ = Image.new('RGB', (gw * 2 + 90, tot), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((30, 18), 'v5 (left) vs v6 (right, DRAFT): T2 and T4 redone per B-107; every other transition is unchanged', font=F(26, True), fill=LIME)
    y = 70
    for tid, a, b in rows:
        d.text((30, y), 'v5: ' + tid, font=F(19, True), fill=(180, 185, 195)); d.text((gw + 60, y), 'v6: ' + tid, font=F(19, True), fill=AMB)
        y += 32
        A = a.resize((gw, int(a.height * gw / a.width)), Image.LANCZOS); B2 = b.resize((gw, int(b.height * gw / b.width)), Image.LANCZOS)
        S_.paste(A, (30, y)); S_.paste(B2, (gw + 60, y))
        y += max(A.height, B2.height) + 12
    return S_.crop((0, 0, S_.width, y + 10))


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(OUT + 'plates', exist_ok=True)
    K2, W_open, W_walls, W_ours = t2()
    s2 = strip(T2TXT['title'], K2, T2TXT['blocks'])
    s2.save(OUT + 't02_street_to_room.jpg', quality=90)
    K4 = t4(W_open, W_walls, W_ours)
    s4 = strip(T4TXT['title'], K4, T4TXT['blocks'], cols=4)
    s4.save(OUT + 't04_fight_end_to_street_or_fail.jpg', quality=90)
    sheet6(K2, K4).save(OUT + 'sheet.jpg', quality=88)
    flow6().save(OUT + 'flow.jpg', quality=90)
    vs(s2, s4).save(OUT + 'v5_vs_v6.jpg', quality=88)
    for k, (lb, im, kind) in enumerate(K2):
        im.save(OUT + 'plates/t2_%02d.jpg' % (k + 1), quality=90)
    for k, (lb, im, kind) in enumerate(K4):
        im.save(OUT + 'plates/t4_%s.jpg' % lb.split()[0].lower(), quality=90)
    print('ok')
