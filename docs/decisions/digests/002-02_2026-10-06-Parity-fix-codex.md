## Implementation decisions (slice from DECISIONS.md:804)

### 2026-10-06 Parity fix, codex / stats / options
- RULING 2026-10-05 menus: Codex and Stats take the M13 build's structure in the v2 kit (CODEX-01, STATS-01); Options match round 31's concept (OPT-01..03). Kept: STORY heading the Codex (Q8); Codex / Options in the pause menu only.
- RULING 2026-10-06 CODEX-01: Codex is `CodexBook`: terminal tab plates over one paper page, entries in two columns; glyphs reuse the 1C atlas, `CorpSeal.draw_crest` and StatIcon, nothing redrawn; `Codex.entries` names each entry's glyph source; an entry never says its title twice (`CodexBook.body_text`).
- RULING 2026-10-06 CODEX pad: tabs are one row of focus stops, LB/RB switch tabs (wrapping); the page is ONE focus stop (up/down scroll a quarter view, move on at the ends); the page scrolls without snapping to entries.
- RULING 2026-10-06 CODEX big text (from 1.6): tabs become one sideways-scrolling row; the page drops caption and heading.
- RULING 2026-10-06 Pause menu Codex: the same book, centred over the scrim in the sticker menu's place.
- RULING 2026-10-06 STATS-01: one scrolling sheet: twelve `StatTile`s (six a row at 1280), best ICE per corporation, ACHIEVEMENTS as round badges (earned badge drawn in code, not a VinylSticker), RUN HISTORY as `RunReceipt` paper cards ("NO RUNS YET" when empty). PROFILE strip and records paragraph are gone. Tiles, badges and cards are focus stops (`link_grid`). Outcome words are new keys (Completed / Died / Aborted / Unfinished).
- RULING 2026-10-06 OPT-01: Options is a centred terminal with an OPTIONS sticker, two columns at 980 px (right 1.1 of left); from the pause menu it opens in the sticker menu's place (`PauseMenu.sub_rect`) and closing shows the menu again.
- SUPERSEDED pause test "one column inside the menu": by the centred two-column Options (OPT-01).
- RULING 2026-10-06 OPT-01 RESET TO DEFAULTS (pad Y): resets the open tab to the Settings script's defaults via the same setters (Controls tab also resets key binds); Close stays beside it.
- RULING 2026-10-06 OPT-01 big text: one column, 620 x text scale up to the room; from 1.5 the LB/RB hint, pad prompts and "saved to profile" give up their rows (keys still work). Section view fits over 3 frames, MORE BELOW counted.
- RULING 2026-10-06 OPT-02: row words are the concept's (REDUCE EFFECTS, FLASH LIMITER, HIGH CONTRAST, SUBTITLES, ASSIST MODE numbers stay the config's, HEAT GLITCH "Off by default"); the LIMITED chip shows with the glitch on under the flash limiter.
- RULING 2026-10-06 OPT-03: right column kept; slider ticks 1.0 / 1.5 / 2.0; skin picker (ART-12) stays on Display.
- RULING 2026-10-06 StatIcon: LOCK, CLOSE, CHECK, PLUS, INFO added; CLOSE in HARM, LOCK in TEXT_MID.
- RULING 2026-10-06 Tests: new `tests/unit/test_parity_menus.gd`; changed test_art10_menus, test_title_and_menus, test_anim_r5_city::test_the_pause_menu_is_as_tall_as_what_it_shows. None dropped.

