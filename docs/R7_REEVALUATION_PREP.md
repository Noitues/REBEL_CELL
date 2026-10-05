# ANIM-R7 re-evaluation: preparation sheet

**Purpose.** Ruling 1 of "Designer rulings: art reintegration, pause point 0" (`docs/DECISIONS.md`, 2026-10-05)
paused ANIM-R7: after M14 every R7 finding is re-checked against the ported screens, and the ones still valid
are fixed (batches A–E, re-cut). Ruling 9 of the same entry sends the overkill wording ("→ 1 LEFT") to the same
re-evaluation. This sheet prepares that review: for every finding in
`docs/handoff/anim_r7/R7_FIX_BATCHES.md` it names the M14 area that rewrites the view, says whether the finding
is likely obsolete, likely still valid, or needs checking, and gives the reason in one line.
It is a forecast from the briefs, not a re-audit: nothing here has been run against the ported screens, and the
designer decides what is dropped.

**M14 areas (from `docs/handoff/art_1..art_4/ART_*_BATCH.md`).**

| Area | What it rewrites |
|---|---|
| **1A** | Palette v2, typography, theme types (Group 1, ART-1) |
| **1B** | The material kit: CRT panel, vinyl sticker, grease pencil, light spill, holo, corp paper, binary bits |
| **1C** | Glyph atlas and id-to-glyph table |
| **1D** | The unified-city render spike (feeds Group 3 wave 2) |
| **2A** | Wheel stack: `wheel_view.gd`, `scripts/ui/wheel/**` (D4 frame, slices, states, hubs, inner ring, corp skins, landings) |
| **2B** | Wheel attachments and the arena: satellites and drones, firmware socket, Daemon rack, card-play preview, combat backdrop |
| **2C** | Cards and FX: sticker cards, binary damage, the locked effect set, Heat on the combat screen; `combat_fx_layer.gd`, card views |
| **2D** | HUD v4: `combat_scene.gd` HUD and layout, result chips (D15), `ram_bar.gd`, top bar, toasts, tooltips, buttons, modal and dialog kit |
| **3A** | Raid presentation (2D parts): panels, node status, pencil rules, drag model, threat icons, raid report; `hq_scene.gd` raid parts, `kit/raid_*`, `city_map_overlay.gd` raid layer |
| **3B** | Netrun presentation (2D parts): route, node states, dossier, jack-in transition, node backdrops |
| **Group 3 wave 2** | ART-5 unified city model and motion; raid, netrun and HQ-run map views on it; ART-8 compounds (briefs not written yet; plan §4.2 ART-5..8) |
| **4A** | MAINFRAME shop, rewards, events (`netrun_scene.gd` shop, loot, event parts, `mainframe_sign.gd`) |
| **4B** | Dialogue and portraits (`dialogue.gd`, `subtitle_strip.gd`) |
| **4C** | Menus, title, settings look, pause, codex, stats, achievements, slots, picker, HQ screen look (`hq_scene.gd`) |
| **4D** | Campaign lost, dossier, run end |
| **ART-0 (done)** | Docs, names pass, accessibility settings, visual QA harness and lint (D), tokens and VFX tiers (E), kit behaviour (F) |

**Verdict key.** *Obsolete* = the view the finding describes is replaced, so the finding goes away with it
(re-check at most for a regression of the same kind). *Valid* = the cause is behaviour, structure or rules text,
which a restyle does not touch. *Check* = depends on how the port lands; run the original repro on the new view.
Names in the R7 text that changed in ART-0: "Modem" is now **Mainframe**; "Seized / Disabled" are TAKEN / DOWN.
File and line references below are R7's and will have moved.

## A — combat

