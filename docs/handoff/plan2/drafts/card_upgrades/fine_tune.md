<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__fine_tune; status ok; tokens in 5190 cache-write 0 cache-read 32585 out 1243; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: fine_tune

1. **Role:** The cheap, flexible 1-RAM precision tool. It buys two ticks of correction on one ring, enough to move Good to Perfect or Weak to Good, and it is shared by 8 classes.

2. **Upgraded card: "Fine Tune+"** (one level; a second would add little).
- RAM cost: 1 (unchanged).
- Cycle cost multiplier: ×1.5 (50 → 75).
- Text: "Two ±1 nudges on one ring. The first is free of resistance."
- Effects, in order:
  1. NUDGE, target OWN_WHEEL (2), ring_scope OUTER or INNER (chosen by the action), amount 1. This nudge ignores resistance. It is the old card's nudge with a new rider.
  2. NUDGE, target OWN_WHEEL (2), same ring, amount 1, normal resistance rules.
- Exhaust: false. wheel_target: ANY (so it can also act on an enemy wheel; on an enemy wheel the first nudge ignores its resistance, like Jam).
- Justification for the wider target: a wider target plus a rider is a sidegrade, not a strict improvement. The + version is the same price and does the same work, but it also plays as a cheap, single-tick Jam. That puts it in the same RAM tier as Ghost Step (1 RAM, two nudges ignoring resistance), where Ghost Step still wins on bulk. The cost is the 50 % higher Cycle price and the extra target-selection step.
- The existing action layer supplies direction and ring per nudge, so each nudge is one choice, as before.

3. **Interplay:**
- **Tick quality:** with variable slice sizes, a 4-tick slice has no Perfect. The + version's extra reach (ANY target) can also steer an enemy needle onto a WEAK sub-tick of an uneven slice. This is exactly the "deny Medicine's Perfect" play in Genome Core P2, and it avoids Compliance Lock's resistance cost on the first tick.
- **Corruption:** the card's cost is 2 RAM when the acting pointer reads a CORRUPTED slice, as for any card. The + version does not change this.

4. **Data:**
- `wheel_target = 2` becomes the ANY value of WheelTarget (check the enum: OWN=0, ENEMY=1, ANY=2; the current file already uses 2, so it is unchanged). Hence the field that actually changes is the effect list.
- Split the single `fx_nudge` (amount 2) into two sub-resources, each amount 1.
- Add `ignores_resistance: bool` to the effect, or reuse the Jam/Ghost Step mechanism (check how `jam.tres` expresses it; if it uses a CUSTOM handler, reuse that).
- `cycle_cost` 50 → 75.
- New system: none, if the mechanism exists. Otherwise it needs a data-only `ignore_resistance` flag on NUDGE (NEW: nudge flag, S).
- `display_name` "Fine Tune+", description updated. Add a `base_id = &"fine_tune"` / `upgraded` link field if the upgrade pass adds one (NEW: card upgrade link, outside N1–N20).

5. **Q:**
- Q: Does the first nudge's resistance bypass overlap too much with Ghost Step, so that the Ghost-class benefit is diluted? An alternative is a pure +1 nudge (3 total) at a 2-RAM cost.
- Q: Should the + version be shop-only upgrades (Rest node: Workshop) or per-class reward upgrades, given that 8 classes share it?
