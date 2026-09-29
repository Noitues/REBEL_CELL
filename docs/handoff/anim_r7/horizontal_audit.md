# ANIM-R7 horizontal audit (main 7b5c0f8)

Report only. Suite: 119 scripts, 1233 tests, 0 failing (441 s); schema smoke and
validate_content PASS (201 motion entries). No windowed runs; 1.6 checked statically.

**R6 confirmed:** REQUIRED_IDS matches the table (201/201); every id used and demoed. D1
motion_passes (raid playout only), motion_keeps (combat replay, route move). Every
registered helper goes through MotionSkip.handle (combat via its documented equivalent);
JackInputGate blocks input while jacking. D4 read_results never raises; disk check works.
D7 passive list matches code. D8 Typing.seconds_for / number_arrive. D9/D10 suite guard in
both run modes, no leaks or orphans. D11 log words translated. Bake cache: drawn_texture
hold, BakedTexture viewport ownership, ROUTE_KEEP release correct; cache bounded
(8 entries / 160 MB); workers joined. One-shot demo waits in MotionDemo, HQ, combat.
Known items: AWAITING_FIX is exactly 11, all still offend (unchanged). Rules English in
toasts is WORSE than described (~90 sites, see Rules P2-2).

## Combat
- **P2-A1** Top bar HP lags VICTORY: `combat_scene.gd` `_land_outcome` (~2020-2043) emits
  `outcome_landed` without clearing `_replay_start_hp` (1207); `top_bar_hp()` (1992-1997)
  returns the turn's start HP until `_release_forecast` (3079-3081). Fix: `_replay_start_hp = -1`
  before the emit, or return state HP once landed.
- **P2-A2** `beat_timing` paces on entries it never asks about (3526-3536 hp_drain settle,
  hit_line, hit_absorb, enemy_break delay; 3477 card_discard; 3514 enemy_turn_spin): with
  hp_drain off the replay still waits a roll per hit. The switch check misses it (per-id).
  Fix: `seconds_live` for motion parts, or list them as holds.
- **P3-A3** Portrait follows only HP that arrives as a travelling number; heals / no-number
  changes via `tv.play_hp` (4011-4012) snap at `_release_forecast`.
- **P3-A4** `replay_press` (772-791) reimplements handle (complete_all twice via consume);
  fine but diverges from STYLE 5.1 "every helper calls handle".
- **P2-A5** Combat view writes profile stats: `RunManager.record_seen/record_perfect` from
  `_on_state_changed` (1186, 1228-1230); `adopt_netrun` re-emits last_events, so a rebuilt
  page counts a PERFECT twice (latent). Fix: count in NetrunSession / RunManager.

## Netrun screens
- **P2-B1** Double translation: ToastNote's Label keeps auto-translate on (`toast_note.gd:29`)
  while callers pass tr() text (`hq_scene.gd:315, 887, 1466`, `netrun_scene.gd:3750`);
  InspectPopup same with tooltips; `DripButton.new(tr(action))` (`deck_view.gd:98`,
  `spinner_view.gd:113`). Fix: AUTO_TRANSLATE_MODE_DISABLED as `toast.gd:35`.
- **P2-B2** Codex fully untranslated: `codex.gd` has no tr/TextDb; raw display_name, English
  frames ("nudge x%d ignoring resistance", "special", "Firmware %s", "Exhaust."), enum
  `.keys()`. Feeds every card/slice/daemon/hub/firmware tooltip (~25 sites, e.g.
  `combat_scene.gd:2147, 2215-2228`, `wheel_view.gd:283-297`, `netrun_scene.gd:2738+`,
  `hq_scene.gd:3147`); also `daemon_row.gd:45`, `combat_scene.gd:525, 2222`.
- **P2-B3** Netrun demos still resume on a possibly freed scene: `_frames_in_tree`
  (`netrun_scene.gd:456-461`) awaits then checks; callers `_demo_route_pulse` (312, 317),
  `_demo_drag` (406-448). Fix: `_after_frames_here` pattern.
- **P3-B4** `netrun_map_view.gd:131-138` draws English ("Elite ", "done", " %+d Heat") at fixed
  10/16 px; built but hidden (`netrun_scene.gd:1219`). Remove or fix.

