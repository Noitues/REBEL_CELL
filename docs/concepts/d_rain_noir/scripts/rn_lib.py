"""RAIN NOIR shared Blender helpers (Blender 5.2, EEVEE, Grease Pencil v3).

Imported by every still script. Conventions:
- Front stills: camera looks down +Y, screen X = world X, screen up = world Z.
  `P(x, y, depth)` maps 1920x1080 pixel coords to world at plane Y=depth.
- All randomness is seeded (random.Random(seed)).
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(SLUG_DIR, "..", "..", ".."))
FONT_DIR = os.path.join(REPO, "assets", "fonts")
STILLS = os.path.join(SLUG_DIR, "stills")

# ---------------------------------------------------------------- palette
PAL = {
    "night": "#05070B", "slate": "#1A2230", "steel": "#2E3A4C", "haze": "#6B7A8F",
    "rain": "#C9D6E6", "pink": "#FF3DA8", "cyan": "#5CE1FF", "acid": "#D4FF00",
    "harm": "#FF4433", "gain": "#7BE07B", "amber": "#FFB000", "violet": "#8C7BFF",
    "paper": "#F2EEE4", "paper_alt": "#E9E4D6", "note_yellow": "#F2DC7A",
    "sticker_pink": "#F5AFCB", "ink": "#111111", "text_hi": "#F2F6FF",
    "text_mid": "#AFC0D6", "text_lo": "#7A889C", "siren_blue": "#3D6BFF",
    "orange": "#FF7A1A", "afflict": "#C85AFF",
}


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h, a=1.0):
    """Hex (or palette key) -> linear RGBA tuple."""
    h = PAL.get(h, h).lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (s2l(r), s2l(g), s2l(b), a)


# ---------------------------------------------------------------- scene
def reset(res=(1920, 1080), samples=24, pct=None):
    """Empty EEVEE scene. RN_PCT env var overrides resolution percentage for quick previews."""
    pct = pct or int(os.environ.get("RN_PCT", "100"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_raytracing = True
    ee.use_shadows = True
    ee.volumetric_tile_size = "4"
    ee.volumetric_samples = 64
    ee.volumetric_end = 400
    ee.use_volumetric_shadows = True
    ee.volumetric_light_clamp = 0.0
    for vt in ("AgX", "Filmic", "Standard"):
        try:
            sc.view_settings.view_transform = vt
            break
        except TypeError:
            pass
    for lk in ("AgX - Punchy", "AgX - Medium High Contrast", "None"):
        try:
            sc.view_settings.look = lk
            break
        except TypeError:
            pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    return sc


def world(color="#020305", strength=1.0, vol_density=0.0, vol_color="#8a98ad", aniso=0.35):
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    nt = w.node_tree if w.node_tree else None
    if nt is None:
        w.use_nodes = True
        nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = col(color)
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if vol_density > 0:
        v = nt.nodes.new("ShaderNodeVolumePrincipled")
        v.inputs["Color"].default_value = col(vol_color)
        v.inputs["Density"].default_value = vol_density
        v.inputs["Anisotropy"].default_value = aniso
        nt.links.new(v.outputs[0], out.inputs["Volume"])
    return w


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


# ---------------------------------------------------------------- materials
_mcache = {}


def _new_mat(name):
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    return m


def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def mat_pbr(name, base="#202a38", rough=0.4, metal=0.0, emit=None, emit_str=0.0, alpha=1.0, spec=0.5, coat=0.0):
    key = ("pbr", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    b = _bsdf(m)
    b.inputs["Base Color"].default_value = col(base)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.03
    if emit:
        b.inputs["Emission Color"].default_value = col(emit)
        b.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    _mcache[key] = m
    return m


def mat_emit(name, color, strength=4.0, alpha=1.0):
    key = ("emit", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = col(color)
    em.inputs["Strength"].default_value = strength
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        m.surface_render_method = "BLENDED"
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    _mcache[key] = m
    return m


def mat_glass_dome(name, tint="#9fc4ff", edge=0.55, base_alpha=0.04):
    """Transparent + glossy mixed by fresnel: reads as a glass dome without refraction cost."""
    key = ("glass", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy") if "ShaderNodeBsdfGlossy" in dir(bpy.types) else nt.nodes.new("ShaderNodeBsdfAnisotropic")
    gl.inputs["Color"].default_value = col(tint)
    gl.inputs["Roughness"].default_value = 0.04
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = base_alpha
    mr.inputs["To Max"].default_value = edge
    nt.links.new(lw.outputs["Fresnel"], mr.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    _mcache[key] = m
    return m


def mat_windows(name, wall="#10151e", lit=("#c9d6e6", "#ffcf8a"), density=0.35, strength=1.2, scale=1.0, seed=0.0, sat_sign=None):
    """Building facade: wet wall + per-window random lights. Windows are cells on (x+y, z) in object space,
    so any axis-aligned box face gets a floor grid. Cell size = (0.8, 0.65) / scale."""
    key = ("win", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    nt = m.node_tree
    b = _bsdf(m)
    b.inputs["Base Color"].default_value = col(wall)
    b.inputs["Roughness"].default_value = 0.3
    b.inputs["Metallic"].default_value = 0.1
    L = nt.links
    def math_(op, a=None, b_=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, b_)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    cw, ch = 0.8 / scale, 0.65 / scale
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    hcoord = math_("DIVIDE", math_("ADD", sep.outputs["X"], sep.outputs["Y"]), cw)
    vcoord = math_("DIVIDE", sep.outputs["Z"], ch)
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    L.new(math_("FLOOR", hcoord), comb.inputs[0])
    L.new(math_("FLOOR", vcoord), comb.inputs[1])
    comb.inputs[2].default_value = seed
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    L.new(comb.outputs[0], wn.inputs["Vector"])
    on = math_("LESS_THAN", wn.outputs["Value"], density)
    fh = math_("FRACT", hcoord); fv = math_("FRACT", vcoord)
    inside = math_("MULTIPLY", math_("MULTIPLY", math_("GREATER_THAN", fh, 0.18), math_("LESS_THAN", fh, 0.82)),
                   math_("MULTIPLY", math_("GREATER_THAN", fv, 0.24), math_("LESS_THAN", fv, 0.76)))
    lit_mask = math_("MULTIPLY", on, inside)
    sepc = nt.nodes.new("ShaderNodeSeparateColor")
    L.new(wn.outputs["Color"], sepc.inputs[0])
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    mixc.inputs[6].default_value = col(lit[0])
    mixc.inputs[7].default_value = col(lit[1])
    L.new(math_("GREATER_THAN", sepc.outputs[0], 0.6), mixc.inputs[0])
    L.new(mixc.outputs[2], b.inputs["Emission Color"])
    # brightness varies per window (0.4..1.0)
    br = math_("MULTIPLY_ADD", sepc.outputs[1], 0.6)
    nt.nodes[-1].inputs[2].default_value = 0.4
    L.new(math_("MULTIPLY", math_("MULTIPLY", lit_mask, br), strength), b.inputs["Emission Strength"])
    _mcache[key] = m
    return m


def mat_holo(name, color, strength=5.0, seed=0.0, bands=60.0, alpha=0.85):
    """Hologram billboard: scanline bands x blocky noise 'glyph' pattern, transparent, emissive."""
    key = ("holo", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # blocky glyph grid: voronoi/noise on snapped UVs
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    wave.inputs["Scale"].default_value = bands
    wave.inputs["Distortion"].default_value = 0.0
    nt.links.new(tc.outputs["UV"], wave.inputs["Vector"])
    snap = nt.nodes.new("ShaderNodeVectorMath")
    snap.operation = "SNAP"
    snap.inputs[1].default_value = (0.018, 0.07, 1)
    nt.links.new(tc.outputs["UV"], snap.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["W"].default_value = seed
    nt.links.new(snap.outputs[0], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.08, 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs["Value"], ramp.inputs["Fac"])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    nt.links.new(ramp.outputs["Color"], m1.inputs[0])
    wr = nt.nodes.new("ShaderNodeMath"); wr.operation = "MULTIPLY_ADD"
    wr.inputs[1].default_value = 0.5; wr.inputs[2].default_value = 0.5
    nt.links.new(wave.outputs["Fac"], wr.inputs[0])
    nt.links.new(wr.outputs[0], m1.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = col(color)
    sm = nt.nodes.new("ShaderNodeMath"); sm.operation = "MULTIPLY"; sm.inputs[1].default_value = strength
    nt.links.new(m1.outputs[0], sm.inputs[0])
    nt.links.new(sm.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    am = nt.nodes.new("ShaderNodeMath"); am.operation = "MULTIPLY"; am.inputs[1].default_value = alpha
    nt.links.new(m1.outputs[0], am.inputs[0])
    nt.links.new(am.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    _mcache[key] = m
    return m


def mat_volume(name, density=0.2, color="#9aa8bd", emit=None, emit_str=0.0, noise_scale=0.0, noise_contrast=2.5, seed=0.0):
    key = ("vol", name)
    if key in _mcache:
        return _mcache[key]
    m = _new_mat(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = col(color)
    v.inputs["Anisotropy"].default_value = 0.4
    if emit:
        v.inputs["Emission Color"].default_value = col(emit)
        v.inputs["Emission Strength"].default_value = emit_str
    if noise_scale > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "4D"
        nz.inputs["W"].default_value = seed
        nz.inputs["Scale"].default_value = noise_scale
        nz.inputs["Detail"].default_value = 3.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        # patchy: (noise - 0.5) * contrast, clamp, * density; plus spherical falloff from object centre
        a = nt.nodes.new("ShaderNodeMath"); a.operation = "SUBTRACT"; a.inputs[1].default_value = 0.48
        nt.links.new(nz.outputs["Fac"], a.inputs[0])
        b = nt.nodes.new("ShaderNodeMath"); b.operation = "MULTIPLY"; b.inputs[1].default_value = noise_contrast; b.use_clamp = True
        nt.links.new(a.outputs[0], b.inputs[0])
        ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
        nt.links.new(tc.outputs["Object"], ln.inputs[0])
        fo = nt.nodes.new("ShaderNodeMapRange")
        fo.inputs["From Min"].default_value = 0.35; fo.inputs["From Max"].default_value = 1.0
        fo.inputs["To Min"].default_value = 1.0; fo.inputs["To Max"].default_value = 0.0
        nt.links.new(ln.outputs["Value"], fo.inputs["Value"])
        c = nt.nodes.new("ShaderNodeMath"); c.operation = "MULTIPLY"
        nt.links.new(b.outputs[0], c.inputs[0]); nt.links.new(fo.outputs[0], c.inputs[1])
        d = nt.nodes.new("ShaderNodeMath"); d.operation = "MULTIPLY"; d.inputs[1].default_value = density
        nt.links.new(c.outputs[0], d.inputs[0])
        nt.links.new(d.outputs[0], v.inputs["Density"])
    else:
        v.inputs["Density"].default_value = density
    nt.links.new(v.outputs[0], out.inputs["Volume"])
    _mcache[key] = m
    return m


# ---------------------------------------------------------------- meshes
def _mesh_obj(name, bm, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if mat:
        me.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    link(ob)
    return ob


def box(name, loc, size, mat=None, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _mesh_obj(name, bm, mat, loc, rot, parent)


def rrect(name, w, h, r, loc, mat=None, depth=0.0, rot=(math.radians(90), 0, 0), parent=None, seg=6):
    """Rounded rectangle in local XY (rotated to face -Y by default)."""
    bm = bmesh.new()
    pts = []
    r = min(r, w / 2, h / 2)
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0))
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    if depth > 0:
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, vec=(0, 0, -depth), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _mesh_obj(name, bm, mat, loc, rot, parent)
    # UVs for planar faces
    me = ob.data
    uv = me.uv_layers.new()
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (co.x / w + 0.5, co.y / h + 0.5)
    return ob


def ring_sector(name, r0, r1, a0, a1, depth, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, seg=None, bevel=0.0):
    """Annulus sector in local XY, extruded along -Z (toward the viewer once rotated)."""
    bm = bmesh.new()
    span = a1 - a0
    seg = seg or max(3, int(abs(span) / math.radians(3)))
    outer, inner = [], []
    for i in range(seg + 1):
        a = a0 + span * i / seg
        outer.append(bm.verts.new((r1 * math.cos(a), r1 * math.sin(a), 0)))
        inner.append(bm.verts.new((r0 * math.cos(a), r0 * math.sin(a), 0)))
    closed = abs(span - 2 * math.pi) < 1e-4
    n = seg if closed else seg
    faces = []
    for i in range(n):
        j = i + 1
        if closed and j == seg:
            j = 0
        faces.append(bm.faces.new((inner[i], outer[i], outer[j], inner[j])))
    if closed:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    if depth > 0:
        ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        bmesh.ops.translate(bm, vec=(0, 0, depth), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _mesh_obj(name, bm, mat, loc, rot, parent)
    if bevel > 0:
        md = ob.modifiers.new("bv", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.limit_method = "ANGLE"
    return ob


def disc(name, r, depth, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, seg=96):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=depth)
    return _mesh_obj(name, bm, mat, loc, rot, parent)


def dome(name, r, height, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """Front half of a flattened sphere: a glass cap bulging along local +Z."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=1.0)
    kill = [v for v in bm.verts if v.co.z < -1e-4]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bmesh.ops.scale(bm, vec=(r, r, height), verts=bm.verts)
    return _mesh_obj(name, bm, mat, loc, rot, parent, smooth=True)


