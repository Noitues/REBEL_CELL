# M14 rolling audit — ART-0, HORIZONTAL (main 3fb5fcf)

Report only; nothing in the repo changed. Worktree at 3fb5fcf, imported.

## Checks run
- Fast tier, `python tools/run_tests.py --tier fast -j 2`: **763 tests, 0 failing** (89 scripts, 89 s).
- One gt.sh call: test_anim_r6_rules (full tier; it also runs tools/test_run_tests.py), test_pools, test_anim_r6_combat, test_anim_r5_city, test_save_service, test_replay, test_saves_folder: **102 passing, 0 failing**.
- `python tools/test_run_tests.py` (the `--shard` tests): 14 OK.
- Schema smoke test PASS (the `_art0` / `_art0_tier` rows all print). Content validation PASS.
- `git status` clean after the fast run, the gt run, the smoke test and validation. No `saves/` folder appeared (tests write no replays).
- Throwaway scripts in my scratchpad (not the repo):
  - `replay_check.gd`: 15 netrun fights (5 seeds x {plain, with a rewind, saved and resumed mid-fight}), recorded with `CombatReplay.record` the way CombatEngine does, round-tripped through JSON and rebuilt with the shipped config and registry. **15/15 match the recorded hash.** Seeded replays still match.
  - `tier_check.gd`: each ui_motion entry against its tier's limits (results under E).
- No windowed capture: no finding needed visual evidence.

---

## E / E2 — tokens, VFX tiers, reduce_effects global

**P2-E1. Shakes are not held to their tier: three entries go past T2's 2 px, and only one is on the carry-over.**
- `Motion.shake` (`scripts/ui/kit/motion.gd:264-283`) shakes by `amplitude(id)` and never clamps to the tier. `Fx.shake_px` (`scripts/autoload/fx.gd:538-541`) does clamp, but nothing calls it (grep: no callers). So the DECISIONS E line "Fx.shake_px and the hit-stop are held to tier" covers no real shake.
- Over the limit (`content/config/ui_motion.tres`):
  - `hit_shake`: 3 px at T2 (line ~1598). This one is on the carry-over to Group 2.
  - `heat_letters_shake`: **3 px at T2** (line 390; called from `heat_poster.gd:334`). Not on the carry-over.
  - `precision_weak`: **4 px at T2** (lines 151-157; called from `combat_scene.gd:1506`). Not on the carry-over.
- Expected (ART_BIBLE v2 §5.3 / VfxTier table): T2 shakes at most 2 px.
- Fix: clamp inside `Motion.shake` with `VfxTier.clamp_shake(VfxTier.of(id), amplitude(id))`, or fix the amplitudes or tiers. Add a test that every entry used by `Motion.shake` fits its tier. Add the two extra entries to the CARRY_OVER row if they go to Group 2.

**P2-E2. Tiers are written on every entry, but 35 of 207 entries run longer than their tier allows, and nothing tests it.**
- Evidence (`tier_check.gd`, duration against `VfxTier.MAX_SECONDS`):
  - T1 (max 0.25 s): `count_up` 0.6, `drip_grow` 0.6, `send_it_ready` 0.6, `ram_spend_float` / `ram_refill_float` 0.8, `city_bake_fade` 0.8, `pointer_orbit` 1.2, `saved_stamp` 1.2, `asset_drop_wait` 1.5, `toast_note_hold` 3.5, and 17 more.
  - T2 (max 0.6 s): `resolve_sequence` 2.0, `forecast_change` 1.4, `buy_fly` 0.7, `loot_pick` 0.7.
  - T3 (max 1.2 s): `combat_end_hold` 1.4.
  - T4 (max 2.5 s): `jack_arrival_wait` 4.0.
- `test_the_fx_layers_effects_fit_their_tier` (`tests/unit/test_vfx_tiers.gd:61`) checks only 9 hand-picked ids. `buy_fly` is one of the bible's own T2 examples and still runs over.
- Many of the 35 are holds, waits or pulses, not effects. So either the tier is wrong for them, or they need a "hold/loop, not an effect" mark.
- Fix: retier the effects, and mark holds and loops (a flag, or T0 for loops). Then add a test that every one-shot entry fits its tier.

**P3-E3. The shader rule is only checked under the top level of `res://shaders`.**
- `test_vfx_tiers.gd:276-283` lists `res://shaders/*.gdshader` only. `assets/glyphs/glyph_sdf.gdshader` (ART-1 1C) and `tools/visual_qa/cvd_filter.gdshader` are not checked. Both are static today: I checked every shader for `TIME`, and every animated line goes through `rc_time` / `rc_live`.
- Fix: scan every `*.gdshader` under the project except `addons/`.

