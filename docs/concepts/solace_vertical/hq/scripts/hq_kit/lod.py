"""hq_kit.lod: atmosphere detail by zoom (the storyboard's lod_bands, same keys and numbers).

    from hq_kit import lod
    z = lod.zoom(d, d_overview, d_decision)       # 0 = OVERVIEW .. 1 = DECISION (log distance)
    w = lod.weights(z, bands=None)                # {band: 0..1}
    lod.band(z, "signage_on_at")

Big layer (always on): fog banks, every beam incl. the scan beam, building / window lights, the route.
Bands (a, b): the layer fades in over zoom a..b with a smoothstep:
  fog_octaves_by_zoom  the fine octave + ragged fog edges        wisps_on_at      the thin wisp strata
  plumes_on_at         rooftop steam plumes                      signage_on_at    signs, holo ads, billboards
  small_lights_on_at   small lights + rain highlights            puddles_sharp_at puddle reflections sharpen
"""
import math

LOD_BANDS = {
    "fog_octaves_by_zoom": (0.25, 0.60),
    "wisps_on_at": (0.45, 0.70),
    "plumes_on_at": (0.50, 0.72),
    "signage_on_at": (0.60, 0.82),
    "small_lights_on_at": (0.75, 0.92),
    "puddles_sharp_at": (0.85, 1.00),
}
# the floor each band keeps when zoomed out (0 = gone), so e.g. a plinth name never vanishes entirely
FLOORS = {"signage_on_at": 0.0, "small_lights_on_at": 0.25}


def sstep(x, a, b):
    t = max(0.0, min(1.0, (x - a) / max(1e-6, b - a)))
    return t * t * (3 - 2 * t)


def zoom(d, d_overview, d_decision):
    return max(0.0, min(1.0, math.log(d_overview / d) / math.log(d_overview / d_decision)))


def band(z, name, bands=None):
    a, b = (bands or LOD_BANDS)[name]
    return sstep(z, a, b)


def weights(z, bands=None, floors=None):
    fl = FLOORS if floors is None else floors
    out = {}
    for k in (bands or LOD_BANDS):
        f = fl.get(k, 0.0)
        out[k] = f + (1.0 - f) * band(z, k, bands)
    return out
