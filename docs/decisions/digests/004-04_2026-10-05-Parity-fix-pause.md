## Implementation decisions (slice from DECISIONS.md:2207)

### Parity fix — pause menu as stickers (2026-10-05)
- RULING 2026-10-05 pause layout: `Columns`; LEFT = RESUME, OPTIONS, CODEX; RIGHT = ABANDON CAMPAIGN, QUIT TO MAIN MENU, QUIT TO DESKTOP; code field below. Focus order left top-down, right top-down, code; Left/Right cross to the same row. Supersedes the icon rows of the earlier pause parity fix and the options A/B/C.
- RULING 2026-10-05 "Save & quit to title" is now "Quit to Main Menu" (saves, returns to the title; same code path, no migration).
- RULING 2026-10-05 abandon slot: top right is ABANDON CAMPAIGN at HQ, ABANDON RUN in a run (same dialogs and hold-to-confirm BURN IT as ExitDialogs, GDD 4.5); absent with no campaign, the quits move up.
- RULING 2026-10-05 stickers: every row is `VinylSticker` via `HoloSticker.word`, always in its role colour: RESUME `Fill.PINK`, ABANDON `Fill.RED`, OPTIONS `Fill.YELLOW`, CODEX and QUIT TO MAIN MENU `Fill.WHITE`, QUIT TO DESKTOP `Fill.HOLO`. Selection = the kit's HOVER state looping while focused (`ambient_sweep`), no lime bracket or halo.
- SUPERSEDED pause focus sweep (white gloss on non-HOLO fills): closed 2026-10-05 by the designer, rainbow gloss sweep plus curl on every sticker's focus ("Parity fix — sticker edge and sticker focus").
- DEFAULT pause sizes: lettering 34 px (Resume) / 22 px (rows); stickers scale with text up to `STICKER_SCALE_MAX` 1.5x; the menu is 760 px wide.
- RULING 2026-10-05 pause notes (`PencilWords`): "Down with the Oligarchy!" under RESUME, "No Going Back" under abandon, "Come Back Soon" under QUIT TO DESKTOP; always below their sticker; all dropped together when they don't fit (they go at text 2.0, stay at 1.6).
- RULING 2026-10-05 `[Esc]` hint: pink mono label under RESUME (`Settings.hint`, pad button when a pad is used); `resume_button` is a `HoloSticker` with no `text`; `resume_hint.text` holds the hint.
- RULING 2026-10-05 `MenuMotion` no longer attaches to the pause menu; the `menu_*` motion entries stay for the title.
- DEFAULT pause strings (once): `Quit to Main Menu`, `Down with the Oligarchy!`, `No Going Back`, `Come Back Soon`.

### Parity fix — pause menu (designer decisions, 2026-10-05)
- RULING 2026-10-05 PAUSE-01/03: pause `Backdrop` is a `GlassScrim` (blur `Palette.SCRIM_BLUR_PX`, dim `Palette.SCRIM`, opaque in high contrast). No PAUSED sticker; the terminal header keeps its `PAUSED` title. The raid playout plays on under the pause menu.
- RULING 2026-10-05 PAUSE-04: abandon and quit stay different dialogs; `confirm_dialog.gd` untouched.
- SUPERSEDED PAUSE-02 rows (Resume VerbSticker, MenuItem lines with icons): replaced by the sticker layout above. Still in force: `CodeField` (`scripts/ui/kit/code_field.gd`) keeps the name `SeedLine`, copy icon `StatIcon.COPY`; `PauseMenu.code_line()` stays for the HQ radio tooltip.
- DEFAULT test seam: `CodeField.clipboard_writer` (Callable, unset in game) replaces `DisplayServer.clipboard_set`.
- DEFAULT strings: `Copy the campaign code`, `Campaign code (share it: it starts this campaign)`, `Copy`.

### TITLE-01 title backdrop (2026-10-05)
- RULING 2026-10-05 the title follows concept round 33; its backdrop is the real 3D city, `BlurredCityBackdrop` (`CityView3D` held at the GRID band, `CityViewMotion`, `city_tilt_shift.gdshader`).
- DEFAULT the concept's numbers live in `CityBackdropLook` (`scripts/city3d/city_backdrop_look.gd`, not under scripts/data); the title's is `content/config/title_city_backdrop.tres`: `city_tiers` [false, true, true], ortho 300 BU, HQ anchor (0.86, 0.64), blur 5 px at 1080, darkening 0.62, vignette 0.35, gain 0.86.
- RULING 2026-10-05 which HQ: the last-played campaign's corp (`corp_of_slot(continue_slot)`, else RunManager.latest_slot), else Halcyon (`default_corp`); the Cell or a corp with no HQ falls back to Halcyon.
- RULING 2026-10-05 fallback: `CyberdeckBackground.use_blurred_city` applies only where the tier takes the 3D city and a renderer exists; tier 0, headless and the title's 2D design-review args keep 2D NeonCity and CITY_DIM. Only the title calls it.
- RULING 2026-10-05 motion: arrival uses `city_bake_fade` (MotionSkip passive); reduce effects/motion = a still frame.
- DEFAULT budget: city GPU under the 8 ms budget (measured about 2.3 ms).

