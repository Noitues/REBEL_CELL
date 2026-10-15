# PT-003 scripted-steps follow-up fixes (designer: "make all the updates", 2026-10-15)

Source: `docs/playtest/claude/steps/PT-003_steps.md`. Screenshots are in `.playtest_sessions/PT003-steps/<step>/`.
The runner is `tools/playtest/steps/pt003_steps.gd` + `tools/playtest/steps_judge.py` (process doc 05 §13).

1. **Step 8, a real gap:** ruling 1a (DECISIONS "Designer rulings: map tags (1a)…") covers the netrun maps too, but
   `netrun_scene.gd` (about line 2654) sets `city_overlay.tag_rule = TagRule.LIT`, which tags plan and lit nodes at
   rest in GRID VIEW.
   - Every map follows 1a: no name tags at rest, a tag only while its node is lit (pointer / list / pad), and MAP KEY
     hover shows all of them.
   - ART-R1 added `CityMapOverlay.tags_all` and wired it on the HQ; wire the netrun map key the same way.
   - Raid maps: status stays on the node, and no name tags at rest.
   - Update the tests that assert tags at rest.
2. **Step 2:** with no tags at rest, the next-step cue (the orange `avail` ring, `SiteMarker.AV_NEXT`) reads on only
   one Site.
   - Make every next-step Site's ring read at rest at 1.0, through weight and contrast only: no tick marks, no motion.
   - The 2 px / 35 % halo is for claimed territory, not this ring.
   - Test: every AV_NEXT Site draws its ring at rest.
3. **Step 9:** Q during a card aim left the aim hints on screen.
   - Ending an aim with Q or E clears every aim hint (W3B-AIM `_refresh`).
   - Also test the free-nudge aim cancel and a target switch mid-aim.
4. **Step 17:** a placed defense's ring and pip (W3-RAID F17, `defence` in the socket spec) are too subtle; make them
   readable at 1.0 on the raid setup map.
   - A plain claimed node had no asset slot, so the drop went to HOME SERVER. Check that against the GDD and log the
     answer.
5. **Step 4:** the scripted run found no map-side marker for "RAID AT HEAT n". Check whether W3-GRID C3 ("a warning
   before a threshold") meant one on the map or gauge. If it did, add it; if not, log that.
6. **Step 15:** the SAVED toast overlaps the Heat header. Toasts never cover UI: extend ART-R1 F7's `Toast.clear_root`
   to labels and the HUD, or give the toast a clear slot.
7. **Step 18:** the CELL HOLDS sticker partly covers a header line on the raid report. The sticker must clear every
   text row; add a measured clearance test (`HOLDS_AT` moved to 0.9 in ART-R1).

Out of scope:
- step 7, node types: waiting on the route redesign;
- steps 11 and 12, motion: approved by the art-pass session; the designer checks those by eye.

Then:
- **Re-run:** steps 2, 4, 8, 9, 15, 17 and 18, in one windowed run (`run_windowed.py`) judged by `steps_judge.py`
  (Batch API, $1 budget). Add a "re-run after fixes" section to `PT-003_steps.md`.
- **Sheet:** one before | after group sheet, `docs/art_review/PLAN1/PT003_FIXES.jpg`, for the art-pass session.
- **DECISIONS:** "### 2026-10-15 — PT-003 steps fixes" under Implementation decisions.
- **Tests:** run the suite-rule tests (`test_suite_integrity`, `test_visual_lint_static`, `test_vfx_tiers`,
  `test_art0_kit_words`, `test_art12b_skin_chrome`, `test_anim_r6_rules`), every touched test, and every test that
  greps for `tag_rule`, `tagged_ids` or `label_rects`.
