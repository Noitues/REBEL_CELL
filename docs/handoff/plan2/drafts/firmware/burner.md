<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__burner; status ok; tokens in 2505 cache-write 0 cache-read 32585 out 1461; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: burner

**Verdict:** CHANGE

1. **What it does today:** the slice is permanently OVERCLOCKED (1.5×) and each trigger adds 1 Heat (MODIFY_HEAT, target CAMPAIGN, on ON_SLICE_TRIGGER). It is the greedy-damage chip for SHIM/OVERFLOW slices on any class (Breaker most of all). The Heat is the price, paid at campaign level.

2. **Under the new rules:**
   - **Burnout conflict.** GDD 2.9 says OVERCLOCKED burns out into CORRUPTED after one trigger. Burner overrides that with a permanent status. Under R9, CORRUPTED means 2× RAM on that slice, so the burnout path is now a real cost. Burner skips it, and the Heat is the only price. That is cheap and flat.
   - **Solar Flares** (Orbital) apply OVERCLOCKED to your slice. On a Burner slice the status is already there, so it is a dead hit and the chip eats Orbital's pressure.
   - **R8 interaction.** OUTPUT_DOWN ×N (Halcyon Citations) stacks multiplicatively against the 1.5×. At ×2 the chip is net about 0.75×, yet it still costs Heat, which makes it a trap against Halcyon.
   - **Cleanse.** Cleansing the slice may strip the permanent OVERCLOCKED. This is unspecified today.
   - **Slice sizes.** The chip is size-neutral, but it is best on 3-tick G P G slices, where every landing is GOOD or better. On 4-tick slices (no Perfect) it is a flat +50 %. It is never dead.
   - **Dominance.** Heat is the only brake, and it matters only at the campaign layer. In a fight the chip is strictly better than Patch+ (same 1.5×). The choice is "Heat vs nothing", which is a poor choice. Multiple Burners add up to 1 Heat per trigger each, which is fine.
   - **Parasite ring.** A parasite that reduces your damage to the boss is a flat reduction, so it stays additive and does not break the chip.

3. **Proposed spec:**
   - **Description:** "Output +50%. Each trigger adds 1 Heat. The slice never burns out. If this slice is read as CORRUPTED, add 1 more Heat."
   - **Rarity:** 1 (uncommon). It is a build-defining risk chip, and today's rarity 0 is too common.
   - **Cycle cost:** 90. The cost is now Heat, so make it cheaper than Patch+ (100).
   - **allowed_slice_types:** SHIM, OVERFLOW. Burner on DEFRAG or SANDBOX pays Heat for defense and adds nothing meaningful.
   - **Multiplier:** `output_multiplier` 1.5. Drop `permanent_status` and implement the 1.5× as a plain multiplier. OVERCLOCKED then stays a pure enemy-applied or card status, and Flares can still stack onto the slice normally.
   - **Trigger:** keep MODIFY_HEAT +1 on ON_SLICE_TRIGGER. Add a 1-Heat surcharge when the slice is CORRUPTED, which is the Burner tax.
   - **Reading on the slice:** an orange heat glyph, and the preview chip shows "+1 HEAT".

4. **Data:**
   - `allowed_slice_types = [0, 1]`.
   - `rarity = 1`, `cycle_cost = 90`.
   - `output_multiplier = 1.5`, `permanent_status = NONE`.
   - Add a second TriggeredEffect with a CORRUPTED condition (a condition field on the trigger, **NEW: trigger condition**, M, data-only fallback: drop the surcharge).
   - Everything else is S and data-only. The preview must show the Heat; it already can.

5. **Q:**
   - Should Heat have an in-fight consequence (e.g. enemy +1 damage after N Burner triggers) so the cost is felt inside a netrun?
   - Is Burner meant to be exclusive with other output chips on the same slice, or may it stack with Patch+ (1.5 × 1.5 = 2.25)?
