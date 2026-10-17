<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__power_tap; status ok; tokens in 5170 cache-write 0 cache-read 32585 out 1164; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: power_tap

1. **Role**: A free RAM-for-HP converter. It is a tempo tool for turns where the hand costs more than the RAM on hand, and it pays for nudges and corrupted-slice surcharges.

2. **Upgraded card: Power Tap+** (one level only; no further tiers needed)
- **RAM cost:** 0 (unchanged)
- **Cycle cost multiplier:** ×1.5 (55 → 83, rounded to 80)
- **Text:** "Gain 3 RAM and take 3 damage."
- **Exhaust:** false (unchanged)
- **wheel_target:** OWN (0, unchanged)
- **Effects:**
  1. GAIN_RAM (type 12), target SELF, amount 3 (FLAT), ring_scope OUTER (unused), status NONE, duration 0
  2. DEAL_DAMAGE (type 0), target SELF, amount 3 (FLAT), duration 0 (unchanged)

**Why this change:** The base rate is 1.5 HP per RAM. The + rate is 1.0 HP per RAM, so the number gets bigger and the card keeps its identity. I rejected cutting the damage to 2 for 2 RAM, because it would make a 0-cost HP trade nearly free and would be a straight upgrade at every HP total. Raising the RAM keeps the HP cost fixed and the decision intact: the player still weighs 3 HP against whether the extra RAM changes the turn. The cost point where the + version is not better is a deliberate sidegrade: at 1 RAM the base version's 2 RAM is enough, and the 1 RAM overshoot is wasted. A max-RAM cap of 12 also limits the + version when RAM is high. The higher Cycle price makes the upgrade a real shop choice.

3. **Interplay**
- **Corruption as double RAM (R9):** Each corrupted slice makes nudges and cards cost 2×. The extra RAM from the + version covers one more surcharged action (a 1-RAM card costing 2 plus a nudge). Power Tap+ pairs well with Cleanse-light decks that accept corruption.
- **Genome Core P4:** Its pierce Adrenaline and corrupting hits make HP the scarcer resource. The 3 self-damage cannot be blocked by BLOCK or SHIELD, but SANDBOX does not stop it either (it is self-damage, not an attack). The + version therefore stays a real cost in P4, and the 1-RAM-per-HP rate makes it a fair trade there.
- **R3 floors** do not apply to the player, so no parking issue.

4. **Data**
- `fx0` (GAIN_RAM): `amount` 2 → 3.
- `display_name`: "Power Tap+". `id`: `power_tap_plus`. Description updated.
- `cycle_cost`: 55 → 80.
- No new effects or systems. It is data-only.
- An upgrade-link field (e.g. `upgrades_to` on `CardData`) is NEW: card upgrade link, which belongs to the card-upgrade pass. It is not needed for this card's data.

5. **Q:**
- Q: Should upgraded cards be `offered = false` in reward pools and only reachable through an upgrade station or a Rack reward?
- Q: Does self-damage from Power Tap+ trigger any future "damage taken" listeners (N6), such as the Echo reactions?