## City, raid, HQ, bake
- **P2-C1** Raid 2x/4x shortens reading holds: `RaidPlayoutPanel.set_speed` sets global
  Motion.speed; Heat banner hold `Motion.delay_of(&"heat_banner")` (`heat_poster.gd:363`)
  3.6 s → 0.9 s at 4x; Toast (`toast.gd:79`) 2.4 → 0.6 s. STYLE 5.5 says holds never shorter
  (only ToastNote.hold_seconds does it). Fix: never-shorter hold helper for all holds.
- **P2-C2** Switching a hold off doesn't do what docs say (STYLE 5.5 / HOLDS: "keeps its
  time"): `Fx.connect_hold` / `note_hold` (`fx.gd:723-741`) return 0 when jack_connect /
  raid_incoming_hold off (read e.enabled, not Motion.switched_on); heat_banner off hides
  banner and note entirely (`heat_poster.gd:351-353`). Fix: one rule; align code, docs, HOLDS.
- **P2-C3** HQ dev flags write state outside DemoSetup: `hq_scene.gd` 200-202
  (RunManager.corporation/.campaign), 225-229 (CampaignRules on_run_completed/claim/
  deploy_asset), 3738-3739, 3825. Motion lab writes live state: `motion_lab.gd` 874-875
  (run.current_node_id/visited), 936/998 (c.armory), 990 (c.schematics), 1093-1215 (hp, block,
  ram, wheel.rotation); DemoSetup.set_armory/set_schematics/demo_first_node exist.
  Structural: HQ actions call CampaignRules straight from the view (`hq_scene.gd` 362-455,
  599) while recruit/raid go via RunManager.
- **P2-C4** Rules text reaches players with raw ids: HQ button paths call `_report` without
  `_named` → English + site/segment ids (`campaign_rules.gd` 479, 483, 572, 722-755,
  833-867); `run_manager.gd:165` raw class id; link badge tooltip (`hq_scene.gd:2752`)
  raid_resolver English with raw ids; new-campaign log line (`hq_scene.gd:299-300`) raw
  home_variant_id / story_path_id; `CampaignRules.name_pending_raids` "Raid incoming: %s."
  with untranslated display_name (`campaign_rules.gd:903`).
- **P3-C5** `map_legend.gd` 11 tr_word strings lack `# TR` (27-32, 54-55), missing from
  strings.csv; "MAP LEGEND" (:96) drawn raw.
- **P3-C6** Views parse the rules' English: `raid_playout_panel.gd` t_name_from / NAME_VERBS
  (593-604), `_count_in` (620-631); `netrun_scene.gd:3769`; `combat_scene.gd:1245`. Breaks
  once rules text is keyed. Add structured event fields.
- **P3-C7** `neon_city.gd:1296-1308` sky fallback keeps drawn_texture (up to 48 MB VRAM) until
  the next bake.

## Motion rules, kit, tests, docs
- **P2-1** Inline motion numbers remain; the R6 scan checks only EASE_/TRANS_ literals and
  exempts every const. Still inline: `wheel_view.gd:322-329` (SPIN_MIN/MAX_SHARE,
  SETTLE_SHARE, NUDGE_TRAVEL_SHARE); `combat_fx_layer.gd:22-32, 61, 644-647` (GROW/FADE_SHARE,
  TRAVEL_FADE_TO, DISCARD_FADE, CARD_GROW_SHARE, POP_SETTLE_*); `page_transition.gd:19`
  FADE_SHARE; `raid_playout_panel.gd:51` FRAME_WAIT_SHARE; `raid_fx_layer.gd:72`
  NUMBER_HOLD_SHARE; `menu_motion.gd:29` CARET_ON_SHARE; `drop_layer.gd:62` STRIP_HOLD;
  `neon_city.gd:56-58` light periods; `city_map_overlay.gd:66/77`; kit BLINK_DIP_SHARE,
  POP_GROW_SHARE, SHAKE_STEPS; `dialogue.gd:14-15` SECONDS_PER_CHAR 0.045 / MIN_SECONDS 1.6
  (a reading hold outside the table). Fix: ALWAYS_ON tunings in the table, or a documented
  "kit shape constants" exemption; extend the scan to numeric shares/durations.
