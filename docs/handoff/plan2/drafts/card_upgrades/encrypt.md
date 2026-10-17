<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__encrypt; status ok; tokens in 5094 cache-write 0 cache-read 32585 out 1202; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: encrypt

1. **Role:** Cheap, neutral status insurance. It makes one chosen slice immune to the next status, a pre-emptive answer to Citations, Flares and Immunization corruption.

2. **Upgraded card: Encrypt+** (one level only; nothing here needs a second)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (55 → 83, as a Mainframe or reward-pool upgrade price).
- **Text:** "ENCRYPT a chosen slice and the slice opposite it: each absorbs the next status."
- **wheel_target:** OWN (0). **exhaust:** false.
- **Effects** (two EffectData entries, both identical in kind):
  1. APPLY_STATUS, target OWN_WHEEL, status ENCRYPTED, slice_pick CHOSEN, ring_scope OUTER, duration_turns 0.
  2. APPLY_STATUS, target OWN_WHEEL, status ENCRYPTED, slice_pick OPPOSITE, ring_scope OUTER, duration_turns 0. (OPPOSITE is the slice 3 positions away in slot order.)
- **Why this rider (wider target):** it stays the same card, and the second slice is usually not the one you wanted, so the upgrade is a bigger-number sidegrade rather than a dominating one. With only one ENCRYPTED slot per slice, re-casting it on an already encrypted slice is wasted, so the second entry does nothing if the opposite slice is already encrypted. There is no cost change, so it strictly dominates the base card at the same RAM. I accept that, because the Cycle price (×1.5) is the real cost and a card that is only a modest gain doesn't need a sidegrade. If the designer wants an actual tradeoff, see Q1.

3. **Interplay**
- **Variable slice sizes:** "opposite" is defined by slot order, not by ticks, so it stays meaningful with uneven sizes. It is also where the Cell's wide, safe slices go, so the second pick is rarely a waste.
- **Statuses as anti-firmware (R8, ×N stacks):** ENCRYPTED absorbs one status application, so against a ×3 Citation it blocks only the first stack. Encrypt+ is best used pre-emptively on the two slices you expect to be read.
- **Corruption as double RAM:** it blocks CORRUPTED on both slices, which protects your RAM economy against Genome Core's Immunization and P4's Code Blue.

4. **Data**
- Changed fields: `id` → `encrypt_plus`, `display_name`, `description`, `cycle_cost` 55 → 83, plus one extra `EffectData` sub-resource (the second APPLY_STATUS).
- **New:** `SlicePick.OPPOSITE` (enum value, N-less). **Fallback:** drop the second entry and use `slice_pick = CHOSEN` twice (the player picks two slices, play-time prompt twice). This needs no new enum but requires the card interpreter to prompt twice, which it already does for multi-effect CHOSEN cards.
- No N# dependency otherwise.

5. **Q:**
- Q: Is OPPOSITE worth a new enum value, or is two CHOSEN picks (more player agency, more clicks) the better + version?
- Q: Should the + version cost 2 RAM and carry a third pick (a true tradeoff), or stay at 1 RAM with the Cycle price as the balancing cost?
