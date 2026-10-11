## Implementation decisions (slice from DECISIONS.md:2909)

### 2026-10-05 ART-12 12s skins (DECISIONS.md:~2910)
- RULING 2026-10-05 skins: three skins `v2` (default, identity), `cobalt`, `graphite`; `verdigris` dropped (failed OKLab ΔE > 0.1 vs PROTECT cyan and GAIN green).
- RULING 2026-10-05 skin scope: `PaletteSkins` (`scripts/ui/kit/palette_skins.gd`) re-values chrome tokens only (TERMINAL_BG/_HOT/_EDGE/_TEXT, TEXT_HI/MID/LO, SELECTED, ON_SELECTED, CRT_GLASS_TOP/BOTTOM), procedural in OKLCH; no redrawn assets.
- RULING 2026-10-05 realisation: Palette consts are NOT changed; skins apply where chrome is drawn (`UiTheme.build` via `PaletteSkins.apply` before high contrast; `terminal_box`/`terminal_button_boxes` via `apply_box`; `HudSkin.draw_terminal_panel`, `CrtTerminalPanel`, `ZinePanel` terminal mode via `PaletteSkins.chrome()`). Non-chrome colours pass through unchanged. `active()` finds Settings by node path.
- RULING 2026-10-05 semantics: PROTECT / TURN Daemon / Uncommon / NET_CYAN stay #5CE1FF on every skin; HARM, GAIN, Heat bands, corp kits, FOCUS lime, stickers keep v2; every Palette.PAIRED_WITH greyscale cue stays.
- RULING 2026-10-05 settings: `Settings.palette_skin` (default `v2`), `PALETTE_SKINS`, `set_palette_skin` (unknown ids ignored), to_dict/from_dict (missing/unknown loads v2). Options > Display "Interface skin" row (`SettingsPanel.skin_option`, "SkinOption"); 4C's panel restyle must keep it. Skins are free (no Profile unlock); see OPEN.
- RULING 2026-10-05 contrast: every skin must pass 1A checks (TEXT_HI/TERMINAL_TEXT/edge >= 9:1 on glass; TEXT_MID/LO >= 4.5; hover glass >= 7; focus lime >= 7; selected-fill words >= 7; Heat/HARM/GAIN/WARN >= 4.5) and ΔE > 0.1 vs HARM, GAIN, Heat bands, FOCUS, stickers, corp colours, and between skins. Cobalt accent shift -0.07.
- OPEN skin unlock: skins free, no Profile unlock; question to designer (listed in the section's open question); default: free.
- DEFAULT views that set own `Palette.TEXT_*` keep v2 near-white text until their batch reads `PaletteSkins.chrome`.
- RULING 2026-10-05 12s-b sweep: 55 chrome lines in 30 files go through `PaletteSkins.chrome`/`track_box`; 146 direct uses in 46 files kept, each listed with a reason in `ALLOWED` of `tests/unit/test_art12b_skin_chrome.gd`. `chrome` maps exact v2 values only (corp accents unchanged; `CrtWindow` routes any accent). `KitState.edge_color` routed. Lint `test_no_new_direct_use_of_a_v2_chrome_colour_...` (tools/ lab scenes not scanned). New helpers `watch`, `bind`, `track_box`.
- Tests: `tests/unit/test_art12_skins.gd` (10), `test_art12b_skin_chrome.gd` (7).

### 2026-10-05 ART-0 audit fixes (DECISIONS.md:~2970)
- RULING 2026-10-05 E1 shakes: `Motion.shake` amplitude clamped via `VfxTier.clamp_shake(VfxTier.of(id), …)`; `Fx.shake_px` delegates. `heat_letters_shake` T3 (3 px), `precision_weak` 2 px (T2), `hit_shake` 2 px; `drop_reject` wiggle not a shake.
- RULING 2026-10-05 E2 motion kinds: `UiMotionEntryData.kind` {ONE_SHOT default, HOLD, LOOP}; `VfxTier.fits` holds only one-shots to `MAX_SECONDS`. HOLD: saved_stamp, toast, toast_note_hold, resolve_sequence, combat_end_hold, jack_arrival_wait, asset_drop_wait, ram_spend_float, ram_refill_float, forecast_change, ransom_countdown, ransom_wipe_hold. LOOP: drop_zone_pulse, pointer_orbit, ram_pending_blink, send_it_ready, route_target_pulse, tutorial_next_pulse, preview_chevron_chase, heat_glitch.
- RULING 2026-10-05 retiers: T1→T2 for wheel_spin, wheel_respin, inner_ring_turn, enemy_turn_spin, pointer_migrate, site_outline_draw, map_camera_ease, route_pulse, visited_dim, loot_fan, count_up, number_roll, drip_grow, drip_halo, minimap_pulse, flight_land_pulse; city_bake_fade T0; backdrop_won_lights T3; dossier_open T3; ransom_sticker_curl/_drop T4; buy_fly and loot_pick 0.7→0.6 s (ANIM-R5 floor 0.6).
- RULING 2026-10-05 E3 shaders: every `*.gdshader` outside addons includes rc_common; any with TIME freezes via `rc_time`/`rc_live`; rc_common include-guarded (`RC_COMMON_INCLUDED`). `glyph_batch.gd` uses `Palette.NO_TINT`.
- RULING 2026-10-05 B1 Heat glitch: `HeatGlitchLayer` + `shaders/heat_glitch.gdshader` between backdrop and UI root (protect mask met); off by default; exempt from VfxTier (`Settings.VFX_TIER_EXEMPT`); flash limiter removes luminance dip/roll brightening; option off = static corp edge tint at HUNTED+ only (HEAT_B if no corp); PURGE = HUNTED; **off under reduce effects** (supersedes §5.5 "tears at NOTICED"). Timing in `ui_motion.tres` `heat_glitch` and `CampaignConfigData.heat_glitch_period/_burst/_tears/_blocks`.
- RULING 2026-10-05 B2: quoted-key old raid word counts only in raid context; `"disabled":` plain in ui_theme.gd, type_chrome_sheet.gd, test_w9_accessibility_settings.gd.
- RULING 2026-10-05 B3: Hub Breach log line and hub line read LOCKDOWN (§3.3, App. C #11); BREACHED stays for home server falling (ruling 6.2). Netrun loot title "RACK BREACHED" unchanged.
- DEFAULT replay cap: `CampaignConfigData.max_replays` 50 (0 = no cap); `SaveService.write_replay` prunes oldest; `export_presets.cfg` excludes `saves/*`.
- RULING 2026-10-05 C1/D2: `Palette.HC_BG` (#000); colour lint counts `Color.WHITE/BLACK/TRANSPARENT`; use `NO_TINT`, `CLEAR`, `WHITE_HOT`, `HC_BG`.
- RULING 2026-10-05 D1: lint baseline has no slack (`test_the_baseline_has_no_slack`).
- SUPERSEDED Part 2 "enum keeps SHIELD / DEPLOY / MISS" and D11 "no band changes": struck. SANDBOX question resolved.
- RULING O2/O3: ci.yml fast-checks runs `python3 tools/test_run_tests.py`; `docs/timeline/.gdignore`.

### 2026-10-05 ART-5 5e city integration (DECISIONS.md:~3040)
- RULING 2026-10-05 reduce motion is not a pause: CityView3D keeps `ambient_scale` 0 under reduce motion; `host_pause_changed`/`host_paused()` (covered/unfocused). Street traffic keeps moving at `CityMotionConfigData.reduce_motion_street_rate` 0.4 (0..1, smoke-checked); supersedes 5c's "street traffic pauses" and answers 5c open question (2).
- RULING 2026-10-05 day look: `CityView3D.set_night_share(n, day)`; `CityViewMotion.day_look(mcfg)`; Grid stays night (no day/suspicion rule; orchestrator call (c)). Answers 5c question (3).
- RULING 2026-10-05 `GridCityLife.of(c, corp, cfg)` pure; DISPATCH fist when `corp.id == rebel_cell`; `NeonCity.set_city_life(d)` called by `hq_scene.show_grid` after `_mount_grid_camera`.
- RULING 2026-10-05 Site landmarks: `CityConfig.site_landmarks` (Solace `t1_c`, Halcyon `lose_the_case_file`, Orbital `o1_d`; Meridian and Cell none). OPEN: those landmark Site choices (question left under the section's open questions); default as listed.
- RULING 2026-10-05 crest reveal: `CityView3D.cell_reveal` property; `play_cell_reveal()` uses `cell_fist_reveal` (T0, 2.0 s); once per process; skipped under reduce effects/motion, headless, entry off.
- RULING 2026-10-05 x2 Site spread (call (a)): `CityConfig.site_spread` 2.0, boss end 3.5 lots from HQ, `site_aim_deg` Halcyon 255, Meridian 140, Rebel_Cell 270, Solace/Orbital 0; `site_mirror` none. Presentation only.
- RULING 2026-10-05 off-screen TARGET: `TargetEdgeMarker` (EDGE_MARGIN 46), click asks page to centre (`pan_requested` -> `CityGridControls.centre_on`).
- RULING 2026-10-05 markers stay on Grid overlay (call (b)); overlay snaps within 4 lots, projection keeps layout lot; a test pins the 4-lot bound.
- RULING 2026-10-05 roof props: from raid zoom; rules in CityConfig `roof_*`; `roof_props_below` 420; spots off turned/odd roofs left out (one deviation from concept); exported `assets/city/roof_props/roof_props.glb`.
- RULING 2026-10-05 `GRID_MIN_ZOOM` 0.3 -> 0.22 (hq_scene.gd).
- RULING 2026-10-05 fixes: Grid network decal cleared only by its own network (`_fed_network`); day look retuned to round 26 cool day, new `day_bloom` 0.2, `day_glow_threshold` 0.92.
- RULING test change: `test_raid_sway_covers_each_corporations_own_sites` now asks the border case (H21 #22).
- Tests: `test_art5_city_integration.gd`; `test_city_motion` updated for the 40 % rule.

### 2026-10-05 ART-5 5c city motion (DECISIONS.md:~3120)
- RULING 2026-10-05 seam: layers read the city only via `CityMotionSite` (`from_model`/`from_district`); groups traffic, sky, props, heat.
- DEFAULT config: `content/config/city_motion_config.tres` (`CityMotionConfigData`); every timing a T0 `ui_motion.tres` entry (sky_lane_cars, street_cars, holo_billboard, aviation_blink, searchlight_sweep, chopper_orbit, drone_orbit, police_strobe, alarm_beacon, heat_node_light, city_light_fade). NeonCity `city_traffic`/`beacon_blink` stay with the 2D city.
- RULING 2026-10-05 colours from derived streams `RngStreams.make_stream(city_seed, &"city_traffic")` and `&"city_ambient"`; never the campaign's streams.
- RULING 2026-10-05 car LOD: FAR/MEDIUM/CLOSE at ortho 400/150, hysteresis 0.04; management zooms drop only lane line to 35 %.
- RULING 2026-10-05 Heat lights: per band COOL none, NOTICED 3 alarm beacons, FLAGGED 2 slow searchlights + 2 alarms, HUNTED +13 strobes, 2 choppers, 6 drones; PURGE uses HUNTED (`CityHeatRig.look_of`); Suspicion adds 13 strobes, 3 choppers, 5 drones round the Cell home.
- SUPERSEDED reduce motion in 5c ("pauses every layer", bible 5.4 40 % not kept): by 5e street-rate ruling above.
- RULING 2026-10-05 netrun transit turns sky-lane cars off (bible 4.1); CLOSE tier only outside netrun band. OPEN: whether CLOSE tier should show in netrun (asked in section; default as built).
- Day/night: crossfade via `city_light_fade`; by day no rain/fog at raid zoom. Day-look call asked of 5a: answered by 5e.

### 2026-10-05 ART-5 5d Grid markers and key (DECISIONS.md:~3160)
- RULING 2026-10-05 markers v4: `SiteMarker.spec_for(campaign, corp, site, selectable)` pure; disc is a 1B `VinylSticker`; cleared = grey vinyl; DOWN = DISABLED state under white bolt; no new Palette tokens.
- RULING 2026-10-05 DOWN/TAKEN: `SiteMarker.draw_bolt` static (3A raid reuse, ruling 11); TAKEN = SEIZURE NOTICE slip, violet pips, orange ring while Reclaim launchable; links to TAKEN/DOWN de-powered; v4 only on the Grid.
- RULING 2026-10-05 hidden nodes: non-selectable regular Sites hidden; Exploit, Heat objective, boss, yours, cleared, TAKEN, selected, run-row-lit always show; key `HOVER: SHOW ALL` (pad `OPEN KEY: SHOW ALL`) reveals; PREV/NEXT SITE still reach hidden ones.
- RULING 2026-10-05 boss: red pencil TARGET (`GreasePencilMark` + `GreasePencilWord`), chip `CENTRAL SERVER // EXPLOITS n/3`.
- RULING 2026-10-05 Exploit tag on hover (bible §4.9): `DecryptedHoloPanel` with `CATEGORY // ITEM`.
- RULING 2026-10-05 fight won (D17): won Site lights windows Cell pink with some lime (`SiteMarker.won_light`, deterministic by Site id); `SiteWonLights` on the 3D city; DOWN node lights out.
- RULING 2026-10-05 key: v4 key (`MapLegend.use_site_markers`), meanings in `SiteMarker.MEANINGS`; every key entry differs in greyscale; "cleared" on other maps' key is `◇`. `why_not_runnable` explains a selected Site with no JACK IN.
- RULING 2026-10-05 projection: `GridMarkerProjection.from_view/from_model/from_camera`; `SiteMarkerLayer` serves views without NeonCity. Proposed: mount `SiteMarkerLayer` when 5a's Grid host lands.
- RULING test changes: pass21/pass22 city tests and `test_city_map_sweeps` skip hidden v4 Sites; boss and claimed nodes carry no pips.
- OPEN SHOW ALL setting: D13's "Always show all nodes" should drive the Grid too once it lands; designer; default: key only.
- OPEN VIRUS badge: bible says INFECT glyph, 1C's table maps `exploit_virus` to `status_corrupted`; default: the table.
- OPEN DOWN lights: won Site whose node is DOWN goes dark; default dark.

### 2026-10-05 ART-5 5a city model (DECISIONS.md:~3200)
- RULING 2026-10-05 `CitySpikeConfig` renamed `CityConfig`; values in `content/config/city_config.tres` (city_rect lots -80..85, chunk_lots 24, lod0_below 400, lod2_above 760, grid_ortho 440, etc.).
- RULING 2026-10-05 `CityModel` deterministic, seed 7, shared via `CityModel.shared`; 64 chunks, recorded in chunk order.
- RULING 2026-10-05 12 building families, per-chunk MultiMeshes; LOD by camera ortho with 6 % hysteresis (`CityLod.building_lod`), never by distance.
- RULING 2026-10-05 view bands (`CityLod.band`): GRID ≥ ortho ≈ 440, RAID down to 200, NETRUN below; zoom bands, no scene change.
- RULING 2026-10-05 materials via `CityMaterials`; `shaders/kit/toon_bands.gdshaderinc` shared; small change to 1B's `toon_ink.gdshader`.
- RULING 2026-10-05 seams: `CityView3D` layers ground, network, buildings, landmarks, props, traffic, sky, heat, fx; `add_to_layer(name,node,ground_pass)`; signals `camera_changed`, `band_changed`, `building_lod_changed`, `ambient_changed`; `ambient_scale` 0 when covered/unfocused/reduce effects/reduce motion; picking API; overlays read camera only via `CityIsoCamera`.
- RULING 2026-10-05 Grid runs on the 3D city (`WireframeBackground.city3d`); never bakes; raid/netrun/HQ-run keep 2D city until next step.
- RULING 2026-10-05 map links are the ground decal (`CityMapOverlay.on_ground_decal`), x-ray pass through buildings.
- RULING 2026-10-05 Grid holds GRID band (`band_lock`); proposed ×2 spread for all views at once, later realised in 5e (above).
- RULING 2026-10-05 player camera: log-linear wheel/+/- zoom about cursor, drag/WASD (physical keys, no new actions)/right stick pan; minimap (`CityMinimap`) hides at text scale ≥ 1.3 (`MapLegend.FOLD_SCALE`).
- RULING 2026-10-05 reuse art pass's assets (designer ruling): landmark glTFs from 5b placed with `LandmarkMaterials`; procedural buildings inside a landmark's ground box give way; missing file keeps stand-in.
- RULING test changes: `test_anim_r5_city` claim stamp and `test_anim_r2_city` 3D covers Grid at once.
- Perf budget: city within 8 ms; Deck unmeasured. Bug fixes in 66e4f1a (merge 66e4f1a or later).

### 2026-10-05 ART-5 5b landmarks (DECISIONS.md:~3280)
- RULING 2026-10-05 glTF is the only export (2× day/night layered sprites dropped); built with Blender 5.2 headless in `tools/art_pipeline/city/`; deterministic.
- RULING 2026-10-05 `rebel_cell.art_export/1` convention: no normals, COLOR_0, alpha in ROUGHNESS, materials named by role (`lm_*`), per-corp `manifest.json`.
- RULING 2026-10-05 origin: glTF x = lot x, z = lot y, 1 unit = 1 BU; HQ origin at plaza centre on 10×10 lot; Site at 6×6 block centre; district at palm.
- RULING 2026-10-05 animations via `gltf_anim_v1.py`: Meridian `loop` 3.0 s, Solace `chaser` 12×90 ms, Halcyon `eye_scan` 12×110 ms.
- RULING 2026-10-05 locked Site faces lot +y. Meridian's regular Site (depot) not exported.
- DEFAULT `LandmarkLook` in `landmark_look.tres` (`lit_emission` 0.25, `fist_gain` 1.8).
- Validator: `tools/landmark_asset_checks.gd`; test `test_art5_landmarks.gd`.

### 2026-10-05 ART-7 3B netrun presentation (DECISIONS.md:~3320)
- RULING 2026-10-05 route look: `RouteOverlay`; node ring states walked (lime, double ring), selectable (orange, thick), not yet (white dashed), cut off (`RING_CUT` grey dotted struck); transit cables one turn per link; projection seam `cable()`, `_axes()`, `icon_pos`, `_to_local`.
- RULING 2026-10-05 D13 hidden nodes: only walked, choices and TARGET drawn; legend hover shows all; `Settings.always_show_all_nodes` default off, Options > Display row "Always show all nodes on the netrun map"; pad reads "OPTIONS > DISPLAY: SHOW ALL NODES".
- RULING 2026-10-05 route key: `COLOR_KEYS` walked / next / later / cut.
- RULING 2026-10-05 calm Heat (D14): `HEAT_B` ring with red/blue lights; "HEAT: +N RESISTANCE" (ENEMY_RESISTANCE), "HEAT: SHOP STOCK -N"; from NOTICED two slow searchlights. Not drawn: "HEAT: +1 ELITE" (needs a rule).
- RULING 2026-10-05 panels: `OperativeDossier` (folds above 24 % width), `RouteNodePanel` (every shown node decrypted under GDD 4.2); no DECK/MENU stickers.
- RULING 2026-10-05 jack-in: `Fx.jack_in_link` (`JackSequence`) with `RunManager.jack_link(site)`; one press skips; reduce effects/motion/headless/no link falls back to old `jack_in`.
- RULING 2026-10-05 node backdrops: `assets/backdrops/netrun/<corp>_<kind>.jpg` via `NodeBackdrop`; fight keeps arena.
- DEFAULT motion ids in ui_motion.tres: route_node_reveal, route_heat_orbit, route_searchlight, jack_terminal_type, jack_link_rain, jack_crt_collapse, jack_wheel_slap, jack_wheel_spin, jack_lens.
- Big text: node panel at most 1.3× and only when ROUTE column has room.

### 2026-10-05 ART-9 4A shop, rewards, events (DECISIONS.md:~3360)
- RULING 2026-10-05 presentation only: prices, removal, rewards, event rules unchanged.
- RULING 2026-10-05 facade state per visit by hash (night 2/4, rain 1, day 1); no time of day in rules. OPEN: question below in section (default: hash).
- RULING 2026-10-05 sign: shop name never translated (§1.2); `MainframeSign` layered; takeover once per visit by hash (never RNG, `hash()` stutters); ambient, off under reduce effects/headless.
- RULING 2026-10-05 reuse rule (designer 2026-10-05): art is the concept's, baked via `tools/art_bake/*`; drawn procedurally only words/numbers, state marks, padlock+strike on unaffordable tag, CAM feed, peel flap, rain.
- RULING 2026-10-05 pricing: current flat rule (no top-3 discount, G14); price is kraft tag; card tag hangs below card (`BuyButton.TAG_BELOW`); drawn objects stop at ×1.3 (`ShopItem.OBJECT_MAX_SCALE`).
- RULING 2026-10-05 slice stock wheel (option B): `SliceStockWheel`, 60 % grey dim, wedge opens UPGRADE viewer; pencil "TOP n ONLY".
- RULING 2026-10-05 removal = recycle bin, cards only; bin never takes a slice (not a rule). Crumple/fizz/lid-slam not built (proposed slice).
- RULING 2026-10-05 LEAVE is holographic VinylSticker over "THE MAINFRAME" plate. Loot sheet (Reward A) `LootSheet`; entrance stays `loot_fan`.
- RULING 2026-10-05 events: CRT terminal + `CamFeed`; corp speaker = `CorpMemo`; DISPATCH "VOICE ONLY // NO FEED"; outcome chips with up/down mark (Heat gained is a cost); stamp reads CHOSEN; "PLAY IT SAFE??" only when a choice changes nothing; from text 1.6 CAM feed/speaker/"> CHOOSE" step aside.
- DEFAULT constants: `SHOP_SPILL_GAIN` 0.6, reach 260 px, `SHOP_WALLET_MAX_SCALE` 1.6, `SHOP_INFO_WIDE_SCALE` 0.92, `SHOP_INFO_IDLE_PAD`.
- RULING 2026-10-05 motion: new entries mainframe_takeover, mainframe_rain, shop_wheel_spin (T3, 1.2 s), loot_peel, event_cam_noise (takeover/rain/CAM T0 ambient, rain and CAM loops).
- RULING 2026-10-05 one CrtWindow: 4C's `kit/chrome/crt_window.gd` wins; 4A's removed; added `with_kind(kind, corp)` and `kind_for(colour)`.
- RULING test ports: listed tests ported to the v2 look, none dropped.
- Files outside area edited: palette.gd, page_transition.gd, outcome_row.gd, buy_button.gd.
