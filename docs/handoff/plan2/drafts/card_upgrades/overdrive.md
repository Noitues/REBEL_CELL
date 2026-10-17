<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__overdrive; status ok; tokens in 5247 cache-write 0 cache-read 32585 out 1291; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: overdrive

1. **Role:** The Breaker's setup card. It spends 1 RAM to turn one slice into a single 1.5× trigger, accepting the CORRUPTED aftermath. It rewards planning a Perfect (or the Perfect hook's double resolve) on a chosen slice.

2. **Upgraded card: Overdrive+** (one + level only; there is no need for a second.)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (60 → 90).
- **Text:** "OVERCLOCK the pointed slice: 1.75x once, then CORRUPTED. If the slice is a defensive type, it is not corrupted afterwards." (Placeholder wording.)
- **Chosen upgrade: a bigger number plus a narrow rider, not a flat dominant buff.** The card is still the pointed-slice OVERCLOCK. The rider is a sidegrade: it is useless on offensive slices, which are the Breaker's main use, and strong only if you pick a defensive slice. That keeps the choice real.
- **Effect list:**
  1. EffectData: type APPLY_STATUS, target OWN_WHEEL, status OVERCLOCKED, slice_pick UNDER_POINTER, ring_scope OUTER, duration_turns 0, amount 0.
  2. Status parameter (see Data): the OVERCLOCKED multiplier of 1.75 for this application, instead of the global 1.5.
  3. Burnout rider: `burnout_to_corrupted = false` when the slice type is DEFRAG, SANDBOX or DETOUR.
- **Exhaust:** false. **wheel_target:** OWN (0).

3. **Interplay:**
- With corruption as double RAM, the burnout is a real cost. The rider lets a BLOCK, SHIELD or SANDBOX slice take the 1.75× without the later RAM tax, so the + version leans toward defensive overclock builds. Offensive builds still pay the corruption tax for 0.25× extra, which is not strictly dominant.
- Calibrated Firmware (R11) stacks multiplicatively on tick quality. A 4-tick slice made G P P G gives two Perfect ticks, which combine well with the Breaker's Perfect hook.
- The overclock is a status, so ENCRYPTED on the slice absorbs it. TIER_DOWN lowers the landing tier before the multiplier applies, which is fine.

4. **Data:**
- `cycle_cost` 60 → 90.
- `id` → `overdrive_plus` (new file; `display_name` "Overdrive+"; `description` updated).
- Effect 1 unchanged from the current .tres.
- **New (data-only, small):** `EffectData.multiplier` is already an existing field, so set `multiplier = 1.75` on the APPLY_STATUS effect. The handler must store it as the stack's multiplier. If it ignores it today, that is a small change in `effect_interpreter.apply_status` (N9-adjacent, S).
- **New:** the burnout exemption needs a flag, **NEW: `status_burnout_exempt_types`** on EffectData, an S-sized change to the OVERCLOCKED burnout path. **Fallback:** drop the rider and ship the 1.75× only (data-only if `multiplier` is honored).
- Update the class files' references (breaker, wrecker) only when upgrades are wired.

5. **Q:**
- Q: Does the OVERCLOCKED multiplier live on the status instance (needed for 1.75× to differ from the Burner Firmware's 1.5×), or is it global?
- Q: Should the burnout exemption cover a Perfect-hook double resolve, so the first resolve overclocks and the second does not re-corrupt?
