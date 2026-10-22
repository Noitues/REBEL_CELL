"""LOOK-TOOLBOX module 12: builds RC Wax, the grease-pencil face, from one stroke source.

Every glyph is a list of pen strokes in writing order on a cap grid (x right, y up, 0 = the baseline stroke's centre,
100 = the cap stroke's centre). One source gives two outputs, so measuring and drawing never disagree:

- `assets/fonts/RcWax-Regular.ttf`: each stroke outlined at the wax width with its pressure (a TrueType face for
  Font users: layout, measuring, the few views that draw the face directly);
- `addons/rc_look/pencil/rc_wax_strokes.json`: the same strokes as centre lines in em units (y up), which
  GreasePencilWord draws as real wax strokes on the one wax engine (GreasePencilMark).

Lowercase is the caps at SMALL_CAPS of their size (marker hands write in capitals). The hand is in the source and in a
per-glyph hash jitter (never an RNG): the same source always builds the same bytes.

    python addons/rc_look/tools/build_wax_font.py [--check]

`--check` builds in memory and exits 1 when the committed outputs differ (the font is stale).
Pure standard library (no fontTools).
"""
import argparse
import json
import math
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TTF_OUT = ROOT / "assets/fonts/RcWax-Regular.ttf"
JSON_OUT = ROOT / "addons/rc_look/pencil/rc_wax_strokes.json"

FAMILY = "RC Wax"
VERSION = "Version 1.000"
UPM = 1000
# Metrics matched to Permanent Marker (the face this replaces) so layouts keep their size: ascent / descent of the
# line box, the ink's cap height.
ASCENT = 1110
DESCENT = 317
CAP_INK = 740
# The wax's width (em units; designer 2026-10-21: thinner so A, R, G keep open counters) and the grid's width: the
# skeleton, bearings and advances are laid for GRID_WIDTH (the baseline stroke's centre half of it up, the cap stroke's
# half of it under the cap height), so a thinner wax never moves a layout.
WIDTH = 160
GRID_WIDTH = 200
GRID_Y0 = GRID_WIDTH / 2
GRID_K = (CAP_INK - GRID_WIDTH) / 100.0
# The side bearings (em units, past the half width) and the space.
BEARING = 34
SPACE_ADV = 300
# The forward slant (x per y) and the small caps' share.
SLANT = 0.11
SMALL_CAPS = 0.8
# The hand: each source point moves up to JITTER grid units (a hash of the codepoint and the point), each glyph turns up
# to TURN radians round its centre.
JITTER = 2.4
TURN = 0.05
# Sampling: points per grid unit along a curve, the centre line's step (em units), a corner sharper than CORNER_DEG
# splits the outline (an offset round a sharp corner folds over itself), round caps' segments.
CURVE_SAMPLES = 0.45
STEP = 14.0
CORNER_DEG = 48.0
CAP_SEGMENTS = 8
# The pressure in the outline: the width swells by SWELL mid-stroke and the pen lands LAND wider for its first LAND_LEN.
SWELL = 0.07
LAND = 0.06
LAND_LEN = 60.0

