"""Street round 2: the facade kits of materials.mix, as per-cell generators (port of the art-pass `r2_kits.py`).

A face is split into cells (one floor tall, about one module wide), so a room cut can remove exactly the cells inside an opening,
and the closed wall over an opening is built by the SAME kit generator. The generators write into recorders (`Faces`) by
material: conc (rough concrete), glass (dark glossy curtain glass), panel (painted metal panels, grilles, mullions), win (lit
glazing / windows, emissive), neon (emissive trims). Nothing is meshed here: a face record is `pts, col, bid, fj`; a roof piece
is a primitive record (`cyl36`, `box`, `beam`) that the renderer (step 2) turns into geometry.

Kits (module index m = 0..2 from repetition.guard changes the cell width / slat count / slot spacing):
  glass_curtain  glass cells, mullions + spandrel bands in panel, 22 % of floors lit as office strips, a few lit cells
  panel_grille   panel cells, a louvre of 2-4 slats per floor, small warm windows (p 0.35), an AC unit now and then
  lit_atrium     the lowest 2-3 floors fully glazed and lit (warm or teal), concrete above with continuous lit slots
  concrete_band  the mainline kit's own facade (fgrid facets, scattered windows, ledges) - not generated here
The part ids (`bid`) the plate drew from a global stream are counter ids here (`Ids`); they never feed a rule.
"""
import math
from typing import Any, Callable, Dict, List, Optional, Sequence

from . import facade as FC
from .config import KITS

_KIT_W = {k: tuple(v) for k, v in KITS["kit_w"].items()}
GLASS_COL = tuple(KITS["glass_col"])
METAL_COL = tuple(KITS["metal_col"])
WIN_COLS = [tuple(c) for c in KITS["win_cols"]]
RED = tuple(KITS["red"])


class Faces:
    """A recorder with the accumulator interface the kits draw into (`face`), plus primitive records for roof pieces."""

    def __init__(self) -> None:
        self.faces: List[Dict[str, Any]] = []
        self.prims: List[List[Any]] = []

    def face(self, pts, col, bid, fj=None) -> None:
        """One polygon: points, colour, part id, tone jitter (None = the renderer draws it)."""
        self.faces.append(dict(pts=[list(p) for p in pts], col=list(col), bid=list(bid) if isinstance(bid, (tuple, list)) else bid, fj=fj))

    def prim(self, kind: str, *args: Any) -> None:
        """A roof primitive: ('cyl36', cx, cy, z0, z1, rad, col), ('box', x0, y0, z0, x1, y1, z1, col), ('beam', p0, p1, w, col)."""
        self.prims.append([kind] + [list(a) if isinstance(a, (tuple, list)) else a for a in args])


class Ids:
    """Counter part ids (the plate drew them from a global random stream; they only tag parts)."""

    def __init__(self) -> None:
        self.n = 0

    def __call__(self) -> int:
        self.n += 1
        return self.n


def new_accs() -> Dict[str, Faces]:
    """One recorder per material."""
    return {k: Faces() for k in ("conc", "glass", "panel", "win", "neon")}


def _cell_pts(a, c, z0, z1, u0, u1, nx, ny, off):
    """A face rectangle between along-fractions u0..u1 and heights z0..z1, pushed `off` along the normal."""
    p0 = (a[0] + (c[0] - a[0]) * u0 + nx * off, a[1] + (c[1] - a[1]) * u0 + ny * off)
    p1 = (a[0] + (c[0] - a[0]) * u1 + nx * off, a[1] + (c[1] - a[1]) * u1 + ny * off)
    return [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)]


def _boxq(acc, a, c, z0, z1, u0, u1, nx, ny, d0, d1, col, bid):
    """A small box on the face: along u0..u1, heights z0..z1, depth d0..d1 out of the face (front, bottom, top)."""
    f = _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d1)
    b = _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d0)
    acc.face(f, col, bid, fj=0.5)
    acc.face([b[1], b[0], f[0], f[1]], col, bid, fj=0.45)     # bottom
    acc.face([f[3], f[2], b[2], b[3]], col, bid, fj=0.55)     # top


