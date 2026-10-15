"""r3 procedural rules (exec'd by fog_r3.py inside the scene build, after the city geometry is merged).

Every r3 look element is placed by a rule that reads the layout data, never by hand, so any netrun street gives the
same look with the same preset (look_preset.py). Inputs:
  - the route layout (LY: columns, storeys, rooms) and the job's room states (which rooms are the decision set);
  - the camera pose of the shot (JOB shots[0].pose);
  - a city HEIGHTFIELD ray-cast straight down over the solid city meshes (roof heights, building mask);
  - the street geometry (a ray-cast transect across the road).
Outputs (the RULES dict): the decision view bounds and fog floor, the street and sky lanes, beam rigs, steam vents,
the fog-bank map (an image the fog shader samples), bank and wisp glow lights, the skyline height.
Seeded streams: 9500 beams, 9510 plumes, 9520 glows (never the shared build stream).
"""
import random as _rq
import sys as _sys

import numpy as _np

if HERE not in _sys.path:
    _sys.path.insert(0, HERE)
import look_preset as _LP  # noqa: E402

PRE = _LP.PRESET
_LP.use_palette(JOB.get("palette", "neon_bay"))
PAL = _LP.colour
RULES = {}
_pose = JOB["shots"][0]["pose"]
CAM = Vector(_pose["loc"])
CAM_X, CAM_Y, CAM_Z = CAM.x, CAM.y, CAM.z
_sens = 36.0
_lens = float(_pose.get("lens", 40.0))
_half = _sens / _lens / 2.0                          # tan of the horizontal half view angle
_shx = float(_pose.get("shift_x", 0.0)) * _sens / _lens
_aspect = 9.0 / 16.0
_tgt = Vector(_pose["tgt"])
_pitch = (_tgt.z - CAM_Z) / max(1e-6, (_tgt - CAM).length)  # sin of the camera's pitch (negative: looking down)
_shy = float(_pose.get("shift_y", 0.0)) * _sens / _lens
FRAME_A = (_shx - _half, _shx + _half)                # view tan range across the frame, horizontally
FRAME_E = (_pitch + _shy - _half * _aspect, _pitch + _shy + _half * _aspect)   # and vertically (small-angle)


def view_a(x, y):
    """The horizontal view tan of a world point (x per depth from the camera)."""
    return (x - CAM_X) / max(1e-3, (y - CAM_Y))


def view_e(y, z):
    return (z - CAM_Z) / max(1e-3, (y - CAM_Y))


# ------------------------------------------------------------------ the decision set's view bounds (the calm zone)
_dec = [i for i, s in JOB.get("room_state", {}).items() if s in ("current", "option")]
_a, _e = [], []
for _i in _dec:
    _x0, _z0, _x1, _z1 = LY["nodes"][_i]["room"]
    _y0 = LY["nodes"][_i]["dy"]
    for _x in (_x0, _x1):
        for _y in (_y0, _y0 + DEPTH):
            for _z in (_z0, _z1):
                _a.append(view_a(_x, _y))
                _e.append(view_e(_y, _z))
RULES["calm_a"] = (min(_a), max(_a)) if _a else (0.0, 0.0)
RULES["calm_e_top"] = max(_e) if _e else -1.0
print("rules: decision view tan x %.3f..%.3f, top elevation tan %.3f" % (RULES["calm_a"] + (RULES["calm_e_top"],)),
      flush=True)


def in_calm(x, y, margin=0.05):
    a = view_a(x, y)
    return RULES["calm_a"][0] - margin < a < RULES["calm_a"][1] + margin


def on_frame(x, y, z, margin=0.02):
    a, e = view_a(x, y), view_e(y, z)
    return FRAME_A[0] + margin < a < FRAME_A[1] - margin and FRAME_E[0] < e < FRAME_E[1] - margin


# ------------------------------------------------------------------ the city heightfield
_hf = PRE["heightfield"]
_step = _hf["step"]
HX = _np.arange(_hf["x"][0], _hf["x"][1], _step)
HY = _np.arange(_hf["y"][0], _hf["y"][1], _step)
HMAP = _np.zeros((len(HY), len(HX)), _np.float32)
_solid = set(o.name for o in SOLID_OBJS)
_dg = bpy.context.evaluated_depsgraph_get()
_down = Vector((0, 0, -1))
for _iy, _y in enumerate(HY):
    for _ix, _x in enumerate(HX):
        _o = Vector((float(_x), float(_y), _hf["z_top"]))
        for _k in range(8):
            _hit, _loc, _n, _fi, _ob, _m = scene.ray_cast(_dg, _o, _down)
            if not _hit:
                break
            if _ob.name in _solid:
                HMAP[_iy, _ix] = max(0.0, _loc.z)
                break
            _o = _loc + Vector((0, 0, -0.02))
BMASK = (HMAP > 8.0).astype(_np.float32)
RULES["skyline"] = float(_np.median(HMAP[(HY[:, None] > 120) & (HMAP > 20)])) if (HMAP > 20).any() else 120.0
print("rules: heightfield %dx%d, skyline median %.1f BU, built share %.2f" % (len(HX), len(HY), RULES["skyline"],
                                                                         BMASK.mean()), flush=True)


