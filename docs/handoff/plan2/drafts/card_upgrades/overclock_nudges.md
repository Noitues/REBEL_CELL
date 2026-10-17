<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__overclock_nudges; status ok; tokens in 5112 cache-write 0 cache-read 32585 out 1188; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: overclock_nudges

1. **Role:** A setup card. For 1 RAM it doubles next turn's nudge cards (Fine Tune, Tap Tap, Jam and the like), so a nudge-heavy hand can reach the exact tick, including the single Perfect tick on an odd-sized slice.

2. **Upgraded card: "Nudge Driver+"** (one level only; the card is too small for two)
- RAM cost 1 (unchanged).
- Cycle cost ×1.25 (65 → 81).
- Text: "Nudge cards trigger twice this turn and next turn."
- Effects (one entry, plus a parameter on the existing handler):
  - `type = DOUBLE_NUDGE_CARDS` (20), `target = SELF`, `amount = 0`, `duration_turns = 2` (the current card has 0; the handler hard-codes "next turn").
  - On play, the window opens for the rest of this turn and all of next turn.
- Exhaust false. `wheel_target` 0 (OWN), unchanged.

**Why this rider:** the current card is dead tempo, since you pay 1 RAM and your hand this turn gets nothing. The + version lets you play it first in a hand that already holds nudge cards, so it pays back at once and still carries into next turn. It sharpens the card without changing what it is. It is also not strictly better in every situation. Doubling only the current turn would be a sidegrade, and ×2 over two turns means a stray Jam or Ghost Step you didn't plan to double gets doubled too. The doubling is nudge cards only, not the free nudge or paid nudges. That keeps it away from the 1-RAM economy, and a card-cost doubling applies only where the card is actually played.

3. **Interplay:**
- On a 4-tick slice (no Perfect) or a 3-tick slice (Perfect only on the centre tick), more nudges per turn mean more precision, so the card matters more when slices vary in size.
- Corruption's 2× RAM applies to the cost of nudges and cards when the pointer reads a CORRUPTED slice. Doubled nudge cards do not double the cost, because the second trigger is an effect repeat and not a new play. This must be stated in the rules text, or the card becomes a strong answer to the RAM tax.
- Ghost (Ghost Step, Jam) wants this most. A Halcyon nudge-lockout (N7) blocks the nudges themselves, so the card does nothing there. That is a deliberate soft counter.

4. **Data:**
- `cycle_cost` 65 → 81.
- `description` updated.
- `fx0.duration_turns` 0 → 2.
- `display_name` "Nudge Driver+".
- **Dependency:** the handler for DOUBLE_NUDGE_CARDS must read `duration_turns` and apply it to the current turn and the next. If it currently hard-codes next-turn only, that is a small change (S, inside N20's neighbourhood but not tied to N20). There is no new system. Fallback: a data-only variant with `amount = 1` meaning "include this turn", if the handler already reads `amount`.
- The preview must show the doubled nudge in the staged result (preview = result). Undo restores the window flag.

5. **Q:**
- Q: Should the second trigger of a doubled nudge card repeat for free in RAM, as written, or should corrupted slices charge the repeat too?
- Q: Does the window stack if the + card is played twice (it could reach 4×), or does it refresh to a flat ×2?
