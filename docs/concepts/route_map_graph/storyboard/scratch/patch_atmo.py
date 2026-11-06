import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "m44/onecity_cycles.py"
s = open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- beams: the r3 rule, scaled to the building heights
i0 = s.index("# beams (the r3 rule on this city)")
i1 = s.index("# ------------------------------------------------------------------ the city fog")
beams = '''# heights the atmosphere scales to (v3-r2: the frontage was raised by the layout rules; the r3 numbers were for the
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
_rk = set(OCJ["route_keys"])
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
_bE = float(LKA.get("beam", 2.0e7))
for k, (zt, c, key) in enumerate(_pick):
    col = _PAL[_BCOL[k % len(_BCOL)]]
    hh = (key * 2654435761) % 1000 / 1000.0
    lx = 0.12 + 0.30 * hh
    ly = 0.18 + 0.12 * ((key * 40503) % 1000 / 1000.0)
    lean = (lx if c[0] > _mid[0] else -lx, ly * (1 if abs(_nrm[1]) > 0.5 else 0) + 0.0, 1.0)
    rot = Vector(lean).normalized().to_track_quat("-Z", "Y").to_euler()
    org = (c[0], c[1], zt + 0.5)
    for part, ang, e in (("soft", 3.0, 1.0), ("core", 0.9, 2.75)):
        ob = _light("oc_beam_%d_%s" % (k, part), "SPOT", org, rot, _bE * e, col, spot=ang, blend=0.5)
        ob.data.use_shadow = False
        BEAMS.append(ob)
print("ONECITY beams", [(round(c[0]), round(c[1]), round(zt)) for zt, c, key in _pick], flush=True)

'''
s = s[:i0] + beams + s[i1:]

# ---------------------------------------------------------------- the fog: r3 strata at street LOD, scaled to heights
old_a = s.index("S = SCALE\nZ = sep.outputs[\"Z\"]")
old_b = s.index("nt.links.new(dens, vs.inputs[\"Density\"])")
fogsrc = '''S = SCALE
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
wisp = _m("SUBTRACT", 1.0, _smooth(_m("ABSOLUTE", _m("SUBTRACT", zw, 1.08 * HF), 0), 0.0, 0.07 * HF))
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
'''
s = s[:old_a] + fogsrc + s[old_b:]
s = s.replace("FX0, FX1, FY0, FY1, FZ1 = -700.0, 900.0, -700.0, 900.0, 240.0 / S",
              "FX0, FX1, FY0, FY1, FZ1 = -700.0, 900.0, -700.0, 900.0, max(240.0 / S, 2.5 * H_SKY)")
old = '''for o in cglow:
    o.data.use_shadow = False'''
assert old in s
s = s.replace(old, '''for o in BEAMS:
    o.light_linking.receiver_collection = _rx      # r3: the full-power beam lights the media only
for o in cglow:
    o.data.use_shadow = False''')
# lanes at half strength (designer note v3-r2): the street glow strips (GLANE, on NEONM) get their own emitter
old = '''        elif o is RPAN_OBJ:
            o.data.materials[si] = PANA'''
assert old in s
s = s.replace(old, '''        elif o is RPAN_OBJ:
            o.data.materials[si] = PANA
        elif o is glaneo:
            o.data.materials[si] = GLANEA''')
s = s.replace('''PANA = _emit_mat("oc_panel", float(LKA.get("panel", 4.0)))''',
              '''PANA = _emit_mat("oc_panel", float(LKA.get("panel", 4.0)))
GLANEA = _emit_mat("oc_glane", float(LKA.get("neon", 3.2)) * float(LKA.get("lane_dim", 0.5)))''')
s = s.replace("for _m in (SURF, LITA, NEONA, WINA, PANA):", "for _m in (SURF, LITA, NEONA, WINA, PANA, GLANEA):")
open(p, "w", encoding="utf-8").write(s)

p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
old = "beam=6.0e5, beams=4,"
assert old in s
s = s.replace(old, "beam=2.0e7, beams=6, beam_rise=1.35, lane_dim=0.5, lane_k=2.5, wisp_k=0.7, fog_front=7.0,")
open(p, "w", encoding="utf-8").write(s)
print("ok")
