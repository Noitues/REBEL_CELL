"""section: the section cut by zoom and the HQ per-frame section params (spec 5.3, 7.4; review Q3.4-Q3.9).

Ports `HK/downtown.py` 46d161ce `section_params`, `SB/sb_ocjobs.py` c83e3b00 `zcut` and `look_w`, and the pure constants
of `HK/section.py`. The Blender shader insertion (`HK/section.py:insert`, `M44/onecity_build.py:section`) is NA-05, not here.
Kit-unit pads convert with `K_UNITS` (and `K_FIT` when the HQ scene is scaled uniformly, O-K). `zcut` is a height above
the local ground (spec 5.3: the cut plane is `ground_z + z_cut`). Standard library only.
"""
import math
from typing import Any, Dict, Optional, Sequence, Tuple

from .units import K_FIT, K_UNITS, kit, smoothstep01

NO_CUT = 1.0e4                          # "no cut" sentinel returned while the smoothstep is 0
ZCUT = dict(zf=60.0, zn=0.4, a=0.25, b=0.85)    # section_by_zoom on zoom_dive (SB/look_preset.py:90)
LOOK_BLEND = (0.20, 0.55)               # look_blend_by_zoom on zoom_dive
POCHE = (0.010, 0.010, 0.013)           # cut-top colour (HK/section.py:33)
EDGE_COL = (0.55, 0.68, 0.85)           # ghost edge colour
CONSTS: Dict[str, Any] = dict(          # section.consts (review Q3.8): kit values x K_UNITS (x K_FIT for the HQ scene)
    k_units=K_UNITS, k_fit=K_FIT, band_overview=kit(30.0) * K_FIT, band_rooms=kit(24.0) * K_FIT,
    zref_margin=kit(1.5) * K_FIT, plinth=kit(0.6), widen=0.45)

Pt3 = Sequence[float]


def zcut(zoom: float, z: Optional[Dict[str, float]] = None) -> float:
    """Cut height (above local ground) at `zoom_dive`: log-interpolated 60 -> 0.4 over a smoothstep of 0.25..0.85."""
    c = z or ZCUT
    u = smoothstep01((zoom - c["a"]) / (c["b"] - c["a"]))
    return math.exp(math.log(c["zf"]) + (math.log(c["zn"]) - math.log(c["zf"])) * u) if u > 0 else NO_CUT


def look_w(zoom: float, blend: Tuple[float, float] = LOOK_BLEND) -> float:
    """Mainline -> AAA-2 look weight at `zoom_dive` (smoothstep over `look_blend`)."""
    return smoothstep01((zoom - blend[0]) / (blend[1] - blend[0]))


def section_params(pose_loc: Pt3, keep: Optional[Sequence[Any]], rooms_pts: Optional[Sequence[Pt3]] = None,
                   zref: Optional[float] = None, zref_k: float = 1.0) -> Dict[str, Any]:
    """The per-pose HQ section cut (HQ only; the street uses `zcut`).

    `keep` is the compound support: `("rect", hx, hy)` or `("circ", r)` in BU (overview, `rooms_pts` None); with
    `rooms_pts` the focus is their centroid. `zref_k` lowers the sight-line target for decision poses. Pads and the
    height margin come from `CONSTS`. Returns the `sec_*` keys (`sec_on` is a bool).
    """
    cx, cy, cz = pose_loc
    if rooms_pts:
        ox = sum(p[0] for p in rooms_pts) / len(rooms_pts)
        oy = sum(p[1] for p in rooms_pts) / len(rooms_pts)
    else:
        ox = oy = 0.0
    dx, dy = cx - ox, cy - oy
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    if rooms_pts:
        s0 = max((p[0] - ox) * ux + (p[1] - oy) * uy for p in rooms_pts)
        w0 = max(abs(-(p[0] - ox) * uy + (p[1] - oy) * ux) for p in rooms_pts) + CONSTS["band_rooms"]
        zr = min(p[2] for p in rooms_pts) if zref is None else zref
    else:
        k = keep or ("circ", 0.0)
        if k[0] == "rect":
            s0 = k[1] * abs(ux) + k[2] * abs(uy)
            w0 = k[1] * abs(uy) + k[2] * abs(ux) + CONSTS["band_overview"]
        else:
            s0 = k[1]
            w0 = k[1] + CONSTS["band_overview"]
        zr = 0.0 if zref is None else zref
    slope = (cz - zr) / max(1.0, L - s0)
    if rooms_pts and zref is None:
        zr = zr * zref_k
    return dict(sec_on=True, sec_ox=ox, sec_oy=oy, sec_ux=ux, sec_uy=uy, sec_s0=s0, sec_w0=w0, sec_slope=slope,
                sec_zref=zr - CONSTS["zref_margin"], sec_widen=CONSTS["widen"], sec_plinth=CONSTS["plinth"])


def section_block() -> Dict[str, Any]:
    """The `section` block of poses_<run>.json: consts, `zcut` and `look_blend` (both on `zoom_dive`)."""
    return dict(consts=dict(CONSTS), zcut=dict(ZCUT), look_blend=list(LOOK_BLEND), no_cut=NO_CUT,
                poche=list(POCHE), edge_col=list(EDGE_COL))
