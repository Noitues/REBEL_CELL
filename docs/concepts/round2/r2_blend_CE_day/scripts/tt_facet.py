"""HYBRID E+C: the faceted-crystal language for the digital layer (net, data, UI).

Physical world = hand-painted + inked (tt_lib.paint).  Digital layer = faceted crystal:
triangulated meshes, each triangle one of three tones of its colour (light / mid / dark),
shaded by a fixed facet light + fresnel rim, emission output (glows at night), no ink lines.
Seeded randomness only.
"""
import bmesh
import bpy
import colorsys
import math
import random
from mathutils import Vector
import tt_lib as T

_FM = {}


def _tones(col, spread=1.0):
    r, g, b = T.hex_rgb(col)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    light = colorsys.hsv_to_rgb((h - 0.02 * spread) % 1, s * (1 - 0.25 * spread), min(1, v * (1 + 0.35 * spread) + 0.08))
    mid = (r, g, b)
    dark = colorsys.hsv_to_rgb((h + 0.03 * spread) % 1, min(1, s * 1.1), v * (1 - 0.42 * spread))
    return light, mid, dark


def facet_mats(col, glow=1.0, light_dir=None, alpha=1.0):
    """Three facet materials (light, mid, dark tone) for one colour."""
    ld = tuple(light_dir) if light_dir is not None else tuple(T.MODE["fake"])
    key = (col, glow, ld, alpha)
    if key in _FM:
        return _FM[key]
    mats = []
    for i, tone in enumerate(_tones(col)):
        m = bpy.data.materials.new("facet_%s_%d" % (col, i))
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        L = nt.links
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
        L.new(geo.outputs["Normal"], dot.inputs[0])
        dot.inputs[1].default_value = Vector(ld).normalized()
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = -1.0
        mr.inputs[2].default_value = 1.0
        mr.inputs[3].default_value = 0.55
        mr.inputs[4].default_value = 1.3
        L.new(dot.outputs["Value"], mr.inputs[0])
        # fresnel rim: faces turned away brighten (crystal edge glint)
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs[0].default_value = 0.35
        rim = nt.nodes.new("ShaderNodeMath"); rim.operation = "MULTIPLY"
        L.new(lw.outputs["Fresnel"], rim.inputs[0]); rim.inputs[1].default_value = 0.45
        sc_ = nt.nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"
        sc_.inputs[0].default_value = T.rgb_lin(tone)[:3]
        L.new(mr.outputs[0], sc_.inputs["Scale"])
        add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = "ADD"
        L.new(sc_.outputs[0], add.inputs[0])
        cc = nt.nodes.new("ShaderNodeCombineXYZ")
        L.new(rim.outputs[0], cc.inputs[0]); L.new(rim.outputs[0], cc.inputs[1]); L.new(rim.outputs[0], cc.inputs[2])
        L.new(cc.outputs[0], add.inputs[1])
        em = nt.nodes.new("ShaderNodeEmission")
        L.new(add.outputs[0], em.inputs[0])
        em.inputs[1].default_value = glow
        sh = em.outputs[0]
        if alpha < 1.0:
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx = nt.nodes.new("ShaderNodeMixShader")
            mx.inputs[0].default_value = alpha
            L.new(tr.outputs[0], mx.inputs[1]); L.new(sh, mx.inputs[2])
            sh = mx.outputs[0]
            m.surface_render_method = "BLENDED"
            m.use_backface_culling = False
        L.new(sh, out.inputs[0])
        mats.append(m)
    _FM[key] = mats
    return mats


def _finish(bm, name, col, glow, seed, loc, rot, parent, alpha=1.0, lined=False, palette=None):
    rng = random.Random(seed)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    cols = palette or [col]
    for f in bm.faces:
        ci = rng.randrange(len(cols))
        f.material_index = ci * 3 + rng.choice((0, 1, 1, 2))
        f.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (T.thin_coll() if lined else T.noline_coll()).objects.link(o)
    for c in cols:
        for m in facet_mats(c, glow, alpha=alpha):
            me.materials.append(m)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if parent is not None:
        o.parent = parent
    return o


def facetize(o, col, glow=1.0, seed=0, jitter=0.0, palette=None, alpha=1.0):
    """Turn an existing mesh object into a faceted crystal object (drops bevels, no ink)."""
    for md in list(o.modifiers):
        o.modifiers.remove(md)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    rng = random.Random(seed + 3)
    if jitter:
        for v in bm.verts:
            v.co += Vector((rng.uniform(-jitter, jitter), rng.uniform(-jitter, jitter), rng.uniform(-jitter, jitter)))
    new = _finish(bm, o.name + "_f", col, glow, seed, tuple(o.location), (0, 0, 0), None, alpha, palette=palette)
    new.rotation_euler = o.rotation_euler.copy()
    new.scale = o.scale.copy()
    new.parent = o.parent
    bpy.data.objects.remove(o)
    return new


