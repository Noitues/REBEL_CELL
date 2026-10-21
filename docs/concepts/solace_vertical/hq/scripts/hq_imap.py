"""HQ Solace v4 option B: the INTERIOR MAPPING shader (Blender node graph; the Godot port is in NOTES.md).

A window is a flat, level, plumb oval in its own plane (never mapped along the tube). Behind it the shader ray-casts a
VIRTUAL BOX (half width HU, depth D, floor ZB .. ceiling ZT, in the window's own frame u / dz / depth) from the view
ray and samples the atlas tile of the face it hits (back, left, right, floor, ceiling), true aspect, 40 px per BU.

Per-corner data (vertex colours, set by hq_build):
  loc  (u + 32, dz + 32, depth + 64)       the patch point in the window frame (depth = along the window normal from C)
  frm  (tw.x + 2, tw.y + 2, nw.x + 2, nw.y + 2 in alpha)   the window's level major axis and normal (world xy)
  vst  (variant row, lit 0/1, blind 0..1)    atlas row, lights on, blinds drawn
  tnt  (r, g, b)                              a per-window light tint
The patch may follow the tube skin (so it never intersects the wall); the ray is first carried to the window plane
(depth DP) and only then enters the box, so the picture is flat, level and unstretched whatever the patch shape.
"""
HU, D, H, ZB, DP = 10.0, 10.5, 8.4, -3.15, 1.45
ROW_W, ROW_H = 3240.0, 420.0
TILE = dict(back=(0.0, 800.0, 336.0), left=(800.0, 420.0, 336.0), right=(1220.0, 420.0, 336.0),
            floor=(1640.0, 800.0, 420.0), ceil=(2440.0, 800.0, 420.0))


