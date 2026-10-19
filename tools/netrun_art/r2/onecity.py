"""One-city helpers the r2 rules read (art-pass `r2_onecity.py` / `layout36.py`, the parts that are pure functions of the lot
data): lot -> BU, building info, merged buildings, frontage rows, the perspective projection.

The art-pass modules read the layout from files; here every function takes the data it needs. Buildings are the raw lot-space
records (`q` polygon in lots, `z0` / `h` in lot-height units, `ts`, `ci`, `key`, `terr`); `bld_info` converts them to BU exactly
as the plate did (`h * KH`), so the layout pass can write back `want / KH` and read `(want / KH) * KH` like the plate."""
import math
from typing import Any, Dict, List, Sequence

from .config import ONECITY as OC

U = OC["u"]
CX, CY = OC["cx"], OC["cy"]
KH = U / OC["kh"][0] * OC["kh"][1]
FLOOR_BU = OC["floor_bu"]
FRONT_BAND = OC["front_band"]
MIN_WIDTH = OC["min_width"]
EXTEND = OC["extend"]
W_, H_ = OC["w"], OC["h"]


def W(p: Sequence[float]):
    """A lot point in BU (layout36.W): y is flipped."""
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


def bld_info(b: Dict[str, Any]) -> Dict[str, Any]:
    """BU record of a raw building (r2_onecity.bld_info)."""
    q = [W(p) for p in b["q"]]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return dict(key=b["key"], uid="%d_%d" % (b["ci"], b["key"]), q=q, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), z0=b["z0"] * KH,
                h=b["h"] * KH, ts=b["ts"])


def merged_buildings(buildings: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Street-level bases with the stacked parts above them merged in (r2_onecity.merged_buildings). Adds `terr` from the raw record
    so the plan can read a district per base (the art-pass keeps a separate key -> terr map)."""
    B = [bld_info(b) for b in buildings]
    bases = [b for b in B if b["z0"] <= 0.05]
    ups = [b for b in B if b["z0"] > 0.05]
    for b in bases:
        b["top"] = b["h"]
        b["parts"] = [b["key"]]
        b["parts_uid"] = [b["uid"]]
    for u in ups:
        cx, cy = (u["x0"] + u["x1"]) / 2, (u["y0"] + u["y1"]) / 2
        for b in bases:
            if b["x0"] <= cx <= b["x1"] and b["y0"] <= cy <= b["y1"]:
                b["top"] = max(b["top"], u["z0"] + u["h"])
                b["parts"].append(u["key"])
                b["parts_uid"].append(u["uid"])
                break
    for b in bases:
        b["h"] = b["top"]
    return bases


def frontage(B: Sequence[Dict[str, Any]], a, c, side: int) -> List[Dict[str, Any]]:
    """Buildings fronting the leg a -> c on `side` (+1 = left of the walking direction), ordered from a (r2_onecity.frontage)."""
    ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
    d = 1 if c[ax] > a[ax] else -1
    lo, hi = sorted((a[ax], c[ax]))
    if ax == 0:
        nrm = (0.0, side * d)
    else:
        nrm = (-side * d, 0.0)
    out = []
    for b in B:
        if b["z0"] > 0.05:
            continue
        if ax == 0:
            a0, a1 = b["x0"], b["x1"]
            near = b["y0"] if nrm[1] > 0 else b["y1"]
            dist = (near - a[1]) * nrm[1]
        else:
            a0, a1 = b["y0"], b["y1"]
            near = b["x0"] if nrm[0] > 0 else b["x1"]
            dist = (near - a[0]) * nrm[0]
        if a1 > lo and a0 < hi and FRONT_BAND[0] < dist < FRONT_BAND[1] and a1 - a0 >= MIN_WIDTH:
            mid = (a0 + a1) / 2
            out.append(dict(b, along=(mid - a[ax]) * d, face=near, nrm=nrm, axis=ax, dirn=d))
    out.sort(key=lambda r: (r["along"], r["key"]))
    return out


def basis(c: Dict[str, Any]):
    """Camera right / up / forward (layout36.basis)."""
    yw, pt = math.radians(c["yaw"]), math.radians(c["pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    right = (math.sin(yw), -math.cos(yw), 0.0)
    up = (right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0])
    return right, up, fwd


def project(c: Dict[str, Any], x: float, y: float, z: float = 0.0, w: float = W_, h: float = H_):
    """Pixel of a world point under a perspective camera `c` (layout36.project, persp branch only: the street cameras are perspective)."""
    r, u, f = basis(c)
    lo = c["persp"]["loc"]
    d = (x - lo[0], y - lo[1], z - lo[2])
    zc = max(1e-3, sum(d[i] * f[i] for i in range(3)))
    k = c["persp"]["lens"] / 36.0
    xc = sum(d[i] * r[i] for i in range(3)) / zc * k - c["persp"].get("sx", 0.0)
    yc = sum(d[i] * u[i] for i in range(3)) / zc * k - c["persp"].get("sy", 0.0)
    return ((xc + 0.5) * w, h / 2.0 - yc * w)


def proj(c: Dict[str, Any], p: Sequence[float]):
    """`project` of a 3-point at the plate's 1920 x 1080."""
    return project(c, p[0], p[1], p[2], W_, H_)
