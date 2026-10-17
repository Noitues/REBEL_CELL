<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__blind_spot; status ok; tokens in 5170 cache-write 0 cache-read 32585 out 1236; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: blind_spot

**1. Role.** Ghost's cheap control card: it denies an enemy respin (a lasting setup) and strips a little resistance so the following nudges and spins stick. It is a setup piece, not a payoff.

**2. Upgraded card: "Blind Spot+"** (one upgrade level; no second level is needed).
- **RAM cost:** 2 → 1
- **Cycle cost multiplier:** ×1.5 of the base 75, so 112, rounded to 110
- **Text:** "The target skips its next respin and loses 2 resistance."
- **Effect list:**
  1. FREEZE, target TARGET_WHEEL (2), ring_scope WHOLE_WHEEL, amount 0, no duration. Unchanged.
  2. MODIFY_RESISTANCE, target TARGET_WHEEL (2), amount −2. The only change is −1 → −2.
- **Exhaust:** false (unchanged). **wheel_target:** ENEMY (1), unchanged.

Why this and not both numbers: the rider alone (−2) is a bigger number, and the RAM reduction is the real upgrade because Ghost plays this alongside ghost_step and nudges. Cutting RAM 2 → 1 puts it at the same price as Strip and Freeze's rival, but it still does strictly more than Strip. Freeze costs 3 and exhausts, so Blind Spot+ at 1 is a clear ladder step, not a replacement.

It is a mild dominance (cheaper and stronger), so the price is the balance lever: it costs more Cycles at the shop (110 vs 75). Cheaper plus −2 resistance was judged better than a sidegrade because the base card is weak next to Ghost's own Perfect hook (Strip 2 resistance), and the + version only matches that on par.

**3. Interplay.**
- **Resistance now stacks with the Ghost core:** the first nudge each turn already ignores resistance, so −2 matters mostly for spin and flip cards. Against Halcyon's nudge lockout (N7) it does not help, so keep Strip-type play for the resistance-3 Meridian Weight (R·3 needs two plays, one with this).
- **Mini-bosses with Weight 3** (Meridian P1): one Blind Spot+ takes it to 1, and a Strip finishes it. This is the intended use.
- **Corruption as double RAM (R9):** a cost-1 card played with the pointer on a CORRUPTED slice costs 2, which equals the base card's price. The + version therefore holds up better under corruption.
- **Compliance Lock** (Genome Core buff) blocks Flip and Respin: this card's resistance strip is what lets Flip through, so its value rises on bosses.

**4. Data.**
- `ram_cost` 2 → 1
- `cycle_cost` 75 → 110
- `fx_strip.amount` −1 → −2
- `display_name` "Blind Spot+"
- `description` updated
- Nothing new: no N# dependency, data-only.
- Needs a way to link base to upgraded card (CardData has no `upgrade_of` field): **NEW: card upgrade link** (`upgraded_id`, StringName). Fallback: a separate `blind_spot_plus.tres` with `offered = false`, swapped by the upgrade service.

**5. Q:**
- Q: Should the + version also hit the free-nudge economy (e.g. the freeze lasts through the enemy's next two turns on Normals), or is a pure resistance and cost upgrade enough?
- Q: The Phantom class also references the card; does it get the same upgrade or a class-specific one?
