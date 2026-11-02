# Combat roadmap steps 1-9: art director final review

Saved by the orchestrator from the art director's returned text. Board: `review_final.jpg`.

# Combat screen, roadmap steps 1-9: art director review (2026-11-02)

**Review board:** D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/review_final.jpg (3000x5881). It has one labelled row per step and a final row of defect crops. The script that builds it is D:/rc_tmp/claude/claude/C--Users-noitu-AppData-Roaming-Claude-scratch-workspaces-1c092eb2-44e7-479e-859a-83b75e36eb3c-d0376422-bd95-40f9-844b-6e7d2a954ea6-scratch-2026-11-01-0b9d75/4dfa2e73-e058-412d-b93c-b95aedb48b42/scratchpad/build_review_final.py

**Rule break by me:** I ran a bare `python -` once by mistake. It was an empty heredoc tacked onto a crop command; it ran no code and wrote nothing, and I stopped it (task bd72ksbnn). All real work ran from script files. Nothing is committed, no Godot or Blender was used, and nothing was written under D:/Godot/rebel_cell. The only file I wrote in the repo is review_final.jpg.

**What I opened:**
- **final/:** p1_decide, before_after, grammar_check, card_sheet, grey_proof, p1 Meridian, p2b Solace, plus 3x zoom crops of p1 and p3.
- **effects/:** the fx_D_damage sheet, fx_block_vs_break, and the strips gun_hit, slice_crack, twist_solace, commit_neutral and refund.
- **hover/:** contact_sheet, h02_brace, h03_trigger, h08_hold, plus HUD crops of 4 plates.
- **backdrop/:** before_after and p1_srv.
- **transitions/:** sheet and strip_t5_solace.
- **port/:** cards_proof.
- **Read in full or in their key sections:** GODOT_PORT_SPEC (intro, 0, 12-14), MAILBOX_DRAFT, ART_BIBLE_COMBAT_DRAFT (C1-C16, Q1-Q10), and the NOTES caveat sections.
- **Not opened:** fx_C, fx_H, fx_L, fx_M, fx_P, fx_S and fx_T at full size; only one sheet (fx_D) was opened.

## Claims checked against the files
Every file named in the agents' path lists exists. The numbers in the JSON files match what the agents said:

- **final/checks.json:**
  - Draw asserts: 63/63 on p1, nowords and both corp p1 plates; 49/49 on p2 and p3; 24/24 on p2b on all three skins.
  - Mark collisions, occlusion and dash audit: 0 everywhere.
  - Hand: closest pixel 458.9 px from centre on every plate.
  - Tower loud share: 48.6% on p1, 57.9% on p2, 57.5% on p3, 47.6% on p2b.
  - Card colours: TOWER 4.94:1 and WAVE 7.86:1; bone vs paper 1.04:1; TOWER vs WAVE in grey 2.19:1.
  - Tape match 100 / 97.7 / 98.0%; enemy-zone pink 0.228-0.229%.
  - Meridian FAR now 2.46:1 (dE 23.3).
  - Cards: all 11 match the state; no required word missing; nowords has 0 text calls.
  - The p3 played slots are named Twist, Trigger and Brace.
- **src_snapshot:** in sync with corp/src (only underscore temp files and fonts/glyphs differ).
- **effects:** the largest flash count anywhere in timings_CDHL.json and timings_MPST.json is 2 per second.
  - CDHL: ward_on and slice_crack reach 2.
  - MPST: shield_block and brace_block reach 2 in their reduce-motion versions, against 1 in full motion. Reduced motion should not flash more than full motion.
  - 16+3 plus 12+1 gives the 32 entries in the port spec, which is the 28 roadmap effects plus 4 variants.
- **hover/checks.json:**
  - all_pass is true on all 26 plates.
  - Hand: h02, h05, h06, h07, h08 and h09 come to 455.6 px, 0.6 px over the line.
  - Tower loud share on h02 Brace is 53.4%, over the 50% target.
- **backdrop/checks.json:** all_pass is true. Room mean is 0.135, board/room ratio 1.61-1.67, room pink 0%.
- **transitions/metrics.json:** 0 whole-frame flashes; the worst 60 px tile has 2 flashes.

## Per step

1. **Lock the player family: PARTIAL (nearly done).**
   - Evidence: final/p1_decide.png, before_after.jpg, card_sheet.jpg, checks.json.
   - All ten O-29 fixes are in, and I confirmed them on the crops: digit 0 is clear of the tape, digit 3 has its own hole, cobalt and orange type plates, played names on p3, Spin 1/2/3 are distinct.
   - Still to do:
     - The tower is 57.9% loud on p2 and 57.5% on p3 (designer call).
     - Digit 3 now crowds the N of "THEN". Shift the label about 6 px left.
     - Rows of 7-8 small brown beads next to each Worm on the tower rim read as dotted lines at 1:1 (crop "beaded rows" on the board). They show on every plate, the effect strips and block_vs_break. The dash audit misses them because it counts draw calls, not pixels.
     - The hand is 1.10x, not 1.15x, and the card bottoms touch the screen edge.
