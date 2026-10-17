<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__overvolt; status ok; tokens in 2386 cache-write 0 cache-read 32585 out 1251; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: overvolt

**Verdict:** CHANGE

1. **What it does today:** SHIM and OVERFLOW slices get ×1.25 output (cost 90, common). It is the cheap, offense-only version of patch_plus (×1.5, any slice). Breaker and Ghost, which run many SHIMs, would put it on a SHIM; no class would give it a second look otherwise.

2. **Under the new rules:**
   - **Strictly worse than patch_plus.** patch_plus is ×1.5 for 100 and fits any slice, so overvolt is a trap pick today. It has no niche.
   - **OUTPUT_DOWN (R8, −25 % per stack).** Today's ×1.25 is multiplicative, so one stack lands at about ×0.94 and wipes the chip out. That is the anti-firmware interaction R8 wants, but a chip this small barely registers it.
   - **Size variance (R11).** On a 2-tick slice (G G) the chip is flat; on a 6-tick slice a WEAK landing at 0.5× still wastes it. Nothing breaks, but there is no sizing hook.
   - **Parasites and corruption.** A parasite that cuts "your damage to the boss" stacks multiplicatively with the chip. Corruption costs RAM and does not touch output.
   - **Degeneracy.** None: there are no loops. The risk is just a dead pick.
   - **Calibrated Firmware (R11).** A 4-tick slice reads G P P G, so a Perfect-conditioned chip becomes much stronger there. That is the best hook for a differentiated overvolt.

3. **Proposed spec:** identity: a *glass-cannon* damage chip that rewards precision and is the natural Perfect-hunter's chip.
   - Description: "SHIM and OVERFLOW slices: output +25%. On a Perfect, +25% more (+50% total)."
   - Rarity 0 (common), Cycle cost 90, allowed_slice_types [0, 1], output_multiplier 1.25.
   - New conditional: `perfect_multiplier` 1.5 (the N20 rider, reused at firmware level; it applies only to this chip's own output).
   - Reads on the slice as a small lightning pip, with a second pip lit when the landing is Perfect.
   - It does not stack with the Breaker hook's double resolve in any special way: each resolve reads its own tier.
   - Against patch_plus: overvolt wins only if the player lands Perfects (centre-tick on odd sizes, or Calibrated), and loses on WEAK or GOOD landings. That is a real tradeoff and a reason to prefer it on a 3-tick slice (G P G), where Perfect is the middle tick.
   - Status handling: one OUTPUT_DOWN stack still takes −25 %, so the net is ×0.94 on non-Perfect and ×1.13 on Perfect. This is intended.

4. **Data:** `output_multiplier` stays 1.25; add `perfect_multiplier` 1.5 to `firmware_data.gd`, or implement it as a `triggered_effects` entry on ON_PERFECT if that is cleaner. Either way it is N20 (S–M); the data-only fallback is plain ×1.25 with a cost drop to 70, which keeps it as the cheap budget option. The Perfect mapping needs N12 for full value.

5. **Q:**
   - Q: Should `perfect_multiplier` live on FirmwareData, or only on SliceData per N20, with a Firmware-level override?
   - Q: Does the Breaker's Perfect hook (resolves twice) apply the Perfect bonus on both resolves? I propose yes, and want a balance check.
