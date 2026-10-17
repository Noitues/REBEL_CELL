<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__hot_swap; status ok; tokens in 5183 cache-write 0 cache-read 32585 out 1237; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: hot_swap

1. **Role:** Rigger's RAM-neutral precision tool. It snaps the outer ring to a Perfect and pays back 1 RAM, so the net cost is 1 RAM for a guaranteed Perfect landing.

2. **Upgraded card: Hot Swap+** (one level only; a second level is not needed).
- **RAM cost:** 2 → 1.
- **Cycle cost multiplier:** ×1.5 (75 → 113, rounded to 115). This is a price on the cost cut, so the upgrade has to be bought.
- **Text:** "Snap your outer ring to the slice center. Gain 2 RAM if the slice was not already Perfect, else 1."
- **Simplest data form (chosen):** keep the snap and make the RAM refund 2 flat. With cost 1, the net is +1 RAM when played. Hot Swap+ becomes a RAM-positive Perfect, which fits Rigger's economy identity (Hub +1 max RAM, Perfect refunds RAM).
- **Effects:**
  1. SNAP_TO_CENTER, target OWN_WHEEL, ring_scope OUTER, amount 0.
  2. GAIN_RAM, target SELF, amount 2, amount_mode FLAT (N1; the field is only a label here, so today's plain int works).
- **Exhaust:** false (same as the base card).
- **wheel_target:** OWN.
- **Dominance:** this strictly dominates the base card at every cost. That is accepted because the upgrade costs 1.5× Cycles and the base card is already weak (it is `snap` plus 1 RAM). The sidegrade alternative would add a free nudge, which overlaps `torque_wrench`.
- **Not dropping the cost to 0:** a 0-cost Perfect plus 2 RAM would loop with Rigger's Perfect refund hook.

3. **Interplay:**
- **Tick quality (R11):** snapping to the slice centre only gives Perfect on odd-size slices (3, 5, 7). On a 4- or 6-tick slice there is no centre tick, so the snap lands on a GOOD tick. The card text should say "best tick" and a preview should show the landing tier. The Calibrated Firmware turns that landing into PERFECT.
- **Corruption (R9):** on a CORRUPTED slice the card costs 2× RAM (cost 1 → 2). The +2 refund then only breaks even, which gives a reason to Cleanse first.
- **Statuses (R8):** TIER_DOWN drops the landing one tier, so Hot Swap+ lands at GOOD at best.

4. **Data (changes against the current .tres):**
- `ram_cost` 2 → 1.
- `cycle_cost` 75 → 115.
- `fx_ram.amount` 1 → 2.
- `display_name` "Hot Swap+" and the description updated.
- Mark the card with an upgrade-pairing entry (`upgrade_of = &"hot_swap"`, NEW: card upgrade link; data-only fallback is a separate card file `hot_swap_plus.tres` with `offered = false` until the upgrade pass builds the swap).
- No other new effects or systems. Nothing in the effect list depends on N8–N12.

5. **Q:**
- Q: Should snap on an even-size slice count as "Perfect" for Rigger's Perfect hook once Calibrated exists, or only true centre ticks?
- Q: Is +1 net RAM per play too strong when stacked with `steady_hand` and the Rigger Hub, or should the refund stay at 1 and only the cost drop to 1?
