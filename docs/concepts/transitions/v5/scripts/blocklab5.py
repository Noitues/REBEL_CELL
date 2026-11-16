"""BLOCK SERVER room plate (transitions v5, B-105 ruling 5): an enhanced bio lab, a giant glowing tank in the centre,
cables from the tank to server racks round the edge ("experimenting on something big").
2D drawing (PIL + numpy) over the v3.1 bio cutaway (combat_backdrop/v3_1/room_bio_bare.png): the street, the building,
the SOLACE signage and the cutaway box geometry stay; the interior is redrawn. Solace palette (STYLE_GUIDE:
corp_solace #3DFF8B, net_cyan #5CE1FF, cell rims as the v3.1 kit).
Run: python <repo>/docs/concepts/transitions/v5/scripts/blocklab5.py   (writes v5/plates/room_block_server.png)."""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers5 import R, MF

OUT = R + 'transitions/v5/plates/'
SOL = (61, 255, 139); CYN = (92, 225, 255); RIM = (150, 255, 70); PNK = (255, 61, 168); AMBR = (255, 176, 0)

# cutaway box, measured on the v3.1 plates (bio and srv share it): back floor corner, the two floor edges, wall height
B = np.array([1467.0, 505.0]); A_ = np.array([-260.0, 125.0]); B_ = np.array([316.0, 178.0]); WALL = 152


def P(u, v, h=0.0):
    p = B + u * A_ + v * B_
    return (float(p[0]), float(p[1] - h))


def poly(d, pts, fill=None, outline=None, width=1):
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=width, joint='curve')


def box(d, u0, u1, v0, v1, h, top, fu, fv, edge=(8, 12, 18), w=2, h0=0.0):
    """iso box on the floor: +u face (toward the left cut edge), +v face (toward the right cut edge), top."""
    poly(d, [P(u1, v0, h0), P(u1, v1, h0), P(u1, v1, h), P(u1, v0, h)], fu, edge, w)
    poly(d, [P(u0, v1, h0), P(u1, v1, h0), P(u1, v1, h), P(u0, v1, h)], fv, edge, w)
    poly(d, [P(u0, v0, h), P(u1, v0, h), P(u1, v1, h), P(u0, v1, h)], top, edge, w)


def leds(d, u0, u1, v0, v1, h, rng, face='u'):
    """LED strips on a rack's visible face (rows of short bars)."""
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


