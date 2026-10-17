<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__nanite_mesh; status ok; tokens in 2595 cache-write 0 cache-read 32585 out 1426; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: nanite_mesh

**Verdict:** CHANGE

1. **What it does today:** On a HOTFIX slice, output ×1.5, and the slice cleanses itself after resolving (trigger 5 = ON_SLICE_TRIGGER, effect 15 = CLEANSE, target OWN_WHEEL, slice_pick 0 = UNDER_POINTER). Role: the HOTFIX slice is enemy-facing. The player classes (Breaker, Ghost, Rigger, Botnet) have none, so the chip is a dead pick for players. Its only live use is on REBEL_CELL mirror elites and the Genome Core (Hub heal is not a slice).

2. **Under the new rules:**
   - **Broken:** HOTFIX is not on any player wheel, so `allowed_slice_types = [6]` leaves it unsocketable in practice.
   - **Better:** under R8, statuses are anti-firmware (OUTPUT_DOWN, TIER_DOWN, ×N stacks). A self-cleanse is the right idea, but it must fit a slice the player owns. Under R9 CORRUPTED costs 2× RAM, so a self-clean on a slice you rely on is real economy.
   - **Degenerate risk:** a cleanse that fires on every trigger makes OUTPUT_DOWN ×N and CORRUPTED meaningless on that one slice. It also beats Encrypt (one-shot absorb) and Cleanse cards. The cleanse should be limited, and should never touch the Parasite ring.
   - **Size interaction:** the self-cleanse has no tick dependence, so it is safe on 2-tick and 6-tick slices. A 2-tick slice (G G) never gets Perfect, so any Perfect gate would be dead there. Do not gate on Perfect.
   - **Ordering:** cleanse after the output is computed, so a ×N OUTPUT_DOWN still bites on the triggering resolve. Unwinding it afterward is the benefit.

3. **Proposed spec:** retarget to the player's defensive slices and make it a status-reset chip.
   - **Description:** "DEFRAG and SANDBOX slices: after resolving, remove 1 stack of OUTPUT_DOWN or TIER_DOWN from this slice, or CORRUPTED if it has no other debuff. Once per turn."
   - **Rarity:** 1 (uncommon). **Cost:** 110.
   - **allowed_slice_types:** [2, 4] (DEFRAG, SANDBOX). Mapped to BLOCK and SHIELD under R13. It is an uncommon sibling of bulkhead, not a replacement.
   - **Multiplier:** 1.0 (drop the +50 %; the output bonus already belongs to patch_plus and bulkhead).
   - **Trigger:** ON_SLICE_TRIGGER, CLEANSE with `slice_pick = UNDER_POINTER` (the resolved slice), 1 stack, priority: OUTPUT_DOWN, TIER_DOWN, CORRUPTED. Cap of 1 per turn on the chip. Parasite segments are untouched.
   - **Reads on the slice:** a small green droplet glyph; the tooltip shows "−1 stack on resolve".
   - **HOTFIX niche:** HOTFIX is enemy-only, so the old version remains only as an enemy-side data note. Retire the player listing.

4. **Data:**
   - `allowed_slice_types` [6] → [2, 4].
   - `output_multiplier` 1.5 → 1.0.
   - Cleanse effect gains a stack count and priority order.
   - Needs N8 (×N stacks) and N9 (status rules). The once-per-turn cap is a counter on the chip.
   - **Data-only fallback:** the current single-status CLEANSE with the type list change. Size S as a fallback, M with N8/N9.

5. **Q:** Should the cleanse also work on enemy-applied statuses from listeners (N6) mid-resolve, or only those present at turn start?
   **Q:** Should a HOTFIX-capable player class exist, or is HOTFIX permanently enemy-facing?
