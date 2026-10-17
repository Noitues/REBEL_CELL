<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__hub_breach; status ok; tokens in 5081 cache-write 0 cache-read 32585 out 1171; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: hub_breach

1. **Role:** A neutral utility answer to enemy Hub passives (resistance, per-turn heal, shield). It opens a 1-turn window for a burst, a Flip or a Spin, and it is the in-fight tool that stands in for a boss's Exploit-counterable buff.

2. **Upgraded card: Hub Breach+** (one level only; the card is simple enough)
- **RAM cost:** 1 (was 2).
- **Cycle cost multiplier:** ×1.25 (70 → 88).
- **Text:** "Disable the target Hub for 1 turn. If it was already disabled, extend by 1 more turn." Rejected: a flat 2-turn duration, because Short Circuit already owns that niche at 3 RAM and Exhaust.
- **Effects:**
  1. HUB_BREACH, target TARGET_WHEEL, amount 1, duration_turns 1 (unchanged).
  2. Rider: `strip_resistance`. MODIFY_RESISTANCE, target TARGET_WHEEL, amount −1. It applies only to the Hub-sourced resistance of the breached Hub, so it is a one-shot, not a passive removal. A breached Hub already suspends its resistance for the turn, so the rider matters for Hub resistance that **refreshes after the breach ends** (Compliance Lock style): the next turn starts at R−1.
- **exhaust:** false. **wheel_target:** 1 (ENEMY).

**Why this shape:** The cost drop makes it playable beside a nudge or spin card in a 5-card hand (breach plus a 2-RAM follow-up). The rider keeps the cost cut from being the whole upgrade. It is a sidegrade against Shatter (breach + strip 1, class-locked) and Short Circuit (2 turns, 3 RAM, Exhaust). Hub Breach+ stays non-exhaust and 1-turn, so it is a repeatable, cheap answer, not a lasting one.

3. **Interplay:**
- A boss with a Hub buff (Metabolism, Compliance Lock) is a repeatable counter only while it is a hub rule. Boss buffs the Exploit system turns off stay Exploit-governed, so the card does not replace the Exploit. Needs a ruling (see Q1).
- With phases (R3), a breach lasts a turn, not a phase. A hub_override on a phase change should replace the hub and clear the breach.

4. **Data:**
- `ram_cost` 2 → 1.
- `cycle_cost` 70 → 88.
- Add a second EffectData: MODIFY_RESISTANCE, target 2, amount −1. Current .tres uses `type = 11` (HUB_BREACH) and `target = 2` (TARGET_WHEEL).
- No new system. The rider uses existing effects.
- `description` text updated.
- N/A: the "extend if already breached" clause needs a small handler tweak (NEW: breach stacking, S). Data-only fallback: drop that clause and ship the cost cut plus strip rider.

5. **Q:**
- Q: Should Hub Breach bypass a boss's hub-based Exploit-counterable buffs (Metabolism, Compliance Lock) for one turn, or should those be immune so the Exploit stays meaningful?
- Q: Does a breached Hub still run phase-change `hub_override`s that fire mid-turn, or does the breach end at the phase change?
