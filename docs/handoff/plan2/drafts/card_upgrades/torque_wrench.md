<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__torque_wrench; status ok; tokens in 5256 cache-write 0 cache-read 32585 out 1060; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: torque_wrench

1. **Role:** Rigger's tempo-and-precision tool. It spins a wheel 5 ticks (exactly one slice step on a 5-tick wheel) and refunds a free nudge for the fine correction that follows, so a slice change plus a Perfect fix costs 1 RAM.

2. **Upgraded card: Torque Wrench+** (one level only; no need for a second)
- **RAM cost:** 1 (unchanged). **Cycle cost multiplier:** ×1.5 (70 → 105).
- **Text:** "Spin a wheel 5 ticks clockwise and gain 2 free nudges."
- **Effects (EffectData):**
  1. SPIN, target TARGET_WHEEL (2), amount 5, ring_scope WHOLE_WHEEL (2), unchanged.
  2. CUSTOM (24), target SELF (0), amount **2** (was 1), custom_handler calibrate_handler, unchanged.
- **Exhaust:** false. **wheel_target:** ANY/as today (2).
- **Why this rider:** it is the bigger-number option on the card's existing second half. It stays the same card, and it doesn't dominate everywhere. At 1 RAM, two free nudges are worth up to 2 RAM, so the card nets positive RAM only when you use both. A turn that needs one correction gains nothing over the base card and pays the higher Cycle price. That keeps the base version a fair pick for cheap decks.
- **Rejected:** a direction toggle (a new choice and a preview burden), and an RAM refund (it would make the card free, which is strictly dominant).

3. **Interplay:**
- **Variable slice sizes (R11):** the 5-tick spin only lines up with a slice step on 5-tick slices. On a 4- or 6-tick wheel it lands mid-slice and the free nudges become the fix, which makes the + version the better answer to uneven layouts.
- **Corruption (R9):** nudges after the spin are free regardless of whether the pointer then reads a CORRUPTED slice. Check that "free" overrides the 2× RAM cost; I propose yes, and the preview must show 0 RAM.
- **Resistance:** the spin loses its first R ticks to resistance on an enemy wheel, while the nudges are your own. Keep the order spin → grant so the preview is exact.

4. **Data:**
- **Changed fields:** `id` torque_wrench_plus (or an `upgraded` link), `display_name`, `description`, `cycle_cost` 105, `fx_nudge.amount` 1 → 2.
- **New systems:** none. This needs only that calibrate_handler already reads `amount` as the free-nudge count. If it hardcodes 1, that is a data-only handler fix (S). The same handler backs the overclocker card, which references this one, so the + version's behaviour should be checked for that class's tests.

5. **Q:**
- Q: Should free nudges granted by several cards stack additively (as Calibrate does now), or be capped per turn at 3?
- Q: Should the + version be cross-class, or Rigger-only like the base?