# --- The source --------------------------------------------------------------------------------------------------
# glyph: (width in grid units, [stroke, ...]); a stroke is "L" (a polyline: its corners stay corners) or "C" (a
# Catmull-Rom curve through the points) and its points. A single-point "D" is a dot (a pen dab).
GLYPHS = {
    "A": (60, [("L", [(0, -2), (31, 102), (62, -2)]), ("L", [(13, 36), (50, 38)])]),
    "B": (52, [("L", [(0, -2), (0, 102)]),
               ("C", [(0, 100), (28, 100), (46, 90), (46, 66), (28, 54), (2, 54)]),
               ("C", [(2, 54), (34, 54), (54, 42), (54, 14), (34, 0), (0, 0)])]),
    "C": (56, [("C", [(56, 82), (42, 98), (20, 98), (4, 78), (0, 50), (4, 20), (20, 0), (42, 0), (58, 16)])]),
    "D": (56, [("L", [(0, -2), (0, 102)]),
               ("C", [(0, 100), (28, 99), (50, 82), (56, 50), (50, 18), (28, 1), (0, 0)])]),
    "E": (52, [("L", [(54, 101), (0, 100), (0, 0), (56, -1)]), ("L", [(0, 52), (42, 53)])]),
    "F": (52, [("L", [(56, 101), (0, 100), (0, -3)]), ("L", [(0, 52), (44, 53)])]),
    "G": (60, [("C", [(56, 84), (42, 98), (20, 98), (4, 78), (0, 50), (4, 20), (22, 0), (44, 0), (60, 14), (60, 42)]),
               ("L", [(34, 44), (66, 45)])]),
    "H": (56, [("L", [(0, 103), (0, -3)]), ("L", [(56, 104), (57, -3)]), ("L", [(-5, 50), (62, 53)])]),
    "I": (0, [("L", [(0, 103), (1, -3)])]),
    "J": (50, [("C", [(52, 102), (51, 40), (46, 10), (28, 0), (10, 4), (0, 22)])]),
    "K": (56, [("L", [(0, 103), (0, -3)]), ("L", [(56, 102), (4, 46), (60, -3)])]),
    "L": (50, [("L", [(0, 103), (0, 0), (54, -1)])]),
    "M": (70, [("L", [(0, -3), (4, 101), (35, 40), (66, 102), (70, -3)])]),
    "N": (56, [("L", [(0, -3), (0, 101), (56, -1), (57, 103)])]),
    "O": (60, [("C", [(30, 100), (52, 88), (60, 50), (53, 13), (30, 0), (7, 12), (0, 50), (7, 87), (32, 100),
                      (50, 92)])]),
    "P": (52, [("L", [(0, -3), (0, 101)]),
               ("C", [(0, 100), (32, 100), (52, 88), (52, 62), (32, 48), (2, 48)])]),
    "Q": (60, [("C", [(30, 100), (52, 88), (60, 50), (53, 13), (30, 0), (7, 12), (0, 50), (7, 87), (32, 100),
                      (50, 92)]), ("L", [(36, 26), (66, -10)])]),
    "R": (54, [("L", [(0, -3), (0, 101)]),
               ("C", [(0, 100), (32, 100), (52, 88), (52, 62), (32, 48), (2, 48)]), ("L", [(22, 48), (58, -3)])]),
    "S": (54, [("C", [(54, 86), (38, 99), (16, 98), (2, 84), (6, 64), (28, 52), (50, 40), (56, 18), (42, 1), (18, 0),
                      (-2, 14)])]),
    "T": (60, [("L", [(-6, 100), (64, 103)]), ("L", [(30, 101), (30, -3)])]),
    "U": (56, [("C", [(0, 103), (0, 30), (8, 6), (28, 0), (48, 6), (56, 30), (57, 103)])]),
    "V": (60, [("L", [(0, 103), (30, -2), (61, 103)])]),
    "W": (76, [("L", [(0, 103), (17, -2), (38, 66), (59, -2), (77, 103)])]),
    "X": (58, [("L", [(0, 103), (59, -3)]), ("L", [(58, 103), (0, -3)])]),
    "Y": (58, [("L", [(0, 103), (29, 50), (59, 103)]), ("L", [(29, 50), (29, -3)])]),
    "Z": (56, [("L", [(0, 100), (57, 101), (0, 0), (59, -1)])]),
    "0": (50, [("C", [(25, 100), (45, 88), (50, 50), (45, 12), (25, 0), (5, 12), (0, 50), (5, 88), (27, 100),
                      (42, 94)])]),
    "1": (28, [("L", [(0, 80), (26, 102), (26, -3)])]),
    "2": (52, [("C", [(2, 82), (16, 98), (36, 100), (50, 86), (48, 64), (24, 32), (0, 2)]), ("L", [(0, 0), (56, -1)])]),
    "3": (50, [("C", [(2, 90), (20, 100), (42, 96), (50, 78), (40, 58), (18, 54)]),
               ("C", [(18, 54), (42, 50), (54, 30), (46, 6), (24, 0), (0, 10)])]),
    "4": (56, [("L", [(42, -3), (42, 102), (0, 32), (60, 33)])]),
    "5": (52, [("L", [(52, 101), (6, 100), (2, 58)]),
               ("C", [(2, 58), (24, 63), (46, 56), (54, 32), (46, 8), (24, 0), (0, 10)])]),
    "6": (52, [("C", [(48, 94), (30, 100), (10, 90), (0, 60), (2, 22), (20, 0), (40, 2), (54, 22), (50, 46), (30, 56),
                      (10, 50), (2, 36)])]),
    "7": (54, [("L", [(0, 100), (56, 101), (16, -3)])]),
    "8": (52, [("C", [(26, 100), (46, 92), (48, 74), (26, 56), (4, 40), (2, 16), (26, 0), (50, 14), (50, 38), (26, 56),
                      (6, 72), (8, 92), (28, 100), (40, 97)])]),
    "9": (52, [("C", [(52, 64), (44, 48), (24, 44), (4, 54), (0, 78), (14, 98), (36, 100), (52, 84), (54, 50),
                      (46, 14), (26, 0), (6, 6)])]),
    "!": (2, [("L", [(1, 103), (0, 34)]), ("D", [(0, 0)])]),
    "?": (48, [("C", [(0, 82), (14, 98), (34, 100), (48, 86), (44, 64), (24, 50), (23, 32)]), ("D", [(23, 0)])]),
    ".": (0, [("D", [(0, 0)])]),
    ",": (6, [("L", [(6, 4), (0, -24)])]),
    "'": (2, [("L", [(2, 103), (0, 74)])]),
    '"': (20, [("L", [(2, 103), (0, 74)]), ("L", [(22, 103), (20, 74)])]),
    "-": (34, [("L", [(0, 46), (36, 49)])]),
    ":": (0, [("D", [(0, 60)]), ("D", [(0, 0)])]),
    ";": (6, [("D", [(6, 60)]), ("L", [(6, 4), (0, -24)])]),
    "/": (40, [("L", [(0, -8), (42, 108)])]),
    "+": (44, [("L", [(0, 46), (46, 49)]), ("L", [(23, 72), (22, 22)])]),
    "%": (54, [("L", [(0, -2), (54, 102)]), ("C", [(10, 98), (18, 88), (10, 76), (2, 86), (10, 98), (16, 96)]),
               ("C", [(44, 24), (52, 14), (44, 2), (36, 12), (44, 24), (50, 22)])]),
    "(": (22, [("C", [(24, 110), (6, 82), (0, 50), (6, 18), (24, -10)])]),
    ")": (22, [("C", [(0, 110), (18, 82), (24, 50), (18, 18), (0, -10)])]),
    "#": (56, [("L", [(14, 96), (8, 2)]), ("L", [(44, 98), (38, 2)]), ("L", [(-2, 66), (58, 68)]),
               ("L", [(-4, 30), (56, 32)])]),
    "&": (60, [("C", [(62, 0), (20, 50), (8, 70), (12, 92), (28, 100), (42, 90), (40, 72), (18, 56), (2, 34), (6, 10),
                      (24, 0), (44, 6), (60, 30)])]),
    "=": (44, [("L", [(0, 62), (46, 64)]), ("L", [(0, 30), (46, 32)])]),
    "*": (40, [("L", [(20, 100), (20, 50)]), ("L", [(0, 88), (40, 62)]), ("L", [(40, 88), (0, 62)])]),
    "$": (52, [("C", [(52, 84), (36, 96), (14, 94), (2, 80), (8, 62), (28, 52), (48, 40), (54, 20), (40, 4), (16, 4),
                      (-2, 16)]), ("L", [(28, 112), (26, -12)])]),
    "<": (40, [("L", [(42, 90), (0, 50), (42, 10)])]),
    ">": (40, [("L", [(0, 90), (42, 50), (0, 10)])]),
    "_": (56, [("L", [(0, -14), (58, -12)])]),
}
SMALL = {chr(c): chr(c).upper() for c in range(ord("a"), ord("z") + 1)}


