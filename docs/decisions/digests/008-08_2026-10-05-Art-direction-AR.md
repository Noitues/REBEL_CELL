## Implementation decisions (slice from DECISIONS.md:5161)

### 2026-10-05 Art direction ART-0 reduce_effects shader global
- RULING 2026-10-05 reduce_effects: a project-wide shader global (`[shader_globals]` in project.godot, float 0.0); supersedes area E's per-material uniform. rc_common declares `global uniform float reduce_effects;`.
- RULING 2026-10-05 Fx owns the global: `Fx.REDUCE_GLOBAL` / `_apply_shader_global()` set it first in `Fx._ready` and on every `apply_settings`; `Fx.shader_reduce` mirrors it for tests.
- SUPERSEDED ShaderReduce (`scripts/ui/fx/shader_reduce.gd`): removed by the global. Scripts' own zeroing of shader strengths stays.
- SUPERSEDED tests `test_every_animating_material_is_tracked`, `test_shader_reduce_follows_the_setting`: replaced by `test_no_script_keeps_a_per_material_reduce_effects` and `test_toggling_the_setting_changes_the_global`.
- DEFAULT reduce_effects global: 0.0 (effects on), in project.godot.

### 2026-10-05 Designer ruling: DISPATCH text
- RULING 2026-10-05 DISPATCH text: always a clean CRT terminal feed (red accent, ART_BIBLE v2 §1.2), never sticker or pencil. GDD 8.2 "never zine-styled" reworded. Closes the ART-0a open question.

### 2026-10-05 Designer ruling: check cadence for M14
- RULING 2026-10-05 agent checks: agents run only the fast tier (`python tools/run_tests.py --tier fast`), their own new or changed tests, the schema smoke test and content validation (`docs/handoff/art_0/process/checks_fast.sh`). No full suite per agent.
- RULING 2026-10-05 merges: import + the same fast checks, then push. A red fast check is never pushed.
- RULING 2026-10-05 end of each ART batch: full suite x3 (`process/checks.sh`), smoke and validate, run in isolation, failures fixed before the audit. A batch is the unit declared done (CLAUDE.md).
- RULING 2026-10-05 parallelism: at most 4–5 agents at once.

### 2026-10-05 Designer rulings: names for M14 (plan §3.1)
- RULING 2026-10-05 D2: ATTACK→SHIM, CRIT→OVERFLOW, DEFEND→DEFRAG, EVADE→DETOUR, HEAL→HOTFIX, AFFLICT→INFECT; SANDBOX, TROJAN, NULL unchanged.
- RULING 2026-10-05 D3: JUDGEMENT retired; Meridian's RAM-drain slice is PRIORITY; Meridian CRIT is AIRMAIL.
- RULING 2026-10-05 D4: INERTIA→WEIGHT; Solace HEAL→GROWTH.
- RULING 2026-10-05 D5: "Mainframe Gate"→Central Server (GDD 11.7); per-corp names The Master Manifest, The Genome Core, The Panopticon, Launch Control as content strings.
- RULING 2026-10-05 D6: player-facing "Firmware" everywhere; "Microchips" retired.
- RULING 2026-10-05 D8: precision tier Partial→WEAK (GDD 2.4).
- RULING 2026-10-05 D11 Heat bands: old FLAGGED→HUNTED, old NOTICED→FLAGGED, new NOTICED = a couple of alarms; thresholds unchanged; screen glitch only as off-by-default Options extra `heat_glitch`, exempt from VfxTier.
- RULING 2026-10-05 D12: respin control reads RESPIN, never CHECKPOINT; the undo block shows on UNDO.
- RULING 2026-10-05 D9, D18–D20: covered by pause-point-0 rulings or presentation only.
- OPEN D13–D17: asked before the batches that need them (ART-3, ART-4, ART-7).
- RULING 2026-10-05 internal names follow display names; no compatibility kept (pause-point-0 ruling 5).