| # | Finding (short) | M14 area | Verdict | Reason |
|---|---|---|---|---|
| A1 | P1: tutorial step 1/7 never shows in a real netrun fight (opening `turn_start` advances an `until: ""` step) | 2D (`combat_scene.gd`), `tutorial_overlay` has no named owner | Valid | A step-advance rule in the tutorial logic; no M14 brief changes it. |
| A2 | P1: at 1.6 the OPERATIVE subtitle dock overlaps the tutorial box; Title → Tutorial runs off the right edge; RESPIN note under Next/Skip | 2D (right-column layout), 4B (subtitle dock), 4C (title and Tutorial entry) | Check | Layout is rebuilt in 2D and the dock in 4B; the overlap may vanish or move. Re-run at 1.0 / 1.3 / 1.6. |
| A3 | P2: tutorial pages cut mid-sentence; instruction after the step advances; CARDS scroll bar at 1.6; Next alpha pulse | 2D (dialog kit), no brief owns `tutorial_overlay` | Valid | Page splitting and copy are content and logic; the 2D restyle does not paginate. Pulse styling may change. |
| A4 | P2: typing subtitles eat the fight's hotkeys (`Dialogue._input` → MotionSkip.handle) | 4B (`dialogue.gd`), ART-0 F / D (MotionSkip rule) | Valid | Input routing, not look; 4B must keep ANIM typing behaviour. Test before and after the 4B merge. |
| A5 | P2: "HITS BILLING DAEMON 6 → 1 LEFT" beside VICTORY reads as enemy HP; "1 LEFT" also means Armory copies | 2D (D15 result chips, GDD 2.10) | Obsolete (designer decides) | Ruling 9: the HP result chip may replace that line; HUD v4 removes the forecast text. Confirm the new chip wording is unambiguous. |
| A6 | P2: "collections drone" named in chips but only an unlabelled rim badge | 2B (collapsed drones, hover bloom), 2D (chips) | Check | Drones are redrawn as collapsed badges with a hover bloom; whether the chip names the drone is a new question on the new view. |
| A7 | P2: real plain turn 3.08 / 2.54 / 1.70 s vs the six synthetic beats in the R6 test | 2C (FX timing), 2D (beats) | Check | Beat schedule changes with new FX; measure a real fight after the port, then retune or correct STYLE 5.2. |
| A8 | P2: top-bar HP lags VICTORY (`_replay_start_hp` not cleared in `_land_outcome`) | 2D (top bar, HP chips) | Check | Same state bug could survive in the new top bar; depends on whether 2D keeps `_land_outcome`. |
| A9 | P2: `beat_timing` paces on hp_drain / hit_line / hit_absorb / enemy_break / card_discard / enemy_turn_spin without asking if they are on | 2C, 2D (`combat_scene.gd` beats) | Valid | Pacing logic over the motion switches; restyle keeps the switches ("art restyles motion, never drops an entry"). |
| A10 | P2: combat view writes profile stats (`record_seen`, `record_perfect`) | 2D (`combat_scene.gd`) | Valid | Structural (Signal Up / Call Down); no brief moves it. |
| A11 | AWAITING_FIX views still animating while switched off: dead_wheel_fade, hp_lag (wheel_view); heal_number, hit_absorb, number_float (combat_scene) | 2A (wheel_view), 2C (heal, block, damage FX), 2D | Check | The views are rebuilt; each id may be rewritten and fixed in passing, or left. Re-check each id against its new code. |
| A12a | P3: portrait snaps for heals / no-number HP changes; PERFECT bark beside DEFEAT; DISPATCH line before JACK OUT; bark pages one line with "…" | 4B (dialogue, portraits), 2D | Check | Portrait and bark views are rewritten; the cause may be in event timing (valid) or in the old view (obsolete). |
| A12b | P3: DEFEAT 0/60 HP stays green; top bar drops HP/CYCLES while DEFEAT shows; WAS line truncated; Heat jumps with no cause shown | 2D (top bar, HUD, result chips) | Obsolete | HUD and top bar are rebuilt on the v2 kit. Re-check "Heat jumps with no cause" in the new Heat read. |
| A12c | P3: enemy hits you in the SEND IT that kills it, with no explanation | 2D (chips and tooltip breakdown) | Check | The result chip's breakdown tooltip may explain it; the rule itself is unchanged. |
| A12d | P3: enemy RAM drain "RAM -1" names no source; RAM bar "(-3)" mixes cost and drain | 2D (`ram_bar.gd`, `−N RAM` chip) | Check | `ram_bar.gd` is restyled and the chip carries other losses; the source naming is a content question. |
| A12e | P3: `replay_press` duplicates handle; typed WheelView across 2 frames; hand-built signs → `TextDb.signed` | 2A, 2D | Valid | Code hygiene in files that are rewritten; the sites move but the pattern can recur. Re-grep. |
| A12f | P3: tutorial note stays up on VICTORY/DEFEAT | 2D (no owner for `tutorial_overlay`) | Valid | Tutorial lifecycle logic; unchanged by the restyle. |

