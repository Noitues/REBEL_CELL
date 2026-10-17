<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__corrupt_packet; status ok; tokens in 5130 cache-write 0 cache-read 32585 out 1277; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: corrupt_packet

1. **Role:** Neutral 1-RAM targeted status applicator. It plants CORRUPTED on the enemy slice under your pointer, so you can pick which slice gets hit instead of leaving it random like Malware Drop.

2. **Upgraded card: Corrupt Packet+** (one + level only)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5, so 90 from 60.
- **Text:** "CORRUPT the enemy slice under your pointer. If it is already CORRUPTED, CORRUPT the next non-NULL slice clockwise instead."
- **Effect list:**
  1. APPLY_STATUS, target POINTER_TARGET (currently 2 = TARGET_WHEEL), status CORRUPTED, slice_pick UNDER_POINTER, duration 0.
  2. A second APPLY_STATUS with the same fields, but a conditional "only if the first landed on an already CORRUPTED slice" and a clockwise-next-non-NULL pick.
- **Exhaust:** false.
- **wheel_target:** ENEMY (1, unchanged).
- **Why a rider, not a bigger number:** the base card wastes itself when it hits a slice that is already CORRUPTED, which is a dead draw on a wheel with few slices. The rider removes that dead draw and keeps the role. It is not strictly better at every cost point: the extra Cycle cost and the redirected placement can pull the status off the slice you wanted.

3. **Interplay:**
- **Corruption as double RAM (R9):** on an enemy wheel CORRUPTED has no defined effect yet (Q3 in V2 §7). This card stays a setup card until that is ruled. If Virus-style enemy CORRUPTED becomes a RAM or output debuff on the enemy, the rider spreads it across two slices.
- **Variable slice sizes:** a 3-tick or 4-tick slice is hard to line up under a pointer, so the redirect is a bonus when you land on a small slice twice.
- **ENCRYPTED (R8):** if the first target slice is ENCRYPTED, the status is absorbed and the card is spent. The + does not change that. Say so in the tooltip.

4. **Data:**
- `cycle_cost` 60 → 90.
- `description` updated.
- A second `EffectData` sub_resource is added.
- **Fix:** the existing `fx0` has `target = 2`, which is TARGET_WHEEL. Compare it with Malware Drop before copying the fields.
- **New effect needed:** NEW: conditional-chain APPLY_STATUS. Either a `slice_pick` value NEXT_CLOCKWISE_NON_NULL_IF_ALREADY_STATUS, or a CUSTOM `custom_handler` script. No N# fits.
- **Data-only fallback:** none that matches the exact text.
  - **Weaker fallback, usable now:** make the card hit TWO distinct slices, the pointed slice plus the next non-NULL slice clockwise, as two plain `APPLY_STATUS` effects with `slice_pick` UNDER_POINTER and a new NEXT_CLOCKWISE value.
  - **Sidegrade fallback:** `ram_cost` 0 (a cost reduction), with no code change.
- No save impact (N8 is not required).
- **Preview:** the preview must show both slices, since the preview must equal the result.

5. **Q:**
- Q: Should the + rider be a CUSTOM handler, or a new `slice_pick` value (cheaper to preview and test)?
- Q: Is the 0-RAM cost reduction a better + once CORRUPTED on enemies has a defined effect?
