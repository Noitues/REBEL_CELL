"""V3 AAA dressing, critique pass (exec'd after dress_aaa.py and holo_route_aaa.py, before the merge).

Own seeded stream DR2 = Random(6161). CRITIQUE.md §3 #5-#8 and §6:
  greebles   per route column: more AC boxes (12-20), ledges every 2 floors, 4 side-wall ducts, 2 bracket box signs,
             roof fans; all off the route floors (rooms stay clear), spill-lit only (no emission except sign faces).
  cables     up to 8 sagging catenaries per alley, behind the route links, at heights with no route room and no link.
  scale      3 mid-row towers that leave the top of the frame, 2 megastructure masses (behind L2 and L5/L6), both
             outside the decision set's calm zone (x 70-114), with our ad bands on them.
  near layer 2 near-black foreground silhouettes at the frame edges (a sign back on a pole, a gantry).
  ads        10 textures from ads_aaa.py (our corps and invented products): box billboards (16:9, dark frame,
             4 floodlights), blade signs (1:4) and one holo panel (scanlines, RGB split, 45 % alpha).
  traffic    the lane in front of the far city (lane 0) gets 1.5x brighter trails.
"""
import random as _random2

DR2 = _random2.Random(6161)
ADS_DIR = os.path.join(os.path.dirname(HERE), "scratch", "ads")
AD_OBJS = []
CALM_X = (70.0, 114.0)      # current room + both options (x); nothing busy is placed behind them


def ad_mat(name, k=1.6, holo=False):
    m = bpy.data.materials.new("ad_" + name)
    if holo:
        for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, prop, val)
            except (AttributeError, TypeError):
                pass
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(ADS_DIR, name + ".png"))
    uv = nt.nodes.new("ShaderNodeUVMap")
    L(uv.outputs["UV"], tex.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    L(tex.outputs["Color"], em.inputs["Color"])
    pw = attr(nt, "pwo", "OBJECT")
    pwk = math_n(nt, "ADD", pw.outputs["Fac"], math_n(nt, "LESS_THAN", pw.outputs["Fac"], 0.001))
    L(math_n(nt, "MULTIPLY", pwk, k), em.inputs["Strength"])
    if holo:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        add = nt.nodes.new("ShaderNodeAddShader")
        L(tr.outputs[0], add.inputs[0])
        L(em.outputs[0], add.inputs[1])
        L(add.outputs[0], out.inputs["Surface"])
    else:
        L(em.outputs[0], out.inputs["Surface"])
    return m


def ad_plane(name, cx, y, cz, w, h, k=1.6, holo=False, flood=True):
    me = bpy.data.meshes.new("adp_" + name)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(p) for p in ((cx - w / 2, y, cz - h / 2), (cx + w / 2, y, cz - h / 2), (cx + w / 2, y, cz + h / 2),
                                     (cx - w / 2, y, cz + h / 2))]
    f = bm.faces.new(vs)
    for lp, uvv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uvl].uv = uvv
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("ad_" + name + "_%d" % len(AD_OBJS), me)
    me.materials.append(ad_mat(name, k, holo))
    scene.collection.objects.link(ob)
    AD_OBJS.append(ob)
    if holo:
        HOLO_OBJS.append(ob)
    else:
        TEXT_OBJS.append(ob)          # power cut + "pwo" like the signs
        # dark frame and 4 floodlights on arms below the panel
        box(cx - w / 2 - 0.5, y + 0.05, cz - h / 2 - 0.5, cx + w / 2 + 0.5, y + 0.6, cz + h / 2 + 0.5, (0.03, 0.03, 0.04), facet=False)
        if flood:
            for q in range(4):
                fx = cx - w / 2 + w * (q + 0.5) / 4
                beam((fx, y + 0.1, cz - h / 2 - 0.5), (fx, y - 1.6, cz - h / 2 - 1.2), 0.12, (0.06, 0.06, 0.07))
                NEON.face([(fx - 0.3, y - 1.75, cz - h / 2 - 1.0), (fx + 0.3, y - 1.75, cz - h / 2 - 1.0),
                           (fx + 0.3, y - 1.75, cz - h / 2 - 0.7), (fx - 0.3, y - 1.75, cz - h / 2 - 0.7)], (2.2, 2.0, 2.4), (0, 0, 0))
    return ob


