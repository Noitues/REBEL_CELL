# Overnight art run, 2026-11-01 to 2026-11-02

All 9 combat-screen roadmap steps have been run and committed on `art-pass` (49b3e365, 7748b55b, d6e762d2). Everything is under `combat_redesign/locked/`, and every choice is logged in `DIRECTION_REVIEW.md` as O-29 and O-30. As agreed, the Godot port spec, the mailbox entry and the ART_BIBLE changes are **drafts**: nothing has been posted to build, and ART_BIBLE.md has not been changed.

Start with: `final/p1_decide.png`, `review_final.jpg` (one row per step), `REVIEW_FINAL.md` (the art director's verdicts and your decisions).

## Per step
| # | Step | Status | Where |
|---|---|---|---|
| 1 | Lock the player family | Done, except the tower loudness call (below) | `final/` (9 plates, card_sheet, grey_proof, before_after, checks.json) |
| 2 | Corp skins (Solace, Meridian proof) | Done. Meridian's stencilled numbers are not drawn | `final/p1_decide_solace.png`, `_meridian.png` |
| 3 | Grammar on the new skins | Done. Meridian FAR marks were lifted after failing (1.1:1) | `final/grammar_check.jpg` |
| 4 | Effects | Done: 28 effects plus 4 variants, in player and corp skins, with keyframes, timings, reduce-motion versions and a 60 fps flash meter (each effect at most 2 per second). The full 13 s resolve beat measures at most 3 per second | `effects/fx_*.png`, `strips/`, `timings_*.json`, `resolve_beat_strip.jpg` |
| 5 | Hover plates | Done: all 11 plus the key, recomputed from the sim, with Brace and Twist also on Solace and Meridian | `hover/contact_sheet.jpg` |
| 6 | Backdrop and loudness | Done: the board reads first, the room is at mean 0.134 with 0 % loud, and the grade applies to every plate | `backdrop/before_after.jpg`, `grade.json` |
| 7 | Transitions | Done: T5/T6 bits FX recoloured (0 whole-frame flashes); T2/T3/T5/T6 frames updated | `transitions/sheet.jpg`, `t5_A.gif`, `t6_A.gif` |
| 8 | Godot port spec | **Draft**: shaders, bakes, skin Resource format, effect timings as data, order of work, 10 GUT tests. Mailbox A-116 drafted, not posted | `GODOT_PORT_SPEC.md`, `MAILBOX_DRAFT.md`, `port/` |
| 9 | ART_BIBLE fold | **Draft**: 16 conflicts with the current bible, each with a proposed resolution, and 10 questions for you | `ART_BIBLE_COMBAT_DRAFT.md` |

## Changes made without asking you (all can be overruled)
- **Card type colours.** TOWER is cobalt #2F5BFF and WAVE is orange #FF8A1F, so violet now means Trace only. Bone was tried first, but it disappeared against the card paper (1.04:1). As a knock-on, the Spin 3 band moved to yellow.
- **The hand is at 1.10x** (it was 1.15x), so no card covers the wheel.
- **Pencil brackets.** Where the HUD rows are too tight for a ring, hover marks LANDS and THROUGH with pencil brackets "( 9 )" instead.
- **FAR threat trim.** The beads were a meaningless dot count and read as a dotted line; FAR is now one solid tapered stroke.
- **Room grade.** T5 starts and T6 returns on the graded bare room, which removes one whole-frame flash in each.

## Decisions for you
1. **Tower loudness.** The tower zone is 48.6 % loud on p1 but 57.9 % on p2 and 57.5 % on p3, against a 50 % target. The whole plate is 12 % loud, against E10's 4 %. Accept this, or dull the yellow and green slice inks?
2. **Card colours.** Confirm cobalt and orange.
3. **Corp-skin and grammar defaults.** Confirm colour plus material with one neutral silver tape (O-27), and the ART CALL 51 grammar.
4. **Effect layer.** Should effects draw under the HUD or above it? 24 of the 32 effects run past the 0.6 s VfxTier T2 cap: allow per-effect overrides, or shorten them?
5. **Movement arrows in effects.** Pink (the player acting), or the hover's yellow PLAN arrow?
6. **Port name mapping.** Jammer vs glitch, Firewall vs scorch, the Hold card vs game-v2's SET dial, and art for halo and bug.
7. **Shove bump.** Do both units lose HP? The art shows no change.
8. **Twist rendering.** The state stores ring +1 at its pre-twist sectors, but p2 and p3 draw it untwisted. The resolve beat works around this; please confirm which is right.
9. **Scope** (bible Q1). Does the punk family replace the D4 wheel and the sticker cards too?
10. **Sign-off.** Approve the port spec and post A-116 (with `waves_art_on` defaulting to false), and fold the bible draft into v2.2.

## Known leftovers (art-pass will clean these up)
- The resolve-beat GIF and strip are on the board from before the re-grade.
- GODOT_PORT_SPEC Appendix A and its section 14 still give the old shield and brace reduce-motion numbers and the old refund source; they need regenerating from `port/fx_timings.json`.
- On h02, the lifted Brace covers more of Spin 3's rules line.
- h04 Meridian still has one dot run, caused by the Meridian rib texture.
- The worst 60 px tile in T5/T6 hits exactly 3 flashes in a second: it passes, but with no margin.
- Five latent effects (strike, ricochet, firewall_burn, Adjuster hit, repair) are drawn on stand-in marks.
- Ring 2 unit kinds are told apart by glyph only (minimum dE about 2.5).

## Other
- Mailbox: nothing new after B-084.
- Agents again ran a bare `python -` a few times despite the rule. Each time it ran no code and was stopped at once.