def cut_gem(r, h_top, h_bot, n=8, loc=(0, 0, 0), col="#3ff0ff", glow=1.0, rot=(0, 0, 0), parent=None, seed=0,
            table=0.55, name="gem", jitter=0.0):
    """Brilliant-ish cut: table on top (+Z), crown down to the girdle, pavilion to a point."""
    bm = bmesh.new()
    rng = random.Random(seed)
    top_c = bm.verts.new((0, 0, h_top))
    tab = [bm.verts.new((math.cos(i / n * math.tau + math.pi / n) * r * table,
                         math.sin(i / n * math.tau + math.pi / n) * r * table, h_top)) for i in range(n)]
    gir = [bm.verts.new((math.cos(i / n * math.tau) * r * (1 + rng.uniform(-jitter, jitter)),
                         math.sin(i / n * math.tau) * r * (1 + rng.uniform(-jitter, jitter)), 0)) for i in range(n)]
    bot = bm.verts.new((0, 0, -h_bot))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top_c, tab[i], tab[j]))
        bm.faces.new((tab[i], gir[i], gir[j]))
        bm.faces.new((tab[i], gir[j], tab[j]))
        bm.faces.new((gir[j], gir[i], bot))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(bm, name, col, glow, seed, loc, rot, parent)


def crystal(r, h_up, h_down, n=6, loc=(0, 0, 0), col="#3ff0ff", glow=1.0, rot=(0, 0, 0), parent=None, seed=0,
            name="crystal", mid=0.0):
    """Elongated bipyramid crystal (map pins, shards). `mid` adds a prism band between the points."""
    bm = bmesh.new()
    rng = random.Random(seed)
    top = bm.verts.new((0, 0, h_up + mid))
    ring_a = [bm.verts.new((math.cos(i / n * math.tau) * r, math.sin(i / n * math.tau) * r, mid + rng.uniform(-0.02, 0.02)))
              for i in range(n)]
    ring_b = [bm.verts.new((math.cos(i / n * math.tau) * r, math.sin(i / n * math.tau) * r, 0.0)) for i in range(n)] if mid else ring_a
    bot = bm.verts.new((0, 0, -h_down))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top, ring_a[i], ring_a[j]))
        if mid:
            bm.faces.new((ring_a[i], ring_b[i], ring_b[j], ring_a[j]))
        bm.faces.new((ring_b[j], ring_b[i], bot))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(bm, name, col, glow, seed, loc, rot, parent)


def shard(size, loc, col, glow=2.0, rng=None, parent=None):
    """Tiny tetrahedral data shard."""
    rng = rng or random.Random(1)
    bm = bmesh.new()
    vs = [bm.verts.new((rng.uniform(-1, 1) * size, rng.uniform(-1, 1) * size, rng.uniform(-1, 1) * size)) for _ in range(4)]
    for f in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
        try:
            bm.faces.new([vs[k] for k in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(bm, "shard", col, glow, rng.randint(0, 999), loc, (rng.uniform(0, 360), rng.uniform(0, 360), 0), parent)


def tri_panel(w, h, cols, rows, palette, loc=(0, 0, 0), rot=(0, 0, 0), glow=1.5, seed=0, parent=None, alpha=1.0,
              image=None, jitter=0.35, name="tripanel"):
    """Triangulated low-poly projected image. `image(u, v) -> palette index` paints the picture
    (u, v in 0..1); otherwise tones are random from the palette."""
    rng = random.Random(seed)
    bm = bmesh.new()
    grid = []
    for j in range(rows + 1):
        row = []
        for i in range(cols + 1):
            x = -w / 2 + w * i / cols
            y = -h / 2 + h * j / rows
            if 0 < i < cols and 0 < j < rows:
                x += rng.uniform(-jitter, jitter) * w / cols
                y += rng.uniform(-jitter, jitter) * h / rows
            row.append(bm.verts.new((x, y, 0)))
        grid.append(row)
    faces = []
    for j in range(rows):
        for i in range(cols):
            a, b, c, d = grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]
            if rng.random() < 0.5:
                faces += [bm.faces.new((a, b, c)), bm.faces.new((a, c, d))]
            else:
                faces += [bm.faces.new((a, b, d)), bm.faces.new((b, c, d))]
    me_mats = []
    for c in palette:
        me_mats += facet_mats(c, glow, alpha=alpha)
    for f in faces:
        cen = f.calc_center_median()
        u, v = (cen.x + w / 2) / w, (cen.y + h / 2) / h
        idx = image(u, v) if image else rng.randrange(len(palette))
        if idx is None:
            bm.faces.remove(f)
            continue
        f.material_index = idx * 3 + rng.choice((0, 1, 1, 2))
        f.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    T.noline_coll().objects.link(o)
    for m in me_mats:
        me.materials.append(m)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if parent is not None:
        o.parent = parent
    return o


def facet_ribbon(pts, width, z, col, glow=1.0, seed=0, thick=0.08, name="facet_path"):
    """Faceted path band: a raised triangulated strip with a ridge down the middle."""
    bm = bmesh.new()
    rng = random.Random(seed)
    L_, M_, R_ = [], [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = Vector(pts[max(0, i - 1)]); b = Vector(pts[min(n - 1, i + 1)])
        d = (b - a).normalized()
        nr = Vector((-d.y, d.x))
        L_.append(bm.verts.new((p[0] + nr.x * width / 2, p[1] + nr.y * width / 2, z)))
        M_.append(bm.verts.new((p[0], p[1], z + thick + rng.uniform(-0.02, 0.03))))
        R_.append(bm.verts.new((p[0] - nr.x * width / 2, p[1] - nr.y * width / 2, z)))
    for i in range(n - 1):
        bm.faces.new((L_[i], M_[i], M_[i + 1], L_[i + 1]))
        bm.faces.new((M_[i], R_[i], R_[i + 1], M_[i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    return _finish(bm, name, col, glow, seed, (0, 0, 0), (0, 0, 0), None)