## B — netrun screens

| # | Finding (short) | M14 area | Verdict | Reason |
|---|---|---|---|---|
| B1 | P2: route shows the silhouette after mid-run Heat changes (1.5–3.6 s lag; prebake the route) | 3B (route), Group 3 wave 2 (route on the unified city) | Check | The route is redrawn on the city; whether the lag survives depends on the new bake. Measure in real time. |
| B2 | P2: interlude playout's Continue gets no focus when the raid finishes | 3A (raid views, playout) | Valid | Focus handling on an event, not look; 3A restyles the playout panel but the finish hook likely stays. |
| B3 | P2: Mainframe (was Modem) focus tips cover buttons (LEAVE at 1.6; BUY / SHRED notes, SLICES tags at 1.3) | 4A (shop layout v5) | Obsolete | The shop layout and its tags are rebuilt. Re-run the focus-tip sweep at 1.3 / 1.6 / 2.0 once. |
| B4 | P2: Mainframe SLICES "BUY 100" stay yellow when unaffordable | 4A (price tags print red when unaffordable, bible 4.10) | Obsolete | Affordability colouring is part of the new shop; the shop sweep checks it. |
| B5 | P2: double translation (ToastNote auto-translate with `tr()` callers; InspectPopup tooltips; `DripButton.new(tr())`) | 2D (toast, tooltip, button kit restyle), 4C | Check | Kit classes are restyled; the double `tr()` is in callers and may remain. Re-grep the listed patterns. |
| B6 | P2: Codex fully untranslated (`codex.gd`, ~25 call sites) | 4C (codex on the v2 kit) | Valid | A restyle does not translate strings; fix once the codex is ported (avoid fixing it twice). |
| B7 | P2: netrun demos `_frames_in_tree` still await then check | 3B (jack-in transition, demos) | Valid | Lab-demo plumbing; 3B adds demos but the helper stays. |
| B8a | P3: event choice stamp is a wordless snapshot | 4A (events: CHOSEN stamp, bible 4.11) | Obsolete | Events get a CHOSEN stamp by design. Check it reads without colour. |
| B8b | P3: "[2] Fight (same road as choice 1)" / "then: Shop" confuse | 4A (event choice outcome chips) | Check | Outcome chips change; the wording lives in event content and may persist. |
| B8c | P3: event body truncated at 1.6 in the storyboard; "NEED 112 HAVE 101" below the CYCLES tag | 4A (event Terminal, shop tags) | Obsolete | Both screens are rebuilt; re-run the 1.6 storyboard. |
| B8d | P3: deck viewer first row overlaps "Left click: select…" | No brief names the deck viewer (nearest: 2D modal kit, 4C) | Check | Unowned view; it may be restyled only incidentally. Re-run the repro. |
| B8e | P3: route page has no focus on arrival; `netrun_map_view.gd` hidden view draws English at fixed sizes | 3B (route, D13 hidden nodes) | Check | The route view is reworked, including hidden-node rules; the focus and the stray view may or may not survive. |

## C — city, raid, HQ, bake

