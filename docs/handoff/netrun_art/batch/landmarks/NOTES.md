DRAFT for the art-pass session; unverified (no render).

# Landmark modules: assumptions and open points

## aurelian (parses; ok)

- ASSUMPTION: `ctx.district` is the `DIST["aurelian"]` dict, indexable as `["mat"][0]` and `["sec"]`, as in the built-in (`D["mat"][0]`, `D["sec"]`). It is not listed in the templates' ctx use, but `landmark_ctx` supplies it.
- ASSUMPTION: `ctx.CP.AURELIAN_LM` has the keys `recess`, `cols`, `col_r`, `steps`, as in the built-in. The ctx hands out CP as an attribute.
- ASSUMPTION: `ctx.hq` is a (x, y) world pair, used exactly as `hq_w` was.
- Ported 1:1 from `landmarks.aurelian()`: same primitives, call arguments, colors and light values (2.4e6/40 and 1.4e6/38). The only edit is that each exec-global became a ctx attribute.
- One small change: the colonnade column angle was `2*pi*(m + 0.5*(k%2==1)*0)/cols`, and the `*0` term is dropped. The result is identical, since it was always 0.
- Return changed from a tuple to the hook dict `dict(label, crown, hue)`. `label` is (hx, hy, 40) and `crown` is (hx, hy, 26), as in the built-in.
- No randomness is used because the built-in uses none. `stream_rng` (FNV-1a 64 plus splitmix64, spec 3.5) is provided but not called. Unverified against the pipeline's reference hash.
- The footprint "ellipse 36 x 30" is read as semi-axes. If it is full width/height, the campanili (outer extent about 24.4 x 19.5 at 45 deg) still fit, and the bowl's outer edge (about 32.5 x 26.3) sits at 90 % of the semi-axes. Verify against `LANDMARK_FP["aurelian"]` and the "inside the lot" check.
- `fit_scale` (spec 8.6 k_fit) is provided but NOT applied in `build(ctx)`. The city footprint is fixed, so k_fit should be about 1.0. Applying it would need a place()-style wrapper like Meridian's.
- `fit_scale`'s margin default of 1.5 BU is `fp_margin` 0.25 lots x 6; its extent uses the campanili radius x 1.2. Both are my guesses.
- `landmark_info()['central_server_name']` is THE ROSTRUM from `identity.md`. The spec says Aurelian's name is a made-up gap name, so confirm it with the designer.
- `hub_name` (THE GRAND STAND) is extra and optional.
- `tier_heights` is derived from constants: 3 tiers of 5.0, attic 3.0 (top 18.0), campanile top about 31.7, rostrum column top 22, laurel ring 25. The 12.2 check reads pass indices {1, 5, 6} (per the template convention), but this city module does not set them. The art-pass session wires them in the Blender build.
- `build_hq` is a stub that raises NotImplementedError. No `hq_build` source was supplied, only the concept's stub and the `hq` preset keys (bowl r 150, terraces, 18 rooms, gate rings). The docstring TODO lists what the HQ builder must expose.
- The concept's HQ numbers (r 150, 18 rooms, gate steps) are in different kit units from the city model (A 31). Spec 8.6b needs a single model, so the HQ must be rebuilt from this city model, not from the concept bowl.
- Spec 8.6b conflict: the concept HQ is a four-tier arcade bowl with turning gate rings, and the city model is a three-tier colonnade plus attic. The city design wins per 8.6b, so the "four arcade tiers" in the `landmarks.py` header doesn't match the code: the code has 3 colonnade tiers and 4 seating rings.
- Design-pass dependency (DR 1398): the HQ netrun view is blocked until the Aurelian HQ design pass is done.
- Not implemented: key-location landmark types (8.8, `key_landmarks.py`). The aqueduct, triumph arch, piazza and campanile building types in the concept scene are separate items.
- To verify by rendering: the silhouette at 320 px against the concept `hq_overview.png`. Whether the recessed wall plus column rows read as a colonnade. The warm floods staying within the 1.5-2.0x landmark ratio. The `bid` and `uvs` window values on the prism and cyl calls (unchanged, but never tested through `ctx`).
- Verify that `prism`, `circle`, `annulus` and `ring_line` in the ctx accept the exact keywords used (`ry`, `k0`, `k1`, `top`, `uvs`, `vz0`, `wc`, `wl`, `wm`, `bid`). They match the built-in's own calls.
- The module needs `ast.parse` and a headless smoke test with a recording ctx stub, which the art-pass session should add. Nothing was run here.