- **P2-2** Rules English reaching players, full scope (~90 sites): HQ toasts (34
  campaign_rules refusals + "Unlocked", 6 launch_error (only RUN_IN_PROGRESS keyed), 3
  run_manager); netrun toasts (~30 netrun_session _refuse/_grant); fight toasts (~17:
  `combat_resolver.gd:209-249`, `combat_session.gd:95`, `netrun_session.gd:266/281`,
  `combat_engine.gd:58/112`, via `combat_scene.gd:1234-1241` where tr(reason) has no key);
  tooltips (raid_resolver links; event choices `netrun_session.gd:612/614`); builder content
  `rebel_cell_builder.gd` 98-191; system log (off by default) ~60 more. `%+d` in core text
  (`heat_rules.gd:40/70`, netrun_session, effect_interpreter, `campaign_rules.gd:365/368`).
  Side finding: `deploy_failed` / `undock_failed` in TOAST_WARN_EVENTS never reach `_report`
  (combat events are kept out of last_events): silent failures. Not logged under DECISIONS
  "Open questions for the designer". Fix: rules emit text_key + args; views format with tr
  and site_word / TextDb.t.
- **P2-3** The switch check is per id, not per reader: `unswitched()` passes an id if any
  script asks, masking a second reader that paces/draws without asking (P2-A2). Static
  per-script scan found no further drawing offenders beyond the 11; pacing reads: combat
  ones, `heat_poster.gd:256` chaining on heat_pulse, netrun page holds (bounded, benign).
  The "animates → registers or says why" test only detects create_tween / Motion helpers;
  unlisted clock-driven animators: `crt_hum.gd`, `drag_ghost.gd`, `raid_fx_layer.gd`,
  `toast_note.gd`.
- **P2-4** Runner can fill the disk and never cleans up: 248 `rebel_cell_tests_*` folders
  (220 MB); `rebel_cell_tests_qf_48dak` 188 MB = one shard1/gut.log with 4,177,799 lines of
  "Object was deleted while awaiting a callback." after a failure in `test_art_w8a_menus.gd`
  (art-pass branch only) ending in signal 11. Fixes: delete the run folder on PASS unless
  --out/--keep; prune old folders at start; cap each shard log (kill a shard past ~50 MB,
  report a crash); scan crashed/no-results shards for guard and exit-leak lines (skipped by
  the `continue` at `run_tests.py:331`) and read guard lines in isolate(). Existing folders
  are logs only and safe to delete.
- **P3-5** Suite guard gaps: doesn't cover Motion._config (22 files use_config a switched-off
  duplicate), TranslationServer locale (~12 files), raw InputMap edits (9), ProjectSettings
  (pseudo-loc helper, pass24), Motion.recording.
- **P3-6** frame_waits gaps: "live" detected only inside the test function; FRAME_WAIT_RE lacks
  GUT's `wait_process_frames(`; helpers not scanned.
- **P3-7** Manifest/TEST_SUITE numbers stale: R6 A/B/C scripts at placeholder 30.0 (measured
  r6_combat 53.4, r6_city 12.5, r6_netrun 8.8); r5_city 40.0 vs 84.5; r5_netrun 40.0 vs 44.2;
  keys out of order (D9's refresh lost in merges). TEST_SUITE says 188-292 s / fast tier 77
  scripts 115 s; now 441 s / 78 scripts 131 s. Fix: --update-times from a green run.
- **P3-8** Doc drift: `motion_skip.gd:57-59` garbled sentence; `motion.gd:370-371` _settle doc
  comment orphaned above `held`; `docs/timeline/motion/README.md` has no R6 entries and says
  resolve_side_gap 0.35 s (now 0.2); R6 retune strips not recaptured (SEND IT pace, 0.16 s
  nudge, jack ease, withdraw, Heat note); ANIMATION_HANDOFF §3 lacks live / seconds_live /
  switched_on and MotionSkip registration; inline-shape scan skips tools/design_lab and
  accepts dictionary-fallback literals (`combat_fx_layer.gd:167, 972`).
- **P3-9** `%+d` in views: `ram_bar.gd:251, 276`, `codex.gd:126`, `netrun_map_view.gd:136`; hand
  signs `combat_scene.gd:2816-2818`, `wheel_view.gd:2566/2582`.
- **P3-10** Lab and combat lifetime: lab screen demos use bare awaits (`motion_lab.gd` 653-696,
  724-745) and `_play_scene` coroutines interleave (1066-1220); `combat_scene.gd:1432-1444`
  typed `view: WheelView` bound across 2 frames errors before its is_instance_valid check; a
  pending MotionDemo Waiter at --quit-after leaks one object at exit.

**Verdict: NOT CLEAN** (no P1; P2: A1, A2, A5, B1-B3, C1-C4, rules 1-4).
