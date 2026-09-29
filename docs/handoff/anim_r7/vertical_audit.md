# ANIM-R7 vertical audit (main 7b5c0f8)

Report only. A scripted player (SceneTree -s boot + player node, kept outside the repo) ran
through `tools/run_windowed.py` at 1280x720 with a fresh APPDATA per run, from the title,
with real input (key, pad and mouse events via Input.parse_input_event, clicks on real
buttons), logging MotionSkip.running(), focus, HUD values and state per step. Most runs
`--fixed-fps 30`; city-bake timings re-measured in real time. Covered 1.0 / 1.3 / 1.6,
reduce effects, pad-only (HQ → Grid → JACK IN → route → fight → loot → event → Modem → B).

**Drag and drop:** synthetic drags start a Godot drag, but the drop is decided at the real OS
pointer (DropLayer._held_at / combat use get_global_mouse_position), so a release always
cancels. Verified via DropLayer.begin_drag + release_at / drop_on and the click-carry +
accept/pad A path. Combat card drag can't be driven; click-aim and pad-aim work.

Dev shortcuts only where noted: DemoSetup.set_heat(20) then a real flatline to cross 25;
lowered enemy HP to win / reach boss phases; --demo-shop for shred; --demo-playout;
--demo-campaign-end=won|lost.

## R6 confirmed in the real game
- Combat: A1 key during the fight-ending replay only skips it. Forecast = applied every turn
  of a 14-turn fight. Chips name their source; clamps "HITS YOU 6 → 1 LEFT"; no fractions.
  Top bar HP holds the turn-start HP during the replay. VICTORY held; LOOT swaps in. Lost fight
  waits for JACK OUT (30 s+). Tags clear of nudge arrows at 1.6. Next pulses. A card click
  during the replay only ends it. Boss phases (Renewal Engine) stamp PHASE 2/3; drones appear.
- Netrun: invisible loot sticker click lands the deal, picks nothing; loot sources FIGHT WON /
  RACK BREACHED / ELITE DOWN; flatline run end city on first frame (real time); titles NETRUN
  // FLATLINED / JACK OUT; jack destination large with T1 icon; Modem glyphs; refusal "NEED
  112 HAVE 101"; buy by click and by drag release; shred (deck 10→9, 120→70, price 50→75).
- City/raid/HQ: new-campaign HQ and first Grid covered on first frame; YOUR NODES fills its
  window; finished playout controls off on 1x, Continue focused at HQ; 2x click and a focus
  move keep the step, a stray key ends it; "HOME -10 · HOLDS" HOLDS in acid; RAIDS drops within
  5 frames of the verdict; Heat banner/note static under reduce effects; Polaroid captions
  whole at 1.3/1.6; claim cross-stamp; campaign end won/lost at 1.0/1.6.
- HQ drops onto JACK IN (click-carry + accept, and drag release) only SELECT. Boost drag onto
  the queue works.

## Combat
- **P1 (1.6) Tutorial box unreadable.** Netrun fight: the OPERATIVE subtitle dock draws over the
  tutorial box (only "plus your class hook), 1 tick off for" shows). Title Tutorial: box and dock
  run off the right edge ("THE WHEEL (1/", "wheel do", "Skip tutor" cut); the RESPIN refusal
  note is covered by the tutorial's Next/Skip row. Fine at 1.0; A16 "box fits" fails at 1.6.
  Fix: lay out the right column (dock + tutorial) from the scaled column width and the dock's
  real height; toasts keep off the tutorial.
- **P2 Typing subtitles eat the fight's hotkeys.** Space (SEND IT) while a bark types only
  finishes the typing (T7 at 1.0; T8, T12, T14 at 1.6); Tutorial: E (nudge) eaten too. Cause:
  `Dialogue._input` → MotionSkip.handle (`dialogue.gd:494-502`); `Settings.apply_controller_bindings`
  removes Space from ui_accept (`settings.gd:311-316`) so works_ui is false → CONSUME. Breaches
  STYLE 5.1 ANIM-R3 ("subtitles consume only presses aimed at them"). Fix: bound game actions
  (end_turn, nudge_*, respin, rewind, card_N, cycle_target, toggle_*) count as works_ui, or
  ambient typing PASSes every press that isn't a click on the dock. Test: bark typing, then
  Space/Q/X → the action happens and the typing completes.
- **P2 First run's tutorial skips step 1/7 "THE WHEEL"** (same as naive P1-1). Title → Tutorial
  starts at 1/7 correctly. Cause `combat_scene.gd:152-157` + `tutorial_overlay.gd:242-250`.