def kit_face(kit, a, c, z0, z1, nx, ny, col, r, accs, module=0, fl=1.9, lit_low=None, lite=False, rh=None, rid: Optional[Callable[[], Any]] = None):
    """Draw one face (a -> c along the bottom, z0..z1) in `kit` into accs (dict conc / glass / panel / win / neon).
    rh = the building's rhythm record (facade.make_rhythm): bay widths, floor heights, window module per floor band, setback,
    balconies. Without it the face is the uniform grid of the first r2 pass. `rid` makes part ids (default: a fresh counter)."""
    rid = rid or Ids()
    L = math.hypot(c[0] - a[0], c[1] - a[1])
    h = z1 - z0
    if L < 0.5 or h < 0.5:
        return
    zs = FC.floor_bounds(rh, z0, h, fl)
    nf = len(zs) - 1
    mods = [FC.floor_module(rh, j, module) for j in range(nf)]
    # one bay list per floor band (the bay edges change where the module changes: mixed window modules)
    edges, band_of = [], []
    for j in range(nf):
        if j and mods[j] == mods[j - 1]:
            edges.append(edges[-1])
        else:
            edges.append(FC.bay_edges(L, _KIT_W[kit][mods[j] % 3], rh, j))
    ins = [FC.floor_inset(rh, j) for j in range(nf)]
    bid = rid()
    floor0 = int(round(z0 / fl))
    ac_ = tuple(rh["acc"]) if rh else (0.4, 0.8, 1.0)
    wt = [tuple(t) for t in rh["tones"]] if rh and rh.get("tones") else WIN_COLS      # at most 2 window tones per building
    rel = rh.get("relief", 0.0) if rh else 0.0                 # per-cell depth relief (geometry, not colour)
    tlo, thi = rh["tone"] if rh and rh.get("tone") else (1.0, 1.0)

    def tn(cc):
        k = r.uniform(tlo, thi)
        return (min(1.0, cc[0] * k), min(1.0, cc[1] * k), min(1.0, cc[2] * k))

    def cp(j, za, zb, u0, u1, off):
        return _cell_pts(a, c, za, zb, u0, u1, nx, ny, off - ins[j])

    def bq(j, za, zb, u0, u1, d0, d1, colr):
        _boxq(accs["panel"], a, c, za, zb, u0, u1, nx, ny, d0 - ins[j], d1 - ins[j], colr, bid)
    if kit == "glass_curtain":
        lit_floor = [r.random() < 0.22 for _ in range(nf)]
    for j in range(nf):
        za, zb = zs[j], zs[j + 1]
        for i, (u0, u1) in enumerate(edges[j]):
            du = u1 - u0
            m = mods[j]
            if kit == "glass_curtain":
                accs["glass"].face(cp(j, za, zb, u0, u1, 0.0), tn(GLASS_COL), bid, fj=0.5)
                mw = 0.06 / max(L, 1e-3)
                if not lite and (m != 1 or i % 2 == 0) and r.random() > 0.3:       # mullions are not on every bay edge
                    accs["panel"].face(cp(j, za, zb, u0, u0 + mw * r.choice((1, 1, 2, 3)), 0.05), METAL_COL, bid, fj=0.5)
                if not lite and r.random() > 0.2:
                    accs["panel"].face(cp(j, za, min(zb, za + r.uniform(0.08, 0.36)), u0, u1, 0.04), METAL_COL, bid, fj=0.5)
                if lit_floor[j] and r.random() < 0.85:
                    sv = 0.5 + 0.5 * r.random()
                    wc = (0.78, 0.9, 1.0) if r.random() < 0.7 else (0.55, 1.0, 0.9)
                    accs["win"].face(cp(j, za + 0.35, zb - 0.3, u0 + 0.06 * du, u1 - 0.06 * du, 0.02), tuple(v * sv for v in wc), (0, 0, 0), fj=0.5)
                elif r.random() < 0.08:
                    accs["win"].face(cp(j, za + 0.4, zb - 0.35, u0 + 0.12 * du, u1 - 0.12 * du, 0.02),
                                     tuple(v * (0.4 + 0.4 * r.random()) for v in r.choice(wt)), (0, 0, 0), fj=0.5)
            elif kit == "panel_grille":
                slats = 2 + m
                pc = tuple(v * 0.9 for v in col)
                dk = tuple(v * 0.55 for v in col)
                accs["panel"].face(cp(j, za, zb, u0, u1, r.uniform(0.0, rel)), tn(pc), bid, fj=0.4 + 0.2 * r.random())
                zz = zb - r.uniform(0.08, 0.2)
                for k in range(0 if lite else slats):               # slats at irregular pitch and thickness (a periodic louvre repeats)
                    th = r.uniform(0.04, 0.1)
                    if zz - th > za:
                        bq(j, zz - th, zz, u0, u1, 0.0, r.uniform(0.12, 0.26), dk)
                    zz -= r.uniform(0.14, 0.32)
                if r.random() < 0.35:
                    sv = 0.7 + 0.3 * r.random()
                    um = (u0 + u1) / 2
                    hw = min(0.3 / max(L, 1e-3), du * 0.4)
                    accs["win"].face(cp(j, za + 0.45, min(zb - 0.1, za + 1.0), um - hw, um + hw, 0.03),
                                     tuple(v * sv for v in r.choice(wt)), (0, 0, 0), fj=0.5)
                if r.random() < 0.05 and j > 0:
                    um = (u0 + u1) / 2
                    hw = min(0.35 / max(L, 1e-3), du * 0.4)
                    _boxq(accs["conc"], a, c, za + 0.05, za + 0.5, um - hw, um + hw, nx, ny, 0.0 - ins[j], 0.45 - ins[j], (0.32, 0.32, 0.35), bid)
            elif kit == "lit_atrium":
                if j == 0 and i == 0:
                    warm = r.random() < 0.55
                    lit_pal = ((1.0, 0.74, 0.46) if warm else (0.45, 0.95, 1.0), r.choice([(1.0, 0.3, 0.7), (0.3, 0.85, 1.0), (1.0, 0.6, 0.2), (0.7, 0.45, 1.0)]))
                    low = lit_low if lit_low is not None else 2 + r.randrange(2)
                lc, sc = lit_pal
                every = 2 + m
                if floor0 + j < low:
                    accs["win"].face(cp(j, za + 0.08, zb - 0.08, u0 + 0.03 * du, u1 - 0.03 * du, 0.0),
                                     tuple(v * (0.55 + 0.25 * r.random()) for v in lc), (0, 0, 0), fj=0.5)
                    accs["panel"].face(cp(j, za, zb, u0, min(u1, u0 + 0.07 / max(L, 1e-3)), 0.04), METAL_COL, bid, fj=0.5)
                    accs["panel"].face(cp(j, zb - 0.1, zb, u0, u1, 0.04), METAL_COL, bid, fj=0.5)
                else:
                    accs["conc"].face(cp(j, za, zb, u0, u1, r.uniform(0.0, rel)), tn(col), bid, fj=0.45 + 0.1 * r.random())
                    if i % every == 0:
                        hw = min(0.11 / max(L, 1e-3), du * 0.4)
                        accs["win"].face(cp(j, za, zb, (u0 + u1) / 2 - hw, (u0 + u1) / 2 + hw, 0.03), tuple(v * 0.75 for v in sc), (0, 0, 0), fj=0.5)
                    elif r.random() < 0.1:
                        accs["win"].face(cp(j, za + 0.5, zb - 0.4, u0 + 0.2 * du, u1 - 0.2 * du, 0.02),
                                         tuple(v * 0.6 for v in r.choice(wt)), (0, 0, 0), fj=0.5)
    if rh and not lite:
        # setback ledge: a slab and a lit lip where the facade steps back
        sb = rh.get("setback")
        if sb and 0 < sb["floor"] < nf:
            zl = zs[sb["floor"]]
            d = sb["d"]
            q0 = _cell_pts(a, c, zl, zl, 0.0, 1.0, nx, ny, 0.0)
            q1 = _cell_pts(a, c, zl, zl, 0.0, 1.0, nx, ny, -d)
            accs["conc"].face([q0[0], q0[1], q1[1], q1[0]], tuple(v * 0.8 for v in col), bid, fj=0.5)
            ln = _cell_pts(a, c, zl - 0.06, zl + 0.02, 0.0, 1.0, nx, ny, 0.04)
            accs["neon"].face(ln, ac_, (0, 0, 0), fj=0.5)
        # balconies: slab, rail, a lit door behind
        for bc in rh.get("balc", []):
            j = bc["floor"]
            if j >= nf or bc["floor"] < 1:
                continue
            wf = min(0.9, bc["w"] / L)
            u0 = max(0.02, bc["c"] - wf / 2)
            u1 = min(0.98, u0 + wf)
            zf = zs[j]
            dp = bc["depth"]
            _boxq(accs["conc"], a, c, zf, zf + 0.14, u0, u1, nx, ny, -ins[j], dp - ins[j], tuple(v * 0.85 for v in col), bid)
            rz = zf + 0.14 + 0.85
            q = _cell_pts(a, c, rz, rz + 0.05, u0, u1, nx, ny, dp - ins[j])
            accs["panel"].face(q, METAL_COL, bid, fj=0.5)
            for pu in (u0, u1):
                accs["panel"].face(_cell_pts(a, c, zf + 0.14, rz, pu, pu + 0.04 / max(L, 1e-3), nx, ny, dp - ins[j]), METAL_COL, bid, fj=0.5)
            if bc["lit"] and zs[j + 1] - zf > 1.2:
                accs["win"].face(_cell_pts(a, c, zf + 0.15, min(zs[j + 1] - 0.2, zf + 1.6), u0 + wf * 0.25, u1 - wf * 0.25, nx, ny, 0.045 - ins[j]),
                                 tuple(v * 0.7 for v in ac_), (0, 0, 0), fj=0.5)