def material(K, atlas_path, nv, k_emit, name="imap"):
    import bpy
    M_, nt = K.new_mat(name)
    mth, attr = K.mth, K.attr

    def sep_color(sock):
        n = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(sock, n.inputs[0])
        return n.outputs[0], n.outputs[1], n.outputs[2]

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    a_loc, a_frm, a_vst, a_tnt = attr(nt, "loc"), attr(nt, "frm"), attr(nt, "vst"), attr(nt, "tnt")
    lr, lg, lb = sep_color(a_loc.outputs["Color"])
    u0, dz0, dP = mth(nt, "SUBTRACT", lr, 32.0), mth(nt, "SUBTRACT", lg, 32.0), mth(nt, "SUBTRACT", lb, 64.0)
    fr_, fg_, fb_ = sep_color(a_frm.outputs["Color"])
    twx, twy, nwx = mth(nt, "SUBTRACT", fr_, 2.0), mth(nt, "SUBTRACT", fg_, 2.0), mth(nt, "SUBTRACT", fb_, 2.0)
    nwy = mth(nt, "SUBTRACT", a_frm.outputs["Alpha"], 2.0)
    vr, vg, vb = sep_color(a_vst.outputs["Color"])
    var, lit, blind = mth(nt, "ROUND", vr), vg, vb

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    inv = nt.nodes.new("ShaderNodeVectorMath")
    inv.operation = "SCALE"
    nt.links.new(geo.outputs["Incoming"], inv.inputs[0])
    inv.inputs["Scale"].default_value = -1.0
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(inv.outputs[0], nrm.inputs[0])
    sx = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nrm.outputs[0], sx.inputs[0])
    Vx, Vy, Vz = sx.outputs[0], sx.outputs[1], sx.outputs[2]
    Vu = mth(nt, "ADD", mth(nt, "MULTIPLY", Vx, twx), mth(nt, "MULTIPLY", Vy, twy))
    Vn = mth(nt, "ADD", mth(nt, "MULTIPLY", Vx, nwx), mth(nt, "MULTIPLY", Vy, nwy))
    a = mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", Vn, -1.0), 0.03)          # speed into the room (along -normal)
    t0 = mth(nt, "DIVIDE", mth(nt, "SUBTRACT", dP, DP), a)               # carry the ray to the window plane
    u1 = mth(nt, "ADD", u0, mth(nt, "MULTIPLY", Vu, t0))
    z1 = mth(nt, "ADD", dz0, mth(nt, "MULTIPLY", Vz, t0))
    # --- the box: back wall, side wall, floor / ceiling
    tb = mth(nt, "DIVIDE", D, a)
    su = mth(nt, "SUBTRACT", mth(nt, "MULTIPLY", mth(nt, "GREATER_THAN", Vu, -1e-6), 2.0), 1.0)      # +1 / -1
    Vus = mth(nt, "MULTIPLY", su, mth(nt, "MAXIMUM", mth(nt, "ABSOLUTE", Vu), 1e-4))
    tu = mth(nt, "DIVIDE", mth(nt, "SUBTRACT", mth(nt, "MULTIPLY", su, HU), u1), Vus)
    up = mth(nt, "GREATER_THAN", Vz, -1e-6)
    sz = mth(nt, "SUBTRACT", mth(nt, "MULTIPLY", up, 2.0), 1.0)
    Vzs = mth(nt, "MULTIPLY", sz, mth(nt, "MAXIMUM", mth(nt, "ABSOLUTE", Vz), 1e-4))
    zlim = mth(nt, "ADD", mth(nt, "MULTIPLY", up, ZB + H), mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, up), ZB))
    tz = mth(nt, "DIVIDE", mth(nt, "SUBTRACT", zlim, z1), Vzs)
    wb = mth(nt, "MULTIPLY", mth(nt, "LESS_THAN", tb, mth(nt, "ADD", tu, 1e-6)),
             mth(nt, "LESS_THAN", tb, mth(nt, "ADD", tz, 1e-6)))
    wu = mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, wb), mth(nt, "LESS_THAN", tu, mth(nt, "ADD", tz, 1e-6)))
    wz = mth(nt, "SUBTRACT", mth(nt, "SUBTRACT", 1.0, wb), wu)
    t = mth(nt, "MINIMUM", tb, mth(nt, "MINIMUM", mth(nt, "MAXIMUM", tu, 0.0), mth(nt, "MAXIMUM", tz, 0.0)))
    hu_ = mth(nt, "ADD", u1, mth(nt, "MULTIPLY", Vu, t))
    hz = mth(nt, "ADD", z1, mth(nt, "MULTIPLY", Vz, t))
    hd = mth(nt, "MULTIPLY", a, t)                                          # depth into the box, 0 .. D

    def clamp(v):
        return mth(nt, "MINIMUM", mth(nt, "MAXIMUM", v, 0.004), 0.996)
    htot = ROW_H * nv

    def atlas_uv(x0, w, h, s, ty):
        """x0 / w / h: tile pixels (x0 may be a socket); s, ty in 0..1 (ty up)."""
        xs = mth(nt, "ADD", x0, mth(nt, "MULTIPLY", clamp(s), w))
        px_u = mth(nt, "DIVIDE", xs, ROW_W)
        rowpx = mth(nt, "ADD", mth(nt, "MULTIPLY", var, ROW_H), mth(nt, "SUBTRACT", h, mth(nt, "MULTIPLY", clamp(ty), h)))
        v = mth(nt, "SUBTRACT", 1.0, mth(nt, "DIVIDE", rowpx, htot))
        c = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(px_u, c.inputs[0])
        nt.links.new(v, c.inputs[1])
        return c.outputs[0]
    img = bpy.data.images.load(atlas_path)

    def tex(uv):
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = img
        tn.interpolation = "Linear"
        tn.extension = "EXTEND"
        nt.links.new(uv, tn.inputs["Vector"])
        return tn.outputs["Color"]
    ty_wall = mth(nt, "DIVIDE", mth(nt, "SUBTRACT", hz, ZB), H)
    back = tex(atlas_uv(TILE["back"][0], TILE["back"][1], TILE["back"][2],
                        mth(nt, "DIVIDE", mth(nt, "SUBTRACT", HU, hu_), 2 * HU), ty_wall))
    left_ = mth(nt, "LESS_THAN", su, 0.0)
    wx0 = mth(nt, "ADD", mth(nt, "MULTIPLY", left_, TILE["left"][0]),
              mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, left_), TILE["right"][0]))
    ws = mth(nt, "ADD", mth(nt, "MULTIPLY", left_, mth(nt, "DIVIDE", mth(nt, "SUBTRACT", D, hd), D)),
             mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, left_), mth(nt, "DIVIDE", hd, D)))
    wall = tex(atlas_uv(wx0, TILE["left"][1], TILE["left"][2], ws, ty_wall))
    fl = mth(nt, "SUBTRACT", 1.0, up)
    fx0 = mth(nt, "ADD", mth(nt, "MULTIPLY", fl, TILE["floor"][0]), mth(nt, "MULTIPLY", up, TILE["ceil"][0]))
    fty = mth(nt, "ADD", mth(nt, "MULTIPLY", fl, mth(nt, "SUBTRACT", 1.0, mth(nt, "DIVIDE", hd, D))),
              mth(nt, "MULTIPLY", up, mth(nt, "DIVIDE", hd, D)))
    fc = tex(atlas_uv(fx0, TILE["floor"][1], TILE["floor"][2], mth(nt, "DIVIDE", mth(nt, "ADD", hu_, HU), 2 * HU), fty))
    col = K.mixc(nt, wu, back, wall)
    col = K.mixc(nt, wz, K.mixc(nt, mth(nt, "MINIMUM", mth(nt, "ADD", wu, wz), 1.0), back, col), fc) \
        if False else K.mixc(nt, wz, K.mixc(nt, wu, back, wall), fc)
    # --- a slight frosted layer + blinds drawn from the top (slats) + lights on / off
    col = K.mixc(nt, 0.10, col, (0.62, 0.66, 0.66))
    hb = mth(nt, "SUBTRACT", 4.2, mth(nt, "MULTIPLY", blind, 7.0))
    top = mth(nt, "GREATER_THAN", z1, hb)
    slat = K.smooth(nt, mth(nt, "FRACT", mth(nt, "MULTIPLY", z1, 2.5)), 0.30, 0.62)
    bm = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", top, mth(nt, "GREATER_THAN", blind, 0.02)),
             mth(nt, "ADD", 0.45, mth(nt, "MULTIPLY", slat, 0.5)))
    col = K.mixc(nt, bm, col, (0.42, 0.38, 0.30))
    tint = a_tnt.outputs["Color"]
    colt = nt.nodes.new("ShaderNodeMix")
    colt.data_type = "RGBA"
    colt.blend_type = "MULTIPLY"
    colt.inputs["Factor"].default_value = 1.0
    nt.links.new(col, colt.inputs[6])
    nt.links.new(tint, colt.inputs[7])
    ks = mth(nt, "ADD", 0.10, mth(nt, "MULTIPLY", lit, 0.9))
    pw = attr(nt, "pwo", "OBJECT")
    bsdf.inputs["Base Color"].default_value = (0.02, 0.03, 0.03, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.30
    bsdf.inputs["Coat Weight"].default_value = 0.4
    bsdf.inputs["Coat Roughness"].default_value = 0.10
    nt.links.new(colt.outputs[2], bsdf.inputs["Emission Color"])
    nt.links.new(mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", ks, pw.outputs["Fac"]), k_emit), bsdf.inputs["Emission Strength"])
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return M_
