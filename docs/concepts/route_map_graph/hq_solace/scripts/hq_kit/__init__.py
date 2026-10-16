"""hq_kit: reusable HQ-run tooling (Halcyon is one config; see ../hq_graph.py, ../hq_cam.py, ../halcyon_preset.py).

Modules (pure python unless noted; no module imports Blender at import time):
  layout     Compound(cfg, watch)   the compound / run generator: spiral | switchback | explicit faces on a stepped
                                    square landmark, galleries, corner stairs, exterior climbs, the TARGET vault, the
                                    scan rule (lighthouse sector / whole face / none), the r3 graph API
  orbit      Orbit(compound, cfg)   the orbit camera: decision / hover / overview poses, zoom, face visibility; Pose
  city_ring  build(...)             the 360 degree ring city (Blender geometry through injected helpers), beams and
                                    glows by azimuth
  lod        weights(zoom)          the lod_bands (the storyboard's keys) and the zoom parameter
  states     STATE_COL, STATE_K     the room-state language: open / in the eye / walked / current / ahead / past / x-ray,
                                    scan lines, the crest badge, the rule word

A new HQ = a config dict for Compound + an Orbit cfg (optional) + a city cfg + a palette; the Halcyon scene
(../hq_scene.py) is the reference Blender build that consumes them.
"""
