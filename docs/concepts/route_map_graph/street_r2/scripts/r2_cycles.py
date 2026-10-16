"""Street round 2: the AAA-2 look (a copy of storyboard/scripts/m44/onecity_cycles.py, exec'd by r2_scene.py).

r2 changes (rules in r2_config.RULES_R2): kit materials (glass, panel); the sign materials (texture boards, neon shapes)
and the per-frame sign LOD by camera distance; kerb lamps at the planned lamp heads; district-coloured city glow, ground
glows and bank glows (palette.districts); a backdrop haze plane, a sky haze the beams cross, steam plumes
(atmosphere.layers); fg streak lanes on the lowered section floor (foreground.street); beams keyed by building uid.

Storyboard v3 (one continuous city): the AAA-2 look on the SAME scene (exec'd by onecity_scene.py, mode "cycles").

Only materials, lights and media change; the geometry is the mainline city exactly as the mainline look renders it:
  surfaces  the kit's per-face colour through a Principled BSDF (concrete albedo, roughness 0.55, specular 0.5);
            the ground is wet asphalt with puddles (noise-driven roughness 0.03 .. 0.3)
  emitters  neon / windows / lanes / lit panels: emission from the per-face colour (the r3 levels)
  light     a dim blue moon, unshadowed city-glow area lights under the fog, the room lights, rule-placed beams
  media     one city fog field (r3 recipe, scaled to the mainline units: the city is ~3x smaller than the old street
            set): dense low, thinning with altitude, broken into banks by low-frequency noise; plus a thin back haze
  passes    Combined (with the media), Emission, Denoising Albedo, Depth -> npy, and the anchors post_aaa.finish reads
The beams are placed by the r3 rule on this city: the tallest roofs within reach of the street, off the route columns.
"""
import time as _tm
import numpy as _np

OCJ = JOB_OC
LKA = OCJ.get("look", {})
SCALE = float(LKA.get("unit_scale", 3.0))       # density per BU x this (the mainline city is ~3x smaller)


def _attr(nt, name):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_name = name
    return n


