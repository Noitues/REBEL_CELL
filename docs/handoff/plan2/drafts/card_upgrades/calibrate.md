<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__calibrate; status ok; tokens in 5138 cache-write 0 cache-read 32585 out 1267; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: calibrate

1. **Role**: a RAM-neutral nudge enabler. Spend 1 RAM to make the next 2 nudges free, which pays off when a precision line needs 3 or more nudges.

2. **Upgraded card: Calibrate+** (one level only; the card is too small to need more)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (55 → 83).
- **Text:** "Your next 3 nudges this turn are free. Nudges you make while a slice is CORRUPTED cost 1 less RAM."
- **Effect list** (one CUSTOM effect on the existing `calibrate_handler`; the rider is a handler flag, not a second effect):
  - type CUSTOM, target SELF (0), amount 3, ring_scope OUTER (unused), status NONE, duration_turns 0 (this turn, as today), `custom_handler` = `calibrate_handler.gd`.
  - The handler sets `free_nudges += 3` and the flag `calibrate_corrupt_relief = true`.
- **Exhaust:** false. **wheel_target:** 0 (OWN).

**Why this is a sidegrade and not a strict upgrade:** Deep Calibrate already gives 3 free nudges for 1 RAM, but it exhausts. Calibrate+ matches its number and stays repeatable, so it overlaps with Deep Calibrate. The corruption-relief rider is what differs: it makes the card a counter to the corruption tax rather than just a bigger number. The Cycle price rises to compensate. The card is weaker than the base card only in cost (83 vs 55 Cycles).

3. **Interplay**
- **Corruption as double RAM (R9):** a nudge on a CORRUPTED slice costs 2× RAM. Free nudges from the base card presumably still zero the cost (confirm in the handler). The rider covers paid nudges taken after the free ones run out, so a CORRUPTED slice costs 1 RAM instead of 2 for the rest of the turn. Flat reduction, minimum 0.
- **Variable slice sizes (R11):** 4-tick slices have no Perfect, and 3-tick slices have a one-tick Perfect, so precise lines often need 3 nudges. The third free nudge matters most there.
- The rider does nothing against parasite or status effects; it is purely about RAM.

4. **Data**
- `amount`: 2 → 3.
- `cycle_cost`: 55 → 83.
- `description`: updated.
- The upgraded card needs its own file, e.g. `calibrate_plus.tres` with `id = &"calibrate_plus"`, and an upgrade link such as `upgrade_of = &"calibrate"`. That link field does not exist yet: **NEW: card upgrade link**.
- The handler needs a small change: read `amount` for the free-nudge count, add the relief flag, and make the RAM cost path in `combat_resolver` consult the flag. The flag is only meaningful once R9's corruption RAM cost exists (**N9**).
- **Fallback without N9:** ship the number change only (3 free nudges, exhaust false, Cycles ×1.5) and drop the rider.
- Class files overclocker and rigger reference the card by id, so they need a swap or an upgrade path once the link field exists.

5. **Q:**
- Q: Does a free nudge from Calibrate on a CORRUPTED slice cost 0 or 1 under R9? Without that ruling the rider's value is unclear.
- Q: Is the + version too close to Deep Calibrate? Should it instead keep 2 free nudges and gain only the corruption relief, so it stays below Deep Calibrate on raw nudge count?
