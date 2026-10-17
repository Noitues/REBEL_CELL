<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__bulwark; status ok; tokens in 5103 cache-write 0 cache-read 32585 out 1314; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: bulwark

1. **Role:** Neutral 2-RAM burst defense. It turns a 2-RAM turn into a safe turn against one big hit. BLOCK expires at the start of your next turn (R13), so it only covers the incoming resolve.

2. **Upgraded card: Bulwark+** (one + level is enough; a second level would be a different card)
- **RAM cost:** 2 (unchanged).
- **Cycle cost multiplier:** ×1.5, so 90 Cycles against 60 today.
- **Text:** "Gain 16 block. If your outer pointer reads a Perfect or Good landing, gain 4 more."
- **Effects (EffectData):**
  1. `GAIN_BLOCK`, target SELF (0), amount 16, `amount_mode` FLAT, ring_scope OUTER (unused).
  2. `GAIN_BLOCK`, target SELF, amount 4, FLAT, conditioned on your current landing tier ≥ GOOD. This reads the preview state, so it stays deterministic.
- **Exhaust:** false. **wheel_target:** OWN (0).

   The base is +4 (12 → 16) and the rider is +4 more. Reaching 20 needs a clean landing, which rewards precision (pillar 1). The card stays a flat block card. A single flat 16 would dominate; the conditional rider is where the upgrade's value varies. Since a WEAK landing gives only 16, a nudge to GOOD is worth 4 block, a real choice against a spent nudge or RAM.

   *Sidegrade check:* Firewall at 1 RAM for 6 block is 6 block per RAM. Bulwark+ at 16–20 for 2 RAM is 8–10 per RAM. Firewall stays better for cheap top-ups when you need less than 12.

3. **Interplay:**
   - The rider reads the tick map (R11). A 4-tick slice (W G G W) has no Perfect but two GOOD ticks, so the rider fires on 50 % of its ticks. A 2-tick slice (G G) always fires it.
   - Pierce (R13) ignores BLOCK entirely, so Bulwark+ is dead against Adrenaline in Genome Core P4. SANDBOX is the answer there. This is the intended weakness.
   - On a CORRUPTED slice the card costs 4 RAM (R9), but only if the pointer reads that slice. Bulwark is a card, so the doubling applies when you play it from a CORRUPTED reading. Cleanse first.

4. **Data:**
   - `ram_cost` 2 → 2.
   - `cycle_cost` 60 → 90.
   - `fx0.amount` 12 → 16.
   - Add `fx1` (the conditional GAIN_BLOCK 4).
   - `description` updated.
   - `id` is `bulwark_plus`, with `display_name` "Bulwark+".
   - **Systems:** `amount_mode` is N1 (can be omitted, since FLAT is the default). The conditional needs a "landing ≥ tier" condition on the effect. It does not exist: NEW: `EffectData.require_tier` (S, a field plus a check in `effect_interpreter`).
   - **Data-only fallback:** drop fx1 and use `amount` 18 flat at 2 RAM and Cycle ×1.5. This is a pure bigger-number upgrade, but it loses the precision hook.

5. **Q:** Does the tier condition read the landing at play time, or at resolve? Reading it at play time lets later nudges break the preview. I propose play time, the same as `steady_hand`.
   **Q:** Should enemy-side tier-scaled BLOCK values compete with this? Today's BLOCK is not scaled by tier on the player side, but the Genome Core P2 Barrier is 20. Is a 16–20 cap what you want against it?
