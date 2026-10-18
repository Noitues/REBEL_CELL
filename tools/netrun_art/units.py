"""Unit factors and conversions shared by the NA-03 modules (NA03_NA04_ANSWERS O-H, O-K).

BU = one-city Blender unit. Plan coordinates are `[x, y]` (x east, y north), heights are BU above local ground.
The HQ kit works in kit units (storey 8 BU); one-city storeys are `FLOOR_BU` (1.9 BU), so `K_UNITS` = 1.9 / 8.
Standard library only.
"""
import math
from typing import Sequence

FLOOR_BU = 1.9              # one storey in BU (the mainline window pitch)
KIT_STOREY = 8.0            # one storey in HQ-kit units
K_UNITS = FLOOR_BU / KIT_STOREY   # 0.2375: kit unit -> BU (spec section 8 rescale rule)
K_FIT = 1.0                 # street: 1. The HQ scene factor when the whole scene is scaled uniformly (O-K; AD 2026-10-18)
LOT_BU_DEFAULT = 6.0        # BU per lot (city.json header carries the real value)
ROUND = 1e-4                # placement positions are rounded to this before hashing (spec 3.5 rule 4)

Vec3 = Sequence[float]


def kit(v: float) -> float:
    """A kit-unit length in BU."""
    return v * K_UNITS


def r4(v: float) -> float:
    """Round to 1e-4 half up, `floor(x * 1e4 + 0.5) / 1e4` (spec 12.8 rule 1)."""
    return math.floor(v * 1e4 + 0.5) / 1e4


def sub3(a: Vec3, b: Vec3) -> list:
    """a - b."""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def dot3(a: Vec3, b: Vec3) -> float:
    """Dot product."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def dist3(a: Vec3, b: Vec3) -> float:
    """Euclidean distance."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def smoothstep01(t: float) -> float:
    """Smoothstep of an already clamped-or-not parameter."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)
