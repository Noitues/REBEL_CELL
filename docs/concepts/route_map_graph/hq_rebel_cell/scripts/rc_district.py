"""Rebel Cell: the district builder shared by the option builds (Blender side, through the kit's K helpers).

The Cell's district (bible 4.4, round 34): a normal street grid of 12 BU blocks over the fist's box; NO landmark
tower. Every block carries a category in its face attribute k: 0 plain, 1 fist, 2 a fist LINE (finger split, thumb
edge, cuff: windowless after the blackout), 3 the blackout RING. One window shader reads two per-frame values:
  SEQ   0 before: an ordinary district, the fist barely hinted (red_before_p of the fist's lit windows red, dim)
        0..1 the BLACKOUT (round 34): the sector washes out (every window lit), then the ring and the lines go dark
        1..2 the red SPREADS from the palm outward through the fist blocks (a front at (SEQ - 1) * spread_r)
        2..3 the full fist: red_full_p of the fist's windows red, at full strength
  PULSE the kill-switch moment: the fist's LINE blocks glow red along their faces (a pulse along the hand's lines)
The red stays a lit-window effect (never a wash or a fog colour). Seeds: preset fist.seed (heights, cells).
"""
import json
import math
import os
import random


def build(K, keep_free=None, cut_y=None, low_near=None):
    """keep_free(x, y) -> True to leave a cell empty (streets, squares); low_near: [(x, y, z)] rooms: blocks within
    14 BU in x and 0..45 BU south of a room are capped below it (no tower ever hides a room from the camera); cut_y:
    the section cut (option A): no blocks south of it. Returns (accs dict, SEQ node, PULSE node, rooftops {room: z})."""
    CP, LH, pal = K.CP, K.LH, K.pal
    FI = CP["fist"]
    PX, PY = CP["palm"]
    rr = random.Random(FI["seed"])
    m, nt = K.new_mat("district")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = K.attr(nt, "col")
    kf = K.attr(nt, "k")
    pw = K.attr(nt, "pwo", "OBJECT")
    g, ps, ns = K.pos_sep(nt)
    M = K.mth

    def eq(v, c):
        return M(nt, "LESS_THAN", M(nt, "ABSOLUTE", M(nt, "SUBTRACT", v, c)), 0.5)
    isF, isL, isR = eq(kf.outputs["Fac"], 1.0), eq(kf.outputs["Fac"], 2.0), eq(kf.outputs["Fac"], 3.0)
    seq = nt.nodes.new("ShaderNodeValue")
    seq.name = "SEQ"
    seq.outputs[0].default_value = 3.0
    pulse = nt.nodes.new("ShaderNodeValue")
    pulse.name = "PULSE"
    pulse.outputs[0].default_value = 0.0
    S, PU = seq.outputs[0], pulse.outputs[0]
    u = M(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
    su, sv = 1.6, 2.6
    cu = M(nt, "FLOOR", M(nt, "DIVIDE", u, su))
    cv = M(nt, "FLOOR", M(nt, "DIVIDE", ps.outputs["Z"], sv))
    fu = M(nt, "FRACT", M(nt, "DIVIDE", u, su))
    fv = M(nt, "FRACT", M(nt, "DIVIDE", ps.outputs["Z"], sv))
    wm = M(nt, "MULTIPLY", M(nt, "MULTIPLY", M(nt, "GREATER_THAN", fu, 0.28), M(nt, "LESS_THAN", fu, 0.72)),
           M(nt, "MULTIPLY", M(nt, "GREATER_THAN", fv, 0.32), M(nt, "LESS_THAN", fv, 0.70)))
    vert = M(nt, "LESS_THAN", M(nt, "ABSOLUTE", ns.outputs["Z"]), 0.3)
    cid = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(cu, cid.inputs[0])
    nt.links.new(cv, cid.inputs[1])
    nt.links.new(M(nt, "FLOOR", M(nt, "DIVIDE", M(nt, "SUBTRACT", ps.outputs["X"], ps.outputs["Y"]), 7.0)), cid.inputs[2])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(cid.outputs[0], wn.inputs["Vector"])
    wsep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(wn.outputs["Color"], wsep.inputs[0])
    # the sequence terms
    wash = M(nt, "MULTIPLY", K.smooth(nt, S, 0.0, 0.45), M(nt, "SUBTRACT", 1.0, K.smooth(nt, S, 0.55, 1.0)))
    dark = M(nt, "MULTIPLY", K.smooth(nt, S, 0.55, 1.0), M(nt, "ADD", isL, isR))
    dx = M(nt, "SUBTRACT", ps.outputs["X"], PX)
    dy = M(nt, "SUBTRACT", ps.outputs["Y"], PY)
    dist = M(nt, "SQRT", M(nt, "ADD", M(nt, "MULTIPLY", dx, dx), M(nt, "MULTIPLY", dy, dy)))
    front = M(nt, "MULTIPLY", M(nt, "SUBTRACT", S, 1.0), LH["spread_r"])
    spread = M(nt, "SUBTRACT", 1.0, K.smooth(nt, M(nt, "SUBTRACT", dist, front), -25.0, 0.0))     # 1 behind the front
    full = K.smooth(nt, S, 2.0, 3.0)
    V3 = K.HZ.get("v3") or {}
    redmix = nt.nodes.new("ShaderNodeValue")             # v3: red as an ACCENT in the netrun section (designer note 1)
    redmix.name = "REDMIX"
    redmix.outputs[0].default_value = float(V3.get("red_mix", 1.0))
    RM = redmix.outputs[0]
    red_p = M(nt, "MULTIPLY", isF, M(nt, "ADD", LH["red_before_p"],
                                      M(nt, "MULTIPLY", spread, LH["red_full_p"] - LH["red_before_p"])))
    red_p = M(nt, "MULTIPLY", red_p, RM)
    is_red = M(nt, "LESS_THAN", wsep.outputs[1], red_p)
    p_lit = M(nt, "ADD", LH["win_p"], M(nt, "MULTIPLY", wash, 0.6))
    p_lit = M(nt, "ADD", p_lit, M(nt, "MULTIPLY", M(nt, "MULTIPLY", isF, spread), 0.5))
    FO = V3.get("falloff") if (V3 and cut_y is not None) else None
    depth = None
    if FO:
        # v3 netrun (PIPELINE_SPEC 13, density.falloff): fewer, warmer, dimmer windows further behind the section; seeded
        # PATCHES of fully dark blocks (dark_block_share); the frontage rows stay full
        depth = K.smooth(nt, ps.outputs["Y"], cut_y + FO["near_d"], cut_y + FO["far_d"])
        p_lit = M(nt, "MULTIPLY", p_lit, M(nt, "SUBTRACT", 1.0, M(nt, "MULTIPLY", depth, 1.0 - FO["far_p"])))
        bcell = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(M(nt, "FLOOR", M(nt, "DIVIDE", ps.outputs["X"], FI["cell"])), bcell.inputs[0])
        nt.links.new(M(nt, "FLOOR", M(nt, "DIVIDE", ps.outputs["Y"], FI["cell"])), bcell.inputs[1])
        pn = K.nn(nt, "ShaderNodeTexNoise", Scale=FO["patch_scale"], Detail=1.0)
        nt.links.new(bcell.outputs[0], pn.inputs["Vector"])
        dark_b = M(nt, "MULTIPLY", M(nt, "LESS_THAN", pn.outputs["Fac"], FO["patch_thr"]),
                   M(nt, "GREATER_THAN", ps.outputs["Y"], cut_y + FO["patch_from"]))
    lit = M(nt, "LESS_THAN", wn.outputs["Value"], p_lit)
    roof = M(nt, "GREATER_THAN", ns.outputs["Z"], 0.7)
    rgrid = M(nt, "MULTIPLY", M(nt, "GREATER_THAN", M(nt, "FRACT", M(nt, "DIVIDE", ps.outputs["X"], 2.4)), 0.55),
              M(nt, "GREATER_THAN", M(nt, "FRACT", M(nt, "DIVIDE", ps.outputs["Y"], 2.4)), 0.55))
    sky = M(nt, "MULTIPLY", M(nt, "MULTIPLY", rgrid, roof), M(nt, "MULTIPLY", isF, M(nt, "MAXIMUM", spread, 0.0)))
    sky = M(nt, "MULTIPLY", sky, M(nt, "LESS_THAN", wsep.outputs[2], RM))     # v3: the skylights thin out with it too
    is_red = M(nt, "MAXIMUM", is_red, sky)
    on = M(nt, "MULTIPLY", M(nt, "MAXIMUM", M(nt, "MULTIPLY", wm, vert), sky), M(nt, "MAXIMUM", lit, is_red))
    on = M(nt, "MULTIPLY", on, M(nt, "SUBTRACT", 1.0, dark))
    if FO:
        on = M(nt, "MULTIPLY", on, M(nt, "SUBTRACT", 1.0, dark_b))
    plain_c = K.mixc(nt, M(nt, "GREATER_THAN", wsep.outputs[0], 0.62), (1.0, 0.66, 0.40), (0.82, 0.90, 1.0))
    if FO:
        plain_c = K.mixc(nt, M(nt, "MULTIPLY", depth, FO["warm"]), plain_c, (1.0, 0.58, 0.32))
    RED = pal("cell_red")
    wcol = K.mixc(nt, is_red, plain_c, RED)
    red_k = M(nt, "ADD", LH["red_before_k"], M(nt, "MULTIPLY", M(nt, "ADD", M(nt, "MULTIPLY", spread, 0.6),
                                                                  M(nt, "MULTIPLY", full, 0.4)),
                                                 LH["red_k"] - LH["red_before_k"]))
    red_k = M(nt, "MULTIPLY", red_k, float(V3.get("red_k_mix", 1.0)))
    win_k = float(V3.get("win_k_net", LH["win_k"])) if (V3 and cut_y is not None) else LH["win_k"]
    k_win = M(nt, "ADD", M(nt, "MULTIPLY", M(nt, "SUBTRACT", 1.0, is_red), win_k), M(nt, "MULTIPLY", is_red, red_k))
    if FO:
        # a per-window brightness spread (not every window at one value) and the dimming with depth
        k_win = M(nt, "MULTIPLY", k_win, M(nt, "ADD", 0.55, M(nt, "MULTIPLY", wsep.outputs[2], 0.7)))
        k_win = M(nt, "MULTIPLY", k_win, M(nt, "SUBTRACT", 1.0, M(nt, "MULTIPLY", depth, FO["far_dim"])))
    k_win = M(nt, "MULTIPLY", k_win, M(nt, "ADD", 1.0, M(nt, "MULTIPLY", wash, LH["wash_k"])))
    strength = M(nt, "MULTIPLY", M(nt, "MULTIPLY", on, k_win), pw.outputs["Fac"])
    # the kill-switch pulse: the LINE blocks' faces glow red
    pl = M(nt, "MULTIPLY", M(nt, "MULTIPLY", M(nt, "MULTIPLY", isL, vert), PU), LH["pulse_k"])
    strength = M(nt, "ADD", strength, pl)
    wcol = K.mixc(nt, M(nt, "MINIMUM", M(nt, "MULTIPLY", M(nt, "MULTIPLY", isL, PU), 4.0), 1.0), wcol, RED)
    n1 = K.nn(nt, "ShaderNodeTexNoise", Scale=0.3, Detail=6.0, Roughness=0.65)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    nt.links.new(K.vsc(nt, col.outputs["Color"], M(nt, "ADD", 0.7, M(nt, "MULTIPLY", n1.outputs["Fac"], 0.6))),
                 b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.5
    nt.links.new(wcol, b.inputs["Emission Color"])
    nt.links.new(strength, b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], out.inputs[0])
    DIST = K.Acc("district", m, 1, K.COLL["compound"])

    MJ = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch",
                                     CP["fist"].get("mask", "fist_mask.json"))))
    MW, MG = MJ["n"], MJ["grid"]
    fcx, fcy = (FI["x"][0] + FI["x"][1]) / 2, (FI["y"][0] + FI["y"][1]) / 2

    def cat(x, y):
        """A block's category from 5 samples over its footprint (v2 r2: a LINE at the centre or on 3+ samples, then the
        fist by majority: the fingers stay as wide as the crest's, the gaps one street-line wide; was: a line anywhere)."""
        cs = [cat1(x + dx, y + dy) for dx, dy in ((0, 0), (-3.5, -3.5), (3.5, -3.5), (3.5, 3.5), (-3.5, 3.5))]
        if cs[0] == 2 or cs.count(2) >= 3:
            return 2
        if cs[0] == 1 or cs.count(1) >= 3:
            return 1
        return 3 if 3 in cs else 0

    def cat1(x, y):
        mx = int((x - FI["x"][0]) / (FI["x"][1] - FI["x"][0]) * MW)
        my = int((FI["y"][1] - y) / (FI["y"][1] - FI["y"][0]) * MW)
        if 0 <= mx < MW and 0 <= my < MW and MG[my][mx]:
            return MG[my][mx]
        r = math.hypot(x - fcx, y - fcy)
        return 3 if FI["ring"][0] <= r <= FI["ring"][1] else 0

    cell, st_ = FI["cell"], FI["street"]
    roofs = {}
    BLOCKS = []                                           # v3: (x0, y0, x1, y1, top) for the NYC roof clutter
    K.HZ["_blocks"] = BLOCKS
    x = FI["x"][0] - 90.0
    n_by = {0: 0, 1: 0, 2: 0, 3: 0}
    while x < FI["x"][1] + 90.0:
        y = FI["y"][0] - 90.0
        while y < FI["y"][1] + 90.0:
            cx, cy = x + cell / 2, y + cell / 2
            y += cell
            if cut_y is not None and cy < cut_y:
                continue
            if keep_free and keep_free(cx, cy):
                continue
            c = cat(cx, cy)
            h = rr.uniform(14.0, 40.0) + (6.0 if c in (1, 2) else 0.0)
            for (rx, ry, rz) in (low_near or []):
                if abs(rx - cx) < 9.0 and abs(ry + 5.0 - cy) < 8.0 and rz > 5.0:
                    h = rz                                # the room's own roof
                elif abs(rx - cx) < 16.0 and 0.0 < ry - cy < 48.0:
                    h = min(h, max(6.0, rz - 6.0))        # never in front of a room
            w = cell - st_
            colr = (0.075, 0.07, 0.08) if rr.random() < 0.7 else (0.09, 0.08, 0.08)
            wx = w
            if cut_y is not None and V3 and cy < cut_y + V3.get("district_touch_d", 0.0):
                wx = cell                                 # v3: the buildings touch (no N-S slots seen from the street)
            K.box(DIST, cx - wx / 2, cy - w / 2, 0.0, cx + wx / 2, cy + w / 2, h, colr, k=float(c))
            BLOCKS.append((cx - wx / 2, cy - w / 2, cx + wx / 2, cy + w / 2, h))
            n_by[c] += 1
        x += cell
    K.box(K.A["ground"], FI["x"][0] - 100, (cut_y if cut_y is not None else FI["y"][0] - 100), -0.02, FI["x"][1] + 100,
          FI["y"][1] + 100, 0.0, (0.07, 0.07, 0.075), k=0.0)
    K.log("district blocks", n_by)
    return {"district": DIST}, seq, pulse, cat
