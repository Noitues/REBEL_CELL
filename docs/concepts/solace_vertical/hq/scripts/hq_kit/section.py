"""hq_kit.section: the OCCLUSION rule of the HQ camera rig, as a clip inserted into the city materials (Blender side;
imports bpy lazily). v3 (designer note 2026-10-15: "The foreground blocking buildings should be flattened or made
transparent when the camera needs to look through them to see the HQ").

The rule (pure python twin: downtown.occlusion_params / downtown.occlusion_state; NOTES "Occlusion: camera-rig rule"):
  inputs   the camera (position) and the TARGET VOLUME: the HQ's active room + the visible route nodes (their front
           points), widened by a ~10 % margin
  cone     every ray from the camera to the target volume; a city building is an OCCLUDER when its footprint meets the
           cone of the targets BEHIND it (laterally) and its top reaches into that cone (its top's sight tangent is
           above the lowest ray to those targets); the cone is sampled at NK depths (knots) and interpolated
  step 1   FLATTEN: an occluder is section-cut to a lit stub of `stub` BU (1-2 storeys: the shop fronts stay lit); its
           open top shows a near-black POCHE, so it reads as a cut model, never as a hollow shell
  step 2   GHOST: if the stub still reaches into the cone, the stub fades to `ghost` opacity (15-20 %) with faint edges
           (a cool edge line on the box edges) and its window dots (dimmed with it); never fully invisible
  outside  buildings outside the cone keep their full height
  easing   the cone has soft borders (`tsoft` lateral, `vsoft` vertical): as the orbit camera moves, a building's cut
           height and opacity slide over the border band instead of snapping. In Godot the same values are per-instance
           targets tweened over 0.4 s (see NOTES).

Per-face data (Acc in hq_scene): "bc" = (building centre x, y, top z; top 0 = never cut), "bh" = (half-size x, y, 0).
Per-frame data: scene custom properties occ_* (set_frame).

    from hq_kit import section
    section.insert(material)          # idempotent
    section.set_frame(scene, params)  # params = downtown.occlusion_params(...) or None (off)
Godot: a uniform block in the city / neon shaders (discard above the per-instance cut height; ALPHA via a dithered
alpha-hash fade for the ghost), the per-instance cut height + opacity from INSTANCE_CUSTOM of the city MultiMesh.
"""

NK = 5                  # depth knots of the cone (downtown.occlusion_params)
KEYS = ("occ_on", "occ_cx", "occ_cy", "occ_cz", "occ_ux", "occ_uy", "occ_tsoft", "occ_a0", "occ_amax", "occ_vsoft",
        "occ_stub", "occ_ghost", "occ_edge") + tuple("occ_%s%d" % (c, k) for c in "tTv" for k in range(NK))
POCHE = (0.010, 0.010, 0.013)
EDGE_COL = (0.55, 0.68, 0.85)
CLUTTER = 25.0          # roof clutter (tanks, antennas, holo boards) stands at most this far above a building's top


def set_frame(scene, params):
    p = params or {}
    for k in KEYS:
        scene[k] = float(p.get(k, 0.0))


