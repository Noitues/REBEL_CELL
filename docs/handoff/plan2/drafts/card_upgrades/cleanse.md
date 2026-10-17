<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__cleanse; status ok; tokens in 5084 cache-write 0 cache-read 32585 out 1261; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: cleanse

1. **Role:** The cheap, precise answer to one CORRUPTED slice. Under R9 it is also the player's RAM economy repair, because each corrupted slice doubles the RAM cost of anything done there.

2. **Upgraded card: "Cleanse+"** (one level is enough; a second level would only add more riders)
- RAM cost: 1 (unchanged)
- Cycle cost multiplier: ×1.5 (55 → 83)
- Text: "Remove CORRUPTED from a chosen slice. If it was CORRUPTED, that slice is ENCRYPTED."
- Effects, in order:
  1. CLEANSE: target OWN_WHEEL, slice_pick CHOSEN, status CORRUPTED (unchanged).
  2. APPLY_STATUS: target OWN_WHEEL, slice_pick CHOSEN (the same slice as step 1), status ENCRYPTED, amount 1. It applies only if step 1 removed a CORRUPTED status (new condition, see Data).
- exhaust: false
- wheel_target: OWN (0)

Why this rider: Cleanse+ becomes a repair plus a ward, so it is no longer only a patch. Encrypt already exists as a separate 1-RAM card, so the rider gives a 2-for-1 only on the cleansed slice. It is not a free Encrypt anywhere you like, because it needs a CORRUPTED target.
- Dead-card cost: on a clean wheel it does what Cleanse does (nothing), so the upgrade has no value there. That keeps it a sidegrade by situation, not a strict dominator.
- Cycle price: the ×1.5 cost covers the extra value.
- Rejected alternatives: a RAM refund on cleanse (it creates an exploitable loop with R9 doubling) and a "cleanse all" version (it replaces Sanitize and Encrypt).

3. **Interplay**
- R9: cleansing a slice you need to use this turn does not refund the doubled cost already paid. Order matters, so play Cleanse+ first.
- R8: ENCRYPTED absorbs the next status, which blocks re-corruption from Immunization or Code Blue in the Genome Core fight, but only the first hit. Under Code Blue (every hit corrupts) ENCRYPTED protects one slice for one hit.
- Parasite ring: Cleanse does not remove ring parasites (N10 defines "Cleanse removes a segment" separately). The + version does not change that.
- ×N stacks (N8): Cleanse removes CORRUPTED only, not OUTPUT_DOWN.

4. **Data**
- `cycle_cost` 55 → 83, plus a second EffectData (APPLY_STATUS, target 1, slice_pick 2, status 3 ENCRYPTED).
- New: a `requires_prior_removal` condition flag on the follow-up APPLY_STATUS. NEW: effect condition flag, S size, in `effect_interpreter`.
- Data-only fallback: drop the condition and always apply ENCRYPTED. That makes Cleanse+ a Cleanse and Encrypt for 1 RAM at a ×1.5 price, which is too strong. If the flag is not built, use the fallback only with RAM cost 2.
- Needs a separate card id (`cleanse_plus`) and an upgrade link on `CardData` (NEW: `upgrade_of`, S).

5. **Q:**
- Should ENCRYPTED applied through a Cleanse+ be exempt from absorbing its own re-corruption in the same resolve?
- Should the + version waive its Cycle surcharge at a Workshop (D4 node) where upgrades are sold?
