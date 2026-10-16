"""hq_tethys: the Blender driver (headless Blender 5.2).

blender -b --factory-startup --python tethys_build.py -- <mode> <cam> <outdir> [res_k] [spp]
  mode  aaa (Cycles AAA-2, HIP GPU; TETHYS_CPU=1 for a CPU smoke test) | main (Eevee, the mainline look: geometry check)
  cam   t_close | t_over (tethys_preset.CAMS)

It runs the city_all_corps build UNCHANGED (its scripts are read from that folder, never edited) with hooks:
  1. presets: the clearer-water values (tethys_preset.WATER) and the cameras go into city_preset at run time; the
     scratch paths (rail json, sign image) point at D:/rc_scratch/tethys so the city agent's scratch is never written
  2. the zoning copy (tethys_quarter.prep_zoned): the buildings under the dam, the lock and the causeway removed;
     for the netrun overview the OCCLUSION rule cuts the dry buildings in the camera -> HQ sight cone to stubs
  3. city_build.py (buildings, ground) -> city_world.py (ring, sea, wall, rail) -> the Tethys hooks: drowned window
     share, the seabed albedo, build_dam(), build_clutter() -> landmarks.py with tethys() replaced by
     tethys_landmark.landmark() -> city_render.py (materials, lights, render, passes)
  4. the route-room anchors (pixel positions) for the overview overlay: <stem>_rooms.json
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import tethys_preset as TP  # noqa: E402

sys.path.insert(1, TP.CITY_SCRIPTS)
import city_preset as CP  # noqa: E402
import occlusion as OC  # noqa: E402
import tethys_quarter as TQ  # noqa: E402
import tethys_landmark as TL  # noqa: E402

T0 = time.time()
_argv = sys.argv[sys.argv.index("--") + 1:]
MODE, CAMK, OUTDIR = _argv[0], _argv[1], _argv[2]
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(TP.SCR, exist_ok=True)

# ------------------------------------------------------------------ 1. presets (run-time only; city_preset.py untouched)
for k, v in TP.WATER.items():
    CP.WATER[k] = dict(v) if isinstance(v, dict) else v
CP.CAMS.update(TP.CAMS)
CP.SCR = TP.SCR                                            # mainframe_blade.png is copied here
CP.RAIL["rail_json"] = os.path.join(TP.SCR, "meridian_rail.json")
if os.environ.get("TETHYS_CPU"):
    os.environ["CITY_CPU"] = "1"


# ------------------------------------------------------------------ 2. the zoning copy (+ occlusion for the overview)
def cam_pos(C, F):
    tgt = (*F.w_ab(*C["target_ab"]), 0.0)
    yw, pt = math.radians(C["yaw"]), math.radians(C["pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    return tuple(tgt[i] - fwd[i] * C["dist"] for i in range(3))


O0 = json.load(open(TP.ZONED_BASE))
F0 = TQ.Frame(O0)
occ_fn, occ_info = None, None
if CAMK in TP.OCC_CAMS:
    L0 = TQ.dam_line(O0)
    lk0 = TQ.lock_pose(O0, L0)
    c0, c1 = TQ.causeway(O0, L0, lk0)
    hx, hy = F0.W(O0["hq"]["tethys"])
    ZW = CP.WATER["z"]
    # the TARGET VOLUME: the station (rim, crown), the pier-end pods, the causeway and the lock (the route's ends)
    svx, svy = TL.server_xy(hx, hy)
    pts = [(hx, hy, ZW + 12.5), (hx, hy, ZW + 30.0), ((hx + svx) / 2, (hy + svy) / 2, ZW + TP.PIER["decks"][2]),
           (svx, svy, ZW + TP.PIER["stair"]["server_z"])]
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts.append((hx + 30 * math.cos(a), hy + 30 * math.sin(a), ZW + 4.0))
    pts += [(c0[0], c0[1], 6.0), ((c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2, 6.0)]
    pts.append((lk0["P"][0] + lk0["N"][0] * (TP.DAM["toe"] - 4.0), lk0["P"][1] + lk0["N"][1] * (TP.DAM["toe"] - 4.0), 12.0))
    cam = cam_pos(TP.CAMS[CAMK], F0)
    P_OCC = OC.occlusion_params(cam, pts)
    ghosts = []

    def occ_fn(b):
        zc, op = OC.occlusion_state(P_OCC, (b["x"], b["y"], b["top"], b["hx"], b["hy"]))
        if op < 0.999:
            ghosts.append((round(b["x"]), round(b["y"]), round(op, 2)))
        return zc
    occ_info = dict(cam=cam, targets=len(pts))

ZD = os.path.join(TP.SCR, "zoned_%s.json" % CAMK)
st = TQ.prep_zoned(TP.ZONED_BASE, ZD, occ=occ_fn, KH=CP.KH)
if occ_info:
    st["ghost_stubs"] = len(ghosts)
print("PREP", st, "%.1fs" % (time.time() - T0), flush=True)
CP.ZONED = ZD

# ------------------------------------------------------------------ 3. the city build with the Tethys hooks
CB = os.path.join(TP.CITY_SCRIPTS, "city_build.py")
src = open(CB, encoding="utf-8").read()
MARK = 'for _f in ("city_world.py", "landmarks.py", "city_render.py"):'
assert MARK in src, "city_build.py changed: the exec loop marker is gone"
ns = {"__file__": CB, "__name__": "city_build_tethys"}
exec(compile(src[:src.index(MARK)], CB, "exec"), ns)
CW = os.path.join(TP.CITY_SCRIPTS, "city_world.py")
exec(compile(open(CW, encoding="utf-8").read(), CW, "exec"), ns)
print("CITY base built %.1fs" % (time.time() - T0), flush=True)

# drowned windows: a higher lit share on every wet facade face; the seabed a little lighter (sand under clear water)
for acc in (ns["SURF"], ns["SMOOTH"]):
    for i in range(len(acc.wl)):
        if acc.wet[i] and acc.wl[i] > 0.0:
            acc.wl[i] = max(acc.wl[i], TP.WET_LIT)
ns["SEABED"].col = [tuple(min(1.0, c * TP.SEABED_K) for c in col) for col in ns["SEABED"].col]
LMF = os.path.join(TP.CITY_SCRIPTS, "landmarks.py")
lsrc = open(LMF, encoding="utf-8").read()
LMARK = 'for _k, _fn in (("halcyon", halcyon)'
assert LMARK in lsrc, "landmarks.py changed: the landmark loop marker is gone"
exec(compile(lsrc[:lsrc.index(LMARK)], LMF, "exec"), ns)          # the landmark defs (+ spot_at, STATION)
QD = TQ.build_dam(ns)
print("DAM built %.1fs" % (time.time() - T0), flush=True)
QC = TQ.build_clutter(ns)
print("CLUTTER built %.1fs" % (time.time() - T0), flush=True)
ns["tethys"] = lambda: TL.landmark(ns)            # ATLANTIS STATION round 2: the floating pier city
exec(compile(lsrc[lsrc.index(LMARK):], LMF, "exec"), ns)
print("LANDMARKS built %.1fs" % (time.time() - T0), flush=True)
if not os.environ.get("TETHYS_NOWILD"):          # the wildlife (designer note 2026-10-16): fish shoals and the whale pod
    TQ.build_street_shoals(ns)
    TQ.build_open_water_shoals(ns)
    TL.build_whales(ns, ns["TETHYS_INFO"]["centre"])
    print("WILDLIFE built %.1fs" % (time.time() - T0), flush=True)

if os.environ.get("TETHYS_BORDER"):          # a crop test: render only this region (x0,y0,x1,y1, 0..1, y up)
    import bpy  # noqa: E402
    _r = bpy.context.scene.render
    _r.border_min_x, _r.border_min_y, _r.border_max_x, _r.border_max_y = (float(v) for v in os.environ["TETHYS_BORDER"].split(","))
    _r.use_border, _r.use_crop_to_border = True, True
CR = os.path.join(TP.CITY_SCRIPTS, "city_render.py")
rsrc = open(CR, encoding="utf-8").read()
RMARK = 'stem = os.path.join(OUTDIR, "%s_%s" % (CAMK, MODE))'
assert RMARK in rsrc, "city_render.py changed: the render marker is gone"
# AD review 3: caustics. Inside the breakwater the caustic pattern is near zero everywhere (a dark mirror); outside, the
# surface layer (the surf material: towers, clutter, fish, whales) gets caustic x CAUSTIC_K.surf (gentle swell, not chop);
# the seabed material keeps its full caustics (patched into city_render.water_fade at run time; city_base is untouched)
BW_ = TP.PIER["breakwater"]
ns["CAUSTIC_CALM"] = dict(cx=ns["TETHYS_INFO"]["centre"][0], cy=ns["TETHYS_INFO"]["centre"][1], r0=BW_["calm_r"] - BW_["calm_soft"],
                          r1=BW_["calm_r"] + BW_["calm_soft"], k_in=BW_["caustic_in"])
ns["CAUSTIC_K"] = dict(surf=BW_["caustic_surf_out"], seabed=BW_["caustic_seabed_out"])
_wf = 'def water_fade(g, base, emis, caustic=False):'
assert _wf in rsrc
rsrc = rsrc.replace(_wf, 'def water_fade(g, base, emis, caustic=False, kscale=1.0):')
_call = 'water_fade(g, base.outputs[2], em, caustic=caustic)'
assert _call in rsrc
rsrc = rsrc.replace(_call, 'water_fade(g, base.outputs[2], em, caustic=caustic, kscale=CAUSTIC_K["surf"])')
_call2 = 'water_fade(g, col, (0.0, 0.0, 0.0) and g.comb(0, 0, 0), caustic=caustic)'
assert _call2 in rsrc
rsrc = rsrc.replace(_call2, 'water_fade(g, col, (0.0, 0.0, 0.0) and g.comb(0, 0, 0), caustic=caustic, kscale=CAUSTIC_K["seabed"] if caustic else 1.0)')
_ck = '        e = g.vmath("ADD", e, g.vmath("SCALE", tuple(C["col"]), scale=ck))'
assert _ck in rsrc
rsrc = rsrc.replace(_ck, '''        ck = g.math("MULTIPLY", ck, kscale)
        CC = globals().get("CAUSTIC_CALM")
        if CC:
            dd = g.math("SQRT", g.math("ADD", g.math("POWER", g.math("SUBTRACT", px, CC["cx"]), 2.0),
                                       g.math("POWER", g.math("SUBTRACT", py, CC["cy"]), 2.0)))
            mr_ = g.n("ShaderNodeMapRange")
            mr_.interpolation_type = "SMOOTHSTEP"
            mr_.inputs["From Min"].default_value = CC["r0"]
            mr_.inputs["From Max"].default_value = CC["r1"]
            mr_.inputs["To Min"].default_value = CC["k_in"]
            mr_.inputs["To Max"].default_value = 1.0
            g.link(dd, mr_.inputs["Value"])
            ck = g.math("MULTIPLY", ck, mr_.outputs[0])
''' + _ck)
exec(compile(rsrc[:rsrc.index(RMARK)], CR, "exec"), ns)       # materials, lights, camera (no render yet)


def calm_water(ns):
    """AD review 2: the water surface. Outside the breakwater: the chop at WATER.surface.wave (half of test 1) and the
    reflection at refl_out x Fresnel; inside the breakwater (PIER.breakwater.calm_r round the station) glass-calm: no
    chop and refl_in x Fresnel, so the moon pool and the server read straight down. A material rule on world position."""
    if MODE != "aaa":
        return
    BW = TP.PIER["breakwater"]
    m = ns["MS"]["water"]
    nt = m.node_tree
    bump = next(n for n in nt.nodes if n.type == "BUMP")
    fr = next(n for n in nt.nodes if n.type == "FRESNEL")
    mx = next(n for n in nt.nodes if n.type == "MIX_SHADER")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    hx_, hy_ = ns["TETHYS_INFO"]["centre"]
    vs = nt.nodes.new("ShaderNodeVectorMath")
    vs.operation = "SUBTRACT"
    nt.links.new(geo.outputs["Position"], vs.inputs[0])
    vs.inputs[1].default_value = (hx_, hy_, ns["ZW"])
    vl = nt.nodes.new("ShaderNodeVectorMath")
    vl.operation = "LENGTH"
    nt.links.new(vs.outputs[0], vl.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = BW["calm_r"] - BW["calm_soft"]
    mr.inputs["From Max"].default_value = BW["calm_r"] + BW["calm_soft"]
    nt.links.new(vl.outputs["Value"], mr.inputs["Value"])

    def M(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    nt.links.new(M("MULTIPLY", mr.outputs[0], TP.WATER["surface"]["wave"] * BW["chop_out"]), bump.inputs["Strength"])
    refl = M("ADD", BW["refl_in"], M("MULTIPLY", mr.outputs[0], BW["refl_out"] - BW["refl_in"]))
    nt.links.new(M("MULTIPLY", fr.outputs[0], refl), mx.inputs[0])
    print("WATER calm inside r %.1f, reflection %.2f / %.2f" % (BW["calm_r"], BW["refl_in"], BW["refl_out"]), flush=True)


calm_water(ns)
exec(compile(rsrc[rsrc.index(RMARK):], CR, "exec"), ns)       # the render + passes

# ------------------------------------------------------------------ 4. route-room anchors (pixels) for the overlay
import bpy  # noqa: E402
import bpy_extras.object_utils as ou  # noqa: E402
from mathutils import Vector  # noqa: E402

scene, camo = ns["scene"], ns["cam"]
RX, RY = ns["RX"], ns["RY"]


def px(p):
    v = ou.world_to_camera_view(scene, camo, Vector(p))
    return None if v.z <= 0 else [round(v.x * RX, 1), round((1 - v.y) * RY, 1), round(v.z, 1)]


info = ns.get("TETHYS_INFO", {})
rooms = dict(info.get("rooms", {}))
rooms["lock"] = QD["lock"]
out = dict(res=[RX, RY], cam=CAMK, rooms={k: dict(world=[round(c, 2) for c in v], px=px(v)) for k, v in sorted(rooms.items())},
           gates=[px(g) for g in QD["gates"]], causeway=[px((*QD["causeway"][0], 5.0)), px((*QD["causeway"][1], 5.0))],
           centre=px((*info.get("centre", (0, 0)), ns["ZW"])), crown=px(info.get("crown", (0, 0, 0))),
           prep=st, clutter=QC)
stem = os.path.join(OUTDIR, "%s_%s" % (CAMK, MODE))
json.dump(out, open(stem + "_rooms.json", "w"), indent=1)
print("TETHYS DONE %.1fs" % (time.time() - T0), flush=True)
