"""Panel 7: combat-wheel frame mockup (2D, PIL) over the panel-6 street render.

python deco_panel7.py <street_plate.png> <out.png>
Runs the round-41 combat screen builder (round41_wheel_stack/scripts, read-only, copied to D:/rc_scratch/art_deco/p7 so no
cache or output lands in the repo) with its backdrop swapped for the deco street plate, then re-skins each wheel's frame:
brass bezel rings, a sunburst of rays at the 30 ticks, chevron tick marks and a stepped hub collar. The slices stay the
CRT "Screens & Data" art of the base screen and the live numbers stay the base's bare Anton.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P7 = r"D:/rc_art/art-pass/docs/concepts/round41_wheel_stack"
SRC = r"D:/rc_art/art-pass/docs/concepts"
sys.dont_write_bytecode = True
sys.path.insert(0, P7 + "/scripts")
# the copy needs the sibling round folders the scripts read (assets, fonts, fixtures): link by junction-free copy on demand
os.chdir(P7 + "/scripts")

import combat41 as C41  # noqa: E402

W, H = 1920, 1080
GOLD = (255, 190, 80)
BRASS = (196, 132, 44)
DEEP = (60, 38, 12)


def street_backdrop(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pool = np.zeros((H, W), np.float32)
    for wh in (C41.PLAYER, C41.BOSS):
        q = np.hypot(xx - wh["c"][0], yy - wh["c"][1]) / (wh["r"] * 1.3)
        pool = np.maximum(pool, np.exp(-q ** 4))
    dim = 0.85 * (1 - 0.55 * pool)
    dim *= 1 - 0.5 * np.clip((yy - 800) / 260, 0, 1)
    soft = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.0)), np.float32)
    a = a * (1 - 0.6 * pool[..., None]) + soft * 0.6 * pool[..., None]
    clean = Image.fromarray(np.clip(a * dim[..., None], 0, 255).astype(np.uint8))
    return clean, clean.copy()


def deco_wheel(img, c, r, accent):
    """Deco frame on one wheel: concentric brass rings, 30 sunburst rays with chevron ticks, stepped hub collar."""
    S = 3
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = c[0] * S, c[1] * S
    R = r * S

    def ring(rr, w, col, a=255):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col + (a,), width=int(w))

    # outer stepped bezel (3 steps), brass with gold edges
    for k, (dr, w, col) in enumerate(((1.20, 22, BRASS), (1.15, 9, GOLD), (1.11, 4, accent), (1.09, 4, accent), (1.06, 12, BRASS),
                                      (1.03, 4, GOLD))):
        ring(R * dr, w * S / 3, col)
    # 30 tick rays: long ray every 5th, pairs of thin parallel lines between; chevron at each 5th
    for k in range(30):
        a = math.radians(k * 12.0 - 90)
        ca, sa = math.cos(a), math.sin(a)
        long_ = k % 5 == 0
        r0, r1 = R * 1.205, R * (1.52 if long_ else 1.31)
        for off in ((-0.012, 0.012) if long_ else (0.0,)):
            b = a + off
            d.line([(cx + math.cos(b) * r0, cy + math.sin(b) * r0), (cx + math.cos(b) * r1, cy + math.sin(b) * r1)],
                   fill=(GOLD if long_ else BRASS) + (230,), width=int(9 * S / 3 if long_ else 5 * S / 3))
        if long_:
            for dr in (1.34, 1.40):                                      # a chevron V on the ray
                p = R * dr
                tip = (cx + ca * (p + 18 * S / 3), cy + sa * (p + 18 * S / 3))
                l = (cx + math.cos(a - 0.05) * p, cy + math.sin(a - 0.05) * p)
                rr_ = (cx + math.cos(a + 0.05) * p, cy + math.sin(a + 0.05) * p)
                d.line([l, tip, rr_], fill=accent + (255,), width=int(3 * S / 3))
        # tick mark on the bezel (chevron-like short bar)
        t0, t1 = R * 1.22, R * 1.26
        d.line([(cx + ca * t0, cy + sa * t0), (cx + ca * t1, cy + sa * t1)], fill=GOLD + (255,), width=int(4 * S / 3))
    layer = layer.resize((W, H), Image.LANCZOS)
    glow = layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(Image.merge("RGBA", (*glow.split()[:3], glow.split()[3].point(lambda v: int(v * 0.5)))))
    img.alpha_composite(layer)
    # stepped hub collar over the centre (3 gold rings), kept small so the hub name still reads
    d2 = ImageDraw.Draw(img)
    for dr, w, col in ((0.285, 4, GOLD), (0.27, 2, BRASS), (0.30, 2, accent)):
        rr = r * dr
        d2.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], outline=col + (255,), width=w)


def slice_colours(img, c, r):
    a = np.asarray(img.convert("RGB"), np.float32)
    out = []
    for k in range(6):
        ang = math.radians(-90 + 60 * k)
        pts = []
        for da in (-14, -7, 0, 7, 14):
            for rr in (0.5, 0.62, 0.74):
                aa = ang + math.radians(da)
                x, y = int(c[0] + math.cos(aa) * r * rr), int(c[1] + math.sin(aa) * r * rr)
                pts.append(a[y, x])
        p = np.array(pts)
        v = p[np.argsort(p.max(axis=1) - p.min(axis=1))[-8:]].mean(axis=0)     # the most saturated samples
        v = v / max(v.max(), 1.0) * 255.0
        out.append(tuple(int(min(255, x * 1.15)) for x in v))
    return out


def arc_poly(cx, cy, r0, r1, a0, a1, n=24):
    pts = [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * r1, cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * r1) for i in range(n + 1)]
    pts += [(cx + math.cos(math.radians(a1 - (a1 - a0) * i / n)) * r0, cy + math.sin(math.radians(a1 - (a1 - a0) * i / n)) * r0) for i in range(n + 1)]
    return pts


def deco_slices(img, c, r, accent, cols):
    """Variant B: each slice becomes a fan-shaped black-lacquer panel. The CRT art and glyphs stay (the lacquer is a
    gradient plus a gloss streak at the slice edges, not a fill), gold inlay edges, three setback steps on the outer edge,
    the slice colour as two thin parallel neon arcs; a stepped sunburst medallion round the hub; a gold spire pointer."""
    S = 3
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, R = c[0] * S, c[1] * S, r * S
    for k in range(6):
        mid = -90 + 60 * k
        col = cols[k]
        # lacquer shading at the slice edges and outer rim (translucent black wedges, strongest at the edges)
        for j, (da, al) in enumerate(((30, 150), (27, 110), (24, 70), (21, 35))):
            d.polygon(arc_poly(cx, cy, R * 0.34, R * 0.93, mid - 30, mid - 30 + (30 - da) + 6 + j * 0, 10), fill=(0, 0, 0, 0))
        # gold inlay on both radial edges: a thick line + a thin neon pair either side
        for e in (mid - 30, mid + 30):
            ea = math.radians(e)
            ca, sa = math.cos(ea), math.sin(ea)
            nx, ny = -sa, ca
            r0, r1 = R * 0.345, R * 0.935
            for off, w, fill in ((0, 5, GOLD + (255,)), (-9, 2, col + (255,)), (9, 2, col + (255,)), (-15, 2, GOLD + (200,)), (15, 2, GOLD + (200,))):
                d.line([(cx + ca * r0 + nx * off * S / 3 * (1 if e > mid else -1) * -1, cy + sa * r0 + ny * off * S / 3 * (1 if e > mid else -1) * -1),
                        (cx + ca * r1 + nx * off * S / 3 * (1 if e > mid else -1) * -1, cy + sa * r1 + ny * off * S / 3 * (1 if e > mid else -1) * -1)],
                       fill=fill, width=int(w * S / 3 * 1.6))
        # stepped (setback) outer edge: three gold arcs, each ~80 % of the span below it, with colour arcs between
        span = 29.0
        for i, rr in enumerate((0.935, 0.962, 0.988)):
            d.polygon(arc_poly(cx, cy, R * rr, R * (rr + 0.012), mid - span, mid + span), fill=GOLD + (255,))
            d.polygon(arc_poly(cx, cy, R * (rr - 0.011), R * (rr - 0.003), mid - span * 0.95, mid + span * 0.95), fill=col + (255,))
            span *= 0.8
        # chevron at the centre of the outer edge
        ang = math.radians(mid)
        p = R * 1.012
        tip = (cx + math.cos(ang) * (p + 14 * S), cy + math.sin(ang) * (p + 14 * S))
        l = (cx + math.cos(ang - 0.05) * p, cy + math.sin(ang - 0.05) * p)
        rr_ = (cx + math.cos(ang + 0.05) * p, cy + math.sin(ang + 0.05) * p)
        d.line([l, tip, rr_], fill=col + (255,), width=3 * S)
    # hub: stepped sunburst medallion (rays between r 0.34 and 0.42 R, stepped rings)
    for k in range(48):
        a = math.radians(k * 7.5)
        r0, r1 = R * 0.335, R * (0.43 if k % 2 == 0 else 0.385)
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=GOLD + (255,), width=2 * S)
    for rr, w, col in ((0.33, 4, GOLD), (0.345, 2, accent), (0.44, 3, BRASS), (0.452, 2, GOLD)):
        d.ellipse([cx - R * rr, cy - R * rr, cx + R * rr, cy + R * rr], outline=col + (255,), width=w * S // 1)
    layer = layer.resize((W, H), Image.LANCZOS)
    glow = layer.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(Image.merge("RGBA", (*glow.split()[:3], glow.split()[3].point(lambda v: int(v * 0.45)))))
    img.alpha_composite(layer)
    # needle: a gold deco spire pointer over the top tab (stepped, with a neon core)
    d2 = ImageDraw.Draw(img)
    x, y = c[0], c[1] - r * 1.17
    for i, (wd, h, col) in enumerate(((16, 16, BRASS), (11, 14, GOLD), (6, 14, (255, 235, 170)))):
        d2.polygon([(x - wd, y - 4 + i * 11 + h), (x + wd, y - 4 + i * 11 + h), (x, y - 4 + i * 11 - 8)], fill=col + (255,))


def main():
    plate, out = sys.argv[1], sys.argv[2]
    _orig = C41.base_plate
    _jpg = _orig()[1]
    C41.base_plate = lambda: (street_backdrop(plate)[0], _jpg)
    import combat44 as C44
    shot, off, hits = C44.screen(False, hover=None)
    shot = shot.convert("RGBA")
    keep = shot.copy()
    base = shot.copy()
    deco_wheel(shot, C41.PLAYER["c"], C41.PLAYER["r"], (255, 61, 168))
    deco_wheel(shot, C41.BOSS["c"], C41.BOSS["r"], (255, 140, 26))
    for bx in ((1236, 726, 1602, 892), (370, 776, 570, 850), (1360, 860, 1790, 940)):
        shot.paste(keep.crop(bx), bx[:2])
    shot.convert("RGB").save(out)
    # variant B: the slices too (on the unframed screen, slice colours sampled from it)
    b = base.copy()
    for wh, acc in ((C41.PLAYER, (255, 61, 168)), (C41.BOSS, (255, 140, 26))):
        cols = slice_colours(base, wh["c"], wh["r"])
        deco_slices(b, wh["c"], wh["r"], acc, cols)
        deco_wheel(b, wh["c"], wh["r"], acc)
    for bx in ((1236, 726, 1602, 892), (370, 776, 570, 850), (1360, 860, 1790, 940)):
        b.paste(keep.crop(bx), bx[:2])
    b.convert("RGB").save(out.replace(".png", "_B.png"))
    print("panel7", out, "off-screen %.1f" % off)


if __name__ == "__main__":
    main()
