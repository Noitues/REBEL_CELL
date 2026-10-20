"""contract: readers for derive v2, poses v1 and dress v1 that reject what they do not know (review Q0.1, Q1.4, AD 19).

`validate_*` return a list of problems (empty = valid): schema subset check, canonical-JSON check, then the semantic
rules a schema cannot say (unknown version, link type, room kind, palette id, quad winding BL BR TR TL seen from the
street, rooms keyed like the run graph). Standard library only.
"""
import os
from typing import Any, Dict, List, Optional

from . import io
from .dress import PALETTE_IDS
from .derive.street import LINK_TYPES, ROOM_KINDS

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas")
VERSIONS = {"derive": 2, "poses": 1, "dress": 1}


def load_schema(name: str) -> Dict[str, Any]:
    """A schema file by name (`derive_v2`, `poses`, `dress`)."""
    return io.load(os.path.join(SCHEMA_DIR, name + ".schema.json"))


def _version(obj: Any, want: int) -> List[str]:
    v = obj.get("version") if isinstance(obj, dict) else None
    return [] if v == want and not isinstance(v, bool) else [f"unknown version {v!r} (this reader knows {want})"]


def _winding(room: Dict[str, Any], nrm: Optional[List[float]], rid: str, errs: List[str]) -> None:
    """BL, BR, TR, TL: bottom edge first, then up; seen from the street (camera looks along nrm) u runs to the right."""
    for side in ("front", "back"):
        q = room[side]
        if not (q[0][2] == q[1][2] < q[2][2] == q[3][2]):
            errs.append(f"rooms.{rid}.{side}: corner heights are not bottom, bottom, top, top")
        if nrm is not None:
            right = (nrm[1], -nrm[0])
            if (q[1][0] - q[0][0]) * right[0] + (q[1][1] - q[0][1]) * right[1] <= 0:
                errs.append(f"rooms.{rid}.{side}: the bottom edge does not run left to right seen from the street")


def validate_derive(obj: Any) -> List[str]:
    """Problems of a derive v2 object (empty = valid)."""
    errs = _version(obj, VERSIONS["derive"])
    if errs:
        return errs
    errs += io.check_canonical(obj) + io.validate(obj, load_schema("derive_v2"))
    if errs:
        return errs
    nrm = obj.get("nrm")
    for rid in sorted(obj["rooms"]):
        r = obj["rooms"][rid]
        errs += io.validate(r, load_schema("derive_v2")["properties"]["rooms"]["x-values"], f"$.rooms.{rid}")
        if r.get("kind") not in ROOM_KINDS:
            errs.append(f"rooms.{rid}: unknown kind {r.get('kind')!r}")
        if not errs and obj["kind"] == "street":
            _winding(r, nrm, rid, errs)
    for e in obj["edges"]:
        if e["type"] not in LINK_TYPES + ("hq",):
            errs.append(f"edge {e['a']}-{e['b']}: unknown link type {e['type']!r}")
        if obj["kind"] == "street" and e["type"] != "facade":
            errs.append(f"edge {e['a']}-{e['b']}: a street derive has facade links only")
    if (obj["kind"] == "street") != ("street" in obj and "nrm" in obj and "start_left" in obj):
        errs.append("street, nrm and start_left are present iff kind is street")
    return errs


def validate_city(obj: Any) -> List[str]:
    """Problems of a city.json v1 object: the schema (with NA-12's optional `coast` and `terrain` sections), then the
    coast's own rules: every shoreline lot is land (not a sea cell) and 4-neighbours a sea cell."""
    if not isinstance(obj, dict) or obj.get("version") != 1:
        return ["version: want 1"]
    errs = io.validate(obj, load_schema("city"))
    if errs or "coast" not in obj:
        return errs
    sea = {(int(c[0]), int(c[1])) for c in obj["coast"]["sea_cells"]}
    for c in obj["coast"]["shoreline"]:
        i, j = int(c[0]), int(c[1])
        if (i, j) in sea:
            errs.append(f"shoreline lot {i},{j} is a sea cell")
        elif not any((i + di, j + dj) in sea for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            errs.append(f"shoreline lot {i},{j} touches no sea cell")
    return errs


def validate_poses(obj: Any) -> List[str]:
    """Problems of a poses v1 object."""
    errs = _version(obj, VERSIONS["poses"])
    if errs:
        return errs
    errs = io.check_canonical(obj) + io.validate(obj, load_schema("poses"))
    if not errs and len(obj["fixtures"]) < 3:
        errs.append("fewer than 3 fixture walks")
    if not errs and obj["kind"] == "street" and len(obj.get("dive", {}).get("samples", [])) != 5:
        errs.append("a street poses file needs 5 dive samples")
    return errs


def validate_dress(obj: Any) -> List[str]:
    """Problems of a dress v1 object (palette ids are ids, never RGB)."""
    errs = _version(obj, VERSIONS["dress"])
    if errs:
        return errs
    errs = io.check_canonical(obj) + io.validate(obj, load_schema("dress"))
    if errs:
        return errs
    for name in ("signs", "lamps", "washes", "glows", "beams", "streak_lanes"):
        for it in obj[name]:
            for k in ("pal", "band_pal"):
                if k in it and it[k] not in PALETTE_IDS:
                    errs.append(f"{name}: unknown palette id {it[k]!r}")
    return errs
