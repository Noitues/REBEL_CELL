<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__duck; status ok; tokens in 5103 cache-write 0 cache-read 32585 out 1148; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: duck

1. **Role**: A 2-RAM, neutral, reward-pool "answer one attack" card. It is SANDBOX under R13 (negates one whole attack resolution). It is the panic button against a big hit, such as Medicine ×4 or a boss Overflow.

2. **Upgraded card: Duck+** (one level is enough; Duck is simple).
- **RAM cost:** 1 (from 2).
- **Cycle cost multiplier:** ×1.25 (60 → 75). The cost cut is the main gain.
- **Text:** "Negate the next incoming attack this turn. Exhaust."
- **Effect list:** one EffectData: type EVADE, target SELF, amount 1, ring_scope OUTER (unused), status NONE, duration_turns 0 (lasts the turn), multiplier 1.0.
- **Exhaust:** true (new on the + version).
- **wheel_target:** OWN (unchanged).

Why this shape: a bigger number does nothing, because SANDBOX already negates a whole attack. A wider target would turn it into a different card. So the upgrade is a cost reduction paid for with Exhaust. It is a sidegrade, not a strict upgrade:
- **Duck (2 RAM, recurring)** stays better in long fights with several dangerous turns (Genome Core P2–P3, Meridian Overtime).
- **Duck+ (1 RAM, once per combat)** is better in short fights (Normal and Elite), where one hit decides the fight, and in the opening turns when RAM is scarce. It also pairs with Calibrate or Cache turns.

3. **Interplay**
- **Pierce:** it does not bypass SANDBOX (R13), so Duck+ is the only clean answer to Adrenaline in Genome Core P4.
- **Corrupted slices (R9):** a card costs double RAM only when the acting pointer reads a CORRUPTED slice. Duck+ would cost 2 there, the same as base Duck, so the discount disappears while you are corrupted. That nudges the player toward Cleanse, which fits the Genome Core theme.
- **Multi-pointer enemies:** "one whole attack" means every hit of one resolution. Against a 2-needle P3 boss, Duck+ negates one needle's resolution, not both. The first resolved attack gets negated, and the preview must show which one.

4. **Data**
- **Changed fields:** `ram_cost` 2 → 1; `cycle_cost` 60 → 75; `exhaust` false → true; `description` as above.
- **Unchanged:** `id` (+ version `duck_plus`), `rarity`, `class_id`, `wheel_target`, and the effect (type 3).
- **Systems:** the EVADE rule change is N14 (SANDBOX negates a whole resolution), which Duck already depends on. No new system. The + version is just a second .tres, so a data-only fallback exists. `upgrade_of` linking is NEW: card upgrade link, which belongs to the card-upgrade pass.

5. **Q:**
- Q: Should Duck+ be Uncommon rarity, or keep the rarity of Duck, so that upgrading doesn't change drop tables?
- Q: Should the base Duck's "next incoming attack" be used up by an enemy's sweep attack or by an attack on a drone? Does the evade take effect only on attacks that reach the player?
