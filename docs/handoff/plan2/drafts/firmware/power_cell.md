<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__power_cell; status ok; tokens in 2562 cache-write 0 cache-read 32585 out 1504; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: power_cell

**Verdict:** CHANGE

1. **What it does today:** The SANDBOX slice (type 4) restores 1 RAM (GAIN_RAM, amount 1) on trigger 5 (ON_SLICE_TRIGGER), at any tier. It is used by Rigger-style wheels, which are the only class with a SANDBOX slice. Under R13 that slice becomes SHIELD (lingering, cap 15). Its role is a small RAM-economy rider on a defensive slice.

2. **Under the new rules:**
   - **Naming breaks.** The allowed type 4 is renamed SHIELD by R13, and the description says "SANDBOX". The enum int stays 4, so the data still works. Only the text must change, or it will read as the new SANDBOX (the evade).
   - **Tier-blind and free.** It fires on a WEAK landing and on a SHIELD that is already capped at 15. That makes it a pure income chip, and a tiny one (+1 of +4 per turn).
   - **Slice size.** Slice sizes are now 2 to 7 ticks. A 2-tick slice reads G G and a 6-tick slice reads W W G G W W, so a flat trigger makes the chip's value independent of the size and precision work the rules want to reward. It is not a dead chip, but it is not interesting either.
   - **Corruption.** CORRUPTED doubles RAM cost, and this chip is a natural counter-economy piece. Today it does nothing about that.
   - **Statuses.** OUTPUT_DOWN scales the shield, but not a flat RAM rider. TIER_DOWN lowers the landing tier, so a tier-gated rider would be hurt by it. That is a good interaction with anti-firmware.
   - **Degeneracy.** No loop: +1 RAM per trigger and one trigger per resolve. Retrigger effects such as Breaker's Perfect hook or Echo would double it, which is fine at this size.
   - **Parasites.** A parasite that drains RAM would offset it. That is fine.

3. **Proposed spec:**
   - **Description:** "SHIELD slice restores 1 RAM on Good or better. On a Perfect, restores 2 instead and the slice's shield is not wasted: RAM refunded equals 1 per 5 shield lost to the cap, max 2 extra." This is too fiddly, so simplify to the following.
   - **Final description:** "SHIELD slice restores 1 RAM on Good or better; 2 on a Perfect."
   - **Rarity:** 1 (uncommon). **Cost:** 110 (unchanged).
   - **allowed_slice_types:** [4] (unchanged).
   - **Effects:** two triggered effects, both GAIN_RAM FLAT. The first is on ON_SLICE_TRIGGER with min_tier = GOOD (1), amount 1. The second is on ON_PERFECT, amount 1, which stacks to 2 on a Perfect.
   - **Reads on the slice** as a small RAM chip glyph, with "+1 / +2" shown in the landing preview, since preview must equal result.
   - **Why:** It matches Leech's Good-or-better gate, so the SHIELD slice has a consistent precision reward. It no longer pays on a WEAK landing or under TIER_DOWN pressure. It also makes the sub-tick map matter: a 4-tick slice (no Perfect) caps at 1, while a 3-tick or 5-tick slice can reach 2.
   - **Interaction with the Calibrated chip:** Calibrated would turn a 4-tick slice into G P P G, so this pair becomes a real combo.

4. **Data:**
   - Change the first triggered effect's `min_tier` from 0 to 1.
   - Add a second TriggeredEffectData with trigger = 6 (ON_PERFECT) and a GAIN_RAM effect of amount 1.
   - Update the description text.
   - **Dependencies:** none beyond today's systems. The RAM amount is FLAT and the player's RAM is not scaled. The R13 naming change is N14, text only. **Size: S, data-only.**

5. **Q:**
   - Q: Should the RAM refund still pay when the shield is wasted at the 15 cap, or only when the slice actually adds shield?
   - Q: Is two total RAM on a Perfect too strong for the Rigger, whose Perfect hook already refunds 1 RAM?
