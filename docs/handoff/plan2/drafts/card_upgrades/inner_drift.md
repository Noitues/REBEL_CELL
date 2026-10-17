<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__inner_drift; status ok; tokens in 5125 cache-write 0 cache-read 32585 out 1101; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: inner_drift

1. **Role:** A free (0 RAM), small, precise inner-ring nudge-by-spin. Cheap tuning of the outer slice's modifier segment. It is the low end of the inner-ring ladder: Inner Drift 3, Gear Shift 5, Ratchet 8.

2. **Upgraded card: "Inner Drift+"**
   - **RAM cost:** 0 (unchanged).
   - **Cycle cost multiplier:** ×1.5 (cycle_cost 50 → 75).
   - **Text:** "Move your inner ring 3 ticks in either direction."
   - **Effects (1):**
     - `type` NUDGE-style ring move, as today's type 5 (SPIN scope INNER as authored); target OWN_WHEEL (1); `amount` 3; `ring_scope` INNER (1); no status, no duration.
     - New field: `direction_choice` = EITHER (the player picks clockwise or counter-clockwise at play time).
   - **Exhaust:** false. **wheel_target:** OWN (0).
   - **Why this upgrade:** the base card's weakness is the fixed direction. A segment 3 ticks away is reachable only one way, and the other 7 ticks are out of reach. Choosing direction doubles the reachable inner positions at zero cost. The number stays 3, so it is not a bigger Gear Shift, and the cost stays 0.
   - **Sidegrade check:** it does not strictly dominate. It is still 3 ticks, so it is useless against a far target; Gear Shift and Ratchet stay relevant for 5 and 8. The inner ring has only 3 segments of 10 ticks, so a ±3 move reaches 2 of the 3 positions at best. The upgrade pays off mainly when the segment boundary is within 3 ticks on the "wrong" side.

3. **Interplay:** The inner ring sets the modifier and precision is measured on the outer ring only, so this card never changes tier. It stays clean under variable slice sizes (N12), since inner segments are separate. Ring Lock still stops it only if the move is authored as a spin; as a ring move it ignores Ring Lock (keep the same rule as today).

4. **Data:**
   - Changed against the current .tres: `id` → `inner_drift_plus`; `display_name`; `description`; `cycle_cost` 50 → 75; `fx0` gains `direction_choice`.
   - **New field:** `EffectData.direction_choice` (CW_ONLY default / CCW_ONLY / EITHER), size S. Both players and UI need a direction prompt. This is not an N# system.
   - **Data-only fallback:** none that is exact. The nearest is two effects authored as "CHOSEN" variants, which is not supported. Alternative: ship as a separate card with amount −3 and "play one of two", which is wasteful.
   - Preview shows both outcomes before the choice. Deterministic, no RNG.

5. **Q:**
   - Q: Should direction choice become a general field for all spin cards (Twist, Whirl and so on), so it is no longer a feature unique to this +?
   - Q: Is a single "+" level enough, or does Inner Drift also get a second level that reaches 4 ticks?
