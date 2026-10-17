<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__bulkhead; status ok; tokens in 2390 cache-write 0 cache-read 32585 out 1318; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: bulkhead

**Verdict:** CHANGE

1. **What it does today:** DEFRAG and SANDBOX slices get ×1.5 output. It is a defense-only multiplier (the mirror of overvolt) for tanky builds: Rigger and Ghost (Defrag/Defrag/Sandbox wheels), and Breaker's single Defrag. Cost 90.

2. **Under the new rules:**
   - **Type mapping breaks.** The enum ints stay for saves, but the display names change. Today's DEFRAG (2) is BLOCK, today's SANDBOX (4) is SHIELD, and DETOUR (3) is the new SANDBOX, which negates a whole attack. `[2, 4]` still means BLOCK and SHIELD, which is correct, but the description must be renamed. Multiplying an evade is meaningless, so keep DETOUR excluded.
   - **Shield cap.** SHIELD caps at 15, so +50% on a 6 shield is fine, but on larger shields the extra is clipped. That makes the SHIELD half of the chip weak. BLOCK expires each turn and is uncapped, so it benefits most.
   - **Pierce.** Pierce ignores both BLOCK and SHIELD, so the chip does nothing against Adrenaline in Genome Core P4. This is acceptable, because the counter is SANDBOX.
   - **Sizes.** Output is tier-based and size-independent, so the chip is never dead on 2-tick or 6-tick slices. But a 4-tick slice has no Perfect, so it is only ever GOOD (1.0×) or WEAK (0.5×); the chip lifts a WEAK landing back to ~0.75×. That is a mild, useful synergy with small slices.
   - **Statuses.** OUTPUT_DOWN (−25% per stack) stacks multiplicatively or additively with ×1.5, which keeps the chip a partial counter to Halcyon Citations. TIER_DOWN is not countered. CORRUPTED doubles RAM cost on the slice, which makes a chip on a defense slice a RAM trap against Immunization.
   - **Degeneracy.** The dominant risk is that it is simply Patch+ for defense at a lower cost, with a better target set than barbed_wire and static_coat, which are 100 and exclusive to BLOCK. Stacking it with Patch+ on one slice is impossible (one socket), so there is no loop.

3. **Proposed spec:**
   - **Description:** "BLOCK and SHIELD slices: output +50%. SHIELD gained this way ignores 3 points of the cap."
   - Rarity 0, Cycle cost 90 (keep).
   - `allowed_slice_types = [2, 4]`, `output_multiplier = 1.5`.
   - **New rider:** a FLAT +3 to the SHIELD cap, applied only to this slice's gain. That keeps the +50% real at high values and makes the SHIELD half competitive with the BLOCK half, while the global cap of 15 stays intact.
   - **Reads on the slice:** a socket glyph with a small shield-plus tag. The preview shows "+50%" on the chip.
   - **Simpler fallback:** drop the cap rider and keep the chip as is, with only the rename. It is still acceptable.

4. **Data:**
   - Description and rename: data only, S.
   - Cap rider: a new `shield_cap_bonus` field on `FirmwareData`, handled in `effect_interpreter.gain_shield`. **N14** (defense trio), S. No rider means no dependency.

5. **Q:**
   - Q: Should the SHIELD cap exception exist at all, or should the chip stay a plain ×1.5 and let the cap punish it?
   - Q: Should SANDBOX (the evade) get its own chip, for example "negates one extra hit", rather than a multiplier?
