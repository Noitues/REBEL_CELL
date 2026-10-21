"""Street-graffiti restyle, shared by every panel. Runs INSIDE Blender after a base pipeline has built its scene and before
it renders (the graf_blender_*.py wrappers patch the call in at run time; nothing on disk in the base pipelines changes).

What it does (see BRIEF.md and RESEARCH.md):
  paint   every facade material gets the two seeded graffiti atlases (graf_atlas.py) box-projected in world space:
          the street layer (pieces, throw-ups, posters, tags) dense from the ground to `street_z`, thinning above it;
          the heaven layer (blockbusters, big roller tags) over the whole height at a larger scale. Paint is matte, takes
          the scene light, and fluoro fills get a small self-glow (`glow_k`); paint partly covers lit windows (`cover_k`).
  air     the pipeline's fog scatter is tinted toward soft neon (`fog_col`) and its glow lights are pushed to Cell neon
          hues (pink / cyan / violet), so the distance haze reads as neon-lit.
All randomness is seeded; same job -> same scene.
"""
import os
import random

import bpy

TEX = os.environ.get("GRAF_TEX", r"D:/rc_scratch/graffiti/tex")
NEON_HAZE = [(1.0, 0.24, 0.66), (0.36, 0.88, 1.0), (0.69, 0.30, 1.0), (1.0, 0.45, 0.85), (0.30, 0.60, 1.0)]


def _img(name, colorspace):
    p = os.path.join(TEX, name)
    im = bpy.data.images.get(name) or bpy.data.images.load(p, check_existing=True)
    im.colorspace_settings.name = colorspace
    if colorspace != "Non-Color":
        im.alpha_mode = "STRAIGHT"
    return im