**Confirmed OK:**
- `project.godot` `[shader_globals] reduce_effects` exists, and `rc_common` declares the global.
- No script keeps a per-material copy; ShaderReduce is gone.
- Every new motion id since 0d628e1 is in REQUIRED_IDS and in a motion-lab demo: `modal_in`, `modal_out`, `focus_scale`, `button_refused`, `wheel_burst_*`, `precision_null_static`, `precision_weak`, `mainframe_*`.
- Carry-over row "hit_shake 3 px" is confirmed, still present.

## B / B2 / B3 — names pass, saves folder

**P2-B1. The Heat glitch is a working Options toggle that does nothing, and the glitch itself has no owner.**
- The toggle: `scripts/ui/kit/settings_panel.gd:103` ("Heat glitch (the screen distorts as Heat rises…)"), and `Settings.heat_glitch` is saved.
- No code reads it: grep `heat_glitch` in `scripts/` finds only settings.gd and settings_panel.gd.
- DECISIONS (names part 2, D11) says "the glitch itself comes in ART-3 / ART-5". But MILESTONES and the ART-3 / ART-5 briefs never mention it; only ART-4 lists the Options row. The ruling is "names for M14", item 7.
- Fix: put the glitch effect on an acceptance line (ART-3 or ART-5) and in CARRY_OVER. Until it lands, hide the row or label it.

**P3-B2. The names sweep's `"disabled":` pattern flags UI-control state keys, and later code dodges it.**
- The pattern is in `_raid_identifier` (`tests/unit/test_names_pass.gd:124-126`).
- Workarounds it caused:
  - `scripts/ui/kit/ui_theme.gd:405` writes `(&"disabled"):`.
  - `tools/design_lab/type_chrome_sheet.gd:13` writes `("disabled"):`.
  - `tests/unit/test_w9_accessibility_settings.gd:220` writes `StringName("disabled")`.
  - ART-1 1A's DECISIONS entry says so itself.
- Fix: limit the dict-key check to the raid files or the raid outcome dictionaries, or match `Condition.DISABLED` and raid outcome keys only.

**P3-B3. BREACHED now means two different things on screen.**
- Ruling 6.2 reserves BREACHED for the home server falling (`raid_verdict.gd:12`). The Hub Breach log line still reads "%s Hub BREACHED for %d turn(s)" (`scripts/core/effect_interpreter.gd:495`).
- This line predates ART-0, but the new raid word now collides with it.
- Fix: give the Hub Breach log its own word (e.g. "Hub breached" in lower case, or "Hub offline"), or log a question for the designer.

**P3-B4. Saves folder hardening.**
- (a) Every finished fight on a source run writes a replay (`combat_engine.gd:66` → `save_service.gd` `record_replay`). Nothing prunes them, so storyboard, demo and harness runs pile files up in `saves/replays/`. Add a cap (config) or prune the oldest.
- (b) `export_presets.cfg` `exclude_filter` relies on `saves/.gdignore` alone. Add `saves/*` as a second guard.
- (c) `tests/integration/test_saves_folder.gd` replays only a standalone fight. My scratch check shows netrun, rewind and resume replays match. Port it into the test so it stays true.

**P3-B5. DECISIONS still says things that are no longer true.**
- The open question "SANDBOX / TROJAN / NULL … the game still shows SHIELD, DEPLOY and MISS. Default: unchanged until you say" (`docs/DECISIONS.md:6252-6254`) is resolved by B3 but not struck.
- The "names pass, part 2" entry's "the enum keeps SHIELD / DEPLOY / MISS (question below)" and its D11 "no band changes" bullet are not marked superseded by part 3.
- Fix: strike or annotate, never delete.

