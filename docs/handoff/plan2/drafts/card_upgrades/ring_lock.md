<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__ring_lock; status ok; tokens in 5133 cache-write 0 cache-read 32585 out 1078; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: ring_lock

1. **Role:** A 0-RAM utility that lets you spin the outer ring (to realign the pointer) without disturbing the inner-ring modifier you have already set. Today it is a niche enabler for inner-ring builds.

2. **Upgraded card:** "Ring Lock+" (one level only; nothing here needs a second).
   - **RAM cost:** 0 (unchanged).
   - **Cycle cost:** ×1.4 (50 → 70).
   - **Text:** "This turn, spins do not move your inner ring. Gain a free nudge on your inner ring."
   - **Effect list:**
     1. CUSTOM (type 24), target OWN_WHEEL (1), handler `ring_lock_handler.gd`, unchanged.
     2. NEW rider effect: NUDGE, target OWN_WHEEL, ring_scope INNER, amount 1 (one ±1 nudge, the player picks the direction when it resolves). This costs no RAM and does not use the per-turn free nudge. It is the same pattern as Feather Touch, but restricted to the inner ring.
   - **Exhaust:** false. **wheel_target:** OWN (0).
   - **Why this rider:** the lock only matters if you have an inner-ring setting worth protecting. A free inner nudge lets you fine-tune the setting you are about to protect, and it fits the card's job. It is a rider rather than a bigger number because the base effect is binary and has no number to grow.
   - **Sidegrade check:** the + version costs more Cycles and is no better in a deck with no inner-ring plan. A deck that already runs Ring Tap or Inner Snap gets a modest edge, because the nudge replaces a 1-RAM card.

3. **Interplay:**
   - Corruption as double RAM does not touch the 0-RAM cost, and the free nudge costs 0 RAM even when it acts on a CORRUPTED slice. This is a deliberate exception: confirm it (Q1).
   - Statuses and parasites are unaffected. The lock does not move statuses, because it blocks the inner-ring spin entirely, so no R6 remap applies.
   - The inner-ring redesign (G1) may change what the ring does. The card's role survives any redesign that keeps a spinnable inner ring.

4. **Data:**
   - Changed against the current .tres: `cycle_cost` 50 → 70, `display_name`, `description`, and one extra `effects` entry.
   - The rider is a plain NUDGE with ring_scope INNER, so it is data-only. The only open point is the choice of direction. Existing nudge cards (Feather Touch, Ring Tap) already handle this, so reuse their flow.
   - No N# is required. The card does not use the new amount modes or any other new system.

5. **Q:**
   - Q: Should the rider's free inner nudge be exempt from the CORRUPTED 2× RAM rule (as proposed, since it is free), or should it count as a card action that has to pay the doubled cost of 0 RAM, which is also 0 and so changes nothing?
   - Q: Should the + version also guard against enemy spins on your inner ring, or only your own spins, as today?
