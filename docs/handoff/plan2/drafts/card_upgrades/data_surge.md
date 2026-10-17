<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__data_surge; status ok; tokens in 5104 cache-write 0 cache-read 32585 out 1243; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: data_surge

1. **Role**: Neutral hand-refill. It converts 2 RAM into card volume, so a turn can take more nudges, spins and defense before End Turn.

2. **Upgraded card**: **Data Surge+** (one level only; there is no need for a second).
- RAM cost: 2 (unchanged).
- Cycle cost multiplier: ×1.5 (65 → 98, rounded to 100).
- Text: "Draw 3 cards. Gain 1 RAM."
- Effects, in order:
  1. DRAW_CARDS (17), target SELF, amount 3. This is unchanged.
  2. GAIN_RAM, target SELF, amount 1, amount_mode FLAT (N1). It has no ring_scope, status or duration (instant). With N1 absent, the existing int `amount` already gives FLAT behavior.
- Exhaust: false (unchanged).
- wheel_target: OWN (0, unchanged).
- Why this rider: a bigger draw (4) would pile up unplayable cards under the 5-card hand and the RAM max of 12. A cost cut to 1 would make it a strict upgrade of Pull. The +1 RAM rider makes the card net cost 1, which is the same as "draw 3 for 1" but keeps the printed cost at 2. The two differ in one way. The printed 2 still needs 2 RAM on hand, and the refund only arrives after the draw. So the card stays a mid-turn decision, not a free play.
- Not a strict upgrade at every cost point:
  - It costs more Cycles.
  - At 1 RAM or less on hand it is still unplayable, where a hypothetical "cost 1" version would be playable.
  - Overflow is wasted: the refund is lost at the 12 RAM cap.
  - Net, it is a sidegrade for RAM-starved decks and a small upgrade for the rest.

3. **Interplay**:
- Corruption as double RAM (R9): the card is played from the hand, not from a slice, so it is not taxed. It pays for the doubled nudge and card costs on CORRUPTED slices, so it is the natural answer to Genome Core P2–P4.
- Variable slice sizes (N12) and tick quality: the extra draws find the Snap, Lock On and nudge cards that fix a narrow 3- or 4-tick slice.
- Parasite ring RAM drains (Meridian Packages): the +1 RAM partly offsets a 2 RAM drain.

4. **Data**:
- Changed fields: `id` becomes `data_surge_plus`, `display_name`, `description`, and `cycle_cost` 65 → 100. The `effects` array gets a second sub_resource (GAIN_RAM = 14, target 0, amount 1).
- Check the type id: 14 is GAIN_RAM, from the enum count (DEAL_DAMAGE 0, … GAIN_RAM 12). Use the named enum value, not a literal, when authoring. In the file's own numbering DRAW_CARDS is 17, so GAIN_RAM is 12.
- New systems: none. N1 is optional because the amount is a FLAT int.
- Upgrade linkage: `upgrade_of` / `upgraded_from` is not in CardData. NEW: card upgrade link (a field on CardData, or a pass-level table). Until then it is a standalone card with `offered = false`.

5. **Q:**
- Q: Should the refund be conditional (only if you drew 3 cards, so an empty-pile reshuffle still pays) or flat as drafted?
- Q: Is a flat Cycle multiplier ×1.5 right for every upgrade, or does each card get its own price?
