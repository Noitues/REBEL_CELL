"""BLOCK SERVER bio lab v2 (B-107 item 2): fits its 3D building. The tank now stands inside the cutaway box (top under
the wall-top line, 3.2 of the 3.3 kit-m wall), the pipes no longer rise out of the box: they leave the cap sideways at
ceiling height into a manifold on the back wall. The specimen gets real detail (spine plates, ribs, membrane veins, gill
fronds, sucker tendrils, umbilical lines into its back, nodules, one lit eye + two dim ones).
Drawn in 2D over the v3.1 bio cutaway (combat_backdrop/v3_1/room_bio_bare.png); geometry, street and SOLACE signage stay.
Also writes the kit breakdown sheet (parts in kit cells and BU).
Run: python blockserver_v2.py   (writes screens_b107/block_server_v2*.png, block_server_kit.png; copies the plate to
transitions/v6/plates/)"""
import os, sys, math, random, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

R = 'D:/rc_art/art-pass/docs/concepts/'
OUT = R + 'screens_b107/'
FNT = 'D:/rc_art/art-pass/assets/fonts/'
SOL = (61, 255, 139); CYN = (92, 225, 255); RIM = (150, 255, 70); PNK = (255, 61, 168); AMBR = (255, 176, 0)

# cutaway box, measured on the v3.1 plates (bio and srv share it): back floor corner, the two floor edges, wall height
B = np.array([1467.0, 505.0]); A_ = np.array([-260.0, 125.0]); B_ = np.array([316.0, 178.0]); WALL = 152
PX_M = WALL / 3.3          # px per kit metre (wall 3.3 m, kit v3.1 room_shell)
BU_CELL = 0.5              # 1 kit cell = 0.5 BU (a storey 3.3 + 0.6 slab = 3.9 cells = 1.95 BU ~ floor_bu 1.9)


def MF(sz):
    return ImageFont.truetype(FNT + 'ShareTechMono-Regular.ttf', sz)


def AF(sz):
    return ImageFont.truetype(FNT + 'Anton-Regular.ttf', sz)


def PF(sz):
    return ImageFont.truetype(FNT + 'IBMPlexSansCondensed-Medium.ttf', sz)


def P(u, v, h=0.0):
    p = B + u * A_ + v * B_
    return (float(p[0]), float(p[1] - h))


def poly(d, pts, fill=None, outline=None, width=1):
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=width, joint='curve')


def box(d, u0, u1, v0, v1, h, top, fu, fv, edge=(8, 12, 18), w=2, h0=0.0):
    poly(d, [P(u1, v0, h0), P(u1, v1, h0), P(u1, v1, h), P(u1, v0, h)], fu, edge, w)
    poly(d, [P(u0, v1, h0), P(u1, v1, h0), P(u1, v1, h), P(u0, v1, h)], fv, edge, w)
    poly(d, [P(u0, v0, h), P(u1, v0, h), P(u1, v1, h), P(u0, v1, h)], top, edge, w)


def leds(d, u0, u1, v0, v1, h, rng, face='u'):
    rows = int(h // 11)
    for r in range(1, rows):
        hh = r * 11 + 2
        col = rng.choice([CYN, CYN, PNK, SOL, (230, 240, 255), (40, 60, 70)])
        if face == 'u':
            a, b = P(u1, v0 + (v1 - v0) * .15, hh), P(u1, v0 + (v1 - v0) * rng.uniform(.45, .85), hh)
        else:
            a, b = P(u0 + (u1 - u0) * .15, v1, hh), P(u0 + (u1 - u0) * rng.uniform(.45, .85), v1, hh)
        d.line((a, b), fill=col, width=3)


def ell(cx, cy, rx, ry):
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def add_glow(im, layer, k=1.0):
    a = np.asarray(im).astype(np.float32) + np.asarray(layer).astype(np.float32) * k
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))


