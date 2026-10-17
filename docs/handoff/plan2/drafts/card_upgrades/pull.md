<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__pull; status ok; tokens in 5069 cache-write 0 cache-read 32585 out 1133; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: pull

1. **Role:** Neutral cheap draw (1 RAM, draw 2). It digs for the wheel-manipulation cards that make Perfects, and Botnet and Hivemind use it to keep drone and parasite turns flowing.

2. **Upgraded card: "Pull+"** (one + level is enough; a single-number card does not need a ladder.)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (55 → 82; the rider is worth the price).
- **Text:** "Draw 2 cards. If your hand is 2 or fewer cards after drawing... " is rejected as an unreadable conditional. Final text: "Draw 2 cards. Gain a free nudge."
- **Effects (EffectData):**
  1. DRAW_CARDS (17), target SELF, amount 2, FLAT. Unchanged.
  2. A free-nudge grant, the same effect Torque Wrench uses ("gain a free nudge"). type and amount follow Torque Wrench's existing .tres: `amount = 1`, target SELF, `duration_turns = 0` (lasts the turn).
- **Exhaust:** false. **wheel_target:** OWN (0).
- **Why this rider:** it adds a use rather than just a bigger draw. Draws find the nudge, and the free nudge pays for the Perfect fix this turn. Draw 3 would be too close to Data Surge (2 RAM, draw 3).
- **Not strictly dominant:** the Cycle price rises 50 %, and the card is not worth it in a deck that already has free-nudge sources (Calibrate, Rigger's Torque Wrench). Taking the base card there is a real choice.

3. **Interplay:**
- A free nudge that fixes a tick is worth most on uneven slice sizes (R11). A 4-tick slice has no Perfect, and a 3-tick slice has a single Perfect tick, so a 1-tick correction decides the outcome.
- Under corruption as double RAM (R9), a nudge costs 2 RAM only if the free one has been used. This rider therefore also offsets part of the CORRUPTED tax. The "free" nudge is the first nudge per turn, and I assume the nudge cost is waived rather than refunded after the fact.

4. **Data:** change `cycle_cost` 55 → 82, add one `EffectData` (the free-nudge grant, already in use by Torque Wrench), `display_name = "Pull+"`, and update the description. No new system. Cards currently have no upgrade link, so the upgrade pass needs a `CardData.upgrade_of` (or `upgraded_id`) field and a class-file reference list. Both class files (botnet, hivemind) must reference the + id wherever they list `pull`. This is the card-upgrade pass's own infrastructure: NEW: card upgrade link.

5. **Q:**
- Q: Is "gain a free nudge" additive with the once-per-turn free nudge (two free nudges in one turn), or does it only restore the free nudge after it has been used? The first reading is stronger, and the choice should be made in the card-upgrade pass for all cards that grant one.
- Q: Should Hivemind (a drone-heavy class) get a class-specific + (draw 2, and the next drone costs −1 RAM) instead of this neutral one?
