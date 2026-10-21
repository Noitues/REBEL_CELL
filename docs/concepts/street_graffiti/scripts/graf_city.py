"""Whole-city panel hook (A2 hero camera): patched into city_render.py (exec'd by city_build.py) before its render stem.

Paints the city facade material at city scale (murals and heaven blockbusters must read from the hero camera), tints the
fog scatter toward soft neon and adds neon haze lights over the districts.
"""
import json
import os

import graf_look as GL

CFG = json.loads(os.environ.get("GRAF_CFG", "{}"))


def patch_src(fname, src):
    if fname == "city_render.py":
        key = 'stem = os.path.join(OUTDIR, "%s_%s" % (CAMK, MODE))'
        assert key in src
        src = src.replace(key, "import graf_city as _GC\n_GC.apply_city(globals())\n" + key, 1)
        k2 = 'vs.inputs["Color"].default_value = (0.85, 0.80, 1.0, 1)'
        assert k2 in src
        c = CFG.get("fog_col", (0.80, 0.66, 0.95))
        src = src.replace(k2, 'vs.inputs["Color"].default_value = (%f, %f, %f, 1)' % tuple(c), 1)
    return src


def apply_city(g):
    if CFG.get("off"):
        return
    # light touch at city zoom (designer 2026-10-21): rare heaven spots, lower floors only, no patches above
    cfg = dict(dict(scale=36.0, heaven_scale=110.0, cell=30.0, heaven_cell=45.0, heaven_p=0.10, street_z=(8.0, 18.0), up_k=0.0,
                    glow_k=0.6, roof_k=0.0, roof_k2=0.0, z_floor=0.5), **CFG)
    MS = g["MS"]
    n = GL.paint(MS.get("surf"), cfg)
    # district glow lights (they light the low fog): half their district hue, half Cell neon, and brighter
    import random
    rng = random.Random(cfg.get("seed", 20261021))
    pal = GL.NEON_HAZE
    ng = 0
    for ob in sorted(g["scene"].objects, key=lambda o: o.name):
        if ob.type == "LIGHT" and ob.name.startswith(("glow_", "roofwash_")):
            c0, c1 = tuple(ob.data.color), rng.choice(pal)
            mk = cfg.get("neon_mix", 0.5)
            ob.data.color = tuple((1 - mk) * a + mk * b for a, b in zip(c0, c1))
            ob.data.energy *= cfg.get("glow_light_k", 1.6)
            ng += 1
    print("[graf] city glow lights retinted", ng, flush=True)
    pts = [tuple(p) for p in cfg.get("haze_pts", [])]
    hl = GL.haze_lights(None, cfg, pts) if pts else []
    print("[graf] city paint bsdf", n, "haze lights", len(hl), flush=True)