## halcyon (parses; ok)

- ASSUMPTION: the city hook is a faithful port of `landmarks.halcyon()`: same tier numbers (29.0 ... 8.6, 5.6 high), gallery ribbons, vault, eye and two spots. Only the globals changed (`hq_w` to `ctx.hq`, `DIST` to `ctx.district`, `CAMDIR` to `ctx.camdir`).
- The original draws no randomness, so `rng()` is provided for the stream contract but is never called. Determinism comes from rules only.
- Everything has to be inside the lot (all geometry is within 29.3 BU of `ctx.hq`). The clearance is 33.6 BU. I did not read `ctx.footprint` because its shape for Halcyon (number, tuple or dict) is not shown. Art-pass: verify, and use it for `k_fit` (8.6) if the game lot is smaller than 58.6 BU.
- The `fit` parameter named in the docstring is NOT implemented. Dropped to keep the port faithful. Add a scale about `ctx.hq` if the build session wants k_fit.
- `landmark_info()['total_height_bu']` is an estimate (vault top + 7 + 3.4 for the eye). It is not a rendered measurement.
- `build_hq` is a stub that raises `NotImplementedError`. No Halcyon hq_build source was supplied; the TODO list is in its docstring (slots from the game graph, eye lights, beams, hooks).
- The 8.6b canonical rule needs the HQ netrun silhouette to match this one (IoU >= 0.85 at 320 px). The NOTES describe the netrun pyramid with tier 13 kit BU on a 6 BU podium and 73 BU half-size. The city version has no podium and 6 tiers at 29 BU. Q: which is canonical for proportions?
- `ctx.camdir` is read as a tuple/vector with `[0]` and `[1]` (`landmark_ctx` passes `tuple(CAMDIR)`). The original used `.x`/`.y`. Verify the eye faces the map camera (yaw 135).
- `ctx.district['hue']` is used for the edge lines, iris and fill light. Relied on: `district`, `camdir`, `hq`, `spot_at`, `sc`, `box`, `cyl`, `bar`, `SURF`, `SMOOTH`, `NEON`. The template Tethys hook also uses `ctx.station`, `ctx.zw`, `ctx.W` and `ctx.O`; none are needed here.
- `NEON.face(pts, col)` and `SURF.face(pts, col)` are called with 2 args for the almond, iris and pupil, as in the original. Verify against the accumulator signature (`face(pts, col, uv, wc, wl, wm, bid, wet)`).
- The `box()` keyword args (`wc`, `wl`, `wm`, `bid`) follow the built-in. They are untested outside `landmarks.py`.
- Spot positions are offsets from the HQ centre as in the original (key at +90, -90, 70; fill at -70, -110, 30). The target is (hx, hy, 18).
- The code imports `SimpleNamespace` but does not use it, so it is harmless. Pure stdlib; it should pass `ast.parse` but was not run.
- Not rendered. Art-pass must check: the gallery ribbons' direction (counter-clockwise from above), the eye reading from the map camera, and the landmark ratio (12.2, 1.5-2x pass; above 2x warns only).
- The HQ netrun Halcyon landmark lighting rule (8.3: coves, uplights, teal reveals) is not part of the city built-in, so it is absent.
- The Halcyon cleared perimeter belt is not built (spec 8.2, C6). The city module draws none.
- The central server name constant is THE PANOPTICON (GDD 11.7 working name), not "Civic Core".
- Q: should the 8.5 netrun landmark keep the eye turret at drum r 12.5 kit BU (about 3.0 city BU after k_units)? The city drum is 3.6 BU, about 15 kit BU. Left as in the city built-in.

