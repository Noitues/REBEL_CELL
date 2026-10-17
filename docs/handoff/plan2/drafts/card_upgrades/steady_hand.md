<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__steady_hand; status ok; tokens in 5149 cache-write 0 cache-read 32585 out 1162; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: steady_hand

1. **Role**: A neutral setup card for RAM economy. It pays off when the player has aimed the wheel for a Perfect, which rewards precision (pillar 1) and funds next turn's nudges and cards.

2. **Upgraded card: Steady Hand+** (one level is enough; it's a single-trigger card)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (55 → 83), since it is a stronger reward.
- **Text:** "If any of your slices resolves Perfect at end of turn, +2 RAM next turn. If it is Good, +1 RAM next turn."
- **Effects (one CUSTOM, same handler, new parameters):**
  - type CUSTOM (24), target SELF (0), amount 2 (Perfect payout), custom_handler `steady_hand_handler.gd`.
  - `multiplier` is not reused. The Good payout is a second parameter, so add `amount_good = 1` (NEW field, below). Data-only fallback: a second `EffectData` entry with the same handler, amount 1, and a `min_tier = GOOD` flag read by the handler. The handler would need to pick the best tier across entries, not stack them.
- **exhaust:** false. **wheel_target:** OWN (0).
- **Why this upgrade:** it's a rider (a consolation payout), not a bigger Perfect payout. A bigger payout would push RAM past the 12 cap and help only skilled lines. The Good payout makes it reliable but pays less than the base Perfect case, so it stays a precision card.
- **Sidegrade check:** it never pays less than the base card. The cost is only the Cycle price, which is acceptable because the base is a weak shop card (55). The RAM payout is still capped by max RAM 12, so the card can't snowball.

3. **Interplay**
- **Tick quality / slice sizes (R11):** 4-tick slices have no Perfect, so the base card never pays there. The + version still pays 1 RAM on a Good, which fixes that dead case. "Calibrated" Firmware, which raises every sub-tick one tier, turns the +1 into +2 on those slices.
- **Corruption as double RAM (R9):** the end-of-turn read looks at the resolving slice's tier, not at the slice's status. A CORRUPTED slice that lands Perfect still pays, which partly offsets the 2× RAM tax.
- **Multiple pointers:** the handler should read the best tier among your wheel's pointers only (see Q).

4. **Data**
- `display_name`: "Steady Hand+".
- `cycle_cost`: 83.
- `description`: new text.
- `effects`: the existing entry keeps amount 2. Add a second `EffectData` (CUSTOM, same handler, amount 1) marked as the Good-tier payout. This is the fallback and needs no new system.
- Handler change: read all entries and pay the highest tier reached, never both.
- Preferred, small: NEW field `EffectData.min_tier` (S). Without it, use the amount order convention in the handler.
- No N# dependency.

Q: Should extra pointers on a Twin Pointer wheel pay once (best tier) or per pointer? I chose once, to protect the 12 RAM cap.
Q: Should the + version also show its expected payout in the preview chip ("+2 RAM next turn")? That's a UI task, with no rule change.
