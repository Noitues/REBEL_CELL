# ANIM-R7 fix batches (ready to launch)

Every round 7 finding, split by area for parallel fix agents. Sources (full evidence,
file:line, repro) are in this folder: `vertical_audit.md` (V), `horizontal_audit.md` (H),
`naive_reviewers.md` (N). Nothing deferred: P3s included. Each agent gets
`process/fix_agent_common_rules.txt`: update its "main 81f1a5f" to the current main, "ANIM-R6"
to "ANIM-R7", "%TEMP%\r6<letter>" to "r7<letter>"; the auditor evidence path is gone.

Launch five agents in worktrees (`isolation: "worktree"`). The four areas match earlier rounds;
**E** is new because the rules-text translation (H P2-2) spans core and every screen and is
too large to share.

## A — combat (combat_scene, wheel_view, combat_fx_layer, resolve_beats, tutorial_overlay, dialogue in the fight)
1. P1 (V, N P1-1): tutorial step 1/7 "THE WHEEL" never shows in a real netrun fight; the opening
   turn_start advances a `until: ""` step (`combat_scene.gd:152-157`, `tutorial_overlay.gd:242-250`).
   Only a turn_start after the tutorial began may advance it. Test: step 0 on the first drawn frame.
2. P1 (V): at 1.6 the OPERATIVE subtitle dock draws over the tutorial box; in Title → Tutorial the
   box and dock run off the right edge; the RESPIN refusal note sits under Next/Skip. Lay out the
   right column from the scaled width and the dock's real height; toasts keep off the tutorial.
3. P2 (N P2-3, P2-6): tutorial pages cut mid-sentence; the step advances before the page with the
   instruction; CARDS overflows with a scroll bar at 1.6; Next's alpha pulse down to 0.45 reads
   disabled. Split at sentence ends, instruction on page 1, pages fit the note at 1.0/1.3/1.6
   (test: no scroll bar), pulse border/colour, alpha never under ~0.8.
4. P2 (V): typing subtitles eat the fight's hotkeys (Space = SEND IT, E = nudge) via
   `Dialogue._input` → MotionSkip.handle (`dialogue.gd:494-502`; Space is not ui_accept,
   `settings.gd:311-316`). Bound game actions count as works_ui (or ambient typing passes every
   press not aimed at the dock). Coordinate with D (MotionSkip rule). Test: bark typing, then
   Space/Q/X → the action happens and the typing completes.
5. P2 (N P2-1): "HITS BILLING DAEMON 6 → 1 LEFT" beside VICTORY reads as "enemy has 1 HP left"; "1
   LEFT" also means Armory copies. Say what happens ("→ 0 HP" / "TAKES THE LAST 1 HP", skull on a
   kill). Code `combat_scene.gd:2775-2778`, `clamp_item` `:3867`, `wheel_view.gd:2578`. This was the
   designer's "8 → 1 left" wording: see the open question in HANDOFF.
6. P2 (N P2-2): "collections drone" named in chips but only an unlabelled rim badge; put the badge's
   icon in its chip, name it (or leader line on hover/aim), pulse the badge when its chip ticks.
7. P2 (V): the real plain turn is 3.08 s (one hit each way), 2.54 s (blocked), 1.70 s (both defend);
   the R6 test uses six synthetic beats (`test_anim_r6_combat.gd:787`). Measure a real fight's
   schedule in the test; retune toward ~2.3 s or correct STYLE 5.2.