# ------------------------------------------------------------------ greebles on the route columns
def greeble_column(l):
    x0, x1 = LY["cols"][str(l)]
    y = LY["dy"][l]
    st = LY["storeys"][str(l)]
    rf = ROUTE_FLOORS.get(l, {})
    top = st * FH
    set_sem(DRESS_SEM, 0, l)
    signs = 0
    for f in range(st):
        if f in rf:
            continue
        za = f * FH
        nslot = int((x1 - x0 - 1.0) / 2.15)
        for s_ in range(nslot):
            if DR2.random() < 0.32:
                ac_unit(x0 + 0.5 + (s_ + 0.5) * (x1 - x0 - 1.0) / nslot + DR2.uniform(-0.3, 0.3), y,
                        za + DR2.choice([1.2, 3.4, 5.6]))
        if f % 2 == 0 and (f - 1) not in rf and f > 0:
            box(x0 + 0.2, y - 0.4, za, x1 - 0.2, y, za + 0.3, (0.26, 0.25, 0.29), facet=False)
        if signs < 2 and l != 7 and DR2.random() < 0.55:
            sx_ = x0 + 1.4 if signs == 0 else x1 - 1.4
            box(sx_ - 0.6, y - 1.1, za + 1.6, sx_ + 0.6, y - 0.6, za + 5.6, (0.04, 0.04, 0.05), facet=False)
            beam((sx_, y, za + 5.0), (sx_, y - 1.0, za + 5.0), 0.1, (0.1, 0.1, 0.12))
            col = DR2.choice([(1.0, 0.16, 0.54), (0.16, 0.83, 1.0), (0.54, 0.24, 1.0)])
            quad_y(NEON, sx_ - 0.45, za + 1.8, sx_ + 0.45, za + 5.4, y - 1.12, tuple(v * 0.9 for v in col))
            signs += 1
    for side, xx in ((-1, x0 - 0.3), (1, x1 + 0.3)):
        for yy in (y + 7.0, y + 10.0):
            beam((xx, yy, 0.0), (xx, yy, top), DR2.uniform(0.35, 0.55), (0.24, 0.23, 0.27))
    zt = top + 0.8
    for k in range(DR2.randint(2, 4)):
        fx, fy = DR2.uniform(x0 + 1.5, x1 - 1.5), y + DR2.uniform(5.0, 10.5)
        tube((fx, fy, zt), (fx, fy, zt + 0.9), 0.8, (0.32, 0.32, 0.36), n=8)
        quad_y(SOLID, fx - 0.5, zt + 0.95, fx + 0.5, zt + 0.96, fy, (0.05, 0.05, 0.06))


for _l in range(8):
    with (Sink() if _l == DRUM_COL else _nullctx()):
        greeble_column(_l)

# ------------------------------------------------------------------ alley cables (behind the links, clear of rooms)
set_sem(DRESS_SEM, 0, 0)
for _l in range(7):
    xa, xb = LY["cols"][str(_l)][1], LY["cols"][str(_l + 1)][0]
    ya = max(LY["dy"][_l], LY["dy"][_l + 1]) + 9.0
    zmax = min(LY["storeys"][str(_l)], LY["storeys"][str(_l + 1)]) * FH - 1.0
    busy = []
    for i, n in LY["nodes"].items():
        if n["layer"] in (_l, _l + 1):
            busy.append((n["room"][1] - 1.5, n["room"][3] + 1.5))
    for e in LY["edges"]:
        for q in e["path"]:
            if xa - 1 <= q[0] <= xb + 1:
                busy.append((q[2] - 2.5, q[2] + 2.5))
    made = 0
    for _t in range(40):
        if made >= 8:
            break
        z = DR2.uniform(3.0, zmax)
        if any(a <= z <= b for a, b in busy):
            continue
        sag = (xb - xa) * DR2.uniform(0.03, 0.06)
        yy = ya + DR2.uniform(-1.0, 1.5)
        pts = [(xa + (xb - xa) * t / 10, yy, z - sag * math.sin(math.pi * t / 10)) for t in range(11)]
        for p0, p1 in zip(pts, pts[1:]):
            beam(p0, p1, 0.1, (0.03, 0.03, 0.035))
        made += 1

