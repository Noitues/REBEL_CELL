"""Object Index pass by class for the golden plates (PIPELINE_SPEC 12.8), shared by city_render.py and tethys_build.py.

Same class numbers and the same export as hq_scene.py: 0 sky (the world, no object), 1 landmark compound, 2 city,
4 ground (terrain, seabed, water surface), 5 rooms, 6 movers, 7 light streaks (make_plate maps 7 to 4).
The city scripts merge everything into a few accumulators (SURF, NEON, ...), so the landmark faces (added by the
landmarks.py loop) and the mover faces (Tethys wildlife) are carved out of them into their own objects before the
meshes are built. Carving moves faces between objects only: the geometry, the materials and so the beauty are unchanged.
"""
ACC_VARS = dict(surf="SURF", smooth="SMOOTH", neon="NEON", glass="GLASS", ground="GROUND", terrain="TERR",
                seabed="SEABED", water="WATER", streak="STREAK", bill="BILL")
# the class of each accumulator's remaining (city) faces
ACC_CLASS = dict(surf=2, smooth=2, neon=2, glass=2, bill=2, ground=4, terrain=4, seabed=4, water=4, streak=7)
LANDMARK, CITY, GROUND, ROOMS, MOVERS, STREAK = 1, 2, 4, 5, 6, 7
_PER_FACE = ("col", "wc", "wl", "wm", "bid", "wet")


def face_counts(ns):
    """Face count of every accumulator that exists in the namespace ns (a mark taken between build phases)."""
    return {k: len(ns[v].F) for k, v in ACC_VARS.items() if v in ns}


def carve(acc, lo, hi=None, suffix="_id"):
    """Move faces [lo:hi) of the accumulator out into a new accumulator of the same kind; return it (None if empty).
    Every face owns its vertices (Acc.face extends V by the face's points), so the vertex ranges are contiguous."""
    n = len(acc.F)
    hi = n if hi is None else min(hi, n)
    if lo >= hi:
        return None
    vlo = acc.F[lo][0]
    vhi = acc.F[hi][0] if hi < n else len(acc.V)
    new = type(acc)(acc.name + suffix, smooth=acc.smooth)
    new.V, new.UV = acc.V[vlo:vhi], acc.UV[vlo:vhi]
    new.F = [tuple(i - vlo for i in f) for f in acc.F[lo:hi]]
    shift = vhi - vlo
    tail = [tuple(i - shift for i in f) for f in acc.F[hi:]]
    for a in _PER_FACE:
        full = getattr(acc, a)
        setattr(new, a, full[lo:hi])
        setattr(acc, a, full[:lo] + full[hi:])
    acc.F = acc.F[:lo] + tail
    acc.V = acc.V[:vlo] + acc.V[vhi:]
    acc.UV = acc.UV[:vlo] + acc.UV[vhi:]
    return new


def carve_all(ns, mark_lm, mark_mv=None):
    """Carve the landmark faces [mark_lm : mark_mv) and the mover faces [mark_mv : end) out of every accumulator.
    Returns {"landmark": {key: Acc}, "movers": {key: Acc}}; the later range is carved first so the marks stay valid."""
    out = {"landmark": {}, "movers": {}}
    for k, v in ACC_VARS.items():
        if v not in ns or k not in mark_lm:
            continue
        acc = ns[v]
        lo = mark_lm[k]
        hi = mark_mv[k] if mark_mv else None
        if mark_mv is not None:
            mv = carve(acc, hi, None, "_mv")
            if mv is not None:
                out["movers"][k] = mv
        lm = carve(acc, lo, None, "_lm")
        if lm is not None:
            out["landmark"][k] = lm
    return out


def set_classes(OBJ, split_objs):
    """pass_index on the built objects. OBJ = {key: object} (the accumulators), split_objs = {"landmark": {key: obj},
    "movers": {key: obj}}."""
    for k, o in OBJ.items():
        o.pass_index = ACC_CLASS.get(k, CITY)
    for k, o in split_objs.get("landmark", {}).items():
        o.pass_index = LANDMARK
    for k, o in split_objs.get("movers", {}).items():
        o.pass_index = MOVERS