| # | Finding (short) | M14 area | Verdict | Reason |
|---|---|---|---|---|
| C1 | P2: a Heat threshold crossed by a flatline plays only in the fight's small poster; HQ shows none | 2C (Heat on combat, five bands), 4C (HQ), Group 3 wave 2 (map Heat) | Obsolete | Heat is shown as the city reacting and a dossier stamp, not as a poster. Re-check that HQ shows a crossing in the new language. |
| C2 | P2: after a won run the cleared district's tint is a bright blob behind the run-end window; CLEARED stamp cut at the left edge | Group 3 wave 2 (unified city), 4D (run end) | Obsolete | District tint and stamps belong to the old neon city; the run-end window is restyled in 4D. |
| C3 | P2 (1.3): dead operative's FLATLINED stamp overlaps "// BREAKER // RANK 0" | 4C (HQ crew roster), 4D (FLATLINED restyle) | Obsolete | Crew card and stamp are rebuilt. |
| C4 | P2: raid 2x/4x shortens reading holds (global `Motion.speed`); one never-shorter helper | 3A (must-survive: reading holds never shortened), ART-0 F / D | Check | 3A's acceptance covers it; a helper may already exist. Confirm before re-cutting. |
| C5 | P2: switching a hold off does not match the docs (`fx.gd`, `heat_poster.gd`); align code, STYLE 5.5, HOLDS | ART-0 E (VFX tiers), 2C | Check | `heat_poster` goes away; the rule for `fx.gd` and the doc may still be open. |
| C6 | P2: HQ dev flags write state outside DemoSetup; HQ actions call CampaignRules from the view | 4C (`hq_scene.gd` look) | Valid | Structural; 4C restyles the look and keeps every action. |
| C7 | P2: raw ids and rules English in HQ toasts and tooltips; Raid feed Heat icon at CORE and icons in lines | 4C (HQ), 3A (raid feed), batch E | Valid | Text comes from rules (batch E); the feed icons may be redone in 3A. |
| C8a | AWAITING_FIX: beacon_blink, city_sign_pick (neon_city) | Group 3 wave 2 (ART-5 unified city), 1D | Obsolete | `neon_city` is replaced by the unified city model. |
| C8b | AWAITING_FIX: asset_drop_grow, route_target_pulse, select_ring_pulse (city_map_overlay) | 3A, 3B (overlay layers), Group 3 wave 2 | Check | The overlay is reworked layer by layer; each pulse may be rewritten with its layer. |
| C8c | AWAITING_FIX: raid_outcome_stagger (raid_fx_layer) | 3A (state marks, TAKEN / DOWN, report) | Check | The raid outcome sequence is redrawn as pencil marks; the stagger may be replaced. |
| C9a | P3: `map_legend.gd` strings lack `# TR`; "MAP LEGEND" drawn raw; threat token missing from MAP LEGEND | 2D (map HUD), 3A, Group 3 wave 2 | Check | The legend follows the new node and marker set (bible 4.5). |
| C9b | P3: views parse rules English (`raid_playout_panel`, `netrun_scene`, `combat_scene`) | 3A, 2D, batch E | Valid | Structural, paired with E's structured event fields. |
| C9c | P3: sky fallback keeps `drawn_texture` up to 48 MB | 1D (city spike), Group 3 wave 2 | Obsolete | The sky and city render path is replaced. |
| C9d | P3: "IF THE RAID RUNS NOW" circle fades half under RAID FEED | 3A (panels, raid layout) | Obsolete | Raid panels are rebuilt as CRT / paper / holo; the pencil rule says no UI covers pencil. |
| C9e | P3: heat banner "(25-)" reads as minus and overlaps NOTICED | 2C, 4C (Heat shown in five bands) | Obsolete | The banner and bands are replaced. |
| C9f | P3: campaign-end profile jargon ("Something opens at ICE 10 everywhere (0/4)", "Best ICE: … −") | 4D (campaign end), 4C (stats) | Valid | Wording lives in strings and profile data; a restyle keeps it. |
| C9g | P3: Grid pad first focus "< PREV SITE", JACK IN three Downs away; loadout viewer shows "Close [Esc]" under the pad | Group 3 wave 2 (Grid), 4C, ART-0 F (PadGlyph, `UiTip.for_input`) | Check | ART-0 F added pad glyphs; the Grid focus order is rebuilt. |
| C9h | P3: feed header "Raid over" while the last step still plays; a threat withdrawing at the verdict unverified | 3A (raid feed, verdict) | Check | The feed is redrawn; the sequencing bug is in playout timing. |

