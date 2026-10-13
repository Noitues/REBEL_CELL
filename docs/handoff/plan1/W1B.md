# Change plan 1 — wave 1b: PT-002a bugs (designer go 2026-10-13; no separate gate, folds into PT-002)

Feedback (verbatim): `docs/playtest/PT-002a_FEEDBACK.md`. Triage and ids: `docs/playtest/PT-002a_TRIAGE.md`.
Rulings: DECISIONS "Designer rulings on the PT-002a triage".

Every slice:
- **Reproduce first**, in a test where possible. Headless Godot drops pushed mouse events, so use key events or call
  the handler, and say so.
- Fix, and keep the test as the regression guard (rule 6).
- Capture before | after at 1.0 and 2.0 for the group sheet (`docs/art_review/PLAN1/W1B_<SLICE>.jpg`).
- DECISIONS entry under "Implementation decisions" (`### date — title`, newest first).
- New player-facing text in **US English**.
- WIP commits every ~30 min; one precommit at a time; stop your own background runs; no motion redesign.

## 1B-PLAYOUT (combat + screens): F3, the top priority
The designer saw:
- SEND IT resolve with no animation;
- the tutorial win jump straight to CONTINUE;
- START DEFENSE go straight to the raid report, with no playout.

This looks like one cause. Candidates:
- motion or reduce effects forced on or off;
- a leaked `Motion.force_live` / instant flag;
- a default in Settings;
- the W1R1 review-pack `_settle` change leaking into the game;
- `MotionSkip`.

Find the cause with a test that runs the real scenes **not** under the test-only instant mode, fix it, and prove the
playouts run at 1× in a normal session. Check `user://settings` defaults too. Report the root cause.

## 1B-STICKER (screens)
- **F1:** CONTINUE shows no sticker fold at all in the real game. W1R1 made the room, but the fold isn't drawn, or
  only shows in captures. It must show on hover / focus, beside the word.
- **F2:** SKIP shows ">>" over its S. Apply the shared fold-room rule (`VinylSticker.fit_fold_room`) to SKIP and every
  other verb sticker, and extend `test_w1r1_sticker_fold.gd` to cover them.
- **F4:** at text 2.0 a hovered reward card clips. Scale the hover zoom so the card stays whole on screen.
- **F5:** at 2.0 the bottom of the loot reward screen is cut off (SKIP / CONTINUE / Deck half shown). Fit or page it.
- **F8:** after a combat win, hovering the loot button opens the loot sheet. Only a click / press opens it.

## 1B-MENU (screens)
- **F6 crash:** `settings_panel.gd:572`. Esc emits `closed`, which frees the panel, then `get_viewport()` is null. Mark
  the input handled before emitting. Add a test.
- **F7, B5 reopened:** the title's QUIT dialog buttons don't respond to clicks; A doesn't quit; CONTINUE has no key.
  The lead: V2 saw `ModalScrim` hovered over the dialog, so the scrim may eat the clicks. Check mouse_filter and z
  order. Give every dialog button its key (Enter / Esc / pad A / B) per the confirm-dialog rules.
- **C-2:** tutorial page 7/7 says "next" while the button says FINISH. Fix the copy.
- **D-UX5:** New Campaign hangs about 1 s before its screen. Show a loading overlay (or the screen first, then build)
  so input is acknowledged at once.
- **F16:** on events, the selected option's wide yellow band doesn't follow arrow-key focus or mouse hover. Make it
  follow both.

## 1B-COMBAT (combat + rules)
- **F9:** Freeze doesn't work on the player's spinner. Check the GDD first: if the GDD says Freeze applies to the
  player's wheel, fix it; if it doesn't, report and change nothing. If it is a rules fix, rule 6 applies (preview =
  result).
- **F10:** in the Compliance Officer fight the backdrop starts on the medical building, then switches to the city when
  the enemy wheel is hovered. One backdrop per fight; hover never changes it.
- **F12:** does SKIP in combat rewards skip **every** reward type, or only the card pick? Verify. If it skips all of
  them, SKIP skips only the current reward and the others stay. The one-screen rewards redesign is a later item, so
  the minimal fix only.

## 1B-MAP (city)
- **F13:** on the netrun map, after zooming out or panning, hovering then leaving the map key re-zooms and snaps to the
  current node. Keep the player's zoom and pan.
- **F14:** hovering the map key does nothing. Expected: it highlights every node of the hovered type on the map, or
  each node type when a row is hovered. Implement the row-hover highlight.
- **F15:** HQ CREW → BREAKER 1 → VIEW LOADOUT → NEXT OPERATIVE → CLOSE leaves the polaroids on BREAKER 1 while the top
  bar shows BREAKER 2's loadout. CLOSE leaves the selection and the bar on the same operative.
