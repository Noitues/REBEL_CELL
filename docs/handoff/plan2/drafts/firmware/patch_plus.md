<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__patch_plus; status ok; tokens in 2273 cache-write 0 cache-read 32585 out 1334; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: patch_plus

**Verdict:** CHANGE

1. **What it does today:** Slice output ×1.5, any slice type, 100 Cycles, common. It's the default "make this slice bigger" pick: OVERFLOW or SHIM for burst, DEFRAG for safety. Every class takes it, and it never creates a decision.

2. **Under the new rules:**
   - **Breaks:** Nothing mechanically. It is a flat multiplier that stacks cleanly with OUTPUT_DOWN (R8): −25% per stack applies on top, so ×1.5 with one stack is ×1.125. It has no answer to TIER_DOWN: a Perfect read down to Good still loses its hook.
   - **Dominant:** It fits any slice, so it is the best chip on the biggest slice. The scarce resource is now slice shape (R11), and this chip ignores shape. A 6-tick slice and a 2-tick G G slice (no Perfect) get the same +50%. On a 2-tick slice it is dead weight in terms of Perfect hooks but fine for raw output, so it cannot be called dead.
   - **Overlaps:** Overvolt (+25%, SHIM/OVERFLOW) and Bulkhead (+50%, DEFRAG/SANDBOX) are strictly narrower, and Bulkhead matches it exactly where it applies. Patch+ makes Bulkhead redundant and Overvolt trivially worse.
   - **Parasites:** A Parasite that cuts damage to the boss multiplies against it, so it does not counter it. The old PARASITE halving was ×0.5 and is now a 2-stack OUTPUT_DOWN (×0.5), so Patch+ only partly offsets it. That is fine.
   - **Degenerate risks:** Burner (OVERCLOCKED 1.5×) stacks to ×2.25. That is intended, but pairing it with Calibrated is the real spike. No loop.
   - **Gets better:** Against Corruption-as-RAM-tax (R9), output chips are the way to get more value per doubled-cost play.

3. **Proposed spec:**
   - **Description:** "Slice output +50%. Cannot socket on a slice smaller than 4 ticks." Better: make it scale with shape, not forbid it.
   - **Chosen:** "Slice output +40%; +60% if the slice has 5 or more ticks." Larger slices are easier to hit reliably, so the bonus rewards the wide body. This makes shape a real build choice against Calibrated (small slices, many Perfects).
   - **Rarity:** common. **Cost:** 100. **allowed_slice_types:** any.
   - **Multipliers:** `output_multiplier` 1.4, plus a new size bonus (`size_bonus_min_ticks` = 5, `size_bonus_multiplier` = 1.6).
   - **Reads on the slice:** a +40% or +60% chip on the socket, with the tick map on the loadout screen showing which applies.
   - **Why:** one line, it ties the generic chip to R11 so it is no longer a free pick, and it fixes the Bulkhead overlap by making Bulkhead the better defense pick on small slices.

4. **Data:** `firmware_data.gd` gains two fields (`size_bonus_min_ticks`, `size_bonus_multiplier`). The multiplier is read where the slice output is computed in `combat_resolver` and the loadout preview. Depends on **N12** (`size_ticks`). Size **S–M**. Data-only fallback: leave the chip as is until N12 ships, then raise only `output_multiplier` to 1.4, which is a one-line change.

5. **Q:** Should Bulkhead be raised to +60% on DEFRAG/SANDBOX so it keeps a niche, or retired as redundant?
   **Q:** Does the size bonus read the slot's `size_ticks`, or the live slice size after any shrink effects?
