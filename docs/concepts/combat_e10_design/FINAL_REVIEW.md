# E10 design: final art director review (after the R3 fix pass)

Date: 2026-11-01. Branch art-pass, documentation only. Reviewed: every plate in `final/` (p1_decide, p2_preview, p2b_hover, p3_resolve, p1_nowords, p1_decide_srv, p1_decide_gh) at full size, in 2-4x crops and at a 1/16 squint, against the approved E10 plates (`D:/rc_tmp/combat_critic/plates/waves_e10/`), the golden plates (street_overview, hq_rebel_cell_overview), DECISIONS.md, the assembly report, `assert_draw_log.txt` (269 PASS), `element_coverage.json` and `state_e10.json`.

## Verdict

**Not ready to hand over as final. The screen now reads as one system, but it has one game-information loss and one legibility regression from the fix pass.** Both are small, exact fixes (O1, O2). Two polish items (O3, O4) and one ruling (O5) go with them.

- **One designed system: yes.** One kit plate across the header, bill, objectives, RAM, UNDO and hover tag. One glyph library across the cards, ring tokens, arc discs, chips and chain. One HP grammar and one coin/square/flame set. The wheel no longer looks like seven clusters pasted together, and the srv and gh rooms carry the same board unchanged.
- **Board-first: by structure, yes. By value, no (measured).** At squint the disc is the largest and most structured mass, and the loud E10 reds are gone (whole-plate loud 0.134 -> 0.046). But the room's p95 (0.38-0.40) is still above the board's (0.30). The bio room is the brightest coherent shape after the hand and SEND IT. Ruling in O5.
- **Drift from decisions:** three items. The bezel spoke now cuts a schedule label (O2). The soak X notch cuts the arms instead of sitting at the crossing (O3). The warded badge placement (Y9) collides with a ring tag (O1). SOAK moved from #464EFF to #3A7EF3. That was a fix-pass instruction with the reason recorded, so it is accepted (see the notes).
- **Same game information: no, one loss.** Unit 3 (Worm, ring 1, sectors 1-2, `warded: True` in f1) has its warded lozenge hidden under the NOW W1 ring tag in p1, p2, p2b and p3. In nowords only a 3 px yellow sliver shows. E10 showed it clearly. Everything else checks: 269 draw asserts pass, no word is missing, and every FINAL row is visible.

## Element list review (the user's request: nothing omitted)

- DECISIONS section 3 has 199 element rows. `element_coverage.json` has the same 199, and I diffed both ways by script: 0 missing, 0 extra. There are 169 FINAL, 21 LATENT, 7 REMOVED and 2 UNSETTLED (no_target_tag placement and challenge_trigger_hits layout, both LATENT in these states). Add the 2 elements owned inside other rows (adjuster_cell_underlay, unit_gone_state) and the 4 section-1 LATENT additions (send_it_key_hint, card_hover_ghosts, card_drag_aim, reduced_effects_state) to get 205, which matches DECISIONS section 1.
- 20 FINAL rows cannot be traced by function name. I checked each of them by eye in the plates, and all are present: slice_frame, icon_turret, icon_repair, the five unit glyphs, chev_hollow, chev_sector_column, warded_mark, shield_bracket, kind_colour_set, sched_plus_cells, arc_now_dot, card_icon_set, hand_fan, stickers_nowords, hover_dim_overlay and nowords_variant.
- **What the coverage audit cannot see:** an element can be drawn and still be covered. warded_mark is drawn twice and visible once, because unit 3's badge is under the tag (O1). The audit needs one more rule: every badge, tag, label and digit box must have 0 px overlap with every other one. It is added to O1.
- The state was checked against the plates as well: f1 has two warded units (3 and 6), two Worms (2 and 3), kills [] and the adjuster. Unit 6's badge reads, and unit 3's does not.

## Open items (go to the designer)