### 2026-10-05 Art direction ART-0 docs landing (ART-0a)
- RULING 2026-10-05 art docs land by `git checkout`/`git show` from tag `art-concepts-r43` (9a62cec), never by merge. Docs only.
- RULING 2026-10-05 plan annotations: plan §1 items 1, 5, 6.2, 6.5, 6.6, 7, 9 and the §5.1 "Renames break saves or replays" row are struck or annotated, never rewritten. Bible Appendix C #12 annotated with ruling 11, #1 with ruling 10.
- DEFAULT `docs/art_reference/`: 60.7 MB, cap 80 MB. Stills over 600 KB are 1600 px JPEG q82. GIFs up to 1.0 MB are byte-identical. The 42 GIFs over 1.0 MB become 8-frame keyframe sheets or the art pass's own strips. Originals stay on the tag. The round 40 raid GIFs stay on the tag.
- RULING 2026-10-05 `docs/art_history/ART_PLAN_M13.md` is the superseded art-pass plan. The 14 M13 entries are copied verbatim below.
- RULING 2026-10-05 GDD §9.1–9.4 rewritten around ART_BIBLE v2; 9.5 unchanged; locked line "Visual baseline: three worlds" struck.
- RULING 2026-10-05 ART_BIBLE v2 is the visual source of truth from M14; STYLE_GUIDE §5 stays binding.

### 2026-10-05 Art direction ART-0 D: visual QA harness and lint
- DEFAULT static lint baseline: `tools/visual_qa/lint_baseline.json`, 205 lines in 41 files. It gates `tests/unit/test_visual_lint_static.gd` (fast). A count may only go down. ART-1…12 drive it to zero.
- RULING 2026-10-05 ported art-pass files with literals add only their own rows to the baseline in that merge, said in the report, never silently.
- DEFAULT harness: 58 screens, text scale 1.0 / 1.6 / 2.0, mouse / pad, reduce effects off / on, grey and deutan filters. Settings axes (high contrast, reduce motion, colour-blind) are skipped until ART-0 C ports them. Pictures are saved at 800x450. The driver refuses to start with < 5 GB free. Packs go under %TEMP%.
- RULING 2026-10-05 the harness waits (max 20 s) for visible cities and starts every screen from a cold bake cache.
- RULING 2026-10-05 `CityBakeCache._stop` checks the painter instance before assigning (freed-scene crash fix).
- DEFAULT first matrix: 696 captures, all ok. At 2.0 the top bar takes two rows and crew dossier / Pirate Radio text is cut (area C layout-at-2.0 work).

### 2026-10-05 Designer rulings: pause point 0
- RULING 2026-10-05 #1 order: M14 first (ART-0…ART-12), then re-evaluate every ANIM-R7 finding, fix the valid ones (batches A–E, re-cut), re-evaluate the horizontal list, H25+, Queued passes. ANIM-R7 is paused, not dropped.
- RULING 2026-10-05 #2: port, don't merge. Art direction wins conflicts, which are raised as questions defaulting to the art direction. M14 fails unless the look and most of the feel are present. ANIM motion behaviour (MotionSkip, holds, reduce effects = end state, `ui_motion.tres` entries) is kept and restyled. Tags: `art-m13-final` = f80f393, `art-concepts-r43` = 9a62cec.
- RULING 2026-10-05 #3: curated `docs/art_reference/` on main; the full archive stays on the tag.
- RULING 2026-10-05 #4: GDD §9 rewritten around ART_BIBLE v2 (cel city + CRT screens + vinyl stickers + grease pencil + light spill; no UI ever covers grease pencil).
- RULING 2026-10-05 #5: no save or replay compatibility. Internal names follow display names. Saves and replays go to a git-ignored project folder (ART-0 S0).
- RULING 2026-10-05 #6.1: Meridian RAM-drain slice is PRIORITY; the Manifest hub `priority_routing` is renamed Customs Seal (`customs_seal`), rules unchanged.
- RULING 2026-10-05 #6.2: raid words replace GDD words: Seized→TAKEN, Disabled→DOWN, Holds→CELL HOLDS (a node that holds shows HOLDS). BREACHED = the home server (CORE) falls (integrity 0, campaign lost). GDD 3.3, 7.1, 7.2 updated, then code and content.
- RULING 2026-10-05 #6.3: Upgrade tiers are Roman numerals I–III; Site tiers stay T1–T4.
- RULING 2026-10-05 #6.4: VAULT / KEY / SPOOF and the raid node glyphs unify on the round 42 icons.
- RULING 2026-10-05 #6.5: shop node "Modem" renamed Mainframe everywhere (node type, ids, strings, GDD 4.2, 6.3, 11.x); the old gate is Central Server (D5).
- RULING 2026-10-05 #6.6: the fist crest is the Cell's mark.
- OPEN Cell vs eventual REBEL_CELL corporation: telling them apart is a future concept slice, logged under "Open questions for the designer".
- RULING 2026-10-05 #7: fidelity first, then optimise. The ART-1 render spike picks the most faithful technique, then optimisation brings it inside the perf budget (plan §5.2). The budget is a gate, not a reason to change the look.
- RULING 2026-10-05 #8: G1–G16 mechanic proposals are re-evaluated after the art integration; art stays in `docs/art_reference/` meanwhile.
- OPEN #9 R7 overkill wording ("→ 1 LEFT"): re-evaluated after the art pass (HP result chip, plan D15, may replace it).
- RULING 2026-10-05 #10 status badges (Appendix C #1): the overlay is the status; a small flat corner badge only carries a ×N stack tab or ×1.5 / ×0.5 tag.
- RULING 2026-10-05 #11 (Appendix C #12): the raid view drops the amber dashed socket for DOWN nodes and uses the Site markers' white bolt over a greyed marker.

