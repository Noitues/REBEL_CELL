<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__stim_patch; status ok; tokens in 5117 cache-write 0 cache-read 32585 out 1244; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: stim_patch

**Level note:** one + version is enough. The card is a single-purpose heal, and a second level would only add a bigger number.

1. **Role:** the neutral emergency heal, a rare-feeling reward-pool card. It converts a turn's RAM (3, about a quarter of the 12 cap) into HP once per combat. It competes with Patch Up (RAM 2, heal 6, exhaust).

2. **Upgraded card: Stim Patch+**
- **RAM cost:** 3 → 2. This is the main upgrade, and it lets the card fit alongside another play in a 4-RAM turn.
- **Cycle cost multiplier:** ×1.0 on the base 70, so the + version is not repriced. The upgrade itself is bought separately in the card-upgrade pass.
- **Text:** "Heal 12. Gain 4 block. Exhaust."
- **Effects:**
  1. HEAL, target SELF, amount 12, amount_mode FLAT (N1; the data-only fallback is the current plain `amount`). Player-side HEAL is not tier-scaled.
  2. GAIN_BLOCK, target SELF, amount 4, FLAT, duration 0 (the standard block rule: it expires at the start of your next turn).
- **exhaust:** true (unchanged).
- **wheel_target:** OWN (0, unchanged).
- **Sidegrade:** the heal stays 12, so the + version can't beat Patch Up on heal per RAM and doesn't make HP a free resource.
- **Rider choice:** a flat 4 block is a small rider, not a new role. It covers the turn you spend healing instead of defending, so it fixes the card's real weakness. Heal also can't overheal, and the block still has value at full HP.
- **Not strictly dominant:** the + version has the same exhaust and heal. Its only advantages are RAM 2 and the 4 block, and neither matters when you can't afford the turn anyway.

3. **Interplay:**
- **Corruption as double RAM:** the card costs RAM only when played, not per slice. The 2 RAM cost is not affected unless the card text ever acts on a corrupted slice (it doesn't).
- **Boss phases:** the card is an answer to parked-damage fights where you must sustain through a 3–4 turn phase. Against the Genome Core, the rider block (4) is still absorbed by Barrier-sized enemy hits, so it only prevents small chip damage like IV.
- **R13:** the block is BLOCK, not SHIELD, so it never lingers or counts toward `shield_cap`.

4. **Data:**
- **Changed fields:** `ram_cost` 3 → 2; add `fx1` (type 2 GAIN_BLOCK, target 0, amount 4); `effects` gets two entries; `description` becomes "Heal 12. Gain 4 block. Exhaust."; `display_name` becomes "Stim Patch+".
- **New systems:** none required. N1 is optional if PERCENT amounts are desired later.
- **Upgrade links:** the base-card to + mapping needs an upgrade field. That belongs to the card-upgrade pass and is NEW: card upgrade link (e.g. `upgrades_to: CardData`).

5. **Q:**
- Q: Should heals ever be PERCENT (a share of max HP) on cards, so the same card is worth more to a high-HP operative? I recommend keeping it FLAT here, because 12 HP is already 20–27 % of a Breaker's or Ghost's HP.
- Q: Does an upgrade pass use the same `cycle_cost`, or should upgrades be priced separately at the shop or Workshop?