8. P2 (H A1): top bar HP lags VICTORY (`_land_outcome` ~2020-2043 doesn't clear `_replay_start_hp`).
9. P2 (H A2): `beat_timing` paces on hp_drain / hit_line / hit_absorb / enemy_break delay /
   card_discard / enemy_turn_spin without asking if they're on (3477, 3514, 3526-3536).
10. P2 (H A5): combat view writes profile stats (`record_seen/record_perfect` from
    `_on_state_changed` 1186, 1228-1230); move to NetrunSession / RunManager.
11. AWAITING_FIX combat views (switched-off entries still animate): dead_wheel_fade, hp_lag
    (wheel_view); heal_number, hit_absorb, number_float (combat_scene). Remove each id from
    `tests/unit/test_motion_lab_demos.gd` AWAITING_FIX as it's fixed.
12. P3: portrait snaps for heals / no-number HP changes (H A3); `replay_press` duplicates handle
    (H A4, align with STYLE 5.1); tutorial note stays up on VICTORY/DEFEAT (N P3-1); DEFEAT: 0/60 HP
    stays green, Heat jumps with no cause shown (N P3-2); enemy hits you in the SEND IT that kills it
    with no explanation (N P3-3); bark pages one line with "…" and a one-word tutorial page 2 (V);
    enemy RAM drain "RAM -1" names no source, RAM bar "(-3)" mixes cost and drain (V); PERFECT bark
    beside DEFEAT, DISPATCH line in the fight before JACK OUT at 1.3 reduce effects (V); top bar
    drops HP/CYCLES and shows campaign tags while DEFEAT still shows (V); WAS line truncates (V);
    `combat_scene.gd:1432-1444` typed WheelView across 2 frames (H P3-10); hand-built signs
    `combat_scene.gd:2816-2818`, `wheel_view.gd:2566/2582`, `ram_bar.gd:251, 276` → TextDb.signed.

## B — netrun screens (netrun_scene, loot, Modem, event, route, run end, toast_note, deck viewer)
1. P2 (V): route shows the silhouette after mid-run Heat changes (+5 event ~1.5-2 s; after the
   interlude playout ~3.6 s): regression. Prebake the route under the post-step Heat
   (`netrun_scene.gd:1859-1867` corp_creep), like prebake_run_end. Measure in real time.
2. P2 (V): interlude playout's Continue gets no focus when the raid finishes (`netrun_scene.gd:1859`).
3. P2 (V): Modem focus tips cover buttons (LEAVE THE MODEM at 1.6; BUY/SHRED notes and SLICES tags at
   1.3). Buttons into FocusTip's avoid set.
4. P2 (N P2-4): Modem SLICES "BUY 100" stay yellow when unaffordable (`netrun_scene.gd:2738-2759`).
5. P2 (H B1): double translation: ToastNote Label auto-translate on (`toast_note.gd:29`) with tr()
   callers (`hq_scene.gd:315, 887, 1466`, `netrun_scene.gd:3750`); InspectPopup tooltips;
   `DripButton.new(tr(action))` (`deck_view.gd:98`, `spinner_view.gd:113`).
6. P2 (H B2): Codex fully untranslated (`codex.gd`, ~25 call sites incl. every card/slice/daemon/
   hub/firmware tooltip; `daemon_row.gd:45`, `combat_scene.gd:525, 2222`; `codex.gd:126` %+d).
7. P2 (H B3): netrun demos `_frames_in_tree` (`netrun_scene.gd:456-461`) still await then check;
   callers `_demo_route_pulse` (312, 317), `_demo_drag` (406-448) → `_after_frames_here`.
8. P3: event choice stamp is a wordless snapshot (N P3-4, V): stamp "TAKEN ✓" or flash the border;
   "[2] Fight (same road as choice 1)" / "then: Shop" still confuse (N P3-5); event body truncated at
   1.6 in the storyboard (N P3-6: check typing ends within settle); "NEED 112 HAVE 101" draws below
   the CYCLES tag paper (V); deck viewer first row overlaps "Left click: select…" (V); route page
   has no focus on arrival (V); `netrun_map_view.gd:131-138` hidden view draws English at fixed
   10/16 px (H B4: remove or fix).

## C — city, raid, HQ, bake (hq_scene, city_map_overlay, neon_city, raid_*, heat_poster, map_legend)
1. P2 (V): a Heat threshold crossed by a flatline plays only in the fight's small poster behind
   DEFEAT; HQ shows no crossing (`heat_poster.gd:134-160` remembers per campaign). Play it on HQ.
2. P2 (V, N): after a won run the cleared district's tint is a large bright blob behind the run-end
   window and CELL STATUS; its CLEARED stamp is cut at the left edge. Keep stamps inside the view or
   skip off-view stamps/tints on non-map pages.
3. P2 (V, 1.3): dead operative's crew card FLATLINED stamp overlaps "// BREAKER // RANK 0".
4. P2 (H C1): raid 2x/4x shortens reading holds (global Motion.speed; `heat_poster.gd:363`,
   `toast.gd:79`): one never-shorter hold helper (coordinate with D).
5. P2 (H C2): switching a hold off doesn't match docs (`fx.gd:723-741` read e.enabled;
   `heat_poster.gd:351-353` hides banner and note). One rule; align code, STYLE 5.5, HOLDS.
6. P2 (H C3): HQ dev flags write state outside DemoSetup (`hq_scene.gd` 200-202, 225-229,
   3738-3739, 3825); motion lab writes live state (`motion_lab.gd` 874-875, 936/998, 990,
   1093-1215). Structural: HQ actions call CampaignRules from the view (362-455, 599) → RunManager.
