"""C x E blend: turn the painted world into uniform triangulated facets (C's geometry) while the
painted toon material (E) shades them in stepped light bands and Freestyle keeps the ink.

facet_all(size) walks every world mesh (not the crystal/overlay/text collections):
  - drops bevel modifiers (facets replace bevels),
  - subdivides every edge longer than `size` (uniform-ish facet density, like C v2),
  - triangulates, jitters vertices a little (facets catch different light bands),
  - flat shading, and a per-face random attribute `facet` the paint shader uses for tone jitter.
Seeded randomness only.
"""
import random
import bmesh
import bpy
from mathutils import Vector
import tt_lib as T


def _skip(o):
    if o.type != "MESH":
        return True
    names = {c.name for c in o.users_collection}
    if names & {"NOLINE", "THIN"}:
        return True
    if o.name.startswith(("txt", "facet", "gem", "crystal", "shard", "tripanel", "path")):
        return True
    return False


def facet_obj(o, size, jitter, rng):
    for md in list(o.modifiers):
        if md.type == "BEVEL":
            o.modifiers.remove(md)
    me = o.data
    if me.users > 1:
        me = me.copy()
        o.data = me
    bm = bmesh.new()
    bm.from_mesh(me)
    # uniform facet density: split long edges a few rounds
    for _ in range(5):
        long_e = [e for e in bm.edges if e.calc_length() > size]
        if not long_e:
            break
        bmesh.ops.subdivide_edges(bm, edges=long_e, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="ALTERNATE")
    sc = max(o.scale) if max(o.scale) > 0 else 1.0
    j = jitter / sc
    for v in bm.verts:
        v.co += Vector((rng.uniform(-j, j), rng.uniform(-j, j), rng.uniform(-j, j) * 0.7))
    lay = bm.faces.layers.float.new("facet")
    for f in bm.faces:
        f.smooth = False
        f[lay] = rng.random()
    bm.to_mesh(me)
    bm.free()


def facet_all(size=0.55, jitter=0.045, seed=7):
    rng = random.Random(seed)
    objs = sorted([o for o in bpy.data.objects if not _skip(o)], key=lambda o: o.name)
    for o in objs:
        facet_obj(o, size, jitter, rng)
    print("faceted", len(objs), "objects")
