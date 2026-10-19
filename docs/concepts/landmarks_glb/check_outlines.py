"""Check each landmark module's FACE_OUTLINE: CCW (positive area), 16-72 points, ENTRY within 1.5 BU of the outline.

Run: python docs/concepts/landmarks_glb/check_outlines.py
Also checks that FACE_OUTLINES.json holds the same outline as each module. Prints one line per corp.
"""
import importlib.util
import json
import math
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE = os.path.normpath(os.path.join(HERE, "..", "route_map_graph"))
JSON_PATH = os.path.join(HERE, "FACE_OUTLINES.json")
MODULES = [
    ("halcyon", "hq_halcyon/scripts/halcyon_landmark.py"),
    ("solace", "hq_solace/scripts/solace_landmark.py"),
    ("orbital", "hq_orbital/scripts/orbital_landmark.py"),
    ("rebel_cell", "hq_rebel_cell/scripts/rebel_cell_landmark.py"),
    ("meridian", "hq_meridian_v3/scripts/meridian_landmark.py"),
    ("tethys", "hq_tethys/scripts/tethys_landmark.py"),
    ("aurelian", "hq_aurelian/scripts/aurelian_landmark.py"),
]
MIN_PTS, MAX_PTS = 16, 72
MAX_ENTRY_DIST = 1.5


def load(corp, rel):
    path = os.path.join(ROUTE, *rel.split("/"))
    spec = importlib.util.spec_from_file_location("check_" + corp, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def area2(poly):
    """Twice the signed area (shoelace); positive = counter-clockwise."""
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_dist(p, poly):
    n = len(poly)
    return min(seg_dist(p, poly[i], poly[(i + 1) % n]) for i in range(n))


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        table = json.load(f)
    all_ok = True
    for corp, rel in MODULES:
        mod = load(corp, rel)
        outline = [tuple(p) for p in mod.FACE_OUTLINE]
        entry = mod.ENTRY["entry"][:2]
        a2 = area2(outline)
        n = len(outline)
        d = poly_dist(entry, outline)
        json_ok = [tuple(p) for p in table.get(corp, [])] == outline
        ok = a2 > 0 and MIN_PTS <= n <= MAX_PTS and d <= MAX_ENTRY_DIST + 1e-9 and json_ok
        all_ok = all_ok and ok
        print("%-11s %s  area=%.2f  points=%d  entry_dist=%.2f  json=%s  %s" % (
            corp, "PASS" if ok else "FAIL", a2 / 2.0, n, d, "match" if json_ok else "MISMATCH",
            "" if ok else "(see notes)"))
    print("ALL PASS" if all_ok else "SOME FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
