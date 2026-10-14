# Animation pass, round P1 (overnight run 2026-10-13: "if you run out and need work, start the animation work after")

The pass was paused after M14 (DECISIONS 2026-10-05). The designer restarted it for this run, after waves 3–5. R7 is retired:
its findings inform this round but are not a fix list (CP-002 ruling 2). Ground rules come from `docs/ANIMATION_HANDOFF.md`:
- views only;
- reduce effects = the end state;
- headless never waits;
- every duration and curve lives in `content/config/ui_motion.tres`;
- the motion kit / runner is reused, never hand-rolled tweens.

Evidence: `docs/playtest/claude/PB-010/_FINDINGS.md` M1–M10, and the motion items queued by plan 1 (DECISIONS: PT-002a
triage ruling 7; W3-ROUTE R5).

Every slice:
- **Tests:** reduce effects ON gives the final state in 0 frames; headless gives the same end state as before (the
  existing flow tests stay green); every motion value comes from `ui_motion.tres` (no literal durations).
- **Captures:** a windowed frame strip (Movie Maker via `run_windowed.py`) before | after, at
  `docs/art_review/PLAN1/ANIM_<SLICE>.jpg`.
- **Paperwork:** a DECISIONS entry. WIP commits; QUICK precommit.

## ANIM-COMBAT (combat): M1, M2, M3, M4, M7
- **M1:** a played card visibly leaves the hand and lands on its target. A nudge or Fine Tune turns the wheel (or its
  ghost) as soon as it is queued, and the RAM chip ticks down.
- **M2:** SEND IT resolves in order, one wheel at a time. Beams don't overlap, damage numbers are readable and land on the
  HP chip, and wheels move with a transition, not a cut.
- **M3:** a Perfect gets a payoff beat: the tag pops, then resolves into the hit.
- **M4:** the turn header never flips back (1 → 2 → 1 is a bug: find the double write).
- **M7:** the enemy's return strike follows the player's hit with no dead lull.

## ANIM-FLOW (screens + city): M5, M6, M8, M9, M10, + queued
- **M5:** map → combat: the click is acknowledged at once, and the combat background is there on the first frame (no dark frame).
- **M6:** a reward pick: unchosen cards leave and the chosen one flies to the deck. No blank slots and no hard cut (fit the new
  W4 rewards list).
- **M8:** raid playout: readable markers, no flicker, CONTINUE enters, and the stamp lands with weight.
- **M9:** HQ arrival: no dead 0.7 s hold, and the layout settles in.
- **M10:** press feedback and entrance motion on menus, the loot sheet and the defeat screen.
- **Queued:** the netrun node animates along the route (PT-002a ruling 7). On hover, a route node animates out to its
  building (R5).
