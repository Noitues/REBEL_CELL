"""r3 fog, beams and their lights (exec'd at the end of light_aaa.py when JOB "r3fog" is on, the default).

Every placement comes from rules_r3.py (layout-driven rules) and every number from look_preset.py; nothing here is
hand-placed for this street. Real heterogeneous volumetrics on the GPU:
  city fog  ONE continuous field (no parallel bands): density thins with altitude; layering is a modulation on a
            warped height coordinate (per-depth wave and wind tilt, so layers bend, merge and split; a broad octave for
            8-15 BU banks and a fine one for 1-3 BU wisps); low-frequency clumps and holes; ragged high-frequency
            edges. Two rule-driven terms make the layering read: BANKS hugging building bases and alleys (the
            heightfield's bank map, z band from the preset) and a thin WISP in front of the first far layer at a
            height relative to the skyline. The fog floor rises over the decision set (its projected bounds).
  plumes    steam columns on N rooftop vents chosen by rule, feeding into the layers.
  mist      a thin ground mist over the road (the street transect), neon colour from shop-glow lights.
  beams     K coloured spot rigs on the tallest non-route roofs; the full-power light is linked to the media only
            (so a shaft lives where the fog is) plus a faint unlinked twin for continuity.
  glows     the city glow, the bank and wisp under-glows and the mist glows: placed by rule, unshadowed, light-linked.
Loop safety: every medium drifts along x and is evaluated twice, D(x - s p) (1 - p) + D(x - s (p - 1)) p, p = t / T, so
p = 0 and p = 1 give the same field. Each medium also has an absorption-only twin for the transmittance pass.
"""
exec(compile(open(os.path.join(HERE, "rules_r3.py")).read(), "rules_r3.py", "exec"), globals())


FOGP = PRE["fog"]
LODB = PRE["lod_bands"]
LOOP_T = float(JOB.get("loop_T", PRE["loop"]["T"]))
STRATA_K = float(JOB.get("strata_k", 1.0))          # a job-level multiplier on the fog peak (1 = the preset)
UNDER_K = float(JOB.get("under_k", FOGP["underlight_k"]))
MIST_K = float(JOB.get("mist_k", 1.0))
BEAM_K = float(JOB.get("beam_k", PRE["beams"]["power_k"]))
STRATA_COL = FOGP["colour"]
STRATA_ANISO = float(JOB.get("strata_aniso", FOGP["aniso"]))
MIST_COL = (0.85, 0.85, 1.0)
UNDERLIGHT_R3 = tuple((pos, PAL(c)) for pos, c in PRE["palette"]["underlight"])
DRIFT = []           # (value node, role, wind): role "o1" | "o2" | "w"
HET = []             # (object, scatter material, absorb material)
BEAM_LIGHTS = []     # (light object, origin, base direction, sweep, phase)
BEAM_HEADS = []      # (none: a housing in mid-air read as a moon)
_X0, _X1 = -340.0, 600.0


def _val(nt, v, role, wind):
    n = nt.nodes.new("ShaderNodeValue")
    n.outputs[0].default_value = v
    DRIFT.append((n, role, wind))
    return n.outputs[0]


def _noise(nt, vec, det, w, rough=0.55, dist=0.0):
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["W"].default_value = w
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = det
    nz.inputs["Roughness"].default_value = rough
    nz.inputs["Distortion"].default_value = dist
    nt.links.new(vec, nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _comb(nt, a, b, c):
    cv = nt.nodes.new("ShaderNodeCombineXYZ")
    for i, s in enumerate((a, b, c)):
        if isinstance(s, (int, float)):
            cv.inputs[i].default_value = s
        else:
            nt.links.new(s, cv.inputs[i])
    return cv.outputs[0]


def _smooth(nt, v, a, b):
    m = nn(nt, "ShaderNodeMapRange", From_Min=a, From_Max=b, To_Min=0.0, To_Max=1.0)
    m.interpolation_type = "SMOOTHSTEP"
    nt.links.new(v, m.inputs["Value"])
    return m.outputs[0]


def _drifted(nt, build, wind):
    """build(X, Y, Z) -> density socket; returns D(x + o1) (1 - w) + D(x + o2) w with the loop-phase values."""
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sx.inputs[0])
    X, Y, Z = sx.outputs["X"], sx.outputs["Y"], sx.outputs["Z"]
    o1 = _val(nt, 0.0, "o1", wind)
    o2 = _val(nt, wind * LOOP_T, "o2", wind)
    w = _val(nt, 0.0, "w", wind)
    d1 = build(math_n(nt, "ADD", X, o1), Y, Z)
    d2 = build(math_n(nt, "ADD", X, o2), Y, Z)
    d = math_n(nt, "ADD", math_n(nt, "MULTIPLY", d1, math_n(nt, "SUBTRACT", 1.0, w)), math_n(nt, "MULTIPLY", d2, w))
    return d, X, Y, Z


