"""Storyboard v3 (one continuous city): the AAA-2 look on the SAME scene (exec'd by onecity_scene.py, mode "cycles").

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
for _m in (SURF, LITA, NEONA, WINA, PANA):
    section(_m)

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
sy = st["a"][1]
cglow = []
for k, xx in enumerate(_np.linspace(sx0 - 120, sx1 + 120, 6)):
    for yy in (sy + 40, sy + 120, sy - 60):
        c = (1.0, 0.3, 0.7) if (k + int(yy)) % 2 else (0.25, 0.75, 1.0)
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
for uu in _np.arange(_u0, _u1, float(LKA.get("lamp_step", 6.0))):
    for side in (-2.6, 2.6):
        pos = (float(uu), _cline + side, 1.6) if _ax0 else (_cline + side, float(uu), 1.6)
        c = (1.0, 0.72, 0.42) if _k % 3 else (0.55, 0.85, 1.0)
        _light("oc_lamp_%d" % _k, "POINT", pos, (0, 0, 0), float(LKA.get("lamp", 25.0)), c)
        _k += 1
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

# beams (the r3 rule on this city): the tallest roofs within 160 BU of the street, not a route column, spaced 45 BU
_cands = []
for (c, q, zt, terr, ts, key) in BUILT:
    if key in set(OCJ["route_keys"]) or zt < 12:
        continue
    d = math.hypot(c[0] - (sx0 + sx1) / 2, c[1] - sy)
    if 25 < d < 160 and c[1] > sy:
        _cands.append((zt, c))
_cands.sort(key=lambda v: (-v[0], v[1][0], v[1][1]))
_pick = []
for zt, c in _cands:
    if all(math.hypot(c[0] - p[1][0], c[1] - p[1][1]) > 45 for p in _pick):
        _pick.append((zt, c))
    if len(_pick) >= int(LKA.get("beams", 4)):
        break
BEAMS = []
for k, (zt, c) in enumerate(_pick):
    col = [(1.0, 0.16, 0.6), (0.16, 0.8, 1.0), (1.0, 0.58, 0.18), (0.62, 0.38, 1.0)][k % 4]
    lean = (0.25 if c[0] > (sx0 + sx1) / 2 else -0.25, 0.2, 1.0)
    rot = Vector(lean).normalized().to_track_quat("-Z", "Y").to_euler()
    BEAMS.append(_light("oc_beam_%d" % k, "SPOT", (c[0], c[1], zt + 0.5), rot, float(LKA.get("beam", 2.0e5)), col, spot=2.2, blend=0.4))
    BEAMS[-1].data.use_shadow = False
print("ONECITY beams", [(round(c[0]), round(c[1]), round(zt)) for zt, c in _pick], flush=True)

# ------------------------------------------------------------------ the city fog (r3 recipe, mainline units)
fm = bpy.data.materials.new("oc_fog")
nt = fm.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
vs = nt.nodes.new("ShaderNodeVolumeScatter")
vs.inputs["Color"].default_value = (0.85, 0.80, 1.0, 1)
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
hf = _m("EXPONENT", _m("MULTIPLY", _m("MAXIMUM", _m("SUBTRACT", Z, 30.0 / S), 0.0), -S / 55.0), 0)
banks = _smooth(_noise((0.004 * S, 0.012 * S, 0.075 * S), 3.0, 3.1), 0.45, 0.66)
clumps = _smooth(_noise((0.0075 * S, 0.014 * S, 0.022 * S), 2.0, 14.1), 0.40, 0.62)
floor_ = _smooth(Z, 2.0 / S, 9.0 / S)
body = _m("ADD", _m("MULTIPLY", clumps, 0.08), _m("MULTIPLY", banks, clumps))
dens = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", body, hf), floor_), float(LKA.get("fog_peak", 0.021)) * S)
nt.links.new(dens, vs.inputs["Density"])
haze = nt.nodes.new("ShaderNodeVolumeScatter")
haze.inputs["Density"].default_value = float(LKA.get("haze", 0.0016)) * S
haze.inputs["Anisotropy"].default_value = 0.2
haze.inputs["Color"].default_value = (0.82, 0.78, 1.0, 1)
add = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(vs.outputs[0], add.inputs[0])
nt.links.new(haze.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], out.inputs["Volume"])
me = bpy.data.meshes.new("oc_fog")
_b = _bm.new()
_bm.ops.create_cube(_b, size=1.0)
_b.to_mesh(me)
_b.free()
fog = bpy.data.objects.new("oc_fog", me)
FX0, FX1, FY0, FY1, FZ1 = -700.0, 900.0, -700.0, 900.0, 240.0 / S
fog.location = ((FX0 + FX1) / 2, (FY0 + FY1) / 2, (FZ1 - 0.5) / 2)
fog.scale = (FX1 - FX0, FY1 - FY0, FZ1 + 0.5)
me.materials.append(fm)
scene.collection.objects.link(fog)
_rx = bpy.data.collections.new("oc_fog_rx")
scene.collection.children.link(_rx)
_rx.objects.link(fog)
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
             edges=[], hidden_fg=[], vol_boxes=[], cam_world=[list(r_) for r_ in cam.matrix_world], lens=cam_data.lens,
             sensor=36.0, shift=[cam_data.shift_x, cam_data.shift_y], look="real", cam=dict(dist=(tg - lo).length))
    with open(os.path.join(OUTDIR, "anchors_%s.json" % fr["name"]), "w") as f:
        json.dump(A, f)
    print("TIME cycles %s %.1f" % (fr["name"], _tm.time() - t0), flush=True)
print("DONE", flush=True)