def _m(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _smooth(nt, v, lo, hi):
    n = nt.nodes.new("ShaderNodeMapRange")
    n.interpolation_type = "SMOOTHSTEP"
    n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = lo, hi
    nt.links.new(v, n.inputs["Value"])
    return n.outputs[0]


def _cell_offset(nt, pos, cell, seed):
    """a random tile offset per world cell (floor(pos / cell) hashed by white noise), so neighbouring blocks show different
    parts of the atlas and the tile never visibly repeats across the city."""
    d = nt.nodes.new("ShaderNodeVectorMath")
    d.operation = "DIVIDE"
    nt.links.new(pos, d.inputs[0])
    d.inputs[1].default_value = (cell, cell, cell * 4.0)
    f = nt.nodes.new("ShaderNodeVectorMath")
    f.operation = "FLOOR"
    nt.links.new(d.outputs[0], f.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "4D"
    wn.inputs["W"].default_value = seed
    nt.links.new(f.outputs[0], wn.inputs["Vector"])
    s = nt.nodes.new("ShaderNodeVectorMath")
    s.operation = "SCALE"
    nt.links.new(wn.outputs["Color"], s.inputs[0])
    s.inputs["Scale"].default_value = 17.0
    return s.outputs[0]


def _sample(nt, pos, scale, off, alb, glow, blend=0.25, cell=None):
    """box-projected atlas sample at world position `pos` / `scale` (+ offset): returns (colour, alpha, glow)."""
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "MULTIPLY_ADD"
    nt.links.new(pos, vm.inputs[0])
    vm.inputs[1].default_value = (1.0 / scale, 1.0 / scale, 1.0 / (scale * 0.5))   # the tile is 2:1, keep letters square
    if cell:
        nt.links.new(_cell_offset(nt, pos, cell, off[0] * 10.0), vm.inputs[2])
    else:
        vm.inputs[2].default_value = off
    out = []
    for im in (alb, glow):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = im
        t.projection = "BOX"
        t.projection_blend = blend
        t.interpolation = "Cubic" if im is alb else "Linear"
        nt.links.new(vm.outputs[0], t.inputs["Vector"])
        out.append(t)
    return out[0].outputs["Color"], out[0].outputs["Alpha"], out[1].outputs["Color"]


def _mixc(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = "MIX"
    nt.links.new(fac, n.inputs[0])
    for sock, v in ((n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, tuple):
            sock.default_value = v
        else:
            nt.links.new(v, sock)
    return n.outputs[2]


def _src(sock):
    """what drives an input socket: the linked output, or its default value as a tuple / float."""
    if sock.is_linked:
        return sock.links[0].from_socket
    v = sock.default_value
    try:
        return tuple(v)
    except TypeError:
        return float(v)


def paint(mat, cfg, street_only=False):
    """Insert the graffiti overlay in front of every Principled BSDF of `mat` (in place)."""
    if mat is None or mat.get("_graf_done"):
        return 0
    nt = mat.node_tree
    alb, glw = _img("graf_albedo.png", "sRGB"), _img("graf_glow.png", "Non-Color")
    halb, hglw = _img("heaven_albedo.png", "sRGB"), _img("heaven_glow.png", "Non-Color")
    s1, s2 = cfg.get("scale", 14.0), cfg.get("heaven_scale", 30.0)
    zs0, zs1 = cfg.get("street_z", (7.0, 14.0))
    up_k, hv_k = (0.0, 0.0) if street_only else (cfg.get("up_k", 0.55), cfg.get("heaven_k", 1.0))
    n = 0
    for b in [x for x in nt.nodes if x.type == "BSDF_PRINCIPLED"]:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        pos = geo.outputs["Position"]
        sp = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(pos, sp.inputs[0])
        spn = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], spn.inputs[0])
        Z = sp.outputs["Z"]
        wall = _m(nt, "SUBTRACT", 1.0, _smooth(nt, _m(nt, "ABSOLUTE", spn.outputs["Z"]), 0.55, 0.9))   # 1 on walls, 0 on roofs
        cell = cfg.get("cell")
        c1, a1, g1 = _sample(nt, pos, s1, (0.13, 0.71, 0.37), alb, glw, cell=cell)
        c2, a2, g2 = _sample(nt, pos, s2, (0.57, 0.29, 0.83), halb, hglw, cell=cell)
        street = _m(nt, "SUBTRACT", 1.0, _smooth(nt, Z, zs0, zs1))
        # above the street band: street paint survives in noise patches (density up_k)
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = cfg.get("up_noise", 0.05)
        nz.inputs["Detail"].default_value = 2.0
        nt.links.new(pos, nz.inputs["Vector"])
        patch = _smooth(nt, nz.outputs["Fac"], 0.62 - 0.25 * up_k, 0.70 - 0.25 * up_k)
        k1 = _m(nt, "MAXIMUM", street, _m(nt, "MULTIPLY", patch, up_k))
        k1 = _m(nt, "MULTIPLY", k1, _m(nt, "ADD", wall, cfg.get("roof_k", 0.15)))
        k2 = _m(nt, "MULTIPLY", _m(nt, "ADD", wall, cfg.get("roof_k2", 0.5)), hv_k)
        if cfg.get("heaven_p", 1.0) < 1.0 and cfg.get("heaven_cell"):
            # heaven spots are rare: only a share of world cells carry the heaven layer at all
            d = nt.nodes.new("ShaderNodeVectorMath")
            d.operation = "DIVIDE"
            nt.links.new(pos, d.inputs[0])
            hc = cfg["heaven_cell"]
            d.inputs[1].default_value = (hc, hc, hc * 4.0)
            f = nt.nodes.new("ShaderNodeVectorMath")
            f.operation = "FLOOR"
            nt.links.new(d.outputs[0], f.inputs[0])
            wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
            wn.noise_dimensions = "4D"
            wn.inputs["W"].default_value = 3.7
            nt.links.new(f.outputs[0], wn.inputs["Vector"])
            k2 = _m(nt, "MULTIPLY", k2, _m(nt, "GREATER_THAN", wn.outputs["Value"], 1.0 - cfg["heaven_p"]))
        if cfg.get("z_floor") is not None:   # nothing below the ground plane / water line
            k1 = _m(nt, "MULTIPLY", k1, _smooth(nt, Z, cfg["z_floor"], cfg["z_floor"] + 0.3))
        A1 = _m(nt, "MINIMUM", _m(nt, "MULTIPLY", a1, k1), 1.0)
        A2 = _m(nt, "MINIMUM", _m(nt, "MULTIPLY", a2, k2), 1.0)
        # composite: heaven layer under the street layer
        base = _src(b.inputs["Base Color"])
        if isinstance(base, tuple):
            base = tuple(base[:3]) + (1.0,)
        col = _mixc(nt, A2, base, c2)
        col = _mixc(nt, A1, col, c1)
        A = _m(nt, "MAXIMUM", A1, A2)
        nt.links.new(col, b.inputs["Base Color"])
        # paint is matte
        r0 = _src(b.inputs["Roughness"])
        r0s = r0 if not isinstance(r0, (float, int)) else _m(nt, "ADD", float(r0), 0.0)
        rr = nt.nodes.new("ShaderNodeMix")
        rr.data_type = "FLOAT"
        nt.links.new(A, rr.inputs[0])
        nt.links.new(r0s, rr.inputs[2])
        rr.inputs[3].default_value = cfg.get("paint_rough", 0.62)
        nt.links.new(rr.outputs[0], b.inputs["Roughness"])
        if "Coat Weight" in b.inputs:
            cw = _src(b.inputs["Coat Weight"])
            cws = cw if not isinstance(cw, (float, int)) else _m(nt, "ADD", float(cw), 0.0)
            nt.links.new(_m(nt, "MULTIPLY", cws, _m(nt, "SUBTRACT", 1.0, A)), b.inputs["Coat Weight"])
        # emission: existing (windows) partly covered; fluoro paint glows a little in its own colour
        es = _src(b.inputs["Emission Strength"])
        ess = es if not isinstance(es, (float, int)) else _m(nt, "ADD", float(es), 0.0)
        ec = _src(b.inputs["Emission Color"])
        cover = _m(nt, "SUBTRACT", 1.0, _m(nt, "MULTIPLY", A, cfg.get("cover_k", 0.75)))
        e_old = _m(nt, "MULTIPLY", ess, cover)
        gsum = _m(nt, "ADD", _m(nt, "MULTIPLY", _bw(nt, g1), A1), _m(nt, "MULTIPLY", _bw(nt, g2), A2))
        e_new = _m(nt, "MULTIPLY", gsum, cfg.get("glow_k", 1.2))
        # one emission socket: colour = weighted mix of old emission colour and paint colour, strength = sum
        tot = _m(nt, "MAXIMUM", _m(nt, "ADD", e_old, e_new), 1e-5)
        w_new = _m(nt, "DIVIDE", e_new, tot)
        ecol = _mixc(nt, w_new, tuple(ec[:3]) + (1.0,) if isinstance(ec, tuple) else ec, col)
        nt.links.new(ecol, b.inputs["Emission Color"])
        nt.links.new(tot, b.inputs["Emission Strength"])
        n += 1
    try:
        mat["_graf_done"] = True
    except Exception:  # noqa: BLE001
        pass
    return n


def _bw(nt, c):
    n = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(c, n.inputs[0])
    return n.outputs[0]


def tint_fog_nodes(mat, col, dens_k=1.0):
    if mat is None:
        return
    for nd in mat.node_tree.nodes:
        if nd.type in ("VOLUME_SCATTER", "PRINCIPLED_VOLUME"):
            key = "Color"
            nd.inputs[key].default_value = tuple(col) + (1.0,)
            if dens_k != 1.0 and not nd.inputs["Density"].is_linked:
                nd.inputs["Density"].default_value *= dens_k


def neon_glow_lights(objs, cfg, prefixes):
    """push the pipeline's fog-glow lights to Cell neon hues (seeded per light), so the haze is lit in soft neon."""
    rng = random.Random(cfg.get("seed", 20261021))
    pal = [tuple(c) for c in cfg.get("haze_pal", NEON_HAZE)]
    n = 0
    for ob in sorted(objs, key=lambda o: o.name):
        if ob.type == "LIGHT" and ob.name.startswith(prefixes):
            ob.data.color = rng.choice(pal)
            ob.data.energy *= cfg.get("haze_light_k", 1.0)
            n += 1
    return n


def haze_lights(add, cfg, pts):
    """extra large, soft, volume-only neon lights deep in the frame (pts: [(x, y, z), ...])."""
    rng = random.Random(cfg.get("seed", 20261021) + 7)
    pal = [tuple(c) for c in cfg.get("haze_pal", NEON_HAZE)]
    obs = []
    for i, p in enumerate(pts):
        ld = bpy.data.lights.new("graf_haze_%d" % i, "POINT")
        ld.energy = cfg.get("haze_w", 4.0e5)
        ld.color = pal[i % len(pal)] if cfg.get("haze_cycle", True) else rng.choice(pal)
        ld.shadow_soft_size = cfg.get("haze_r", 12.0)
        try:
            ld.use_shadow = False
        except Exception:  # noqa: BLE001
            pass
        ob = bpy.data.objects.new("graf_haze_%d" % i, ld)
        ob.location = p
        # media only: invisible to surfaces' diffuse / glossy (so walls keep their own light), lights the fog
        for k in ("visible_diffuse", "visible_glossy", "visible_transmission"):
            if hasattr(ob, k):
                setattr(ob, k, False)
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    return obs


# ----------------------------------------------------------------------------------------------- entry points
def apply_hq(g, cfg):
    """HQ pipelines (hq_scene.py globals): paint the city facades fully and the corp compound at street level only."""
    if cfg.get("off"):
        return
    # light touch at HQ zoom (designer 2026-10-21: the street view carries the graffiti; the overviews only hint at it)
    cfg = dict(dict(scale=26.0, heaven_scale=90.0, cell=22.0, heaven_cell=30.0, heaven_p=0.12, street_z=(6.0, 14.0), up_k=0.0,
                    glow_k=0.5, haze_light_k=3.0), **cfg)
    n = paint(g.get("M_CITY"), cfg)
    n += paint(g.get("M_CIVIC"), dict(cfg, scale=cfg.get("civic_scale", 10.0)), street_only=not cfg.get("civic_full", False))
    tint_fog_nodes(g.get("FOG_M"), cfg.get("fog_col", (0.78, 0.66, 0.92)), cfg.get("fog_dens_k", 1.0))
    nl = neon_glow_lights([o for o, e, gr in g.get("LIGHTS", [])], cfg, ("cityglow_", "bankglow_"))
    print("[graf] hq paint bsdf", n, "glow lights", nl, flush=True)
