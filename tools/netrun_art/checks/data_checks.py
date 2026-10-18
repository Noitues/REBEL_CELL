"""Data checks: 12.3.1 and 12.3.4 determinism, 12.4 rail and viaduct clearance, 12.5.1 and 12.5.3 beams,
12.6 parity and occlusion. Standard library only (no numpy), so the data-hash path stays free of it.

Input shapes (all canonical JSON, BU units; NA02 / NA03_NA04_ANSWERS O-C, O-H, O-5):
- `zoned`: `rail = {pts: [[x, y]..], half_clear, deck_z, side_cap, side_d, piers?: [[x, y]..]}`.
- `city` (city.json v1): `buildings[] = {bid, parts[] = {poly, z0, h, taper}}`, `streets[] = {lot: [i, j]}`, `lot_bu`,
  `origin_lot`. Plan BU to lots: `lx = x / lot_bu + origin_x`, `ly = origin_y - y / lot_bu`; a street tile is the lot
  cell `(floor(lx), floor(ly))` (assumption: a lot `[i, j]` covers `[i, i+1) x [j, j+1)`).
- `derive` (v2): `rooms{id: {front, back, bld}}`, `edges[] = {a, b, path}`; `occlusion = {params, buildings[]}`.
- `dress` (`dress_<run>.json` v1, review Q4): the typed lists `signs, lamps, washes, glows, beams, streak_lanes,
  fog_fields`. For 12.4.5c every list item with a `pos` is flattened to `(list name, pos)`; an `items[{kind, pos}]` list is
  rejected. `beams[] = {bid, pos [x, y, z], lean [x, y], sweep_deg, phase, pal}`.
- `beams` check input (built by `beams_input`): the dress `beams` plus `top` from city.json, the `spot {cone_deg, blend,
  shadow, media_linked}` / `shaft {material, shadow}` look.preset beam rig (`BEAM_RIG`, not stored per beam in dress) and
  `route_bids` = derive `route_keys` (bids).
Thresholds come from `composition.json` (`checks.data`). Every check returns records (see `report`).
"""
import hashlib
import importlib
import importlib.util
import math
import os
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .. import io
from .report import FAIL, NA, PASS, Record, record

Pt = Sequence[float]
Files = Dict[str, Any]


# ---------------------------------------------------------------- 12.3 determinism
def file_hashes(files: Files) -> Dict[str, str]:
    """SHA-256 hex of the canonical JSON bytes of each named object."""
    return {n: hashlib.sha256(io.canonical_dumps(o).encode("utf-8")).hexdigest() for n, o in sorted(files.items())}


def data_hash(files: Files) -> str:
    """One SHA-256 over the sorted `name:hash` lines of `file_hashes`."""
    h = file_hashes(files)
    return hashlib.sha256("".join(f"{n}:{v}\n" for n, v in h.items()).encode("utf-8")).hexdigest()


def load_producer(spec: str) -> Callable[..., Files]:
    """Producer function from `path/to/file.py:func` or `module:func`. It takes a layout seed (decimal string) and
    returns `{file name: object}`."""
    target, _, fn = spec.rpartition(":")
    if target.endswith(".py"):
        s = importlib.util.spec_from_file_location("na04_producer", target)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)  # type: ignore[union-attr]
    else:
        mod = importlib.import_module(target)
    return getattr(mod, fn)