# ------------------------------------------------------------------ scale: 3 towers out of frame, 2 megastructures
set_sem(0.6, 0, 0)
for (tx0, tx1, ty, th, bl) in ((16.0, 28.0, 58.0, 190.0, "blade_hotel"), (140.0, 152.0, 62.0, 210.0, "blade_clinic"),
                               (-48.0, -34.0, 52.0, 175.0, "blade_solace")):
    c = (0.07, 0.065, 0.085)
    box(tx0, ty, 0, tx1, ty + 12, th, c, facet=False)
    box(tx0 + 1.5, ty + 1.5, th, tx1 - 1.5, ty + 10.5, th + 20, c, facet=False)
    for z in range(30, int(th), 44):          # short corner markers, not full-width lines
        quad_y(NEON, tx1 - 1.4, z, tx1 - 0.3, z + 2.2, ty - 0.06, (0.16, 0.83, 1.0) if z % 88 else (1.0, 0.16, 0.54))
    ad_plane(bl, tx1 - 2.6, ty - 0.08, 70.0, 4.0, 16.0, k=1.8, flood=False)
set_sem(0.85, 0, 0)
for (mx0, mx1, my, mh, ads) in ((22.0, 70.0, 120.0, 290.0, ("solace", "meridian")),
                                (124.0, 166.0, 140.0, 320.0, ("halcyon", "noodle"))):
    c = (0.05, 0.045, 0.065)
    if mx0 < 50:      # r2: the critique's drum megastructure (stepped drums), its ads on the front
        _cx, _r = (mx0 + mx1) / 2, (mx1 - mx0) / 2 + 2
        prism(fp_circle(_cx, my + _r, _r, n=40), 0, mh * 0.55, c)
        prism(fp_circle(_cx, my + _r, _r * 0.8, n=40), mh * 0.55, mh * 0.8, c)
        prism(fp_circle(_cx, my + _r, _r * 0.56, n=40), mh * 0.8, mh, c)
        for _z in (mh * 0.55, mh * 0.8):
            ring_trim(fp_circle(_cx, my + _r, _r * (0.8 if _z > mh * 0.6 else 1.0) + 0.3, n=40), _z - 0.6,
                      (0.28, 0.12, 0.3), 0.8, front_only=True, cy=my + _r)
    else:
        box(mx0, my, 0, mx1, my + 40, mh * 0.55, c, facet=False)
        box(mx0 + 5, my + 4, mh * 0.55, mx1 - 5, my + 36, mh * 0.8, c, facet=False)
        box(mx0 + 11, my + 8, mh * 0.8, mx1 - 11, my + 32, mh, c, facet=False)
    for k_, z in enumerate((mh * 0.22, mh * 0.42)):
        w = (mx1 - mx0) * 0.62
        ad_plane(ads[k_], (mx0 + mx1) / 2, my - 0.3, z, w, w * 9 / 16, k=1.6)
