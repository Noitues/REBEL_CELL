<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_015ftewqQnqUqce5GrnWp3Dj, custom_id fw__leech; status ok; tokens in 2510 cache-write 0 cache-read 32585 out 1308; cost $0.012. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# firmware: leech

**Verdict:** CHANGE

1. **What it does today:** a SHIM slice restores 1 RAM when it triggers at Good or better (ON_SLICE_TRIGGER, min_tier GOOD, GAIN_RAM 1). It is a common chip for SHIM slices. Breaker, Ghost, Rigger and Botnet all have several SHIM slices. The role is a small RAM engine that rewards accurate landings.

2. **Under the new rules:**
   - **Breaks:** quality now depends on slice size and the tick the pointer lands on. A 2-tick slice (G G) is never WEAK, so Leech always fires. A 4-tick slice (W G G W) is 50 % WEAK and a 3-tick slice is mostly GOOD. The chip therefore pays out by slice size, not by player skill. Good-or-better is also nearly free in the common case.
   - **Gets better:** it pairs with CORRUPTED. Corrupted slices cost 2× RAM, so +1 RAM is a real counter. TIER_DOWN lowers a landing by one tier, so a Perfect becomes Good and still pays. A Good becomes WEAK and pays nothing, which makes the chip a natural target for that status.
   - **Degenerate:** a flat +1 on each trigger stacks with Retrigger, Mirror (both neighbours on a Perfect), the Breaker's double-resolve Perfect hook and the Rigger's refund. Several SHIM slices with Leech make RAM effectively unlimited, and RAM drives nudges and cards. Leech also dies on a slice that is 6 ticks wide with a long WEAK fringe.
   - **Parasites and OUTPUT_DOWN:** neither touches the RAM rider. A parasite that drains RAM is a clean counter, which is good.
   - **Satellites:** satellites are fixed to a slice, so Leech on the host slice is not affected.

3. **Proposed spec:**
   - Description: "SHIM slice restores 1 RAM on Good or better. Restores 2 on a Perfect. Once per resolve, however many times the slice triggers."
   - Rarity 0 (common), Cycle cost 100, allowed_slice_types [SHIM].
   - Effects, both ON_SLICE_TRIGGER:
     - GAIN_RAM FLAT 1 at min_tier GOOD.
     - GAIN_RAM FLAT +1 more at min_tier PERFECT.
   - Cap: 1 trigger of the chip per resolve (`max_per_resolve = 1`).
   - Reads on the slice as a small RAM pip, with "+1 / +2" shown in the landing preview. The preview and the result are both deterministic.
   - Why: the Perfect bonus restores the skill gate that variable slice sizes erode. The per-resolve cap stops it stacking with Retrigger and Mirror. Total RAM per turn stays modest next to +4 base.

4. **Data:**
   - Fields changed: a second TriggeredEffectData (Perfect tier) and a new `max_per_resolve` field on TriggeredEffectData (or FirmwareData). `amount_mode` is not needed, since the amount is FLAT.
   - Dependencies: the per-resolve cap is NEW: trigger cap. A data-only fallback is to drop the cap and accept the stacking risk. The Perfect-tier bonus is data-only.
   - Size: S for the data change, S-M with the cap. Review again once N12 lands.

5. **Q:**
   - Q: Should a per-resolve cap be a general field on TriggeredEffectData, since other chips (Siphon, Skimmer) have the same stacking risk?
   - Q: Should Leech read the sub-tick quality of the actual landing, or the slice's best tick, on 2-tick slices where every landing is Good?