# ---------------------------------------------------------------- the specimen (drawn big, then scaled into the tank)
def specimen(w=900, h=620, live=True):
    """SPECIMEN 0: a curled, half-grown thing. Body as an arc of overlapping segments with spine plates; ribs and veins
    on a translucent membrane; gill fronds behind the head; sucker tendrils trailing down; umbilical lines into its back;
    nodules. Drawn at large size on transparent RGBA."""
    L = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    body = (12, 58, 36, 255) if live else (14, 26, 22, 255)
    skin = (24, 96, 62, 255) if live else (26, 40, 34, 255)
    rim = (150, 255, 190, 255) if live else (70, 96, 84, 255)
    vein = (90, 210, 150, 200) if live else (50, 66, 60, 200)
    pnk = (255, 80, 180, 255) if live else (80, 50, 70, 255)
    cx, cy = w * .52, h * .52
    # umbilical lines from the top (into the cap) down into its back
    for k, ox in enumerate((-.10, .02, .14)):
        pts = [(cx + ox * w + 30 * math.sin(t * 3 + k), h * .02 + t * h * .30) for t in np.linspace(0, 1, 20)]
        d.line(pts, fill=(8, 34, 24, 255), width=18 - 3 * k, joint='curve')
        d.line(pts, fill=(40, 120, 90, 255) if live else (40, 56, 50, 255), width=5, joint='curve')
    # tendrils (behind the body), with suckers
    for k in range(6):
        a0 = math.radians(200 + k * 14)
        pts = []
        for t in np.linspace(0, 1, 30):
            r_ = w * (.18 + .30 * t)
            pts.append((cx + math.cos(a0 - .9 * t) * r_ * .9, cy + h * .12 + t * h * .38 + 18 * math.sin(t * 7 + k)))
        wd = 20 - 2 * k
        d.line(pts, fill=body, width=wd, joint='curve')
        d.line(pts, fill=skin, width=max(3, wd // 3), joint='curve')
        for j in range(4, 28, 4):
            x, y = pts[j]
            r_ = max(2, wd * .22)
            d.ellipse(ell(x, y + wd * .3, r_, r_), fill=rim if live else (60, 80, 70, 255))
    # the curled body: segments along an arc (head top-left, tail curling under)
    seg = []
    for i in range(16):
        t = i / 15
        a = math.radians(150 - 290 * t)
        rr = w * (.30 - .10 * t)
        x = cx + math.cos(a) * rr
        y = cy - math.sin(a) * rr * .78
        s = w * (.15 - .085 * t)
        seg.append((x, y, s))
    for x, y, s in reversed(seg):
        d.ellipse(ell(x, y, s, s * .86), fill=body, outline=(4, 20, 12, 255), width=4)
        d.ellipse(ell(x - s * .15, y - s * .2, s * .7, s * .55), fill=skin)
    # membrane veins over the segments
    rng = random.Random(7)
    for x, y, s in seg[2:]:
        for k in range(3):
            a = rng.uniform(0, math.tau)
            pts = [(x + math.cos(a + j * .25) * s * (.2 + .12 * j), y + math.sin(a + j * .25) * s * (.15 + .1 * j)) for j in range(6)]
            d.line(pts, fill=vein, width=3, joint='curve')
    # spine plates along the outer edge of the arc
    for i, (x, y, s) in enumerate(seg[1:13]):
        a = math.radians(150 - 290 * ((i + 1) / 15))
        ox, oy = math.cos(a), -math.sin(a) * .78
        nx, ny = x + ox * s * .9, y + oy * s * .9
        tx, ty = -oy, ox
        pts = [(nx + tx * s * .35, ny + ty * s * .35), (nx + ox * s * .55, ny + oy * s * .55), (nx - tx * s * .35, ny - ty * s * .35)]
        d.polygon(pts, fill=(30, 80, 56, 255) if live else (30, 40, 36, 255), outline=rim, width=3)
    # ribs on the inner curve
    for x, y, s in seg[3:11]:
        d.arc(ell(x + s * .2, y + s * .25, s * .7, s * .45), 200, 320, fill=rim, width=3)
    # head: the first segment, bigger, with gill fronds and eyes
    hx, hy, hs = seg[0][0] - w * .03, seg[0][1] - h * .02, w * .17
    for k in range(5):
        a = math.radians(110 + k * 16)
        x1, y1 = hx + math.cos(a) * hs * 1.7, hy - math.sin(a) * hs * 1.3
        d.line([(hx, hy), ((hx + x1) / 2 + 10, (hy + y1) / 2 - 8), (x1, y1)], fill=body, width=14, joint='curve')
        for j in range(1, 6):
            px = hx + (x1 - hx) * j / 6; py = hy + (y1 - hy) * j / 6
            d.line([(px, py), (px - 14, py - 10)], fill=skin, width=4)
    d.ellipse(ell(hx, hy, hs, hs * .84), fill=body, outline=(4, 20, 12, 255), width=5)
    d.ellipse(ell(hx - hs * .1, hy - hs * .2, hs * .75, hs * .5), fill=skin)
    d.arc(ell(hx, hy, hs * .98, hs * .82), 200, 340, fill=rim, width=5)
    # eyes: one lit, two dim
    ex, ey = hx - hs * .35, hy + hs * .05
    if live:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse(ell(ex, ey, hs * .55, hs * .45), fill=(255, 60, 170, 160))
        L.alpha_composite(g.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(L)
    d.ellipse(ell(ex, ey, hs * .24, hs * .19), fill=pnk, outline=(30, 0, 20, 255), width=4)
    d.ellipse(ell(ex - hs * .05, ey, hs * .07, hs * .15), fill=(20, 0, 14, 255))
    d.ellipse(ell(ex + hs * .08, ey - hs * .07, hs * .05, hs * .04), fill=(255, 230, 245, 255) if live else (90, 80, 86, 255))
    for k, (ox, oy) in enumerate(((.20, -.30), (.38, -.05))):
        d.ellipse(ell(hx + hs * ox, hy + hs * oy, hs * .09, hs * .07), fill=(60, 30, 50, 255), outline=(10, 0, 8, 255), width=2)
    # mouth slit + small teeth
    d.arc(ell(hx - hs * .2, hy + hs * .45, hs * .35, hs * .14), 10, 170, fill=(4, 16, 10, 255), width=5)
    # core and nodules (bioluminescent)
    corex, corey = cx + w * .04, cy + h * .02
    if live:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse(ell(corex, corey, 70, 60), fill=(255, 60, 170, 150))
        L.alpha_composite(g.filter(ImageFilter.GaussianBlur(26))); d = ImageDraw.Draw(L)
    d.ellipse(ell(corex, corey, 34, 28), fill=pnk, outline=(40, 0, 26, 255), width=4)
    d.ellipse(ell(corex - 6, corey - 6, 12, 9), fill=(255, 200, 235, 255) if live else (110, 90, 100, 255))
    for k in range(14):
        x, y, s = seg[rng.randrange(2, 15)]
        d.ellipse(ell(x + rng.uniform(-s * .5, s * .5), y + rng.uniform(-s * .4, s * .4), 6, 6), fill=pnk if k % 3 else rim)
    return L


# ---------------------------------------------------------------- the room
TANK_U, TANK_V = .50, .50
TANK_R_M = 1.1        # glass radius, kit m (glass dia 2.2)
PLINTH_H_M, GLASS_H_M, CAP_H_M = .25, 2.6, .35     # top of cap at 3.2 m < 3.3 m wall


def build(src=R + 'combat_backdrop/v3_1/room_bio_bare.png', state='live'):
    rng = random.Random(107)
    base = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
    im = base.copy(); d = ImageDraw.Draw(im)
    live = state == 'live'
    wl = [P(0, 0, 0), P(1, 0, 0), P(1, 0, WALL), P(0, 0, WALL)]
    wr = [P(0, 0, 0), P(0, 1, 0), P(0, 1, WALL), P(0, 0, WALL)]
    poly(d, wl, (20, 50, 50)); poly(d, wr, (16, 42, 46))
    for k in range(1, 12):
        d.line((P(k / 12, 0, 0), P(k / 12, 0, WALL)), fill=(12, 34, 36), width=2)
        d.line((P(0, k / 12, 0), P(0, k / 12, WALL)), fill=(10, 30, 34), width=2)
    for hh, col in ((WALL - 14, RIM), (62, (40, 120, 110))):
        d.line((P(0, 0, hh), P(1, 0, hh)), fill=col, width=3); d.line((P(0, 0, hh), P(0, 1, hh)), fill=col, width=3)
    poly(d, [P(0, 0), P(1, 0), P(1, 1), P(0, 1)], (22, 64, 54))
    for k in range(1, 7):
        d.line((P(k / 7, 0), P(k / 7, 1)), fill=(30, 84, 70), width=2)
    for k in range(1, 9):
        d.line((P(0, k / 9), P(1, k / 9)), fill=(30, 84, 70), width=2)
    cx, cy = P(TANK_U, TANK_V)
    RX = TANK_R_M * PX_M * 1.55          # iso: the circle's width on screen
    RY = RX * .5
    PL, TH, CAPH = PLINTH_H_M * PX_M, GLASS_H_M * PX_M, CAP_H_M * PX_M
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    if live:
        gd.ellipse(ell(cx, cy, RX * 2.7, RY * 2.7), fill=(20, 110, 60))
        g = g.filter(ImageFilter.GaussianBlur(40)); im = add_glow(im, g, .9); d = ImageDraw.Draw(im)
    d.ellipse(ell(cx, cy, RX * 1.7, RY * 1.7), outline=(AMBR if live else (110, 90, 40)), width=4)
    for k in range(24):
        a = k / 24 * math.tau
        if k % 2 == 0:
            d.arc(ell(cx, cy, RX * 1.58, RY * 1.58), math.degrees(a), math.degrees(a) + 7, fill=(30, 30, 30), width=6)
    # wall manifold: a pipe header along the back-left wall at ceiling height, the tank pipes end in it
    for k, hh in enumerate((WALL - 30, WALL - 44)):
        d.line((P(.15, 0, hh), P(.85, 0, hh)), fill=(8, 12, 16), width=12)
        d.line((P(.15, 0, hh), P(.85, 0, hh)), fill=(64, 82, 90), width=6)
        for j in range(5):
            u = .2 + j * .15
            d.line((P(u, 0, hh - 8), P(u, 0, hh + 8)), fill=(20, 26, 30), width=4)
    racks = []
    for i in range(5):
        u0 = .06 + i * .17; racks.append((u0, u0 + .12, .02, .13, rng.choice([110, 118, 126])))
    for i in range(5):
        v0 = .16 + i * .15; racks.append((.02, .14, v0, v0 + .11, rng.choice([110, 118, 126])))
    racks.sort(key=lambda r: r[1] + r[3])
    for k, (u0, u1, v0, v1, h) in enumerate(racks):
        ru, rv = (u0 + u1) / 2, (v0 + v1) / 2
        ang = math.atan2(rv - TANK_V, ru - TANK_U)
        su, sv = TANK_U + math.cos(ang) * .2, TANK_V + math.sin(ang) * .2
        mu, mv = (su + ru) / 2 + .04 * math.sin(k * 1.7), (sv + rv) / 2 + .04 * math.cos(k * 1.3)
        pts = [P((1 - t) ** 2 * su + 2 * (1 - t) * t * mu + t * t * ru, (1 - t) ** 2 * sv + 2 * (1 - t) * t * mv + t * t * rv) for t in np.linspace(0, 1, 24)]
        d.line(pts, fill=(6, 10, 14), width=11, joint='curve')
        d.line(pts, fill=(CYN if k % 3 else SOL) if live else (40, 60, 64), width=3, joint='curve')
    for r in racks:
        u0, u1, v0, v1, h = r
        box(d, u0, u1, v0, v1, h, (34, 46, 58), (18, 24, 34), (24, 32, 44))
        leds(d, u0, u1, v0, v1, h, rng if live else random.Random(1), 'u')
        if live:
            leds(d, u0, u1, v0, v1, h, rng, 'v')
        d.line((P(u0, v1, h), P(u1, v1, h), P(u1, v0, h)), fill=(90, 200, 190) if live else (60, 80, 80), width=2)
    for a, b in ((P(0, 0, WALL), P(1, 0, WALL)), (P(0, 0, WALL), P(0, 1, WALL))):
        d.line((a, b), fill=RIM, width=5)

    def cyl(d_, cx_, top_y, bot_y, rx, ry, side, top, edge=(8, 12, 18)):
        d_.rectangle((cx_ - rx, top_y, cx_ + rx, bot_y), fill=side)
        d_.ellipse(ell(cx_, bot_y, rx, ry), fill=side)
        d_.line((cx_ - rx, top_y, cx_ - rx, bot_y), fill=edge, width=3); d_.line((cx_ + rx, top_y, cx_ + rx, bot_y), fill=edge, width=3)
        d_.arc(ell(cx_, bot_y, rx, ry), 0, 180, fill=edge, width=3)
        d_.ellipse(ell(cx_, top_y, rx, ry), fill=top, outline=edge, width=3)
    cyl(d, cx, cy - PL, cy, RX + 16, RY + 9, (30, 40, 46), (52, 66, 72))
    for k in range(12):
        a = math.pi * (k + .5) / 12
        x = cx - math.cos(a) * (RX + 16); y = cy - PL / 2 + math.sin(a) * (RY + 9) * .9
        d.rectangle((x - 4, y - 3, x + 4, y + 3), fill=SOL if live else (50, 70, 60))
    gb = cy - PL - 4
    gt = gb - TH
    W2 = int(2 * RX + 1); Hh = int(gb - gt) + int(RY) + 1
    xs = np.linspace(-1, 1, W2); shade = np.sqrt(np.clip(1 - xs ** 2, 0, 1))
    c0, c1 = (np.array([8, 70, 40]), np.array(SOL)) if live else (np.array([10, 22, 18]), np.array([40, 70, 56]))
    yy = np.linspace(0, 1, Hh)[:, None]
    tone = (.35 + .65 * shade[None, :]) * (0.75 + .25 * (1 - yy))
    arr = c0[None, None, :] + (c1 - c0)[None, None, :] * tone[..., None]
    col = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    m = Image.new('L', col.size, 0); md = ImageDraw.Draw(m)
    md.rectangle((0, 0, col.width, Hh - RY), fill=255); md.ellipse((0, Hh - 2 * RY - 1, col.width - 1, Hh - 1), fill=255)
    im.paste(col, (int(cx - RX), int(gt)), m)
    # the specimen, scaled into the glass
    sp = specimen(900, 620, live)
    sw = int(RX * 2.05); sh = int(sw * 620 / 900)
    sp = sp.resize((sw, sh), Image.LANCZOS)
    imr = im.convert('RGBA'); imr.alpha_composite(sp, (int(cx - sw / 2), int(gt + (TH - sh) * .55))); im = imr.convert('RGB')
    d = ImageDraw.Draw(im)
    for k in range(46):
        x = cx + rng.uniform(-RX * .85, RX * .85); y = rng.uniform(gt + 8, gb - 6); r = rng.choice([2, 2, 3, 3, 4, 5])
        if live:
            d.ellipse(ell(x, y, r, r), outline=(210, 255, 225), width=1 if r < 4 else 2)
    d.line((cx - RX * .62, gt + 10, cx - RX * .62, gb - 6), fill=(220, 255, 235) if live else (90, 110, 100), width=5)
    d.line((cx - RX * .46, gt + 22, cx - RX * .46, gb - 22), fill=(170, 240, 200) if live else (70, 90, 80), width=2)
    d.line((cx + RX * .74, gt + 14, cx + RX * .74, gb - 14), fill=(120, 230, 170) if live else (50, 70, 60), width=2)
    d.line((cx - RX, gt, cx - RX, gb), fill=(10, 20, 18), width=4); d.line((cx + RX, gt, cx + RX, gb), fill=(10, 20, 18), width=4)
    hb = gt + TH * .5
    d.rectangle((cx - RX - 4, hb - 6, cx + RX + 4, hb + 6), fill=(44, 56, 62))
    d.arc(ell(cx, hb + 6, RX + 4, RY), 0, 180, fill=(10, 14, 18), width=3)
    for k in range(7):
        x = cx - RX + 16 + k * (2 * RX - 32) / 6
        d.rectangle((x - 4, hb - 3, x + 4, hb + 3), fill=SOL if live else (40, 60, 50))
    d.arc(ell(cx, gb, RX, RY), 0, 180, fill=(10, 20, 18), width=4)
    # cap (top under the wall-top line), pipes leave it SIDEWAYS into the wall manifold (no riser)
    cyl(d, cx, gt - CAPH, gt + 4, RX + 10, RY + 6, (40, 52, 58), (62, 78, 86))
    for k in range(10):
        a = math.pi * (k + .5) / 10
        x = cx - math.cos(a) * (RX + 10); y = gt - CAPH / 2 + math.sin(a) * (RY + 6) * .7
        d.line((x, y - 8, x, y + 8), fill=(20, 26, 30), width=3)
    for k, (du, hh) in enumerate(((-.10, WALL - 30), (0.0, WALL - 44), (.10, WALL - 30))):
        sx, sy = cx - RX * .25 + k * RX * .25, gt - CAPH + 2
        tx, ty = P(TANK_U + du, .0, hh)
        mid = (sx, sy - 6)
        pts = [(sx, sy), mid, (sx + (tx - sx) * .3, sy - 8 - (sy - ty) * .2), (tx, ty)]
        d.line(pts, fill=(8, 12, 16), width=13, joint='curve')
        d.line(pts, fill=(56, 72, 80), width=7, joint='curve')
        d.line(pts, fill=(110, 140, 150), width=2, joint='curve')
    d.ellipse(ell(cx, gt - CAPH, RX * .45, RY * .45), fill=(30, 38, 44), outline=(8, 12, 18), width=3)
    for k, (u0, u1, v0, v1, h) in enumerate(racks):
        tx, ty = P((u0 + u1) / 2, (v0 + v1) / 2, h)
        sx, sy = cx + (RX + 6) * (1 if tx > cx else -1) * .8, gt - CAPH * .3 + (k % 3) * 5
        sag = 26 + 12 * (k % 3)
        pts = [(sx + (tx - sx) * t, sy + (ty - sy) * t + sag * math.sin(math.pi * t)) for t in np.linspace(0, 1, 20)]
        d.line(pts, fill=(8, 10, 14), width=6, joint='curve')
        if live and k % 2 == 0:
            d.line(pts, fill=CYN if k % 4 == 0 else SOL, width=2, joint='curve')
    for (u0, v0) in ((.80, .24), (.76, .68)):
        box(d, u0, u0 + .09, v0, v0 + .13, 38, (60, 76, 84), (30, 40, 48), (40, 52, 60))
        a, b, c_, e = P(u0 + .02, v0 + .02, 44), P(u0 + .02, v0 + .11, 44), P(u0 + .02, v0 + .11, 74), P(u0 + .02, v0 + .02, 74)
        poly(d, [a, b, c_, e], CYN if live else (30, 50, 60), (8, 12, 18), 2)
    if live:
        g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rectangle((cx - RX, gt, cx + RX, gb), fill=(20, 120, 60))
        g = g.filter(ImageFilter.GaussianBlur(40))
        ImageDraw.Draw(g).rectangle((cx - RX + 6, gt + 6, cx + RX - 6, gb), fill=(0, 0, 0))
        im = add_glow(im, g.filter(ImageFilter.GaussianBlur(4)), .8)
    d = ImageDraw.Draw(im)
    for a, b in ((P(1, 0, 0), P(1, 1, 0)), (P(0, 1, 0), P(1, 1, 0)), (P(1, 0, 0), P(1, 0, WALL)), (P(0, 1, 0), P(0, 1, WALL))):
        d.line((a, b), fill=RIM, width=5)
    d.line((P(0, 0, 0), P(0, 0, WALL)), fill=(12, 30, 30), width=3)
    d.text((cx + RX + 18, gt + 4), 'SPECIMEN 0', font=MF(17), fill=(200, 255, 220) if live else (120, 140, 130))
    return im.filter(ImageFilter.GaussianBlur(.4)), (cx, cy, RX, RY, gt, gb, CAPH)


def kit_sheet(plate, geo):
    """Kit breakdown: the plate, a plan (9 x 7 cells), an elevation against the wall height, the specimen big, parts list."""
    Wd, Hd = 2600, 1500
    S_ = Image.new('RGB', (Wd, Hd), (14, 15, 20)); d = ImageDraw.Draw(S_)
    d.text((40, 24), 'BLOCK SERVER v2: kit room breakdown (B-107 item 2)', font=AF(48), fill=RIM)
    d.text((40, 92), 'v3.1 kit shell (bio), 1 cell = 1 kit m = %.1f BU (a storey 3.3 + 0.6 slab = 3.9 cells = 1.95 BU ~ floor_bu 1.9). Tank top 3.2 < wall 3.3: nothing leaves the box.' % BU_CELL,
           font=PF(24), fill=(210, 212, 222))
    pl = plate.crop((1100, 150, 1900, 900)).resize((640, 600), Image.LANCZOS)
    S_.paste(pl, (40, 150)); d.rectangle((40, 150, 680, 750), outline=RIM, width=3)
    d.text((40, 760), 'the room (v2 plate, crop)', font=PF(22), fill=(190, 194, 206))
    # plan
    ox, oy, c = 740, 190, 62
    d.text((ox, 150), 'PLAN  9 x 7 cells (4.5 x 3.5 BU), cut edges lime', font=PF(24), fill=(230, 232, 240))
    for i in range(10):
        d.line((ox + i * c, oy, ox + i * c, oy + 7 * c), fill=(50, 60, 70), width=1)
    for j in range(8):
        d.line((ox, oy + j * c, ox + 9 * c, oy + j * c), fill=(50, 60, 70), width=1)
    d.line((ox, oy, ox + 9 * c, oy), fill=(150, 160, 170), width=8); d.line((ox, oy, ox, oy + 7 * c), fill=(150, 160, 170), width=8)
    d.line((ox, oy + 7 * c, ox + 9 * c, oy + 7 * c), fill=RIM, width=4); d.line((ox + 9 * c, oy, ox + 9 * c, oy + 7 * c), fill=RIM, width=4)
    for i in range(5):
        d.rectangle((ox + (.3 + i * 1.7) * c, oy + 4, ox + (1.3 + i * 1.7) * c, oy + c), fill=(40, 52, 66), outline=CYN, width=2)
    for i in range(4):
        d.rectangle((ox + 4, oy + (1.4 + i * 1.4) * c, ox + c, oy + (2.4 + i * 1.4) * c), fill=(40, 52, 66), outline=CYN, width=2)
    tcx, tcy = ox + 4.5 * c, oy + 3.6 * c
    d.ellipse(ell(tcx, tcy, 2.1 * c, 2.1 * c), outline=AMBR, width=3)
    d.ellipse(ell(tcx, tcy, 1.5 * c, 1.5 * c), fill=(30, 40, 46), outline=(120, 140, 150), width=3)
    d.ellipse(ell(tcx, tcy, 1.3 * c, 1.3 * c), fill=(20, 110, 60), outline=SOL, width=3)
    for k in range(3):
        d.line((tcx - .4 * c + k * .4 * c, tcy - 1.3 * c, tcx - .4 * c + k * .4 * c, oy + .9 * c), fill=(110, 140, 150), width=5)
    d.rectangle((ox + 7.2 * c, oy + 1.5 * c, ox + 8.1 * c, oy + 2.4 * c), fill=(60, 76, 84), outline=CYN, width=2)
    d.rectangle((ox + 7.0 * c, oy + 4.6 * c, ox + 7.9 * c, oy + 5.5 * c), fill=(60, 76, 84), outline=CYN, width=2)
    d.line((ox + 3.5 * c, oy + 7 * c, ox + 5.5 * c, oy + 7 * c), fill=PNK, width=8)
    d.text((ox + 3.6 * c, oy + 7 * c + 8), 'door aisle (3 cells, kept clear)', font=PF(18), fill=PNK)
    d.text((tcx - 40, tcy - 12), 'TANK', font=AF(26), fill=(230, 255, 240))
    d.text((ox + 9 * c + 14, oy + 3 * c), 'cut', font=PF(20), fill=RIM)
    # elevation
    ex, ey = 740, 1110
    d.text((ex, 690), 'ELEVATION  (front cut, heights in kit m)', font=PF(24), fill=(230, 232, 240))
    sc = 72
    d.rectangle((ex, ey, ex + 9 * c, ey + .6 * sc), fill=(40, 46, 56)); d.text((ex + 9 * c + 10, ey), 'slab 0.6', font=PF(18), fill=(190, 194, 206))
    d.line((ex, ey - 3.3 * sc, ex + 9 * c, ey - 3.3 * sc), fill=RIM, width=3)
    d.text((ex + 9 * c + 10, ey - 3.3 * sc - 12), 'wall top 3.3 (1.65 BU)', font=PF(18), fill=RIM)
    tx0 = ex + 4.5 * c
    d.rectangle((tx0 - 1.5 * c, ey - .35 * sc, tx0 + 1.5 * c, ey), fill=(52, 66, 72))
    d.rectangle((tx0 - 1.3 * c, ey - 2.7 * sc, tx0 + 1.3 * c, ey - .35 * sc), fill=(20, 110, 60), outline=SOL, width=2)
    d.rectangle((tx0 - 1.45 * c, ey - 3.2 * sc, tx0 + 1.45 * c, ey - 2.7 * sc), fill=(62, 78, 86))
    d.line((tx0 - 1.45 * c, ey - 3.2 * sc, tx0 + 1.45 * c, ey - 3.2 * sc), fill=AMBR, width=2)
    d.text((tx0 + 1.6 * c, ey - 3.2 * sc - 6), 'cap top 3.2', font=PF(18), fill=AMBR)
    d.line((tx0 - .4 * c, ey - 3.15 * sc, ex + 8, ey - 2.9 * sc), fill=(110, 140, 150), width=6)
    d.text((ex, ey + 80), 'cap pipes: sideways at 2.9 into the wall header (no riser)', font=PF(18), fill=(160, 190, 200))
    for k in range(5):
        hh = (2.5, 2.5, 2.6, 2.4, 2.5)[k]
        d.rectangle((ex + 8 + k * 30, ey - hh * sc, ex + 34 + k * 30, ey), outline=CYN, width=2)
    d.text((ex + 8, ey + 50), 'racks 2.5', font=PF(18), fill=CYN)
    d.line((tx0 + .3 * c, ey - 3.3 * sc, tx0 + .3 * c, ey - 4.3 * sc), fill=(232, 20, 30), width=4)
    d.line((tx0 + .1 * c, ey - 4.1 * sc, tx0 + .5 * c, ey - 4.3 * sc), fill=(232, 20, 30), width=4)
    d.text((tx0 + .7 * c, ey - 4.35 * sc), 'v5 riser pipes: removed', font=PF(20), fill=(255, 110, 110))
    # specimen big
    sp = specimen(900, 620, True)
    bg = Image.new('RGBA', (660, 470), (10, 50, 32, 255))
    bg.alpha_composite(sp.resize((640, 441), Image.LANCZOS), (10, 14))
    S_.paste(bg.convert('RGB'), (1500, 150)); d.rectangle((1500, 150, 2160, 620), outline=SOL, width=3)
    d.text((1500, 630), 'SPECIMEN 0 (more detail, B-107): spine plates, ribs, membrane veins, gill fronds, sucker', font=PF(20), fill=(210, 212, 222))
    d.text((1500, 656), 'tendrils, umbilical lines from the cap into its back, glowing nodules, a lit core, one lit eye', font=PF(20), fill=(210, 212, 222))
    # parts list
    parts = [('room_shell (bio)', '9 x 7, wall 3.3, slab 0.6, wall 0.3 thick', '4.5 x 3.5, 1.65', 'kit v3.1 shell, corp trim'),
             ('tank_plinth', 'dia 3.0, h 0.35', '1.5, 0.18', '12 lime status lamps'),
             ('tank_glass', 'dia 2.6, h 2.35', '1.3, 1.18', 'liquid emissive, 1 steel band'),
             ('tank_cap', 'dia 2.9, h 0.5 (top 3.2)', '1.45, 0.25', 'under the wall top'),
             ('cap_pipes x3', 'dia 0.25, run 3.0 at h 2.9', '0.13, 1.5', 'sideways into the header'),
             ('wall_header', '7.0 x 0.3 x 0.3, two runs', '3.5 x 0.15', 'back-left wall, h 2.75 / 2.9'),
             ('specimen_0', '2.2 x 1.4 x 1.6 (curled)', '1.1 x 0.7 x 0.8', 'eye + core + nodules emissive'),
             ('rack x9', '1 x 1 x 2.4-2.6', '0.5 x 0.5 x 1.25', 'kit rack, LED faces'),
             ('cable_floor x9', 'conduit, rack to tank', '-', 'kit draw_cable (v3.1)'),
             ('cable_overhead x5', 'dia 0.08, sag 0.5', '-', 'cap rim to rack tops'),
             ('console x2', '2 x 1 x 1.3 + screen', '1 x 0.5 x 0.65', 'kit console, face the tank'),
             ('hazard_ring', 'decal dia 4.2', '2.1', 'amber, dashed')]
    px, py = 1500, 720
    d.text((px, py), 'PARTS', font=AF(34), fill=RIM)
    hdr = ('part', 'size (cells / kit m)', 'BU', 'note')
    xs_ = (px, px + 230, px + 560, px + 760)
    for k, h_ in enumerate(hdr):
        d.text((xs_[k], py + 50), h_, font=MF(20), fill=CYN)
    for i, row in enumerate(parts):
        y = py + 84 + i * 36
        if i % 2 == 0:
            d.rectangle((px - 8, y - 4, Wd - 30, y + 30), fill=(22, 24, 32))
        for k, t in enumerate(row):
            d.text((xs_[k], y), t, font=PF(20), fill=(225, 228, 236) if k == 0 else (190, 194, 206))
    d.text((40, 1440), 'Beaten state (T12): the same kit with the liquid emissive off, the eye and core dark, cables unlit (block_server_v2_beaten.png).', font=PF(22), fill=(190, 194, 206))
    return S_


if __name__ == '__main__':
    live, geo = build()
    live.save(OUT + 'block_server_v2.png')
    dead, _ = build(state='dead')
    dead.save(OUT + 'block_server_v2_beaten.png')
    kit_sheet(live, geo).save(OUT + 'block_server_kit.png')
    v6 = R + 'transitions/v6/plates/'
    if os.path.isdir(v6):
        shutil.copy(OUT + 'block_server_v2.png', v6 + 'room_block_server_v2.png')
        shutil.copy(OUT + 'block_server_v2_beaten.png', v6 + 'room_block_server_v2_beaten.png')
    print('ok')