def insert(mat):
    import bpy  # noqa: F401
    if mat is None or mat.node_tree is None or mat.get("hq_occ"):
        return
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None or not out.inputs["Surface"].links:
        return
    src = out.inputs["Surface"].links[0].from_socket

    def V(name):
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "VIEW_LAYER"
        a.attribute_name = name
        return a.outputs["Fac"]

    def M(op, a, b=None, c=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for k, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[k].default_value = v
            else:
                nt.links.new(v, n.inputs[k])
        return n.outputs[0]

    def soft(x, w):
        """smoothstep(0, w, x) (w a socket or a number)."""
        t = M("MINIMUM", M("MAXIMUM", M("DIVIDE", x, M("MAXIMUM", w, 1e-4)), 0.0), 1.0)
        return M("MULTIPLY", M("MULTIPLY", t, t), M("SUBTRACT", 3.0, M("MULTIPLY", t, 2.0)))

    def geo_attr(name):
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "GEOMETRY"
        a.attribute_name = name
        s = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(a.outputs["Vector"], s.inputs[0])
        return s.outputs
    bx, by, top = geo_attr("bc")
    hx, hy, _ = geo_attr("bh")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gp.inputs[0])
    PX, PY, Z = gp.outputs[0], gp.outputs[1], gp.outputs[2]
    on = M("MULTIPLY", M("GREATER_THAN", top, 0.5), V("occ_on"))
    r = M("MAXIMUM", M("SQRT", M("ADD", M("MULTIPLY", hx, hx), M("MULTIPLY", hy, hy))), 0.5)
    dx = M("SUBTRACT", bx, V("occ_cx"))
    dy = M("SUBTRACT", by, V("occ_cy"))
    ux, uy = V("occ_ux"), V("occ_uy")
    al = M("ADD", M("MULTIPLY", dx, ux), M("MULTIPLY", dy, uy))                  # along the view (horizontal)
    la = M("SUBTRACT", M("MULTIPLY", dy, ux), M("MULTIPLY", dx, uy))             # across it
    alc = M("MAXIMUM", al, 1.0)
    ts = V("occ_tsoft")
    # the cone at the building's depth: only the targets BEHIND it count (knots k = 0..NK-1 from the nearest target's
    # depth occ_a0 to the farthest occ_amax; piecewise linear between them)
    fk = M("MINIMUM", M("MAXIMUM", M("MULTIPLY", M("DIVIDE", M("SUBTRACT", M("SUBTRACT", al, r), V("occ_a0")),
                                                     M("MAXIMUM", M("SUBTRACT", V("occ_amax"), V("occ_a0")), 1.0)),
                                              float(NK - 1)), 0.0), float(NK - 1))

    def knot(key):
        v = V("occ_%s0" % key)
        for k in range(1, NK):
            w_ = M("MINIMUM", M("MAXIMUM", M("SUBTRACT", fk, float(k - 1)), 0.0), 1.0)
            v = M("ADD", v, M("MULTIPLY", w_, M("SUBTRACT", V("occ_%s%d" % (key, k)), V("occ_%s%d" % (key, k - 1)))))
        return v
    tmin, tmax, vmin = knot("t"), knot("T"), knot("v")
    lat = M("MULTIPLY", soft(M("SUBTRACT", M("DIVIDE", M("ADD", la, r), alc), tmin), ts),
            soft(M("SUBTRACT", tmax, M("DIVIDE", M("SUBTRACT", la, r), alc)), ts))
    front = M("MULTIPLY", M("GREATER_THAN", al, 0.0), soft(M("SUBTRACT", V("occ_amax"), M("SUBTRACT", al, r)), 6.0))
    far = M("ADD", al, r)
    vs = V("occ_vsoft")

    def blocks(ztop):
        return soft(M("SUBTRACT", M("DIVIDE", M("SUBTRACT", ztop, V("occ_cz")), M("MAXIMUM", far, 1.0)), vmin), vs)
    fc = M("MULTIPLY", M("MULTIPLY", on, lat), M("MULTIPLY", front, blocks(top)))     # 0..1: the occluder weight
    stub = M("MINIMUM", V("occ_stub"), top)
    # the cut height: full (above the roof clutter) outside the cone, the stub inside, sliding over the soft border
    zc = M("ADD", stub, M("MULTIPLY", M("SUBTRACT", 1.0, fc), M("SUBTRACT", M("ADD", top, CLUTTER), stub)))
    cut = M("GREATER_THAN", Z, zc)
    g = M("MULTIPLY", fc, blocks(stub))                                             # 0..1: the ghost weight
    # faint edges for a ghost: on a face, two of the four box distances (x, y, cut top, ground) are near zero
    w = 0.4

    def near(d):
        return M("LESS_THAN", M("ABSOLUTE", d), w)
    ex = near(M("SUBTRACT", hx, M("ABSOLUTE", M("SUBTRACT", PX, bx))))
    ey = near(M("SUBTRACT", hy, M("ABSOLUTE", M("SUBTRACT", PY, by))))
    ez = near(M("SUBTRACT", M("MINIMUM", zc, top), Z))
    eb = near(M("SUBTRACT", Z, 0.16))
    edge = M("GREATER_THAN", M("ADD", M("ADD", ex, ey), M("ADD", ez, eb)), 1.5)
    ge = M("MULTIPLY", g, edge)
    alpha = M("MINIMUM", M("ADD", M("SUBTRACT", 1.0, M("MULTIPLY", g, M("SUBTRACT", 1.0, V("occ_ghost")))),
                           M("MULTIPLY", ge, 0.22)), 1.0)
    poche = M("MULTIPLY", M("GREATER_THAN", fc, 0.5), geo.outputs["Backfacing"])
    dk = nt.nodes.new("ShaderNodeBsdfDiffuse")
    dk.inputs["Color"].default_value = POCHE + (1.0,)
    m1 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(poche, m1.inputs[0])
    nt.links.new(src, m1.inputs[1])
    nt.links.new(dk.outputs[0], m1.inputs[2])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = EDGE_COL + (1.0,)
    nt.links.new(M("MULTIPLY", ge, V("occ_edge")), em.inputs["Strength"])
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(m1.outputs[0], ad.inputs[0])
    nt.links.new(em.outputs[0], ad.inputs[1])
    tr0 = nt.nodes.new("ShaderNodeBsdfTransparent")
    m15 = nt.nodes.new("ShaderNodeMixShader")                                      # the ghost fade
    nt.links.new(alpha, m15.inputs[0])
    nt.links.new(tr0.outputs[0], m15.inputs[1])
    nt.links.new(ad.outputs[0], m15.inputs[2])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m2 = nt.nodes.new("ShaderNodeMixShader")                                       # the flatten (section cut)
    nt.links.new(cut, m2.inputs[0])
    nt.links.new(m15.outputs[0], m2.inputs[1])
    nt.links.new(tr.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"])
    mat["hq_occ"] = 1
    try:
        mat.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        pass
    try:
        mat.use_backface_culling = False
    except AttributeError:
        pass