# box billboards on the route-row billboard arch (col 5) and the mid-row billboard frame (both off the calm zone)
_bx0, _bx1 = LY["cols"]["5"]
_bzt = LY["storeys"]["5"] * FH + 0.8
# the arch billboard is built with the column's depth offset: its face is at y = 3.0 + DY - 0.6
ad_plane("volta", (_bx0 + _bx1) / 2, 3.0 + LY["dy"][5] - 0.75, _bzt + 8.3, 14.0, 7.9, k=1.6)
ad_plane("orbital", 72.0, 17.2, 61.3, 14.0, 7.9, k=1.6)
# the Orbital holo panel sits right under its globe and above the VOLTA board, so globe + name read as one ad
ad_plane("holo_orbital", 128.0, 40.0, 75.0, 11.0, 6.2, k=1.6, holo=True)
# a readable Halcyon holo billboard where the helix was (left, mid row)
ad_plane("holo_halcyon", -38.0, 30.0, 66.0, 16.0, 9.0, k=1.6, holo=True)
for _o in list(TEXT_OBJS):
    if _o.type == "FONT" and _o.data.body == "ORBITAL" and abs(_o.location[0] - 72.0) < 1 or (
            _o.type == "FONT" and _o.data.body == "ORBITAL" and abs(_o.location[0] - 128.0) < 1):
        TEXT_OBJS.remove(_o)
        bpy.data.objects.remove(_o, do_unlink=True)

# ------------------------------------------------------------------ near layer: 2 near-black silhouettes at the edges
set_sem(0.95, 0, 0)
_nb = (0.012, 0.011, 0.016)
# storyboard: each silhouette is its own foreground object, so the occlusion rule can hide it (it stood 2 BU from the
# DECISION camera and blacked out half its frame)
_nl, _nr = Acc("near_l"), Acc("near_r")
beam((-8.0, -75.0, 0.0), (-8.0, -75.0, 42.0), 1.0, _nb, acc=_nl)
box(-15.0, -76.0, 24.0, -1.0, -74.5, 36.0, _nb, facet=False, acc=_nl)
beam((-8.0, -75.0, 30.0), (-1.0, -75.0, 30.0), 0.4, _nb, acc=_nl)
for gx in (198.0, 214.0):
    beam((gx, -82.0, 0.0), (gx, -82.0, 34.0), 1.2, _nb, acc=_nr)
beam((196.0, -82.0, 33.0), (216.0, -82.0, 33.0), 1.4, _nb, acc=_nr)
box(200.0, -83.0, 26.0, 212.0, -81.5, 32.5, _nb, facet=False, acc=_nr)
for _nm_, _a_ in (("near_l", _nl), ("near_r", _nr)):
    _o_ = _a_.obj(TOON, "FG_%s_s" % _nm_)
    SOLID_OBJS.append(_o_)
    FG_OBJS[_nm_] = [_o_]

# ------------------------------------------------------------------ sky traffic: two lanes only (designer: the far lane
# read as glitch lines); far roof trims are dimmed in mats_aaa (CLASS_EMIT far)
for _objs, _x0, _y, _z, _sp in TRAFFIC:
    if _objs[0].name.startswith("trafficbody_2_"):
        for _o in _objs:
            _o.hide_render = True
# ------------------------------------------------------------------ the front sky lane: 1.5x trails
TRAILM_HI = mat_air2("trail_hi", 6.0)
for _ob in ATMOS_OBJS:
    if _ob.name.startswith("traffictrail_0_"):
        _ob.data.materials[0] = TRAILM_HI
print("dress2: ads", len(AD_OBJS), flush=True)

# ------------------------------------------------------------------ a last dark skyline wall (y 600): the haze glowed
# through the open slots of the far layers as pale "pills" at the frame top; this wall closes them, all silhouette
set_sem(0.85, 0, 0)
_wx = -160.0
while _wx < 420.0:
    _ww = DR2.uniform(36.0, 62.0)
    box(_wx, 600.0, 0.0, _wx + _ww, 640.0, DR2.uniform(330.0, 460.0), (0.03, 0.028, 0.04), facet=False)
    _wx += _ww + DR2.uniform(0.0, 6.0)
