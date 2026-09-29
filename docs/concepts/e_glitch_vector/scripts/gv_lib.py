"""GLITCH VECTOR CRT - shared Blender helpers (Blender 5.2, Grease Pencil v3, EEVEE).

Import from a Blender script with:
    sys.path.insert(0, os.path.dirname(__file__)); import gv_lib as gv
All randomness is seeded by the caller.
"""
import bpy, math

# ---------------------------------------------------------------- palette (linear-ish, Standard view)
def hexc(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    # sRGB -> linear so Standard view shows the hex we mean
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), a)

P = {
    "void": "#020408",
    "phosphor": "#39FF9C",   # hologram green: city structure
    "phos_dim": "#0F6B48",
    "cyan": "#5CE1FF",       # NET_CYAN: glass edges, net, defend
    "magenta": "#FF2BD6",    # hologram magenta: ads, afflict
    "pink": "#FF3DA8",       # CELL_PINK: the Cell, attack, marker
    "acid": "#D4FF00",       # CELL_ACID: focus / turf
    "harm": "#FF4433",
    "amber": "#FFB000",
    "violet": "#B04DFF",
    "white": "#E8FFF6",
    "gain": "#7BE07B",
    "orange": "#FF8C1A",     # Meridian
}


def col(name, a=1.0, mul=1.0):
    c = hexc(P[name] if name in P else name, a)
    return (c[0] * mul, c[1] * mul, c[2] * mul, a)


# ---------------------------------------------------------------- scene
def reset(res=(1920, 1080), samples=8, transparent=False, black=False):
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = samples
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    # black=True: pure black so the layer can be ADDED over a background in post
    # (additive GP layers write no alpha on a transparent film, so film_transparent loses them)
    bg.inputs[0].default_value = (0, 0, 0, 1) if black else col("void")
    bg.inputs[1].default_value = 1.0
    return sc


def camera(loc, rot_deg, ortho_scale=None, lens=50, shift=(0, 0)):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new("cam")
    if ortho_scale:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho_scale
    else:
        cam.lens = lens
    cam.shift_x, cam.shift_y = shift
    cam.clip_end = 500
    o = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    sc.camera = o
    return o


def bloom(strength=1.0, threshold=0.25, size=0.6, streaks=False):
    """Compositor (5.x node-group API): Render Layers -> Glare(Bloom) -> Group Output."""
    sc = bpy.context.scene
    tree = bpy.data.node_groups.new("gv_comp", "CompositorNodeTree")
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = tree.nodes.new("CompositorNodeRLayers")
    out = tree.nodes.new("NodeGroupOutput")
    g = tree.nodes.new("CompositorNodeGlare")
    g.inputs["Type"].default_value = "Bloom"
    g.inputs["Threshold"].default_value = threshold
    g.inputs["Strength"].default_value = strength
    g.inputs["Size"].default_value = size
    tree.links.new(rl.outputs["Image"], g.inputs["Image"])
    last = g
    if streaks:
        g2 = tree.nodes.new("CompositorNodeGlare")
        g2.inputs["Type"].default_value = "Streaks"
        g2.inputs["Threshold"].default_value = threshold * 3
        g2.inputs["Strength"].default_value = 0.25
        g2.inputs["Streaks"].default_value = 2
        tree.links.new(g.outputs["Image"], g2.inputs["Image"])
        last = g2
    # keep alpha for transparent renders
    if sc.render.film_transparent:
        sa = tree.nodes.new("CompositorNodeSetAlpha")
        tree.links.new(last.outputs["Image"], sa.inputs["Image"])
        tree.links.new(rl.outputs["Alpha"], sa.inputs["Alpha"])
        last = sa
    tree.links.new(last.outputs["Image"], out.inputs[0])
    sc.compositing_node_group = tree
    sc.render.use_compositing = True


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- grease pencil batcher
class GP:
    """Collect strokes, then build one GP object with one layer per call to flush().

    Colour comes from per-point vertex colour over a white LINE material, so one material
    serves every stroke. Layers can be additive (phosphor)."""

    def __init__(self, name, blend="ADD", depth_3d=True):
        self.data = bpy.data.grease_pencils.new(name)
        self.obj = bpy.data.objects.new(name, self.data)
        bpy.context.scene.collection.objects.link(self.obj)
        if depth_3d:
            try:
                self.data.stroke_depth_order = "3D"
            except Exception:
                pass
        m = bpy.data.materials.new(name + "_line")
        bpy.data.materials.create_gpencil_data(m)
        m.grease_pencil.color = (1, 1, 1, 1)
        m.grease_pencil.show_fill = False
        self.data.materials.append(m)
        mf = bpy.data.materials.new(name + "_fill")
        bpy.data.materials.create_gpencil_data(mf)
        mf.grease_pencil.show_stroke = False
        mf.grease_pencil.show_fill = True
        mf.grease_pencil.fill_color = (1, 1, 1, 1)
        self.data.materials.append(mf)
        self.blend = blend
        self.strokes = []
        self.nlayers = 0

    def line(self, pts, color, radius=0.02, opacity=1.0, cyclic=False, radii=None, opac=None,
             cols=None, fill=None):
        """pts: list of (x,y,z). color: rgba. radii/opac/cols: optional per-point lists.
        fill: rgba -> a filled shape (fill material) instead of a line."""
        self.strokes.append((pts, color, radius, opacity, cyclic, radii, opac, cols, fill))

    def hidden_line(self, bvh, vdir, step=0.08, eps=0.03):
        """GP v3 strokes are NOT depth-tested against meshes in EEVEE (5.2, headless), and GP fills
        did not render as occluders either. So hidden lines are removed here: every stroke is
        resampled, each sample casts a ray toward the (ortho) camera through the occluder BVH,
        and the stroke is split into its visible runs."""
        from mathutils import Vector
        back = -Vector(vdir).normalized()
        out = []
        for (pts, c, r, o, cyc, radii, opac, cols, fill) in self.strokes:
            if fill is not None or len(pts) < 2:
                out.append((pts, c, r, o, cyc, radii, opac, cols, fill))
                continue
            P = [Vector(p) for p in pts] + ([Vector(pts[0])] if cyc else [])
            n0 = len(pts)
            idx = lambda k: k % n0
            samples = []  # (pos, src_index_a, src_index_b, t)
            for i in range(len(P) - 1):
                a, b = P[i], P[i + 1]
                n = max(1, int((b - a).length / step))
                for s in range(n):
                    samples.append((a.lerp(b, s / n), idx(i), idx(i + 1), s / n))
            samples.append((P[-1], idx(len(P) - 1), idx(len(P) - 1), 0.0))
            vis = []
            for (p, ia, ib, t) in samples:
                hit = bvh.ray_cast(p + back * eps, back)
                vis.append(hit[0] is None)
            run = []

            def emit(run):
                if len(run) < 2:
                    return
                q = [tuple(s[0]) for s in run]
                rr = [radii[s[1]] + (radii[s[2]] - radii[s[1]]) * s[3] for s in run] if radii else None
                oo = [opac[s[1]] + (opac[s[2]] - opac[s[1]]) * s[3] for s in run] if opac else None
                cc = [cols[s[2] if s[3] > 0.5 else s[1]] for s in run] if cols else None
                out.append((q, c, r, o, False, rr, oo, cc, None))
            for s, v in zip(samples, vis):
                if v:
                    run.append(s)
                else:
                    emit(run)
                    run = []
            if all(vis) and cyc:
                out.append((pts, c, r, o, cyc, radii, opac, cols, fill))
            else:
                emit(run)
        self.strokes = out

    def flush(self, layer_name="L", blend=None, opacity=1.0):
        if not self.strokes:
            return
        layer = self.data.layers.new(layer_name + str(self.nlayers))
        self.nlayers += 1
        layer.blend_mode = blend or self.blend
        layer.opacity = opacity
        layer.use_lights = False  # v3 layers are lit by default -> strokes render dark
        dr = layer.frames.new(1).drawing
        dr.add_strokes([len(s[0]) for s in self.strokes])
        pos, rad, op, vc = [], [], [], []
        for (pts, c, r, o, cyc, radii, opac, cols, fill) in self.strokes:
            n = len(pts)
            for i, p in enumerate(pts):
                pos.extend(p)
                rad.append(radii[i] if radii else r)
                op.append(opac[i] if opac else o)
                cc = cols[i] if cols else (fill if fill else c)
                vc.extend(cc if len(cc) == 4 else (*cc, 1.0))
        def _attr(name, typ):
            if name not in dr.attributes:
                dr.attributes.new(name, typ, "POINT")
            return dr.attributes[name]
        dr.attributes["position"].data.foreach_set("vector", pos)
        _attr("radius", "FLOAT").data.foreach_set("value", rad)
        _attr("opacity", "FLOAT").data.foreach_set("value", op)
        _attr("vertex_color", "FLOAT_COLOR").data.foreach_set("color", vc)
        for i, s in enumerate(self.strokes):
            st = dr.strokes[i]
            st.cyclic = s[4]
            if s[8] is not None:
                st.material_index = 1
                st.fill_color = s[8]
            # caps are int attributes in v3 (0 = round, the default)
        self.strokes = []
        return layer