def _blur(a, sig_cells):
    r = max(1, int(sig_cells * 3))
    k = _np.exp(-0.5 * (_np.arange(-r, r + 1) / max(sig_cells, 1e-3)) ** 2)
    k /= k.sum()
    a = _np.apply_along_axis(lambda v: _np.convolve(_np.pad(v, r, mode="edge"), k, "valid"), 1, a)
    return _np.apply_along_axis(lambda v: _np.convolve(_np.pad(v, r, mode="edge"), k, "valid"), 0, a)


def _local_max(rad):
    out = []
    for iy in range(len(HY)):
        for ix in range(len(HX)):
            h = HMAP[iy, ix]
            if h <= 0:
                continue
            win = HMAP[max(0, iy - rad):iy + rad + 1, max(0, ix - rad):ix + rad + 1]
            if h >= win.max():
                out.append((float(h), float(HX[ix]), float(HY[iy])))
    out.sort(key=lambda c: (-c[0], c[1], c[2]))     # tie-break by position, never by dict order
    return out


def _spaced(cands, n, spacing, rng=None):
    pick = []
    for c in cands:
        if all((c[1] - p[1]) ** 2 + (c[2] - p[2]) ** 2 >= spacing ** 2 for p in pick):
            pick.append(c)
        if len(pick) >= n:
            break
    return pick


# ------------------------------------------------------------------ the street (a transect across the road)
_ys = _np.arange(-80.0, 20.0, 0.5)
_road = []
for _y in _ys:
    _hit, _loc, _n, _fi, _ob, _m = scene.ray_cast(_dg, Vector((CAM_X, float(_y), 50.0)), _down)
    if _hit and 0.04 < _loc.z < 0.14:
        _road.append(float(_y))
_yn, _yf = (max(_road), min(_road)) if _road else (-9.5, -40.0)
_yc = (_yn + _yf) / 2.0
_sl = PRE["street_lanes"]
RULES["street"] = dict(near=_yn, far=_yf, centre=_yc)
RULES["street_lanes"] = ([_yn - f * (_yn - _yc) for f in _sl["fractions_near"]] +
                         [_yc - f * (_yc - _yf) for f in _sl["fractions_far"]])
print("rules: road y %.1f..%.1f, lanes %s" % (_yf, _yn, [round(v, 1) for v in RULES["street_lanes"]]), flush=True)

# ------------------------------------------------------------------ sky lanes: heights relative to the skyline
_sk = PRE["sky_lanes"]
RULES["sky_lanes"] = [(y, RULES["skyline"] * f) for y, f in zip(_sk["y"], _sk["z_frac"])][:_sk["n"]]

# ------------------------------------------------------------------ beams: the K tallest non-route roofs
_bp = PRE["beams"]
_rb = _rq.Random(9500)
_cands = [c for c in _local_max(4) if _bp["y_range"][0] <= c[2] <= _bp["y_range"][1] and c[0] >= _bp["roof_min"]
          and not in_calm(c[1], c[2], 0.06) and on_frame(c[1], c[2], c[0] + 2.0)
          and view_e(c[2], c[0]) < FRAME_E[1] - _bp["min_rise"]]      # a long visible shaft above the roof
_picked = _spaced(_cands, _bp["k"], _bp["min_spacing"])
_mid_a = (FRAME_A[0] + FRAME_A[1]) / 2.0
_left = [c for c in _picked if view_a(c[1], c[2]) < _mid_a]
_right = [c for c in _picked if view_a(c[1], c[2]) >= _mid_a]
RIGS = []
_heroes = []
if _left:
    _heroes.append((_left[0], "district_a", "a"))
if _right:
    _heroes.append((_right[0], "district_b", "b"))
_hero_set = set(id(h[0]) for h in _heroes[:_bp["heroes"]])
_ci = {-1.0: 0, 1.0: 0}
for c in _picked:
    h, x, y = c
    side = 1.0 if view_a(x, y) >= _mid_a else -1.0
    lean = side * _rb.uniform(*_bp["lean"])
    dirv = (lean, _rb.uniform(*_bp["lean_y"]), 1.0)
    sweep = _rb.uniform(*_bp["sweep_deg"])
    ph = _rb.random()
    hero = next((hh for hh in _heroes if hh[0] is c), None)
    if hero:
        colname = hero[1]
        if hero[2] == "a":
            soft, core, twin = _bp["hero_soft"], _bp["hero_core"], _bp["haze_twin"]
        else:
            soft, core, twin = _bp["hero_b_soft"], _bp["hero_b_core"], _bp["haze_twin_b"]
    else:
        sl = _bp["side_colours"]["left" if side < 0 else "right"]       # each side keeps its district
        colname = sl[_ci[side] % len(sl)]
        _ci[side] += 1
        soft, core, twin = None, _bp["thin"], (_bp["haze_twin_b"] if colname == "district_b" else _bp["haze_twin"])
    RIGS.append(dict(name="%s_%d_%d" % (colname, int(x), int(y)), colour=PAL(colname), origin=(x, y, h + 0.6), dir=dirv,
                     soft=soft, core=core, sweep=sweep, phase=ph, twin=twin))
