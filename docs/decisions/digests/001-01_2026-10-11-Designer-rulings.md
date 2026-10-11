## Locked design decisions (v0.9) + Implementation decisions, 2026-10-11 .. 2026-10-06
(Line refs approximate; the slice has no line numbers, order = file order.)

### CP-001 process (DECISIONS.md top of Implementation decisions)
- RULING 2026-10-11 CP-001.1 rule 6 scope: rule 6 applies to rule-bearing code (core, state, resolvers, save, RNG, content, layout at 1.0/1.6/2.0, reduce effects = end state); view glue, labs, tools get one flow test per screen plus the playtest gate; CLAUDE.md updated.
- RULING 2026-10-11 CP-001.2 full-suite cadence: between gates `tools/precommit.sh`; at a gate the full suite once in isolation, red run read via runner rerun-alone verdict, fixed, run once more; supersedes every "x3" cadence.
- RULING 2026-10-11 CP-001.3 Batch API lane: allowed for docstrings, cleanup, unit tests, refactors, renames; results land on `batch/<name>` branches and go through normal hand-back and gate.
- OPEN 2026-10-11 Batch API key: designer must set `ANTHROPIC_API_KEY`; no batch is submitted until present.
- RULING 2026-10-11 CP-001.4 playtest gates: one Human Playtest Task List and one checkpoint batch per User-Ready Gate; first list is the M14 completion gate.
- DEFAULT 2026-10-10 process redesign (`docs/process/00..04`): proposed tooling (precommit, select_tests, tools/batch, code-cleanup sub-agent, State Handoff at 65 % orchestrator / 60 % agents context, playtest list). `batches/` git-ignored; M14 pause stands.

