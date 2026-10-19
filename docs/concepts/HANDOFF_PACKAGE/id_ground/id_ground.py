"""ID pass ground split (B-015 / A-029): the grade-level parts of a glb go into their own mesh, `id_ground`.

Blender-side helper, imported by build_hq_compound.py, build_dispatch_canyon.py and landmark_build_v1.py (not run alone).
`install(Acc)` makes every Acc.face call tag its face "ground" when the statement that made it is one of SITES (the
vendored builders stay unchanged) or when it runs inside `with ground():` (our own scripts). `split_ground(acc)` moves the
tagged faces out of an accumulator into a second bmesh (the colour / jitter / part-id layers come along), `join_ground`
joins the per-role pieces into ONE object named `id_ground` with one material slot per role. No rng call moves: the rest of
the geometry is the old geometry, minus these faces.
"""
import sys

import bpy

# (function, line in the vendored file) of every statement that lays a part on the ground. Sub-1 BU parts only, no
# vertical body: a kerb or rail lying on the ground counts, a lamp post or a wall does not. File of each line:
SITES = {
    ("plaza", 138), ("plaza", 140),                          # heroes24.py: carpet disc (z .02), the two ring strips (.05)
    ("faceted_water", 137), ("faceted_water", 138),          # heroes30.py: Meridian's moat surface (-.06..+.18)
    ("moat_edges", 267), ("moat_edges", 268),                # heroes30.py: moat kerb (.05..65) and its lit rim (.62..77)
    ("rails", 28), ("rails", 30), ("rails", 31),             # heroes30.py: rail heads (.24..46), sleepers, ballast (.03)
    ("orbital_parts", 22), ("orbital_parts", 23),            # compound: heroes26 orbital_silo26 lines 387 / 388 as
    ("orbital_silo26", 387), ("orbital_silo26", 388),        #   exec'd by heroes42 / landmark: shaft floor (.6), rim ring
    ("tokyo_street", 120),                                   # street34.py: the two pavement slabs (0..0.2)
    ("shophouse", 107),                                      # street34.py: wet-street sign streaks (.05)
    ("build_district", 116), ("build_district", 123),        # landmark_district_v1.py: asphalt (0), block pavement (.01)
    ("build_district", 148), ("build_district", 152), ("build_district", 154),  # lane bed (.02), lane strokes (.04)
}
# primitives that only forward to Acc.face: the "statement" is the first caller that is not one of them
PRIMS = {"face", "facet_quad", "_acc_face", "box", "beam", "strip", "cyl", "disc", "ring_beams", "flat_quad", "tube"}
LAYER = "gnd"
_depth = [0]


class ground:
    """`with ground(): SOLID.face(...)`: every face made inside is ground (our own scripts' statements)."""

    def __enter__(self):
        _depth[0] += 1

    def __exit__(self, *exc):
        _depth[0] -= 1


def _site():
    f = sys._getframe(2)  # 0 _site, 1 the patched face, 2 its caller
    while f is not None:
        if f.f_code.co_name not in PRIMS:
            return (f.f_code.co_name, f.f_lineno)
        f = f.f_back
    return None


def install(acc_cls):
    """Patch Acc.face (once). Faces keep their rng draw order; only an int face layer `gnd` is added to the bmesh."""
    if getattr(acc_cls, "_id_ground", False):
        return
    orig = acc_cls.face

    def face(self, pts, col, bid, fj=None):
        tag = _depth[0] or _site() in SITES
        if tag:  # add the layer BEFORE the face: adding it later invalidates the face handle
            lay = self.bm.faces.layers.int.get(LAYER) or self.bm.faces.layers.int.new(LAYER)
        f = orig(self, pts, col, bid, fj)
        if tag:
            f[lay] = 1
        return f

    acc_cls.face = face
    acc_cls._id_ground = True


def split_ground(acc):
    """Remove the ground faces from acc.bm; return a new bmesh holding exactly them (None when there are none)."""
    import bmesh
    bm = acc.bm
    lay = bm.faces.layers.int.get(LAYER)
    if lay is None:
        return None
    dead = [f for f in bm.faces if f[lay]]
    if not dead:
        bm.faces.layers.int.remove(lay)
        return None
    g = bm.copy()
    glay = g.faces.layers.int.get(LAYER)
    bmesh.ops.delete(g, geom=[f for f in g.faces if not f[glay]], context="FACES")
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    g.faces.layers.int.remove(glay)
    bm.faces.layers.int.remove(lay)
    return g


def holder(acc_cls, name, bm):
    """An Acc around an existing bmesh (so Acc.obj / objectify / acc_object take it as they take any accumulator)."""
    a = acc_cls(name)
    a.bm.free()
    a.bm = bm
    return a


def join_ground(objs, name="id_ground"):
    """Join the per-role ground objects (one material each) into one object called `name`; the survivor is objs[0]."""
    objs = [o for o in objs if o is not None]
    if not objs:
        return None
    for o in list(bpy.context.view_layer.objects):
        if o is not None:  # the view layer can hold stale (removed) entries
            o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    objs[0].name = name
    objs[0].data.name = name
    return objs[0]
