"""Single-stroke vector font (original, drawn for this concept). Cap height 6, width ~4.

Each glyph is a list of polylines in (x, y) with y up. Used for vector-monitor type
(neon sign, hologram ads) and, jittered and thickened, as the Cell's marker hand.
Pure Python: importable from Blender and from Pillow scripts.
"""
import math


def _arc(cx, cy, rx, ry, a0, a1, n=10):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


G = {
    "A": [[(0, 0), (2, 6), (4, 0)], [(0.8, 2.3), (3.2, 2.3)]],
    "B": [[(0, 0), (0, 6), (2.6, 6)] + _arc(2.6, 4.6, 1.3, 1.4, 90, -90, 6)[1:] + [(0, 3.2)],
          [(2.8, 3.2)] + _arc(2.8, 1.6, 1.4, 1.6, 90, -90, 6)[1:] + [(0, 0)]],
    "C": [_arc(2.2, 3, 2.2, 3, 50, 310, 14)],
    "D": [[(0, 0), (0, 6), (1.6, 6)] + _arc(1.6, 3, 2.4, 3, 90, -90, 10)[1:] + [(0, 0)]],
    "E": [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3.1), (3, 3.1)]],
    "F": [[(4, 6), (0, 6), (0, 0)], [(0, 3.1), (3, 3.1)]],
    "G": [_arc(2.2, 3, 2.2, 3, 50, 320, 14)[:-1] + [(4.2, 2.6), (2.4, 2.6)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3.1), (4, 3.1)]],
    "I": [[(2, 0), (2, 6)], [(1, 6), (3, 6)], [(1, 0), (3, 0)]],
    "J": [[(4, 6), (4, 1.6)] + _arc(2.2, 1.6, 1.8, 1.6, 0, -170, 8)[1:]],
    "K": [[(0, 0), (0, 6)], [(4, 6), (0, 2.2)], [(1.3, 3.4), (4, 0)]],
    "L": [[(0, 6), (0, 0), (3.8, 0)]],
    "M": [[(0, 0), (0, 6), (2, 2.6), (4, 6), (4, 0)]],
    "N": [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    "O": [_arc(2, 3, 2.1, 3, 90, 450, 20)],
    "P": [[(0, 0), (0, 6), (2.4, 6)] + _arc(2.4, 4.4, 1.6, 1.6, 90, -90, 8)[1:] + [(0, 2.8)]],
    "Q": [_arc(2, 3, 2.1, 3, 90, 450, 20), [(2.4, 1.2), (4.2, -0.4)]],
    "R": [[(0, 0), (0, 6), (2.4, 6)] + _arc(2.4, 4.4, 1.6, 1.6, 90, -90, 8)[1:] + [(0, 2.8)],
          [(1.8, 2.8), (4, 0)]],
    "S": [_arc(2, 4.5, 1.9, 1.5, 20, 270, 9) + _arc(2, 1.5, 2.0, 1.5, 90, -160, 9)[1:]],
    "T": [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    "U": [[(0, 6), (0, 2)] + _arc(2, 2, 2, 2, 180, 360, 10)[1:] + [(4, 6)]],
    "V": [[(0, 6), (2, 0), (4, 6)]],
    "W": [[(0, 6), (1, 0), (2, 4), (3, 0), (4, 6)]],
    "X": [[(0, 6), (4, 0)], [(4, 6), (0, 0)]],
    "Y": [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]],
    "Z": [[(0, 6), (4, 6), (0, 0), (4, 0)]],
    "0": [_arc(2, 3, 1.8, 3, 90, 450, 18), [(0.8, 1.2), (3.2, 4.8)]],
    "1": [[(0.8, 4.6), (2.2, 6), (2.2, 0)], [(0.8, 0), (3.6, 0)]],
    "2": [_arc(2, 4.3, 1.9, 1.7, 160, -20, 8) + [(0, 0), (4, 0)]],
    "3": [_arc(2, 4.5, 1.8, 1.5, 150, -90, 8) + _arc(2, 1.5, 2.0, 1.5, 90, -150, 8)[1:]],
    "4": [[(3, 0), (3, 6), (0, 1.8), (4.2, 1.8)]],
    "5": [[(3.8, 6), (0.4, 6), (0.2, 3.4)] + _arc(2, 1.9, 2, 1.9, 120, -150, 10)[1:]],
    "6": [_arc(2, 1.8, 1.9, 1.8, 180, 540, 14) + [(0.6, 4.4), (2.6, 6.2)]],
    "7": [[(0, 6), (4, 6), (1.4, 0)]],
    "8": [_arc(2, 4.6, 1.6, 1.4, -90, 270, 12), _arc(2, 1.6, 2, 1.6, 90, 450, 14)],
    "9": [_arc(2, 4.2, 1.9, 1.8, 0, 360, 14) + [(3.9, 3), (2.6, 0)]],
    "!": [[(2, 6), (2, 1.8)], [(2, 0.3), (2, 0)]],
    "-": [[(0.6, 3), (3.4, 3)]],
    "/": [[(0, 0), (4, 6)]],
    ">": [[(0.5, 6), (3.8, 3), (0.5, 0)]],
    "<": [[(3.5, 6), (0.2, 3), (3.5, 0)]],
    ".": [[(2, 0.2), (2, 0)]],
    ":": [[(2, 4.2), (2, 4)], [(2, 0.2), (2, 0)]],
    "#": [[(1.2, 0), (1.6, 6)], [(2.8, 0), (3.2, 6)], [(0, 2), (4.2, 2)], [(0, 4), (4.2, 4)]],
    " ": [],
}
ADV = 5.4  # advance per glyph


