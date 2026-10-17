<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__barbed_wire; status ok; tokens in 2573 cache-write 32585 cache-read 0 out 1424; cost $0.050. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: barbed_wire

**Verdict:** CHANGE

1. **What it does today:** A DEFRAG slice also deals 2 flat damage to the pointer target (trigger 5 = ON_SLICE_TRIGGER, effect DEAL_DAMAGE, target POINTER_TARGET). It fits only DEFRAG (BLOCK). It turns a pure defense slice into a hybrid, so it suits defensive classes with 2 DEFRAG slices (Ghost, Rigger, Botnet). The Breaker has only one DEFRAG slice.

2. **Under the new rules:**
   - **Flat 2 is weak.** Enemy HP is banded (phases of about 42–105 HP at T4), and the reference player does 9–18 damage per turn. 2 damage is noise and doesn't scale with the slice. Patch+ and Bulkhead also don't touch it, because the damage is an effect on the chip, not the slice's output.
   - **Slice size matters.** On a 2-tick slice (G G) the chip fires on every landing. On a 4-tick slice (W G G W) it fires on WEAK edges too. Today the chip ignores tier and always deals the full 2 on a WEAK landing, while the BLOCK is halved. That is an odd mismatch, so the damage should read the landing tier.
   - **Phase parking (R3).** Chip damage is lost at a threshold, which is fine and harmless.
   - **Listeners (N6).** Enemies that counter on ON_HIT_DEALT could punish a chip that adds hits. This is a good tension and not degenerate.
   - **Statuses.** OUTPUT_DOWN should shrink the chip's damage as well as the BLOCK (it is anti-firmware). Today a CORRUPTED slice would still pay RAM only when it is played, but the chip never costs anything extra. TIER_DOWN lowers the chip's tier gate. ENCRYPTED blocks applying statuses to the slice and doesn't interact otherwise.
   - **Pierce and SANDBOXed targets.** A SANDBOXed enemy negates only attacks, and this chip's hit is an attack, so it is negated on a sandboxed target. That is correct and gives a read.
   - **Loops:** none. No RAM or Heat is generated.
   - **Dead cases:** a tiny 2-tick DEFRAG slice with this chip would be a poor pick. That is acceptable.

3. **Proposed spec:**
   - **Description:** "DEFRAG slice also deals damage equal to 25% of the BLOCK it gains (minimum 2) to the pointer target."
   - **Rarity:** common (0). **Cycle cost:** 100. **allowed_slice_types:** [DEFRAG].
   - **Effect:** DEAL_DAMAGE on POINTER_TARGET, `amount_mode` = PERCENT of the slice's own output, minimum 2. It scales with Patch+, Bulkhead and OUTPUT_DOWN, and it is halved on WEAK like the block. It is tier-independent (R2, buffs are independent).
   - **Numbers:** a 12 BLOCK slice deals 3, Perfect 12 BLOCK deals 3, and Bulkhead (+50 % → 18 BLOCK) deals 4.5, rounded to 5. The chip is a small top-up, with Counterstrike as the premium version.
   - **How it reads:** the slice shows "12 BLOCK + 3 dmg", and the preview shows both numbers per pointer.

4. **Data:** change the description. Add the `amount_mode` PERCENT with a `min_amount` field on `EffectData`, with the percent base being the slice's resolved output. This needs N1 and N20 (a rider-style output reference). **Fallback:** flat 3 instead of 2, which only fixes the weakness and not the scaling. Size: S–M.

5. **Q:**
   - Should a percent-of-output damage effect become a general effect mode (base = the slice's own output), or stay a one-off for this chip?
   - Should the chip's damage ignore SANDBOX like a rider, so that a hybrid slice has a reason to exist against sandboxed bosses?
