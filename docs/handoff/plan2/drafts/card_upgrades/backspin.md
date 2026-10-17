<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__backspin; status ok; tokens in 5122 cache-write 0 cache-read 32585 out 1155; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: backspin

1. **Role:** Heavy counter-clockwise spin (9 ticks, 2 RAM). It is the only big CCW repositioning in the shared pool, and the mirror of Heavy Spin. It sets up a landing 9 ticks away when nudges can't reach.

2. **Upgraded card: Backspin+** (one level; a second would add nothing)
- RAM cost: 2 → **1**.
- Cycle cost multiplier: ×1.5 (60 → 90).
- Text: "Spin a wheel 9 ticks counter-clockwise. If it is your own wheel, gain a free nudge this turn."
- Effects:
  1. SPIN, target OWN_WHEEL/TARGET_WHEEL (as today, `wheel_target` WheelTarget.ANY), amount −9, ring_scope WHOLE_WHEEL (unchanged).
  2. GRANT_FREE_NUDGE (the effect Torque Wrench uses for "gain a free nudge"), target SELF, amount 1. The rider applies only when the spin hit your own wheel (conditional on the spin's target, same as the rider on Torque Wrench).
- Exhaust: false. `wheel_target`: unchanged (ANY).

**Why this is a sidegrade-ish change and not strict dominance:** the cost cut is the main buff. The rider is small and only fires on your own wheel, so the card stays a reposition tool. It does not gain Torque Wrench's clockwise 5. The rider is worth about 1 RAM, so the + version is effectively a 2-RAM-value card for 1 RAM. That is the strength cap: nothing more is added (no draw, no wider target). Used on an enemy wheel it is just a cheaper Backspin, so the rider rewards the self-steer use.

3. **Interplay:**
- **Variable slice sizes / sub-tick maps (R11):** a fixed 9 ticks lands on odd sub-ticks of 4- or 7-tick slices. The free nudge gives the ±1 correction to reach a Perfect, which suits the new maps.
- **Corruption (R9):** a nudge on a CORRUPTED slice costs double RAM, but the free nudge is a free action, so it still pays out as a correction. Whether the 2× applies to a free nudge is Q1.
- **Resistance:** the spin's first R ticks are absorbed on enemy wheels as before. The rider only fires on your own wheel, so it ignores the absorption.

4. **Data:** against the current .tres, change `ram_cost` 2 → 1, `cycle_cost` 60 → 90, `description`, and add one EffectData (type RESPIN-free "grant free nudge" via the existing Torque Wrench handler, `amount` = 1). The conditional "own wheel only" needs either a `condition` flag on the effect or a CUSTOM handler. **No N# system required**; fallback is a plain CUSTOM handler if no condition field exists. The card needs an upgrade-link field (`upgrade_of`, or a `plus_id` on CardData) from the card-upgrades pass: **NEW: card upgrade link**.

5. **Q:**
- Q: Does a free nudge on a CORRUPTED slice still cost 1 RAM (open question 3 in §7)?
- Q: Should the rider also fire when the spin targets an enemy wheel, so the card has one rule instead of two?