def cyl(name, r, depth, mat, loc, rot=(0, 0, 0), seg=24, parent=None):
    return disc(name, r, depth, mat, loc, rot, parent, seg)


def torus(name, R, r, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, seg=128, mseg=12):
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(mseg):
            b = 2 * math.pi * j / mseg
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            ring.append(bm.verts.new((x, y, z)))
        verts.append(ring)
    for i in range(seg):
        for j in range(mseg):
            a, b = verts[i][j], verts[(i + 1) % seg][j]
            c, d = verts[(i + 1) % seg][(j + 1) % mseg], verts[i][(j + 1) % mseg]
            bm.faces.new((a, b, c, d))
    return _mesh_obj(name, bm, mat, loc, rot, parent, smooth=True)


def tube(name, pts, radius, mat, cyclic=False, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Polyline -> bevelled curve (neon tube)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    link(ob)
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.rotation_euler = rot
    if parent:
        e.parent = parent
    link(e)
    return e


# ---------------------------------------------------------------- text
_fonts = {}


def font(fname):
    if fname not in _fonts:
        p = os.path.join(FONT_DIR, fname)
        if not os.path.exists(p):
            p = os.path.join("C:/Windows/Fonts", fname)
        _fonts[fname] = bpy.data.fonts.load(p)
    return _fonts[fname]


MONO, ANTON, MARKER = "ShareTechMono-Regular.ttf", "Anton-Regular.ttf", "PermanentMarker-Regular.ttf"
PLEX = "IBMPlexSansCondensed-Medium.ttf"


def text(body, loc, size, mat, fnt=MONO, align="LEFT", valign="CENTER", rot=(math.radians(90), 0, 0), parent=None, name="txt", spacing=1.0, extrude=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = font(fnt)
    cu.size = size
    cu.align_x = align
    cu.align_y = valign
    cu.space_character = spacing
    cu.extrude = extrude
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    link(ob)
    return ob


# ---------------------------------------------------------------- lights
def point(loc, color, power, radius=0.2, name="pt", shadow=True):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color = col(color)[:3]
    ld.energy = power
    ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    return link(ob)


def area(loc, rot, color, power, size=2.0, size_y=None, name="ar", shape="RECTANGLE"):
    ld = bpy.data.lights.new(name, "AREA")
    ld.color = col(color)[:3]
    ld.energy = power
    ld.shape = shape
    ld.size = size
    ld.size_y = size_y or size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob)


def spot(loc, target, color, power, angle=20, blend=0.3, radius=0.1, name="spot", vol=1.0):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.color = col(color)[:3]
    ld.energy = power
    ld.spot_size = math.radians(angle)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    ld.volume_factor = vol
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return link(ob)


# ---------------------------------------------------------------- camera
CAM_D = 26.6667  # distance at which a 50mm/36mm-sensor camera sees 19.2 units wide (1 unit = 100 px)


def front_camera(lens=50.0, fstop=None, focus=CAM_D, shift=(0, 0)):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_width = 36
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_end = 1000
    cd.shift_x, cd.shift_y = shift
    if fstop:
        cd.dof.use_dof = True
        cd.dof.focus_distance = focus
        cd.dof.aperture_fstop = fstop
    ob = bpy.data.objects.new("cam", cd)
    ob.location = (0, -CAM_D * lens / 50.0, 0)
    ob.rotation_euler = (math.radians(90), 0, 0)
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def P(x, y, depth=0.0, lens=50.0):
    """Pixel (1920x1080) -> world point on plane Y=depth for front_camera(lens)."""
    D = CAM_D * lens / 50.0
    k = (D + depth) / D
    return Vector(((x - 960) / 100.0 * k, depth, (540 - y) / 100.0 * k))


def S(px, depth=0.0, lens=50.0):
    D = CAM_D * lens / 50.0
    return px / 100.0 * (D + depth) / D


# ---------------------------------------------------------------- grease pencil
class GP:
    """One Grease Pencil v3 object with named layers and a material palette."""

    def __init__(self, name, loc=(0, 0, 0), rot=(0, 0, 0)):
        self.data = bpy.data.grease_pencils.new(name)
        self.ob = bpy.data.objects.new(name, self.data)
        self.ob.location = loc
        self.ob.rotation_euler = rot
        link(self.ob)
        self.mats = {}
        self.layers = {}

    def mat(self, key, color, alpha=1.0, fill=None):
        if key in self.mats:
            return self.mats[key]
        m = bpy.data.materials.new(self.data.name + "_" + key)
        bpy.data.materials.create_gpencil_data(m)
        c = col(color, alpha)
        m.grease_pencil.color = c
        if fill:
            m.grease_pencil.show_fill = True
            m.grease_pencil.fill_color = col(fill, alpha)
        self.data.materials.append(m)
        self.mats[key] = len(self.data.materials) - 1
        return self.mats[key]

    def layer(self, name, use_lights=False):
        if name not in self.layers:
            l = self.data.layers.new(name)
            l.use_lights = use_lights
            fr = l.frames.new(bpy.context.scene.frame_current)
            self.layers[name] = fr.drawing
        return self.layers[name]

    def stroke(self, layer, pts, radius, mat, opacity=1.0, cyclic=False, fill=False):
        """pts: list of 3D points (object space). radius/opacity: scalar or per-point list."""
        if len(pts) < 2:
            return
        dr = self.layer(layer)
        dr.add_strokes([len(pts)])
        s = dr.strokes[len(dr.strokes) - 1]
        s.material_index = mat
        s.cyclic = cyclic
        for i, p in enumerate(pts):
            pt = s.points[i]
            pt.position = tuple(p)
            pt.radius = radius[i] if isinstance(radius, (list, tuple)) else radius
            pt.opacity = opacity[i] if isinstance(opacity, (list, tuple)) else opacity
        return s


def catmull(pts, n=6):
    """Catmull-Rom smoothing of a 2D/3D polyline."""
    if len(pts) < 3:
        return pts
    P_ = [Vector(pts[0])] + [Vector(p) for p in pts] + [Vector(pts[-1])]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Vector(pts[-1]))
    return out


