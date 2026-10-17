<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__03_future_halcyon; status ok; tokens in 3509 cache-write 0 cache-read 32585 out 1588; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/03_future_halcyon

**Verdict:** FIX

## Issues

1. **MAJOR, template/mechanic: Choice 3 is mostly not a FUTURE-vs-cost trade.** The label says "-15 Cycles", yet the result text says units "hit harder" and the notes call +20% a "threat tax". The draft never says whether the extra nudge is only turn 1 or per turn. The "+20% over three fights is 6 to 10 HP" claim is unsupported. Normal intake at the reference player is 2-12 per turn (Genome Core table), so 3 fights x 3-4 turns x +20% is closer to 3-8 HP at T1-T2 and more at T3-T4. At T1 it is cheap, so the choice is nearly dominant for a Tier 1 event.
2. **MAJOR, balance/dominance: Choice 1 and Choice 3 are stacking-dominated by a flat window.** One free nudge on turn 1 only is worth about 1 RAM and trivial. Choice 1 (Frozen + -1 resistance for one fight, 8 HP) buys more than choice 3's 15 Cycles. A Frozen start on a normal 3-4 turn fight skips one respin (R1 fight length), which barely matters. The reward is weak, so choice 2 (+30 Cycles) likely dominates both.
3. **MAJOR, systems: "enemy resistance -1" and "start Frozen" are asserted without fit.** Most Halcyon normals have no resistance, so -1 min 0 often does nothing and the preview would show an empty benefit. State when it applies or swap it for a stronger, checkable override (e.g. enemy HP -15%, which is in the family list).
4. **MINOR→MAJOR, rule: tier damage scaling.** "+20% ... tier-independent per R2" is correct (buff/debuff). But the draft says N16 "needs N2 for the enemy damage factor", which contradicts this. N16 depends on N2 only per the N-table, so state that as the table does.
5. **NIT, rule: Heat.** "+2 Heat is below a MINOR threshold step" is meaningless; MINOR thresholds are every 10 Heat. Say "+2 Heat, 20% of a minor step".
6. **NIT, template: the Voice enum is stated as STREET_MERC (1)** while Voice order is NARRATOR, STREET_MERC... so 1 is correct. OK. The `foreshadows: &""` is fine.
7. **NIT, text: the notes cite "Billing Loop"** (an event name not provided) and the Ghost hook "strips resistance" (it does). The "Billing Loop" reference may be an invented event; remove it.
8. **NIT, fallback: the draft concedes there is no data-only fallback.** Acceptable, but also give the one data-only remedy: replace choice 1 with an immediate "+HP-cost trade" if N16 slips.

## Concrete fixes

- **Choice 3 replacement:**
  - label: "Broadcast the glitch across the district (-15 Cycles)"
  - next_combat_overrides (new): next 2 combats: enemy HP -20% (percent of its max); enemy damage +25% (tier-independent buff, per R2). Duration: next 2 combats, including elite and Rack fights.
  - The player now trades a shorter fight for more intake. This is a real cost at any tier.
- **Choice 1 replacement:**
  - next_combat_overrides (new): next 1 combat: enemy starts Frozen AND enemy HP -15%. Drop the resistance line, or add "if resistance > 0".
  - Keep hp_cost 8.
- **Numbers line:** "+25% enemy damage over 2 fights at 2-6 intake per turn is about 3-6 extra HP lost at T1-T2."
- **N-dependency line:** "N16; the enemy HP percent change reads the enemy's own max HP (R2 percent mode); no N2 dependence."
- **Heat line:** replace with "+2 Heat, one fifth of a MINOR step."
- Delete the "Billing Loop" comparison.

## Keep
- Four choices with distinct currencies (HP, Cycles plus Heat, Cycles plus tempo, nothing).
- Chips in the next combat's HUD so overrides are visible before commit.
- A deterministic, fixed-value design with no RNG, persisted in the run state.

## Q:
- Q: Should boss and mini-boss fights be exempt from "enemy HP -X%" overrides (it would break the phase budgets of R2)? I suggest yes.
- Q: Does "next N combats" count an interrupting raid interlude? I suggest no.