## orbital (parses; ok)

- ASSUMPTION: `ctx.district` is `DIST["orbital"]` with keys `hue`, `sec` (the built-in uses `D["hue"]`, `D["sec"]`); `HUE` is only a fallback.
- ASSUMPTION: `ctx.CP.ORBITAL_PAD` exists with `n`, `mast_h`, `aim_z`, `power`, `cone`, `blend`, `rim_lamp_k` (the built-in reads it). Not verified.
- ASSUMPTION: the city's light list accepts `dict(loc, tgt, col, power, cone, blend, k)` appended to `ctx.light_spots`, as the built-in does. `ctx.spot_at` has no blend argument, so I used the list directly.
- Not run and not rendered; only meant to parse with `ast.parse`.
- City build is a faithful port of `landmarks.orbital()`. All coordinates, colors, call shapes (including the odd `annulus` call for the dish bases) are kept verbatim. Its `Vector` use was replaced by tuple helpers because of the stdlib-only rule.
- The city build draws no random numbers, so `ctx.seed` is unused there. `stream_seed` (FNV-1a 64) is provided for the HQ dish tilts (legacy literal 7320). The GDScript twin must match it.
- Footprint: podium r 22 plus the rim lamps and the tower corner (17.6, 15.6) give about 24 BU. `FOOTPRINT_R_BU` is derived by me. The art-pass session must check it against `ctx.footprint` (landmark_r 5.6 lots = 33.6 BU). There is no `k_fit` (spec 8.6) in the city build; if the lot differs, wrap with a scale.
- The rocket tops out at 38 BU and the antenna at 83 BU with its mast. This is taller than the podium-scale tiers, so check the silhouette at 320 px in the map camera (8.6b IoU check).
- `build_hq` is ported from `hq_build.py`: podium, painted marks, door rails, shaft, lock lamps, doors, rocket and three hack bands, gantry, antenna truss, dishes, stations, causeway, pad flood masts, hero beams.
- Dropped from `build_hq`: the launch cutscene props (strike site, flight, trail, boom), `hooks["apply"]` (shaft/lock/band weights, per-frame key/rim re-aiming) and `post_build`. Reason: they depend on bpy or on per-frame mover state, and the pipeline's mechanic visuals are driven from game state (8.4 rule 4). A follow-up port is needed; the per-frame occlusion and key lights belong with `apply`.
- Dropped: the `rim_*` area lights with the `rim_rx` collection (needs `bpy.data.collections`). Add them in the kit via a `K.new_collection` hook, or accept the city's own rim.
- Dropped: the 4 outer-room dish bowl faces (6x28 patches) and the `underfog_*` lights. Only the lit rim ring and the dish stem remain on the stations.
- `build_hq` needs these K attributes beyond the Meridian template: `K.obox`, `K.oquad`, `K.mover(name)` returning a dict with `accs`, `K.rf`, `K.room_shell`, `K.Vector`, `K.ROOM_EMIT`, `K.COLL["movers"/"media"]`, `K.M["emit"/"rough"]`, `K.G.az_vec/STATION/ORDER/ROOM/RL/GROUND_Z`.
- `place()` proxies A, Acc, movers and add_light. Mover objects (rocket, doors) still need their rest transforms scaled by the kit when placed in the city. Not verified.
- Topology (8.4): stations and antenna rooms are built only from `G.STATION`/`G.ROOM`/`AN["rooms"]`, i.e. the game graph mapped to slots. The mock circuit lists are not read here. A graph with a different slot count needs the hq_graph slot generator (Q2 in spec 14.1).
- `rooms=False` skips stations, vault rooms and the causeway (the city has no rooms). The mover rocket is still built, so the HQ and city silhouettes can differ in the doors (HQ shut/open is state-driven, the city is open). Check against the 8.6b rule.
- The rocket in the city is permanently risen out of the open silo. If the pipeline wants "doors shut" as the default, the city hook needs a state flag. Not specified in the supplied sources.
- Landmark ratio (12.2): the old HQ stills measured 2.5-3.0x, which warns but does not fail. Check again after the city lights (pad masts) and the keyed rocket are rendered. `landmark_info()["tier_heights"]` is my summary of the built-in numbers, not a spec value.
- `CENTRAL_SERVER_NAME = "LAUNCH CONTROL"` is the GDD 11.7 working name. The NOTES flag the name as open (Q1: Launch Control / Commons Array / Missile Bay).
- The tower is placed at lot offset (+14, +12) in world axes, as in the built-in. The `landmark_ctx` rotation of the map camera (yaw 135) is not applied. Check that the tower faces the camera as intended.
- The build has not been checked for overlap with `LANDMARK_FP["orbital"]`; an unverified claim in the docstring ("everything inside the footprint") must be confirmed by a footprint check in `checks`.

