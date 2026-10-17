<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__tracer; status ok; tokens in 2576 cache-write 0 cache-read 32585 out 1350; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: tracer

**Verdict:** CHANGE

1. **What it does today:** A SHIM or OVERFLOW slice strips 1 resistance from the target on a Perfect (trigger 5 = ON_PERFECT, min_tier 2, MODIFY_RESISTANCE −1 on the target wheel). It's a niche counter to enemy resistance (Meridian Weight, Compliance Lock) and fits any attacker. The Ghost's hook already strips 2 resistance on a Perfect, so it overlaps there.

2. **Under the new rules:**
   - **Breaks:** Perfect is now much rarer. A 2-tick slice has no Perfect, a 4-tick has none, a 6-tick has none, and 3- and 7-tick slices have a one-tick window. The chip would be dead on even-sized slices, and "Calibrated" (which raises every sub-tick a tier) would make it fire far too easily.
   - **Weak payoff:** 1 resistance is trivial. Resistance 3 is restored every turn, so a stripped point never carries over, and a Perfect that costs nudge RAM to land is a poor return. It only matters with the Perfect-then-next-slice ordering inside one resolve.
   - **Compliance Lock (R7):** the buff is turned off by an Exploit, so tracer is a soft, non-guaranteed counter, which is good. However, the Flip and Respin block applies while resistance is above 0, so stripping is the only way to unlock them mid-turn. That is where the chip is actually valuable, and today it is too small to do it.
   - **Degenerate risk:** none, because nothing loops. Do not give it a stacking effect. Listeners ("counter on any player Perfect") punish Perfect play, so a chip that depends on Perfect is a trap against Clawback-style enemies. A Good-tier fallback helps.
   - **Statuses:** TIER_DOWN pushes Perfect to Good and shuts the chip off. OUTPUT_DOWN does not affect it, since it strips a flat 1. ENCRYPTED, parasites and CORRUPTED do not interact.

3. **Proposed spec:**
   - **Description:** "SHIM or OVERFLOW slice: on Good or better, strips 1 resistance from the target. On a Perfect, strips 3."
   - **Rarity:** 1 (uncommon). **Cost:** 120 (unchanged).
   - **allowed_slice_types:** [0, 1] (unchanged).
   - **Effects:** two triggered entries.
     - ON_SLICE_TRIGGER, min_tier GOOD: MODIFY_RESISTANCE −1, target wheel (FLAT).
     - ON_PERFECT, min_tier PERFECT: MODIFY_RESISTANCE −2 more, so a Perfect strips 3 in total.
   - Both entries use FLAT, and the resistance strip is not scaled by tier.
   - **Reads on the slice:** a small wrench glyph with "−1 / −3 RES". The loadout sub-tick map shows which ticks qualify, so a 4-tick G G slice still reads −1 and a 5-tick centre reads −3.
   - **Why:** this fixes the dead 4- and 6-tick case by giving Good a function, and the Perfect bonus is enough to clear Weight 3 outright and open Flip and Respin.

4. **Data:** change the description. Add a second TriggeredEffectData (trigger ON_SLICE_TRIGGER, min_tier 1, amount −1). Change the existing perfect entry's amount from −1 to −2. No new fields, no N#, **S**, data-only.

5. **Q:**
   - Does resistance stripped mid-resolve apply to the player's own later nudges and cards this turn, or only to the resolve? I assume it lasts until the next start-of-turn restore.
   - Should a Parasite-ring "anti-tracer" exist (a segment that restores resistance), or is that overkill?
