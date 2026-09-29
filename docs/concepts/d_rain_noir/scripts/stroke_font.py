"""Single-stroke capital font for the pink marker (Grease Pencil) and neon tubes (bevelled curves).

Glyphs live in a unit box (height 1, y up). Each glyph: (width, [(smooth, [(x, y), ...]), ...]).
Stroke order inside a glyph is the write-on order.
"""
import math, random
from mathutils import Vector

G = {
    "S": (0.85, [(1, [(0.8, 0.84), (0.55, 0.99), (0.22, 0.95), (0.07, 0.77), (0.17, 0.58), (0.47, 0.5), (0.76, 0.4), (0.85, 0.2), (0.64, 0.03), (0.3, 0.01), (0.04, 0.16)])]),
    "E": (0.78, [(0, [(0.76, 1.0), (0.05, 1.0), (0.05, 0.0), (0.8, 0.0)]), (0, [(0.05, 0.52), (0.6, 0.52)])]),
    "F": (0.74, [(0, [(0.76, 1.0), (0.05, 1.0), (0.05, 0.0)]), (0, [(0.05, 0.52), (0.6, 0.52)])]),
    "N": (0.82, [(0, [(0.05, 0.0), (0.05, 1.0), (0.77, 0.0), (0.77, 1.0)])]),
    "D": (0.84, [(0, [(0.06, 0.0), (0.06, 1.0)]), (1, [(0.06, 1.0), (0.45, 0.97), (0.74, 0.76), (0.8, 0.45), (0.66, 0.15), (0.36, 0.02), (0.05, 0.0)])]),
    "I": (0.26, [(0, [(0.12, 1.0), (0.12, 0.0)])]),
    "T": (0.82, [(0, [(0.0, 1.0), (0.82, 1.0)]), (0, [(0.41, 1.0), (0.41, 0.0)])]),
    "L": (0.68, [(0, [(0.06, 1.0), (0.06, 0.0), (0.68, 0.0)])]),
    "A": (0.84, [(0, [(0.0, 0.0), (0.42, 1.0), (0.84, 0.0)]), (0, [(0.17, 0.38), (0.66, 0.38)])]),
    "V": (0.82, [(0, [(0.0, 1.0), (0.41, 0.0), (0.82, 1.0)])]),
    "H": (0.8, [(0, [(0.05, 1.0), (0.05, 0.0)]), (0, [(0.75, 1.0), (0.75, 0.0)]), (0, [(0.05, 0.5), (0.75, 0.5)])]),
    "M": (0.94, [(0, [(0.04, 0.0), (0.1, 1.0), (0.47, 0.33), (0.84, 1.0), (0.9, 0.0)])]),
    "O": (0.86, [(1, [(0.45, 1.0), (0.12, 0.88), (0.02, 0.5), (0.14, 0.1), (0.45, 0.0), (0.76, 0.12), (0.86, 0.5), (0.74, 0.88), (0.42, 1.0)])]),
    "C": (0.82, [(1, [(0.8, 0.85), (0.55, 1.0), (0.2, 0.92), (0.03, 0.55), (0.12, 0.15), (0.45, 0.0), (0.8, 0.12)])]),
    "G": (0.86, [(1, [(0.8, 0.85), (0.55, 1.0), (0.2, 0.92), (0.03, 0.55), (0.12, 0.15), (0.45, 0.0), (0.78, 0.15), (0.8, 0.45)]), (0, [(0.8, 0.45), (0.46, 0.45)])]),
    "K": (0.78, [(0, [(0.06, 1.0), (0.06, 0.0)]), (0, [(0.72, 1.0), (0.08, 0.44), (0.76, 0.0)])]),
    "J": (0.76, [(1, [(0.7, 1.0), (0.7, 0.28), (0.55, 0.02), (0.25, 0.02), (0.06, 0.2)])]),
    "U": (0.8, [(1, [(0.05, 1.0), (0.05, 0.32), (0.2, 0.03), (0.55, 0.03), (0.75, 0.32), (0.75, 1.0)])]),
    "R": (0.8, [(0, [(0.06, 0.0), (0.06, 1.0)]), (1, [(0.06, 1.0), (0.5, 0.98), (0.72, 0.8), (0.6, 0.55), (0.08, 0.5)]), (0, [(0.35, 0.5), (0.78, 0.0)])]),
    "P": (0.76, [(0, [(0.06, 0.0), (0.06, 1.0)]), (1, [(0.06, 1.0), (0.5, 0.98), (0.72, 0.8), (0.6, 0.55), (0.08, 0.5)])]),
    "B": (0.8, [(0, [(0.06, 0.0), (0.06, 1.0)]), (1, [(0.06, 1.0), (0.5, 0.98), (0.68, 0.8), (0.5, 0.56), (0.08, 0.53)]), (1, [(0.08, 0.53), (0.6, 0.5), (0.8, 0.28), (0.6, 0.03), (0.05, 0.0)])]),
    "Y": (0.8, [(0, [(0.0, 1.0), (0.4, 0.5), (0.8, 1.0)]), (0, [(0.4, 0.5), (0.4, 0.0)])]),
    "W": (1.0, [(0, [(0.0, 1.0), (0.22, 0.0), (0.5, 0.62), (0.78, 0.0), (1.0, 1.0)])]),
    "X": (0.78, [(0, [(0.0, 1.0), (0.78, 0.0)]), (0, [(0.78, 1.0), (0.0, 0.0)])]),
    "!": (0.28, [(0, [(0.12, 1.0), (0.12, 0.3)]), (0, [(0.12, 0.07), (0.13, 0.02)])]),
    "-": (0.5, [(0, [(0.05, 0.45), (0.45, 0.45)])]),
    " ": (0.42, []),
}


