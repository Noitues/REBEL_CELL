"""ART-5 5b: the REBEL_CELL crest (bible 4.4, round 34 LOCKED), as pure functions on the iso SCREEN PLANE.

Ported from art-pass d14b8f6 docs/concepts/round34_rebel_cell/scripts/map34.py (Crest.zone, ring_rho, ring_weight,
the dispatch glitch bands), with the map's 2D pixel space replaced by the 3D iso camera's screen plane in BU, so the
same rule works for the glTF district, the crest mask texture and the game's CityModel window shader.

Screen plane: X = dot(p, RIGHT), Y = dot(p, UP) for a point p in the concept frame (x = lot x, y = -lot y, z up),
with the game camera (yaw 135, pitch 40). The palm (the district's anchor) projects to (0, 0); the crest's centre
stands CREST_LIFT_BU above it; crest units: k = CREST_H_BU / 14.8 BU per unit, u to the right, v up from the
crest's bottom edge.
Zones: 0 outside, 1 the red fist, 2 a blacked-out detail line (finger splits, thumb upper edge, thumb tip, half palm
line on the right, the vertical tucked-thumb line; round 34: no knuckle crease).
"""
import math
import random

import landmark_spec_v1 as SPEC

_Y = math.radians(SPEC.YAW)
_P = math.radians(SPEC.PITCH)
FWD = (math.cos(_Y) * math.cos(_P), math.sin(_Y) * math.cos(_P), -math.sin(_P))
RIGHT = (math.sin(_Y), -math.cos(_Y), 0.0)
UP = (RIGHT[1] * FWD[2] - RIGHT[2] * FWD[1], RIGHT[2] * FWD[0] - RIGHT[0] * FWD[2], RIGHT[0] * FWD[1] - RIGHT[1] * FWD[0])

H = SPEC.CREST_H_BU
K = H / SPEC.CREST_UNITS_H
YC = SPEC.CREST_LIFT_BU            # crest centre (screen Y)
YB = YC - H / 2.0                  # crest bottom (screen Y)
RX, RY = SPEC.RING_RX * H, SPEC.RING_RY * H
THUMB_U = 0.4
FINGERS = [(-5.4, -2.75), (-2.75, -0.05), (-0.05, 2.75), (2.75, 5.6)]
LW = 0.75
_r = random.Random(29)
BANDS = {}
for _b in range(-40, 40):  # map34: dispatch screen-row bands shifted sideways (the glitch); same draw order as map34
    BANDS[_b] = _r.choice([0, 0, 0, 0, _r.uniform(-1.3, 1.3)])


def screen(p):
    """Screen-plane (X, Y) in BU of concept-frame point p."""
    return (p[0] * RIGHT[0] + p[1] * RIGHT[1] + p[2] * RIGHT[2], p[0] * UP[0] + p[1] * UP[1] + p[2] * UP[2])


def uv(X, Y, dispatch=False):
    u = X / K
    v = (Y - YB) / K
    if dispatch:
        u -= BANDS.get(int(math.floor(v / 0.9)), 0.0)
    return u, v


def zone_uv(u, v):
    """map34.Crest.zone in crest units."""
    if v < 0 or v > 14.2 or u < -5.4 or u > 5.6:
        return 0
    if v < 5.2 and not (-3.6 <= u <= 3.6):
        return 0
    if v > 13.3:
        for i, (a0, a1) in enumerate(FINGERS):
            top = 13.6 + (0.6 if i in (1, 2) else 0.0)
            c = (a0 + a1) / 2
            r = (a1 - a0) / 2
            if a0 <= u <= a1 and v <= top - (1 - math.sqrt(max(0.0, 1 - ((u - c) / r) ** 2))) * 0.9:
                break
        else:
            return 0
    for (a0, a1) in FINGERS[:-1]:
        if abs(u - (a1 + 0.12)) < LW / 2 and v > 8.3:
            return 2
    if abs(v - 8.25) < LW / 2 and -5.4 <= u <= 4.4:
        return 2
    if 4.4 <= u <= 5.6 and abs(v - (8.25 - (u - 4.4) * 1.6)) < LW * 0.6:
        return 2
    if abs(v - 5.2) < LW / 2 and THUMB_U <= u <= 5.0:
        return 2
    if abs(u - THUMB_U) < LW / 2 and 5.2 - LW / 2 <= v <= 8.25:
        return 2
    return 1


def zone(X, Y, dispatch=False):
    return zone_uv(*uv(X, Y, dispatch))


def ring_rho(X, Y):
    dx, dy = X / RX, -(Y - YC) / RY   # map34 works in y-down pixels: keep its rough outline the same way round
    a = math.atan2(dy, dx)
    rough = 1.0 + 0.10 * math.sin(3 * a + 0.7) + 0.07 * math.sin(7 * a + 2.1) + 0.04 * math.sin(13 * a)
    return math.hypot(dx, dy) / rough


def ring_weight(X, Y):
    """1 inside the blackout ring band (between the fist and the outer edge), fading out past the edge; 0 on the fist."""
    r = ring_rho(X, Y)
    if r < 0.5 or zone(X, Y) == 1:
        return 0.0
    if r < 1.7:
        return 1.0
    return max(0.0, 1.0 - (r - 1.7) / 0.4)