### M13 art pass (art-pass branch, superseded in part)
- SUPERSEDED M13 entries: they implement ART_BIBLE v1.0 (zine / neon / cyberdeck), superseded by v2. Direction-agnostic infrastructure is ported by ART-0 salvage S1–S5. Entries describe the art-pass branch, not main.
- RULING 2026-09-28 Q1 cards: about 30 base illustrations tinted per type, unique art for rares and class cards.
- RULING 2026-09-28 Q2 class accents: the §7.1 proposals are the token values.
- RULING 2026-09-28 Q3 body face: IBM Plex Sans Condensed (OFL) for text blocks over 3 lines.
- RULING 2026-09-28 Q4 HQ: full DECK frame.
- RULING 2026-09-28 Q5 text scale: `Settings.TEXT_SCALE_MAX` 2.0, additive.
- RULING 2026-09-28 Q6: concept images are script-drawn pixel art / vector, under `docs/art_review/<W>/concepts/`, never shipped without designer approval.
- RULING 2026-09-28 autonomy: the orchestrator answers open questions itself and logs them. Review output goes to `docs/art_review/W<n>/`.
- DEFAULT W1: MSDF on every face (`msdf_pixel_range` 16, font `.import` files force-tracked). HP exactly 50% = GAIN, exactly 25% = WARN. Unknown class gets the `TEXT_MID` accent. Heat bands come from the config's MAJOR levels.
- RULING 2026-09-28 W1: at `STEP_ICONS_SCALE` and above Back to HQ shows its icon only.
- RULING 2026-09-28 W6 reduce effects: one `reduce_effects` global uniform from Fx (now superseded by the ART-0 shader global, which supersedes the uniform). Script-side zeroing stays.
- DEFAULT W6 `UiMotionEntryData.tier` T0–T4, default T1; limits in `VfxTier`. Schema change, logged.
- RULING 2026-09-28 W6 flashes: `Fx.flash` defaults to T3, a full-screen flash must pass T4 and does nothing under reduce effects. `screen_flash` 0.45 is clamped to 0.4 (T4), `victory_flash` 0.8 to 0.7 (T3).
- DEFAULT W6 tiers: T0 loops and ambience; T1 hover, focus, UI moves; T2 hits, stamps, drops, buys, refusals, `raid_move`; T3 Perfect, kill, phase, Heat band, claim, influence, VICTORY/DEFEAT; T4 jack transitions and `screen_flash`. Caps bind only FX-layer effects; UI motion keeps §10 budgets.
- OPEN W6 for W3: miss static not triggered; `slice_hit` should get the attacker's slice type; `hit_shake` 3 px exceeds T2's 2 px (route through `Fx.shake_px`); `WheelView` hit flash through `Fx.request_flash`; scale the slash with damage.
- RULING 2026-09-28 W10: static lint never rises unless given `--reset`; runtime lint is a report, not a gate. The harness uses private members (`_panel`, `_show_current`, `_preview_card`), so owners keep them or add public hooks.
- RULING 2026-09-29 W9s: colour-blind is a global LMS daltonize correction on canvas layer 127 (`off` = no layer; W10 filter at 128). Patterns and glyphs stay the primary cue.
- RULING 2026-09-29 W9s: `HighContrast.apply(theme)` gives black fills, 2 px tinted edges, `TEXT_HI` text, 4 px `FOCUS`, 3 px button edges. Views with their own `_draw` must read `Settings.high_contrast`.
- RULING 2026-09-29 W9s: reduce motion is independent of reduce effects (`Motion.camera_moves_allowed()`, `parallax_allowed()`, `page_transition_style()`). Resolve speed is x1 / x2 / instant; holding `resolve_fast_forward` runs 4× and is exempt from MotionSkip.
- DEFAULT W9s: pad glyph set auto / xbox / playstation / switch / deck (unknown = xbox). Steam Deck first-run `text_scale` 1.2 (`TEXT_SCALE_STEAM_DECK`).
- RULING 2026-09-29 W2: `FOCUS` corner brackets (`StyleBoxBrackets`) replace the acid ring. The 1.03 scale is pad focus only. Named button variants size to label + 32 px; plain `Button` keeps its 10 px row padding. `MenuItem` text is at `body`. Disabled labels use `TEXT_MID`. `ConfirmDialog`: Yes = Danger, No = Secondary.
- RULING 2026-09-29 W2 toast: hold is the longer of 2.5 s and the stamp reading rule; `toast_note_hold` retired but kept. Tooltips are 36 columns at every scale.
- OPEN W2 owners: switch `Palette.STATUS_GLYPHS` users to `StatIcon.draw_status`; replace native controls with kit components; `IconMark.attach(b, StatIcon.TRASH)` on Delete buttons; RESPIN sticker words overrun at 1.6.
- RULING 2026-09-29 W5: operative tint is the class accent ±7%. Expression enum is `PortraitArt.Expr`. Class pair distance floor 0.12 (closest pair 0.142). Polaroid caption is the rank. FLATLINED stamps and low-HP glitch bars use `HARM`. Enemies fill with their corp's `CorpPattern`; bosses add a halo. Hologram intro is T4, a cross-fade under reduce effects. `crt_overlay` settings scan 0.18, roll 0.12, flicker 0.02.
- RULING 2026-09-29 W4: hand cards (112×148) show a compact face; Modem, loot, deck view and detail show the full face. No ellipsis: text steps down, then art (floor 15%), then the band drops, then the card grows. Card colour comes from the first effect: WHEEL paper, SYSTEM black, HACK pink. `CardData.art` is the final-art override (no schema change). Cost gem is `NOTE_YELLOW`; `CELL_ACID` is reserved for focus. Hover is 12 px and ×1.12; ghost scale 0.6. HACK stock gets a diagonal hatch for greyscale.
- RULING 2026-09-29 W7: HDR 2D off, all lighting in shaders. Grade is parametric, in `content/config/city_look.tres` (`CityLookData`, schema logged). A context's dim is the total, including the `NeonCity.dim` veil. Territory is a 40% `CELL_TURF` hatch wash. Blinks are floored at 3 s; life timings live in `city_look.tres`. Reduce effects: no aircraft or drones, billboards on frame 0, searchlights still, rim flicker off. City quality tiers 0/1/2, default 2, Deck default 1.
- RULING 2026-09-29 W7 perf: +12% combat, +22% grid, +23% title over the 15% relative budget is accepted (absolute +0.2–0.8 ms GPU, worst scene 4.9 ms, §13's 60 fps target holds).
- OPEN W7 hookups: `set_map_mode` on Grid, Route and Raid; calm zones on HQ, event pages and title panels; `set_context(&"combat")` in place of `city.dim = 0.55`; sirens can hook `CityAtmosphere.state.hunted()`.
- RULING 2026-09-29 W3: operative bezel is stickered paper with `CELL_PINK` rim; enemy bezel uses the corp hue, `CorpPattern`, notched edge; `FOCUS` brackets mean target only. HP number sits under the arc on every wheel. Boss is 120% with a nameplate, phase pips, hologram and T4 `BossIntro`. One hub stamp at a time (`HubQueue`). One net-damage line under the operative's HP equals the real result. Overkill reads "(12 capped)". The NEXT plate reads "NEXT TURN 56". Wheel lettering stops growing at 1.3 and wheels keep ≥70% size at 1.6/2.0. Resolve speed works through `Engine.time_scale`.
- OPEN W3: top bar squeezed at 2.0; Polaroid caption clipped at 2.0; paper-ink variants of GAIN/HARM; `StickerButton` very large at 2.0.
- RULING 2026-09-29 W8a: logo and scrawls are path-drawn SVGs (`tools/art/w8a_svgs.py`); NEVER SLEEP subtitle shows in every locale except English. The title keeps exactly one PAPER note. Options sections are built once at the largest section's size. Pause is narrow, `MENU_SIZE` wide while Options or Codex are open. Shared APIs: `PageTransition.enter`, `open_modal`, `close_modal`, `after_modals`; `TerminalWindow.scroll_body`; `ZinePanel.scroll_content`.
- RULING 2026-09-29 W8a/W8c: LEAVE THE MODEM sits `SP_M` under the REMOVE A CARD spinner in `netrun_scene.gd`; W8c keeps this rule.
- OPEN W8a: high contrast doesn't restyle custom-drawn paper pieces (case files, receipts, badges); W9 sweep.
- RULING 2026-09-29 WF: FitScroll treats a height above 4096 px × text scale as pre-layout, waits up to 3 frames, then clamps (the crash still needs a windowed confirmation). TilePicker names wrap onto up to 2 lines. StickerButton `max_share` is opt-in (combat opts in). `combat_scene.HAND_SCALE_MAX` is 1.15. Polaroid caption never goes under 12 px. New tokens `HARM_INK` #AB2E22 and `GAIN_INK` #396739 (≥4.8:1 on paper stocks). High contrast on PAPER: paper stock kept, INK words at 7:1, 2 px opaque INK edges (`PaperInk`). Steam Deck first run sets `Settings.city_quality` to 1 (−1 means the look's default). Tracking is px per step via `UiTheme.TRACKING_PX` (Anton +1 caption–title, +2 heading/display, +3 hero; mono caps +1 caption–label, +2 title/heading, +3 display, +4 hero).
- RULING 2026-09-29 W8c: loot "hover size" is at least `HOVER_SCALE`, up to 1.4×; the picked card is stamped TAKEN (T2). Modem: two columns up to text scale 1.15, then one scrolling column; unaffordable keeps paper with a DISABLED edge, a lock and "NEED n · HAVE m". Raid interlude: asset picked once per interlude, each node row has "Deploy here". Events drop a leading "SPEAKER:". `run_end_flatline` is 2.4 s, skippable; reduce effects shows the end state at once.
- OPEN W8c merge with the ANIM-R5 netrun branch: B1 shares `EventText` and `VC_CHARS_AFTER_SHAPING`; B3 keep `RunEndStage` (`end_fate()`/`heat_reason()` into `stage.fate_label`); B5 loot hold extended by the stamp; B9 `_ahead_row` keeps node names; B11 keep `SlotPicker` and take its SOCKET_TIP words; B4 `words_typing()` must ignore `RunEndStage`'s `Typing.META` tween.
- OPEN W8c: Modem CARDS window >25% empty at 1.6/2.0; DeckView "Left click / Right click" wording and canvas overflow at 2.0 (W8b, W9).
- RULING 2026-09-29 W8b: the top bar is always one row; from text scale 1.3 tag labels, page title and VIEW LOADOUT fold into tooltips. Subtitle band is two lines above 1.0. Only the HQ gets the full DECK frame. Raid setup re-lays out at 1.3 and 1.8. Wrapping is whole-word only (`AUTOWRAP_WORD`). The raid map shows no tier pips; zoom floor 0.36 (0.2 at big text). Home hits that land together fly as one summed number.
- OPEN W8b handed to W9F: `hud.watch_drops(drops)`, `route_legend.set_opened(...)` in `cycle_target`, interlude START DEFENSE as `UiTheme.PRIMARY` with PLAY, `city_overlay.corp_id` in the grid-zoom view (all in `netrun_scene.gd`); the `crew_card.gd` WORD_SMART split; Polaroid "R0" overlap; `spinner_view` hub name clip; `dialogue.gd` `_fit_page` shrinking below caption; runtime lint scaled subtrees and modal scrims; tall empty subtitle band at 2.0.
- RULING 2026-09-29 W8d: WON landmark tips 20°, sinks 10%, two `CELL_PINK` `marker_stroke` strikes at ±48°, CORP DOWN in `GAIN`; survivors TRIUMPHANT, dead FLATLINED; city leans to 1.0 (`city_lean` signal), a new campaign resets it. LOST: hexagon cracks in `INK`, CELL BURNED in `HARM`, survivors HURT. A full-stage GlassScrim sits behind the stage. Story text folds at 70 characters; at 1.6 and 2.0 the page stacks and scrolls, never a scroll inside a scroll. Motions `campaign_end_won` / `campaign_end_lost` (T4, 2.4 s, skippable).
- RULING 2026-09-29 W8d merge: when art-pass merges into main, keep `CampaignEndStage` over main's ANIM-R5 `show_end` (81f1a5f).
- RULING 2026-09-29 W9F: 2.0 is the verified maximum; `LayoutScales` removed, layout tests run at `Settings.TEXT_SCALE_MAX`. §4.3.3: a word that can't fit makes its label grow to the longest word (no width-driven step-down). §5.2/§10.5: an empty subtitle band holds one line and grows once per screen. `flatline` is an additive `CityLookData` context with an optional `lean` key (schema change, smoke-tested); FLATLINED and campaign LOST grey the whole city. `PageTransition.settle` calls `settle_motion()`. Critique 55: button reads "UPGRADE · n CYCLES" with NEED/HAVE in `HARM` when short. Reduce motion also removes shake and makes the jack zoom a cross-fade. The raid playout and report map keys fold above 1.3. No `WORD_SMART` or `ARBITRARY` remains in `scripts/**` (tested). Pad variants exist for all mouse-worded strings, and FocusTip filters mouse words on pad. `UiTheme.track_label` is applied to Anton and mono caps.
- OPEN W9F for the designer: the SAVED toast can sit over an event's story for 2.5 s on a pad at 2.0; text drawn in `_draw` isn't linted; colour-blind stays a daltonize correction while ART_BIBLE §12 says "remap".

### 2026-09-28 Test suite: bounded waits
- RULING 2026-09-28 tests that start a motion wait on the real condition with `BoundedWait.until(tree, cond, limit)` (`tests/helpers/bounded_wait.gd`). The limit is game time plus `MIN_FRAMES` 60; `SLACK` is 2 s over the Motion table. `timed` and `frozen_frames` exist for "ends in its time" and "still under way" asserts.
- RULING 2026-09-28 `test_suite_integrity.gd::test_no_fixed_wait_gates_an_assertion`: `create_timer(`, `wait_seconds(` or `Time.get_ticks_msec/usec(` followed by an assertion, or in a helper, is flagged unless marked `# fixed-wait-ok: <reason>`. Fixed frame counts are not flagged. Review rule in `docs/TEST_SUITE.md` ("Waiting on motion").
- OPEN R2 city multi-band Heat rise reads the banner at the first frame after each pulse and could miss the first banner on a long frame (no flake seen). `motion_seconds_left()` measures wall time.
- DEFAULT evidence: 969 tests; 10 consecutive `-j 4` and 5 consecutive `-j 8` runs passed.
