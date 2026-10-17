<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__gear_shift; status ok; tokens in 5093 cache-write 0 cache-read 32585 out 1201; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: gear_shift

1. **Role**: A cheap, precise inner-ring repositioner. It is a 1-RAM, fixed-size step that sits between Inner Drift (3 ticks, 0 RAM) and Ratchet (8 ticks, 2 RAM). It exists so you can reach a specific inner segment without paying for a large move.

2. **Upgraded card: Gear Shift+** (one level is enough; there is no +2)
   - RAM cost: 1 (unchanged)
   - Cycle cost multiplier: ×1.5 (50 → 75)
   - Text: "Move your inner ring 5 ticks in a direction you choose."
   - Effect list: one EffectData
     - type NUDGE (5)
     - target OWN_WHEEL (1)
     - ring_scope INNER (1)
     - amount 5
     - direction: **chosen (CW or CCW)**, a new field (see §4)
     - status NONE
     - duration 0
   - Exhaust: false
   - wheel_target: OWN (0)

   **Why this upgrade:** the base card only goes clockwise. A segment you want 5 ticks counter-clockwise is 25 ticks clockwise away, so it is out of reach. A choice of direction is a wider-target rider, not a bigger number. The inner ring has 3 segments of 10 ticks, so a 5-tick step goes ±5 from the current alignment. The + version reaches 2 of the 3 half-step alignments instead of 1, which is a real gain in reach.

   **Why it isn't a strict upgrade:** it costs more Cycles, and it adds no raw power. Inner Drift (0 RAM, 3 ticks) and Ratchet (2 RAM, 8 ticks) keep their jobs. I chose direction over a RAM cut because 0-RAM would collide with Inner Drift.

3. **Interplay**: Inner-ring segments act as modifiers. Corruption now doubles RAM when the acting pointer reads a CORRUPTED slice, so Gear Shift+ costs 2 RAM there. A reliable ±5 step lets you reposition the ring without relying on the outer slice. It fits "cheap, predictable" play, and previews stay exact because the direction is chosen before the action is staged. Variable slice sizes don't affect it, since the inner ring stays at 3×10.

4. **Data**
   - `cycle_cost` 50 → 75
   - `display_name` "Gear Shift+", `description` updated
   - `id` `gear_shift_plus`, flagged as the upgrade of `gear_shift`
   - The direction choice has no data-only version. `EffectData` has no direction field, and the base card's sign is implied by a positive amount. **Data-only fallback:** `amount = ±5` on two sibling effect entries gives a choice between two variants only if card-play UI supports picking; otherwise it needs **NEW: chosen-direction nudge** (a `direction_choice` bool on `EffectData`, or a CHOSEN slot, plus preview for both outcomes). Size S.
   - No upgrade-link field exists yet. It depends on the card-upgrade pass (G5), and the upgrade's offering rules fall under N18.

5. **Q:**
   - Should the upgrade also allow a 5-tick nudge in either direction on the outer ring (a wheel-scope wider target), or stay inner-ring only?
   - Is a chosen-direction input acceptable on cards, or should direction stay fixed on all cards, with upgrades adding RAM-efficiency instead?