### TITLE-01b grade and LOOT-04 (2026-10-05)
- RULING 2026-10-05 (1) keep the last-played corp's HQ.
- RULING 2026-10-05 (2) the backdrop has its own grade in `CityBackdropLook` (`grade_saturation`, `grade_gain`, `grade_lift`, `haze_out_of_focus`); the shared city grade and the Grid are never touched (tested). Values at the time: saturation 1.2, gain 0.765, lift (0.04, 0.03, 0), haze 3.0.
- RULING 2026-10-05 (3) LOOT-04: loot and event overlays use the blurred city via `WireframeBackground.show_blurred_city(on, look, corp)`, per page through `BLURRED_CITY_SCREENS` in `netrun_scene.gd`; look `content/config/overlay_city_backdrop.tres`. Tier 0 and headless keep the 2D net city.
- RULING 2026-10-05 the shop keeps its MainframeFacade with no city behind it (designer round 3, "a waste of cycles"; closed).
- RULING 2026-10-05 other pages (HQ, combat, labs, other netrun pages) unchanged; only the title calls `use_blurred_city`, only netrun_scene calls `show_blurred_city`.

### TITLE-01c lively city (2026-10-05)
- RULING 2026-10-05 designer round 3: less haze (keep the pink grade), lively traffic, less blur and brighter on loot/event.
- DEFAULT `CityBackdropLook.traffic_density` 2.0, `traffic_light_scale` 1.6: `BlurredCityBackdrop.motion_config` hands a copy of the shipped CityMotionConfigData to its CityViewMotion; the loaded resource and the Grid/raid/netrun motion stay unchanged.
- RULING 2026-10-05 kept-light bokeh in the tilt-shift shader (`light_threshold` 0.55, `light_keep` 0.8); included in `shown` / `worst_behind`.
- DEFAULT `haze_out_of_focus` 3.0 -> 1.8. Loot/event (`overlay_city_backdrop.tres`): blur 5 -> 3 px, gain 0.62 -> 0.74; event terminal words keep 4.5:1.

### TITLE-01d no yellow cast (2026-10-05)
- RULING 2026-10-05 designer round 4: the title is unchanged ("looking really good"); loot page and HQ had a yellowish hue and are too zoomed in.
- DEFAULT `overlay_city_backdrop.tres` has its own violet grade: gain (0.80, 0.70, 0.86), lift (0.03, 0, 0.035); the title's look is untouched. Loot/event ortho 300 -> 440 BU.
- DEFAULT `CyberdeckBackground.NIGHT_TINT` (0.94, 0.78, 1.0) as the 2D city's `modulate` fixes the HQ cast. Drop it with the 2D HQ city (HQ-BUILD); HQ framing not changed.
- OPEN HQ framing and colour on the Grid / HQ-run / raid pages: the designer must rule; unchanged meanwhile. The colour-space probe showed no loss.
- RULING 2026-10-05 `test_anim_r5_city`: the shop step checks that the facade shows and the city is hidden.

