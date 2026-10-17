<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__reroll; status ok; tokens in 5108 cache-write 0 cache-read 32585 out 1182; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: reroll

1. **Role:** A neutral reward-pool card. It is the random-outcome tool: a respin when the current landing is bad, at the price of a checkpoint (no undo past it) and 2 RAM. It is the only card that gambles instead of steering.

2. **Upgraded card: Reroll+** (one level only)
- RAM cost: 2 → 1.
- Cycle cost multiplier: ×1.5 (55 → 83, rounded).
- Text: "Respin a wheel to a random tick. If the new landing is WEAK or NULL, gain 1 free nudge this turn."
- wheel_target: ANY (unchanged, 2).
- exhaust: false (unchanged).
- Effects:
  1. RESPIN, target TARGET_WHEEL, ring_scope WHOLE_WHEEL (unchanged, `type = 8`, `target = 2`).
  2. Rider: CUSTOM `reroll_consolation`. If the pointer reads WEAK or NULL after the respin, grant a free nudge (the same state flag Calibrate sets, +1). Condition is evaluated on the post-respin outcome of the acting wheel's primary pointer.

Why this shape: the cost cut alone is a plain bigger number and would make the card a spam tool. The rider softens the bad tail of the gamble (a WEAK or NULL landing) without making a good outcome better. Reroll+ is a sidegrade-leaning upgrade, not a strict dominator: it is better only when the gamble fails, and the cost drop is the real gain. Unchanged from the base: the checkpoint is still set, and still blocked by resistance on enemy wheels.

3. **Interplay:**
- Tick quality (R11) and variable sizes (R12) change the odds. A wheel with many 4-tick slices (no Perfect) or 2-tick slices makes WEAK/NULL landings more or less likely, so the rider's value varies by wheel. The preview must show the odds as a distribution, per GDD 2.10 (random effects show odds).
- Corruption (R9): if the pointer lands on a CORRUPTED slice, the nudge the rider grants costs 2× RAM. That is a fair cap on its value.
- Parasite ring (N10): a respin moves your wheel, and the ring rotates with it, so a respin can also dodge or hit a Parasite segment. Document this in the Codex text.

4. **Data:**
- `ram_cost` 2 → 1.
- `cycle_cost` 55 → 83.
- `description` updated.
- Add effect `fx1` of type CUSTOM with a `custom_handler` script `reroll_consolation.gd` (**NEW: a CUSTOM handler; no N# fits**).
- Data-only fallback: Calibrate's "next nudge free" is expressible, but it is unconditional. A conditional version needs the handler. Fallback: ship only the cost cut (RAM 1, Cycle ×1.5, no rider), which is data-only.
- Save and determinism: the handler reads the post-respin result from the checkpointed RNG stream. It uses no randomness of its own, and the preview shows the odds before play.

5. **Q:**
- Q: Should the rider count a NULL landing on an enemy wheel (the player respinning the enemy's wheel) as a consolation, or only on the player's own wheel?
- Q: Is a conditional free nudge too fiddly for the tooltip, or should the upgrade be the plain RAM 1 cost cut?