def roof_clutter(kit, top, zt, r, acc_s, acc_n, kinds, ants=None, rid: Optional[Callable[[], Any]] = None):
    """Roof clutter by kit (>= 3 kinds over a frontage): ac, tank, vent_stack, antenna, dish. `kinds` collects them. Solid pieces are
    primitive records in `acc_s` (`cyl36` / `box` / `beam`, see `Faces.prim`), the antenna lamp is a face in `acc_n`, `ants` collects
    the aircraft-light positions."""
    rid = rid or Ids()
    ants = ants if ants is not None else []
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if x1 - x0 < 2.2 or y1 - y0 < 2.2:
        return
    if kit in ("glass_curtain", "panel_grille"):
        for _ in range(r.randint(1, 3)):                       # vent stacks
            vx, vy = r.uniform(x0 + 0.5, x1 - 0.5), r.uniform(y0 + 0.5, y1 - 0.5)
            acc_s.prim("cyl36", vx, vy, zt, zt + r.uniform(1.0, 2.4), r.uniform(0.25, 0.45), (0.3, 0.3, 0.34))
        kinds.add("vent_stack")
    if kit in ("panel_grille", "lit_atrium"):
        for _ in range(r.randint(1, 3)):                       # AC units
            vx, vy = r.uniform(x0 + 0.4, x1 - 1.3), r.uniform(y0 + 0.4, y1 - 1.1)
            acc_s.prim("box", vx, vy, zt, vx + 0.9, vy + 0.7, zt + 0.55, (0.34, 0.34, 0.38))
        kinds.add("ac")
    if kit in ("lit_atrium", "glass_curtain") and r.random() < 0.6:   # dish on a stub
        dx, dy = r.uniform(x0 + 1.0, x1 - 1.0), r.uniform(y0 + 1.0, y1 - 1.0)
        acc_s.prim("beam", (dx, dy, zt), (dx, dy, zt + 1.0), 0.14, (0.25, 0.25, 0.3))
        rr = r.uniform(0.6, 1.0)
        pts = [(dx + rr * math.cos(2 * math.pi * k / 10), dy - 0.3, zt + 1.4 + rr * math.sin(2 * math.pi * k / 10)) for k in range(10)]
        acc_s.face(pts, (0.55, 0.55, 0.6), rid())
        kinds.add("dish")
    if r.random() < 0.35:                                     # antenna with a red light
        ax, ay = (x0 + x1) / 2 + r.uniform(-0.5, 0.5), (y0 + y1) / 2
        hh = r.uniform(2.5, 5.5)
        acc_s.prim("beam", (ax, ay, zt), (ax, ay, zt + hh), 0.12, (0.25, 0.25, 0.3))
        acc_n.face([(ax - 0.22, ay, zt + hh), (ax + 0.22, ay, zt + hh), (ax + 0.22, ay, zt + hh + 0.35), (ax - 0.22, ay, zt + hh + 0.35)],
                   RED, (0, 0, 0))
        ants.append((ax, ay, zt + hh + 0.2))
        kinds.add("antenna")
