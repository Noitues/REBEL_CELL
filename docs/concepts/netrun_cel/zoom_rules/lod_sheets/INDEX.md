# LOD sheets: every city element by zoom band

Spec: `../ZOOM_RULES.md` (bands in section 1, per-element tables in section 2 and 3). Code state: art/netrun-zoom round 1, head 9a5069c1 (read through the lab tool on branch `art/zoom-lod-sheets`).
Contact sheet: `INDEX.jpg`. One sheet per element, 1920 px wide: five band columns (City < 8 px/BU, District 8-16, Near-street 16-28, Street 28-56, Close >= 56).

Each sheet has, top to bottom:
1. the band header with a status bar: green BUILT, yellow PARTIAL, blue AS R43 (the r43 look carries the band, the spec's additions are not built), red NOT YET BUILT;
2. ISOLATED row: the element alone, scaled to fill the cell, at that band's px/BU (the corner label gives px/BU and the upscale). A dark cell with the spec text = nothing is built for that band;
3. IN CONTEXT row: the real city (seed 7, zoom rules on) at the same band and scale, wider crop, camera on a real instance;
4. caption strip: SPEC (condensed from ZOOM_RULES) and CODE (what round 1 actually builds, and what is missing, in the status colour).
Close is never rendered: nothing is built for it anywhere, so every Close column is a NOT YET BUILT cell with the spec text.

How the isolated shots were made (tool `tools/look_parity/lod_lab.gd`, branch `art/zoom-lod-sheets` in `D:/rc_art/godot_look_lod`): "lab" = a real prism and the band builders (`CityStreetPlan.wall` / `lamps`) alone on the dark outer ground with the city's lighting and post; "real instance" = no band-parametrised builder exists, so the real CityView3D camera is driven to the band's px/BU on a real instance and cropped tight.

| Sheet | Element | City | District | Near | Street | Close | Isolated source |
|---|---|---|---|---|---|---|---|
| lod_tower.jpg | Building: tall tower | built | partial | partial | built | none | lab prism |
| lod_midrise.jpg | Building: mid-rise with storefront | built | partial | partial | built | none | lab prism + storefront |
| lod_storefront.jpg | Storefront band | none | none | partial | built | none | lab prism + storefront |
| lod_sign_fascia.jpg | Signs: fascia T5 | none | none | partial | built | none | lab prism + storefront |
| lod_sign_blade.jpg | Signs: blade T3 | none | none | none | none | none | real instance (nothing to show) |
| lod_sign_roof.jpg | Signs: roof T2 | built | built | partial | partial | none | real instance |
| lod_sign_hero.jpg | Signs: hero T1 | built | built | partial | partial | none | real instance |
| lod_lamp.jpg | Lamp | built (r43) | as r43 | partial | partial | none | real (City, District), lab (Near, Street) |
| lod_tree.jpg | Tree / bush | built (r43) | as r43 | as r43 | as r43 | none | real instance |
| lod_park.jpg | Park / lawn | built (r43) | as r43 | as r43 | as r43 | none | real instance |
| lod_road.jpg | Road surface | built (r43) | partial | partial | partial | none | real instance |
| lod_clutter.jpg | Street clutter | none | none | partial | partial | none | real instance |
| lod_roofprops.jpg | Roof clutter | built | built | partial | partial | none | real instance |
| lod_modules.jpg | Facade modules (balcony, AC, pipe, fire escape) | none | none | none | partial | none | real instance |
| lod_highway.jpg | Highway deck and traffic | built (r43) | as r43 | as r43 | as r43 | none | real instance |
| lod_water.jpg | Water / quay | built (r43) | as r43 | as r43 | as r43 | none | real instance |
| lod_sky.jpg | Sky / fog | built (r43) | as r43 | partial | partial | none | lab: six towers at 15-360 BU |

Not given a sheet: HQ / site landmarks (2.8), aviation lights and sky traffic (2.9), terrain (2.7), netrun node objects (section 6, nothing built in round 1). They are listed here so the plan is complete.

## What to look at, for the designer
- **Tower / mid-rise:** compare the Near-street and Street cells with City. The facade grammar (cells, panel kinds, floor lines, mechanical band, corner neon) is the biggest built change; check the wall still reads as a dark plate and the windows are sparse. Missing at both: balcony / AC / pipe geometry, ledges, pilasters, crown ring.
- **Storefront and fascia:** the band is the brightest horizontal of the plate. Check continuity and brightness against the wall above it. The fascia text is clipped and overlaps on a 9 BU wall (visible as "LEALEMOEAR"): a known fault.
- **Lamp:** the real-scale lamp (pole, head, glow pool) only starts at Near-street; the District cell is still the r43 toy. Check whether the swap needs a District stage.
- **Tree / park / water / highway / roof signs / hero:** these show the r43 look at every band. The blue-boxed AS R43 cells are the plan to review: nothing of the spec's trunk, lumps, leaf cards, mow stripes, deck underside, quay detail is built.
- **Road:** the one element with a full Near-street and Street build; look at the lane lines, tracks and the pink lane glow strip, which dominates the carriageway and reads as a slab.
- **Sign blade, modules, clutter:** mostly red; review the spec text as the plan.
- **Sky:** the lab rig shows depth fog on six towers; the in-context row is the better read of sky and haze.

## Caveats seen while rendering
- The lab ground is the city's outer ground under the post: it reads dark blue at City / District and as a sea at Street. It is not a neutral grey.
- The isolated cell upscales small things (x2 to x15 on the City band); the corner label gives the factor. Soft edges there are the upscale, not the render.
- Tree and park in-context shots disable the forecourt discard (`zr_clear`), otherwise the rules remove the trees from the shot. In the Near-street shot a melting occluder shows as a dithered dark mass over the lawn.
- Real-instance shots use whatever the real city has at that pose, so neighbours and a melting occluder are visible.

Regenerate: `bash tools/look_parity/lod_lab.sh <raw dir> <log>` (worktree `D:/rc_art/godot_look_lod`, GPU lock) then `python scripts/make_lod_sheets.py <raw dir> <this dir>`.
