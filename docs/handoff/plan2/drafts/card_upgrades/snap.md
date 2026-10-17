<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__snap; status ok; tokens in 5084 cache-write 0 cache-read 32585 out 1274; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: snap

1. **Role:** Neutral precision tool. It converts any landing into a Perfect on the nearest slice, so the player can enable Perfect hooks and ×4-style payoffs. It is the reliable but expensive (2 RAM) answer to bad respins.

2. **Upgraded card: Snap+ ("Snap+")**
- **RAM cost:** 1 (down from 2). Reasoning: the card exists to save RAM versus nudging. Today a 2-tick correction costs 1 RAM (after the free nudge) and Snap costs 2, so Snap only pays off against steering and Perfect-hook turns.
- **Cycle cost multiplier:** ×1.25 (65 → 81). The card gets cheaper to play, so it costs more to buy.
- **Text:** "Move your outer ring to the nearest slice centre (Perfect). The next card you play this turn that moves a wheel costs 0 RAM... " **Rejected.** That rider turns it into a combo card.
- **Chosen text:** "Move your outer ring to the nearest slice centre (Perfect). Costs 1 RAM."
- **Effects:**
  1. `SNAP_TO_CENTER` (type 16), target OWN_WHEEL (1), ring_scope OUTER (0), amount 0, duration 0. This is unchanged.
- **Exhaust:** false (unchanged).
- **wheel_target:** OWN (0, unchanged).

Why a pure cost cut: this is the "cost reduction" option. It sharpens the card without changing what it does. It does not dominate every cost point, because Lock On (0 RAM, exhaust) remains the cheaper one-shot. Snap+ stays the repeatable option, so it is a sidegrade at the margin.

Alternative considered: keep 2 RAM and add the rider "the Perfect landing is protected from TIER_DOWN this turn". **Rejected** as too niche while TIER_DOWN does not exist yet.

3. **Interplay**
- **Variable slice sizes:** on 4-tick slices (no Perfect) and any even slice with no centre tick, Snap lands on the best sub-tick (GOOD) and the "(Perfect)" text is false. Snap must target the nearest best-quality tick, not the geometric centre.
- **Corruption as double RAM:** playing it while the pointer reads a CORRUPTED slice costs 2 RAM, and 1 RAM after the upgrade. This makes the cheaper cost matter more.
- **Calibrated Firmware:** this keeps Snap useful on 4-tick slices, which read G P P G.

4. **Data**
- `ram_cost` 2 → 1.
- `cycle_cost` 65 → 81.
- `display_name` "Snap+".
- `description` updated.
- The effect list and its fields are unchanged.
- Add an upgrade link (e.g. `upgrade_of = &"snap"`) as a field of the upgrade system. **NEW: card upgrade system** (a pass of its own). A data-only fallback is a separate `snap_plus.tres` with `offered = false` until upgrades exist.
- The ghost and phantom class files reference `snap`. They must keep referencing the base card. The upgrade is applied at runtime, so no class-file edits are needed.
- The "best sub-tick" behaviour needs **N12** (`snap_to_center` on variable sizes).

5. **Q:**
- Q: Should Snap on a size-4 slice (no Perfect) pick a GOOD tick, or stay refused and show a "no Perfect available" preview?
- Q: Does Snap+ at 1 RAM make Lock On (0 RAM, exhaust) redundant in neutral decks, so that Lock On needs its own revisit?
