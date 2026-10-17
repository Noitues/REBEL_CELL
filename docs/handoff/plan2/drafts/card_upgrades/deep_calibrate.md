<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__deep_calibrate; status ok; tokens in 5191 cache-write 0 cache-read 32585 out 1051; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: deep_calibrate

1. **Role:** A once-per-combat RAM-saver for nudge-heavy turns. It pays off most with two or more extra nudges, when a turn needs a precise multi-tick correction (steering a needle, dodging a hazard) and the free nudge isn't enough.

2. **Upgraded card: Deep Calibrate+** (one + level only; there is no reason for a second.)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (60 → 90).
- **Text:** "Your next 4 nudges this turn are free. Nudges ignore 1 resistance this turn. Exhaust."
- **Effects, in order:**
  1. CUSTOM, target SELF (0), handler `calibrate_handler`, amount 4. Free-nudge counter, same as today.
  2. CUSTOM, target SELF, handler `calibrate_handler`, amount 1, `ring_scope` OUTER. This is the new rider: the first tick of each nudge is absorbed by 0 resistance, i.e. each nudge strips 1 resistance from what it must pay. See the Q below.
- **Exhaust:** true. **wheel_target:** 0 (OWN).
- **Why this shape:** Two bigger-number steps (3 → 4 free nudges) plus a narrow rider. The rider covers the card's one weakness, which is that free nudges still get absorbed by Compliance Lock and Weight-style resistance. It is not a strict upgrade: the Cycle cost is 50 % higher, and the card stays exhausting. A player with no resistance on the field gets only +1 nudge for +30 Cycles, so the base card stays the right buy in light-resistance runs.

3. **Interplay:**
- **Corruption (R9):** Free nudges are 0 RAM, so a CORRUPTED slice's 2× multiplier multiplies 0. The + card is the clean answer to a heavily corrupted wheel, as long as the free-nudge counter is consumed before the ×2 is applied.
- **Variable slice sizes (R10-R12):** Sub-tick precision on 3-4-tick slices needs more nudges, so the 4th free nudge is worth more once N12 exists.

4. **Data:**
- `amount` 3 → 4 on fx0.
- Add fx1 (CUSTOM, same handler) with the resistance-ignore rider.
- `cycle_cost` 60 → 90.
- Description changed.
- **New system:** none from N1-N20. The handler needs a second parameter (an `ignore_resistance` flag, amount 1). Data-only fallback: drop the rider and ship a plain 4-nudge version, which is a weaker sidegrade.

5. **Q:**
- Q: Should the rider ignore resistance on the free nudges only, or on all nudges this turn, paid ones included? Free-only is cleaner to preview, and I lean that way.
- Q: Does the 4th free nudge still read correctly under N7 nudge-lock effects (the lock takes precedence, and the card is not refunded)?