### 2026-10-05 Parity fix, HQ runs and gate
- RULING 2026-10-05 scope: HQ run and Central Server gate match the concepts, with no mechanic the rules lack. HQRUN-01, 03..08, GATE-01..03 done.
- OPEN HQRUN-02: held; the question is not in this slice (designer must answer; no default recorded here).
- RULING 2026-10-05 HQRUN-01: title sticker "<CORPORATION>: HQ RUN" (first word of display name); the concept's names (CLIMB THE HELIX etc.) are G12 and not used. State key strip has no "danger" (G12). `> HQ MECHANIC` terminal presents only existing rules (breach with N = `min_exploits_for_breach`, or the layers with a `STEP walked/layers` chip). Chrome takes no focus or clicks and steps aside while the gate is open.
- RULING 2026-10-05 HQRUN-03/04: selectable nodes get a name tab (route key's kind word, led by the choice number when there is more than one); the Central Server keeps its chip; cut-off nodes sit on a pale disc; ring styles unchanged.
- DEFAULT HQ run page framing: CityConfig "HQ run page" (`hq_run_ortho_scale_by_corp`, `hq_run_target_by_corp`, `hq_run_pitch_by_corp`, `hq_run_yaw_by_corp`, `hq_run_fov_by_corp`, `hq_run_fit_pans`, `hq_run_fit_step`, `hq_run_fit_share_perspective` 1.25, `hq_run_fit_slack_px`); FIT_MAX_SHARE 2.0 const. `HqCompoundStage.page_camera` for the page, the combat backdrop keeps `camera`.
- RULING 2026-10-05 HQRUN-08: the REBEL_CELL canyon page is a perspective view (fov 36.9, pitch 19, round 34 CAM27); `CityIsoCamera.fov_deg` 0 = iso, other views unchanged.
- RULING 2026-10-05 GATE-01: panel follows the concept (corp-colour edge once the breach is ready, sockets 128 x 175, BREACH under the panel with Back beside it); width 427 x text scale (max 1.5x).
- RULING 2026-10-05 GATE-02: one label: gate joins `CentralServerGate.GROUP` and tells `HqRunView.GROUP` pages (`set_gate_open`); page hides chip and chrome until the last gate leaves. Exploit-effect card and cut slices on the preview are G6: not built. Preview == result unchanged (`breach_preview`).
- RULING 2026-10-05 GATE-03: shared GlassScrim plus a darker left side and a dark disc under the wheel.
- RULING 2026-10-05 Kept: motion entries gate_keycard_stagger / gate_socket_ring / gate_breach_ready / sticker_slap, MotionSkip, reduce effects = end state, pad focus on BREACH.
- DEFAULT perf budget: 8 ms (measured within budget).
- OPEN Relay netrun_scene.gd (S-NETRUN): HUD band still reads NETRUN // ROUTE over the page's title sticker; `hud.set_heat`/`hud.set_screen("", "")` on a boss run's map would leave one title. Not done; the S-NETRUN owner decides.
- Not built (G12): Meridian call-outs, Orbital loop route and MISSILE BAY, Halcyon switchback and eye, HEIGHT/LAP chips.

### 2026-10-05 HQ redesign, direction B (designer rulings, binding)
- RULING 2026-10-05 Direction B: HQ is the live 3D city at the RAID band with a hand of cards behind tabs CREW / MARKET / DEFENCE, the selected thing's card at the right, one pink verb sticker slot bottom right. Grid page folds into it.
- RULING 2026-10-05 Q1: HEAT gauge takes the top bar's first slot on every screen; WANTED poster and CELL STATUS badges go, motion entries move onto the tag.
- RULING 2026-10-05 Q2: in a run the tag opens the Heat terminal read-only.
- RULING 2026-10-05 Q3: JACK IN with a raid pending plays the raid as a mid-run interlude; system word says `raid incoming mid-run`.
- RULING 2026-10-05 Q4: HQ wheel may zoom out past `raid_fit_max` into the GRID band.
- RULING 2026-10-05 Q5: fit frames the network and launchable Sites up to the clamp; Central Server by edge arrow when outside.
- RULING 2026-10-05 Q6: no title sticker; `hq_scene` keeps its name.
- RULING 2026-10-05 Q7: pirate radio is one ON AIR ticker line (`OnAirTicker`).
- RULING 2026-10-05 Q8: story is a STORY section in the Codex plus a corp-news toast on a revealed beat.
- RULING 2026-10-05 Q9: no Save button (autosave; pause menu keeps Save & quit).
- RULING 2026-10-05 Q10: route dossier's Heat stamp goes.
- RULING 2026-10-05 Q11 (updated, supersedes first default): CLAIM, REPAIR, UPGRADE, PATCH are ALL stickers in the verb slot, price in a gold tag under, never on it.
- RULING 2026-10-05 Q12: crew cards in roster order, flatlined last, ineligible greyed with the rule's reason.
- RULING 2026-10-05 Q13: Rank 3 inner-ring swaps move to the Loadout's SPINNER tab.
- RULING 2026-10-05 JACK IN is the normal netrun start on this same city; Codex / Options / Save live in the pause menu only.
- RULING 2026-10-05 HQ-B (a): `HeatGauge` extends HeatPoster (motion unchanged); look is `HeatGaugeLook` in `content/config/heat_gauge_look.tres` (240 x 44 at 1.0, grows up to x1.3). `HudBar.set_heat(value, max, marks, interactive, tip)`; other screens call it, read-only terminal is `HeatTerminal.new(campaign, config, true)`. SCRUB HEAT numbers are the rules' own `scaled_delta` / `heat_purchase_price` (preview == purchase).
- RULING 2026-10-05 HQ-B (a) input: new runtime action `open_heat` (H, not rebindable yet); pad View opens it at the HQ. In a run View stays rewind.
- OPEN Pad route for the Heat terminal in a run: View stays rewind, so the run's agent must pick another pad route; no default.
- RULING 2026-10-05 HQ-B (a) call: CELL STATUS's SITES bump (`sticky_bump`) plays on the HEAT tag.
- RULING 2026-10-05 HQ-B (b): `HqPage` layout via `HqLayout`; fit `hq_fit_lots` with `RaidZoomFit`, up to `HQ_FIT_PASSES` 4; camera kept across rebuilds; `HqMapCursor` is the pad's place on the map; `show_grid` opens the HQ.
- DEFAULT `HQ_FIT_SHARE` 0.65 (was 0.75, designer "err on showing more city" then "frame wider than the default"); nothing tints the city.
- RULING 2026-10-05 Hand: tabs `Tab_CREW / Tab_MARKET / Tab_DEFENCE`, LB/RB or Q/E switch; DEFENCE pink while a raid waits. Boosts as BLUE vinyl stickers over gold `PriceTag`s (changing value never on a sticker, bible 1.2). Station/recall/patch via `StationHere`, `RecallHere`, `Recall_<id>`, `PatchHome`.
- RULING 2026-10-05 JACK IN is the verb slot's pink `Launch` VinylSticker; words drawn in-engine (translatable), not baked PNGs.
- RULING 2026-10-05 `MapLegend.always_fold`: HQ's key is the one-line MAP KEY at every text size.
- DEFAULT Big text: from 1.3 tabs show only their word; hand scrolls sideways; JACK IN system word one clipped line (full in tooltip).
- RULING 2026-10-05 HQ-B (c): `show_raid` and `show_hq` build one page (`HQ_PAGES` = hq, raid); raid setup is the DEFENCE tab (`panel_name` "raid"); B or the CREW tab go back. Defence hand is `AssetCard`s (`Asset_<id>`); card column THREAT INTEL and YOUR NETWORK (`NodeOrders`); START DEFENSE (`RunRaid`) over Speed / Skip. Click on a Cell node makes it the target (a corporate Site is none).
- RULING 2026-10-05 Kept from S-OVERLAPS: RAID-02 plate, RAID-08 peel (`_start_was`), GRID-12 fit-then-pan (`grid_city_pan`).
- RULING 2026-10-05 Map mode: `hq_map_mode(on)` is the one call point; HQ draws no dimming of its own.
- RULING 2026-10-05 HQ-B (d): `site_verb(site, runnable)` picks the one verb from the rules; the press makes the same rule call as the old buttons (`press_verb`). Claim pick (`claim_pick`) sets the sticker price; `PatrolHere` for a Site whose verb is not JACK IN; `IfCleared` on runnable Sites; nothing to do leaves the slot empty with a WHY NOT note.
- RULING 2026-10-05 HQ-B (e): JACK IN calls `launch` -> `RunManager.go_to_netrun(start, site)` -> `Fx.jack_in_link` with `RunManager.jack_link(site)` on this city; resume uses `resume_run` / `resume_site`. No HQ jack, no deck-monitor CRT push.
- RULING 2026-10-05 HQ-B (f): `tell_new_beats` toast `CORP NEWS // <title>...` when the HQ shows; nothing told the first time a campaign's HQ shows; `_beats_seen` is view memory, never game state.
- RULING 2026-10-05 HQ-B (g): dead Grid/HQ code removed from `hq_scene.gd`; kept `show_grid`, `raid_min_zoom`, `grid_city_pan`; the start page's Codex line opens the pause-menu Codex (`open_codex`).
- RULING 2026-10-05 S-MAPVIEW hookups: `raid_graph` and setup's `hq_graph(projection)` draw major nodes only (`RaidMapNodes.major_ids` / `shown_routes`); the CREW / MARKET / DEFENCE-armory map keeps every Site (pickable).
- RULING 2026-10-05 Motion entries re-pointed, none dropped: hq_crt_hum, radio_type, jack_ring_breathe, polaroid_tilt, minimap_pulse, select_ring_ease, drag-and-drop motions, sticky_bump on the Heat gauge.
- RULING 2026-10-05 S-RAID items (round 40): RAID-01 defence cards in the hand's row (no steps panel); RAID-05 NO RAID SETUP title sticker; RAID-06 YOUR NETWORK top left, START DEFENSE bottom right, `IfPlaced` terminal (`if_placed_lines`, preview == result); RAID-09 Continue keeps its room unseen while the raid plays; RAID-12 no result disc, CELL HOLDS slaps at `HOLDS_AT`.
- DEFAULT Setup map: `HQ_SETUP_FIT_SHARE` 0.9, `_hq_fit_passes` = 1, may zoom past the raid range (stays RAID band), skips GRID-12 pan, `CARD_COLUMN` x `object_scale`, refit within `HQ_SETTLE_FRAMES` (`HQ_REFIT_PX`).
- OPEN Setup layout at text 1.3+: round 40's two columns leave a late network too little map (all nodes on screen but not all at once). Designer must answer; default built: YOUR NETWORK top left, THREAT INTEL / IF PLACED right; alternative is YOUR NETWORK under THREAT INTEL at big text.
- RULING 2026-10-05 S-END kept: campaign-end hold build, lock's camera fit, `_set_panel` guard.
- RULING 2026-10-05 Port fixes: `_hold_selected_in`, `NeonCity.MARK_SPOT_RINGS`, `CityMapOverlay._loose_spot`, `HQ_KEY_SHARE`, `show_only`, `popping()` includes the Heat gauge bump, `netrun_scene._warm_hq` removed.
- RULING 2026-10-05 Dropped tests (look-pinned to removed pages, nine listed): test_anim4_drag_drop crew-chip click test; pass24 decision_log_gives_grid_fit_passes; anim_r3_city grid_column_never_ends_in_a_cut_row; anim_r5_city runs_end_warms_the_hq; anim_r6_city start_page_bakes; pass21_screens cell_status_badges; pass22_screens grid_runs_show_map_icon; pass23_city hq_mini_map; pass24_city run_rows_say_what_clearing_gives; pass24_city step_row_stays_in_column. Ported tests listed in the log (behaviour kept).

### 2026-10-05 Parity fix, card aiming and combat HUD
- RULING 2026-10-05 designer: (1) card aiming is grease pencil, not a dashed line; (2) aim over a target wheel shows the play's result on the affected wheel (preview == result, no new rule); (3) combat matches the concept.
- RULING 2026-10-05 CMB-10 `AimLinePencil`: plan-yellow solid wax via RaidPencilPool on pencil CanvasLayer 95 above all UI; stops at 0.28 of wheel for whole-wheel plays, 10 px short for other zones; loop on a target; `aim_line_draw`, `target_snap`, `pencil_wipe`; acid reticle tracked but not drawn (`CombatFxLayer.reticle_drawn`).
- SUPERSEDED H24 "aim line under the wheels": by the pencil rule (test renamed `test_the_aim_is_grease_pencil_above_every_ui`).
- RULING 2026-10-05 `PlayResultPlate`: while aiming at a target every changed wheel shows `IF YOU PLAY <CARD>` with HP from -> to and the same `ResultChipModel` chips; changed slices circled in pencil; random plays (GDD 2.10) keep odds on chips, no plate; plain hover shows chips only.
- RULING 2026-10-05 Hovered hand card draws at `HOVERED_CARD_Z` over HUD chips; motion layer, toast, inspect popup, aim hint, tutorial stay above (`OVER_HAND_Z`).
- RULING 2026-10-05 CMB-05: TURN strip `TURN n | FREE NUDGE n` over the address line; key hints are the tooltip only; outcome word follows the address.
- RULING 2026-10-05 CMB-06: EXECUTE system word on a dark terminal plate.
- RULING 2026-10-05 CMB-07: no global top bar in a fight (netrun_scene hides HudBar).
- OPEN CMB-07 vs the Heat gauge: the fight's top bar is untouched pending the designer; no default beyond hidden.
- RULING 2026-10-05 CMB-08: "Breaker 1" reads `CELL-1 // BREAKER`; SAVED stamp avoids the RAM panel and name sticker.
- RULING 2026-10-05 CMB-12: chip glyph box 20 px; block / shield keep `picto_block`.
- RULING 2026-10-05 CMB-14: held word `FIGHT WON` in sticker yellow; `DELETED` vinyl sticker on the beaten wheel.
- RULING 2026-10-05 CMB-16: FLATLINED stamps on the hub, square hollow box in the class accent.
- RULING 2026-10-05 CMB-18: tutorial card sits between the wheels (checked at 1.0 / 1.6 / 2.0).
- RULING 2026-10-05 Kept: CMB-11, CMB-13 (HARM edge + no-entry mark), CMB-15 / CMB-17 (white die-cut stickers on the dark PROCEED plate).
- RULING 2026-10-05 Follow-up b: aim hint sits just above the hand (above RAM row only while RAM is in the bottom row); SEND IT, next step and RESPIN / UNDO join CardPreviewOverlay's label-blocker group and labels turn round the wheel (±0.35 rad steps up to ±1.05).
- OPEN Key-hint line left the TURN strip (tooltip only); if W / R switches must show on screen the default proposal is a small key caption under the target's nudge pair. Designer must answer.
- Tests: new `test_parity_combat_hud.gd` (full tier); updated test_horizontal_pass24 (two tests), test_anim_r6_combat and test_anim_r4_combat; none dropped.

### 2026-10-05 Designer ruling, city as a map in raid and netrun views (S-MAPVIEW)
- RULING 2026-10-05 `CityView3D.map_mode`: on for RAID and NETRUN bands only (`map_band`), off for Grid, title, blurred backdrop, combat backdrop, HQ-run views; follows `band_lock`, no page calls it. City is greyed and lowered so nodes and links pop.
- DEFAULT Map mode numbers in CityConfig "Map mode": `map_saturation` 0.7, `map_contrast` 0.8, `map_mid` 0.22, `map_bloom` 0.45, `map_veil` violet at `map_veil_alpha` 0.22 (priority 15, between ambient layers and decal), `map_net_halo` 0.35.
- RULING 2026-10-05 Linear-as-sRGB check: raid pages and route need no decoding; no darkening.
- RULING 2026-10-05 `RaidMapNodes` (pure): raid map shows the Cell's network plus Sites the shown raid's threats enter and cross; never netrun sub-nodes; preview == result (map routes == `fight_raid` events).
- RULING 2026-10-05 `RouteLinkLayout` (pure): route nodes lie along the jack's link; layer k of L at k/L of the way, entry on the Cell's node, `route_link_lateral` 2.0 lots, `route_link_min_lots` 6; `RunManager.jack_link` uses `RouteLinkLayout.from_site`. No rule change.
- RULING 2026-10-05 Kept: route generation, raid resolution, Grid look, ANIM motion entries; decal disc fill, link strokes, badges stay with S-GRID / S-RAID (GRID-01 / RAID-04). Playout's orange spread unchanged.
- Tests: new `test_s_mapview.gd`; none dropped or changed.

### 2026-10-05 Parity fix, combat backdrop, round 2
- RULING 2026-10-05 designer round 2: every fight gets its own unique backdrop, the HQ boss fight a special view; placeholder built now.
- OPEN Unique per-fight backdrops: logged as a target, not built (proposed slice); owed: clean-run line in `docs/art_review/ART-12/perf.md` with a backdrop LOD / far-chunk-cut proposal.
- OPEN Question 4: with the orthographic close-up a far HQ stays out of frame while the Site is large (shows only for Sites near it); designer to decide whether to accept.
- RULING 2026-10-05 Site fights frame the fought Site's own lot (`BackdropCatalog.site_shot`); 28-lot inset and `site_close_up_lot` gone; landmark only on its own Site (`CityLandmarks.site_of`). Subject framed in `backdrop_site_frame`, share between `backdrop_site_subject_min` 0.3 and 0.6, camera along the diagonal view pointing to the corp's HQ (`site_yaw`).
- DEFAULT Subject focus: `backdrop_focus_radius` 0.18, `backdrop_focus_blur` 3, `backdrop_focus_dim` 0.22, `backdrop_focus_lift` 1.3 (not the DISPATCH canyon).
- DEFAULT Camera: `backdrop_hq_pitch_deg` 24, `backdrop_site_pitch_deg` 22 (designer 22-30, over budget accepted); `backdrop_site_ortho` 60.
- RULING 2026-10-05 Landmarks clear only a footprint mask (`CityView3D.footprint_lots`); the Cell's district keeps its whole box; Grid look otherwise unchanged.
- RULING 2026-10-05 Site or HQ close-up extends the city past the edge (`backdrop_extend_lots` 56) in its own model copy; shared model and Grid unchanged.
- DEFAULT Brightness: `backdrop_exposure` 5.0; `backdrop_tint_by_corp` lifts Halcyon.
- RULING 2026-10-05 Round 2 finding (3): raid and netrun views grey the city on purpose (S-MAPVIEW); not changed here.
- Tests: `test_parity_arena_backdrop.gd` fixtures replaced, new tests added; `test_hq_run_city.gd` updated; none dropped.

### 2026-10-05 Parity fix, combat backdrop (round 1)
- RULING 2026-10-05 designer: combat matches the concept (CMB-01, BOSS-03, BACKDROP-01, BACKDROP-02, MOTION-07).
- RULING 2026-10-05 MOTION-07 cause: linear ViewportTexture shown as sRGB; fixed by lit night look through `CityView3D.set_night_share` at share 0 (`BackdropCatalog.city_look`) plus a canvas grade on the city only (`city_grade`, never stills; `CombatBackdrop.graded` mirrors it).
- DEFAULT Backdrop look: CityConfig `backdrop_ramp`, `backdrop_sky`, `_haze`, `_grade`, `_bloom`, `_glow_threshold`; `backdrop_exposure` (now 5.0), `backdrop_saturation` 0.72, `backdrop_luma_band` 0.05-0.19, `backdrop_pool_dark` 0.55, `backdrop_pool_falloff` 4, `backdrop_render_height` 640, `budget_ms` 8.
- RULING 2026-10-05 HUD contrast: HP numbers 4.5:1, slice numbers 4.5:1, wheel edges 3:1 for every corp accent and the Cell's pink.
- RULING 2026-10-05 BACKDROP-01: boss fight fits the corp's whole HQ landmark into `backdrop_hq_frame` (`backdrop_hq_fit_keep_by_corp`, `backdrop_hq_frame_by_corp`, `backdrop_hq_ortho_by_corp`); HQ in day look (`backdrop_hq_landmarks_night` false), Site and DISPATCH canyon at night (`backdrop_site_landmarks_night` true); DISPATCH canyon unchanged.
- SUPERSEDED Round 1 site inset (`backdrop_site_inset` 28) and pitches (site 34, HQ 40): by round 2.
- RULING 2026-10-05 BACKDROP-02: corp Site landmark stands on the run's Site lot (Meridian none, keeps nearest building).
- RULING 2026-10-05 BOSS-03: no change needed; white bead chain was helix chaser lights, fine under the day look.
- RULING 2026-10-05 Kept: tier 0 and headless keep ungraded baked stills; reduce effects / skip land the won look at once; no motion entry changed.
- OPEN Combat backdrop open question 3 (linear-as-sRGB elsewhere): raid and route answered by S-MAPVIEW; others not in this slice.
- Tests: new `test_parity_arena_backdrop.gd`; `test_hq_run_city.gd` test changed; none dropped.

### 2026-10-05 Parity fix, combat wheels, designer round 2
- RULING 2026-10-05 Tone per kit: `WheelKit.TONE` table (sat, thresh, gain, pull, expo; `WheelKit.tone` mirrors the shader); Player 1.15 / 0.6 over 0.35, Meridian 1.1 / 0.6, Rebel_Cell 0.9 / 0.4 over 0.4 exposure 0.85; Solace, Halcyon, Orbital keep round 1 (1.4 / 1.1 over 0.3). Table is wheel material in code, not a `.tres`.
- DEFAULT Slice outlines at least 1.6 screen px (`OUTLINE_PX`); corp tier border 0.95.
- DEFAULT Scanlines fade below 2.5 screen px period (`SCANLINE_FADE_PX`).
- RULING 2026-10-05 Meridian screens pulled 0.65 toward Palette.CORP_MERIDIAN (#FF8C1A), expo x1.6; tested within 15 degrees of palette hue and not dark.
- RULING 2026-10-05 BOSS-04: keep main's full-blade needles (crowned on a boss), `pointer_spot` reads the blade window; multi-needle rails ±24 degrees; round 1's `d4corp.pin` readers reverted (SUPERSEDED).
- RULING 2026-10-05 Tests: `test_parity_wheel.gd` updated; NULL-contrast check now asks 3 of 5 families >= 1.5.
