<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__leech_worm; status ok; tokens in 5140 cache-write 0 cache-read 32585 out 1233; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: leech_worm

1. **Role:** A neutral, expensive (3 RAM), exhaust answer to one dangerous enemy slice. It halves that slice's output for the rest of the combat, as a per-fight "turn off the big hit" tool.

2. **Upgraded card: Leech Worm+** (one level is enough; the card is a single-target status applier with little to scale)
- **RAM cost:** 2 (was 3). **Cycle cost multiplier:** ×1.5 (75 → 113).
- **Exhaust:** true (kept). **wheel_target:** ENEMY (1, unchanged).
- **Text:** "Pointed enemy slice gets a PARASITE (half output). If that slice is already PARASITED, ENCRYPTED, or NULL, the worm jumps to a random non-NULL slice instead. Exhaust."
- **Wait, simplified (chosen):** "Pointed enemy slice gets a PARASITE (half output). A second worm lands on the slice opposite the pointer. Exhaust." The second worm is a wider-target rider, but it needs a new slice pick, and a bonus slice with no player control is weaker design. So the final choice is a **cost cut plus a free second pick**:
- **Effects (final):**
  1. APPLY_STATUS, target TARGET_WHEEL, status PARASITE, slice_pick UNDER_POINTER, duration 0 (as today).
  2. APPLY_STATUS, target TARGET_WHEEL, status PARASITE, slice_pick CHOSEN, duration 0. Skipped if no valid slice remains.
- **Text:** "Pointed enemy slice gets a PARASITE (half output). Then choose a second enemy slice to PARASITE. Exhaust."
- **RAM 3 → 3, Cycle ×1.5.** The rider (a second, chosen slice) is what makes it sharper, and the RAM stays at 3 so it isn't a strict dominator: the + version is a sidegrade-leaning upgrade for boss wheels with several threats, while the base card stays better as a cheap single answer. The tradeoff is a higher shop price, not a lower RAM cost.

3. **Interplay:**
- Under R8, PARASITE becomes a 2-stack OUTPUT_DOWN (−25 % per stack, −50 % total). The two worms remain a 50 % cut on each slice, so the card stays consistent after N8/N9.
- ENCRYPTED enemy slices absorb the first worm, so the second pick lets you route around that.
- With variable slice sizes (N12) the chosen pick can hit a 3-tick Medicine slice that a pointer-only card would miss.
- With statuses kept across phases (R6), both worms survive via the centre-tick remap, unless the boss has Sterile Field.

4. **Data:**
- Add a second `EffectData` sub-resource (`fx1`) with slice_pick = 2 (CHOSEN).
- Change `description`.
- Change `cycle_cost` 75 → 113.
- `ram_cost` stays 3.
- Set `id` to `leech_worm_plus`.
- No new system. It uses the existing SlicePick.CHOSEN as Cleanse and Encrypt do. N8/N9 only change what PARASITE means.
- **Fallback:** none needed.

5. **Q:**
- Should the second target be CHOSEN (more control, an extra UI step) or the slice opposite the pointer (deterministic and no UI, but less choice)?
- Should upgrades share a rule that "+ never lowers RAM below the base card's RAM cost when it also adds a rider"?