# ---------------------------------------------------------------- compositor
def compositor(bloom=0.9, bloom_thresh=0.9, streak=0.35, streak_thresh=2.5, dispersion=0.004, distortion=-0.015, bloom_size=0.9):
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    g1 = ng.nodes.new("CompositorNodeGlare")
    g1.inputs["Type"].default_value = "Bloom"
    g1.inputs["Threshold"].default_value = bloom_thresh
    g1.inputs["Strength"].default_value = bloom
    g1.inputs["Size"].default_value = bloom_size
    g1.inputs["Quality"].default_value = "High"
    ng.links.new(rl.outputs["Image"], g1.inputs["Image"])
    last = g1.outputs["Image"]
    if streak > 0:
        g2 = ng.nodes.new("CompositorNodeGlare")
        g2.inputs["Type"].default_value = "Streaks"
        g2.inputs["Streaks"].default_value = 2
        g2.inputs["Streaks Angle"].default_value = 0.0
        g2.inputs["Threshold"].default_value = streak_thresh
        g2.inputs["Strength"].default_value = streak
        g2.inputs["Fade"].default_value = 0.93
        g2.inputs["Iterations"].default_value = 5
        g2.inputs["Tint"].default_value = (0.55, 0.75, 1.0, 1.0)
        g2.inputs["Saturation"].default_value = 0.6
        ng.links.new(last, g2.inputs["Image"])
        last = g2.outputs["Image"]
    ld = ng.nodes.new("CompositorNodeLensdist")
    ld.inputs["Distortion"].default_value = distortion
    ld.inputs["Dispersion"].default_value = dispersion
    ld.inputs["Fit"].default_value = True
    ng.links.new(last, ld.inputs["Image"])
    out = ng.nodes.new("NodeGroupOutput")
    ng.links.new(ld.outputs["Image"], out.inputs[0])
    return ng


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def out_arg(default):
    if "--" in sys.argv:
        a = sys.argv[sys.argv.index("--") + 1:]
        if a:
            return a[0]
    return default


def sun(rot, color, strength, angle=2.0, name="sun"):
    ld = bpy.data.lights.new(name, "SUN")
    ld.color = col(color)[:3]
    ld.energy = strength
    ld.angle = math.radians(angle)
    ob = bpy.data.objects.new(name, ld)
    ob.rotation_euler = rot
    return link(ob)
