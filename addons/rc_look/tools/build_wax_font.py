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
# The wax's width (em units; designer 2026-10-21: thinner, twice, so A, R, G and W keep open counters) and the grid's width: the
# skeleton is laid for GRID_WIDTH (the baseline stroke's centre half of it up, the cap stroke's
# half of it under the cap height); the bearings sit past the wax's own half width (tight, as a marker hand packs).
WIDTH = 115
GRID_WIDTH = 200
GRID_Y0 = GRID_WIDTH / 2
GRID_K = (CAP_INK - GRID_WIDTH) / 100.0
# The side bearings (em units, past the half width) and the space.
BEARING = 16
SPACE_ADV = 260
# The forward slant (x per y) and the small caps' share.
SLANT = 0.16
SMALL_CAPS = 0.8
# The hand: each source point moves up to JITTER grid units (a hash of the codepoint and the point), each glyph turns up
# to TURN radians round its centre.
JITTER = 1.0
TURN = 0.035
# Sampling: points per grid unit along a curve and the centre line's step (em units).
CURVE_SAMPLES = 0.45
STEP = 7.0
# The pressure: the nib swells by SWELL mid-stroke. The pen start (designer 2026-10-21: bolder, pen shaped) is
# START_BOLD bigger, easing out over START_LEN; the end tapers by END_THIN over END_LEN as the pen lifts.
SWELL = 0.07
START_BOLD = 0.24
START_LEN = 110.0
END_THIN = 0.45
END_LEN = 160.0
# The broad nib (designer 2026-10-21: calligraphic, fluid): an ellipse held at NIB_DEG (up to the right), NIB_CONTRAST
# thinner across its edge than along it; NIB_LONG scales it so a downstroke draws about WIDTH wide. It is stamped every
# STAMP_STEP em units as NIB_POINTS points; consecutive stamps are hulled into one smooth band. RcPencilLook.word_nib_deg
# / word_nib_contrast carry the same numbers for the engine's wax words.
NIB_DEG = 25.0
NIB_CONTRAST = 0.7
NIB_LONG = 1.12
NIB_POINTS = 12
STAMP_STEP = 16.0