def _edge_fade(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    g = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], g.inputs[0])
    f = 1.0
    for ax in ("X", "Y"):
        f = math_n(nt, "MULTIPLY", f, math_n(nt, "MULTIPLY", _smooth(nt, g.outputs[ax], 0.0, 0.15),
                                             _smooth(nt, g.outputs[ax], 1.0, 0.85)))
    return f, g.outputs["Z"]


def _vol_out(nt, dens, col, aniso, mode, emit_col=None, emit_k=None):
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if mode == "absorb":
        va = nt.nodes.new("ShaderNodeVolumeAbsorption")
        # extinction of Volume Scatter is density x colour per channel; the absorption twin is density x (1 - colour)
        va.inputs["Color"].default_value = tuple(1.0 - c for c in col) + (1,)
        nt.links.new(dens, va.inputs["Density"])
        nt.links.new(va.outputs[0], out.inputs["Volume"])
        return
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = tuple(col) + (1,)
    vs.inputs["Anisotropy"].default_value = aniso
    nt.links.new(dens, vs.inputs["Density"])
    if emit_col is None:
        nt.links.new(vs.outputs[0], out.inputs["Volume"])
        return
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit_col, em.inputs["Color"])
    nt.links.new(emit_k, em.inputs["Strength"])
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(vs.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Volume"])


# ------------------------------------------------------------------ the city fog
def _cityfog_density(nt, X, Y, Z, seed):
    def n(vx, vy, vz, det, w, rough=0.55):
        return _noise(nt, _comb(nt, vx, vy, vz), det, w, rough)

    def M(a, k):
        return math_n(nt, "MULTIPLY", a, k)
    A = math_n
    # domain warp along the wind, a per-depth wave and a per-depth tilt of the height coordinate
    warp = n(M(X, 0.006), M(Y, 0.01), M(Z, 0.01), 2.0, seed + 3.0)
    xw = A(nt, "ADD", X, M(A(nt, "SUBTRACT", warp, 0.5), FOGP["warp"]))
    wave = n(M(X, 0.008), M(Y, 0.012), 0.0, 2.0, seed + 5.0)
    tiltn = n(0.0, M(Y, 0.004), 0.0, 1.0, seed + 7.0)
    zw = A(nt, "ADD", Z, M(A(nt, "SUBTRACT", wave, 0.5), FOGP["wave"]))
    zw = A(nt, "ADD", zw, M(X, M(A(nt, "SUBTRACT", tiltn, 0.5), FOGP["tilt"])))
    # layering: a broad octave (banks) and a fine one (wisps), mixed
    (b0, b1, b2), (f0, f1, f2) = FOGP["layer_scales"]
    lb = n(M(xw, b0), M(Y, b1), M(zw, b2), 3.0, seed)
    lf = n(M(xw, f0), M(Y, f1), M(zw, f2), 3.0, seed + 13.0)
    lay = A(nt, "ADD", M(lb, FOGP["layer_mix"]), M(lf, 1.0 - FOGP["layer_mix"]))
    zoom_ = A(nt, "SUBTRACT", 1.0, attr(nt, "unzoom", "OBJECT").outputs["Fac"])
    k_oct = _smooth(nt, zoom_, *LODB["fog_octaves_by_zoom"])
    lay = A(nt, "ADD", M(lb, A(nt, "SUBTRACT", 1.0, k_oct)), M(lay, k_oct))      # city view: the broad octave only
    lay = _smooth(nt, lay, *FOGP["layer_remap"])
    # clumps and holes (low frequency): layers fade in and out, never full width
    c0, c1, c2 = FOGP["clump_scale"]
    cl = _smooth(nt, n(M(X, c0), M(Y, c1), M(Z, c2), 2.0, seed + 11.0), *FOGP["clump_remap"])
    # ragged, feathered edges (high frequency)
    rag = A(nt, "ADD", 0.45, M(n(M(xw, 0.05), M(Y, 0.05), M(zw, 0.6), 2.0, seed + 17.0), 0.75))
    rag = A(nt, "ADD", A(nt, "SUBTRACT", 1.0, k_oct), M(rag, k_oct))
    # height: dense low, thinning with altitude
    hf = A(nt, "EXPONENT", M(A(nt, "MAXIMUM", A(nt, "SUBTRACT", Z, 30.0), 0.0), -1.0 / FOGP["height_scale"]))
    body = A(nt, "ADD", M(cl, FOGP["base"]), M(A(nt, "MULTIPLY", lay, cl), rag))
    body = A(nt, "MULTIPLY", body, hf)
    # BANKS: the heightfield's bank map (alleys, building bases) x the bank z band x clumps x ragged edges
    bx0, by0, bx1, by1 = RULES["bank_map"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = RULES["bank_image"]
    tex.interpolation = "Linear"
    tex.extension = "EXTEND"
    nt.links.new(_comb(nt, A(nt, "DIVIDE", A(nt, "SUBTRACT", X, bx0), bx1 - bx0),
                       A(nt, "DIVIDE", A(nt, "SUBTRACT", Y, by0), by1 - by0), 0.0), tex.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex.outputs["Color"], sep.inputs[0])
    bz0, bz1 = FOGP["bank_z"]
    vb = A(nt, "DIVIDE", A(nt, "SUBTRACT", zw, bz0 - (bz1 - bz0) * 0.0), bz1 - bz0)
    bprof = A(nt, "MULTIPLY", _smooth(nt, vb, -0.1, 0.2),
              A(nt, "POWER", A(nt, "MAXIMUM", A(nt, "SUBTRACT", 1.0, vb), 0.0), 1.3))
    bank = A(nt, "MULTIPLY", A(nt, "MULTIPLY", sep.outputs[0], bprof), A(nt, "MULTIPLY", cl, rag))
    # WISP: a thin layer in front of the first far layer, at a height relative to the skyline, tilted and waving
    wy0, wy1 = RULES["wisp_y"]
    zwisp = A(nt, "ADD", RULES["wisp_z"], A(nt, "ADD", M(X, FOGP["wisp_tilt"]), M(A(nt, "SUBTRACT", wave, 0.5), 10.0)))
    dz = A(nt, "DIVIDE", A(nt, "SUBTRACT", Z, zwisp), FOGP["wisp_thick"])
    thin = A(nt, "EXPONENT", A(nt, "MULTIPLY", A(nt, "MULTIPLY", dz, dz), -1.0))
    slab = A(nt, "MULTIPLY", _smooth(nt, Y, wy0, wy0 + 5.0), _smooth(nt, Y, wy1, wy1 - 5.0))
    wcl = _smooth(nt, n(M(X, 0.012), M(Y, 0.03), 0.0, 2.0, seed + 23.0), 0.42, 0.6)
    wisp = A(nt, "MULTIPLY", A(nt, "MULTIPLY", thin, slab), A(nt, "MULTIPLY", wcl, rag))
    wisp = A(nt, "MULTIPLY", wisp, _smooth(nt, zoom_, *LODB["wisps_on_at"]))
    tot = A(nt, "ADD", body, A(nt, "ADD", M(bank, FOGP["bank_peak"] / FOGP["peak"]), M(wisp, FOGP["wisp_peak"] / FOGP["peak"])))
    lo, za, zb = LODB["fog_density_by_zoom"]
    tot = M(tot, A(nt, "ADD", lo, M(_smooth(nt, zoom_, za, zb), 1.0 - lo)))
    return tot


def cityfog_mat(name, mode, seed=3.1, fill=False):
    m = bpy.data.materials.new(name + ("_abs" if mode == "absorb" else ""))
    nt = m.node_tree
    nt.nodes.clear()
    A = math_n
    d, X, Y, Z = _drifted(nt, lambda x, y, z: _cityfog_density(nt, x, y, z, seed), FOGP["wind"])
    fade, _gz = _edge_fade(nt)
    # the floor: FOGP floor in general; inside the decision set's view angle (its projected bounds + a margin) it rises
    # to the decision rooms' projected top elevation + a margin, so nothing sits behind them
    a = A(nt, "DIVIDE", A(nt, "SUBTRACT", X, FOG_CAM.x), A(nt, "SUBTRACT", Y, FOG_CAM.y))
    ca0, ca1 = RULES["fog_calm_a"]
    m0, m1 = FOGP["calm_margin"]
    calm = A(nt, "MULTIPLY", _smooth(nt, a, ca0 - m1, ca0 - m0), _smooth(nt, a, ca1 + m1, ca1 + m0))
    if fill:
        calm = 0.0
    zc = A(nt, "ADD", FOG_CAM.z + FOGP["floor_margin"], A(nt, "MULTIPLY", A(nt, "SUBTRACT", Y, FOG_CAM.y), RULES["fog_calm_e_top"]))
    fl = FOGP["floor"]
    zf = A(nt, "ADD", fl, A(nt, "MULTIPLY", calm, A(nt, "SUBTRACT", A(nt, "MAXIMUM", zc, fl), fl)))
    floor_ = _smooth(nt, A(nt, "SUBTRACT", Z, zf), 0.0, 9.0)
    top = _smooth(nt, Z, FOGP["box_top"], FOGP["box_top"] - 40.0)
    dens = A(nt, "MULTIPLY", A(nt, "MULTIPLY", d, A(nt, "MULTIPLY", floor_, top)),
             A(nt, "MULTIPLY", fade, FOGP["peak"] * STRATA_K))
    if fill:
        # storyboard FILL FOG: the same field (no calm) plus the back haze's density, outside the stage's own media
        # (complement of the back-haze box with a 60 BU soft edge, so the sum is seamless), times the object attribute
        # "fk" (the dive fades it to 0 per frame without touching the shader)
        bx0, by0, bx1, by1 = FILL_CORE
        inx = A(nt, "MULTIPLY", _smooth(nt, X, bx0, bx0 + 60.0), _smooth(nt, X, bx1, bx1 - 60.0))
        iny = A(nt, "MULTIPLY", _smooth(nt, Y, by0, by0 + 60.0), _smooth(nt, Y, by1, by1 - 60.0))
        outside = A(nt, "SUBTRACT", 1.0, A(nt, "MULTIPLY", inx, iny))
        hz = A(nt, "MULTIPLY", _smooth(nt, Z, 420.0, 300.0), FILL_HAZE)
        fk = attr(nt, "fk", "OBJECT").outputs["Fac"]
        fkh = attr(nt, "fkh", "OBJECT").outputs["Fac"]
        # the layered field at fk, the haze body at fkh (the city-wide haze of the aerial matches the stage's back haze)
        dens = A(nt, "MULTIPLY", A(nt, "ADD", A(nt, "MULTIPLY", dens, fk), A(nt, "MULTIPLY", hz, fkh)), outside)
    if mode == "absorb":
        _vol_out(nt, dens, STRATA_COL, STRATA_ANISO, mode)
        return m
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = UNDERLIGHT_R3[0][0], tuple(UNDERLIGHT_R3[0][1]) + (1,)
    els[1].position, els[1].color = UNDERLIGHT_R3[-1][0], tuple(UNDERLIGHT_R3[-1][1]) + (1,)
    for pos, c in UNDERLIGHT_R3[1:-1]:
        e = els.new(pos)
        e.color = tuple(c) + (1,)
    nt.links.new(A(nt, "DIVIDE", A(nt, "SUBTRACT", X, _X0), _X1 - _X0), ramp.inputs[0])
    low = A(nt, "POWER", A(nt, "SUBTRACT", 1.0, _smooth(nt, Z, 25.0, 130.0)), 2.0)   # city glow from below
    ek = A(nt, "MULTIPLY", A(nt, "MULTIPLY", dens, low), UNDER_K)
    _vol_out(nt, dens, STRATA_COL, STRATA_ANISO, mode, ramp.outputs["Color"], ek)
    return m


def plume_mat(name, px, py, pz, lean, ph, seed, mode):
    m = bpy.data.materials.new(name + ("_abs" if mode == "absorb" else ""))
    nt = m.node_tree
    nt.nodes.clear()

    def build(x, y, z):
        h = math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", z, pz), 0.0)
        cx = math_n(nt, "ADD", px, math_n(nt, "MULTIPLY", h, lean))
        r = math_n(nt, "ADD", 1.2, math_n(nt, "MULTIPLY", h, 0.28))
        dx = math_n(nt, "SUBTRACT", x, cx)
        dy = math_n(nt, "SUBTRACT", y, py)
        rr = math_n(nt, "DIVIDE", math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", dx, dx),
                                                              math_n(nt, "MULTIPLY", dy, dy))), r)
        core = math_n(nt, "POWER", math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", 1.0, rr), 0.0), 1.5)
        turb = _smooth(nt, _noise(nt, _comb(nt, math_n(nt, "MULTIPLY", x, 0.12), math_n(nt, "MULTIPLY", y, 0.12),
                                            math_n(nt, "MULTIPLY", z, 0.09)), 3.0, seed, 0.6, 0.4), 0.35, 0.7)
        fade = math_n(nt, "MULTIPLY", _smooth(nt, h, 0.0, 3.0), _smooth(nt, h, ph, ph * 0.45))
        return math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", core, turb), fade)
    d, X, Y, Z = _drifted(nt, build, 1.0)
    dens = math_n(nt, "MULTIPLY", d, float(JOB.get("plume_peak", PRE["plumes"]["peak"])))
    zp = math_n(nt, "SUBTRACT", 1.0, attr(nt, "unzoom", "OBJECT").outputs["Fac"])
    dens = math_n(nt, "MULTIPLY", dens, _smooth(nt, zp, *LODB["plumes_on_at"]))
    _vol_out(nt, dens, (0.9, 0.88, 0.95), 0.3, mode)
    return m


def mist_mat(name, mode, box):
    m = bpy.data.materials.new(name + ("_abs" if mode == "absorb" else ""))
    nt = m.node_tree
    nt.nodes.clear()

    def build(x, y, z):
        n = _noise(nt, _comb(nt, math_n(nt, "MULTIPLY", x, 0.02), math_n(nt, "MULTIPLY", y, 0.07),
                             math_n(nt, "MULTIPLY", z, 0.45)), 3.0, 41.0, 0.55, 0.3)
        return _smooth(nt, n, 0.40, 0.70)
    d, X, Y, Z = _drifted(nt, build, 2.0)
    fade, _gz = _edge_fade(nt)
    h = math_n(nt, "POWER", math_n(nt, "SUBTRACT", 1.0, _smooth(nt, Z, 0.0, PRE["mist"]["height"])), 1.5)
    dens = math_n(nt, "MULTIPLY", math_n(nt, "ADD", 0.25, math_n(nt, "MULTIPLY", d, 0.75)),
                  math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", h, fade), PRE["mist"]["peak"] * MIST_K))
    _vol_out(nt, dens, MIST_COL, 0.3, mode)
    return m


def _rx(name, objs):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    for o in objs:
        c.objects.link(o)
    return c


_ms = cityfog_mat("vm_r3cityfog", "scatter")
FILL_CORE = (-340.0, 16.0, 600.0, 700.0)          # the back-haze box (the stage's media live inside it)
FILL_HAZE = float(JOB.get("back_haze", PRE["back_haze"]))
FILL_FOG = []
if JOB.get("fill"):
    _fx0, _fy0, _fx1, _fy1 = -1700.0, -1500.0, 1900.0, 1500.0
    _fm = cityfog_mat("vm_r3fillfog", "scatter", fill=True)
    _fo = vol_box("r3strata_fill", _fx0, _fy0, -2.0, _fx1, _fy1, 420.0, _fm)
    _fo["fk"] = float(JOB.get("fill_fk", 1.0))
    HET.append((_fo, _fm, cityfog_mat("vm_r3fillfog", "absorb", fill=True)))
    FILL_FOG.append(_fo)
    # the stage's back haze takes the same city-level strength in the aerial (object attribute "bhcut": 0 = r3)
    _bh = bpy.data.objects.get("vol_back_haze")
    if _bh:
        _bnt = _bh.data.materials[0].node_tree
        _vs = next(n for n in _bnt.nodes if n.type == "VOLUME_SCATTER")
        _d0 = _vs.inputs["Density"].default_value
        _cut = attr(_bnt, "bhcut", "OBJECT").outputs["Fac"]
        _bnt.links.new(math_n(_bnt, "MULTIPLY", math_n(_bnt, "SUBTRACT", 1.0, _cut), _d0), _vs.inputs["Density"])
        FILL_FOG.append(_bh)
_ob = vol_box("r3strata_cityfog", _X0, FOGP["box_y"][0], FOGP["floor"] - 8.0, _X1, FOGP["box_y"][1], FOGP["box_top"], _ms)
HET.append((_ob, _ms, cityfog_mat("vm_r3cityfog", "absorb")))
for k, (px, py, pz, lean, ph, seed) in enumerate(RULES["plumes"]):
    ms = plume_mat("vm_r3plume_%d" % k, px, py, pz, lean, ph, seed, "scatter")
    rmax = 1.2 + ph * 0.28 + 2.0
    ob = vol_box("r3strata_plume_%d" % k, px - rmax, py - rmax, pz, px + ph * lean + rmax, py + rmax, pz + ph, ms)
    HET.append((ob, ms, plume_mat("vm_r3plume_%d" % k, px, py, pz, lean, ph, seed, "absorb")))
_st = RULES["street"]
MIST_BOX = (-160.0, _st["far"] - 22.0, -0.5, 380.0, _st["near"] + 1.5, PRE["mist"]["height"] + 0.5)
_mm = mist_mat("vm_r3mist", "scatter", MIST_BOX)
_mo = vol_box("r3mist", *MIST_BOX, _mm)
HET.append((_mo, _mm, mist_mat("vm_r3mist", "absorb", MIST_BOX)))
_strata_coll = _rx("strata_receivers", [o for o, a, b in HET if o.name.startswith("r3strata")])
_mist_coll = _rx("mist_receivers", [_mo])
_beam_rx = _rx("beam_receivers", [o for o, a, b in HET])

# ------------------------------------------------------------------ rule-placed glows (all unshadowed, light-linked)
# the city glow: the street grid's bounce light, under the fog at two depths, spread across the frame
for ob, e0, grp in LIGHTS:
    if ob.name.startswith("cityglow"):
        ob.hide_render = True                   # (r2's hand-placed six are replaced by the rule below)
_cg = 0
for yy in (60.0, 160.0):
    for k, a in enumerate((0.15, 0.4, 0.62, 0.85)):
        aa = FRAME_A[0] + (FRAME_A[1] - FRAME_A[0]) * a
        x = CAM_X + aa * (yy - CAM_Y)
        lt = add_light("cityglow_r_%d" % _cg, "AREA", (x, yy, 6.0), (math.pi, 0, 0), 1.2e5 * float(JOB.get("cityglow_k", PRE["cityglow_k"])) * 0.75,
                       PAL("district_a" if (k + int(yy > 100)) % 2 == 0 else "district_b"), "sky", size=120.0, size_y=60.0)
        lt.light_linking.receiver_collection = _strata_coll
        lt.data.use_shadow = False
        _cg += 1
# the bank and wisp under-glows (rules_r3: under the densest bank spots and along the wisp)
for k, (loc, col, en) in enumerate(RULES["glows"]):
    lt = add_light("featglow_%d" % k, "AREA", loc, (math.pi, 0, 0), en * float(JOB.get("featglow_k", 1.0)), col, "sky",
                   size=90.0, size_y=60.0)
    lt.light_linking.receiver_collection = _strata_coll
    lt.data.use_shadow = False
# the mist glows: shop-front colour along the near kerb
_mg = PRE["mist"]
for k, mx in enumerate(_np.arange(-40.0, 240.0, _mg["glow_step"])):
    c = PAL(("district_a", "district_b", "accent_cool", "accent_warm")[k % 4])
    add_light("mistglow_%d" % k, "AREA", (float(mx), _st["near"] - 0.5, 0.4), (math.radians(-60), 0, 0),
              _mg["glow_w"] * MIST_K, c, "street", size=5.0, size_y=1.2).light_linking.receiver_collection = _mist_coll
# the backglow reaches the back haze only (through the tower gaps it cut the city fog into pillars)
_bg_rx = _rx("backglow_receivers", [o for o in VOLUME_OBJS if o.name == "vol_back_haze"])
for _row in LIGHTS:
    if _row[0].name.startswith("backglow"):
        _row[0].light_linking.receiver_collection = _bg_rx


# ------------------------------------------------------------------ beams (rules_r3: the K tallest non-route roofs)
def _look_rot(d):
    return Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()


for rig in RULES["beams"]:
    d = Vector(rig["dir"])
    col = rig["colour"]
    parts = [("core", rig["core"], 0.35, 0.5)] + ([("soft", rig["soft"], 1.0, 1.6)] if rig["soft"] else [])
    for part, (deg, en), blend, rad in parts:
        c_ = tuple(0.55 * v + 0.45 for v in col) if (part == "core" and rig["soft"]) else col   # hot, half-white core
        ob = add_light("beam_%s_%s" % (rig["name"], part), "SPOT", rig["origin"], _look_rot(d), en * BEAM_K, c_, "sky",
                       spot=deg, blend=blend, radius=rad)
        ob.data.use_shadow = False
        ob.light_linking.receiver_collection = _beam_rx      # full power only where the fog is
        BEAM_LIGHTS.append((ob, Vector(rig["origin"]), d.normalized(), rig["sweep"], rig["phase"]))
        tw = add_light("beam_%s_%s_haze" % (rig["name"], part), "SPOT", rig["origin"], _look_rot(d), en * BEAM_K * rig["twin"],
                       c_, "sky", spot=deg, blend=blend, radius=rad)
        tw.data.use_shadow = False
        BEAM_LIGHTS.append((tw, Vector(rig["origin"]), d.normalized(), rig["sweep"], rig["phase"]))


def set_beams(t):
    """Sweep every beam about world Z (yaw) and a little in pitch, periodic in the loop (t in s)."""
    for ob, org, d0, sweep, ph in BEAM_LIGHTS:
        a = 2 * math.pi * (t / LOOP_T + ph)
        yaw = math.radians(sweep) * math.sin(a)
        pitch = math.radians(sweep * 0.25) * math.cos(a)
        d = Matrix.Rotation(yaw, 3, "Z") @ d0
        side = d.cross(Vector((0, 0, 1)))
        if side.length > 1e-6:
            d = Matrix.Rotation(pitch, 3, side.normalized()) @ d
        ob.rotation_euler = _look_rot(d)


def set_fog_time(t):
    """Drift every medium along its wind; p = t / T, the two evaluations cross over so p = 0 and p = 1 match."""
    p = (t % LOOP_T) / LOOP_T
    for n, role, wind in DRIFT:
        if role == "o1":
            n.outputs[0].default_value = -wind * p * LOOP_T
        elif role == "o2":
            n.outputs[0].default_value = -wind * (p - 1.0) * LOOP_T
        else:
            n.outputs[0].default_value = p


build_still_streaks(RULES["street_lanes"], RULES["sky_lanes"])
set_beams(float(JOB.get("t_loop", 0.0)))
set_fog_time(float(JOB.get("t_loop", 0.0)))
print("fog_r3: city fog + %d plumes, mist, %d beam lights, %d glows, drift nodes %d" % (
    len(RULES["plumes"]), len(BEAM_LIGHTS), len(RULES["glows"]), len(DRIFT)), flush=True)