# ---------------------------------------------------------------- emissive mesh helpers
def emit_mat(name, rgba, strength=1.0, alpha=1.0, additive=True):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = strength
    if additive:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        add = nt.nodes.new("ShaderNodeAddShader")
        # scale emission by alpha, add to fully transparent -> pure additive glow
        em.inputs["Strength"].default_value = strength * alpha
        nt.links.new(em.outputs[0], add.inputs[0])
        nt.links.new(tr.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    try:
        # opaque occluders must write depth (DITHERED) so GP strokes behind them are hidden
        m.surface_render_method = "BLENDED" if additive else "DITHERED"
    except Exception:
        pass
    return m


def radial_glow_mat(name, rgba, strength=2.0, falloff=2.0):
    """Additive disc glow: emission * (1 - r)^falloff on a unit plane (UV centred)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (0, 0, 0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = falloff
    nt.links.new(gr.outputs["Fac"], pw.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    nt.links.new(pw.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], add.inputs[0])
    nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m


def mesh_from(name, verts, faces, mat, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    o.location = loc
    o.rotation_euler = rot
    return o


def disc(name, radius, mat, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Unit-object-space disc: Object coords run -1..1 across it, for radial_glow_mat."""
    n = 64
    verts = [(0, 0, 0)] + [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    o = mesh_from(name, verts, faces, mat, loc, rot)
    o.scale = (radius, radius, radius)
    return o


def annulus_sector(name, r0, r1, a0, a1, mat, z=0.0, seg=24):
    verts, faces = [], []
    for i in range(seg + 1):
        a = a0 + (a1 - a0) * i / seg
        verts.append((r0 * math.cos(a), r0 * math.sin(a), z))
        verts.append((r1 * math.cos(a), r1 * math.sin(a), z))
    for i in range(seg):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    return mesh_from(name, verts, faces, mat)


def text(body, mat, loc, size=1.0, rot=(0, 0, 0), font=None, align="CENTER", extrude=0.0):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = extrude
    if font:
        cu.font = font
    o = bpy.data.objects.new("txt", cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    o.location = loc
    o.rotation_euler = rot
    return o


def load_font(path):
    try:
        return bpy.data.fonts.load(path, check_existing=True)
    except Exception:
        return None