def _surf_mat(name, rough=0.55, alb=0.85, spec=0.5, emit_k=0.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    a = _attr(nt, "col")
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    mul.inputs["Scale"].default_value = alb
    nt.links.new(a.outputs["Color"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = rough
    try:
        bs.inputs["Specular IOR Level"].default_value = spec
    except KeyError:
        pass
    if emit_k > 0:
        nt.links.new(a.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = emit_k
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def _emit_mat(name, k):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(_attr(nt, "col").outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = k
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def _wet_mat():
    m = bpy.data.materials.new("oc_wet")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    a = _attr(nt, "col")
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    mul.inputs["Scale"].default_value = 0.55
    nt.links.new(a.outputs["Color"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bs.inputs["Base Color"])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.09 * SCALE
    nz.inputs["Detail"].default_value = 5.0
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.45
    mr.inputs["From Max"].default_value = 0.6
    mr.inputs["To Min"].default_value = 0.3
    mr.inputs["To Max"].default_value = 0.03
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], bs.inputs["Roughness"])
    try:
        bs.inputs["Specular IOR Level"].default_value = 0.7
    except KeyError:
        pass
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


SURF = _surf_mat("oc_surf")
GROUND_SKIP = "oc_wet"
LITA = _surf_mat("oc_lit", emit_k=0.42)
WET = _wet_mat()
NEONA = _emit_mat("oc_neon", float(LKA.get("neon", 3.2)))
WINA = _emit_mat("oc_win", float(LKA.get("win", 1.6)))
PANA = _emit_mat("oc_panel", float(LKA.get("panel", 4.0)))
GLANEA = _emit_mat("oc_glane", float(LKA.get("neon", 3.2)) * float(LKA.get("lane_dim", 0.5)))
_emitters = {m.name for m in bpy.data.materials if m.name.startswith(("neon", "win", "sign", "glow", "eye", "anim"))}
_emitters |= {NEONM.name, WINM.name}
for o in [o for o in scene.objects if o.type in ("MESH", "FONT")]:
    for si, m in enumerate(o.data.materials):
        if m is None:
            continue
        if o is groundo:
            o.data.materials[si] = WET
        elif o is RPAN_OBJ:
            o.data.materials[si] = PANA
        elif o is glaneo:
            o.data.materials[si] = GLANEA
        elif m is WINM or m.name.startswith("win"):
            o.data.materials[si] = WINA
        elif m.name in _emitters or m.name.startswith(("neon", "sign", "Neon")):
            o.data.materials[si] = NEONA
        elif m is LITM:
            o.data.materials[si] = LITA
        else:
            o.data.materials[si] = SURF
for o in scene.objects:
    if o.type == "LIGHT":
        o.hide_render = True
        o["oc_off"] = True
for _m in (SURF, LITA, NEONA, WINA, PANA, GLANEA):
    section(_m)


def _kit_mat(name, rough, metal, alb, spec=0.5):
    m = _surf_mat(name, rough=rough, alb=alb, spec=spec)
    bs = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bs.inputs["Metallic"].default_value = metal
    section(m)
    return m


GLASSM = _kit_mat("r2_glass", 0.12, 0.2, 1.0, spec=1.0)
PANELM = _kit_mat("r2_panel", 0.45, 0.3, 1.0)
DARKM = _surf_mat("r2_dark", rough=0.45, alb=1.0)               # lamp posts: not sectioned (they stand on the kerb)
LHEADM = _emit_mat("r2_lamphead", 8.0)
SGN = float(LKA.get("sign_k", 1.0))


def _tex_mat(name, path, k, additive=False):
    m = bpy.data.materials.new(name)
    nt_ = m.node_tree
    nt_.nodes.clear()
    o_ = nt_.nodes.new("ShaderNodeOutputMaterial")
    tx = nt_.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path)
    tx.interpolation = "Cubic"
    em_ = nt_.nodes.new("ShaderNodeEmission")
    nt_.links.new(tx.outputs["Color"], em_.inputs["Color"])
    em_.inputs["Strength"].default_value = k
    if additive:
        tr_ = nt_.nodes.new("ShaderNodeBsdfTransparent")
        ad_ = nt_.nodes.new("ShaderNodeAddShader")
        nt_.links.new(tr_.outputs[0], ad_.inputs[0])
        nt_.links.new(em_.outputs[0], ad_.inputs[1])
        nt_.links.new(ad_.outputs[0], o_.inputs["Surface"])
    else:
        # a lit board: emission plus a little glossy so the rain-wet face catches the street
        gl_ = nt_.nodes.new("ShaderNodeBsdfGlossy")
        gl_.inputs["Roughness"].default_value = 0.15
        gl_.inputs["Color"].default_value = (0.05, 0.05, 0.06, 1)
        ad_ = nt_.nodes.new("ShaderNodeAddShader")
        nt_.links.new(gl_.outputs[0], ad_.inputs[0])
        nt_.links.new(em_.outputs[0], ad_.inputs[1])
        nt_.links.new(ad_.outputs[0], o_.inputs["Surface"])
    return m


_SDIR = OCJ["signs_dir"]
for o in scene.objects:
    n_ = o.name
    if o.type != "MESH":
        continue
    if n_.endswith("_glass") or n_.startswith("city_glass"):
        o.data.materials[0] = GLASSM
    elif n_.endswith("_panel") or n_.startswith("city_panel"):
        o.data.materials[0] = PANELM
    elif n_.startswith("r2_lamp_post"):
        o.data.materials[0] = DARKM
    elif n_.startswith("r2_lamp_head"):
        o.data.materials[0] = LHEADM
SHAPE_MATS = {}
for so in SIGN_OBJS:
    sg = so["sign"]
    add_ = sg["tex"]["style"] == "holo"
    so["t2"][0].data.materials.append(_tex_mat("r2s_" + sg["id"], os.path.join(_SDIR, sg["id"] + ".png"), sg["emit"] * SGN, add_))
    for o in so["t1"] + so["t3"][:1]:
        k_ = round(sg["emit"] * (0.8 if o in so["t1"] else 1.2), 2)
        if k_ not in SHAPE_MATS:
            SHAPE_MATS[k_] = _emit_mat("r2_shape_%.2f" % k_, k_ * SGN)
        o.data.materials[0] = SHAPE_MATS[k_]
    so["t2"][1].data.materials[0] = DARKM
    so["t3"][1].data.materials[0] = DARKM
if PLAN.get("mega"):
    for o in MEGA_OBJS:
        if o.name.startswith("r2_mega_board"):
            o.data.materials.append(_tex_mat("r2_mega_tex", os.path.join(_SDIR, "mega.png"), PLAN["mega"]["emit"] * SGN,
                                             PLAN["mega"]["kind"] == "holo"))
        elif o.name.startswith("r2_mega_neon"):
            o.data.materials[0] = _emit_mat("r2_mega_neon", PLAN["mega"]["emit"] * SGN)
        else:
            o.data.materials[0] = SURF

# ------------------------------------------------------------------ world, moon, city glow, room lights
wd = bpy.data.worlds.new("oc_world")
scene.world = wd
_bg = next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND")
_bg.inputs["Color"].default_value = (0.006, 0.006, 0.014, 1)
_bg.inputs["Strength"].default_value = 1.0


def _light(name, kind, loc, rot, energy, col, size=None, spot=None, blend=0.3):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = col
    if kind == "AREA" and size:
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
        ld.shadow_soft_size = 0.2
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    return ob


_light("oc_moon", "SUN", (0, 0, 100), (math.radians(40), 0, math.radians(30)), 0.05, (0.55, 0.62, 1.0))
st = OCJ["street"]
sx0, sx1 = sorted((st["a"][0], st["c"][0]))
_STOPS = PLAN["bank_stops"]


def _stop_col(u):
    """palette.districts: the district colour of the bank stop nearest along the street."""
    return tuple(min(_STOPS, key=lambda s_: abs(s_["u"] - u))["col"])
sy = st["a"][1]
cglow = []
for k, xx in enumerate(_np.linspace(sx0 - 120, sx1 + 120, 6)):
    for yy in (sy + 40, sy + 120, sy - 60):
        c = _stop_col(float(xx)) if (k + int(yy)) % 2 else ((1.0, 0.3, 0.7) if k % 2 else (0.25, 0.75, 1.0))
        cglow.append(_light("oc_cityglow_%d_%d" % (k, int(yy)), "AREA", (float(xx), float(yy), 2.0), (math.pi, 0, 0),
                            float(LKA.get("cityglow", 2.5e3)), c, size=(45, 30)))
for (i, p, tl, w, dep) in ROOM_LIGHTS:
    _light("oc_room_" + i, "AREA", p, (math.pi, 0, 0), float(LKA.get("room", 60.0)) * w, tl, size=(max(0.5, w - 0.4), dep * 0.8))

# street lights and the neon wash on the netrun street's frontage (rules, from the derived street):
#  - lamps along both kerbs every lamp_step BU (warm, the r3 mist glows' role);
#  - each route column's street face washed from across the street in the district palette (a / b alternating), the
#    light the AAA street got from its shopfronts and signs
_nrm = OCJ.get("nrm", [0.0, 1.0])
_ax0 = abs(_nrm[1]) > 0.5
_cline = st["a"][1] if _ax0 else st["a"][0]
_u0, _u1 = (sx0, sx1) if _ax0 else sorted((st["a"][1], st["c"][1]))
_k = 0
for (pos, c) in LAMP_HEADS:
    _ld = _light("oc_lamp_%d" % _k, "POINT", pos, (0, 0, 0), float(LKA.get("lamp", 25.0)), c)
    _ld.data.shadow_soft_size = 0.25
    _k += 1
# v3-r3 (art director: the foreground slabs read as a black checkerboard): street-level glows among the plinths on the
# camera side. Jittered on a ground_glow_step grid from the near kerb out to ground_glow_depth, palette colours (the
# warm sodium of the lamps and the district pair), low over the wet plinth tops: they pool on the wet tops (the puddle
# highlights) and light the ground bank from inside, so the slabs sink into coloured haze instead of a hard grid
_gr = random.Random(7719)
_gs = float(LKA.get("ground_glow_step", 9.0))
_gsign = (_nrm[1] if _ax0 else _nrm[0])
_gcols = ((1.0, 0.62, 0.3), (1.0, 0.2, 0.62), (0.2, 0.78, 1.0), (1.0, 0.62, 0.3), (0.62, 0.38, 1.0)) + tuple(
    tuple(s_["col"]) for s_ in _STOPS if s_["district"])[:3]
_k = 0
for uu in _np.arange(_u0 - 30.0, _u1 + 30.0, _gs):
    for dd in _np.arange(float(OCJ.get("plinth_off", 4.2)) + 2.0, float(LKA.get("ground_glow_depth", 60.0)), _gs * 0.8):
        if _gr.random() > float(LKA.get("ground_glow_p", 0.55)):
            continue
        pu = float(uu) + _gr.uniform(-0.4, 0.4) * _gs
        pd = float(dd) + _gr.uniform(-0.3, 0.3) * _gs
        pos = (pu, _cline - _gsign * pd, 0.9) if _ax0 else (_cline - _gsign * pd, pu, 0.9)
        _ld = _light("oc_gglow_%d" % _k, "POINT", pos, (0, 0, 0), float(LKA.get("ground_lamp", 40.0)) * _gr.uniform(0.6, 1.2),
                     _gcols[_gr.randrange(len(_gcols))])
        _ld.data.shadow_soft_size = 0.6
        _k += 1
print("ONECITY ground glows", _k, flush=True)
_cols = {}
for i, r in OCJ["rooms"].items():
    _cols.setdefault(r["bld"], []).append(r)
for k, (bk, rs) in enumerate(sorted(_cols.items())):
    f0 = rs[0]["front"]
    us = [p[0 if _ax0 else 1] for r in rs for p in r["front"]]
    face = f0[0][1] if _ax0 else f0[0][0]
    top = max(p[2] for r in rs for p in r["front"])
    c = (1.0, 0.16, 0.6) if k % 2 else (0.16, 0.8, 1.0)
    wmid = (min(us) + max(us)) / 2
    d = -3.5 * (_nrm[1] if _ax0 else _nrm[0])
    pos = (wmid, face + d, 0.4) if _ax0 else (face + d, wmid, 0.4)
    aim = Vector((0, _nrm[1], 0.55) if _ax0 else (_nrm[0], 0, 0.55)).normalized()
    _light("oc_wash_%d" % k, "SPOT", pos, aim.to_track_quat("-Z", "Y").to_euler(), float(LKA.get("wash", 120.0)), c,
           spot=70, blend=0.8)

# r2 streets.light: an uplight wash on every non-route frontage face (its trim colour), so the street front reads as
# lit volumes, not black boxes
_rset = set(OCJ["route_uids"])
for k_, ff in enumerate(PLAN.get("front_faces", [])):
    if ff["uid"] in _rset:
        continue
    wmid = (ff["u0"] + ff["u1"]) / 2
    d = ff["out"] * 2.6
    pos = (wmid, ff["face"] + d, 0.3) if _ax0 else (ff["face"] + d, wmid, 0.3)
    aim = Vector((0, -ff["out"], 1.4) if _ax0 else (-ff["out"], 0, 1.4)).normalized()
    _light("oc_fwash_%d" % k_, "SPOT", pos, aim.to_track_quat("-Z", "Y").to_euler(), float(LKA.get("facade_wash", 700.0)),
           tuple(ff["col"]), spot=60, blend=0.9)

for k_, ff in enumerate(PLAN.get("near_faces", [])):
    w_ = ff["u1"] - ff["u0"]
    h_ = min(12.0, ff["top"])
    wmid = (ff["u0"] + ff["u1"]) / 2
    pos = (wmid, ff["face"] + ff["out"] * 0.3, h_ / 2) if _ax0 else (ff["face"] + ff["out"] * 0.3, wmid, h_ / 2)
    aim = Vector((0, ff["out"], 0) if _ax0 else (ff["out"], 0, 0))
    ob_ = _light("oc_spill_%d" % k_, "AREA", pos, aim.to_track_quat("-Z", "Y").to_euler(),
                 float(LKA.get("section_spill", 14.0)) * w_ * h_, tuple(ff["col"]), size=(w_, h_))
    ob_.visible_camera = False
    ob_.visible_glossy = False

# heights the atmosphere scales to (v3-r2: the frontage was raised by the layout rules; the r3 numbers were for the
# old street set): H_FRONT the median roof of the frontage across the netrun street, H_SKY the 90th percentile roof
# within beam reach behind it
_far = lambda c: (c[1] - sy) * _nrm[1] if abs(_nrm[1]) > 0.5 else (c[0] - st["a"][0]) * _nrm[0]
_mid = ((sx0 + sx1) / 2, sy)
_fr = sorted(zt for (c, q, zt, terr, ts, key) in BUILT if 0 < _far(c) < 18 and sx0 - 10 < c[0] < sx1 + 10)
_sk = sorted(zt for (c, q, zt, terr, ts, key) in BUILT if 18 < _far(c) < 160 and math.hypot(c[0] - _mid[0], c[1] - _mid[1]) < 180)
H_FRONT = _fr[len(_fr) // 2] if _fr else 14.0
H_SKY = _sk[int(len(_sk) * 0.9)] if _sk else 2.2 * H_FRONT
print("ONECITY heights front %.1f sky %.1f" % (H_FRONT, H_SKY), flush=True)

# beams (the r3 rule on this city): the K tallest roofs behind the netrun street that clear the frontage by
# beam_rise x H_FRONT (so the beam is seen rising over it), within reach, not a route column, min spacing 45 BU.
# Each rig is a soft cone and a core (r3 hero_soft / hero_core) linked to the fog only (no twin: the haze is in the
# same fog object); lean from the preset ranges by a hash of the building key (deterministic).
_rk = set(OCJ["route_uids"]) | ({PLAN["mega"]["key"]} if PLAN.get("mega") else set())


def _kh(uid, mul):
    return (sum(ord(ch) * (k + 1) for k, ch in enumerate(uid)) * mul) % 1000 / 1000.0
_cands = []
for (c, q, zt, terr, ts, key) in BUILT:
    if key in _rk or zt < float(LKA.get("beam_rise", 1.35)) * H_FRONT:
        continue
    d = math.hypot(c[0] - _mid[0], c[1] - _mid[1])
    if 25 < d < 170 and _far(c) > 12:
        _cands.append((zt, c, key))
_cands.sort(key=lambda v: (-v[0], v[2]))
_pick = []
for zt, c, key in _cands:
    if all(math.hypot(c[0] - p[1][0], c[1] - p[1][1]) > 45 for p in _pick):
        _pick.append((zt, c, key))
    if len(_pick) >= int(LKA.get("beams", 6)):
        break
_PAL = {"district_a": (1.0, 0.16, 0.6), "district_b": (0.16, 0.8, 1.0), "accent_warm": (1.0, 0.58, 0.18),
        "accent_cool": (0.62, 0.38, 1.0)}
_BCOL = ["district_a", "district_b", "accent_warm", "district_b", "district_a", "accent_cool"]
BEAMS = []
BEAM_SHAFTS = []
_bE = float(LKA.get("beam", 2.0e7))


def _beam_mat(name, col, k_emit):
    """v3-r3 (art director: no solid rods): the visible shaft is an emissive cone with a radial AND an axial falloff.
    Radial: s = the offset from the axis in units of the local radius, from the view facing (x = |N.V|, s^2 = 1 - x^2);
    a narrow hot core (gaussian, sigma beam_core_s) over a wide soft skirt (gaussian, sigma beam_soft_s, x (1 - s^2) so
    the silhouette is never an edge). Axial: t = 0 at the source .. 1 at the far end; brightest at the source (e-fold
    beam_efold), gone by beam_fade (0.6) of the length, with a short fade-in so the open start is not a disc. A slow
    world noise breaks it where the haze thins. Transparent + emission: it adds light to the ray and never occludes."""
    m = bpy.data.materials.new(name)
    t_ = m.node_tree
    t_.nodes.clear()
    o_ = t_.nodes.new("ShaderNodeOutputMaterial")

    def M(op, a, b=None):
        n = t_.nodes.new("ShaderNodeMath")
        n.operation = op
        for idx, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[idx].default_value = v
            else:
                t_.links.new(v, n.inputs[idx])
        return n.outputs[0]

    def SS(v, a, b):
        mr = t_.nodes.new("ShaderNodeMapRange")
        mr.interpolation_type = "SMOOTHSTEP"
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = a, b
        t_.links.new(v, mr.inputs["Value"])
        return mr.outputs[0]
    lw = t_.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    x = M("SUBTRACT", 1.0, lw.outputs["Facing"])
    s2 = M("MAXIMUM", M("SUBTRACT", 1.0, M("MULTIPLY", x, x)), 0.0)
    sc, ss = float(LKA.get("beam_core_s", 0.13)), float(LKA.get("beam_soft_s", 0.42))
    core = M("EXPONENT", M("MULTIPLY", s2, -1.0 / (2 * sc * sc)))
    soft = M("MULTIPLY", M("EXPONENT", M("MULTIPLY", s2, -1.0 / (2 * ss * ss))), M("SUBTRACT", 1.0, s2))
    rad = M("ADD", M("MULTIPLY", core, float(LKA.get("beam_core_w", 1.0))), M("MULTIPLY", soft, float(LKA.get("beam_soft_w", 0.3))))
    tc = t_.nodes.new("ShaderNodeTexCoord")
    sp = t_.nodes.new("ShaderNodeSeparateXYZ")
    t_.links.new(tc.outputs["Object"], sp.inputs[0])
    t = sp.outputs["Z"]                                   # the mesh is built with its length = 1 in object space
    fade = float(LKA.get("beam_fade", 0.6))
    ax = M("MULTIPLY", M("EXPONENT", M("MULTIPLY", t, -1.0 / float(LKA.get("beam_efold", 0.22)))),
           M("SUBTRACT", 1.0, SS(t, fade * 0.45, fade)))
    ax = M("MULTIPLY", ax, SS(t, 0.0, 0.025))
    gz = t_.nodes.new("ShaderNodeNewGeometry")
    vm = t_.nodes.new("ShaderNodeVectorMath")
    vm.operation = "SCALE"
    vm.inputs["Scale"].default_value = 0.09
    t_.links.new(gz.outputs["Position"], vm.inputs[0])
    nz = t_.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Detail"].default_value = 2.0
    t_.links.new(vm.outputs[0], nz.inputs["Vector"])
    brk = M("ADD", 0.55, M("MULTIPLY", SS(nz.outputs["Fac"], 0.35, 0.65), 0.45))
    stren = M("MULTIPLY", M("MULTIPLY", M("MULTIPLY", rad, ax), brk), k_emit)
    em = t_.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (col[0], col[1], col[2], 1)
    t_.links.new(stren, em.inputs["Strength"])
    eh = t_.nodes.new("ShaderNodeEmission")                  # the core runs hotter (toward white)
    eh.inputs["Color"].default_value = (min(1, col[0] * 0.4 + 0.6), min(1, col[1] * 0.4 + 0.6), min(1, col[2] * 0.4 + 0.6), 1)
    t_.links.new(M("MULTIPLY", M("MULTIPLY", stren, core), float(LKA.get("beam_hot", 0.5))), eh.inputs["Strength"])
    tr = t_.nodes.new("ShaderNodeBsdfTransparent")
    ad = t_.nodes.new("ShaderNodeAddShader")
    t_.links.new(tr.outputs[0], ad.inputs[0])
    t_.links.new(em.outputs[0], ad.inputs[1])
    ad2 = t_.nodes.new("ShaderNodeAddShader")
    t_.links.new(ad.outputs[0], ad2.inputs[0])
    t_.links.new(eh.outputs[0], ad2.inputs[1])
    t_.links.new(ad2.outputs[0], o_.inputs["Surface"])
    return m


def _beam_shaft(name, org, dirv, length, half_deg, mat, seg=48):
    me_ = bpy.data.meshes.new(name)
    b_ = _bm.new()
    r0, r1 = 0.18 / length, math.tan(math.radians(half_deg))      # object space: length 1 (scaled), a small start radius
    lo_ = [b_.verts.new((r0 * math.cos(2 * math.pi * i / seg), r0 * math.sin(2 * math.pi * i / seg), 0.0)) for i in range(seg)]
    hi_ = [b_.verts.new((r1 * math.cos(2 * math.pi * i / seg), r1 * math.sin(2 * math.pi * i / seg), 1.0)) for i in range(seg)]
    for i in range(seg):
        j = (i + 1) % seg
        f_ = b_.faces.new((lo_[i], lo_[j], hi_[j], hi_[i]))
        f_.smooth = True
    b_.to_mesh(me_)
    b_.free()
    me_.materials.append(mat)
    ob_ = bpy.data.objects.new(name, me_)
    ob_.location = org
    ob_.rotation_euler = Vector(dirv).normalized().to_track_quat("Z", "Y").to_euler()
    ob_.scale = (length, length, length)
    for v_ in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
        setattr(ob_, v_, False)                            # seen by the camera only: the spot below lights the haze
    scene.collection.objects.link(ob_)
    return ob_


_bL = float(LKA.get("beam_len", 3.5)) * H_FRONT
for k, (zt, c, key) in enumerate(_pick):
    col = _PAL[_BCOL[k % len(_BCOL)]]
    hh = _kh(key, 2654435761)
    lx = 0.12 + 0.30 * hh
    ly = 0.18 + 0.12 * _kh(key, 40503)
    lean = (lx if c[0] > _mid[0] else -lx, ly * (1 if abs(_nrm[1]) > 0.5 else 0) + 0.0, 1.0)
    rot = Vector(lean).normalized().to_track_quat("-Z", "Y").to_euler()
    org = (c[0], c[1], zt + 0.5)
    # the haze light: one wide, fully soft spot, linked to the fog only, so the air around the shaft glows (strongest
    # near the source by the inverse square); the shaft itself is the emissive cone (v3-r3: no core spot, no rod)
    ob = _light("oc_beam_%d_haze" % k, "SPOT", org, rot, _bE, col, spot=float(LKA.get("beam_cone", 30.0)), blend=1.0)
    ob.data.use_shadow = False
    BEAMS.append(ob)
    BEAM_SHAFTS.append(_beam_shaft("oc_beam_%d_shaft" % k, org, lean, _bL, float(LKA.get("beam_half", 6.0)),
                                   _beam_mat("oc_beam_%d_mat" % k, col, float(LKA.get("beam_emit", 3.0)))))
print("ONECITY beams", [(round(c[0]), round(c[1]), round(zt)) for zt, c, key in _pick], "len %.1f" % _bL, flush=True)

# ------------------------------------------------------------------ the city fog (r3 recipe, mainline units)
fm = bpy.data.materials.new("oc_fog")
nt = fm.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
vs = nt.nodes.new("ShaderNodeVolumeScatter")
vs.inputs["Color"].default_value = tuple(LKA.get("scatter", (0.85, 0.80, 1.0))) + (1,)
vs.inputs["Anisotropy"].default_value = 0.45
geo = nt.nodes.new("ShaderNodeNewGeometry")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(geo.outputs["Position"], sep.inputs[0])


def _m(op, a, b):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for idx, v in enumerate((a, b)):
        if isinstance(v, (int, float)):
            n.inputs[idx].default_value = v
        else:
            nt.links.new(v, n.inputs[idx])
    return n.outputs[0]


def _noise(scale_xyz, det, w):
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "MULTIPLY"
    sc.inputs[1].default_value = scale_xyz
    nt.links.new(geo.outputs["Position"], sc.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["W"].default_value = w
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = det
    nt.links.new(sc.outputs[0], nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _smooth(v, a, b):
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = a
    mr.inputs["From Max"].default_value = b
    nt.links.new(v, mr.inputs["Value"])
    return mr.outputs[0]


S = SCALE
Z = sep.outputs["Z"]
HF = H_FRONT
# r3 recipe on the warped height coordinate, every height in units of the frontage (H_FRONT):
#  body    dense low, thinning above 0.5 H with an e-folding of H_SKY (r3: 30 BU / 55 BU on its street set)
#  strata  layers ~0.42 H apart on a height coordinate warped by a broad noise (+-0.22 H) and tilted along the street,
#          so they bend, merge and split (r3 warp / wave / tilt); a broad octave (banks) and a fine one (wisps) mixed
#          0.62 / 0.38 and remapped (0.47, 0.64): layers fade in and out, never full width (clumps)
#  wisp    one thin layer just over the frontage roofs (1.08 H), the skyline-relative wisp of r3
#  where   behind the street face only (far side, r3 box_y): the camera's corridor and the rooms stay clear;
#          the low floor keeps the wet street readable (r3 floor relative to the rooms)
warp = _m("MULTIPLY", _m("SUBTRACT", _noise((0.006 * S, 0.010 * S, 0.02 * S), 2.0, 7.7), 0.5), 0.44 * HF)
tilt = _m("MULTIPLY", sep.outputs["X"], 0.07 * (1 if abs(_nrm[1]) > 0.5 else 0))
zw = _m("ADD", _m("ADD", Z, warp), tilt)
hf = _m("EXPONENT", _m("MULTIPLY", _m("MAXIMUM", _m("SUBTRACT", Z, 0.5 * HF), 0.0), -1.0 / max(H_SKY, 1.0)), 0)
lay_s = _m("ADD", 0.5, _m("MULTIPLY", _m("SINE", _m("MULTIPLY", zw, 2 * math.pi / (0.42 * HF)), 0), 0.5))
banks = _noise((0.004 * S, 0.012 * S, 0.075 * S), 3.0, 3.1)
wisps = _noise((0.009 * S, 0.02 * S, 0.33 * S), 2.0, 5.3)
lay_n = _m("ADD", _m("MULTIPLY", banks, 0.62), _m("MULTIPLY", wisps, 0.38))
lay = _m("MULTIPLY", _smooth(lay_n, 0.47, 0.64), _smooth(lay_s, 0.35, 0.95))
clumps = _smooth(_noise((0.0075 * S, 0.014 * S, 0.022 * S), 2.0, 14.1), 0.40, 0.62)
wisp = _m("SUBTRACT", 1.0, _smooth(_m("ABSOLUTE", _m("SUBTRACT", zw, 1.08 * HF), 0), 0.0, 0.12 * HF))
wisp = _m("MULTIPLY", _m("MULTIPLY", wisp, _smooth(wisps, 0.42, 0.6)), float(LKA.get("wisp_k", 0.7)))
if abs(_nrm[1]) > 0.5:
    _fd = _m("MULTIPLY", _m("SUBTRACT", sep.outputs["Y"], sy), _nrm[1])
else:
    _fd = _m("MULTIPLY", _m("SUBTRACT", sep.outputs["X"], st["a"][0]), _nrm[0])
where = _smooth(_fd, float(LKA.get("fog_front", 7.0)), float(LKA.get("fog_front", 7.0)) + 10.0)
floor_ = _smooth(Z, 0.08 * HF, 0.3 * HF)
body = _m("ADD", _m("MULTIPLY", clumps, 0.08), _m("MULTIPLY", lay, clumps))
body = _m("MAXIMUM", body, wisp)
dens = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", body, hf), floor_), where), float(LKA.get("fog_peak", 0.021)) * S)
# v3-r2c (art director): visible banks.
#  ground bank  a low layer (thick to gb_top x 0.2, gone at gb_top) over the cut slabs on the camera side, from the
#               near kerb outward; broken by a low-frequency noise so it reads as banks, never a flat sheet
#  mid banks    low banks between the building rows behind the frontage (0.05 .. 0.8 H), banks-octave noise
_kerb = float(OCJ.get("plinth_off", 4.2))
gb_side = _smooth(_m("MULTIPLY", _fd, -1.0), _kerb + 0.5, _kerb + 4.0)
_gt = float(LKA.get("gb_top", 2.2))
gb_z = _m("SUBTRACT", 1.0, _smooth(Z, 0.2 * _gt, _gt))
gb_n = _smooth(_noise((0.018 * S, 0.03 * S, 0.25 * S), 2.0, 21.3), 0.35, 0.68)
gb = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", gb_side, gb_z), _m("ADD", 0.25, _m("MULTIPLY", gb_n, 0.75))),
        float(LKA.get("ground_bank", 0.05)) * S)
mb_z = _m("MULTIPLY", _smooth(Z, 0.05 * HF, 0.15 * HF), _m("SUBTRACT", 1.0, _smooth(Z, 0.5 * HF, 0.8 * HF)))
mb = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", mb_z, where), _smooth(banks, 0.42, 0.62)), float(LKA.get("mid_bank", 0.03)) * S)
dens = _m("ADD", dens, mb)
# r2 atmosphere.layers: a backdrop haze plane behind the street (ramps in over back_haze_band BU behind the face, thins
# above back_haze_top x H_SKY), so the backdrop towers sit in a lit haze and the beams cross fog
_bh0, _bh1 = LKA.get("back_haze_band", (30.0, 120.0))
_bh = _m("MULTIPLY", _m("MULTIPLY", _smooth(_fd, float(_bh0), float(_bh1)),
                       _m("EXPONENT", _m("MULTIPLY", Z, -1.0 / max(1.0, float(LKA.get("back_haze_top", 2.4)) * H_SKY)), 0)),
         float(LKA.get("back_haze", 0.0)) * S)
dens = _m("ADD", dens, _bh)
dens_all = _m("ADD", dens, gb)
nt.links.new(dens_all, vs.inputs["Density"])
haze = nt.nodes.new("ShaderNodeVolumeScatter")
haze.inputs["Density"].default_value = float(LKA.get("haze", 0.0016)) * S
_hz = _m("MULTIPLY", _m("EXPONENT", _m("MULTIPLY", _m("MAXIMUM", _m("SUBTRACT", Z, H_SKY), 0.0), -1.0 / float(LKA.get("haze_efold", 40.0))), 0),
         float(LKA.get("haze", 0.0016)) * S)
nt.links.new(_hz, haze.inputs["Density"])
haze.inputs["Anisotropy"].default_value = 0.2
haze.inputs["Color"].default_value = tuple(LKA.get("scatter", (0.82, 0.78, 1.0))) + (1,)
add = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(vs.outputs[0], add.inputs[0])
nt.links.new(haze.outputs[0], add.inputs[1])
# r3 underlight: the strata glow faintly from below in the palette by height (the city's light caught in the layers;
# r3 underlight ramp + underlight_k), so they read against the night sky without lifting the whole frame
ramp = nt.nodes.new("ShaderNodeValToRGB")
_el = ramp.color_ramp.elements
_el[0].position, _el[0].color = 0.0, (1.0, 0.16, 0.6, 1)
_UL = [tuple(c_) for c_ in PLAN.get("underlight", [])] or [(1.0, 0.16, 0.6), (0.62, 0.38, 1.0)]
_el[1].position, _el[1].color = 1.0, _UL[-1] + (1,)
for _p, _c in ((0.3, (0.16, 0.8, 1.0, 1)), (0.55, _UL[0] + (1,)), (0.8, (0.16, 0.8, 1.0, 1))):
    _e = _el.new(_p)
    _e.color = _c
nt.links.new(_m("DIVIDE", zw, 2.2 * HF), ramp.inputs["Fac"])
emv = nt.nodes.new("ShaderNodeEmission")
nt.links.new(ramp.outputs["Color"], emv.inputs["Color"])
nt.links.new(_m("MULTIPLY", dens, float(LKA.get("underlight_k", 0.06))), emv.inputs["Strength"])
gramp = nt.nodes.new("ShaderNodeValToRGB")
_gl = gramp.color_ramp.elements
_gl[0].position, _gl[0].color = 0.3, (1.0, 0.16, 0.6, 1)
_gl[1].position, _gl[1].color = 0.7, (0.16, 0.8, 1.0, 1)
nt.links.new(_noise((0.012 * S, 0.012 * S, 0.05 * S), 1.0, 33.0), gramp.inputs["Fac"])
gem = nt.nodes.new("ShaderNodeEmission")
nt.links.new(gramp.outputs["Color"], gem.inputs["Color"])
nt.links.new(_m("MULTIPLY", gb, float(LKA.get("ground_glow", 0.35))), gem.inputs["Strength"])
add3 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(emv.outputs[0], add3.inputs[0])
nt.links.new(gem.outputs[0], add3.inputs[1])
emv = add3
# v3-r3: the mid-ground banks pick up the neon of the rows around them (the district pair and the warm accent, by a
# slow noise along the street, so a bank reads pink in one place and cyan in the next)
mramp = nt.nodes.new("ShaderNodeValToRGB")
_ml = mramp.color_ramp.elements
_ml[0].position, _ml[0].color = 0.32, (0.16, 0.8, 1.0, 1)
_ml[1].position, _ml[1].color = 0.68, (1.0, 0.16, 0.6, 1)
_bu0, _bu1 = _STOPS[0]["u"], _STOPS[-1]["u"]
_ml[0].position, _ml[0].color = 0.0, tuple(_STOPS[0]["col"]) + (1,)
_ml[1].position, _ml[1].color = 1.0, tuple(_STOPS[-1]["col"]) + (1,)
for _s in _STOPS[1:-1]:
    _e = _ml.new((_s["u"] - _bu0) / (_bu1 - _bu0))
    _e.color = tuple(_s["col"]) + (1,)
_mrel = sep.outputs["X"] if _ax0 else sep.outputs["Y"]
_mw = _m("ADD", _m("DIVIDE", _m("SUBTRACT", _mrel, _bu0), _bu1 - _bu0),
         _m("MULTIPLY", _m("SUBTRACT", _noise((0.010 * S, 0.016 * S, 0.04 * S), 1.0, 41.0), 0.5), 0.08))
nt.links.new(_mw, mramp.inputs["Fac"])
mem = nt.nodes.new("ShaderNodeEmission")
nt.links.new(mramp.outputs["Color"], mem.inputs["Color"])
nt.links.new(_m("MULTIPLY", mb, float(LKA.get("mid_glow", 0.1))), mem.inputs["Strength"])
add4 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(emv.outputs[0], add4.inputs[0])
nt.links.new(mem.outputs[0], add4.inputs[1])
emv = add4
add2 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(add.outputs[0], add2.inputs[0])
nt.links.new(emv.outputs[0], add2.inputs[1])
nt.links.new(add2.outputs[0], out.inputs["Volume"])
me = bpy.data.meshes.new("oc_fog")
_b = _bm.new()
_bm.ops.create_cube(_b, size=1.0)
_b.to_mesh(me)
_b.free()
fog = bpy.data.objects.new("oc_fog", me)
FX0, FX1, FY0, FY1, FZ1 = -700.0, 900.0, -700.0, 900.0, max(240.0 / S, 2.5 * H_SKY)
fog.location = ((FX0 + FX1) / 2, (FY0 + FY1) / 2, (FZ1 - 0.5) / 2)
fog.scale = (FX1 - FX0, FY1 - FY0, FZ1 + 0.5)
me.materials.append(fm)
scene.collection.objects.link(fog)
_rx = bpy.data.collections.new("oc_fog_rx")
scene.collection.children.link(_rx)
_rx.objects.link(fog)
for o in BEAMS:
    o.light_linking.receiver_collection = _rx      # r3: the full-power beam lights the media only
for o in cglow:
    o.data.use_shadow = False
    o.light_linking.receiver_collection = _rx      # the city glow lights the fog only (r3: it cut pillars otherwise)

# ------------------------------------------------------------------ render setup and the frames
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "HIP"
try:
    prefs.use_hiprt = False
except Exception:
    pass
prefs.refresh_devices()
for d in prefs.devices:
    d.use = d.type == "HIP"
scene.render.engine = "CYCLES"
cy = scene.cycles
cy.device = "GPU"
cy.samples = int(OCJ.get("spp", 32))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.use_denoising = True
try:
    cy.denoiser = "OPENIMAGEDENOISE"
except Exception:
    pass
cy.max_bounces = 6
cy.diffuse_bounces = 2
cy.glossy_bounces = 3
cy.volume_bounces = 0
cy.transparent_max_bounces = 128     # rays cross many sectioned (clipped) buildings
cy.sample_clamp_indirect = 6.0
cy.volume_step_rate = float(LKA.get("step_rate", 2.0))
cy.volume_max_steps = int(LKA.get("max_steps", 128))
try:
    cy.seed = 0
    cy.use_animated_seed = False
except Exception:
    pass
scene.render.use_persistent_data = True
scene.view_settings.view_transform = "Standard"
vl = bpy.context.view_layer
vl.use_pass_z = True
vl.use_pass_emit = True
vl.cycles.denoising_store_passes = True
im = scene.render.image_settings
im.media_type = "MULTI_LAYER_IMAGE"
im.file_format = "OPEN_EXR_MULTILAYER"
im.color_depth = "32"
scene.render.resolution_percentage = 100


def _exr_npy(path, stem):
    import OpenImageIO as oiio
    want = {"Combined": "combined", "Emission": "emit", "Denoising Albedo": "albedo", "Depth": "z"}
    inp = oiio.ImageInput.open(path)
    k = 0
    while inp.seek_subimage(k, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        pas = ".".join(names[0].split(".")[1:-1]) if names[0].count(".") >= 2 else names[0]
        if pas in want:
            px = _np.asarray(inp.read_image(k, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
            if pas == "Depth":
                _np.save(stem + "_z.npy", px[..., :1].astype(_np.float32))
            else:
                _np.save(stem + "_" + want[pas] + ".npy", px[..., :3].astype(_np.float16))
        k += 1
    inp.close()
    os.remove(path)


import bpy_extras.object_utils as _ou  # noqa: E402

# ------------------------------------------------------------------ city alive on the netrun street: traffic streak lanes
# (the r3 street-lane rule on the derived street: lanes at fractions of the road's half width, head lights one way and
# tail lights the other, one lane period per 4 s loop; they move per frame)
LANE_P = float(LKA.get("lane_period", 80.0))
LANEM = _emit_mat("oc_lane", float(LKA.get("lane_k", 5.0)))
# r2: not sectioned (the streaks stand at headlight height on the camera side of the street centre line)
_lr = random.Random(9402)
LANES = []
_half = float(OCJ.get("street_width", 8.0)) / 2.0
for li, (fr_, dirn, col) in enumerate(((0.28, 1, (1.0, 0.92, 0.8)), (0.62, 1, (1.0, 0.85, 0.6)), (-0.3, -1, (1.0, 0.12, 0.08)),
                                       (-0.64, -1, (0.95, 0.15, 0.1)))):
    acc = Acc("oc_lane_%d" % li)
    off = fr_ * _half
    x = _u0 - LANE_P * 2 - 120
    while x < _u1 + 120 + LANE_P:
        L_ = _lr.uniform(3.0, 16.0)
        k_ = _lr.uniform(0.5, 1.3)
        c_ = tuple(v * k_ for v in col)
        za, zb = (0.42, 0.6) if dirn > 0 else (0.5, 0.64)
        if _ax0:
            acc.face([(x, _cline + off, za), (x + L_, _cline + off, za), (x + L_, _cline + off, zb), (x, _cline + off, zb)], c_, (0, 0, 0))
        else:
            acc.face([(_cline + off, x, za), (_cline + off, x + L_, za), (_cline + off, x + L_, zb), (_cline + off, x, zb)], c_, (0, 0, 0))
        x += L_ + _lr.uniform(4.0, 22.0)
    ob = acc.obj(LANEM)
    LANES.append((ob, dirn))


FGLANEM = _emit_mat("r2_fglane", float(LKA.get("lane_k", 5.0)) * 0.8)      # not sectioned: they lie on the lowered fill
_side = -(_nrm[1] if _ax0 else _nrm[0])
for li, off in enumerate(PLAN.get("fg_lanes", [])):
    acc = Acc("r2_fglane_%d" % li)
    col = (1.0, 0.9, 0.75) if li % 2 == 0 else (1.0, 0.14, 0.1)
    dirn = 1 if li % 2 == 0 else -1
    x = _u0 - LANE_P * 2 - 160
    while x < _u1 + 160 + LANE_P:
        L_ = _lr.uniform(4.0, 18.0)
        c_ = tuple(v * _lr.uniform(0.5, 1.3) for v in col)
        cc = _cline + _side * abs(off)
        za, zb = (0.42, 0.62)
        if _ax0:
            acc.face([(x, cc, za), (x + L_, cc, za), (x + L_, cc, zb), (x, cc, zb)], c_, (0, 0, 0))
        else:
            acc.face([(cc, x, za), (cc, x + L_, za), (cc, x + L_, zb), (cc, x, zb)], c_, (0, 0, 0))
        x += L_ + _lr.uniform(5.0, 26.0)
    ob = acc.obj(FGLANEM)
    LANES.append((ob, dirn))

# plumes (atmosphere.layers): soft rising steam columns over the planned roof vents
PLUMES = []
for k_, pl in enumerate(PLAN.get("plumes", [])):
    pm = bpy.data.materials.new("r2_plume_%d" % k_)
    pn = pm.node_tree
    pn.nodes.clear()
    po = pn.nodes.new("ShaderNodeOutputMaterial")
    pv = pn.nodes.new("ShaderNodeVolumeScatter")
    pv.inputs["Color"].default_value = (0.9, 0.88, 0.95, 1)
    pv.inputs["Anisotropy"].default_value = 0.3
    tc_ = pn.nodes.new("ShaderNodeTexCoord")
    sp_ = pn.nodes.new("ShaderNodeSeparateXYZ")
    pn.links.new(tc_.outputs["Generated"], sp_.inputs[0])

    def PM(op, a, b=None):
        n = pn.nodes.new("ShaderNodeMath")
        n.operation = op
        for idx, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[idx].default_value = v
            else:
                pn.links.new(v, n.inputs[idx])
        return n.outputs[0]
    gx, gy, gz = sp_.outputs["X"], sp_.outputs["Y"], sp_.outputs["Z"]
    rr2 = PM("ADD", PM("POWER", PM("SUBTRACT", gx, 0.5), 2.0), PM("POWER", PM("SUBTRACT", gy, 0.5), 2.0))
    wid = PM("ADD", 0.04, PM("MULTIPLY", gz, 0.14))                  # widens as it rises
    radial = PM("EXPONENT", PM("MULTIPLY", PM("DIVIDE", rr2, wid), -1.0))
    up = PM("MULTIPLY", PM("POWER", PM("SUBTRACT", 1.0, gz), 1.5), PM("MINIMUM", PM("MULTIPLY", gz, 12.0), 1.0))
    nz_ = pn.nodes.new("ShaderNodeTexNoise")
    nz_.inputs["Scale"].default_value = 3.0
    nz_.inputs["Detail"].default_value = 4.0
    pn.links.new(tc_.outputs["Generated"], nz_.inputs["Vector"])
    brk_ = PM("MAXIMUM", PM("MULTIPLY", PM("SUBTRACT", nz_.outputs["Fac"], 0.3), 2.0), 0.0)
    pn.links.new(PM("MULTIPLY", PM("MULTIPLY", PM("MULTIPLY", radial, up), brk_), float(LKA.get("plume_k", 0.09)) * S), pv.inputs["Density"])
    pn.links.new(pv.outputs[0], po.inputs["Volume"])
    me_ = bpy.data.meshes.new("r2_plume_%d" % k_)
    b_ = _bm.new()
    _bm.ops.create_cube(b_, size=1.0)
    b_.to_mesh(me_)
    b_.free()
    ob = bpy.data.objects.new("r2_plume_%d" % k_, me_)
    x_, y_, z_ = pl["pos"]
    ob.location = (x_, y_, z_ + pl["h"] / 2)
    ob.scale = (pl["r"] * 4.0, pl["r"] * 4.0, pl["h"])
    me_.materials.append(pm)
    scene.collection.objects.link(ob)
    PLUMES.append(ob)
print("R2 fg lanes", len(PLAN.get("fg_lanes", [])), "plumes", len(PLUMES), flush=True)

LOD = PLAN["lod"]


def sign_lod(cam_loc):
    """Per sign, by its distance to the camera (BU): t1 shape (<= t1_shape), t2 full (<= t2_full), t3 detail
    (<= t3_detail). A sign over an opening goes with its wall."""
    cnt = {"t0": 0, "t1": 0, "t2": 0, "t3": 0}
    for so in SIGN_OBJS:
        d_ = (Vector(so["centre"]) - cam_loc).length
        tier = 3 if d_ <= LOD["t3_detail"] else 2 if d_ <= LOD["t2_full"] else 1 if d_ <= LOD["t1_shape"] else 0
        gone = bool(so["sign"].get("wall")) and WALL_STATE.get(so["sign"]["wall"], False)
        if gone:
            tier = 0
        for o in so["t1"]:
            o.hide_render = tier != 1
        for o in so["t2"]:
            o.hide_render = tier < 2
        for o in so["t3"]:
            o.hide_render = tier < 3
        cnt["t%d" % tier] += 1
    return cnt


def set_lanes(t, show=True):
    p = (t % 4.0) / 4.0
    for ob, dirn in LANES:
        ob.hide_render = not show
        d = dirn * p * LANE_P
        ob.location = (d, 0.0, 0.0) if _ax0 else (0.0, d, 0.0)


_EMS = []
for _m in (NEONA, WINA, PANA):
    _e = next(n_ for n_ in _m.node_tree.nodes if n_.type == "EMISSION")
    _EMS.append((_e, _e.inputs["Strength"].default_value))
_LB = next(n_ for n_ in LITA.node_tree.nodes if n_.type == "BSDF_PRINCIPLED")
_LB0 = _LB.inputs["Emission Strength"].default_value


def dyn_mode(on):
    """Emission-only: the lanes are the only emitters (their reflections on the wet street come with them)."""
    for e, v in _EMS:
        e.inputs["Strength"].default_value = 0.0 if on else v
    _LB.inputs["Emission Strength"].default_value = 0.0 if on else _LB0
    _bg.inputs["Strength"].default_value = 0.0 if on else 1.0
    for o in scene.objects:
        if o.type == "LIGHT":
            o.hide_render = on or o.name.startswith(("key",)) or (o.get("oc_off") is True)
    fog.hide_render = on
    for o in BEAM_SHAFTS:
        o.hide_render = on


for o in scene.objects:
    if o.type == "LIGHT" and not o.name.startswith("oc_"):
        o["oc_off"] = True

for fr in OCJ["frames"]:
    t0 = _tm.time()
    pz = fr["persp"]
    lo, tg = Vector(pz["loc"]), Vector(pz["tgt"])
    fv = (tg - lo).normalized()
    cam_data.type = "PERSP"
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = 36.0
    cam_data.lens = pz["lens"]
    cam_data.shift_x, cam_data.shift_y = pz.get("sx", 0.0), pz.get("sy", 0.0)
    cam.location = lo
    cam.rotation_euler = fv.to_track_quat("-Z", "Y").to_euler()
    set_walls(fr.get("dis", {}))
    _lod = sign_lod(lo)
    print("R2 sign LOD", fr["name"], _lod, flush=True)
    dyn_mode(bool(fr.get("dyn")))
    set_lanes(float(fr.get("t", 0.0)), show=fr.get("lanes", True))
    scene["oc_zcut"] = float(fr.get("zcut", 1.0e4))
    for _o in (cityo, RB_OBJ, solid, cwino, cneono, lito):
        _o.update_tag()
    scene.render.resolution_x, scene.render.resolution_y = fr.get("res", OCJ.get("res", [1280, 720]))
    bpy.context.view_layer.update()
    stem = os.path.join(OUTDIR, fr["name"])
    scene.render.filepath = stem + ".exr"
    bpy.ops.render.render(write_still=True)
    _exr_npy(stem + ".exr", stem)

    def _p(P):
        v = _ou.world_to_camera_view(scene, cam, Vector(P))
        return None if v.z <= 0 else (v.x * 1920.0, (1 - v.y) * 1080.0)
    A = dict(rooms={i: dict(front=[_p(q) for q in r["front"]], back=[_p(q) for q in r["back"]]) for i, r in OCJ["rooms"].items()},
             edges=[dict(a=e["a"], b=e["b"], type=e["type"], pts=[_p(q) for q in e["path"]], world=e["path"]) for e in OCJ.get("edges", [])],
             hidden_fg=[], vol_boxes=[], cam_world=[list(r_) for r_ in cam.matrix_world], lens=cam_data.lens,
             sensor=36.0, shift=[cam_data.shift_x, cam_data.shift_y], look="real", cam=dict(dist=(tg - lo).length),
             sign_lod=_lod)
    # the landmark box for the metrics: the megastructure's projected bounds (an object pass, not a hand box)
    if MEGA_OBJS:
        _pp = []
        for o in MEGA_OBJS:
            for v_ in o.bound_box:
                q_ = _p(o.matrix_world @ Vector(v_))
                if q_:
                    _pp.append(q_)
        if _pp:
            A["landmark_box"] = [min(p[0] for p in _pp) / 1920.0, min(p[1] for p in _pp) / 1080.0,
                                 max(p[0] for p in _pp) / 1920.0, max(p[1] for p in _pp) / 1080.0]
    A["signs"] = {so["sign"]["id"]: [_p(Vector(so["centre"]))] for so in SIGN_OBJS}
    with open(os.path.join(OUTDIR, "anchors_%s.json" % fr["name"]), "w") as f:
        json.dump(A, f)
    print("TIME cycles %s %.1f" % (fr["name"], _tm.time() - t0), flush=True)
print("DONE", flush=True)
