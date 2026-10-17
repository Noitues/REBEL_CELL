<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__skimmer; status ok; tokens in 2583 cache-write 0 cache-read 32585 out 1370; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: skimmer

**Verdict:** CHANGE

1. **What it does today:** A SHIM slice gains +3 Cycles on a Perfect (ON_PERFECT, `min_tier` 2, twice per combat). It is an economy chip for any class that runs SHIM slices (Breaker, Ghost, Rigger, Botnet). It trades slice power for run-wide Cycles, which pay for shop purchases and convert to Schematics at 10:1.

2. **Under the new rules:**
   - **Perfect window varies.** Perfect exists only at d = 0, and only on odd sizes of 3, 5 or 7. On a 2-, 4- or 6-tick SHIM slice the chip is dead. That makes it a good chip for a deliberately uneven wheel and a trap on an even one.
   - **Calibrated interaction.** Calibrated turns a 4-tick slice into G P P G, so Skimmer would work there and pay more often. That is fine, but the twice-per-combat cap bounds it.
   - **Enemy listeners.** "Counter on any player Perfect" (Account Manager's Clawback, the Handler's Echo) makes a Perfect cost something. Skimmer's +3 Cycles is a small reward for a hit you may not want to take. This tension is good design and needs no change.
   - **TIER_DOWN.** The status drops a landing one tier, so a Perfect reads as Good and Skimmer silently fails. That is the intended anti-firmware interaction.
   - **Degeneracy.** None: the cap is per combat and the Cycles come from a Perfect, not a loop. The Cycles are tiny (about 6 per fight), which makes the chip weak. A 120-cost rare that pays back only 6 Cycles per fight is a poor pick. It also competes with Patch+ and Overvolt for the same socket.

3. **Proposed spec:**
   - **Description:** "SHIM slice: a Perfect pays 4 Cycles (3 times per combat). A Good landing pays 1 (once per combat)."
   - **Rarity:** 1 (uncommon).
   - **Cost:** 110.
   - **allowed_slice_types:** `[0]` (SHIM). OVERFLOW is excluded to keep the niche tight.
   - **Effects:**
     - Perfect: GAIN_CYCLES 4 FLAT, limit 3 per combat.
     - Good: GAIN_CYCLES 1 FLAT, `min_tier` GOOD, limit 1 per combat.
   - **Why:** Good landings are the common case on even slices, so the chip pays something there without needing a Perfect. The best-case total is about 13 Cycles, so slice power is still traded for modest income.
   - **Reads on the slice:** a coin glyph, with "P 4 / G 1" in the tooltip.
   - **Cap placement:** the cap counts per combat, so a plan that fires it on each of three Perfects stays within the budget.

4. **Data:**
   - **Fields:** edit the existing `triggered_effects`, adding a second TriggeredEffectData (trigger ON_SLICE_TRIGGER, `min_tier` 1) and changing the amounts and limit.
   - **Size:** S, data-only.
   - **Dependencies:** none. `amount_mode` (N1) is not needed since Cycles stay FLAT.
   - **Good-tier hook:** this assumes ON_SLICE_TRIGGER (trigger 5) can carry `min_tier`, as it does today. The Good effect must be exclusive of the Perfect effect so a Perfect does not pay both. If the interpreter cannot express that, drop the Good payout and keep only the raised Perfect payout (4 FLAT, limit 3). That fallback is still data-only.

5. **Q:**
   - Should Cycles scale with node tier (PERCENT of shop prices), or stay flat for a predictable economy?
   - Should the chip be barred from even-sized slices at loadout, or just carry a warning? A dead socket is a trap for new players.