2. **Corp skins: DONE (Meridian as a proof).**
   - Evidence: p1_decide_solace.png, p1_decide_meridian.png, grey_proof.jpg.
   - The Meridian hazard rim is calmer and its gap from the amber HOLD arc is now 37 px. Both corps read as themselves in colour and in grey.
   - Still to do: Meridian's stencilled numbers. Ring 2 unit kinds are close (minimum dE 2.3-2.7), so only the glyph tells them apart there.
3. **Grammar on the new skins: DONE.**
   - Evidence: final/grammar_check.jpg, checks.json grammar_step3.
   - The HOT/COLD/FAR marks, hatch swatches, arrowed outline and enemy outline are checked on all three skins.
   - Still to do:
     - The red hatch on BURST pink and REPAIR green is only about 1.3:1. It separates by hue and by the ink keyline, which is acceptable.
     - The sector-0 chevron probe found no HOT chevron in its column, so that check is empty, not passed.
4. **Effects: DONE, with caveats.**
   - Evidence: effects/fx_*.png, strips/ (52 files), timings_CDHL.json, timings_MPST.json.
   - All 28 effects plus 4 variants are built on the real board, with keyframes, timings, a reduce-motion version and a measured flash check (at most 2 per second).
   - Still to do:
     - Strike, steel ricochet, firewall_burn, the hit_land Adjuster variant and repair_mend are drawn on stand-in marks, not checked against real numbers.
     - The full resolve sequence has never been flash-measured as a whole.
     - Effects are composited above the HUD and the hand. The bible draft (Q4) wants them under the HUD.
     - Twist, Pull and Shove use pink movement arrows, while hover uses yellow PLAN arrows. Pink is defensible as "player acting", but write the rule down.
     - Reduce motion counts 2 flashes against 1 in full motion on shield_block and brace_block.
     - The fx_refund strip pastes the RAM panel next to the board instead of showing its real position. Its source line says "ram 3+1", but the frames show 2 coins lit going to 3. Verify.
5. **Hover plates: DONE, one defect.**
   - Evidence: hover/contact_sheet.jpg, h01-h11 (plus nowords, Solace and Meridian versions), checks.json.
   - All 11 plates are recomputed from the sim, and the grammar matches the key.
   - Defect: the yellow pencil rings round LANDS and THROUGH cover HUD column labels. On h02 "BRACE" reads "BRA_E"; on h03 the ring cuts into "SHOT". The hover collision test does not include HUD labels.
   - Still to do:
     - The lifted card in slot 0 sits 0.6 px outside r455 and visually touches the rim landing marks (crop on the board).
     - h02 tower loud share is 53.4%.
     - Hover uses a private copy of the generator (hover/src), which can drift from corp/src.
6. **Backdrop and loudness: DONE, not carried to the other sets.**
   - Evidence: backdrop/before_after.jpg, p1_*.png, grade.json, checks.json.
   - Every target passes, and the board clearly reads first.
   - Still to do: the new grade exists only on the backdrop/ plates. final/ (plate mean 0.229, the old grade), hover/, effects/ and the T5/T6 end frames all still use the old r2_ground grade. bd_grade is not in corp/src.
7. **Transitions: DONE.**
   - Evidence: transitions/sheet.jpg, strip_t5/t6 (plus Solace), t5_A.gif, t6_A.gif, metrics.json.
   - The spinner and rings come from the generator's own layers, the dashed ghost paths are gone, and the flash check passes.
   - Still to do:
     - T5 K6 and T6 K1 use the old-grade plate.
     - The glyph source points for the srv and gh rooms are not checked.
     - No won-state plate exists.
8. **Godot port spec: DRAFT (not sent).**
   - Evidence: GODOT_PORT_SPEC.md, MAILBOX_DRAFT.md, port/ (fx_timings, skin_tables, cards_atlas, cards_proof).
   - It is complete: target code on game-v2, data classes, shaders, bakes, order of work and 10 GUT tests.
   - Still to do:
     - 5 OPEN name mappings: Jammer vs glitch, halo, Firewall vs scorch, the Hold card vs the SET dial, and bug.
     - The tower sheet bake has not been run.
     - The game-v2 head needs re-checking.
     - The mailbox entry (A-116) is not posted.
9. **ART_BIBLE: DRAFT (not folded).**
   - Evidence: ART_BIBLE_COMBAT_DRAFT.md, with 16 conflicts (C1-C16), each resolved, and 10 questions (Q1-Q10).
   - Still to do: the designer's sign-off, then the mechanical fold to v2.2, the Palette update and a DECISIONS line.

