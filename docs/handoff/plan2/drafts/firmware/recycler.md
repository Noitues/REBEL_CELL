<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__recycler; status ok; tokens in 2561 cache-write 0 cache-read 32585 out 1352; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: recycler

**Verdict:** CHANGE

1. **What it does today:** the NULL slice restores 2 RAM when it resolves (trigger 5 = ON_SLICE_TRIGGER, effect 12 = GAIN_RAM, amount 2, NULL only). It is a niche chip. It makes the dead slice a small RAM battery for classes with a spare NULL (Breaker, Ghost, Rigger, Botnet all carry one). It is weak: 2 RAM is under half a turn's +4, and the player is not trying to land on NULL.

2. **Under the new rules:**
   - **Better:** CORRUPTED now doubles RAM costs, so RAM is a more valuable resource. A reliable RAM source has more value.
   - **Better:** uneven needles, pointers on any tick, and enemy needles that steer you make NULL landings more frequent and less avoidable. Meridian PRIORITY and Halcyon Citations could push you onto it.
   - **Stays fine:** Zero Day, Fault Tolerance and Stolen Intent already reward NULL, so the chip stacks with those builds.
   - **Breaks:** at 2 ticks, a NULL slice is hard to land on. At 6–7 ticks it is a large target that you can farm. Resolving NULL every turn gives +2 RAM per turn, which is a free half of your regen with no card cost. A big NULL plus Recycler plus the free nudge becomes a dominant RAM engine with no loss, since NULL does nothing else.
   - **Dead case:** a socket on a 2-tick NULL is almost never read.
   - **Loop check:** with RETRIGGER or Echo on a NULL it fires multiple times per resolve. Needs a cap.
   - **Statuses:** OUTPUT_DOWN scales the amount, and a PERCENT mode would not exist here, so keep FLAT. TIER_DOWN has no effect (NULL has no tier gate). CORRUPTED on this slice doubles the RAM you spend when acting there, but you gain RAM when it resolves, so it taxes an unrelated action. ENCRYPTED, Hardened or a Parasite that reads the slice are all fine.

3. **Proposed spec:**
   - **Description:** "When the NULL slice resolves, restore 2 RAM (3 on a Perfect). Once per turn."
   - **Rarity:** 0 (COMMON). **Cost:** 90. **Allowed:** NULL (8) only.
   - **Effects:** ON_SLICE_TRIGGER, GAIN_RAM FLAT 2, min_tier 0. A second entry at ON_PERFECT with FLAT +1. Add a `once_per_turn` limiter to the trigger, or a per-turn counter.
   - **Reads on the slice:** a small RAM glyph over the NULL slice, "+2 / +3 on Perfect". The NULL's sub-tick map is shown on the loadout screen, so size matters: a 4-tick NULL (no Perfect) pays 2, a 5-tick or 7-tick NULL pays 3 on its centre tick, so the choice of size is a real decision.
   - Does not count as a "miss" for Cold Exit, which still counts any resolve of NULL. That is a deliberate tension with Cold Exit.

4. **Data:** change description, add a ON_PERFECT entry, add a once-per-turn flag on TriggeredEffectData (NEW: `max_per_turn`, S), and keep the cap by default for all RAM-restoring chips. The rest is data only. N12 is needed for the size interactions, but the chip works on today's 5-tick slices without it. Size S.

5. **Q:**
   - Q: Should NULL slices be allowed to grow (6–7 ticks) at all, or should the loadout cap NULL at 5 to protect this chip's economy?
   - Q: Should Recycler count as a Cold Exit NULL resolve (a conflict between the two chips), or should it be separated?