- **P2 The plain turn is not ~2.3 s in the game.** First fight (Billing Daemon), motion_seconds_left
  right after SEND IT: one hit each way 3.08 s; one blocked hit 2.54 s; both defend 1.70 s.
  `test_a_plain_turn_replays_in_about_two_and_a_half_seconds` (`test_anim_r6_combat.gd:787`)
  uses six synthetic beats and misses the real turn's extra beats (enemy RAM drain, hand
  discard/deal). Fix: measure a real fight's schedule in the test; retune or document.
- **P3** Right column at 1.0 with the tutorial up: the bark pages one line with "…"; the
  tutorial's page 2 holds one word ("it.") in a column-tall box.
- **P3** An enemy RAM drain shows as bare "RAM -1" on the player's tag (no source, unlike A4's
  other losses); the RAM bar's "(-3)" mixes card cost and drain.
- **P3** Barks at DEFEAT: a PERFECT bark beside the DEFEAT stamp; at 1.3 under reduce effects
  the run end's DISPATCH line shows in the fight before JACK OUT.
- **P3** The top bar drops HP/CYCLES and shows campaign tags (Heat, Schematics) while the lost
  fight still shows DEFEAT / JACK OUT.
- **P3** The hovered tag's WAS line truncates ("WAS DEFEND · perfect aim · +1…").

## Netrun screens
- **P2 Route shows the silhouette after Heat changes mid-run (real time):** after an event that
  adds Heat (+5) ~1.5-2 s; after the interlude playout (Heat 31→36) ~3.6 s. R5 measured first-frame
  coverage: regression. Likely `netrun_scene.gd:1859-1867` sets background.corp_creep from the
  new Heat when the playout finishes (and events change Heat); the route prebake is for the
  old look. Fix: prebake the route under the post-step Heat (as prebake_run_end does).
- **P2 Interlude playout: Continue gets no focus when the raid finishes** (focus <none> at 1.6);
  HQ does (`hq_scene.gd:3242`), netrun's finished handler (`netrun_scene.gd:1859`) doesn't.
  Fix: cont.grab_focus().
- **P2 Focus tips land on buttons in the Modem:** a refused chip's (Bulkhead) tip covers LEAVE THE
  MODEM at 1.6; at 1.3 covers the sign's BUY/SHRED notes and SLICES BUY tags. Fix: buttons in
  FocusTip's avoid set in the Modem.
- **P3** Event chosen-outcome "stamp" (FlightFx.stamp_on, word "") is a snapshot of the row
  settling on itself: reads only as a pink highlight.
- **P3** "NEED 112 HAVE 101" in the top bar's CYCLES tag draws below the tag's paper.
- **P3** Deck viewer's first card row overlaps the "Left click: select…" line.
- **P3** Route page has no focus on arrival (focus <none> after 200 frames); the first A works.

## City, raid, HQ
- **P2 A Heat threshold crossed by a flatline plays only inside the fight:** "HEAT 31 · NOTICED
  (25+)" banner and note (~10 px at 1.0) play in the fight's small poster behind DEFEAT over the
  silhouette; HQ shows no crossing because `heat_poster.gd:134-160` remembers the value per
  campaign. Fix: play crossings on the HQ poster (don't mark seen from a fight poster that ended
  the run), or hold them for the next screen.
- **P2 After a won run, the cleared district's acid tint is a large bright blob** behind the run-end
  window and HQ's CELL STATUS panel; its CLEARED stamp is cut at the left edge ("…RED"). This
  is R6's naive "green blob" (shows on COMPLETED, C12 checked only LOST). Fix: keep stamps inside
  the view, or skip stamps/tints for off-view sites on non-map pages.
- **P2 (1.3)** A dead operative's crew card: the FLATLINED stamp overlaps "// BREAKER // RANK 0".
- **P3** Grid with the pad: first focus "< PREV SITE"; JACK IN takes Down ×3 (via Chip, OperativePick).
- **P3** Loadout viewer under pad shows "Close [Esc]".
- **P3** Raid feed header reads "Raid over" with the summary while the last step's effects still
  play and Continue is disabled.

## Motion rules, kit, tests, docs
- The hotkey swallow is a MotionSkip rule gap: works_ui knows focus moves, accept and clicks,
  not the game's own action keys.
- The plain-turn test uses synthetic beats.
- Known items: AWAITING_FIX 11 unchanged (none looked broken); rules English still shown ("Step 1:
  Collector reaches CORE: 5 damage, HP 50 → 45", "Heat +5: Collector reached CORE: 31 → 36").
- Unverified: a threat withdrawing at the verdict (all threats reached CORE in every raid);
  combat card drag (OS pointer).

**Verdict: NOT CLEAN** (1 P1: tutorial and dock at 1.6; 10 P2).
