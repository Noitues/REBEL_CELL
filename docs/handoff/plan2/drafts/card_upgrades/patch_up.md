<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__patch_up; status ok; tokens in 5114 cache-write 0 cache-read 32585 out 1309; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: patch_up

1. **Role:** Cheap, neutral, one-shot emergency sustain. It sits below Stim Patch (3 RAM, heal 12) as the "I'm short on HP, not RAM" option, and exhaust keeps it from becoming a stalling engine.

2. **Upgraded card: Patch Up+** (one level is enough; there is no ladder here)
- **RAM cost:** 2 → 1.
- **Cycle cost multiplier:** ×1.5 (60 → 90), since the upgrade is a real cost cut.
- **Text:** "Heal 6. Remove CORRUPTED from a chosen slice. Exhaust."
- **Effects:**
  1. HEAL, target SELF, amount 6, amount_mode FLAT (unchanged).
  2. CLEANSE, target OWN_WHEEL, slice_pick CHOSEN, status CORRUPTED, ring_scope OUTER, duration 0.
- **Exhaust:** true (kept). **wheel_target:** OWN (unchanged).
- **Why this and not a bigger heal:** the heal number stays at 6 so Stim Patch keeps its niche. The rider is a mini Sanitize. Under R9, a CORRUPTED slice costs 2× RAM, so the cleanse refunds RAM over the next turns. At 1 RAM the card can cleanse and heal on a turn when the player could otherwise only afford one of the two.
- **Sidegrade, not a strict upgrade:** the + version has no block (Sanitize gives 3), and it costs 50 % more Cycles. It also doesn't scale: heal stays 6. A player with a clean wheel gets only a 1-RAM discount, which is the whole benefit. Only a corrupted wheel makes it clearly better.

3. **Interplay:**
- **R9 (corruption as RAM tax):** this is the main synergy. Cleansing a slice the pointer will read, or one your cards act through, saves RAM for the rest of the turn. It is also a natural answer to Genome Core P2–P4, where every IV scales with your CORRUPTED count (the heal and cleanse are one play there).
- **R8 (statuses):** the cleanse removes only CORRUPTED. It does not touch OUTPUT_DOWN or TIER_DOWN, so Cleanse and Encrypt keep their jobs.

4. **Data:** changes against the current .tres:
- `ram_cost` 2 → 1.
- `cycle_cost` 60 → 90.
- `display_name` "Patch Up+" and the new description.
- Add a second sub_resource effect: type 15 (CLEANSE), target 1 (OWN_WHEEL), slice_pick 2 (CHOSEN), status 1 (CORRUPTED).
- The heal stays FLAT. This is a data-only change that reuses the existing CLEANSE effect and the chosen-slice picker already used by Cleanse and Sanitize, so there is no new system. The optional `amount_mode` field (N1) is not needed, because the heal is unchanged. If hub heals ever move to PERCENT, this card stays FLAT and, under R2, does not scale with tier because it is a player card.
- Add a `base_id = patch_up` / `upgrade_of` field, or whatever the card-upgrade pass decides. Card upgrades have no data home yet: NEW: card upgrade linkage.

5. **Q:**
- Q: Should the chosen-slice picker allow skipping when no slice is CORRUPTED, so the card isn't blocked from playing and the 1-RAM heal stays usable on a clean wheel?
- Q: Is a heal-6 + cleanse card too close to Sanitize (cleanse + block 3) for deck slots, or should the + keep the heal-only identity with a flat cost cut, to RAM 1 and nothing else?
