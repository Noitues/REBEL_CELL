"""HQ Solace v3: the frosted-glass interiors atlas (designer after t3: non-node windows get translucency, "frosted or
tinted glass with interior shapes visible behind it: lab benches, plants, figures, light fixtures").

python hq_glass_atlas.py [out.png]   (default D:/rc_scratch/hq_rev/solace/v3/glass_atlas.png; seed 6360)
4 x 4 tiles, each the window's 2.24 : 1 aspect: a frosted backlit pane (ceiling fixtures bright at the top, the glow
falling off down the room), the room's contents as soft silhouettes behind the frost (blurred = seen through it).
Rows: 0 labs (benches, glassware, figures), 1 greenhouse (plants, planters), 2 wards / offices (beds, desks, figures),
3 dim rooms (few lights, a figure or a plant). The build maps one tile per window (seeded) and tints it per window.
"""
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

TW, TH = 512, 228
N = 4
OUT = sys.argv[1] if len(sys.argv) > 1 else r"D:\rc_scratch\hq_rev\solace\v3\glass_atlas.png"
rr = random.Random(6360)


def figure(d, x, base, h, col):
    hw = h * 0.16
    d.ellipse([x - h * 0.09, base - h, x + h * 0.09, base - h * 0.80], fill=col)                     # head
    d.rounded_rectangle([x - hw, base - h * 0.78, x + hw, base - h * 0.30], radius=int(hw * 0.7), fill=col)   # torso
    d.rectangle([x - hw * 0.8, base - h * 0.32, x - hw * 0.15, base], fill=col)                       # legs
    d.rectangle([x + hw * 0.15, base - h * 0.32, x + hw * 0.8, base], fill=col)


def bench(d, x0, x1, top, base, col):
    d.rectangle([x0, top, x1, top + 7], fill=col)
    for x in (x0 + 6, x1 - 12):
        d.rectangle([x, top, x + 6, base], fill=col)
    for _ in range(rr.randint(2, 5)):                       # glassware on the bench
        gx = rr.uniform(x0 + 10, x1 - 10)
        gh = rr.uniform(10, 26)
        d.rounded_rectangle([gx - 4, top - gh, gx + 4, top], radius=3, fill=col)


def plant(d, x, base, s, col):
    d.rectangle([x - s * 0.25, base - s * 0.45, x + s * 0.25, base], fill=col)                          # pot
    for _ in range(rr.randint(5, 9)):
        ox, oy = rr.uniform(-s * 0.7, s * 0.7), rr.uniform(-s * 1.6, -s * 0.5)
        r = rr.uniform(s * 0.22, s * 0.42)
        d.ellipse([x + ox - r, base + oy - r, x + ox + r, base + oy + r], fill=col)


def fixture(d, x, w, y, col):
    d.rounded_rectangle([x - w / 2, y, x + w / 2, y + 6], radius=3, fill=col)


def tile(row, k):
    tints = [(225, 255, 235), (240, 250, 255), (255, 244, 222), (215, 255, 225)]
    bg = tints[(row + k) % 4]
    dim = 0.45 if row == 3 else rr.uniform(0.85, 1.0)
    im = Image.new("RGB", (TW, TH), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(TH):                                     # the room's light: bright under the fixtures, falling off
        k_ = dim * (1.0 - 0.55 * (y / TH) ** 1.3)
        d.line([(0, y), (TW, y)], fill=tuple(int(c * k_) for c in bg))
    sil = tuple(int(c * 0.30 * (0.7 if row == 3 else 1.0)) for c in bg)
    hot = (255, 255, 250)
    for _ in range(1 if row == 3 else rr.randint(2, 4)):
        fixture(d, rr.uniform(150, TW - 150), rr.uniform(70, 150), rr.uniform(34, 52), hot)   # inside the oval's top
    floor_y = TH - rr.uniform(18, 30)
    if row == 0:
        x = rr.uniform(20, 60)
        while x < TW - 120:
            w = rr.uniform(110, 170)
            bench(d, x, x + w, floor_y - rr.uniform(55, 70), floor_y, sil)
            x += w + rr.uniform(30, 70)
        for _ in range(rr.randint(1, 3)):
            figure(d, rr.uniform(40, TW - 40), floor_y, rr.uniform(105, 135), sil)
    elif row == 1:
        for _ in range(rr.randint(4, 7)):
            plant(d, rr.uniform(30, TW - 30), floor_y, rr.uniform(26, 48), sil)
        d.rectangle([0, floor_y - 18, TW, floor_y - 12], fill=sil)                                      # a planter rail
        if rr.random() < 0.6:
            figure(d, rr.uniform(60, TW - 60), floor_y, rr.uniform(105, 130), sil)
    elif row == 2:
        for _ in range(rr.randint(2, 3)):
            x = rr.uniform(20, TW - 160)
            d.rectangle([x, floor_y - 42, x + 140, floor_y - 30], fill=sil)                             # a bed / desk
            d.rectangle([x + 4, floor_y - 30, x + 10, floor_y], fill=sil)
            d.rectangle([x + 130, floor_y - 30, x + 136, floor_y], fill=sil)
            if rr.random() < 0.5:
                d.rectangle([x + 100, floor_y - 95, x + 104, floor_y - 42], fill=sil)                   # a drip stand
                d.ellipse([x + 94, floor_y - 104, x + 110, floor_y - 90], fill=sil)
        for _ in range(rr.randint(1, 2)):
            figure(d, rr.uniform(40, TW - 40), floor_y, rr.uniform(105, 135), sil)
    else:
        if rr.random() < 0.6:
            figure(d, rr.uniform(60, TW - 60), floor_y, rr.uniform(105, 130), sil)
        plant(d, rr.uniform(40, TW - 40), floor_y, rr.uniform(26, 40), sil)
    d.rectangle([0, floor_y, TW, TH], fill=tuple(int(c * 0.45) for c in sil))                          # the floor
    im = im.filter(ImageFilter.GaussianBlur(5.5))                                                      # the frost
    return im


atlas = Image.new("RGB", (TW * N, TH * N))
for row in range(N):
    for k in range(N):
        atlas.paste(tile(row, k), (k * TW, row * TH))
atlas.save(OUT)
print("atlas", OUT, atlas.size)
