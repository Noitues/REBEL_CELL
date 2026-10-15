"""AAA-2 only: the route as glowing holo-projections in world space (exec'd from scene_aaa.py after the dressing).

Each edge of the run becomes an emissive tube along its 3D path (the same path the overlay cable is projected from), so
it lights the haze, reflects in the wet street and sits in the world. State colours are the locked overlay ones:
lime walked (solid), orange next options (dashed), white ahead (dashed), grey past (thin, faint). A thin bright core
plus a wider translucent sheath gives the holo look. The 2D overlay cables are still drawn on top at reduced strength,
because the tunnel and some lift lanes run behind structure (readability first).
"""

HOLO_EDGE = JOB.get("edge_states", {})
SRGB = lambda c: tuple((v / 255.0) ** 2.2 for v in c)  # noqa: E731
HR_STYLE = {
    #          colour (sRGB)       core r  sheath r  core k  sheath k  dash on/off (BU)
    "walked": ((212, 255, 0), 0.20, 0.55, 14.0, 1.4, None),
    "option": ((255, 140, 26), 0.22, 0.60, 16.0, 1.6, (2.2, 1.1)),
    "future": ((242, 246, 255), 0.12, 0.38, 7.0, 0.7, (1.4, 1.0)),
    "grey":   ((122, 118, 134), 0.07, 0.20, 1.2, 0.15, None),
}
HOLO_ROUTE_OBJS = []


def mat_route(name, k, alpha):
    m = bpy.data.materials.new(name)
    for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, prop, val)
        except (AttributeError, TypeError):
            pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = attr(nt, "col")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = k
    nt.links.new(col.outputs["Color"], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def dash_segments(pts, on, off):
    segs, cur, t, state_on = [], [Vector(pts[0])], 0.0, True
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        s = 0.0
        while s < L - 1e-6:
            lim = (on if state_on else off) - t
            step = min(lim, L - s)
            p = a.lerp(b, (s + step) / L)
            if state_on:
                cur.append(p)
            s += step
            t += step
            if t >= (on if state_on else off) - 1e-6:
                if state_on and len(cur) > 1:
                    segs.append(cur)
                state_on = not state_on
                t = 0.0
                cur = [p]
    if state_on and len(cur) > 1:
        segs.append(cur)
    return segs


if LOOK == "real" and HOLO_EDGE:
    for state, (c, rc, rs, kc, ks, dash) in HR_STYLE.items():
        core, sheath = Acc("hr_core_" + state), Acc("hr_sheath_" + state)
        set_sem(0.0, 0, 0)
        for e in LY["edges"]:
            if HOLO_EDGE.get("%s|%s" % (e["a"], e["b"])) != state:
                continue
            path = [tuple(q) for q in e["path"]]
            pieces = dash_segments(path, *dash) if dash else [[Vector(q) for q in path]]
            for pc in pieces:
                for a, b in zip(pc, pc[1:]):
                    tube(a, b, rc, SRGB(c), acc=core, n=6, bid=(0, 0, 0))
                    tube(a, b, rs, SRGB(c), acc=sheath, n=8, bid=(0, 0, 0))
        if core.n:
            HOLO_ROUTE_OBJS.append(core.obj(mat_route("hr_core_" + state, kc, 0.95), "holo_route_core_" + state))
            HOLO_ROUTE_OBJS.append(sheath.obj(mat_route("hr_sheath_" + state, ks, 0.35), "holo_route_sheath_" + state))
    HOLO_OBJS.extend(HOLO_ROUTE_OBJS)
    print("holo route objects", len(HOLO_ROUTE_OBJS), flush=True)
