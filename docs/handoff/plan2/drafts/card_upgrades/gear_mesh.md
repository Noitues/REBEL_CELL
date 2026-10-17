<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__gear_mesh; status ok; tokens in 5199 cache-write 0 cache-read 32585 out 1291; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: gear_mesh

1. **Role**: A neutral, two-wheel set-up card. It moves your wheel and the target's wheel by the same amount in one play. It is the tool for lining up a good landing for you and a bad one for the enemy at once.

2. **Upgraded card: Gear Mesh+** (one level only; no second level is needed)
- **RAM cost:** 1 (was 2). **Cycle cost multiplier:** ×1.4 (65 → 91).
- **Text:** "Spin the target and your own wheel 5 ticks clockwise. If you already spun this turn, spin the target 2 more."
- **Exhaust:** false. **wheel_target:** ENEMY (1 in the file, kept as is).
- **Effect list:**
  1. SPIN, target TARGET_WHEEL, amount 5, ring_scope WHOLE_WHEEL (unchanged).
  2. SPIN, target OWN_WHEEL, amount 5, ring_scope WHOLE_WHEEL (unchanged).
  3. SPIN, target TARGET_WHEEL, amount 2, ring_scope WHOLE_WHEEL, conditional on "already spun this turn" (the same condition as Momentum's spin 2 / spin 5).
- **Why this choice:** I took a cost cut plus a small conditional rider. The cost cut is the main upgrade. At RAM 1 it competes with Torque Wrench, Jolt and Twist, so you can combine it with a card or nudge in the same turn. The rider is the Momentum condition, so it rewards sequencing and turns the second spin into a chain finisher.
- **Not strictly dominant:** the rider only pays when you spun earlier, and in that case it displaces the enemy's wheel by an extra 2 ticks. You may not want that, because it can push the enemy off a slice you wanted it to read. The Cycle cost is also +40 %. If you want to cancel the rider, a nudge can do it, at 1 RAM.

3. **Interplay**
- **Tick quality / slice sizes (R11):** the 5-tick spin keeps the same-slice shift on today's 5-tick slices, but on mixed sizes (3, 4 or 7 ticks) the same 5 ticks lands on different slices for each wheel. The card becomes a calculation, not an automatic "next slice". The +2 rider shifts by sub-tick, so on 4-tick slices it can move a landing from WEAK to GOOD.
- **Resistance:** the spin on the target is still reduced by resistance. The rider, being a separate effect, is absorbed first. Because Gear Mesh+ has two target spins, one against resistance 2 loses 2 of the first 5 and none of the rider.

4. **Data**
- **Changes in `gear_mesh.tres`:** `ram_cost` 2 → 1, `cycle_cost` 65 → 91, `description` updated, and one extra `EffectData` (`type = 6`, `target = 2`, `amount = 2`, `ring_scope = 2`) with a condition.
- **Dependency:** the conditional is the one new piece. Momentum already has an "already spun this turn" condition, so reuse it. Use `custom_handler` on the extra effect if the condition isn't generic in EffectData. This is not an N# system; it is a small NEW: conditional-effect field (`requires_spun_this_turn`). The fallback is data only: drop the rider and keep the RAM cut alone (RAM 1, cycle ×1.4).

5. **Q:**
- Q: Is the RAM 1 cost too cheap given that both wheels move in one play? Alternative: keep RAM 2 and make the rider unconditional.
- Q: Should the conditional reuse Momentum's check, or should "already spun" count the first free nudge and spins from Firmware?
