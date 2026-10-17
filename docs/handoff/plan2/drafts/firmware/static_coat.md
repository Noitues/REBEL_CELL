<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__static_coat; status ok; tokens in 2561 cache-write 0 cache-read 32585 out 1456; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: static_coat

**Verdict:** CHANGE

1. **What it does today:** A DEFRAG slice also grants 2 SANDBOX shield (type 2 = DEFRAG, trigger 5 = ON_SLICE_TRIGGER, effect type 2 = GAIN_SHIELD). It's a common chip that turns a temporary-block slice into a hybrid. It suits Ghost and Rigger, which run two DEFRAG slices, and any build that wants lingering defense without spending a slice on shield.

2. **Under the new rules:**
   - **Mapping:** DEFRAG becomes BLOCK, and its shield becomes SHIELD (R13). The text "grants 2 shield" now reads as intended: a BLOCK slice that also leaves a lingering layer.
   - **Weak at any tier:** The flat 2 is not scaled by quality, and WEAK halves only the slice's own output. A 2-tick or 3-tick slice rarely lands WEAK, so the chip mostly pays 2 SHIELD per trigger. That is tiny against the cap of 15 and against enemy hits of 5–10. Compare bulkhead, which scales the whole slice, and barbed_wire, which adds damage. Static Coat is a dead pick.
   - **Dead on tick maps:** It has no sub-tick interaction, so it is not dead on small slices. It simply under-delivers everywhere.
   - **Degenerate risk:** If raised naively, a repeating or Retrigger BLOCK slice (Breaker Perfect hook, Echo ring, Mirror) stacks SHIELD up to the cap of 15, which makes enemy chip damage irrelevant. The Genome Core's IV chip hits and P2 Medicine would also be absorbed by SHIELD, though Adrenaline pierce ignores it.
   - **Statuses and parasites:**
     - OUTPUT_DOWN (−25 % per stack) should reduce the shield too. Today the chip's flat effect ignores it, which makes the chip an anti-status answer.
     - TIER_DOWN does not affect it, because the effect is not tier-gated.
     - A Parasite that reduces the slice's output should not be bypassed by this chip.
     - CORRUPTED doubles the RAM cost of acting on the slice; the chip does not interact.
     - ENCRYPTED/Hardened stacks fine.
     - Halcyon's Citation stacks make a defensive rider valuable.

3. **Proposed spec:**
   - **Description:** "BLOCK slice also gains SHIELD equal to 15% of your max HP on Good or better. WEAK landings grant half."
   - **Rarity:** 0 (common).
   - **Cycle cost:** 100.
   - **allowed_slice_types:** [2] (BLOCK only).
   - **Effect:** GAIN_SHIELD, `amount_mode` = PERCENT, amount 15, trigger ON_SLICE_TRIGGER, `min_tier` = GOOD. The percent value is 9 on Breaker (60 HP), 7 on Botnet (45 HP) and 8 on Ghost (50 HP), so it matters in the 5–10 hit range.
   - **Output scaling:** Output multipliers and OUTPUT_DOWN scale it; it is still bounded by `shield_cap` 15.
   - **On the slice:** The chip's socket shows a small shield glyph next to the BLOCK number, e.g. "12 + 9 SH", and the preview chip adds the shield line.

4. **Data:**
   - Set `min_tier = 1` and `amount = 15` on `te0`, and set `amount_mode = PERCENT` on `fx0_0` (the field is new).
   - Update `description`.
   - **Dependencies:** N1 (amount modes). A data-only fallback is FLAT 4 with `min_tier = 1`, which works today without N1.
   - **Size:** S.

5. **Q:**
   - Q: Should chip-granted PERCENT shield be scaled by OUTPUT_DOWN, or is it exempt so the chip counters Citation?
   - Q: Does a Retrigger of the slice (Breaker Perfect, Echo ring) fire this chip's shield again, or only the slice's own BLOCK?
