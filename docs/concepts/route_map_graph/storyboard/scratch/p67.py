D = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts\\"
s = open(D + "m44/onecity_cycles.py").read()
o = '''import bpy_extras.object_utils as _ou  # noqa: E402

for fr in OCJ["frames"]:'''
n = '''import bpy_extras.object_utils as _ou  # noqa: E402

# ------------------------------------------------------------------ city alive on the netrun street: traffic streak lanes
# (the r3 street-lane rule on the derived street: lanes at fractions of the road's half width, head lights one way and
# tail lights the other, one lane period per 4 s loop; they move per frame)
LANE_P = float(LKA.get("lane_period", 80.0))
LANEM = _emit_mat("oc_lane", float(LKA.get("lane_k", 5.0)))
section(LANEM)
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
        w_ = 0.12
        if _ax0:
            acc.face([(x, _cline + off - w_, 0.12), (x + L_, _cline + off - w_, 0.12), (x + L_, _cline + off + w_, 0.12),
                      (x, _cline + off + w_, 0.12)], c_, (0, 0, 0))
        else:
            acc.face([(_cline + off - w_, x, 0.12), (_cline + off + w_, x, 0.12), (_cline + off + w_, x + L_, 0.12),
                      (_cline + off - w_, x + L_, 0.12)], c_, (0, 0, 0))
        x += L_ + _lr.uniform(4.0, 22.0)
    ob = acc.obj(LANEM)
    LANES.append((ob, dirn))


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


for o in scene.objects:
    if o.type == "LIGHT" and not o.name.startswith("oc_"):
        o["oc_off"] = True

for fr in OCJ["frames"]:'''
assert o in s
s = s.replace(o, n)
o2 = '''    set_walls(fr.get("dis", {}))'''
n2 = '''    set_walls(fr.get("dis", {}))
    dyn_mode(bool(fr.get("dyn")))
    set_lanes(float(fr.get("t", 0.0)), show=fr.get("lanes", True))'''
assert o2 in s
s = s.replace(o2, n2)
o3 = '''             edges=[], hidden_fg=[], vol_boxes=[],'''
n3 = '''             edges=[dict(a=e["a"], b=e["b"], type=e["type"], pts=[_p(q) for q in e["path"]], world=e["path"]) for e in OCJ.get("edges", [])],
             hidden_fg=[], vol_boxes=[],'''
assert o3 in s
s = s.replace(o3, n3)
s = s.replace('''    if o.type == "LIGHT":
        o.hide_render = True
for _m in (SURF, LITA, NEONA, WINA, PANA):''', '''    if o.type == "LIGHT":
        o.hide_render = True
        o["oc_off"] = True
for _m in (SURF, LITA, NEONA, WINA, PANA):''')
open(D + "m44/onecity_cycles.py", "w").write(s)
print("ok")