| # | Element | Exact change | Why |
|---|---|---|---|
| O1 | **warded_mark** (wave_rings `wr2_units.warded`, Y9 placement) | Before the badge is drawn, test its box against every ring-tag box (`r2_misc.tag_anchor`, all beats) and the HP tray. If they intersect, mirror the badge to the other start-cap diagonal (45 deg toward the start cap and the **inner** radius, 31 px from the token centre, same 30 px lozenge and 16 px skull). Keep the draw order badge -> glyph. Add asserts: badge ∩ (tag, chevron column, HP tray, glyph) = 0 px in p1, p2, p2b, p3 and nowords. Apply the same test to the dead badge. | Content loss. Unit 3 is warded and the badge is under NOW W1 (crop at 610-720 x 340-440). The tag is drawn after the units (asm_r2 line 212; in p2b it is redrawn above the veil at line 235). |
| O2 | **bezel_spokes** vs **sched_hold_cells** label (asm_r2.py lines 182-184 and 222-226) | Keep the fix-8 spoke layer, but draw the schedule labels (the HOLD NEXT and HOLD THEN text and their hold glyphs) **after** it. Or give the spoke a knockout under every schedule label's text box. Move the r353-360 continuity assert outside the label boxes. | Regression. The 150 deg spoke cuts the O of HOLD NEXT ("H LD NEXT") in all five beats. The R2 outer_rings plate and E10 both read clean. Words win over line continuity. |
| O3 | **slice_soak_break_x** (soakx B, `wc2.break_x(soak=True)`) | Remove the notches cut into the four arms. Put one 5 px INK notch (a diamond knockout) only at the crossing, as decided ("the notch at the crossing"), with the 1 px INK keyline. The arms stay continuous at the 2.7 px stroke. | Drift. The current X reads as a stepped gash and a render fault (checks_soak_notch.jpg), not as a soak X. |
| O4 | **sched_this_turn** live label (nowords) and **card_multiplier** (cards_nowords) | Nowords: draw the "+" with a 2-stroke white tally (the same tally as the ring tags and sector digits). Give Spin's ×3 a 3-stroke tally, in the same form as the Trigger loud tab's 1-stroke tally. | In nowords every other number became a tally, but these two drop their count: the tape shows "+" alone and Spin shows no ×3. E10 nowords also lacked them, so this is not a regression, but it breaks the system's own nowords rule. |
| O5 | **backdrop_grade** (room relight, `r2_ground.room_relight`), DECISIONS 6.5 | AD ruling: **(c) then (a).** Lower the room lift one step, x0.57 -> x0.50, saturation unchanged, on all three rooms. After that, accept the remaining gap: the board reads by structure, and p95 cannot see 3-6 px strokes. **Do not** lift the tower icons or tokens (b). They are already white, and lifting them brings back the E10 clutter. Re-measure and record the new room p95 and loud. Do not chase board p95 >= room p95. | The board must be the first mass (golden plates: dark city, neon accents). The bio room is the brightest coherent block, and the board's own elements are FINAL, so the backdrop is the variable to move. |

Notes, not blocking (the designer should know them):
- SOAK = #3A7EF3 (fix 6, replacing Y1's #464EFF). It passes every check, but the margins are thin: deutan vs TRACE_VIOLET is 11.0 (floor 10) and tritan vs LANE_PLUS1 is 13.1. The notch (O3) and the chevron shape carry the meaning when hue fails. At 320 px the notch is sub-pixel, so soak reads by hue and blob shape there.
- The hover tag leader in p2b crosses about 250 px of the outer rings as a thin wax line. This is accepted (a leader has to reach the wheel), and it misses every landing arc.
- The right-hand cards are pushed out 28 px with a lift cap of x1.12 (fix 10). This is accepted: no letters are covered, and Spin's rules text is now uncovered.
- The 6 px white tick on the bezel at 262 deg (about x32, y612) is in the R2 outer_rings plate too. It belongs to that cluster and is not new.

## What changed per element vs approved E10 (summary by cluster)

