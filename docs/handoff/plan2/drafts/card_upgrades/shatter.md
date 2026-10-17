<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__shatter; status ok; tokens in 5199 cache-write 0 cache-read 32585 out 1214; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: shatter

1. **Role**: Breaker's hub-and-resistance opener. It clears the Hub passive and the first layer of spin resistance so the Breaker's big spins and Perfect hooks can land. It is the "open the wall" card.

2. **Upgraded card: Shatter+**
- **RAM cost:** 2 → 1.
- **Cycle cost multiplier:** ×1.5 (70 → 105).
- **Text:** "Breach the target Hub for 1 turn and strip 2 resistance."
- **Effects:**
  - fx0: HUB_BREACH (type 11), target TARGET_WHEEL, amount 1 (turns), ring_scope OUTER (unused), status NONE, duration_turns 0 (unchanged).
  - fx1: MODIFY_RESISTANCE (type 10), target TARGET_WHEEL, amount **−2** (FLAT), unchanged otherwise.
- **Exhaust:** false (unchanged).
- **wheel_target:** ENEMY (1, unchanged).

**Why this and not a bigger breach:** Hub Breach already has a 2-turn card (Short Circuit, exhaust), so a longer breach would blur the line between them. The upgrade is a cost cut plus +1 strip. At 1 RAM it does what Strip (1 RAM, −2) does and adds the Hub breach, so it is not a free sidegrade in the deck. It also costs 50% more Cycles, which is the price of the efficiency.

**Not strictly dominant:** the 105 Cycle cost and the shop slot are the trade. A player who rarely meets resistance gains almost nothing from the +1 strip. Bosses with Compliance Lock or Weight (resistance 2–3) gain a lot, because one + card can clear the whole resistance.

3. **Interplay**
- **Boss buffs (R7):** a Compliance Lock boss with resistance 2 is zeroed by one Shatter+, so the card is a soft answer when its counter Exploit isn't drawn. The Hub-breach half still turns off Metabolism-type heal for one turn only when that heal is a Hub passive, so it does not replace the Exploit.
- **Parasite ring and corruption (R9):** at 1 RAM it stays cheap even on a CORRUPTED slice. A 2 RAM base would cost 4 there, and the + version costs 2.

4. **Data** (changes to `shatter.tres`)
- `ram_cost` 2 → 1.
- `cycle_cost` 70 → 105.
- `fx1.amount` −1 → −2.
- `display_name` "Shatter" → "Shatter+" and the description string updated.
- No new effect or system. The upgrade-state mechanism (a `+` variant resource or an `upgraded_from` field on CardData) is the card-upgrade pass's own system, **NEW: card upgrade link**. The data-only fallback is a separate `shatter_plus.tres` with `offered = false` and a rename in the upgrade UI.
- The `breaker` and `wrecker` class files reference `shatter` by id, so the upgrade link must resolve the + id, or both files need an upgrade-aware lookup.

5. **Q:**
- Q: Should resistance strip on an enemy with a passive trait (restores each turn) count as the same "absorbed" tick that nudges use, so Shatter+ reads as "clear one nudge of tax" in the preview?
- Q: Does the Hub breach on a boss whose heal is a buff (Metabolism) get ignored, and is that the intended Exploit tension?
