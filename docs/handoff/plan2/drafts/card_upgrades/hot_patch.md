<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__hot_patch; status ok; tokens in 5140 cache-write 0 cache-read 32585 out 1289; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: hot_patch

1. **Role**: A neutral setup card. It trades a slice's future (a CORRUPTED slice, which is now a 2× RAM tax per R9) for one 1.5× trigger. It is a burst tool for the one slice you plan to land.

2. **Upgraded card: Hot Patch+** (one level only; no Level I–IV needed)
- **RAM cost:** 2 → 1.
- **Cycle cost multiplier:** ×1.3 (65 → ~85).
- **Text:** "OVERCLOCK a chosen slice: 2× next trigger, then CORRUPTED."
- **Effect list:** one EffectData.
  - `type` APPLY_STATUS, `target` OWN_WHEEL, `status` OVERCLOCKED, `slice_pick` CHOSEN, `duration_turns` 0 (until triggered).
  - `amount` and `multiplier` are unchanged on the card. The 1.5× → 2.0× output lives in the status rule, so the + needs a per-application override (see §4).
  - `ring_scope` OUTER (unchanged).
- **Exhaust:** false → **true**.
- **wheel_target:** OWN (unchanged).

**Why a sidegrade:** the + is cheaper and hits harder (2× vs 1.5×), but it exhausts, so it can be played once per combat cycle. The base card stays the better pick for decks that cycle it repeatedly. The price is that you can no longer rebuy the CORRUPTED tax every shuffle. I chose the exhaust over a bigger rider because it keeps the role "one planned burst" and stops 2× from becoming a loop.

3. **Interplay**
- **R9:** the CORRUPTED aftermath now costs 2× RAM for cards and nudges. At RAM 1, Hot Patch+ is cheap to set up but its back end is not, so pair it with Cleanse or Sanitize right after the trigger.
- **R8:** OVERCLOCKED is a status, so Encrypt on the same slice absorbs it. Don't Encrypt the slice you are about to overclock.
- **R11:** it is best on a Perfect-only slice (e.g. a 3-tick G P G) where a landing reliably hits. On a WEAK-heavy 6-tick slice, 2× × 0.5 only gets you back to 1×.
- Overclock multiplies the slice's output; it does not stack with Patch+ Firmware beyond what the current multiplier order already does. Confirm that order in the sim.

4. **Data**
- **Changed against the current .tres:** `ram_cost` 2 → 1; `cycle_cost` 65 → 85; `exhaust` false → true; `description` updated; `id` `hot_patch_plus` (the upgrade link needs a pointer from the base card).
- **New field:** `EffectData.multiplier` is already on the schema, but APPLY_STATUS ignores it today. The OVERCLOCK handler would need to read it and store the per-slice overclock factor, defaulting to 1.5 (`campaign_config` value). This is **NEW: status magnitude on APPLY_STATUS**, a small change inside N9's status rules.
- **Data-only fallback:** none for 2×. A reduced + (RAM 1, exhaust, still 1.5×) is purely data. It is weaker, but it is still a real sidegrade.

5. **Q:**
- Q: Should the 2× multiplier be authored per card (the `multiplier` field) or become a global OVERCLOCKED tuning value? Per card keeps Burner and Solar Flares unaffected.
- Q: Should the + also skip the burn-out into CORRUPTED when the slice lands Perfect? It is a stronger rider, but it turns the card into a safe buff rather than a trade-off.