def fresh_process_hash(spec: str, seed: str, hashseed: str, timeout: float = 120.0) -> str:
    """`data_hash` computed in a new Python process with PYTHONHASHSEED=`hashseed`."""
    tools = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = dict(os.environ, PYTHONHASHSEED=hashseed, PYTHONPATH=tools)
    r = subprocess.run([sys.executable, "-m", "netrun_art.checks.hash_worker", spec, seed], env=env, cwd=tools,
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("hash worker failed: " + r.stderr[-300:])
    return r.stdout.strip()


def check_determinism(spec: str, seeds: Sequence[str]) -> List[Record]:
    """12.3.1: twice in this process and once in a fresh process (different PYTHONHASHSEED) per seed."""
    producer = load_producer(spec)
    out = []
    for i, s in enumerate(seeds):
        a = data_hash(producer(s))
        b = data_hash(producer(s))
        c = fresh_process_hash(spec, s, str(1000 + i))
        ok = a == b == c
        out.append(record(f"12.3.1:{s}", PASS if ok else FAIL, a, "3 equal hashes",
                          "" if ok else f"in-process {a[:12]} {b[:12]}, fresh {c[:12]}"))
    return out


def check_seed_sensitivity(spec: str, seeds: Sequence[str]) -> List[Record]:
    """12.3.4 (a): the data hash differs for each consecutive seed pair (cyclic, so 3 seeds give 3 pairs)."""
    producer = load_producer(spec)
    hashes = {s: data_hash(producer(s)) for s in seeds}
    n = len(seeds)
    out = []
    for i in range(n if n > 2 else n - 1):
        s, t = seeds[i], seeds[(i + 1) % n]
        ok = hashes[s] != hashes[t]
        out.append(record(f"12.3.4a:{s}-{t}", PASS if ok else FAIL, hashes[s][:12], "hash differs",
                          "" if ok else "same hash for different seeds"))
    return out


def check_key_independence(before: Dict[str, Any], after: Dict[str, Any], changed: Any) -> Record:
    """12.3.4 (b): per-key streams. `before` and `after` map bid to placement; only the `changed` bid(s) (one bid,
    or the old and new bid of a rename) may differ, appear or disappear."""
    ch = {changed} if isinstance(changed, str) else set(changed)
    bad = [k for k in sorted(set(before) & set(after))
           if k not in ch and io.canonical_dumps(before[k]) != io.canonical_dumps(after[k])]
    missing = sorted((set(before) ^ set(after)) - ch)
    ok = not bad and not missing
    note = "" if ok else ("changed: " + ",".join(bad[:5])) + (" missing: " + ",".join(missing[:5]) if missing else "")
    return record("12.3.4b", PASS if ok else FAIL, len(bad), 0, note)


# ---------------------------------------------------------------- 12.6 parity
def first_diff_path(a: Any, b: Any, path: str = "$") -> Optional[str]:
    """JSON path of the first difference between two parsed values (sorted keys), or None when equal."""
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))
                                       and not isinstance(a, bool) and not isinstance(b, bool)):
        return path
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k}"
            d = first_diff_path(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        for i in range(min(len(a), len(b))):
            d = first_diff_path(a[i], b[i], f"{path}[{i}]")
            if d:
                return d
        return None if len(a) == len(b) else f"{path}[{min(len(a), len(b))}]"
    return None if a == b else path


def compare_json_files(path_a: str, path_b: str) -> Record:
    """12.6 parity: byte-for-byte comparison; on a difference report the first differing JSON path."""
    with open(path_a, "rb") as f:
        ba = f.read()
    with open(path_b, "rb") as f:
        bb = f.read()
    name = os.path.basename(path_a)
    if ba == bb:
        return record(f"12.6:{name}", PASS, len(ba), "identical bytes", "")
    off = next((i for i in range(min(len(ba), len(bb))) if ba[i] != bb[i]), min(len(ba), len(bb)))
    where = f"byte {off}"
    try:
        import json
        jp = first_diff_path(json.loads(ba.decode("utf-8")), json.loads(bb.decode("utf-8")))
        where = f"path {jp or '$ (values equal, formatting differs)'} at byte {off}"
    except ValueError:
        where += " (not parseable as JSON)"
    return record(f"12.6:{name}", FAIL, off, "identical bytes", "first difference: " + where)


# ---------------------------------------------------------------- geometry helpers
def _seg_dist(p: Pt, a: Pt, b: Pt) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _orient(a: Pt, b: Pt, c: Pt) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segs_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool:
    return (_orient(a, b, c) * _orient(a, b, d) < 0) and (_orient(c, d, a) * _orient(c, d, b) < 0)


def point_in_poly(p: Pt, poly: Sequence[Pt]) -> bool:
    """Even-odd point in polygon test."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi, xj, yj = poly[i][0], poly[i][1], poly[j][0], poly[j][1]
        if (yi > p[1]) != (yj > p[1]) and p[0] < (xj - xi) * (p[1] - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def poly_polyline_dist(poly: Sequence[Pt], line: Sequence[Pt]) -> float:
    """Minimum plan distance between a polygon (filled) and a polyline; 0 when they touch or overlap."""
    if len(line) == 1:
        line = [line[0], line[0]]
    px = [p[0] for p in poly]
    py = [p[1] for p in poly]
    best = math.inf
    n = len(poly)
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        if point_in_poly(a, poly):
            return 0.0
        for k in range(n):
            c, d = poly[k], poly[(k + 1) % n]
            if _segs_cross(a, b, c, d):
                return 0.0
            best = min(best, _seg_dist(c, a, b), _seg_dist(a, c, d), _seg_dist(b, c, d))
    if point_in_poly(line[-1], poly):
        return 0.0
    return best if best != math.inf else min(_seg_dist(p, line[0], line[-1]) for p in poly)


def _near(poly: Sequence[Pt], line: Sequence[Pt], r: float) -> bool:
    """Cheap prefilter: bbox of `poly` grown by `r` overlaps the polyline bbox."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    lx = [p[0] for p in line]
    ly = [p[1] for p in line]
    return not (max(xs) + r < min(lx) or min(xs) - r > max(lx) or max(ys) + r < min(ly) or min(ys) - r > max(ly))


def _rail_dist(poly: Sequence[Pt], line: Sequence[Pt], r: float) -> float:
    """Distance poly to the rail, exact where it can be below `r`, else a value above `r` (inf when far)."""
    if not _near(poly, line, r):
        return math.inf
    # exact test on the whole line is O(segments); restrict to segments whose bbox is near
    best = math.inf
    n = len(poly)
    x0 = min(p[0] for p in poly) - r
    x1 = max(p[0] for p in poly) + r
    y0 = min(p[1] for p in poly) - r
    y1 = max(p[1] for p in poly) + r
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        if max(a[0], b[0]) < x0 or min(a[0], b[0]) > x1 or max(a[1], b[1]) < y0 or min(a[1], b[1]) > y1:
            continue
        d = poly_polyline_dist(poly, [a, b])
        if d < best:
            best = d
            if best == 0.0:
                break
    return best


def poly_rail_dist(poly: Sequence[Pt], line: Sequence[Pt], r: float) -> float:
    """Distance polygon to the rail polyline, exact where it can be below `r` (inf when far); shared with `zoning`."""
    return _rail_dist(poly, line, r)


def _parts(city: Dict[str, Any]):
    for b in city["buildings"]:
        for i, p in enumerate(b["parts"]):
            yield b["bid"], i, p


def _many(items: Sequence[str], n: int = 4) -> str:
    return ", ".join(items[:n]) + (f" (+{len(items) - n} more)" if len(items) > n else "")


# ---------------------------------------------------------------- 12.4
def check_rail_footprints(zoned: Dict[str, Any], city: Dict[str, Any]) -> Record:
    """12.4.1: no building footprint within `rail.half_clear` of the rail polyline."""
    if "rail" not in zoned:
        return record("12.4.1", NA, None, "0 footprints near the rail", "zoned has no rail object")
    rail = zoned["rail"]
    r = rail["half_clear"]
    bad = sorted({bid for bid, _, p in _parts(city) if _rail_dist(p["poly"], rail["pts"], r) < r})
    return record("12.4.1", FAIL if bad else PASS, len(bad), f"0 footprints within {r} BU", _many(bad))


def check_rail_heights(zoned: Dict[str, Any], city: Dict[str, Any]) -> Record:
    """12.4.2: within `rail.side_d` of the rail, every building top is at most `rail.side_cap`."""
    if "rail" not in zoned:
        return record("12.4.2", NA, None, "rail-side tops capped", "zoned has no rail object")
    rail = zoned["rail"]
    d, cap = rail["side_d"], rail["side_cap"]
    bad = sorted({bid for bid, _, p in _parts(city)
                  if p["z0"] + p["h"] > cap + 1e-6 and _rail_dist(p["poly"], rail["pts"], d) <= d})
    return record("12.4.2", FAIL if bad else PASS, len(bad), f"tops <= {cap} BU within {d} BU", _many(bad))


def street_tiles(city: Dict[str, Any]) -> set:
    """Set of `(i, j)` street lot cells of a city.json."""
    return {(int(s["lot"][0]), int(s["lot"][1])) for s in city["streets"]}


def plan_to_lot(city: Dict[str, Any], x: float, y: float) -> Tuple[int, int]:
    """Lot cell of a plan point (BU), see the module docstring for the convention."""
    ox, oy = city["origin_lot"]
    return int(math.floor(x / city["lot_bu"] + ox)), int(math.floor(oy - y / city["lot_bu"]))


def check_piers(zoned: Dict[str, Any], city: Dict[str, Any]) -> Record:
    """12.4.3: every viaduct pier stands on a street tile (n/a when the rail has no `piers`)."""
    if "rail" not in zoned:
        return record("12.4.3", NA, None, "all piers on street tiles", "zoned has no rail object")
    piers = zoned["rail"].get("piers")
    if piers is None:
        return record("12.4.3", NA, None, "all piers on street tiles", "zoned rail has no piers list")
    tiles = street_tiles(city)
    bad = [f"({p[0]:.1f},{p[1]:.1f})" for p in piers if plan_to_lot(city, p[0], p[1]) not in tiles]
    return record("12.4.3", FAIL if bad else PASS, len(bad), "0 piers off street tiles", _many(bad))


def check_one_line(zoned: Dict[str, Any], hq_rail: Dict[str, Any]) -> Record:
    """12.4.4: the HQ scene's rail polyline and `deck_z` equal the `zoned.json` ones, byte for byte."""
    if "rail" not in zoned:
        return record("12.4.4", NA, None, "byte equal", "zoned has no rail object")
    keys = ("pts", "deck_z")
    a = io.canonical_dumps({k: zoned["rail"][k] for k in keys})
    b = io.canonical_dumps({k: hq_rail[k] for k in keys})
    return record("12.4.4", PASS if a == b else FAIL, None, "byte equal", "" if a == b else "rail polyline or deck_z differs")


def _segment_samples(path: Sequence[Sequence[float]], step: float) -> List[Sequence[float]]:
    out = [path[0]]
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        n = max(1, int(math.ceil(math.dist(a, b) / step)))
        out += [[a[k] + (b[k] - a[k]) * t / n for k in range(3)] for t in range(1, n + 1)]
    return out


def _inside_building(city: Dict[str, Any], p: Sequence[float], skip: set) -> Optional[str]:
    for bid, _, part in _parts(city):
        if bid in skip:
            continue
        if part["z0"] <= p[2] <= part["z0"] + part["h"] and point_in_poly(p, part["poly"]):
            return bid
    return None


def check_links(derive: Dict[str, Any], city: Dict[str, Any], step: float = 0.5) -> Record:
    """12.4.5a: no link path passes through a building that hosts no room of the run."""
    route = {r["bld"] for r in derive["rooms"].values()}
    bad = []
    for e in derive["edges"]:
        for p in _segment_samples(e["path"], step):
            b = _inside_building(city, p, route)
            if b:
                bad.append(f"{e['a']}-{e['b']} in {b}")
                break
    return record("12.4.5a", FAIL if bad else PASS, len(bad), "0 links through other buildings", _many(bad))


def _quad_points(q: Sequence[Sequence[float]]) -> List[List[float]]:
    c = [sum(p[k] for p in q) / len(q) for k in range(3)]
    return [list(p) for p in q] + [c]


def check_openings(derive: Dict[str, Any], city: Dict[str, Any]) -> Record:
    """12.4.5b: no room front or back opening lies inside another building (corners and centre sampled)."""
    bad = []
    for rid in sorted(derive["rooms"]):
        r = derive["rooms"][rid]
        for side in ("front", "back"):
            for p in _quad_points(r[side]):
                b = _inside_building(city, p, {r["bld"]})
                if b:
                    bad.append(f"{rid}.{side} in {b}")
                    break
    return record("12.4.5b", FAIL if bad else PASS, len(bad), "0 openings inside other buildings", _many(bad))


def check_foreground(derive: Dict[str, Any], dress: Dict[str, Any], margin: float,
                     depth_max: float = 1.0) -> Record:
    """12.4.5c (AD 2026-10-18 Q1): no dress item stands in front of a room opening as seen from the camera: its lateral
    coordinate within the opening's span grown by `margin` (0.15 BU), its height inside the opening's height span, and
    its depth from the face outward (along the street side of the face) in `(0, depth_max]` (1.0 BU: the facade zone; the
    far kerb, washes and ground glows stand further out by design). Reads the typed lists of
    `dress_<run>.json`; an `items` list is an input-shape failure."""
    if "items" in dress or not all(n in dress for n in DRESS_LISTS):
        return record("12.4.5c", FAIL, None, "typed dress lists", "dress input must be the typed lists of dress_<run>.json")
    boxes = []
    for rid in sorted(derive["rooms"]):
        r = derive["rooms"][rid]
        gz = r.get("ground_z", 0.0)
        q = r["front"]
        # the face is the axis on which all four front corners agree; the lateral axis is the other one
        face_ax = 0 if len({round(p[0], 6) for p in q}) == 1 else 1
        lat = 1 - face_ax
        out = -1.0 if r["back"][0][face_ax] > q[0][face_ax] else 1.0
        boxes.append((rid, face_ax, q[0][face_ax], out, min(p[lat] for p in q) - margin, max(p[lat] for p in q) + margin,
                      min(p[2] for p in q) + gz, max(p[2] for p in q) + gz))
    bad = []
    for name, pos in dress_positions(dress):
        for rid, fax, face, out, l0, l1, z0, z1 in boxes:
            lat = pos[1 - fax]
            if l0 <= lat <= l1 and z0 <= pos[2] <= z1 and 0.0 < (pos[fax] - face) * out <= depth_max:
                bad.append(f"{name} at ({pos[0]:.1f},{pos[1]:.1f}) before {rid}")
                break
    return record("12.4.5c", FAIL if bad else PASS, len(bad), "0 items before openings", _many(bad))


# ---------------------------------------------------------------- dress and beam inputs
DRESS_LISTS = ("signs", "lamps", "washes", "glows", "beams", "streak_lanes", "fog_fields")
BEAM_RIG: Dict[str, Any] = {   # look.preset beam rig (SB/sb_ocjobs.py LOOK): merged by the loader, not stored per beam
    "spot": {"cone_deg": 30.0, "blend": 1.0, "shadow": False, "media_linked": True},
    "shaft": {"material": "beam_shaft", "shadow": False}}


def dress_positions(dress: Dict[str, Any]) -> List[Tuple[str, Sequence[float]]]:
    """`(list name, pos)` of every typed-list item that has a `pos` (washes, lamps, signs, glows, beams)."""
    out = []
    for name in DRESS_LISTS:
        for it in dress.get(name, []):
            if "pos" in it:
                out.append((name, it["pos"]))
    return out


def beams_input(dress: Dict[str, Any], derive: Dict[str, Any], city: Dict[str, Any],
                rig: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The 12.5 beam check input from `dress_<run>.json`, `derive` and `city.json` (see the module docstring)."""
    r = rig or BEAM_RIG
    tops: Dict[str, float] = {}
    for bid, _, p in _parts(city):
        tops[bid] = max(tops.get(bid, 0.0), p["z0"] + p["h"])
    beams = [dict(b, top=tops.get(b["bid"], 0.0), spot=dict(r["spot"]), shaft=dict(r["shaft"])) for b in dress["beams"]]
    return {"route_bids": list(derive["route_keys"]), "beams": beams}


# ---------------------------------------------------------------- 12.5
def check_beam_config(beams: Dict[str, Any], cfg: Dict[str, Any]) -> Record:
    """12.5.1: spot cone and blend limits for media-linked spots, no shadowed beam, shaft material."""
    c = cfg["data"]["beams"]
    bad = []
    for b in beams["beams"]:
        s, h = b["spot"], b["shaft"]
        if s.get("media_linked") and s["cone_deg"] < c["min_cone_deg"]:
            bad.append(f"{b['bid']} cone {s['cone_deg']}")
        if s.get("media_linked") and s["blend"] < c["min_blend"]:
            bad.append(f"{b['bid']} blend {s['blend']}")
        if s.get("shadow") or h.get("shadow"):
            bad.append(f"{b['bid']} shadowed")
        if h.get("material") != c["shaft_material"]:
            bad.append(f"{b['bid']} shaft material {h.get('material')}")
    return record("12.5.1", FAIL if bad else PASS, len(bad), c, _many(bad))


def check_beam_layout(beams: Dict[str, Any], cfg: Dict[str, Any]) -> Record:
    """12.5.3: at most `max` beams, pairwise plan spacing at least `min_spacing`, none on a route column."""
    c = cfg["data"]["beams"]
    lst = beams["beams"]
    bad = []
    if len(lst) > c["max"]:
        bad.append(f"{len(lst)} beams")
    for i in range(len(lst)):
        if lst[i]["bid"] in set(beams.get("route_bids", [])):
            bad.append(f"{lst[i]['bid']} on route column")
        for j in range(i + 1, len(lst)):
            d = math.dist(lst[i]["pos"][:2], lst[j]["pos"][:2])
            if d < c["min_spacing"]:
                bad.append(f"{lst[i]['bid']}-{lst[j]['bid']} {d:.1f} BU")
    return record("12.5.3", FAIL if bad else PASS, len(lst), {"max": c["max"], "min_spacing": c["min_spacing"]}, _many(bad))


# ---------------------------------------------------------------- 12.6 occlusion
def occlusion_blocks(poses: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The occlusion blocks of a `poses_<run>.json`: overview, decision and every fixture decision."""
    recs = [poses["overview"], poses["decision"]] + [f["decision"] for f in poses.get("fixtures", [])]
    return [r["occlusion"] for r in recs]


def check_occlusion(derive: Dict[str, Any], city: Optional[Dict[str, Any]], cfg: Dict[str, Any]) -> Record:
    """12.6: every building opacity is at least `occ_ghost`; the stub stays: cut_height >= min(occ_stub, top)."""
    eps = cfg["data"]["occlusion"]["opacity_eps"]
    blocks = derive["occlusion"] if isinstance(derive["occlusion"], list) else [derive["occlusion"]]
    tops: Dict[str, float] = {}
    if city:
        for bid, _, p in _parts(city):
            tops[bid] = max(tops.get(bid, 0.0), p["z0"] + p["h"])
    bad = []
    for fi, blk in enumerate(blocks):
        ghost, stub = blk["params"]["occ_ghost"], blk["params"]["occ_stub"]
        for b in blk["buildings"]:
            if b["opacity"] < ghost - eps:
                bad.append(f"f{fi} {b['bid']} opacity {b['opacity']:.3f} < {ghost}")
            need = min(stub, tops[b["bid"]]) if b["bid"] in tops else stub
            if b["cut_height"] < need - eps:
                bad.append(f"f{fi} {b['bid']} cut {b['cut_height']:.2f} < {need:.2f}")
    return record("12.6:occlusion", FAIL if bad else PASS, len(bad), "opacity >= ghost, stub kept", _many(bad))


def run_data_suite(inputs: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[List[Record], float]:
    """Run every data check whose inputs are present; returns `(records, seconds)`.

    Keys of `inputs`: `producer` (spec) with `seeds`; `zoned`, `city`, `derive`, `beams`, `dress`, `hq_rail`
    (parsed objects); `parity` (list of `(path_a, path_b)`).
    """
    t0 = time.time()
    recs: List[Record] = []
    if inputs.get("producer"):
        recs += check_determinism(inputs["producer"], inputs["seeds"])
        recs += check_seed_sensitivity(inputs["producer"], inputs["seeds"])
    z, c, d = inputs.get("zoned"), inputs.get("city"), inputs.get("derive")
    if z and c:
        recs += [check_rail_footprints(z, c), check_rail_heights(z, c), check_piers(z, c)]
    if z and inputs.get("hq_rail"):
        recs.append(check_one_line(z, inputs["hq_rail"]))
    if d and c:
        recs += [check_links(d, c), check_openings(d, c)]
    if d and inputs.get("dress"):
        recs.append(check_foreground(d, inputs["dress"], cfg["data"]["dress"]["opening_margin"],
                                     cfg["data"]["dress"]["depth_max"]))
        if c and not inputs.get("beams"):
            inputs = dict(inputs, beams=beams_input(inputs["dress"], d, c))
    if inputs.get("beams"):
        recs += [check_beam_config(inputs["beams"], cfg), check_beam_layout(inputs["beams"], cfg)]
    if d and "occlusion" in d:
        recs.append(check_occlusion(d, c, cfg))
    for a, b in inputs.get("parity", []):
        recs.append(compare_json_files(a, b))
    return recs, time.time() - t0
