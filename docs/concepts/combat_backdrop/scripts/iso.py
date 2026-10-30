"""Isometric helpers shared by the cutaway and the x-ray backdrops."""
import math, random
from cel_lib import *

SC = 42.0
C = 0.866 * SC
N = 0.5 * SC
OX, OY = 1390.0, 536.0
INK = (5, 10, 14, 255)


def Pt(x, y, z):
    return (OX + (x - y) * C, OY + (x + y) * N - z * SC)


def face(img, pts3, fill, ink=INK, w=2.5):
    pts = [Pt(*p) for p in pts3]
    poly(img, pts, fill=fill, outline=ink, width=w)


def shade(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k), c[3] if len(c) > 3 else 255)


def box(img, x0, y0, z0, x1, y1, z1, base, ink=INK, w=2.5, top_k=1.25, left_k=0.62, right_k=0.82):
    """Visible faces only: +z top, +x right face, +y left face."""
    face(img, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], shade(base, top_k), ink, w)
    face(img, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], shade(base, right_k), ink, w)
    face(img, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], shade(base, left_k), ink, w)


def windows_on_face(img, axis, fixed, a0, a1, z0, z1, cols, rows, lit_col, p_lit=0.45, seed=0, pad=0.25):
    """Window grid on an +x face (axis='x', fixed x, varies y) or +y face (axis='y')."""
    rng = random.Random(seed)
    for i in range(cols):
        for j in range(rows):
            if rng.random() > p_lit:
                continue
            u0 = a0 + (a1 - a0) * (i + pad) / cols
            u1 = a0 + (a1 - a0) * (i + 1 - pad) / cols
            v0 = z0 + (z1 - z0) * (j + pad) / rows
            v1 = z0 + (z1 - z0) * (j + 1 - pad) / rows
            if axis == 'x':
                pts = [(fixed, u0, v0), (fixed, u1, v0), (fixed, u1, v1), (fixed, u0, v1)]
            else:
                pts = [(u0, fixed, v0), (u1, fixed, v0), (u1, fixed, v1), (u0, fixed, v1)]
            c = lit_col if rng.random() > 0.2 else (200, 170, 110, 255)
            poly(img, [Pt(*p) for p in pts], fill=c)


def cyl(img, x, y, z, r, h, body, liquid, cap=(34, 46, 46, 255), glass=(60, 120, 116, 255), ink=INK, frac=0.82):
    cx, cy = Pt(x, y, z)
    rx, ry = r * SC * 1.22, r * SC * 0.71
    hh = h * SC
    ellipse(img, [cx - rx * 1.2, cy - ry * 0.9, cx + rx * 1.2, cy + ry * 1.5], fill=(0, 0, 0, 110))
    rect(img, [cx - rx, cy - hh, cx + rx, cy], fill=glass)
    ellipse(img, [cx - rx, cy - ry, cx + rx, cy + ry], fill=glass)
    lt = cy - hh * frac
    rect(img, [cx - rx + 2, lt, cx + rx - 2, cy], fill=shade(liquid, 0.7))
    rect(img, [cx - rx * 0.6, lt, cx + rx * 0.15, cy], fill=liquid)
    rect(img, [cx - rx * 0.42, lt, cx - rx * 0.05, cy], fill=shade(liquid, 1.25))
    ellipse(img, [cx - rx + 2, lt - ry, cx + rx - 2, lt + ry], fill=shade(liquid, 1.3), outline=ink, width=2)
    ellipse(img, [cx - rx + 2, cy - ry, cx + rx - 2, cy + ry], fill=shade(liquid, 0.7))
    line(img, [cx - rx, cy - hh, cx - rx, cy], ink, 2.5)
    line(img, [cx + rx, cy - hh, cx + rx, cy], ink, 2.5)
    ellipse(img, [cx - rx, cy - ry, cx + rx, cy + ry], outline=ink, width=2.5)
    ellipse(img, [cx - rx * 1.05, cy - hh - ry, cx + rx * 1.05, cy - hh + ry], fill=cap, outline=ink, width=2.5)
    line(img, [cx - rx * 0.75, cy - hh * 0.9, cx - rx * 0.75, cy - hh * 0.1], (230, 255, 240, 110), 3)
