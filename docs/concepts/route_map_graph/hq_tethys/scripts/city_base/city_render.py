"""City-all-corps (exec'd by city_build.py): materials (AAA-2 Cycles / MAINLINE Eevee), lights, media, camera, passes.

The clear-water recipe (water_fade, every material): below the water (attribute wet, z < sea level) a surface is seen
through d / |I.z| + d BU of water (the view leg plus the down leg of its light). Transmittance T = exp(-sigma * path)
with sigma per channel (red dies first); the surface colour and its emission are multiplied by T and the water's own
in-scatter (deep blue) is added as (1 - T) * inscatter. So the water stays CLEAR near the surface (T ~ 1 for the top
5-10 BU) and fades to the deep blue with depth AND viewing distance (a grazing view crosses more water). Caustics:
two soft noise-ridge ripple layers (low contrast) on up-facing faces, fading exp(-d / depth). Shafts: spot lights from above linked to a thin
scattering volume in the water (and the seabed, so they land as pools).
"""
import numpy as _np
import bpy_extras.object_utils as _ou0


class NB:
    def __init__(self, mat):
        self.m = mat
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.nt.nodes.new("ShaderNodeOutputMaterial")

    def n(self, kind, **kw):
        nd = self.nt.nodes.new(kind)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.nt.links.new(a, b)

    def attr(self, name):
        a = self.n("ShaderNodeAttribute")
        a.attribute_name = name
        return a

    def math(self, op, a, b=0.0, clamp=False):
        nd = self.n("ShaderNodeMath")
        nd.operation = op
        nd.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                nd.inputs[i].default_value = v
            else:
                self.link(v, nd.inputs[i])
        return nd.outputs[0]

    def vmath(self, op, a, b=None, scale=None):
        nd = self.n("ShaderNodeVectorMath")
        nd.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (tuple, list)):
                nd.inputs[i].default_value = v
            else:
                self.link(v, nd.inputs[i])
        if scale is not None:
            if isinstance(scale, (int, float)):
                nd.inputs["Scale"].default_value = scale
            else:
                self.link(scale, nd.inputs["Scale"])
        return nd.outputs[0]

    def sep(self, v):
        s = self.n("ShaderNodeSeparateXYZ")
        self.link(v, s.inputs[0])
        return s.outputs

    def comb(self, x, y, z):
        c = self.n("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            if isinstance(v, (int, float)):
                c.inputs[i].default_value = v
            else:
                self.link(v, c.inputs[i])
        return c.outputs[0]

    def band(self, x, a, b):
        return self.math("MULTIPLY", self.math("GREATER_THAN", x, a), self.math("LESS_THAN", x, b))


def window_graph(g, win_k):
    """-> (mask, emission rgb) from the facade UV (metres along, height) and the face attributes."""
    uvn = g.n("ShaderNodeUVMap")
    uvn.uv_map = "UVMap"
    u, v, _ = g.sep(uvn.outputs["UV"])
    ux = g.math("DIVIDE", u, CP.COLW)
    vy = g.math("DIVIDE", v, CP.FLOOR)
    fx = g.math("FRACT", ux)
    fy = g.math("FRACT", vy)
    wm = g.attr("wm").outputs["Fac"]
    grid = g.math("MULTIPLY", g.band(fx, 0.22, 0.78), g.band(fy, 0.30, 0.72))
    rib = g.band(fy, 0.32, 0.70)
    port = g.math("MULTIPLY", g.band(fx, 0.36, 0.64), g.band(fy, 0.36, 0.64))
    arch = g.math("MULTIPLY", g.band(fx, 0.16, 0.84), g.band(fy, 0.06, 0.80))
    m0 = g.math("MULTIPLY", grid, g.math("LESS_THAN", wm, 0.5))
    m1 = g.math("MULTIPLY", rib, g.band(wm, 0.5, 1.5))
    m2 = g.math("MULTIPLY", port, g.band(wm, 1.5, 2.5))
    m4 = g.math("MULTIPLY", arch, g.math("GREATER_THAN", wm, 3.5))
    mask = g.math("ADD", g.math("ADD", m0, m1), g.math("ADD", m2, m4))
    bid = g.attr("bid").outputs["Fac"]
    # ribbon windows light in runs of 4 columns
    cx = g.math("FLOOR", g.math("DIVIDE", ux, g.math("ADD", 1.0, g.math("MULTIPLY", 3.0, g.band(wm, 0.5, 1.5)))))
    wn = g.n("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "4D"
    g.link(g.comb(cx, g.math("FLOOR", vy), g.math("MULTIPLY", bid, 517.0)), wn.inputs["Vector"])
    g.link(g.math("MULTIPLY", bid, 13.0), wn.inputs["W"])
    lit = g.math("LESS_THAN", wn.outputs["Value"], g.attr("wl").outputs["Fac"])
    cr, cg, _ = g.sep(wn.outputs["Color"])
    var = g.math("ADD", 0.3, g.math("MULTIPLY", cr, 0.95))
    k = g.math("MULTIPLY", g.math("MULTIPLY", mask, lit), g.math("MULTIPLY", var, win_k))
    em = g.vmath("SCALE", g.attr("wc").outputs["Color"], scale=k)
    return mask, em


def water_fade(g, base, emis, caustic=False):
    """The clear-water recipe (module doc). base / emis: colour sockets; returns (base', emis')."""
    geo = g.n("ShaderNodeNewGeometry")
    px, py, pz = g.sep(geo.outputs["Position"])
    _, _, iz = g.sep(geo.outputs["Incoming"])
    wet = g.attr("wet").outputs["Fac"]
    d = g.math("MULTIPLY", g.math("MAXIMUM", g.math("SUBTRACT", ZW, pz), 0.0), wet)
    izc = g.math("MAXIMUM", g.math("ABSOLUTE", iz), 0.12)
    path = g.math("MINIMUM", g.math("ADD", g.math("DIVIDE", d, izc), d), WAT["path_cap"])
    sg = WAT["sigma"]
    T = g.comb(*[g.math("EXPONENT", g.math("MULTIPLY", path, -sg[i])) for i in range(3)])
    base2 = g.vmath("MULTIPLY", base, T)
    one_m = g.vmath("SUBTRACT", (1.0, 1.0, 1.0), T)
    ins = g.vmath("MULTIPLY", one_m, tuple(WAT["inscatter"]))
    e = g.vmath("ADD", g.vmath("MULTIPLY", emis, T), ins)
    if caustic:
        C = WAT["caustic"]
        tc = geo.outputs["Position"]

        def ripple(scale, off, w):
            # (art review 6) soft caustic RIPPLES, not a voronoi crack net: the ridge of a distorted noise field
            # (|2n - 1| near 0), widened by a smoothstep, so the lines are soft, organic and low in contrast
            mp = g.n("ShaderNodeMapping")
            mp.inputs["Scale"].default_value = (scale, scale, scale * 0.15)
            mp.inputs["Location"].default_value = (off, off * 0.7, 0)
            g.link(tc, mp.inputs[0])
            nz_ = g.n("ShaderNodeTexNoise")
            nz_.noise_dimensions = "4D"
            nz_.inputs["W"].default_value = w
            nz_.inputs["Scale"].default_value = 1.0
            nz_.inputs["Detail"].default_value = 1.5
            nz_.inputs["Distortion"].default_value = C["distort"]
            g.link(mp.outputs[0], nz_.inputs["Vector"])
            rd = g.math("ABSOLUTE", g.math("SUBTRACT", g.math("MULTIPLY", nz_.outputs["Fac"], 2.0), 1.0))
            mr = g.n("ShaderNodeMapRange")
            mr.interpolation_type = "SMOOTHSTEP"
            mr.inputs["From Min"].default_value = C["width"]
            mr.inputs["From Max"].default_value = 0.0
            g.link(rd, mr.inputs["Value"])
            return mr.outputs[0]
        rip = g.math("MULTIPLY", g.math("ADD", ripple(C["scale"], 0.0, 1.3), ripple(C["scale"] * 1.6, 3.3, 7.9)), 0.5)
        cnet = g.math("ADD", C["floor"], g.math("MULTIPLY", rip, 1.0 - C["floor"]))     # low contrast: a lit floor
        # soft and patchy (the surface waves focus light in drifting patches, never an even net over the seabed)
        pn = g.n("ShaderNodeTexNoise")
        pn.inputs["Scale"].default_value = 0.025
        pn.inputs["Detail"].default_value = 2.0
        g.link(tc, pn.inputs["Vector"])
        pm = g.n("ShaderNodeMapRange")
        pm.interpolation_type = "SMOOTHSTEP"
        pm.inputs["From Min"].default_value = 0.42
        pm.inputs["From Max"].default_value = 0.68
        g.link(pn.outputs["Fac"], pm.inputs["Value"])
        cnet = g.math("MULTIPLY", cnet, g.math("ADD", C["patch"], g.math("MULTIPLY", pm.outputs[0], 1.0 - C["patch"])))
        _, _, nz = g.sep(geo.outputs["Normal"])
        up = g.math("POWER", nz, 2.0)          # either winding (the lot -> world map flips y)
        fade = g.math("EXPONENT", g.math("DIVIDE", d, -C["depth"]))
        under = g.math("GREATER_THAN", d, 0.05)
        ck = g.math("MULTIPLY", g.math("MULTIPLY", cnet, up), g.math("MULTIPLY", g.math("MULTIPLY", fade, under), C["k"]))
        e = g.vmath("ADD", e, g.vmath("SCALE", tuple(C["col"]), scale=ck))
    return base2, e


def principled(g, base, emis, rough):
    bs = g.n("ShaderNodeBsdfPrincipled")
    g.link(base, bs.inputs["Base Color"])
    if isinstance(rough, (int, float)):
        bs.inputs["Roughness"].default_value = rough
    else:
        g.link(rough, bs.inputs["Roughness"])
    try:
        bs.inputs["Specular IOR Level"].default_value = 0.5
    except KeyError:
        pass
    g.link(emis, bs.inputs["Emission Color"])
    bs.inputs["Emission Strength"].default_value = 1.0
    return bs


def mat_surf_aaa(name, caustic=False):
    m = bpy.data.materials.new(name)
    g = NB(m)
    col = g.attr("col").outputs["Color"]
    mask, em = window_graph(g, CP.AAA["win"])
    base = g.n("ShaderNodeMix")
    base.data_type = "RGBA"
    g.link(g.math("MULTIPLY", mask, 0.85), base.inputs["Factor"])
    g.link(col, base.inputs[6])
    base.inputs[7].default_value = (0.015, 0.02, 0.03, 1)
    em = g.vmath("SCALE", em, scale=g.math("ADD", 1.0, g.math("MULTIPLY", g.attr("wet").outputs["Fac"], WAT["win_boost"])))   # drowned windows read (art review 3)
    b2, e2 = water_fade(g, base.outputs[2], em, caustic=caustic)
    rough = g.math("SUBTRACT", 0.62, g.math("MULTIPLY", mask, 0.48))
    bs = principled(g, b2, e2, rough)
    g.link(bs.outputs[0], g.out.inputs[0])
    try:
        m.emission_sampling = "NONE"        # windows are seen, they do not light the city (the r3 levels come from lights)
    except Exception:
        pass
    return m


def mat_emit_aaa(name, k, sampling="AUTO"):
    m = bpy.data.materials.new(name)
    g = NB(m)
    col = g.attr("col").outputs["Color"]
    e0 = g.vmath("SCALE", col, scale=k)
    _, e = water_fade(g, (0, 0, 0) if False else col, e0)
    em = g.n("ShaderNodeEmission")
    g.link(e, em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0
    g.link(em.outputs[0], g.out.inputs[0])
    try:
        m.emission_sampling = sampling
    except Exception:
        pass
    return m


def mat_ground_aaa(name, caustic):
    m = bpy.data.materials.new(name)
    g = NB(m)
    col = g.vmath("SCALE", g.attr("col").outputs["Color"], scale=0.6)
    geo = g.n("ShaderNodeNewGeometry")
    nz = g.n("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.16
    nz.inputs["Detail"].default_value = 5.0
    g.link(geo.outputs["Position"], nz.inputs["Vector"])
    mr = g.n("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.45
    mr.inputs["From Max"].default_value = 0.6
    mr.inputs["To Min"].default_value = 0.32
    mr.inputs["To Max"].default_value = 0.04
    g.link(nz.outputs["Fac"], mr.inputs["Value"])
    b2, e2 = water_fade(g, col, (0.0, 0.0, 0.0) and g.comb(0, 0, 0), caustic=caustic)
    bs = principled(g, b2, e2, mr.outputs[0])
    try:
        bs.inputs["Specular IOR Level"].default_value = 0.45
    except KeyError:
        pass
    g.link(bs.outputs[0], g.out.inputs[0])
    return m


def mat_glass_aaa():
    m = bpy.data.materials.new("glass_aaa")
    g = NB(m)
    lw = g.n("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    tr = g.n("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.72, 0.88, 0.95, 1)
    gl = g.n("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.06
    mx = g.n("ShaderNodeMixShader")
    g.link(lw.outputs["Fresnel"], mx.inputs[0])
    g.link(tr.outputs[0], mx.inputs[1])
    g.link(gl.outputs[0], mx.inputs[2])
    em = g.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.3, 0.6, 1.0, 1)
    em.inputs["Strength"].default_value = 0.04
    ad = g.n("ShaderNodeAddShader")
    g.link(mx.outputs[0], ad.inputs[0])
    g.link(em.outputs[0], ad.inputs[1])
    g.link(ad.outputs[0], g.out.inputs[0])
    return m


def mat_water_aaa():
    S = WAT["surface"]
    m = bpy.data.materials.new("water_aaa")
    g = NB(m)
    geo = g.n("ShaderNodeNewGeometry")
    nz = g.n("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.35
    nz.inputs["Detail"].default_value = 6.0
    mp = g.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 2.4, 1.0)
    g.link(geo.outputs["Position"], mp.inputs[0])
    g.link(mp.outputs[0], nz.inputs["Vector"])
    bump = g.n("ShaderNodeBump")
    bump.inputs["Strength"].default_value = S["wave"]
    g.link(nz.outputs["Fac"], bump.inputs["Height"])
    fr = g.n("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.33
    g.link(bump.outputs[0], fr.inputs["Normal"])
    tr = g.n("ShaderNodeBsdfTransparent")
    gl = g.n("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = S["rough"]
    g.link(bump.outputs[0], gl.inputs["Normal"])
    mx = g.n("ShaderNodeMixShader")
    g.link(fr.outputs[0], mx.inputs[0])
    g.link(tr.outputs[0], mx.inputs[1])
    g.link(gl.outputs[0], mx.inputs[2])
    g.link(mx.outputs[0], g.out.inputs[0])
    return m


def mat_fog():
    A = CP.AAA
    m = bpy.data.materials.new("fog")
    g = NB(m)
    geo = g.n("ShaderNodeNewGeometry")
    _, _, z = g.sep(geo.outputs["Position"])

    def noise(scale, det, w):
        sc_ = g.vmath("MULTIPLY", geo.outputs["Position"], tuple(scale))
        nz = g.n("ShaderNodeTexNoise")
        nz.noise_dimensions = "4D"
        nz.inputs["W"].default_value = w
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = det
        g.link(sc_, nz.inputs["Vector"])
        return nz.outputs["Fac"]

    def smooth(v, a, b):
        mr = g.n("ShaderNodeMapRange")
        mr.interpolation_type = "SMOOTHSTEP"
        mr.inputs["From Min"].default_value = a
        mr.inputs["From Max"].default_value = b
        g.link(v, mr.inputs["Value"])
        return mr.outputs[0]
    # banks: the broad octave (200+ BU masses) broken by a fine one (ragged edges, the r3 bank / wisp mix 0.62 / 0.38)
    fine = noise(tuple(v * 4.0 for v in A["bank_scale"]), 2.0, 5.3)
    banks = smooth(g.math("ADD", g.math("MULTIPLY", noise(A["bank_scale"], 3.0, 3.1), 0.65), g.math("MULTIPLY", fine, 0.35)), 0.53, 0.70)
    clumps = smooth(noise(A["clump_scale"], 2.0, 14.1), 0.40, 0.62)
    hf = g.math("EXPONENT", g.math("MULTIPLY", g.math("MAXIMUM", g.math("SUBTRACT", z, A["fog_floor"][1]), 0.0), -1.0 / A["fog_h"]))
    lowcut = smooth(z, -0.5, 1.5)
    body = g.math("ADD", g.math("MULTIPLY", clumps, A["fog_base"]), g.math("MULTIPLY", banks, clumps))
    dens = g.math("ADD", g.math("MULTIPLY", g.math("MULTIPLY", g.math("MULTIPLY", body, hf), lowcut), A["fog_peak"]), A["haze"])
    # clear air over the water (rule): from the drowned quarter's edge to 20 lots out to sea the low fog thins to 15 %,
    # so the water reads; the sea mist returns farther out. b (lots, away from the map camera) = (y - x) / (U sqrt 2)
    px_, py_, _ = g.sep(geo.outputs["Position"])
    bpos = g.math("DIVIDE", g.math("SUBTRACT", py_, px_), U * R2)
    lag = g.math("MULTIPLY", smooth(bpos, O["b_split"] + 0.5, O["b_split"] + 5.0),
                 g.math("SUBTRACT", 1.0, smooth(bpos, B_COAST + 20.0, B_COAST + 40.0)))
    dens = g.math("MULTIPLY", dens, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", lag, A["bay_clear"])))
    # the shore bank (art review 6): a low dense bank along the dry side of the levee (the city edge over the drowned
    # quarter), torn by the clump noise, so the shore city sits in fog and the water past it stays clear
    SB = A["shore_bank"]
    shore = g.math("MULTIPLY", smooth(bpos, O["b_split"] - SB["width"], O["b_split"] - SB["width"] * 0.4),
                   g.math("SUBTRACT", 1.0, smooth(bpos, O["b_split"] - 1.0, O["b_split"] + 1.5)))
    shf = g.math("EXPONENT", g.math("MULTIPLY", g.math("MAXIMUM", z, 0.0), -1.0 / SB["h"]))
    dens = g.math("ADD", dens, g.math("MULTIPLY", g.math("MULTIPLY", g.math("MULTIPLY", shore, shf),
                                                       g.math("ADD", 0.35, g.math("MULTIPLY", clumps, 0.65))), SB["peak"]))
    # fog strata (art review): the low district bank above, plus a thin upper SHEET over the skyline, torn by noise
    sh = A["sheet"]
    sheet_d = g.math("EXPONENT", g.math("MULTIPLY", g.math("POWER", g.math("DIVIDE", g.math("SUBTRACT", z, sh["z"]), sh["thick"]), 2.0), -1.0))
    sheet_n = smooth(noise(sh["scale"], 3.0, 9.7), sh["remap"][0], sh["remap"][1])
    dens = g.math("ADD", dens, g.math("MULTIPLY", g.math("MULTIPLY", sheet_d, sheet_n), sh["peak"]))
    # the beam haze: a thin band over the skyline where the beams travel (not over the whole camera path)
    hb = g.math("MULTIPLY", smooth(z, 25.0, 70.0), g.math("SUBTRACT", 1.0, smooth(z, 180.0, 310.0)))
    hb = g.math("MULTIPLY", hb, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", lag, A["bay_clear"])))      # clear air over the bay (art review 6)
    dens = g.math("ADD", dens, g.math("MULTIPLY", g.math("MULTIPLY", hb, g.math("ADD", 0.55, g.math("MULTIPLY", clumps, 0.9))), A["haze_hi"]))
    vs = g.n("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = (0.85, 0.80, 1.0, 1)
    vs.inputs["Anisotropy"].default_value = 0.45
    g.link(dens, vs.inputs["Density"])
    g.link(vs.outputs[0], g.out.inputs["Volume"])
    return m


def mat_water_vol():
    m = bpy.data.materials.new("water_vol")
    g = NB(m)
    vs = g.n("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = (0.35, 0.75, 1.0, 1)
    vs.inputs["Anisotropy"].default_value = 0.65
    vs.inputs["Density"].default_value = WAT["shafts"]["density"]
    g.link(vs.outputs[0], g.out.inputs["Volume"])
    return m


# ------------------------------------------------------------------ MAINLINE (Eevee): toon ramp + window emission
def mat_toon_main(name, windows=True, ground=False):
    M = CP.MAINLINE
    m = bpy.data.materials.new(name)
    g = NB(m)
    col = g.attr("col").outputs["Color"]
    dif = g.n("ShaderNodeBsdfDiffuse")
    s2r = g.n("ShaderNodeShaderToRGB")
    g.link(dif.outputs[0], s2r.inputs[0])
    bw = g.n("ShaderNodeRGBToBW")
    g.link(s2r.outputs["Color"], bw.inputs[0])
    ramp = g.n("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[1].position = 0.12
    el.new(0.32)
    for e, c in zip(el, M["ramp"]):
        e.color = (*c, 1)
    g.link(bw.outputs[0], ramp.inputs[0])
    lit = g.vmath("MULTIPLY", ramp.outputs["Color"], col)
    lit = g.vmath("SCALE", lit, scale=2.6 if not ground else 2.0)
    if windows:
        mask, em = window_graph(g, 1.0)
        tot = g.vmath("ADD", g.vmath("SCALE", lit, scale=g.math("SUBTRACT", 1.0, g.math("MULTIPLY", mask, 0.8))), em)
    else:
        tot = lit
    # the mainline water: a plain depth tint toward the map's water blue (no media in the mainline look)
    geo = g.n("ShaderNodeNewGeometry")
    _, _, pz = g.sep(geo.outputs["Position"])
    d = g.math("MULTIPLY", g.math("MAXIMUM", g.math("SUBTRACT", ZW, pz), 0.0), g.attr("wet").outputs["Fac"])
    f = g.math("SUBTRACT", 1.0, g.math("EXPONENT", g.math("MULTIPLY", d, -0.06)))
    mx = g.n("ShaderNodeMix")
    mx.data_type = "RGBA"
    g.link(f, mx.inputs["Factor"])
    g.link(tot, mx.inputs[6])
    mx.inputs[7].default_value = (0.03, 0.07, 0.16, 1)
    em = g.n("ShaderNodeEmission")
    g.link(mx.outputs[2], em.inputs["Color"])
    g.link(em.outputs[0], g.out.inputs[0])
    return m


def mat_emit_main(name, k):
    m = bpy.data.materials.new(name)
    g = NB(m)
    col = g.vmath("SCALE", g.attr("col").outputs["Color"], scale=k)
    geo = g.n("ShaderNodeNewGeometry")
    _, _, pz = g.sep(geo.outputs["Position"])
    d = g.math("MULTIPLY", g.math("MAXIMUM", g.math("SUBTRACT", ZW, pz), 0.0), g.attr("wet").outputs["Fac"])
    col = g.vmath("SCALE", col, scale=g.math("EXPONENT", g.math("MULTIPLY", d, -0.06)))
    em = g.n("ShaderNodeEmission")
    g.link(col, em.inputs["Color"])
    g.link(em.outputs[0], g.out.inputs[0])
    return m


def mat_transp_main(name, col, alpha):
    m = bpy.data.materials.new(name)
    g = NB(m)
    tr = g.n("ShaderNodeBsdfTransparent")
    em = g.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*col, 1)
    mx = g.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = alpha
    g.link(tr.outputs[0], mx.inputs[1])
    g.link(em.outputs[0], mx.inputs[2])
    g.link(mx.outputs[0], g.out.inputs[0])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m


scene = bpy.context.scene
for o in list(scene.objects):
    bpy.data.objects.remove(o)

if MODE == "aaa":
    MS = dict(surf=mat_surf_aaa("surf_aaa", caustic=True), neon=mat_emit_aaa("neon_aaa", CP.AAA["neon"]),
              streak=mat_emit_aaa("streak_aaa", CP.AAA["streak"]), glass=mat_glass_aaa(),
              ground=mat_ground_aaa("ground_aaa", False), seabed=mat_ground_aaa("seabed_aaa", True), water=mat_water_aaa())
else:
    MS = dict(surf=mat_toon_main("surf_main"), neon=mat_emit_main("neon_main", 1.0), streak=mat_emit_main("streak_main", 1.4),
              glass=mat_transp_main("glass_main", (0.45, 0.7, 0.95), 0.35), ground=mat_toon_main("ground_main", False, True),
              seabed=mat_toon_main("seabed_main", False, True), water=mat_transp_main("water_main", (0.05, 0.16, 0.36), 0.42))
OBJ = dict(surf=SURF.obj(MS["surf"]), smooth=SMOOTH.obj(MS["surf"]), neon=NEON.obj(MS["neon"]), streak=STREAK.obj(MS["streak"]),
           glass=GLASS.obj(MS["glass"]), ground=GROUND.obj(MS["ground"]), seabed=SEABED.obj(MS["seabed"]), water=WATER.obj(MS["water"]))
OBJ["water"].visible_shadow = False
# textured sign panels (the MAINFRAME blade): an image emitter, both faces, in both looks
for si, (corners, img_path) in enumerate(SIGNS):
    me_s = bpy.data.meshes.new("sign_%d" % si)
    me_s.from_pydata(corners, [], [(0, 1, 2, 3)])
    uvs = me_s.uv_layers.new(name="UVMap")
    uvs.data.foreach_set("uv", [0, 0, 1, 0, 1, 1, 0, 1])
    ms = bpy.data.materials.new("sign_mat_%d" % si)
    gs = NB(ms)
    tex = gs.n("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(img_path)
    tex.interpolation = "Smart"
    em_s = gs.n("ShaderNodeEmission")
    gs.link(tex.outputs["Color"], em_s.inputs["Color"])
    em_s.inputs["Strength"].default_value = 3.0 if MODE == "aaa" else 1.0
    gs.link(em_s.outputs[0], gs.out.inputs[0])
    me_s.materials.append(ms)
    ob_s = bpy.data.objects.new("sign_%d" % si, me_s)
    scene.collection.objects.link(ob_s)
OBJ["glass"].visible_shadow = False
if os.environ.get("CITY_NOWATER"):          # debug: the drowned quarter without its water surface
    OBJ["water"].hide_render = True
print("OBJECTS %.1fs" % (time.time() - T0), flush=True)


def light(name, kind, loc, energy, col, rot=(0, 0, 0), size=None, spot=None, blend=0.3, shadow=True):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = col
    ld.use_shadow = shadow
    if kind == "AREA" and size:
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
        ld.shadow_soft_size = 0.3
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    if kind == "AREA":                 # the emitter sheets are never seen (camera, reflections)
        ob.visible_camera = False
        ob.visible_glossy = False
        ob.visible_transmission = False
    return ob


def aim(frm, to):
    return (Vector(to) - Vector(frm)).normalized().to_track_quat("-Z", "Y").to_euler()


def district_of(x, y):
    best = None
    for k, v in O["hq"].items():
        hx_, hy_ = W(v)
        d = math.hypot(x - hx_, y - hy_)
        if best is None or d < best[0]:
            best = (d, k)
    return best[1]


# ------------------------------------------------------------------ camera
C = CP.CAMS[CAMK]
tgt = Vector((*w_ab(*C["target_ab"]), 0.0))
yw, pt = math.radians(C["yaw"]), math.radians(C["pitch"])
fwd = Vector((math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt)))
cam_d = bpy.data.cameras.new("cam")
cam_d.type = "PERSP"
cam_d.sensor_fit = "HORIZONTAL"
cam_d.sensor_width = 36.0
cam_d.lens = C["lens"]
cam_d.shift_y = C.get("sy", 0.0)
cam_d.clip_start = 1.0
cam_d.clip_end = 80000.0
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
cam.location = tgt - fwd * C["dist"]
cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
scene.camera = cam
RX, RY = int(C["res"][0] * RES_K), int(C["res"][1] * RES_K)
scene.render.resolution_x, scene.render.resolution_y = RX, RY
scene.render.resolution_percentage = 100
print("CAM loc", tuple(round(v) for v in cam.location), "tgt", tuple(round(v) for v in tgt), flush=True)

wd = bpy.data.worlds.new("world")
scene.world = wd
wd.use_nodes = True
bg = next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND")

if MODE == "aaa":
    A = CP.AAA
    # night sky: a city-glow horizon (violet-magenta) over a deep navy zenith; the sea reflects it
    wnt = wd.node_tree
    tco = wnt.nodes.new("ShaderNodeTexCoord")
    sxyz = wnt.nodes.new("ShaderNodeSeparateXYZ")
    wnt.links.new(tco.outputs["Generated"], sxyz.inputs[0])
    mrz = wnt.nodes.new("ShaderNodeMapRange")
    mrz.interpolation_type = "SMOOTHSTEP"
    mrz.inputs["From Min"].default_value = -0.02
    mrz.inputs["From Max"].default_value = 0.4
    wnt.links.new(sxyz.outputs["Z"], mrz.inputs["Value"])
    mxs = wnt.nodes.new("ShaderNodeMix")
    mxs.data_type = "RGBA"
    wnt.links.new(mrz.outputs[0], mxs.inputs["Factor"])
    mxs.inputs[6].default_value = (0.045, 0.028, 0.07, 1)
    mxs.inputs[7].default_value = (0.002, 0.003, 0.009, 1)
    wnt.links.new(mxs.outputs[2], bg.inputs["Color"])
    MOON = light("moon", "SUN", (0, 0, 500), A["moon"], (0.55, 0.62, 1.0), rot=(math.radians(35), 0, math.radians(200)))
    # media: the city fog field (+ haze) and the water's shaft volume
    me = bpy.data.meshes.new("fogbox")
    bmm = bmesh.new()
    bmesh.ops.create_cube(bmm, size=1.0)
    bmm.to_mesh(me)
    bmm.free()
    fog = bpy.data.objects.new("fog", me)
    FZ = 320.0
    fog.location = (0.0, 0.0, FZ / 2 - 0.5)
    fog.scale = (3600.0, 3600.0, FZ + 1.0)
    me.materials.append(mat_fog())
    scene.collection.objects.link(fog)
    rx_fog = bpy.data.collections.new("rx_fog")
    scene.collection.children.link(rx_fog)
    rx_fog.objects.link(fog)
    fog.hide_render = bool(os.environ.get("CITY_NOFOG"))       # debug switch
    # sea mist (art review): a homogeneous low layer over the open sea from 30 lots past the wall to the horizon; it
    # thickens with distance by path length alone, so the horizon dissolves (no ruler line) and costs no ray marching
    SM = WAT["sea_mist"]
    vm = []
    for (a_, b_) in ((-2400.0, 0.0), (2400.0, 0.0), (2400.0, 1.0), (-2400.0, 1.0)):
        bb = (B_COAST + SM["from"]) if b_ == 0.0 else (B_COAST + WAT["sea_out"] / U)
        vm.append(w_ab(a_, bb))
    me3 = bpy.data.meshes.new("seamist")
    me3.from_pydata([(x, y, z) for z in (0.0, SM["top"]) for (x, y) in vm], [],
                    [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    me3.validate()
    me3.update()
    mm = bpy.data.materials.new("seamist")
    gm = NB(mm)
    vsm = gm.n("ShaderNodeVolumeScatter")
    vsm.inputs["Color"].default_value = (0.55, 0.65, 0.9, 1)
    vsm.inputs["Density"].default_value = SM["density"]
    vsm.inputs["Anisotropy"].default_value = 0.3
    gm.link(vsm.outputs[0], gm.out.inputs["Volume"])
    me3.materials.append(mm)
    mist = bpy.data.objects.new("seamist", me3)
    scene.collection.objects.link(mist)
    rx_fog.objects.link(mist)
    # water volume: the lagoon + the near sea (box), under the surface
    xs_ = [W((c[0], c[1]))[0] for c in O["lagoon_cells"]]
    ys_ = [W((c[0], c[1]))[1] for c in O["lagoon_cells"]]
    sea_far = [w_ab(a, bwall(a) + 40) for a in (-120, 0, 120)]
    xs_ += [p[0] for p in sea_far]
    ys_ += [p[1] for p in sea_far]
    me2 = bpy.data.meshes.new("waterbox")
    bmm = bmesh.new()
    bmesh.ops.create_cube(bmm, size=1.0)
    bmm.to_mesh(me2)
    bmm.free()
    wv = bpy.data.objects.new("water_vol", me2)
    zb = -135.0
    wv.location = ((min(xs_) + max(xs_)) / 2, (min(ys_) + max(ys_)) / 2, (zb + ZW - 0.05) / 2)
    wv.scale = (max(xs_) - min(xs_) + 20, max(ys_) - min(ys_) + 20, ZW - 0.05 - zb)
    me2.materials.append(mat_water_vol())
    scene.collection.objects.link(wv)
    wv.hide_render = bool(os.environ.get("CITY_NOWVOL"))       # debug switch
    wv.visible_shadow = False
    rx_w = bpy.data.collections.new("rx_water")
    scene.collection.children.link(rx_w)
    rx_w.objects.link(wv)
    # city glow under the fog, tinted by the district it sits in (the fog reads the district colours)
    GL = []
    for gx in range(-6, 7):
        for gy in range(-6, 7):
            x, y = gx * 130.0, gy * 130.0
            a_, b_ = ab_w(x, y)
            if b_ > bwall(a_) + 8:          # over the sea: Tethys' blue sea mist (half power)
                o = light("seaglow_%d_%d" % (gx, gy), "AREA", (x, y, ZW + 1.0), A["glow_area"] * 0.5, mixc(DIST["tethys"]["hue"], (0.6, 0.8, 1.0), 0.5),
                          rot=(math.pi, 0, 0), size=(110, 110), shadow=False)
                o.light_linking.receiver_collection = rx_fog
                continue
            k_ = district_of(x, y)
            c = DIST[k_]["sec" if k_ == "aurelian" else "hue"]          # Aurelian: travertine / gilt fog
            c = mixc(c, (0.85, 0.75, 0.95), A["glow_mix"])
            pw = A["glow_area"] * (A["rebel_glow_k"] if k_ == "rebel_cell" else 1.0)   # REBEL_CELL: the strongest red glow
            o = light("glow_%d_%d" % (gx, gy), "AREA", (x, y, 1.0), pw, c, rot=(math.pi, 0, 0), size=(110, 110), shadow=False)
            o.light_linking.receiver_collection = rx_fog
            GL.append(o)
            # the sky-glow wash on the roofs (the city glow bounced off the cloud base): district-tinted, soft
            c2 = mixc(DIST[k_]["hue"], (0.7, 0.68, 0.9), 0.55)
            light("roofwash_%d_%d" % (gx, gy), "AREA", (x, y, 160.0), A["glow_area"] * A.get("roofwash", 0.35), c2,
                  rot=(0, 0, 0), size=(130, 130), shadow=True)
    # beams (art director, revision 2): ONE beam per landmark, rising from its crown (max 7; REBEL_CELL has no crown,
    # so 6). The storyboard round-3 implementation (m44/onecity_cycles.py): the visible shaft is an emissive cone seen
    # by the camera only (a hot gaussian core over a wide soft skirt, brightest at the source, gone by beam_fade of its
    # length, a slow noise breakup); a wide fully soft spot linked to the fog only makes the air round it glow.
    # Each beam is shortened (in steps) until its far end sits inside the frame margin.
    bpy.context.view_layer.update()
    BM = A["beam"]

    def in_frame(p, m=(0.06, 0.04)):
        v = _ou0.world_to_camera_view(scene, cam, Vector(p))
        return v.z > 0 and m[0] < v.x < 1 - m[0] and m[1] < v.y < 1 - m[1]

    def beam_mat(name, col, k_emit):
        m = bpy.data.materials.new(name)
        g = NB(m)
        lw = g.n("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        x = g.math("SUBTRACT", 1.0, lw.outputs["Facing"])
        s2 = g.math("MAXIMUM", g.math("SUBTRACT", 1.0, g.math("MULTIPLY", x, x)), 0.0)
        sc_, ss_ = BM["core_s"], BM["soft_s"]
        core = g.math("EXPONENT", g.math("MULTIPLY", s2, -1.0 / (2 * sc_ * sc_)))
        soft = g.math("MULTIPLY", g.math("EXPONENT", g.math("MULTIPLY", s2, -1.0 / (2 * ss_ * ss_))), g.math("SUBTRACT", 1.0, s2))
        rad = g.math("ADD", g.math("MULTIPLY", core, BM["core_w"]), g.math("MULTIPLY", soft, BM["soft_w"]))
        tc = g.n("ShaderNodeTexCoord")
        _, _, t = g.sep(tc.outputs["Object"])                # the mesh has length 1 in object space

        def ss(v, a, b):
            mr = g.n("ShaderNodeMapRange")
            mr.interpolation_type = "SMOOTHSTEP"
            mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = a, b
            g.link(v, mr.inputs["Value"])
            return mr.outputs[0]
        ax = g.math("MULTIPLY", g.math("EXPONENT", g.math("MULTIPLY", t, -1.0 / BM["efold"])),
                    g.math("SUBTRACT", 1.0, ss(t, BM["fade"] * 0.45, BM["fade"])))
        ax = g.math("MULTIPLY", ax, ss(t, 0.0, 0.025))
        geo = g.n("ShaderNodeNewGeometry")
        nz = g.n("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 2.0
        g.link(g.vmath("SCALE", geo.outputs["Position"], scale=BM["noise"]), nz.inputs["Vector"])
        brk = g.math("ADD", 0.55, g.math("MULTIPLY", ss(nz.outputs["Fac"], 0.35, 0.65), 0.45))
        stren = g.math("MULTIPLY", g.math("MULTIPLY", g.math("MULTIPLY", rad, ax), brk), k_emit)
        em = g.n("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*col, 1)
        g.link(stren, em.inputs["Strength"])
        eh = g.n("ShaderNodeEmission")                       # the core runs hotter (toward white)
        eh.inputs["Color"].default_value = (min(1, col[0] * 0.4 + 0.6), min(1, col[1] * 0.4 + 0.6), min(1, col[2] * 0.4 + 0.6), 1)
        g.link(g.math("MULTIPLY", g.math("MULTIPLY", stren, core), BM["hot"]), eh.inputs["Strength"])
        tr = g.n("ShaderNodeBsdfTransparent")
        ad = g.n("ShaderNodeAddShader")
        g.link(tr.outputs[0], ad.inputs[0])
        g.link(em.outputs[0], ad.inputs[1])
        ad2 = g.n("ShaderNodeAddShader")
        g.link(ad.outputs[0], ad2.inputs[0])
        g.link(eh.outputs[0], ad2.inputs[1])
        g.link(ad2.outputs[0], g.out.inputs["Surface"])
        return m

    def beam_shaft(name, org, dirv, length, half_deg, mat, seg=48):
        me_ = bpy.data.meshes.new(name)
        b_ = bmesh.new()
        r0, r1 = 0.4 / length, math.tan(math.radians(half_deg))
        lo_ = [b_.verts.new((r0 * math.cos(2 * math.pi * i / seg), r0 * math.sin(2 * math.pi * i / seg), 0.0)) for i in range(seg)]
        hi_ = [b_.verts.new((r1 * math.cos(2 * math.pi * i / seg), r1 * math.sin(2 * math.pi * i / seg), 1.0)) for i in range(seg)]
        for i in range(seg):
            j = (i + 1) % seg
            f_ = b_.faces.new((lo_[i], lo_[j], hi_[j], hi_[i]))
            f_.smooth = True
        b_.to_mesh(me_)
        b_.free()
        me_.materials.append(mat)
        ob_ = bpy.data.objects.new(name, me_)
        ob_.location = org
        ob_.rotation_euler = Vector(dirv).normalized().to_track_quat("Z", "Y").to_euler()
        ob_.scale = (length, length, length)
        for v_ in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
            setattr(ob_, v_, False)                          # camera only
        scene.collection.objects.link(ob_)
        return ob_
    BEAMS, BEAM_AX = [], []
    for k_, v in sorted(LM.items()):
        if v[1] is None:
            continue
        hh = (sum(map(ord, k_)) % 97) / 97.0
        lean = Vector(((hh - 0.5) * BM["lean"], (0.5 - hh) * BM["lean"] * 0.6, 1.0)).normalized()
        org = Vector(v[1]) + Vector((0, 0, 0.5))
        L_ = BM["len"]
        while L_ > 40.0 and not in_frame(org + lean * L_ * BM["fade"]):
            L_ *= 0.9
        rot = lean.to_track_quat("-Z", "Y").to_euler()
        ob = light("beam_%s_haze" % k_, "SPOT", tuple(org), BM["haze_power"], v[2], rot=rot, spot=BM["haze_cone"], blend=1.0, shadow=False)
        ob.light_linking.receiver_collection = rx_fog
        BEAMS.append(ob)
        beam_shaft("beam_%s_shaft" % k_, tuple(org), tuple(lean), L_, BM["half"], beam_mat("beam_%s_mat" % k_, v[2], BM["emit"]))
        BEAM_AX.append((k_, tuple(org), tuple(org + lean * L_ * BM["fade"])))
    print("BEAMS landmarks", [(k_, round((Vector(b_) - Vector(a_)).length / BM["fade"])) for k_, a_, b_ in BEAM_AX], flush=True)
    # landmark key lights (the landmark lighting rig: one key + one hue fill each)
    for k_, s in enumerate(LIGHT_SPOTS):
        o = light("lmk_%d" % k_, "SPOT", s["loc"], s["power"] * 1.5, s["col"], rot=aim(s["loc"], s["tgt"]), spot=s["cone"], blend=0.6)
    # water shafts: spots from above the surface, tilted along the moon, linked to the water volume + seabed
    SH = WAT["shafts"]
    RS2 = random.Random(CP.SEEDS["sea"] + 1)
    hx_, hy_ = W(O["hq"]["tethys"])
    for k_ in range(SH["n"]):
        x = hx_ + RS2.uniform(-140, 140)
        y = hy_ + RS2.uniform(-140, 140)
        a_, b_ = ab_w(x, y)
        if not ((math.floor(x / U + CX), math.floor(-y / U + CY)) in WET_CELLS or b_ > bwall(a_) + 2):
            x, y = hx_ + RS2.uniform(-40, 40), hy_ + RS2.uniform(-40, 40)
        tl = RS2.uniform(*SH["tilt"])
        o = light("shaft_%d" % k_, "SPOT", (x, y, ZW + 40.0), SH["power"], (0.75, 0.92, 1.0),
                  rot=Vector((tl, -tl * 0.5, -1.0)).normalized().to_track_quat("-Z", "Y").to_euler(), spot=SH["cone"], blend=0.4, shadow=False)
        o.light_linking.receiver_collection = rx_w
    rx_w.objects.link(OBJ["seabed"])
    # the media are lit by their own lights only (r3: city glow and beams light the fog; the shafts light the water):
    # the moon and the sky skip both volumes, so the water is not a moonlit milk
    ex = bpy.data.collections.new("moon_excl")
    scene.collection.children.link(ex)
    ex.objects.link(fog)
    ex.objects.link(wv)
    MOON.light_linking.receiver_collection = ex
    for co in ex.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    # the underwater skylight (rule): the lit surface seen from below. Area lights just under the surface, facing
    # down, one per 60 BU tile that has drowned cells under it; they skip the media (no milk) and light the drowned
    # roofs and the seabed with shadows, so the submerged city keeps its form
    UW = WAT["under_sky"]
    tiles_ = {}
    for (i, j) in WET_CELLS:
        x, y = W((i + 0.5, j + 0.5))
        tiles_.setdefault((int(math.floor(x / UW["tile"])), int(math.floor(y / UW["tile"]))), 0)
        tiles_[(int(math.floor(x / UW["tile"])), int(math.floor(y / UW["tile"])))] += 1
    for a_ in range(-12, 13):                 # the near sea along the wall too
        for b_off in (4.0, 14.0):
            x, y = w_ab(a_ * 9.0, bwall(a_ * 9.0) + 1.2 + b_off)
            tiles_.setdefault((int(math.floor(x / UW["tile"])), int(math.floor(y / UW["tile"]))), 1)
    for (tx_, ty_), n_ in sorted(tiles_.items()):
        o = light("uw_%d_%d" % (tx_, ty_), "AREA", ((tx_ + 0.5) * UW["tile"], (ty_ + 0.5) * UW["tile"], UW["z"]), UW["power"],
                  UW["col"], rot=(0, 0, 0), size=(UW["tile"], UW["tile"]), shadow=True)
        o.light_linking.receiver_collection = ex
    print("UNDERWATER sky tiles", len(tiles_), flush=True)
    try:
        wd.visibility.scatter = False
    except Exception:
        try:
            wd.cycles_visibility.scatter = False
        except Exception as e:
            print("world scatter visibility not set", e)
    for o in BEAMS:
        pass
    # render settings
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "HIP"
    try:
        prefs.use_hiprt = False
    except Exception:
        pass
    prefs.refresh_devices()
    for dv in prefs.devices:
        dv.use = dv.type == "HIP"
    print("DEVICES", [(dv.name, dv.type, dv.use) for dv in prefs.devices], flush=True)
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU" if os.environ.get("CITY_CPU") else "GPU"   # CITY_CPU=1: a tiny CPU smoke test (no GPU, no lock)
    cy.samples = SPP
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    cy.max_bounces = 6
    cy.diffuse_bounces = 1
    cy.glossy_bounces = 2
    cy.transmission_bounces = 2
    cy.volume_bounces = 0
    cy.transparent_max_bounces = 16
    cy.sample_clamp_indirect = 6.0
    cy.volume_step_rate = A["step_rate"]
    cy.volume_max_steps = A["max_steps"]
    cy.seed = 0
    cy.use_animated_seed = False
    scene.view_settings.view_transform = "Standard"
    vl = bpy.context.view_layer
    vl.use_pass_z = True
    vl.use_pass_emit = True
    im = scene.render.image_settings
    im.media_type = "MULTI_LAYER_IMAGE"
    im.file_format = "OPEN_EXR_MULTILAYER"
    im.color_depth = "32"
else:
    # MAINLINE: the kit's key (sun) + a dim world; no media (the post adds the mainline fog patches and haze)
    bg.inputs["Color"].default_value = (0.03, 0.025, 0.06, 1)
    bg.inputs["Strength"].default_value = 1.0
    light("key", "SUN", (0, 0, 500), 2.2, (1.0, 0.95, 0.9), rot=(math.radians(50), 0, math.radians(110)), shadow=True)
    light("fill", "SUN", (0, 0, 500), 0.5, (0.6, 0.65, 1.0), rot=(math.radians(60), 0, math.radians(-60)), shadow=False)
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    ee = scene.eevee
    ee.taa_render_samples = 16
    try:
        ee.shadow_resolution_scale = 1.0
    except Exception:
        pass
    scene.view_settings.view_transform = "Standard"
    vl = bpy.context.view_layer
    vl.use_pass_z = True
    im = scene.render.image_settings
    im.media_type = "MULTI_LAYER_IMAGE"
    im.file_format = "OPEN_EXR_MULTILAYER"
    im.color_depth = "32"


def exr_npy(path, stem, want):
    import OpenImageIO as oiio
    inp = oiio.ImageInput.open(path)
    k = 0
    got = []
    while inp.seek_subimage(k, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        px = _np.asarray(inp.read_image(k, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
        groups = {}
        for ci, nm in enumerate(names):
            parts = nm.split(".")
            pas = ".".join(parts[1:-1]) if len(parts) >= 3 else (parts[0] if len(parts) == 2 else nm)
            groups.setdefault(pas, []).append(ci)
        for pas, idx in groups.items():
            if pas in want:
                arr = px[..., idx[:3]] if pas != "Depth" else px[..., idx[:1]]
                _np.save(stem + "_" + want[pas] + ".npy", arr.astype(_np.float32 if pas == "Depth" else _np.float16))
                got.append(pas)
        k += 1
    inp.close()
    os.remove(path)
    print("EXR passes", got, flush=True)


import bpy_extras.object_utils as _ou  # noqa: E402


def anchors(path):
    def P(p):
        v = _ou.world_to_camera_view(scene, cam, Vector(p))
        return None if v.z <= 0 else [v.x * RX, (1 - v.y) * RY, v.z]
    A_ = {k: dict(label=P(v[0]), crown=P(v[1]) if v[1] else None, base=P((v[0][0], v[0][1], 0.0))) for k, v in LM.items()}
    A_["_station"] = P((*STATION["centre"], ZW))
    A_["_mainframe"] = P(STATION["mainframe"]) if "mainframe" in STATION else None
    A_["_sprawl"] = [P((*W(c["centre"]), 20.0)) for c in O["clusters"] if c["to"] == "sprawl"]
    A_["_beams"] = {k_: [P(a_), P(b_)] for k_, a_, b_ in globals().get("BEAM_AX", [])}
    json.dump(dict(anchors=A_, res=[RX, RY], cam=dict(loc=list(cam.location), lens=cam_d.lens)), open(path, "w"), indent=1)


stem = os.path.join(OUTDIR, "%s_%s" % (CAMK, MODE))
bpy.context.view_layer.update()
anchors(stem + "_anchors.json")
t1 = time.time()
scene.render.filepath = stem + ".exr"
bpy.ops.render.render(write_still=True)
print("TIME render %s %.1f s (build %.1f s)" % (stem, time.time() - t1, t1 - T0), flush=True)
exr_npy(stem + ".exr", stem, {"Combined": "rgb", "Emit": "emit", "Emission": "emit", "Depth": "z"})
if MODE == "main":
    # ink passes: normals and building ids as flat emission (material override), PNG
    def ov(kind):
        m = bpy.data.materials.new("ov_" + kind)
        g = NB(m)
        em = g.n("ShaderNodeEmission")
        if kind == "normal":
            geo = g.n("ShaderNodeNewGeometry")
            g.link(g.vmath("ADD", g.vmath("SCALE", geo.outputs["Normal"], scale=0.5), (0.5, 0.5, 0.5)), em.inputs["Color"])
        else:
            wn = g.n("ShaderNodeTexWhiteNoise")
            wn.noise_dimensions = "1D"
            g.link(g.math("MULTIPLY", g.attr("bid").outputs["Fac"], 97.0), wn.inputs["W"])
            g.link(wn.outputs["Color"], em.inputs["Color"])
        g.link(em.outputs[0], g.out.inputs[0])
        return m
    im.media_type = "IMAGE"
    im.file_format = "PNG"
    im.color_depth = "8"
    scene.eevee.taa_render_samples = 1
    scene.render.filter_size = 0.01
    for o in scene.objects:
        if o.type == "LIGHT":
            o.hide_render = True
    for kind in ("normal", "id"):
        bpy.context.view_layer.material_override = ov(kind)
        scene.render.filepath = stem + "_" + kind + ".png"
        bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.material_override = None
print("DONE %.1f s" % (time.time() - T0), flush=True)
