<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__strip; status ok; tokens in 5072 cache-write 0 cache-read 32585 out 1278; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: strip

1. **Role:** Cheap, reliable resistance removal on the enemy wheel. It opens the way for Flip, Respin and full-value spins against resistance-holding enemies. It is a neutral card, and ghost and phantom lean on it.

2. **Upgraded card: Strip+** (one level is enough; no Level II needed)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5, so 55 → 83.
- **Text:** "Remove 3 resistance from the target. If that clears all its resistance, your next nudge this turn is free."
- **Effects (EffectData):**
  1. MODIFY_RESISTANCE, target TARGET_WHEEL, amount −3, ring_scope OUTER (as today), no status, duration 0.
  2. CUSTOM rider: if the target's resistance is 0 after effect 1, grant 1 free nudge this turn. Fallback with no new code: reuse the existing free-nudge grant that `calibrate` uses (a GAIN-free-nudge effect, amount 1), conditioned on the resistance state. The condition is the only new piece.
- **Exhaust:** false.
- **wheel_target:** ENEMY (1), unchanged.

**Why this shape:** 3 is the bigger number, and it is the sweet spot. Typical authored resistance is 1–3 (Weight 1/3, Compliance Lock 2), so Strip+ clears most of them in one card. The rider rewards finishing the strip: you pay 1 RAM and get the free nudge back, so on a resistance-2 target the card is effectively free. It is a sidegrade against Deep Strip (RAM 2, −4): Deep Strip still wins on high resistance (Meridian P1 Weight 3 is fine, but boss-level 4+ is not). Strip+ also does nothing on an enemy with resistance 0, whereas base Strip is just a dead card there. Not strictly dominant: it costs more Cycles, and the rider is a conditional bonus, not a flat one.

3. **Interplay:**
- A refunded nudge is worth more when corruption doubles RAM on a corrupted slice, because it saves a 2 RAM nudge.
- The rider fires only when the resistance really reaches 0. Compliance Lock restoring each turn, or a Weight hub that re-applies, makes Strip+ a one-turn window, which suits phase play.
- No interplay with slice sizes or parasites.

4. **Data:**
- `amount`: −2 → −3.
- `cycle_cost`: 55 → 83.
- `description`: updated.
- New second effect (conditional free nudge).
- Needs the condition "resistance == 0 after this effect". **Fallback, data-only:** drop the rider and keep just −3 for the 1.5× price. It is still a valid bigger-number upgrade. With the rider it needs NEW: conditional effect gate (a small `condition` field on EffectData, which N6 listeners could share). Check whether the interpreter already has a resistance-state query.
- `id`: `strip_plus`, with `upgrade_of = &"strip"` (NEW: upgrade_of field, owned by the card-upgrade pass).
- Upgrade-pass carry-over: the class files referencing `strip` (ghost, phantom) must resolve to the base card, and the upgrade is chosen at upgrade time.

5. **Q:**
- Q: Should the free-nudge rider trigger only on an exact clear to 0, or also when resistance was already 0 (which would let Strip+ double as a cheap nudge refund)?
- Q: Do the ghost and phantom "first nudge ignores resistance" hooks make Strip+ redundant for them, so should the rider be class-neutral at all?