## D — motion rules, kit, tests, docs, runner

| # | Finding (short) | M14 area | Verdict | Reason |
|---|---|---|---|---|
| D1 | P2: inline motion numbers remain; the R6 scan only checks EASE_/TRANS_; `dialogue.gd` reading hold into the table | ART-0 E (tokens, VFX tiers) and D (static lint), 4B | Check | ART-0 added token lints; new M14 views add more inline numbers, so re-run the scan after the port. |
| D2 | P2: the switch check is per id, not per reader; clock-driven animators (`crt_hum`, `drag_ghost`, `raid_fx_layer`, `toast_note`) escape it | ART-0 D, 1B (new animators), 2C | Valid | Test-design gap; M14 adds more clock-driven animators, so it grows. |
| D3 | P2: runner never cleans up (`rebel_cell_tests_*` in %TEMP%, a 188 MB log) | None (`tools/run_tests.py`) | Valid | No M14 brief touches the runner; check `docs/TEST_SUITE.md` for later changes. |
| D4 | The MotionSkip rule gap behind A4; the never-shorter hold helper behind C4 | ART-0 F (kit behaviour), 3A | Check | ART-0 F landed kit behaviour; confirm the two gaps remain before re-cutting. |
| D5a | P3: suite guard gaps; frame_waits gaps; stale manifest times and TEST_SUITE numbers | None | Valid | Test infrastructure; M14 adds scripts, so the manifest times go stale again. Run `--update-times` last. |
| D5b | P3: doc drift (`motion_skip.gd`, `motion.gd`, motion README R6 rows, resolve_side_gap, recapture R6 retune strips, ANIMATION_HANDOFF §3) | 2C, 3A, 3B (motion restyled) | Obsolete in part | Strips and R6 rows are recaptured by the art captures; the code comments stay valid. |
| D5c | P3: lab bare awaits and interleaving `_play_scene` coroutines, MotionDemo Waiter leak; `--quit-after` leaks 2 ObjectDB instances | 2C, 3B (more lab demos) | Valid | Lab and engine plumbing; M14 adds demos on the same helpers. |

## E — rules text keys

| # | Finding (short) | M14 area | Verdict | Reason |
|---|---|---|---|---|
| E1 | H P2-2 / N P2-5: rules write English sentences and `%+d` in core (~90 sites); emit `text_key` + args and structured fields; `deploy_failed` / `undock_failed` never reach `_report` | None rewrites it; touches every group's text | Valid | Core text is outside every M14 brief. Do it after M14 so the new strings (names pass, new chips, new panels) are converted once. Log it in DECISIONS and update the schema smoke check if a payload schema changes. |

## Reading the totals

- **Likely obsolete** (replaced views): A5, A12b, B3, B4, B8a, B8c, C1, C2, C3, C8a, C9c, C9d, C9e, part of D5b.
- **Likely still valid** (behaviour, structure, rules text, test infrastructure): A1, A3, A4, A9, A10, A12e, A12f,
  B2, B6, B7, C6, C7, C9b, C9f, D2, D3, D5a, D5c, E1.
- **Needs checking on the ported screens:** A2, A6, A7, A8, A11, A12a, A12c, A12d, B1, B5, B8b, B8d, B8e, C4,
  C5, C8b, C8c, C9a, C9g, C9h, D1, D4.
- **Unowned views** (no M14 brief names them, so they get only incidental restyling): `tutorial_overlay`, the deck
  viewer, `map_legend` (partly), the netrun-run end window outside 4D. Their findings stay open unless a
  later brief picks them up.
- **Order of the re-cut (for the designer's discussion):** re-run the "Check" repros first, because they
  decide which of A–C remain; then batch E; then D.
