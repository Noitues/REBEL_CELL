# M14 asset parity: city and screens (inventory)

Ruling (designer, 2026-10-05): every icon, sprite, texture, model or sheet the art pass made is
exported by running its own generator script from tag `art-concepts-r43` (drawing code unchanged;
a wrapper may split a sheet or pack channels) and used on main. Procedural only where no concept
asset exists. Wrappers live in `tools/art_pipeline/parity/`; each asset folder carries a
`manifest.json` (or `vehicles_manifest.json`) naming the source function and arguments.

Extract the concept scripts once: `git archive -o c.tar art-concepts-r43 docs/concepts/<round>/scripts ...`,
`tar -xf c.tar`; then `python tools/art_pipeline/parity/export_<x>.py --concepts <dir>/docs/concepts`.
Vehicles: `blender -b --factory-startup --python tools/art_pipeline/parity/blender_export_vehicles.py -- <concepts> assets/city/vehicles`.

## Replaced (exported, in use)

| Item | Folder | Source (tag art-concepts-r43) | Used by |
|---|---|---|---|
| Site disc art x14, pads x9, slip, cleared badge, DOWN bolt, Exploit key plate | `assets/city/grid_markers/` | round 42 `markers42.disc`, `cell_disc`, `seizure_memo`, `badge`, `pad`, `bolt_mask` (v4 key) | `SiteMarker`, `SiteMarkerView` |
| Route node stickers x5 (+ past), operative token | `assets/netrun/route/` | round 37 `r32ui.node_sd`, `token_sd` | `RouteOverlay` |
| Corp seal emblems x5, padlock, house motifs x5, post-its x4, print stock, manila | `assets/campaign_end/` | round 20 `lost20.padlock`, `motif`, `emblems20`; round 21 `dossier21.postit`, `sheet`, `manila` | `CorpSeal`, `RansomLock` (+ `ransom_lock.gdshader` `motif_tex`), `PostIt`, `DossierPhoto`, `AuditDossier` |
| Holo billboard panels (4, atlas; R = lightened-colour mask, A = alpha) | `assets/city/billboards/` | round 26 `cm._billboard_tex` (black and white renders packed) | `shaders/city/holo_billboard.gdshader` (`panel_tex`), set in `CityMotionLayers` |
| CLOSE flying car (36 triangles with part ids; also `flying_car.glb`) | `assets/city/vehicles/` | round 38 `unified38.flying_car` through Blender 5.2 | `CityMotionMeshes.car` (CLOSE tier; `sky_car.gdshader` parts) |
| Police chopper (body, neon, blades), drone (body, neon) glb | `assets/city/vehicles/` | round 20 `district20.heli_geo`, `drone_geo` through Blender 5.2 | `CityMotionMeshes.chopper` / `drone`, `CityMotionLayers._aircraft_body` (toon + ink; the blur disc takes the model's blade radius and height) |

## Procedural, with reasons

- State rings, pips, cables, depowered links, lock disc: follow state and zoom; the concept draws them as plain outlines.
- TARGET and the Heat words: the 1B grease-pencil kit, written on.
- Heat orbit lights and searchlights: move.
- Seal rings and name ring: translated text.
- Stamps: translated text with the 1B ink shader.
- Tape: a flat translucent rect, as the concept's `tape()`.
- PortraitFeed chrome: text and UI; its cracks are a seeded random walk in the concept too.
- 4B polaroid card: flat (246, 244, 236) in the concept.
- Dossier and node panel: text layouts on 1B paper and holo.
- NetrunMapView: hidden (`visible = false`; only the route model).
- FAR and MEDIUM car tiers, the street car, the lane line behind a car: a dot, a box and a streak in the concept (`cars_lod`).
- Billboard wipe, dropout, jitter, gain and tint: shader motion over the exported panels.
- Rotor blur disc: the ANIM entry replaces the concept's static blades.

## Proposed slice (not done here)

- Jack-in wheel (`jack_sequence._draw_wheel`): the concept notes call for the operative's real wheel
  scene; `zoom36.wheel` has fixed English labels and slice colours, so it is not the right asset.
  Slice: host the 2A WheelView as a ViewportTexture in `JackSequence`, with the combat parity sweep.

## Captures

`docs/art_review/ART-parity/city_screens/`: vehicles and billboards (`tools/city/vehicle_lab`), city close
night, Grid markers, campaign lost notice, audit dossier, netrun route.
