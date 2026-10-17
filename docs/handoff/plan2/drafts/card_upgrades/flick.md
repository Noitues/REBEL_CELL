<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__flick; status ok; tokens in 5115 cache-write 0 cache-read 32585 out 1267; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: flick

1. **Role.** Free 1-tick micro-adjust of either wheel (including the enemy's). It fixes a one-tick error at 0 RAM and nothing else. It is the cheapest Perfect/Good repair in the shared pool, and it spends a card draw rather than a nudge.

2. **Upgraded card: Flick+** (one level is enough; the card is too small for a second).
- **RAM cost:** 0 (unchanged).
- **Cycle cost multiplier:** ×1.5, so 75.
- **Text:** "Spin a wheel 1 tick in a direction of your choice. Draw 1 card."
- **wheel_target:** ANY (RC.WheelTarget.ANY, value 2, unchanged).
- **Exhaust:** false.
- **Effects:**
  1. SPIN, target TARGET_WHEEL, amount 1, ring_scope WHOLE_WHEEL. The direction is chosen on play (CW or CCW). Today's card is clockwise only.
  2. DRAW_CARDS, target SELF, amount 1, ring_scope OUTER (unused).

**Why this is not strict dominance.** Both riders are small. The choosable direction fixes the card's real weakness: a clockwise-only 1-tick spin is useless half the time. The cantrip makes it hand-neutral, so it never costs a slot. Cycle cost rises 50%. A spin is still absorbed by enemy resistance, which a nudge-style fix would ignore (hence the card stays a spin, and Jam / Feather Touch keep their niches). The + card is still not a nudge: it is whole-wheel, so a docked satellite moves with the host. It stays a 1-tick tool.

3. **Interplay.**
- **Variable slice sizes and tick quality (R11):** 1-tick precision matters most on 3-tick and 4-tick slices, where only one tick is Perfect, or none (the 4-tick WGGW). The choosable direction lets you step onto the Perfect tick from either side. This is the card's best new role.
- **Corruption as double RAM (R9):** the card costs 0 RAM, so the doubling does nothing. Flick+ is the way to leave a CORRUPTED slice without paying 2× for a nudge, or to put a pointer onto one cheaply.

4. **Data.**
- **Changed:** `id` stays `flick` (the + is a separate `flick_plus` file); `cycle_cost` 50 → 75; the description; effects gain `DRAW_CARDS` (type 18, target 0, amount 1).
- **The SPIN effect:** direction chosen at play. Today's `amount = 1` is a fixed clockwise spin, and negative amounts probably already mean counter-clockwise. `Counter-Spin` shows the pattern, so a chosen direction needs a player-choice prompt: **NEW: spin_direction_choice** (a `choose_direction: bool` on `EffectData`, small, and the preview shows both outcomes). **Fallback without it:** author `amount = 1` clockwise and keep the draw rider; the card is still a sidegrade, just a weaker one.
- **Existing systems:** DRAW_CARDS is already an effect type.
- **No N# dependency** for the fallback. The choice prompt reuses the CHOSEN-style prompt flow, with no randomness, and the preview equals the result.

5. **Q:**
- Q: Should direction choice become a general `choose_direction` flag on all spin cards (Twist+, Whirl+), or stay a Flick+ feature?
- Q: Does the draw rider push a deck toward 0-RAM cycling loops (Flick+, Scrap Code, Cache), and should Flick+ exhaust to prevent that?
