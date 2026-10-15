"""V3 AAA render loop (exec'd at the end of scene_aaa.py). Per shot: anchors, the Cycles main render, the Cycles
volume render, the Eevee data passes. See scene_aaa.py for the outputs."""
OV = {k: override_mat(k) for k in ("normal", "id", "depth", "sem", "wz")}
DATA_PASSES = JOB.get("data_passes", ["normal", "id", "depth", "sem", "wz"])
DATA_RES = JOB.get("data_res", JOB["res"])
VOL_RES = JOB.get("vol_res", [JOB["res"][0] // 2, JOB["res"][1] // 2])
RENDERS = JOB.get("renders", ["main", "vol", "trans", "data"])
DATA_WORLD = bpy.data.worlds.new("w_data")
_dbg = next(n for n in DATA_WORLD.node_tree.nodes if n.type == "BACKGROUND")


def set_view(raw):
    try:
        scene.view_settings.view_transform = "Raw" if raw else "Standard"
    except TypeError:
        pass
    scene.view_settings.look = "None"


GPU_OK = None


def gpu_setup():
    """r2: the RX 6700 XT through HIP (driver updated). Falls back to the CPU (and says so) if no HIP device shows."""
    global GPU_OK
    if GPU_OK is not None:
        return GPU_OK
    GPU_OK = False
    if JOB.get("cpu"):
        return False
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "HIP"
        # HIP-RT: its BVH build costs ~86 s per render here (debug-cycles), but it traces ~3x faster than the plain
        # HIP BVH2 (14 s vs 45 s for the mini main pass), so it wins on every final pass; "hiprt": false turns it off
        try:
            prefs.use_hiprt = bool(JOB.get("hiprt", True))
        except (AttributeError, TypeError):
            pass
        prefs.refresh_devices()
        n = 0
        for d in prefs.devices:
            d.use = (d.type == "HIP")
            n += d.use
            print("cycles device", d.type, d.name, "use" if d.use else "-", flush=True)
        GPU_OK = n > 0
    except Exception as e:      # noqa: BLE001
        print("HIP setup failed", e, flush=True)
    print("RENDER DEVICE", "GPU (HIP)" if GPU_OK else "CPU", flush=True)
    return GPU_OK


def cycles_setup(samples, res, threshold):
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "GPU" if gpu_setup() else "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = threshold
    cy.adaptive_min_samples = min(16, samples)
    cy.use_denoising = True
    for k, v in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_input_passes", "RGB_ALBEDO_NORMAL"),
                 ("denoising_prefilter", "ACCURATE"), ("denoising_quality", "HIGH"), ("denoising_use_gpu", True)):
        try:
            setattr(cy, k, v)
        except (TypeError, AttributeError) as e:
            print("cycles setting", k, e, flush=True)
    cy.use_light_tree = True
    cy.max_bounces = 6
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 3
    cy.transmission_bounces = 4
    cy.volume_bounces = 0
    cy.transparent_max_bounces = 32
    cy.sample_clamp_direct = 0.0
    cy.sample_clamp_indirect = 6.0
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.volume_step_rate = JOB.get("step_rate", 1.0)
    cy.volume_max_steps = int(JOB.get("max_steps", 256))
    try:
        cy.volume_biased = bool(JOB.get("vol_biased", False))     # r3: ray marching instead of null scattering
    except AttributeError:
        pass
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    vl = bpy.context.view_layer
    vl.use_pass_combined = True
    vl.use_pass_z = True
    vl.use_pass_emit = True
    vl.use_pass_diffuse_color = True
    vl.cycles.denoising_store_passes = True
    s = scene.render.image_settings
    s.media_type = "MULTI_LAYER_IMAGE"
    s.file_format = "OPEN_EXR_MULTILAYER"
    s.color_depth = "32"
    try:
        s.exr_codec = "ZIP"
    except TypeError:
        pass
    set_view(False)


def exr_to_npy(path, stem, want):
    """Read a Blender multilayer EXR (multi-part: one subimage per pass) with OpenImageIO and save the wanted passes as
    .npy (h, w, c): float16 colour, float32 depth."""
    import OpenImageIO as oiio
    import numpy as _np
    inp = oiio.ImageInput.open(path)
    found = {}
    k = 0
    while inp.seek_subimage(k, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        pas = ".".join(names[0].split(".")[1:-1]) if names[0].count(".") >= 2 else names[0]
        if pas in want:
            px = _np.asarray(inp.read_image(k, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
            keep = [ci for ci, nm in enumerate(names) if not nm.endswith(".A")]
            arr = px[..., keep]
            out = want[pas]
            if pas == "Depth":
                _np.save(stem + "_" + out + ".npy", arr[..., :1].astype(_np.float32))
            else:
                _np.save(stem + "_" + out + ".npy", arr[..., :3].astype(_np.float16))
            found[pas] = out
        k += 1
    inp.close()
    print("exr passes saved", sorted(found), "missing", sorted(set(want) - set(found)), flush=True)


WRAP = {}


def wrapped(m, see_through):
    """Volume render: camera rays see a holdout (or nothing, for translucent things); every other ray sees the real
    material, so surfaces still block light (god rays) and emitters still light the haze."""
    key = (m.name, see_through)
    if key in WRAP:
        return WRAP[key]
    w = m.copy()
    w.name = m.name + ("_vt" if see_through else "_vh")
    nt = w.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    if out.inputs["Surface"].links:
        src = out.inputs["Surface"].links[0].from_socket
        lp = nt.nodes.new("ShaderNodeLightPath")
        hold = nt.nodes.new("ShaderNodeBsdfTransparent" if see_through else "ShaderNodeHoldout")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
        nt.links.new(src, mix.inputs[1])
        nt.links.new(hold.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
    if not see_through and not m.name.startswith("txt_"):
        try:
            w.cycles.emission_sampling = "NONE"     # the haze is lit by the real lights; neon glow is bloom
        except (AttributeError, TypeError):
            pass
    WRAP[key] = w
    return w


def all_surface_objs():
    vol = set(o.name for o in VOLUME_OBJS)
    return [o for o in scene.objects if o.type in ("MESH", "FONT") and o.name not in vol]


TRANSLUCENT = set(["air", "trail", "steam"]) | set(m.name for m in HOLO_M.values())
HET = globals().get("HET", [])
_T_EMIT = bpy.data.materials.new("t_emit")
_T_SEE = bpy.data.materials.new("t_see")
for _m, _kind in ((_T_EMIT, "ShaderNodeEmission"), (_T_SEE, "ShaderNodeBsdfTransparent")):
    _m.node_tree.nodes.clear()
    _o = _m.node_tree.nodes.new("ShaderNodeOutputMaterial")
    _s = _m.node_tree.nodes.new(_kind)
    _m.node_tree.links.new(_s.outputs[0], _o.inputs[0])
T_WORLD = bpy.data.worlds.new("w_trans")
next(n for n in T_WORLD.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (1, 1, 1, 1)


def neon_fog(on):
    """r3 designer review: the merged neon (the far towers' vertical strips above all) lit the denser fog into vertical
    pillars. In the volume render the neon meshes are not seen by volume-scatter rays (bloom carries their glow);
    signs, holograms and the real lights still light the fog."""
    for o in NEON_OBJS + TEXT_OBJS:      # (text signs too: the vertical blades made the pillars)
        try:
            o.visible_volume_scatter = on
        except AttributeError:
            pass


def is_see_through(m):
    return m.name in TRANSLUCENT or m.name.startswith(("hr_", "fogcard", "ad_holo"))


def trans_pass(stem, res, samples):
    """r3: the transmittance of the heterogeneous media (strata, ground mist) along every camera ray, up to the first
    opaque surface: surfaces emit 1 (camera rays only, no lights), the world is white, translucent things are clear,
    the media are their absorption-only twins. Combined = T per channel. The homogeneous boxes stay analytic (post)."""
    saved = {}
    for o in all_surface_objs():
        mats = list(o.data.materials)
        saved[o.name] = mats
        for si, m in enumerate(mats):
            if m is not None:
                o.data.materials[si] = _T_SEE if is_see_through(m) else _T_EMIT
    het = {o.name: (ms, ma) for o, ms, ma in HET}
    vis = {}
    for o in VOLUME_OBJS + ATMOS_OBJS:
        vis[o.name] = o.hide_render
        o.hide_render = o.name not in het
    for o, ms, ma in HET:
        o.data.materials[0] = ma
    lvis = {}
    for ob, e0, grp in LIGHTS:
        lvis[ob.name] = ob.hide_render
        ob.hide_render = True
    moon = bpy.data.objects.get("moon")
    if moon:
        lvis["moon"] = moon.hide_render
        moon.hide_render = True
    live_world = scene.world
    scene.world = T_WORLD
    cycles_setup(samples, res, 0.05)
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    render(stem + "_trans.exr")
    exr_to_npy(stem + "_trans.exr", stem + "_trans", {"Combined": "combined"})
    scene.world = live_world
    for o in all_surface_objs():
        for si, m in enumerate(saved.get(o.name, [])):
            o.data.materials[si] = m
    for o in VOLUME_OBJS + ATMOS_OBJS:
        o.hide_render = vis[o.name]
    for o, ms, ma in HET:
        o.data.materials[0] = ms
    for ob, e0, grp in LIGHTS:
        ob.hide_render = lvis[ob.name]
    if moon:
        moon.hide_render = lvis["moon"]

if JOB.get("power"):
    power_cut(JOB["power"])

import time as _time  # noqa: E402

if JOB.get("sb"):                # storyboard: the per-frame render driver (sb_r.py)
    exec(compile(open(os.path.join(HERE, "sb_r.py")).read(), "sb_r.py", "exec"), globals())
for _nm in JOB.get("fg_hide", []):     # storyboard v2: the loop shares the sequence-wide hidden occluders
    for _o in FG_OBJS.get(_nm, []):
        _o.hide_render = True
if JOB.get("loop"):              # r3: the idle loop renders (loop_r3.py), instead of the still's passes
    exec(compile(open(os.path.join(HERE, "loop_r3.py")).read(), "loop_r3.py", "exec"), globals())
for shot in JOB["shots"]:
    name = shot["name"]
    set_pose(shot["pose"])
    animate(shot.get("t", 2.0))
    sync_moving_lights()
    bpy.context.view_layer.update()
    hidden = protect_hide(shot)
    for _nm in JOB.get("fg_hide", []):
        for _o in FG_OBJS.get(_nm, []):
            _o.hide_render = True
    A = anchors_for(shot)
    A["hidden_fg"] = hidden
    A["vol_boxes"] = [list(v[1:7]) + [v[7], list(v[8])] for v in VOL_BOXES]
    A["cam_world"] = [list(r) for r in cam.matrix_world]
    A["lens"], A["sensor"] = cam_data.lens, cam_data.sensor_width
    A["shift"] = [cam_data.shift_x, cam_data.shift_y]
    A["look"] = LOOK
    with open(os.path.join(OUTDIR, "anchors_%s.json" % name), "w") as f:
        json.dump(A, f, indent=1)
    stem = os.path.join(OUTDIR, name)
    if "main" in RENDERS:
        t0 = _time.time()
        for o in VOLUME_OBJS:
            o.hide_render = True
        WORLD_CAM_MUL.inputs[1].default_value = 0.0
        cycles_setup(JOB.get("samples", 64), JOB["res"], JOB.get("threshold", 0.02))
        render(stem + "_main.exr")
        exr_to_npy(stem + "_main.exr", stem, {"Combined": "combined", "Emission": "emit", "Denoising Albedo": "albedo",
                                              "Depth": "z", "Diffuse Color": "diffcol"})
        print("TIME main", name, round(_time.time() - t0, 1), flush=True)
    if "vol" in RENDERS:
        t0 = _time.time()
        saved = {}
        for o in all_surface_objs():
            mats = list(o.data.materials)
            saved[o.name] = mats
            for si, m in enumerate(mats):
                if m is not None:
                    o.data.materials[si] = wrapped(m, m.name in TRANSLUCENT or m.name.startswith(("hr_", "fogcard", "ad_holo")))
        for o in ATMOS_OBJS:
            o.hide_render = True
        for o in VOLUME_OBJS:
            o.hide_render = bool(JOB.get("no_steam")) and o in STEAM_OBJS
        for ob, e0, grp in LIGHTS:
            if any(ob.name.startswith(pfx) for pfx in JOB.get("hide_prefix", "").split(",") if pfx):
                ob.hide_render = True
        if JOB.get("vol_nolights"):
            for ob, e0, grp in LIGHTS:
                ob.hide_render = True
        # r3 loop statics: render a subset of the media / of the lights (vol_hide: volume-name prefixes to hide;
        # vol_only_prefix: only the lights with this name prefix)
        for o in VOLUME_OBJS:
            if any(o.name.startswith(p_) for p_ in JOB.get("vol_hide", [])):
                o.hide_render = True
        if JOB.get("vol_only_prefix"):
            for ob, e0, grp in LIGHTS:
                if not ob.name.startswith(JOB["vol_only_prefix"]):
                    ob.hide_render = True
        WORLD_CAM_MUL.inputs[1].default_value = 1.0
        neon_fog(False)
        cycles_setup(JOB.get("vol_samples", 64), VOL_RES, JOB.get("vol_threshold", 0.03))
        render(stem + "_vol.exr")
        exr_to_npy(stem + "_vol.exr", stem + "_vol", {"Combined": "combined"})
        for o in all_surface_objs():
            for si, m in enumerate(saved.get(o.name, [])):
                o.data.materials[si] = m
        for o in VOLUME_OBJS:
            o.hide_render = True
        for o in ATMOS_OBJS:
            o.hide_render = False
        WORLD_CAM_MUL.inputs[1].default_value = 0.0
        print("TIME vol", name, round(_time.time() - t0, 1), flush=True)
    if "trans" in RENDERS and HET:
        t0 = _time.time()
        trans_pass(stem, JOB.get("trans_res", VOL_RES), int(JOB.get("trans_samples", 24)))
        print("TIME trans", name, round(_time.time() - t0, 1), flush=True)
    if "data" in RENDERS:
        t0 = _time.time()
        scene.render.engine = EEVEE
        scene.render.resolution_x, scene.render.resolution_y = DATA_RES
        scene.render.image_settings.media_type = "IMAGE"
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_depth = "16"
        live_world = scene.world
        scene.world = DATA_WORLD
        for o in ATMOS_OBJS + HOLO_OBJS + VOLUME_OBJS:
            o.hide_render = True
        for ps in DATA_PASSES:
            set_view(ps in ("sem", "wz"))
            scene.render.image_settings.color_mode = "BW" if ps in ("depth", "wz") else "RGB"
            scene.eevee.taa_render_samples = 1
            bpy.context.view_layer.material_override = OV[ps]
            _dbg.inputs["Color"].default_value = (1, 1, 1, 1) if ps == "depth" else (0, 0, 0, 1)
            render(os.path.join(OUTDIR, "%s_%s.png" % (name, ps)))
            bpy.context.view_layer.material_override = None
            scene.render.image_settings.color_mode = "RGB"
        scene.world = live_world
        for o in ATMOS_OBJS + HOLO_OBJS:
            o.hide_render = False
        print("TIME data", name, round(_time.time() - t0, 1), flush=True)
    print("SHOT", name, "hidden", hidden, flush=True)
print("DONE", flush=True)
