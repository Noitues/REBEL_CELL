"""V3 AAA materials for Cycles (exec'd into scene_aaa.py's namespace; LOOK = "cel" | "real" | "hybrid").

The V3 dynamic faces carry: col (base colour), fj (facet jitter 0..1), sem (R = class, G = room / 32, B = column / 10),
bid (a per-part random colour). Every look reads those, so the geometry is shared and only the shading changes.
  surf   Principled BSDF. Class 0.2 (ground) is wet asphalt with mirror puddles (all looks). Classes 0.6 / 0.85 (mid row,
         far city) get a procedural window grid (dark glass + a seeded share of lit cells), so the skyline is dense.
         "real" adds concrete grime, streaks and bump, metal link structure and glossy glass; "cel" and "hybrid" keep
         flat vertex colour with the facet jitter (the post bands the light for "cel").
  neon / win   emission (strength per look); the post reads the Emit pass for bloom and rain light.
  air / steam  additive (transparent + emission), the V3 dynamic shafts and trails, scaled per look.
"""

LK = {
    # neon / window emission strength, additive-air strength, albedo scale, wall roughness, specular, window-grid share
    # lit on the far city (pf) and the mid row (pm), and the window-grid emission strength (gs)
    # critique pass: neon is the TRIM level (1.2-1.8); hero signs are the text signs (dress_aaa, 6-8, at most 6)
    "cel":    dict(neon=1.6, win=0.32, air=0.12, alb=1.0, rough=0.78, spec=0.22, gs=0.18),
    "hybrid": dict(neon=1.6, win=0.32, air=0.08, alb=1.0, rough=0.62, spec=0.38, gs=0.18),
    "real":   dict(neon=1.6, win=0.32, air=0.0, alb=0.85, rough=0.55, spec=0.5, gs=0.18),
}[LOOK]
ROOM_EMIT_K = 4.0      # room faces: 4 x the trim level (6.4) x the room's state factor (pw, written per shot)
CLASS_EMIT = {0.85: 0.14, 0.6: 0.6, 0.2: 0.35, 0.7: 0.6}   # far x0.14 (roof trims read as floating lines), mid x0.6, street paint x0.35, link glazing x0.6
# windows: 80 % warm 3200 K, 15 % cool 5500 K, 5 % accent from the district pair (magenta / cyan)
WINDOW_WARM, WINDOW_COOL, WINDOW_PINK = (1.0, 0.70, 0.42), (0.92, 0.95, 1.0), (1.0, 0.16, 0.54)
P_FLOOR_LIT, P_WIN_LIT = 0.35, 0.75


