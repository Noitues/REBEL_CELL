<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__scrap_code; status ok; tokens in 5186 cache-write 0 cache-read 32585 out 1064; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: scrap_code

1. **Role:** A free cantrip that converts a card slot into a small RAM gain and a fresh draw (net: it cycles itself and nets +1 RAM). It is the neutral deck-thinning and smoothing filler. It exhausts, so it is single-use per combat.

2. **Upgraded card: "Scrap Code+"**
- RAM cost: 0 (unchanged)
- Cycle cost multiplier: ×1.5 (50 → 75)
- Text: "Gain 1 RAM and draw 2 cards. Exhaust."
- Effects:
  - fx0: type GAIN_RAM (12), target SELF, amount 1 (unchanged)
  - fx1: type DRAW_CARDS (17), target SELF, amount **2** (was 1)
- exhaust: true
- wheel_target: OWN (0), unchanged
- No other fields change.

**Why a bigger draw instead of more RAM or removing exhaust:** more RAM would make it a Cache clone (Cache: 0 RAM, +3 RAM, exhaust). Removing exhaust makes it an infinite engine. The draw stays the card's identity, and drawing 2 for 0 RAM nets +1 card against the slot it used. At Pull (1 RAM, draw 2) the + is a RAM-positive Pull that exhausts, so it doesn't dominate: Pull is repeatable, and the + is once per combat. The hand cap is 5, so the extra card matters most when the deck has been cycled. This is a mild sidegrade with a real Cycle price, not a strict upgrade across every cost point.

3. **Interplay:**
- Corruption as double RAM: the +1 RAM refund partially offsets a CORRUPTED-slice nudge tax, which makes it a better answer to the tax than the base card is. Drawing 2 also digs for Cleanse and Sanitize.
- Boss listeners (N6) that react to ON_CARD_PLAYED (e.g. Late Fee) see one play for two draws, which makes this a cheaper way to fish than playing two cards.

4. **Data:**
- `fx1.amount` 1 → 2
- `cycle_cost` 50 → 75
- `id` `scrap_code_plus` (or a `level` field on CardData if the upgrade pass adds one; this card has only one level)
- `display_name` "Scrap Code+"
- `description` updated to "Gain 1 RAM and draw 2 cards. Exhaust."
- No new systems. Data-only. The only new thing is a CardData upgrade link (`upgrades_to`, or an `upgraded` flag), which belongs to the card-upgrade pass, not to this card (NEW: card upgrade link, field only).

5. **Q:** Does the upgraded variant keep the same `id` plus a `plus` flag (cleaner for saves and Codex), or a separate resource with `upgrades_to`?
**Q:** Should the draw bonus respect the 5-card hand cap (overdraw is discarded), or can the hand exceed 5 mid-turn? Draw 2 on a full hand would otherwise be a dead rider.