def build(src=R + 'combat_backdrop/v3_1/room_bio_bare.png', state='live'):
    """state 'live' (the tank glows) or 'dead' (BLOCK SERVER beaten: the tank goes dark, cables cut)."""
    rng = random.Random(105)
    base = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
    im = base.copy(); d = ImageDraw.Draw(im)
    live = state == 'live'
    # ---- walls (left wall along u at v=0, right wall along v at u=0) and floor
    wl = [P(0, 0, 0), P(1, 0, 0), P(1, 0, WALL), P(0, 0, WALL)]
    wr = [P(0, 0, 0), P(0, 1, 0), P(0, 1, WALL), P(0, 0, WALL)]
    poly(d, wl, (20, 50, 50)); poly(d, wr, (16, 42, 46))
    for k in range(1, 12):   # wall panel seams
        d.line((P(k / 12, 0, 0), P(k / 12, 0, WALL)), fill=(12, 34, 36), width=2)
        d.line((P(0, k / 12, 0), P(0, k / 12, WALL)), fill=(10, 30, 34), width=2)
    for hh, col in ((WALL - 14, RIM), (62, (40, 120, 110))):
        d.line((P(0, 0, hh), P(1, 0, hh)), fill=col, width=3); d.line((P(0, 0, hh), P(0, 1, hh)), fill=col, width=3)
    fl = [P(0, 0), P(1, 0), P(1, 1), P(0, 1)]
    poly(d, fl, (22, 64, 54))
    for k in range(1, 7):
        d.line((P(k / 7, 0), P(k / 7, 1)), fill=(30, 84, 70), width=2)
    for k in range(1, 9):
        d.line((P(0, k / 9), P(1, k / 9)), fill=(30, 84, 70), width=2)
    # ---- floor glow pool round the tank
    TU, TV = .52, .5
    cx, cy = P(TU, TV)
    RX, RY, TH = 104, 54, 345
    g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    if live:
        gd.ellipse(ell(cx, cy, RX * 2.6, RY * 2.6), fill=(20, 110, 60))
        g = g.filter(ImageFilter.GaussianBlur(40)); im = add_glow(im, g, .9); d = ImageDraw.Draw(im)
    # hazard ring on the floor
    d.ellipse(ell(cx, cy, RX * 1.75, RY * 1.75), outline=(AMBR if live else (110, 90, 40)), width=4)
    for k in range(24):
        a = k / 24 * math.tau
        if k % 2 == 0:
            d.arc(ell(cx, cy, RX * 1.62, RY * 1.62), math.degrees(a), math.degrees(a) + 7, fill=(30, 30, 30), width=6)

    # ---- server racks round the edge (back-left wall, back-right wall, right end)
    racks = []
    for i in range(5):
        u0 = .08 + i * .17; racks.append((u0, u0 + .12, .02, .13, rng.choice([118, 132, 140])))
    for i in range(5):
        v0 = .16 + i * .15; racks.append((.02, .14, v0, v0 + .11, rng.choice([118, 132, 140])))
    racks.sort(key=lambda r: r[1] + r[3])
    # cables on the floor first (under racks and tank)
    cab = []
    for (u0, u1, v0, v1, h) in racks:
        ru, rv = (u0 + u1) / 2, (v0 + v1) / 2
        cab.append((ru, rv))
    for k, (ru, rv) in enumerate(cab):
        ang = math.atan2(rv - TV, ru - TU)
        su, sv = TU + math.cos(ang) * .17, TV + math.sin(ang) * .17
        mu, mv = (su + ru) / 2 + .04 * math.sin(k * 1.7), (sv + rv) / 2 + .04 * math.cos(k * 1.3)
        pts = []
        for t in np.linspace(0, 1, 24):
            uu = (1 - t) ** 2 * su + 2 * (1 - t) * t * mu + t * t * ru
            vv = (1 - t) ** 2 * sv + 2 * (1 - t) * t * mv + t * t * rv
            pts.append(P(uu, vv))
        d.line(pts, fill=(6, 10, 14), width=11, joint='curve')
        d.line(pts, fill=(CYN if k % 3 else SOL) if live else (40, 60, 64), width=3, joint='curve')
    # back racks (drawn before the tank: they sit behind it)
    def draw_rack(r):
        u0, u1, v0, v1, h = r
        box(d, u0, u1, v0, v1, h, (34, 46, 58), (18, 24, 34), (24, 32, 44))
        if live:
            leds(d, u0, u1, v0, v1, h, rng, 'u'); leds(d, u0, u1, v0, v1, h, rng, 'v')
        else:
            leds(d, u0, u1, v0, v1, h, random.Random(1), 'u')
        d.line((P(u0, v1, h), P(u1, v1, h), P(u1, v0, h)), fill=(90, 200, 190) if live else (60, 80, 80), width=2)
    for r in racks:
        draw_rack(r)
    # wall-top rims sit behind the tank
    for a, b in ((P(0, 0, WALL), P(1, 0, WALL)), (P(0, 0, WALL), P(0, 1, WALL))):
        d.line((a, b), fill=RIM, width=5)

    # ---- the tank: plinth, glass column, specimen, bands, cap, pipes
    def cyl(d_, cx_, top_y, bot_y, rx, ry, side, top, edge=(8, 12, 18)):
        d_.rectangle((cx_ - rx, top_y, cx_ + rx, bot_y), fill=side)
        d_.ellipse(ell(cx_, bot_y, rx, ry), fill=side)
        d_.line((cx_ - rx, top_y, cx_ - rx, bot_y), fill=edge, width=3); d_.line((cx_ + rx, top_y, cx_ + rx, bot_y), fill=edge, width=3)
        d_.arc(ell(cx_, bot_y, rx, ry), 0, 180, fill=edge, width=3)
        d_.ellipse(ell(cx_, top_y, rx, ry), fill=top, outline=edge, width=3)
    PL = 34
    cyl(d, cx, cy - PL, cy, RX + 26, RY + 14, (30, 40, 46), (52, 66, 72))
    for k in range(10):   # plinth lights
        a = math.pi * (k + .5) / 10
        x = cx - math.cos(a) * (RX + 26); y = cy - PL / 2 + math.sin(a) * (RY + 14) * .9
        d.rectangle((x - 4, y - 3, x + 4, y + 3), fill=SOL if live else (50, 70, 60))
    gt, gb = cy - PL - TH, cy - PL - 6
    # glass with liquid: horizontal cylinder shading
    col = Image.new('RGB', (2 * RX + 1, int(gb - gt) + RY + 1), (0, 0, 0))
    xs = np.linspace(-1, 1, 2 * RX + 1)
    shade = np.sqrt(np.clip(1 - xs ** 2, 0, 1))
    if live:
        c0, c1 = np.array([8, 70, 40]), np.array(SOL)
    else:
        c0, c1 = np.array([10, 22, 18]), np.array([40, 70, 56])
    rows = col.height
    yy = np.linspace(0, 1, rows)[:, None]
    tone = (.35 + .65 * shade[None, :]) * (0.75 + .25 * (1 - yy))
    arr = c0[None, None, :] + (c1 - c0)[None, None, :] * tone[..., None]
    col = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    m = Image.new('L', col.size, 0); md = ImageDraw.Draw(m)
    md.rectangle((0, 0, col.width, rows - RY), fill=255); md.ellipse((0, rows - 2 * RY - 1, col.width - 1, rows - 1), fill=255)
    im.paste(col, (int(cx - RX), int(gt)), m); d = ImageDraw.Draw(im)
    # the specimen: a huge curled silhouette, umbilical tubes from the cap
    sp = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sp)
    dark = (4, 26, 16, 240) if live else (4, 12, 10, 245)
    sd.ellipse(ell(cx + 8, gt + TH * .56, RX * .80, TH * .25), fill=dark)          # body, curled
    sd.ellipse(ell(cx - 22, gt + TH * .27, RX * .55, TH * .15), fill=dark)         # head
    sd.ellipse(ell(cx + 38, gt + TH * .40, RX * .45, TH * .14), fill=dark)         # shoulder
    sd.polygon([(cx - 60, gt + TH * .30), (cx - 92, gt + TH * .16), (cx - 40, gt + TH * .22)], fill=dark)  # horn / fin
    for k, (ox, ln) in enumerate(((-46, .22), (-14, .26), (22, .24), (54, .20))):   # tendrils
        pts = [(cx + ox + 10 * math.sin(t * 6 + k), gt + TH * (.74 + ln * t)) for t in np.linspace(0, 1, 12)]
        sd.line(pts, fill=dark, width=16 - 2 * k, joint='curve')
    for k, ox in enumerate((-30, 0, 30)):                                            # tubes from the cap
        sd.line([(cx + ox, gt + 2), (cx + ox * .6 + 6, gt + TH * .12), (cx - 10 + ox * .3, gt + TH * .26)], fill=(10, 40, 30, 230), width=6, joint='curve')
    if live:
        sd.ellipse(ell(cx - 40, gt + TH * .26, 11, 7), fill=(255, 90, 190, 255))    # one eye, lit
        sd.ellipse(ell(cx + 12, gt + TH * .56, 16, 11), fill=(255, 61, 168, 150))   # core
        sd.ellipse(ell(cx + 12, gt + TH * .56, 7, 5), fill=(255, 170, 220, 255))
    im = Image.alpha_composite(im.convert('RGBA'), sp).convert('RGB'); d = ImageDraw.Draw(im)
    # bubbles
    for k in range(40):
        x = cx + rng.uniform(-RX * .85, RX * .85); y = rng.uniform(gt + 20, gb - 10); r = rng.choice([2, 3, 3, 4, 6])
        if live:
            d.ellipse(ell(x, y, r, r), outline=(210, 255, 225), width=1 if r < 4 else 2)
    # glass highlights, rims, bands
    d.line((cx - RX * .55, gt + 14, cx - RX * .55, gb - 8), fill=(220, 255, 235) if live else (90, 110, 100), width=6)
    d.line((cx - RX * .38, gt + 30, cx - RX * .38, gb - 30), fill=(170, 240, 200) if live else (70, 90, 80), width=2)
    d.line((cx + RX * .7, gt + 20, cx + RX * .7, gb - 20), fill=(120, 230, 170) if live else (50, 70, 60), width=2)
    d.line((cx - RX, gt, cx - RX, gb), fill=(10, 20, 18), width=4); d.line((cx + RX, gt, cx + RX, gb), fill=(10, 20, 18), width=4)
    for hb in (gt + TH * .34, gt + TH * .68):
        d.rectangle((cx - RX - 4, hb - 7, cx + RX + 4, hb + 7), fill=(44, 56, 62))
        d.arc(ell(cx, hb + 7, RX + 4, RY), 0, 180, fill=(10, 14, 18), width=3)
        d.arc(ell(cx, hb - 7, RX + 4, RY), 0, 180, fill=(80, 100, 108), width=2)
        for k in range(5):
            x = cx - RX + 18 + k * (2 * RX - 36) / 4
            d.rectangle((x - 4, hb - 3, x + 4, hb + 3), fill=SOL if live else (40, 60, 50))
    d.arc(ell(cx, gb, RX, RY), 0, 180, fill=(10, 20, 18), width=4)
    # cap and pipes
    CAP = 46
    cyl(d, cx, gt - CAP, gt + 4, RX + 14, RY + 8, (40, 52, 58), (62, 78, 86))
    for k in range(8):
        a = math.pi * (k + .5) / 8
        x = cx - math.cos(a) * (RX + 14); y = gt - CAP / 2 + math.sin(a) * (RY + 8) * .7
        d.line((x, y - 14, x, y + 14), fill=(20, 26, 30), width=3)
    d.ellipse(ell(cx, gt - CAP, RX * .5, RY * .5), fill=(30, 38, 44), outline=(8, 12, 18), width=3)
    for ox in (-34, 0, 34):
        d.rectangle((cx + ox - 9, 0, cx + ox + 9, gt - CAP), fill=(28, 36, 42), outline=(8, 12, 18), width=2)
        d.line((cx + ox - 3, 0, cx + ox - 3, gt - CAP), fill=(70, 90, 96), width=2)
    # overhead cables: tank cap to each rack top, sagging
    for k, (u0, u1, v0, v1, h) in enumerate(racks):
        tx, ty = P((u0 + u1) / 2, (v0 + v1) / 2, h)
        sx, sy = cx + (RX + 10) * (1 if tx > cx else -1) * .8, gt - CAP * .4 + (k % 3) * 9
        sag = 40 + 20 * (k % 3)
        pts = [(sx + (tx - sx) * t, sy + (ty - sy) * t + sag * math.sin(math.pi * t)) for t in np.linspace(0, 1, 20)]
        d.line(pts, fill=(8, 10, 14), width=7, joint='curve')
        if live and k % 2 == 0:
            d.line(pts, fill=CYN if k % 4 == 0 else SOL, width=2, joint='curve')
    # two lab consoles facing the tank (dark benches, lit screens)
    for (u0, v0) in ((.80, .26), (.74, .66)):
        box(d, u0, u0 + .09, v0, v0 + .13, 38, (60, 76, 84), (30, 40, 48), (40, 52, 60))
        a, b, c_, e = P(u0 + .02, v0 + .02, 44), P(u0 + .02, v0 + .11, 44), P(u0 + .02, v0 + .11, 74), P(u0 + .02, v0 + .02, 74)
        poly(d, [a, b, c_, e], CYN if live else (30, 50, 60), (8, 12, 18), 2)
    # ---- tank glow over everything (additive)
    if live:
        g = Image.new('RGB', im.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rectangle((cx - RX, gt, cx + RX, gb), fill=(20, 120, 60))
        g = g.filter(ImageFilter.GaussianBlur(46))
        ImageDraw.Draw(g).rectangle((cx - RX + 6, gt + 6, cx + RX - 6, gb), fill=(0, 0, 0))   # keep the specimen dark
        im = add_glow(im, g.filter(ImageFilter.GaussianBlur(4)), .8)
    d = ImageDraw.Draw(im)
    # cutaway rims: wall tops and the cut floor edges (lime, as the v3.1 kit)
    for a, b in ((P(1, 0, 0), P(1, 1, 0)), (P(0, 1, 0), P(1, 1, 0)),
                 (P(1, 0, 0), P(1, 0, WALL)), (P(0, 1, 0), P(0, 1, WALL))):
        d.line((a, b), fill=RIM, width=5)
    d.line((P(0, 0, 0), P(0, 0, WALL)), fill=(12, 30, 30), width=3)
    # label tag on the cap (small, Share Tech style mono)
    d.text((cx - 60, gt - CAP - 30), 'SPECIMEN 0', font=MF(18), fill=(200, 255, 220) if live else (120, 140, 130))
    return im.filter(ImageFilter.GaussianBlur(.5))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build().save(OUT + 'room_block_server.png')
    build(state='dead').save(OUT + 'room_block_server_beaten.png')
    print('ok')