def nn(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k.startswith("op"):
            n.operation = v
        elif k == "dt":
            n.data_type = v
        elif k == "blend":
            n.blend_type = v
        else:
            key = k.replace("_", " ")
            n.inputs[key].default_value = v
    return n


def math_n(nt, op, a, b=None, c=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for idx, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[idx].default_value = v
        else:
            nt.links.new(v, n.inputs[idx])
    return n.outputs[0]


def vmath(nt, op, a, b=None, scale=None):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    for idx, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, tuple):
            n.inputs[idx].default_value = v
        else:
            nt.links.new(v, n.inputs[idx])
    if scale is not None:
        if isinstance(scale, (int, float)):
            n.inputs["Scale"].default_value = scale
        else:
            nt.links.new(scale, n.inputs["Scale"])
    return n.outputs["Vector"] if op != "DOT_PRODUCT" and op != "LENGTH" else n.outputs["Value"]


def mix_col(nt, fac, a, b, blend="MIX"):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = blend
    for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = v + (1.0,) if len(v) == 3 else v
        else:
            nt.links.new(v, sock)
    return n.outputs[2]


def is_class(nt, sem_r, c, eps=0.04):
    return math_n(nt, "COMPARE", sem_r, c, eps)


def mat_surface():
    m = bpy.data.materials.new("surf_" + LOOK)
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    fj = attr(nt, "fj")
    sem = attr(nt, "sem")
    bid = attr(nt, "bid")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    L(sem.outputs["Color"], sep.inputs[0])
    sem_r = sep.outputs[0]
    psep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], psep.inputs[0])
    nsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(geo.outputs["Normal"], nsep.inputs[0])
    # base colour: vertex colour x facet jitter
    lo, hi = (0.86, 1.12) if LOOK != "real" else (0.95, 1.04)
    mr = nn(nt, "ShaderNodeMapRange", To_Min=lo, To_Max=hi)
    L(fj.outputs["Fac"], mr.inputs["Value"])
    base = vmath(nt, "SCALE", col.outputs["Color"], scale=mr.outputs[0])
    base = vmath(nt, "SCALE", base, scale=LK["alb"])
    ground = is_class(nt, sem_r, 0.2)
    link = is_class(nt, sem_r, 0.7)
    far = is_class(nt, sem_r, 0.85)
    mid = is_class(nt, sem_r, 0.6)
    vert = math_n(nt, "LESS_THAN", math_n(nt, "ABSOLUTE", nsep.outputs["Z"]), 0.3)
    rough = LK["rough"]
    rough_s = None
    bump_h = None
    if LOOK == "real":
        # concrete: low-frequency albedo variation, vertical rain streaks, fine bump
        n1 = nn(nt, "ShaderNodeTexNoise", Scale=0.35, Detail=6.0, Roughness=0.6)
        L(geo.outputs["Position"], n1.inputs["Vector"])
        g1 = nn(nt, "ShaderNodeMapRange", From_Min=0.3, From_Max=0.7, To_Min=0.78, To_Max=1.08)
        L(n1.outputs["Fac"], g1.inputs["Value"])
        stretch = vmath(nt, "MULTIPLY", geo.outputs["Position"], (1.0, 1.0, 0.1))
        n2 = nn(nt, "ShaderNodeTexNoise", Scale=1.1, Detail=3.0)
        L(stretch, n2.inputs["Vector"])
        g2 = nn(nt, "ShaderNodeMapRange", From_Min=0.45, From_Max=0.75, To_Min=1.0, To_Max=0.72)
        L(n2.outputs["Fac"], g2.inputs["Value"])
        base = vmath(nt, "SCALE", base, scale=g1.outputs[0])
        base = vmath(nt, "SCALE", base, scale=g2.outputs[0])
        # desaturate a little (painted concrete, not toy plastic)
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        L(base, bw.inputs[0])
        base = mix_col(nt, 0.3, base, bw.outputs[0])
        rmr = nn(nt, "ShaderNodeMapRange", From_Min=0.3, From_Max=0.7, To_Min=0.38, To_Max=0.82)
        L(n2.outputs["Fac"], rmr.inputs["Value"])
        rough_s = rmr.outputs[0]
        n3 = nn(nt, "ShaderNodeTexNoise", Scale=4.0, Detail=8.0)
        L(geo.outputs["Position"], n3.inputs["Vector"])
        bump_h = n3.outputs["Fac"]
    # window grid on the mid row and far city (vertical faces only)
    u = math_n(nt, "ADD", psep.outputs["X"], psep.outputs["Y"])
    su, sv = 1.8, 2.9
    cu = math_n(nt, "FLOOR", math_n(nt, "DIVIDE", u, su))
    cv = math_n(nt, "FLOOR", math_n(nt, "DIVIDE", psep.outputs["Z"], sv))
    fu = math_n(nt, "FRACT", math_n(nt, "DIVIDE", u, su))
    fv = math_n(nt, "FRACT", math_n(nt, "DIVIDE", psep.outputs["Z"], sv))
    wmask = math_n(nt, "MULTIPLY",
                   math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", fu, 0.30), math_n(nt, "LESS_THAN", fu, 0.70)),
                   math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", fv, 0.34), math_n(nt, "LESS_THAN", fv, 0.66)))
    bsep = nt.nodes.new("ShaderNodeSeparateColor")
    L(bid.outputs["Color"], bsep.inputs[0])
    cid = nt.nodes.new("ShaderNodeCombineXYZ")
    L(cu, cid.inputs[0])
    L(cv, cid.inputs[1])
    L(math_n(nt, "MULTIPLY", bsep.outputs[0], 97.0), cid.inputs[2])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    L(cid.outputs[0], wn.inputs["Vector"])
    cls_on = math_n(nt, "ADD", far, mid)
    # lit by floor runs: a floor (per building) is lit with P 0.35, then each window with P 0.75; bays of 3 go dark
    fid = nt.nodes.new("ShaderNodeCombineXYZ")
    L(cv, fid.inputs[0])
    L(math_n(nt, "MULTIPLY", bsep.outputs[0], 131.0), fid.inputs[1])
    fid.inputs[2].default_value = 3.3
    fn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    fn.noise_dimensions = "3D"
    L(fid.outputs[0], fn.inputs["Vector"])
    bay = nt.nodes.new("ShaderNodeCombineXYZ")
    L(math_n(nt, "FLOOR", math_n(nt, "DIVIDE", cu, 3.0)), bay.inputs[0])
    L(cv, bay.inputs[1])
    L(math_n(nt, "MULTIPLY", bsep.outputs[1], 71.0), bay.inputs[2])
    bn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    bn.noise_dimensions = "3D"
    L(bay.outputs[0], bn.inputs["Vector"])
    lit = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", fn.outputs["Value"], P_FLOOR_LIT),
                 math_n(nt, "LESS_THAN", wn.outputs["Value"], P_WIN_LIT))
    lit = math_n(nt, "MULTIPLY", lit, math_n(nt, "GREATER_THAN", bn.outputs["Value"], 0.12))
    on = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", wmask, vert), cls_on)
    wsep = nt.nodes.new("ShaderNodeSeparateColor")
    L(wn.outputs["Color"], wsep.inputs[0])
    wcol = mix_col(nt, math_n(nt, "GREATER_THAN", wsep.outputs[0], 0.80), WINDOW_WARM, WINDOW_COOL)
    wcol = mix_col(nt, math_n(nt, "GREATER_THAN", wsep.outputs[0], 0.95), wcol, WINDOW_PINK)
    # log-normal intensity (sigma 0.5): exp(0.5 * z), z ~ (u - 0.5) * 3.4
    lgn = math_n(nt, "EXPONENT", math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", wsep.outputs[2], 0.5), 1.7))
    clsk = math_n(nt, "ADD", math_n(nt, "MULTIPLY", far, 0.30), math_n(nt, "MULTIPLY", mid, 0.6))
    wint = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", lgn, clsk), math_n(nt, "MULTIPLY", on, lit))
    wem = vmath(nt, "SCALE", wcol, scale=wint)
    # unlit panes: darker glass
    dark = math_n(nt, "MULTIPLY", on, math_n(nt, "SUBTRACT", 1.0, lit))
    base = vmath(nt, "SCALE", base, scale=math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MULTIPLY", dark, 0.55)))
    # wet ground: darker, mirror puddles
    pn = nn(nt, "ShaderNodeTexNoise", Scale=0.09, Detail=5.0, Roughness=0.55)
    L(geo.outputs["Position"], pn.inputs["Vector"])
    puddle = nn(nt, "ShaderNodeMapRange", From_Min=0.47, From_Max=0.56, To_Min=0.0, To_Max=1.0)
    L(pn.outputs["Fac"], puddle.inputs["Value"])
    g_rough = nn(nt, "ShaderNodeMapRange", From_Min=0.0, From_Max=1.0, To_Min=0.25, To_Max=0.03)
    L(puddle.outputs[0], g_rough.inputs["Value"])
    g_alb = nn(nt, "ShaderNodeMapRange", From_Min=0.0, From_Max=1.0, To_Min=0.62, To_Max=0.35)
    L(puddle.outputs[0], g_alb.inputs["Value"])
    gscale = math_n(nt, "ADD", math_n(nt, "MULTIPLY", ground, math_n(nt, "SUBTRACT", g_alb.outputs[0], 1.0)), 1.0)
    base = vmath(nt, "SCALE", base, scale=gscale)
    r_wall = rough_s if rough_s is not None else rough
    r1 = math_n(nt, "ADD", r_wall, 0.0) if not isinstance(r_wall, float) else None
    rsock = nt.nodes.new("ShaderNodeMix")
    rsock.data_type = "FLOAT"
    L(ground, rsock.inputs[0])
    if r1 is not None:
        L(r1, rsock.inputs[2])
    else:
        rsock.inputs[2].default_value = r_wall
    L(g_rough.outputs[0], rsock.inputs[3])
    rough_out = rsock.outputs[0]
    # glass windows reflect (lower roughness on window cells)
    rough_out = math_n(nt, "SUBTRACT", rough_out, math_n(nt, "MULTIPLY", dark, 0.45 if LOOK == "real" else 0.2))
    rough_out = math_n(nt, "MAXIMUM", rough_out, 0.03)
    if LOOK == "real":
        met = math_n(nt, "MULTIPLY", link, 0.8)
        L(met, bsdf.inputs["Metallic"])
        rough_out = math_n(nt, "SUBTRACT", rough_out, math_n(nt, "MULTIPLY", link, 0.2))
    L(base, bsdf.inputs["Base Color"])
    L(rough_out, bsdf.inputs["Roughness"])
    spec = math_n(nt, "ADD", LK["spec"], math_n(nt, "MULTIPLY", ground, 0.5 - LK["spec"]))
    L(spec, bsdf.inputs["Specular IOR Level"])
    L(wem, bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = LK["gs"]
    # ripples on the damp asphalt (0.5 BU, strength 0.15), only on the ground class; concrete bump on "real" walls
    rp = nn(nt, "ShaderNodeTexNoise", Scale=2.0, Detail=3.0, Roughness=0.5)
    L(geo.outputs["Position"], rp.inputs["Vector"])
    hgt = math_n(nt, "MULTIPLY", rp.outputs["Fac"], ground)
    if bump_h is not None:
        hgt = math_n(nt, "ADD", hgt, math_n(nt, "MULTIPLY", bump_h, math_n(nt, "SUBTRACT", 1.0, ground)))
    bump = nn(nt, "ShaderNodeBump", Strength=0.15, Distance=0.05)
    L(hgt, bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"])
    L(bsdf.outputs[0], out.inputs[0])
    return m


def mat_emit(name, k):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = attr(nt, "col")
    pw = attr(nt, "pw")                      # the hover power cut writes this face attribute (1 when absent: see below)
    em = nt.nodes.new("ShaderNodeEmission")
    # pw is 0 when the attribute is missing; the power pass writes 1 or k everywhere, so map 0 -> 1
    pwk = math_n(nt, "ADD", pw.outputs["Fac"], math_n(nt, "LESS_THAN", pw.outputs["Fac"], 0.001))
    sem = attr(nt, "sem")
    ssep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(sem.outputs["Color"], ssep.inputs[0])
    roomk = math_n(nt, "ADD", 1.0, math_n(nt, "MULTIPLY", is_class(nt, ssep.outputs[0], 0.5), ROOM_EMIT_K - 1.0))
    # street-level storefront glow on the route facades at half strength (CRITIQUE §2.6: keep it, at about half)
    _g = nt.nodes.new("ShaderNodeNewGeometry")
    _gz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(_g.outputs["Position"], _gz.inputs[0])
    shop = math_n(nt, "MULTIPLY", is_class(nt, ssep.outputs[0], 0.1), math_n(nt, "LESS_THAN", _gz.outputs["Z"], 4.2))
    roomk = math_n(nt, "MULTIPLY", roomk, math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MULTIPLY", shop, 0.5)))
    for cval, ck in CLASS_EMIT.items():
        roomk = math_n(nt, "MULTIPLY", roomk, math_n(nt, "ADD", 1.0, math_n(nt, "MULTIPLY", is_class(nt, ssep.outputs[0], cval), ck - 1.0)))
    nt.links.new(col.outputs["Color"], em.inputs["Color"])
    nt.links.new(math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", pwk, k), roomk), em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_air2(name, k, noise=False):
    m = mat_air(name, noise=noise)
    nt = m.node_tree
    em = next(n for n in nt.nodes if n.type == "EMISSION")
    em.inputs["Strength"].default_value = k
    return m


TOON = mat_surface()
NEONM = mat_emit("neon", LK["neon"])
WINM = mat_emit("win", LK["win"])
FARWINM = mat_emit("farwin", LK["win"] * 0.55)
AIRM = mat_air2("air", LK["air"])
TRAILM = mat_air2("trail", 4.0)
STEAMM = mat_air2("steam", 1.4, noise=True)

world = bpy.data.worlds.new("w")
scene.world = world
wnt = world.node_tree
wnt.nodes.clear()
_wo = wnt.nodes.new("ShaderNodeOutputWorld")
bg = wnt.nodes.new("ShaderNodeBackground")
_tc = wnt.nodes.new("ShaderNodeTexCoord")
_ws = wnt.nodes.new("ShaderNodeSeparateXYZ")
wnt.links.new(_tc.outputs["Generated"], _ws.inputs[0])
_wr = wnt.nodes.new("ShaderNodeValToRGB")
_wr.color_ramp.elements[0].position = 0.0
_wr.color_ramp.elements[0].color = (0.11, 0.035, 0.12, 1)
_wr.color_ramp.elements[1].position = 0.45
_wr.color_ramp.elements[1].color = (0.004, 0.004, 0.016, 1)
_we = _wr.color_ramp.elements.new(0.12)
_we.color = (0.035, 0.016, 0.06, 1)
wnt.links.new(_ws.outputs["Z"], _wr.inputs[0])
_wlp = wnt.nodes.new("ShaderNodeLightPath")
_wmix = wnt.nodes.new("ShaderNodeMix")
_wmix.data_type = "RGBA"
WORLD_CAM_K = _wmix                                     # factor 1 = the camera sees black (the volume render)
_wmix.inputs[0].default_value = 0.0
wnt.links.new(_wr.outputs["Color"], _wmix.inputs[6])
_wmix.inputs[7].default_value = (0, 0, 0, 1)
_wcam = math_n(wnt, "MULTIPLY", _wlp.outputs["Is Camera Ray"], 1.0)
WORLD_CAM_MUL = _wcam.node
wnt.links.new(_wcam, _wmix.inputs[0])
WORLD_CAM_MUL.inputs[1].default_value = 0.0
wnt.links.new(_wmix.outputs[2], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
wnt.links.new(bg.outputs[0], _wo.inputs["Surface"])

sun = bpy.data.lights.new("moon", "SUN")
sun.energy = 0.12      # a cool moon: route facades land at 0.03-0.08 scene-linear (CRITIQUE §3 #5)
sun.color = (0.62, 0.68, 1.0)
sun.angle = math.radians(2.0)
so = bpy.data.objects.new("moon", sun)
so.rotation_euler = (math.radians(52), math.radians(-28), math.radians(-24))
scene.collection.objects.link(so)

# Light-tree hygiene: the surface shader's window grid and the thousands of tiny window quads are seen, not sampled
# as lights (they would cost every shading point and add noise); neon, signs and holograms stay sampled.
for _m in (TOON, WINM, FARWINM):
    try:
        _m.cycles.emission_sampling = "NONE"
    except (AttributeError, TypeError) as _e:
        print("emission_sampling", _e, flush=True)
