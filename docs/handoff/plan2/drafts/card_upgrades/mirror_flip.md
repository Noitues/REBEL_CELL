<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__mirror_flip; status ok; tokens in 5138 cache-write 0 cache-read 32585 out 1214; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: mirror_flip

1. **Role**: The expensive precision reversal. It flips a wheel to bring the opposite slice to the pointer and reverse slice order. It is a hard-to-use way to reroll your landing deterministically, and the only way to bypass a single enemy intent with certainty.

2. **Upgraded card**: "Mirror Flip+". One + level is enough.
- RAM cost: 3 → 2.
- Cycle cost multiplier: ×1.5 (75 → 112).
- Text: "Flip a wheel. If it has resistance, the flip is only absorbed by 1 resistance instead of being blocked."

   Wait, this rewrites the card. Final choice, keeping it a sharpening: the + version is a **cost cut plus a wider target**:
- Text: "Flip a wheel. Blocked while the target has resistance. Costs 1 less RAM if you flipped your own wheel."

   That reads as two cards, so I drop it. Decision: **RAM 3 → 2, no other change**, with an added rider that keeps the card a flip.
- Rider: after the flip, the flipped wheel's pointer reading is previewed on the card (no effect).
- Effect list (unchanged): FLIP, target TARGET_WHEEL (2), ring_scope WHOLE_WHEEL, amount 0, multiplier 1.0, status NONE, duration 0.
- Added effect: NUDGE, target OWN_WHEEL, ring_scope OUTER, amount 1 (one free ±1 nudge, bound to the card, costs no RAM and does not use the turn's free nudge).
- Exhaust: false. wheel_target: ANY (the current file's value 2 is kept; check it matches the ENEMY/ANY enum used by the original).

   The free nudge fixes the flip's main weakness: a flip lands you on the mirrored tick, usually off-centre, and cannot be adjusted without spending RAM.

   **Sidegrade, not dominance:** it is still blocked by resistance, still whole-wheel only, and the extra nudge is ±1 only. It costs 1.5× Cycles. At 2 RAM it competes with Flip Switch (2 RAM, own wheel only), so the + stays worth it only for the extra target and nudge.

3. **Interplay**:
- With variable slice sizes, a mirror maps ticks via cumulative boundaries, so a flip often lands on a WEAK or edge sub-tick of a 4- or 6-tick slice. The bundled nudge is the repair.
- On a CORRUPTED slice the nudge does not double in RAM cost, because it is card-bound and free.
- Parasite-ring segments rotate with the wheel and flip with it, so the card can reposition them without clearing them.

4. **Data**:
- `ram_cost` 3 → 2, `cycle_cost` 75 → 112.
- Add one sub_resource `EffectData`: type 5 (NUDGE), target 1 (OWN_WHEEL), ring_scope 0, amount 1.
- `description` updated.
- No new systems. Needs a free-nudge flag: a NUDGE inside a card is already free in the data (Feather Touch is a RAM 0 card), so no N#. Fallback is not needed.

5. **Q:**
- Q: Should the bundled nudge be able to move the wheel the card just flipped when that wheel is the enemy's, or stay own-wheel only as drafted?
- Q: Is "+" enough, or does the Flip need a second level that lifts the resistance block (Compliance Lock counter) at a higher cost?
