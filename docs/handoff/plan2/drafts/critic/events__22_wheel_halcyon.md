<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__22_wheel_halcyon; status ok; tokens in 3795 cache-write 0 cache-read 32585 out 1577; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/22_wheel_halcyon
**Verdict:** FIX

## Issues
1. **BLOCKER, arithmetic/template: the wheel is not nudgeable as a decision.** Sizes are 6+4+5+3+6+6 = 30, so that sums correctly. But the draft says "Nudge ±1 tick moves the whole wheel" and "Perfect/Good/Weak do not matter," while the EV line gives area-weighted odds. The odds are wrong: Rebate 6/30 = 20 %, Citation 4/30 = 13 %, Clinic 5/30 = 17 %, Curfew 3/30 = 10 %, Holiday 20 %, Award 20 %. These sum to 100 %, but Holiday and Award are listed as pure upside and Rebate as a flat +30 Cycles. The stated EV "roughly 12 Cycles equivalent" is never derived, and no value is given for Firmware, HEAL or Heat. Show the arithmetic or drop the claim.
2. **BLOCKER, determinism: Curfew's random slice pick is drawn "at confirm."** That is a second random draw after the checkpoint, with the "odds" preview. Preview must equal result. Draw it at wheel open (same checkpoint), or make it deterministic.
3. **MAJOR, adjacency claim is false.** The notes say "Citation beside Free Clinic and Curfew beside Holiday and Merit." In the listed order, Citation (2) neighbors Rebate (1) and Clinic (3), and Curfew (4) neighbors Clinic (3) and Holiday (5). Curfew is not adjacent to Merit. The ring wraps 6→1, so Merit neighbors Rebate, so the best two slices sit together. The "best next to worst" premise in the one-liner fails, and the nudge decision is trivial (nudge away from Citation and Curfew, which are only 23 % of the wheel).
4. **MAJOR, dominated choice.** Option 3's +10 Cycles is only "not dominated" against option 1 (EV unproven). Option 2 (free spin, +2 Heat, 0 free nudges) vs option 1: with 0 free nudges, extra nudges cost Heat 1 each, which is cheap, so option 2 beats option 1 whenever Heat is low. The 15-Cycle fee buys only one free nudge.
5. **MAJOR, systems.** The "HEAL 12 (CAMPAIGN-scope)" is wrong: HEAL targets the operative (SELF). The Curfew status "lasts the next combat" has no field; use a `next_combat_overrides` entry (N16) or apply it at wheel time. The slice's `hp_cost` and "Reward" fields are not EffectData. Tag N17 per slice. The fallback is stated, but it should be a data-only version (e.g., choices that split the slices).
6. **NIT:** "Rookie's HP" (Breaker has 60 HP, so 8 HP is 13 %); the Firmware is named "Patch+" (an existing id, which is fine as a working description). The text has 5 sentences, but "Terminal" is capitalized inconsistently.

## Concrete fixes
- Reorder the ring so the risk is adjacent to the reward: Rebate 6 · Curfew 3 · Merit 6 · Citation 4 · Clinic 5 · Holiday 6 (sum 30). Now a nudge off Merit or Rebate risks Curfew.
- Curfew: "CORRUPTED on one non-NULL slice, chosen from `events` at wheel open (shown as a marked slice in the preview)."
- Option 1 label: "Take the dial (-15 Cycles), 2 free nudges, extra nudges 8 HP each, max 2 extra." Option 2: "1 free nudge, extra nudges 2 Heat each, max 2 extra."
- Clinic: `HEAL, target SELF, amount 12`.
- EV line: Rebate 0.20×30 = 6 Cycles; Clinic 0.17×12 HP; Award a Firmware worth ~25 Cycles at 0.20 = 5; Citation and Curfew subtract; state the total.

## Keep
The three-way structure, with a safe skip, is clean. The slice sizes are legible. Fixing the Heat-for-nudge currency in option 2 is a good idea (a risk that pays in a different currency). The CORRUPTED payoff ties to R9.

## Q:
Q: Should the wheel's start tick be shown before the player commits to paying the fee?
Q: Should Heat-paid nudges stay capped at 2 so the Heat swing is bounded?
