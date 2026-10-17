<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__16_ambush_halcyon; status ok; tokens in 3704 cache-write 0 cache-read 32585 out 1533; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/16_ambush_halcyon

**Verdict:** FIX

## Issues

1. **BLOCKER, template / rulings (the AMBUSH stake):** Choice 1's stake is only "keeps whatever HP the fight costs." That is not a stake. The fight is also not an ambush: the player chooses it, so it is a hatch toll, not an impromptu fight. A loss carries "no event-specific penalty", and the fight already pays for itself plus a skip. Choice 1 therefore dominates choice 2 (40 Cycles, no fight, same skip) for any player who can win a 1-phase normal. The Design notes' "no dominated option" claim fails.
2. **BLOCKER, design (choice 3):** The text says "slip past", but the effect is +2 Heat for −15 % HP on the next fight only. That is strictly worse than choice 4 for anyone below FLAGGED. Nothing is skipped, so the label and the effect disagree. A 15 % HP cut on a normal (about 8 HP) is not worth 2 Heat, which is two thirds of a minor threshold step.
3. **MAJOR, R2 / R1 (the fight):** `patrol_unit` at T+1 is one tier above the node. The draft says only "caps at T4" and does not show the HP band. T2 to T3 gives 44–56 HP at ~14 reference dpt, which is 3.5 turns. That is fine for R1, but the arithmetic is not shown. The choice-1 preview must also state the tier.
4. **MAJOR, N16 (the skip):** `map_edits` sets the nearest "Router or Elite Router ahead" to `cleared`. It does not say what happens if layers 4–7 hold only a Rack, Mainframe or Terminal, or how an Elite is handled. Skipping an Elite node costs its ~+1 Heat, so the Heat reasoning is inconsistent (it would be a pure gain). The two Qs about cleared versus removed also leave the edit undefined.
5. **MAJOR, choice 2:** `cycle_cost 40` is described as "loses roughly 70 Cycles of value". That is unsupported, because choice 1 yields 30 Cycles plus Firmware. The claim fails if the fight is won, and the skip is the only real value.
6. **NIT:** The `dispatch_clue` and `foreshadows` fields are empty or marked false. "Interactions" claim Cold Exit and Scrubber are "not affected" without reason. "6 a.m." is fine. US spelling is OK. No Site names appear.

## Concrete fixes

**Fix 1 (stake plus ambush feel):** Reframe choice 1 as the forced-fight option. Replace its stake with: "On a loss, the operative dies as normal. On a win, the fight pays 20 Cycles plus 1 common Firmware (events stream). Win or lose, +1 Heat when the fight starts. The skip is granted only on a win."
- Add a first-turn penalty to give the ambush bite: `combat_overrides`: tier +1, and the enemy's wheel starts with an extra Citation slice (OUTPUT_DOWN ×1 on your first landing). If that edit is not available, use the HP-only tier bump.
- Reduce the reward to 20 Cycles so choice 2 is not dominated: the player pays 40 Cycles to avoid HP risk, or fights for +20 Cycles, Firmware and the skip.

**Fix 2 (choice 3):** Replace its effects with `MODIFY_HEAT` +1 (not 2) and `next_combat_overrides`: enemy HP −25 %, and the next combat starts with the operative's free nudge refreshed. Duration: 1 combat. Alternatively, turn it into a real skip: "slip past: skip the next combat node, no reward, +2 Heat." That gives it a distinct role between 2 and 4.

**Fix 4 (edit scope):** Specify the target: "the nearest Router ahead; if none, no skip is offered and the choice is hidden. Elite Routers are never skipped."

## Keep

- The setting and text hook (the schedule is wrong, the lights come on) are strong noir.
- Node-skip as a reward is a good, deterministic use of N16 and tests the full-graph view (D7).
- The warning not to skip your only shop is a genuine tension.

## Q:

Q: Should a skip be refused when the next layer holds a Mainframe or Terminal?
Q: Does the +1 Heat on fight start still apply if the player wins on turn 1?
