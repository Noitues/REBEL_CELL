"""Single-stroke marker font for the Cell's voice (pure Python, no bpy).

Each glyph is a list of polylines in a box 1.0 high; the glyph width is the max x.
Single strokes (not outlines) so the words can *write on* stroke by stroke (feedback 6).
`layout_word` returns hand-jittered strokes in pixel space with a pressure per point.
"""
import math
import random


def _ellipse(cx, cy, rx, ry, n=18, start=0.25):
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * (start + i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


GLYPHS = {
    "A": [[(0, 0), (0.3, 1), (0.6, 0)], [(0.12, 0.38), (0.48, 0.38)]],
    "B": [[(0, 0), (0, 1), (0.4, 1), (0.55, 0.88), (0.55, 0.64), (0.4, 0.53), (0, 0.53)],
          [(0.4, 0.53), (0.6, 0.4), (0.6, 0.14), (0.45, 0), (0, 0)]],
    "C": [[(0.6, 0.85), (0.45, 1), (0.15, 1), (0, 0.75), (0, 0.25), (0.15, 0), (0.45, 0), (0.6, 0.15)]],
    "D": [[(0, 0), (0, 1), (0.3, 1), (0.55, 0.8), (0.6, 0.5), (0.55, 0.2), (0.3, 0), (0, 0)]],
    "E": [[(0.58, 1), (0, 1), (0, 0), (0.6, 0)], [(0, 0.52), (0.45, 0.52)]],
    "F": [[(0.6, 1), (0, 1), (0, 0)], [(0, 0.52), (0.45, 0.52)]],
    "G": [[(0.6, 0.85), (0.45, 1), (0.15, 1), (0, 0.75), (0, 0.25), (0.15, 0), (0.45, 0), (0.6, 0.2),
           (0.6, 0.45), (0.35, 0.45)]],
    "H": [[(0, 1), (0, 0)], [(0.6, 1), (0.6, 0)], [(0, 0.52), (0.6, 0.52)]],
    "I": [[(0.1, 1), (0.1, 0)]],
    "J": [[(0.6, 1), (0.6, 0.2), (0.45, 0.02), (0.15, 0.02), (0, 0.2)]],
    "K": [[(0, 1), (0, 0)], [(0.6, 1), (0, 0.4)], [(0.18, 0.56), (0.62, 0)]],
    "L": [[(0, 1), (0, 0), (0.55, 0)]],
    "M": [[(0, 0), (0, 1), (0.35, 0.4), (0.7, 1), (0.7, 0)]],
    "N": [[(0, 0), (0, 1), (0.6, 0), (0.6, 1)]],
    "O": [_ellipse(0.32, 0.5, 0.32, 0.5)],
    "P": [[(0, 0), (0, 1), (0.45, 1), (0.6, 0.85), (0.6, 0.63), (0.45, 0.48), (0, 0.48)]],
    "R": [[(0, 0), (0, 1), (0.45, 1), (0.6, 0.85), (0.6, 0.65), (0.45, 0.5), (0, 0.5)], [(0.3, 0.5), (0.62, 0)]],
    "S": [[(0.6, 0.85), (0.45, 0.99), (0.15, 0.99), (0.02, 0.82), (0.08, 0.62), (0.5, 0.42), (0.6, 0.2),
           (0.48, 0.01), (0.15, 0.01), (0, 0.15)]],
    "T": [[(0, 1), (0.64, 1)], [(0.32, 1), (0.32, 0)]],
    "U": [[(0, 1), (0, 0.2), (0.15, 0), (0.45, 0), (0.6, 0.2), (0.6, 1)]],
    "V": [[(0, 1), (0.3, 0), (0.6, 1)]],
    "W": [[(0, 1), (0.18, 0), (0.35, 0.6), (0.52, 0), (0.7, 1)]],
    "X": [[(0, 1), (0.6, 0)], [(0.6, 1), (0, 0)]],
    "Y": [[(0, 1), (0.3, 0.5), (0.6, 1)], [(0.3, 0.5), (0.3, 0)]],
    "!": [[(0.1, 1), (0.1, 0.3)], [(0.1, 0.07), (0.1, 0.0)]],
    " ": [],
}
WIDTH = {" ": 0.35}


def glyph_width(ch):
    if ch in WIDTH:
        return WIDTH[ch]
    pts = [p for s in GLYPHS[ch] for p in s]
    return max(p[0] for p in pts) if pts else 0.3


def _chaikin(poly, it=2):
    for _ in range(it):
        out = [poly[0]]
        for a, b in zip(poly, poly[1:]):
            out.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            out.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        out.append(poly[-1])
        poly = out
    return poly


def _resample(poly, step):
    out = [poly[0]]
    for a, b in zip(poly, poly[1:]):
        d = math.dist(a, b)
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def layout_word(text, x, y, height, seed, slant=0.18, spacing=0.3, rot_deg=-4.0, wobble=0.035):
    """Return marker strokes for `text` with its baseline-left at pixel (x, y).

    Each stroke is a list of (px, py, pressure). Pixel space: y grows down.
    Deterministic for a seed.
    """
    rng = random.Random(seed)
    strokes = []
    cx = 0.0
    rot = math.radians(rot_deg)
    for ch in text.upper():
        sc = 1.0 + rng.uniform(-0.08, 0.08)
        dy = rng.uniform(-0.05, 0.05)
        for poly in GLYPHS.get(ch, []):
            jit = [(px + rng.uniform(-wobble, wobble), py + rng.uniform(-wobble, wobble)) for px, py in poly]
            fine = _resample(_chaikin(jit, 1), 0.04)
            n = len(fine)
            stroke = []
            for i, (gx, gy) in enumerate(fine):
                t = i / max(1, n - 1)
                # marker pressure: heavy landing, slight thinning mid, lift at the end
                pr = 0.85 + 0.25 * math.exp(-t * 8) - 0.25 * max(0, t - 0.85) / 0.15
                lx = cx + (gx * sc + gy * sc * slant)
                ly = (gy * sc + dy)
                rx = lx * math.cos(rot) - ly * math.sin(rot)
                ry = lx * math.sin(rot) + ly * math.cos(rot)
                stroke.append((x + rx * height, y - ry * height, pr))
            strokes.append(stroke)
        cx += glyph_width(ch) * sc + spacing
    return strokes


def word_extent(strokes):
    xs = [p[0] for s in strokes for p in s]
    ys = [p[1] for s in strokes for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def drip_sources(strokes, seed, count, height):
    """Pick low points of strokes as drip origins (pixel coords)."""
    rng = random.Random(seed)
    cands = []
    base = max(p[1] for s in strokes for p in s)
    top = min(p[1] for s in strokes for p in s)
    for s in strokes:
        if len(s) < 5:
            continue
        # a drip hangs only off a stroke end that is heading down (ink pools where the pen stops)
        for p, q in ((s[0], s[4]), (s[-1], s[-5])):
            dx, dy = p[0] - q[0], p[1] - q[1]
            if dy > 0 and dy > abs(dx) * 1.2 and p[1] > top + (base - top) * 0.45:
                if all(math.dist(p[:2], c) > 12 for c in cands):
                    cands.append((p[0], p[1]))
    rng.shuffle(cands)
    cands.sort(key=lambda p: -p[1])
    pick = cands[: max(count * 2, count)]
    rng.shuffle(pick)
    return [(px, py, rng.uniform(0.4, 1.0)) for px, py in pick[:count]]


def truncate(strokes, frac):
    """Write-on: keep the first `frac` of the total ink length, stroke by stroke."""
    lens = []
    for s in strokes:
        lens.append(sum(math.dist(a[:2], b[:2]) for a, b in zip(s, s[1:])))
    total = sum(lens) * frac
    out = []
    for s, ln in zip(strokes, lens):
        if total <= 0:
            break
        if ln <= total:
            out.append(s)
            total -= ln
            continue
        part = [s[0]]
        acc = 0.0
        for a, b in zip(s, s[1:]):
            d = math.dist(a[:2], b[:2])
            if acc + d > total:
                t = (total - acc) / max(d, 1e-6)
                part.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, b[2]))
                break
            part.append(b)
            acc += d
        out.append(part)
        total = 0
    return out