# --- The source --------------------------------------------------------------------------------------------------
# glyph: (width in grid units, [stroke, ...]); a stroke is "L" (a polyline: its corners stay corners) or "C" (a
# Catmull-Rom curve through the points) and its points. A single-point "D" is a dot (a pen dab). "F" is a flourish: a
# curve like "C" that the advance leaves out, so a swash tucks under the next letter instead of pushing it away.
GLYPHS = {
    # Marker capitals after the kit's HIT IT (designer 2026-10-21: hand-built, never a geometric face): narrow, mostly
    # straight strokes with a hand's bends, crossbars that climb and run past the stems, bowls of a few pushes.
    "A": (56, [("L", [(-1, -3), (23, 101), (33, 102), (57, -4)]), ("L", [(9, 37), (51, 41)]),
               ("F", [(57, -4), (64, -10), (74, -9), (80, -1)])]),
    "B": (50, [("L", [(1, -2), (0, 103)]),
               ("C", [(0, 101), (30, 102), (44, 93), (42, 73), (26, 59), (4, 58)]),
               ("C", [(4, 58), (36, 58), (52, 44), (50, 15), (32, -1), (1, 0)])]),
    "C": (52, [("C", [(52, 88), (40, 101), (16, 97), (2, 70), (0, 34), (10, 7), (30, -1), (54, 7), (60, 18)])]),
    "D": (52, [("L", [(1, -3), (0, 103)]),
               ("C", [(0, 101), (30, 100), (50, 82), (54, 46), (44, 14), (24, 0), (1, 0)])]),
    "E": (50, [("L", [(52, 102), (1, 100), (0, 1), (50, -2)]), ("L", [(0, 52), (40, 55)]),
               ("F", [(50, -2), (62, -5), (72, -2), (76, 4)])]),
    "F": (50, [("L", [(52, 103), (1, 100), (-1, -3)]), ("L", [(0, 54), (40, 57)])]),
    "G": (56, [("C", [(52, 86), (40, 101), (16, 97), (2, 70), (0, 34), (10, 7), (30, -1), (50, 4), (57, 22),
                      (57, 46)]), ("L", [(28, 47), (62, 45)])]),
    "H": (50, [("L", [(1, 103), (0, -3)]), ("L", [(50, 104), (48, -4)]), ("L", [(-4, 46), (55, 50)])]),
    "I": (0, [("L", [(1, 103), (0, -3)])]),
    "J": (48, [("L", [(22, 101), (66, 104)]), ("C", [(48, 103), (49, 40), (43, 8), (24, -2), (6, 4), (-2, 22),
                                                         (2, 34)])]),
    "K": (52, [("L", [(0, 103), (0, -3)]), ("L", [(52, 103), (6, 47)]),
               ("C", [(6, 47), (30, 24), (44, 6), (54, -3)]), ("F", [(54, -3), (62, -11), (76, -13), (86, -4)])]),
    "L": (46, [("L", [(0, 104), (0, 0), (44, 2)]), ("F", [(44, 2), (58, -1), (68, 2), (72, 8)])]),
    "M": (64, [("L", [(0, -3), (5, 102), (32, 42), (60, 103), (64, -3)])]),
    "N": (52, [("L", [(0, -3), (1, 102), (50, -1), (52, 104)])]),
    "O": (54, [("C", [(28, 100), (48, 88), (54, 52), (48, 16), (28, 0), (8, 10), (0, 46), (6, 84), (26, 100),
                      (44, 96)])]),
    "P": (50, [("L", [(1, -3), (0, 103)]),
               ("C", [(0, 101), (34, 101), (50, 88), (48, 62), (30, 43), (2, 43)])]),
    "Q": (54, [("C", [(28, 100), (48, 88), (54, 52), (48, 16), (28, 0), (8, 10), (0, 46), (6, 84), (26, 100),
                      (44, 96)]), ("F", [(24, 24), (40, 4), (56, -12), (76, -16), (92, -8)])]),
    "R": (52, [("L", [(1, -3), (0, 103)]),
               ("C", [(0, 101), (34, 101), (50, 88), (48, 64), (30, 46), (2, 46)]),
               ("C", [(18, 46), (32, 26), (44, 8), (54, -3)]), ("F", [(54, -3), (62, -12), (76, -16), (90, -10), (98, 4)])]),
    "S": (50, [("C", [(52, 88), (36, 100), (12, 96), (2, 78), (12, 60), (30, 52), (48, 40), (52, 16), (36, 0), (12, 0),
                      (-2, 12), (-4, 24)])]),
    "T": (56, [("C", [(-8, 88), (-7, 97), (2, 99), (62, 103)]), ("L", [(29, 101), (27, -3)])]),
    "U": (50, [("C", [(0, 103), (-1, 32), (6, 6), (26, -1), (44, 6), (50, 32), (51, 103)]),
               ("L", [(51, 100), (52, -3)]), ("F", [(52, -3), (60, -10), (70, -9), (76, 0)])]),
    "V": (54, [("L", [(0, 103), (26, -3), (54, 104)])]),
    "W": (70, [("L", [(0, 103), (14, -3), (34, 70), (54, -3), (70, 104)])]),
    "X": (52, [("L", [(0, 103), (54, -4)]), ("L", [(52, 104), (2, -3)])]),
    "Y": (54, [("L", [(0, 103), (27, 52), (56, 104)]), ("L", [(27, 52), (25, -3)])]),
    "Z": (52, [("L", [(0, 100), (54, 102), (1, 1), (50, -2)]), ("F", [(50, -2), (62, -5), (72, -2), (76, 4)])]),
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
        if kind in ("C", "F"):
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
        elif kind in ("C", "F"):
            em = _resample(em, STEP)
        else:
            em = _resample_keep_corners(em, STEP)
        out.append((kind, em))
    # shift so the ink starts BEARING past the origin
    body = [s for kind, s in out if kind != "F"] or [s for _, s in out]
    min_x = min(p[0] for s in body for p in s)
    max_x = max(p[0] for s in body for p in s)
    dx = BEARING + WIDTH / 2 - min_x
    out = [(kind, [(x + dx, y) for (x, y) in s]) for kind, s in out]
    # a flourish is the pen running on: it joins the stroke whose end it leaves from (one pen start, one end)
    joined = []
    for kind, s in out:
        if kind == "F" and joined:
            j = min(range(len(joined)), key=lambda q: math.dist(joined[q][1][-1], s[0]))
            joined[j] = ("L", joined[j][1] + s[1:])
        else:
            joined.append((kind, s))
    out = joined
    adv = int(round(max_x - min_x + WIDTH + 2 * BEARING))
    return out, adv


def _half_width(along, total):
    """The nib's scale (half the width) `along` em units into a stroke `total` long: the bold start, the swell, the
    tapered end (the pen lifting)."""
    w = WIDTH * (1.0 + SWELL * math.sin(math.pi * along / max(total, 1.0)))
    if along < START_LEN:
        w *= 1.0 + START_BOLD * (1.0 - along / START_LEN) ** 2
    into_end = total - along
    if into_end < END_LEN:
        t = 1.0 - into_end / END_LEN
        w *= 1.0 - END_THIN * t * t
    return w * 0.5


def _nib_shape(h):
    """The broad nib at scale `h` (em units): an ellipse NIB_DEG up to the right, h * NIB_LONG along its edge and
    h * (1 - NIB_CONTRAST) * NIB_LONG across it, so a downstroke draws about 2 h wide and a stroke along the nib thin."""
    th = math.radians(NIB_DEG)
    ca, sa = math.cos(th), math.sin(th)
    a = h * NIB_LONG
    bb = a * (1.0 - NIB_CONTRAST)
    out = []
    for k in range(NIB_POINTS):
        t = math.tau * k / NIB_POINTS
        x, y = math.cos(t) * a, math.sin(t) * bb
        out.append((x * ca - y * sa, x * sa + y * ca))
    return out


def _hull(pts):
    """The convex hull of `pts` (monotone chain), clockwise in y-up coordinates."""
    p = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(p) < 3:
        return p

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in p:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(p):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    ring = lower[:-1] + upper[:-1]  # counter-clockwise
    ring.reverse()
    return ring


def _stroke_contours(pts):
    """A stroke drawn by the nib: the hull of each two consecutive stamps along it (TrueType fills their union)."""
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    path = _resample(pts, STAMP_STEP) if len(pts) > 1 else list(pts)
    acc = [0.0]
    for a, b in zip(path, path[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    stamps = []
    for p, d in zip(path, acc):
        h = _half_width(d, total)
        stamps.append([(p[0] + x, p[1] + y) for x, y in _nib_shape(h)])
    if len(stamps) == 1:
        return [_hull(stamps[0])]
    return [_hull(stamps[i] + stamps[i + 1]) for i in range(len(stamps) - 1)]


def _area(ring):
    s = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        s += x0 * y1 - x1 * y0
    return s * 0.5


def glyph_contours(strokes, cp=0):
    contours = []
    for kind, pts in strokes:
        contours.extend(c for c in _stroke_contours(pts) if len(c) >= 3)
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
        glyph_data.append((ch, glyph_contours(strokes, ord(ch)), adv))
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
