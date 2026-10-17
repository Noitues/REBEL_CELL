<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__counter_spin; status ok; tokens in 5100 cache-write 0 cache-read 32585 out 1400; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: counter_spin

1. **Role**: A cheap, precise counter-clockwise spin of 5 ticks. It is the mirror of Twist/Gear Mesh. It rotates a wheel (yours or the enemy's) one slice in the opposite direction, for a 1 RAM fix when the cheap clockwise cards overshoot.

2. **Upgraded card: Counter-Spin+** (one level only; the card is too simple for a second)
- **RAM cost:** 1 (unchanged)
- **Cycle cost multiplier:** ×1.5 (50 → 75)
- **Text:** "Spin a wheel 5 ticks counter-clockwise. If you already spun this turn, spin 8 instead."
- **wheel_target:** ANY (was 2; check `RC.WheelTarget` to confirm that 2 = ANY, since `EffectData.target = 2` is TARGET_WHEEL, so the existing .tres appears to mean "choose a wheel")
- **exhaust:** false
- **Effects (EffectData):**
  1. SPIN, target TARGET_WHEEL, ring_scope WHOLE_WHEEL, amount −5. This is unchanged.
  2. SPIN, target TARGET_WHEEL, ring_scope WHOLE_WHEEL, amount −3, conditional "already spun this turn". It must resolve on the same wheel as effect 1, which makes the total −8 on a combo.

   The condition is the same one Momentum already uses, so the conditional is reused, not invented.

**Why this and not a flat bigger number:** a straight −5 → −8 would only duplicate Backspin (−9, 2 RAM). A conditional rider keeps Counter-Spin as the cheap fine-tuning spin. It rewards the second spin of a turn, so it becomes a combo piece. It is a sidegrade: alone it does exactly what the base card does, so it does not dominate in every situation. It costs +25 Cycles more in the shop and is only better with a prior spin. Momentum already covers the clockwise side of this pattern, and the + version adds the counter-clockwise one.

3. **Interplay**
- **Variable slice sizes (R11):** 5 ticks no longer equals exactly one slice on wheels with uneven slices. A spin of −8 gives more reach on wheels of 3–4-tick slices, where it can skip two slices. Spin previews must show the landing slice and tier, as they always do.
- **Resistance:** enemy spin resistance still absorbs the first R ticks. The −8 version loses proportionally less, which is a small benefit against Weight enemies.
- **Satellites (R12):** a spin carries docked satellites with the host, so this behaviour is unchanged.

4. **Data**
- **Changed fields:** `id` → `counter_spin_plus` (or an `upgraded_from` link); `display_name`; `description`; `cycle_cost` 50 → 75; the effect list gains a second SPIN.
- **New system:** the conditional "if you already spun this turn" must be shared with Momentum. If it is currently hard-coded to Momentum, use `CUSTOM` with Momentum's handler, parameterised with the amounts (−3 extra). **NEW: generic `condition` field on EffectData** (e.g. `requires_prior_spin`). **Data-only fallback:** a CUSTOM handler reusing Momentum's logic.
- **Upgrade linkage:** N/A. The upgrade pass itself needs a field, `CardData.upgrade_of` or `upgraded_id`. **NEW: card upgrade link**, not covered by N1–N20.
- The referenced class files (botnet, hivemind) need no edits if the upgrade replaces the card in place.

5. **Q:**
- Q: Does the existing Momentum "already spun" flag count spins from other cards and from the free nudge (nudges are not spins), or only SPIN effects? The rule must be identical on both cards.
- Q: Should the spin combo apply on the first card of the turn when Counter-Spin+ follows an enemy-triggered spin (e.g. a boss listener), or only on player-played spins?
