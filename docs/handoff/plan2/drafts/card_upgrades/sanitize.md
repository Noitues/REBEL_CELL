<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__sanitize; status ok; tokens in 5181 cache-write 0 cache-read 32585 out 1328; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: sanitize

1. **Role:** Cheap shared cleanse with a small defensive rider. It repairs a CORRUPTED slice, and under R9 that removes the 2× RAM tax on it.

2. **Upgraded card: Sanitize+** (a single + level is enough; no Level I–IV ladder needed)
- **RAM cost:** 1 (unchanged).
- **Cycle cost multiplier:** ×1.4 (55 → 77).
- **Text:** "Remove CORRUPTED from a chosen slice and gain 3 block. If the slice was CORRUPTED, ENCRYPT it."
- **Effects:**
  1. CLEANSE (type 15), target OWN_WHEEL, slice_pick CHOSEN, status CORRUPTED. Unchanged.
  2. GAIN_BLOCK, target SELF, amount 3, amount_mode FLAT. Unchanged.
  3. APPLY_STATUS, target OWN_WHEEL, status ENCRYPTED, slice_pick CHOSEN, same slice as effect 1. **Rider:** it applies only if effect 1 actually removed CORRUPTED, which makes it a conditional rider.
- **Exhaust:** false. **wheel_target:** OWN (0).
- **Why this rider:** it widens the card from "undo one corruption" to "undo it and cover that slice against the next status." That is the same job, done more durably. I rejected a bigger block number: block is the filler half of this card, and the cleanse is its point. I also rejected a cost cut to 0: a free Cleanse would crowd out Cleanse itself and Encrypt.
- **Not strictly dominant:** it costs 22 more Cycles, and it plays like Cleanse (1 RAM) + Encrypt (1 RAM) for 1 RAM. The conditional means it gives nothing extra on a slice that isn't CORRUPTED, so plain Sanitize stays the better buy as a pure 3-block play, or when the slice would hold ENCRYPTED anyway.

3. **Interplay:**
- **Corruption as RAM ×2 (R9):** the ENCRYPTED rider absorbs the next status, including a re-CORRUPT from Immunization or Code Blue. That keeps the slice cheap for a full cycle. Against Genome Core P2, where IV scales with your CORRUPTED count, this is strong.
- **Statuses vs Parasite ring (R8):** the rider does not stop parasites, because ENCRYPTED absorbs statuses only. The card stays anti-status.

4. **Data (changes against the current .tres):**
- `display_name` "Sanitize+", `cycle_cost` 77, new `description`.
- One added sub_resource: APPLY_STATUS, target 1, status 3 (ENCRYPTED), slice_pick 2.
- **New:** a "only if the preceding CLEANSE removed a status" condition on an effect. No N# fits; **NEW: conditional effect (`requires_prior_success`)**. A data-only fallback exists. Drop the condition, so ENCRYPT applies always. That makes the card ≈ Cleanse + Encrypt in one, still 1 RAM, and probably too strong. If the condition cannot be built, raise the RAM cost to 2 instead.
- **Slice targeting:** effects 1 and 3 must share one CHOSEN pick. `slice_pick = CHOSEN` is resolved per effect today, so the card needs a single shared chosen slice, a second **NEW** item. Check how Overdrive-style multi-effect cards resolve it.

5. **Q:**
- Should the ENCRYPT rider apply when the chosen slice is not CORRUPTED, with the condition dropped for simplicity and the RAM cost raised to 2?
- Is "reward pool only" intended to keep + versions out of Mainframes, or is that the same pool in the data?