**Confirmed OK:**
- Grep finds no `modem` or `priority routing` anywhere under scripts, scenes, tests, tools, content, assets/text or project.godot.
- No old raid word in `strings.csv` or in content strings.
- No old slice words in code (`SLICE_DEPLOY` / `SLICE_MISS` appear only in the sweep's own regex).
- GDD uses the old words only as "(was …)" history.
- The allow-lists are justified, each matching one real string:
  - "Seized goods": `ev_mer_customs_warehouse`.
  - "reads CRITICAL": `ev_mer_cold_chain`.
  - The three Tariff flavour strings.
  - "Miss a payment": the Solace description.
- The new words all have strings.csv keys: SBOX, TRJN, AIRMAIL, GROWTH, CELL HOLDS, BREACHED, purge, MAINFRAME SHOP, LEAVE MAINFRAME.
- Saves:
  - A source run saves under `res://saves`, an export under `user://saves`; the `.gdignore` is written under the source folder.
  - Replays are off in GUT (`replays_enabled` false); a `-s` tool run gives `is_source_run=true`, `replays_enabled=true`, `save_dir=res://saves`.
  - Version 1 and too-new files are refused through `load_dict` with no crash (tested).
  - git status is clean after the fast run.

## C — accessibility settings

**P3-C1. A literal colour slipped past the lint.** `HighContrast.BG := Color.BLACK` (`scripts/ui/kit/high_contrast.gd:23`) is a colour outside Palette, and the static lint misses it (see D2). Fix: add a Palette token such as `HC_BG`.

**Confirmed OK:**
- All seven new keys are in `to_dict` / `from_dict` with defaults equal to main (`settings.gd:648-692`): `colorblind_mode` off, `high_contrast` false, `reduce_motion` false, `resolve_speed` x1, `pad_glyph_set` auto, `city_quality` -1, `heat_glitch` false.
- Unknown values fall back to the default (`_pick`).
- Steam Deck defaults apply only on a first run on a detected Deck; test runs never probe the machine.
- `snapshot()` carries every new key plus `device_probe_override`. The suite guard also restores `Engine.time_scale`.
- `test_w9_accessibility_settings.gd` takes a snapshot in `before_each` and restores it in `after_each`, and checks the snapshot covers the new keys.
- The panel's choice words are `# TR` constants with strings.csv keys.

## D — visual QA harness, static lint

**P3-D1. The lint baseline has slack: a count that went down is only printed, never enforced.**
- The fast run printed "ui_theme.gd [color] 12 < baseline 24". ART-1 1A halved the file, but `tools/visual_qa/lint_baseline.json` still allows 24, so 12 literals could come back silently.
- 1A's merge did add new `Color(0, 0, 0, 0)` literals in `ui_theme.gd` (`Palette.AUTO` exists). They are absorbed by that slack.
- Fix: lower the baseline now (`update_lint_baseline.py`), and make `test_no_file_gains_literal_colours_or_font_sizes` fail on a count that went down.

**P3-D2. The colour rule does not count named `Color.*` constants.**
- 12 uses under `scripts/ui`: 10 `Color.WHITE` (mostly neutral modulate), 1 `Color.TRANSPARENT`, 1 `Color.BLACK` (C1 above).
- Fix: count `Color.<NAME>` except WHITE used as a modulate, or allow-list per line.

**Static lint baseline answer:** no file's count went up since ART-0 (`test_visual_lint_static` green). The only baseline changes since 0d628e1 are D's seed (f20ba95) and the `modem_sign` → `mainframe_sign` row rename (9612e8c). ART-0's new kit files have no literal `Color(...)`; their px sizes are named constants (`StyleBoxBrackets.THICKNESS` 3 / `OFFSET` 7 and so on).

## F — kit behaviour

No finding.
- MotionSkip still owns the one-press skip: `test_anim_r6_rules` is green, with `kit_state`, `refusal_mark` and `ui_focus` in NOT_SKIPPABLE and STYLE_GUIDE 5.5.
- `PageTransition.open_modal` / `close_modal` cut at once where motion doesn't play (headless, reduce effects) and never wait.
- `test_pad_reachability` and the confirm-on-scrim pad test are green.
- Carry-over "1.03 focus scale on full-width Options rows" → ART-10 stands.

## Orchestrator / process

**P3-O1. A merge left a broken line in the open questions.** `docs/DECISIONS.md:6218` is a one-line, cut-off duplicate of the D11 question ("…the plan's "old FLAGGED →"); the full, struck version is at 6242. Remove the stray line.

**P3-O2. `--shard` works.**
- `parse_shard` / `pick_shard` reuse the local longest-first balance with deterministic ties.
- The shards are disjoint and complete (tested).
- `--tier` defaults to `all`, so the CI shards cover the whole suite.
- `ci.yml` SHARDS 6 matches the matrix.
- One small gap: `tools/test_run_tests.py` runs only inside `test_anim_r6_rules` (full tier). Run it in the fast-checks CI job too.

**P3-O3. Godot imports `docs/timeline` images.** It has no `.gdignore`: 59 `.import` files, including the six `17_art0` frames ART-0 added. Add `docs/timeline/.gdignore`, as `docs/art_reference` and `docs/concepts` have.

**Carry-over confirmations:**
- E: `hit_shake` 3 px is still there. Two more shakes need adding to that row (E1).
- E: MSDF on and the signal-11 crash were closed by ART-1 1A, per its entry.
- E: CLASS_ACCENTS were closed by 1A.
- B3: seeded replays were re-checked here on netrun fights (15/15 match); the full sweep stays for after ART-12.

---

**Verdict: NOT CLEAN** — no P1; 3 P2 (E1 shakes over tier with no clamp, E2 entries over their tier with no test, B1 Heat glitch toggle with no effect or owner); 12 P3.
