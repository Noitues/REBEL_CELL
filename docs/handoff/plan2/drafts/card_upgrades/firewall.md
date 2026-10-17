<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__firewall; status ok; tokens in 5100 cache-write 0 cache-read 32585 out 1169; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: firewall

1. **Role**: The cheapest reliable BLOCK, a 1-RAM filler that blunts one incoming turn without spending a slice. It is the neutral baseline of the R13 defense trio.

2. **Upgraded card**: "Firewall+" (one level is enough; a second level would only be a bigger number).
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.5 (50 → 75).
- **Text:** "Gain 8 block. If you have no block, gain 4 more."
- **Effects:**
  1. GAIN_BLOCK, target SELF, amount 8, amount_mode FLAT.
  2. GAIN_BLOCK, target SELF, amount 4, FLAT, conditional on "block = 0 at play time" (the rider).
- **Exhaust:** false. **wheel_target:** OWN (0).

**Why this shape:** The base is 6 for 1 RAM. The + gives 8 on a second copy or when stacked after a Bulwark, and 12 as the opener, which matches Bulwark (12 for 2 RAM) at half the RAM. A flat +2 alone is too dull. The "first block of the turn" rider rewards playing it first and discourages stacking several. Stacking Firewalls therefore yields 12 + 8 + 8, not a runaway. It is not strictly dominant: Bulwark+ and slice BLOCK still beat it in a block-heavy hand, and opening with it taxes sequencing.

**Preview = result:** The condition reads current block at staging. If an earlier staged card gives block, the preview shows 8, and undo restores the old value deterministically.

3. **Interplay**:
- **Corrupted slices:** Firewall is not slice-bound and costs only 1 RAM, so it is the best way to defend when R9's double RAM makes slice-reading cards expensive.
- **Pierce:** Genome Core P4's Adrenaline and other pierce hits ignore BLOCK entirely (R13), so the + is weak there. That is intended, and it is where SANDBOX and steering take over.
- **Enrage:** The bigger opener helps against enrage steps without outscaling Bulwark.

4. **Data**: Changes against the current .tres:
- `id`: `&"firewall_plus"` (or an `upgrade_of` field, see Q).
- `display_name`: "Firewall+".
- `description`: updated.
- `cycle_cost`: 75.
- `fx0.amount`: 6 → 8.
- Add `fx1` (GAIN_BLOCK, amount 4) with a condition.
- **New system:** the conditional effect needs a `condition` on EffectData ("owner block == 0"). NEW: effect conditions (small; EffectData is shared, so build it with N1's amount-mode work).
- **Data-only fallback:** drop the rider and use plain GAIN_BLOCK 9. It works with no new code but loses the sequencing texture.
- Under R5, amount_mode FLAT is the default once N1 lands. Player block is not tier-scaled.

5. **Q:**
- Q: Should upgrades be separate card ids (as above) or an `upgrade_of` link plus a `level` field on CardData, so the reward and shop UI can show a before/after?
- Q: Does a card that has conditions on state count as "different from the role"? If the designer prefers no conditions on commons, take the 9-flat fallback.