RULES["beams"] = RIGS
print("rules: beams", [(r["name"], tuple(round(v) for v in r["origin"])) for r in RIGS], flush=True)

# ------------------------------------------------------------------ steam plumes: N rooftop vents, seeded, off the decision set
_pp = PRE["plumes"]
_rp = _rq.Random(9510)
_vc = [c for c in _local_max(2) if _pp["roof_z"][0] <= c[0] <= _pp["roof_z"][1] and not in_calm(c[1], c[2], 0.08)
       and on_frame(c[1], c[2], c[0] + 10.0)]
for _l in range(len(LY["cols"])):          # the route columns' own roofs qualify, unless they hold a decision room
    _cx0, _cx1 = LY["cols"][str(_l)]
    _top = LY["storeys"][str(_l)] * FH
    _cx, _cy = (_cx0 + _cx1) / 2.0 + 2.0, LY["dy"][_l] + DEPTH * 0.4
    if not any(LY["nodes"][i]["room"][0] < _cx < LY["nodes"][i]["room"][2] for i in _dec) and not in_calm(_cx, _cy, 0.08) \
            and _pp["roof_z"][0] <= _top <= _pp["roof_z"][1]:
        _vc.append((float(_top), float(_cx), float(_cy)))
_rp.shuffle(_vc)
_vc.sort(key=lambda c: (round(c[0] / 20.0), c[1]))        # mix heights, deterministic order
_rp.shuffle(_vc)
RULES["plumes"] = [(x, y, h + 0.8, _rp.uniform(*_pp["lean"]), _rp.uniform(*_pp["height"]), 51.0 + k)
                   for k, (h, x, y) in enumerate(_spaced(_vc, _pp["n"], _pp["min_spacing"]))]
print("rules: plumes", [tuple(round(v) for v in p[:3]) for p in RULES["plumes"]], flush=True)

# ------------------------------------------------------------------ the fog-bank map: alleys and tower bases
_fp = PRE["fog"]
near = _blur(BMASK, _fp["bank_reach"] / _step)
BANK = _np.clip(near * (1.0 - _blur(BMASK, 0.7)) * 2.6, 0, 1).astype(_np.float32)
RULES["bank_map"] = (HX[0], HY[0], HX[-1] + _step, HY[-1] + _step)
_img = bpy.data.images.new("r3_bankmap", width=len(HX), height=len(HY), alpha=False, float_buffer=True)
_px = _np.zeros((len(HY), len(HX), 4), _np.float32)
_px[..., 0] = BANK
_px[..., 1] = BMASK
_px[..., 3] = 1.0
_img.pixels.foreach_set(_px.ravel())
_img.pack()
_img.colorspace_settings.name = "Non-Color"
RULES["bank_image"] = _img
# the first far layer's front (the depth where the built share first peaks behind the route row) holds the wisp
_occ = BMASK.mean(axis=1)
_iy0 = int(_np.argmax((HY > 40) & (_occ > 0.25))) if ((HY > 40) & (_occ > 0.25)).any() else len(HY) // 4
RULES["wisp_y"] = (float(HY[_iy0]) - 20.0, float(HY[_iy0]) - 4.0)
RULES["wisp_z"] = RULES["skyline"] * _fp["wisp_frac"]
# glows under the densest bank spots and along the wisp, off the decision set, district colours alternating
_rg = _rq.Random(9520)
_bc = []
_bs = _blur(BANK, 3.0)
for iy in range(len(HY)):
    for ix in range(len(HX)):
        x, y = float(HX[ix]), float(HY[iy])
        if _bs[iy, ix] > 0.25 and not in_calm(x, y, 0.08) and on_frame(x, y, _fp["bank_z"][0]):
            _bc.append((float(_bs[iy, ix]), x, y))
_bc.sort(key=lambda c: (-c[0], c[1], c[2]))
GLOWS = []
for k, (v, x, y) in enumerate(_spaced(_bc, _fp["bank_glow_n"], 45.0)):
    GLOWS.append(((x, y, _fp["bank_z"][0] - 8.0), PAL("district_a" if k % 2 == 0 else "district_b"), _fp["bank_glow_w"]))
_wx = [x for x in _np.linspace(FRAME_A[0], FRAME_A[1], 9)[1:-1]]
_wy = sum(RULES["wisp_y"]) / 2.0
_wc = [(CAM_X + a * (_wy - CAM_Y)) for a in _wx]
_wc = [x for x in _wc if not in_calm(x, _wy, 0.1)]
_rg.shuffle(_wc)
for k, x in enumerate(sorted(_wc[:_fp["wisp_glow_n"]])):
    GLOWS.append(((x, _wy, RULES["wisp_z"] - 34.0), PAL("district_b" if k % 2 == 0 else "district_a"), _fp["wisp_glow_w"]))
RULES["glows"] = GLOWS
print("rules: wisp y %.0f..%.0f z %.1f; glows %d" % (RULES["wisp_y"] + (RULES["wisp_z"], len(GLOWS))), flush=True)
