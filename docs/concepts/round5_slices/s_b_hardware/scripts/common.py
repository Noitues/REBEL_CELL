"""Shared data for the s_b_hardware slice study (pure Python, importable from Blender too).

World units: 1 unit = 100 px at master size. Every tile is built in its own local frame:
hub centre at the origin, the tile's axis along +Y (outward), so a tile spanning N ticks
covers angles 90 +/- N*6 degrees and radii R_IN..R_OUT.

Texture frame (the per-tile atlas cell): a 3.6 x 3.6 unit square, x in [-1.8, 1.8],
y in [0.9, 4.5]; u = (x + 1.8) / 3.6, v = (y - 0.9) / 3.6. A 5-tick (60 deg) tile at
R_OUT exactly fills its width, so one cell serves every tile width.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # docs/concepts/round5_slices/s_b_hardware
ROOT = os.path.abspath(os.path.join(OUT, "..", "..", "..", ".."))  # worktree root
WORK = os.environ.get(
    "SBH_WORK",
    os.path.join(os.environ.get("TEMP", "/tmp"), "sbh_work"),
)
FONT_NUM = os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf")
FONT_UI = os.path.join(ROOT, "assets", "fonts", "IBMPlexSansCondensed-Medium.ttf")
FONT_MONO = os.path.join(ROOT, "assets", "fonts", "ShareTechMono-Regular.ttf")

TICKS = 30
TICK_DEG = 360.0 / TICKS
R_OUT = 3.6
R_IN = 1.3
GAP = 0.05            # gap between neighbouring tiles (units)
ANCHOR_F = 0.60       # glyph+number centre at 60% of the radius span
R_ANCHOR = R_IN + ANCHOR_F * (R_OUT - R_IN)
TEX_PX = 720
TEX_X0, TEX_Y0, TEX_SIZE = -1.8, 0.9, 3.6
PPU = 100.0           # px per unit at master size

# key: (program name, colour hex, glyph id)
PROGRAMS = {
    "ATTACK":   ("EXPLOIT",  "#FF3DA8", "dagger"),
    "CRITICAL": ("ZERO-DAY", "#FF5CC0", "burst"),
    "DEFEND":   ("FIREWALL", "#5CE1FF", "shield"),
    "SHIELD":   ("SANDBOX",  "#3FD6C8", "cube"),
    "EVADE":    ("PROXY",    "#7BE07B", "chevrons"),
    "HEAL":     ("PATCH",    "#7BE07B", "cross"),
    "AFFLICT":  ("VIRUS",    "#C85AFF", "virus"),
    "DEPLOY":   ("TROJAN",   "#B08CFF", "gift"),
    "MISS":     ("NULL",     "#6A6A6A", "null"),
}
ORDER = ["ATTACK", "CRITICAL", "DEFEND", "SHIELD", "EVADE", "HEAL", "AFFLICT", "DEPLOY", "MISS"]

# Player wheel: (slice type, ticks, value), clockwise from the pointer.
PLAYER_WHEEL = [
    ("ATTACK", 3, 6), ("CRITICAL", 2, 12), ("EVADE", 3, 4), ("AFFLICT", 3, 3),
    ("DEFEND", 4, 9), ("MISS", 2, 0), ("HEAL", 3, 5), ("ATTACK", 3, 8),
    ("SHIELD", 3, 5), ("DEPLOY", 4, 2),
]
# Enemy wheel (Meridian, corporate machined).
ENEMY_WHEEL = [
    ("ATTACK", 3, 6), ("EVADE", 3, 3), ("AFFLICT", 3, 4), ("ATTACK", 3, 9),
    ("DEFEND", 4, 6), ("MISS", 3, 0), ("ATTACK", 3, 8), ("SHIELD", 3, 6),
    ("CRITICAL", 2, 14), ("DEFEND", 3, 5),
]
assert sum(t for _, t, _ in PLAYER_WHEEL) == TICKS
assert sum(t for _, t, _ in ENEMY_WHEEL) == TICKS

# Programs sheet: (slice type, ticks, value, hub x, hub y) in world units; camera centre (0,0),
# ortho width 19.2 (= 1920 px at master scale).
SHEET_ORTHO = 19.2
_R1, _R2, _R3 = 0.65, -2.55, -5.76
SHEET = [
    ("ATTACK", 3, 6, -6.4, _R1), ("CRITICAL", 3, 12, -3.2, _R1), ("DEFEND", 3, 5, 0.0, _R1),
    ("SHIELD", 3, 4, 3.2, _R1), ("EVADE", 3, 3, 6.4, _R1),
    ("HEAL", 3, 5, -4.8, _R2), ("AFFLICT", 3, 3, -1.6, _R2), ("DEPLOY", 3, 2, 1.6, _R2),
    ("MISS", 3, 0, 4.8, _R2),
    ("DEFEND", 2, 3, -4.6, _R3), ("DEFEND", 3, 5, -1.2, _R3), ("DEFEND", 5, 11, 2.6, _R3),
]

WHEEL_ORTHO = 9.6     # square 960 px render, wheel centred
WHEEL_RES = 960


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(h, k=1.0):
    r, g, b = hexrgb(h)
    return (srgb_to_lin(r) * k, srgb_to_lin(g) * k, srgb_to_lin(b) * k, 1.0)


def half_angle(ticks):
    return math.radians(ticks * TICK_DEG / 2.0)


def edge_angle(ticks, r, side, gap=GAP):
    """Angle (radians, CCW from +X) of a tile side edge at radius r after the gap inset."""
    h = half_angle(ticks)
    d = math.asin(min(0.99, (gap / 2.0) / max(r, 1e-6)))
    return math.pi / 2 - h + d if side > 0 else math.pi / 2 + h - d


def inside(ticks, x, y, margin=0.0, r0=R_IN, r1=R_OUT):
    """True when the point sits inside the tile with `margin` (units) to every edge."""
    r = math.hypot(x, y)
    if r < r0 + margin or r > r1 - margin:
        return False
    a = math.atan2(y, x)
    h = half_angle(ticks)
    dist_side = r * math.sin(h - abs(a - math.pi / 2))
    return abs(a - math.pi / 2) < h and dist_side > GAP / 2 + margin


def wheel_slices(wheel):
    """Yield (type, ticks, value, centre_angle_deg) clockwise from the top pointer."""
    start = 0
    out = []
    for typ, t, v in wheel:
        mid = start + t / 2.0
        out.append((typ, t, v, 90.0 - mid * TICK_DEG))
        start += t
    return out


# Seeded feature placements, tile-local units (generated once, deterministic).
def _lcg(seed):
    s = seed & 0xFFFFFFFF
    while True:
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        yield s / 0x7FFFFFFF


def pustules():
    """VIRUS: (x, y, radius) candidates, filtered per tile by inside()."""
    return [(-0.28, 1.6, 0.14), (0.3, 1.75, 0.11), (0.0, 1.45, 0.07), (-0.55, 2.3, 0.12),
            (0.58, 2.55, 0.13), (-0.75, 3.0, 0.15), (0.78, 3.15, 0.13), (-0.3, 3.42, 0.1),
            (0.35, 3.4, 0.12), (-0.5, 2.75, 0.08), (0.45, 2.15, 0.08), (-1.15, 3.2, 0.13),
            (1.2, 2.9, 0.12)]


def mirror_tiles():
    """PROXY: square mirror tile centres along a diagonal reroute band (size, list)."""
    size, step = 0.17, 0.205
    ang = math.radians(32)
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(-14, 15):
        for j in range(-1, 1):
            p = (i + 0.5) * step
            q = (j + 0.5) * step + 0.0
            x = p * ca - q * sa
            y = 2.45 + p * sa + q * ca
            pts.append((x, y))
    g = _lcg(77)
    pts = [pp for pp in pts if next(g) > 0.12]  # a few tiles missing (salvaged)
    return size, ang, pts


SOLDER = (0.0, 1.66, 0.13)   # PATCH solder blob (x, y, radius)
SEAM_X = 0.0                  # TROJAN seam: radial line along the axis
RIBBON_Y = (1.52, 1.78)       # TROJAN ribbon band (tangential)
CORE_INSET = 0.16             # ZERO-DAY core inset under the glass
CUBE = (0.0, 1.86, 0.36)      # SANDBOX cube centre (x, y) and edge
FIN_PITCH = 0.27              # FIREWALL fin pitch
FIN_W = 0.13