def layout(txt, height=1.0, tracking=0.16, slant=0.18, jitter=0.03, rot_deg=4.0, seed=1, smooth_n=6):
    """Return list of strokes in reading/write order. Each stroke: list of 2D Vectors (x right, y up).
    Coordinates start at x=0 baseline y=0 and scale with `height`."""
    rng = random.Random(seed)
    strokes = []
    x = 0.0
    for ch in txt.upper():
        w, glyph = G.get(ch, G[" "])
        sc = 1.0 + rng.uniform(-0.06, 0.08)
        rot = math.radians(rng.uniform(-rot_deg, rot_deg))
        base = rng.uniform(-0.04, 0.04)
        for smooth, pts in glyph:
            pp = []
            for (gx, gy) in pts:
                gx += rng.uniform(-jitter, jitter)
                gy += rng.uniform(-jitter, jitter)
                cx, cy = gx - w / 2, gy - 0.5
                rx = cx * math.cos(rot) - cy * math.sin(rot)
                ry = cx * math.sin(rot) + cy * math.cos(rot)
                gx2, gy2 = (rx + w / 2) * sc, (ry + 0.5) * sc + base
                pp.append(Vector(((x + gx2 + gy2 * slant) * height, gy2 * height)))
            if smooth:
                from rn_lib import catmull
                pp = [Vector((p.x, p.y)) for p in catmull([(p.x, p.y, 0) for p in pp], smooth_n)]
            else:
                # densify straight segments so pressure varies along them
                dense = []
                for a, b in zip(pp[:-1], pp[1:]):
                    n = max(2, int((b - a).length / (0.08 * height)))
                    for k in range(n):
                        dense.append(a.lerp(b, k / n))
                dense.append(pp[-1])
                pp = dense
            strokes.append(pp)
        x += (w * sc + tracking)
    return strokes, x * height


def length(pts):
    return sum((b - a).length for a, b in zip(pts[:-1], pts[1:]))


def truncate(strokes, progress):
    """Write-on: keep the first `progress` (0..1) of the total ink length. Returns (strokes, nib point)."""
    total = sum(length(s) for s in strokes)
    budget = total * max(0.0, min(1.0, progress))
    out, nib = [], None
    for s in strokes:
        L = length(s)
        if budget >= L:
            out.append(s)
            budget -= L
            nib = s[-1]
            continue
        if budget > 0:
            part = [s[0]]
            acc = 0.0
            for a, b in zip(s[:-1], s[1:]):
                seg = (b - a).length
                if acc + seg >= budget:
                    t = (budget - acc) / seg if seg > 0 else 0
                    part.append(a.lerp(b, t))
                    break
                part.append(b)
                acc += seg
            out.append(part)
            nib = part[-1]
        break
    return out, nib


def drip_roots(strokes, rng, count, height):
    """Pick drip starting points at low points of strokes (where ink pools)."""
    cands = []
    for s in strokes:
        for i, p in enumerate(s):
            if p.y < 0.12 * height:
                cands.append(p)
    rng.shuffle(cands)
    chosen = []
    for c in cands:
        if all(abs(c.x - o.x) > 0.35 * height for o in chosen):
            chosen.append(c)
        if len(chosen) >= count:
            break
    chosen.sort(key=lambda v: v.x)
    return chosen
