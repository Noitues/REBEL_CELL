"""Pillow/numpy: the per-tile atlas cells (720 px, tile-local frame, see common.py).

Writes into WORK: exploit_scratch.png, zeroday_cracks.png, proxy_weave.png (R height,
G tow direction), patch_pcb.png (R traces, G pads, B tape), trojan_panel.png
(R panel groove + seam, G ribbon). Seeded, deterministic.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import common as C

N = C.TEX_PX
S = N / C.TEX_SIZE  # px per unit


def px(x, y):
    return ((x - C.TEX_X0) * S, (C.TEX_Y0 + C.TEX_SIZE - y) * S)


def save(img, name):
    os.makedirs(C.WORK, exist_ok=True)
    img.save(os.path.join(C.WORK, name))


def scratches():
    rng = np.random.default_rng(51)
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)
    for _ in range(130):
        x, y = rng.uniform(-1.8, 1.8), rng.uniform(1.0, 4.4)
        a = math.radians(rng.normal(24, 14))
        ln = rng.uniform(0.05, 0.9) if rng.random() < 0.85 else rng.uniform(0.9, 1.8)
        x2, y2 = x + math.cos(a) * ln, y + math.sin(a) * ln
        w = 1 if rng.random() < 0.8 else 2
        d.line([px(x, y), px(x2, y2)], fill=int(rng.uniform(60, 200)), width=w)
    # two deep crowbar gouges near the notch side
    for k in range(2):
        y0 = 3.0 + 0.16 * k
        d.line([px(0.25, y0 - 0.35), px(1.05, y0 + 0.08)], fill=255, width=4)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    save(im, "exploit_scratch.png")


def cracks():
    rng = np.random.default_rng(1337)
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)
    cx, cy = 0.42, 3.05  # impact point
    rays = []
    n = 11
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        pts = [(cx, cy)]
        x, y, r = cx, cy, 0.0
        while r < 3.2:
            step = rng.uniform(0.12, 0.3)
            a += rng.normal(0, 0.22)
            x, y = x + math.cos(a) * step, y + math.sin(a) * step
            r += step
            pts.append((x, y))
        rays.append(pts)
        d.line([px(*p) for p in pts], fill=255, width=2)
        # branch
        if len(pts) > 4:
            bx, by = pts[len(pts) // 3]
            ba = a + rng.choice([-1, 1]) * rng.uniform(0.5, 1.0)
            q = [(bx, by)]
            for _ in range(5):
                ba += rng.normal(0, 0.25)
                bx, by = bx + math.cos(ba) * 0.16, by + math.sin(ba) * 0.16
                q.append((bx, by))
            d.line([px(*p) for p in q], fill=190, width=2)
    # spider-web rings joining neighbouring rays
    for ring in (0.28, 0.62, 1.05):
        for i in range(n):
            if rng.random() < 0.25:
                continue
            p, q = rays[i], rays[(i + 1) % n]

            def at(pts, rr):
                acc = 0.0
                for k in range(1, len(pts)):
                    seg = math.dist(pts[k - 1], pts[k])
                    if acc + seg >= rr:
                        t = (rr - acc) / seg
                        return (pts[k - 1][0] + (pts[k][0] - pts[k - 1][0]) * t,
                                pts[k - 1][1] + (pts[k][1] - pts[k - 1][1]) * t)
                    acc += seg
                return pts[-1]
            a1, a2 = at(p, ring * rng.uniform(0.85, 1.15)), at(q, ring * rng.uniform(0.85, 1.15))
            mid = ((a1[0] + a2[0]) / 2 + rng.normal(0, 0.03), (a1[1] + a2[1]) / 2 + rng.normal(0, 0.03))
            d.line([px(*a1), px(*mid), px(*a2)], fill=210, width=2)
    d.ellipse([px(cx - 0.07, cy + 0.07), px(cx + 0.07, cy - 0.07)], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    save(im, "zeroday_cracks.png")


def weave():
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    x = xx / S + C.TEX_X0
    y = (C.TEX_Y0 + C.TEX_SIZE) - yy / S
    a = math.radians(45)
    p = x * math.cos(a) + y * math.sin(a)
    q = -x * math.sin(a) + y * math.cos(a)
    w = 0.11
    i = np.floor(p / w).astype(int)
    j = np.floor(q / w).astype(int)
    over = ((i + j) % 4) < 2  # 2x2 twill
    fp = (p / w) % 1.0
    fq = (q / w) % 1.0
    h_over = np.sin(np.pi * fq)  # tow running along p, rounded across q
    h_under = np.sin(np.pi * fp)
    h = np.where(over, h_over, h_under) ** 0.6
    rng = np.random.default_rng(9)
    fib = rng.normal(0, 1, (N, N)).astype(np.float32)
    fib = np.array(Image.fromarray(((fib * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    h = h * 0.85 + fib * 0.15
    r = (h.clip(0, 1) * 255).astype(np.uint8)
    g = np.where(over, 255, 0).astype(np.uint8)
    b = np.zeros_like(r)
    save(Image.fromarray(np.dstack([r, g, b]), "RGB"), "proxy_weave.png")


def pcb():
    rng = np.random.default_rng(404)
    tr = Image.new("L", (N, N), 0)
    pd = Image.new("L", (N, N), 0)
    dt, dp = ImageDraw.Draw(tr), ImageDraw.Draw(pd)
    wpx = int(0.035 * S)
    for k in range(15):
        x, y = rng.uniform(-1.6, 1.6), rng.uniform(1.1, 4.3)
        pts = [(x, y)]
        for _ in range(rng.integers(2, 5)):
            dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (0.7071, 0.7071), (-0.7071, 0.7071)]
            dx, dy = dirs[rng.integers(0, len(dirs))]
            ln = rng.uniform(0.2, 0.8)
            x, y = x + dx * ln, y + dy * ln
            pts.append((x, y))
        dt.line([px(*p) for p in pts], fill=255, width=wpx, joint="curve")
        for p in (pts[0], pts[-1]):
            r = 0.055 if rng.random() < 0.7 else 0.08
            dp.ellipse([px(p[0] - r, p[1] + r), px(p[0] + r, p[1] - r)], fill=255)
    # pad under the solder blob
    sx, sy, sr = C.SOLDER
    dp.ellipse([px(sx - sr * 1.25, sy + sr * 1.25), px(sx + sr * 1.25, sy - sr * 1.25)], fill=255)
    dt.line([px(sx, sy), px(sx, sy + 0.6), px(sx + 0.4, sy + 1.0)], fill=255, width=wpx)
    # green tape strip, slightly rotated, ragged ends
    tape = Image.new("L", (N, N), 0)
    dtp = ImageDraw.Draw(tape)
    a = math.radians(-14)
    c0 = (0.0, 3.3)
    hw, hl = 0.2, 2.2
    corners = []
    for sx_, sy_ in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)):
        corners.append((c0[0] + sx_ * math.cos(a) - sy_ * math.sin(a),
                        c0[1] + sx_ * math.sin(a) + sy_ * math.cos(a)))
    dtp.polygon([px(*p) for p in corners], fill=255)
    rgb = np.dstack([np.array(tr), np.array(pd), np.array(tape.filter(ImageFilter.GaussianBlur(0.8)))])
    save(Image.fromarray(rgb.astype(np.uint8), "RGB"), "patch_pcb.png")


def trojan():
    grv = Image.new("L", (N, N), 0)
    rib = Image.new("L", (N, N), 0)
    dg, dr = ImageDraw.Draw(grv), ImageDraw.Draw(rib)
    # seam along the axis (the panel splits here)
    dg.line([px(C.SEAM_X, C.R_IN + 0.32), px(C.SEAM_X, C.R_OUT - 0.2)], fill=255, width=4)
    # panel line: an arc near the outer edge and one near the inner edge
    for r in (C.R_OUT - 0.2, C.R_IN + 0.32):
        pts = [px(r * math.cos(t), r * math.sin(t))
               for t in np.linspace(math.radians(55), math.radians(125), 120)]
        dg.line(pts, fill=255, width=3)
    # ribbon band, tangential, with a fold
    y0, y1 = C.RIBBON_Y
    dr.rectangle([px(-1.8, y1), px(1.8, y0)], fill=255)
    rib = rib.filter(ImageFilter.GaussianBlur(1.2))
    grv = grv.filter(ImageFilter.GaussianBlur(0.6))
    rgb = np.dstack([np.array(grv), np.array(rib), np.zeros((N, N), np.uint8)])
    save(Image.fromarray(rgb, "RGB"), "trojan_panel.png")


def main():
    scratches()
    cracks()
    weave()
    pcb()
    trojan()
    print("textures ->", C.WORK)


if __name__ == "__main__":
    main()