def layout(textstr, size=1.0, spacing=ADV, slant=0.0, origin=(0.0, 0.0)):
    """Returns a list of polylines (each a list of (x, y)) for the string, scaled so cap = 6*size/6."""
    s = size / 6.0
    out = []
    x0 = 0.0
    for ch in textstr.upper():
        for pl in G.get(ch, []):
            out.append([(origin[0] + (x0 + x + y * slant) * s, origin[1] + y * s) for (x, y) in pl])
        x0 += spacing * (0.6 if ch == " " else (0.55 if ch == "I" and G["I"] and len(G["I"]) == 1 else 1.0))
    return out


def width(textstr, size=1.0, spacing=ADV):
    return (len(textstr) * spacing - (spacing - 4)) * size / 6.0


def resample(pl, step):
    """Resample a polyline to roughly even spacing `step` (keeps corners)."""
    out = [pl[0]]
    for (a, b) in zip(pl, pl[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def marker_hand(textstr, size, rng, origin=(0, 0), slant=0.22, spacing=5.0, wobble=0.05, rot_deg=-4.0):
    """Jittered, slanted, resampled strokes that read as a quick marker hand.
    Returns [(polyline, pressure_list)], in write order."""
    saved = G["I"]
    G["I"] = [[(0.9, 6.2), (0.7, 0)]]  # the hand writes a bare, narrow I
    raw = layout(textstr, size, spacing=spacing, slant=slant)
    G["I"] = saved
    ca, sa = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    s = size / 6.0
    out = []
    # per-glyph baseline bounce
    for pl in raw:
        pts = resample(pl, s * 0.35)
        dx, dy = rng.uniform(-0.12, 0.12) * s, rng.uniform(-0.2, 0.2) * s
        ph = rng.uniform(0, 6.28)
        q = []
        for i, (x, y) in enumerate(pts):
            x += dx + math.sin(ph + i * 0.7) * wobble * s
            y += dy + math.cos(ph + i * 0.5) * wobble * s
            xr, yr = x * ca - y * sa, x * sa + y * ca
            q.append((origin[0] + xr, origin[1] + yr))
        n = len(q)
        pr = [0.75 + 0.25 * math.sin(math.pi * min(1.0, (i + 0.5) / max(1, n - 1))) for i in range(n)]
        out.append((q, pr))
    return out
