"""Storyboard render driver (exec'd by render_aaa.py when the job has "sb"; the scene, rules and r3 loop machinery are in
scope). Persistent data, fixed seed, passes batched by type so materials are swapped once per batch, not per frame.

JOB["sb"]:
  mode "full"    moving-camera frames: per frame the main pass (every moving emitter at its time t), then all Eevee
                 sem passes, then all volume passes (every medium + beams, at vres), then all transmittance passes.
                 Outputs <name>_combined/_emit/_albedo/_z.npy, <name>_vol_combined.npy, <name>_trans_combined.npy,
                 <name>_sem.png, anchors_<name>.json - exactly what post_aaa.finish reads.
  mode "static"  one held camera: "static" = the hi-res base (moving emitters hidden), the static media without beams
                 (vol_static), the beams through every medium (beams_full, for the fit), trans, sem, anchors; then per
                 frame the emission-only dyn layer (streak lanes + globe) and the beams through the homogeneous haze only.
  frames: [{name, pose, t, power: {keep, k} | null}]  (power: the hover power cut, applied in 3D)
"""
import time as _tm

_SB = JOB["sb"]


def _dissolve_nodes(mat):
    """The bits dissolve on a surface material: cells of 0.7 BU (the bits) vanish where their white noise < the object's
    "dis" (0 = solid .. 1 = gone); the cells just above the threshold flash in the Cell's lime / cyan."""
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    if not out.inputs["Surface"].links:
        return
    src = out.inputs["Surface"].links[0].from_socket
    dis = attr(nt, "dis", "OBJECT").outputs["Fac"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = 1.0 / 0.7
    nt.links.new(geo.outputs["Position"], sc.inputs[0])
    fl = nt.nodes.new("ShaderNodeVectorMath")
    fl.operation = "FLOOR"
    nt.links.new(sc.outputs[0], fl.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(fl.outputs[0], wn.inputs["Vector"])
    nz = wn.outputs["Value"]
    on = math_n(nt, "GREATER_THAN", dis, 0.001)
    cut = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", nz, dis), on)
    edge = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", math_n(nt, "LESS_THAN", nz, math_n(nt, "ADD", dis, 0.10)), cut), on)
    em = nt.nodes.new("ShaderNodeEmission")
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    nt.links.new(math_n(nt, "GREATER_THAN", wn.outputs["Color"], 0.5) if False else math_n(nt, "GREATER_THAN", nz, 0.55), mixc.inputs["Factor"])
    mixc.inputs[6].default_value = (0.83, 1.0, 0.0, 1.0)
    mixc.inputs[7].default_value = (0.2, 0.9, 1.0, 1.0)
    nt.links.new(mixc.outputs[2], em.inputs["Color"])
    em.inputs["Strength"].default_value = 4.0
    m1 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(edge, m1.inputs[0])
    nt.links.new(src, m1.inputs[1])
    nt.links.new(em.outputs[0], m1.inputs[2])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    m2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cut, m2.inputs[0])
    nt.links.new(m1.outputs[0], m2.inputs[1])
    nt.links.new(tr.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"])


WALL_M = TOON.copy()
WALL_M.name = "sb_wall"
_dissolve_nodes(WALL_M)
WALLS = {}


def build_walls():
    """Rule: a facade wall over the opening of EVERY route room (the layout's room list), in its column's facade colour
    with the window-grid shader, so the aerial sees solid buildings; the dive dissolves them room by room."""
    for i, n in sorted(LY["nodes"].items()):
        l = int(i[1:].split("_")[0])
        x0c, x1c = LY["cols"][str(l)]
        _, z0, _, z1 = n["room"]
        f = int(round((z0 - SLAB / 2) / FH))
        za, zb = f * FH, (f + 1) * FH
        y = LY["dy"][l]
        c = FAMS[(l * 3 + 1) % len(FAMS)] if l != 7 else (0.34, 0.3, 0.36)
        acc = Acc("wall_" + i)
        set_sem(0.6, 0, l)
        box(x0c - 0.05, y - 0.32, za + 0.02, x1c + 0.05, y - 0.04, zb - 0.02, c, facet=False, acc=acc)
        ob = acc.obj(WALL_M, "wall_" + i)
        ob["dis"] = 0.0
        WALLS[i] = ob
    print("SB walls", len(WALLS), flush=True)


build_walls()
_FR = _SB["frames"]
# v2: the flicker groups are picked once from the street OVERVIEW (the rules pose) in every job, so the same signs,
# strobes and windows flicker in every shot (designer rule: city-alive activity never pauses)
JOB["shots"] = [dict(name=_FR[0]["name"], pose=JOB.get("rules_pose") or _FR[0]["pose"], t=_FR[0].get("t", 0.0), protect=[])]
JOB["loop"] = dict(mode="none", groups=bool(_SB.get("groups", True)), T=4.0)
exec(compile(open(os.path.join(HERE, "loop_r3.py")).read(), "loop_r3.py", "exec"), globals())
JOB.pop("loop", None)
JOB["shots"] = []
if globals().get("FILL_LANES"):
    DYN.extend(o for o, ax, dr in FILL_LANES)
    _slt0 = set_loop_time

    def set_loop_time(t):
        _slt0(t)
        p = (t % L_T) / L_T
        for o, ax, dr in FILL_LANES:
            o.location = (dr * p * LANE_P, 0.0, 0.0) if ax == "x" else (0.0, dr * p * LANE_P, 0.0)
scene.render.use_persistent_data = True

# ------------------------------------------------------------------ the hover power cut, re-applicable per frame
_PW0 = {}


def _pw_save():
    if _PW0:
        return
    _PW0["gs"] = next(n for n in TOON.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"].default_value
    _PW0["air"] = [(next(n for n in m.node_tree.nodes if n.type == "EMISSION"), None) for m in (AIRM, TRAILM, STEAMM)]
    _PW0["air"] = [(em, em.inputs["Strength"].default_value) for em, _ in _PW0["air"]]


_PW_CUR = [None]


def set_power(pw):
    """pw = None (no cut, the room state factors only) or {"keep": [...], "k": k}. Restores the originals first."""
    key = None if not pw else (tuple(sorted(pw["keep"])), round(pw["k"], 4))
    if key == _PW_CUR[0]:
        return
    _pw_save()
    next(n for n in TOON.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Emission Strength"].default_value = _PW0["gs"]
    for em, v in _PW0["air"]:
        em.inputs["Strength"].default_value = v
    for ob, e0, grp in LIGHTS:
        ob.data.energy = e0
    for o in TEXT_OBJS + HOLO_OBJS:
        o["pwo"] = 1.0
        o.update_tag()
    cfg = dict(room_k=JOB["room_k"])
    if pw and pw["k"] < 0.999:
        cfg.update(keep=pw["keep"], k=pw["k"], boost=1.0 + 0.45 * (1.0 - pw["k"]) / (1.0 - 0.22))
    power_cut(cfg)
    for o in TEXT_OBJS + HOLO_OBJS:
        o.update_tag()
    for o in NEON_OBJS:
        o.data.update_tag()
    _PW_CUR[0] = key


_FK = [None]
_HZ = [1.0]
FILL_HAZE_K = float(JOB.get("fill_haze_k", 4.5))     # haze body / layered field (0.15 x 4.5 = 0.68 of the back haze)
_ZM = [None]
FILL_OFF = all(float(f.get("fk", JOB.get("fill_fk", 1.0))) <= 0.0 for f in _FR) and not _SB.get("static", {}).get("fk")


def _fill_vis():
    for o in FILL_FOG:
        if FILL_OFF and o.name != "vol_back_haze":
            o.hide_render = True


def _place(fr_):
    set_pose(fr_["pose"])
    for i, ob in WALLS.items():
        v = float(fr_.get("dis", {}).get(i, fr_.get("dis_all", _SB.get("dis_all", 0.0))))
        hide = v >= 0.999
        if ob.hide_render != hide:
            ob.hide_render = hide
        if abs(ob.get("dis", 0.0) - v) > 1e-6:
            ob["dis"] = v
            ob.update_tag()
    z = float(fr_.get("zoom", 1.0))
    if z != _ZM[0]:
        for o in VOLUME_OBJS:
            if o.name.startswith("r3strata"):
                o["unzoom"] = 1.0 - z
                o.update_tag()
        lo, za, zb = PRE["lod_bands"]["cityglow_by_zoom"]
        uu = min(1.0, max(0.0, (z - za) / (zb - za)))
        gk = lo + (1.0 - lo) * uu * uu * (3 - 2 * uu)
        for ob, e0, grp in LIGHTS:
            if ob.name.startswith(("cityglow_r_", "featglow_")):
                ob.data.energy = e0 * gk
        if fr_.get("power") is None:
            a, b = PRE["lod_bands"]["signage_on_at"]
            u = min(1.0, max(0.0, (z - a) / (b - a)))
            ks = max(0.0015, u * u * (3 - 2 * u))
            for o in TEXT_OBJS + HOLO_OBJS:
                o["pwo"] = ks if ks < 0.999 else 1.0
                o.update_tag()
        _ZM[0] = z
    # sign flicker on rendered frames (pwo is an object attribute: free per frame); held shots composite every layer
    if _SB["mode"] == "full" and GROUPS and fr_.get("live", True):
        import sb_live as _LV
        a_, b_ = PRE["lod_bands"]["signage_on_at"]
        uu = min(1.0, max(0.0, (z - a_) / (b_ - a_)))
        sk = max(0.0015, uu * uu * (3 - 2 * uu)) if fr_.get("power") is None else 1.0
        fi = int(round(float(fr_.get("t", 0.0)) * 24))
        for g in ("sign_buzz", "sign_flicker", "sign_broken"):
            if g in GROUPS and GROUPS[g].get("kind") == "obj":
                o = bpy.data.objects.get(GROUPS[g]["obj"])
                if o is not None:
                    o["pwo"] = max(0.0015, sk * _LV.gain(g, fi))
                    o.update_tag()
    fk = float(fr_.get("fk", JOB.get("fill_fk", 1.0)))
    if FILL_FOG and fk != _FK[0]:
        hk = float(fr_.get("haze", 1.0))
        for o in FILL_FOG:
            if o.name == "vol_back_haze":
                o["bhcut"] = 1.0 - hk
            else:
                o["fk"] = fk
                o["fkh"] = float(fr_.get("fkh", 0.0))
            o.update_tag()
        _HZ[0] = hk
        _FK[0] = fk
    t = float(fr_.get("t", 0.0))
    animate(t)
    sync_moving_lights()
    set_loop_time(t)
    bpy.context.view_layer.update()


def _anchors(fr_):
    A = anchors_for(dict(fr_, protect=[]))
    A["hidden_fg"] = []
    A["vol_boxes"] = [list(v[1:7]) + [v[7] * (_HZ[0] if v[0] == "back_haze" else 1.0), list(v[8])] for v in VOL_BOXES]
    A["cam_world"] = [list(r) for r in cam.matrix_world]
    A["lens"], A["sensor"] = cam_data.lens, cam_data.sensor_width
    A["shift"] = [cam_data.shift_x, cam_data.shift_y]
    A["look"] = LOOK
    with open(os.path.join(OUTDIR, "anchors_%s.json" % fr_["name"]), "w") as f:
        json.dump(A, f)


def _tr(path):
    t0 = _tm.time()
    render(path)
    return _tm.time() - t0


def _main_batch(frames, spp, res, hide_dyn=False):
    for o in VOLUME_OBJS:
        o.hide_render = True
    for o in DYN:
        o.hide_render = hide_dyn
    _fill_vis()
    WORLD_CAM_MUL.inputs[1].default_value = 0.0
    cycles_setup(spp, res, 0.01)
    for fr_ in frames:
        set_power(fr_.get("power"))
        _place(fr_)
        _anchors(fr_)
        stem = os.path.join(OUTDIR, fr_["name"])
        dt = _tr(stem + "_main.exr")
        exr_to_npy(stem + "_main.exr", stem, {"Combined": "combined", "Emission": "emit", "Denoising Albedo": "albedo",
                                              "Depth": "z"})
        os.remove(stem + "_main.exr")
        print("TIME main %s %.1f" % (fr_["name"], dt), flush=True)
    for o in DYN:
        o.hide_render = False


def _sem_batch(frames, res):
    scene.render.engine = EEVEE
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_depth = "16"
    live_world = scene.world
    scene.world = DATA_WORLD
    for o in ATMOS_OBJS + HOLO_OBJS + VOLUME_OBJS:
        o.hide_render = True
    set_view(True)
    scene.render.image_settings.color_mode = "RGB"
    scene.eevee.taa_render_samples = 1
    bpy.context.view_layer.material_override = OV["sem"]
    _dbg.inputs["Color"].default_value = (0, 0, 0, 1)
    for fr_ in frames:
        _place(fr_)
        render(os.path.join(OUTDIR, "%s_sem.png" % fr_["name"]))
    bpy.context.view_layer.material_override = None
    scene.world = live_world
    for o in ATMOS_OBJS + HOLO_OBJS:
        o.hide_render = False
    set_view(False)


def _vol_batch(frames, spp, res, suffix="_vol", flags=(True, True, True, True, True)):
    vol_wrap()
    vol_show(*flags)
    _fill_vis()
    cycles_setup(spp, res, 0.01)
    for fr_ in frames:
        set_power(fr_.get("power"))
        _place(fr_)
        stem = os.path.join(OUTDIR, fr_["name"] + suffix)
        dt = _tr(stem + ".exr")
        exr_to_npy(stem + ".exr", stem, {"Combined": "combined"})
        os.remove(stem + ".exr")
        print("TIME %s %s %.1f" % (suffix, fr_["name"], dt), flush=True)
    vol_show(True, True, True, True, True)
    vol_unwrap()


def _trans_batch(frames, spp, res):
    for fr_ in frames:
        _place(fr_)
        t0 = _tm.time()
        trans_pass(os.path.join(OUTDIR, fr_["name"]), res, spp)
        os.remove(os.path.join(OUTDIR, fr_["name"] + "_trans.exr"))
        print("TIME trans %s %.1f" % (fr_["name"], _tm.time() - t0), flush=True)


def _dyn_batch(frames, spp, res):
    for o in VOLUME_OBJS:
        o.hide_render = True
    emission_only(on_objs=tuple(o.name for o in DYN))
    cycles_setup(spp, res, 0.02)
    for fr_ in frames:
        _place(fr_)
        stem = os.path.join(OUTDIR, fr_["name"] + "_dyn")
        dt = _tr(stem + ".exr")
        exr_to_npy(stem + ".exr", stem, {"Combined": "combined"})
        os.remove(stem + ".exr")
        print("TIME dyn %s %.1f" % (fr_["name"], dt), flush=True)
    restore_all()


# the v3_dynamic occlusion rule, made sequence-wide: a foreground occluder that would cover a protected room (the
# current room + the options) in ANY route framing is hidden for the whole storyboard, so it never pops between shots
_HID = set()
for _pz in _SB.get("protect_poses", []):
    set_pose(_pz)
    bpy.context.view_layer.update()
    _HID |= set(protect_hide(dict(protect=_SB.get("protect", []))))
for _nm, _objs in FG_OBJS.items():
    for _o in _objs:
        _o.hide_render = _nm in _HID
print("SB hidden foreground", sorted(_HID), flush=True)
if JOB.get("debug_rays"):
    from bpy_extras.object_utils import world_to_camera_view as _w2c
    for _fr in _FR:
        set_pose(_fr["pose"])
        bpy.context.view_layer.update()
        _dg = bpy.context.evaluated_depsgraph_get()
        for (_u, _v) in ((0.6, 0.5), (0.75, 0.5), (0.9, 0.5), (0.75, 0.25), (0.75, 0.8)):
            _fr_ = cam.data.view_frame(scene=scene)
            _p = cam.matrix_world @ (_fr_[2] + (_fr_[1] - _fr_[2]) * _u + (_fr_[0] - _fr_[1]) * _v)
            _o = cam.matrix_world.translation
            _h = scene.ray_cast(_dg, _o, (_p - _o).normalized())
            print("RAY", _fr["name"], _u, _v, _h[0], _h[4].name if _h[0] else None, tuple(round(x, 1) for x in _h[1]), flush=True)
    raise SystemExit(0)
_T0 = _tm.time()
_P = _SB.get("passes", ["main", "sem", "vol", "trans"])
if _SB["mode"] == "full":
    if "main" in _P:
        _main_batch(_FR, int(_SB.get("spp", 48)), _SB.get("res", [1280, 720]))
    if "sem" in _P:
        _sem_batch(_FR, _SB.get("res", [1280, 720]))
    if "vol" in _P:
        _vol_batch(_FR, int(_SB.get("vspp", 16)), _SB.get("vres", [640, 360]), _SB.get("vol_suffix", "_vol"))
    if "trans" in _P:
        _trans_batch(_FR, int(_SB.get("tspp", 16)), _SB.get("vres", [640, 360]))
elif _SB["mode"] == "static":
    S = _SB["static"]
    st = dict(name=S["name"], pose=S["pose"], t=S.get("t", 0.0), power=S.get("power"))
    st.update(S.get("extra", {}))          # v2: fk / haze / fkh / zoom / dis_all for a held shot (the HQ aerial)
    if "main" in _P:
        _main_batch([st], int(S.get("spp", 128)), S["res"], hide_dyn=True)
        _sem_batch([st], S["res"])
    if "vol" in _P:
        _vol_batch([st], int(S.get("vspp", 32)), S.get("vres", S["res"]), "_volstatic", (True, True, True, False, True))
        _vol_batch([st], int(S.get("bspp", 32)), S.get("bres", [640, 360]), "_beamsfull", (True, True, True, True, False))
        _trans_batch([st], int(S.get("tspp", 24)), S.get("vres", S["res"]))
    if "layers" in _P and GROUPS:
        # the emission-only flicker layers of this held shot (r3 loop statics), composited per frame in 2D
        set_power(S.get("power"))
        _place(st)
        for o in VOLUME_OBJS:
            o.hide_render = True
        for o in DYN:
            o.hide_render = True
        cycles_setup(int(_SB.get("lspp", 64)), _SB.get("res", [1280, 720]), 0.01)
        for g, d in sorted(GROUPS.items()):
            if d["kind"] == "obj":
                emission_only(on_objs=(d["obj"],), alt=(d["obj"], d["alt"]) if d.get("alt") else None)
            else:
                emission_only(on_mats=tuple(d["mats"]))
            stem = os.path.join(OUTDIR, "%s_layer_%s" % (S["name"], g))
            dt = _tr(stem + ".exr")
            exr_to_npy(stem + ".exr", stem, {"Combined": "combined"})
            os.remove(stem + ".exr")
            restore_all()
            print("TIME layer %s %.1f" % (g, dt), flush=True)
        for o in DYN:
            o.hide_render = False
    if "dyn" in _P and _FR:
        set_power(S.get("power"))
        _dyn_batch(_FR, int(_SB.get("dspp", 32)), _SB.get("res", [1280, 720]))
    if "beams" in _P and _FR:
        set_power(S.get("power"))
        _vol_batch(_FR, int(_SB.get("bspp", 32)), _SB.get("bres", [640, 360]), "_beams", (False, False, True, True, False))
print("SB DONE %.1f s" % (_tm.time() - _T0), flush=True)