**Ground and room.** E10's ochre city backdrop is replaced by the Solace room (bio, srv or gh) through one grade, scrim and plate (Y10). Room lift is x0.57 with neon saturation at 0.33. The board plate is an ink gutter. The E10 loose orange and red bezel hairlines outside the board are gone, and the bezel is one teal ring with rim lines, ticks, spokes and a recessed schedule track.

**Tower core (wheel_core).** Hub: a quiet lens, one bevel, an engraved crest and the BREAKER label. Slices: phosphor screens without code text, and new library icons (burst shells replace the E10 sunburst, turret, plain repair strip, shield kept). The HP bars and pips use the X10 grammar (HARM pip with white slash, SOAK pip with notch). The break X now has a HARM hatch. The soak X is notched (O3). Threat trim keeps separate thirds. The HP ring has no slivers at the spokes. The nudge ghost is removed. Preview and resolve tracers are one drawing (tracer at 55 percent, result at 100 percent). Shield pop is hex shards. Brace is the clamp plate with the Brace glyph.

**Wave rings.** The E10 M and arrow tokens are replaced by library unit glyphs on a 26 percent disc with a shadow halo and lane ring, placed 38 px from the start cap. The cell outline is 4/3/3 with a 12/8 dash. Chevrons are solid and hollow, and stacks compress only at 4. Warded and dead badges sit on the token rim (Y9; O1 is open). The adjuster is a gold diamond with a grouped HP bar. The kind wash set is R (Y6). The dim in hover is a true composite at 0.38.

**Outer rings and schedule.** The live cell "+2 THIS TURN" is muted under L1 (it was the loudest orange in E10). The hold cells use the library hourglass. Sector digits sit in discs 6 px clear of lane 0. The needle follows X9. Landing arcs use a 2.8 px frame, a kind-wash glyph disc, wear marks, the now dot, turn dots, chevrons and diamonds (HARM_UP), a check, soak, brace and twist marks. The future-wave tape keeps its true extents, and W4-W6 tags have INK knockouts.

**Top HUD.** The same information in one kit plate. The YOU tally uses the HP grammar, with LANDS 12 -> THROUGH 6 as the hero pair. RAW/SHOT/BRACE/RIDER = LANDS is one equation row. The SPLIT row routes to destination icons (hub, soak funnel, HP socket). The NEXT row's slice lost is a HARM slash pip at 60 percent. The p2 chips have library plan glyphs and outcome bars. The p3 chain strip has step discs, glyphs, tallies and prose. The HUD bottoms are 384, 518 and 538 (Y13).

**Objectives and resources.** Star tiles; WIN, SLICES KEPT (label only), KILL ADJUSTER and TRACE LOW. RAM coins, trace squares with a padlock cap, and Heat flames all come from one coin/square/flame set (Y4). The refund pop uses the plus coin.

**Cards.** The P frame and header, the coin cost badge (obj2 coin plus the digit), a 66 px library icon, the ×N multiplier, title, type band and rules text. The loud tab uses the trace square. The hover grow is a peel, and played cards show a dashed liner. The nowords cards use bars.

**Actions.** SEND IT and UNDO [Z] are stickers inside the margin. The nameplate is at r >= 520 (min 523.7). The hover tag is a kit plate (5 lines, the E10 text reflowed) with a leader, lime focus brackets on the hovered cell and a 0.38 dim on the others. The trigger path is pencil with an X end cap. The twist badge is anchored to the ring tag. There is a refund token and tag. The bottom hint is turn_resolve.exe.

## Checks I re-ran or confirmed

- The squint strip (E10 / new p1 / golden street / golden HQ, then srv, gh, p2b, p3): the hierarchy is as described above.
- I diffed decision rows against the coverage rows by script: 0 missing, 0 extra.
- In `state_e10.json` f1, units 3 and 6 are warded. In p1 only unit 6's badge reads, and unit 3's is covered (O1).
- R2 outer_rings `plate_p1_decide.png` shows HOLD NEXT intact, which confirms O2 comes from the fix pass.
