<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__deep_strip; status ok; tokens in 5111 cache-write 0 cache-read 32585 out 1271; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: deep_strip

1. **Role:** Shared-pool utility that strips enemy spin resistance (4 for 2 RAM), so Flip, Respin and Spin can work and nudges stop being absorbed. Resistance is the enemy's anti-manipulation wall.

2. **Upgraded card: Deep Strip+** (one level; no further levels needed)
- **RAM cost:** 2 (unchanged). **Cycle cost:** ×1.4 (65 → 91).
- **Text:** "Remove 6 resistance from the target. If that clears all its resistance, your next nudge this turn is free."
- **Effects:**
  1. MODIFY_RESISTANCE, target TARGET_WHEEL, amount −6, amount mode FLAT, ring_scope OUTER (as today), status NONE, duration_turns 0.
  2. Conditional rider: if the target's resistance is 0 after effect 1, grant 1 free nudge (same grant as Calibrate, but a single one). Implemented as an effect of type CUSTOM with a handler. No data-only form exists.
- **Exhaust:** false. **wheel_target:** ENEMY (1), unchanged.
- **Why this shape:** it is a bigger number plus a rider that rewards exactly the job the card already does (open the wheel, then act on it). Resistance 4–6 is common (Compliance Lock 2, Weight 3, Hub passives), so −6 clears nearly every normal and elite wheel. The free nudge only triggers on a full clear, so on stacked-resistance bosses it is just a +2 strip.
- **Not strictly dominant:** the Cycle cost rises 40%. Against resistance 1–2, Strip (1 RAM, −2) is still the better buy. The + only pays off against Weight 3+ or a bundle (hub + trait).

3. **Interplay:**
- Resistance-gated boss rules (Compliance Lock blocking Flip and Respin) become a one-card unlock. The free nudge then covers the fine-tune after a Flip or Spin.
- With variable slice sizes and uneven pointers, the free nudge matters more: a 1-tick correction decides Perfect vs Good on 3–4-tick slices.
- Corrupted slices double RAM, so the free nudge is worth 2 RAM when your pointer reads a corrupted slice. The rider offsets that tax.
- A restored-each-turn resistance trait (Weight) means the strip must be played the same turn it is needed, so the rider is a same-turn bonus only.

4. **Data (vs current .tres):**
- `amount` −4 → −6.
- `cycle_cost` 65 → 91.
- `description` updated.
- Append a second effect of type CUSTOM with `custom_handler` = a new "grant free nudge if target resistance is 0" script. A data-only fallback is to drop the rider and ship plain −6 at 2 RAM; the cost is that the card then dominates Deep Strip at a minor Cycle price.
- Dependencies: no N# required. It uses the existing CUSTOM path. The preview must show "free nudge" when the strip would clear resistance; the preview has to evaluate the same condition deterministically.
- Cards in the +version need a `base_id` / upgrade link field on CardData (NEW: card upgrade link, unless the card-upgrade pass already defines one).

5. **Q:**
- Q: Should the free-nudge rider trigger when resistance was already 0 before the play (a "free nudge" on a no-op strip)? I propose no (it requires removing at least 1), to prevent card cycling abuse.
- Q: Should the amount be a PERCENT of the target's max resistance for Heat-scaled +1 resistance modifiers, or stay FLAT?
