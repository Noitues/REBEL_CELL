# Cohesion redo 1: map pages on the r42 city

Pages (1920x1080): `hq_idle.png` (City Grid), `hq_node_selected.png` (Site dossier, Solace lime Site file, a different Site selected with focus brackets and cursor, no plan arrow), `route_page.png`, `raid_setup.png`. Also `grade_strengths.jpg`, `contact_old_vs_new.jpg`, `squint_<page>.png` (page left, 1/16 scale + blur back up, right).

## Chosen grade: STRONG, on all four pages
| strength | value outside / inside focus rect | saturation pull buildings / neon+avenues |
|---|---|---|
| light | x0.76 / x0.92 | 0.04 / 0.22 |
| mid (the brief's start) | x0.68 / x0.86 | 0.10 / 0.38 |
| strong (chosen) | x0.58 / x0.78 | 0.18 / 0.55 |
Neon = bright and saturated pixels (S>0.45, V>0.55), grown 1 px and blurred; they also lose a further 12% value outside the lit spot. Mid left the r42 towers and strips louder than the chrome once the page was squinted; strong keeps lime park, violet/blue towers and cyan/green avenues recognisable (hue untouched) but lets lime links, orange options and red pencil lead. Extras: a soft lit vignette round the selected Site (hq pages, 70% lift), a corridor dim round the route (route page, x0.62 away from the path), raid page one more x0.9 notch (raid-mode step back; the roadmap raid grade is not otherwise made).

## What was reused / rebuilt
- Reused unchanged (copied from round44 A_map/scripts, originals untouched): all chrome draw code: HUD strip, work order paper, polaroids, tabs, JACK IN / START DEFENSE / NETRUN stickers, holo panels, terminals, dossier, key strip, pencils, markers, toasts (`hq44.py`, `route44.py`, `raid44.py`, `kit44.py` etc., imported and patched at run time in `build_*.py`; only change in the copies: font ROOT path in `sticker_lib19/31.py`).
- Chrome was NOT separate layers; it is PIL draw code over a Blender plate. The plate cannot be reused, so rebuilt: (1) the backdrop (r42 `plan_r42.png`; route page is a 2x crop of the downtown, with unsharp); (2) the Blender camera, replaced by an affine lot->pixel map (`Aff` in `r42lib.py`); (3) links, which were Blender decals, as PIL glow lines (lime owned, orange dashed border, grey cleared); (4) the raid node frames, forecast rings and health fill as PIL iso diamonds (approximation of the old decals); (5) the grade.
- `veh_beauty/veh_layout` (THREAT INTEL silhouettes) re-rendered with Blender headless by `run44.py veh` into scratch/ (not committed).
- Solace: site file holo uses lime #96FF46 (set in the run-time `K.CORP`, `ui31.py` still holds the old #3DFF8B); corporate Site discs carry the Solace helix emblem in lime instead of Meridian's crane. Availability rings and border links stay orange and Cell links stay Cell lime #D4FF00 (bible 2.4: Solace never on a link or ring).

## Placement
- HQ pages and raid: network sits on the downtown streets between the ring highway and the park; all nodes on land, no link over water or the helix. The Solace helix is the TARGET: red pencil circle round it plus the CENTRAL SERVER chip (the old page's off-screen edge arrow no longer applies since the HQ is in frame). Raid network is shifted left so entry A and the THREAT INTEL panel do not collide.
- Route page: TARGET rack node and route sit in the dense downtown, no water or helix in the crop.
- Nodes are on grid lines projected by one affine, not snapped to the exact r42 road lattice (approximate, as allowed).

## Squint verdicts (1/16 scale)
- hq_idle: PASS. Lime network, circled Site (yellow pencil) and red TARGET circle read first after the paper and Site file. Fix applied: strong grade, lit vignette, thicker links with a dark under-stroke, smaller TARGET circle. Weakest read: the selected Site's yellow circle (small).
- hq_node_selected: PASS with the same caveat (selected heat Site is an orange flame disc, brackets are small).
- route_page: PASS after fixes. First squint failed (TARGET and options lost in a bright, sharp 2x city). Fixed with strong grade, corridor dim round the route, route lines 9 px (walked) / 6.5 px dashed (options), no lit vignette. Now the lime path, orange options and the red TARGET read.
- raid_setup: PASS. Red threat routes, entry circles and the pink core frame lead; green frames read as a grid.

## Open issues
1. Site names and rewards are still the Meridian-flavoured data (PRIORITY LANE EXCHANGE, SINK THE CARGO LOGS) under a SOLACE file; the node_selected rows (heat objective, rewards, link) are placeholder text I wrote. Needs a Solace site list.
2. The work order, toast and THREAT INTEL stay Meridian (read as a rival corp raiding the Solace-city Cell). Designer to confirm. The "RUNNER" polaroid etc. unchanged.
3. Solace lime (#96FF46) vs Cell lime (#D4FF00) are close: Site file and crests vs fists. Separated by shape and placement only; check in the build.
4. Route page and raid frames are approximations of the old decals (no packets, no health bars drain art); the route page dossier still says MERIDIAN.
5. r42 at 2x crop is soft/upscaled; a proper route-page plate would need an r42-style camera render at transit zoom.
6. Old pages' hover_all route variant and HQ CORE-selected card were not remade (not requested).
7. Process slip: I twice typed `python -` inside a shell command (a stdin read that hung, then was stopped by task id). No code was run from it and nothing was changed by it.

Rebuild: from `scripts/`: `python layout36.py`, `NET36=net_scope.json python scope39.py`, `python run44.py veh` (Blender), copy `route_map_graph/hq_solace/scratch/emblems/*.png` to `scratch/emblems/`, `python runmap38.py` (RUN_V3=1 NET36=net_scope.json), then `python build_hq.py idle selected --grade strong`, `python build_route.py --grade strong`, `python build_raid.py --grade strong`, `python squint.py hq_idle hq_node_selected route_page raid_setup`, `python make_strip.py`, `python make_contact.py`.

## Solace names (2026-10-30)
Designer ruling: Solace is the only vertical slice, so every name and order on these four plates is Solace. Display text only: data ids (`sink_the_cargo_logs`, `m2_d`), corp keys (`meridian`, `MERIDIAN` in the veh/unit data) and gameplay terms are unchanged.

| old (Meridian) | new (Solace) | where |
|---|---|---|
| MERIDIAN FREIGHT | SOLACE BIOSYSTEMS | work order head (hq, raid), THREAT INTEL sub, route dossier header |
| ROUTE AUDIT | CULTURE AUDIT | HQ work order title |
| MANIFEST AUDIT | STRAIN AUDIT | raid work order title |
| YARD SECURITY | GARDEN SECURITY | HQ work order sub |
| WO 52-MF / WO 52-MF-207 | WO 52-SB / WO 52-SB-207 | work order codes (MF = Meridian Freight) |
| YARD SECURITY NET | GARDEN NET | THREAT INTEL sub (shortened to fit the holo) |
| PRIORITY LANE EXCHANGE | SEED VAULT EXCHANGE | Site name tag, T2 Site file title, jack hint (PRIORITY_LANE to SEED_VAULT) |
| Priority exchange // router run | Seed exchange // router run | T2 Site file TYPE row |
| SINK THE CARGO LOGS | BURN THE TRIAL LOGS | T3 Site file title, name tag (SINK CARGO LOGS to BURN TRIAL LOGS), jack hint |
| RETURNS PROCESSING / RETURNS PROC. | CULTURE INTAKE | Site LINK row, NOVA status, YOUR NETWORK row |
| SHIFT PLANNER | GROWTH PLANNER | T3 Site LINK row, YOUR NETWORK row |
| HAULER + COURIER | WARDEN + SPORE DRONE | THREAT INTEL route rows A/B/C |
| HAULER / COURIER (silhouette labels) | WARDEN / SPORE DRONE | THREAT INTEL unit labels (the silhouettes are still the truck and van models) |
| MERIDIAN (dossier header) | SOLACE | route page CELL-9 file |
| FREIGHT SECURITY | BIOSECURITY | route page CELL-9 file |
| INTERCEPTED // MERIDIAN: lane audit moved up a shift | INTERCEPTED // SOLACE: culture-lane audit moved up a shift | HQ toast (already the text on the idle plate in build_hq) |

Code touched (copies in `scripts/` only): `build_hq.py`, `hq44.py`, `raid44.py`, `kit44.py` (work_order defaults), `r35ui.py` (dossier). One non-text fix in `kit44.py` `chip()`: the box width now includes the 0.8 px K.text tracking, so the last glyph of the Site name tags (e.g. the S in BURN TRIAL LOGS) no longer runs into the box border. This also widens chips on any other plate that uses `KT.chip`.

Kept as is, to decide: ROUTING MIRROR (YOUR NETWORK node, not in the ruling list); the TARGET / CENTRAL SERVER / CORE (home) wording; the threat silhouettes (truck and van models under WARDEN / SPORE DRONE); the route dossier header stays in the Meridian orange (`MER`), not Solace lime.

Rebuilt: `python build_hq.py idle selected --grade strong`, `python build_route.py --grade strong`, `python build_raid.py --grade strong`, `python build_hq.py strengths`, `python make_strip.py`, `python make_contact.py`, `python squint.py hq_idle hq_node_selected route_page raid_setup`.
