<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__static_shock; status ok; tokens in 5107 cache-write 0 cache-read 32585 out 1089; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: static_shock

1. **Role**: The cheapest neutral direct-damage card (4 damage, 1 RAM). It gives any class a small burst that does not depend on wheel alignment, and it works as a finisher against a phase floor.

2. **Upgraded card**: **Static Shock+** (one level is enough; the card is too simple for a second).
   - RAM cost: 1 (unchanged)
   - Cycle cost multiplier: ×1.5 (55 → 83)
   - Text: "Deal 6 damage to the target. If the target has block or shield, also remove 2 of it first." *Rejected as too fiddly; the chosen version is below.*
   - **Chosen text:** "Deal 6 damage to the target. Pierce."
   - Effect list:
     1. DEAL_DAMAGE, target POINTER_TARGET (enum 2 as in the current file; keep it), amount 6, `pierce` = true (**NEW: effect-level pierce flag**; today pierce exists only as the ring segment and as the N20 slice rider)
   - Exhaust: false
   - wheel_target: ENEMY (1, unchanged)

   **Why pierce and not just +2:** a plain 4 → 6 is the safe option, but the base card is already dead against BLOCK and SHIELD (Genome Core Barrier 12–20, Triage Reserve 5 %). Pierce gives a different job: it is the neutral answer to defensive phases. The 6 damage is at a flat tier-independent amount (R2 buffs/debuffs don't scale), so it stays small beside the Perfect ×4 burst slices.
   - Not strictly dominant: the Cycle cost is +50 %. Against an undefended enemy the card is only +2 damage. If a data-only fallback is wanted, use amount 6 with no pierce at ×1.25 Cycles.
   - Preview: this is deterministic, so the chip shows "6 (pierce)". Parked damage still applies (R3 floors the HP).

3. **Interplay**
   - Pierce does not bypass SANDBOX or satellite bodyguards (R13, GDD 2.7). The card is therefore bad against Fortress and Retainer guards, and good against Barrier and Triage Reserve.
   - Damage ignores statuses and sizes. It is the safe pick when a CORRUPTED slice (double RAM) makes alignment plays expensive.

4. **Data**
   - `amount` 4 → 6.
   - `display_name` "Static Shock+" and `description` updated; `cycle_cost` 55 → 83; `id` &"static_shock_plus".
   - New field: `EffectData.pierce: bool` (**NEW: card-level pierce**; the same flag is needed by N20's slice `pierce`, so share the implementation in `effect_interpreter.deal_hit`; size S). Data-only fallback: 6 damage without pierce.

5. **Q:**
   - Q: Should the + version be one tool per card (pierce here), or should the upgrade pass avoid effect-level pierce until N20 exists?
   - Q: Does pierce on a card bypass an enemy percent shield (R5), or should the enemy shield cap (open question 9) apply to it?
