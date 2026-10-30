"""Backdrop 3 (alternative): X-RAY SCAN. The Cell's own jack-in view: the chosen building as a cyan holo wireframe
standing in the dimmed real city, the fight floor highlighted. Reads as the netrun made visible; near-monochrome
so the board's colours lead."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
from iso import *
import numpy as np
from bd_common import *

CY = (0, 229, 255)


def wire_box(L, x0, y0, z0, x1, y1, z1, a=255, w=3):
    pts = {}
    for i, x in enumerate((x0, x1)):
        for j, y in enumerate((y0, y1)):
            for k, z in enumerate((z0, z1)):
                pts[(i, j, k)] = Pt(x, y, z)
    edges = []
    for i in (0, 1):
        for j in (0, 1):
            edges.append(((i, j, 0), (i, j, 1)))
    for i in (0, 1):
        for k in (0, 1):
            edges.append(((i, 0, k), (i, 1, k)))
    for j in (0, 1):
        for k in (0, 1):
            edges.append(((0, j, k), (1, j, k)))
    for p, q in edges:
        line(L, [pts[p][0], pts[p][1], pts[q][0], pts[q][1]], CY + (a,), w)


def city_base():
    src = Image.open(R + 'docs/concepts/tide_raid/G1_parity/r42/plan_r42.png').convert('RGB')
    crop = src.crop((520, 200, 1400, 700)).resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    a = np.asarray(crop).astype(np.float32) / 255
    gray = a.mean(2, keepdims=True)
    a = gray + (a - gray) * 0.30
    tint = np.array([0.55, 0.85, 1.0], np.float32)
    a = (a * 0.55 + gray * tint * 0.45) * 0.42
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    d = np.hypot((xx - 1390) / 900, (yy - 600) / 600)
    a = a * (0.55 + 0.45 * np.exp(-d ** 2 * 1.5))[..., None]
    a[..., 2] += 0.03
    return a


def build():
    base = city_base()
    img = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8), 'RGB').convert('RGBA').resize((W * K, H * K), Image.BICUBIC)
    X, Y = 10.0, 10.0
    # ground footprint + ranging rings
    G = layer(W, H)
    for r_, al in ((6.5, 150), (8.5, 90), (11.0, 55)):
        pts = []
        for i in range(73):
            t = i / 72 * 6.283
            pts.append(Pt(5 + r_ * math.cos(t), 5 + r_ * math.sin(t), 0))
        line(G, [c for p in pts for c in p], CY + (al,), 2.5)
    poly(G, [Pt(0, 0, 0), Pt(X, 0, 0), Pt(X, Y, 0), Pt(0, Y, 0)], fill=CY + (22,), outline=CY + (200,), width=3)
    # floor slabs
    for f in range(4):
        z = 3.0 * f
        al = 150 if f in (1, 2) else 90
        poly(G, [Pt(0, 0, z), Pt(X, 0, z), Pt(X, Y, z), Pt(0, Y, z)], outline=CY + (al,), width=2.5)
    # the fight floor (z=3..6): highlighted slab, grid, schematic contents
    z = 3.0
    poly(G, [Pt(0, 0, z), Pt(X, 0, z), Pt(X, Y, z), Pt(0, Y, z)], fill=CY + (26,), outline=CY + (235,), width=4)
    for k in range(1, 10):
        a, b = Pt(k, 0, z), Pt(k, Y, z)
        line(G, [a[0], a[1], b[0], b[1]], CY + (60,), 1.5)
        a, b = Pt(0, k, z), Pt(X, k, z)
        line(G, [a[0], a[1], b[0], b[1]], CY + (60,), 1.5)
    for (x0, y0, x1, y1, h) in [(2.6, 0.2, 3.8, 1.1, 2.2), (4.4, 0.2, 5.6, 1.1, 2.2), (6.2, 0.2, 7.4, 1.1, 2.2), (8.0, 0.2, 9.2, 1.1, 2.2),
                                (3.6, 3.6, 6.2, 5.6, 0.9), (8.4, 6.8, 9.4, 8.9, 1.0), (5.6, 8.0, 7.2, 9.2, 0.7)]:
        wire_box(G, x0, y0, z, x1, y1, z + h, 190, 2.5)
    for yy in (1.8, 3.9, 6.0, 8.1):
        pts = []
        for i in range(25):
            t = i / 24 * 6.283
            pts.append(Pt(1.0 + 0.62 * math.cos(t), yy + 0.62 * math.sin(t), z))
        line(G, [c for p in pts for c in p], CY + (220,), 2.5)
        pts2 = [Pt(1.0 + 0.62 * math.cos(t / 24 * 6.283), yy + 0.62 * math.sin(t / 24 * 6.283), z + 2.4) for t in range(25)]
        line(G, [c for p in pts2 for c in p], CY + (220,), 2.5)
        for s_ in (0, 12):
            a, b = pts[s_], pts2[s_]
            line(G, [a[0], a[1], b[0], b[1]], CY + (160,), 2)
    # the whole tower, wire
    wire_box(G, 0, 0, 0, X, Y, 9.0, 235, 3)
    for zz in (3.0, 6.0):
        for (a, b) in [((0, 0), (X, 0)), ((X, 0), (X, Y)), ((X, Y), (0, Y)), ((0, Y), (0, 0))]:
            p, q = Pt(a[0], a[1], zz), Pt(b[0], b[1], zz)
            line(G, [p[0], p[1], q[0], q[1]], CY + (170,), 2.5)
    # scan plane sweeping through the fight floor
    zs = 4.6
    poly(G, [Pt(-1.5, -1.5, zs), Pt(X + 1.5, -1.5, zs), Pt(X + 1.5, Y + 1.5, zs), Pt(-1.5, Y + 1.5, zs)], fill=CY + (12,), outline=CY + (170,), width=2)
    # corner beams
    for (x, y) in [(0, 0), (X, 0), (X, Y), (0, Y)]:
        a, b = Pt(x, y, 0), Pt(x, y, 14)
        line(G, [a[0], a[1], b[0], b[1]], CY + (110,), 2)
    img2 = glow(img, G, 8, 0.6)
    img2.alpha_composite(G)
    # binary bit rain around the tower
    rng = random.Random(9)
    B = layer(W, H)
    f = font('mono', 18)
    d = draw(B)
    for i in range(170):
        x = rng.uniform(1000, 1900)
        y = rng.uniform(380, 900)
        al = int(rng.uniform(50, 190))
        d.text((x * K, y * K), rng.choice('01'), font=f, fill=CY + (al,), anchor='mm')
    img2 = glow(img2, B, 3, 0.8)
    img2.alpha_composite(B)
    return img2


def run():
    img = build()
    out = img.convert('RGB').resize((1920, 1080), Image.LANCZOS)
    a = np.asarray(out).astype(np.float32) / 255
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    vg = 1 - 0.40 * np.clip(np.hypot((xx - 1390) / 1000, (yy - 560) / 640) - 0.30, 0, 1)
    # scanlines
    sl = np.where((yy.astype(int) % 3) == 0, 0.9, 1.0).astype(np.float32)
    a = a * vg[..., None] * sl[..., None] * 0.80
    rng = np.random.default_rng(3)
    a += rng.normal(0, 0.010, a.shape).astype(np.float32)
    return np.clip(a, 0, 1)


if __name__ == '__main__':
    save(run(), SCR + 'bd3_xray_raw.png')
