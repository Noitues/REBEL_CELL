<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__coolant_loop; status ok; tokens in 2585 cache-write 0 cache-read 32585 out 1196; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: coolant_loop

**Verdict:** CHANGE

1. **What it does today:** Once per combat, a Perfect on this slice (min_tier 2) applies MODIFY_HEAT −1 to the campaign. Any slice type can carry it, and the role is a campaign-economy chip for Heat-management builds. It sits in the same niche as the Clean Signal, Cold Exit and Scrubber Daemons.

2. **Under the new rules:**
   - **Perfect access splits by size.** A 2-tick slice (G G) and a 4-tick slice (W G G W) have no Perfect, so the chip is dead there unless a "Calibrated" Firmware lifts the ticks. A 3-tick slice (G P G) makes Perfect 1 tick in 3. Only 3-, 5- and 7-tick slices carry it. It also has to compete for the one socket with Patch+.
   - **It is nearly dead weight.** One Heat per combat is about 5 per run, and it pays only if a Perfect lands on one specific slice, which is a poor use of a socket. Burner puts Heat into the same socket and loses.
   - **No loop risk.** The limit is 1 per combat, so it is safe.
   - **Enemy listeners are the new hazard.** Halcyon's Clawback-style listeners punish a Perfect. A chip that wants Perfects now sits across a real tradeoff, which makes it more interesting.
   - **Statuses:** TIER_DOWN reads a Perfect as Good, so the trigger fails. Stacks make the chip unreliable and give Cleanse and Encrypt a reason to protect the slice. OUTPUT_DOWN does not affect it, and neither does CORRUPTED (it only taxes RAM).
   - **Parasites:** a parasite that reduces your damage does not touch a Heat effect.

3. **Proposed spec:**
   - **Description:** "Once per combat, when this slice lands Good or better, lowers Heat by 1. A Perfect lowers it by 2."
   - **Rarity:** 1 (uncommon). **Cost:** 120.
   - **allowed_slice_types:** any (unchanged).
   - **Triggered effects:**
     - te0: ON_SLICE_TRIGGER, min_tier GOOD, limit 1 per combat, MODIFY_HEAT −1.
     - te1: ON_PERFECT, limit 1 per combat, MODIFY_HEAT −1 more. Total is 2 on a Perfect, so a Perfect only adds value.
   - **Reads on the slice:** a small coolant icon on the socket. The preview shows "HEAT −1" or "HEAT −2".
   - **Why:** Good access makes it work on 2- and 4-tick slices, so it is no longer dead there. It is also not dominated by Patch+ when Perfects are scarce.

4. **Data:** change `min_tier` from 2 to 1 on te0, add an ON_PERFECT effect te1, and update rarity, cost and description. This is data-only, **S**. It needs no N# (the triggers exist). The preview line for MODIFY_HEAT is not in the N-list. It is covered by the existing preview system, so check it as part of the change.

5. **Q:**
   - Should the total be capped at 2 Heat per combat, or should a Perfect give 1 and a Good 1, ignoring tier?
   - Should Heat-reduction chips be exclusive to Rack or elite rewards, to keep the Heat-sink economy in tune with the Daemons?