### ART-3 6w raid on the city (2026-10-05)
- RULING 2026-10-05 raid setup, playout and report (`hq_scene.RAID_CITY_PAGES`) use `WireframeBackground.use_city3d(on, band)` at `CityLod.Band.RAID`; the Grid keeps GRID. Picking, the drag model and the raid verdict are unchanged.
- RULING 2026-10-05 `RaidZoomFit` (pure): frames the network plus `raid_fit_margin` (40 BU). Call: `raid_fit_max` 380 -> 640. `playout_zoom` = `raid_fit_min` 220.
- RULING 2026-10-05 uplink pads (`RaidUplinkPads.of`, `assets/raid/uplink/uplink_pads.glb`, built from the concept's own lines): pad half-size `uplink_pad_share` 0.32 of the roof's shorter side; roofs under `uplink_min_top` 3 BU carry none; the riser is on the corner nearest the street door. Calls: a tapered roof keeps its shrunk pad; the socket keeps floating over its roof; a node's pad stays through the playout.
- RULING 2026-10-05 `NeonCity.view_cover` grows the 3D viewport to cover a held frame, at most `COVER_MAX` 3.
- RULING 2026-10-05 raid setup fixes: `Fx.avoid_rects` keeps SAVED off `RaidSpeedStrip`; `hq_scene._fit_card_row` shares one row down to `CARD_ROW_MIN_SHARE` 0.8.

### ART-6 3A raid presentation (2026-10-05)
- RULING 2026-10-05 panels by fiction: RAID INCOMING = `RaidPaper` over `CorpPaperPanel`; YOUR NETWORK = `RaidTerminal` over `CrtTerminalPanel` (`RaidChip`: HOLDS green, DOWN amber, TAKEN red, always the word); THREAT INTEL = `RaidHolo`; START DEFENSE = `RaidSticker`; re-skin per raiding corp (`RaidSkin`). THREAT INTEL lists at most 3 entry routes at text 1.0.
- RULING 2026-10-05 sockets (`RaidSocket`): fill drains north to south; DOWN = white bolt over a greyed socket (ruling 11); TAKEN = burnt socket with embers; the projected outcome is a dashed ring. Sockets drain live from `RaidFxLayer.socket_state`.
- RULING 2026-10-05 grease pencil (`RaidPencilPool`, CanvasLayer 95): threat routes are the projection's own routes (preview equals result), snapped to streets. Marks write about 0.4 s, hold 1.5 s, wipe about 0.4 s in real time, never shortened at 2x/4x (`raid_mark_*`); the hold stays under reduce effects. BREACHED is one slow pass (`raid_breached_write`). All marks are anchored through `RaidMapAnchor`.
- RULING 2026-10-05 card drag (`RaidDragPencil`): the DropLayer still does every drop; IF PLACED comes from the rules on a campaign copy.
- OPEN 3A "remove = click the node": not built (a click still picks the target; Withdraw button or drag to the loadout remove). It is a behaviour change; the designer must rule. Question "below" was not in this slice.
- RULING 2026-10-05 threats (`RaidVehicle`, icons v4): FAST moves 2 links a step, SPECIAL freezes/alters links, else HEAVY; FLYING has no rule and stays in docs/art_reference; `threat_enters` carries `integrity` (a view field).
- RULING 2026-10-05 the raid report is the raiding corp's AFTER-ACTION REPORT; CELL HOLDS is slapped on whenever the Cell survived (GDD 7.2); it can show beside HOME -5. BACK TO THE GRID is a sticker.
- RULING 2026-10-05 designer correction "never redraw concept art": all raid art is baked from art-concepts-r43 generators (see the source table in DECISIONS). Supersedes "node glyphs are vector stand-ins" and "R3 beacons not done". Compiler Rack uses round 17 `picto_ram`, scheduled for the post-M14 glyph slice. New token `Palette.RAID_SLOW_BLUE`.
- RULING 2026-10-05 M14 fixes: the fallen home server reads **BREACHED** (`hq_scene.shown_outcome`, not "2 → 0 HOLDS"); START and the Speed/Skip strip are pinned in `RaidFoot` outside the scroll; `ScrollHint.in_outer_views` hides clipped tags; INCOMING clears an entry letter (`RaidFxLayer.mark_centres`); the SAVED stamp is 20 px with keyline (`SAVED_OUTLINE`, `SAVED_KEYLINE`).
- DEFAULT motion entries (REQUIRED_IDS): `raid_mark_write/_hold/_wipe`, `raid_breached_write`, `raid_bits_burst`, `raid_slow_field`, `raid_ice_grow`, `raid_repair_rise`, `raid_route_write/_wipe`, `raid_dock_circle`, `raid_drag_arrow`; end state under reduce effects/headless; MotionSkip passive.

### ART-8 8w HQ runs on the city (2026-10-05)
- RULING 2026-10-05 DISPATCH's HQ run plays in the round 43 Tokyo canyon (`build_dispatch_canyon.py`, round 34 `hq34.py` vendored); it replaces 8p's rebel_base compound for rebel_cell. Canyon camera yaw 180 / pitch 40; the corps keep azimuth 55. Rows at 10/28/46/64/80/100 BU; a rooftop over a gap seeks a roof only toward the camera end.
- RULING 2026-10-05 HQ-run page (`HqRunView`) mounts when `run.kind == "boss"`; Central Server = rack sticker with red pencil **TARGET** and the yellow chip `CENTRAL SERVER // <Site name>`.
- RULING 2026-10-05 `CentralServerGate` opens only via UI press paths (`_request_node`); `enter_node` is unchanged. `NetrunSession.breach_preview()` draws from a COPY of the combat stream (preview equals real start). Motion `gate_keycard_stagger`, `gate_socket_ring`, `gate_breach_ready`.
- RULING 2026-10-05 keycards and the BREACH vinyl come from round 38 `exploits.py` (`assets/hq_run/`), baked English words kept (orchestrator).
- OPEN keycards' baked English words and translation (the "translation question below" was not in this slice); the orchestrator kept English meanwhile.
- RULING 2026-10-05 the Cell's Central Server is **DISPATCH CORE** (Site display name "DISPATCH" -> "DISPATCH CORE").
- DEFAULT D17 on the city: `CityConfig.backdrop_city_tiers` default [false, true, true]; tier 0 uses the stills. Boss ortho 140; the Cell's boss uses the canyon at 0.7x; regular fights ortho 90. Budget 8 ms (measured under it).

### ART-10 4C menus, title, settings, HQ (2026-10-05)
- RULING 2026-10-05 designer correction: menu art is baked by running round 33 scripts unchanged (`tools/art/bake_menus_r33.py`), never redrawn. The title backdrop is the live city, dimmed (later superseded by TITLE-01 above).
- RULING 2026-10-05 title option A (D10, confirmed): REBEL_CELL neon sign; 1. BREACH (pink, default focus) = Continue; 2. SIMULATE = Tutorial; 3. OVERTHROW = New campaign. DISABLE stays the Cell's motto. With no saved campaign BREACH is grey and disabled and SIMULATE takes focus; OVERTHROW starts in the first empty slot (the slots page when all three are full). The chips do the same action as their stickers.
- RULING 2026-10-05 big text (≥ 1.6): MORE heads the right column, chips drop their second line, motto and PROFILE give way.
- RULING 2026-10-05 abandon dialog (`AbandonDialog`): there is no in-run abandon on main (GDD has no voluntary abandon), so it serves the title's delete slot (DELETE SLOT, verb DELETE); `dialog_burn_it` is baked for a future abandon-run rule. Quit confirms stay 2D ConfirmDialog. (Later pause rulings add abandon in the pause menu per ExitDialogs.)
- OPEN pad hold-A 0.8 s on the verb (bible §4.13 proposal): not built; designer to rule.
- RULING 2026-10-05 options: below text 1.5, and never in the pause menu (`compact`), one column. The reference's RESET TO DEFAULTS is not built (no such rule). D13 "Always show all nodes" row is not on main (3B); it takes a CrtSwitch row when it lands.
- RULING 2026-10-05 HQ (G13 not ruled: every action kept). Not done: the crew dossier on `CorpPaperPanel` and JACK IN as a vinyl sticker (proposed slices).
- OPEN Heat count-up vs banner (P3, ART-5 poster timing) and raid setup SAVED stamp: reported, not fixed here.
- DEFAULT motion: `title_glitch_burst`, `title_sign_flicker`, `on_air_ticker` (T0). Tokens: STICKER_BLUE/_LOW, NEON_TUBE/_CORE, BOARD_*.

### ART-7 7w netrun on the city (2026-10-05)
- RULING 2026-10-05 `RouteCableRouter` (pure A*, 45°/90° turns); its costs are constants, not config (they shape a drawing only).
- RULING 2026-10-05 the route page is on CityView3D at the NETRUN band, see-through at any zoom; GRID VIEW at GRID. Other netrun pages stay on the 2D city until their slices.
- DEFAULT `car_close_below` ortho 150: CLOSE cars appear below it; MEDIUM at the fitted zoom.
- RULING 2026-10-05 the route bake and `ROUTE_KEEP` are removed; `_prebake_backdrops` bakes later pages' frames behind the 3D route via `under_3d`.
- RULING 2026-10-05 dropped test: `test_anim_r6_netrun.gd::test_the_route_bake_is_let_go_at_the_run_end`.

### Asset parity: combat and foundations (M14)
- RULING 2026-10-05 "REUSE ART-PASS ASSETS": images come from the art pass's own generators (tag art-concepts-r43); inventory in `docs/handoff/m14_asset_parity/combat.md`.
- RULING 2026-10-05 landing word WEAK is the word "WEAK" in amber (was x0.5, which stays on the rail). New strings: WEAK, WHEEL, HACK, SYSTEM (`CardFace.KIND_WORDS`).
- OPEN `test_every_script_that_animates_registers_or_says_why_not` fails for `campaign_end/rubber_stamp.gd` and `kit/route_overlay.gd` (ART-11 / ART-5 5d files); a later entry notes `NOT_SKIPPABLE` registration kept.

### Asset parity: city and screens
- RULING 2026-10-05 art-pass assets are never redrawn (inventory `docs/handoff/m14_asset_parity/city_screens.md`).
- RULING 2026-10-05 the Exploit marker is the v4 single gold key (MEANINGS word "Gold key"); corp seals use the round 6 `EM_` emblems (orchestrator).
- DEFAULT `CityMotionMeshes.car` reads `flying_car_tris.json`; `chopper_color` / `drone_color` stay the body tone.
- RULING 2026-10-05 dropped test assertion: `GlyphIcon` sub-badge on Site `type_glyph()`.
- OPEN proposed slice (not built): host the 2A WheelView as a ViewportTexture in `JackSequence._draw_wheel` with the combat parity sweep.
