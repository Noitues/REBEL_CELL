<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__overload; status ok; tokens in 5176 cache-write 0 cache-read 32585 out 1222; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: overload

1. **Role**: Neutral burst card. It converts 4 HP into 10 damage for 3 RAM, once per combat (Exhaust). Players use it to finish a phase or hit a threshold before enrage.

2. **Upgraded card: Overload+** (one level only, so no Level naming)
- **RAM cost:** 3 (unchanged).
- **Cycle cost multiplier:** ×1.5 (70 → 105). Uncommon at Mainframe prices.
- **Text:** "Deal 14 damage to the target and take 4. Exhaust."
- **Effects:**
  1. DEAL_DAMAGE, target TARGET_WHEEL (2), amount 14, amount mode FLAT, ring_scope OUTER, no status, duration 0.
  2. DEAL_DAMAGE, target SELF (0), amount 4, FLAT. Unchanged.
- **Exhaust:** true. **wheel_target:** ENEMY (1), unchanged.
- **Choice:** the bigger number only, with the self-cost held. The self-damage is the card's identity, so the + version improves the ratio from 2.5 to 3.5 damage per HP. I rejected a RAM cut to 2 because Overload at 2 RAM fits every hand and removes the "pay 3, plan around it" decision. I rejected a rider like pierce because pierce is reserved for Adrenaline-type content.
- **Not strictly dominant:** it is better at every cost point except Cycles, which is a deliberate price. 14 damage also overshoots parked thresholds more often (R3 loses the excess), so the base card is the better pick when finishing a short phase. Against Normal 28–36 HP at T1, 14 is about 40 % of the fight, so the + version has to be rationed (see Q).

3. **Interplay**
- **R3 parking:** a 14-damage hit wastes more damage against a nearby floor. Prefer the + version in a long phase (Genome Core P3/P4, about 105 HP each) and the base version when a threshold is close.
- **Corruption (R9):** the 3 RAM becomes 6 if the acting pointer reads a CORRUPTED slice. Cards can't be steered around that, so plan the landing first. The 4 self-damage is a plain loss, so it is not a Parasite-ring conflict, but it makes the card risky against IV chip damage.
- **SANDBOX/BLOCK:** the damage is not pierce, so BLOCK or SHIELD still absorbs it. Hold it for a Barrier-free turn.

4. **Data** (changes against the current .tres)
- `fx0.amount`: 10 → 14.
- `id`: `overload_plus`. `display_name`: "Overload+". `description` updated.
- `cycle_cost`: 70 → 105.
- `rarity`: stays 1.
- Everything else is unchanged. No new system. The amount-mode field (N1) would be written explicitly as FLAT, with a data-only default of FLAT if N1 isn't built yet.
- The upgrade link needs a field such as `upgrades_to: StringName` (NEW: card upgrade link). Fallback: a separate card file with `offered = false`, reached through the upgrade-station reward row (N18).

5. **Q:**
- Q: Should the upgrade also lower the self-damage (4 → 3) at a later level, or is a one-level pass enough for a card with a built-in cost?
- Q: Should enemy-side damage reduction (the Clawback-style "damage to you" listeners in mini-bosses) count the self-damage of this card, since it comes from the player?
