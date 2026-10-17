<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__flip_switch; status ok; tokens in 5110 cache-write 0 cache-read 32585 out 1142; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: flip_switch

1. **Role:** A neutral, whole-wheel rearrangement tool. Flip mirrors your own wheel, so the slice opposite the pointer arrives under it and the slice order reverses. It is a deterministic "bring the far slice to the front" button that costs no nudge ticks.

2. **Upgraded card: Flip Switch+** (one + level is enough; the card has one lever, cost)
- **RAM cost:** 1 (was 2).
- **Cycle cost multiplier:** 1.5× (60 → 90), which prices the 1-RAM cut.
- **Text:** "Flip your own wheel. Then one free ±1 nudge this turn."
- **Effects:**
  1. FLIP, target OWN_WHEEL, ring_scope WHOLE_WHEEL (unchanged).
  2. MODIFY_FREE_NUDGE-style rider, expressed with the existing Calibrate mechanism: grant 1 free nudge, target SELF, amount 1. This is the same effect Torque Wrench uses ("gain a free nudge").
- **Exhaust:** false. **wheel_target:** OWN.

**Why this shape:** A flip lands you on the mirrored tick, which is often 1–2 ticks off a centre. The rider covers that error, so the card's job (set up a precise landing) works more often. The RAM cut alone would make it a strict upgrade. The extra Cycle cost and the unchanged flip keep it a sidegrade: Snap+ and Lock On still do a more reliable single-slice align. The free nudge is not tied to the played-card count, so it can't chain. It does stack with Calibrate or a first free nudge only as +1 nudge, never as an extra card draw.

3. **Interplay:**
- **Variable slice sizes (N12, R11):** Flip maps tick t → (2p + 15 − t) mod 30. With uneven slice sizes the mirrored landing is rarely a centre, so the free nudge matters more. A 4-tick slice has no Perfect anyway.
- **Corruption as double RAM (R9):** the rider is a card effect, not a nudge spent on a corrupted slice. If the pointer reads a CORRUPTED slice after the flip, the free nudge removes the 2× RAM penalty for that first nudge only, and the card pairs well with Cleanse.
- **Resistance:** this affects the enemy side only. Flip on your own wheel is unaffected.

4. **Data:** changes from the current .tres:
- `ram_cost` 2 → 1.
- `cycle_cost` 60 → 90.
- `description` updated.
- Add a second EffectData, `type = 3` (FLIP stays at index 0). The free-nudge effect needs a grant in the interpreter, which Calibrate and Torque Wrench already use. If it is not an existing EffectType, **NEW: free-nudge grant effect** (data-only fallback: reuse the Torque Wrench handler via `custom_handler`).
- Add `id = &"flip_switch_plus"` and a name field. No other new systems.

5. **Q:**
- Should the + version keep the base card's reward-pool presence, or appear only as an upgrade at Workshop/Rest nodes (D4)?
- Does the free nudge need a "this turn only, unused expires" rule to stay deterministic across rewinds? I propose yes.