# --- Geometry ------------------------------------------------------------------------------------------------------

def _hash01(a, b, c=0):
    """An integer hash in 0..1 (KitNoise.h01's arithmetic, 64-bit wrapped)."""
    n = ((a * 73856093) ^ (b * 19349663) ^ (c * 83492791)) & 0xFFFFFFFFFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFFFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 65535.0


def _h11(a, b, c=0):
    return _hash01(a, b, c) * 2.0 - 1.0


def _catmull(pts, per_unit):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        n = max(2, int(math.dist(p1, p2) * per_unit))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def _resample(pts, step):
    if len(pts) < 2:
        return list(pts)
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        d = step - carry
        while d <= seg and seg > 0:
            t = d / seg
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            d += step
        carry = seg - (d - step)
    if math.dist(out[-1], pts[-1]) > 1e-6:
        out.append(pts[-1])
    return out


def _resample_keep_corners(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        seg = _resample([a, b], step)
        out.extend(seg[1:])
    return out


def glyph_strokes(ch):
    """The centre lines of `ch` in em units (y up, x from the left bearing): [(kind, [(x, y), ...]), ...], adv."""
    src = SMALL.get(ch, ch)
    k = SMALL_CAPS if ch in SMALL else 1.0
    gw, strokes = GLYPHS[src]
    cp = ord(ch)
    cx, cy = gw * 0.5, 50.0
    turn = _h11(cp, 991) * TURN
    cs, sn = math.cos(turn), math.sin(turn)
    out = []
    idx = 0
    for kind, pts in strokes:
        moved = []
        for (x, y) in pts:
            jx = _h11(cp, idx, 1) * JITTER
            jy = _h11(cp, idx, 2) * JITTER
            idx += 1
            x, y = x + jx - cx, y + jy - cy
            x, y = x * cs - y * sn + cx, x * sn + y * cs + cy
            moved.append((x, y))
        if kind == "C":
            moved = _catmull(moved, CURVE_SAMPLES)
        em = []
        for (x, y) in moved:
            ey = (GRID_Y0 + y * GRID_K) * k
            ex = x * GRID_K * k + ey * SLANT
            em.append((ex, ey))
        if kind == "D":
            # a dab: the pen down and a short push
            x, y = em[0]
            em = [(x - WIDTH * 0.08, y + WIDTH * 0.02), (x + WIDTH * 0.08, y - WIDTH * 0.02)]
        elif kind == "C":
            em = _resample(em, STEP)
        else:
            em = _resample_keep_corners(em, STEP)
        out.append((kind, em))
    # shift so the ink starts BEARING past the origin
    min_x = min(p[0] for _, s in out for p in s)
    max_x = max(p[0] for _, s in out for p in s)
    dx = BEARING + GRID_WIDTH / 2 - min_x
    out = [(kind, [(x + dx, y) for (x, y) in s]) for kind, s in out]
    adv = int(round(max_x - min_x + GRID_WIDTH + 2 * BEARING))
    return out, adv


def _split_corners(pts):
    """Splits a polyline where it turns sharper than CORNER_DEG (the outline of each piece never folds)."""
    pieces = [[pts[0]]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        pieces[-1].append(b)
        if l1 > 0 and l2 > 0:
            cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
            if math.degrees(math.acos(max(-1.0, min(1.0, cosang)))) > CORNER_DEG:
                pieces.append([b])
    pieces[-1].append(pts[-1])
    return [p for p in pieces if len(p) >= 2]


def _half_width(t, along):
    w = WIDTH * (1.0 + SWELL * math.sin(math.pi * t))
    if along < LAND_LEN:
        w *= 1.0 + LAND * (1.0 - along / LAND_LEN)
    return w * 0.5


def _outline(pts):
    """A closed outline round polyline `pts` (round caps), clockwise in y-up coordinates."""
    n = len(pts)
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) or 1.0
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        h = _half_width(acc[i] / total, acc[i])
        left.append((p[0] + nx * h, p[1] + ny * h))
        right.append((p[0] - nx * h, p[1] - ny * h))

    def cap(centre, frm, h, sweep_from):
        out = []
        for k in range(1, CAP_SEGMENTS):
            ang = sweep_from - math.pi * k / CAP_SEGMENTS
            out.append((centre[0] + math.cos(ang) * h, centre[1] + math.sin(ang) * h))
        return out

    def ang_of(c, q):
        return math.atan2(q[1] - c[1], q[0] - c[0])

    end_h = _half_width(1.0, acc[-1])
    start_h = _half_width(0.0, 0.0)
    ring = list(left)
    ring += cap(pts[-1], left[-1], end_h, ang_of(pts[-1], left[-1]))
    ring += list(reversed(right))
    ring += cap(pts[0], right[0], start_h, ang_of(pts[0], right[0]))
    # left-then-reversed-right is counter-clockwise for a stroke going +x with the left normal up; TrueType wants
    # clockwise outer contours
    if _area(ring) > 0:
        ring.reverse()
    return ring


def _area(ring):
    s = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        s += x0 * y1 - x1 * y0
    return s * 0.5


def _segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def _self_crosses(ring):
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        for j in range(i + 2, n):
            if (j + 1) % n == i:
                continue
            if _segments_cross(a, b, ring[j], ring[(j + 1) % n]):
                return True
    return False


def _capsules(pts):
    """Fallback for a piece whose outline would fold: one capsule per span of a few samples (all clockwise)."""
    out = []
    span = 3
    for i in range(0, len(pts) - 1, span):
        seg = pts[i:i + span + 1]
        if len(seg) >= 2:
            out.append(_outline(seg))
    return out


def glyph_contours(strokes):
    contours = []
    for kind, pts in strokes:
        for piece in _split_corners(pts):
            ring = _outline(piece)
            if _self_crosses(ring):
                contours.extend(_capsules(piece))
            else:
                contours.append(ring)
    return contours


# --- TrueType writer --------------------------------------------------------------------------------------------

def _checksum(data):
    data = data + b"\0" * ((4 - len(data) % 4) % 4)
    return sum(struct.unpack(">%dI" % (len(data) // 4), data)) & 0xFFFFFFFF


def _glyf_entry(contours):
    if not contours:
        return b"", (0, 0, 0, 0), 0, 0
    pts = [(int(round(x)), int(round(y))) for c in contours for (x, y) in c]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    ends, n = [], 0
    for c in contours:
        n += len(c)
        ends.append(n - 1)
    out = struct.pack(">hhhhh", len(contours), *bbox)
    out += struct.pack(">%dH" % len(ends), *ends)
    out += struct.pack(">H", 0)  # no instructions
    out += bytes([0x01] * len(pts))  # on-curve, 16-bit deltas
    px = py = 0
    xb, yb = b"", b""
    for x, y in pts:
        xb += struct.pack(">h", x - px)
        yb += struct.pack(">h", y - py)
        px, py = x, y
    out += xb + yb
    out += b"\0" * ((4 - len(out) % 4) % 4)
    return out, bbox, len(pts), len(contours)


def _name_table():
    names = {0: "Copyright REBEL_CELL project (own work)", 1: FAMILY, 2: "Regular", 3: FAMILY + " Regular 1.000",
             4: FAMILY + " Regular", 5: VERSION, 6: "RCWax-Regular"}
    recs, strings = [], b""
    for nid, s in sorted(names.items()):
        b = s.encode("utf-16-be")
        recs.append(struct.pack(">HHHHHH", 3, 1, 0x409, nid, len(b), len(strings)))
        strings += b
    head = struct.pack(">HHH", 0, len(recs), 6 + 12 * len(recs))
    return head + b"".join(recs) + strings


def _cmap_table(cmap):
    codes = sorted(c for c in cmap if c <= 0xFFFF)
    segs = []
    for c in codes:
        if segs and c == segs[-1][1] + 1 and cmap[c] == cmap[segs[-1][1]] + 1:
            segs[-1][1] = c
        else:
            segs.append([c, c])
    segs.append([0xFFFF, 0xFFFF])
    n = len(segs)
    ends = [e for _, e in segs]
    starts = [s for s, _ in segs]
    deltas = [((cmap[s] - s) & 0xFFFF) if s != 0xFFFF else 1 for s, _ in segs]
    search = 2 * (2 ** int(math.log2(n)))
    sub = struct.pack(">HHHHHHH", 4, 0, 0, 2 * n, search, int(math.log2(search // 2)), 2 * n - search)
    sub += struct.pack(">%dH" % n, *ends) + b"\0\0" + struct.pack(">%dH" % n, *starts)
    sub += struct.pack(">%dH" % n, *deltas) + struct.pack(">%dH" % n, *([0] * n))
    sub = sub[:2] + struct.pack(">H", len(sub)) + sub[4:]
    return struct.pack(">HHHHI", 0, 1, 3, 1, 12) + sub


def build():
    chars = [" "] + sorted(set(GLYPHS) | set(SMALL), key=ord)
    glyph_data = [(".notdef", [], 500)]
    stroke_json = {}
    for ch in chars:
        if ch == " ":
            glyph_data.append((ch, [], SPACE_ADV))
            stroke_json[str(ord(ch))] = {"adv": SPACE_ADV, "strokes": []}
            continue
        strokes, adv = glyph_strokes(ch)
        glyph_data.append((ch, glyph_contours(strokes), adv))
        stroke_json[str(ord(ch))] = {"adv": adv, "strokes": [[round(v, 1) for p in s for v in p] for _, s in strokes]}
    # .notdef: an open box
    nd = [[(60, 0), (60, 700), (440, 700), (440, 0)], [(110, 50), (390, 50), (390, 650), (110, 650)]]
    glyph_data[0] = (".notdef", nd, 500)

    glyf, loca = b"", [0]
    hmtx = b""
    bbox_all = [0, 0, 0, 0]
    max_pts = max_cont = 0
    for i, (ch, contours, adv) in enumerate(glyph_data):
        entry, bbox, npts, ncont = _glyf_entry(contours)
        glyf += entry
        loca.append(len(glyf))
        hmtx += struct.pack(">Hh", adv, bbox[0] if contours else 0)
        if contours:
            bbox_all = [min(bbox_all[0], bbox[0]), min(bbox_all[1], bbox[1]), max(bbox_all[2], bbox[2]),
                        max(bbox_all[3], bbox[3])]
        max_pts, max_cont = max(max_pts, npts), max(max_cont, ncont)
    n = len(glyph_data)
    cmap = {ord(ch): i for i, (ch, _, _) in enumerate(glyph_data) if i > 0}
    stamp = 0  # fixed: the same source builds the same bytes
    head = struct.pack(">IIIIHHqqhhhhHHhhh", 0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0x000B, UPM, stamp, stamp,
                       *bbox_all, 0, 8, 2, 1, 0)
    advs = [a for _, _, a in glyph_data]
    hhea = struct.pack(">IhhhHhhhhhhhhhhhH", 0x00010000, ASCENT, -DESCENT, 0, max(advs), min(0, bbox_all[0]),
                       0, bbox_all[2], 1, 0, 0, 0, 0, 0, 0, 0, n)
    maxp = struct.pack(">IHHHHHHHHHHHHHH", 0x00010000, n, max_pts, max_cont, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
    avg = int(sum(advs) / len(advs))
    os2 = struct.pack(">HhHHHhhhhhhhhhhh", 4, avg, 400, 5, 0, 650, 700, 0, 140, 650, 700, 0, 480, 50, 300, 0)
    os2 += bytes(10)  # panose
    os2 += struct.pack(">IIII", 1, 0, 0, 0)  # unicode ranges: Basic Latin
    os2 += b"RCLL"
    os2 += struct.pack(">HHH", 0x40, min(cmap), min(max(cmap), 0xFFFF))
    os2 += struct.pack(">hhhHH", ASCENT, -DESCENT, 0, ASCENT, DESCENT)
    os2 += struct.pack(">II", 1, 0)
    os2 += struct.pack(">hhHHH", int(CAP_INK * SMALL_CAPS), CAP_INK, 0, 32, 0)
    post = struct.pack(">IIhhIIIII", 0x00030000, int(-SLANT * 0) & 0xFFFFFFFF, -120, 60, 0, 0, 0, 0, 0)
    tables = {
        b"OS/2": os2, b"cmap": _cmap_table(cmap), b"glyf": glyf, b"head": head, b"hhea": hhea, b"hmtx": hmtx,
        b"loca": struct.pack(">%dI" % len(loca), *loca), b"maxp": maxp, b"name": _name_table(), b"post": post,
    }
    tags = sorted(tables)
    num = len(tags)
    es = int(math.log2(num))
    sr = (2 ** es) * 16
    font = struct.pack(">IHHHH", 0x00010000, num, sr, es, num * 16 - sr)
    offset = 12 + 16 * num
    dir_, body = b"", b""
    head_off = 0
    for t in tags:
        data = tables[t]
        if t == b"head":
            head_off = offset
        dir_ += struct.pack(">4sIII", t, _checksum(data), offset, len(data))
        padded = data + b"\0" * ((4 - len(data) % 4) % 4)
        body += padded
        offset += len(padded)
    ttf = bytearray(font + dir_ + body)
    adj = (0xB1B0AFBA - _checksum(bytes(ttf))) & 0xFFFFFFFF
    struct.pack_into(">I", ttf, head_off + 8, adj)
    meta = {"family": FAMILY, "upm": UPM, "ascent": ASCENT, "descent": DESCENT, "cap": CAP_INK, "width": WIDTH,
            "slant": SLANT, "glyphs": stroke_json,
            "_note": "built by addons/rc_look/tools/build_wax_font.py; do not edit"}
    return bytes(ttf), json.dumps(meta, indent=None, separators=(",", ":"), sort_keys=True) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ttf, js = build()
    if a.check:
        ok = TTF_OUT.exists() and TTF_OUT.read_bytes() == ttf and JSON_OUT.exists() and JSON_OUT.read_bytes() == js.encode("utf-8")
        print("wax font: current" if ok else "wax font: STALE (run build_wax_font.py)")
        sys.exit(0 if ok else 1)
    TTF_OUT.write_bytes(ttf)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_bytes(js.encode("utf-8"))
    print(f"wax font: {TTF_OUT} ({len(ttf)} B), {JSON_OUT}")


if __name__ == "__main__":
    main()
