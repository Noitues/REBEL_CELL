"""lod: atmosphere detail bands by camera distance and the two zoom converters (spec 5.1, 5.2; review Q3.1-Q3.3).

Ports `HK/lod.py` c47c67a9 and the band numbers of `SB/look_preset.py` c83e3b00. `weights` takes a DISTANCE in BU, never a
zoom number. The bands are stored as `zoom_dive` pairs `(a, b)` (the source of truth); the distances come from
`d(z) = D0 * (D1 / D0) ** z` at the table anchors (3833, 114.6 BU). Weight 1 at the near end, 0 at the far end:
`t = clamp(ln(d_far / d) / ln(d_far / d_near))`, `w = t * t * (3 - 2 * t)` (smoothstep in `ln d`). Band names follow
AD resolution 3 (`fog_octaves`, `wisps`, ...). Standard library only.
"""
import math
from typing import Any, Dict, Optional, Tuple

from .units import smoothstep01

D0 = 3833.0      # BU, the 460 BU HQ frame emulated by a 300 mm lens (table anchor; spec 5.1)
D1 = 114.6       # BU, the street OVERVIEW (table anchor)

# The six `lod` bands, zoom_dive pairs (a, b)
DEFAULT_BANDS: Dict[str, Tuple[float, float]] = {
    "fog_octaves": (0.25, 0.60),
    "wisps": (0.45, 0.70),
    "plumes": (0.50, 0.72),
    "signage": (0.60, 0.82),
    "small_lights": (0.75, 0.92),
    "puddles_sharp": (0.85, 1.00),
}
FLOORS: Dict[str, float] = {"signage": 0.0, "small_lights": 0.25}
# Look ramps owned by `look.preset` (reported next to the bands; not `lod` weights)
RAMPS: Dict[str, Tuple[float, float]] = {
    "fog_density": (0.30, 0.90), "cityglow": (0.30, 0.90), "look_blend": (0.20, 0.55), "section": (0.25, 0.85)}
RAMP_LEVELS: Dict[str, float] = {"fog_density": 0.35, "cityglow": 0.45}   # level at zoom 0


def band_distance(z: float, d0: float = D0, d1: float = D1) -> float:
    """Camera distance of `zoom_dive` value `z` at the anchors: `d0 * (d1 / d0) ** z`."""
    return d0 * (d1 / d0) ** z


def zoom_dive(d: float, d0: float, d1: float) -> float:
    """`zoom_dive` (0 = HQ page distance `d0`, 1 = street OVERVIEW distance `d1`), clamped (spec 5.1).

    `d` is the distance from the camera to the OVERVIEW target; `d0`, `d1` are per run.
    """
    return max(0.0, min(1.0, math.log(d0 / max(d, 1e-3)) / math.log(d0 / d1)))


def zoom_detail(d: float, d_ov: float, d_dec: float) -> float:
    """`zoom_detail` (0 = OVERVIEW distance, 1 = DECISION distance), clamped (`HK/lod.py` `zoom`)."""
    return max(0.0, min(1.0, math.log(d_ov / max(d, 1e-3)) / math.log(d_ov / d_dec)))


def dive_from_detail(zd: float, d_ov: float, d_dec: float, d0: float) -> float:
    """Spec 5.1 relation `zoom_dive = 1 + zoom_detail * ln(d_ov / d_dec) / ln(d0 / d_ov)` for `zd >= 0` (saturates at 1)."""
    return min(1.0, 1.0 + zd * math.log(d_ov / d_dec) / math.log(d0 / d_ov))


def sstep(x: float, a: float, b: float) -> float:
    """Smoothstep of `x` over `a..b` (`b - a` floored at 1e-6)."""
    return smoothstep01((x - a) / max(1e-6, b - a))


def band_edges(ab: Tuple[float, float], d0: float = D0, d1: float = D1) -> Tuple[float, float]:
    """`(d_far, d_near)` in BU of a zoom pair at the anchors."""
    return band_distance(ab[0], d0, d1), band_distance(ab[1], d0, d1)


def band(d: float, name: str, bands: Optional[Dict[str, Tuple[float, float]]] = None) -> float:
    """Band weight 0..1 at camera distance `d` (0 at the far edge, 1 at the near edge)."""
    far, near = band_edges((bands or DEFAULT_BANDS)[name])
    t = max(0.0, min(1.0, math.log(far / max(d, 1e-3)) / math.log(far / near)))
    return smoothstep01(t)


def weights(d: float, bands: Optional[Dict[str, Tuple[float, float]]] = None,
            floors: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """`{band: weight}` at camera distance `d`; a band with a floor f gives `f + (1 - f) * w`."""
    fl = FLOORS if floors is None else floors
    out = {}
    for k in sorted(bands or DEFAULT_BANDS):
        f = fl.get(k, 0.0)
        out[k] = f + (1.0 - f) * band(d, k, bands)
    return out


def lod_block() -> Dict[str, Any]:
    """The `lod` block of poses_<run>.json: anchors, the zoom pairs, the computed distances, the floors."""
    bands = {}
    for k, ab in sorted({**DEFAULT_BANDS, **RAMPS}.items()):
        far, near = band_edges(ab)
        bands[k] = dict(a=ab[0], b=ab[1], d_far=far, d_near=near)
    return dict(d0=D0, d1=D1, bands=bands, floors=dict(sorted(FLOORS.items())), ramp_levels=dict(sorted(RAMP_LEVELS.items())),
                lod_bands=sorted(DEFAULT_BANDS))