## rebel_cell (parses; ok)

- First-line conflict: the answer starts with the =====PY===== marker as the task format demands; the DRAFT line is the first line of the module docstring.
- ASSUMPTION: `ctx.camdir` is the xy direction from the scene toward the camera (Halcyon's built-in uses CAMDIR that way). The built-in's `seen()` is not in ctx, so `_seen()` is my reimplementation (outward normal, visible if normal . camdir > 0.05). The 0.05 threshold is a guess; the original `seen` must be compared on the seed-1 city to confirm the same building and face get chosen.
- Not in ctx: `KH` (I read `ctx.CP.KH`, as the Tethys template does), `SIGNS` (the built-in's module global) and `os`. I append the sign quad to `ctx.station["signs"]`; the city renderer must read it from there, or `landmarks.py` must expose a `signs` attribute. Needs a one-line change on the build session's side.
- The sign texture path is `str(ctx.CP.SCR) + "/mainframe_blade.png"` (no `os` allowed); on Windows the mixed separator should be harmless but is unverified.
- `ctx.station["mainframe"]` and `["mainframe_building"]` are set; the original set only `"mainframe"`.
- Hue is `ctx.district["hue"]` (ctx.district = DIST[corp]); the built-in returned `DIST["rebel_cell"]["hue"]`. Same value if the ctx wiring is as documented.
- "Everything inside the lot footprint" cannot hold: the sign belongs to the building nearest the HQ lot anywhere in the Rebel Cell territory, and the blade overhangs the street by 3.3 BU. `ctx.footprint` is None for this corp (no landmark). Check 8.6 (the 90 % lot cover) must be exempt for Rebel Cell. Q for the designer below.
- Not ported: nothing in the city function is dropped. No randomness is drawn; `_rng` exists only for the HQ build and is currently unused there as well.
- MAINFRAME is now held to the normal 2x landmark rule (spec 8.5, Designer 2026-10-16). The built-in's red spot (3.0e4) and the wash strip are unchanged, so they are probably too weak for 1.5-2x. The art-pass session must render and check R-FOCUS-1 and 12.2 with the sign box from the object-index pass, and tune the spot or add a floor wash.
- The HQ page's MAINFRAME hero (`mf_w` 11 BU, about 45 BU tall in kit units) differs from the city blade (3 x 12 BU). Spec 8.6b says the full-city design is canonical, so the netrun sign should be rebuilt to the city blade's proportions. `build_hq` does NOT build any MAINFRAME sign: it lived in rc_alley, which was not supplied.
- Where MAINFRAME stands in a netrun (at the target, DISPATCH, per spec 8.5) is open; the city hook keeps the nearest-to-HQ-lot rule only.
- `build_hq` ports hq_build_A.py's non-v3 path only. The v3 branch (`rc_alley3`, `rc_sewer`, continuous frontage, rooftop lane) is dropped. Option C is not ported (the designer chose A).
- `build_hq` needs hooks that were not supplied: `K.district_build` (rc_district.build), `K.alley_build` (rc_alley.build), `K.new_collection` (replaces `import bpy` for the rim receivers collection) and `K.seq_lights` (rc_alley.seq_lights). Without `district_build` it logs and returns near-empty hooks. K.HZ["alley"]["x_a"/"x_b"] replaces the rc_alley.AL global in `free()`; that key path is a guess.
- Topology: G.ROOM, G.LANE, G.KIND, G.PATH, the three lanes and the SYNC STRIKE are MOCK route data (spec 8.4, C15). The game's graph must be mapped onto slots; this module does not do it. The SYNC STRIKE is a proposal, not in the GDD (see NOTES section 3).
- Sorting: the original iterated dicts in insertion order; I iterate `sorted(builds)` and `sorted(G.ROOM)` for determinism (spec 3.6). This can change draw order only, not geometry.
- `place()` is copied from the Meridian template (k_units 0.2375). `build_hq` was not run through `place()`; the `box`, `tube`, `obox` and `seg_box` helpers on K are used directly, so the K passed in must already be wrapped.
- The detour-hut lookup guards `if i not in G.ROOM`, a small addition to the original.
- `landmark_info()`: `footprint_bu` is None (ASSUMPTION; no compound). `tier_heights` holds the sign extents (2.4 .. 14.4), label z 34 and the 10 BU building minimum; there are no real tiers. The 12.2 check must use a sign box, not a compound box.
- No crown, no beam: returns `crown=None`, as the built-in's note 8 and the designer's ruling require. Verify the city renderer accepts None (the hook already does for other corps).
- Verify by rendering: sign readability at 320 px from the map camera (yaw 135), the sign not clipping a neighbor's face, the sign corner at 0.8 BU from the face corner, and that the red does not collide with the fist-window red (R-HUE rules exempt corp HQ views).
- Verify the `NEON.face(pts, col)` call with two arguments against `city_build.Acc.face` defaults; the template uses the longer signature for SURF.
- Q: Should the Rebel Cell sign (not the HQ) be allowed to exceed the lot-fill check 8.6, or should the sign be required to stand on the HQ lot's building itself?
- Q: Which is canonical for the MAINFRAME dimensions, the city blade (3 x 12 BU) or the HQ page hero (11 BU wide, about 45 BU tall in kit units)?
- Q: Does the pipeline want the sign's target placement (at DISPATCH, spec 8.5) driven from the game's key-location list instead of "nearest building to the HQ lot"?

## solace (parses; ok)

- ASSUMPTION: the city hook is a line-for-line port of `landmarks.solace()`. Only the Blender `Vector` use was replaced by tuple helpers (`_sub`, `_cross`, ...). Geometry, uv/window arguments, light powers and the SOLACE_LIFT factor are unchanged.
- The city build has no random draws, so no seed is consumed there. `art_rng` (fnv1a64 + splitmix64, stream names `landmark.solace.<use>`) is used only by the HQ podium planters. Legacy literals 6330/6331/6420 are listed in `LEGACY_SEEDS` for golden-image parity only. Spec 3.5 says the FNV and splitmix details need a build-session twin in GDScript; I did not check that the two match.
- `ctx.footprint`: I do not know Solace's `LANDMARK_FP` value. The code only prints a warning if a numeric footprint radius is under 12.0 BU. Verify against `city_preset.LANDMARK_FP["solace"]`.
- Spec 8.6c says "Solace (x1.8)" for the built-in. The supplied `solace()` has no scale parameter, so I ported it at x1.0 and did not guess where the 1.8 enters. Q: is x1.8 a CP value (e.g. the SOLACE_LIFT-style constant) or applied in `city_build`? If applied outside, `landmark_info()` footprint_bu must be multiplied by it.
- `landmark_info()["footprint_bu"]` is the plinth diameter (24 BU), a guess for the "footprint" the checks need. The helix itself spans 21.8 BU. `hue` is None because the district hue only exists on ctx at build time.
- ctx attributes used: `SURF, SMOOTH, NEON, box, cyl, dome, bar, ring_line, sc, spot_at, hq, district, footprint, CP` (CP only for `SOLACE_LIFT`, with a getattr default of 1.0). Not used from ctx: `GLASS, STREAK, strip, annulus, circle, prism, mixc, W, O, station, zw, seed`. The ctx primitives are assumed to accept the argument forms visible in `landmarks.py`.
- `SMOOTH.face` is called with the positional form from the built-in `(pts, col, uv, wc, wl, wm, bid, wet)`. Verify against `city_build.Acc.face`.
- The HQ port is reduced. Dropped: node cutaway windows with snapped vertices, jambs and frame rings, the office-floor kit (`hq_office`), the interior-mapping atlas and material (`hq_imap`), the frosted unread covers and their `apply` hook, the halo volume material, the container/porcelain material graphs, the tower-front stair ribbons, the planter loop's collection linking (`PLX`, `RIMRX`) and `post_build`.
- Strands in HQ mode are segment tubes (`K.tube`, 1.5 BU steps, 20 sides). That is many small solids and is not the shared-vertex smooth mesh of the original. Expect a faceted look and a higher object count. Render and compare against `H_overview_v3.png`.
- The HQ build uses `K.M["civic"]` for porcelain instead of the custom `porcelain_flat` / rim material. The leaf-green fresnel rim (`rim_k`, `rim_pow`) is not reproduced, so the landmark ratio will likely read low. The art session must restore the material in `hq_scene` or pass a porcelain material in `K.M`.
- HQ axis and azimuth conventions are guessed. If `K.G.tube_pt` exists it is used for the axis. Otherwise `theta = 90 + twist*(z - podium)/floor_h` degrees from +x, tower B at +180. The ground-spot and rim azimuth uses `(sin a, cos a)` for `G.az_vec`. Verify both against `hq_graph.py`.
- The crown boxes are axis-aligned on x. The original orients them on the tower-A normal with the `obox`/`oquad` frame. The crown, the Genome Core and the halo ring are centered on the midpoint of the two strand axes at the top. This is an approximation.
- The SOLACE lettering needs `K.oquad` and is silently skipped if absent. The bridge is built from axis to axis, trimmed by 0.8 tube radius, not from the cutaway window frames (`G.bridge_frame`). Check the bridge entry against the node windows.
- Route rooms are cut with `K.room_shell` only when `K.G` is given (spec 8.4: slots from the game graph). The module never creates nodes, edges or kinds. Needed from G: `NODES, TOWER, ROOM, floor_z, deck_z, tube_pt, stair_phi` (the last three optional, with fallbacks).
- Spec 8.6b silhouette match: the city twist is one turn per 62 BU of height at radius 7.5 (helix angle 37.2 deg). The HQ v3 is 36.7 deg (27 floors x 13.33 deg). The two builds are separate code paths with different tube radius/centerline ratios (city 3.4/7.5, HQ 10/40). The IoU >= 0.85 check at 320 px is untested; run it.
- Placing: `place()` copies the Meridian proxy. It scales the accumulators and lights (energy x k^2) but not K.tube / K.box radii, because those go through the accumulators' `.face` only if the helper emits faces there. Verify tube radii scale in a render, since `K.tube` may take a Blender path that bypasses `.face`.
- `build_hq` ignores `rail` (accepted only for API parity with Meridian). `K.seed` is optional (getattr), defaulting to 6331.
- Light levels (`LH["..."]` keys: `atrium_k, down_k, bridge_wall_k, bridge_route_k, trim_k, sign_k, plaza_wash_w, ground_spot_w, rim_w`) are read from the preset as in `hq_build.py`. The `entry_w` area light (0 in v3) and the `down_w` downlight spots were dropped.
- Not checked by any render: landmark ratio 1.5-2.0 (the v3 HQ reached 2.2-2.4x with the rim and porthole glow, which this port lacks), the value band, silhouette at 320 px, and that every vertex stays inside the lot (the city drum is r 12.0 by arithmetic only).
- Q: should the HQ port keep the per-window cutaways in this module, or stay in `corps/solace/` as a Blender-side plugin that calls this module for the silhouette only?
