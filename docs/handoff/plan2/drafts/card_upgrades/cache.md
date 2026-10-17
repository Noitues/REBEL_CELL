<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__cache; status ok; tokens in 5085 cache-write 0 cache-read 32585 out 957; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: cache

1. **Role:** a free (0 RAM) RAM-engine card. It converts a hand slot into RAM for a bigger turn, and it exhausts so it cannot loop.

2. **Upgraded card: "Cache+"**
- RAM cost: 0 (unchanged).
- Cycle cost multiplier: ×1.5 (55 → 83, rounded). The upgrade is a bigger number, so it is priced above the base.
- Text: "Gain 4 RAM. Exhaust."
- Effects:
  - GAIN_RAM (type 12), target SELF (0), amount 4, FLAT, ring_scope OUTER (unused), status NONE, duration 0.
- Exhaust: true.
- wheel_target: OWN (0).

Justification for +1 and nothing more:
- RAM caps at 12 and a turn gives +4, so extra RAM beyond about 4 per card quickly overflows the cap.
- A rider such as a free nudge or a draw would turn it into Scrap Code or Calibrate, which are different cards.
- A cost reduction is impossible because it is already 0.
- Cache+ does not strictly dominate: it costs more Cycles, and it is still only worth playing when you have RAM headroom.

3. **Interplay:**
- Corruption as double RAM makes RAM much tighter on CORRUPTED slices. 4 RAM funds exactly two nudges or card plays on a corrupted landing, versus 3 RAM, which funds one and a half. This is the main reason the +1 matters.
- Pairs with Perfect-based RAM refunds (the Rigger hook). The Rigger gets the most from it.
- Variable slice sizes, tick quality, statuses and parasites do not touch it. Parasites that drain RAM make a stockpile slightly riskier, which is a fair tension.

4. **Data:** changes against the current .tres:
- `id`: `cache_plus` (or an `upgrade_of = &"cache"` field if the upgrade pass adds one; see Q).
- `display_name`: "Cache+".
- `description`: "Gain 4 RAM. Exhaust."
- `cycle_cost`: 83.
- Effect `amount`: 3 → 4.
- Everything else unchanged.
- No new effect or system, so it is data-only. Only an upgrade-link field would be new, and that belongs to the shared card-upgrade pass (NEW: card upgrade link).

5. **Q:**
- Q: Should RAM gains that overflow the 12 cap be refunded or wasted? If wasted, Cache+ is weaker late in a turn, which would argue for an "up to 4, min 1 after cap" rider.
- Q: Does the upgrade pass keep both versions as separate card ids in the deck, or swap in place with an `upgrade_of` link?
