## Implementation decisions (slice from DECISIONS.md:5934)
### 2026-09-27 Designer rulings on open questions (DECISIONS.md:5934)
- RULING 2026-09-27 Grid labels: late-campaign Grid labels keep off other nodes' icons too (built in ANIM-R1).
- RULING 2026-09-27 Grid at 1.6: keep folding map key, icon-only step buttons, LABEL_REACH 110 px.
- RULING 2026-09-27 Subtitles outside combat stay in the top band; toasts stay for refusals, saves, unlocks.
- RULING 2026-09-27 Drag pick-up is X / Space; A keeps each button's meaning.
- RULING 2026-09-27 Recall is a drop on CORE.
- RULING 2026-09-27 Dropping on JACK IN does NOT start a run: select the operative, then press JACK IN; crew drags only select (ANIM-R1). Supersedes ANIM-4's drop-launch.
- RULING 2026-09-27 Cards upgrade (cards in shop, upgrades a balance lever): new horizontal pass designs/builds card upgrades (Queued passes in MILESTONES).
- RULING 2026-09-27 Players may rearrange wheel slices any time outside combat (new horizontal pass).
- RULING 2026-09-27 Daily run changes more than the seed: a pass builds a list of daily modifiers and tests each one (not combinations).
- RULING 2026-09-27 Pacing: raise rewards slightly (not lower enemies); tune by simulation.
- RULING 2026-09-27 Rigger at ICE 0: small buff to its hub or deck. Rigger speed: leave Atk 16 slices.
- RULING 2026-09-27 Final Rack: extra Schematics payout; ICE 0 length fine.
- RULING 2026-09-27 REBEL_CELL difficulty: leave Mirror factor. Ghost: leave until playtest.
- RULING 2026-09-27 Corporation unlocks differ: beat Solace opens Meridian; Halcyon bought with Schematics; REBEL_CELL opens after ICE X on each other corporation; Orbital's rule set in the unlock pass.
- RULING 2026-09-27 Meridian difficulty: no change (ICE ladder handles it).
- RULING 2026-09-27 Boss stalls: add a soft enrage. Solace: no guaranteed Cleanse-type card.
- RULING 2026-09-27 Enemy damage scaling stays 1.2 per tier. Patrol runs: no cap.
- RULING 2026-09-27 Schematics surplus: add more sinks (boosts, unlocks).
- RULING 2026-09-27 Confirmed as built: Perfect-hook burst for every class, hooks repeat per resolution, alternatives cost 60 with no base unlock, freeze cooldown, custom-handler Daemons not mirrored, Meridian without own raid music.
- RULING 2026-09-27 Motion values as chosen from the strips.
### 2026-09-27 Test suite optimization
- RULING Test-run-only NeonCity switches `geometry_memo_enabled` (cap `GEOMETRY_MEMO_CAP`) and `emit_triangles` off, on only under GUT (`gut_cmdln.gd`), off in game.
- RULING Under GUT `SaveService.save_dir` is `user://saves/gut_<pid>`; temp files carry pid; each shard has own user://.
- RULING `tools/run_tests.py` shards by `tests/test_manifest.json` times; fails on failing test, crash, timeout, or script not run. Tiers `fast` (<2 min; guards for preview, rewind, replay, RNG, wheel math, raid resolver, map generator, save) and `full`. Full suite required before done. `test_suite_integrity` enforces.
- RULING `test_city_map_sweeps` is the single every-corporation Grid sweep (1.0/1.3/1.6, early/late); no UI sweep sampled down. Removed assertions mapped in `docs/TEST_SUITE.md`.
- DEFAULT full suite ~10-12 min single process; runner N=4 ~4.7 min.
### 2026-09-27 H24 combat
- RULING Nothing is deferred: every finding gets a slice; motion is its own Animation pass (designer standing rule).
- RULING Translate once via `tr()` (slice/aim/status words `Palette.*_WORDS`, YOU, RAM bar, WANTED letters capped `RANSOM_LETTERS_MAX`, RESPIN/UNDO, toasts); pre-translated labels don't re-translate (`StickerButton.pre_translated`). No "%+d": use "%s" with `CombatScene.signed()`.
- DEFAULT status line font floor `STATUS_MIN_FONT`; `hp_layout()` places HP number, NEXT and LAST TURN plates; LAST TURN shrinks to 1.0 size, then second line, then smaller; wheel keeps size.
- RULING `gain_shield` reports gain after cap, request kept as `requested`; `CombatOutcome.soaked` count drives "N BLOCKED".
- RULING Hit-testing: nearest satellite/arrow within reach takes the click. Toasts sit at foot of right column under subtitles.
- RULING Corrected: in a run the wheel is 108 px at 1.0, 81 px at 1.3/1.6; `BIG_TEXT_RADIUS_KEEP` is the tested bound (126→97 was standalone).
### 2026-09-27 H24 city
- RULING From `MapLegend.FOLD_SCALE` (1.3) the Grid key folds to a MAP KEY button (pad Y `cycle_target`); step buttons icon-only; map framed for the folded line.
- DEFAULT LABEL_REACH 110 screen px, binds every label (`_free_spot` checks reach); two-line labels via `CityMapOverlay.wrap_lines`.
- RULING Every Site with room gets a label (`CityMapOverlay.unplaced_with_room`); labels never overlap.
- DEFAULT GRID_FITS_MAX 4 (H23 entry saying 3 corrected).
- RULING `CampaignRules.clear_preview(c, corp, cfg, site, lookup)` applies `on_run_completed` to a copy; preview = result; run rows show badges.
- RULING One icon per concept (`KIND_SHAPES`/`KIND_SYMBOLS`, no shared silhouette); COOLING icon for Heat reduction; snowflake is ICE's only. Map screens use no SHD/shield wording; combat words DEFEND/ATTACK/EVADE.
- RULING Grid icons never overlap (ICON_FAN, ICON_STACK_MAX, ICON_STACK_LIMIT; ties by node id).
- RULING Map words via `CityMapOverlay.tr_word`, translated once. Mini-map labels shorten or are omitted, never cover Site blocks.
- SUPERSEDED H23 open questions (Grid at 1.6, key size, LABEL_REACH): answered here and by designer rulings above.
### 2026-09-27 H24 screens
- RULING `tools/export_text.gd` exports literals in tr/atr/TranslationServer.translate/`TextDb.mark` and lines marked `# TR`; re-export strings.csv after merging a branch with new tr() words.
- RULING `TextDb.signed(n)`; no `%+d` in translated lines (combat's still do: other owner).
- RULING Pages translate where built and show as given (`TextDb.shown_as_given`); kit parts use `tr`, not `atr`. REBEL_CELL brand tag on title/start not translated. `TextDb.t/ui/voice` with a missing key gives content text, never the key.
- DEFAULT `RAID_MIN_ZOOM` 0.45 (was 0.6); raid key becomes strip key when columns won't fit.
- RULING Only pad B (`InputEventJoypadButton`) leaves Modem/Grid/raid setup.
- RULING Pager `_wrap` takes `lead`; EVENT_RIGHT_GAP 16 px x text size; no-change choice shows `OutcomeRow.no_change`.
- DEFAULT Modem: `CHIP_ICON_SHRINK`, `TWO_LINES_BELOW` 85%.
- DEFAULT `CrewCard.COMPACT_FROM` 1.3, `CARD_MAX_SCALE`; share code moved to tooltip and pause menu (`PauseMenu.code_line`).
- DEFAULT Route: `ROUTE_FITS_MAX`, `ROUTE_MIN_ZOOM`.
- RULING Title Continue is one word + `IconLine`; supersedes H23 S12.
- RULING RUN THE RAID renamed START DEFENSE; `armory_words()` "ARMORY 3/6".
- RULING Screen-tied lines: a `scope` line ends on `Dialogue.enter_screen`; scopeless lines (Heat thresholds, run raid warnings, barks) play out.
- RULING Top bar captions CAMPAIGN / THIS RUN with tooltips; loot stickers carry FocusTip.
### Motion pass (timings in content/config/ui_motion.tres)
#### ANIM-R6 rules 2026-09-29
- RULING D1 helpers may answer `motion_passes(event)`; `complete_all` leaves passing helpers running; playout answers `drives_playout`.
- RULING D2 no inline tween shapes/motion numbers in kit (test scans for `Tween.EASE_*`/`TRANS_*` literals); new ids `flight_lift_share`, `flight_fade_share`, `choice_stamp_down_share`, `choice_stamp_hold_share` (ALWAYS_ON); `Motion.POP_GROW_EASE`.
- RULING D3 every entry with own motion must be asked via kit (`live`, `seconds_live`, `switched_on`); holds listed (`resolve_landing_hold`, `resolve_result_hold`, `combat_end_hold`, `toast_note_hold`, `jack_arrival_wait`, `asset_drop_wait`, `raid_incoming_hold`, `jack_connect`, `resolve_sequence`, `resolve_beat`, `resolve_pass`). OPEN `AWAITING_FIX` list only shrinks: A's `dead_wheel_fade`, `heal_number`, `hit_absorb`, `hp_lag`, `number_float`; C's `asset_drop_grow`, `beacon_blink`, `city_sign_pick`, `raid_outcome_stagger`, `route_target_pulse`, `select_ring_pulse`.
- RULING D4 runner survives broken results; free-disk check (`--min-free-gb` 1 stops exit 2, `--warn-free-gb` 5).
- RULING D5 schema checks go in `tools/schema_smoke_checks.gd`, not `schema_smoke_test.gd`.
- RULING D7 short motions join the one press passively (`MotionSkip.register_passive`); non-skippables listed in STYLE_GUIDE 5.5.
- RULING D9 `Settings.snapshot()/restore()`; suite guard (`SETTINGS LEAK`, `ORPHAN LEFT`, also compares `Engine.time_scale`, `Motion.speed`, `Motion.force_live`).
- RULING D8 `Typing.seconds_for` one cap; `number_arrive()` one answer; `Fx.flash` never flashes under reduce effects.
- RULING D11 system log words go through `tr`; rules' English event text stays untranslated (finding for screens).
#### ANIM-R6 city/raid/HQ
- RULING C1 Heat poster is a MotionSkip helper; reading hold (`heat_banner` delay) survives a press.
- RULING C5 Heat note consequence reworded ("A raid is queued. While Heat stays at 25 or more, elites are more frequent."); MAJOR thresholds' event_text reworded.
- RULING C11 RAIDS drops with the verdict, not the "Raid over" line.
- RULING C15 CLAIMABLE is "CAN BE YOUR NODE".
- OPEN hq_scene.gd dev-flag state writes (`--demo-classes`, `c.schematics = 100`, heat demo) to move to DemoSetup; owner: city/HQ agent.
- OPEN Unchanged timings: first Grid open 1.5-2.4 s cold start.
#### ANIM-R6 combat
- RULING A1 one press, one job (replay_press). A2 bark at `_land_outcome`. A4 chips say applied numbers ("HITS YOU 8 → 1 LEFT"; fully blocked "HITS YOU 0").
- RULING A5/A6 top bar HP reads fight HP; lost fight waits for JACK OUT; win moves on after `combat_end_hold` (1.4 s).
- RULING A7 replay retuned (plain turn 2.3 s, tested ≤2.6); STYLE_GUIDE 5.2 holds measured numbers.
- RULING A13 hover names "YOUR JOLT"/"YOUR NUDGE" on tape. A14 `NeonCity.hold_landing` during SEND IT. A19 `wheel_nudge` 0.16 s. New id `tutorial_next_pulse`.
#### ANIM-R6 netrun screens
- RULING B2 views never write game state; dev flags go through `DemoSetup`.
- RULING B5 run end title follows verdict (FLATLINED / JACK OUT / HOME FELL); `CombatScene.BARK_SCOPE`.
- RULING B7 toast holds `toast_note_hold` at slower of speed or raw (reading time).
- RULING B12 event story not repeated in subtitle bar; no operative event lines. B14 twin choice "(same road as choice 1)".
#### ANIM-R5 city/raid/HQ 2026-09-28
- RULING P1 kept bake via `BakedTexture` (Texture2DRD abandoned); unusable bake falls back to silhouette.
- RULING P9 Heat banner hold `heat_banner` retuned 1.4 → 3.6 s.
- RULING P17 schema smoke test is a runner loading content first (fixes exit 139).
- RULING P18 lookup rebuilt via `_restore_lookup`; node Disabled then Seized counts as one SEIZED (feed still tells both lines).
#### ANIM-R5 rules
- RULING R2 one press completes all helpers (MotionSkip.GROUP). R3 off-by-kind: own motion → no play, keeps time/size; `OFF_PARTS` → zero; `ALWAYS_ON` refused off by validate.
- RULING R4 lab demos must exercise real pieces. R6 fixed-wait rule scans tests/helpers.
#### ANIM-R5 combat / netrun
- RULING 1 outcome held until replay lands (`outcome_landed`). 5 dead enemy never acts: replay reorders via `ResolveBeats.doomed_first`, engine unchanged (GDD 2.2 simultaneous). 7 tag tape "WAS". New id `defeat_stamp`.
- RULING B3 flatline is permanent (permadeath, GDD 4.2/5.1); completed run verdict JACKED OUT, aborted HOME FELL. New id `flight_land_pulse`; `buy_fly` 0.7 s, `loot_pick` 0.7 s.
#### ANIM-R4
- RULING C2 `MotionSkip.verdict`; replay keeps presses on fight controls. H3 `RaidVerdict` words (ALL HOLD, "HOME -5", "1 DISABLED", "1 SEIZED", CAMPAIGN LOST; "HOME HIT" gone).
- RULING H5 schema change: `HeatThresholdData.id` ("heat_25", required, unique). H4 resolver events carry `threat_content`. H11a Heat events carry `before`/`after`.
- RULING H10 figures corrected by R5 Measurements.
- RULING C5 new ids `hit_line_flight`, `ride_swap`, `ride_shrink`, `ride_perfect`, `break_crack`, `modem_sign_strike`, `modem_sign_flicker`, `resolve_side_gap`, `resolve_attacker_gap`, `ram_refill_float`, `event_type`.
#### ANIM-R3
- RULING B6 territory colour `Palette.CELL_TURF` acid #D4FF00, never `cell_pink` (pink is damage); acid ≥40° hue from every corporation (Meridian nearest; first claim "furthest" corrected in R4 H9); every territory mark has a non-colour cue.
- RULING B5 one verdict per node; home gets banner not stamp. B11 no lambda on frame signals (rule).
- RULING A6f tick not strike-through for forecast chips; A5 snap result rather than slack.
#### Bake crash 2026-09-28
- RULING Root cause lambda one-shot on `process_frame`; rule: no lambda connected to `process_frame`, `physics_frame`, `frame_pre_draw`, `frame_post_draw` in scripts/ (`test_no_lambda_is_connected_to_a_frame_signal`). OPEN uncertain: display stress does not reach the deferred-redraw free; covered by `test_bake_crash.gd`.
#### ANIM-R2 / R1 (2026-09-28/27)
- RULING R2 city: JackInputGate sees events first; only `print("<tag>` capture markers (`anim4: `, `anim4b: `, `anim5: `, `MotionDemo: `) allowed in scripts/; `MAX_BUILDING` one bake at a time; equal route choices say "(same as 1)" (later reworded).
- RULING R2 combat: held choices focusable not disabled (pad); event titled "TERMINAL EVENT"; SEND IT hits one at a time, coloured by side; result waits for HP rolls.
- RULING ANIM-R1 M1 one jack, one run: `CampaignRules.launch_error` refuses with run in progress; designer ruling "prefer select, then jack in" applied.
- RULING R1 C2 one press rule (a press that completes a motion is consumed); C4 spawn/deploy/boss_phase events carry hp/spawned/ticks (hashes unchanged); `resolve_sequence` 2.0 s.
- RULING R1 M8 jack lands on built screen (`arrival_ready`, cap `jack_arrival_wait` 4 s); M6 Heat banner per crossing; M15 full-suite hang not reproduced, loops bounded.
#### ANIM-4b / 4 / 6 / 3 / 2 / 5 / 1
- RULING ANIM-4/4b `DropLayer`: drop makes same call as the button; `drop_error` runs rule on duplicate state; not-drags: deck viewer, Daemon tray, VIEW LOADOUT, combat cards (ANIM-3), route moves, Rack payouts; X/Space picks up, A keeps button meaning, B cancels. New ids `drop_stamp`, `market_fly`, `drop_buy`, `shred_feed`.
- RULING ANIM-6 page transitions: rebuilt page on same screen doesn't re-enter; focus lands when it ends; subtitle typing 0.025 s/char with Settings.subtitle_typing (default on); text size/language changes animate nothing.
- RULING ANIM-2 replay rule: engine state final on return, motion replays events (preview = result); any press skips to end state; rewind never crosses checkpoint.
- RULING ANIM-5 sped-up raid does NOT hurry the city (city keeps own clock; 4x would strobe beacons); `move` events gained `target`/`decoy` (hashes unchanged); jack_in 0.8 s, reduce effects 0.2 s fade.
- RULING ANIM-1 schema: new `UiMotionEntryData` and `UiMotionData` (`REQUIRED_IDS`) in `scripts/data/`, table loaded by `ContentRegistry` `MOTION_PATH`; `Motion.speed` clamped 0.25x-4x; reduce effects/headless show end state; ambient loops ignore speed.
