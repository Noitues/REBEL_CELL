<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__inner_snap; status ok; tokens in 5116 cache-write 0 cache-read 32585 out 1151; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: inner_snap

1. **Role.** A cheap, precise inner-ring realignment: it fixes the ring modifier when the inner segment sits off-center, so Pierce, ×2 or Corrupt applies cleanly. It is a utility card for classes whose payoff lives on the inner ring (Breaker's ×2 / Pierce).

2. **Upgraded card: Inner Snap+**
- RAM cost: 0 (from 1).
- Cycle cost multiplier: ×1.5 (90).
- Text: "Snap your inner ring to the nearest center. Draw 1 card if it was already centered." (Alternative considered and rejected: exhaust-free repeat. A rider is better.)
- Rarity stays 1. wheel_target stays 0 (OWN). Exhaust: false.
- Effects:
  1. SNAP_TO_CENTER, target OWN_WHEEL, ring_scope INNER (unchanged).
  2. DRAW_CARDS, target SELF, amount 1, **conditional: only if the snap moved 0 ticks**.

Why a 0-RAM rider rather than a bigger number: the card has no number to grow. A 1-RAM card that costs 0 is the standard cost-reduction upgrade. The draw rider only fires when the snap was unneeded, so the card is never dead and never a pure cantrip.

It is not a strict superset at every point: the + costs 50% more Cycles in the shop, and the draw is a dead rider whenever you actually needed the snap. In a deck that never touches the inner ring it is still a free cycle card, which is fine because the conditional keeps it weaker than Pull. Because the 1-RAM and 0-RAM versions are not in competition for slots, a pure cost reduction is acceptable.

3. **Interplay.**
- Inner ring segments are 10 ticks each, so "centered" is unaffected by variable outer slice sizes (N12). If the inner ring is later redesigned (G1), the snap target must follow the new segment geometry.
- A 0-RAM card played on a CORRUPTED slice costs 0 × 2 = 0, so corruption does not tax it. That is a mild but real synergy for corrupted decks.

4. **Data.** Changes from the current `.tres`:
- `ram_cost` 1 → 0
- `cycle_cost` 60 → 90
- `display_name` "Inner Snap+"
- `description` updated
- `id` = `inner_snap_plus` (a separate resource, upgrade pointer from the base card)
- add the second EffectData (DRAW_CARDS, amount 1)

New system: the conditional draw needs a "only if the previous effect moved 0 ticks" condition. There is no such field on EffectData. NEW: effect condition (`condition_prev_zero_move`). Data-only fallback: an unconditional "Draw 1" with cost 0 would make it a free cantrip, which is too strong; the fallback is to ship the cost reduction alone (RAM 0, no rider) at ×1.25 Cycles. Alternatively, `CUSTOM` with a `custom_handler` script avoids a schema change.

5. **Q:**
- Q: Do upgraded cards need a general conditional-effect field (reusable by other + versions), or should each use a CUSTOM handler?
- Q: Should the snap preview show "0 ticks, draw" on hover so the rider is legible before playing?
