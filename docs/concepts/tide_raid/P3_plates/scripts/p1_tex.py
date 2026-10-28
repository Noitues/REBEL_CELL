"""P1 ribbon textures (RGBA, sRGB). u = along the street (tile LEN_BU), v = across. Casing is dark ink, core is the type hue,
pattern = the non-hue channel (D chain links, N braid, E hazard chevrons). python p1_tex.py -> WORK/tex/ribbon_{D,N,E}.png"""
import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
WORK = 'D:/rc_scratch/tide_concepts/p3_work/'
os.makedirs(WORK + 'tex', exist_ok=True)
TW, TH = 1024, 256          # tile px
LEN_BU = {'D': 16.0, 'N': 12.0, 'E': 16.0}
WID_BU = 4.0
SS = 3


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


COL = {'D': hexc('4690FF'), 'N': hexc('FF40D6'), 'E': hexc('FFEE3A')}
INK = hexc('070515')


def mk(typ):
    W, H = TW * SS, TH * SS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = COL[typ]
    cas = int(H * 0.085)                      # casing thickness
    # casing (ink) full width, then core inset
    d.rectangle([0, 0, W, H], fill=INK + (255,))
    core_y0, core_y1 = cas, H - cas
    if typ == 'D':
        # continuous azure band + dark cross-cuts (chain links) + a bright centre filament and chevrons
        d.rectangle([0, core_y0, W, core_y1], fill=col + (255,))
        link = W // 4                         # 4 links per tile
        for i in range(4):
            x0 = i * link
            d.rectangle([x0, core_y0, x0 + link * 0.07, core_y1], fill=INK + (255,))
            # link inner highlight
            d.rounded_rectangle([x0 + link * 0.14, core_y0 + H * .07, x0 + link * 0.90, core_y1 - H * .07], radius=H * .12, outline=tuple(int(c * .55 + 255 * .45) for c in col) + (255,), width=int(H * .035))
            # chevron
            cx = x0 + link * .52; cy = H / 2; s = H * .17
            d.line([(cx - s * .8, cy - s), (cx + s * .8, cy), (cx - s * .8, cy + s)], fill=INK + (255,), width=int(H * .07), joint='curve')
        d.rectangle([0, H * .46, W, H * .54], fill=tuple(int(c * .5 + 255 * .5) for c in col) + (120,))
    elif typ == 'N':
        d.rectangle([0, core_y0, W, core_y1], fill=tuple(int(c * .22) for c in col) + (255,))
        amp = (core_y1 - core_y0) * .32
        cy = H / 2
        per = W / 1.0
        pts_a, pts_b = [], []
        for x in range(0, W + 4, 4):
            ph = 2 * math.pi * x / (W / 1.0)
            pts_a.append((x, cy + amp * math.sin(ph)))
            pts_b.append((x, cy - amp * math.sin(ph)))
        # rungs between strands
        for x in range(0, W, W // 24):
            ph = 2 * math.pi * x / (W / 1.0)
            d.line([(x, cy + amp * math.sin(ph)), (x, cy - amp * math.sin(ph))], fill=tuple(int(c * .55) for c in col) + (255,), width=int(H * .03))
        for pts in (pts_a, pts_b):
            d.line(pts, fill=col + (255,), width=int(H * .15), joint='curve')
            d.line(pts, fill=tuple(int(c * .35 + 255 * .65) for c in col) + (255,), width=int(H * .05), joint='curve')
        # chevrons riding the centre
        for i in range(2):
            cx = W * (i + .5) / 2; s = H * .13
            d.line([(cx - s * .7, cy - s), (cx + s * .8, cy), (cx - s * .7, cy + s)], fill=(255, 255, 255, 255), width=int(H * .05), joint='curve')
    else:
        d.rectangle([0, core_y0, W, core_y1], fill=col + (255,))
        # hazard: diagonal ink bars forming bold chevrons
        n = 8
        step = W / n
        for i in range(n):
            x = i * step
            cy0, cy1 = core_y0, core_y1
            mid = H / 2
            bar = step * .34
            d.polygon([(x, cy0), (x + bar, cy0), (x + bar + (mid - cy0) * .55, mid), (x + bar, cy1), (x, cy1), (x + (mid - cy0) * .55, mid)], fill=INK + (255,))
        d.rectangle([0, H * .47, W, H * .53], fill=(255, 255, 255, 70))
    # inner rim lights on the casing edge (thin bright line just inside the casing)
    d.rectangle([0, cas - SS, W, cas], fill=tuple(int(c * .6 + 255 * .4) for c in col) + (255,))
    d.rectangle([0, H - cas, W, H - cas + SS], fill=tuple(int(c * .6 + 255 * .4) for c in col) + (255,))
    im = im.resize((TW, TH), Image.LANCZOS)
    im.save(WORK + 'tex/ribbon_%s.png' % typ)


for t in 'DNE':
    mk(t)
print('ok')


# ---------------------------------------------------------------- stop blocks (tier carrier on the street) and guard walls
TIERC = {'UNTOUCHED': 'B8FFF2', 'HOLDS': '19C9B4', 'SITES_LOST': 'C98410', 'DAMAGED': 'FF9A00', 'BREACHED': 'FF3347'}


def block_tex(tier):
    """u across the street, v along. Non-hue channel = hatch: HOLDS vertical bars, SITES LOST diagonal, DAMAGED chevrons, BREACHED crosshatch+border."""
    W_, H_ = 512 * SS, 192 * SS
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = hexc(TIERC[tier])
    d.rounded_rectangle([0, 0, W_ - 1, H_ - 1], radius=H_ * .12, fill=INK + (255,))
    b = int(H_ * .1)
    d.rounded_rectangle([b, b, W_ - b, H_ - b], radius=H_ * .08, fill=col + (255,))
    ink = INK + (255,)
    if tier == 'HOLDS':
        for i in range(10):
            x = b + (W_ - 2 * b) * (i + .5) / 10
            d.rectangle([x - W_ * .012, b, x + W_ * .012, H_ - b], fill=ink)
    elif tier == 'SITES_LOST':
        for i in range(-4, 16):
            x = i * W_ / 11
            d.polygon([(x, H_ - b), (x + W_ * .03, H_ - b), (x + W_ * .03 + H_ * .7, b), (x + H_ * .7, b)], fill=ink)
    elif tier == 'DAMAGED':
        for i in range(8):
            x = W_ * i / 8
            d.line([(x, b), (x + W_ * .06, H_ / 2), (x, H_ - b)], fill=ink, width=int(H_ * .12))
    elif tier == 'BREACHED':
        for i in range(-4, 18):
            x = i * W_ / 14
            d.line([(x, H_ - b), (x + H_ * .7, b)], fill=ink, width=int(H_ * .06))
            d.line([(x, b), (x + H_ * .7, H_ - b)], fill=ink, width=int(H_ * .06))
    else:
        for i in range(6):
            d.ellipse([W_ * (i + .5) / 6 - H_ * .1, H_ / 2 - H_ * .1, W_ * (i + .5) / 6 + H_ * .1, H_ / 2 + H_ * .1], fill=ink)
    im = im.resize((W_ // SS, H_ // SS), Image.LANCZOS)
    im.save(WORK + 'tex/block_%s.png' % tier)


def wall_tex(typ):
    """firewall: hex-brick lattice in the type hue on a faint pane, type glyph chip top-left."""
    W_, H_ = 512 * SS, 384 * SS
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = COL[typ]
    d.rectangle([0, 0, W_, H_], fill=col + (46,))
    r = W_ / 9
    hh = r * math.sqrt(3) / 2
    for row in range(-1, int(H_ / hh) + 2):
        for cc in range(-1, 12):
            cx = cc * r * 1.5
            cy = row * hh * 2 + (hh if cc % 2 else 0)
            pts = [(cx + r * .92 * math.cos(math.radians(60 * k)), cy + r * .92 * math.sin(math.radians(60 * k))) for k in range(6)]
            d.polygon(pts, outline=col + (255,), width=int(r * .09))
    d.rectangle([0, 0, W_ - 1, H_ - 1], outline=tuple(int(c * .5 + 127) for c in col) + (255,), width=int(H_ * .018))
    im = im.resize((W_ // SS, H_ // SS), Image.LANCZOS)
    im.save(WORK + 'tex/wall_%s.png' % typ)


for t in []:
    block_tex(t)
for t in 'DNE':
    wall_tex(t)


def hunter_tex():
    """white dashed street for the hunter's candidate routes."""
    W_, H_ = 512 * SS, 96 * SS
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(4):
        x = W_ * i / 4
        d.rectangle([x + W_ * .02, H_ * .18, x + W_ * .17, H_ * .82], fill=(244, 248, 255, 255))
    im = im.resize((W_ // SS, H_ // SS), Image.LANCZOS)
    im.save(WORK + 'tex/hunter.png')


hunter_tex()
