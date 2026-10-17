<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__micro_adjust; status ok; tokens in 5097 cache-write 0 cache-read 32585 out 1241; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: micro_adjust

1. **Role:** A free (0 RAM), one-shot precision fix. It gives two ±1 nudges on the enemy wheel (`wheel_target = 2`, ANY, so the player picks the wheel at play time) and then exhausts. It is the cheap tool for a Perfect or for denying one.

2. **Upgraded card: Micro-Adjust+** (one level is enough; it is a small card)
- **RAM cost:** 0 (unchanged).
- **Cycle cost multiplier:** ×1.5 (50 → 75).
- **Text:** "Three ±1 nudges. Exhaust." The third nudge is a bigger number, not a new effect.
- **Effect list** (one EffectData):
  - type NUDGE, target OWN_WHEEL (as the current file's `target = 2` field; keep whatever value it holds), ring_scope OUTER, amount 3, no status, duration 0.
  - No `amount_mode` is needed: NUDGE is a tick count, not a heal, block, shield or corruption amount (R5).
- **exhaust:** true (unchanged).
- **wheel_target:** 2 (ANY, unchanged).
- **Why this and not a cost cut or a rider:** the card is already 0 RAM, so no cost reduction is possible. Three ticks reaches any tick on a 5-tick slice from an off-centre landing and covers more of the dangerous sub-tick cases. It is not strictly dominating because it costs 50 % more Cycles and still exhausts. At 0 RAM it competes with Tap Tap (2 RAM, three nudges, no exhaust); it stays a one-shot, so Tap Tap remains the reusable option.
- **Rejected alternatives:**
  - Dropping exhaust would turn it into a different card (a repeatable free fix), and it would trivialise the free-nudge economy.
  - A split ring-scope rider would add complexity, and Ring Tap and Fine Tune already cover it.

3. **Interplay:**
- **Tick quality and slice sizes (R11, R12):** on 4-tick slices there is no Perfect. On a 3-tick slice a ±1 nudge crosses a whole quality band (G P G). On a 7-tick slice, getting from the WEAK edge to P needs three nudges, which is exactly what the + version delivers, and the base version can't.
- **Corruption as double RAM (R9):** a nudge on a CORRUPTED slice costs 2× RAM. The card's 0 RAM stays 0 (0 × 2), so it is a free way to move off a corrupted slice. Q2 asks whether that is intended.
- **Resistance:** each tick is absorbed by 1 resistance, so against resistance 2 the base card leaves a net 0 tick and the + version leaves 1. This is a modest edge against Compliance Lock-style bosses.

4. **Data:**
- `amount` 2 → 3, `cycle_cost` 50 → 75, display name and description updated.
- Add `upgrade_of = &"micro_adjust"` on the + resource if the upgrade pass adds that field (NEW: card upgrade link, data-only).
- No new effect type and no N# dependency.
- The ghost and phantom class files that list the card need an id swap or a reference to the + version once upgrades exist.

5. **Q:**
- Q: Should a 0-RAM card cost 0 on a CORRUPTED slice, or a minimum of 1 RAM, so the free fix doesn't dodge the R9 tax?
- Q: Should the upgraded version be offered only as a Rack or "flash" reward (N18), or also as a Mainframe purchase?
