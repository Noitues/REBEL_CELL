<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__ghost_step; status ok; tokens in 5133 cache-write 0 cache-read 32585 out 1225; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: ghost_step

1. **Role:** Ghost's precision tool. For 1 RAM it makes two exact ±1 adjustments to an enemy wheel through resistance, so the enemy's pointer lands on a chosen slice or tick, usually a Null, a WEAK edge, or a denied Perfect.

2. **Upgraded card: Ghost Step+** (one level only; there's no case for a second)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (70 → 105).
- **Text:** "Two ±1 nudges on an enemy wheel, ignoring resistance. The first nudge is free of any nudge lock."
  - Rejected: the lock rider, because N7 isn't built and the text would be dead until then.
  - **Chosen instead:** "Three ±1 nudges on an enemy wheel, ignoring resistance." One nudge more is a plain bigger number.
- **Final text:** "Three ±1 nudges on an enemy wheel, ignoring resistance."
- **Effect list** (one EffectData):
  - type NUDGE (5)
  - target TARGET_WHEEL (2)
  - amount 3
  - ring_scope OUTER
  - multiplier 0.0
  - status NONE
  - duration_turns 0
- **Exhaust:** false.
- **wheel_target:** ENEMY (1).
- **Why it's a sidegrade, not a strict upgrade:** it costs 50 % more Cycles. Three nudges can't fix a ±2 offset exactly: 3 ticks is an odd total, so reaching a target tick at an even distance needs the player to net out one tick, which can't be done in a single card. Ghost then pairs it with a free nudge or Feather Touch when parity matters. It reaches 3 ticks where the base reaches 2, which covers the next slice's WEAK edge or a 4-tick slice's far side.
- **Strict dominance check:** the base card still has a cheaper price point and a precise 2-tick reach, so neither version beats the other everywhere.

3. **Interplay:**
- **Variable slice sizes and tick quality (R11):** 2- and 4-tick slices have no Perfect, and Perfect sits on a single tick in odd slices, so 3 ticks of reach can move an enemy needle off a Perfect tick. This is more useful than on today's 5-tick slices.
- **Uneven needles (R10):** with 2 needles, a nudge moves both, so the player must aim for the safer outcome. The extra tick gives more options.
- **Resistance (Compliance Lock):** ignoring resistance is the key property against that buff. It is unchanged.

4. **Data:** in `ghost_step.tres` change `amount` 2 → 3 on sub_resource `fx`, `cycle_cost` 70 → 105, and `display_name` to "Ghost Step+", plus the description text. If the + version lives in a separate file (assumed, so the base card stays in reward pools), use id `ghost_step_plus`. No new effect or system needed; this is data-only. Upgrade-pass plumbing (a link from base to +) is outside this card.

5. **Q:**
- Q: Should the upgrade be a separate card id (so the base card can still appear in a pool), or a swap of the same card in place? This also decides whether `phantom`'s class file needs to reference the + id.
- Q: Does the +1 nudge interact with Calibrate / Deep Calibrate (free nudges)? Today it likely doesn't, because card nudges are not "nudge actions". Please confirm so the text doesn't mislead.