## Do the board, effects and hover plates read as one system?
Yes. The three layers hold everywhere: player punk print (pink, ink keyline, paper), corp enamel and material, and the cyan system HUD.
- The effects keep to their materials: pink comic hits are ours, red X-halftone is harm, the corp acts with a shutter, and the only soft glow is life.
- Block and break never look alike, in colour or in grey.
- Hover dims the board and lifts the plan in yellow pencil, and that grammar does not clash with the effect materials.

There are three seams:
1. **Two room grades are in circulation.** backdrop/ has the new one; everything else has the old one.
2. **Movement arrows.** They are yellow in the plan (hover) and pink in the resolve (effects).
3. **Effect layer.** The plates put effects above the HUD; the spec and bible draft lean toward under it.

## Game information lost or at risk
1. The hover pencil rings cover HUD column labels: BRACE on h02, SHOT on h03. A word is occluded. This is the only real loss I found.
2. Digit 3 touches the N of "THEN". Both stay legible, but there is no gap.
3. Played-slot names print at 70% on a transparent slot over the room. They are legible but faint.
4. Ring 2 unit kinds are told apart by glyph only (dE 2.3-2.7).
5. The fx_refund RAM count does not match its own source line (unverified).
6. Not a loss but a known gap: Meridian's stencilled numbers are not drawn.

No card number, word or state field is missing; checks.json game_info agrees.

## Top fixes, ranked
1. **Hover HUD collisions.** Add the HUD labels as an occluder class in the hover collision test. Shrink or offset the pencil ellipses round LANDS and THROUGH (or ring only the digit glyph box) so no column label is cut. Re-render h01-h11.
2. **Carry the room grade through.** Put bd_grade into corp/src as the default grade, then re-render final/, hover/, the effect bases and the T5/T6 end frames. Otherwise the port has two references for the room.
3. **Beaded rows near the Worms.** Find what they encode (probably the gun muzzle beads). If they are a count, draw them as a solid tally bar or one tapered stroke. Extend the dash audit to a pixel check for runs of evenly spaced dots.
4. **Measure the full resolve beat.** Sequence the E10 p3 resolve with the spec's spacing and run the 60 fps flash meter once. Also fix the reduce-motion versions of shield_block and brace_block so reduced motion never flashes more than full motion.
5. **Slot-0 lift.** Lower the lift scale a little, or slide the fan another 8-10 px, so the lifted card clears r455 by at least 4 px and leaves the rim landing marks alone.
6. **Digit 3 / HOLD THEN.** Move the label about 6 px left or narrow its letter spacing.
7. **Effect layer.** Re-composite the effects under the HUD, except hp_through, refund and trace_add (bible C14 / Q4), once the designer rules.
8. **One generator.** Merge the hover/src deltas back into corp/src, or make hover import corp/src read-only like the effects do. The port should have one source of truth.
9. **Later, once the latent effects have game sources:** check them against real numbers, and fix the refund RAM count.

## Decisions the designer must make in the morning
1. **Tower loudness.** p2/p3 are at 57.9% and 57.5%, and h02 at 53.4%, against a 50% target. The whole plate is 12.2% loud against E10's 4.1%. Accept, or dull the yellow and green slice inks (bible Q8)?
2. **Card type colours.** Say yes to TOWER cobalt #2F5BFF and WAVE orange #FF8A1F, which replaces bone. As a knock-on, the Spin 3 band moved to yellow (Q9).
3. **Art-pass defaults.** Confirm O-27 (colour plus material, one neutral silver tape) and the ART CALL 51 grammar (Q10).
4. **Name mapping for the port.** Jammer vs glitch; Firewall vs scorch; the Hold card vs game-v2's SET dial (the art has a Hold card and a HOLD THEN plate); art for halo and bug.
5. **Shove bump.** Do both units lose HP? The art currently shows no change.
6. **Effect layer.** Effects under the HUD or above it (Q4)? And effect lengths: 24 of 32 run past the 0.6 s VfxTier T2 cap. Allow per-effect overrides, or shorten them (Q3)?
7. **Movement arrows in effects.** Pink (player acting) or the yellow PLAN arrow, which keeps one movement colour?
8. **Scope and checks.** Does the punk family stay on the ring board only, or also replace the D4 wheel and the sticker cards (Q1)? Should the shipping build run the colour-blind check on this screen (Q2)? Drop L8 dotted entirely (Q7)?
9. **Sign-off to start the build.** Approve the port spec and post MAILBOX A-116, with the `waves_art_on` flag defaulting to false. Approve folding the ART_BIBLE draft into v2.2.