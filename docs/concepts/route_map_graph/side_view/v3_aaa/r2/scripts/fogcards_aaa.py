"""Fog strata as lit cards (exec'd after light_aaa.py). Designer feedback: the haze above the buildings must be streaky,
wind-sheared horizontal bands and wisps in thin layers at different heights, lit from below by the city glow.

A path-traced heterogeneous medium did this (light_aaa.py, job flag "vol_strata") but cost ~7x the volume pass on this
CPU. Cards are what Godot would ship anyway (layered fog sprites), so this is the production-faithful version:
  - 6 bands (CRITIQUE §4): z 40-45, 52-58, 66-73, 92-100, 130-140, 168-180, pushed deeper as they rise (y 30..420);
    the lowest sits above the highest option room (z 32) + 6 BU;
  - density = 4D noise on (x' * 0.0035, z_tilted * 0.15) where x' = x + a 35 BU domain warp and z_tilted = z - x tan(t)
    with a per-band wind tilt t of +-2-4 deg; soft remap 0.46-0.68, power 1.4; asymmetric profile
    smoothstep(0, 0.12, v) * (1 - v)^1.6 (sharp underside, feathered top); 15 % edge fade in x;
  - shading = Translucent BSDF (lit from below / behind by the city-glow up-lights, light-linked to the cards only)
    plus an underlight emission = density x district colour(x) x (1 - v)^3 x 2.1. Alpha <= 0.55, so it is never a slab.
Seeded (the noise W per card is fixed). Hidden in the data passes; see-through for camera rays in the volume pass.
"""

FOG_CARDS = [
    # band z0, z1 (the bright underside sits at z0), card y (higher bands deeper), opacity, wind tilt (rad), drift seed
    (40.0, 45.0, 30.0, 0.90, 0.045, 1.3),
    (52.0, 58.0, 62.0, 0.90, -0.035, 7.0),
    (66.0, 73.0, 112.0, 0.95, 0.060, 12.7),
    (92.0, 100.0, 190.0, 0.95, -0.050, 18.4),
    (130.0, 140.0, 300.0, 0.95, 0.040, 24.1),
    (168.0, 180.0, 420.0, 0.90, -0.065, 29.8),
]
FOG_OBJS = []
UNDERLIGHT = ((0.0, (1.0, 0.16, 0.54)), (0.3, (0.16, 0.83, 1.0)), (0.55, (1.0, 0.16, 0.54)), (0.8, (0.16, 0.83, 1.0)),
              (1.0, (0.54, 0.24, 1.0)))     # the district pair along x, as if the street below lit the band


