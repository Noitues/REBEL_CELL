<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__parasite_pulse; status ok; tokens in 5135 cache-write 0 cache-read 32585 out 1218; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: parasite_pulse

1. **Role:** Botnet's single-target debuff. It halves the output of the enemy slice under your pointer, usually the slice that would hit you hardest, for 2 RAM and an exhaust.

2. **Upgraded card: Parasite Pulse+** (one + level only)
- **RAM cost:** 2 → 1.
- **Cycle cost multiplier:** ×1.5 (80 → 120).
- **Text:** "Pointed target slice gets a PARASITE (half output) and OUTPUT_DOWN ×1. Exhaust."
- **Effect list:**
  1. APPLY_STATUS, target POINTER_TARGET, status PARASITE, slice_pick UNDER_POINTER, duration 0. This is the same as today.
  2. APPLY_STATUS, target POINTER_TARGET, status OUTPUT_DOWN (stacks 1, −25 %), slice_pick UNDER_POINTER, duration 0.
- **Exhaust:** true. Kept, so it stays a one-shot answer.
- **wheel_target:** ENEMY (1), unchanged.
- **Justification:** this is the "added rider" route, and the card gets cheaper. The slice ends at 0.5 × 0.75 = 0.375× output, not 0.5×. A sidegrade is possible, but a rider on top of a cost cut is not one. It still doesn't strictly dominate, because:
  - the higher Cycle price (120 vs 80) makes it a shop commitment;
  - a slice under ENCRYPTED absorbs only the first status. The second APPLY_STATUS lands on the same slice, so Encrypt blocks only the PARASITE and the OUTPUT_DOWN still lands, or vice versa depending on order. Put PARASITE first so the Encrypt is spent on the stronger status.

3. **Interplay:**
   - Under R8, PARASITE becomes a 2-stack OUTPUT_DOWN. The + card is then effectively 3 stacks, an OUTPUT_DOWN of −75 %. Check whether stacks are capped at 3 (Halcyon's Citation stacks to ×3).
   - If PARASITE moves to the Parasite ring as "anti-slices", this card keeps the status meaning and does not become a ring parasite. Botnet's drone "Parasite drone" text should be reconciled separately.
   - On a WEAK landing the status still applies (Q11 default), so the card is safe to use off-precision.

4. **Data:**
   - `ram_cost = 1`.
   - `cycle_cost = 120`.
   - Add a second sub_resource `EffectData` with `type = 4` (APPLY_STATUS) and `target = 2`.
   - Update `description`.
   - The upgraded card gets a new `id` (e.g. `parasite_pulse_plus`) with the same `class_id` and `exhaust`.
   - Depends on **N8/N9** (OUTPUT_DOWN status and ×N stacks). **Fallback:** apply PARASITE twice, or give the first effect `multiplier` 0.375. That needs `apply_status` to accept stacking, so it is not truly data-only. Without N8/N9 the cleaner fallback is the pure cost cut: 2 → 1 RAM, ×1.25 Cycles.

5. **Q:**
   - Q: Should hivemind (the other class referencing this card) get the same + version, or a variant with a different rider?
   - Q: Should the second status stack be preview-visible as a combined "×0.375" chip on the enemy slice?