### B4 b / B4 HQ round 44 (2026-10-06)
- RULING B4 b: MAP KEY chip kept; minimap hidden by default (M / `toggle_minimap` or opened MAP KEY shows it); ON AIR in HQ foot band; PATCH stays CORE's verb; top bar one-strip restyle is B5's; selection marker = vignette + one tag.
- RULING B4 b amends D17: holo fill 15 % and scanlines 12 % are for the Meridian hue; brighter corp hues scale by `body_share` (hue luminance ratio, max 1). Site card stamp at 60 % (`SiteHoloCard.STAMP_SHARE`).
- RULING B4 b D18: HQ-run page frames the run network at 60 % of frame height (`hq_run_landmark_share`); compound footprint is fallback only; canyon keeps CAM27.
- DEFAULT territory stamps: hold `territory_stamp_hold` 1.5 s, wipe `territory_stamp_wipe` 0.3 s (ui_motion.tres); wiped at once with motion off.
- RULING B4 b: Q3 raid-incoming words live in the system word's tooltip (pink line removed). Selection ring only while MapCursor focused (`CityMapOverlay.select_ring_shown`).
- OPEN B4 b perf: HQ idle 10.1 ms mean (tier 2) vs 8 ms budget; city at GRID band costs 5.6 ms GPU. Needs designer call: cheaper city at GRID band, or HQ idle at RAID band.
- RULING B4 HQ idle: City Grid look (`hq_band` GRID at every zoom; raid setup keeps RAID); map dim numbers in `ui_scrim_look.tres` "Map dim".
- RULING B4: HQ idle verb is JACK IN (`idle_pick`); UPGRADE/CLAIM/REPAIR/PATCH only once a Cell node is selected; one plan arrow (`HqPlanPencil`) along JACK IN link.
- RULING B4: corporate/seized Site file = decrypted holo (`SiteHoloCard`); Cell nodes keep terminal cards; CORE card ends with `> HQ ACTIONS` and HEAT SCRUB at rules' price (preview == result tested).
- RULING B4: raid warning at HQ is intercepted corp news (`intercept_raid_warning`), not the subtitle band.
- RULING B4 D20: ON AIR in foot gap when >= 520 px (at 1.0), else along whole foot.
- RULING B4 D7: Heat gauge has no stamp box; band word pops.
- SUPERSEDED B4 Q10 RAID SETUP column sticker + 1.6 step-aside: by B3 b (title is page title's baked sticker via HudBar.set_screen; instruction panel in paper tooltip).
- RULING B4 HQ runs (D18, Q11): titles "<CORP>: <CENTRAL SERVER NAME>"; city is solid GRID (`band_lock`), lanes glow 100 %; cut-off nodes 60 % grey discs.
- RULING B4 D25: no pencil fades; plan arrow and TARGET pencils write on 0.4 s and wipe with cloth.
- OPEN B4 (designer's call, kept against still): minimap terminal and MAP KEY strip stay top right; UPGRADE on CORE needs a home-upgrade rule the GDD lacks, so CORE's verb stays PATCH; overlay lime brackets/cursor and stacked CLAIMED/DOWN map stamps are B3's clutter rule; top bar look is HudBar's.
- OPEN known red not B4's: `test_anim6_screen_motion::test_end_state_layout_is_the_instant_layout_at_every_text_size` fails on loot page at 2.0 on main.

### Site fight backdrops (2026-10-06)
- RULING 2026-10-06 Site fight subject interim (Solace, Orbital busy): accepted until per-fight backdrops.
- RULING (designer, relayed) per-fight unique backdrops deferred until after gameplay polish passes; interim stands through M14.

### B2 c / B2 b / B2 combat composition (2026-10-06)
- DEFAULT Site block light (`combat_backdrop.gdshader subject_on`): `subject_base` 0.72, `backdrop_site_window_gain` 2, `backdrop_site_rim_gain` 0.9, `backdrop_site_street_gain` 0.5, `backdrop_site_focus_dim` 0.45; `backdrop_site_focus_lift` HQ/stills only.
- RULING B2 c: focus brackets sit on the die-cut edge and move with lift. Orbital Site busy accepted by art director, logged against per-fight backdrops.
- DEFAULT Site close-up framing: `backdrop_site_close_centre` (0.5,0.45), `backdrop_site_close_height` 0.4 (lock 35-45 %), `backdrop_site_close_max_width` 0.6, `backdrop_site_close_min_eye_bu` 180, lens >= 10 deg, `backdrop_site_reach`, `backdrop_site_focus_reach` 1.2. HQ-behind-Site waits for per-fight backdrops.
- DEFAULT grade: haze = `CityConfig.haze` night violet 18 %; `backdrop_saturation` 1.0 between wheels (0.6 cap is wheel pools'); `backdrop_rain_alpha` 0.15, `rain_keep_blacks` 1.
- RULING B2 b: lime brackets are focus only (never static marker, never while aiming; `CombatScene._target_focus`). Passive = emblem + tooltip.
- RULING B2 b: hub name 12 px (bible 4.2 floor wins), emblem alone under r 90 at 1080p. (Superseded by B2 original 10 px value; baseline wheel_view `font_const` back to 2.)
- RULING B2 D1 camera: perspective close-up for every fight: `backdrop_close_pitch_deg` 8, `backdrop_close_fov_deg` 44, `backdrop_haze_k` 0.18, `backdrop_close_cut_margin` 6, `backdrop_close_far_bu` 1400, `backdrop_close_sight_share` 0.2 (later 0 in B2 b). Replaces `backdrop_hq_pitch_deg`/`backdrop_site_pitch_deg`/`backdrop_haze`. Canyon uses `backdrop_canyon_share`.
- OPEN B2 perf: perspective adds +1.3..+3 ms city GPU; city budget 8 ms (`CityConfig.budget_ms`) exceeded only by worst fixture tier 1 (8.57). Proposed slice "perspective close-up LOD" (far-chunk LOD); designer to schedule.
- RULING B2 D4: target lime brackets never while aiming; only when >1 living wheel; drone keeps crosshair (not while aiming).
- RULING B2 D2 hub: emblem + tiny name; BLOCK/SHIELD/RESIST/FROZEN/LOCKDOWN are standing chips (not in preview row); `lint_baseline` wheel_view `font_const` 2 -> 3.
- RULING 2026-10-06 (designer) aiming result: `PlayResultPlate` removed; affected wheels' HP and result chips underlined in yellow wax (write on 0.4 s, wipe with cloth, never alpha fade); `play_plates()` -> `play_results()`.
- RULING B2 D15 hand: fan 2.5 deg/place, 12 % overlap, 6 px arc rise; aiming others 75 % brightness opaque; short-of-RAM card greyscale with NEED tag.
- RULING B2 D16 EXECUTE: Share Tech Mono 25 % alpha (`SendItSticker.SYSTEM_WORD_ALPHA`; round 22 said 30), `COVER_AT` (0.25,0.35).
- RULING B2 Q1(c): no top bar in a fight; Heat chip top-left (`heat_chip_look.tres`, 80x22 canvas px), read-only, campaign only.
- RULING B2 Q2: aim caption line removed (card tooltip); nudge buttons show key letter alone with 3 px keyline; Settings is 32 px terminal icon chip (procedural gear; tooltip carries name/key).
- OPEN B2 designer questions (defaults built): (1) lime target brackets with several enemy wheels: kept as attacks' focus; alt none outside aiming. (2) passive name: tooltip only; alt short chip. (3) Site close-ups can read small where Site building is low (Meridian, Orbital).

### B1b wax pencil (2026-10-06)
- RULING B1b: one wax material everywhere (`marker_stroke.gdshader`; `GreasePencilMark`/`Word`/`Art`, `PencilSet`); no draw call may use pencil ink outside material files (static test).
- DEFAULT pencil look: 9 px at 1080p (`WIDTH_1080`), one screen width regardless of zoom; shadow (2,3) px `PENCIL_SHADOW` #060308 85 %; wax alpha 0.96; sheen 35 %; `SHADOW_GROW_1080` 2.
- DEFAULT dropouts: nibble 40-70 % width (`DROPOUT_BITE`), gaps uniform 40-70 px (`DROPOUT_GAP`, words 70-110), alpha 0.35, seeded; shadow fades only under bite (`dropout_shadow_extra` 0.15). Pencil must never read as dashed.
- DEFAULT loops: `PencilShapes.hand_circle` 20 deg tail, `JITTER` 3 %, `START_IN` 5 %, `TAIL_OUT` 9 % (seeded view-only).
- RULING D25 motion: `pencil_write_on` 0.4 s, `pencil_wipe` 0.4, `aim_line_draw` 0.4, `raid_route_write` 0.4, `raid_drag_arrow` 0.4, `raid_dock_circle` 0.4; `raid_breached_write` keeps 1.2 s. No pencil appears whole (auto_write). MotionSkip completes; reduce effects shows end state.
- RULING pencil audit (K kept / R ruled / X removed): all raid, aim, TARGET, OURS NOW, dead-operative X, corp-down X, loot "+1 = N", Mainframe TOP N ONLY / BIN IT kept; CAN'T UNDO on every folder, pause menu notes, NEVER SLEEP, "ask about the back room", PLAY IT SAFE?? kept (bible appendix A: one pencil slogan per screen); TRUST NO ONE removed (round 19 bans pencil jokes); `raid_route_mark` A/B/C ring and heading chevron/minimap not pencil.
- OPEN B1b: raid home verdict ("HOME -5", "HOLDS") kept as pencil for now; review RAID-10 moves it to CELL HOLDS sticker on after-action paper; proposed slice "RAID-10 verdict onto the paper" (assigned to B3).
- OPEN B1b: HQ run's TARGET not verified windowed; covered by `test_hq_run_city` and static check (art director accepted). HQ run TARGET pencil joins `UiScrimPools.LIFT_GROUP`.

### B1a / B1a b scrim pools (2026-10-06)
- RULING B1a: `UiScrimPools` layer (shader `ui_scrim_pools.gdshader`, numbers `content/config/ui_scrim_look.tres`) between world and UI; pools x0.55; bands; up to 32 shapes; child `UiSpillShadows` (shadow black 45 %, 18 px soft, 6 px drop; spill 25 % out to 1.5x radius; pencil 48 px). Static, no clocks; tier 0 keeps pools, drops shadows/spill. API: `attach_after`, `add_wheels`, `mark_panel`, `mark_band`, `mark_panels_in`, `mark_spill`, `mark_verb_stickers_in`, `add_spill_source`. Title: shadows and pink spill only, no pools/bands.
- DEFAULT B1a b: wheel pool x0.55 to 1.25 R fading 0.3 R (`wheel_pool_fade`); panels x0.55 over 70 % of margin (`panel_pool_hold`), `panel_pool_margin_px` 120; `band_hold` 0.75; `pool_saturation` 0.6; bands x0.58 (42 % black); `CityConfig.net_keep_edge_px` 2. Acceptance: combat ring <= 0.6 x between; map margin/foot band 0.55-0.65. Fixtures `tests/fixtures/ui_scrim/` recapture when world look changes.
- RULING Q1 (B1a b): network draws over the scrim (bible 4.1); `LIFT_GROUP`, `NETWORK_GROUP`/`keep_network`.
- RULING Q2 (B1a b): any word directly over world carries ink keyline (>= 3 px at 1080p) or a plate; contrast not left to pool.
- OPEN B1a b bare words for B5: nudge key hints, HQ verb system word, raid setup intro line, title foot line and pad prompts.
- OPEN B1a: HQ D7 0.68 map-band darkening is not this layer (done in B4 map dim). Day stills' brightest 10 % under 0.55 pool fall to 3.0-4.4:1 contrast; words there keep outline/plate.

### Designer rulings on integration review (2026-10-06)
- RULING 2026-10-06 pause menu: keep all-sticker pause menu; overrides review D13.
- RULING 2026-10-06 campaign slots: LOAD and DELETE stickers on every folder with CAN'T UNDO; overrides D21.
- RULING 2026-10-06 sticker focus: rainbow gloss sweep on a scheduler (one at a time, D22); focus/hover show peel-back curl only.
- RULING 2026-10-06 aiming result: no hub plate; yellow-underlined HP result chips plus ghost landings.
- RULING 2026-10-06 DISPATCH: voice only with captioned words, no memo paper; supersedes EVT-03 memo (the later netrun-pages entry built a memo transcript; the ruling wins).
- RULING 2026-10-06 loot: add CONTINUE (FIGHT WON + OURS NOW + CONTINUE on dimmed fought Site). (The netrun-pages entry listed it as not built.)
- RULING 2026-10-06 (relayed): combat camera = perspective close-up for every fight; skins = accent tokens only; HQ behind Sites waits for per-fight backdrops; map links = only links the route uses, all on hover; RESET TO DEFAULTS = every tab (terminal button).
- OPEN: literal HQ rebuild to `direction_B.png` and route zoom to 40 % (review section f) not yet ruled (HQ round 44 build later done in B4).

### Parity fix route map c / b / base (2026-10-06)
- RULING route c: YOU ARE HERE on street marker is a placed label under `HERE_KEY` "#here"; `label_marks_of(n)` hook keeps labels off number chips.
- RULING route b (ROUTE-04 built): choices are focus stops on map stickers (`RouteStopPlacer`), numbered order then GRID VIEW; Enter/A presses; number keys still pick; "then:" line shows for lit choice only; dossier sub line wraps (`sub_lines`).
- RULING route (ROUTE-01): hidden nodes are grey "not yet" discs (`GHOST_SHARE` 0.42) with hairline dashes; district plates (`landmark_plates`); D13 stays.
- RULING ROUTE-05: key strip words "selectable", "not yet (hidden)"; node kinds stay.
- RULING ROUTE-06: `NetrunScene.ROUTE_TITLE` = "THE GRID"; route fit rescue `ROUTE_RESCUE_PASSES` 2 (no zoom in).
- OPEN (answered by route b, route base question closed): "one link per route" question still open, link logic unchanged.

### Parity fix netrun pages (2026-10-06)
- RULING RAID-13: mid-run raid is the 3D city at RAID band; routes = projection's (preview == result).
- OPEN RAID-13: `raid_socket_spec` duplicates `hq_scene.raid_socket`; proposed move to `RaidMapNodes` (HQ-BUILD owns file).
- RULING RAID-14: START DEFENSE is pink `VinylButton`; empty-assets line ported.
- RULING ROUTE-03: DECRYPTED small chip in foot; values wrap whole. Not built: JACK IN sticker under holo (HQ verb), OPTIONS > MAP switch (proposed slice if wanted).
- SUPERSEDED ROUTE-06 first attempt (rename to THE GRID reverted) by the route-map entry's fit fix.
- RULING SHOP-03: `BuyButton.BUY_FONT` 16; wallet at end of Daemons row at big text.
- RULING SHOP-05: LEAVE arrow art baked via `mainframe_parts_bake.py --part leave`.
- RULING SHOP-06: socket choice is the small spinner (`SpinnerMini.make_pickable`); new `NetrunSession.firmware_slot_error`. Not built (G14): amber REPLACE? on occupied socket.
- RULING SHOP-08: UPGRADE action reads "UPGRADE · 100 CYCLES" (`SpinnerView.action_words`).
- RULING EVT-01/02: terminal header names place; RUN side terminal; outcome chips beside choices (`EVENT_CHOICE_SHARE` 0.55); per-choice mono aside not added (no data).
- RULING EVT-03 (superseded by 2026-10-06 designer ruling 5: DISPATCH voice only, no memo).
- RULING LOOT-02/03: title sticker stays payout source; PAYOUT block top right; `LOOT_SIDE_FROM` 1.25, `LOOT_BIG_FLOOR` 1.25. CONTINUE not built here (later ruled to add).
- RULING END-01/02: run end = RunEndStage v2 with Polaroid, verdict sticker, BACK TO HQ; lost run greys city (`screen_grey.gdshader`, dim 0.35); `END_WIDTH` 600.
- OPEN known reds not from slice: `test_anim4b_run_drag_drop::test_the_new_pieces_keep_the_layout_at_each_text_size` (deck viewer 6 px over canvas at 1.3), `test_anim6_screen_motion` (mainframe purchase CARDS tag 10 px; end-state layout event 1.3 / loot 2.0), `test_anim_r1_campaign` three HQ-B tests.

- DECISIONS.md locked-design section (top, v0.9): wheel 30 ticks/6 slices; no Miss tier; spin resistance replaces jitter; Flip mirrors; resolution defensive -> offensive -> statuses; Heat one campaign meter; Armory cap 6; Mainframe gate min 3 Exploits; ICE 5 = tuning target; REBEL_CELL final unlock at ICE 10. SUPERSEDED: three-worlds visual baseline by ART_BIBLE v2 (2026-10-05 ruling 4); Cell colour stays hot pink.