def mat_fogcard(name, opacity, tilt, seed):
    m = bpy.data.materials.new(name)
    for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, prop, val)
        except (AttributeError, TypeError):
            pass
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], sx.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gen = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(tc.outputs["Generated"], gen.inputs[0])
    X, Z = sx.outputs["X"], sx.outputs["Z"]

    def noise4(vx, vz, det, w, rough=0.55, dist=0.0):
        cv = nt.nodes.new("ShaderNodeCombineXYZ")
        L(vx, cv.inputs[0])
        L(vz, cv.inputs[1])
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "4D"
        nz.inputs["W"].default_value = w
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = det
        nz.inputs["Roughness"].default_value = rough
        nz.inputs["Distortion"].default_value = dist
        L(cv.outputs[0], nz.inputs["Vector"])
        return nz.outputs["Fac"]
    # domain warp along the wind: a slow noise x 35 BU added to x
    warp = noise4(math_n(nt, "MULTIPLY", X, 0.01), math_n(nt, "MULTIPLY", Z, 0.01), 2.0, seed + 3.0)
    xw = math_n(nt, "ADD", X, math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", warp, 0.5), 120.0))
    # wind tilt: z' = z - x tan(theta), then the 170:1 anisotropic scales (x 0.0035, z 0.6)
    zt = math_n(nt, "SUBTRACT", Z, math_n(nt, "MULTIPLY", X, tilt))
    n = noise4(math_n(nt, "MULTIPLY", xw, 0.010), math_n(nt, "MULTIPLY", zt, 0.15), 4.0, seed, 0.6, 0.2)   # soft wind-sheared bands (~7 BU), not crisp lines
    cr = nn(nt, "ShaderNodeMapRange", From_Min=0.46, From_Max=0.68, To_Min=0.0, To_Max=1.0)   # soft remap; Blender noise sits lower than FastNoise
    L(n, cr.inputs["Value"])
    d = math_n(nt, "POWER", cr.outputs[0], 1.4)
    # tear the band along x (a near-camera band read as a ruler-straight bar): a second, x-only noise breaks it
    #  into wisps 20-60 BU long with gaps
    tear = noise4(math_n(nt, "MULTIPLY", xw, 0.035), math_n(nt, "MULTIPLY", zt, 0.05), 3.0, seed + 17.0)
    tr_ = nn(nt, "ShaderNodeMapRange", From_Min=0.38, From_Max=0.62, To_Min=0.0, To_Max=1.0)
    L(tear, tr_.inputs["Value"])
    d = math_n(nt, "MULTIPLY", d, tr_.outputs[0])
    # asymmetric profile: sharp bottom, feathered top (v = 0 at the band's underside)
    v = gen.outputs["Z"]
    sm = nn(nt, "ShaderNodeMapRange", From_Min=0.0, From_Max=0.12, To_Min=0.0, To_Max=1.0)
    sm.interpolation_type = "SMOOTHSTEP"
    L(v, sm.inputs["Value"])
    prof = math_n(nt, "MULTIPLY", sm.outputs[0], math_n(nt, "POWER", math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", 1.0, v), 0.0), 1.6))
    # 15 % edge fade in x (kills the card ends)
    e0 = nn(nt, "ShaderNodeMapRange", From_Min=0.0, From_Max=0.15, To_Min=0.0, To_Max=1.0)
    e0.interpolation_type = "SMOOTHSTEP"
    L(gen.outputs["X"], e0.inputs["Value"])
    e1 = nn(nt, "ShaderNodeMapRange", From_Min=1.0, From_Max=0.85, To_Min=0.0, To_Max=1.0)
    e1.interpolation_type = "SMOOTHSTEP"
    L(gen.outputs["X"], e1.inputs["Value"])
    dens = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", d, prof), math_n(nt, "MULTIPLY", e0.outputs[0], e1.outputs[0]))
    a = math_n(nt, "MINIMUM", math_n(nt, "MULTIPLY", dens, opacity), 0.55)
    # underlight: density x district colour(x) x (1 - v)^3 x 0.35 (emission), plus real translucency
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = UNDERLIGHT[0][0], UNDERLIGHT[0][1] + (1,)
    els[1].position, els[1].color = UNDERLIGHT[-1][0], UNDERLIGHT[-1][1] + (1,)
    for pos, c in UNDERLIGHT[1:-1]:
        e = els.new(pos)
        e.color = c + (1,)
    L(gen.outputs["X"], ramp.inputs[0])
    lip = math_n(nt, "POWER", math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", 1.0, v), 0.0), 3.0)
    em = nt.nodes.new("ShaderNodeEmission")
    L(ramp.outputs["Color"], em.inputs["Color"])
    L(math_n(nt, "MULTIPLY", lip, FOG_UNDERLIGHT_K), em.inputs["Strength"])
    tl = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (0.75, 0.72, 0.85, 1)
    add = nt.nodes.new("ShaderNodeAddShader")
    L(tl.outputs[0], add.inputs[0])
    L(em.outputs[0], add.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    L(a, mix.inputs[0])
    L(tr.outputs[0], mix.inputs[1])
    L(add.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs["Surface"])
    try:
        m.cycles.emission_sampling = "NONE"
    except (AttributeError, TypeError):
        pass
    return m


FOG_UNDERLIGHT_K = 0.35 * 6.0 * JOB.get("fog_k", 1.0)   # x3: the cards are thin, the volume recipe's 0.35 was per BU

if not JOB.get("vol_strata") and not JOB.get("no_fogcards"):
    fog_coll = bpy.data.collections.new("fog_receivers")
    scene.collection.children.link(fog_coll)
    for k, (z0, z1, y, op, tilt, seed) in enumerate(FOG_CARDS):
        th = z1 - z0
        za, zb = z0 - th * 0.12, z0 + th * 2.2          # v = 0.05 at the underside; the top feathers above the band
        me = bpy.data.meshes.new("fogcard_%d" % k)
        bm = bmesh.new()
        nx = 24
        vs = []
        for i in range(nx + 1):
            x = -340.0 + 940.0 * i / nx
            vs.append((bm.verts.new((x, y, za)), bm.verts.new((x, y, zb))))
        for i in range(nx):
            bm.faces.new((vs[i][0], vs[i + 1][0], vs[i + 1][1], vs[i][1]))
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("fogcard_%d" % k, me)
        me.materials.append(mat_fogcard("fogcard_m%d" % k, op, tilt, seed))
        scene.collection.objects.link(ob)
        fog_coll.objects.link(ob)
        ob.visible_shadow = False
        FOG_OBJS.append(ob)
    # (the haze volumes are NOT receivers: city glow on the haze made vertical light columns behind the options)
    # city glow reaches only the fog (cards + haze) through light linking; it no longer needs the haze-only flags
    for ob, e0, grp in LIGHTS:
        if ob.name.startswith("cityglow"):
            for attr_ in ("visible_diffuse", "visible_glossy", "visible_transmission"):
                setattr(ob, attr_, True)
            ob.light_linking.receiver_collection = fog_coll
    HOLO_OBJS.extend(FOG_OBJS)        # hidden in the data passes like the holograms
    print("fog cards", len(FOG_OBJS), flush=True)