7. P2 (H C4, N P2-5): raw ids and rules English in HQ toasts/tooltips (see H C4 list). Coordinate
   with E (E changes the rules side, C the HQ views). Raid feed: Heat icon float at CORE when the
   collector arrives; icons in feed lines.
8. AWAITING_FIX city views: asset_drop_grow, route_target_pulse, select_ring_pulse
   (city_map_overlay); beacon_blink, city_sign_pick (neon_city); raid_outcome_stagger (raid_fx_layer).
9. P3: `map_legend.gd` 11 tr_word strings lack `# TR` and "MAP LEGEND" drawn raw (H C5); views parse
   rules English (`raid_playout_panel.gd` 593-604, 620-631; `netrun_scene.gd:3769`;
   `combat_scene.gd:1245`) → structured event fields, with E (H C6); sky fallback keeps
   drawn_texture up to 48 MB (H C7); threat token missing from MAP LEGEND and the "IF THE RAID RUNS
   NOW" circle fades half under RAID FEED (N P3-7); heat banner "(25-)" reads as minus and overlaps
   NOTICED (N P3-8); campaign-end profile jargon "Something opens at ICE 10 everywhere (0/4)",
   "Best ICE: … −" (N P3-9); Grid pad first focus "< PREV SITE", JACK IN 3 Downs away (V); loadout
   viewer under pad shows "Close [Esc]" (V); feed header "Raid over" while the last step still plays
   (V). Unverified by V: a threat withdrawing at the verdict (build a raid where one is destroyed).

## D — motion rules, kit, tests, docs, runner
1. P2 (H P2-1): inline motion numbers remain (list in H); the R6 scan only checks EASE_/TRANS_.
   Table (ALWAYS_ON tunings) or a documented kit-shape exemption; extend the scan to numeric
   shares/durations; `dialogue.gd:14-15` reading hold into the table.
2. P2 (H P2-3): the switch check is per id, not per reader (masks A9); make it per script.
   "animates → registers or says why" misses clock-driven animators (`crt_hum.gd`, `drag_ghost.gd`,
   `raid_fx_layer.gd`, `toast_note.gd`).
3. P2 (H P2-4): runner never cleans up (%TEMP% had ~248 `rebel_cell_tests_*`, one 188 MB log from a
   runaway art-pass test ending in signal 11). Delete the run folder on PASS unless --out/--keep;
   prune old ones at start; cap shard logs (~50 MB → kill, report crash); scan crashed shards and
   isolate() for guard/exit-leak lines (`run_tests.py:331`).
4. The MotionSkip rule gap behind A4 (game action keys in works_ui) and the never-shorter hold helper
   behind C4: own the kit side.
5. P3: suite guard gaps (Motion._config, TranslationServer locale, InputMap, ProjectSettings,
   Motion.recording) (H P3-5); frame_waits gaps (`wait_process_frames(`, live via helpers, helpers
   scanned) (H P3-6); manifest times and TEST_SUITE numbers stale (`--update-times`) (H P3-7); doc
   drift (`motion_skip.gd:57-59`, `motion.gd:370-371`, motion README R6 rows and
   resolve_side_gap 0.2, recapture R6 retune strips, ANIMATION_HANDOFF §3) (H P3-8); lab bare awaits
   and interleaving `_play_scene` coroutines, MotionDemo Waiter leak (H P3-10); every
   `--quit-after` Movie Maker run leaks 2 ObjectDB instances (N P3-10).

## E — rules text keys (core + views; new this round)
H P2-2 (~90 player-facing sites) and N P2-5: rules write English sentences (HQ refusals incl.
launch_error, netrun_session _refuse/_grant, combat_resolver/combat_session/combat_engine toasts,
raid_resolver link texts, event choices, rebel_cell_builder content, system log) and `%+d` in core
(`heat_rules.gd:40/70`, netrun_session, effect_interpreter, `campaign_rules.gd:365/368`). Rules
emit `text_key` + args (and structured fields views can read instead of parsing English); views
format with tr / TextDb.t / site_word. Silent failures: `deploy_failed` / `undock_failed` never
reach `_report`. This touches `scripts/core/` (pure, deterministic; keep replays identical) and
possibly event payload schemas: log in DECISIONS, update `tools/schema_smoke_checks.gd` if a
schema changes. Also log it under DECISIONS "Open questions for the designer" if any wording
choice needs a designer call.
