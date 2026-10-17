<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__lock_on; status ok; tokens in 5131 cache-write 0 cache-read 32585 out 1252; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: lock_on

1. **Role:** A free, one-shot Perfect. It is a burst-turn enabler for Perfect hooks, and it is the answer to "I'm one tick off" at 0 RAM.

2. **Upgraded card: Lock On+**
- RAM cost: 0 (unchanged).
- Cycle cost multiplier: ×1.5 (60 → 90).
- Text: "Move your outer ring to the nearest slice center (Perfect). Exhaust only if the ring moved 2+ ticks."
- Effects (the same single effect, with a conditional exhaust):
  - `fx0`: type SNAP_TO_CENTER (16), target OWN_WHEEL, ring_scope OUTER, amount 0, no status, duration 0. Unchanged.
  - New rider: `exhaust_unless_perfect`. If the pointer was already on a slice center (0 ticks moved), the card returns to the discard pile instead of exhausting.
- Exhaust: conditional (see above). Base `exhaust` stays true.
- wheel_target: OWN.

**Why this rider.** The base card is exhausted even when you needed it least. The + version rewards planning: you nudge or spin to put the pointer close, then Lock On+ finishes the job for nothing. A card that recycles on a pre-aligned wheel still pays off when you use it as a verification step (Perfect confirmed, card kept). It also stays a 0 RAM card, so it keeps its identity.

**Why it doesn't strictly dominate.** It costs 50 % more Cycles in the shop. In practice it is a sidegrade for players who run it as an emergency button, because the exhaust there is identical to the base.

Where the player mostly benefits: in the middle of a long fight, aligned plays recycle the card. That makes it a "setup" card in Perfect-hook decks (Breaker, Ghost).

3. **Interplay**
- **Variable slice sizes:** SNAP_TO_CENTER must use the cumulative boundaries (N12). On even-sized slices (4 or 6 ticks) there is no single centre tick, so define the snap target as the nearest tick of the best sub-tick quality. On a 4-tick slice (W G G W) it lands on a GOOD tick, never PERFECT. The text should therefore say "best tick", not "Perfect", once N12 lands.
- **Calibrated Firmware:** a snap onto a 4-tick slice then reads P. Lock On+ gains real value there.
- **Corruption (R9):** the card costs 0 RAM, so a CORRUPTED slice doubles 0 and stays 0. Lock On+ is the cleanest card to play on a corrupted slice.

4. **Data**
- Changed fields in the .tres: `id` → `lock_on_plus`, `display_name`, `description`, `cycle_cost` 60 → 90.
- New field on `CardData`: `exhaust_unless_aligned: bool = false` (set true on the + version). The resolver checks the tick offset before the snap. **NEW: conditional exhaust flag**, size S, no N#. Data-only fallback: drop the rider and make the + version RAM 0, `exhaust = false`, Cycle ×2.0 (a plain cost-reduction upgrade, which is stronger because it is repeatable).
- The preview must show "Exhausts" or "Returns" from the current offset. This is deterministic.

5. **Q:**
- Q: Is the repeatable fallback (no exhaust, Cycle ×2) too strong for a free Perfect? It would let a deck snap every turn.
- Q: Should the snap rule on even-sized slices pick the nearest best tick, or the slice's geometric centre?
